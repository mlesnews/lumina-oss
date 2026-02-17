#!/usr/bin/env python3
"""
Complete Email Configuration
Finalizes remaining email setup items.

Tags: #EMAIL #CONFIGURATION #MAILSTATION #GMAIL #OUTLOOK
@JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CompleteEmailConfig")


class EmailConfigurationCompleter:
    """Complete remaining email configuration items"""

    def __init__(self):
        """Initialize completer"""
        self.base_path = Path(__file__).parent.parent.parent
        self.results = {
            "gmail_config": {},
            "outlook_mobile": {},
            "imap_port_993": {},
            "summary": {}
        }

    def create_gmail_mailstation_guide(self) -> Dict[str, Any]:
        """Create guide for Gmail in MailStation External Mail"""
        logger.info("=" * 80)
        logger.info("📧 GMAIL + MAILSTATION EXTERNAL MAIL CONFIGURATION")
        logger.info("=" * 80)

        guide = {
            "method": "mailstation_external_mail",
            "status": "manual_configuration_required",
            "steps": [
                {
                    "step": 1,
                    "action": "Access MailStation on NAS",
                    "details": "Navigate to DSM → MailStation → External Mail"
                },
                {
                    "step": 2,
                    "action": "Add Gmail Account",
                    "details": "Click 'Add External Mail Account' → Select 'Gmail'"
                },
                {
                    "step": 3,
                    "action": "OAuth2 Authentication",
                    "details": "Click 'Authenticate with Google' → Complete OAuth2 flow"
                },
                {
                    "step": 4,
                    "action": "Configure Sync Settings",
                    "details": "Set sync frequency, folders to sync, and retention policy"
                },
                {
                    "step": 5,
                    "action": "Verify Connection",
                    "details": "Test connection and verify emails are syncing"
                }
            ],
            "alternative_method": {
                "description": "If MailStation doesn't support External Mail OAuth2",
                "method": "n8n_gmail_workflow",
                "steps": [
                    "Use N8N Gmail OAuth2 node",
                    "Create workflow to fetch Gmail emails",
                    "Forward to MailStation via SMTP",
                    "Store credentials in Azure Vault"
                ]
            },
            "credentials_storage": {
                "location": "Azure Vault",
                "secrets": [
                    "gmail-oauth2-access-token",
                    "gmail-oauth2-refresh-token",
                    "gmail-oauth2-client-id",
                    "gmail-oauth2-client-secret"
                ]
            }
        }

        logger.info("✅ Gmail configuration guide created")
        logger.info("")
        return guide

    def create_outlook_mobile_config(self) -> Dict[str, Any]:
        """Create Outlook Mobile configuration"""
        logger.info("=" * 80)
        logger.info("📱 OUTLOOK MOBILE CONFIGURATION")
        logger.info("=" * 80)

        config = {
            "account_name": "MailStation Hub",
            "email_address": "mlesn@<LOCAL_HOSTNAME>",
            "server_settings": {
                "imap": {
                    "server": "<NAS_PRIMARY_IP>",
                    "port": 993,
                    "security": "SSL/TLS",
                    "username": "mlesn@<LOCAL_HOSTNAME>",
                    "password": "stored_in_secure_location"
                },
                "smtp": {
                    "server": "<NAS_PRIMARY_IP>",
                    "port": 25,
                    "security": "STARTTLS",
                    "username": "mlesn@<LOCAL_HOSTNAME>",
                    "password": "stored_in_secure_location"
                }
            },
            "sync_settings": {
                "sync_frequency": "Push",
                "days_to_sync": 30,
                "sync_folders": ["Inbox", "Sent", "Drafts", "Archive"]
            },
            "setup_instructions": {
                "ios": [
                    "1. Open Settings → Mail → Accounts → Add Account",
                    "2. Select 'Other' → 'Add Mail Account'",
                    "3. Enter name, email, password",
                    "4. Select 'IMAP'",
                    "5. Enter IMAP settings (<NAS_PRIMARY_IP>:993 SSL)",
                    "6. Enter SMTP settings (<NAS_PRIMARY_IP>:25 STARTTLS)",
                    "7. Save and verify connection"
                ],
                "android": [
                    "1. Open Outlook app → Settings → Add Account",
                    "2. Select 'Advanced setup' → 'IMAP'",
                    "3. Enter email: mlesn@<LOCAL_HOSTNAME>",
                    "4. Enter password",
                    "5. IMAP server: <NAS_PRIMARY_IP>, Port: 993, SSL",
                    "6. SMTP server: <NAS_PRIMARY_IP>, Port: 25, STARTTLS",
                    "7. Save and test connection"
                ]
            },
            "note": "IMAP port 993 must be enabled on MailStation for this to work"
        }

        logger.info("✅ Outlook Mobile configuration created")
        logger.info("")
        return config

    def create_imap_port_993_guide(self) -> Dict[str, Any]:
        """Create guide for enabling IMAP port 993"""
        logger.info("=" * 80)
        logger.info("🔌 MAILSTATION IMAP PORT 993 CONFIGURATION")
        logger.info("=" * 80)

        guide = {
            "current_status": "port_993_closed",
            "required_action": "enable_imap_service",
            "steps": [
                {
                    "step": 1,
                    "action": "Access MailStation Settings",
                    "details": "DSM → MailStation → Settings → Mail Service"
                },
                {
                    "step": 2,
                    "action": "Enable IMAP Service",
                    "details": "Check 'Enable IMAP service' checkbox"
                },
                {
                    "step": 3,
                    "action": "Configure IMAP Port",
                    "details": "Set IMAP port to 993 (SSL/TLS)"
                },
                {
                    "step": 4,
                    "action": "Configure SSL/TLS",
                    "details": "Enable SSL/TLS encryption for IMAP"
                },
                {
                    "step": 5,
                    "action": "Firewall Configuration",
                    "details": "Ensure port 993 is open in DSM Firewall"
                },
                {
                    "step": 6,
                    "action": "Verify Port",
                    "details": "Run: python scripts/python/verify_complete_email_setup.py"
                }
            ],
            "verification": {
                "script": "scripts/python/verify_complete_email_setup.py",
                "expected_result": "IMAP port 993: ✅ Open"
            },
            "troubleshooting": {
                "port_still_closed": [
                    "Check MailStation service is running",
                    "Verify firewall rules allow port 993",
                    "Check for port conflicts",
                    "Review MailStation logs"
                ]
            }
        }

        logger.info("✅ IMAP port 993 configuration guide created")
        logger.info("")
        return guide

    def save_configurations(self):
        try:
            """Save all configurations to files"""
            logger.info("=" * 80)
            logger.info("💾 SAVING CONFIGURATIONS")
            logger.info("=" * 80)

            # Save Gmail guide
            gmail_path = self.base_path / "docs" / "email" / "GMAIL_MAILSTATION_SETUP.md"
            gmail_path.parent.mkdir(parents=True, exist_ok=True)
            with open(gmail_path, 'w', encoding='utf-8') as f:
                f.write(f"# Gmail + MailStation External Mail Setup\n\n")
                f.write(f"**Date**: {Path(__file__).stat().st_mtime}\n\n")
                f.write(f"```json\n{json.dumps(self.results['gmail_config'], indent=2)}\n```\n")
            logger.info(f"✅ Saved: {gmail_path}")

            # Save Outlook Mobile config
            outlook_path = self.base_path / "config" / "outlook" / "outlook_mobile_config.json"
            outlook_path.parent.mkdir(parents=True, exist_ok=True)
            with open(outlook_path, 'w', encoding='utf-8') as f:
                json.dump(self.results['outlook_mobile'], f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Saved: {outlook_path}")

            # Save IMAP port guide
            imap_path = self.base_path / "docs" / "email" / "IMAP_PORT_993_SETUP.md"
            imap_path.parent.mkdir(parents=True, exist_ok=True)
            with open(imap_path, 'w', encoding='utf-8') as f:
                f.write(f"# MailStation IMAP Port 993 Configuration\n\n")
                f.write(f"**Date**: {Path(__file__).stat().st_mtime}\n\n")
                f.write(f"```json\n{json.dumps(self.results['imap_port_993'], indent=2)}\n```\n")
            logger.info(f"✅ Saved: {imap_path}")

            logger.info("")

        except Exception as e:
            self.logger.error(f"Error in save_configurations: {e}", exc_info=True)
            raise
    def complete_all(self) -> Dict[str, Any]:
        """Complete all remaining email configuration"""
        logger.info("")
        logger.info("=" * 80)
        logger.info("📧 COMPLETING EMAIL CONFIGURATION")
        logger.info("=" * 80)
        logger.info("")

        # Create Gmail guide
        self.results['gmail_config'] = self.create_gmail_mailstation_guide()

        # Create Outlook Mobile config
        self.results['outlook_mobile'] = self.create_outlook_mobile_config()

        # Create IMAP port 993 guide
        self.results['imap_port_993'] = self.create_imap_port_993_guide()

        # Save configurations
        self.save_configurations()

        # Generate summary
        self.results['summary'] = {
            "status": "configuration_guides_created",
            "items_completed": [
                "Gmail + MailStation External Mail guide",
                "Outlook Mobile configuration",
                "IMAP port 993 setup guide"
            ],
            "next_steps": [
                "Enable IMAP port 993 on MailStation",
                "Configure Gmail in MailStation External Mail (or use N8N)",
                "Set up Outlook Mobile using provided configuration"
            ]
        }

        logger.info("=" * 80)
        logger.info("📊 SUMMARY")
        logger.info("=" * 80)
        logger.info("✅ Gmail configuration guide created")
        logger.info("✅ Outlook Mobile configuration created")
        logger.info("✅ IMAP port 993 setup guide created")
        logger.info("")
        logger.info("Next steps:")
        for step in self.results['summary']['next_steps']:
            logger.info(f"  • {step}")
        logger.info("=" * 80)

        return self.results


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Complete Email Configuration")
        parser.add_argument("--json", action="store_true", help="Output as JSON")
        parser.add_argument("--save", type=str, help="Save results to file")

        args = parser.parse_args()

        completer = EmailConfigurationCompleter()
        results = completer.complete_all()

        if args.save:
            output_path = Path(args.save)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Results saved to: {output_path}")

        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    exit(main())