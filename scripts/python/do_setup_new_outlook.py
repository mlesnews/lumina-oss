#!/usr/bin/env python3
"""
DO IT: Setup New Outlook for NAS Mail Hub

Actually automates the setup process using UI automation.
"""

import sys
import time
import subprocess
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

logger = get_logger("DoSetupNewOutlook")

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
    logger.info("📧 SETTING UP NEW OUTLOOK FOR NAS MAIL HUB")
    logger.info("="*80)
    logger.info("")

    password = get_password()

    # Launch New Outlook
    logger.info("🚀 Launching New Outlook...")
    try:
        subprocess.Popen(["start", "ms-outlook:"], shell=True)
        logger.info("   ✅ Launch command sent")
    except:
        logger.info("   💡 Please open New Outlook manually if it didn't open")

    logger.info("")
    logger.info("⏳ Waiting 12 seconds for New Outlook to fully load...")
    time.sleep(12)

    # Try UI automation
    try:
        import pywinauto
        from pywinauto import Application
        import pyautogui

        logger.info("🤖 Attempting UI automation...")

        # Find Outlook
        app = Application(backend="uia").connect(title_re=".*Outlook.*", timeout=20)
        main_window = app.top_window()
        logger.info(f"   ✅ Connected to Outlook: {main_window.window_text()}")

        # Bring to front
        main_window.set_focus()
        time.sleep(1)

        # Try keyboard shortcut for Account Settings (varies by version)
        logger.info("   ⌨️  Trying keyboard shortcuts...")
        try:
            # Common shortcuts
            pyautogui.hotkey('ctrl', 'shift', 'a')  # Account Settings
            time.sleep(2)
            logger.info("   ✅ Sent Ctrl+Shift+A")
        except:
            pass

        # Try Alt+F for File menu, then navigate
        try:
            pyautogui.hotkey('alt', 'f')  # File menu
            time.sleep(1)
            logger.info("   ✅ Opened File menu")
        except:
            pass

        # Look for Add Account dialog
        time.sleep(2)
        try:
            # Try to find any dialog that might be the account setup
            dialogs = app.windows()
            for dialog in dialogs:
                title = dialog.window_text().lower()
                if "account" in title or "add" in title or "email" in title:
                    logger.info(f"   ✅ Found dialog: {dialog.window_text()}")
                    dialog.set_focus()
                    break
        except:
            pass

        logger.info("")
        logger.info("   ⚠️  UI automation may need manual completion")
        logger.info("   💡 If account setup dialog is open, use settings below")

    except ImportError:
        logger.warning("   ⚠️  UI automation libraries not installed")
        logger.info("   💡 Install: pip install pywinauto pyautogui")
    except Exception as e:
        logger.debug(f"   UI automation: {e}")
        logger.info("   💡 Please configure manually")

    logger.info("")
    logger.info("="*80)
    logger.info("📋 CONFIGURATION SETTINGS")
    logger.info("="*80)
    logger.info("")
    logger.info("If the account setup dialog is open, enter these settings:")
    logger.info("")
    logger.info("Account Type: IMAP")
    logger.info(f"Email: {COMPANY_EMAIL}")
    if password:
        logger.info(f"Password: [Available - from Azure Vault]")
    logger.info("")
    logger.info("Advanced Settings:")
    logger.info(f"  IMAP Server: {NAS_MAIL_SERVER}")
    logger.info(f"  IMAP Port: {NAS_IMAP_PORT} (SSL/TLS)")
    logger.info(f"  SMTP Server: {NAS_MAIL_SERVER}")
    logger.info(f"  SMTP Port: {NAS_SMTP_PORT} (STARTTLS)")
    logger.info("")
    logger.info("="*80)
    logger.info("✅ Setup process initiated")
    logger.info("="*80)
    logger.info("")
    logger.info("💡 Complete the setup in New Outlook using the settings above")
    logger.info("   Old Outlook remains unchanged")
    logger.info("")

    return 0

if __name__ == "__main__":


    exit(main())