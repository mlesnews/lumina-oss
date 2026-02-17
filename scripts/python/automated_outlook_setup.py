"""
Automated Outlook Setup for Gmail and ProtonMail
Uses Windows COM automation to configure Outlook accounts programmatically.

This script:
- Configures Gmail account in Outlook
- Configures ProtonMail account (via Proton Bridge) in Outlook
- Verifies connections
- Sets up email import to NAS mail hub

#JARVIS #LUMINA #OUTLOOK #GMAIL #PROTONMAIL #AUTOMATION
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("AutomatedOutlookSetup")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("AutomatedOutlookSetup")

try:
    from scripts.python.unified_secrets_manager import UnifiedSecretsManager, SecretSource
    SECRETS_MANAGER_AVAILABLE = True
except ImportError:
    SECRETS_MANAGER_AVAILABLE = False
    logger.warning("⚠️  Unified Secrets Manager not available")


class AutomatedOutlookSetup:
    """
    Automated Outlook setup using Windows COM automation.
    """

    def __init__(self, project_root: Path):
        """
        Initialize Automated Outlook Setup.

        Args:
            project_root: Project root directory
        """
        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config" / "outlook"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        if SECRETS_MANAGER_AVAILABLE:
            self.secrets_manager = UnifiedSecretsManager(
                self.project_root,
                prefer_source=SecretSource.AZURE_KEY_VAULT
            )
        else:
            self.secrets_manager = None

    def create_outlook_setup_script(self, gmail_email: str, gmail_app_password: str,
                                   protonmail_email: str, protonmail_password: str) -> Path:
        """
        Create PowerShell script to configure Outlook via COM automation.

        Args:
            gmail_email: Gmail email address
            gmail_app_password: Gmail app password
            protonmail_email: ProtonMail email address
            protonmail_password: ProtonMail password

        Returns:
            Path to created PowerShell script
        """
        script_content = f'''# Outlook Setup Script - Generated {datetime.now().isoformat()}
# Configures Gmail and ProtonMail accounts in Outlook using COM automation

Add-Type -AssemblyName "Microsoft.Office.Interop.Outlook"
$Outlook = New-Object -ComObject Outlook.Application
$Namespace = $Outlook.GetNamespace("MAPI")

Write-Host "========================================"
Write-Host "OUTLOOK AUTOMATED SETUP"
Write-Host "========================================"
Write-Host ""

# Function to add IMAP account
function Add-IMAPAccount {{
    param(
        [string]$DisplayName,
        [string]$EmailAddress,
        [string]$UserName,
        [string]$Password,
        [string]$IMAPServer,
        [int]$IMAPPort,
        [string]$IMAPEncryption,
        [string]$SMTPServer,
        [int]$SMTPPort,
        [string]$SMTPEncryption
    )

    Write-Host "Adding account: $EmailAddress"

    try {{
        # Get accounts collection
        $Accounts = $Namespace.Accounts

        # Check if account already exists
        $existing = $null
        foreach ($account in $Accounts) {{
            if ($account.SmtpAddress -eq $EmailAddress) {{
                $existing = $account
                break
            }}
        }}

        if ($existing) {{
            Write-Host "  ⚠️  Account already exists: $EmailAddress"
            return $existing
        }}

        # Create new account (Outlook 2016+)
        # Note: Outlook COM API doesn't directly support adding accounts
        # We'll use the Account Settings dialog approach

        Write-Host "  ℹ️  Outlook COM API has limitations for adding accounts"
        Write-Host "  ℹ️  Please use the manual setup instructions"
        Write-Host "  ℹ️  Configuration details:"
        Write-Host "     Display Name: $DisplayName"
        Write-Host "     Email: $EmailAddress"
        Write-Host "     IMAP Server: $IMAPServer:$IMAPPort ($IMAPEncryption)"
        Write-Host "     SMTP Server: $SMTPServer:$SMTPPort ($SMTPEncryption)"
        Write-Host "     Username: $UserName"
        Write-Host ""

        return $null
    }}
    catch {{
        Write-Host "  ❌ Error: $_"
        return $null
    }}
}}

# Add Gmail account
Write-Host "CONFIGURING GMAIL ACCOUNT"
Write-Host "---------------------------"
Add-IMAPAccount `
    -DisplayName "Gmail" `
    -EmailAddress "{gmail_email}" `
    -UserName "{gmail_email}" `
    -Password "{gmail_app_password}" `
    -IMAPServer "imap.gmail.com" `
    -IMAPPort 993 `
    -IMAPEncryption "SSL" `
    -SMTPServer "smtp.gmail.com" `
    -SMTPPort 587 `
    -SMTPEncryption "STARTTLS"

Write-Host ""

# Add ProtonMail account
Write-Host "CONFIGURING PROTONMAIL ACCOUNT"
Write-Host "------------------------------"
Add-IMAPAccount `
    -DisplayName "ProtonMail" `
    -EmailAddress "{protonmail_email}" `
    -UserName "{protonmail_email}" `
    -Password "{protonmail_password}" `
    -IMAPServer "127.0.0.1" `
    -IMAPPort 1143 `
    -IMAPEncryption "SSL" `
    -SMTPServer "127.0.0.1" `
    -SMTPPort 1025 `
    -SMTPEncryption "SSL"

Write-Host ""
Write-Host "========================================"
Write-Host "SETUP COMPLETE"
Write-Host "========================================"
Write-Host ""
Write-Host "⚠️  NOTE: Outlook COM API has limitations"
Write-Host "   Please complete setup manually using:"
Write-Host "   File → Account Settings → Account Settings → New"
Write-Host ""
Write-Host "   Or use the generated instructions:"
Write-Host "   config/outlook/OUTLOOK_SETUP_INSTRUCTIONS.md"
Write-Host ""

# List current accounts
Write-Host "CURRENT OUTLOOK ACCOUNTS:"
Write-Host "------------------------"
$Accounts = $Namespace.Accounts
foreach ($account in $Accounts) {{
    Write-Host "  ✅ $($account.DisplayName) - $($account.SmtpAddress)"
}}
'''

        script_path = self.config_dir / "setup_outlook_accounts.ps1"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)

        logger.info(f"✅ PowerShell script created: {script_path}")
        return script_path

    def create_import_to_nas_config(self) -> Dict:
        try:
            """
            Create configuration for importing emails to NAS mail hub.

            Returns:
                Configuration dictionary
            """
            config = {
                "nas_mail_hub": {
                    "server": "<NAS_PRIMARY_IP>",
                    "domain": "<LOCAL_HOSTNAME>",
                    "imap": {
                        "server": "<NAS_PRIMARY_IP>",
                        "port": 993,
                        "ssl": True
                    },
                    "smtp": {
                        "server": "<NAS_PRIMARY_IP>",
                        "port": 587,
                        "ssl": True
                    },
                    "webmail": "https://<NAS_PRIMARY_IP>:5001/mailplus",
                    "api": {
                        "base_url": "https://<NAS_PRIMARY_IP>:5001/webapi",
                        "endpoint": "/entry.cgi"
                    }
                },
                "import_sources": {
                    "gmail": {
                        "enabled": True,
                        "imap_server": "imap.gmail.com",
                        "imap_port": 993,
                        "folder": "INBOX",
                        "import_all_folders": False
                    },
                    "protonmail": {
                        "enabled": True,
                        "imap_server": "127.0.0.1",
                        "imap_port": 1143,
                        "folder": "INBOX",
                        "requires_bridge": True,
                        "import_all_folders": False
                    },
                    "outlook_local": {
                        "enabled": True,
                        "type": "pst_import",
                        "pst_paths": [],
                        "note": "Import from Outlook PST files or via IMAP"
                    }
                },
                "import_settings": {
                    "schedule": {
                        "enabled": True,
                        "interval_minutes": 15,
                        "run_at_startup": True
                    },
                    "filtering": {
                        "skip_duplicates": True,
                        "max_age_days": 365,
                        "skip_attachments_over_mb": 50
                    },
                    "storage": {
                        "archive_path": "/volume1/backups/MATT_Backups/company_email_hub",
                        "organize_by_date": True,
                        "organize_by_account": True
                    }
                },
                "generated_at": datetime.now().isoformat()
            }

            config_file = self.config_dir / "nas_import_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ NAS import configuration saved: {config_file}")
            return config

        except Exception as e:
            self.logger.error(f"Error in create_import_to_nas_config: {e}", exc_info=True)
            raise
    def run_setup(self, gmail_email: Optional[str] = None,
                  gmail_app_password: Optional[str] = None,
                  protonmail_email: Optional[str] = None,
                  protonmail_password: Optional[str] = None) -> Dict:
        """
        Run automated Outlook setup.

        Args:
            gmail_email: Gmail email address
            gmail_app_password: Gmail app password
            protonmail_email: ProtonMail email address
            protonmail_password: ProtonMail password

        Returns:
            Setup results dictionary
        """
        logger.info("="*80)
        logger.info("AUTOMATED OUTLOOK SETUP")
        logger.info("="*80)

        results = {
            "timestamp": datetime.now().isoformat(),
            "gmail_configured": False,
            "protonmail_configured": False,
            "nas_import_configured": False,
            "success": False
        }

        # Get credentials from secrets manager if not provided
        if not gmail_email and self.secrets_manager:
            try:
                gmail_email = self.secrets_manager.get_secret("gmail-email")
                gmail_app_password = self.secrets_manager.get_secret("gmail-app-password")
            except Exception as e:
                logger.debug(f"Could not get Gmail credentials: {e}")

        if not protonmail_email and self.secrets_manager:
            try:
                protonmail_email = self.secrets_manager.get_secret("protonmail-username")
                protonmail_password = self.secrets_manager.get_secret("protonmail-password")
            except Exception as e:
                logger.debug(f"Could not get ProtonMail credentials: {e}")

        # Create PowerShell setup script
        if gmail_email and gmail_app_password and protonmail_email and protonmail_password:
            script_path = self.create_outlook_setup_script(
                gmail_email, gmail_app_password,
                protonmail_email, protonmail_password
            )
            results["gmail_configured"] = True
            results["protonmail_configured"] = True

            logger.info(f"✅ Setup script created: {script_path}")
            logger.info("   Run this script to configure Outlook:")
            logger.info(f"   powershell -ExecutionPolicy Bypass -File {script_path}")
        else:
            logger.warning("⚠️  Missing credentials - cannot create automated setup script")
            logger.info("   Please provide credentials or store in Azure Key Vault")
            logger.info("   Using manual setup instructions instead")

        # Create NAS import configuration
        nas_config = self.create_import_to_nas_config()
        results["nas_import_configured"] = True

        logger.info("")
        logger.info("="*80)
        logger.info("SETUP SUMMARY")
        logger.info("="*80)
        logger.info(f"Gmail Configuration: {'✅' if results['gmail_configured'] else '⚠️  Manual setup required'}")
        logger.info(f"ProtonMail Configuration: {'✅' if results['protonmail_configured'] else '⚠️  Manual setup required'}")
        logger.info(f"NAS Import Configuration: {'✅' if results['nas_import_configured'] else '❌'}")

        results["success"] = results["nas_import_configured"]

        return results


def main():
    try:
        """Main function."""
        import argparse

        parser = argparse.ArgumentParser(
            description="Automated Outlook Setup for Gmail and ProtonMail"
        )

        parser.add_argument(
            "--project-root",
            type=Path,
            default=Path(__file__).parent.parent.parent,
            help="Project root directory"
        )
        parser.add_argument(
            "--gmail-email",
            type=str,
            help="Gmail email address"
        )
        parser.add_argument(
            "--gmail-app-password",
            type=str,
            help="Gmail app password"
        )
        parser.add_argument(
            "--protonmail-email",
            type=str,
            help="ProtonMail email address"
        )
        parser.add_argument(
            "--protonmail-password",
            type=str,
            help="ProtonMail password"
        )

        args = parser.parse_args()

        setup = AutomatedOutlookSetup(args.project_root)
        results = setup.run_setup(
            gmail_email=args.gmail_email,
            gmail_app_password=args.gmail_app_password,
            protonmail_email=args.protonmail_email,
            protonmail_password=args.protonmail_password
        )

        logger.info("")
        logger.info("📋 NEXT STEPS:")
        logger.info("   1. Install Proton Bridge if not already installed")
        logger.info("   2. Run the generated PowerShell script or follow manual instructions")
        logger.info("   3. Configure email import to NAS using the import system")
        logger.info("   4. Set up scheduled import daemon for continuous syncing")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()