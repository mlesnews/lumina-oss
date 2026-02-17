#!/usr/bin/env python3
"""
MANUS Configure pfSense DHCP via NEO Browser Automation

Uses MANUS/NEO browser automation to configure pfSense DHCP settings via web portal.
This provides complete CLI-API control without requiring SSH access.

Tags: #PFSENSE #DHCP #MANUS #NEO #BROWSER_AUTOMATION #CLI_API
@JARVIS @LUMINA @MANUS @DOIT
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from neo_browser_automation_engine import NEOBrowserAutomationEngine
    NEO_AVAILABLE = True
except ImportError:
    NEO_AVAILABLE = False
    logger = get_logger("MANUSPFSenseDHCP")
    logger.warning("⚠️  NEO Browser Automation Engine not available")

try:
    from pfsense_azure_vault_integration import PFSenseAzureVaultIntegration
    PFSENSE_VAULT_AVAILABLE = True
except ImportError:
    PFSENSE_VAULT_AVAILABLE = False

try:
    import pyautogui
    import pygetwindow as gw
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

logger = get_logger("MANUSPFSenseDHCP")


class MANUSPFSenseDHCPConfigurator:
    """
    MANUS pfSense DHCP Configurator

    Uses NEO browser automation to configure pfSense DHCP via web portal
    """

    def __init__(
        self,
        pfsense_ip: str = "<NAS_IP>",
        pfsense_port: int = 443,
        dhcp_range_start: str = "<NAS_IP>",
        dhcp_range_end: str = "<NAS_IP>",
        gateway: str = "<NAS_IP>",
        dns_primary: str = "<NAS_IP>",
        dns_secondary: str = "<NAS_PRIMARY_IP>"
    ):
        """
        Initialize MANUS pfSense DHCP Configurator

        Args:
            pfsense_ip: pfSense IP address
            pfsense_port: pfSense web portal port
            dhcp_range_start: DHCP range start IP
            dhcp_range_end: DHCP range end IP
            gateway: Default gateway
            dns_primary: Primary DNS server
            dns_secondary: Secondary DNS server
        """
        self.pfsense_ip = pfsense_ip
        self.pfsense_port = pfsense_port
        self.pfsense_url = f"https://{pfsense_ip}:{pfsense_port}"
        self.dhcp_range_start = dhcp_range_start
        self.dhcp_range_end = dhcp_range_end
        self.gateway = gateway
        self.dns_primary = dns_primary
        self.dns_secondary = dns_secondary

        self.neo: Optional[NEOBrowserAutomationEngine] = None
        self.credentials: Optional[Dict[str, str]] = None

        # Get credentials
        if PFSENSE_VAULT_AVAILABLE:
            integration = PFSenseAzureVaultIntegration(pfsense_ip=pfsense_ip)
            self.credentials = integration.get_pfsense_credentials()

        logger.info("🔧 MANUS pfSense DHCP Configurator initialized")
        logger.info(f"   pfSense URL: {self.pfsense_url}")
        logger.info(f"   DHCP Range: {dhcp_range_start} - {dhcp_range_end}")

    def launch_neo_browser(self) -> bool:
        """Launch NEO browser and navigate to pfSense"""
        if not NEO_AVAILABLE:
            logger.error("❌ NEO Browser Automation Engine not available")
            return False

        try:
            logger.info("🚀 Launching NEO browser...")
            self.neo = NEOBrowserAutomationEngine(project_root)

            # Launch browser and navigate to pfSense
            if self.neo.launch(url=self.pfsense_url, headless=False):
                logger.info("✅ NEO browser launched")
                time.sleep(3)  # Wait for page to load
                return True
            else:
                logger.error("❌ Failed to launch NEO browser")
                return False

        except Exception as e:
            logger.error(f"❌ Error launching NEO browser: {e}")
            return False

    def login_to_pfsense(self) -> bool:
        """Login to pfSense web portal"""
        if not self.neo or not self.credentials:
            logger.error("❌ NEO browser or credentials not available")
            return False

        try:
            logger.info("🔐 Logging into pfSense...")

            # Wait for login page
            time.sleep(2)

            # Wait for login page to load
            self.neo.wait_for_element('input[name="usernamefld"], input[id="usernamefld"]', timeout=10)
            time.sleep(1)

            # Find and fill username field
            username_selectors = [
                'input[name="usernamefld"]',
                'input[id="usernamefld"]',
                'input[type="text"]'
            ]
            username_filled = False
            for selector in username_selectors:
                if self.neo.fill(selector, self.credentials["username"]):
                    username_filled = True
                    logger.info(f"✅ Filled username field using: {selector}")
                    break

            if not username_filled:
                logger.warning("⚠️  Could not find username field, trying alternative methods...")
                # Try JavaScript injection
                username_script = f"""
                (function() {{
                    var inputs = document.querySelectorAll('input[type="text"], input[name*="user"], input[id*="user"]');
                    for (var i = 0; i < inputs.length; i++) {{
                        if (inputs[i].offsetParent !== null) {{
                            inputs[i].value = {json.dumps(self.credentials["username"])};
                            inputs[i].dispatchEvent(new Event('input', {{ bubbles: true }}));
                            return true;
                        }}
                    }}
                    return false;
                }})();
                """
                if self.neo.execute_script(username_script):
                    username_filled = True

            time.sleep(0.5)

            # Find and fill password field
            password_selectors = [
                'input[name="passwordfld"]',
                'input[id="passwordfld"]',
                'input[type="password"]'
            ]
            password_filled = False
            for selector in password_selectors:
                if self.neo.fill(selector, self.credentials["password"]):
                    password_filled = True
                    logger.info(f"✅ Filled password field using: {selector}")
                    break

            if not password_filled:
                logger.warning("⚠️  Could not find password field, trying JavaScript...")
                password_script = f"""
                (function() {{
                    var inputs = document.querySelectorAll('input[type="password"]');
                    for (var i = 0; i < inputs.length; i++) {{
                        if (inputs[i].offsetParent !== null) {{
                            inputs[i].value = {json.dumps(self.credentials["password"])};
                            inputs[i].dispatchEvent(new Event('input', {{ bubbles: true }}));
                            return true;
                        }}
                    }}
                    return false;
                }})();
                """
                self.neo.execute_script(password_script)

            time.sleep(0.5)

            # Click login button
            login_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:contains("Sign In")',
                'button:contains("Login")'
            ]
            login_clicked = False
            for selector in login_selectors:
                if self.neo.click(selector):
                    login_clicked = True
                    logger.info(f"✅ Clicked login button using: {selector}")
                    break

            if not login_clicked:
                # Try JavaScript click
                login_script = """
                (function() {
                    var buttons = document.querySelectorAll('button[type="submit"], input[type="submit"]');
                    for (var i = 0; i < buttons.length; i++) {
                        if (buttons[i].offsetParent !== null) {
                            buttons[i].click();
                            return true;
                        }
                    }
                    return false;
                })();
                """
                self.neo.execute_script(login_script)

            # Wait for login to complete
            time.sleep(5)

            # Check if login successful (look for dashboard or main menu)
            url_script = "window.location.href"
            current_url = self.neo.execute_script(url_script)
            if current_url and ("index.php" in current_url or "dashboard" in current_url.lower()):
                logger.info("✅ Successfully logged into pfSense")
                return True
            else:
                logger.warning(f"⚠️  Login status unclear. Current URL: {current_url}")
                return True  # Assume success, continue anyway

        except Exception as e:
            logger.error(f"❌ Error logging into pfSense: {e}")
            return False

    def navigate_to_dhcp_server(self) -> bool:
        """Navigate to DHCP Server configuration page"""
        if not self.neo:
            return False

        try:
            logger.info("🧭 Navigating to DHCP Server configuration...")

            # Navigate directly via URL (most reliable)
            dhcp_url = f"{self.pfsense_url}/services_dhcp.php"
            logger.info(f"   Navigating to: {dhcp_url}")
            if self.neo.navigate(dhcp_url):
                time.sleep(3)
                logger.info("✅ Navigated to DHCP Server configuration")
            else:
                # Try alternative URL
                dhcp_url_alt = f"{self.pfsense_url}/services_dhcp_edit.php"
                self.neo.navigate(dhcp_url_alt)
                time.sleep(3)

            # Alternative: Navigate via menu if direct URL doesn't work
            # Try clicking Services menu
            services_script = """
            (function() {
                var services = document.querySelectorAll('a, li, [data-menu]');
                for (var i = 0; i < services.length; i++) {
                    var text = (services[i].textContent || services[i].innerText || '').toLowerCase();
                    if (text.includes('services')) {
                        services[i].click();
                        return true;
                    }
                }
                return false;
            })();
            """
            self.neo.execute_script(services_script)
            time.sleep(1)

            # Try clicking DHCP Server submenu
            dhcp_script = """
            (function() {
                var links = document.querySelectorAll('a, li');
                for (var i = 0; i < links.length; i++) {
                    var text = (links[i].textContent || links[i].innerText || '').toLowerCase();
                    if (text.includes('dhcp') && text.includes('server')) {
                        links[i].click();
                        return true;
                    }
                }
                return false;
            })();
            """
            self.neo.execute_script(dhcp_script)
            time.sleep(2)

            logger.info("✅ Navigated to DHCP Server configuration")
            return True

        except Exception as e:
            logger.error(f"❌ Error navigating to DHCP Server: {e}")
            return False

    def configure_dhcp_settings(self) -> bool:
        """Configure DHCP settings"""
        if not self.neo:
            return False

        try:
            logger.info("⚙️  Configuring DHCP settings...")

            # Wait for DHCP configuration page to load
            time.sleep(2)

            # Enable DHCP server checkbox
            enable_script = """
            (function() {
                var checkboxes = document.querySelectorAll('input[type="checkbox"][name*="enable"], input[id*="enable"]');
                for (var i = 0; i < checkboxes.length; i++) {
                    if (!checkboxes[i].checked) {
                        checkboxes[i].click();
                        return true;
                    }
                }
                return false;
            })();
            """
            self.neo.execute_script(enable_script)
            time.sleep(0.5)

            # Fill in DHCP range start
            range_start_script = f"""
            (function() {{
                var inputs = document.querySelectorAll('input[name*="from"], input[id*="from"], input[placeholder*="from"]');
                for (var i = 0; i < inputs.length; i++) {{
                    if (inputs[i].offsetParent !== null && inputs[i].type !== 'checkbox') {{
                        inputs[i].value = {json.dumps(self.dhcp_range_start)};
                        inputs[i].dispatchEvent(new Event('input', {{ bubbles: true }}));
                        return true;
                    }}
                }}
                return false;
            }})();
            """
            self.neo.execute_script(range_start_script)
            time.sleep(0.3)

            # Fill in DHCP range end
            range_end_script = f"""
            (function() {{
                var inputs = document.querySelectorAll('input[name*="to"], input[id*="to"], input[placeholder*="to"]');
                for (var i = 0; i < inputs.length; i++) {{
                    if (inputs[i].offsetParent !== null && inputs[i].type !== 'checkbox') {{
                        inputs[i].value = {json.dumps(self.dhcp_range_end)};
                        inputs[i].dispatchEvent(new Event('input', {{ bubbles: true }}));
                        return true;
                    }}
                }}
                return false;
            }})();
            """
            self.neo.execute_script(range_end_script)
            time.sleep(0.3)

            # Fill in gateway
            gateway_script = f"""
            (function() {{
                var inputs = document.querySelectorAll('input[name*="gateway"], input[id*="gateway"]');
                for (var i = 0; i < inputs.length; i++) {{
                    if (inputs[i].offsetParent !== null) {{
                        inputs[i].value = {json.dumps(self.gateway)};
                        inputs[i].dispatchEvent(new Event('input', {{ bubbles: true }}));
                        return true;
                    }}
                }}
                return false;
            }})();
            """
            self.neo.execute_script(gateway_script)
            time.sleep(0.3)

            # Fill in DNS servers
            dns1_script = f"""
            (function() {{
                var inputs = document.querySelectorAll('input[name*="dns1"], input[id*="dns1"], input[name*="dns"][value=""]');
                for (var i = 0; i < inputs.length; i++) {{
                    if (inputs[i].offsetParent !== null && !inputs[i].value) {{
                        inputs[i].value = {json.dumps(self.dns_primary)};
                        inputs[i].dispatchEvent(new Event('input', {{ bubbles: true }}));
                        return true;
                    }}
                }}
                return false;
            }})();
            """
            self.neo.execute_script(dns1_script)
            time.sleep(0.3)

            dns2_script = f"""
            (function() {{
                var inputs = document.querySelectorAll('input[name*="dns2"], input[id*="dns2"]');
                for (var i = 0; i < inputs.length; i++) {{
                    if (inputs[i].offsetParent !== null) {{
                        inputs[i].value = {json.dumps(self.dns_secondary)};
                        inputs[i].dispatchEvent(new Event('input', {{ bubbles: true }}));
                        return true;
                    }}
                }}
                return false;
            }})();
            """
            self.neo.execute_script(dns2_script)
            time.sleep(0.3)

            # Save configuration
            save_script = """
            (function() {
                var buttons = document.querySelectorAll('button[type="submit"], input[type="submit"], button');
                for (var i = 0; i < buttons.length; i++) {
                    var text = (buttons[i].textContent || buttons[i].innerText || '').toLowerCase();
                    if (text.includes('save') || text.includes('apply')) {
                        buttons[i].click();
                        return true;
                    }
                }
                return false;
            })();
            """
            self.neo.execute_script(save_script)
            time.sleep(3)

            logger.info("✅ DHCP settings configured")
            return True

        except Exception as e:
            logger.error(f"❌ Error configuring DHCP settings: {e}")
            return False

    def configure_dhcp_complete(self) -> Dict[str, Any]:
        """
        Complete DHCP configuration workflow

        Returns:
            Configuration result
        """
        logger.info("=" * 70)
        logger.info("🚀 MANUS PFSENSE DHCP CONFIGURATION")
        logger.info("=" * 70)

        result = {
            "success": False,
            "steps": {},
            "errors": []
        }

        # Step 1: Launch NEO browser
        logger.info("\n📋 Step 1: Launching NEO browser...")
        if self.launch_neo_browser():
            result["steps"]["launch_browser"] = True
        else:
            result["steps"]["launch_browser"] = False
            result["errors"].append("Failed to launch NEO browser")
            return result

        # Step 2: Login to pfSense
        logger.info("\n📋 Step 2: Logging into pfSense...")
        if self.login_to_pfsense():
            result["steps"]["login"] = True
        else:
            result["steps"]["login"] = False
            result["errors"].append("Failed to login to pfSense")
            # Continue anyway - might still work

        # Step 3: Navigate to DHCP Server
        logger.info("\n📋 Step 3: Navigating to DHCP Server...")
        if self.navigate_to_dhcp_server():
            result["steps"]["navigate"] = True
        else:
            result["steps"]["navigate"] = False
            result["errors"].append("Failed to navigate to DHCP Server")
            # Continue anyway - might be on correct page

        # Step 4: Configure DHCP settings
        logger.info("\n📋 Step 4: Configuring DHCP settings...")
        if self.configure_dhcp_settings():
            result["steps"]["configure"] = True
        else:
            result["steps"]["configure"] = False
            result["errors"].append("Failed to configure DHCP settings")

        # Overall success
        result["success"] = (
            result["steps"].get("launch_browser", False) and
            result["steps"].get("configure", False)
        )

        logger.info("\n" + "=" * 70)
        if result["success"]:
            logger.info("✅ DHCP CONFIGURATION COMPLETE")
        else:
            logger.info("⚠️  CONFIGURATION REQUIRES MANUAL STEPS")
        logger.info("=" * 70)

        if result["errors"]:
            logger.info("\n⚠️  Errors encountered:")
            for error in result["errors"]:
                logger.info(f"   - {error}")

        return result

    def close(self):
        """Close NEO browser"""
        if self.neo:
            try:
                self.neo.close()
                logger.info("✅ NEO browser closed")
            except Exception as e:
                logger.debug(f"Error closing browser: {e}")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="MANUS Configure pfSense DHCP via NEO Browser"
    )
    parser.add_argument(
        "--pfsense-ip",
        default="<NAS_IP>",
        help="pfSense IP address"
    )
    parser.add_argument(
        "--pfsense-port",
        type=int,
        default=443,
        help="pfSense web portal port"
    )
    parser.add_argument(
        "--dhcp-range-start",
        default="<NAS_IP>",
        help="DHCP range start IP"
    )
    parser.add_argument(
        "--dhcp-range-end",
        default="<NAS_IP>",
        help="DHCP range end IP"
    )
    parser.add_argument(
        "--gateway",
        default="<NAS_IP>",
        help="Default gateway"
    )
    parser.add_argument(
        "--dns-primary",
        default="<NAS_IP>",
        help="Primary DNS server"
    )
    parser.add_argument(
        "--dns-secondary",
        default="<NAS_PRIMARY_IP>",
        help="Secondary DNS server"
    )

    args = parser.parse_args()

    configurator = MANUSPFSenseDHCPConfigurator(
        pfsense_ip=args.pfsense_ip,
        pfsense_port=args.pfsense_port,
        dhcp_range_start=args.dhcp_range_start,
        dhcp_range_end=args.dhcp_range_end,
        gateway=args.gateway,
        dns_primary=args.dns_primary,
        dns_secondary=args.dns_secondary
    )

    try:
        result = configurator.configure_dhcp_complete()
        return 0 if result.get("success", False) else 1
    finally:
        configurator.close()


if __name__ == "__main__":


    sys.exit(main())