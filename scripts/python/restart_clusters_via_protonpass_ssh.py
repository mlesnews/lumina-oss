#!/usr/bin/env python3
"""
Restart Clusters via ProtonPass + SSH + Docker Terminal
1. Authenticate ProtonPass CLI
2. Get SSH credentials for KAIJU_NO_8 from ProtonPass
3. SSH to KAIJU_NO_8 and restart containers via Docker terminal

Tags: #PROTONPASS #SSH #DOCKER #CLUSTER #IRON_LEGION @JARVIS @LUMINA @DOIT
"""
import sys
import json
import time
import subprocess
import paramiko
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("RestartClustersProtonPassSSH")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("RestartClustersProtonPassSSH")

try:
    from unified_secrets_manager import UnifiedSecretsManager
    from azure.keyvault.secrets import SecretClient
    from azure.identity import AzureCliCredential, DefaultAzureCredential
except ImportError:
    UnifiedSecretsManager = None
    SecretClient = None
    AzureCliCredential = None
    DefaultAzureCredential = None


class ClusterRestarterViaProtonPass:
    """Restart clusters using ProtonPass credentials + SSH + Docker"""

    def __init__(self):
        self.kaiju_ip = "<NAS_IP>"
        self.ssh_port = 22
        self.ssh_client = None
        self.protonpass_path = None
        self.ssh_credentials = None
        self.ssh_key_path = Path.home() / ".ssh" / "id_rsa_kaiju"

        # Containers to restart (will be auto-detected from actual container names)
        self.containers = [
            "iron-legion-router",      # Port 3000
        ]
        # Mark II, III, VI, VII will be auto-detected

        # Find ProtonPass CLI
        self._find_protonpass_cli()

    def _find_protonpass_cli(self):
        """Find ProtonPass CLI executable"""
        import os

        # Check environment variable first
        protonpass_path = os.getenv("PROTONPASS_CLI_PATH")
        if protonpass_path and Path(protonpass_path).exists():
            self.protonpass_path = protonpass_path
            logger.info(f"✅ Using ProtonPass CLI from PROTONPASS_CLI_PATH: {protonpass_path}")
            return

        # Try common locations
        possible_paths = [
            Path(r"C:\Users\mlesn\AppData\Local\Programs\ProtonPass\pass-cli.exe"),
            Path(r"C:\Users\mlesn\AppData\Local\Programs\pass-cli.exe"),
            Path(r"C:\Program Files\ProtonPass\pass-cli.exe"),
            Path(os.path.expanduser("~/.protonpass/pass-cli.exe")),
            Path(os.path.expanduser("~/AppData/Local/ProtonPass/pass-cli.exe")),
            Path(os.path.expanduser("~/AppData/Roaming/ProtonPass/pass-cli.exe")),
        ]

        for path in possible_paths:
            if path.exists():
                self.protonpass_path = str(path)
                logger.info(f"✅ Found ProtonPass CLI at: {self.protonpass_path}")
                return

        # Try as command in PATH
        for cmd in ["protonpass", "ppass", "pass-cli", "pass"]:
            try:
                result = subprocess.run(
                    [cmd, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    self.protonpass_path = cmd
                    logger.info(f"✅ Found ProtonPass CLI in PATH: {cmd}")
                    return
            except:
                continue

        logger.error("❌ ProtonPass CLI not found")
        logger.info("💡 Please set PROTONPASS_CLI_PATH environment variable")

    def authenticate_protonpass(self) -> bool:
        """Check if ProtonPass CLI is authenticated"""
        if not self.protonpass_path:
            logger.error("❌ ProtonPass CLI not available")
            return False

        logger.info("🔐 Checking ProtonPass CLI authentication...")

        try:
            # Check if already authenticated by trying to list items
            result = subprocess.run(
                [self.protonpass_path, "item", "list", "--output", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                logger.info("✅ ProtonPass CLI already authenticated")
                return True

            # Check error message
            error_msg = result.stderr.lower() if result.stderr else ""
            if "not logged in" in error_msg or "session" in error_msg:
                logger.warning("⚠️  ProtonPass CLI requires authentication")
                logger.info("")
                logger.info("💡 To authenticate ProtonPass CLI, run:")
                logger.info(f'   & "{self.protonpass_path}" login --interactive')
                logger.info("")
                logger.info("   Or use the auto-login script:")
                logger.info("   python scripts/python/protonpass_auto_login.py")
                logger.info("")
                return False

            logger.warning(f"⚠️  Unexpected ProtonPass status: {result.stderr}")
            return False

        except subprocess.TimeoutExpired:
            logger.error("❌ ProtonPass CLI command timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Error checking ProtonPass authentication: {e}")
            return False

    def get_ssh_credentials_from_azure_vault(self) -> Optional[Dict[str, str]]:
        """Get SSH credentials from Azure Key Vault as fallback"""
        if not AzureCliCredential:
            return None

        logger.info(f"🔍 Checking Azure Key Vault for SSH credentials...")

        try:
            import os
            # Use Windows account username for SSH key authentication
            windows_username = os.getenv("USERNAME") or os.getenv("USER")
            if windows_username:
                logger.info(f"   ✅ Using Windows account: {windows_username}")

            vault_url = "https://jarvis-lumina.vault.azure.net/"
            credential = AzureCliCredential()
            client = SecretClient(vault_url=vault_url, credential=credential)

            # Prefer Windows username for SSH key auth, fallback to Azure Vault
            username = windows_username.lower() if windows_username else None
            password = None

            # Only get username from Vault if Windows username not available
            if not username:
                for secret_name in ["kaiju-ssh-username", "kaiju-username", "nas-username"]:
                    try:
                        username = client.get_secret(secret_name).value
                        logger.info(f"   ✅ Found username in: {secret_name}")
                        break
                    except:
                        continue

            # Get password from Vault (for fallback if key auth fails)
            for secret_name in ["kaiju-ssh-password", "kaiju-password", "nas-password"]:
                try:
                    password = client.get_secret(secret_name).value
                    logger.info(f"   ✅ Found password in: {secret_name}")
                    break
                except:
                    continue

            if username:
                creds = {"username": username}
                if password:
                    creds["password"] = password
                logger.info("✅ Retrieved SSH credentials from Azure Key Vault")
                return creds

            return None
        except Exception as e:
            logger.debug(f"Azure Vault check failed: {e}")
            return None

    def get_ssh_credentials_from_protonpass(self) -> Optional[Dict[str, str]]:
        """Get SSH credentials for KAIJU_NO_8 from ProtonPass"""
        if not self.protonpass_path:
            return None

        logger.info(f"🔍 Searching ProtonPass for SSH credentials (KAIJU_NO_8 / {self.kaiju_ip})...")

        try:
            # List all items
            result = subprocess.run(
                [self.protonpass_path, "item", "list", "--output", "json"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                logger.error(f"❌ Failed to list ProtonPass items: {result.stderr}")
                return None

            items = json.loads(result.stdout) if result.stdout.strip() else []

            # Search for KAIJU/SSH related items
            search_terms = ["kaiju", "<NAS_IP>", "ssh", "nas", "synology"]
            matching_items = []

            for item in items:
                title = item.get("title", "").lower()
                username = item.get("username", "").lower()
                urls = [url.get("url", "").lower() if isinstance(url, dict) else str(url).lower() 
                       for url in item.get("urls", [])]
                all_text = f"{title} {username} {' '.join(urls)}".lower()

                if any(term in all_text for term in search_terms):
                    matching_items.append(item)
                    logger.info(f"   ✅ Found potential match: {item.get('title', 'Untitled')}")

            if not matching_items:
                logger.warning("⚠️  No SSH credentials found in ProtonPass")
                logger.info("   💡 Searching for any NAS/Synology entries...")
                # Broader search
                for item in items:
                    title = item.get("title", "").lower()
                    if "nas" in title or "synology" in title or "server" in title:
                        matching_items.append(item)
                        logger.info(f"   ✅ Found NAS entry: {item.get('title', 'Untitled')}")

            if not matching_items:
                return None

            # Get details of first matching item
            item = matching_items[0]
            item_id = item.get("itemId") or item.get("id")

            if not item_id:
                logger.warning("⚠️  Item has no ID")
                return None

            logger.info(f"📥 Getting details for: {item.get('title', 'Untitled')}")

            # Get full item details
            result = subprocess.run(
                [self.protonpass_path, "item", "read", item_id, "--output", "json"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                logger.error(f"❌ Failed to read item: {result.stderr}")
                return None

            item_data = json.loads(result.stdout) if result.stdout.strip() else {}

            # Extract credentials
            username = item_data.get("username") or item_data.get("login") or ""
            password = item_data.get("password") or ""

            # Try alternative paths
            if not username or not password:
                content = item_data.get("content", {})
                if isinstance(content, dict):
                    username = username or content.get("username", "")
                    password = password or content.get("password", "")
                elif isinstance(content, list):
                    for field in content:
                        if isinstance(field, dict):
                            field_name = field.get("fieldName", "").lower()
                            if field_name == "username" or field_name == "login":
                                username = field.get("value", "")
                            elif field_name == "password":
                                password = field.get("value", "")

            if not username or not password:
                logger.error("❌ Could not extract username or password from item")
                return None

            logger.info(f"✅ Retrieved SSH credentials from ProtonPass")
            logger.info(f"   Username: {username}")
            logger.info(f"   Password: [REDACTED]")

            return {
                "username": username,
                "password": password
            }

        except Exception as e:
            logger.error(f"❌ Error getting SSH credentials: {e}")
            import traceback
            traceback.print_exc()
            return None

    def connect_ssh(self) -> bool:
        """Connect to KAIJU_NO_8 via SSH (prefer key-based auth)"""
        if not self.ssh_credentials:
            self.ssh_credentials = self.get_ssh_credentials_from_protonpass()

        if not self.ssh_credentials:
            logger.error("❌ No SSH credentials available")
            return False

        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Try key-based authentication first
            if self.ssh_key_path.exists():
                try:
                    logger.info("🔑 Attempting SSH key authentication...")
                    private_key = paramiko.RSAKey.from_private_key_file(str(self.ssh_key_path))
                    self.ssh_client.connect(
                        hostname=self.kaiju_ip,
                        port=self.ssh_port,
                        username=self.ssh_credentials["username"],
                        pkey=private_key,
                        timeout=10
                    )
                    logger.info("✅ SSH connection established via key authentication")
                    return True
                except paramiko.AuthenticationException:
                    logger.info("   ⚠️  Key authentication failed, trying password...")
                except Exception as e:
                    logger.debug(f"   Key auth error: {e}, trying password...")

            # Fallback to password authentication
            logger.info("🔐 Using password authentication...")
            self.ssh_client.connect(
                hostname=self.kaiju_ip,
                port=self.ssh_port,
                username=self.ssh_credentials["username"],
                password=self.ssh_credentials["password"],
                timeout=10
            )
            logger.info("✅ SSH connection established via password authentication")
            return True
        except paramiko.AuthenticationException:
            logger.error("❌ SSH authentication failed (both key and password)")
            return False
        except Exception as e:
            logger.error(f"❌ SSH connection error: {e}")
            return False

    def execute_docker_command(self, command: str) -> Dict[str, Any]:
        """Execute Docker command via SSH"""
        if not self.ssh_client:
            return {"success": False, "error": "Not connected"}

        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command, timeout=30)
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            exit_status = stdout.channel.recv_exit_status()

            return {
                "success": exit_status == 0,
                "output": output,
                "error": error if error else None,
                "exit_status": exit_status
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def restart_container(self, container_name: str) -> Dict[str, Any]:
        """Restart a container using Docker terminal"""
        logger.info(f"🔄 Restarting {container_name}...")

        # Check if container exists
        check_cmd = f"docker ps -a --filter name={container_name} --format '{{{{.Names}}}}'"
        check_result = self.execute_docker_command(check_cmd)

        if not check_result["success"] or container_name not in check_result["output"]:
            logger.warning(f"   ⚠️  Container {container_name} not found")
            return {"success": False, "error": "Container not found"}

        # Restart container
        restart_cmd = f"docker restart {container_name}"
        result = self.execute_docker_command(restart_cmd)

        if result["success"]:
            logger.info(f"   ✅ {container_name} restarted")
            return {"success": True, "message": "Restarted"}
        else:
            logger.warning(f"   ⚠️  {container_name}: {result.get('error', 'Unknown error')}")
            return result

    def restart_all_containers(self) -> Dict[str, Any]:
        """Restart all Iron Legion containers"""
        logger.info("🚀 Restarting Iron Legion containers via Docker terminal...")
        logger.info("")

        results = {}
        for container_name in self.containers:
            result = self.restart_container(container_name)
            results[container_name] = result
            time.sleep(1)  # Small delay between restarts

        return {"success": True, "results": results}

    def check_cluster_status(self) -> Dict[str, Any]:
        """Check current cluster status"""
        logger.info("🔍 Checking Iron Legion cluster status...")

        status = {
            "main_cluster": False,
            "models": {},
            "timestamp": datetime.now().isoformat()
        }

        # Check main cluster
        try:
            response = requests.get(f"http://{self.kaiju_ip}:3000/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Iron Legion main cluster (port 3000) is online")
                status["main_cluster"] = True
            else:
                logger.warning(f"⚠️  Main cluster error: {response.status_code}")
        except requests.exceptions.ConnectionError:
            logger.warning("⚠️  Main cluster (port 3000) is offline")
        except Exception as e:
            logger.error(f"❌ Error checking main cluster: {e}")

        # Check individual models
        for port in range(3001, 3008):
            model_name = f"Mark {port - 3000}"
            try:
                response = requests.get(f"http://{self.kaiju_ip}:{port}/health", timeout=3)
                if response.status_code == 200:
                    logger.info(f"✅ {model_name} (port {port}) is online")
                    status["models"][model_name] = True
                else:
                    logger.warning(f"⚠️  {model_name} (port {port}) error: {response.status_code}")
                    status["models"][model_name] = False
            except requests.exceptions.ConnectionError:
                logger.warning(f"⚠️  {model_name} (port {port}) is offline")
                status["models"][model_name] = False
            except Exception as e:
                logger.error(f"❌ Error checking {model_name}: {e}")
                status["models"][model_name] = False

        return status

    def restart_clusters(self) -> Dict[str, Any]:
        """Main routine: authenticate ProtonPass, get credentials, restart clusters"""
        logger.info("=" * 70)
        logger.info("🚀 RESTART CLUSTERS VIA PROTONPASS + SSH + DOCKER")
        logger.info("=" * 70)
        logger.info("")

        # Step 1: Check ProtonPass authentication
        logger.info("STEP 1: Checking ProtonPass CLI authentication...")
        auth_status = self.authenticate_protonpass()
        if not auth_status:
            logger.warning("⚠️  ProtonPass authentication check failed, but attempting to retrieve credentials anyway...")
            logger.info("   (Credentials may be cached or available)")
        logger.info("")

        # Step 2: Get SSH credentials (try ProtonPass first, then Azure Vault fallback)
        logger.info("STEP 2: Getting SSH credentials...")
        self.ssh_credentials = self.get_ssh_credentials_from_protonpass()

        # Fallback to Azure Key Vault if ProtonPass fails
        if not self.ssh_credentials:
            logger.info("   ⚠️  ProtonPass unavailable, trying Azure Key Vault...")
            self.ssh_credentials = self.get_ssh_credentials_from_azure_vault()

        if not self.ssh_credentials:
            logger.error("❌ Failed to get SSH credentials from ProtonPass or Azure Vault")
            logger.info("")
            logger.info("💡 Options:")
            logger.info("   1. Authenticate ProtonPass CLI:")
            logger.info(f'      & "{self.protonpass_path}" login --interactive')
            logger.info("   2. Store SSH credentials in Azure Key Vault:")
            logger.info("      - kaiju-ssh-username")
            logger.info("      - kaiju-ssh-password")
            logger.info("")
            return {"success": False, "error": "No SSH credentials found"}
        logger.info("")

        # Step 3: Check initial status
        initial_status = self.check_cluster_status()
        logger.info("")

        # If all online, skip
        if initial_status["main_cluster"] and all(initial_status["models"].values()):
            logger.info("✅ All services are already online!")
            return {"success": True, "status": initial_status, "action": "none"}

        # Step 4: Connect via SSH
        logger.info("STEP 3: Connecting to KAIJU_NO_8 via SSH...")
        if not self.connect_ssh():
            logger.error("❌ Failed to connect via SSH")
            return {"success": False, "error": "SSH connection failed", "status": initial_status}
        logger.info("")

        # Step 5: List containers and find Iron Legion containers
        logger.info("STEP 4: Listing Docker containers...")
        list_result = self.execute_docker_command("docker ps -a --format '{{.Names}}'")
        if list_result["success"]:
            containers = [c.strip() for c in list_result["output"].split('\n') if c.strip()]
            logger.info(f"📋 Found {len(containers)} containers")

            # Find all Iron Legion related containers
            iron_legion_containers = [c for c in containers if 'iron' in c.lower() or 'legion' in c.lower()]
            if iron_legion_containers:
                logger.info(f"   🔍 Iron Legion containers found: {', '.join(iron_legion_containers)}")
                # Update container list to match actual names
                actual_containers = []

                # Always include router
                if "iron-legion-router" in containers:
                    actual_containers.append("iron-legion-router")

                # Find Mark II, III, VI, VII containers (they have different naming)
                mark_containers = {
                    "mark-2": ["mark-ii", "mark-2"],
                    "mark-3": ["mark-iii", "mark-3"],
                    "mark-6": ["mark-vi", "mark-6"],
                    "mark-7": ["mark-vii", "mark-7"]
                }

                for mark_num, patterns in mark_containers.items():
                    found = False
                    for pattern in patterns:
                        matches = [c for c in iron_legion_containers if pattern in c.lower()]
                        if matches:
                            # Prefer ollama containers, but take any
                            ollama_match = [c for c in matches if 'ollama' in c.lower()]
                            if ollama_match:
                                actual_containers.append(ollama_match[0])
                            else:
                                actual_containers.append(matches[0])
                            found = True
                            break
                    if not found:
                        logger.warning(f"   ⚠️  Mark {mark_num} container not found")

                if actual_containers:
                    logger.info(f"   ✅ Will restart: {', '.join(actual_containers)}")
                    self.containers = list(set(actual_containers))  # Remove duplicates
        logger.info("")

        # Step 6: Restart containers
        logger.info("STEP 5: Restarting containers...")
        restart_result = self.restart_all_containers()
        logger.info("")

        # Close SSH connection
        if self.ssh_client:
            self.ssh_client.close()
            logger.info("🔌 SSH connection closed")

        # Wait for services to initialize
        logger.info("⏳ Waiting 25 seconds for services to initialize...")
        time.sleep(25)

        # Check final status
        final_status = self.check_cluster_status()
        logger.info("")

        return {
            "success": True,
            "initial_status": initial_status,
            "final_status": final_status,
            "restart_results": restart_result.get("results", {}),
            "containers_found": list_result.get("output", "").split('\n') if list_result.get("success") else []
        }


def main():
    try:
        """Main execution"""
        logger.info("=" * 70)
        logger.info("🚀 RESTART CLUSTERS VIA PROTONPASS + SSH + DOCKER")
        logger.info("=" * 70)
        logger.info("")

        restarter = ClusterRestarterViaProtonPass()
        result = restarter.restart_clusters()

        logger.info("=" * 70)
        logger.info("📊 SUMMARY")
        logger.info("=" * 70)
        logger.info("")

        final_status = result.get("final_status") or result.get("status", {})

        if final_status.get("main_cluster"):
            logger.info("✅ Main cluster router: ONLINE")
        else:
            logger.error("❌ Main cluster router: OFFLINE")

        models_online = sum(1 for v in final_status.get("models", {}).values() if v)
        models_total = len(final_status.get("models", {}))
        logger.info(f"📊 Models: {models_online}/{models_total} online")

        if models_online < models_total:
            offline = [name for name, status in final_status.get("models", {}).items() if not status]
            logger.warning(f"⚠️  Offline models: {', '.join(offline)}")

        logger.info("")

        # Save report
        report_file = project_root / "data" / "syphon_results" / f"restart_clusters_protonpass_ssh_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(json.dumps(result, indent=2))
        logger.info(f"📄 Report saved to: {report_file}")

        return 0 if (final_status.get("main_cluster") and models_online == models_total) else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":

    sys.exit(main())