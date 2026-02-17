"""
ProtonBridge Integration
Full email services integration for ProtonMail via ProtonBridge desktop app.

ProtonBridge provides local IMAP/SMTP servers that allow accessing ProtonMail
as if it were a standard email provider. This integration treats ProtonMail
as a first-class email service alongside Gmail.

Features:
- IMAP access to ProtonMail via ProtonBridge
- SMTP sending via ProtonBridge
- Full email import/export
- Unified with Gmail integration
- Secure credential management

#JARVIS #LUMINA #PROTONMAIL #PROTONBRIDGE #EMAIL #SECURITY
"""

import json
import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("ProtonBridgeIntegration")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ProtonBridgeIntegration")

# Import unified secrets manager
try:
    from scripts.python.unified_secrets_manager import UnifiedSecretsManager, SecretSource
    SECRETS_MANAGER_AVAILABLE = True
except ImportError:
    SECRETS_MANAGER_AVAILABLE = False
    logger.warning("⚠️  Unified Secrets Manager not available")


@dataclass
class ProtonMailMessage:
    """ProtonMail email message structure."""
    message_id: str
    subject: str
    from_address: str
    to_address: str
    date: str
    body: str
    html_body: Optional[str] = None
    attachments: List[Dict[str, Any]] = None
    headers: Dict[str, str] = None

    def __post_init__(self):
        if self.attachments is None:
            self.attachments = []
        if self.headers is None:
            self.headers = {}


class ProtonBridgeIntegration:
    """
    ProtonBridge Integration for ProtonMail

    Provides full email services via ProtonBridge desktop app:
    - IMAP access (receiving emails)
    - SMTP access (sending emails)
    - Full email import/export
    - Unified with Gmail integration

    ACCOUNT INFORMATION SECRETS REMINDER: LOCATION AZURE VAULT / PROTONPASSCLI / DASHLANE.
    """

    def __init__(self, project_root: Path, account_name: str = "default"):
        """
        Initialize ProtonBridge Integration.

        Args:
            project_root: Project root directory
            account_name: ProtonMail account name (for multi-account support)
        """
        self.project_root = Path(project_root)
        self.account_name = account_name
        self.data_dir = self.project_root / "data" / "protonmail" / account_name
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Unified Secrets Manager
        # ACCOUNT INFORMATION SECRETS REMINDER: LOCATION AZURE VAULT / PROTONPASSCLI / DASHLANE.
        if SECRETS_MANAGER_AVAILABLE:
            self.secrets_manager = UnifiedSecretsManager(
                self.project_root,
                prefer_source=SecretSource.AZURE_KEY_VAULT
            )
        else:
            self.secrets_manager = None
            logger.warning("⚠️  Unified Secrets Manager not available")

        # ProtonBridge default ports (local IMAP/SMTP servers)
        self.imap_host = "127.0.0.1"
        self.imap_port = 1143  # Default ProtonBridge IMAP port
        self.smtp_host = "127.0.0.1"
        self.smtp_port = 1025  # Default ProtonBridge SMTP port

        # Load configuration
        self.config = self._load_config()

        # Connection objects
        self.imap_connection = None
        self.smtp_connection = None

        logger.info(f"✅ ProtonBridge Integration initialized for account: {account_name}")

    def _load_config(self) -> Dict[str, Any]:
        try:
            """Load ProtonBridge configuration."""
            config_file = self.project_root / "config" / "protonbridge_config.json"

            if config_file.exists():
                with open(config_file, 'r') as f:
                    return json.load(f)

            # Default configuration
            default_config = {
                "account_name": self.account_name,
                "imap_host": self.imap_host,
                "imap_port": self.imap_port,
                "smtp_host": self.smtp_host,
                "smtp_port": self.smtp_port,
                "use_tls": True,
                "use_ssl": False,
                "timeout": 30
            }

            # Save default config
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)

            return default_config

        except Exception as e:
            self.logger.error(f"Error in _load_config: {e}", exc_info=True)
            raise
    def _get_credentials(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Get ProtonMail credentials from secrets manager.

        ACCOUNT INFORMATION SECRETS REMINDER: LOCATION AZURE VAULT / PROTONPASSCLI / DASHLANE.
        """
        if not self.secrets_manager:
            logger.warning("⚠️  Secrets manager not available")
            return None, None

        # Try multiple possible secret names
        credential_secrets = [
            f"protonmail-{self.account_name}-password",
            f"protonmail-{self.account_name}-credentials",
            "protonmail-password",
            "protonmail-credentials",
            "protonbridge-password"
        ]

        password = None
        for secret_name in credential_secrets:
            password = self.secrets_manager.get_secret(secret_name)
            if password:
                logger.info(f"✅ Retrieved ProtonMail credentials from secrets manager ({secret_name})")
                break

        if not password:
            logger.warning("⚠️  ProtonMail credentials not found in Azure Key Vault / ProtonPass / Dashlane")
            logger.info("💡 Store ProtonMail password using: unified_secrets_manager.py --set protonmail-password <value>")

        # Username is typically the ProtonMail email address
        username_secrets = [
            f"protonmail-{self.account_name}-username",
            f"protonmail-{self.account_name}-email",
            "protonmail-username",
            "protonmail-email"
        ]

        username = None
        for secret_name in username_secrets:
            username = self.secrets_manager.get_secret(secret_name)
            if username:
                break

        return username, password

    def connect_imap(self) -> bool:
        """
        Connect to ProtonBridge IMAP server.

        Returns:
            True if connection successful
        """
        try:
            username, password = self._get_credentials()

            if not username or not password:
                logger.error("❌ Cannot connect: credentials not available")
                return False

            # Connect to ProtonBridge IMAP
            imap_host = self.config.get("imap_host", self.imap_host)
            imap_port = self.config.get("imap_port", self.imap_port)
            use_ssl = self.config.get("use_ssl", False)

            if use_ssl:
                self.imap_connection = imaplib.IMAP4_SSL(imap_host, imap_port)
            else:
                self.imap_connection = imaplib.IMAP4(imap_host, imap_port)

            # Login
            self.imap_connection.login(username, password)

            logger.info(f"✅ Connected to ProtonBridge IMAP ({imap_host}:{imap_port})")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to connect to ProtonBridge IMAP: {e}")
            self.imap_connection = None
            return False

    def connect_smtp(self) -> bool:
        """
        Connect to ProtonBridge SMTP server.

        Returns:
            True if connection successful
        """
        try:
            username, password = self._get_credentials()

            if not username or not password:
                logger.error("❌ Cannot connect: credentials not available")
                return False

            # Connect to ProtonBridge SMTP
            smtp_host = self.config.get("smtp_host", self.smtp_host)
            smtp_port = self.config.get("smtp_port", self.smtp_port)
            use_tls = self.config.get("use_tls", True)

            if use_tls:
                self.smtp_connection = smtplib.SMTP(smtp_host, smtp_port)
                self.smtp_connection.starttls()
            else:
                self.smtp_connection = smtplib.SMTP(smtp_host, smtp_port)

            # Login
            self.smtp_connection.login(username, password)

            logger.info(f"✅ Connected to ProtonBridge SMTP ({smtp_host}:{smtp_port})")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to connect to ProtonBridge SMTP: {e}")
            self.smtp_connection = None
            return False

    def search_emails(self, 
                     query: str = "ALL",
                     days_back: int = 30,
                     folder: str = "INBOX") -> List[ProtonMailMessage]:
        """
        Search emails via ProtonBridge IMAP.

        Args:
            query: IMAP search query (default: "ALL")
            days_back: Days to search back
            folder: Mailbox folder (default: "INBOX")

        Returns:
            List of ProtonMailMessage objects
        """
        if not self.imap_connection:
            if not self.connect_imap():
                return []

        try:
            # Select folder
            self.imap_connection.select(folder)

            # Build date-based query if needed
            if days_back > 0:
                since_date = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")
                query = f"{query} SINCE {since_date}"

            # Search
            status, message_ids = self.imap_connection.search(None, query)

            if status != "OK" or not message_ids[0]:
                # Handle empty accounts gracefully (e.g., newly created accounts)
                logger.info(f"ℹ️  No emails found for account '{self.account_name}' (query: {query})")
                logger.info(f"   This is normal for new or empty accounts")
                return []

            # Fetch messages
            messages = []
            for msg_id in message_ids[0].split():
                try:
                    message = self._fetch_message(msg_id)
                    if message:
                        messages.append(message)
                except Exception as e:
                    logger.warning(f"Failed to fetch message {msg_id}: {e}")

            logger.info(f"✅ Found {len(messages)} emails")
            return messages

        except Exception as e:
            logger.error(f"❌ Failed to search emails: {e}")
            return []

    def _fetch_message(self, msg_id: bytes) -> Optional[ProtonMailMessage]:
        """Fetch a single message by ID."""
        try:
            status, msg_data = self.imap_connection.fetch(msg_id, "(RFC822)")

            if status != "OK":
                return None

            # Parse email
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)

            # Extract headers
            subject = self._decode_header(email_message["Subject"] or "")
            from_addr = email_message["From"] or ""
            to_addr = email_message["To"] or ""
            date = email_message["Date"] or ""
            message_id = email_message["Message-ID"] or ""

            # Extract body
            body = ""
            html_body = None

            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition", ""))

                    if "attachment" in content_disposition:
                        continue

                    if content_type == "text/plain":
                        body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                    elif content_type == "text/html":
                        html_body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
            else:
                body = email_message.get_payload(decode=True).decode("utf-8", errors="ignore")

            # Extract attachments
            attachments = []
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_disposition = str(part.get("Content-Disposition", ""))
                    if "attachment" in content_disposition:
                        filename = part.get_filename()
                        if filename:
                            attachments.append({
                                "filename": self._decode_header(filename),
                                "content_type": part.get_content_type(),
                                "size": len(part.get_payload(decode=True))
                            })

            return ProtonMailMessage(
                message_id=message_id,
                subject=subject,
                from_address=from_addr,
                to_address=to_addr,
                date=date,
                body=body,
                html_body=html_body,
                attachments=attachments,
                headers=dict(email_message.items())
            )

        except Exception as e:
            logger.error(f"Failed to fetch message {msg_id}: {e}")
            return None

    def _decode_header(self, header: str) -> str:
        """Decode email header."""
        if not header:
            return ""

        decoded_parts = decode_header(header)
        decoded_string = ""

        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                if encoding:
                    decoded_string += part.decode(encoding, errors="ignore")
                else:
                    decoded_string += part.decode("utf-8", errors="ignore")
            else:
                decoded_string += part

        return decoded_string

    def send_email(self,
                   to_address: str,
                   subject: str,
                   body: str,
                   html_body: Optional[str] = None,
                   from_address: Optional[str] = None,
                   attachments: List[Path] = None) -> bool:
        """
        Send email via ProtonBridge SMTP.

        Args:
            to_address: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
            from_address: Sender address (defaults to account email)
            attachments: Optional list of attachment file paths

        Returns:
            True if sent successfully
        """
        if not self.smtp_connection:
            if not self.connect_smtp():
                return False

        try:
            # Get sender address
            if not from_address:
                username, _ = self._get_credentials()
                from_address = username or f"protonmail-{self.account_name}@protonmail.com"

            # Create message
            if html_body:
                msg = MIMEMultipart("alternative")
                msg.attach(MIMEText(body, "plain"))
                msg.attach(MIMEText(html_body, "html"))
            else:
                msg = MIMEText(body, "plain")

            msg["From"] = from_address
            msg["To"] = to_address
            msg["Subject"] = subject

            # Add attachments if any
            if attachments:
                from email.mime.base import MIMEBase
                from email import encoders

                for attachment_path in attachments:
                    if attachment_path.exists():
                        with open(attachment_path, "rb") as f:
                            attachment = MIMEBase("application", "octet-stream")
                            attachment.set_payload(f.read())
                            encoders.encode_base64(attachment)
                            attachment.add_header(
                                "Content-Disposition",
                                f"attachment; filename={attachment_path.name}"
                            )
                            msg.attach(attachment)

            # Send
            self.smtp_connection.sendmail(from_address, [to_address], msg.as_string())

            logger.info(f"✅ Email sent to {to_address}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            return False

    def import_emails(self, days_back: int = 60, folder: str = "INBOX") -> List[ProtonMailMessage]:
        """
        Import emails from ProtonMail via ProtonBridge.

        Args:
            days_back: Days to import back
            folder: Mailbox folder

        Returns:
            List of imported ProtonMailMessage objects
        """
        logger.info(f"Importing emails from ProtonMail (last {days_back} days)")

        messages = self.search_emails(query="ALL", days_back=days_back, folder=folder)

        # Save imported emails
        import_dir = self.data_dir / "imported"
        import_dir.mkdir(parents=True, exist_ok=True)

        imported = []
        for message in messages:
            try:
                # Save message
                message_file = import_dir / f"{message.message_id.replace('<', '').replace('>', '')}.json"
                with open(message_file, 'w') as f:
                    json.dump(asdict(message), f, indent=2, ensure_ascii=False)

                imported.append(message)
            except Exception as e:
                logger.warning(f"Failed to save message {message.message_id}: {e}")

        logger.info(f"✅ Imported {len(imported)} emails from ProtonMail")
        return imported

    def disconnect(self):
        """Disconnect from IMAP and SMTP servers."""
        if self.imap_connection:
            try:
                self.imap_connection.close()
                self.imap_connection.logout()
            except Exception:
                pass
            self.imap_connection = None

        if self.smtp_connection:
            try:
                self.smtp_connection.quit()
            except Exception:
                pass
            self.smtp_connection = None

        logger.info("✅ Disconnected from ProtonBridge")


def main():
    try:
        """Test ProtonBridge Integration."""
        import argparse

        parser = argparse.ArgumentParser(description="ProtonBridge Integration")
        parser.add_argument("--project-root", type=Path, default=Path(__file__).parent.parent.parent)
        parser.add_argument("--account", type=str, default="default", help="ProtonMail account name")
        parser.add_argument("--import-emails", action="store_true", dest="import_emails", help="Import emails")
        parser.add_argument("--days", type=int, default=30, help="Days to import back")
        parser.add_argument("--search", type=str, help="Search query")
        parser.add_argument("--send", nargs=3, metavar=("TO", "SUBJECT", "BODY"), help="Send email")

        args = parser.parse_args()

        bridge = ProtonBridgeIntegration(args.project_root, args.account)

        if args.import_emails:
            messages = bridge.import_emails(days_back=args.days)
            print(f"✅ Imported {len(messages)} emails")
        elif args.search:
            messages = bridge.search_emails(query=args.search, days_back=args.days)
            print(f"✅ Found {len(messages)} emails")
            for msg in messages[:5]:  # Show first 5
                print(f"  - {msg.subject} ({msg.from_address})")
        elif args.send:
            to, subject, body = args.send
            if bridge.send_email(to, subject, body):
                print(f"✅ Email sent to {to}")
            else:
                print(f"❌ Failed to send email")
        else:
            parser.print_help()

        bridge.disconnect()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()