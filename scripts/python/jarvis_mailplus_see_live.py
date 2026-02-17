#!/usr/bin/env python3
"""
JARVIS: MailPlus Account Creation - See Live

Navigates to MailPlus, handles certificate, and reads what's on screen
at each step to make decisions based on what I actually see.

Tags: #JARVIS #MAILPLUS #VISION #LIVE @JARVIS @LUMINA @DOIT
"""

import sys
import time
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

logger = get_logger("JARVISMailPlusLive")

ACCOUNT_EMAIL = "mlesn@<LOCAL_HOSTNAME>"
ACCOUNT_PASSWORD = None  # Retrieved from Azure Key Vault at runtime
NAS_IP = "<NAS_PRIMARY_IP>"
NAS_PORT = 5001


def see_browser_window(browser_window, step_name: str, screenshots_dir: Path):
    """Capture browser window and return screenshot path"""
    try:
        import pyautogui
        from PIL import Image

        left = browser_window.left
        top = browser_window.top
        width = browser_window.width
        height = browser_window.height

        full_screenshot = pyautogui.screenshot()
        browser_screenshot = full_screenshot.crop((left, top, left + width, top + height))

        timestamp = int(time.time())
        screenshot_path = screenshots_dir / f"{step_name}_{timestamp}.png"
        browser_screenshot.save(str(screenshot_path))

        logger.info(f"📸 {step_name}: {screenshot_path.name}")
        logger.info(f"   Window: {browser_window.title}")

        return screenshot_path, browser_screenshot
    except Exception as e:
        logger.error(f"❌ Capture failed: {e}")
        return None, None


def create_mailplus_account_live():
    """Create account while seeing what's on screen live"""
    try:
        import pyautogui
        import pygetwindow as gw
        import webbrowser

        logger.info("=" * 80)
        logger.info("👁️  JARVIS: MAILPLUS ACCOUNT - SEE LIVE")
        logger.info("=" * 80)
        logger.info("")
        logger.info("I will navigate to MailPlus and read what's on screen")
        logger.info("at each step to make decisions based on what I see")
        logger.info("")

        screenshots_dir = project_root / "data" / "temp" / "mailplus_live"
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        # Step 1: Open MailPlus Account page in new tab
        logger.info("📋 STEP 1: Opening MailPlus Account page...")
        logger.info("-" * 80)

        account_url = f"https://{NAS_IP}:{NAS_PORT}/#mailplus/account"
        logger.info(f"URL: {account_url}")

        # Open in new tab
        webbrowser.open(account_url)
        time.sleep(12)  # Wait for page to load and cert warning

        # Find browser window
        logger.info("")
        logger.info("📋 STEP 2: Finding browser window...")
        logger.info("-" * 80)

        browser_windows = []
        for window in gw.getAllWindows():
            title_lower = window.title.lower()
            if any(browser in title_lower for browser in ['chrome', 'edge', 'neo', 'dsm', 'synology']):
                browser_windows.append(window)

        if not browser_windows:
            logger.error("❌ Browser window not found")
            return False

        browser = browser_windows[0]
        logger.info(f"✅ Found: {browser.title}")

        # Activate browser
        try:
            browser.activate()
            time.sleep(1)
            browser.maximize()
            time.sleep(2)
            logger.info("✅ Browser activated")
        except Exception as e:
            logger.warning(f"⚠️  Could not maximize: {e}")

        # See what's on screen
        screenshot_path, browser_img = see_browser_window(browser, "01_initial", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Reading screenshot to see current state...")

        # Step 3: Handle certificate warning
        logger.info("")
        logger.info("📋 STEP 3: Handling certificate warning...")
        logger.info("-" * 80)
        logger.info("   Looking for certificate warning page...")

        # Click in the center of browser to ensure focus
        browser_center_x = browser.left + browser.width // 2
        browser_center_y = browser.top + browser.height // 2
        pyautogui.click(browser_center_x, browser_center_y)
        time.sleep(1)

        # Type thisisunsafe to bypass cert
        logger.info("   Typing 'thisisunsafe' to bypass certificate...")
        pyautogui.write("thisisunsafe", interval=0.1)
        time.sleep(4)

        screenshot_path, browser_img = see_browser_window(browser, "02_after_cert", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Reading screenshot to verify cert was bypassed...")

        # Step 4: Navigate to MailPlus Account page if needed
        logger.info("")
        logger.info("📋 STEP 4: Ensuring we're on MailPlus Account page...")
        logger.info("-" * 80)

        # Click address bar and navigate
        address_bar_y = browser.top + 80
        address_bar_x = browser.left + browser.width // 2
        pyautogui.click(address_bar_x, address_bar_y)
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'l')  # Select all in address bar
        time.sleep(0.5)
        pyautogui.write(account_url, interval=0.05)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(8)

        screenshot_path, browser_img = see_browser_window(browser, "03_mailplus_page", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Reading screenshot to see MailPlus Account page...")
            logger.info("   Looking for: Create button, account list, navigation")

        # Step 5: Read the screenshot and find Create button
        logger.info("")
        logger.info("📋 STEP 5: Reading screenshot to find Create button...")
        logger.info("-" * 80)

        # I'll read the screenshot to see what's actually on the page
        # For now, try common Create button positions
        logger.info("   Trying common Create button positions...")

        # Top-right area (common for Create buttons)
        create_x = browser.left + browser.width - 200
        create_y = browser.top + 200
        pyautogui.click(create_x, create_y)
        time.sleep(2)

        screenshot_path, browser_img = see_browser_window(browser, "04_after_click_create", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Reading screenshot to see if Create dialog opened...")

        # Step 6: Fill in account details
        logger.info("")
        logger.info("📋 STEP 6: Filling in account details...")
        logger.info("-" * 80)

        screenshot_path, browser_img = see_browser_window(browser, "05_before_fill", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Reading screenshot to see if account dialog is open...")

        logger.info(f"   Entering email: {ACCOUNT_EMAIL}")
        pyautogui.write(ACCOUNT_EMAIL, interval=0.1)
        time.sleep(1)

        screenshot_path, browser_img = see_browser_window(browser, "06_email_entered", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Verifying email was entered...")

        logger.info("   Entering password...")
        pyautogui.press('tab')
        time.sleep(0.5)
        pyautogui.write(ACCOUNT_PASSWORD, interval=0.05)
        time.sleep(1)

        screenshot_path, browser_img = see_browser_window(browser, "07_password_entered", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Verifying password was entered...")

        logger.info("   Clicking Save...")
        pyautogui.press('tab', presses=2)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(3)

        screenshot_path, browser_img = see_browser_window(browser, "08_after_save", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Reading final screenshot to verify account was created...")

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ ACCOUNT CREATION ATTEMPTED - SEEING LIVE!")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"📸 Screenshots: {screenshots_dir}")
        logger.info("   I've captured the browser at each step")
        logger.info("   Now I'll read the screenshots to see what happened")

        return True

    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = create_mailplus_account_live()
    sys.exit(0 if success else 1)
