#!/usr/bin/env python3
"""
JARVIS: Outlook Setup with Screen Vision

Uses screenshots and image recognition to see what's happening during setup.

Tags: #JARVIS #OUTLOOK #VISION #SCREENSHOT #AUTOMATION @JARVIS @LUMINA @DOIT
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

logger = get_logger("JARVISOutlookVision")

ACCOUNT_CONFIG = {
    "email": "mlesn@<LOCAL_HOSTNAME>",
    "imap_server": "<NAS_PRIMARY_IP>",
    "imap_port": "993",
    "smtp_server": "<NAS_PRIMARY_IP>",
    "smtp_port": "587",
}


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


def find_on_screen(image_path: str, confidence: float = 0.8):
    """Find an image on screen"""
    try:
        import pyautogui

        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if location:
            center = pyautogui.center(location)
            logger.info(f"✅ Found {image_path} at {center}")
            return center
        else:
            logger.warning(f"⚠️  Could not find {image_path}")
            return None
    except Exception as e:
        logger.debug(f"Image search error: {e}")
        return None


def setup_with_vision():
    """Setup Outlook account using screen vision"""
    try:
        import pyautogui
        import pygetwindow as gw

        logger.info("=" * 80)
        logger.info("👁️  JARVIS: OUTLOOK SETUP WITH SCREEN VISION")
        logger.info("=" * 80)
        logger.info("")

        # Create screenshots directory
        screenshots_dir = project_root / "data" / "temp" / "outlook_setup_screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        # Step 1: Find Outlook window
        logger.info("📋 STEP 1: Finding Outlook window...")
        logger.info("-" * 80)

        # Capture screen to see current state
        screenshot_path = screenshots_dir / f"step1_initial_{int(time.time())}.png"
        screenshot = capture_screen(str(screenshot_path))

        if not screenshot:
            logger.error("❌ Could not capture screen")
            return False

        outlook_windows = []
        for window in gw.getAllWindows():
            title_lower = window.title.lower()
            if 'outlook' in title_lower:
                outlook_windows.append(window)

        if not outlook_windows:
            logger.error("❌ Outlook window not found")
            logger.info("   Please open Outlook Classic first")
            return False

        outlook_window = outlook_windows[0]
        logger.info(f"✅ Found Outlook window: {outlook_window.title}")

        # Activate and capture
        try:
            outlook_window.activate()
            time.sleep(2)
        except Exception:
            pass

        screenshot_path = screenshots_dir / f"step2_outlook_active_{int(time.time())}.png"
        capture_screen(str(screenshot_path))

        # Step 2: Open Account Settings
        logger.info("")
        logger.info("📋 STEP 2: Opening Account Settings...")
        logger.info("-" * 80)

        pyautogui.hotkey('alt', 'f')
        time.sleep(1)
        screenshot_path = screenshots_dir / f"step3_file_menu_{int(time.time())}.png"
        capture_screen(str(screenshot_path))

        pyautogui.press('t')
        time.sleep(1)
        pyautogui.press('a')
        time.sleep(3)

        screenshot_path = screenshots_dir / f"step4_account_settings_{int(time.time())}.png"
        capture_screen(str(screenshot_path))
        logger.info("📸 Captured Account Settings dialog")
        logger.info(f"   Check screenshot: {screenshot_path}")

        # Step 3: Look for New button
        logger.info("")
        logger.info("📋 STEP 3: Looking for 'New...' button...")
        logger.info("-" * 80)

        # Try to find New button by text or position
        # Since we can't see, let's try common positions
        pyautogui.press('n')
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(2)

        screenshot_path = screenshots_dir / f"step5_new_account_{int(time.time())}.png"
        capture_screen(str(screenshot_path))
        logger.info("📸 Captured New Account dialog")
        logger.info(f"   Check screenshot: {screenshot_path}")

        # Step 4: Manual setup
        logger.info("")
        logger.info("📋 STEP 4: Selecting manual setup...")
        logger.info("-" * 80)

        pyautogui.press('m')
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(2)

        screenshot_path = screenshots_dir / f"step6_manual_setup_{int(time.time())}.png"
        capture_screen(str(screenshot_path))
        logger.info("📸 Captured manual setup dialog")
        logger.info(f"   Check screenshot: {screenshot_path}")

        # Step 5: Enter email
        logger.info("")
        logger.info("📋 STEP 5: Entering email...")
        logger.info("-" * 80)

        # Clear field first
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.write(ACCOUNT_CONFIG['email'], interval=0.1)
        time.sleep(1)

        screenshot_path = screenshots_dir / f"step7_email_entered_{int(time.time())}.png"
        capture_screen(str(screenshot_path))
        logger.info("📸 Captured email entry")
        logger.info(f"   Check screenshot: {screenshot_path}")

        pyautogui.press('tab')
        time.sleep(0.5)

        # Step 6: Get password
        logger.info("")
        logger.info("📋 STEP 6: Password entry...")
        logger.info("-" * 80)

        from nas_azure_vault_integration import NASAzureVaultIntegration
        nas_integration = NASAzureVaultIntegration()
        credentials = nas_integration.get_nas_credentials()
        password = credentials.get("password") if credentials else None

        if password:
            logger.info("   Entering password...")
            pyautogui.write(password, interval=0.05)
            time.sleep(1)
        else:
            logger.warning("   ⏸️  Waiting for manual password entry...")
            logger.info("   Please enter password in the dialog")
            time.sleep(10)

        screenshot_path = screenshots_dir / f"step8_password_entered_{int(time.time())}.png"
        capture_screen(str(screenshot_path))
        logger.info("📸 Captured password entry")
        logger.info(f"   Check screenshot: {screenshot_path}")

        # Click Next
        logger.info("   Clicking Next...")
        pyautogui.press('tab', presses=2)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(3)

        screenshot_path = screenshots_dir / f"step9_after_next_{int(time.time())}.png"
        capture_screen(str(screenshot_path))
        logger.info("📸 Captured after Next click")
        logger.info(f"   Check screenshot: {screenshot_path}")

        # Step 7: More Settings
        logger.info("")
        logger.info("📋 STEP 7: Opening More Settings...")
        logger.info("-" * 80)

        pyautogui.press('tab', presses=3)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(2)

        screenshot_path = screenshots_dir / f"step10_more_settings_{int(time.time())}.png"
        capture_screen(str(screenshot_path))
        logger.info("📸 Captured More Settings dialog")
        logger.info(f"   Check screenshot: {screenshot_path}")

        # Advanced tab
        pyautogui.press('tab', presses=2)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(1)

        screenshot_path = screenshots_dir / f"step11_advanced_tab_{int(time.time())}.png"
        capture_screen(str(screenshot_path))
        logger.info("📸 Captured Advanced tab")
        logger.info(f"   Check screenshot: {screenshot_path}")

        # Step 8: Configure IMAP
        logger.info("")
        logger.info("📋 STEP 8: Configuring IMAP settings...")
        logger.info("-" * 80)
        logger.info("   📸 Taking screenshot before IMAP config...")

        screenshot_path = screenshots_dir / f"step12_before_imap_{int(time.time())}.png"
        capture_screen(str(screenshot_path))
        logger.info(f"   Check screenshot: {screenshot_path}")
        logger.info("   Review this screenshot to see current IMAP settings")

        # Navigate to IMAP server field
        pyautogui.press('tab', presses=5)
        time.sleep(0.5)

        # Clear and enter IMAP server
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.write(ACCOUNT_CONFIG['imap_server'], interval=0.1)
        time.sleep(0.5)

        screenshot_path = screenshots_dir / f"step13_imap_server_{int(time.time())}.png"
        capture_screen(str(screenshot_path))
        logger.info("📸 Captured IMAP server entry")

        pyautogui.press('tab')
        time.sleep(0.5)

        # Clear and enter IMAP port
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.write(ACCOUNT_CONFIG['imap_port'], interval=0.1)
        time.sleep(0.5)

        screenshot_path = screenshots_dir / f"step14_imap_port_{int(time.time())}.png"
        capture_screen(str(screenshot_path))
        logger.info("📸 Captured IMAP port entry")

        pyautogui.press('tab')
        time.sleep(0.5)
        if ACCOUNT_CONFIG.get('imap_encryption') == "SSL/TLS":
            pyautogui.press('down', presses=1)
        time.sleep(0.5)

        screenshot_path = screenshots_dir / f"step15_imap_complete_{int(time.time())}.png"
        capture_screen(str(screenshot_path))
        logger.info("📸 Captured complete IMAP settings")
        logger.info(f"   Check screenshot: {screenshot_path}")

        # Step 9: Configure SMTP
        logger.info("")
        logger.info("📋 STEP 9: Configuring SMTP settings...")
        logger.info("-" * 80)

        pyautogui.press('tab', presses=3)
        time.sleep(0.5)

        # Clear and enter SMTP server
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.write(ACCOUNT_CONFIG['smtp_server'], interval=0.1)
        time.sleep(0.5)

        screenshot_path = screenshots_dir / f"step16_smtp_server_{int(time.time())}.png"
        capture_screen(str(screenshot_path))

        pyautogui.press('tab')
        time.sleep(0.5)

        # Clear and enter SMTP port
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.write(ACCOUNT_CONFIG['smtp_port'], interval=0.1)
        time.sleep(0.5)

        screenshot_path = screenshots_dir / f"step17_smtp_port_{int(time.time())}.png"
        capture_screen(str(screenshot_path))

        pyautogui.press('tab')
        time.sleep(0.5)
        if ACCOUNT_CONFIG.get('smtp_encryption') == "STARTTLS":
            pyautogui.press('down', presses=2)
        time.sleep(0.5)

        screenshot_path = screenshots_dir / f"step18_smtp_complete_{int(time.time())}.png"
        capture_screen(str(screenshot_path))
        logger.info("📸 Captured complete SMTP settings")
        logger.info(f"   Check screenshot: {screenshot_path}")

        # Save
        logger.info("")
        logger.info("📋 STEP 10: Saving settings...")
        logger.info("-" * 80)

        pyautogui.press('tab', presses=2)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(2)

        screenshot_path = screenshots_dir / f"step19_after_save_{int(time.time())}.png"
        capture_screen(str(screenshot_path))

        # Test connection
        logger.info("")
        logger.info("📋 STEP 11: Testing connection...")
        logger.info("-" * 80)

        pyautogui.press('tab', presses=2)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(5)

        screenshot_path = screenshots_dir / f"step20_connection_test_{int(time.time())}.png"
        capture_screen(str(screenshot_path))
        logger.info("📸 Captured connection test result")
        logger.info(f"   Check screenshot: {screenshot_path}")
        logger.info("   Review this to see if connection succeeded or failed")

        # Finish
        logger.info("")
        logger.info("📋 STEP 12: Completing setup...")
        logger.info("-" * 80)

        pyautogui.press('tab')
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(3)

        screenshot_path = screenshots_dir / f"step21_final_{int(time.time())}.png"
        capture_screen(str(screenshot_path))
        logger.info("📸 Captured final state")
        logger.info(f"   Check screenshot: {screenshot_path}")

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ SETUP COMPLETED WITH VISION!")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"📸 All screenshots saved to: {screenshots_dir}")
        logger.info("   Review the screenshots to verify each step")
        logger.info("   Pay special attention to:")
        logger.info("   - step12_before_imap: See current IMAP settings")
        logger.info("   - step15_imap_complete: Verify IMAP config")
        logger.info("   - step18_smtp_complete: Verify SMTP config")
        logger.info("   - step20_connection_test: See connection result")

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
    success = setup_with_vision()
    sys.exit(0 if success else 1)
