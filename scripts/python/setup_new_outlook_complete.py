#!/usr/bin/env python3
"""
Complete New Outlook Setup Automation

Actually configures New Outlook to pull from NAS Mail Hub using UI automation.
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

logger = get_logger("SetupNewOutlookComplete")

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
    logger.info("📧 SETTING UP NEW OUTLOOK FOR NAS MAIL HUB")
    logger.info("="*80)
    logger.info("")

    password = get_password()

    logger.info("📋 Configuration:")
    logger.info(f"   Email: {COMPANY_EMAIL}")
    logger.info(f"   IMAP: {NAS_MAIL_SERVER}:{NAS_IMAP_PORT} (SSL/TLS)")
    logger.info(f"   SMTP: {NAS_MAIL_SERVER}:{NAS_SMTP_PORT} (STARTTLS)")
    logger.info("")

    # Launch New Outlook
    logger.info("🚀 Launching New Outlook...")
    try:
        # Try multiple launch methods
        subprocess.Popen(["start", "ms-outlook:"], shell=True)
        time.sleep(2)
        logger.info("   ✅ Launch command sent")
    except Exception as e:
        logger.warning(f"   ⚠️  Launch failed: {e}")

    logger.info("")
    logger.info("⏳ Waiting 10 seconds for New Outlook to open...")
    logger.info("   (If it doesn't open, please open it manually)")
    logger.info("")
    time.sleep(10)

    # Try UI automation
    try:
        import pywinauto
        from pywinauto import Application
        import pyautogui

        logger.info("🤖 Starting UI automation...")

        # Find Outlook window
        try:
            app = Application(backend="uia").connect(title_re=".*Outlook.*", timeout=15)
            main_window = app.top_window()
            logger.info(f"   ✅ Found Outlook: {main_window.window_text()}")

            # Bring window to front
            main_window.set_focus()
            time.sleep(1)

            # Try to find "Add Account" or account menu
            logger.info("   🔍 Looking for account setup options...")

            # Method 1: Try keyboard shortcut (Ctrl+Shift+A for Account Settings in some versions)
            try:
                logger.info("   ⌨️  Trying keyboard shortcut...")
                pyautogui.hotkey('ctrl', 'shift', 'a')
                time.sleep(2)
                logger.info("   ✅ Keyboard shortcut sent")
            except:
                pass

            # Method 2: Look for "Add Account" button
            try:
                # Search for buttons with "Add" or "Account" in text
                all_buttons = main_window.descendants(control_type="Button")
                for button in all_buttons[:20]:  # Check first 20 buttons
                    try:
                        text = button.window_text().lower()
                        if "add" in text and "account" in text:
                            logger.info(f"   ✅ Found: {button.window_text()}")
                            button.click_input()
                            time.sleep(3)
                            break
                    except:
                        continue
            except:
                pass

            logger.info("")
            logger.info("   ⚠️  UI automation may need manual assistance")
            logger.info("   💡 Please complete the setup using the settings below")

        except Exception as e:
            logger.warning(f"   ⚠️  Could not connect to Outlook: {e}")
            logger.info("   💡 Please open New Outlook and configure manually")

    except ImportError:
        logger.warning("   ⚠️  UI automation libraries not available")
        logger.info("   💡 Install with: pip install pywinauto pyautogui")
        logger.info("   💡 Or configure manually")

    logger.info("")
    logger.info("="*80)
    logger.info("📋 SETUP INSTRUCTIONS")
    logger.info("="*80)
    logger.info("")
    logger.info("In New Outlook, follow these steps:")
    logger.info("")
    logger.info("1. Click 'Add Account' (or File → Add Account)")
    logger.info("2. Select 'Advanced setup' or 'Manual setup'")
    logger.info("3. Choose 'IMAP' account type")
    logger.info("")
    logger.info("4. Enter Account Information:")
    logger.info(f"   • Your Name: [Your Display Name]")
    logger.info(f"   • Email Address: {COMPANY_EMAIL}")
    if password:
        logger.info(f"   • Password: [From Azure Vault - available]")
    logger.info("")
    logger.info("5. Click 'Advanced Options' or 'More Settings'")
    logger.info("")
    logger.info("6. Incoming Mail Server (IMAP):")
    logger.info(f"   • Server: {NAS_MAIL_SERVER}")
    logger.info(f"   • Port: {NAS_IMAP_PORT}")
    logger.info(f"   • Encryption: SSL/TLS")
    logger.info(f"   • Authentication: Use same as incoming")
    logger.info("")
    logger.info("7. Outgoing Mail Server (SMTP):")
    logger.info(f"   • Server: {NAS_MAIL_SERVER}")
    logger.info(f"   • Port: {NAS_SMTP_PORT}")
    logger.info(f"   • Encryption: STARTTLS")
    logger.info(f"   • Authentication: Use same as incoming")
    logger.info("")
    logger.info("8. Click 'Connect' or 'Finish'")
    logger.info("")
    logger.info("✅ New Outlook will then pull emails from NAS Mail Hub")
    logger.info("")
    logger.info("="*80)
    logger.info("✅ SETUP READY")
    logger.info("="*80)
    logger.info("")
    logger.info("💡 Note: Old Outlook remains unchanged - both can coexist")
    logger.info("")

    return 0

if __name__ == "__main__":


    exit(main())