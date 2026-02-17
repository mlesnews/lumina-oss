"""
Unified Secrets Manager
Centralized secret management supporting Azure Key Vault, ProtonPass CLI, and Dashlane.

ACCOUNT INFORMATION SECRETS REMINDER: LOCATION AZURE VAULT / PROTONPASSCLI / DASHLANE.

#SECURITY #AZURE_KEY_VAULT #PROTONPASS #DASHLANE #SECRETS #JARVIS #LUMINA
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional, Any, List
from enum import Enum

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("UnifiedSecretsManager")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("UnifiedSecretsManager")


class SecretSource(Enum):
    """Secret storage source."""
    AZURE_KEY_VAULT = "azure_key_vault"
    PROTONPASS = "protonpass"
    DASHLANE = "dashlane"
    FALLBACK = "fallback"  # For development/testing only


class UnifiedSecretsManager:
    """
    Unified Secrets Manager

    Supports:
    - Azure Key Vault (primary for company secrets)
    - ProtonPass CLI (personal/secure passwords)
    - Dashlane (alternative password manager)

    ACCOUNT INFORMATION SECRETS REMINDER: LOCATION AZURE VAULT / PROTONPASSCLI / DASHLANE.
    """

    def __init__(self, project_root: Path, prefer_source: SecretSource = SecretSource.AZURE_KEY_VAULT):
        """
        Initialize Unified Secrets Manager.

        Args:
            project_root: Project root directory
            prefer_source: Preferred secret source (fallback order: Azure > ProtonPass > Dashlane)
        """
        self.project_root = Path(project_root)
        self.prefer_source = prefer_source

        # Initialize clients
        self.azure_vault_client = None
        self.protonpass_available = False
        self.dashlane_available = False

        self._initialize_clients()

    def _initialize_clients(self) -> None:
        """Initialize all available secret clients."""
        # Azure Key Vault
        try:
            from azure.identity import DefaultAzureCredential, AzureCliCredential
            from azure.keyvault.secrets import SecretClient

            vault_url = "https://jarvis-lumina.vault.azure.net/"

            # Try Azure CLI credential first (faster, if az login was done)
            # Then fallback to DefaultAzureCredential (excluding certificate auth to prevent prompts)
            try:
                credential = AzureCliCredential()
                # Test the credential quickly
                test_client = SecretClient(vault_url=vault_url, credential=credential)
                # Quick test access (won't fail if authenticated)
                self.azure_vault_client = test_client
                logger.info("✅ Azure Key Vault client initialized (using Azure CLI credential)")
            except Exception:
                # Fallback to DefaultAzureCredential but exclude certificate-based authentication
                # This prevents certificate selection prompts during startup
                try:
                    credential = DefaultAzureCredential(
                        exclude_interactive_browser_credential=False,
                        exclude_shared_token_cache_credential=False
                    )
                    self.azure_vault_client = SecretClient(vault_url=vault_url, credential=credential)
                    logger.info("✅ Azure Key Vault client initialized (using DefaultAzureCredential)")
                except Exception as default_error:
                    logger.warning(f"⚠️  DefaultAzureCredential failed: {default_error}")
                    self.azure_vault_client = None
        except ImportError:
            logger.warning("⚠️  Azure Key Vault SDK not installed")
        except Exception as e:
            logger.warning(f"⚠️  Azure Key Vault not available: {e}")

        # ProtonPass CLI - check multiple possible locations
        protonpass_paths = [
            Path(r"C:\Users\mlesn\AppData\Local\Programs\pass-cli.exe"),  # Actual install location
            Path(r"C:\Users\mlesn\AppData\Local\Programs\ProtonPass\pass-cli.exe"),  # Expected location
        ]

        self.protonpass_path = None
        try:
            for path in protonpass_paths:
                if path.exists():
                    result = subprocess.run(
                        [str(path), "--version"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        self.protonpass_path = path
                        self.protonpass_available = True
                        logger.info(f"✅ ProtonPass CLI available at {self.protonpass_path}")
                        break

            # Try PATH as fallback
            if not self.protonpass_available:
                result = subprocess.run(
                    ["protonpass", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self.protonpass_path = Path("protonpass")
                    self.protonpass_available = True
                    logger.info("✅ ProtonPass CLI available in PATH")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            logger.debug("ProtonPass CLI not available")

        # Dashlane (Web Extension Only)
        # Rationale: Dashlane is no longer a desktop app but a web extension.
        # Automation is limited to manual CSV imports/exports.
        self.dashlane_available = False
        logger.info("ℹ️  Dashlane marked as 'Web Extension Only' (Manual Tier)")

    def get_secret(self, secret_name: str, source: Optional[SecretSource] = None) -> Optional[str]:
        """
        Get secret from preferred source with fallback.

        Args:
            secret_name: Name of the secret
            source: Specific source to use (None = auto-select with fallback)

        Returns:
            Secret value or None if not found
        """
        # Determine source priority
        if source:
            sources = [source]
        else:
            sources = self._get_source_priority()

        # Try each source in priority order
        for secret_source in sources:
            try:
                secret = self._get_secret_from_source(secret_name, secret_source)
                if secret:
                    logger.debug(f"✅ Retrieved '{secret_name}' from {secret_source.value}")
                    return secret
            except Exception as e:
                logger.debug(f"⚠️  Failed to get '{secret_name}' from {secret_source.value}: {e}")
                continue

        logger.warning(f"❌ Secret '{secret_name}' not found in any source")
        return None

    def _get_source_priority(self) -> List[SecretSource]:
        """Get source priority list based on preference and availability."""
        priority = []

        # Add preferred source first
        if self.prefer_source == SecretSource.AZURE_KEY_VAULT and self.azure_vault_client:
            priority.append(SecretSource.AZURE_KEY_VAULT)
        elif self.prefer_source == SecretSource.PROTONPASS and self.protonpass_available:
            priority.append(SecretSource.PROTONPASS)
        elif self.prefer_source == SecretSource.DASHLANE and self.dashlane_available:
            priority.append(SecretSource.DASHLANE)

        # Add other available sources
        if SecretSource.AZURE_KEY_VAULT not in priority and self.azure_vault_client:
            priority.append(SecretSource.AZURE_KEY_VAULT)
        if SecretSource.PROTONPASS not in priority and self.protonpass_available:
            priority.append(SecretSource.PROTONPASS)
        if SecretSource.DASHLANE not in priority and self.dashlane_available:
            priority.append(SecretSource.DASHLANE)

        return priority if priority else [SecretSource.FALLBACK]

    def _get_secret_from_source(self, secret_name: str, source: SecretSource) -> Optional[str]:
        """Get secret from specific source."""
        if source == SecretSource.AZURE_KEY_VAULT:
            return self._get_from_azure_vault(secret_name)
        elif source == SecretSource.PROTONPASS:
            return self._get_from_protonpass(secret_name)
        elif source == SecretSource.DASHLANE:
            return self._get_from_dashlane(secret_name)
        elif source == SecretSource.FALLBACK:
            return self._get_from_fallback(secret_name)
        else:
            return None

    def _get_from_azure_vault(self, secret_name: str) -> Optional[str]:
        """Get secret from Azure Key Vault."""
        if not self.azure_vault_client:
            return None

        try:
            secret = self.azure_vault_client.get_secret(secret_name)
            return secret.value
        except Exception as e:
            logger.debug(f"Azure Key Vault error: {e}")
            return None

    def _get_from_protonpass(self, secret_name: str) -> Optional[str]:
        """Get secret from ProtonPass CLI using item view or search by username."""
        if not self.protonpass_available:
            return None

        try:
            cmd = str(self.protonpass_path) if self.protonpass_path.exists() else "protonpass"

            # Special handling for mobile phone - search by configured username
            if secret_name in ["sms-phone-number", "mobile", "phone"]:
                # Try to find user account and extract mobile phone
                mobile = self._get_mobile_from_user_account(cmd)
                if mobile:
                    return mobile

            # Standard retrieval by item title
            result = subprocess.run(
                [cmd, "item", "view", "--item-title", secret_name, "--output", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Parse JSON output
                try:
                    data = json.loads(result.stdout)
                    # Try different field names depending on item type
                    value = (data.get("password") or 
                            data.get("value") or 
                            data.get("field_value") or
                            data.get("mobile") or
                            data.get("phone"))
                    if value:
                        return str(value).strip()
                except json.JSONDecodeError:
                    # If not JSON, try to extract from text output
                    output = result.stdout.strip()
                    if output and not output.startswith("Error"):
                        return output
        except Exception as e:
            logger.debug(f"ProtonPass error: {e}")

        return None

    def _get_mobile_from_user_account(self, cmd: str) -> Optional[str]:
        """Get mobile phone number from user account in ProtonPass (searches by PROTONPASS_USERNAME)."""
        import os

        # Get username from environment variable or use None to search all accounts
        search_username = os.getenv("PROTONPASS_USERNAME", "").strip().upper()
        if not search_username:
            logger.debug("PROTONPASS_USERNAME not set - will search all ProtonPass items for mobile phone")

        try:
            # List all items to find user account
            list_result = subprocess.run(
                [cmd, "item", "list", "--output", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if list_result.returncode != 0:
                # May need authentication - check error
                error_msg = (list_result.stderr or list_result.stdout or "").lower()
                if "extra password" in error_msg or "session" in error_msg or "needs extra password" in error_msg:
                    logger.debug("ProtonPass requires authentication (extra password) - mobile phone in user account")
                    # Return None but don't log as error - this is expected if not authenticated
                return None

            try:
                items = json.loads(list_result.stdout)
                if not isinstance(items, list):
                    items = [items] if items else []

                # Find item with username matching configured username
                for item in items:
                    if not isinstance(item, dict):
                        continue

                    # Check username, name, or title fields
                    username = (item.get("username", "") or 
                               item.get("name", "") or 
                               item.get("title", "") or
                               str(item.get("itemId", "")))

                    # If PROTONPASS_USERNAME is set, match exactly; otherwise try common patterns
                    if search_username:
                        if search_username in str(username).upper():
                            # Found matching account - get full item details
                            item_id = item.get("itemId") or item.get("id")
                            if not item_id:
                                continue

                            # View the full item to get mobile phone field
                            view_result = subprocess.run(
                                [cmd, "item", "view", "--item-id", str(item_id), "--output", "json"],
                                capture_output=True,
                                text=True,
                                timeout=10
                            )

                            if view_result.returncode == 0:
                                item_data = json.loads(view_result.stdout)
                                # Look for mobile phone in various fields
                                mobile = (item_data.get("mobile") or 
                                         item_data.get("phone") or
                                         item_data.get("mobilePhone") or
                                         item_data.get("phoneNumber") or
                                         self._extract_phone_from_item(item_data))
                                if mobile:
                                    logger.info(f"✅ Found mobile phone in user ProtonPass account")
                                    return str(mobile).strip()
                    else:
                        # No username configured - check if item has a mobile phone field
                        item_id = item.get("itemId") or item.get("id")
                        if item_id:
                            view_result = subprocess.run(
                                [cmd, "item", "view", "--item-id", str(item_id), "--output", "json"],
                                capture_output=True,
                                text=True,
                                timeout=10
                            )

                            if view_result.returncode == 0:
                                item_data = json.loads(view_result.stdout)
                                mobile = (item_data.get("mobile") or 
                                         item_data.get("phone") or
                                         item_data.get("mobilePhone") or
                                         item_data.get("phoneNumber") or
                                         self._extract_phone_from_item(item_data))
                                if mobile:
                                    logger.info(f"✅ Found mobile phone in ProtonPass account")
                                    return str(mobile).strip()
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                logger.debug(f"ProtonPass parse error: {e}")
        except Exception as e:
            logger.debug(f"Error searching user account: {e}")

        return None

    def _extract_phone_from_item(self, item_data: Dict[str, Any]) -> Optional[str]:
        """Extract phone number from ProtonPass item data structure."""
        # Check in extraFields or customFields
        extra_fields = item_data.get("extraFields", [])
        if isinstance(extra_fields, list):
            for field in extra_fields:
                if isinstance(field, dict):
                    field_type = field.get("type", "").lower()
                    field_name = field.get("name", "").lower()
                    if "phone" in field_type or "mobile" in field_type or "phone" in field_name or "mobile" in field_name:
                        return field.get("value") or field.get("content")

        # Check in customFields
        custom_fields = item_data.get("customFields", [])
        if isinstance(custom_fields, list):
            for field in custom_fields:
                if isinstance(field, dict):
                    field_type = field.get("type", "").lower()
                    if "phone" in field_type or "mobile" in field_type:
                        return field.get("value") or field.get("content")

        return None

    def _get_from_dashlane(self, secret_name: str) -> Optional[str]:
        """Get secret from Dashlane CLI."""
        if not self.dashlane_available:
            return None

        try:
            # Dashlane CLI commands may vary - adjust based on actual CLI
            result = subprocess.run(
                ["dashlane", "get", secret_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            logger.debug(f"Dashlane error: {e}")

        return None

    def _get_from_fallback(self, secret_name: str) -> Optional[str]:
        """Fallback: Check local config (development only - NOT for production)."""
        logger.warning(f"⚠️  Using fallback for '{secret_name}' - NOT SECURE for production")

        # Check local secrets file (if exists for development)
        secrets_file = self.project_root / "config" / "local_secrets.json"
        if secrets_file.exists():
            try:
                with open(secrets_file, 'r') as f:
                    secrets = json.load(f)
                    return secrets.get(secret_name)
            except Exception:
                pass

        return None

    def set_secret(self, secret_name: str, secret_value: str, source: Optional[SecretSource] = None) -> bool:
        """
        Set secret in preferred source.

        Args:
            secret_name: Name of the secret
            secret_value: Secret value
            source: Specific source to use (None = use preferred source)

        Returns:
            True if successful
        """
        target_source = source or self.prefer_source

        try:
            if target_source == SecretSource.AZURE_KEY_VAULT:
                return self._set_in_azure_vault(secret_name, secret_value)
            elif target_source == SecretSource.PROTONPASS:
                return self._set_in_protonpass(secret_name, secret_value)
            elif target_source == SecretSource.DASHLANE:
                return self._set_in_dashlane(secret_name, secret_value)
            else:
                logger.error(f"❌ Cannot set secret in {target_source.value}")
                return False
        except Exception as e:
            logger.error(f"❌ Failed to set secret '{secret_name}': {e}")
            return False

    def _set_in_azure_vault(self, secret_name: str, secret_value: str) -> bool:
        """Set secret in Azure Key Vault."""
        if not self.azure_vault_client:
            return False

        try:
            self.azure_vault_client.set_secret(secret_name, secret_value)
            logger.info(f"✅ Set '{secret_name}' in Azure Key Vault")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to set in Azure Key Vault: {e}")
            return False

    def _set_in_protonpass(self, secret_name: str, secret_value: str) -> bool:
        """Set secret in ProtonPass."""
        if not self.protonpass_available:
            return False

        try:
            cmd = str(self.protonpass_path) if self.protonpass_path.exists() else "protonpass"
            # Use 'item create login' for general secrets
            result = subprocess.run(
                [cmd, "item", "create", "login", "--title", secret_name, "--password", secret_value, "--username", "admin"],
                capture_output=True,
                text=True,
                timeout=15
            )
            if result.returncode == 0:
                logger.info(f"✅ Set '{secret_name}' in ProtonPass")
                return True
            else:
                # If item already exists, this might fail - ideally we'd update it
                # For now, log the error
                logger.error(f"❌ Failed to set in ProtonPass: {result.stderr.strip()}")
        except Exception as e:
            logger.error(f"❌ Failed to set in ProtonPass: {e}")

        return False

    def _set_in_dashlane(self, secret_name: str, secret_value: str) -> bool:
        """Set secret in Dashlane."""
        if not self.dashlane_available:
            return False

        try:
            # Dashlane set command (adjust based on actual CLI)
            result = subprocess.run(
                ["dashlane", "set", secret_name, secret_value],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                logger.info(f"✅ Set '{secret_name}' in Dashlane")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to set in Dashlane: {e}")

        return False

    def list_secrets(self, source: Optional[SecretSource] = None) -> Dict[str, List[str]]:
        """
        List all secrets from available sources.

        Args:
            source: Specific source to list (None = all available)

        Returns:
            Dictionary mapping source names to lists of secret names
        """
        results = {}

        sources = [source] if source else [SecretSource.AZURE_KEY_VAULT, SecretSource.PROTONPASS, SecretSource.DASHLANE]

        for secret_source in sources:
            try:
                secrets = self._list_from_source(secret_source)
                if secrets:
                    results[secret_source.value] = secrets
            except Exception as e:
                logger.debug(f"Failed to list from {secret_source.value}: {e}")

        return results

    def _list_from_source(self, source: SecretSource) -> List[str]:
        """List secrets from specific source."""
        if source == SecretSource.AZURE_KEY_VAULT and self.azure_vault_client:
            try:
                secrets = list(self.azure_vault_client.list_properties_of_secrets())
                return [s.name for s in secrets]
            except Exception:
                return []
        elif source == SecretSource.PROTONPASS and self.protonpass_available:
            try:
                cmd = str(self.protonpass_path) if self.protonpass_path.exists() else "protonpass"
                result = subprocess.run(
                    [cmd, "item", "list", "--output", "json"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    entries = json.loads(result.stdout)
                    # Extract item titles/names from the list
                    return [e.get("name", "") or e.get("title", "") for e in entries if isinstance(e, dict) and (e.get("name") or e.get("title"))]
            except Exception as e:
                logger.debug(f"ProtonPass list error: {e}")
                pass
        elif source == SecretSource.DASHLANE and self.dashlane_available:
            try:
                result = subprocess.run(
                    ["dashlane", "list"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    # Parse Dashlane output (adjust based on actual format)
                    return [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
            except Exception:
                pass

        return []

    def get_status(self) -> Dict[str, Any]:
        """Get status of all secret sources."""
        return {
            "azure_key_vault": {
                "available": self.azure_vault_client is not None,
                "vault_url": "https://jarvis-lumina.vault.azure.net/" if self.azure_vault_client else None
            },
            "protonpass": {
                "available": self.protonpass_available
            },
            "dashlane": {
                "available": self.dashlane_available
            },
            "preferred_source": self.prefer_source.value,
            "reminder": "ACCOUNT INFORMATION SECRETS REMINDER: LOCATION AZURE VAULT / PROTONPASSCLI / DASHLANE."
        }


def main():
    try:
        """Test Unified Secrets Manager."""
        import argparse

        parser = argparse.ArgumentParser(description="Unified Secrets Manager")
        parser.add_argument("--project-root", type=Path, default=Path(__file__).parent.parent.parent)
        parser.add_argument("--get", type=str, help="Get secret by name")
        parser.add_argument("--set", nargs=2, metavar=("NAME", "VALUE"), help="Set secret")
        parser.add_argument("--list", action="store_true", help="List all secrets")
        parser.add_argument("--status", action="store_true", help="Show status")
        parser.add_argument("--source", type=str, choices=["azure_key_vault", "protonpass", "dashlane"],
                           help="Specific source to use")

        args = parser.parse_args()

        source = SecretSource(args.source) if args.source else None
        manager = UnifiedSecretsManager(args.project_root)

        if args.status:
            status = manager.get_status()
            print(json.dumps(status, indent=2))
        elif args.get:
            secret = manager.get_secret(args.get, source)
            if secret:
                print(f"✅ Secret '{args.get}': {secret[:10]}...{secret[-4:] if len(secret) > 14 else '***'}")
            else:
                print(f"❌ Secret '{args.get}' not found")
        elif args.set:
            name, value = args.set
            if manager.set_secret(name, value, source):
                print(f"✅ Secret '{name}' set successfully")
            else:
                print(f"❌ Failed to set secret '{name}'")
        elif args.list:
            secrets = manager.list_secrets(source)
            for source_name, secret_list in secrets.items():
                print(f"\n{source_name}:")
                for secret_name in secret_list:
                    print(f"  - {secret_name}")
        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()