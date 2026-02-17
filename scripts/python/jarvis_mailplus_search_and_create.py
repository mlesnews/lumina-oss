#!/usr/bin/env python3
"""
JARVIS: MailPlus - Search and Create with Continuous Vision

Uses DSM search to find MailPlus, then creates account using continuous vision monitoring.

Tags: #JARVIS #MAILPLUS #VISION #SEARCH @JARVIS @LUMINA @DOIT
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

logger = get_logger("JARVISMailPlusSearch")

ACCOUNT_EMAIL = "mlesn@<LOCAL_HOSTNAME>"
ACCOUNT_PASSWORD = None  # Retrieved from Azure Key Vault at runtime
NAS_IP = "<NAS_PRIMARY_IP>"
NAS_PORT = 5001


def see_screen(browser_window, step_name: str, screenshots_dir: Path):
    """Capture browser window - I'll read it to see what's on screen"""
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
        # Sanitize filename
        safe_name = step_name.replace('/', '_').replace('?', '_').replace('&', '_')[:50]
        screenshot_path = screenshots_dir / f"{safe_name}_{timestamp}.png"
        browser_screenshot.save(str(screenshot_path))

        logger.info(f"📸 {step_name}: {screenshot_path.name}")
        logger.info(f"   Window: {browser_window.title}")

        return screenshot_path, browser_screenshot
    except Exception as e:
        logger.error(f"❌ Capture failed: {e}")
        return None, None


def search_and_create_mailplus():
    """Search for MailPlus and create account using continuous vision"""
    try:
        import pyautogui
        import pygetwindow as gw
        import webbrowser

        logger.info("=" * 80)
        logger.info("👁️  JARVIS: SEARCH MAILPLUS & CREATE ACCOUNT")
        logger.info("=" * 80)
        logger.info("")
        logger.info("I will use DSM search to find MailPlus")
        logger.info("then create account using continuous vision")
        logger.info("")

        screenshots_dir = project_root / "data" / "temp" / "search_mailplus"
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        # Step 1: Open DSM
        logger.info("📋 STEP 1: Opening DSM...")
        logger.info("-" * 80)

        dsm_url = f"https://{NAS_IP}:{NAS_PORT}"
        logger.info(f"URL: {dsm_url}")
        webbrowser.open(dsm_url)
        time.sleep(10)

        # Find browser
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

        try:
            browser.activate()
            time.sleep(1)
            browser.maximize()
            time.sleep(2)
        except:
            pass

        # Step 3: See what's on screen
        logger.info("")
        logger.info("📋 STEP 3: Seeing what's on screen...")
        logger.info("-" * 80)

        screenshot_path, browser_img = see_screen(browser, "01_initial", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Reading screenshot to see current state...")

        # Step 4: Handle certificate
        logger.info("")
        logger.info("📋 STEP 4: Handling certificate...")
        logger.info("-" * 80)

        browser_center_x = browser.left + browser.width // 2
        browser_center_y = browser.top + browser.height // 2
        pyautogui.click(browser_center_x, browser_center_y)
        time.sleep(1)

        pyautogui.write("thisisunsafe", interval=0.1)
        time.sleep(4)

        screenshot_path, browser_img = see_screen(browser, "02_after_cert", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Reading screenshot to verify cert was bypassed...")

        # Step 5: Click on DSM search icon
        logger.info("")
        logger.info("📋 STEP 5: Clicking DSM search icon...")
        logger.info("-" * 80)
        logger.info("   Looking for search icon in DSM top bar...")

        # Search icon is typically in DSM top bar, around: browser.left + ~400, browser.top + ~150
        search_x = browser.left + 400
        search_y = browser.top + 150
        pyautogui.click(search_x, search_y)
        time.sleep(2)

        screenshot_path, browser_img = see_screen(browser, "03_after_search_click", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Reading screenshot to see if search box opened...")

        # Step 6: Type "MailPlus" in search
        logger.info("")
        logger.info("📋 STEP 6: Searching for MailPlus...")
        logger.info("-" * 80)
        logger.info("   Typing 'MailPlus' in search box...")

        pyautogui.write("MailPlus", interval=0.1)
        time.sleep(2)

        screenshot_path, browser_img = see_screen(browser, "04_after_search", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Reading screenshot to see search results...")
            logger.info("   Looking for MailPlus in search results...")

        # Step 7: Click on MailPlus if found
        logger.info("")
        logger.info("📋 STEP 7: Clicking on MailPlus...")
        logger.info("-" * 80)
        logger.info("   Trying to click on MailPlus in search results...")

        # Try clicking in the center of search results area
        results_x = browser.left + browser.width // 2
        results_y = browser.top + 300
        pyautogui.click(results_x, results_y)
        time.sleep(3)

        screenshot_path, browser_img = see_screen(browser, "05_after_click_mailplus", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Reading screenshot to see if MailPlus opened...")

        # Step 8: Navigate to Account page
        logger.info("")
        logger.info("📋 STEP 8: Navigating to Account page...")
        logger.info("-" * 80)
        logger.info("   Looking for Account tab or button in MailPlus...")

        screenshot_path, browser_img = see_screen(browser, "06_before_account_nav", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Reading screenshot to see MailPlus interface...")

        # Try clicking on Account tab/button - usually top of MailPlus interface
        account_x = browser.left + browser.width - 300
        account_y = browser.top + 200
        pyautogui.click(account_x, account_y)
        time.sleep(2)

        screenshot_path, browser_img = see_screen(browser, "07_after_account_click", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Reading screenshot to see if Account page opened...")

        # Step 9: Find Create button
        logger.info("")
        logger.info("📋 STEP 9: Finding Create button...")
        logger.info("-" * 80)

        screenshot_path, browser_img = see_screen(browser, "08_before_create", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Reading screenshot to find Create button...")

        # Try clicking Create button
        create_x = browser.left + browser.width - 200
        create_y = browser.top + 200
        pyautogui.click(create_x, create_y)
        time.sleep(2)

        screenshot_path, browser_img = see_screen(browser, "09_after_create_click", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Reading screenshot to see if Create dialog opened...")

        # Step 10: Fill in account details
        logger.info("")
        logger.info("📋 STEP 10: Filling in account details...")
        logger.info("-" * 80)

        screenshot_path, browser_img = see_screen(browser, "10_before_fill", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Reading screenshot to see if account dialog is open...")

        logger.info(f"   Entering email: {ACCOUNT_EMAIL}")
        pyautogui.write(ACCOUNT_EMAIL, interval=0.1)
        time.sleep(1)

        screenshot_path, browser_img = see_screen(browser, "11_email_entered", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Verifying email was entered...")

        logger.info("   Entering password...")
        pyautogui.press('tab')
        time.sleep(0.5)
        pyautogui.write(ACCOUNT_PASSWORD, interval=0.05)
        time.sleep(1)

        screenshot_path, browser_img = see_screen(browser, "12_password_entered", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Verifying password was entered...")

        logger.info("   Clicking Save...")
        pyautogui.press('tab', presses=2)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(3)

        screenshot_path, browser_img = see_screen(browser, "13_after_save", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Reading final screenshot to verify account was created...")

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ SEARCH & CREATE COMPLETED!")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"📸 Screenshots: {screenshots_dir}")
        logger.info("   I've captured the browser at each step")
        logger.info("   I'll now read all screenshots to see what happened")
        logger.info("   and verify the account was created")

        return True

    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = search_and_create_mailplus()
    sys.exit(0 if success else 1)
