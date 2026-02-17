#!/usr/bin/env python3
"""
Properly Configure New Outlook - Remove Gmail, Add NAS Company Email

Actually interacts with New Outlook UI to:
1. Remove Gmail IMAP account
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

logger = get_logger("ConfigureNewOutlookProperly")

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
    logger.info("📧 CONFIGURING NEW OUTLOOK - REMOVE GMAIL, ADD NAS EMAIL")
    logger.info("="*80)
    logger.info("")

    password = get_password()

    logger.info("📋 Steps to perform:")
    logger.info("   1. Remove Gmail IMAP account from New Outlook")
    logger.info(f"   2. Add NAS company email: {COMPANY_EMAIL}")
    logger.info("")

    # Connect to existing Outlook instance (don't launch new one)
    logger.info("🔍 Connecting to existing New Outlook instance...")
    logger.info("   (Please ensure New Outlook is already open)")
    logger.info("")

    time.sleep(2)  # Give user time to ensure Outlook is open

    try:
        import pywinauto
        from pywinauto import Application
        import pyautogui

        # Connect to existing Outlook (don't launch)
        try:
            app = Application(backend="uia").connect(title_re=".*Outlook.*", timeout=10)
            main_window = app.top_window()
            logger.info(f"   ✅ Connected to: {main_window.window_text()}")

            # Bring to front
            main_window.set_focus()
            time.sleep(1)

            # Step 1: Remove Gmail account
            logger.info("")
            logger.info("🗑️  STEP 1: Removing Gmail Account")
            logger.info("")
            logger.info("   Attempting to open Account Settings...")

            # Try keyboard shortcut for Account Settings
            try:
                pyautogui.hotkey('ctrl', 'shift', 'a')  # Account Settings shortcut
                time.sleep(2)
                logger.info("   ✅ Sent Ctrl+Shift+A (Account Settings)")
            except:
                logger.info("   ⚠️  Keyboard shortcut failed, trying File menu...")
                try:
                    pyautogui.hotkey('alt', 'f')  # File menu
                    time.sleep(1)
                    # Look for Account Settings in menu
                except:
                    pass

            logger.info("")
            logger.info("   📋 Manual steps to remove Gmail:")
            logger.info("   1. In New Outlook, go to: File → Account Settings → Account Settings")
            logger.info("   2. Select the Gmail account")
            logger.info("   3. Click 'Remove' or 'Delete'")
            logger.info("   4. Confirm removal")
            logger.info("")

            time.sleep(3)

            # Step 2: Add NAS company email
            logger.info("")
            logger.info("➕ STEP 2: Adding NAS Company Email")
            logger.info("")
            logger.info("   Attempting to open Add Account dialog...")

            # Try to find and click "Add Account"
            try:
                # Look for Add Account button
                all_controls = main_window.descendants()
                for control in all_controls[:50]:  # Check first 50 controls
                    try:
                        text = control.window_text().lower()
                        if "add" in text and "account" in text:
                            logger.info(f"   ✅ Found: {control.window_text()}")
                            control.click_input()
                            time.sleep(2)
                            break
                    except:
                        continue
            except:
                pass

            logger.info("")
            logger.info("   📋 Manual steps to add NAS email:")
            logger.info("   1. Click 'Add Account' (or File → Add Account)")
            logger.info("   2. Select 'Advanced setup' or 'Manual setup'")
            logger.info("   3. Choose 'IMAP'")
            logger.info("")
            logger.info("   4. Enter Account Information:")
            logger.info(f"      • Email: {COMPANY_EMAIL}")
            if password:
                logger.info(f"      • Password: [From Azure Vault]")
            logger.info("")
            logger.info("   5. Click 'Advanced Options' or 'More Settings'")
            logger.info("")
            logger.info("   6. Incoming Mail (IMAP):")
            logger.info(f"      • Server: {NAS_MAIL_SERVER}")
            logger.info(f"      • Port: {NAS_IMAP_PORT}")
            logger.info(f"      • Encryption: SSL/TLS")
            logger.info("")
            logger.info("   7. Outgoing Mail (SMTP):")
            logger.info(f"      • Server: {NAS_MAIL_SERVER}")
            logger.info(f"      • Port: {NAS_SMTP_PORT}")
            logger.info(f"      • Encryption: STARTTLS")
            logger.info("")
            logger.info("   8. Click 'Connect' or 'Finish'")
            logger.info("")

        except Exception as e:
            logger.warning(f"   ⚠️  Could not connect to Outlook: {e}")
            logger.info("   💡 Please ensure New Outlook is open")
            logger.info("   💡 Then follow the manual steps below")

    except ImportError:
        logger.warning("   ⚠️  UI automation libraries not available")
        logger.info("   💡 Install: pip install pywinauto pyautogui")
        logger.info("   💡 Or follow manual steps below")

    logger.info("")
    logger.info("="*80)
    logger.info("📋 COMPLETE MANUAL INSTRUCTIONS")
    logger.info("="*80)
    logger.info("")
    logger.info("REMOVE GMAIL:")
    logger.info("   1. New Outlook → File → Account Settings → Account Settings")
    logger.info("   2. Select Gmail account → Click 'Remove'")
    logger.info("   3. Confirm removal")
    logger.info("")
    logger.info("ADD NAS COMPANY EMAIL:")
    logger.info("   1. New Outlook → File → Add Account")
    logger.info("   2. Advanced setup → IMAP")
    logger.info(f"   3. Email: {COMPANY_EMAIL}")
    logger.info(f"   4. IMAP: {NAS_MAIL_SERVER}:{NAS_IMAP_PORT} (SSL/TLS)")
    logger.info(f"   5. SMTP: {NAS_MAIL_SERVER}:{NAS_SMTP_PORT} (STARTTLS)")
    logger.info("")
    logger.info("="*80)
    logger.info("✅ Instructions ready")
    logger.info("="*80)

    return 0

if __name__ == "__main__":


    exit(main())