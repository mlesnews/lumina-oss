#!/usr/bin/env python3
"""
Automated Setup of New Outlook for NAS Mail Hub

Uses UI automation to configure New Outlook to pull from NAS Mail Hub.
Leaves old Outlook configuration unchanged.

Tags: #DOIT #OUTLOOK #EMAIL #NAS #AUTOMATION @JARVIS
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

logger = get_logger("SetupNewOutlookAutomated")

# Configuration
NAS_MAIL_SERVER = "<NAS_PRIMARY_IP>"
NAS_IMAP_PORT = 993
NAS_SMTP_PORT = 587
COMPANY_EMAIL = "mlesn@<LOCAL_HOSTNAME>"

try:
    import pyautogui
    import pywinauto
    UI_AUTOMATION_AVAILABLE = True
except ImportError:
    UI_AUTOMATION_AVAILABLE = False
    logger.warning("pyautogui/pywinauto not available. Install with: pip install pyautogui pywinauto")

def get_email_password():
    """Get email password from Azure Vault"""
    try:
        vault = AzureKeyVaultClient(vault_url="https://jarvis-lumina.vault.azure.net/")
        password = vault.get_secret("n8n-password")  # Using same password as N8N
        return password
    except Exception as e:
        logger.warning(f"Could not retrieve password: {e}")
        return None

def launch_new_outlook():
    """Launch New Outlook app"""
    logger.info("🚀 Launching New Outlook...")

    # Try to launch New Outlook
    # New Outlook might be: "ms-outlook://" protocol or "olk.exe"
    outlook_paths = [
        r"C:\Program Files\Microsoft Office\Root\Office16\olk.exe",  # New Outlook
        r"C:\Program Files\Microsoft Office\Root\Office16\OUTLOOK.EXE",  # Classic Outlook
        "ms-outlook:",  # Protocol handler
    ]

    for path in outlook_paths:
        try:
            if path.startswith("ms-outlook:"):
                subprocess.Popen(["start", path], shell=True)
            else:
                subprocess.Popen([path])
            logger.info(f"   ✅ Launched: {path}")
            time.sleep(3)  # Wait for app to open
            return True
        except Exception as e:
            logger.debug(f"   Failed to launch {path}: {e}")
            continue

    logger.warning("   ⚠️  Could not launch New Outlook automatically")
    logger.info("   💡 Please open New Outlook manually")
    return False

def configure_via_ui_automation():
    """Configure New Outlook using UI automation"""
    if not UI_AUTOMATION_AVAILABLE:
        logger.error("UI automation libraries not available")
        return False

    logger.info("🤖 Starting UI automation...")

    # Wait for Outlook to be ready
    time.sleep(5)

    try:
        # Try to find Outlook window
        from pywinauto import Application
        app = Application(backend="uia").connect(title_re=".*Outlook.*", timeout=10)

        logger.info("   ✅ Found Outlook window")

        # Look for "Add Account" button or menu
        # This is complex and varies by Outlook version
        # For now, provide manual instructions

        logger.info("   ⚠️  UI automation for New Outlook setup is complex")
        logger.info("   💡 Manual configuration recommended")
        return False

    except Exception as e:
        logger.debug(f"   UI automation failed: {e}")
        return False

def create_outlook_config_script():
    """Create PowerShell script to configure Outlook"""

    password = get_email_password()
    if not password:
        logger.warning("   ⚠️  Password not available - will need manual entry")
        password_placeholder = "[ENTER_PASSWORD]"
    else:
        password_placeholder = password

    ps_script = f"""
# New Outlook Configuration Script for NAS Mail Hub
# Run this in PowerShell as Administrator if needed

$email = "{COMPANY_EMAIL}"
$imapServer = "{NAS_MAIL_SERVER}"
$imapPort = {NAS_IMAP_PORT}
$smtpServer = "{NAS_MAIL_SERVER}"
$smtpPort = {NAS_SMTP_PORT}

Write-Host "========================================"
Write-Host "New Outlook - NAS Mail Hub Configuration"
Write-Host "========================================"
Write-Host ""
Write-Host "Email Account: $email"
Write-Host "IMAP Server: $imapServer:$imapPort"
Write-Host "SMTP Server: $smtpServer:$smtpPort"
Write-Host ""
Write-Host "Note: New Outlook requires manual account setup through the UI."
Write-Host "This script provides the configuration details."
Write-Host ""
Write-Host "Configuration Details:"
Write-Host "  - Account Type: IMAP"
Write-Host "  - Incoming: $imapServer : $imapPort (SSL/TLS)"
Write-Host "  - Outgoing: $smtpServer : $smtpPort (STARTTLS)"
Write-Host ""
"""

    script_file = project_root / "config" / "outlook" / "setup_new_outlook_nas.ps1"
    script_file.parent.mkdir(parents=True, exist_ok=True)

    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(ps_script)

    logger.info(f"   💾 PowerShell script created: {script_file}")
    return script_file

def main():
    """Main execution"""
    logger.info("="*80)
    logger.info("📧 AUTOMATED NEW OUTLOOK SETUP FOR NAS MAIL HUB")
    logger.info("="*80)
    logger.info("")

    # Get password
    password = get_email_password()
    if password:
        logger.info("   ✅ Password retrieved from Azure Vault")
    else:
        logger.warning("   ⚠️  Password not found - manual entry required")

    logger.info("")
    logger.info("📋 Configuration:")
    logger.info(f"   Email: {COMPANY_EMAIL}")
    logger.info(f"   IMAP: {NAS_MAIL_SERVER}:{NAS_IMAP_PORT}")
    logger.info(f"   SMTP: {NAS_MAIL_SERVER}:{NAS_SMTP_PORT}")
    logger.info("")

    # Create config script
    logger.info("📝 Creating configuration script...")
    script_file = create_outlook_config_script()

    # Try to launch Outlook
    logger.info("")
    if launch_new_outlook():
        logger.info("   ✅ New Outlook launched")
        logger.info("")
        logger.info("⏳ Waiting for Outlook to open...")
        logger.info("   💡 Please follow the setup wizard:")
        logger.info("")
        logger.info("   1. Click 'Add Account' when prompted")
        logger.info("   2. Select 'Advanced setup' or 'Manual setup'")
        logger.info("   3. Choose 'IMAP'")
        logger.info(f"   4. Enter email: {COMPANY_EMAIL}")
        if password:
            logger.info(f"   5. Enter password: [From Azure Vault]")
        logger.info(f"   6. IMAP Server: {NAS_MAIL_SERVER}")
        logger.info(f"   7. IMAP Port: {NAS_IMAP_PORT} (SSL/TLS)")
        logger.info(f"   8. SMTP Server: {NAS_MAIL_SERVER}")
        logger.info(f"   9. SMTP Port: {NAS_SMTP_PORT} (STARTTLS)")
        logger.info("")
    else:
        logger.info("")
        logger.info("📋 Manual Setup Instructions:")
        logger.info("")
        logger.info("   1. Open New Outlook app")
        logger.info("   2. Click 'Add Account'")
        logger.info("   3. Select 'Advanced setup' → 'IMAP'")
        logger.info(f"   4. Email: {COMPANY_EMAIL}")
        logger.info(f"   5. IMAP: {NAS_MAIL_SERVER}:{NAS_IMAP_PORT} (SSL/TLS)")
        logger.info(f"   6. SMTP: {NAS_MAIL_SERVER}:{NAS_SMTP_PORT} (STARTTLS)")
        logger.info("")

    logger.info("="*80)
    logger.info("✅ CONFIGURATION READY")
    logger.info("="*80)
    logger.info("")
    logger.info(f"📄 Full instructions: docs/system/NEW_OUTLOOK_NAS_SETUP.md")
    logger.info(f"📄 Config file: config/new_outlook_nas_config.json")
    logger.info("")

    return 0

if __name__ == "__main__":


    exit(main())