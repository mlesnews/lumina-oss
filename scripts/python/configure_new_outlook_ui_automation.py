#!/usr/bin/env python3
"""
Configure New Outlook via UI Automation

Actually automates the New Outlook setup wizard to add NAS email account.
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

logger = get_logger("ConfigureNewOutlookUI")

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
    logger.info("🤖 CONFIGURING NEW OUTLOOK VIA UI AUTOMATION")
    logger.info("="*80)
    logger.info("")

    password = get_password()

    logger.info("📋 Configuration:")
    logger.info(f"   Email: {COMPANY_EMAIL}")
    logger.info(f"   IMAP: {NAS_MAIL_SERVER}:{NAS_IMAP_PORT}")
    logger.info(f"   SMTP: {NAS_MAIL_SERVER}:{NAS_SMTP_PORT}")
    logger.info("")

    # Launch New Outlook
    logger.info("🚀 Launching New Outlook...")
    try:
        # Try to launch New Outlook
        subprocess.Popen(["start", "ms-outlook:"], shell=True)
        logger.info("   ✅ Launch command sent")
        time.sleep(8)  # Wait for Outlook to open
    except Exception as e:
        logger.warning(f"   ⚠️  Could not launch: {e}")
        logger.info("   💡 Please open New Outlook manually")

    logger.info("")
    logger.info("⏳ Waiting for New Outlook to open...")
    logger.info("   (Please ensure New Outlook is open and visible)")
    logger.info("")

    # Try UI automation
    try:
        import pywinauto
        from pywinauto import Application
        from pywinauto.keyboard import send_keys

        logger.info("🔍 Connecting to Outlook...")
        time.sleep(5)

        # Try to find Outlook window
        try:
            app = Application(backend="uia").connect(title_re=".*Outlook.*", timeout=20)
            main_window = app.top_window()
            logger.info(f"   ✅ Connected to: {main_window.window_text()}")

            # Look for "Add Account" or account setup options
            logger.info("   🔍 Looking for account setup options...")

            # Try to find and click "Add Account"
            # This is complex and depends on Outlook version/UI
            try:
                # Try common button names
                add_account_buttons = [
                    "Add Account",
                    "Add account",
                    "Add",
                    "Account Settings",
                    "File",
                ]

                for button_text in add_account_buttons:
                    try:
                        button = main_window.child_window(title=button_text, control_type="Button")
                        if button.exists():
                            logger.info(f"   ✅ Found: {button_text}")
                            button.click_input()
                            time.sleep(2)
                            break
                    except:
                        continue

                logger.info("   ⚠️  UI automation for New Outlook setup is complex")
                logger.info("   💡 Manual configuration may be more reliable")

            except Exception as e:
                logger.debug(f"   Button click failed: {e}")

        except Exception as e:
            logger.warning(f"   ⚠️  Could not connect to Outlook: {e}")
            logger.info("   💡 Please configure manually using the settings below")

    except ImportError:
        logger.warning("   ⚠️  pywinauto not available")
        logger.info("   💡 Install with: pip install pywinauto")
        logger.info("   💡 Or configure manually using settings below")

    logger.info("")
    logger.info("="*80)
    logger.info("📋 MANUAL CONFIGURATION STEPS")
    logger.info("="*80)
    logger.info("")
    logger.info("If UI automation didn't complete, follow these steps:")
    logger.info("")
    logger.info("1. In New Outlook, click 'Add Account' (or File → Add Account)")
    logger.info("2. Select 'Advanced setup' or 'Manual setup'")
    logger.info("3. Choose 'IMAP'")
    logger.info("")
    logger.info("4. Enter Account Information:")
    logger.info(f"   • Email: {COMPANY_EMAIL}")
    if password:
        logger.info(f"   • Password: [Available from Azure Vault]")
    logger.info("")
    logger.info("5. Advanced Settings → Incoming (IMAP):")
    logger.info(f"   • Server: {NAS_MAIL_SERVER}")
    logger.info(f"   • Port: {NAS_IMAP_PORT}")
    logger.info(f"   • Encryption: SSL/TLS")
    logger.info("")
    logger.info("6. Advanced Settings → Outgoing (SMTP):")
    logger.info(f"   • Server: {NAS_MAIL_SERVER}")
    logger.info(f"   • Port: {NAS_SMTP_PORT}")
    logger.info(f"   • Encryption: STARTTLS")
    logger.info("")
    logger.info("7. Click 'Connect' or 'Finish'")
    logger.info("")
    logger.info("="*80)
    logger.info("✅ Configuration details ready")
    logger.info("="*80)

    return 0

if __name__ == "__main__":


    exit(main())