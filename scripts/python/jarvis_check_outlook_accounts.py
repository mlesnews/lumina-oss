#!/usr/bin/env python3
"""
JARVIS: Check Outlook Accounts

Checks what email accounts are configured in Outlook Classic.

Tags: #JARVIS #OUTLOOK #DIAGNOSTIC @JARVIS @LUMINA
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

logger = get_logger("JARVISCheckOutlook")


def check_outlook_accounts():
    """Check Outlook accounts via GUI"""
    try:
        import pyautogui
        import pygetwindow as gw

        logger.info("=" * 80)
        logger.info("📧 JARVIS: CHECKING OUTLOOK ACCOUNTS")
        logger.info("=" * 80)
        logger.info("")

        # Find Outlook window
        logger.info("📋 Looking for Outlook window...")
        outlook_windows = []
        for window in gw.getAllWindows():
            title_lower = window.title.lower()
            if 'outlook' in title_lower:
                outlook_windows.append(window)

        if not outlook_windows:
            logger.warning("⚠️  Outlook window not found")
            logger.info("   Please open Outlook Classic first")
            return False

        outlook_window = outlook_windows[0]
        logger.info(f"✅ Found Outlook window: {outlook_window.title}")
        logger.info("")

        # Activate Outlook
        try:
            outlook_window.activate()
            time.sleep(2)
            logger.info("✅ Outlook window activated")
        except Exception as e:
            logger.warning(f"⚠️  Could not activate window: {e}")

        # Navigate to Account Settings
        logger.info("")
        logger.info("📋 Opening Account Settings...")
        logger.info("-" * 80)

        # Press Alt+F to open File menu
        pyautogui.hotkey('alt', 'f')
        time.sleep(1)

        # Press T for Account Settings
        pyautogui.press('t')
        time.sleep(1)

        # Press A for Account Settings
        pyautogui.press('a')
        time.sleep(2)

        logger.info("✅ Account Settings dialog should be open")
        logger.info("")
        logger.info("📋 Please check the Account Settings dialog:")
        logger.info("   - Look for your company email account")
        logger.info("   - If it's not there, we'll need to add it")
        logger.info("")
        logger.info("💡 If the account is missing, I can re-run the setup")

        return True

    except ImportError:
        logger.error("❌ Required modules not available")
        logger.info("   Install: pip install pyautogui pygetwindow")
        return False
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = check_outlook_accounts()
    sys.exit(0 if success else 1)
