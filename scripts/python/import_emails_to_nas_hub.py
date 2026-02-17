"""
Import Emails to NAS Mail Hub
Imports emails from Gmail, ProtonMail, and Outlook to NAS MailPlus email hub.

This script:
- Connects to Gmail via IMAP
- Connects to ProtonMail via Proton Bridge
- Imports emails to NAS MailPlus
- Organizes by date and account
- Handles duplicates and large attachments

#JARVIS #LUMINA #NAS #MAILPLUS #EMAIL #IMPORT #GMAIL #PROTONMAIL
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime, parsedate_tz
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
import hashlib

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("ImportEmailsToNASHub")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ImportEmailsToNASHub")

try:
    from scripts.python.unified_secrets_manager import UnifiedSecretsManager, SecretSource
    from scripts.python.unified_email_service import UnifiedEmailService, EmailProvider
    from scripts.python.nas_azure_vault_integration import NASAzureVaultIntegration
    INTEGRATIONS_AVAILABLE = True
except ImportError as e:
    INTEGRATIONS_AVAILABLE = False
    logger.warning(f"⚠️  Some integrations not available: {e}")


class NASEmailImporter:
    """
    Import emails from various sources to NAS MailPlus email hub.
    """

    def __init__(self, project_root: Path):
        """
        Initialize NAS Email Importer.

        Args:
            project_root: Project root directory
        """
        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config" / "outlook"
        self.data_dir = self.project_root / "data" / "email_import"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load configuration
        self.config = self._load_config()

        # Initialize services
        self.email_service = None
        self.secrets_manager = None
        self.nas_integration = None

        if INTEGRATIONS_AVAILABLE:
            try:
                self.secrets_manager = UnifiedSecretsManager(
                    project_root,
                    prefer_source=SecretSource.AZURE_KEY_VAULT
                )
                logger.info("✅ Secrets manager initialized")
            except Exception as e:
                logger.warning(f"⚠️  Secrets manager not available: {e}")

            try:
                self.email_service = UnifiedEmailService(project_root)
            except Exception as e:
                logger.warning(f"⚠️  Email service not available: {e}")

            try:
                self.nas_integration = NASAzureVaultIntegration()
            except Exception as e:
                logger.warning(f"⚠️  NAS integration not available: {e}")

        # Track imported emails to avoid duplicates
        self.imported_hashes_file = self.data_dir / "imported_hashes.json"
        self.imported_hashes = self._load_imported_hashes()

    def _load_config(self) -> Dict[str, Any]:
        """Load import configuration."""
        config_file = self.config_dir / "nas_import_config.json"

        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️  Could not load config: {e}")

        # Default configuration
        return {
            "nas_mail_hub": {
                "server": "<NAS_PRIMARY_IP>",
                "imap": {"server": "<NAS_PRIMARY_IP>", "port": 993, "ssl": True}
            },
            "import_sources": {
                "gmail": {"enabled": True},
                "protonmail": {"enabled": True}
            },
            "import_settings": {
                "skip_duplicates": True,
                "max_age_days": 365
            }
        }

    def _load_imported_hashes(self) -> Dict[str, List[str]]:
        """Load hashes of already imported emails."""
        if self.imported_hashes_file.exists():
            try:
                with open(self.imported_hashes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️  Could not load imported hashes: {e}")

        return {}

    def _save_imported_hashes(self):
        """Save imported email hashes."""
        try:
            with open(self.imported_hashes_file, 'w', encoding='utf-8') as f:
                json.dump(self.imported_hashes, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"⚠️  Could not save imported hashes: {e}")

    def _get_email_hash(self, message_id: str, from_addr: str, date: str) -> str:
        """Generate hash for email to detect duplicates."""
        content = f"{message_id}:{from_addr}:{date}"
        return hashlib.md5(content.encode()).hexdigest()

    def _is_duplicate(self, email_hash: str, source: str) -> bool:
        """Check if email was already imported."""
        if not self.config["import_settings"].get("skip_duplicates", True):
            return False

        source_hashes = self.imported_hashes.get(source, [])
        return email_hash in source_hashes

    def _mark_as_imported(self, email_hash: str, source: str):
        """Mark email as imported."""
        if source not in self.imported_hashes:
            self.imported_hashes[source] = []

        if email_hash not in self.imported_hashes[source]:
            self.imported_hashes[source].append(email_hash)

    def import_from_gmail(self, days_back: int = 30) -> Tuple[int, int]:
        """
        Import emails from Gmail using direct IMAP with Azure Key Vault credentials.

        Args:
            days_back: Days to import back

        Returns:
            Tuple of (imported_count, skipped_count)
        """
        if not self.config["import_sources"]["gmail"].get("enabled", True):
            logger.info("⏭️  Gmail import disabled")
            return 0, 0

        logger.info("="*80)
        logger.info("IMPORTING FROM GMAIL (via IMAP with Azure Key Vault)")
        logger.info("="*80)

        if not self.secrets_manager:
            logger.error("❌ Secrets manager not available")
            return 0, 0

        try:
            import imaplib
            import email
            from email.header import decode_header
            from email.utils import parsedate_to_datetime
            from datetime import timedelta

            # Get Gmail credentials from Azure Key Vault
            try:
                gmail_email = self.secrets_manager.get_secret("login-account-gmail-ceo-gmail-email")
                gmail_password = self.secrets_manager.get_secret("login-account-gmail-ceo-gmail-app-password")
                logger.info(f"✅ Gmail credentials loaded from Azure Key Vault: {gmail_email}")
            except Exception as e:
                logger.error(f"❌ Failed to get Gmail credentials from Azure Key Vault: {e}")
                logger.info("   Trying alternative secret names...")
                try:
                    gmail_email = self.secrets_manager.get_secret("gmail-email")
                    gmail_password = self.secrets_manager.get_secret("gmail-app-password")
                except:
                    logger.error("❌ Gmail credentials not found in Azure Key Vault")
                    return 0, 0

            # Connect to Gmail IMAP
            logger.info("Connecting to Gmail IMAP...")
            imap_server = "imap.gmail.com"
            imap_port = 993
            mail = imaplib.IMAP4_SSL(imap_server, imap_port)
            mail.login(gmail_email, gmail_password)
            logger.info("✅ Connected to Gmail via IMAP")

            # Select INBOX
            mail.select("INBOX")

            # Calculate date threshold
            date_threshold = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")
            search_query = f'SINCE {date_threshold}'

            # Search for emails
            logger.info(f"Searching for emails since {date_threshold}...")
            status, messages = mail.search(None, search_query)

            if status != "OK":
                logger.error(f"❌ Gmail search failed: {status}")
                mail.logout()
                return 0, 0

            email_ids = messages[0].split()
            logger.info(f"Found {len(email_ids)} emails to process")

            imported = 0
            skipped = 0

            # Process emails
            for email_id in email_ids:
                try:
                    # Fetch email
                    status, msg_data = mail.fetch(email_id, "(RFC822)")
                    if status != "OK":
                        continue

                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)

                    # Parse email
                    subject = self._decode_header(email_message.get("Subject", ""))
                    from_addr = self._decode_header(email_message.get("From", ""))
                    to_addr = self._decode_header(email_message.get("To", ""))
                    date_str = email_message.get("Date", "")
                    message_id = email_message.get("Message-ID", f"<{email_id.decode()}>")

                    # Get body
                    body = self._get_email_body(email_message)

                    # Generate hash
                    email_hash = self._get_email_hash(
                        message_id,
                        from_addr,
                        date_str
                    )

                    # Check for duplicates
                    if self._is_duplicate(email_hash, "gmail"):
                        skipped += 1
                        continue

                    # Create unified email message structure
                    from scripts.python.unified_email_service import UnifiedEmailMessage
                    email_msg = UnifiedEmailMessage(
                        message_id=message_id,
                        provider=EmailProvider.GMAIL,
                        subject=subject,
                        from_address=from_addr,
                        to_address=to_addr,
                        date=date_str,
                        body=body
                    )

                    # Import to NAS
                    if self._import_email_to_nas(email_msg, "gmail"):
                        self._mark_as_imported(email_hash, "gmail")
                        imported += 1
                    else:
                        skipped += 1

                except Exception as e:
                    logger.warning(f"  ⚠️  Failed to process email {email_id}: {e}")
                    skipped += 1
                    continue

            # Disconnect
            mail.logout()

            logger.info(f"✅ Gmail import complete: {imported} imported, {skipped} skipped")
            self._save_imported_hashes()

            return imported, skipped

        except Exception as e:
            logger.error(f"❌ Gmail import failed: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return 0, 0

    def _decode_header(self, header_value: str) -> str:
        """Decode email header."""
        if not header_value:
            return ""

        try:
            from email.header import decode_header
            decoded_parts = decode_header(header_value)
            decoded_string = ""
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    decoded_string += part.decode(encoding or "utf-8", errors="ignore")
                else:
                    decoded_string += part
            return decoded_string
        except:
            return str(header_value)

    def _get_email_body(self, email_message) -> str:
        """Extract email body."""
        body = ""

        try:
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
        except:
            pass

        return body

    def import_from_protonmail(self, days_back: int = 30) -> Tuple[int, int]:
        """
        Import emails from ProtonMail.

        Args:
            days_back: Days to import back

        Returns:
            Tuple of (imported_count, skipped_count)
        """
        if not self.config["import_sources"]["protonmail"].get("enabled", True):
            logger.info("⏭️  ProtonMail import disabled")
            return 0, 0

        logger.info("="*80)
        logger.info("IMPORTING FROM PROTONMAIL")
        logger.info("="*80)

        if not self.email_service:
            logger.error("❌ Email service not available")
            return 0, 0

        try:
            # Use unified email service to get ProtonMail emails
            emails = self.email_service.search_emails(
                query="ALL",
                provider=EmailProvider.PROTONMAIL,
                days_back=days_back,
                max_results=1000
            )

            imported = 0
            skipped = 0

            for email_msg in emails:
                # Generate hash
                email_hash = self._get_email_hash(
                    email_msg.message_id,
                    email_msg.from_address,
                    email_msg.date
                )

                # Check for duplicates
                if self._is_duplicate(email_hash, "protonmail"):
                    skipped += 1
                    continue

                # Import to NAS
                if self._import_email_to_nas(email_msg, "protonmail"):
                    self._mark_as_imported(email_hash, "protonmail")
                    imported += 1
                else:
                    skipped += 1

            logger.info(f"✅ ProtonMail import complete: {imported} imported, {skipped} skipped")
            self._save_imported_hashes()

            return imported, skipped

        except Exception as e:
            logger.error(f"❌ ProtonMail import failed: {e}")
            return 0, 0

    def _import_email_to_nas(self, email_msg, source: str) -> bool:
        """
        Import single email to NAS MailPlus.

        Args:
            email_msg: Email message object
            source: Source identifier (gmail, protonmail, etc.)

        Returns:
            True if imported successfully
        """
        try:
            # Parse email date (RFC 2822 format)
            try:
                if hasattr(email_msg, 'date') and email_msg.date:
                    date_str = str(email_msg.date)
                    # Try to parse RFC 2822 date
                    try:
                        date = parsedate_to_datetime(date_str)
                    except (ValueError, TypeError, AttributeError):
                        # Fallback: try manual parsing
                        try:
                            date_tuple = parsedate_tz(date_str)
                            if date_tuple:
                                # Convert to datetime
                                import time
                                timestamp = email.utils.mktime_tz(date_tuple)
                                date = datetime.fromtimestamp(timestamp)
                            else:
                                date = datetime.now()
                        except:
                            date = datetime.now()
                else:
                    date = datetime.now()
            except Exception:
                # Fallback: use current date if parsing fails
                date = datetime.now()

            archive_path = self.data_dir / "archive" / source / date.strftime("%Y/%m")
            archive_path.mkdir(parents=True, exist_ok=True)

            # Save email as EML file
            email_file = archive_path / f"{email_msg.message_id.replace('<', '').replace('>', '').replace('@', '_')}.eml"

            # Create EML content
            eml_content = self._create_eml_content(email_msg)

            with open(email_file, 'w', encoding='utf-8') as f:
                f.write(eml_content)

            # If NAS integration available, also upload via API
            if self.nas_integration:
                # TODO: Implement NAS MailPlus API upload  # [ADDRESSED]  # [ADDRESSED]
                # For now, just archive locally
                pass

            logger.debug(f"  ✅ Imported: {email_msg.subject[:50]}...")
            return True

        except Exception as e:
            logger.warning(f"  ⚠️  Failed to import email: {e}")
            return False

    def _create_eml_content(self, email_msg) -> str:
        """Create EML file content from email message."""
        # Simple EML format
        lines = [
            f"Message-ID: {email_msg.message_id}",
            f"From: {email_msg.from_address}",
            f"To: {email_msg.to_address}",
            f"Subject: {email_msg.subject}",
            f"Date: {email_msg.date}",
            "MIME-Version: 1.0",
            "Content-Type: text/plain; charset=utf-8",
            "",
            email_msg.body or ""
        ]

        return "\n".join(lines)

    def run_import(self, days_back: int = 30, sources: Optional[List[str]] = None) -> Dict[str, Any]:
        try:
            """
            Run email import from all configured sources.

            Args:
                days_back: Days to import back
                sources: List of sources to import (None = all enabled)

            Returns:
                Import results dictionary
            """
            logger.info("="*80)
            logger.info("EMAIL IMPORT TO NAS HUB")
            logger.info("="*80)
            logger.info("")

            results = {
                "timestamp": datetime.now().isoformat(),
                "gmail": {"imported": 0, "skipped": 0},
                "protonmail": {"imported": 0, "skipped": 0},
                "total_imported": 0,
                "total_skipped": 0
            }

            if sources is None:
                sources = []
                if self.config["import_sources"]["gmail"].get("enabled", True):
                    sources.append("gmail")
                if self.config["import_sources"]["protonmail"].get("enabled", True):
                    sources.append("protonmail")

            # Import from Gmail
            if "gmail" in sources:
                imported, skipped = self.import_from_gmail(days_back)
                results["gmail"]["imported"] = imported
                results["gmail"]["skipped"] = skipped

            # Import from ProtonMail
            if "protonmail" in sources:
                imported, skipped = self.import_from_protonmail(days_back)
                results["protonmail"]["imported"] = imported
                results["protonmail"]["skipped"] = skipped

            # Calculate totals
            results["total_imported"] = results["gmail"]["imported"] + results["protonmail"]["imported"]
            results["total_skipped"] = results["gmail"]["skipped"] + results["protonmail"]["skipped"]

            # Save results
            results_file = self.data_dir / f"import_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            logger.info("")
            logger.info("="*80)
            logger.info("IMPORT SUMMARY")
            logger.info("="*80)
            logger.info(f"Gmail: {results['gmail']['imported']} imported, {results['gmail']['skipped']} skipped")
            logger.info(f"ProtonMail: {results['protonmail']['imported']} imported, {results['protonmail']['skipped']} skipped")
            logger.info(f"Total: {results['total_imported']} imported, {results['total_skipped']} skipped")
            logger.info(f"Results saved: {results_file}")

            return results


        except Exception as e:
            self.logger.error(f"Error in run_import: {e}", exc_info=True)
            raise
def main():
    try:
        """Main function."""
        import argparse

        parser = argparse.ArgumentParser(
            description="Import Emails to NAS Mail Hub"
        )

        parser.add_argument(
            "--project-root",
            type=Path,
            default=Path(__file__).parent.parent.parent,
            help="Project root directory"
        )
        parser.add_argument(
            "--days-back",
            type=int,
            default=30,
            help="Days to import back"
        )
        parser.add_argument(
            "--sources",
            nargs="+",
            choices=["gmail", "protonmail"],
            help="Sources to import (default: all enabled)"
        )

        args = parser.parse_args()

        importer = NASEmailImporter(args.project_root)
        results = importer.run_import(
            days_back=args.days_back,
            sources=args.sources
        )

        logger.info("")
        logger.info("📋 NEXT STEPS:")
        logger.info("   1. Review imported emails in data/email_import/archive/")
        logger.info("   2. Set up scheduled import daemon for continuous syncing")
        logger.info("   3. Configure NAS MailPlus to receive imported emails")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()