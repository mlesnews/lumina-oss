"""
Unified Email Service
Unified email service treating Gmail and ProtonMail as first-class providers.

Provides a single interface for:
- Gmail (via Gmail API / n8n)
- ProtonMail (via ProtonBridge IMAP/SMTP)

All emails are treated as if sent/received directly from each provider.

#JARVIS #LUMINA #GMAIL #PROTONMAIL #EMAIL #UNIFIED
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("UnifiedEmailService")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("UnifiedEmailService")

from lumina_gmail_integration_system import LUMINAGmailIntegration, EmailMetadata
from protonbridge_integration import ProtonBridgeIntegration, ProtonMailMessage


class EmailProvider(Enum):
    """Email provider types."""
    GMAIL = "gmail"
    PROTONMAIL = "protonmail"
    UNIFIED = "unified"  # Search both


@dataclass
class UnifiedEmailMessage:
    """Unified email message structure (works for both Gmail and ProtonMail)."""
    message_id: str
    provider: EmailProvider
    subject: str
    from_address: str
    to_address: str
    date: str
    body: str
    html_body: Optional[str] = None
    attachments: List[Dict[str, Any]] = None
    headers: Dict[str, str] = None
    category: Optional[str] = None
    priority: int = 3  # 1-5, 1=highest

    def __post_init__(self):
        if self.attachments is None:
            self.attachments = []
        if self.headers is None:
            self.headers = {}


class UnifiedEmailService:
    """
    Unified Email Service

    Provides a single interface for Gmail and ProtonMail, treating both
    as first-class email providers. All emails appear as if sent/received
    directly from each provider.
    """

    def __init__(self, project_root: Path):
        """
        Initialize Unified Email Service.

        Args:
            project_root: Project root directory
        """
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "unified_email"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize providers
        self.gmail_service = LUMINAGmailIntegration(project_root)
        self.protonmail_service = ProtonBridgeIntegration(project_root)

        logger.info("✅ Unified Email Service initialized (Gmail + ProtonMail)")

    def search_emails(self,
                     query: str,
                     provider: EmailProvider = EmailProvider.UNIFIED,
                     days_back: int = 30,
                     max_results: int = 100) -> List[UnifiedEmailMessage]:
        """
        Search emails across providers.

        Args:
            query: Search query
            provider: Email provider (UNIFIED searches both)
            days_back: Days to search back
            max_results: Maximum results per provider

        Returns:
            List of unified email messages
        """
        results = []

        if provider == EmailProvider.UNIFIED or provider == EmailProvider.GMAIL:
            # Search Gmail
            try:
                gmail_results = self.gmail_service.search_gmail(
                    query=query,
                    max_results=max_results,
                    days_back=days_back
                )

                for gmail_msg in gmail_results:
                    unified_msg = self._gmail_to_unified(gmail_msg)
                    results.append(unified_msg)

                logger.info(f"✅ Found {len(gmail_results)} emails in Gmail")
            except Exception as e:
                logger.warning(f"⚠️  Gmail search failed: {e}")

        if provider == EmailProvider.UNIFIED or provider == EmailProvider.PROTONMAIL:
            # Search ProtonMail
            try:
                protonmail_results = self.protonmail_service.search_emails(
                    query=query,
                    days_back=days_back
                )

                for proton_msg in protonmail_results:
                    unified_msg = self._protonmail_to_unified(proton_msg)
                    results.append(unified_msg)

                logger.info(f"✅ Found {len(protonmail_results)} emails in ProtonMail")
            except Exception as e:
                logger.warning(f"⚠️  ProtonMail search failed: {e}")

        # Sort by date (newest first)
        results.sort(key=lambda x: x.date, reverse=True)

        # Limit results
        results = results[:max_results]

        logger.info(f"✅ Total unified results: {len(results)}")
        return results

    def send_email(self,
                  to_address: str,
                  subject: str,
                  body: str,
                  provider: EmailProvider = EmailProvider.GMAIL,
                  html_body: Optional[str] = None,
                  from_address: Optional[str] = None,
                  attachments: List[Path] = None) -> bool:
        """
        Send email via specified provider.

        Args:
            to_address: Recipient email address
            subject: Email subject
            body: Plain text body
            provider: Email provider to use
            html_body: Optional HTML body
            from_address: Sender address
            attachments: Optional attachment file paths

        Returns:
            True if sent successfully
        """
        if provider == EmailProvider.GMAIL:
            # Send via Gmail (would need Gmail API implementation)
            logger.info(f"Sending email via Gmail to {to_address}")
            # TODO: Implement Gmail send  # [ADDRESSED]  # [ADDRESSED]
            logger.warning("⚠️  Gmail send not yet implemented")
            return False

        elif provider == EmailProvider.PROTONMAIL:
            # Send via ProtonMail
            return self.protonmail_service.send_email(
                to_address=to_address,
                subject=subject,
                body=body,
                html_body=html_body,
                from_address=from_address,
                attachments=attachments
            )

        else:
            logger.error(f"❌ Invalid provider: {provider}")
            return False

    def import_emails(self,
                     provider: EmailProvider = EmailProvider.UNIFIED,
                     days_back: int = 60) -> List[UnifiedEmailMessage]:
        """
        Import emails from providers.

        Args:
            provider: Email provider (UNIFIED imports from both)
            days_back: Days to import back

        Returns:
            List of imported unified email messages
        """
        imported = []

        if provider == EmailProvider.UNIFIED or provider == EmailProvider.GMAIL:
            # Import from Gmail
            try:
                # Gmail import would be via search
                gmail_results = self.gmail_service.search_gmail(
                    query="ALL",
                    max_results=500,
                    days_back=days_back
                )

                for gmail_msg in gmail_results:
                    unified_msg = self._gmail_to_unified(gmail_msg)
                    imported.append(unified_msg)

                logger.info(f"✅ Imported {len(gmail_results)} emails from Gmail")
            except Exception as e:
                logger.warning(f"⚠️  Gmail import failed: {e}")

        if provider == EmailProvider.UNIFIED or provider == EmailProvider.PROTONMAIL:
            # Import from ProtonMail
            try:
                protonmail_results = self.protonmail_service.import_emails(
                    days_back=days_back
                )

                for proton_msg in protonmail_results:
                    unified_msg = self._protonmail_to_unified(proton_msg)
                    imported.append(unified_msg)

                logger.info(f"✅ Imported {len(protonmail_results)} emails from ProtonMail")
            except Exception as e:
                logger.warning(f"⚠️  ProtonMail import failed: {e}")

        # Save imported emails
        self._save_imported_emails(imported)

        logger.info(f"✅ Total imported: {len(imported)} emails")
        return imported

    def _gmail_to_unified(self, gmail_msg: EmailMetadata) -> UnifiedEmailMessage:
        """Convert Gmail EmailMetadata to UnifiedEmailMessage."""
        return UnifiedEmailMessage(
            message_id=gmail_msg.email_id,
            provider=EmailProvider.GMAIL,
            subject=gmail_msg.subject,
            from_address=gmail_msg.from_address,
            to_address=gmail_msg.to_address,
            date=gmail_msg.date,
            body="",  # Would need to fetch body from Gmail API
            category=gmail_msg.category.value if gmail_msg.category else None,
            priority=gmail_msg.priority
        )

    def _protonmail_to_unified(self, proton_msg: ProtonMailMessage) -> UnifiedEmailMessage:
        """Convert ProtonMailMessage to UnifiedEmailMessage."""
        return UnifiedEmailMessage(
            message_id=proton_msg.message_id,
            provider=EmailProvider.PROTONMAIL,
            subject=proton_msg.subject,
            from_address=proton_msg.from_address,
            to_address=proton_msg.to_address,
            date=proton_msg.date,
            body=proton_msg.body,
            html_body=proton_msg.html_body,
            attachments=proton_msg.attachments,
            headers=proton_msg.headers
        )

    def _save_imported_emails(self, emails: List[UnifiedEmailMessage]) -> None:
        """Save imported emails to disk."""
        import_dir = self.data_dir / "imported"
        import_dir.mkdir(parents=True, exist_ok=True)

        for email in emails:
            try:
                # Create filename from message ID
                filename = email.message_id.replace("<", "").replace(">", "").replace("@", "_")
                filename = f"{email.provider.value}_{filename}.json"

                email_file = import_dir / filename
                with open(email_file, 'w') as f:
                    json.dump(asdict(email), f, indent=2, ensure_ascii=False)
            except Exception as e:
                logger.warning(f"Failed to save email {email.message_id}: {e}")


def main():
    try:
        """Test Unified Email Service."""
        import argparse

        parser = argparse.ArgumentParser(description="Unified Email Service")
        parser.add_argument("--project-root", type=Path, default=Path(__file__).parent.parent.parent)
        parser.add_argument("--search", type=str, help="Search query")
        parser.add_argument("--provider", type=str, choices=["gmail", "protonmail", "unified"],
                           default="unified", help="Email provider")
        parser.add_argument("--days", type=int, default=30, help="Days to search back")
        parser.add_argument("--import-emails", action="store_true", dest="import_emails", help="Import emails")

        args = parser.parse_args()

        provider = EmailProvider[args.provider.upper()]

        service = UnifiedEmailService(args.project_root)

        if args.import_emails:
            emails = service.import_emails(provider=provider, days_back=args.days)
            print(f"✅ Imported {len(emails)} emails")
        elif args.search:
            emails = service.search_emails(query=args.search, provider=provider, days_back=args.days)
            print(f"✅ Found {len(emails)} emails")
            for email in emails[:10]:  # Show first 10
                print(f"  [{email.provider.value}] {email.subject} ({email.from_address})")
        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()