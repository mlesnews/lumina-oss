"""
Gmail IMAP Manager
Manages and organizes Gmail using IMAP with Azure Key Vault credentials
- Organize emails
- Cite/reference emails
- Archive emails (6 months to 1 year)
- Purge older emails

#JARVIS #LUMINA #GMAIL #IMAP #EMAIL_MANAGEMENT
"""
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.azure_service_bus_integration import AzureKeyVaultClient
    AZURE_VAULT_AVAILABLE = True
except ImportError:
    AZURE_VAULT_AVAILABLE = False

try:
    import imaplib
    IMAP_AVAILABLE = True
except ImportError:
    IMAP_AVAILABLE = False

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("GmailIMAPManager")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("GmailIMAPManager")


class GmailIMAPManager:
    """Manage Gmail via IMAP using Azure Key Vault credentials."""

    def __init__(self, project_root: Path):
        """Initialize Gmail IMAP Manager."""
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "gmail_management"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.citations_dir = self.data_dir / "citations"
        self.citations_dir.mkdir(parents=True, exist_ok=True)

        self.archive_dir = self.data_dir / "archive"
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        self.email_account = None
        self.email_password = None
        self.imap_connection = None

        # Load credentials from Azure Key Vault
        self._load_credentials_from_vault()

    def _load_credentials_from_vault(self) -> bool:
        """Load Gmail credentials from Azure Key Vault."""
        if not AZURE_VAULT_AVAILABLE:
            logger.error("Azure Key Vault SDK not available")
            return False

        try:
            vault_url = os.getenv("AZURE_KEY_VAULT_URL", "https://jarvis-lumina.vault.azure.net/")
            vault_client = AzureKeyVaultClient(vault_url=vault_url)

            # Get email and app password
            self.email_account = vault_client.get_secret("login-account-gmail-ceo-gmail-email")
            self.email_password = vault_client.get_secret("login-account-gmail-ceo-gmail-app-password")

            logger.info(f"✅ Loaded Gmail credentials from Azure Key Vault")
            logger.info(f"   Email: {self.email_account}")
            return True

        except Exception as e:
            logger.error(f"Failed to load credentials from Azure Key Vault: {e}")
            return False

    def connect(self) -> bool:
        """Connect to Gmail via IMAP."""
        if not IMAP_AVAILABLE:
            logger.error("imaplib not available (should be in Python stdlib)")
            return False

        if not self.email_account or not self.email_password:
            logger.error("Gmail credentials not loaded")
            return False

        try:
            # Gmail IMAP settings
            imap_server = "imap.gmail.com"
            imap_port = 993

            logger.info(f"Connecting to {imap_server}:{imap_port}...")
            self.imap_connection = imaplib.IMAP4_SSL(imap_server, imap_port)
            self.imap_connection.login(self.email_account, self.email_password)
            logger.info("✅ Connected to Gmail via IMAP")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Gmail: {e}")
            return False

    def disconnect(self):
        """Disconnect from Gmail."""
        if self.imap_connection:
            try:
                self.imap_connection.logout()
                logger.info("Disconnected from Gmail")
            except:
                pass
            self.imap_connection = None

    def get_email_ids(self, folder: str = "INBOX", days_back: int = 365, search_criteria: Optional[str] = None) -> List[int]:
        """Get email IDs from folder."""
        if not self.imap_connection:
            if not self.connect():
                return []

        try:
            self.imap_connection.select(folder)

            # Calculate date threshold
            date_threshold = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")

            # Build search criteria
            if search_criteria:
                search_query = f'({search_criteria}) SINCE {date_threshold}'
            else:
                search_query = f'SINCE {date_threshold}'

            status, messages = self.imap_connection.search(None, search_query)

            if status == "OK":
                email_ids = [int(msg_id) for msg_id in messages[0].split()]
                logger.info(f"Found {len(email_ids)} emails in {folder} (last {days_back} days)")
                return email_ids
            else:
                logger.warning(f"Search failed: {status}")
                return []

        except Exception as e:
            logger.error(f"Error getting email IDs: {e}")
            return []

    def fetch_email(self, email_id: int) -> Optional[Dict[str, Any]]:
        """Fetch email by ID."""
        if not self.imap_connection:
            return None

        try:
            status, msg_data = self.imap_connection.fetch(str(email_id), "(RFC822)")

            if status != "OK":
                return None

            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)

            # Parse email
            subject = self._decode_header(email_message["Subject"])
            from_addr = self._decode_header(email_message["From"])
            to_addr = self._decode_header(email_message["To"])
            date_str = email_message["Date"]
            date_obj = parsedate_to_datetime(date_str) if date_str else None

            # Get body
            body = self._get_email_body(email_message)

            return {
                "id": email_id,
                "subject": subject,
                "from": from_addr,
                "to": to_addr,
                "date": date_obj.isoformat() if date_obj else date_str,
                "body": body,
                "raw": email_message
            }

        except Exception as e:
            logger.error(f"Error fetching email {email_id}: {e}")
            return None

    def _decode_header(self, header_value: Optional[str]) -> str:
        """Decode email header."""
        if not header_value:
            return ""

        decoded_parts = decode_header(header_value)
        decoded_string = ""
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_string += part.decode(encoding or "utf-8", errors="ignore")
            else:
                decoded_string += part

        return decoded_string

    def _get_email_body(self, email_message) -> str:
        """Extract email body."""
        body = ""

        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        try:
                            body = payload.decode("utf-8", errors="ignore")
                            break
                        except:
                            pass
        else:
            payload = email_message.get_payload(decode=True)
            if payload:
                try:
                    body = payload.decode("utf-8", errors="ignore")
                except:
                    pass

        return body

    def create_citation(self, email_data: Dict[str, Any]) -> str:
        try:
            """Create citation/reference for email."""
            citation_id = f"email_{email_data['id']}_{datetime.now().strftime('%Y%m%d')}"

            citation = {
                "citation_id": citation_id,
                "email_id": email_data["id"],
                "subject": email_data["subject"],
                "from": email_data["from"],
                "date": email_data["date"],
                "citation_text": f"[{citation_id}] {email_data['subject']} - {email_data['from']} ({email_data['date']})",
                "email_data": email_data
            }

            # Save citation
            citation_file = self.citations_dir / f"{citation_id}.json"
            with open(citation_file, 'w', encoding='utf-8') as f:
                json.dump(citation, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"Created citation: {citation_id}")
            return citation_id

        except Exception as e:
            self.logger.error(f"Error in create_citation: {e}", exc_info=True)
            raise
    def organize_emails(self, days_back: int = 365) -> Dict[str, Any]:
        """Organize emails from the past N days."""
        logger.info(f"Organizing emails from the past {days_back} days...")

        email_ids = self.get_email_ids(days_back=days_back)

        organized = {
            "total_emails": len(email_ids),
            "by_sender": {},
            "by_date": {},
            "citations": [],
            "archive_candidates": []
        }

        cutoff_date = datetime.now() - timedelta(days=180)  # 6 months for archive

        for email_id in email_ids[:100]:  # Limit to 100 for now
            email_data = self.fetch_email(email_id)
            if not email_data:
                continue

            # Organize by sender
            sender = email_data["from"]
            if sender not in organized["by_sender"]:
                organized["by_sender"][sender] = []
            organized["by_sender"][sender].append({
                "id": email_data["id"],
                "subject": email_data["subject"],
                "date": email_data["date"]
            })

            # Organize by date
            try:
                date_obj = datetime.fromisoformat(email_data["date"].replace('Z', '+00:00'))
                date_key = date_obj.strftime("%Y-%m")
                if date_key not in organized["by_date"]:
                    organized["by_date"][date_key] = 0
                organized["by_date"][date_key] += 1

                # Check if should be archived
                if date_obj < cutoff_date:
                    organized["archive_candidates"].append(email_data["id"])
            except:
                pass

            # Create citation
            citation_id = self.create_citation(email_data)
            organized["citations"].append(citation_id)

        # Save organization data
        org_file = self.data_dir / f"organization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(org_file, 'w', encoding='utf-8') as f:
            json.dump(organized, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"✅ Organized {organized['total_emails']} emails")
        logger.info(f"   Citations created: {len(organized['citations'])}")
        logger.info(f"   Archive candidates: {len(organized['archive_candidates'])}")

        return organized

    def archive_emails(self, email_ids: List[int], archive_name: Optional[str] = None) -> bool:
        try:
            """Archive emails (move to archive folder or export)."""
            if archive_name is None:
                archive_name = f"archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            archive_data = {
                "archive_name": archive_name,
                "created_at": datetime.now().isoformat(),
                "email_count": len(email_ids),
                "emails": []
            }

            logger.info(f"Archiving {len(email_ids)} emails...")

            for email_id in email_ids:
                email_data = self.fetch_email(email_id)
                if email_data:
                    archive_data["emails"].append(email_data)

            # Save archive
            archive_file = self.archive_dir / f"{archive_name}.json"
            with open(archive_file, 'w', encoding='utf-8') as f:
                json.dump(archive_data, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"✅ Archived {len(archive_data['emails'])} emails to {archive_file}")
            return True


        except Exception as e:
            self.logger.error(f"Error in archive_emails: {e}", exc_info=True)
            raise
def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Gmail IMAP Manager")
    parser.add_argument("--project-root", type=Path, default=project_root)
    parser.add_argument("--organize", action="store_true", help="Organize emails")
    parser.add_argument("--days", type=int, default=365, help="Days to look back")
    parser.add_argument("--archive", type=str, help="Archive emails (comma-separated IDs or 'old' for candidates)")

    args = parser.parse_args()

    manager = GmailIMAPManager(args.project_root)

    try:
        if not manager.connect():
            print("❌ Failed to connect to Gmail")
            return

        if args.organize:
            print(f"\n📧 Organizing emails (last {args.days} days)...")
            organized = manager.organize_emails(days_back=args.days)
            print(f"\n✅ Organization complete:")
            print(f"   Total emails: {organized['total_emails']}")
            print(f"   Citations: {len(organized['citations'])}")
            print(f"   Archive candidates: {len(organized['archive_candidates'])}")

        elif args.archive:
            if args.archive.lower() == "old":
                # Archive old emails
                organized = manager.organize_emails(days_back=args.days)
                if organized['archive_candidates']:
                    manager.archive_emails(organized['archive_candidates'])
                else:
                    print("No emails to archive")
            else:
                # Archive specific IDs
                email_ids = [int(id.strip()) for id in args.archive.split(",")]
                manager.archive_emails(email_ids)

        else:
            parser.print_help()

    finally:
        manager.disconnect()


if __name__ == "__main__":


    main()