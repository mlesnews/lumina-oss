#!/usr/bin/env python3
"""
Configure New Outlook to Connect to NAS Mail Hub

Sets up the new Outlook app (not classic Outlook) to pull from company email on NAS.
Leaves old Outlook configuration unchanged.

Tags: #DOIT #OUTLOOK #EMAIL #NAS @JARVIS
"""

import sys
import json
import winreg
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

logger = get_logger("ConfigureNewOutlook")

# NAS Mail Hub Configuration
NAS_MAIL_SERVER = "<NAS_PRIMARY_IP>"
NAS_IMAP_PORT = 993
NAS_SMTP_PORT = 587  # Or 465 for SSL
COMPANY_EMAIL = "mlesn@<LOCAL_HOSTNAME>"
COMPANY_DOMAIN = "<LOCAL_HOSTNAME>"

def get_email_password():
    """Get email password from Azure Vault"""
    try:
        vault = AzureKeyVaultClient(vault_url="https://jarvis-lumina.vault.azure.net/")
        # Try different secret names
        for secret_name in ["nas-email-password", "company-email-password", "email-password", "n8n-password"]:
            try:
                password = vault.get_secret(secret_name)
                if password:
                    logger.info(f"   ✅ Retrieved password from: {secret_name}")
                    return password
            except:
                continue
        logger.warning("   ⚠️  Could not find email password in Azure Vault")
        return None
    except Exception as e:
        logger.error(f"   ❌ Failed to access Azure Vault: {e}")
        return None

def configure_new_outlook_via_registry():
    """Configure New Outlook via Windows Registry"""

    logger.info("="*80)
    logger.info("📧 CONFIGURING NEW OUTLOOK FOR NAS MAIL HUB")
    logger.info("="*80)
    logger.info("")

    # New Outlook uses different registry paths than classic Outlook
    # New Outlook stores accounts in: HKEY_CURRENT_USER\Software\Microsoft\Office\16.0\Outlook\Profiles

    logger.info("🔍 Checking New Outlook installation...")

    # Check if New Outlook is installed
    new_outlook_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\olk.exe",  # New Outlook
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\OUTLOOK.EXE",  # Classic Outlook
    ]

    outlook_found = False
    for path in new_outlook_paths:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
            outlook_found = True
            outlook_exe, _ = winreg.QueryValueEx(key, "")
            logger.info(f"   ✅ Found Outlook at: {outlook_exe}")
            winreg.CloseKey(key)
            break
        except FileNotFoundError:
            continue

    if not outlook_found:
        logger.warning("   ⚠️  Outlook not found in registry")
        logger.info("   💡 New Outlook may need to be installed or configured manually")

    logger.info("")
    logger.info("📋 New Outlook Configuration:")
    logger.info(f"   Email Account: {COMPANY_EMAIL}")
    logger.info(f"   IMAP Server: {NAS_MAIL_SERVER}")
    logger.info(f"   IMAP Port: {NAS_IMAP_PORT} (SSL/TLS)")
    logger.info(f"   SMTP Server: {NAS_MAIL_SERVER}")
    logger.info(f"   SMTP Port: {NAS_SMTP_PORT}")
    logger.info("")

    password = get_email_password()
    if password:
        logger.info(f"   ✅ Password retrieved from Azure Vault")
    else:
        logger.warning("   ⚠️  Password not found - you'll need to enter it manually")

    logger.info("")
    logger.info("="*80)
    logger.info("📝 MANUAL CONFIGURATION REQUIRED")
    logger.info("="*80)
    logger.info("")
    logger.info("New Outlook requires manual account setup through the app UI.")
    logger.info("")
    logger.info("🚀 Steps to Configure New Outlook:")
    logger.info("")
    logger.info("1. Open New Outlook app")
    logger.info("2. Click 'Add Account' or 'File' → 'Add Account'")
    logger.info("3. Select 'Advanced setup' or 'Manual setup'")
    logger.info("4. Choose 'IMAP' account type")
    logger.info("")
    logger.info("5. Enter Account Settings:")
    logger.info(f"   • Your Name: Your Display Name")
    logger.info(f"   • Email Address: {COMPANY_EMAIL}")
    logger.info(f"   • Password: [From Azure Vault or enter manually]")
    logger.info("")
    logger.info("6. Click 'Advanced Options' or 'More Settings'")
    logger.info("")
    logger.info("7. Incoming Mail Server (IMAP):")
    logger.info(f"   • Server: {NAS_MAIL_SERVER}")
    logger.info(f"   • Port: {NAS_IMAP_PORT}")
    logger.info(f"   • Encryption: SSL/TLS")
    logger.info(f"   • Authentication: Use same as incoming")
    logger.info("")
    logger.info("8. Outgoing Mail Server (SMTP):")
    logger.info(f"   • Server: {NAS_MAIL_SERVER}")
    logger.info(f"   • Port: {NAS_SMTP_PORT} (or 465 for SSL)")
    logger.info(f"   • Encryption: STARTTLS (or SSL)")
    logger.info(f"   • Authentication: Use same as incoming")
    logger.info("")
    logger.info("9. Click 'Connect' or 'Finish'")
    logger.info("")
    logger.info("✅ New Outlook will now pull emails from NAS Mail Hub")
    logger.info("")
    logger.info("="*80)

    # Create a configuration file for reference
    config = {
        "account_name": COMPANY_EMAIL,
        "display_name": "Company Email (NAS)",
        "imap": {
            "server": NAS_MAIL_SERVER,
            "port": NAS_IMAP_PORT,
            "encryption": "SSL/TLS",
            "username": COMPANY_EMAIL
        },
        "smtp": {
            "server": NAS_MAIL_SERVER,
            "port": NAS_SMTP_PORT,
            "encryption": "STARTTLS",
            "username": COMPANY_EMAIL
        },
        "notes": "New Outlook configuration - leaves old Outlook unchanged"
    }

    config_file = project_root / "config" / "new_outlook_nas_config.json"
    config_file.parent.mkdir(parents=True, exist_ok=True)

    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

    logger.info(f"💾 Configuration saved to: {config_file}")
    logger.info("")

    return 0

def main():
    """Main execution"""
    return configure_new_outlook_via_registry()

if __name__ == "__main__":


    exit(main())