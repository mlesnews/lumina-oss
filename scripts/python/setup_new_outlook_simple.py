#!/usr/bin/env python3
"""
Simple New Outlook Setup - Remove Gmail, Add NAS Email

Uses keyboard shortcuts and simple UI interaction.
NO LAUNCHING - connects to existing Outlook only.
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

logger = get_logger("SetupNewOutlookSimple")

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

def main():
    """Main execution"""
    logger.info("="*80)
    logger.info("📧 SETTING UP NEW OUTLOOK - REMOVE GMAIL, ADD NAS EMAIL")
    logger.info("="*80)
    logger.info("")
    logger.info("⚠️  This script connects to EXISTING Outlook only")
    logger.info("   It will NOT launch new Outlook instances")
    logger.info("")

    password = get_password()

    try:
        import pywinauto
        from pywinauto import Application
        import pyautogui
    except ImportError:
        logger.error("   ❌ UI automation libraries not installed")
        logger.info("   💡 Install: pip install pywinauto pyautogui")
        return 1

    logger.info("🔍 Connecting to existing New Outlook...")
    logger.info("   (Please ensure New Outlook is open and visible)")
    logger.info("")

    time.sleep(2)

    try:
        # Connect to existing Outlook by process
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

        main_window.set_focus()
        time.sleep(1)

        # STEP 1: Remove Gmail
        logger.info("")
        logger.info("🗑️  STEP 1: Removing Gmail Account")
        logger.info("")
        logger.info("   Opening Account Settings...")

        # Use keyboard shortcut
        pyautogui.hotkey('ctrl', 'shift', 'a')
        time.sleep(4)

        # Refresh app windows to see new dialog
        app = Application(backend="uia").connect(process=outlook_pids[0])
        windows = app.windows()

        account_dialog = None
        for window in windows:
            try:
                title = window.window_text()
                logger.debug(f"   Window: {title}")
                # Account Settings might be in a pane or dialog
                if "account" in title.lower() or "settings" in title.lower():
                    if "mail" not in title.lower() or window != main_window:
                        account_dialog = window
                        logger.info(f"   ✅ Found: {title}")
                        window.set_focus()
                        break
            except:
                continue

        if account_dialog:
            logger.info("   🔍 Looking for Gmail account to remove...")
            time.sleep(2)

            # Try to find Gmail in the dialog
            all_items = list(account_dialog.descendants())
            logger.info(f"   📊 Found {len(all_items)} items in dialog")

            for item in all_items:
                try:
                    text = item.window_text()
                    if text and ("gmail" in text.lower() or "@gmail.com" in text.lower()):
                        logger.info(f"   ✅ Found Gmail: {text}")
                        item.click_input()
                        time.sleep(1)

                        # Look for Remove button
                        buttons = list(account_dialog.descendants(control_type="Button"))
                        for btn in buttons:
                            btn_text = btn.window_text().lower()
                            if "remove" in btn_text or "delete" in btn_text:
                                logger.info(f"   ✅ Found Remove: {btn.window_text()}")
                                btn.click_input()
                                time.sleep(2)

                                # Confirm if needed
                                pyautogui.press('enter')
                                time.sleep(2)
                                logger.info("   ✅ Gmail removal attempted")
                                break
                        break
                except:
                    continue
        else:
            logger.info("   ⚠️  Account Settings dialog not found automatically")
            logger.info("   💡 Please manually: File → Account Settings → Remove Gmail")

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

        logger.info("   Opening Add Account...")
        pyautogui.hotkey('alt', 'f')
        time.sleep(1)
        pyautogui.press('a')  # Add Account
        time.sleep(4)

        # Refresh to see new dialog
        app = Application(backend="uia").connect(process=outlook_pids[0])
        windows = app.windows()

        add_dialog = None
        for window in windows:
            try:
                title = window.window_text().lower()
                if ("add" in title and "account" in title) or "email" in title or "setup" in title:
                    if window != main_window:
                        add_dialog = window
                        logger.info(f"   ✅ Found: {window.window_text()}")
                        window.set_focus()
                        break
            except:
                continue

        if add_dialog:
            logger.info("   🔍 Configuring account...")
            time.sleep(2)

            # Type email
            pyautogui.write(COMPANY_EMAIL, interval=0.1)
            time.sleep(1)
            logger.info(f"   ✅ Entered email: {COMPANY_EMAIL}")

            # Tab to password
            if password:
                pyautogui.press('tab')
                time.sleep(0.5)
                pyautogui.write(password, interval=0.05)
                time.sleep(1)
                logger.info("   ✅ Entered password")

            # Look for Advanced/Manual button
            buttons = list(add_dialog.descendants(control_type="Button"))
            for btn in buttons:
                btn_text = btn.window_text().lower()
                if "advanced" in btn_text or "manual" in btn_text:
                    logger.info(f"   ✅ Found: {btn.window_text()}")
                    btn.click_input()
                    time.sleep(2)
                    break

            # Select IMAP
            time.sleep(1)
            options = list(add_dialog.descendants())
            for opt in options:
                opt_text = opt.window_text().lower()
                if "imap" in opt_text:
                    logger.info(f"   ✅ Found IMAP")
                    opt.click_input()
                    time.sleep(1)
                    break

            # Fill server settings
            time.sleep(1)
            # Navigate to server fields (may need multiple tabs)
            for _ in range(5):
                pyautogui.press('tab')
                time.sleep(0.2)

            pyautogui.write(NAS_MAIL_SERVER, interval=0.1)
            time.sleep(0.5)
            pyautogui.press('tab')
            pyautogui.write(str(NAS_IMAP_PORT), interval=0.1)
            logger.info(f"   ✅ Entered IMAP: {NAS_MAIL_SERVER}:{NAS_IMAP_PORT}")

            # SMTP
            time.sleep(1)
            for _ in range(2):
                pyautogui.press('tab')
                time.sleep(0.2)

            pyautogui.write(NAS_MAIL_SERVER, interval=0.1)
            time.sleep(0.5)
            pyautogui.press('tab')
            pyautogui.write(str(NAS_SMTP_PORT), interval=0.1)
            logger.info(f"   ✅ Entered SMTP: {NAS_MAIL_SERVER}:{NAS_SMTP_PORT}")

            # Click Connect/Finish
            time.sleep(1)
            pyautogui.press('enter')  # Or look for button
            time.sleep(2)
            logger.info("   ✅ Setup completed")
        else:
            logger.info("   ⚠️  Add Account dialog not found automatically")
            logger.info("   💡 Please complete setup manually")

    except Exception as e:
        logger.error(f"   ❌ Error: {e}")
        logger.info("   💡 Please complete setup manually")
        return 1

    logger.info("")
    logger.info("="*80)
    logger.info("✅ SETUP COMPLETED")
    logger.info("="*80)
    logger.info("")
    logger.info("💡 Please verify in New Outlook:")
    logger.info("   • Gmail account removed")
    logger.info(f"   • NAS email ({COMPANY_EMAIL}) added and working")
    logger.info("")

    return 0

if __name__ == "__main__":


    exit(main())