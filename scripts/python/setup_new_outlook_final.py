#!/usr/bin/env python3
"""
Final New Outlook Setup - Remove Gmail, Add NAS Email

Connects to EXISTING Outlook instance and automates:
1. Remove Gmail account
2. Add NAS company email account

Tags: #DOIT #OUTLOOK #EMAIL #NAS @JARVIS
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

logger = get_logger("SetupNewOutlookFinal")

# Configuration
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
    logger.info("⚠️  IMPORTANT: Do NOT launch Outlook - connect to existing instance")
    logger.info("")

    password = get_password()

    logger.info("📋 Configuration:")
    logger.info(f"   Remove: Gmail IMAP account")
    logger.info(f"   Add: {COMPANY_EMAIL}")
    logger.info(f"   IMAP: {NAS_MAIL_SERVER}:{NAS_IMAP_PORT}")
    logger.info(f"   SMTP: {NAS_MAIL_SERVER}:{NAS_SMTP_PORT}")
    logger.info("")

    # Connect to EXISTING Outlook (don't launch)
    logger.info("🔍 Connecting to existing New Outlook instance...")
    logger.info("   (Please ensure New Outlook is already open)")
    logger.info("")

    time.sleep(3)  # Give user time

    try:
        import pywinauto
        from pywinauto import Application
        import pyautogui

        # Connect to existing Outlook
        try:
            app = Application(backend="uia").connect(title_re=".*Outlook.*", timeout=15)
            main_window = app.top_window()
            logger.info(f"   ✅ Connected to existing Outlook: {main_window.window_text()}")

            # Bring to front
            main_window.set_focus()
            time.sleep(1)

            # STEP 1: Remove Gmail
            logger.info("")
            logger.info("🗑️  STEP 1: Removing Gmail Account")
            logger.info("")

            # Open Account Settings
            logger.info("   Opening Account Settings...")
            try:
                # Try keyboard shortcut
                pyautogui.hotkey('ctrl', 'shift', 'a')
                time.sleep(3)
                logger.info("   ✅ Sent Ctrl+Shift+A (Account Settings)")

                # Look for Account Settings dialog
                try:
                    account_dialog = app.window(title_re=".*Account.*Settings.*")
                    if account_dialog.exists():
                        logger.info("   ✅ Account Settings dialog opened")
                        account_dialog.set_focus()

                        # Look for Gmail account in list
                        logger.info("   🔍 Looking for Gmail account...")
                        time.sleep(2)

                        # Try to find list or tree view with accounts
                        try:
                            # Look for controls that might contain account list
                            all_controls = account_dialog.descendants()
                            for control in all_controls:
                                try:
                                    text = control.window_text().lower()
                                    if "gmail" in text or "@gmail.com" in text:
                                        logger.info(f"   ✅ Found Gmail: {control.window_text()}")
                                        # Try to select it
                                        control.click_input(button='left', double=False)
                                        time.sleep(1)

                                        # Look for Remove button
                                        remove_buttons = account_dialog.descendants(control_type="Button")
                                        for btn in remove_buttons:
                                            btn_text = btn.window_text().lower()
                                            if "remove" in btn_text or "delete" in btn_text:
                                                logger.info(f"   ✅ Found Remove button: {btn.window_text()}")
                                                btn.click_input()
                                                time.sleep(2)
                                                logger.info("   ✅ Clicked Remove - please confirm if dialog appears")
                                                break
                                        break
                                except:
                                    continue
                        except Exception as e:
                            logger.debug(f"   Account removal automation: {e}")
                            logger.info("   💡 Please manually remove Gmail account")
                            logger.info("      Select Gmail → Click Remove → Confirm")

                except:
                    logger.info("   💡 Account Settings may have opened - please check")
                    logger.info("   💡 If not, manually: File → Account Settings → Account Settings")

            except Exception as e:
                logger.debug(f"   Account Settings: {e}")
                logger.info("   💡 Please manually open Account Settings")

            logger.info("")
            logger.info("   ⏳ Waiting 5 seconds for Gmail removal...")
            time.sleep(5)

            # STEP 2: Add NAS email
            logger.info("")
            logger.info("➕ STEP 2: Adding NAS Company Email")
            logger.info("")

            # Try to open Add Account
            logger.info("   Opening Add Account dialog...")
            try:
                # Try File menu → Add Account
                pyautogui.hotkey('alt', 'f')  # File menu
                time.sleep(1)
                logger.info("   ✅ Opened File menu")

                # Try to find "Add Account" in menu
                time.sleep(1)
                # Type 'a' to select Add Account (if it's the first option)
                pyautogui.press('a')
                time.sleep(2)
                logger.info("   ✅ Attempted to select Add Account")

            except Exception as e:
                logger.debug(f"   Add Account: {e}")
                logger.info("   💡 Please manually: File → Add Account")

            logger.info("")
            logger.info("   ⏳ Waiting for Add Account dialog...")
            time.sleep(3)

            # If Add Account dialog is open, try to fill it
            try:
                # Look for any dialog that might be Add Account
                dialogs = app.windows()
                for dialog in dialogs:
                    title = dialog.window_text().lower()
                    if "add" in title and "account" in title or "email" in title:
                        logger.info(f"   ✅ Found dialog: {dialog.window_text()}")
                        dialog.set_focus()

                        # Try to find and click "Advanced setup" or "Manual setup"
                        time.sleep(1)
                        try:
                            advanced_buttons = dialog.descendants(control_type="Button")
                            for btn in advanced_buttons:
                                btn_text = btn.window_text().lower()
                                if "advanced" in btn_text or "manual" in btn_text:
                                    logger.info(f"   ✅ Found: {btn.window_text()}")
                                    btn.click_input()
                                    time.sleep(2)
                                    break
                        except:
                            pass

                        # Try to find IMAP option
                        time.sleep(1)
                        try:
                            imap_options = dialog.descendants()
                            for opt in imap_options:
                                opt_text = opt.window_text().lower()
                                if "imap" in opt_text:
                                    logger.info(f"   ✅ Found IMAP option")
                                    opt.click_input()
                                    time.sleep(1)
                                    break
                        except:
                            pass

                        break
            except:
                pass

            logger.info("")
            logger.info("   ⚠️  UI automation may need manual completion")
            logger.info("   💡 Please complete setup using settings below")

        except Exception as e:
            logger.warning(f"   ⚠️  Could not connect to Outlook: {e}")
            logger.info("   💡 Please ensure New Outlook is open")
            logger.info("   💡 Then follow manual steps below")

    except ImportError:
        logger.warning("   ⚠️  UI automation libraries not available")
        logger.info("   💡 Install: pip install pywinauto pyautogui")
        logger.info("   💡 Or follow manual steps below")

    logger.info("")
    logger.info("="*80)
    logger.info("📋 MANUAL STEPS (if automation didn't complete)")
    logger.info("="*80)
    logger.info("")
    logger.info("REMOVE GMAIL:")
    logger.info("   1. New Outlook → File → Account Settings → Account Settings")
    logger.info("   2. Select Gmail account")
    logger.info("   3. Click 'Remove'")
    logger.info("   4. Confirm removal")
    logger.info("")
    logger.info("ADD NAS EMAIL:")
    logger.info("   1. File → Add Account")
    logger.info("   2. Advanced setup → IMAP")
    logger.info(f"   3. Email: {COMPANY_EMAIL}")
    logger.info(f"   4. IMAP: {NAS_MAIL_SERVER}:{NAS_IMAP_PORT} (SSL/TLS)")
    logger.info(f"   5. SMTP: {NAS_MAIL_SERVER}:{NAS_SMTP_PORT} (STARTTLS)")
    logger.info("")
    logger.info("="*80)
    logger.info("✅ Setup process initiated")
    logger.info("="*80)

    return 0

if __name__ == "__main__":


    exit(main())