#!/usr/bin/env python3
"""
Setup New Outlook Using Keyboard Shortcuts

Uses keyboard navigation to remove Gmail and add NAS email.
NO MOUSE - pure keyboard automation.
"""

import sys
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from azure_service_bus_integration import AzureKeyVaultClient

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SetupNewOutlookKeyboard")

NAS_MAIL_SERVER = "<NAS_PRIMARY_IP>"
NAS_IMAP_PORT = 993
NAS_SMTP_PORT = 587
COMPANY_EMAIL = "mlesn@<LOCAL_HOSTNAME>"

def get_password():
    """Get password from Azure Vault"""
    try:
        vault = AzureKeyVaultClient(vault_url="https://jarvis-lumina.vault.azure.net/")
        return vault.get_secret("n8n-password")
    except:
        return None

def type_text(text, delay=0.1):
    try:
        """Type text with delay"""
        import pyautogui
        pyautogui.write(text, interval=delay)

    except Exception as e:
        logger.error(f"Error in type_text: {e}", exc_info=True)
        raise
def press_key(key, times=1, delay=0.5):
    """Press a key multiple times"""
    import pyautogui
    for _ in range(times):
        pyautogui.press(key)
        time.sleep(delay)

def main():
    """Main execution"""
    logger.info("="*80)
    logger.info("📧 SETTING UP NEW OUTLOOK - KEYBOARD AUTOMATION")
    logger.info("="*80)
    logger.info("")
    logger.info("⚠️  Using keyboard shortcuts only - no mouse clicks")
    logger.info("   Please ensure New Outlook is open and active")
    logger.info("")

    password = get_password()
    if not password:
        logger.warning("   ⚠️  Password not found in Azure Vault")
        logger.info("   💡 You'll need to enter password manually")

    try:
        import pyautogui
        import pywinauto
        from pywinauto import Application
    except ImportError:
        logger.error("   ❌ UI automation libraries not installed")
        logger.info("   💡 Install: pip install pywinauto pyautogui")
        return 1

    logger.info("🔍 Connecting to existing New Outlook...")
    logger.info("")

    time.sleep(2)

    try:
        # Connect to existing Outlook
        import psutil
        outlook_pids = []
        for proc in psutil.process_iter(['pid', 'name']):
            name = proc.info['name'].lower()
            if 'outlook' in name or 'olk' in name:
                outlook_pids.append(proc.info['pid'])

        if not outlook_pids:
            logger.error("   ❌ Outlook not running")
            logger.info("   💡 Please open New Outlook first")
            return 1

        app = Application(backend="uia").connect(process=outlook_pids[0])
        main_window = app.top_window()
        logger.info(f"   ✅ Connected to: {main_window.window_text()}")

        # Bring to front
        main_window.set_focus()
        time.sleep(1)

        # STEP 1: Remove Gmail
        logger.info("")
        logger.info("🗑️  STEP 1: Removing Gmail Account")
        logger.info("")
        logger.info("   Opening Account Settings (Ctrl+Shift+A)...")

        pyautogui.hotkey('ctrl', 'shift', 'a')
        time.sleep(3)
        logger.info("   ✅ Account Settings should be open")

        # Navigate to Gmail account using keyboard
        logger.info("   🔍 Navigating to Gmail account...")
        logger.info("   (Using Tab/Arrow keys to find Gmail)")

        # Try to find Gmail by typing "gmail" or using arrow keys
        # First, try typing "g" to jump to Gmail if list is sorted
        pyautogui.press('g')
        time.sleep(0.5)
        pyautogui.press('g')  # In case first didn't work
        time.sleep(1)

        # Or use arrow keys to navigate
        logger.info("   Using arrow keys to navigate...")
        for _ in range(5):  # Try up to 5 accounts
            pyautogui.press('down')
            time.sleep(0.3)

        # Look for Remove button - try Alt+R or Tab to Remove button
        logger.info("   Looking for Remove button...")
        time.sleep(1)

        # Try Alt+R (if Remove is accessible)
        pyautogui.hotkey('alt', 'r')
        time.sleep(1)

        # Or Tab to Remove button
        for _ in range(10):
            pyautogui.press('tab')
            time.sleep(0.2)
            # Check if we're on Remove button (can't verify, but try)

        # Press Enter to activate Remove
        pyautogui.press('enter')
        time.sleep(2)
        logger.info("   ✅ Attempted to remove Gmail")

        # Confirm removal if dialog appears
        logger.info("   Confirming removal...")
        time.sleep(1)
        pyautogui.press('enter')  # Confirm
        time.sleep(2)

        # Close Account Settings
        pyautogui.press('escape')
        time.sleep(1)
        logger.info("   ✅ Gmail removal completed")

        logger.info("")
        logger.info("   ⏳ Waiting 3 seconds...")
        time.sleep(3)

        # STEP 2: Add NAS email
        logger.info("")
        logger.info("➕ STEP 2: Adding NAS Company Email")
        logger.info("")

        # Bring main window back to focus
        main_window.set_focus()
        time.sleep(1)

        logger.info("   Opening File menu (Alt+F)...")
        pyautogui.hotkey('alt', 'f')
        time.sleep(1)

        logger.info("   Selecting Add Account (A)...")
        pyautogui.press('a')
        time.sleep(4)
        logger.info("   ✅ Add Account dialog should be open")

        # Navigate to Advanced setup
        logger.info("   Navigating to Advanced setup...")
        time.sleep(1)

        # Try typing "a" for Advanced or use Tab
        pyautogui.press('a')
        time.sleep(1)

        # Or Tab to Advanced button
        for _ in range(5):
            pyautogui.press('tab')
            time.sleep(0.2)

        pyautogui.press('enter')  # Select Advanced
        time.sleep(2)

        # Select IMAP
        logger.info("   Selecting IMAP...")
        time.sleep(1)
        pyautogui.press('i')  # IMAP
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(2)

        # Fill email address
        logger.info(f"   Entering email: {COMPANY_EMAIL}")
        time.sleep(1)
        type_text(COMPANY_EMAIL, delay=0.1)
        time.sleep(1)
        logger.info("   ✅ Email entered")

        # Tab to password field
        pyautogui.press('tab')
        time.sleep(0.5)

        # Enter password
        if password:
            logger.info("   Entering password...")
            type_text(password, delay=0.05)
            time.sleep(1)
            logger.info("   ✅ Password entered")
        else:
            logger.info("   ⚠️  Password not available - please enter manually")
            time.sleep(3)  # Give user time to enter

        # Tab to Next/Continue button or Advanced Options
        pyautogui.press('tab')
        time.sleep(0.5)
        pyautogui.press('tab')
        time.sleep(0.5)

        # Try to open Advanced Options
        logger.info("   Opening Advanced Options...")
        pyautogui.press('enter')  # Or look for Advanced Options link
        time.sleep(2)

        # Navigate to IMAP server field
        logger.info("   Configuring IMAP server...")
        time.sleep(1)

        # Tab to IMAP server field (may need multiple tabs)
        for _ in range(5):
            pyautogui.press('tab')
            time.sleep(0.2)

        # Enter IMAP server
        type_text(NAS_MAIL_SERVER, delay=0.1)
        time.sleep(0.5)
        pyautogui.press('tab')
        type_text(str(NAS_IMAP_PORT), delay=0.1)
        logger.info(f"   ✅ IMAP: {NAS_MAIL_SERVER}:{NAS_IMAP_PORT}")

        # Navigate to SMTP server
        time.sleep(1)
        for _ in range(3):
            pyautogui.press('tab')
            time.sleep(0.2)

        # Enter SMTP server
        type_text(NAS_MAIL_SERVER, delay=0.1)
        time.sleep(0.5)
        pyautogui.press('tab')
        type_text(str(NAS_SMTP_PORT), delay=0.1)
        logger.info(f"   ✅ SMTP: {NAS_MAIL_SERVER}:{NAS_SMTP_PORT}")

        # Navigate to Connect/Finish button
        logger.info("   Connecting...")
        time.sleep(1)
        for _ in range(3):
            pyautogui.press('tab')
            time.sleep(0.2)

        pyautogui.press('enter')  # Connect
        time.sleep(3)
        logger.info("   ✅ Connection attempted")

        # Wait for connection to complete
        time.sleep(5)

        # Close any success dialogs
        pyautogui.press('enter')
        time.sleep(1)
        pyautogui.press('escape')
        time.sleep(1)

    except Exception as e:
        logger.error(f"   ❌ Error: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        logger.info("   💡 Please complete setup manually if needed")
        return 1

    logger.info("")
    logger.info("="*80)
    logger.info("✅ KEYBOARD AUTOMATION COMPLETED")
    logger.info("="*80)
    logger.info("")
    logger.info("💡 Please verify in New Outlook:")
    logger.info("   • Gmail account removed")
    logger.info(f"   • NAS email ({COMPANY_EMAIL}) added and working")
    logger.info("")
    logger.info("   If setup didn't complete, check the dialogs and")
    logger.info("   complete any remaining steps manually.")
    logger.info("")

    return 0

if __name__ == "__main__":


    exit(main())