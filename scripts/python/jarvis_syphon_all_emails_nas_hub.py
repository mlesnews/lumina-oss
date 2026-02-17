#!/usr/bin/env python3
"""
JARVIS: Syphon All Emails via NAS Company Mail Hub

Syphons all email accounts through NAS company mail hub:
- All email accounts (Gmail, Outlook, ProtonMail, etc.)
- Via NAS MailPlus/DSM Mail Server
- Extracts learnings and intelligence
- Stores in Holocron and R5

Tags: #JARVIS #EMAIL #SYPHON #NAS #MAIL_HUB #HOLOCRON @JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISEmailSyphon")


@dataclass
class EmailSyphonResult:
    """Result from syphoning an email account"""
    account_id: str
    account_name: str
    emails_found: int = 0
    emails_processed: int = 0
    emails_new: int = 0
    learnings_extracted: int = 0
    errors: List[str] = field(default_factory=list)
    learnings: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class JARVISEmailSyphonNASHub:
    """
    JARVIS: Syphon All Emails via NAS Company Mail Hub

    Connects to NAS MailPlus/DSM Mail Server and syphons all email accounts.
    """

    def __init__(self):
        """Initialize email syphon system"""
        logger.info("=" * 80)
        logger.info("📧 JARVIS: Email Syphon via NAS Company Mail Hub")
        logger.info("=" * 80)
        logger.info("")
        logger.info("   ℹ️  NAS Mail Hub aggregates ALL emails from ALL providers:")
        logger.info("      • Gmail, Apple Mail, ProtonMail, Outlook, Xfinity, Yahoo, etc.")
        logger.info("   ℹ️  All emails available in company email accounts:")
        logger.info("      • mlesn@<LOCAL_HOSTNAME>")
        logger.info("      • glesn@<LOCAL_HOSTNAME>")
        logger.info("   ℹ️  Employees access via Outlook (seamless company email)")
        logger.info("")

        self.project_root = project_root
        self.data_dir = project_root / "data" / "email_syphon"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # NAS configuration - Unified Company Mail Hub
        self.nas_ip = "<NAS_PRIMARY_IP>"  # NAS IP
        self.nas_mail_hub_port = 993  # IMAP port (or 143 for non-SSL)
        self.nas_mail_hub_web = f"http://{self.nas_ip}:5001"  # MailStation/MailPlus web interface
        self.company_domain = "<LOCAL_HOSTNAME>"
        self.mail_system = "MailStation"  # MailStation is running (or MailPlus if available)

        # Account configurations - Company email accounts on NAS Hub
        # These accounts receive ALL aggregated emails from all providers:
        # - Gmail, Apple Mail, ProtonMail, Outlook, Xfinity, Yahoo, etc.
        self.email_accounts: List[Dict[str, Any]] = []

        # Results
        self.syphon_results: List[EmailSyphonResult] = []

        logger.info("✅ JARVIS Email Syphon initialized")
        logger.info(f"   NAS Mail Hub: {self.nas_mail_hub_web}")

    def load_email_accounts(self) -> List[Dict[str, Any]]:
        """Load email account configurations"""
        # Try to load from config
        config_file = self.project_root / "config" / "email_accounts.json"

        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                    # Handle different config formats
                    if isinstance(config_data, dict):
                        # Check for nested structure
                        if 'email_accounts' in config_data and 'accounts' in config_data['email_accounts']:
                            self.email_accounts = config_data['email_accounts']['accounts']
                        elif 'accounts' in config_data:
                            self.email_accounts = config_data['accounts']
                        else:
                            # Assume it's a list directly
                            self.email_accounts = config_data if isinstance(config_data, list) else []
                    elif isinstance(config_data, list):
                        self.email_accounts = config_data
                    else:
                        self.email_accounts = []

                logger.info(f"   ✅ Loaded {len(self.email_accounts)} email accounts from config")
                return self.email_accounts
            except Exception as e:
                logger.warning(f"   ⚠️  Error loading config: {e}")

        # Try Azure Key Vault
        try:
            from scripts.python.setup_email_credentials_azure_vault import get_email_accounts_from_vault
            self.email_accounts = get_email_accounts_from_vault()
            logger.info(f"   ✅ Loaded {len(self.email_accounts)} email accounts from Azure Vault")
            return self.email_accounts
        except Exception as e:
            logger.debug(f"   Azure Vault not available: {e}")

        # Default: Use NAS Company Mail Hub (unified hub with all aggregated emails)
        logger.info("   ℹ️  Using NAS Company Mail Hub as unified email source")
        logger.info("   ℹ️  Hub aggregates: Gmail, Apple Mail, ProtonMail, Outlook, Xfinity, Yahoo, etc.")

        # Company email accounts on NAS Hub
        # These accounts contain ALL emails from all providers
        return [
            {
                'account_id': 'mlesn_company',
                'account_name': 'mlesn@<LOCAL_HOSTNAME> (Company Email)',
                'email': 'mlesn@<LOCAL_HOSTNAME>',
                'type': 'nas_mailplus',
                'server': self.nas_ip,
                'port': self.nas_mail_hub_port,
                'domain': self.company_domain,
                'description': 'Primary company email - all aggregated emails from all providers',
                'enabled': True
            },
            {
                'account_id': 'glesn_company',
                'account_name': 'glesn@<LOCAL_HOSTNAME> (Company Email)',
                'email': 'glesn@<LOCAL_HOSTNAME>',
                'type': 'nas_mailplus',
                'server': self.nas_ip,
                'port': self.nas_mail_hub_port,
                'domain': self.company_domain,
                'description': 'Company email - all aggregated emails from all providers',
                'enabled': True
            }
        ]

    def syphon_all_accounts(self, days: int = 30) -> Dict[str, Any]:
        """
        Syphon all email accounts via NAS Mail Hub.

        Args:
            days: Number of days to syphon (default: 30)

        Returns:
            Complete syphon results
        """
        logger.info(f"\n📧 Starting Email Syphon (last {days} days)...")

        start_time = time.time()
        accounts = self.load_email_accounts()

        total_emails = 0
        total_learnings = 0

        for account in accounts:
            # Handle both dict and string account formats
            if isinstance(account, str):
                # Convert string to dict format
                account = {
                    'account_id': account,
                    'account_name': account,
                    'enabled': True
                }

            if not account.get('enabled', True):
                continue

            account_start = time.time()
            logger.info(f"\n  📬 Syphoning: {account.get('account_name', account.get('account_id', 'Unknown'))}")

            result = EmailSyphonResult(
                account_id=account.get('account_id', 'unknown'),
                account_name=account.get('account_name', 'Unknown Account')
            )

            try:
                # Syphon via NAS Mail Hub
                emails, learnings = self._syphon_account_via_nas(account, days)

                result.emails_found = len(emails)
                result.emails_processed = len(emails)
                result.emails_new = len(emails)  # Assume new for now
                result.learnings_extracted = len(learnings)
                total_emails += len(emails)
                total_learnings += len(learnings)

                # Handle empty accounts gracefully
                if len(emails) == 0:
                    logger.info(f"     ℹ️  No emails found (account may be empty or new)")
                    result.learnings.append("Account is empty or has no emails in date range")
                else:
                    # Save emails
                    self._save_emails(account['account_id'], emails)

                    # Save learnings
                    if learnings:
                        self._save_learnings(account['account_id'], learnings)

                    logger.info(f"     ✅ Found {len(emails)} emails, {len(learnings)} learnings")

            except Exception as e:
                error_msg = f"Error syphoning account: {e}"
                result.errors.append(error_msg)
                logger.error(f"     ❌ {error_msg}", exc_info=True)

            result.duration_seconds = time.time() - account_start
            self.syphon_results.append(result)

        total_duration = time.time() - start_time

        summary = {
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': total_duration,
            'accounts_processed': len(self.syphon_results),
            'total_emails': total_emails,
            'total_learnings': total_learnings,
            'results': [asdict(r) for r in self.syphon_results]
        }

        logger.info(f"\n✅ Email Syphon Complete")
        logger.info(f"   Duration: {total_duration:.1f} seconds")
        logger.info(f"   Accounts: {len(self.syphon_results)}")
        logger.info(f"   Total Emails: {total_emails}")
        logger.info(f"   Total Learnings: {total_learnings}")

        # Save summary
        self._save_summary(summary)

        # Return summary dict (contains all info)
        return summary

    def _syphon_account_via_nas(self, account: Dict[str, Any], days: int) -> tuple[List[Dict[str, Any]], List[str]]:
        """
        Syphon email account via NAS Mail Hub.

        Args:
            account: Account configuration
            days: Number of days to syphon

        Returns:
            Tuple of (emails, learnings)
        """
        emails = []
        learnings = []

        account_type = account.get('type', 'nas_mailplus')

        if account_type == 'nas_mailplus':
            # Use NAS MailPlus API or IMAP
            try:
                # Try IMAP connection to NAS Mail Hub
                emails = self._syphon_via_imap_nas(account, days)
            except Exception as e:
                logger.warning(f"     IMAP connection failed: {e}")
                # Fallback: Try MailPlus API
                try:
                    emails = self._syphon_via_mailplus_api(account, days)
                except Exception as e2:
                    logger.warning(f"     MailPlus API failed: {e2}")
                    # Fallback: Use existing email syphon script
                    try:
                        from syphon_all_emails_to_holocron_youtube import EmailSyphonSystem
                        syphon_system = EmailSyphonSystem()
                        emails = syphon_system.syphon_account(account, days=days)
                    except Exception as e3:
                        logger.error(f"     All methods failed: {e3}")

        # Extract learnings from emails
        for email in emails:
            email_learnings = self._extract_learnings_from_email(email)
            learnings.extend(email_learnings)

        return emails, learnings

    def _syphon_via_imap_nas(self, account: Dict[str, Any], days: int) -> List[Dict[str, Any]]:
        """Syphon via IMAP connection to NAS Mail Hub"""
        import imaplib
        import email
        from email.header import decode_header

        emails = []
        cutoff_date = datetime.now() - timedelta(days=days)

        try:
            # Connect to NAS Mail Hub via IMAP
            server = account.get('server', self.nas_ip)
            port = account.get('port', 993)
            username = account.get('username')
            password = account.get('password')

            if not username or not password:
                logger.warning("     ⚠️  No credentials provided for NAS Mail Hub")
                return emails

            # Connect
            mail = imaplib.IMAP4_SSL(server, port) if account.get('use_ssl', True) else imaplib.IMAP4(server, port)
            mail.login(username, password)
            mail.select('INBOX')

            # Search for emails in date range
            date_str = cutoff_date.strftime('%d-%b-%Y')
            status, messages = mail.search(None, f'SINCE {date_str}')

            if status == 'OK':
                email_ids = messages[0].split()

                for email_id in email_ids[-100:]:  # Limit to last 100 for performance
                    try:
                        status, msg_data = mail.fetch(email_id, '(RFC822)')
                        if status == 'OK':
                            email_body = msg_data[0][1]
                            email_message = email.message_from_bytes(email_body)

                            # Extract email data
                            email_data = self._parse_email_message(email_message, account)
                            emails.append(email_data)

                            # Maintain local encrypted copy (AI-encrypted)
                            try:
                                from ai_encrypted_email_storage import AIEncryptedEmailStorage
                                storage = AIEncryptedEmailStorage()
                                email_id = email_data.get('message_id', email_id.decode()).replace('<', '').replace('>', '')
                                storage.maintain_local_copy_on_imap(email_data, email_id)
                            except Exception as e:
                                logger.debug(f"     Local encrypted copy not maintained: {e}")
                    except Exception as e:
                        logger.debug(f"     Error parsing email {email_id}: {e}")

            mail.close()
            mail.logout()

        except Exception as e:
            logger.error(f"     IMAP connection error: {e}")
            raise

        return emails

    def _syphon_via_mailplus_api(self, account: Dict[str, Any], days: int) -> List[Dict[str, Any]]:
        """Syphon via NAS MailPlus API"""
        import requests

        emails = []

        try:
            # NAS MailPlus API endpoint
            api_url = f"{self.nas_mail_hub_web}/webapi/entry.cgi"

            # API call to get emails (requires authentication)
            # This is a placeholder - actual API calls depend on MailPlus API documentation
            logger.info("     ℹ️  MailPlus API integration (placeholder)")
            logger.info("     ℹ️  Requires MailPlus API credentials")

        except Exception as e:
            logger.debug(f"     MailPlus API error: {e}")

        return emails

    def _parse_email_message(self, email_message, account: Dict[str, Any]) -> Dict[str, Any]:
        """Parse email message into structured data"""
        subject = ""
        from_addr = ""
        to_addr = ""
        body = ""
        date = None

        # Decode subject
        subject_header = email_message.get('Subject', '')
        if subject_header:
            decoded = decode_header(subject_header)[0]
            subject = decoded[0]
            if isinstance(subject, bytes):
                subject = subject.decode(decoded[1] or 'utf-8', errors='ignore')

        # Get addresses
        from_addr = email_message.get('From', '')
        to_addr = email_message.get('To', '')

        # Get date
        date_header = email_message.get('Date', '')
        if date_header:
            try:
                from email.utils import parsedate_to_datetime
                date = parsedate_to_datetime(date_header)
            except:
                pass

        # Get body
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
                elif content_type == "text/html" and not body:
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
        else:
            body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')

        return {
            'message_id': email_message.get('Message-ID', ''),
            'subject': subject,
            'from': from_addr,
            'to': to_addr,
            'date': date.isoformat() if date else None,
            'body': body[:1000],  # Limit body size
            'account_id': account.get('account_id', ''),
            'account_name': account.get('account_name', ''),
            'timestamp': datetime.now().isoformat()
        }

    def _extract_learnings_from_email(self, email: Dict[str, Any]) -> List[str]:
        """Extract learnings from email content"""
        learnings = []

        subject = email.get('subject', '').lower()
        body = email.get('body', '').lower()
        text = subject + " " + body

        # Extract actionable items
        if any(word in text for word in ['action required', 'todo', 'task', 'follow up']):
            learnings.append(f"Action item from {email.get('from', 'unknown')}: {email.get('subject', '')[:50]}")

        # Extract important information
        if any(word in text for word in ['important', 'urgent', 'critical', 'deadline']):
            learnings.append(f"Important email from {email.get('from', 'unknown')}: {email.get('subject', '')[:50]}")

        # Extract project-related
        if any(word in text for word in ['project', 'meeting', 'update', 'status']):
            learnings.append(f"Project update from {email.get('from', 'unknown')}: {email.get('subject', '')[:50]}")

        return learnings

    def _save_emails(self, account_id: str, emails: List[Dict[str, Any]]):
        try:
            """Save syphoned emails"""
            account_dir = self.data_dir / account_id
            account_dir.mkdir(parents=True, exist_ok=True)

            today = datetime.now().strftime('%Y%m%d')
            emails_file = account_dir / f"emails_{today}.jsonl"

            with open(emails_file, 'a') as f:
                for email in emails:
                    f.write(json.dumps(email) + '\n')

            logger.debug(f"     Saved {len(emails)} emails to {emails_file}")

        except Exception as e:
            self.logger.error(f"Error in _save_emails: {e}", exc_info=True)
            raise
    def _save_learnings(self, account_id: str, learnings: List[str]):
        try:
            """Save extracted learnings"""
            account_dir = self.data_dir / account_id
            account_dir.mkdir(parents=True, exist_ok=True)

            today = datetime.now().strftime('%Y%m%d')
            learnings_file = account_dir / f"learnings_{today}.json"

            data = {
                'account_id': account_id,
                'timestamp': datetime.now().isoformat(),
                'learnings': learnings
            }

            with open(learnings_file, 'w') as f:
                json.dump(data, f, indent=2)

            logger.debug(f"     Saved {len(learnings)} learnings to {learnings_file}")

        except Exception as e:
            self.logger.error(f"Error in _save_learnings: {e}", exc_info=True)
            raise
    def _save_summary(self, summary: Dict[str, Any]):
        try:
            """Save syphon summary"""
            today = datetime.now().strftime('%Y%m%d')
            summary_file = self.data_dir / f"syphon_summary_{today}.json"

            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2, default=str)

            logger.info(f"📄 Summary saved: {summary_file}")


        except Exception as e:
            self.logger.error(f"Error in _save_summary: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='JARVIS: Syphon All Emails via NAS Mail Hub')
    parser.add_argument('--days', type=int, default=30, help='Number of days to syphon (default: 30)')
    parser.add_argument('--account', help='Specific account ID to syphon')

    args = parser.parse_args()

    syphon = JARVISEmailSyphonNASHub()
    summary = syphon.syphon_all_accounts(days=args.days)

    print("\n" + "=" * 80)
    print("📧 Email Syphon Summary")
    print("=" * 80)
    print(f"Duration: {summary['duration_seconds']:.1f} seconds")
    print(f"Accounts Processed: {summary['accounts_processed']}")
    print(f"Total Emails: {summary['total_emails']}")
    print(f"Total Learnings: {summary['total_learnings']}")
    print("=" * 80)


if __name__ == "__main__":


    main()