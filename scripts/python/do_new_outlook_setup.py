#!/usr/bin/env python3
"""
DO IT: Setup New Outlook - Remove Gmail, Add NAS Email

Actually automates the process by connecting to EXISTING Outlook and interacting with UI.
NO NEW OUTLOOK INSTANCES - connects to existing one only.
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

logger = get_logger("DoNewOutlookSetup")

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
    logger.info("📧 SETTING UP NEW OUTLOOK")
    logger.info("="*80)
    logger.info("")
    logger.info("⚠️  Connecting to EXISTING Outlook instance (not launching new ones)")
    logger.info("")

    password = get_password()

    # Check for UI automation
    try:
        import pywinauto
        from pywinauto import Application
        import pyautogui
        UI_AVAILABLE = True
        logger.info("   ✅ UI automation libraries available")
    except ImportError:
        UI_AVAILABLE = False
        logger.warning("   ⚠️  UI automation not available")
        logger.info("   💡 Install: pip install pywinauto pyautogui")
        logger.info("   💡 Or follow manual steps")

    logger.info("")
    logger.info("🔍 Connecting to existing New Outlook...")
    logger.info("   (Please ensure New Outlook is already open)")
    logger.info("")

    time.sleep(2)

    if UI_AVAILABLE:
        try:
            # Connect to EXISTING Outlook (don't launch)
            app = Application(backend="uia").connect(title_re=".*Outlook.*", timeout=10)
            main_window = app.top_window()
            logger.info(f"   ✅ Connected to: {main_window.window_text()}")

            main_window.set_focus()
            time.sleep(1)

            # STEP 1: Remove Gmail
            logger.info("")
            logger.info("🗑️  STEP 1: Removing Gmail Account")
            logger.info("")

            # Open Account Settings
            logger.info("   Opening Account Settings (Ctrl+Shift+A)...")
            pyautogui.hotkey('ctrl', 'shift', 'a')
            time.sleep(3)

            # Look for Account Settings dialog
            try:
                # Find any dialog that opened
                dialogs = app.windows()
                account_dialog = None
                for dialog in dialogs:
                    title = dialog.window_text().lower()
                    if "account" in title and "settings" in title:
                        account_dialog = dialog
                        logger.info(f"   ✅ Found: {dialog.window_text()}")
                        dialog.set_focus()
                        break

                if account_dialog:
                    # Look for Gmail in account list
                    logger.info("   🔍 Searching for Gmail account...")
                    time.sleep(2)

                    # Try to find list view or tree view
                    all_items = account_dialog.descendants()
                    gmail_found = False

                    for item in all_items:
                        try:
                            text = item.window_text().lower()
                            if "gmail" in text or "@gmail.com" in text:
                                logger.info(f"   ✅ Found Gmail: {item.window_text()}")
                                item.click_input()
                                time.sleep(1)
                                gmail_found = True

                                # Look for Remove button
                                remove_btn = None
                                buttons = account_dialog.descendants(control_type="Button")
                                for btn in buttons:
                                    btn_text = btn.window_text().lower()
                                    if "remove" in btn_text or "delete" in btn_text:
                                        remove_btn = btn
                                        logger.info(f"   ✅ Found Remove button: {btn.window_text()}")
                                        break

                                if remove_btn:
                                    remove_btn.click_input()
                                    time.sleep(2)
                                    logger.info("   ✅ Clicked Remove - please confirm if dialog appears")

                                break
                        except:
                            continue

                    if not gmail_found:
                        logger.info("   ⚠️  Gmail account not found automatically")
                        logger.info("   💡 Please manually: Select Gmail → Remove")

            except Exception as e:
                logger.debug(f"   Account Settings automation: {e}")
                logger.info("   💡 Please manually open Account Settings and remove Gmail")

            logger.info("")
            logger.info("   ⏳ Waiting 5 seconds...")
            time.sleep(5)

            # STEP 2: Add NAS email
            logger.info("")
            logger.info("➕ STEP 2: Adding NAS Company Email")
            logger.info("")

            # Open Add Account
            logger.info("   Opening Add Account (File menu)...")
            pyautogui.hotkey('alt', 'f')
            time.sleep(1)

            # Try to navigate to Add Account
            # In many Outlook versions, it's 'A' for Add Account
            pyautogui.press('a')
            time.sleep(3)
            logger.info("   ✅ Attempted to open Add Account")

            # Look for Add Account dialog
            try:
                dialogs = app.windows()
                add_dialog = None
                for dialog in dialogs:
                    title = dialog.window_text().lower()
                    if ("add" in title and "account" in title) or "email" in title:
                        add_dialog = dialog
                        logger.info(f"   ✅ Found: {dialog.window_text()}")
                        dialog.set_focus()
                        break

                if add_dialog:
                    # Try to find and click Advanced/Manual setup
                    time.sleep(1)
                    buttons = add_dialog.descendants(control_type="Button")
                    for btn in buttons:
                        btn_text = btn.window_text().lower()
                        if "advanced" in btn_text or "manual" in btn_text:
                            logger.info(f"   ✅ Found: {btn.window_text()}")
                            btn.click_input()
                            time.sleep(2)
                            break

                    # Try to find IMAP option
                    time.sleep(1)
                    options = add_dialog.descendants()
                    for opt in options:
                        opt_text = opt.window_text().lower()
                        if "imap" in opt_text:
                            logger.info(f"   ✅ Found IMAP")
                            opt.click_input()
                            time.sleep(1)
                            break

                    # Try to type email address
                    time.sleep(1)
                    pyautogui.write(COMPANY_EMAIL, interval=0.1)
                    time.sleep(1)
                    logger.info(f"   ✅ Typed email: {COMPANY_EMAIL}")

                    # Tab to password field and type password
                    if password:
                        pyautogui.press('tab')
                        time.sleep(0.5)
                        pyautogui.write(password, interval=0.05)
                        time.sleep(1)
                        logger.info("   ✅ Entered password")

                    # Look for Advanced Options or More Settings
                    time.sleep(1)
                    advanced_buttons = add_dialog.descendants(control_type="Button")
                    for btn in advanced_buttons:
                        btn_text = btn.window_text().lower()
                        if "advanced" in btn_text or "more" in btn_text or "settings" in btn_text:
                            logger.info(f"   ✅ Found: {btn.window_text()}")
                            btn.click_input()
                            time.sleep(2)
                            break

                    # In advanced settings, fill IMAP/SMTP
                    time.sleep(1)
                    # Tab through fields to get to IMAP server
                    for _ in range(3):
                        pyautogui.press('tab')
                        time.sleep(0.3)

                    pyautogui.write(NAS_MAIL_SERVER, interval=0.1)
                    time.sleep(0.5)
                    pyautogui.press('tab')
                    pyautogui.write(str(NAS_IMAP_PORT), interval=0.1)
                    logger.info(f"   ✅ Entered IMAP: {NAS_MAIL_SERVER}:{NAS_IMAP_PORT}")

            except Exception as e:
                logger.debug(f"   Add Account automation: {e}")
                logger.info("   💡 Please complete setup manually")

            logger.info("")
            logger.info("   ⚠️  UI automation may need manual completion")
            logger.info("   💡 Please verify and complete any remaining steps")

        except Exception as e:
            logger.warning(f"   ⚠️  Could not connect: {e}")
            logger.info("   💡 Please ensure New Outlook is open")
            logger.info("   💡 Then follow manual steps")

    logger.info("")
    logger.info("="*80)
    logger.info("📋 MANUAL STEPS (if needed)")
    logger.info("="*80)
    logger.info("")
    logger.info("REMOVE GMAIL:")
    logger.info("   1. File → Account Settings → Account Settings (or Ctrl+Shift+A)")
    logger.info("   2. Select Gmail → Remove → Confirm")
    logger.info("")
    logger.info("ADD NAS EMAIL:")
    logger.info("   1. File → Add Account")
    logger.info("   2. Advanced setup → IMAP")
    logger.info(f"   3. Email: {COMPANY_EMAIL}")
    logger.info(f"   4. IMAP: {NAS_MAIL_SERVER}:{NAS_IMAP_PORT} (SSL/TLS)")
    logger.info(f"   5. SMTP: {NAS_MAIL_SERVER}:{NAS_SMTP_PORT} (STARTTLS)")
    logger.info("")
    logger.info("="*80)
    logger.info("✅ Setup attempted")
    logger.info("="*80)

    return 0

if __name__ == "__main__":


    exit(main())