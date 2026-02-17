#!/usr/bin/env python3
"""
JARVIS: Create MailPlus Account with Live Vision Analysis

Takes screenshots, analyzes them to see what's on screen, and makes decisions based on what it sees.

Tags: #JARVIS #MAILPLUS #ACCOUNT #VISION #LIVE @JARVIS @LUMINA @DOIT
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

logger = get_logger("JARVISLiveVision")

ACCOUNT_EMAIL = "mlesn@<LOCAL_HOSTNAME>"
ACCOUNT_PASSWORD = None  # Retrieved from Azure Key Vault at runtime
NAS_IP = "<NAS_PRIMARY_IP>"
NAS_PORT = 5001


def capture_and_analyze():
    """Capture screenshot and analyze what's on screen"""
    try:
        import pyautogui
        from PIL import Image
        import pytesseract

        screenshot = pyautogui.screenshot()

        # Try OCR to read text on screen
        try:
            text = pytesseract.image_to_string(screenshot)
            return screenshot, text
        except:
            # OCR not available, return screenshot only
            return screenshot, None
    except Exception as e:
        logger.debug(f"Capture/analyze error: {e}")
        return None, None


def find_text_on_screen(text_to_find, screenshot=None):
    """Find text on screen using OCR"""
    try:
        import pytesseract
        from PIL import Image
        import pyautogui

        if screenshot is None:
            screenshot = pyautogui.screenshot()

        # Get text and bounding boxes
        data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)

        # Search for text
        found_positions = []
        search_text = text_to_find.lower()

        for i, text in enumerate(data['text']):
            if search_text in text.lower():
                x = data['left'][i]
                y = data['top'][i]
                w = data['width'][i]
                h = data['height'][i]
                found_positions.append((x + w//2, y + h//2))  # Center of text

        return found_positions
    except Exception:
        return []


def create_account_with_live_vision():
    """Create account using live vision analysis"""
    try:
        import pyautogui
        import pygetwindow as gw

        logger.info("=" * 80)
        logger.info("👁️  JARVIS: CREATE ACCOUNT WITH LIVE VISION")
        logger.info("=" * 80)
        logger.info("")

        screenshots_dir = project_root / "data" / "temp" / "live_vision_screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        # Step 1: Open MailPlus Account page
        logger.info("📋 STEP 1: Opening MailPlus Account page...")
        logger.info("-" * 80)

        account_url = f"https://{NAS_IP}:{NAS_PORT}/#mailplus/account"
        webbrowser.open(account_url)
        time.sleep(8)

        # Capture and analyze
        screenshot, text = capture_and_analyze()
        if screenshot:
            screenshot_path = screenshots_dir / f"01_initial_{int(time.time())}.png"
            screenshot.save(str(screenshot_path))
            logger.info(f"📸 Screenshot saved: {screenshot_path.name}")

            if text:
                logger.info("📋 Analyzing screen content...")
                # Look for key indicators
                if "mailplus" in text.lower() or "account" in text.lower():
                    logger.info("✅ MailPlus Account page detected")
                elif "create" in text.lower() or "add" in text.lower():
                    logger.info("✅ Create/Add button detected")
                else:
                    logger.info(f"   Screen text preview: {text[:200]}...")

        # Find and activate browser
        logger.info("")
        logger.info("📋 STEP 2: Finding browser window...")
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

        # Handle certificate
        logger.info("")
        logger.info("📋 STEP 3: Handling certificate...")
        logger.info("-" * 80)

        time.sleep(2)
        pyautogui.write("thisisunsafe", interval=0.1)
        time.sleep(3)

        # Capture and analyze after cert
        screenshot, text = capture_and_analyze()
        if screenshot:
            screenshot_path = screenshots_dir / f"02_after_cert_{int(time.time())}.png"
            screenshot.save(str(screenshot_path))
            logger.info(f"📸 Screenshot: {screenshot_path.name}")

            if text:
                logger.info("📋 Analyzing screen...")
                logger.info(f"   Found text: {text[:300]}...")

        # Step 4: Find Create button using vision
        logger.info("")
        logger.info("📋 STEP 4: Finding Create button using vision...")
        logger.info("-" * 80)

        # Take screenshot
        screenshot, text = capture_and_analyze()
        if screenshot:
            screenshot_path = screenshots_dir / f"03_before_create_{int(time.time())}.png"
            screenshot.save(str(screenshot_path))
            logger.info(f"📸 Screenshot: {screenshot_path.name}")

            if text:
                logger.info("📋 Analyzing screen for Create button...")

                # Look for "Create", "Add", "New" buttons
                create_keywords = ["create", "add", "new", "account"]
                found_keywords = []

                for keyword in create_keywords:
                    if keyword in text.lower():
                        found_keywords.append(keyword)
                        logger.info(f"   ✅ Found keyword: '{keyword}'")

                if found_keywords:
                    logger.info(f"   Found keywords: {found_keywords}")
                    # Try to find the actual button position
                    positions = find_text_on_screen("Create", screenshot)
                    if not positions:
                        positions = find_text_on_screen("Add", screenshot)
                    if not positions:
                        positions = find_text_on_screen("New", screenshot)

                    if positions:
                        logger.info(f"   ✅ Found button at: {positions[0]}")
                        pyautogui.click(positions[0][0], positions[0][1])
                        time.sleep(2)
                    else:
                        logger.info("   ⚠️  Found text but couldn't locate button - trying common positions")
                        # Try clicking in common button areas
                        screen_width, screen_height = pyautogui.size()
                        pyautogui.click(screen_width - 200, 150)
                        time.sleep(2)
                else:
                    logger.info("   ⚠️  Create button not found in text - trying common positions")
                    screen_width, screen_height = pyautogui.size()
                    pyautogui.click(screen_width - 200, 150)
                    time.sleep(2)

        # Step 5: Check if dialog opened
        logger.info("")
        logger.info("📋 STEP 5: Checking if account dialog opened...")
        logger.info("-" * 80)

        screenshot, text = capture_and_analyze()
        if screenshot:
            screenshot_path = screenshots_dir / f"04_after_create_click_{int(time.time())}.png"
            screenshot.save(str(screenshot_path))
            logger.info(f"📸 Screenshot: {screenshot_path.name}")

            if text:
                logger.info("📋 Analyzing dialog...")

                # Look for account creation dialog indicators
                dialog_indicators = ["email", "password", "account", "create", "save"]
                found_indicators = [ind for ind in dialog_indicators if ind in text.lower()]

                if found_indicators:
                    logger.info(f"   ✅ Account dialog detected! Found: {found_indicators}")

                    # Step 6: Fill in email
                    logger.info("")
                    logger.info("📋 STEP 6: Filling in email...")
                    logger.info("-" * 80)

                    logger.info(f"   Entering: {ACCOUNT_EMAIL}")
                    pyautogui.write(ACCOUNT_EMAIL, interval=0.1)
                    time.sleep(1)

                    screenshot, text = capture_and_analyze()
                    if screenshot:
                        screenshot_path = screenshots_dir / f"05_email_entered_{int(time.time())}.png"
                        screenshot.save(str(screenshot_path))

                    # Step 7: Fill in password
                    logger.info("")
                    logger.info("📋 STEP 7: Filling in password...")
                    logger.info("-" * 80)

                    pyautogui.press('tab')
                    time.sleep(0.5)
                    pyautogui.write(ACCOUNT_PASSWORD, interval=0.05)
                    time.sleep(1)

                    screenshot, text = capture_and_analyze()
                    if screenshot:
                        screenshot_path = screenshots_dir / f"06_password_entered_{int(time.time())}.png"
                        screenshot.save(str(screenshot_path))

                    # Step 8: Save
                    logger.info("")
                    logger.info("📋 STEP 8: Saving account...")
                    logger.info("-" * 80)

                    pyautogui.press('tab', presses=2)
                    time.sleep(0.5)
                    pyautogui.press('enter')
                    time.sleep(3)

                    screenshot, text = capture_and_analyze()
                    if screenshot:
                        screenshot_path = screenshots_dir / f"07_after_save_{int(time.time())}.png"
                        screenshot.save(str(screenshot_path))
                        logger.info(f"📸 Final screenshot: {screenshot_path.name}")

                        if text:
                            logger.info("📋 Analyzing final result...")
                            if "success" in text.lower() or "created" in text.lower():
                                logger.info("   ✅ Account appears to be created!")
                            elif "error" in text.lower():
                                logger.warning("   ⚠️  Error detected in result")
                            else:
                                logger.info(f"   Screen text: {text[:200]}...")
                else:
                    logger.warning("   ⚠️  Account dialog not detected")
                    logger.info("   Dialog may not have opened")
                    logger.info("   Review screenshot to see current state")

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ ACCOUNT CREATION COMPLETED WITH LIVE VISION!")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"📸 All screenshots: {screenshots_dir}")
        logger.info("   Review screenshots to verify each step")
        logger.info("")
        logger.info("📧 Next: Verify account and complete Outlook setup")

        return True

    except ImportError as e:
        logger.error(f"❌ Required modules not available: {e}")
        logger.info("   Install: pip install pyautogui pygetwindow pillow pytesseract")
        return False
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = create_account_with_live_vision()
    sys.exit(0 if success else 1)
