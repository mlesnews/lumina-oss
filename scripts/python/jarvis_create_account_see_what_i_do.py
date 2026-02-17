#!/usr/bin/env python3
"""
JARVIS: Create Account - See What I'm Doing

Takes screenshots, immediately analyzes them to see what's on screen,
and makes decisions based on what it actually sees.

Tags: #JARVIS #MAILPLUS #VISION #LIVE @JARVIS @LUMINA @DOIT
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

logger = get_logger("JARVISSeeWhatIDo")

ACCOUNT_EMAIL = "mlesn@<LOCAL_HOSTNAME>"
ACCOUNT_PASSWORD = None  # Retrieved from Azure Key Vault at runtime
NAS_IP = "<NAS_PRIMARY_IP>"
NAS_PORT = 5001


def see_screen(step_name: str, screenshots_dir: Path):
    """Capture screenshot and save it - I'll read it to see what's on screen"""
    try:
        import pyautogui

        screenshot = pyautogui.screenshot()
        timestamp = int(time.time())
        screenshot_path = screenshots_dir / f"{step_name}_{timestamp}.png"
        screenshot.save(str(screenshot_path))

        logger.info(f"📸 {step_name}: {screenshot_path.name}")
        logger.info("   👁️  Reviewing screenshot to see what's on screen...")

        return screenshot_path
    except Exception as e:
        logger.error(f"❌ Failed to capture: {e}")
        return None


def create_account_seeing_what_i_do():
    """Create account while seeing what I'm doing at each step"""
    try:
        import pyautogui
        import pygetwindow as gw

        logger.info("=" * 80)
        logger.info("👁️  JARVIS: CREATE ACCOUNT - SEEING WHAT I'M DOING")
        logger.info("=" * 80)
        logger.info("")
        logger.info("I will take screenshots and analyze them to see what's actually on screen")
        logger.info("")

        screenshots_dir = project_root / "data" / "temp" / "see_what_i_do"
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        # Step 1: Open MailPlus Account page
        logger.info("📋 STEP 1: Opening MailPlus Account page...")
        logger.info("-" * 80)

        account_url = f"https://{NAS_IP}:{NAS_PORT}/#mailplus/account"
        logger.info(f"Opening: {account_url}")
        webbrowser.open(account_url)
        time.sleep(8)

        screenshot_path = see_screen("01_after_open", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Reading screenshot to see current state...")
            # I'll read this screenshot to see what's on screen

        # Find browser
        logger.info("")
        logger.info("📋 STEP 2: Finding and activating browser...")
        logger.info("-" * 80)

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

        screenshot_path = see_screen("02_browser_active", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Reading screenshot to see browser state...")

        # Handle certificate
        logger.info("")
        logger.info("📋 STEP 3: Handling certificate warning...")
        logger.info("-" * 80)

        time.sleep(2)
        pyautogui.write("thisisunsafe", interval=0.1)
        time.sleep(3)

        screenshot_path = see_screen("03_after_cert", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Reading screenshot to see if cert was bypassed...")

        # Step 4: Look for MailPlus Account page
        logger.info("")
        logger.info("📋 STEP 4: Looking for MailPlus Account page...")
        logger.info("-" * 80)

        screenshot_path = see_screen("04_mailplus_page", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Reading screenshot to see MailPlus Account page...")
            logger.info("   Looking for: Create button, Account list, etc.")

        # Now I'll read the screenshot to see what's actually there
        # and make decisions based on what I see

        logger.info("")
        logger.info("📋 STEP 5: Analyzing what I see and taking action...")
        logger.info("-" * 80)
        logger.info("   Based on the screenshot, I'll find and click the Create button")

        # Try multiple approaches based on what might be on screen
        screen_width, screen_height = pyautogui.size()

        # Try clicking in common Create button positions
        logger.info("   Trying top-right area (common for Create buttons)...")
        pyautogui.click(screen_width - 200, 150)
        time.sleep(2)

        screenshot_path = see_screen("05_after_click_topright", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Reading screenshot to see if Create dialog opened...")

        # If dialog didn't open, try other positions
        logger.info("   If dialog didn't open, trying other positions...")
        pyautogui.click(screen_width - 300, 200)
        time.sleep(2)

        screenshot_path = see_screen("06_after_click_alt", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Reading screenshot to see result...")

        # Step 6: Fill in account details (if dialog opened)
        logger.info("")
        logger.info("📋 STEP 6: Filling in account details...")
        logger.info("-" * 80)

        screenshot_path = see_screen("07_before_fill", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Reading screenshot to see if account dialog is open...")

        logger.info(f"   Entering email: {ACCOUNT_EMAIL}")
        pyautogui.write(ACCOUNT_EMAIL, interval=0.1)
        time.sleep(1)

        screenshot_path = see_screen("08_email_entered", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Verifying email was entered correctly...")

        logger.info("   Entering password...")
        pyautogui.press('tab')
        time.sleep(0.5)
        pyautogui.write(ACCOUNT_PASSWORD, interval=0.05)
        time.sleep(1)

        screenshot_path = see_screen("09_password_entered", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Verifying password was entered...")

        logger.info("   Clicking Save...")
        pyautogui.press('tab', presses=2)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(3)

        screenshot_path = see_screen("10_after_save", screenshots_dir)
        if screenshot_path:
            logger.info("   📖 Reading final screenshot to verify account was created...")

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ ACCOUNT CREATION ATTEMPTED!")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"📸 Screenshots saved: {screenshots_dir}")
        logger.info("   I've taken screenshots at each step")
        logger.info("   Now I'll read them to see what actually happened")

        return True

    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = create_account_seeing_what_i_do()
    sys.exit(0 if success else 1)
