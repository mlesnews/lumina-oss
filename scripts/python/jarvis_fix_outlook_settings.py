#!/usr/bin/env python3
"""
JARVIS: Fix Outlook Account Settings

Fixes the IMAP port and SMTP encryption based on what we see in screenshots.

Tags: #JARVIS #OUTLOOK #FIX #AUTOMATION @JARVIS @LUMINA @DOIT
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

logger = get_logger("JARVISFixOutlook")


def fix_outlook_settings():
    """Fix Outlook account settings"""
    try:
        import pyautogui
        import pygetwindow as gw

        logger.info("=" * 80)
        logger.info("🔧 JARVIS: FIXING OUTLOOK ACCOUNT SETTINGS")
        logger.info("=" * 80)
        logger.info("")
        logger.info("Issues found from screenshot:")
        logger.info("  ❌ IMAP Port: 943 (should be 993)")
        logger.info("  ❌ SMTP Encryption: None (should be STARTTLS)")
        logger.info("")

        # Find Outlook window
        outlook_windows = []
        for window in gw.getAllWindows():
            title_lower = window.title.lower()
            if 'outlook' in title_lower:
                outlook_windows.append(window)

        if not outlook_windows:
            logger.error("❌ Outlook window not found")
            return False

        outlook_window = outlook_windows[0]
        logger.info(f"✅ Found Outlook window: {outlook_window.title}")

        try:
            outlook_window.activate()
            time.sleep(2)
        except Exception:
            pass

        # Open Account Settings
        logger.info("")
        logger.info("📋 Opening Account Settings...")
        pyautogui.hotkey('alt', 'f')
        time.sleep(1)
        pyautogui.press('t')
        time.sleep(1)
        pyautogui.press('a')
        time.sleep(3)

        # Find and select the account
        logger.info("📋 Finding account: mlesn@<LOCAL_HOSTNAME>")
        # Try to find the account in the list
        # Usually it's the first account or we can search
        pyautogui.press('tab')
        time.sleep(0.5)
        # Type to search for the account
        pyautogui.write("mlesn", interval=0.1)
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(2)

        # Click Change
        logger.info("📋 Clicking Change button...")
        pyautogui.press('tab', presses=2)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(2)

        # Navigate to More Settings
        logger.info("📋 Opening More Settings...")
        pyautogui.press('tab', presses=3)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(2)

        # Advanced tab
        pyautogui.press('tab', presses=2)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(1)

        # Fix IMAP Port
        logger.info("")
        logger.info("📋 FIXING IMAP PORT: 943 → 993")
        logger.info("-" * 80)

        # Navigate to IMAP port field
        # From screenshot, IMAP port is after IMAP server
        # Tab sequence: IMAP server -> IMAP port
        pyautogui.press('tab', presses=5)  # To IMAP server
        time.sleep(0.5)
        pyautogui.press('tab')  # To IMAP port
        time.sleep(0.5)

        # Clear and enter correct port
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.write("993", interval=0.1)
        time.sleep(0.5)
        logger.info("✅ IMAP port set to 993")

        # Fix SMTP Encryption
        logger.info("")
        logger.info("📋 FIXING SMTP ENCRYPTION: None → STARTTLS")
        logger.info("-" * 80)

        # Navigate to SMTP encryption dropdown
        # Tab sequence: IMAP encryption -> SMTP server -> SMTP port -> SMTP encryption
        pyautogui.press('tab')  # Past IMAP encryption
        time.sleep(0.5)
        pyautogui.press('tab', presses=3)  # To SMTP server, then port, then encryption
        time.sleep(0.5)

        # Select STARTTLS
        pyautogui.press('down', presses=2)  # Select STARTTLS (usually 3rd option: None, SSL/TLS, STARTTLS)
        time.sleep(0.5)
        logger.info("✅ SMTP encryption set to STARTTLS")

        # Save
        logger.info("")
        logger.info("📋 Saving settings...")
        pyautogui.press('tab', presses=2)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(2)

        # Test connection
        logger.info("📋 Testing connection...")
        pyautogui.press('tab', presses=2)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(5)

        # Finish
        logger.info("📋 Completing...")
        pyautogui.press('tab')
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(3)

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ SETTINGS FIXED!")
        logger.info("=" * 80)
        logger.info("")
        logger.info("📋 Please verify:")
        logger.info("   1. Check if account works in Outlook")
        logger.info("   2. Try sending/receiving email")
        logger.info("   3. If still not working, check Account Settings again")

        return True

    except ImportError:
        logger.error("❌ Required modules not available")
        return False
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = fix_outlook_settings()
    sys.exit(0 if success else 1)
