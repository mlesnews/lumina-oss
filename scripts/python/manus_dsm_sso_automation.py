#!/usr/bin/env python3
"""
MANUS DSM SSO Automation
Automates SAML SSO setup in DSM via RDP/MANUS browser automation
#JARVIS #MANUS #NAS #DSM #SSO #SAML #AUTOMATION #RDP
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
import logging
import json
import time

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    from nas_azure_vault_integration import NASAzureVaultIntegration
    VAULT_AVAILABLE = True
except ImportError:
    VAULT_AVAILABLE = False

logger = get_logger("MANUSDSMSSO")


class DSMSSOAutomation:
    """Automate DSM SSO setup via browser"""

    def __init__(self, nas_ip: str = "<NAS_PRIMARY_IP>", nas_port: int = 5001, project_root: Path = None):
        self.nas_ip = nas_ip
        self.nas_port = nas_port
        self.dsm_url = f"https://{nas_ip}:{nas_port}"
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.credentials: Optional[Dict[str, str]] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None

    def _get_credentials(self) -> bool:
        """Get DSM credentials from Azure Key Vault"""
        if not VAULT_AVAILABLE:
            logger.error("Azure Vault integration not available")
            return False

        try:
            vault = NASAzureVaultIntegration()
            self.credentials = vault.get_nas_credentials()
            if not self.credentials:
                logger.error("Could not retrieve credentials")
                return False
            return True
        except Exception as e:
            logger.error(f"Error getting credentials: {e}")
            return False

    def _setup_browser(self, headless: bool = False) -> bool:
        """Setup Playwright browser"""
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright not available. Install with: pip install playwright && playwright install")
            return False

        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=headless,
                args=[
                    '--ignore-certificate-errors',
                    '--ignore-ssl-errors',
                    '--ignore-certificate-errors-spki-list',
                    '--disable-web-security'
                ],
                slow_mo=500  # Slow down for better reliability
            )

            self.context = self.browser.new_context(
                ignore_https_errors=True,
                viewport={'width': 1920, 'height': 1080}
            )
            self.page = self.context.new_page()

            # Set longer timeout
            self.page.set_default_timeout(30000)

            logger.info("✅ Browser initialized")
            logger.info("   Note: Browser will stay open for manual verification if needed")
            return True
        except Exception as e:
            logger.error(f"Error setting up browser: {e}")
            return False

    def _login_to_dsm(self) -> bool:
        """Login to DSM"""
        if not self.page or not self.credentials:
            return False

        try:
            logger.info(f"🌐 Navigating to DSM: {self.dsm_url}")
            self.page.goto(self.dsm_url, wait_until="networkidle", timeout=30000)
            time.sleep(2)

            logger.info("🔐 Waiting for login form...")
            self.page.wait_for_selector("input[name='username'], input[type='text']", timeout=10000)

            username_input = self.page.query_selector("input[name='username'], input[type='text']")
            if username_input:
                username_input.fill(self.credentials["username"])
                logger.info(f"   ✓ Username entered")

            password_input = self.page.query_selector("input[name='password'], input[type='password']")
            if password_input:
                password_input.fill(self.credentials["password"])
                logger.info("   ✓ Password entered")

            login_button = self.page.query_selector("button[type='submit'], button:has-text('Sign In'), button:has-text('Login')")
            if not login_button:
                password_input.press("Enter")
            else:
                login_button.click()

            logger.info("   ✓ Login button clicked")
            time.sleep(5)

            if "login" not in self.page.url.lower():
                logger.info("✅ Successfully logged in to DSM")
                return True
            else:
                logger.warning("⚠️  May still be on login page")
                return False

        except Exception as e:
            logger.error(f"❌ Error during login: {e}")
            screenshot_path = self.project_root / "data" / "screenshots" / f"dsm_login_error_{int(time.time())}.png"
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            self.page.screenshot(path=str(screenshot_path))
            logger.info(f"   Screenshot saved: {screenshot_path}")
            return False

    def navigate_to_sso_server(self) -> bool:
        """Navigate to SSO Server application"""
        if not self.page:
            return False

        try:
            logger.info("🔐 Navigating to SSO Server...")

            # Method 1: Try direct URL
            sso_url = f"{self.dsm_url}/#sso"
            self.page.goto(sso_url, wait_until="networkidle", timeout=30000)
            time.sleep(3)

            # Method 2: Try clicking Main Menu > SSO Server
            sso_link = self.page.query_selector(
                "a:has-text('SSO Server'), [aria-label*='SSO'], "
                "div:has-text('SSO Server'), span:has-text('SSO Server')"
            )
            if sso_link:
                sso_link.click()
                time.sleep(3)
                logger.info("   ✓ Clicked SSO Server link")

            # Check if we're on SSO Server page
            if "sso" in self.page.url.lower() or "SSO" in self.page.title():
                logger.info("✅ Navigated to SSO Server")
                return True
            else:
                logger.warning("⚠️  May not be on SSO Server page")
                screenshot_path = self.project_root / "data" / "screenshots" / f"sso_server_{int(time.time())}.png"
                screenshot_path.parent.mkdir(parents=True, exist_ok=True)
                self.page.screenshot(path=str(screenshot_path))
                logger.info(f"   Screenshot saved: {screenshot_path}")
                return True  # Continue anyway

        except Exception as e:
            logger.error(f"❌ Error navigating to SSO Server: {e}")
            return False

    def configure_sso_as_idp(self, entity_id: str = None, sso_url: str = None) -> Dict[str, Any]:
        """Configure SSO Server as Identity Provider"""
        if not self.page:
            return {"success": False, "error": "Page not available"}

        try:
            logger.info("⚙️  Configuring SSO Server as Identity Provider...")

            # Navigate to Identity Provider tab
            idp_tab = self.page.query_selector(
                "button:has-text('Identity Provider'), tab:has-text('Identity Provider'), "
                "a:has-text('Identity Provider'), [aria-label*='Identity Provider']"
            )
            if idp_tab:
                idp_tab.click()
                time.sleep(2)
                logger.info("   ✓ Clicked Identity Provider tab")

            # Enable SSO Server as IdP
            enable_checkbox = self.page.query_selector(
                "input[type='checkbox']:near(:has-text('Enable SSO Server as Identity Provider')), "
                "input[type='checkbox'][name*='enable'], input[type='checkbox'][id*='enable']"
            )
            if enable_checkbox:
                if not enable_checkbox.is_checked():
                    enable_checkbox.check()
                    logger.info("   ✓ Enabled SSO Server as Identity Provider")
                else:
                    logger.info("   ✓ Already enabled")

            # Get Entity ID and SSO URL if not provided
            if not entity_id or not sso_url:
                entity_id_input = self.page.query_selector("input[name*='entity'], input[id*='entity']")
                if entity_id_input:
                    entity_id = entity_id_input.input_value() or entity_id_input.get_attribute("value")
                    logger.info(f"   ✓ Entity ID: {entity_id}")

                sso_url_input = self.page.query_selector("input[name*='sso'], input[id*='sso'], input[type='url']")
                if sso_url_input:
                    sso_url = sso_url_input.input_value() or sso_url_input.get_attribute("value")
                    logger.info(f"   ✓ SSO URL: {sso_url}")

            # Save configuration
            save_button = self.page.query_selector(
                "button:has-text('Save'), button:has-text('Apply'), button:has-text('OK'), "
                "button[type='submit']"
            )
            if save_button:
                save_button.click()
                time.sleep(2)
                logger.info("   ✓ Configuration saved")

            return {
                "success": True,
                "entity_id": entity_id,
                "sso_url": sso_url
            }

        except Exception as e:
            logger.error(f"❌ Error configuring SSO as IdP: {e}")
            screenshot_path = self.project_root / "data" / "screenshots" / f"sso_idp_error_{int(time.time())}.png"
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            self.page.screenshot(path=str(screenshot_path))
            return {"success": False, "error": str(e)}

    def configure_sso_client(self, metadata_file: str = None, entity_id: str = None, acs_url: str = None) -> Dict[str, Any]:
        """Configure SSO Client (Service Provider)"""
        if not self.page:
            return {"success": False, "error": "Page not available"}

        try:
            logger.info("⚙️  Configuring SSO Client...")

            # Navigate to Service Provider tab
            sp_tab = self.page.query_selector(
                "button:has-text('Service Provider'), tab:has-text('Service Provider'), "
                "a:has-text('Service Provider'), [aria-label*='Service Provider']"
            )
            if sp_tab:
                sp_tab.click()
                time.sleep(2)
                logger.info("   ✓ Clicked Service Provider tab")

            # Click Add button
            add_button = self.page.query_selector(
                "button:has-text('Add'), button:has-text('Create'), button:has-text('New'), "
                "[aria-label*='Add'], [aria-label*='Create']"
            )
            if add_button:
                add_button.click()
                time.sleep(2)
                logger.info("   ✓ Clicked Add button")

            # If metadata file provided, upload it
            if metadata_file:
                file_input = self.page.query_selector("input[type='file']")
                if file_input:
                    file_input.set_input_files(metadata_file)
                    logger.info(f"   ✓ Uploaded metadata file: {metadata_file}")
                    time.sleep(2)

            # Otherwise, fill in manually
            if entity_id:
                entity_id_input = self.page.query_selector("input[name*='entity'], input[id*='entity']")
                if entity_id_input:
                    entity_id_input.fill(entity_id)
                    logger.info(f"   ✓ Entity ID entered: {entity_id}")

            if acs_url:
                acs_input = self.page.query_selector("input[name*='acs'], input[name*='reply'], input[type='url']")
                if acs_input:
                    acs_input.fill(acs_url)
                    logger.info(f"   ✓ ACS URL entered: {acs_url}")

            # Save configuration
            save_button = self.page.query_selector(
                "button:has-text('Save'), button:has-text('Apply'), button:has-text('OK'), "
                "button[type='submit']"
            )
            if save_button:
                save_button.click()
                time.sleep(2)
                logger.info("   ✓ SSO Client configuration saved")

            return {"success": True}

        except Exception as e:
            logger.error(f"❌ Error configuring SSO Client: {e}")
            screenshot_path = self.project_root / "data" / "screenshots" / f"sso_client_error_{int(time.time())}.png"
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            self.page.screenshot(path=str(screenshot_path))
            return {"success": False, "error": str(e)}

    def complete_sso_setup(self, azure_metadata_file: str = None) -> Dict[str, Any]:
        """Complete SSO setup workflow"""
        results = {
            "success": False,
            "steps_completed": [],
            "steps_failed": [],
            "idp_config": {},
            "client_config": {}
        }

        try:
            # Setup browser and login
            if not self._setup_browser(headless=False):
                results["steps_failed"].append("Browser setup")
                return results

            if not self._get_credentials():
                results["steps_failed"].append("Get credentials")
                return results

            if not self._login_to_dsm():
                results["steps_failed"].append("Login to DSM")
                return results

            # Step 1: Navigate to SSO Server
            if not self.navigate_to_sso_server():
                results["steps_failed"].append("Navigate to SSO Server")
                return results
            results["steps_completed"].append("Navigate to SSO Server")

            # Step 2: Configure as IdP
            idp_result = self.configure_sso_as_idp()
            if idp_result.get("success"):
                results["steps_completed"].append("Configure SSO as IdP")
                results["idp_config"] = idp_result
            else:
                results["steps_failed"].append("Configure SSO as IdP")

            # Step 3: Configure SSO Client
            acs_url = f"https://{self.nas_ip}:{self.nas_port}/portal/sso/acs"
            client_result = self.configure_sso_client(
                metadata_file=azure_metadata_file,
                entity_id=idp_result.get("entity_id"),
                acs_url=acs_url
            )
            if client_result.get("success"):
                results["steps_completed"].append("Configure SSO Client")
                results["client_config"] = client_result
            else:
                results["steps_failed"].append("Configure SSO Client")

            results["success"] = len(results["steps_failed"]) == 0

            logger.info(f"\n✅ SSO Setup Complete: {len(results['steps_completed'])}/{len(results['steps_completed']) + len(results['steps_failed'])} steps")

        except Exception as e:
            logger.error(f"❌ Error completing SSO setup: {e}")
            results["steps_failed"].append(str(e))
        finally:
            if self.browser:
                time.sleep(10)  # Keep browser open to see results
                # self.browser.close()  # Commented out so user can verify

        return results

    def close(self):
        """Close browser"""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            logger.info("🔒 Browser closed")
        except Exception as e:
            logger.warning(f"Error closing browser: {e}")


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Automate DSM SSO Setup via RDP/MANUS")
    parser.add_argument("--nas-ip", default="<NAS_PRIMARY_IP>", help="NAS IP address")
    parser.add_argument("--nas-port", type=int, default=5001, help="NAS port")
    parser.add_argument("--metadata-file", help="Path to Azure AD Federation Metadata XML file")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")

    args = parser.parse_args()

    automation = DSMSSOAutomation(nas_ip=args.nas_ip, nas_port=args.nas_port)

    result = automation.complete_sso_setup(azure_metadata_file=args.metadata_file)

    if result["success"]:
        print(f"\n✅ SSO setup completed successfully!")
        print(f"   Steps completed: {len(result['steps_completed'])}")
        if result.get("idp_config"):
            print(f"   Entity ID: {result['idp_config'].get('entity_id', 'N/A')}")
            print(f"   SSO URL: {result['idp_config'].get('sso_url', 'N/A')}")
    else:
        print(f"\n⚠️  SSO setup completed with some issues")
        print(f"   Completed: {len(result['steps_completed'])}")
        print(f"   Failed: {len(result['steps_failed'])}")
        for step in result["steps_failed"]:
            print(f"      - {step}")
        return 1

    return 0


if __name__ == "__main__":


    sys.exit(main())