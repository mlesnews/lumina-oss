"""
Email Management System
Manage, organize, SYPHON, and purge emails from Gmail account

Features:
- Access Gmail via N8N/IMAP (already configured)
- SYPHON intelligence extraction from all emails
- Organize and categorize emails
- Process last 6-12 months of emails
- Purge older emails

#JARVIS #LUMINA #EMAIL #SYPHON #N8N #IMAP
"""
import sys
import json
import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
import ssl

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("EmailManagementSystem")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("EmailManagementSystem")

try:
    from azure_service_bus_integration import AzureKeyVaultClient
    KEY_VAULT_AVAILABLE = True
except ImportError:
    KEY_VAULT_AVAILABLE = False
    logger.warning("Azure Key Vault not available")

try:
    from nas_azure_vault_integration import NASAzureVaultIntegration
    NAS_INTEGRATION_AVAILABLE = True
except ImportError:
    NAS_INTEGRATION_AVAILABLE = False
    logger.warning("NAS integration not available")

try:
    from syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    logger.warning("SYPHON system not available")


@dataclass
class EmailMessage:
    """Email message data"""
    message_id: str
    email_id: str
    subject: str
    body: str
    from_address: str
    to_address: str
    date: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if data.get("date"):
            data["date"] = data["date"].isoformat()
        return data


class EmailManagementSystem:
    """
    Email Management System

    Manages, organizes, SYPHONs, and purges emails from Gmail account.
    Uses existing N8N/IMAP setup.
    """

    def __init__(self, project_root: Path):
        """Initialize email management system."""
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "email_management"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.syphon_dir = self.project_root / "data" / "syphon" / "email_intelligence"
        self.syphon_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Azure Key Vault for credentials
        self.vault_client = None
        if KEY_VAULT_AVAILABLE:
            try:
                import os
                vault_url = os.getenv("AZURE_KEY_VAULT_URL", "https://jarvis-lumina.vault.azure.net/")
                self.vault_client = AzureKeyVaultClient(vault_url=vault_url)
                logger.info("✅ Azure Key Vault initialized")
            except Exception as e:
                logger.warning(f"Azure Key Vault not available: {e}")

        # Initialize NAS integration for company email hub
        self.nas_integration = None
        if NAS_INTEGRATION_AVAILABLE:
            try:
                self.nas_integration = NASAzureVaultIntegration()
                logger.info("✅ NAS integration initialized (Company Email Hub)")
            except Exception as e:
                logger.warning(f"NAS integration not available: {e}")

        # NAS email hub paths
        self.nas_email_hub_base = "/volume1/backups/MATT_Backups/company_email_hub"
        self.nas_email_hub_secure = f"{self.nas_email_hub_base}/secure"
        self.nas_email_hub_unsecure = f"{self.nas_email_hub_base}/unsecure"

        # Get Gmail credentials from Key Vault
        self.gmail_email = None
        self.gmail_password = None
        self._load_gmail_credentials()

        # Initialize SYPHON
        self.syphon = None
        if SYPHON_AVAILABLE:
            try:
                config = SYPHONConfig(
                    project_root=self.project_root,
                    subscription_tier=SubscriptionTier.PREMIUM,
                    enable_self_healing=True
                )
                self.syphon = SYPHONSystem(config)
                logger.info("✅ SYPHON system initialized")
            except Exception as e:
                logger.warning(f"SYPHON not available: {e}")

        # IMAP settings
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993

        logger.info("✅ Email Management System initialized")

    def _load_gmail_credentials(self) -> None:
        """Load Gmail credentials from Azure Key Vault."""
        if not self.vault_client:
            logger.warning("Key Vault not available - cannot load credentials")
            return

        try:
            self.gmail_email = self.vault_client.get_secret("login-account-gmail-ceo-gmail-email")
            self.gmail_password = self.vault_client.get_secret("login-account-gmail-ceo-gmail-app-password")
            logger.info(f"✅ Gmail credentials loaded for: {self.gmail_email}")
        except Exception as e:
            logger.error(f"Failed to load Gmail credentials: {e}")

    def connect_imap(self) -> Optional[imaplib.IMAP4_SSL]:
        """Connect to Gmail via IMAP."""
        if not self.gmail_email or not self.gmail_password:
            logger.error("Gmail credentials not available")
            return None

        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.gmail_email, self.gmail_password)
            logger.info("✅ Connected to Gmail via IMAP")
            return mail
        except Exception as e:
            logger.error(f"Failed to connect to Gmail: {e}")
            return None

    def fetch_emails(
        self,
        days_back: int = 180,
        folder: str = "INBOX",
        limit: Optional[int] = None
    ) -> List[EmailMessage]:
        """
        Fetch emails from Gmail.

        Args:
            days_back: Number of days to look back (default: 180 = ~6 months)
            folder: Mailbox folder (default: INBOX)
            limit: Maximum number of emails to fetch (None = all)

        Returns:
            List of EmailMessage objects
        """
        mail = self.connect_imap()
        if not mail:
            return []

        emails = []

        try:
            # Select folder
            status, messages = mail.select(folder)
            if status != "OK":
                logger.error(f"Failed to select folder: {folder}")
                mail.close()
                mail.logout()
                return []

            # Calculate date threshold
            cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")
            search_query = f'(SINCE {cutoff_date})'

            logger.info(f"Searching for emails since {cutoff_date} ({days_back} days back)")

            # Search for emails
            status, message_ids = mail.search(None, search_query)
            if status != "OK":
                logger.error("Failed to search emails")
                mail.close()
                mail.logout()
                return []

            message_id_list = message_ids[0].split()

            # Apply limit if specified
            if limit:
                message_id_list = message_id_list[-limit:]  # Get most recent

            logger.info(f"Found {len(message_id_list)} emails to process")

            # Fetch emails
            for i, msg_id in enumerate(message_id_list):
                try:
                    status, msg_data = mail.fetch(msg_id, "(RFC822)")
                    if status != "OK":
                        continue

                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)

                    # Extract email data
                    subject = self._decode_header(email_message["Subject"] or "")
                    from_addr = self._decode_header(email_message["From"] or "")
                    to_addr = self._decode_header(email_message["To"] or "")

                    # Parse date
                    date_str = email_message["Date"]
                    email_date = None
                    if date_str:
                        try:
                            email_date = parsedate_to_datetime(date_str)
                        except:
                            pass

                    # Extract body
                    body = self._extract_body(email_message)

                    # Create EmailMessage
                    email_obj = EmailMessage(
                        message_id=msg_id.decode(),
                        email_id=email_message.get("Message-ID", ""),
                        subject=subject,
                        body=body,
                        from_address=from_addr,
                        to_address=to_addr,
                        date=email_date,
                        metadata={
                            "folder": folder,
                            "size": len(email_body)
                        }
                    )

                    emails.append(email_obj)

                    if (i + 1) % 100 == 0:
                        logger.info(f"Processed {i + 1}/{len(message_id_list)} emails")

                except Exception as e:
                    logger.error(f"Error processing email {msg_id}: {e}")
                    continue

            mail.close()
            mail.logout()

            logger.info(f"✅ Fetched {len(emails)} emails")
            return emails

        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            try:
                mail.close()
                mail.logout()
            except:
                pass
            return []

    def _decode_header(self, header: str) -> str:
        """Decode email header."""
        try:
            decoded_parts = decode_header(header)
            decoded_string = ""
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    if encoding:
                        decoded_string += part.decode(encoding)
                    else:
                        decoded_string += part.decode('utf-8', errors='ignore')
                else:
                    decoded_string += part
            return decoded_string
        except:
            return header

    def _extract_body(self, email_message: email.message.EmailMessage) -> str:
        """Extract text body from email."""
        body = ""

        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body += payload.decode('utf-8', errors='ignore')
                    except:
                        pass
        else:
            try:
                payload = email_message.get_payload(decode=True)
                if payload:
                    body = payload.decode('utf-8', errors='ignore')
            except:
                pass

        return body

    def syphon_emails(self, emails: List[EmailMessage]) -> Dict[str, Any]:
        """
        SYPHON intelligence from emails.

        Args:
            emails: List of EmailMessage objects

        Returns:
            Dictionary with SYPHON results
        """
        if not self.syphon:
            logger.warning("SYPHON not available - skipping extraction")
            return {"success": False, "error": "SYPHON not available"}

        logger.info(f"@SYPHON: Extracting intelligence from {len(emails)} emails")

        results = {
            "total_emails": len(emails),
            "syphoned": 0,
            "failed": 0,
            "extracted_data": []
        }

        for i, email_msg in enumerate(emails):
            try:
                # SYPHON extract intelligence
                result = self.syphon.extract_email(
                    email_id=email_msg.email_id or email_msg.message_id,
                    subject=email_msg.subject,
                    body=email_msg.body,
                    from_address=email_msg.from_address,
                    to_address=email_msg.to_address,
                    metadata=email_msg.metadata
                )

                if result.success and result.data:
                    results["syphoned"] += 1
                    results["extracted_data"].append(result.data.to_dict())

                    if (i + 1) % 50 == 0:
                        logger.info(f"@SYPHON: Processed {i + 1}/{len(emails)} emails")
                else:
                    results["failed"] += 1

            except Exception as e:
                logger.error(f"Error SYPHONing email {email_msg.message_id}: {e}")
                results["failed"] += 1

        # Save SYPHON results
        syphon_file = self.syphon_dir / f"email_syphon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(syphon_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"✅ @SYPHON: Extracted intelligence from {results['syphoned']}/{results['total_emails']} emails")
        logger.info(f"   Results saved to: {syphon_file}")

        return results

    def _determine_email_security(self, email_msg: EmailMessage) -> str:
        """
        Determine if email is from secure or unsecure source.

        Args:
            email_msg: EmailMessage object

        Returns:
            "secure" or "unsecure"
        """
        from_addr_lower = email_msg.from_address.lower()

        # Secure domains/patterns (Gmail, Outlook, enterprise domains, etc.)
        secure_patterns = [
            "@gmail.com", "@outlook.com", "@microsoft.com", "@office365.com",
            "@protonmail.com", "@proton.me", "@company.", "@corp.", "@enterprise."
        ]

        # Check if from secure source
        for pattern in secure_patterns:
            if pattern in from_addr_lower:
                return "secure"

        # Default to unsecure for unknown/legacy sources
        return "unsecure"

    def organize_emails(self, emails: List[EmailMessage]) -> Dict[str, List[EmailMessage]]:
        """
        Organize emails into categories.

        Args:
            emails: List of EmailMessage objects

        Returns:
            Dictionary with categorized emails
        """
        categories = {
            "important": [],
            "action_required": [],
            "financial": [],
            "technical": [],
            "personal": [],
            "other": []
        }

        for email_msg in emails:
            subject_lower = email_msg.subject.lower()
            body_lower = email_msg.body.lower()

            # Categorize
            if any(word in subject_lower or word in body_lower for word in ["urgent", "important", "critical", "asap"]):
                categories["important"].append(email_msg)
            elif any(word in subject_lower or word in body_lower for word in ["action", "todo", "task", "required", "please"]):
                categories["action_required"].append(email_msg)
            elif any(word in subject_lower or word in body_lower for word in ["invoice", "payment", "bill", "financial", "money", "$"]):
                categories["financial"].append(email_msg)
            elif any(word in subject_lower or word in body_lower for word in ["code", "error", "bug", "technical", "api", "system"]):
                categories["technical"].append(email_msg)
            elif any(word in subject_lower or word in body_lower for word in ["family", "friend", "personal"]):
                categories["personal"].append(email_msg)
            else:
                categories["other"].append(email_msg)

        logger.info(f"✅ Organized {len(emails)} emails into categories:")
        for category, emails_list in categories.items():
            logger.info(f"   {category}: {len(emails_list)} emails")

        # Also organize by security level
        secure_emails = [e for e in emails if self._determine_email_security(e) == "secure"]
        unsecure_emails = [e for e in emails if self._determine_email_security(e) == "unsecure"]

        categories["_security"] = {
            "secure": len(secure_emails),
            "unsecure": len(unsecure_emails)
        }

        logger.info(f"   Security: {len(secure_emails)} secure, {len(unsecure_emails)} unsecure")

        return categories

    def upload_to_nas_email_hub(
        self,
        emails: List[EmailMessage],
        syphon_results: Optional[Dict[str, Any]] = None,
        organized: Optional[Dict[str, List[EmailMessage]]] = None
    ) -> Dict[str, Any]:
        """
        Upload processed emails to NAS Company Email Hub.
        Organizes by secure/unsecure and categories.

        Args:
            emails: List of processed emails
            syphon_results: SYPHON extraction results
            organized: Organized email categories

        Returns:
            Dictionary with upload results
        """
        if not self.nas_integration:
            logger.warning("NAS integration not available - skipping upload")
            return {"success": False, "error": "NAS integration not available"}

        logger.info("="*80)
        logger.info("UPLOADING TO NAS COMPANY EMAIL HUB")
        logger.info("="*80)

        try:
            # Create base directory structure
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            # Upload structure:
            # /company_email_hub/
            #   /secure/
            #     /{timestamp}/
            #       /categories/
            #       /syphon/
            #   /unsecure/
            #     /{timestamp}/
            #       /categories/
            #       /syphon/

            upload_results = {
                "success": True,
                "timestamp": timestamp,
                "secure": {"uploaded": 0, "failed": 0},
                "unsecure": {"uploaded": 0, "failed": 0},
                "files_uploaded": []
            }

            # Separate emails by security
            secure_emails = []
            unsecure_emails = []
            for email_msg in emails:
                security = self._determine_email_security(email_msg)
                if security == "secure":
                    secure_emails.append(email_msg)
                else:
                    unsecure_emails.append(email_msg)

            # Upload secure emails
            if secure_emails:
                logger.info(f"Uploading {len(secure_emails)} secure emails...")
                secure_path = f"{self.nas_email_hub_secure}/{timestamp}"
                result = self._upload_email_batch(secure_emails, secure_path, "secure", organized)
                upload_results["secure"] = result

            # Upload unsecure emails
            if unsecure_emails:
                logger.info(f"Uploading {len(unsecure_emails)} unsecure emails...")
                unsecure_path = f"{self.nas_email_hub_unsecure}/{timestamp}"
                result = self._upload_email_batch(unsecure_emails, unsecure_path, "unsecure", organized)
                upload_results["unsecure"] = result

            # Upload SYPHON results
            if syphon_results:
                logger.info("Uploading SYPHON results...")
                syphon_file = self.data_dir / f"syphon_results_{timestamp}.json"
                with open(syphon_file, 'w', encoding='utf-8') as f:
                    json.dump(syphon_results, f, indent=2, ensure_ascii=False, default=str)

                # Upload to both secure and unsecure (shared intelligence)
                for security_type in ["secure", "unsecure"]:
                    base_path = self.nas_email_hub_secure if security_type == "secure" else self.nas_email_hub_unsecure
                    remote_path = f"{base_path}/{timestamp}/syphon/syphon_results_{timestamp}.json"
                    if self.nas_integration.upload_file(syphon_file, remote_path):
                        upload_results["files_uploaded"].append(remote_path)
                        logger.info(f"✅ Uploaded SYPHON results to {security_type}")

            logger.info("✅ Upload to NAS Company Email Hub complete")
            return upload_results

        except Exception as e:
            logger.error(f"Error uploading to NAS: {e}")
            return {"success": False, "error": str(e)}

    def _upload_email_batch(
        self,
        emails: List[EmailMessage],
        base_path: str,
        security_type: str,
        organized: Optional[Dict[str, List[EmailMessage]]] = None
    ) -> Dict[str, int]:
        """Upload batch of emails to NAS, organized by category."""
        uploaded = 0
        failed = 0

        try:
            # Create directory structure
            self.nas_integration.create_folder(base_path)
            self.nas_integration.create_folder(f"{base_path}/categories")
            self.nas_integration.create_folder(f"{base_path}/raw")

            # Save raw emails JSON
            raw_file = self.data_dir / f"emails_{security_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            emails_data = [e.to_dict() for e in emails]
            with open(raw_file, 'w', encoding='utf-8') as f:
                json.dump(emails_data, f, indent=2, ensure_ascii=False, default=str)

            remote_raw = f"{base_path}/raw/emails_{security_type}.json"
            if self.nas_integration.upload_file(raw_file, remote_raw):
                uploaded += 1
                logger.info(f"✅ Uploaded {len(emails)} {security_type} emails (raw)")
            else:
                failed += 1

            # Upload by category if organized
            if organized:
                for category, category_emails in organized.items():
                    if category.startswith("_"):  # Skip metadata keys
                        continue

                    # Filter emails in this category
                    category_emails_list = [e for e in emails if e in category_emails]
                    if not category_emails_list:
                        continue

                    category_file = self.data_dir / f"emails_{security_type}_{category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    category_data = [e.to_dict() for e in category_emails_list]
                    with open(category_file, 'w', encoding='utf-8') as f:
                        json.dump(category_data, f, indent=2, ensure_ascii=False, default=str)

                    remote_category = f"{base_path}/categories/{category}.json"
                    if self.nas_integration.upload_file(category_file, remote_category):
                        uploaded += 1
                        logger.info(f"✅ Uploaded {len(category_emails_list)} {security_type} emails ({category})")
                    else:
                        failed += 1

            return {"uploaded": uploaded, "failed": failed}

        except Exception as e:
            logger.error(f"Error uploading {security_type} batch: {e}")
            return {"uploaded": uploaded, "failed": failed + len(emails)}

    def purge_old_emails(
        self,
        days_old: int = 365,
        folder: str = "INBOX",
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Purge emails older than specified days.

        Args:
            days_old: Delete emails older than this many days
            folder: Mailbox folder
            dry_run: If True, only report what would be deleted

        Returns:
            Dictionary with purge results
        """
        mail = self.connect_imap()
        if not mail:
            return {"success": False, "error": "Failed to connect"}

        try:
            status, messages = mail.select(folder)
            if status != "OK":
                return {"success": False, "error": f"Failed to select folder: {folder}"}

            # Calculate cutoff date
            cutoff_date = (datetime.now() - timedelta(days=days_old)).strftime("%d-%b-%Y")
            search_query = f'(BEFORE {cutoff_date})'

            logger.info(f"Searching for emails before {cutoff_date} ({days_old} days old)")

            status, message_ids = mail.search(None, search_query)
            if status != "OK":
                return {"success": False, "error": "Failed to search"}

            message_id_list = message_ids[0].split()
            count = len(message_id_list)

            result = {
                "success": True,
                "dry_run": dry_run,
                "emails_found": count,
                "cutoff_date": cutoff_date,
                "deleted": 0 if dry_run else None
            }

            if dry_run:
                logger.info(f"DRY RUN: Would delete {count} emails older than {days_old} days")
                result["deleted"] = 0
            else:
                logger.warning(f"DELETING {count} emails older than {days_old} days...")
                for msg_id in message_id_list:
                    try:
                        mail.store(msg_id, '+FLAGS', '\\Deleted')
                    except Exception as e:
                        logger.error(f"Error marking email {msg_id} for deletion: {e}")

                mail.expunge()
                result["deleted"] = count
                logger.info(f"✅ Deleted {count} emails")

            mail.close()
            mail.logout()

            return result

        except Exception as e:
            logger.error(f"Error purging emails: {e}")
            try:
                mail.close()
                mail.logout()
            except:
                pass
            return {"success": False, "error": str(e)}

    def process_emails(
        self,
        days_back: int = 180,
        syphon_enabled: bool = True,
        organize_enabled: bool = True
    ) -> Dict[str, Any]:
        """
        Main method to process emails.

        Args:
            days_back: Number of days to process (default: 180 = ~6 months)
            syphon_enabled: Enable SYPHON intelligence extraction
            organize_enabled: Enable email organization

        Returns:
            Dictionary with processing results
        """
        logger.info("="*80)
        logger.info("EMAIL MANAGEMENT SYSTEM - Processing Emails")
        logger.info("="*80)
        logger.info(f"Processing last {days_back} days of emails")
        logger.info("")

        # Fetch emails
        emails = self.fetch_emails(days_back=days_back)

        if not emails:
            return {"success": False, "error": "No emails found"}

        results = {
            "success": True,
            "total_emails": len(emails),
            "days_back": days_back,
            "processed_at": datetime.now().isoformat()
        }

        # SYPHON intelligence extraction
        if syphon_enabled:
            logger.info("")
            logger.info("="*80)
            logger.info("@SYPHON: Extracting Intelligence")
            logger.info("="*80)
            syphon_results = self.syphon_emails(emails)
            results["syphon"] = syphon_results

        # Organize emails
        organized = None
        if organize_enabled:
            logger.info("")
            logger.info("="*80)
            logger.info("Organizing Emails")
            logger.info("="*80)
            organized = self.organize_emails(emails)

            # Save organization
            org_file = self.data_dir / f"email_organization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            org_data = {k: [e.to_dict() for e in v] if isinstance(v, list) else v for k, v in organized.items()}
            with open(org_file, 'w', encoding='utf-8') as f:
                json.dump(org_data, f, indent=2, ensure_ascii=False, default=str)
            logger.info(f"✅ Organization saved to: {org_file}")

            results["organization"] = {k: len(v) if isinstance(v, list) else v for k, v in organized.items()}

        # Upload to NAS Company Email Hub
        logger.info("")
        logger.info("="*80)
        logger.info("UPLOADING TO NAS COMPANY EMAIL HUB")
        logger.info("="*80)
        upload_results = self.upload_to_nas_email_hub(
            emails=emails,
            syphon_results=syphon_results if syphon_enabled else None,
            organized=organized
        )
        results["nas_upload"] = upload_results

        logger.info("")
        logger.info("="*80)
        logger.info("✅ EMAIL PROCESSING COMPLETE")
        logger.info("="*80)

        return results


def main():
    try:
        """Main function."""
        import argparse

        parser = argparse.ArgumentParser(description="Email Management System")
        parser.add_argument("--project-root", type=Path, default=project_root)
        parser.add_argument("--days-back", type=int, default=180, help="Days to look back (default: 180 = 6 months)")
        parser.add_argument("--syphon", action="store_true", default=True, help="Enable SYPHON extraction")
        parser.add_argument("--organize", action="store_true", default=True, help="Enable organization")
        parser.add_argument("--purge", type=int, metavar="DAYS", help="Purge emails older than DAYS")
        parser.add_argument("--purge-dry-run", action="store_true", help="Dry run for purge (don't actually delete)")

        args = parser.parse_args()

        system = EmailManagementSystem(args.project_root)

        if args.purge:
            # Purge old emails
            logger.info("="*80)
            logger.info("EMAIL PURGE")
            logger.info("="*80)
            result = system.purge_old_emails(
                days_old=args.purge,
                dry_run=args.purge_dry_run
            )
            print(json.dumps(result, indent=2, default=str))
        else:
            # Process emails
            result = system.process_emails(
                days_back=args.days_back,
                syphon_enabled=args.syphon,
                organize_enabled=args.organize
            )
            print(json.dumps(result, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()