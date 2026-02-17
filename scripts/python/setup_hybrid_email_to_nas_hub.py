"""
Setup Hybrid Email System: Gmail + ProtonMail → NAS Mail Hub → Outlook Classic
Complete setup for importing Gmail and ProtonMail to NAS Mail Hub, then connecting Outlook Classic.

Architecture:
- Gmail → Import to NAS Mail Hub
- ProtonMail (via Bridge) → Import to NAS Mail Hub  
- Outlook Classic → Connect to NAS Mail Hub (receives all emails)

#JARVIS #LUMINA #NAS #MAILPLUS #GMAIL #PROTONMAIL #OUTLOOK #HYBRID
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("SetupHybridEmailToNASHub")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("SetupHybridEmailToNASHub")

try:
    from scripts.python.unified_secrets_manager import UnifiedSecretsManager, SecretSource
    from scripts.python.unified_email_service import UnifiedEmailService, EmailProvider
    from scripts.python.nas_azure_vault_integration import NASAzureVaultIntegration
    INTEGRATIONS_AVAILABLE = True
except ImportError:
    INTEGRATIONS_AVAILABLE = False
    logger.warning("⚠️  Some integrations not available")


class HybridEmailToNASHubSetup:
    """
    Setup hybrid email system: Gmail + ProtonMail → NAS Mail Hub → Outlook Classic
    """

    def __init__(self, project_root: Path):
        """
        Initialize hybrid email setup.

        Args:
            project_root: Project root directory
        """
        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config" / "outlook"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        if INTEGRATIONS_AVAILABLE:
            self.secrets_manager = UnifiedSecretsManager(
                project_root,
                prefer_source=SecretSource.AZURE_KEY_VAULT
            )
            self.email_service = UnifiedEmailService(project_root)
            try:
                self.nas_integration = NASAzureVaultIntegration()
            except Exception as e:
                logger.warning(f"⚠️  NAS integration not available: {e}")
                self.nas_integration = None
        else:
            self.secrets_manager = None
            self.email_service = None
            self.nas_integration = None

    def create_hybrid_email_config(self,
                                       protonmail_email: str = "mlesnews@protonmail.com",
                                       protonmail_bridge_password: str = "9n5m3Hn_8PhRcG8KeXKo0w") -> Dict[str, Any]:
        try:
            """
            Create complete hybrid email configuration.

            Args:
                protonmail_email: ProtonMail email address
                protonmail_bridge_password: ProtonMail Bridge password

            Returns:
                Configuration dictionary
            """
            config = {
                "architecture": {
                    "description": "Hybrid Email System: Gmail + ProtonMail → NAS Mail Hub → Outlook Classic",
                    "flow": [
                        "1. Gmail emails imported to NAS Mail Hub",
                        "2. ProtonMail emails (via Bridge) imported to NAS Mail Hub",
                        "3. Outlook Classic connects to NAS Mail Hub to receive all emails"
                    ]
                },
                "nas_mail_hub": {
                    "server": "<NAS_PRIMARY_IP>",
                    "domain": "<LOCAL_HOSTNAME>",
                    "imap": {
                        "server": "<NAS_PRIMARY_IP>",
                        "port": 993,
                        "encryption": "SSL/TLS",
                        "ssl": True
                    },
                    "smtp": {
                        "server": "<NAS_PRIMARY_IP>",
                        "port": 587,
                        "encryption": "STARTTLS",
                        "ssl": True
                    },
                    "webmail": "https://<NAS_PRIMARY_IP>:5001/mailplus",
                    "accounts": {
                        "mlesn": {
                            "email": "mlesn@<LOCAL_HOSTNAME>",
                            "username": "mlesn",
                            "description": "Primary company email account"
                        }
                    }
                },
                "protonmail_bridge": {
                    "email": protonmail_email,
                    "bridge_password": protonmail_bridge_password,
                    "imap": {
                        "server": "127.0.0.1",
                        "port": 1143,
                        "encryption": "STARTTLS",
                        "username": protonmail_email,
                        "password": protonmail_bridge_password
                    },
                    "smtp": {
                        "server": "127.0.0.1",
                        "port": 1025,
                        "encryption": "STARTTLS",
                        "username": protonmail_email,
                        "password": protonmail_bridge_password
                    },
                    "note": "Proton Bridge must be running on host PC"
                },
                "gmail": {
                    "imap": {
                        "server": "imap.gmail.com",
                        "port": 993,
                        "encryption": "SSL",
                        "requires_app_password": True
                    },
                    "smtp": {
                        "server": "smtp.gmail.com",
                        "port": 587,
                        "encryption": "STARTTLS",
                        "requires_app_password": True
                    },
                    "note": "Requires Gmail App Password (not regular password)"
                },
                "outlook_classic": {
                    "connection": {
                        "type": "IMAP",
                        "server": "<NAS_PRIMARY_IP>",
                        "port": 993,
                        "encryption": "SSL/TLS",
                        "username": "mlesn@<LOCAL_HOSTNAME>",
                        "description": "Connect Outlook Classic to NAS Mail Hub to receive all emails"
                    },
                    "note": "Outlook Classic connects to NAS Mail Hub, not directly to Gmail/ProtonMail"
                },
                "import_settings": {
                    "enabled": True,
                    "schedule": {
                        "interval_minutes": 15,
                        "run_at_startup": True
                    },
                    "sources": {
                        "gmail": {
                            "enabled": True,
                            "import_to_nas": True,
                            "days_back": 365
                        },
                        "protonmail": {
                            "enabled": True,
                            "import_to_nas": True,
                            "requires_bridge": True,
                            "days_back": 365
                        }
                    },
                    "storage": {
                        "nas_path": "/volume1/backups/MATT_Backups/company_email_hub",
                        "organize_by_date": True,
                        "organize_by_source": True
                    }
                },
                "generated_at": datetime.now().isoformat()
            }

            config_file = self.config_dir / "hybrid_email_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Hybrid email configuration saved: {config_file}")
            return config

        except Exception as e:
            self.logger.error(f"Error in create_hybrid_email_config: {e}", exc_info=True)
            raise
    def create_outlook_nas_hub_instructions(self) -> Path:
        """
        Create instructions for connecting Outlook Classic to NAS Mail Hub.

        Returns:
            Path to instructions file
        """
        instructions = """# Outlook Classic Setup: Connect to NAS Mail Hub

## Overview

This setup connects Outlook Classic to your **NAS Mail Hub** (not directly to Gmail/ProtonMail).
All emails from Gmail and ProtonMail are imported to the NAS Mail Hub, and Outlook Classic
receives all emails from the hub.

## Architecture

```
Gmail ──┐
        ├──→ NAS Mail Hub ──→ Outlook Classic
ProtonMail ──┘
```

## Prerequisites

1. **Microsoft Outlook** (Classic/Desktop version) installed
2. **NAS Mail Hub** configured and running (<NAS_PRIMARY_IP>)
3. **Gmail and ProtonMail** emails being imported to NAS Mail Hub
4. **Company email account** on NAS Mail Hub (mlesn@<LOCAL_HOSTNAME>)

---

## Step 1: Verify NAS Mail Hub Access

1. Open web browser
2. Navigate to: https://<NAS_PRIMARY_IP>:5001/mailplus
3. Log in with your company email account
4. Verify you can see emails from Gmail and ProtonMail

---

## Step 2: Add NAS Mail Hub Account to Outlook

1. Open Outlook
2. Go to **File** → **Account Settings** → **Account Settings**
3. Click **New...**
4. Select **Manual setup or additional server types**
5. Click **Next**
6. Select **POP or IMAP**
7. Click **Next**
8. Fill in the account information:
   - **Your Name**: Your display name
   - **Email Address**: mlesn@<LOCAL_HOSTNAME>
   - **Account Type**: IMAP
   - **Incoming mail server**: <NAS_PRIMARY_IP>
   - **Outgoing mail server (SMTP)**: <NAS_PRIMARY_IP>
   - **User Name**: mlesn@<LOCAL_HOSTNAME>
   - **Password**: [Your NAS Mail Hub password]
9. Click **More Settings...**
10. Go to **Outgoing Server** tab:
    - Check "My outgoing server (SMTP) requires authentication"
    - Select "Use same settings as my incoming mail server"
11. Go to **Advanced** tab:
    - **Incoming server (IMAP)**: 993
    - **Use the following type of encrypted connection**: SSL/TLS
    - **Outgoing server (SMTP)**: 587
    - **Use the following type of encrypted connection**: STARTTLS
12. Click **OK**
13. Click **Next**
14. Outlook will test the connection
15. Click **Finish** when successful

---

## Step 3: Verify Email Reception

1. In Outlook, check your inbox
2. You should see emails from:
   - Gmail (imported to NAS Mail Hub)
   - ProtonMail (imported to NAS Mail Hub)
   - Company email (direct to NAS Mail Hub)
3. All emails are now in one unified inbox

---

## Step 4: Configure Email Folders (Optional)

1. In Outlook, organize emails by creating folders:
   - Gmail
   - ProtonMail
   - Company
2. Set up rules to automatically organize emails by source

---

## Troubleshooting

### Cannot Connect to NAS Mail Hub
- **Issue**: "Cannot connect to server"
  - **Solution**: Verify NAS Mail Hub is running (check webmail interface)
  - **Solution**: Check network connectivity to <NAS_PRIMARY_IP>
  - **Solution**: Verify firewall allows connections on ports 993 (IMAP) and 587 (SMTP)

### Authentication Fails
- **Issue**: "Username and password not accepted"
  - **Solution**: Verify username is: mlesn@<LOCAL_HOSTNAME>
  - **Solution**: Verify password is correct for NAS Mail Hub account
  - **Solution**: Check if account exists in NAS Mail Hub

### No Emails from Gmail/ProtonMail
- **Issue**: Only seeing company emails, not Gmail/ProtonMail
  - **Solution**: Verify email import system is running
  - **Solution**: Check import logs: data/email_import/
  - **Solution**: Verify Gmail and ProtonMail are configured in import system

---

## Configuration Summary

### NAS Mail Hub Settings
- **IMAP Server**: <NAS_PRIMARY_IP>:993 (SSL/TLS)
- **SMTP Server**: <NAS_PRIMARY_IP>:587 (STARTTLS)
- **Username**: mlesn@<LOCAL_HOSTNAME>
- **Webmail**: https://<NAS_PRIMARY_IP>:5001/mailplus

### Email Sources (Imported to NAS Mail Hub)
- **Gmail**: Imported via IMAP every 15 minutes
- **ProtonMail**: Imported via Proton Bridge every 15 minutes

---

## Next Steps

1. Set up email import daemon to continuously sync Gmail/ProtonMail to NAS Mail Hub
2. Configure email rules in Outlook for organization
3. Set up email archiving and backup
4. Monitor import logs for any issues

For email import setup, see: `scripts/python/import_emails_to_nas_hub.py`
"""

        instructions_file = self.config_dir / "OUTLOOK_NAS_HUB_SETUP.md"
        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write(instructions)

        logger.info(f"✅ Outlook NAS Hub instructions saved: {instructions_file}")
        return instructions_file

    def update_import_system_for_nas_hub(self) -> Dict[str, Any]:
        try:
            """
            Update email import system to import directly to NAS Mail Hub.

            Returns:
                Updated import configuration
            """
            import_config = {
                "import_to_nas_hub": True,
                "nas_mail_hub": {
                    "server": "<NAS_PRIMARY_IP>",
                    "imap": {
                        "server": "<NAS_PRIMARY_IP>",
                        "port": 993,
                        "ssl": True
                    },
                    "account": {
                        "email": "mlesn@<LOCAL_HOSTNAME>",
                        "username": "mlesn"
                    }
                },
                "sources": {
                    "gmail": {
                        "enabled": True,
                        "import_to_nas": True,
                        "method": "imap_forward",
                        "imap_server": "imap.gmail.com",
                        "imap_port": 993
                    },
                    "protonmail": {
                        "enabled": True,
                        "import_to_nas": True,
                        "method": "bridge_forward",
                        "bridge_imap": "127.0.0.1:1143",
                        "bridge_smtp": "127.0.0.1:1025"
                    }
                },
                "forwarding": {
                    "enabled": True,
                    "forward_to": "mlesn@<LOCAL_HOSTNAME>",
                    "preserve_original": True,
                    "add_source_tag": True
                }
            }

            config_file = self.config_dir / "nas_hub_import_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(import_config, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ NAS Hub import configuration saved: {config_file}")
            return import_config

        except Exception as e:
            self.logger.error(f"Error in update_import_system_for_nas_hub: {e}", exc_info=True)
            raise
    def run_complete_setup(self) -> Dict[str, Any]:
        """
        Run complete hybrid email setup.

        Returns:
            Setup results
        """
        logger.info("="*80)
        logger.info("HYBRID EMAIL SYSTEM SETUP")
        logger.info("Gmail + ProtonMail → NAS Mail Hub → Outlook Classic")
        logger.info("="*80)
        logger.info("")

        results = {
            "timestamp": datetime.now().isoformat(),
            "config_created": False,
            "instructions_created": False,
            "import_config_created": False,
            "success": False
        }

        # Step 1: Create hybrid email configuration
        logger.info("STEP 1: Creating Hybrid Email Configuration")
        logger.info("-" * 80)
        try:
            config = self.create_hybrid_email_config()
            results["config_created"] = True
            logger.info("✅ Configuration created with Proton Bridge settings")
        except Exception as e:
            logger.error(f"❌ Failed to create configuration: {e}")

        logger.info("")

        # Step 2: Create Outlook NAS Hub instructions
        logger.info("STEP 2: Creating Outlook NAS Hub Setup Instructions")
        logger.info("-" * 80)
        try:
            instructions_file = self.create_outlook_nas_hub_instructions()
            results["instructions_created"] = True
            logger.info(f"✅ Instructions created: {instructions_file.name}")
        except Exception as e:
            logger.error(f"❌ Failed to create instructions: {e}")

        logger.info("")

        # Step 3: Update import system configuration
        logger.info("STEP 3: Updating Email Import System for NAS Hub")
        logger.info("-" * 80)
        try:
            import_config = self.update_import_system_for_nas_hub()
            results["import_config_created"] = True
            logger.info("✅ Import system configured for NAS Hub")
        except Exception as e:
            logger.error(f"❌ Failed to update import config: {e}")

        logger.info("")

        # Summary
        results["success"] = all([
            results["config_created"],
            results["instructions_created"],
            results["import_config_created"]
        ])

        logger.info("="*80)
        if results["success"]:
            logger.info("✅ HYBRID EMAIL SYSTEM SETUP COMPLETE")
        else:
            logger.info("⚠️  SETUP PARTIALLY COMPLETE")
        logger.info("="*80)
        logger.info("")

        self._print_next_steps()

        return results

    def _print_next_steps(self):
        """Print next steps for user."""
        logger.info("📋 NEXT STEPS:")
        logger.info("")
        logger.info("1. SET UP EMAIL IMPORT TO NAS HUB:")
        logger.info("   - Run: python scripts/python/import_emails_to_nas_hub.py --days-back 365")
        logger.info("   - Set up scheduled import daemon")
        logger.info("")
        logger.info("2. CONFIGURE OUTLOOK CLASSIC:")
        logger.info("   - Follow instructions: config/outlook/OUTLOOK_NAS_HUB_SETUP.md")
        logger.info("   - Connect to NAS Mail Hub: <NAS_PRIMARY_IP>:993 (IMAP)")
        logger.info("")
        logger.info("3. VERIFY SETUP:")
        logger.info("   - Check NAS Mail Hub webmail for imported emails")
        logger.info("   - Verify Outlook Classic receives all emails")
        logger.info("   - Monitor import logs")
        logger.info("")


def main():
    try:
        """Main function."""
        import argparse

        parser = argparse.ArgumentParser(
            description="Setup Hybrid Email System: Gmail + ProtonMail → NAS Mail Hub → Outlook Classic"
        )

        parser.add_argument(
            "--project-root",
            type=Path,
            default=Path(__file__).parent.parent.parent,
            help="Project root directory"
        )
        parser.add_argument(
            "--protonmail-email",
            type=str,
            default="mlesnews@protonmail.com",
            help="ProtonMail email address"
        )
        parser.add_argument(
            "--protonmail-bridge-password",
            type=str,
            default="9n5m3Hn_8PhRcG8KeXKo0w",
            help="ProtonMail Bridge password"
        )

        args = parser.parse_args()

        setup = HybridEmailToNASHubSetup(args.project_root)
        results = setup.run_complete_setup()

        logger.info("")
        logger.info("✅ Setup complete! Review the generated configuration files and instructions.")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()