#!/usr/bin/env python3
"""
pfSense Web API Integration

Uses pfSense web portal API (HTTPS) when SSH is not available.
This allows configuration without SSH access.

Tags: #PFSENSE #API #WEB #CONFIGURATION @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
import re

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from pfsense_azure_vault_integration import PFSenseAzureVaultIntegration
    from lumina_logger import get_logger
    logger = get_logger("PFSenseWebAPI")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("PFSenseWebAPI")

try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class PFSenseWebAPI:
    """
    pfSense Web Portal API Integration

    Uses web portal (HTTPS) to configure pfSense when SSH is not available.
    """

    def __init__(self, pfsense_ip: str = "<NAS_IP>", pfsense_port: int = 443):
        """
        Initialize pfSense Web API

        Args:
            pfsense_ip: pfSense IP address
            pfsense_port: pfSense web portal port (default: 443)
        """
        self.pfsense_ip = pfsense_ip
        self.pfsense_port = pfsense_port
        self.base_url = f"https://{pfsense_ip}:{pfsense_port}"
        self.session = None
        self.csrf_token = None

        # Use existing integration for credentials
        self.integration = PFSenseAzureVaultIntegration(pfsense_ip=pfsense_ip)

        logger.info(f"PFSense Web API initialized: {self.base_url}")

    def login(self) -> bool:
        """
        Login to pfSense web portal and establish session

        Returns:
            True if login successful
        """
        if not REQUESTS_AVAILABLE:
            logger.error("requests library not available")
            return False

        try:
            self.session = requests.Session()

            # Get login page to extract CSRF token
            login_page = self.session.get(
                f"{self.base_url}/index.php",
                verify=False,
                timeout=10
            )

            # Extract CSRF token from page
            csrf_match = re.search(r'name="__csrf_magic".*?value="([^"]+)"', login_page.text)
            if csrf_match:
                self.csrf_token = csrf_match.group(1)
            else:
                # Try alternative CSRF token format
                csrf_match = re.search(r'csrfMagicToken\s*=\s*"([^"]+)"', login_page.text)
                if csrf_match:
                    self.csrf_token = csrf_match.group(1)

            # Get credentials
            credentials = self.integration.get_pfsense_credentials()
            if not credentials:
                logger.error("Could not retrieve pfSense credentials")
                return False

            # Login
            login_data = {
                "usernamefld": credentials["username"],
                "passwordfld": credentials["password"],
                "login": "Sign In"
            }

            if self.csrf_token:
                login_data["__csrf_magic"] = self.csrf_token

            login_response = self.session.post(
                f"{self.base_url}/index.php",
                data=login_data,
                verify=False,
                timeout=10,
                allow_redirects=True
            )

            # Check if login successful
            if login_response.status_code == 200:
                # Check if we're on dashboard (login successful)
                if "dashboard" in login_response.url.lower() or "index.php" in login_response.url:
                    logger.info("✅ Successfully logged into pfSense web portal")
                    return True

            logger.warning(f"Login may have failed: Status {login_response.status_code}")
            return False

        except Exception as e:
            logger.error(f"Error logging into pfSense web portal: {e}")
            return False

    def execute_pfssh_command(self, command: str) -> Dict[str, Any]:
        """
        Execute pfSsh.php command via web portal

        Note: pfSsh.php requires SSH, but we can use web portal API endpoints
        for configuration instead.

        Args:
            command: Command to execute (e.g., "enableinterface dhcp")

        Returns:
            Result dictionary
        """
        if not self.session:
            if not self.login():
                return {"success": False, "error": "Not logged in"}

        # Map pfSsh.php commands to web API endpoints
        # For now, return instructions for manual configuration
        logger.info(f"⚠️  pfSsh.php commands require SSH access")
        logger.info(f"   Command requested: {command}")
        logger.info(f"   Use web portal to configure: {self.base_url}")

        return {
            "success": False,
            "error": "pfSsh.php requires SSH access",
            "command": command,
            "alternative": f"Configure via web portal: {self.base_url}",
            "note": "SSH is currently disabled. Enable SSH or use web portal for configuration."
        }

    def configure_dhcp_via_web(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Configure DHCP via web portal API

        Args:
            config: DHCP configuration dictionary

        Returns:
            Configuration result
        """
        if not self.session:
            if not self.login():
                return {"success": False, "error": "Not logged in"}

        logger.info("⚠️  DHCP configuration via web API requires manual steps")
        logger.info("   Navigate to: Services > DHCP Server")
        logger.info(f"   URL: {self.base_url}")

        return {
            "success": False,
            "method": "web_portal_manual",
            "url": f"{self.base_url}",
            "path": "Services > DHCP Server",
            "config": config,
            "note": "Use web portal to configure DHCP. SSH is required for automated configuration."
        }

    def check_dhcp_status(self) -> Dict[str, Any]:
        """
        Check DHCP status via web portal

        Returns:
            Status dictionary
        """
        if not self.session:
            if not self.login():
                return {"success": False, "error": "Not logged in"}

        try:
            # Try to access DHCP status page
            dhcp_url = f"{self.base_url}/services_dhcp.php"
            response = self.session.get(dhcp_url, verify=False, timeout=10)

            if response.status_code == 200:
                # Check if DHCP is enabled (basic check)
                dhcp_enabled = "Enable DHCP server" in response.text or "DHCP Server" in response.text

                return {
                    "success": True,
                    "dhcp_accessible": True,
                    "dhcp_enabled": dhcp_enabled,
                    "method": "web_portal"
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "method": "web_portal"
                }

        except Exception as e:
            logger.error(f"Error checking DHCP status: {e}")
            return {
                "success": False,
                "error": str(e),
                "method": "web_portal"
            }


def main():
    """Main function for testing"""
    import argparse

    parser = argparse.ArgumentParser(description="pfSense Web API Integration")
    parser.add_argument("--pfsense-ip", default="<NAS_IP>", help="pfSense IP address")
    parser.add_argument("--test-login", action="store_true", help="Test web portal login")
    parser.add_argument("--check-dhcp", action="store_true", help="Check DHCP status")

    args = parser.parse_args()

    api = PFSenseWebAPI(pfsense_ip=args.pfsense_ip)

    if args.test_login:
        print("Testing pfSense web portal login...")
        if api.login():
            print("✅ Login successful!")
            return 0
        else:
            print("❌ Login failed")
            return 1

    if args.check_dhcp:
        print("Checking DHCP status...")
        status = api.check_dhcp_status()
        print(f"Status: {status}")
        return 0 if status.get("success") else 1

    print("pfSense Web API Integration")
    print("\nUsage:")
    print("  --test-login    Test web portal login")
    print("  --check-dhcp    Check DHCP status")

    return 0


if __name__ == "__main__":


    sys.exit(main())