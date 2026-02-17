#!/usr/bin/env python3
"""
SYPHON NAS DSM Mail Server Integration

Integrates SYPHON with NAS DSM mail server email aggregation system:
- Corporate email aggregation via NAS DSM
- Secure email (ProtonMail with Proton Bridge)
- Unsecure email providers (Google, Apple, etc.)
- Complete control over email accounts and handling
"""

import sys
import json
import imaplib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from email import message_from_bytes
from email.header import decode_header
from dataclasses import dataclass, field

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
    from syphon.models import DataSourceType
except ImportError:
    from syphon_system import SYPHONSystem

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SyphonNASDSMMailIntegration")


@dataclass
class EmailAccountConfig:
    """Email account configuration"""
    account_id: str
    account_name: str
    email_address: str
    account_type: str  # "secure" (ProtonMail/Bridge) or "unsecure" (Google/Apple/etc)
    imap_server: Optional[str] = None
    imap_port: int = 993
    imap_ssl: bool = True
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_ssl: bool = True
    username: Optional[str] = None
    password: Optional[str] = None
    nas_dsm_aggregated: bool = True  # Email aggregated through NAS DSM
    enabled: bool = True


@dataclass
class NASDSMMailServerConfig:
    """NAS DSM Mail Server configuration"""
    nas_host: str = "<NAS_PRIMARY_IP>"
    nas_dsm_port: int = 5000
    mail_server_port: int = 993  # IMAP
    mail_smtp_port: int = 587  # SMTP
    aggregation_enabled: bool = True
    accounts: List[EmailAccountConfig] = field(default_factory=list)


class NASDSMMailServerIntegration:
    """Integrate SYPHON with NAS DSM mail server"""

    def __init__(
        self,
        project_root: Path,
        nas_config: Optional[NASDSMMailServerConfig] = None,
        syphon_config: Optional[SYPHONConfig] = None
    ):
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "syphon" / "nas_dsm_mail"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.data_dir / "nas_dsm_mail_config.json"
        self.logger = get_logger("NASDSMMailServerIntegration")

        # Load or create NAS DSM config
        self.nas_config = nas_config or self._load_config()

        # Initialize SYPHON
        try:
            if syphon_config is None:
                syphon_config = SYPHONConfig(
                    project_root=self.project_root,
                    subscription_tier=SubscriptionTier.ENTERPRISE,
                    enable_self_healing=True,
                    enable_banking=False
                )
            self.syphon = SYPHONSystem(syphon_config)
        except Exception as e:
            self.logger.warning(f"SYPHON initialization failed: {e}")
            self.syphon = None

        # Email extraction stats
        self.stats = {
            "total_emails_processed": 0,
            "secure_emails": 0,
            "unsecure_emails": 0,
            "actionable_items_extracted": 0,
            "tasks_extracted": 0,
            "decisions_extracted": 0,
            "last_sync": None
        }

    def _load_config(self) -> NASDSMMailServerConfig:
        """Load NAS DSM mail server configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)

                # Convert accounts list to EmailAccountConfig objects
                accounts = [
                    EmailAccountConfig(**account_data)
                    for account_data in config_data.get("accounts", [])
                ]

                return NASDSMMailServerConfig(
                    nas_host=config_data.get("nas_host", "<NAS_PRIMARY_IP>"),
                    nas_dsm_port=config_data.get("nas_dsm_port", 5000),
                    mail_server_port=config_data.get("mail_server_port", 993),
                    mail_smtp_port=config_data.get("mail_smtp_port", 587),
                    aggregation_enabled=config_data.get("aggregation_enabled", True),
                    accounts=accounts
                )
            except Exception as e:
                self.logger.warning(f"Error loading config: {e}")

        # Default config
        return NASDSMMailServerConfig()

    def _save_config(self) -> None:
        try:
            """Save NAS DSM mail server configuration"""
            config_data = {
                "nas_host": self.nas_config.nas_host,
                "nas_dsm_port": self.nas_config.nas_dsm_port,
                "mail_server_port": self.nas_config.mail_server_port,
                "mail_smtp_port": self.nas_config.mail_smtp_port,
                "aggregation_enabled": self.nas_config.aggregation_enabled,
                "accounts": [
                    {
                        "account_id": acc.account_id,
                        "account_name": acc.account_name,
                        "email_address": acc.email_address,
                        "account_type": acc.account_type,
                        "imap_server": acc.imap_server,
                        "imap_port": acc.imap_port,
                        "imap_ssl": acc.imap_ssl,
                        "smtp_server": acc.smtp_server,
                        "smtp_port": acc.smtp_port,
                        "smtp_ssl": acc.smtp_ssl,
                        "username": acc.username,
                        "password": None,  # Don't save password in plain text
                        "nas_dsm_aggregated": acc.nas_dsm_aggregated,
                        "enabled": acc.enabled
                    }
                    for acc in self.nas_config.accounts
                ]
            }

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _save_config: {e}", exc_info=True)
            raise
    def register_account(
        self,
        account_id: str,
        account_name: str,
        email_address: str,
        account_type: str,
        imap_server: Optional[str] = None,
        smtp_server: Optional[str] = None,
        nas_dsm_aggregated: bool = True
    ) -> EmailAccountConfig:
        """Register a new email account"""
        # Default to NAS DSM mail server if aggregated
        if nas_dsm_aggregated:
            imap_server = imap_server or self.nas_config.nas_host
            smtp_server = smtp_server or self.nas_config.nas_host

        account = EmailAccountConfig(
            account_id=account_id,
            account_name=account_name,
            email_address=email_address,
            account_type=account_type,
            imap_server=imap_server,
            smtp_server=smtp_server,
            nas_dsm_aggregated=nas_dsm_aggregated
        )

        self.nas_config.accounts.append(account)
        self._save_config()

        self.logger.info(f"Registered email account: {account_name} ({email_address})")

        return account

    def fetch_emails(
        self,
        account_config: EmailAccountConfig,
        folder: str = "INBOX",
        limit: int = 50,
        since_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Fetch emails from account"""
        if not account_config.enabled:
            self.logger.debug(f"Account {account_config.account_id} is disabled")
            return []

        emails = []

        try:
            # Connect to IMAP server
            if account_config.imap_ssl:
                mail = imaplib.IMAP4_SSL(account_config.imap_server, account_config.imap_port)
            else:
                mail = imaplib.IMAP4(account_config.imap_server, account_config.imap_port)

            # Login
            if account_config.username and account_config.password:
                mail.login(account_config.username, account_config.password)
            else:
                self.logger.warning(f"No credentials for account {account_config.account_id}")
                return []

            # Select folder
            mail.select(folder)

            # Search for emails
            if since_date:
                date_str = since_date.strftime("%d-%b-%Y")
                status, messages = mail.search(None, f'SINCE {date_str}')
            else:
                status, messages = mail.search(None, 'ALL')

            if status != 'OK':
                self.logger.error(f"Search failed for account {account_config.account_id}")
                mail.close()
                mail.logout()
                return []

            # Get email IDs
            email_ids = messages[0].split()
            email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids

            # Fetch emails
            for email_id in email_ids:
                try:
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    if status != 'OK':
                        continue

                    email_body = msg_data[0][1]
                    email_message = message_from_bytes(email_body)

                    # Parse email
                    email_data = self._parse_email(email_message, account_config)
                    if email_data:
                        emails.append(email_data)

                except Exception as e:
                    self.logger.debug(f"Error fetching email {email_id}: {e}")
                    continue

            mail.close()
            mail.logout()

        except Exception as e:
            self.logger.error(f"Error fetching emails from {account_config.account_id}: {e}")

        return emails

    def _parse_email(self, email_message, account_config: EmailAccountConfig) -> Optional[Dict[str, Any]]:
        """Parse email message"""
        try:
            # Decode subject
            subject = email_message["Subject"]
            if subject:
                decoded_subject = decode_header(subject)[0][0]
                if isinstance(decoded_subject, bytes):
                    subject = decoded_subject.decode('utf-8', errors='ignore')
                else:
                    subject = decoded_subject

            # Get from/to
            from_address = email_message["From"]
            to_address = email_message["To"]

            # Get body
            body = ""
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
            else:
                body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')

            # Generate email ID
            email_id = email_message["Message-ID"] or f"{account_config.account_id}_{datetime.now().timestamp()}"

            return {
                "email_id": email_id,
                "subject": subject or "",
                "body": body,
                "from_address": from_address or "",
                "to_address": to_address or "",
                "date": email_message["Date"],
                "account_id": account_config.account_id,
                "account_type": account_config.account_type,
                "nas_dsm_aggregated": account_config.nas_dsm_aggregated
            }

        except Exception as e:
            self.logger.debug(f"Error parsing email: {e}")
            return None

    def syphon_emails(
        self,
        account_id: Optional[str] = None,
        folder: str = "INBOX",
        limit: int = 50
    ) -> Dict[str, Any]:
        """Syphon emails from account(s)"""
        self.logger.info("=" * 70)
        self.logger.info("SYPHON: Extracting Email Intelligence from NAS DSM Mail Server")
        self.logger.info("=" * 70)

        results = {
            "timestamp": datetime.now().isoformat(),
            "accounts_processed": [],
            "emails_processed": 0,
            "actionable_items": 0,
            "tasks": 0,
            "decisions": 0,
            "errors": []
        }

        # Determine which accounts to process
        accounts_to_process = [
            acc for acc in self.nas_config.accounts
            if (account_id is None or acc.account_id == account_id) and acc.enabled
        ]

        for account_config in accounts_to_process:
            self.logger.info(f"Processing account: {account_config.account_name} ({account_config.email_address})")

            try:
                # Fetch emails
                emails = self.fetch_emails(account_config, folder=folder, limit=limit)

                account_results = {
                    "account_id": account_config.account_id,
                    "account_name": account_config.account_name,
                    "account_type": account_config.account_type,
                    "emails_fetched": len(emails),
                    "emails_syphoned": 0
                }

                # Syphon each email
                for email_data in emails:
                    if self.syphon:
                        try:
                            result = self.syphon.extract(
                                DataSourceType.EMAIL,
                                email_data,
                                metadata={
                                    "account_id": account_config.account_id,
                                    "account_type": account_config.account_type,
                                    "nas_dsm_aggregated": account_config.nas_dsm_aggregated
                                }
                            )

                            if result.success and result.data:
                                account_results["emails_syphoned"] += 1
                                results["actionable_items"] += len(result.data.actionable_items)
                                results["tasks"] += len(result.data.tasks)
                                results["decisions"] += len(result.data.decisions)

                                # Update stats
                                if account_config.account_type == "secure":
                                    self.stats["secure_emails"] += 1
                                else:
                                    self.stats["unsecure_emails"] += 1

                        except Exception as e:
                            self.logger.debug(f"Error syphoning email: {e}")
                            results["errors"].append(f"{account_config.account_id}: {e}")

                results["emails_processed"] += account_results["emails_syphoned"]
                results["accounts_processed"].append(account_results)

            except Exception as e:
                self.logger.error(f"Error processing account {account_config.account_id}: {e}")
                results["errors"].append(f"{account_config.account_id}: {e}")

        # Update stats
        self.stats["total_emails_processed"] += results["emails_processed"]
        self.stats["actionable_items_extracted"] += results["actionable_items"]
        self.stats["tasks_extracted"] += results["tasks"]
        self.stats["decisions_extracted"] += results["decisions"]
        self.stats["last_sync"] = datetime.now().isoformat()

        # Save stats
        stats_file = self.data_dir / "stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)

        # Save results
        results_file = self.data_dir / f"syphon_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("SYPHON RESULTS")
        self.logger.info("=" * 70)
        self.logger.info(f"Accounts processed: {len(results['accounts_processed'])}")
        self.logger.info(f"Emails processed: {results['emails_processed']}")
        self.logger.info(f"Actionable items: {results['actionable_items']}")
        self.logger.info(f"Tasks: {results['tasks']}")
        self.logger.info(f"Decisions: {results['decisions']}")
        self.logger.info("=" * 70)

        return results

    def get_infrastructure_summary(self) -> Dict[str, Any]:
        """Get email infrastructure summary"""
        return {
            "nas_dsm_mail_server": {
                "host": self.nas_config.nas_host,
                "aggregation_enabled": self.nas_config.aggregation_enabled,
                "imap_port": self.nas_config.mail_server_port,
                "smtp_port": self.nas_config.mail_smtp_port
            },
            "accounts": {
                "total": len(self.nas_config.accounts),
                "secure": len([acc for acc in self.nas_config.accounts if acc.account_type == "secure"]),
                "unsecure": len([acc for acc in self.nas_config.accounts if acc.account_type == "unsecure"]),
                "enabled": len([acc for acc in self.nas_config.accounts if acc.enabled]),
                "nas_dsm_aggregated": len([acc for acc in self.nas_config.accounts if acc.nas_dsm_aggregated])
            },
            "stats": self.stats
        }


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="SYPHON NAS DSM Mail Server Integration")
        parser.add_argument(
            "--project-root",
            type=str,
            default=str(project_root),
            help="Project root directory"
        )
        parser.add_argument(
            "--register-account",
            nargs=5,
            metavar=("ACCOUNT_ID", "ACCOUNT_NAME", "EMAIL", "ACCOUNT_TYPE", "IMAP_SERVER"),
            help="Register a new email account"
        )
        parser.add_argument(
            "--syphon",
            action="store_true",
            help="Syphon emails from all accounts"
        )
        parser.add_argument(
            "--account-id",
            type=str,
            help="Syphon emails from specific account"
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=50,
            help="Limit number of emails to fetch"
        )
        parser.add_argument(
            "--summary",
            action="store_true",
            help="Show infrastructure summary"
        )

        args = parser.parse_args()

        integration = NASDSMMailServerIntegration(Path(args.project_root))

        if args.register_account:
            account_id, account_name, email_address, account_type, imap_server = args.register_account
            integration.register_account(
                account_id=account_id,
                account_name=account_name,
                email_address=email_address,
                account_type=account_type,
                imap_server=imap_server if imap_server != "None" else None
            )
            logger.info(f"Registered account: {account_name}")

        if args.syphon:
            results = integration.syphon_emails(account_id=args.account_id, limit=args.limit)
            logger.info(f"Syphoned {results['emails_processed']} emails")

        if args.summary:
            summary = integration.get_infrastructure_summary()
            print(json.dumps(summary, indent=2, ensure_ascii=False))

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    sys.exit(main())