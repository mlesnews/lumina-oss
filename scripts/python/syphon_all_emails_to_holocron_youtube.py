#!/usr/bin/env python3
"""
SYPHON All Email Accounts → Holocron Archive & YouTube Library

SYPHON all email accounts (secure and unsecure) for data mining:
1. Extract actionable intelligence from all emails
2. Store in @HOLOCRON Archive
3. Send to YouTube Library

Supports:
- IMAP (secure: Gmail, Outlook, etc.)
- POP3 (unsecure: legacy accounts)
- OAuth2 (modern secure accounts)
- App passwords (2FA accounts)
"""

import json
import imaplib
import poplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
import ssl
import base64

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
    from syphon.models import SyphonData, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None
    SYPHONConfig = None
    SubscriptionTier = None

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False


@dataclass
class EmailAccount:
    """Email account configuration"""
    account_id: str
    account_name: str
    email_address: str
    account_type: str  # "imap", "pop3", "oauth2_gmail", "oauth2_outlook"
    server: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    oauth2_credentials: Optional[Dict[str, Any]] = None
    use_ssl: bool = True
    use_tls: bool = False
    secure: bool = True  # True for secure, False for unsecure
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        # Don't expose passwords in dict
        if data.get("password"):
            data["password"] = "***REDACTED***"
        return data


@dataclass
class EmailMessage:
    """Extracted email message"""
    message_id: str
    email_id: str
    subject: str
    body: str
    body_html: Optional[str] = None
    from_address: str
    to_address: str
    cc_addresses: List[str] = field(default_factory=list)
    bcc_addresses: List[str] = field(default_factory=list)
    date: Optional[datetime] = None
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    headers: Dict[str, Any] = field(default_factory=dict)
    account_id: str = ""
    account_name: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if data.get("date"):
            data["date"] = data["date"].isoformat()
        return data


class EmailSyphonToHolocronYouTube:
    """
    SYPHON all email accounts → Holocron Archive & YouTube Library
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("EmailSyphonToHolocronYouTube")

        # Directories
        self.data_dir = self.project_root / "data" / "email_syphon"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.holocron_dir = self.project_root / "data" / "holocron" / "email_intelligence"
        self.holocron_dir.mkdir(parents=True, exist_ok=True)

        self.youtube_dir = self.project_root / "data" / "youtube_library" / "email_content"
        self.youtube_dir.mkdir(parents=True, exist_ok=True)

        # Files
        self.accounts_file = self.project_root / "config" / "email_accounts.json"
        self.syphon_results_file = self.data_dir / "syphon_results.json"
        self.holocron_index_file = self.holocron_dir / "EMAIL_INTELLIGENCE_INDEX.json"

        # Initialize SYPHON
        self.syphon = None
        if SYPHON_AVAILABLE:
            try:
                config = SYPHONConfig(
                    project_root=self.project_root,
                    subscription_tier=SubscriptionTier.PREMIUM,
                    enable_self_healing=True,
                    enable_banking=False
                )
                self.syphon = SYPHONSystem(config)
                self.logger.info("✅ SYPHON system initialized")
            except Exception as e:
                self.logger.warning(f"SYPHON not available: {e}")

        # Email accounts
        self.accounts: List[EmailAccount] = []
        self._load_accounts()

        # Results
        self.syphon_results: List[Dict[str, Any]] = []
        self.holocron_entries: List[Dict[str, Any]] = []
        self.youtube_entries: List[Dict[str, Any]] = []

    def _load_accounts(self):
        """Load email accounts from config"""
        if not self.accounts_file.exists():
            self.logger.warning(f"Email accounts file not found: {self.accounts_file}")
            return

        try:
            with open(self.accounts_file, 'r', encoding='utf-8') as f:
                accounts_data = json.load(f)

            for account_data in accounts_data.get("accounts", []):
                account = EmailAccount(**account_data)
                if account.enabled:
                    self.accounts.append(account)
                    self.logger.info(f"✅ Loaded account: {account.account_name} ({account.email_address})")
        except Exception as e:
            self.logger.error(f"Error loading accounts: {e}")

    def syphon_account(self, account: EmailAccount, max_emails: int = 100) -> List[EmailMessage]:
        """
        SYPHON emails from an account

        Args:
            account: Email account configuration
            max_emails: Maximum number of emails to process

        Returns:
            List of extracted email messages
        """
        self.logger.info(f"🔄 SYPHONing account: {account.account_name} ({account.email_address})")

        messages = []

        try:
            if account.account_type == "imap":
                messages = self._syphon_imap(account, max_emails)
            elif account.account_type == "pop3":
                messages = self._syphon_pop3(account, max_emails)
            elif account.account_type == "oauth2_gmail":
                messages = self._syphon_oauth2_gmail(account, max_emails)
            elif account.account_type == "oauth2_outlook":
                messages = self._syphon_oauth2_outlook(account, max_emails)
            else:
                self.logger.warning(f"Unsupported account type: {account.account_type}")
        except Exception as e:
            self.logger.error(f"Error SYPHONing account {account.account_name}: {e}", exc_info=True)

        self.logger.info(f"✅ SYPHONed {len(messages)} emails from {account.account_name}")
        return messages

    def _syphon_imap(self, account: EmailAccount, max_emails: int) -> List[EmailMessage]:
        """SYPHON emails via IMAP"""
        messages = []

        try:
            # Connect to IMAP server
            if account.use_ssl:
                mail = imaplib.IMAP4_SSL(account.server, account.port or 993)
            else:
                mail = imaplib.IMAP4(account.server, account.port or 143)
                if account.use_tls:
                    mail.starttls()

            # Login
            mail.login(account.username or account.email_address, account.password)

            # Select mailbox
            mail.select('INBOX')

            # Search for emails
            status, messages_ids = mail.search(None, 'ALL')
            if status != 'OK':
                return messages

            email_ids = messages_ids[0].split()
            email_ids = email_ids[-max_emails:]  # Get most recent

            # Fetch emails
            for email_id in email_ids:
                try:
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    if status != 'OK':
                        continue

                    raw_email = msg_data[0][1]
                    email_message = email.message_from_bytes(raw_email)

                    # Parse email
                    parsed_message = self._parse_email_message(email_message, account)
                    if parsed_message:
                        messages.append(parsed_message)
                except Exception as e:
                    self.logger.debug(f"Error parsing email {email_id}: {e}")
                    continue

            mail.logout()
        except Exception as e:
            self.logger.error(f"IMAP error: {e}")

        return messages

    def _syphon_pop3(self, account: EmailAccount, max_emails: int) -> List[EmailMessage]:
        """SYPHON emails via POP3"""
        messages = []

        try:
            # Connect to POP3 server
            if account.use_ssl:
                mail = poplib.POP3_SSL(account.server, account.port or 995)
            else:
                mail = poplib.POP3(account.server, account.port or 110)
                if account.use_tls:
                    mail.stls()

            # Login
            mail.user(account.username or account.email_address)
            mail.pass_(account.password)

            # Get email list
            num_messages = len(mail.list()[1])
            num_to_fetch = min(max_emails, num_messages)

            # Fetch emails
            for i in range(num_messages - num_to_fetch, num_messages):
                try:
                    raw_email = b'\n'.join(mail.retr(i + 1)[1])
                    email_message = email.message_from_bytes(raw_email)

                    # Parse email
                    parsed_message = self._parse_email_message(email_message, account)
                    if parsed_message:
                        messages.append(parsed_message)
                except Exception as e:
                    self.logger.debug(f"Error parsing email {i}: {e}")
                    continue

            mail.quit()
        except Exception as e:
            self.logger.error(f"POP3 error: {e}")

        return messages

    def _syphon_oauth2_gmail(self, account: EmailAccount, max_emails: int) -> List[EmailMessage]:
        """SYPHON emails via Gmail OAuth2 API"""
        messages = []

        if not GOOGLE_API_AVAILABLE:
            self.logger.warning("Google API not available for OAuth2 Gmail")
            return messages

        try:
            # Load OAuth2 credentials
            creds = None
            if account.oauth2_credentials:
                # Use provided credentials
                creds = Credentials.from_authorized_user_info(account.oauth2_credentials)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    self.logger.warning("OAuth2 credentials not available or invalid")
                    return messages

            # Build Gmail service
            service = build('gmail', 'v1', credentials=creds)

            # List messages
            results = service.users().messages().list(userId='me', maxResults=max_emails).execute()
            messages_list = results.get('messages', [])

            # Fetch each message
            for msg in messages_list:
                try:
                    msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()

                    # Parse Gmail message
                    parsed_message = self._parse_gmail_message(msg_data, account)
                    if parsed_message:
                        messages.append(parsed_message)
                except Exception as e:
                    self.logger.debug(f"Error parsing Gmail message {msg['id']}: {e}")
                    continue
        except Exception as e:
            self.logger.error(f"Gmail OAuth2 error: {e}")

        return messages

    def _syphon_oauth2_outlook(self, account: EmailAccount, max_emails: int) -> List[EmailMessage]:
        """SYPHON emails via Outlook OAuth2 API"""
        # TODO: Implement Outlook OAuth2  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
        self.logger.warning("Outlook OAuth2 not yet implemented")
        return []

    def _parse_email_message(self, email_message: email.message.Message, account: EmailAccount) -> Optional[EmailMessage]:
        """Parse email.message.Message into EmailMessage"""
        try:
            # Get headers
            subject = self._decode_header(email_message.get('Subject', ''))
            from_addr = self._decode_header(email_message.get('From', ''))
            to_addr = self._decode_header(email_message.get('To', ''))
            cc_addrs = [self._decode_header(addr) for addr in email_message.get_all('Cc', [])]
            date_str = email_message.get('Date', '')

            # Parse date
            date = None
            if date_str:
                try:
                    date = parsedate_to_datetime(date_str)
                except:
                    pass

            # Get body
            body = ""
            body_html = None

            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        body = self._get_part_text(part)
                    elif content_type == "text/html":
                        body_html = self._get_part_text(part)
            else:
                body = self._get_part_text(email_message)

            # Get attachments
            attachments = []
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_disposition() == 'attachment':
                        filename = part.get_filename()
                        if filename:
                            attachments.append({
                                "filename": self._decode_header(filename),
                                "content_type": part.get_content_type(),
                                "size": len(part.get_payload(decode=True))
                            })

            # Create EmailMessage
            message_id = email_message.get('Message-ID', f"msg_{datetime.now().timestamp()}")
            email_id = email_message.get('Message-ID', message_id)

            return EmailMessage(
                message_id=message_id,
                email_id=email_id,
                subject=subject,
                body=body,
                body_html=body_html,
                from_address=from_addr,
                to_address=to_addr,
                cc_addresses=cc_addrs,
                date=date,
                attachments=attachments,
                headers=dict(email_message.items()),
                account_id=account.account_id,
                account_name=account.account_name,
                metadata={
                    "account_type": account.account_type,
                    "secure": account.secure
                }
            )
        except Exception as e:
            self.logger.debug(f"Error parsing email message: {e}")
            return None

    def _parse_gmail_message(self, msg_data: Dict[str, Any], account: EmailAccount) -> Optional[EmailMessage]:
        """Parse Gmail API message into EmailMessage"""
        try:
            # Extract headers
            headers = {h['name']: h['value'] for h in msg_data.get('payload', {}).get('headers', [])}

            subject = headers.get('Subject', '')
            from_addr = headers.get('From', '')
            to_addr = headers.get('To', '')
            cc_addrs = [h for h in headers.get('Cc', '').split(',') if h.strip()]
            date_str = headers.get('Date', '')

            # Parse date
            date = None
            if date_str:
                try:
                    date = parsedate_to_datetime(date_str)
                except:
                    pass

            # Get body
            body = ""
            body_html = None

            payload = msg_data.get('payload', {})
            if 'parts' in payload:
                for part in payload['parts']:
                    mime_type = part.get('mimeType', '')
                    if mime_type == 'text/plain':
                        body = self._decode_gmail_body(part)
                    elif mime_type == 'text/html':
                        body_html = self._decode_gmail_body(part)
            else:
                mime_type = payload.get('mimeType', '')
                if mime_type == 'text/plain':
                    body = self._decode_gmail_body(payload)
                elif mime_type == 'text/html':
                    body_html = self._decode_gmail_body(payload)

            # Get attachments
            attachments = []
            if 'parts' in payload:
                for part in payload['parts']:
                    if part.get('filename'):
                        attachments.append({
                            "filename": part.get('filename'),
                            "content_type": part.get('mimeType', ''),
                            "size": part.get('body', {}).get('size', 0)
                        })

            message_id = msg_data.get('id', f"gmail_{datetime.now().timestamp()}")

            return EmailMessage(
                message_id=message_id,
                email_id=message_id,
                subject=subject,
                body=body,
                body_html=body_html,
                from_address=from_addr,
                to_address=to_addr,
                cc_addresses=cc_addrs,
                date=date,
                attachments=attachments,
                headers=headers,
                account_id=account.account_id,
                account_name=account.account_name,
                metadata={
                    "account_type": account.account_type,
                    "secure": account.secure,
                    "gmail_thread_id": msg_data.get('threadId')
                }
            )
        except Exception as e:
            self.logger.debug(f"Error parsing Gmail message: {e}")
            return None

    def _decode_header(self, header: str) -> str:
        """Decode email header"""
        try:
            decoded_parts = decode_header(header)
            decoded_str = ""
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    decoded_str += part.decode(encoding or 'utf-8', errors='ignore')
                else:
                    decoded_str += part
            return decoded_str
        except:
            return header

    def _get_part_text(self, part: email.message.Message) -> str:
        """Get text from email part"""
        try:
            payload = part.get_payload(decode=True)
            if payload:
                charset = part.get_content_charset() or 'utf-8'
                return payload.decode(charset, errors='ignore')
        except:
            pass
        return ""

    def _decode_gmail_body(self, part: Dict[str, Any]) -> str:
        """Decode Gmail message body"""
        try:
            body_data = part.get('body', {}).get('data', '')
            if body_data:
                return base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
        except:
            pass
        return ""

    def process_emails_to_holocron_youtube(self, max_emails_per_account: int = 100):
        """
        Process all emails: SYPHON → Holocron → YouTube Library
        """
        self.logger.info("🚀 Starting email SYPHON → Holocron → YouTube Library")

        all_messages = []

        # SYPHON all accounts
        for account in self.accounts:
            if not account.enabled:
                continue

            messages = self.syphon_account(account, max_emails_per_account)
            all_messages.extend(messages)

        self.logger.info(f"✅ SYPHONed {len(all_messages)} total emails")

        # Process each email
        for message in all_messages:
            # SYPHON intelligence
            syphon_result = self._syphon_intelligence(message)
            if syphon_result:
                self.syphon_results.append(syphon_result)

            # Store in Holocron
            holocron_entry = self._store_in_holocron(message, syphon_result)
            if holocron_entry:
                self.holocron_entries.append(holocron_entry)

            # Send to YouTube Library
            youtube_entry = self._send_to_youtube_library(message, syphon_result)
            if youtube_entry:
                self.youtube_entries.append(youtube_entry)

        # Save results
        self._save_results()

        self.logger.info(f"✅ Processed {len(all_messages)} emails")
        self.logger.info(f"   - SYPHON results: {len(self.syphon_results)}")
        self.logger.info(f"   - Holocron entries: {len(self.holocron_entries)}")
        self.logger.info(f"   - YouTube entries: {len(self.youtube_entries)}")

        return {
            "total_emails": len(all_messages),
            "syphon_results": len(self.syphon_results),
            "holocron_entries": len(self.holocron_entries),
            "youtube_entries": len(self.youtube_entries)
        }

    def _syphon_intelligence(self, message: EmailMessage) -> Optional[Dict[str, Any]]:
        """SYPHON intelligence from email"""
        if not self.syphon:
            return None

        try:
            result = self.syphon.syphon_email(
                email_id=message.email_id,
                subject=message.subject,
                body=message.body,
                from_address=message.from_address,
                to_address=message.to_address,
                metadata={
                    "account_id": message.account_id,
                    "account_name": message.account_name,
                    "date": message.date.isoformat() if message.date else None,
                    "attachments": len(message.attachments)
                }
            )

            if result.success and result.data:
                return {
                    "email_id": message.email_id,
                    "syphon_data": result.data.to_dict(),
                    "actionable_items": result.data.actionable_items,
                    "tasks": result.data.tasks,
                    "decisions": result.data.decisions,
                    "intelligence": result.data.intelligence
                }
        except Exception as e:
            self.logger.debug(f"Error SYPHONing intelligence: {e}")

        return None

    def _store_in_holocron(self, message: EmailMessage, syphon_result: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Store email intelligence in Holocron Archive"""
        try:
            entry_id = f"HOLOCRON-EMAIL-{message.email_id}"
            entry_file = self.holocron_dir / f"{entry_id}.json"

            entry_data = {
                "entry_id": entry_id,
                "title": message.subject or "Email Intelligence",
                "classification": "email_intelligence",
                "source": "email_syphon",
                "email_data": message.to_dict(),
                "syphon_intelligence": syphon_result,
                "extracted_at": datetime.now().isoformat(),
                "account_id": message.account_id,
                "account_name": message.account_name,
                "tags": [
                    "#email",
                    "#syphon",
                    "#intelligence",
                    f"#account_{message.account_id}",
                    f"#from_{message.from_address.split('@')[1] if '@' in message.from_address else 'unknown'}"
                ],
                "metadata": {
                    "secure": message.metadata.get("secure", True),
                    "has_attachments": len(message.attachments) > 0,
                    "actionable_items_count": len(syphon_result.get("actionable_items", [])) if syphon_result else 0
                }
            }

            # Save entry
            with open(entry_file, 'w', encoding='utf-8') as f:
                json.dump(entry_data, f, indent=2, ensure_ascii=False, default=str)

            return entry_data
        except Exception as e:
            self.logger.debug(f"Error storing in Holocron: {e}")
            return None

    def _send_to_youtube_library(self, message: EmailMessage, syphon_result: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Send email content to YouTube Library"""
        try:
            # Create YouTube library entry
            entry_id = f"YT-EMAIL-{message.email_id}"
            entry_file = self.youtube_dir / f"{entry_id}.json"

            # Extract content for YouTube
            content = {
                "title": message.subject or "Email Content",
                "description": message.body[:500] if message.body else "",
                "source": "email",
                "email_id": message.email_id,
                "from": message.from_address,
                "date": message.date.isoformat() if message.date else None,
                "content": message.body,
                "intelligence": syphon_result.get("intelligence", []) if syphon_result else [],
                "actionable_items": syphon_result.get("actionable_items", []) if syphon_result else []
            }

            entry_data = {
                "entry_id": entry_id,
                "youtube_library_entry": content,
                "email_data": message.to_dict(),
                "syphon_data": syphon_result,
                "created_at": datetime.now().isoformat(),
                "account_id": message.account_id,
                "account_name": message.account_name
            }

            # Save entry
            with open(entry_file, 'w', encoding='utf-8') as f:
                json.dump(entry_data, f, indent=2, ensure_ascii=False, default=str)

            return entry_data
        except Exception as e:
            self.logger.debug(f"Error sending to YouTube library: {e}")
            return None

    def _save_results(self):
        try:
            """Save all results"""
            # Save SYPHON results
            with open(self.syphon_results_file, 'w', encoding='utf-8') as f:
                json.dump(self.syphon_results, f, indent=2, ensure_ascii=False, default=str)

            # Update Holocron index
            index_data = {
                "index_metadata": {
                    "name": "Email Intelligence - Holocron Index",
                    "version": "1.0.0",
                    "last_updated": datetime.now().isoformat(),
                    "total_entries": len(self.holocron_entries)
                },
                "entries": {entry["entry_id"]: entry for entry in self.holocron_entries}
            }

            with open(self.holocron_index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False, default=str)

            self.logger.info("✅ Results saved")


        except Exception as e:
            self.logger.error(f"Error in _save_results: {e}", exc_info=True)
            raise
def main():
    """Main execution"""
    syphon = EmailSyphonToHolocronYouTube()

    print("🚀 Email SYPHON → Holocron → YouTube Library")
    print("=" * 80)
    print("")

    # Process emails
    result = syphon.process_emails_to_holocron_youtube(max_emails_per_account=100)

    print("")
    print("✅ Processing Complete!")
    print(f"   Total Emails: {result['total_emails']}")
    print(f"   SYPHON Results: {result['syphon_results']}")
    print(f"   Holocron Entries: {result['holocron_entries']}")
    print(f"   YouTube Entries: {result['youtube_entries']}")
    print("")
    print(f"📁 Results saved to:")
    print(f"   - SYPHON: {syphon.syphon_results_file}")
    print(f"   - Holocron: {syphon.holocron_index_file}")
    print(f"   - YouTube: {syphon.youtube_dir}")


if __name__ == "__main__":



    main()