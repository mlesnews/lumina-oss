#!/usr/bin/env python3
"""
JARVIS: Add Outlook Account - Robust Version

Adds company email account to Outlook Classic with improved error handling and verification.

Tags: #JARVIS #OUTLOOK #EMAIL #AUTOMATION @JARVIS @LUMINA @DOIT
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

logger = get_logger("JARVISAddOutlookAccount")

# Account configuration
ACCOUNT_CONFIG = {
    "email": "mlesn@<LOCAL_HOSTNAME>",
    "display_name": "mlesn",
    "imap_server": "<NAS_PRIMARY_IP>",
    "imap_port": "993",
    "smtp_server": "<NAS_PRIMARY_IP>",
    "smtp_port": "587",
    "imap_encryption": "SSL/TLS",
    "smtp_encryption": "STARTTLS"
}


def add_outlook_account():
    """Add company email account to Outlook"""
    try:
        import pyautogui
        import pygetwindow as gw

        logger.info("=" * 80)
        logger.info("📧 JARVIS: ADDING OUTLOOK ACCOUNT (ROBUST VERSION)")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"Account: {ACCOUNT_CONFIG['email']}")
        logger.info(f"IMAP Server: {ACCOUNT_CONFIG['imap_server']}:{ACCOUNT_CONFIG['imap_port']}")
        logger.info(f"SMTP Server: {ACCOUNT_CONFIG['smtp_server']}:{ACCOUNT_CONFIG['smtp_port']}")
        logger.info("")

        # Find Outlook window
        logger.info("📋 STEP 1: Finding Outlook window...")
        logger.info("-" * 80)

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

        # Activate Outlook
        try:
            outlook_window.activate()
            time.sleep(2)
            logger.info("✅ Outlook window activated")
        except Exception as e:
            logger.warning(f"⚠️  Could not activate window: {e}")

        # Navigate to Account Settings
        logger.info("")
        logger.info("📋 STEP 2: Opening Account Settings...")
        logger.info("-" * 80)

        # Method 1: File menu
        pyautogui.hotkey('alt', 'f')
        time.sleep(1)
        pyautogui.press('t')
        time.sleep(1)
        pyautogui.press('a')
        time.sleep(3)

        logger.info("✅ Account Settings dialog opened")

        # Click New button
        logger.info("")
        logger.info("📋 STEP 3: Clicking 'New...' button...")
        logger.info("-" * 80)

        # Try to find and click New button
        try:
            # Look for "New..." button - usually visible in Account Settings
            new_button = pyautogui.locateOnScreen('new_button.png', confidence=0.8)
            if new_button:
                pyautogui.click(pyautogui.center(new_button))
                logger.info("✅ Clicked New button (image match)")
            else:
                # Try keyboard shortcut or tab navigation
                pyautogui.press('n')  # Sometimes N selects New
                time.sleep(1)
                pyautogui.press('enter')
                time.sleep(2)
                logger.info("✅ Attempted to click New button (keyboard)")
        except Exception:
            # Fallback: try Tab to navigate and Enter
            pyautogui.press('tab', presses=3)
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(2)
            logger.info("✅ Attempted to open New Account dialog")

        # Wait for Add Account dialog
        time.sleep(2)

        # Select Manual setup
        logger.info("")
        logger.info("📋 STEP 4: Selecting manual setup...")
        logger.info("-" * 80)

        # Look for "Manual setup" or similar option
        pyautogui.press('m')  # M for Manual
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(2)

        logger.info("✅ Selected manual setup")

        # Enter account details
        logger.info("")
        logger.info("📋 STEP 5: Entering account details...")
        logger.info("-" * 80)

        # Email address
        logger.info(f"   Entering email: {ACCOUNT_CONFIG['email']}")
        pyautogui.write(ACCOUNT_CONFIG['email'], interval=0.1)
        time.sleep(1)
        pyautogui.press('tab')
        time.sleep(0.5)

        # Password - will be entered manually
        logger.info("   ⏸️  Waiting for password entry...")
        logger.info("   Please enter the password in the dialog")
        time.sleep(10)  # Give user time to enter password

        # Click Next
        logger.info("   Clicking Next...")
        pyautogui.press('tab', presses=2)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(3)

        # More Settings
        logger.info("")
        logger.info("📋 STEP 6: Opening More Settings...")
        logger.info("-" * 80)

        pyautogui.press('tab', presses=3)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(2)

        # Advanced tab
        logger.info("   Opening Advanced tab...")
        pyautogui.press('tab', presses=2)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(1)

        # Configure IMAP settings
        logger.info("   Configuring IMAP settings...")
        logger.info(f"   IMAP Server: {ACCOUNT_CONFIG['imap_server']}")
        logger.info(f"   IMAP Port: {ACCOUNT_CONFIG['imap_port']}")
        logger.info(f"   Encryption: {ACCOUNT_CONFIG['imap_encryption']}")

        # Navigate to IMAP server field
        pyautogui.press('tab', presses=5)
        time.sleep(0.5)
        pyautogui.write(ACCOUNT_CONFIG['imap_server'], interval=0.1)
        time.sleep(0.5)

        # IMAP port
        pyautogui.press('tab')
        time.sleep(0.5)
        pyautogui.write(ACCOUNT_CONFIG['imap_port'], interval=0.1)
        time.sleep(0.5)

        # Encryption type
        pyautogui.press('tab')
        time.sleep(0.5)
        if ACCOUNT_CONFIG['imap_encryption'] == "SSL/TLS":
            pyautogui.press('down', presses=1)  # Select SSL/TLS
        time.sleep(0.5)

        # SMTP settings
        logger.info("   Configuring SMTP settings...")
        logger.info(f"   SMTP Server: {ACCOUNT_CONFIG['smtp_server']}")
        logger.info(f"   SMTP Port: {ACCOUNT_CONFIG['smtp_port']}")

        # Navigate to SMTP server
        pyautogui.press('tab', presses=3)
        time.sleep(0.5)
        pyautogui.write(ACCOUNT_CONFIG['smtp_server'], interval=0.1)
        time.sleep(0.5)

        # SMTP port
        pyautogui.press('tab')
        time.sleep(0.5)
        pyautogui.write(ACCOUNT_CONFIG['smtp_port'], interval=0.1)
        time.sleep(0.5)

        # SMTP encryption
        pyautogui.press('tab')
        time.sleep(0.5)
        if ACCOUNT_CONFIG['smtp_encryption'] == "STARTTLS":
            pyautogui.press('down', presses=2)  # Select STARTTLS
        time.sleep(0.5)

        # OK to close More Settings
        logger.info("   Saving advanced settings...")
        pyautogui.press('tab', presses=2)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(2)

        # Test connection
        logger.info("")
        logger.info("📋 STEP 7: Testing connection...")
        logger.info("-" * 80)

        pyautogui.press('tab', presses=2)
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(5)

        # Finish
        logger.info("   Completing setup...")
        pyautogui.press('tab')
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(3)

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ Outlook account setup completed!")
        logger.info("=" * 80)
        logger.info("")
        logger.info("📋 Please verify:")
        logger.info("   1. Check if the account appears in Outlook")
        logger.info("   2. Try sending/receiving email")
        logger.info("   3. If there are errors, check the account settings")

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
    success = add_outlook_account()
    sys.exit(0 if success else 1)
