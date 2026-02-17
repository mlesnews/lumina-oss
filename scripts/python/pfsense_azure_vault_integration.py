#!/usr/bin/env python3
"""
pfSense Access with Azure Vault Credentials
Retrieves pfSense credentials from Azure Key Vault and provides SSH and web portal access
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
import subprocess
import logging
import json
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential
    KEY_VAULT_AVAILABLE = True
except ImportError:
    KEY_VAULT_AVAILABLE = False
    SecretClient = None  # Type hint fallback
    print("WARNING: Azure Key Vault SDK not installed")
    print("Install with: pip install azure-keyvault-secrets azure-identity")

try:
    import paramiko
    SSH_AVAILABLE = True
except ImportError:
    SSH_AVAILABLE = False
    print("WARNING: paramiko not installed. Install with: pip install paramiko")

try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("WARNING: requests not installed. Install with: pip install requests")

try:
    from lumina_logger import get_logger
    logger = get_logger("PFSenseAzureVaultIntegration")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("PFSenseAzureVaultIntegration")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class PFSenseAzureVaultIntegration:
    """Access pfSense using credentials from Azure Key Vault"""

    def __init__(
        self,
        vault_name: Optional[str] = None,
        vault_url: Optional[str] = None,
        pfsense_ip: str = "<NAS_IP>",
        pfsense_web_port: int = 443,
        pfsense_ssh_port: int = 22
    ):
        """
        Initialize pfSense Azure Vault integration

        Args:
            vault_name: Azure Key Vault name (e.g., "jarvis-lumina")
            vault_url: Full Azure Key Vault URL (overrides vault_name)
            pfsense_ip: pfSense IP address
            pfsense_web_port: pfSense web portal port (default: 443)
            pfsense_ssh_port: pfSense SSH port (default: 22)
        """
        self.pfsense_ip = pfsense_ip
        self.pfsense_web_port = pfsense_web_port
        self.pfsense_ssh_port = pfsense_ssh_port
        self.vault_client: Optional[SecretClient] = None
        self.web_session: Optional[requests.Session] = None

        # Determine vault URL
        if vault_url:
            self.vault_url = vault_url
        elif vault_name:
            self.vault_url = f"https://{vault_name}.vault.azure.net/"
        else:
            # Try environment variable or default
            self.vault_url = os.getenv(
                "AZURE_KEY_VAULT_URL",
                os.getenv("AZURE_KEY_VAULT_NAME", "jarvis-lumina")
            )
            if not self.vault_url.startswith("https://"):
                self.vault_url = f"https://{self.vault_url}.vault.azure.net/"

        logger.info(f"Initialized with Vault URL: {self.vault_url}")
        logger.info(f"pfSense: {pfsense_ip}:{pfsense_web_port} (web), {pfsense_ssh_port} (SSH)")

    def get_key_vault_client(self) -> Optional[SecretClient]:
        """Get Azure Key Vault client"""
        if not KEY_VAULT_AVAILABLE:
            logger.error("Azure Key Vault SDK not available")
            return None

        if self.vault_client:
            return self.vault_client

        try:
            credential = DefaultAzureCredential(

                                exclude_interactive_browser_credential=False,

                                exclude_shared_token_cache_credential=False

                            )
            self.vault_client = SecretClient(
                vault_url=self.vault_url,
                credential=credential
            )
            logger.info("Azure Key Vault client initialized")
            return self.vault_client
        except Exception as e:
            logger.error(f"Failed to initialize Key Vault client: {e}")
            return None

    def get_pfsense_credentials(self) -> Optional[Dict[str, str]]:
        """
        Retrieve pfSense credentials from Azure Key Vault

        Returns:
            Dictionary with 'username' and 'password', or None if failed
        """
        if not KEY_VAULT_AVAILABLE:
            logger.error("Azure Key Vault SDK not available")
            return None

        client = self.get_key_vault_client()
        if not client:
            return None

        try:
            # Try multiple secret name patterns
            secret_patterns = [
                f"pfsense-username-{self.pfsense_ip.replace('.', '-')}",
                "pfsense-username",
                f"pfsense-password-{self.pfsense_ip.replace('.', '-')}",
                "pfsense-password"
            ]

            username = None
            password = None

            # Try to get username
            for pattern in [f"pfsense-username-{self.pfsense_ip.replace('.', '-')}", "pfsense-username"]:
                try:
                    secret = client.get_secret(pattern)
                    username = secret.value
                    logger.info(f"Retrieved username from: {pattern}")
                    break
                except Exception:
                    continue

            # Default username if not found
            if not username:
                username = "admin"
                logger.info("Using default username: admin")

            # Try to get password
            for pattern in [f"pfsense-password-{self.pfsense_ip.replace('.', '-')}", "pfsense-password"]:
                try:
                    secret = client.get_secret(pattern)
                    password = secret.value
                    logger.info(f"Retrieved password from: {pattern}")
                    break
                except Exception:
                    continue

            if not password:
                logger.error("Could not retrieve pfSense password from Key Vault")
                return None

            return {
                "username": username,
                "password": password
            }
        except Exception as e:
            logger.error(f"Failed to retrieve pfSense credentials: {e}")
            return None

    def test_web_portal_connection(self) -> bool:
        """Test connection to pfSense web portal"""
        if not REQUESTS_AVAILABLE:
            logger.error("requests library not available")
            return False

        try:
            url = f"https://{self.pfsense_ip}:{self.pfsense_web_port}"
            response = requests.get(url, verify=False, timeout=10)
            logger.info(f"Web portal accessible: {url} (Status: {response.status_code})")
            return response.status_code in [200, 401, 403]  # 401/403 means server is responding
        except Exception as e:
            logger.error(f"Web portal connection failed: {e}")
            return False

    def login_web_portal(self) -> bool:
        """Login to pfSense web portal"""
        if not REQUESTS_AVAILABLE:
            logger.error("requests library not available")
            return False

        credentials = self.get_pfsense_credentials()
        if not credentials:
            logger.error("Could not retrieve pfSense credentials from Azure Vault")
            return False

        try:
            self.web_session = requests.Session()
            url = f"https://{self.pfsense_ip}:{self.pfsense_web_port}"

            # Get login page first
            response = self.web_session.get(url, verify=False, timeout=10)

            # pfSense uses form-based authentication
            # Extract CSRF token if present
            login_data = {
                "usernamefld": credentials["username"],
                "passwordfld": credentials["password"],
                "login": "Sign In"
            }

            # Try to login
            login_url = f"{url}/index.php"
            response = self.web_session.post(
                login_url,
                data=login_data,
                verify=False,
                timeout=10,
                allow_redirects=True
            )

            # Check if login was successful (redirect or dashboard)
            if response.status_code == 200 and "dashboard" in response.url.lower():
                logger.info("Successfully logged in to pfSense web portal")
                return True
            elif response.status_code == 200:
                # Check if we're redirected to dashboard
                if "index.php" in response.url or response.url == url:
                    logger.info("Successfully logged in to pfSense web portal")
                    return True
                else:
                    logger.warning(f"Login response unclear: {response.url}")
                    return False
            else:
                logger.error(f"Login failed with status: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Web portal login error: {e}")
            return False

    def get_ssh_client(self) -> Optional[Any]:
        """Get SSH client for pfSense operations"""
        if not SSH_AVAILABLE:
            logger.error("paramiko not available. Install with: pip install paramiko")
            return None

        credentials = self.get_pfsense_credentials()
        if not credentials:
            logger.error("Could not retrieve pfSense credentials from Azure Vault")
            return None

        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(
                hostname=self.pfsense_ip,
                port=self.pfsense_ssh_port,
                username=credentials["username"],
                password=credentials["password"],
                timeout=30
            )
            logger.info("SSH connection established to pfSense")
            return ssh_client
        except Exception as e:
            logger.error(f"Failed to establish SSH connection: {e}")
            return None

    def execute_ssh_command(self, command: str) -> Dict[str, Any]:
        """Execute command on pfSense via SSH"""
        ssh_client = self.get_ssh_client()
        if not ssh_client:
            return {"success": False, "error": "SSH connection failed"}

        try:
            stdin, stdout, stderr = ssh_client.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')

            result = {
                "success": exit_status == 0,
                "exit_status": exit_status,
                "output": output,
                "error": error if error else None
            }

            # Publish to Lumina if available
            self._publish_to_lumina("pfsense_ssh_command", {
                "command": command,
                "result": result
            })

            return result
        except Exception as e:
            logger.error(f"Failed to execute SSH command: {e}")
            return {"success": False, "error": str(e)}
        finally:
            ssh_client.close()

    def _publish_to_lumina(self, event_type: str, data: Dict[str, Any]) -> None:
        """Publish pfSense operations to Lumina API"""
        if not REQUESTS_AVAILABLE:
            return

        try:
            # Try to publish to R5 system
            lumina_endpoint = os.getenv("LUMINA_API_ENDPOINT", "http://localhost:8000")
            payload = {
                "event_type": event_type,
                "source": "pfsense_azure_vault",
                "data": data
            }

            response = requests.post(
                f"{lumina_endpoint}/r5/events",
                json=payload,
                timeout=5
            )

            if response.status_code == 200:
                logger.debug(f"Published to Lumina: {event_type}")
        except Exception as e:
            logger.debug(f"Could not publish to Lumina (may not be running): {e}")


def main():
    """Main function for testing"""
    import argparse

    parser = argparse.ArgumentParser(description="Access pfSense with Azure Vault credentials")
    parser.add_argument("--vault-name", help="Azure Key Vault name")
    parser.add_argument("--vault-url", help="Azure Key Vault URL")
    parser.add_argument("--pfsense-ip", default="<NAS_IP>", help="pfSense IP address")
    parser.add_argument("--pfsense-web-port", type=int, default=443, help="pfSense web portal port")
    parser.add_argument("--pfsense-ssh-port", type=int, default=22, help="pfSense SSH port")
    parser.add_argument("--test", action="store_true", help="Test web portal connection only")
    parser.add_argument("--test-web", action="store_true", help="Test web portal login")
    parser.add_argument("--ssh", help="Execute SSH command on pfSense")
    parser.add_argument("--ssh-test", action="store_true", help="Test SSH connection")

    args = parser.parse_args()

    # Initialize integration
    integration = PFSenseAzureVaultIntegration(
        vault_name=args.vault_name,
        vault_url=args.vault_url,
        pfsense_ip=args.pfsense_ip,
        pfsense_web_port=args.pfsense_web_port,
        pfsense_ssh_port=args.pfsense_ssh_port
    )

    # Test SSH connection
    if args.ssh_test:
        print("Testing SSH connection to pfSense...")
        ssh_client = integration.get_ssh_client()
        if ssh_client:
            print("✅ Successfully connected to pfSense via SSH!")
            ssh_client.close()
            return 0
        else:
            print("❌ Failed to connect to pfSense via SSH")
            print("\nTroubleshooting:")
            print("  1. Verify pfSense password in Key Vault:")
            print(f"     az keyvault secret show --vault-name jarvis-lumina --name pfsense-password")
            print("  2. Verify SSH is enabled on pfSense")
            print(f"  3. Test network connectivity: Test-Connection {args.pfsense_ip}")
            return 1

    # Test web portal connection
    if args.test:
        print("Testing web portal connection to pfSense...")
        if integration.test_web_portal_connection():
            print("✅ Web portal is accessible!")
            return 0
        else:
            print("❌ Web portal connection failed")
            return 1

    # Test web portal login
    if args.test_web:
        print("Testing web portal login to pfSense...")
        if integration.login_web_portal():
            print("✅ Successfully logged in to pfSense web portal!")
            return 0
        else:
            print("❌ Web portal login failed")
            print("\nTroubleshooting:")
            print("  1. Verify pfSense password in Key Vault:")
            print(f"     az keyvault secret show --vault-name jarvis-lumina --name pfsense-password")
            print("  2. Verify web portal is accessible:")
            print(f"     Test-Connection {args.pfsense_ip} -Port {args.pfsense_web_port}")
            return 1

    # Execute SSH command
    if args.ssh:
        print(f"Executing SSH command on pfSense: {args.ssh}")
        result = integration.execute_ssh_command(args.ssh)
        if result["success"]:
            print("✅ Command executed successfully!")
            print("\nOutput:")
            print(result["output"])
            return 0
        else:
            print("❌ Command failed!")
            if result.get("error"):
                print(f"Error: {result['error']}")
            return 1

    # Default: show help
    print("pfSense Azure Vault Integration")
    print("\nUsage:")
    print("  --test              Test web portal connection")
    print("  --test-web          Test web portal login")
    print("  --ssh-test          Test SSH connection")
    print("  --ssh COMMAND       Execute SSH command on pfSense")
    print("\nExample:")
    print("  python pfsense_azure_vault_integration.py --ssh-test")
    print("  python pfsense_azure_vault_integration.py --test-web")
    print("  python pfsense_azure_vault_integration.py --ssh 'uptime'")

    return 0


if __name__ == "__main__":



    sys.exit(main())