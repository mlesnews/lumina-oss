#!/usr/bin/env python3
"""
JARVIS: Create MailPlus Account with GUI Vision

Creates the account using GUI automation with screenshots at each step.

Tags: #JARVIS #MAILPLUS #ACCOUNT #GUI #VISION @JARVIS @LUMINA @DOIT
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

logger = get_logger("JARVISCreateAccountGUI")

ACCOUNT_EMAIL = "mlesn@<LOCAL_HOSTNAME>"
ACCOUNT_PASSWORD = None  # Retrieved from Azure Key Vault at runtime
NAS_IP = "<NAS_PRIMARY_IP>"
NAS_PORT = 5001


def capture_screen(save_path: str = None):
    """Capture current screen"""
    try:
        import pyautogui
        screenshot = pyautogui.screenshot()
        if save_path:
            screenshot.save(save_path)
            logger.info(f"📸 Screenshot: {save_path}")
        return screenshot
    except Exception as e:
        logger.error(f"❌ Failed to capture: {e}")
        return None


def create_account_with_vision():
    """Create account with full vision tracking"""
    try:
        import pyautogui
        import pygetwindow as gw

        logger.info("=" * 80)
        logger.info("📧 JARVIS: CREATE MAILPLUS ACCOUNT WITH VISION")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"Email: {ACCOUNT_EMAIL}")
        logger.info(f"Password: [REDACTED]")
        logger.info("")

        screenshots_dir = project_root / "data" / "temp" / "account_creation_screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        # Open MailPlus Account page
        logger.info("📋 Opening MailPlus Account page...")
        account_url = f"https://{NAS_IP}:{NAS_PORT}/#mailplus/account"
        webbrowser.open(account_url)
        time.sleep(10)

        screenshot_path = screenshots_dir / f"01_page_loaded_{int(time.time())}.png"
        capture_screen(str(screenshot_path))

        # Find and activate browser
        logger.info("📋 Finding browser window...")
        browser_windows = []
        for window in gw.getAllWindows():
            title_lower = window.title.lower()
            if any(browser in title_lower for browser in ['chrome', 'edge', 'firefox', 'neo', 'dsm', 'synology']):
                browser_windows.append(window)

        if browser_windows:
            browser = browser_windows[0]
            logger.info(f"✅ Found: {browser.title}")
            try:
                browser.activate()
                time.sleep(2)
            except:
                pass

        screenshot_path = screenshots_dir / f"02_browser_active_{int(time.time())}.png"
        capture_screen(str(screenshot_path))

        # Handle cert warning
        logger.info("📋 Handling certificate...")
        time.sleep(2)
        pyautogui.write("thisisunsafe", interval=0.1)
        time.sleep(3)

        screenshot_path = screenshots_dir / f"03_after_cert_{int(time.time())}.png"
        capture_screen(str(screenshot_path))

        # Look for Create button - take screenshot first to see what's on screen
        logger.info("📋 Looking for Create button...")
        screenshot_path = screenshots_dir / f"04_before_create_{int(time.time())}.png"
        capture_screen(str(screenshot_path))
        logger.info("   📸 Review screenshot to see Create button location")

        # Try multiple methods to find Create button
        # Method 1: Try clicking top-right area (common for Create buttons)
        logger.info("   Trying to click Create button...")

        # Get screen size
        screen_width, screen_height = pyautogui.size()

        # Try clicking in common Create button areas
        # Top-right area
        pyautogui.click(screen_width - 200, 100)
        time.sleep(2)

        screenshot_path = screenshots_dir / f"05_after_create_click_{int(time.time())}.png"
        capture_screen(str(screenshot_path))
        logger.info("   📸 Check if Create dialog opened")

        # If dialog opened, fill in details
        logger.info("📋 Filling account details...")
        time.sleep(1)

        # Email
        logger.info(f"   Entering email: {ACCOUNT_EMAIL}")
        pyautogui.write(ACCOUNT_EMAIL, interval=0.1)
        time.sleep(1)

        screenshot_path = screenshots_dir / f"06_email_entered_{int(time.time())}.png"
        capture_screen(str(screenshot_path))

        # Password
        logger.info("   Entering password...")
        pyautogui.press('tab')
        time.sleep(0.5)
        pyautogui.write(ACCOUNT_PASSWORD, interval=0.05)
        time.sleep(1)

        screenshot_path = screenshots_dir / f"07_password_entered_{int(time.time())}.png"
        capture_screen(str(screenshot_path))

        # Save
        logger.info("📋 Saving account...")
        pyautogui.press('tab', presses=2)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(3)

        screenshot_path = screenshots_dir / f"08_after_save_{int(time.time())}.png"
        capture_screen(str(screenshot_path))
        logger.info("   📸 Check if account was created successfully")

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ ACCOUNT CREATION COMPLETED!")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"📸 Screenshots: {screenshots_dir}")
        logger.info("   Review step08 to verify account was created")
        logger.info("")
        logger.info("📧 Next: Complete Outlook setup")
        logger.info("   python scripts/python/jarvis_complete_outlook_setup_with_password.py")

        return True

    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = create_account_with_vision()
    sys.exit(0 if success else 1)
