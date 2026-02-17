#!/usr/bin/env python3
"""
JARVIS: Create MailPlus Account via GUI with Vision

Creates the email account in MailPlus using GUI automation with screenshots.

Tags: #JARVIS #MAILPLUS #ACCOUNT #GUI #VISION #AUTOMATION @JARVIS @LUMINA @DOIT
"""

import sys
import time
import webbrowser
from pathlib import Path

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

logger = get_logger("JARVISCreateMailPlusGUI")

ACCOUNT_EMAIL = "mlesn@<LOCAL_HOSTNAME>"
NAS_IP = "<NAS_PRIMARY_IP>"
NAS_PORT = 5001


def capture_screen(save_path: str = None):
    """Capture current screen"""
    try:
        import pyautogui
        screenshot = pyautogui.screenshot()
        if save_path:
            screenshot.save(save_path)
            logger.info(f"📸 Screenshot saved: {save_path}")
        return screenshot
    except Exception as e:
        logger.error(f"❌ Failed to capture screen: {e}")
        return None


def create_account_with_vision():
    """Create MailPlus account using GUI automation with vision"""
    try:
        import pyautogui
        import pygetwindow as gw

        logger.info("=" * 80)
        logger.info("📧 JARVIS: CREATING MAILPLUS ACCOUNT WITH VISION")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"Account: {ACCOUNT_EMAIL}")
        logger.info("")

        # Create screenshots directory
        screenshots_dir = project_root / "data" / "temp" / "mailplus_account_screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        # Step 1: Open MailPlus Account page
        logger.info("📋 STEP 1: Opening MailPlus Account page...")
        logger.info("-" * 80)

        account_url = f"https://{NAS_IP}:{NAS_PORT}/#mailplus/account"
        logger.info(f"Opening: {account_url}")
        webbrowser.open(account_url)

        logger.info("⏳ Waiting 10 seconds for page to load...")
        time.sleep(10)

        screenshot_path = screenshots_dir / f"step1_page_loaded_{int(time.time())}.png"
        capture_screen(str(screenshot_path))
        logger.info("📸 Captured page load")
        logger.info(f"   Check: {screenshot_path}")

        # Step 2: Find browser window
        logger.info("")
        logger.info("📋 STEP 2: Finding browser window...")
        logger.info("-" * 80)

        browser_windows = []
        for window in gw.getAllWindows():
            title_lower = window.title.lower()
            if any(browser in title_lower for browser in ['chrome', 'edge', 'firefox', 'opera', 'brave', 'neo', 'dsm']):
                browser_windows.append(window)

        if not browser_windows:
            logger.warning("⚠️  Could not find browser window")
            logger.info("   Please ensure browser is open and visible")
            return False

        browser_window = browser_windows[0]
        logger.info(f"✅ Found browser window: {browser_window.title}")

        try:
            browser_window.activate()
            time.sleep(2)
        except Exception:
            pass

        screenshot_path = screenshots_dir / f"step2_browser_active_{int(time.time())}.png"
        capture_screen(str(screenshot_path))

        # Step 3: Handle certificate warning
        logger.info("")
        logger.info("📋 STEP 3: Handling certificate warning...")
        logger.info("-" * 80)

        logger.info("   Typing 'thisisunsafe' to bypass certificate...")
        time.sleep(2)
        pyautogui.write("thisisunsafe", interval=0.1)
        time.sleep(3)

        screenshot_path = screenshots_dir / f"step3_after_cert_{int(time.time())}.png"
        capture_screen(str(screenshot_path))

        # Step 4: Look for Create/Add button
        logger.info("")
        logger.info("📋 STEP 4: Looking for Create/Add button...")
        logger.info("-" * 80)

        screenshot_path = screenshots_dir / f"step4_before_create_{int(time.time())}.png"
        capture_screen(str(screenshot_path))
        logger.info("📸 Captured current state")
        logger.info("   Review screenshot to see if Create button is visible")

        # Try common positions for Create button
        # Usually top-right or in a toolbar
        logger.info("   Attempting to find Create button...")

        # Try clicking common Create button positions
        # Method 1: Look for "Create" text (might need OCR or image matching)
        # Method 2: Try keyboard shortcut (usually Ctrl+N or just clicking)
        # Method 3: Try clicking in common button areas

        # For now, try Tab navigation to find Create button
        logger.info("   Trying Tab navigation to find Create button...")
        pyautogui.press('tab', presses=5)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(2)

        screenshot_path = screenshots_dir / f"step5_after_create_click_{int(time.time())}.png"
        capture_screen(str(screenshot_path))
        logger.info("📸 Captured after Create click")
        logger.info(f"   Check: {screenshot_path}")
        logger.info("   Review to see if account creation dialog opened")

        # Step 5: Fill in account details
        logger.info("")
        logger.info("📋 STEP 5: Filling in account details...")
        logger.info("-" * 80)

        # Email field
        logger.info(f"   Entering email: {ACCOUNT_EMAIL}")
        pyautogui.write(ACCOUNT_EMAIL, interval=0.1)
        time.sleep(1)

        screenshot_path = screenshots_dir / f"step6_email_entered_{int(time.time())}.png"
        capture_screen(str(screenshot_path))

        # Password field
        logger.info("   Entering password...")
        pyautogui.press('tab')
        time.sleep(0.5)

        from nas_azure_vault_integration import NASAzureVaultIntegration
        nas_integration = NASAzureVaultIntegration()
        credentials = nas_integration.get_nas_credentials()
        password = credentials.get("password") if credentials else None

        if password:
            pyautogui.write(password, interval=0.05)
            time.sleep(1)
        else:
            logger.warning("   ⏸️  Waiting for manual password entry...")
            time.sleep(10)

        screenshot_path = screenshots_dir / f"step7_password_entered_{int(time.time())}.png"
        capture_screen(str(screenshot_path))

        # Step 6: Save/Create account
        logger.info("")
        logger.info("📋 STEP 6: Saving account...")
        logger.info("-" * 80)

        # Try to find Save/Create button
        # Usually Tab to it or Enter
        pyautogui.press('tab', presses=2)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(3)

        screenshot_path = screenshots_dir / f"step8_after_save_{int(time.time())}.png"
        capture_screen(str(screenshot_path))
        logger.info("📸 Captured after save")
        logger.info(f"   Check: {screenshot_path}")
        logger.info("   Review to see if account was created successfully")

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ ACCOUNT CREATION ATTEMPTED!")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"📸 All screenshots saved to: {screenshots_dir}")
        logger.info("   Review the screenshots to verify:")
        logger.info("   - step5: Did Create dialog open?")
        logger.info("   - step8: Was account created successfully?")
        logger.info("")
        logger.info("💡 If account was created, next step:")
        logger.info("   python scripts/python/jarvis_complete_outlook_setup_with_password.py")

        return True

    except ImportError:
        logger.error("❌ Required modules not available")
        logger.info("   Install: pip install pyautogui pygetwindow pillow")
        return False
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = create_account_with_vision()
    sys.exit(0 if success else 1)
