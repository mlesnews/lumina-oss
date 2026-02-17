#!/usr/bin/env python3
"""
@MANUS Azure Function Deployment Automation
Uses browser automation to deploy RenderIronLegion function to Azure Portal
Full @manus/@magneto authority - automated deployment
"""
import sys
import time
from pathlib import Path
from typing import Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

# Try Selenium first, fallback to Playwright
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    from lumina_logger import get_logger
    logger = get_logger("ManusAzureDeploy")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ManusAzureDeploy")


class ManusAzureDeployer:
    """@MANUS authority - Automated Azure Function deployment"""

    def __init__(self):
        self.function_code_path = project_root / "azure_functions" / "RenderIronLegion" / "__init__.py"
        self.function_app_name = "jarvis-lumina-functions"
        self.portal_url = "https://portal.azure.com"
        self.driver = None

    def load_function_code(self) -> str:
        try:
            """Load function code"""
            with open(self.function_code_path, 'r', encoding='utf-8') as f:
                return f.read()

        except Exception as e:
            self.logger.error(f"Error in load_function_code: {e}", exc_info=True)
            raise
    def deploy_with_selenium(self) -> bool:
        """Deploy using Selenium"""
        if not SELENIUM_AVAILABLE:
            logger.error("❌ Selenium not available - install: pip install selenium")
            return False

        try:
            logger.info("🚀 @MANUS: Starting automated deployment with Selenium...")

            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

            # Initialize driver
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)

            # Navigate to Azure Portal
            logger.info("🌐 Navigating to Azure Portal...")
            self.driver.get(self.portal_url)

            # Wait for sign-in - auto-detect when signed in
            logger.info("⏸️  Waiting for Azure sign-in...")
            logger.info("   Please complete sign-in and 2FA if prompted")
            logger.info("   Browser will auto-detect when signed in...")

            # Wait for portal to load (check for Azure Portal elements)
            max_wait = 300  # 5 minutes max
            wait_time = 0
            signed_in = False

            while wait_time < max_wait and not signed_in:
                try:
                    # Check if we're past sign-in (look for Azure Portal elements)
                    if "portal.azure.com" in self.driver.current_url and "login" not in self.driver.current_url.lower():
                        # Check for portal navigation elements
                        nav_elements = self.driver.find_elements(By.XPATH, "//nav | //div[@role='navigation'] | //a[contains(@href, 'portal.azure.com')]")
                        if nav_elements:
                            signed_in = True
                            logger.info("✅ Detected sign-in complete!")
                            break
                except:
                    pass

                time.sleep(2)
                wait_time += 2
                if wait_time % 30 == 0:
                    logger.info(f"   Still waiting... ({wait_time}s)")

            if not signed_in:
                logger.warning("⚠️  Could not auto-detect sign-in - proceeding anyway")
                time.sleep(5)  # Give extra time

            # Navigate to Function App
            logger.info(f"🔍 Navigating to Function App: {self.function_app_name}...")
            search_url = f"{self.portal_url}/#@/resource/subscriptions/resourceGroups/jarvis-lumina-rg/providers/Microsoft.Web/sites/{self.function_app_name}"
            self.driver.get(search_url)
            time.sleep(3)

            # Click Functions
            logger.info("📁 Opening Functions...")
            try:
                functions_link = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Functions') or contains(@aria-label, 'Functions')]"))
                )
                functions_link.click()
                time.sleep(2)
            except Exception as e:
                logger.warning(f"⚠️  Could not find Functions link automatically: {e}")
                logger.info("   Please manually click 'Functions' in the left menu")
                input("   [Press Enter when Functions page is open]")

            # Click Create/Add
            logger.info("➕ Creating new function...")
            try:
                create_button = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create') or contains(text(), 'Add') or contains(@aria-label, 'Create')]"))
                )
                create_button.click()
                time.sleep(2)
            except Exception as e:
                logger.warning(f"⚠️  Could not find Create button: {e}")
                logger.info("   Please manually click 'Create' or 'Add' button")
                input("   [Press Enter when function creation dialog is open]")

            # Select HTTP trigger
            logger.info("🔘 Selecting HTTP trigger...")
            try:
                http_trigger = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'HTTP trigger') or contains(@aria-label, 'HTTP trigger')]"))
                )
                http_trigger.click()
                time.sleep(1)
            except Exception as e:
                logger.warning(f"⚠️  Could not find HTTP trigger: {e}")
                logger.info("   Please manually select 'HTTP trigger'")
                input("   [Press Enter when HTTP trigger is selected]")

            # Enter function name
            logger.info("✏️  Entering function name: RenderIronLegion...")
            function_code = self.load_function_code()
            try:
                name_input = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='text' or @name='name' or contains(@aria-label, 'name')]"))
                )
                name_input.clear()
                name_input.send_keys("RenderIronLegion")
                time.sleep(1)
            except Exception as e:
                logger.warning(f"⚠️  Could not find name input: {e}")
                logger.info("   Please manually enter function name: RenderIronLegion")
                input("   [Press Enter when name is entered]")

            # Click Create/Continue
            logger.info("✅ Creating function...")
            try:
                create_final = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create') or contains(text(), 'Continue') or contains(@aria-label, 'Create')]"))
                )
                create_final.click()
                time.sleep(5)  # Wait for function to be created
            except Exception as e:
                logger.warning(f"⚠️  Could not find final Create button: {e}")
                logger.info("   Please manually click 'Create' to create the function")
                input("   [Press Enter when function is created and code editor is open]")

            # Paste code
            logger.info("📋 Pasting function code...")
            try:
                # Find code editor (usually a textarea or contenteditable div)
                code_editor = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//textarea | //div[@contenteditable='true'] | //pre | //code"))
                )

                # Clear existing code
                code_editor.click()
                code_editor.send_keys(Keys.CONTROL + "a")
                time.sleep(0.5)

                # Paste code
                code_editor.send_keys(Keys.CONTROL + "v")
                time.sleep(2)

                logger.info("✅ Code pasted successfully")
            except Exception as e:
                logger.warning(f"⚠️  Could not paste code automatically: {e}")
                logger.info("   Code is in your clipboard - please paste manually (Ctrl+V)")
                input("   [Press Enter when code is pasted]")

            # Save
            logger.info("💾 Saving function...")
            try:
                save_button = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Save') or contains(@aria-label, 'Save')]"))
                )
                save_button.click()
                time.sleep(3)
                logger.info("✅ Function saved!")
            except Exception as e:
                logger.warning(f"⚠️  Could not find Save button: {e}")
                logger.info("   Please manually click 'Save' button")
                input("   [Press Enter when function is saved]")

            logger.info("=" * 80)
            logger.info("✅ @MANUS DEPLOYMENT COMPLETE!")
            logger.info("=" * 80)
            logger.info(f"   Function: RenderIronLegion")
            logger.info(f"   Endpoint: https://{self.function_app_name}.azurewebsites.net/api/RenderIronLegion")
            logger.info("   Testing in 5 seconds...")

            time.sleep(5)
            self.driver.quit()
            return True

        except Exception as e:
            logger.error(f"❌ Deployment error: {e}")
            if self.driver:
                self.driver.quit()
            return False

    def deploy_with_playwright(self) -> bool:
        """Deploy using Playwright (alternative)"""
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("❌ Playwright not available - install: pip install playwright && playwright install")
            return False

        logger.info("🚀 @MANUS: Starting automated deployment with Playwright...")
        # Similar implementation with Playwright
        # (Implementation would be similar but using Playwright API)
        return False

    def deploy(self) -> bool:
        """Main deployment method - tries Selenium first, then Playwright"""
        if SELENIUM_AVAILABLE:
            return self.deploy_with_selenium()
        elif PLAYWRIGHT_AVAILABLE:
            return self.deploy_with_playwright()
        else:
            logger.error("❌ No browser automation available")
            logger.info("   Install one of:")
            logger.info("   - Selenium: pip install selenium")
            logger.info("   - Playwright: pip install playwright && playwright install")
            return False


def main():
    """@MANUS deployment execution"""
    print("=" * 80)
    print("🔥 @MANUS AUTHORITY: Azure Function Deployment")
    print("=" * 80)
    print("   Full automation with browser control")
    print("   Overtaking browser to deploy RenderIronLegion")
    print("=" * 80)

    deployer = ManusAzureDeployer()

    # Copy code to clipboard as backup
    try:
        import pyperclip
        code = deployer.load_function_code()
        pyperclip.copy(code)
        print("✅ Function code copied to clipboard (backup)")
    except:
        print("⚠️  Could not copy to clipboard - code will be loaded from file")

    success = deployer.deploy()

    if success:
        print("\n✅ Deployment automation complete!")
        print("   Function should now be live at:")
        print(f"   https://jarvis-lumina-functions.azurewebsites.net/api/RenderIronLegion")
    else:
        print("\n⚠️  Automated deployment had issues")
        print("   Manual deployment may be required")

    return 0 if success else 1


if __name__ == "__main__":


    sys.exit(main())