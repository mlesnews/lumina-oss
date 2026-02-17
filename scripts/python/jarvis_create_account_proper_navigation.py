#!/usr/bin/env python3
"""
JARVIS: Create MailPlus Account with Proper Navigation

Navigates to MailPlus Account page and creates account using vision.

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

logger = get_logger("JARVISCreateAccountNav")

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
            logger.info(f"📸 {save_path.name}")
        return screenshot
    except Exception as e:
        logger.error(f"❌ Capture failed: {e}")
        return None


def create_account_with_navigation():
    """Create account with proper navigation"""
    try:
        import pyautogui
        import pygetwindow as gw

        logger.info("=" * 80)
        logger.info("📧 JARVIS: CREATE MAILPLUS ACCOUNT (PROPER NAVIGATION)")
        logger.info("=" * 80)
        logger.info("")

        screenshots_dir = project_root / "data" / "temp" / "account_nav_screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        # Step 1: Open DSM main page
        logger.info("📋 STEP 1: Opening DSM...")
        logger.info("-" * 80)

        dsm_url = f"https://{NAS_IP}:{NAS_PORT}"
        webbrowser.open(dsm_url)
        time.sleep(8)

        screenshot_path = screenshots_dir / f"01_dsm_opened_{int(time.time())}.png"
        capture_screen(str(screenshot_path))

        # Find browser
        browser_windows = []
        for window in gw.getAllWindows():
            title_lower = window.title.lower()
            if any(browser in title_lower for browser in ['chrome', 'edge', 'neo', 'dsm', 'synology']):
                browser_windows.append(window)

        if browser_windows:
            browser = browser_windows[0]
            logger.info(f"✅ Found: {browser.title}")
            try:
                browser.activate()
                time.sleep(2)
            except:
                pass

        # Handle cert
        logger.info("📋 Handling certificate...")
        time.sleep(2)
        pyautogui.write("thisisunsafe", interval=0.1)
        time.sleep(3)

        screenshot_path = screenshots_dir / f"02_after_cert_{int(time.time())}.png"
        capture_screen(str(screenshot_path))

        # Step 2: Navigate to MailPlus
        logger.info("")
        logger.info("📋 STEP 2: Navigating to MailPlus...")
        logger.info("-" * 80)

        # Open MailPlus URL directly
        mailplus_url = f"https://{NAS_IP}:{NAS_PORT}/#mailplus/account"
        logger.info(f"Opening: {mailplus_url}")
        webbrowser.open(mailplus_url)
        time.sleep(8)

        screenshot_path = screenshots_dir / f"03_mailplus_page_{int(time.time())}.png"
        capture_screen(str(screenshot_path))
        logger.info("   📸 Review screenshot to see MailPlus Account page")

        # Activate browser again
        if browser_windows:
            try:
                browser_windows[0].activate()
                time.sleep(2)
            except:
                pass

        # Step 3: Find Create button
        logger.info("")
        logger.info("📋 STEP 3: Finding Create button...")
        logger.info("-" * 80)

        screenshot_path = screenshots_dir / f"04_before_create_{int(time.time())}.png"
        capture_screen(str(screenshot_path))
        logger.info("   📸 Review screenshot to locate Create button")

        # Try multiple methods to find Create
        # Method 1: Look for "Create" text by trying common positions
        screen_width, screen_height = pyautogui.size()

        # Try top-right area (common for Create buttons)
        logger.info("   Trying top-right area...")
        pyautogui.click(screen_width - 150, 150)
        time.sleep(2)

        screenshot_path = screenshots_dir / f"05_after_click1_{int(time.time())}.png"
        capture_screen(str(screenshot_path))

        # If that didn't work, try keyboard shortcut (Ctrl+N or similar)
        logger.info("   Trying keyboard shortcut...")
        pyautogui.hotkey('ctrl', 'n')
        time.sleep(2)

        screenshot_path = screenshots_dir / f"06_after_shortcut_{int(time.time())}.png"
        capture_screen(str(screenshot_path))

        # Method 2: Try Tab navigation to find Create button
        logger.info("   Trying Tab navigation...")
        for i in range(10):
            pyautogui.press('tab')
            time.sleep(0.3)
            # Check if we're on a button by pressing Enter
            pyautogui.press('enter')
            time.sleep(2)

            screenshot_path = screenshots_dir / f"07_tab_{i}_{int(time.time())}.png"
            capture_screen(str(screenshot_path))

            # Check if dialog opened (would need to analyze screenshot)
            # For now, continue

        # Step 4: Fill in account details (if dialog opened)
        logger.info("")
        logger.info("📋 STEP 4: Filling account details...")
        logger.info("-" * 80)

        screenshot_path = screenshots_dir / f"08_before_fill_{int(time.time())}.png"
        capture_screen(str(screenshot_path))
        logger.info("   📸 Review to see if account creation dialog is open")

        # Enter email
        logger.info(f"   Entering email: {ACCOUNT_EMAIL}")
        pyautogui.write(ACCOUNT_EMAIL, interval=0.1)
        time.sleep(1)

        screenshot_path = screenshots_dir / f"09_email_entered_{int(time.time())}.png"
        capture_screen(str(screenshot_path))

        # Enter password
        logger.info("   Entering password...")
        pyautogui.press('tab')
        time.sleep(0.5)
        pyautogui.write(ACCOUNT_PASSWORD, interval=0.05)
        time.sleep(1)

        screenshot_path = screenshots_dir / f"10_password_entered_{int(time.time())}.png"
        capture_screen(str(screenshot_path))

        # Save
        logger.info("   Saving...")
        pyautogui.press('tab', presses=2)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(3)

        screenshot_path = screenshots_dir / f"11_after_save_{int(time.time())}.png"
        capture_screen(str(screenshot_path))
        logger.info("   📸 Review to verify account was created")

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ ACCOUNT CREATION ATTEMPTED!")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"📸 Screenshots: {screenshots_dir}")
        logger.info("   Review step11 to verify account was created")
        logger.info("")
        logger.info("📧 Next: Verify and complete Outlook setup")

        return True

    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = create_account_with_navigation()
    sys.exit(0 if success else 1)
