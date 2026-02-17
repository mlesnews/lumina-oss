"""
LUMINA Gmail Integration System
Direct LUMINA<>GOOGLE Gmail integration for search, filtering, and email management.
Integrated with Admin SME job slot and Holocron/Jedi Archives.

#JARVIS #LUMINA #GMAIL #ADMIN #HOLOCRON #JEDIARCHIVES
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("LUMINAGmailIntegration")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("LUMINAGmailIntegration")


class EmailCategory(Enum):
    """Email categories for organization."""
    ADMINISTRATIVE = "administrative"
    FINANCIAL = "financial"
    TECHNICAL = "technical"
    PERSONAL = "personal"
    PROJECT = "project"
    REFERENCE = "reference"
    ARCHIVE = "archive"
    ACTION_REQUIRED = "action_required"
    FOLLOW_UP = "follow_up"
    JEDI_ARCHIVES = "jedi_archives"  # For Holocron integration


class EmailPriority(Enum):
    """Email priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    ARCHIVE = "archive"


@dataclass
class EmailMetadata:
    """Email metadata for organization."""
    email_id: str
    thread_id: str
    subject: str
    from_address: str
    to_address: str
    date: str
    category: EmailCategory
    priority: EmailPriority
    tags: List[str]
    holocron_reference: Optional[str] = None
    jedi_archive_path: Optional[str] = None
    admin_notes: Optional[str] = None
    action_required: bool = False
    follow_up_date: Optional[str] = None


class LUMINAGmailIntegration:
    """
    LUMINA Gmail Integration System.

    Features:
    - Direct Gmail API integration
    - Advanced search and filtering
    - Admin SME role management
    - Secretarial workflows
    - Holocron/Jedi Archives integration
    """

    def __init__(self, project_root: Path):
        """
        Initialize LUMINA Gmail Integration.

        Args:
            project_root: Root path of the LUMINA project
        """
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "gmail_integration"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.metadata_dir = self.data_dir / "metadata"
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

        self.holocron_dir = self.project_root / "data" / "holocron"
        self.jedi_archives_dir = self.project_root / "data" / "jedi_archives"

        # Admin SME configuration
        self.admin_config_file = self.data_dir / "admin_sme_config.json"
        self.load_admin_config()

        # Gmail API setup
        self.gmail_service = None
        self._initialize_gmail_api()

    def load_admin_config(self) -> Dict[str, Any]:
        try:
            """Load Admin SME configuration."""
            if self.admin_config_file.exists():
                with open(self.admin_config_file, 'r') as f:
                    return json.load(f)

            # Default config
            default_config = {
                "admin_sme": {
                    "role": "Administrative Subject Matter Expert",
                    "responsibilities": [
                        "Email sending and receiving",
                        "Email categorization and organization",
                        "Jedi Archives/Holocron integration",
                        "Priority management",
                        "Action item tracking"
                    ],
                    "permissions": [
                        "read_all_emails",
                        "send_emails",
                        "categorize_emails",
                        "archive_emails",
                        "access_holocron"
                    ]
                },
                "secretarial_workflows": {
                    "incoming": {
                        "auto_categorize": True,
                        "auto_priority": True,
                        "auto_archive": False,
                        "holocron_sync": True
                    },
                    "outgoing": {
                        "track_sent": True,
                        "follow_up_reminders": True,
                        "archive_sent": True
                    }
                },
                "jedi_archives_integration": {
                    "enabled": True,
                    "auto_categorize": True,
                    "archive_path": "data/jedi_archives/emails",
                    "holocron_sync": True
                }
            }

            with open(self.admin_config_file, 'w') as f:
                json.dump(default_config, f, indent=2)

            return default_config

        except Exception as e:
            self.logger.error(f"Error in load_admin_config: {e}", exc_info=True)
            raise
    def _initialize_gmail_api(self) -> bool:
        """Initialize Gmail API connection."""
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            import pickle

            SCOPES = [
                'https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.send',
                'https://www.googleapis.com/auth/gmail.modify'
            ]

            creds = None
            token_file = self.project_root / "config" / "gmail_token.pickle"
            credentials_file = self.project_root / "config" / "gmail_credentials.json"

            # Load existing token
            if token_file.exists():
                with open(token_file, 'rb') as token:
                    creds = pickle.load(token)

            # If no valid credentials, need to authenticate
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not credentials_file.exists():
                        logger.warning("Gmail credentials not found. Please set up OAuth2.")
                        return False
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(credentials_file), SCOPES)
                    creds = flow.run_local_server(port=0)

                # Save credentials
                token_file.parent.mkdir(parents=True, exist_ok=True)
                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)

            # Build Gmail service
            self.gmail_service = build('gmail', 'v1', credentials=creds)
            logger.info("✓ Gmail API initialized")
            return True

        except ImportError:
            logger.error("Google API libraries not installed")
            logger.info("Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
            return False
        except Exception as e:
            logger.error(f"Error initializing Gmail API: {e}")
            return False

    def search_emails(self, 
                     query: str,
                     max_results: int = 50,
                     label_ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Search Gmail with advanced query.

        Args:
            query: Gmail search query
            max_results: Maximum number of results
            label_ids: Optional label IDs to filter

        Returns:
            List of email message dictionaries
        """
        if not self.gmail_service:
            logger.error("Gmail API not initialized")
            return []

        try:
            results = self.gmail_service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results,
                labelIds=label_ids
            ).execute()

            messages = results.get('messages', [])
            logger.info(f"Found {len(messages)} emails for query: {query[:50]}...")

            email_data = []
            for msg in messages:
                email_info = self._get_email_details(msg['id'])
                if email_info:
                    email_data.append(email_info)

            return email_data

        except Exception as e:
            logger.error(f"Error searching emails: {e}")
            return []

    def _get_email_details(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get full email details."""
        try:
            message = self.gmail_service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            headers = message['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            from_addr = next((h['value'] for h in headers if h['name'] == 'From'), '')
            to_addr = next((h['value'] for h in headers if h['name'] == 'To'), '')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), '')

            body = self._extract_body(message['payload'])
            attachments = self._extract_attachments_info(message['payload'])

            return {
                'id': message_id,
                'thread_id': message.get('threadId', ''),
                'subject': subject,
                'from': from_addr,
                'to': to_addr,
                'date': date,
                'body': body,
                'attachments': attachments,
                'labels': message.get('labelIds', [])
            }
        except Exception as e:
            logger.error(f"Error getting email details: {e}")
            return None

    def _extract_body(self, payload: Dict) -> str:
        """Extract email body text."""
        body = ""

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data')
                    if data:
                        import base64
                        body += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        else:
            if payload.get('mimeType') == 'text/plain':
                data = payload['body'].get('data')
                if data:
                    import base64
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

        return body

    def _extract_attachments_info(self, payload: Dict) -> List[Dict[str, Any]]:
        """Extract attachment information."""
        attachments = []

        def process_part(part):
            if part.get('filename'):
                attachments.append({
                    'filename': part['filename'],
                    'mimeType': part.get('mimeType', ''),
                    'size': part.get('body', {}).get('size', 0),
                    'attachmentId': part.get('body', {}).get('attachmentId')
                })
            if 'parts' in part:
                for subpart in part['parts']:
                    process_part(subpart)

        if 'parts' in payload:
            for part in payload['parts']:
                process_part(part)
        else:
            process_part(payload)

        return attachments

    def categorize_email(self, email_data: Dict[str, Any]) -> EmailCategory:
        """
        Auto-categorize email using Admin SME rules.

        Args:
            email_data: Email data dictionary

        Returns:
            EmailCategory
        """
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()
        from_addr = email_data.get('from', '').lower()

        # Admin SME categorization rules
        if any(term in subject or term in body for term in ['invoice', 'payment', 'bill', 'financial', 'cost', 'budget']):
            return EmailCategory.FINANCIAL

        if any(term in subject or term in body for term in ['project', 'task', 'milestone', 'deadline']):
            return EmailCategory.PROJECT

        if any(term in subject or term in body for term in ['technical', 'code', 'bug', 'error', 'system']):
            return EmailCategory.TECHNICAL

        if any(term in subject or term in body for term in ['action required', 'urgent', 'please', 'need', 'request']):
            return EmailCategory.ACTION_REQUIRED

        if any(term in subject or term in body for term in ['reference', 'document', 'archive', 'record']):
            return EmailCategory.REFERENCE

        # Default to administrative
        return EmailCategory.ADMINISTRATIVE

    def determine_priority(self, email_data: Dict[str, Any]) -> EmailPriority:
        """
        Determine email priority using Admin SME rules.

        Args:
            email_data: Email data dictionary

        Returns:
            EmailPriority
        """
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()

        # Critical keywords
        if any(term in subject or term in body for term in ['urgent', 'critical', 'emergency', 'asap', 'immediate']):
            return EmailPriority.CRITICAL

        # High priority keywords
        if any(term in subject or term in body for term in ['important', 'priority', 'attention', 'deadline']):
            return EmailPriority.HIGH

        # Low priority keywords
        if any(term in subject or term in body for term in ['newsletter', 'notification', 'update', 'digest']):
            return EmailPriority.LOW

        # Default to medium
        return EmailPriority.MEDIUM

    def save_to_holocron(self, email_metadata: EmailMetadata, email_data: Dict[str, Any]) -> str:
        try:
            """
            Save email to Holocron/Jedi Archives.

            Args:
                email_metadata: Email metadata
                email_data: Full email data

            Returns:
                Holocron reference path
            """
            # Create Holocron entry
            holocron_entry = {
                "type": "email",
                "email_id": email_metadata.email_id,
                "thread_id": email_metadata.thread_id,
                "subject": email_metadata.subject,
                "from": email_metadata.from_address,
                "to": email_metadata.to_address,
                "date": email_metadata.date,
                "category": email_metadata.category.value,
                "priority": email_metadata.priority.value,
                "tags": email_metadata.tags,
                "body": email_data.get('body', ''),
                "attachments": email_data.get('attachments', []),
                "admin_notes": email_metadata.admin_notes,
                "action_required": email_metadata.action_required,
                "follow_up_date": email_metadata.follow_up_date,
                "archived_at": datetime.now().isoformat(),
                "jedi_archive_path": None
            }

            # Save to Holocron
            category_dir = self.holocron_dir / "emails" / email_metadata.category.value
            category_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"email_{email_metadata.email_id}_{timestamp}.json"
            holocron_path = category_dir / filename

            with open(holocron_path, 'w', encoding='utf-8') as f:
                json.dump(holocron_entry, f, indent=2, ensure_ascii=False)

            # Also save to Jedi Archives
            jedi_archive_path = self.jedi_archives_dir / "emails" / email_metadata.category.value / filename
            jedi_archive_path.parent.mkdir(parents=True, exist_ok=True)

            with open(jedi_archive_path, 'w', encoding='utf-8') as f:
                json.dump(holocron_entry, f, indent=2, ensure_ascii=False)

            logger.info(f"✓ Saved email to Holocron: {holocron_path}")
            logger.info(f"✓ Saved email to Jedi Archives: {jedi_archive_path}")

            return str(holocron_path)

        except Exception as e:
            self.logger.error(f"Error in save_to_holocron: {e}", exc_info=True)
            raise
    def process_incoming_email(self, email_data: Dict[str, Any]) -> EmailMetadata:
        try:
            """
            Process incoming email through secretarial workflow.

            Args:
                email_data: Email data dictionary

            Returns:
                EmailMetadata object
            """
            # Auto-categorize
            category = self.categorize_email(email_data)
            priority = self.determine_priority(email_data)

            # Create metadata
            metadata = EmailMetadata(
                email_id=email_data['id'],
                thread_id=email_data.get('thread_id', ''),
                subject=email_data.get('subject', ''),
                from_address=email_data.get('from', ''),
                to_address=email_data.get('to', ''),
                date=email_data.get('date', ''),
                category=category,
                priority=priority,
                tags=self._extract_tags(email_data),
                action_required=priority in [EmailPriority.CRITICAL, EmailPriority.HIGH]
            )

            # Save metadata
            metadata_file = self.metadata_dir / f"email_{metadata.email_id}.json"
            with open(metadata_file, 'w') as f:
                json.dump(asdict(metadata), f, indent=2, default=str)

            # Save to Holocron if configured
            config = self.load_admin_config()
            if config.get('secretarial_workflows', {}).get('incoming', {}).get('holocron_sync', False):
                holocron_path = self.save_to_holocron(metadata, email_data)
                metadata.holocron_reference = holocron_path
                metadata.jedi_archive_path = holocron_path.replace('holocron', 'jedi_archives')

            logger.info(f"✓ Processed incoming email: {metadata.subject[:50]}")
            return metadata

        except Exception as e:
            self.logger.error(f"Error in process_incoming_email: {e}", exc_info=True)
            raise
    def _extract_tags(self, email_data: Dict[str, Any]) -> List[str]:
        """Extract tags from email content."""
        tags = []
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()

        # Extract common tags
        tag_patterns = {
            '#JARVIS': ['jarvis', 'automation'],
            '#LUMINA': ['lumina', 'project'],
            '#HOLOCRON': ['holocron', 'archive'],
            '#JEDIARCHIVES': ['jedi', 'archives'],
            '#ADMIN': ['admin', 'administrative'],
            '#FINANCIAL': ['financial', 'invoice', 'payment'],
            '#TECHNICAL': ['technical', 'code', 'system'],
        }

        for tag, keywords in tag_patterns.items():
            if any(keyword in subject or keyword in body for keyword in keywords):
                tags.append(tag)

        return tags

    def send_email(self, 
                   to: str,
                   subject: str,
                   body: str,
                   attachments: Optional[List[Path]] = None) -> Dict[str, Any]:
        """
        Send email through Admin SME workflow.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            attachments: Optional list of attachment file paths

        Returns:
            Send result dictionary
        """
        if not self.gmail_service:
            logger.error("Gmail API not initialized")
            return {"success": False, "error": "Gmail API not initialized"}

        try:
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            from email.mime.base import MIMEBase
            from email import encoders
            import base64

            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            message.attach(MIMEText(body, 'plain'))

            # Add attachments
            if attachments:
                for file_path in attachments:
                    if Path(file_path).exists():
                        with open(file_path, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {Path(file_path).name}'
                            )
                            message.attach(part)

            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            # Send
            send_message = self.gmail_service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()

            logger.info(f"✓ Sent email to {to}: {subject[:50]}")

            # Track sent email
            self._track_sent_email(to, subject, send_message['id'])

            return {
                "success": True,
                "message_id": send_message['id'],
                "thread_id": send_message.get('threadId', '')
            }

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {"success": False, "error": str(e)}

    def _track_sent_email(self, to: str, subject: str, message_id: str) -> None:
        try:
            """Track sent email for follow-up."""
            sent_dir = self.data_dir / "sent_emails"
            sent_dir.mkdir(parents=True, exist_ok=True)

            tracking_data = {
                "message_id": message_id,
                "to": to,
                "subject": subject,
                "sent_at": datetime.now().isoformat(),
                "follow_up_required": False,
                "follow_up_date": None
            }

            tracking_file = sent_dir / f"sent_{message_id}.json"
            with open(tracking_file, 'w') as f:
                json.dump(tracking_data, f, indent=2)


        except Exception as e:
            self.logger.error(f"Error in _track_sent_email: {e}", exc_info=True)
            raise
def main():
    """Main function for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(description="LUMINA Gmail Integration")
    parser.add_argument("--project-root", type=Path,
                       default=Path(__file__).parent.parent.parent,
                       help="Project root directory")
    parser.add_argument("--search", type=str,
                       help="Search query for Gmail")
    parser.add_argument("--send", action="store_true",
                       help="Send email mode")
    parser.add_argument("--to", type=str,
                       help="Recipient email address")
    parser.add_argument("--subject", type=str,
                       help="Email subject")
    parser.add_argument("--body", type=str,
                       help="Email body")
    parser.add_argument("--process-incoming", action="store_true",
                       help="Process incoming emails")

    args = parser.parse_args()

    integration = LUMINAGmailIntegration(args.project_root)

    if args.search:
        emails = integration.search_emails(args.search)
        print(f"\n✓ Found {len(emails)} email(s)")
        for email in emails[:10]:
            print(f"  - {email.get('subject', 'No subject')[:60]}")

    if args.send and args.to and args.subject and args.body:
        result = integration.send_email(args.to, args.subject, args.body)
        if result.get("success"):
            print(f"✓ Email sent: {result['message_id']}")
        else:
            print(f"✗ Error: {result.get('error')}")

    if args.process_incoming:
        # Process recent emails
        emails = integration.search_emails("is:unread", max_results=20)
        for email in emails:
            metadata = integration.process_incoming_email(email)
            print(f"✓ Processed: {metadata.subject[:50]} - {metadata.category.value}")


if __name__ == "__main__":


    main()