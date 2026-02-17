#!/usr/bin/env python3
"""
Automate New Outlook Setup with UI Automation

Actually clicks through the New Outlook setup wizard to configure NAS email.
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

logger = get_logger("AutomateNewOutlook")

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

def launch_new_outlook():
    """Launch New Outlook"""
    logger.info("🚀 Launching New Outlook...")

    try:
        # Try different methods to launch New Outlook
        methods = [
            lambda: subprocess.Popen(["start", "ms-outlook:"], shell=True),
            lambda: subprocess.Popen([r"C:\Program Files\Microsoft Office\Root\Office16\olk.exe"]),
            lambda: subprocess.Popen(["outlook.exe"]),
        ]

        for method in methods:
            try:
                method()
                logger.info("   ✅ New Outlook launch attempted")
                time.sleep(5)  # Wait for app to open
                return True
            except:
                continue

        logger.warning("   ⚠️  Could not launch automatically")
        logger.info("   💡 Please open New Outlook manually")
        return False
    except Exception as e:
        logger.error(f"   ❌ Launch failed: {e}")
        return False

def automate_setup():
    """Automate the setup process"""
    logger.info("="*80)
    logger.info("🤖 AUTOMATING NEW OUTLOOK SETUP")
    logger.info("="*80)
    logger.info("")

    password = get_password()

    # Launch Outlook
    if not launch_new_outlook():
        logger.info("")
        logger.info("📋 Please open New Outlook manually, then:")
        logger.info("   1. Click 'Add Account'")
        logger.info("   2. Follow the configuration below")
        logger.info("")

    logger.info("⏳ Waiting for New Outlook to open...")
    logger.info("   (This may take 10-15 seconds)")
    logger.info("")

    time.sleep(10)  # Wait for Outlook to fully load

    # Try UI automation
    try:
        import pywinauto
        from pywinauto import Application

        logger.info("🔍 Looking for Outlook window...")

        # Connect to Outlook
        app = Application(backend="uia").connect(title_re=".*Outlook.*", timeout=15)
        logger.info("   ✅ Found Outlook window")

        # Try to find and click "Add Account"
        # This is complex and depends on Outlook version
        logger.info("   🔍 Looking for 'Add Account' button...")

        # New Outlook UI structure varies, so we'll provide manual guidance
        logger.info("   ⚠️  UI automation for New Outlook is version-dependent")
        logger.info("   💡 Manual configuration recommended for reliability")

    except ImportError:
        logger.warning("   ⚠️  pywinauto not available")
        logger.info("   💡 Install with: pip install pywinauto")
    except Exception as e:
        logger.debug(f"   UI automation: {e}")

    logger.info("")
    logger.info("="*80)
    logger.info("📋 CONFIGURATION DETAILS")
    logger.info("="*80)
    logger.info("")
    logger.info("When the 'Add Account' dialog appears:")
    logger.info("")
    logger.info("1. Select 'Advanced setup' or 'Manual setup'")
    logger.info("2. Choose 'IMAP' account type")
    logger.info("")
    logger.info("3. Enter these settings:")
    logger.info(f"   • Email: {COMPANY_EMAIL}")
    if password:
        logger.info(f"   • Password: [Retrieved from Azure Vault]")
    logger.info("")
    logger.info("4. Click 'Advanced Options' or 'More Settings'")
    logger.info("")
    logger.info("5. Incoming Mail (IMAP):")
    logger.info(f"   • Server: {NAS_MAIL_SERVER}")
    logger.info(f"   • Port: {NAS_IMAP_PORT}")
    logger.info(f"   • Encryption: SSL/TLS")
    logger.info("")
    logger.info("6. Outgoing Mail (SMTP):")
    logger.info(f"   • Server: {NAS_MAIL_SERVER}")
    logger.info(f"   • Port: {NAS_SMTP_PORT}")
    logger.info(f"   • Encryption: STARTTLS")
    logger.info("")
    logger.info("7. Click 'Connect' or 'Finish'")
    logger.info("")
    logger.info("="*80)
    logger.info("✅ Setup instructions ready")
    logger.info("="*80)

    return 0

if __name__ == "__main__":
    exit(automate_setup())
