#!/usr/bin/env python3
"""
NAS Access with Azure Vault Credentials
Retrieves NAS credentials from Azure Key Vault and uses NAS API.
Supports both NAS API (Synology) and SSH access with Lumina integration.

@triad: NAS credentials are stored in Azure Key Vault (Tier 1) and ProtonPass CLI
(Tier 2), per Triad Password Manager policy. Clawedbot-style: same logic as
1Password CLI but using ProtonPass CLI (pass-cli / protonpass). A proxy-cache
(NAS) server is used that only pulls passwords every thirty minutes; in-memory
credential cache TTL is 30 minutes to match. Azure secrets: nas-username
(e.g. backupadm), nas-password; or nas-username-{ip}, nas-password-{ip}.
ProtonPass: item title/username matching NAS, Synology, backupadm. See
docs/system/TRIAD_PASSWORD_MANAGER_SYSTEM.md, TRIAD_VAULT_STRATEGY.md, and
config/triad_nas_credentials.json (proxy_cache).
"""

import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

# Optional: Universal decision tree (for future AI fallback decisions)
try:
    from universal_decision_tree import DecisionContext, DecisionOutcome, decide

    UNIVERSAL_DECISION_TREE_AVAILABLE = True
except ImportError:
    UNIVERSAL_DECISION_TREE_AVAILABLE = False
    # Decision tree not available - continue without it

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from azure.identity import DefaultAzureCredential
    from azure.keyvault.secrets import SecretClient

    KEY_VAULT_AVAILABLE = True
except ImportError:
    KEY_VAULT_AVAILABLE = False
    print("WARNING: Azure Key Vault SDK not installed")
    print("Install with: pip install azure-keyvault-secrets azure-identity")

try:
    from synology_nas_upload import SynologyNASUploader

    NAS_API_AVAILABLE = True
except ImportError:
    NAS_API_AVAILABLE = False
    print("WARNING: NAS API module not found")

try:
    import paramiko

    SSH_AVAILABLE = True
except ImportError:
    SSH_AVAILABLE = False
    print("WARNING: paramiko not installed. Install with: pip install paramiko")

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from lumina_logger import get_logger

    logger = get_logger("NASAzureVaultIntegration")
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("NASAzureVaultIntegration")


# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

# Module-level credential cache (shared across instances)
# TTL: 30 minutes to match NAS proxy-cache server retention policy
_credential_cache: Dict[str, Dict[str, Any]] = {}
_CREDENTIAL_CACHE_TTL = timedelta(
    minutes=30
)  # Cache credentials for 30 minutes (matches NAS proxy-cache)


class NASAzureVaultIntegration:
    """Access NAS using credentials from Azure Key Vault"""

    def __init__(
        self,
        vault_name: Optional[str] = None,
        vault_url: Optional[str] = None,
        nas_ip: str = "<NAS_PRIMARY_IP>",
        nas_port: int = 5001,
        credential_cache_ttl: Optional[timedelta] = None,
    ):
        """
        Initialize NAS Azure Vault integration

        Args:
            vault_name: Azure Key Vault name (e.g., "jarvis-lumina")
            vault_url: Full Azure Key Vault URL (overrides vault_name)
            nas_ip: NAS IP address
            nas_port: NAS port (default: 5001 for DSM)
            credential_cache_ttl: TTL for credential cache (default: 30 minutes, matches NAS proxy-cache retention)
        """
        self.nas_ip = nas_ip
        self.nas_port = nas_port
        self.vault_client: Optional[SecretClient] = None
        self.nas_uploader: Optional[SynologyNASUploader] = None
        self._cache_ttl = credential_cache_ttl or _CREDENTIAL_CACHE_TTL

        # Determine vault URL
        if vault_url:
            self.vault_url = vault_url
        elif vault_name:
            self.vault_url = f"https://{vault_name}.vault.azure.net/"
        else:
            # Try environment variable or default
            self.vault_url = os.getenv(
                "AZURE_KEY_VAULT_URL", os.getenv("AZURE_KEY_VAULT_NAME", "jarvis-lumina")
            )
            if not self.vault_url.startswith("https://"):
                self.vault_url = f"https://{self.vault_url}.vault.azure.net/"

        logger.info(f"Initialized with Vault URL: {self.vault_url}")
        logger.info(f"NAS: {nas_ip}:{nas_port}")

    def get_key_vault_client(self) -> Optional[SecretClient]:
        """
        Get Azure Key Vault client

        Uses in-memory caching with 30-minute TTL to match NAS proxy-cache retention policy.
        Credentials are cached in-memory to reduce Azure Key Vault API calls.
        """
        if not KEY_VAULT_AVAILABLE:
            logger.error("Azure Key Vault SDK not available")
            return None

        if self.vault_client:
            return self.vault_client

        try:
            credential = DefaultAzureCredential(
                exclude_interactive_browser_credential=False,
                exclude_shared_token_cache_credential=False,
            )
            self.vault_client = SecretClient(vault_url=self.vault_url, credential=credential)
            logger.info(
                "Azure Key Vault client created (30-min in-memory cache, matching NAS proxy-cache retention)"
            )
            return self.vault_client
        except Exception as e:
            logger.error(f"Failed to create Key Vault client: {e}")
            return None

    def get_nas_credentials(self) -> Optional[Dict[str, str]]:
        """
        Retrieve NAS credentials from Azure Key Vault (with caching)

        Expected secret names:
        - nas-username or nas-username-{nas_ip}
        - nas-password or nas-password-{nas_ip}

        Returns:
            Dict with 'username' and 'password' keys, or None if failed

        Note: Credentials are cached for 1 hour to reduce Azure Key Vault API calls
        """
        # Check cache first (module-level cache shared across all instances)
        cache_key = f"{self.nas_ip}:{self.vault_url}"
        cached = _credential_cache.get(cache_key)
        if cached:
            cached_time = cached.get("cached_at")
            if cached_time and isinstance(cached_time, datetime):
                age = datetime.now() - cached_time
                if age < self._cache_ttl:
                    logger.info(
                        f"✅ Using cached credentials for {cache_key} (age: {age.total_seconds():.1f}s, TTL: {self._cache_ttl.total_seconds():.0f}s)"
                    )
                    return cached.get("credentials")
                else:
                    # Cache expired, remove it
                    logger.debug(f"Cache expired for {cache_key} (age: {age.total_seconds():.1f}s)")
                    _credential_cache.pop(cache_key, None)

        client = self.get_key_vault_client()
        if not client:
            return None

        # Try different secret name patterns
        secret_patterns = [
            f"nas-username-{self.nas_ip.replace('.', '-')}",
            "nas-username",
            f"nas-password-{self.nas_ip.replace('.', '-')}",
            "nas-password",
        ]

        username = None
        password = None

        try:
            # Try to get username
            for pattern in [f"nas-username-{self.nas_ip.replace('.', '-')}", "nas-username"]:
                try:
                    secret = client.get_secret(pattern)
                    username = secret.value
                    logger.info(f"Retrieved username from secret: {pattern}")
                    break
                except Exception:
                    continue

            # Try to get password
            for pattern in [f"nas-password-{self.nas_ip.replace('.', '-')}", "nas-password"]:
                try:
                    secret = client.get_secret(pattern)
                    password = secret.value
                    logger.info(f"Retrieved password from secret: {pattern}")
                    break
                except Exception:
                    continue

            if username and password:
                credentials = {"username": username, "password": password}
                # Cache credentials
                cache_key = f"{self.nas_ip}:{self.vault_url}"
                _credential_cache[cache_key] = {
                    "credentials": credentials,
                    "cached_at": datetime.now(),
                }
                logger.info(
                    f"💾 Cached credentials for {cache_key} (TTL: {self._cache_ttl.total_seconds():.0f}s)"
                )
                return credentials

            # @triad fallback: try UnifiedSecretManager (Triad coordinator)
            try:
                try:
                    from unified_secret_manager import SecretCategory, UnifiedSecretManager
                except ImportError:
                    from scripts.python.unified_secret_manager import (
                        SecretCategory,
                        UnifiedSecretManager,
                    )
                usm = UnifiedSecretManager(azure_vault_url=self.vault_url)
                u = usm.get_secret(
                    f"nas-username-{self.nas_ip.replace('.', '-')}",
                    category=SecretCategory.CREDENTIAL,
                ) or usm.get_secret("nas-username", category=SecretCategory.CREDENTIAL)
                p = usm.get_secret(
                    f"nas-password-{self.nas_ip.replace('.', '-')}",
                    category=SecretCategory.CREDENTIAL,
                ) or usm.get_secret("nas-password", category=SecretCategory.CREDENTIAL)
                if u and p:
                    credentials = {"username": u, "password": p}
                    cache_key = f"{self.nas_ip}:{self.vault_url}"
                    _credential_cache[cache_key] = {
                        "credentials": credentials,
                        "cached_at": datetime.now(),
                    }
                    logger.info("Retrieved NAS credentials via Triad UnifiedSecretManager")
                    return credentials
            except Exception as usm_err:
                logger.debug(f"UnifiedSecretManager fallback skipped: {usm_err}")

            # @triad Tier 2: ProtonPass CLI (Clawedbot-style: 1Password logic with ProtonPass)
            creds_pp = self._get_nas_credentials_from_protonpass()
            if creds_pp:
                cache_key = f"{self.nas_ip}:{self.vault_url}"
                _credential_cache[cache_key] = {
                    "credentials": creds_pp,
                    "cached_at": datetime.now(),
                }
                logger.info("Retrieved NAS credentials via Triad ProtonPass CLI")
                return creds_pp

            logger.warning("Could not retrieve both username and password")
            if not username:
                logger.warning("Username not found in Key Vault")
            if not password:
                logger.warning("Password not found in Key Vault")
            return None

        except Exception as e:
            logger.error(f"Failed to retrieve NAS credentials: {e}")
            return None

    def get_nas_credentials_from_protonpass(self) -> Optional[Dict[str, str]]:
        """Public wrapper for Triad Tier 2: get NAS credentials from ProtonPass CLI (Clawedbot-style)."""
        return self._get_nas_credentials_from_protonpass()

    def _find_protonpass_cli(self) -> Optional[str]:
        """Find ProtonPass CLI (pass-cli.exe or protonpass in PATH). Used for Triad Tier 2."""
        path = os.getenv("PROTONPASS_CLI_PATH")
        if path and Path(path).exists():
            return path
        for candidate in [
            Path(os.path.expanduser("~/AppData/Local/Programs/ProtonPass/pass-cli.exe")),
            Path(os.path.expanduser("~/AppData/Local/Programs/pass-cli.exe")),
            Path(r"C:\Program Files\ProtonPass\pass-cli.exe"),
        ]:
            if candidate.exists():
                return str(candidate)
        for cmd in ["protonpass", "pass-cli", "ppass"]:
            try:
                r = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=5)
                if r.returncode == 0:
                    return cmd
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        return None

    def _get_nas_credentials_from_protonpass(self) -> Optional[Dict[str, str]]:
        """
        Get NAS credentials from ProtonPass CLI (Triad Tier 2, Clawedbot-style).
        Looks for item matching nas, synology, backupadm, or NAS IP in title/username/urls.
        """
        cli = self._find_protonpass_cli()
        if not cli:
            logger.debug("ProtonPass CLI not found; skip Tier 2")
            return None
        search_terms = ["nas", "synology", "backupadm", self.nas_ip.replace(".", "-"), "10-17-17-32"]
        try:
            triad_cfg = script_dir.parent.parent / "config" / "triad_nas_credentials.json"
            if triad_cfg.exists():
                with open(triad_cfg, encoding="utf-8") as f:
                    cfg = json.load(f)
                terms = (cfg.get("protonpass_cli") or {}).get("search_terms")
                if terms:
                    search_terms = list(terms)
        except Exception:
            pass
        try:
            # item list (pass-cli style) or list (protonpass style)
            for args in (
                [cli, "item", "list", "--output", "json"],
                [cli, "list", "--format", "json"],
            ):
                r = subprocess.run(args, capture_output=True, text=True, timeout=15)
                if r.returncode != 0 or not (r.stdout or "").strip():
                    continue
                try:
                    items = json.loads(r.stdout) if isinstance(r.stdout, str) else r.stdout
                except json.JSONDecodeError:
                    continue
                if not isinstance(items, list):
                    items = items.get(
                        "items", items.get("data", []) if isinstance(items, dict) else []
                    )
                matching = []
                for item in items:
                    title = (item.get("title") or item.get("name") or "").lower()
                    un = (item.get("username") or item.get("login") or "").lower()
                    urls = item.get("urls") or []
                    url_str = " ".join(
                        u.get("url", u) if isinstance(u, dict) else str(u) for u in urls
                    ).lower()
                    text = f"{title} {un} {url_str}"
                    if any(term in text or term.replace("-", ".") in text for term in search_terms):
                        matching.append(item)
                if not matching:
                    continue
                item = matching[0]
                item_id = item.get("itemId") or item.get("id") or item.get("uuid")
                title = item.get("title") or item.get("name") or ""
                if item_id:
                    rr = subprocess.run(
                        [cli, "item", "read", str(item_id), "--output", "json"],
                        capture_output=True,
                        text=True,
                        timeout=15,
                    )
                else:
                    rr = subprocess.run(
                        [cli, "get", "--name", title, "--show-details"],
                        capture_output=True,
                        text=True,
                        timeout=15,
                    )
                if rr.returncode != 0 or not (rr.stdout or "").strip():
                    continue
                try:
                    data = json.loads(rr.stdout)
                except json.JSONDecodeError:
                    continue
                username = data.get("username") or data.get("login") or ""
                password = data.get("password") or ""
                if not username or not password:
                    content = data.get("content") or {}
                    if isinstance(content, dict):
                        username = username or content.get("username", "")
                        password = password or content.get("password", "")
                    elif isinstance(content, list):
                        for f in content:
                            if isinstance(f, dict):
                                fn = (f.get("fieldName") or f.get("name") or "").lower()
                                if fn in ("username", "login"):
                                    username = username or f.get("value", "")
                                elif fn == "password":
                                    password = password or f.get("value", "")
                if username and password:
                    return {"username": username, "password": password}
        except Exception as e:
            logger.debug(f"ProtonPass NAS credential fetch failed: {e}")
        return None

    @staticmethod
    def clear_credential_cache():
        """Clear the credential cache (useful for testing or forced refresh)"""
        global _credential_cache
        _credential_cache.clear()
        logger.info("Credential cache cleared")

    def connect_to_nas(self) -> bool:
        """
        Connect to NAS using credentials from Azure Key Vault

        Returns:
            True if connection successful, False otherwise
        """
        if not NAS_API_AVAILABLE:
            logger.error("NAS API module not available")
            return False

        # Get credentials from Azure Vault
        credentials = self.get_nas_credentials()
        if not credentials:
            logger.error("Could not retrieve NAS credentials from Azure Vault")
            return False

        # Initialize NAS uploader
        self.nas_uploader = SynologyNASUploader(nas_ip=self.nas_ip, nas_port=self.nas_port)

        # Login
        if self.nas_uploader.login(credentials["username"], credentials["password"]):
            logger.info("Successfully connected to NAS using Azure Vault credentials")
            return True
        else:
            logger.error("Failed to login to NAS")
            return False

    def upload_file(self, local_path: Path, remote_path: str) -> bool:
        """Upload file to NAS"""
        if not self.nas_uploader:
            if not self.connect_to_nas():
                return False

        return self.nas_uploader.upload_file(local_path, remote_path)

    def upload_directory(self, local_dir: Path, remote_base: str) -> Dict[str, Any]:
        """Upload directory to NAS"""
        if not self.nas_uploader:
            if not self.connect_to_nas():
                return {"success": 0, "failed": 0, "files": []}

        return self.nas_uploader.upload_directory(local_dir, remote_base)

    def create_folder(self, remote_path: str) -> bool:
        """Create folder on NAS"""
        if not self.nas_uploader:
            if not self.connect_to_nas():
                return False

        return self.nas_uploader.create_folder(remote_path)

    def disconnect(self):
        """Disconnect from NAS"""
        if self.nas_uploader:
            self.nas_uploader.logout()
            self.nas_uploader = None

    def get_ssh_client(self) -> Optional[Any]:
        """Get SSH client for NAS operations"""
        if not SSH_AVAILABLE:
            logger.error("paramiko not available. Install with: pip install paramiko")
            return None

        credentials = self.get_nas_credentials()
        if not credentials:
            logger.error("Could not retrieve NAS credentials from Azure Vault")
            return None

        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(
                hostname=self.nas_ip,
                port=22,
                username=credentials["username"],
                password=credentials["password"],
                timeout=30,
                allow_agent=False,  # Disable SSH agent (prevents publickey attempts)
                look_for_keys=False,  # Don't look for SSH keys (password-only auth)
            )
            logger.info("SSH connection established (password authentication)")
            return ssh_client
        except Exception as e:
            logger.error(f"Failed to establish SSH connection: {e}")
            return None

    def execute_ssh_command(self, command: str) -> Dict[str, Any]:
        """Execute command on NAS via SSH"""
        ssh_client = self.get_ssh_client()
        if not ssh_client:
            return {"success": False, "error": "SSH connection failed"}

        try:
            stdin, stdout, stderr = ssh_client.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode("utf-8")
            error = stderr.read().decode("utf-8")

            result = {
                "success": exit_status == 0,
                "exit_status": exit_status,
                "output": output,
                "error": error if error else None,
            }

            # Publish to Lumina if available
            self._publish_to_lumina("nas_ssh_command", {"command": command, "result": result})

            return result
        except Exception as e:
            logger.error(f"Failed to execute SSH command: {e}")
            return {"success": False, "error": str(e)}
        finally:
            ssh_client.close()

    def _publish_to_lumina(self, event_type: str, data: Dict[str, Any]) -> None:
        """Publish NAS operations to Lumina API"""
        if not REQUESTS_AVAILABLE:
            return

        try:
            # Try to publish to R5 system
            lumina_endpoint = os.getenv("LUMINA_API_ENDPOINT", "http://localhost:8000")
            payload = {"event_type": event_type, "source": "nas_azure_vault", "data": data}

            response = requests.post(f"{lumina_endpoint}/r5/events", json=payload, timeout=5)

            if response.status_code == 200:
                logger.debug(f"Published to Lumina: {event_type}")
        except Exception as e:
            logger.debug(f"Could not publish to Lumina (may not be running): {e}")


def main():
    try:
        """Main function for testing"""
        import argparse

        parser = argparse.ArgumentParser(description="Access NAS with Azure Vault credentials")
        parser.add_argument("--vault-name", help="Azure Key Vault name")
        parser.add_argument("--vault-url", help="Azure Key Vault URL")
        parser.add_argument("--nas-ip", default="<NAS_PRIMARY_IP>", help="NAS IP address")
        parser.add_argument("--nas-port", type=int, default=5001, help="NAS port")
        parser.add_argument("--test", action="store_true", help="Test connection only")
        parser.add_argument("--upload", help="File or directory to upload")
        parser.add_argument("--target", default="/backups/MATT_Backups", help="Target path on NAS")
        parser.add_argument("--ssh", help="Execute SSH command on NAS")
        parser.add_argument("--ssh-test", action="store_true", help="Test SSH connection")

        args = parser.parse_args()

        # Initialize integration
        integration = NASAzureVaultIntegration(
            vault_name=args.vault_name,
            vault_url=args.vault_url,
            nas_ip=args.nas_ip,
            nas_port=args.nas_port,
        )

        # Test SSH connection
        if args.ssh_test:
            print("Testing SSH connection to NAS...")
            ssh_client = integration.get_ssh_client()
            if ssh_client:
                print("✅ Successfully connected to NAS via SSH!")
                ssh_client.close()
                return 0
            else:
                print("❌ Failed to connect to NAS via SSH")
                return 1

        # Execute SSH command
        if args.ssh:
            print(f"Executing SSH command: {args.ssh}")
            result = integration.execute_ssh_command(args.ssh)
            if result["success"]:
                print(result["output"])
                return 0
            else:
                print(f"❌ Command failed: {result.get('error', 'Unknown error')}")
                if result.get("error"):
                    print(f"Error output: {result['error']}")
                return 1

        # Test connection
        if args.test:
            print("Testing NAS connection with Azure Vault credentials...")
            if integration.connect_to_nas():
                print("✅ Successfully connected to NAS!")
                integration.disconnect()
                return 0
            else:
                print("❌ Failed to connect to NAS")
                return 1

        # Upload file/directory
        if args.upload:
            if integration.connect_to_nas():
                source = Path(args.upload)
                if source.is_file():
                    if integration.upload_file(source, args.target):
                        print(f"✅ Successfully uploaded {source.name}")
                        integration.disconnect()
                        return 0
                    else:
                        print(f"❌ Failed to upload {source.name}")
                        integration.disconnect()
                        return 1
                else:
                    results = integration.upload_directory(source, args.target)
                    print("✅ Upload complete!")
                    print(f"   Success: {results['success']}")
                    print(f"   Failed: {results['failed']}")
                    integration.disconnect()
                    return 0 if results["failed"] == 0 else 1
            else:
                print("❌ Failed to connect to NAS")
                return 1

        print("Usage:")
        print("  --test              Test NAS API connection")
        print("  --ssh-test          Test SSH connection")
        print("  --ssh COMMAND       Execute SSH command on NAS")
        print("  --upload PATH       Upload file/directory to NAS")
        print("  --target PATH       Target path on NAS (with --upload)")
        return 0

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    sys.exit(main())
