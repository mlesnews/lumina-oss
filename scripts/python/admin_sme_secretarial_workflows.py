"""
Admin SME Secretarial Workflows
Secretarial roles and responsibilities for email management:
- Sending emails
- Receiving emails
- Categorizing/organizing emails
- Holocron/Jedi Archives integration

#JARVIS #LUMINA #ADMIN #SECRETARIAL #HOLOCRON #JEDIARCHIVES
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import asdict

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("AdminSMESecretarialWorkflows")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("AdminSMESecretarialWorkflows")

from lumina_gmail_integration import (
    LUMINAGmailIntegration,
    EmailCategory,
    EmailPriority,
    EmailMetadata
)


class AdminSMESecretarialWorkflows:
    """
    Secretarial workflows for Admin SME role.

    Handles:
    - Incoming email processing
    - Outgoing email management
    - Email categorization and organization
    - Holocron/Jedi Archives integration
    """

    def __init__(self, project_root: Path):
        """
        Initialize secretarial workflows.

        Args:
            project_root: Root path of the LUMINA project
        """
        self.project_root = Path(project_root)
        self.gmail_integration = LUMINAGmailIntegration(project_root)
        self.config_file = self.project_root / "config" / "admin_sme_job_slot.json"
        self.load_config()

    def load_config(self) -> Dict[str, Any]:
        try:
            """Load Admin SME configuration."""
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            return {}

        except Exception as e:
            self.logger.error(f"Error in load_config: {e}", exc_info=True)
            raise
    def process_incoming_emails(self, 
                                max_emails: int = 50,
                                unread_only: bool = True) -> List[EmailMetadata]:
        """
        Process incoming emails through secretarial workflow.

        Args:
            max_emails: Maximum number of emails to process
            unread_only: Only process unread emails

        Returns:
            List of processed email metadata
        """
        logger.info("Processing incoming emails through secretarial workflow...")

        query = "is:unread" if unread_only else "in:inbox"
        emails = self.gmail_integration.search_emails(query, max_results=max_emails)

        processed = []
        for email in emails:
            try:
                metadata = self.gmail_integration.process_incoming_email(email)
                processed.append(metadata)

                logger.info(f"✓ Processed: {metadata.subject[:50]} - {metadata.category.value} - {metadata.priority.value}")

            except Exception as e:
                logger.error(f"Error processing email {email.get('id', 'unknown')}: {e}")

        logger.info(f"✓ Processed {len(processed)} email(s)")
        return processed

    def send_email_workflow(self,
                           to: str,
                           subject: str,
                           body: str,
                           attachments: Optional[List[Path]] = None,
                           follow_up_days: Optional[int] = None) -> Dict[str, Any]:
        """
        Send email through secretarial workflow.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            attachments: Optional attachment files
            follow_up_days: Days until follow-up reminder

        Returns:
            Send result with tracking information
        """
        logger.info(f"Sending email to {to}: {subject[:50]}...")

        result = self.gmail_integration.send_email(to, subject, body, attachments)

        if result.get("success"):
            # Set follow-up if requested
            if follow_up_days:
                follow_up_date = (datetime.now() + timedelta(days=follow_up_days)).isoformat()
                self._set_follow_up_reminder(result['message_id'], to, subject, follow_up_date)

            logger.info(f"✓ Email sent successfully: {result['message_id']}")
        else:
            logger.error(f"✗ Failed to send email: {result.get('error')}")

        return result

    def _set_follow_up_reminder(self, message_id: str, to: str, subject: str, follow_up_date: str) -> None:
        try:
            """Set follow-up reminder for sent email."""
            reminders_dir = self.project_root / "data" / "gmail_integration" / "follow_up_reminders"
            reminders_dir.mkdir(parents=True, exist_ok=True)

            reminder = {
                "message_id": message_id,
                "to": to,
                "subject": subject,
                "follow_up_date": follow_up_date,
                "created_at": datetime.now().isoformat(),
                "status": "pending"
            }

            reminder_file = reminders_dir / f"reminder_{message_id}.json"
            with open(reminder_file, 'w') as f:
                json.dump(reminder, f, indent=2)

            logger.info(f"✓ Follow-up reminder set for {follow_up_date}")

        except Exception as e:
            self.logger.error(f"Error in _set_follow_up_reminder: {e}", exc_info=True)
            raise
    def categorize_and_organize_emails(self,
                                      email_ids: Optional[List[str]] = None,
                                      auto_process: bool = True) -> Dict[str, Any]:
        """
        Categorize and organize emails.

        Args:
            email_ids: Specific email IDs to process (None = process all unread)
            auto_process: Automatically process through workflow

        Returns:
            Organization results
        """
        logger.info("Categorizing and organizing emails...")

        if email_ids:
            emails = []
            for email_id in email_ids:
                email = self.gmail_integration._get_email_details(email_id)
                if email:
                    emails.append(email)
        else:
            emails = self.gmail_integration.search_emails("in:inbox", max_results=100)

        results = {
            "total_processed": 0,
            "by_category": {},
            "by_priority": {},
            "holocron_synced": 0,
            "jedi_archives_synced": 0
        }

        for email in emails:
            try:
                if auto_process:
                    metadata = self.gmail_integration.process_incoming_email(email)
                else:
                    category = self.gmail_integration.categorize_email(email)
                    priority = self.gmail_integration.determine_priority(email)
                    metadata = EmailMetadata(
                        email_id=email['id'],
                        thread_id=email.get('thread_id', ''),
                        subject=email.get('subject', ''),
                        from_address=email.get('from', ''),
                        to_address=email.get('to', ''),
                        date=email.get('date', ''),
                        category=category,
                        priority=priority,
                        tags=self.gmail_integration._extract_tags(email)
                    )

                # Update statistics
                results["total_processed"] += 1
                category_name = metadata.category.value
                results["by_category"][category_name] = results["by_category"].get(category_name, 0) + 1

                priority_name = metadata.priority.value
                results["by_priority"][priority_name] = results["by_priority"].get(priority_name, 0) + 1

                if metadata.holocron_reference:
                    results["holocron_synced"] += 1
                if metadata.jedi_archive_path:
                    results["jedi_archives_synced"] += 1

            except Exception as e:
                logger.error(f"Error processing email {email.get('id', 'unknown')}: {e}")

        logger.info(f"✓ Organized {results['total_processed']} email(s)")
        logger.info(f"  Categories: {results['by_category']}")
        logger.info(f"  Priorities: {results['by_priority']}")

        return results

    def search_and_filter_emails(self,
                                    query: str,
                                    category: Optional[EmailCategory] = None,
                                    priority: Optional[EmailPriority] = None,
                                    tags: Optional[List[str]] = None,
                                    date_from: Optional[datetime] = None,
                                    date_to: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Advanced search and filtering of emails.

        Args:
            query: Gmail search query
            category: Filter by category
            priority: Filter by priority
            tags: Filter by tags
            date_from: Filter from date
            date_to: Filter to date

        Returns:
            List of filtered email data with metadata
        """
        try:
            logger.info(f"Searching emails: {query}")

            # Build Gmail query
            gmail_query = query

            if date_from:
                gmail_query += f" after:{date_from.strftime('%Y/%m/%d')}"
            if date_to:
                gmail_query += f" before:{date_to.strftime('%Y/%m/%d')}"

            # Search Gmail
            emails = self.gmail_integration.search_emails(gmail_query, max_results=100)

            # Apply filters
            filtered = []
            for email in emails:
                # Load metadata if exists
                metadata_file = self.gmail_integration.metadata_dir / f"email_{email['id']}.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata_dict = json.load(f)
                        metadata = EmailMetadata(**metadata_dict)
                else:
                    # Create metadata on the fly
                    category_obj = self.gmail_integration.categorize_email(email)
                    priority_obj = self.gmail_integration.determine_priority(email)
                    metadata = EmailMetadata(
                        email_id=email['id'],
                        thread_id=email.get('thread_id', ''),
                        subject=email.get('subject', ''),
                        from_address=email.get('from', ''),
                        to_address=email.get('to', ''),
                        date=email.get('date', ''),
                        category=category_obj,
                        priority=priority_obj,
                        tags=self.gmail_integration._extract_tags(email)
                    )

                # Apply filters
                if category and metadata.category != category:
                    continue
                if priority and metadata.priority != priority:
                    continue
                if tags and not any(tag in metadata.tags for tag in tags):
                    continue

                # Add metadata to email data
                email['metadata'] = asdict(metadata)
                filtered.append(email)

            logger.info(f"✓ Found {len(filtered)} email(s) matching filters")
            return filtered

        except Exception as e:
            logger.error(f"Error in search_and_filter_emails: {e}", exc_info=True)
            raise

    def sync_to_holocron(self, email_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Sync emails to Holocron/Jedi Archives.

        Args:
            email_ids: Specific email IDs (None = sync all unprocessed)

        Returns:
            Sync results
        """
        logger.info("Syncing emails to Holocron/Jedi Archives...")

        if email_ids:
            emails = []
            for email_id in email_ids:
                email = self.gmail_integration._get_email_details(email_id)
                if email:
                    emails.append(email)
        else:
            # Get unprocessed emails
            emails = self.gmail_integration.search_emails("in:inbox", max_results=100)

        results = {
            "total": len(emails),
            "synced": 0,
            "errors": 0,
            "holocron_paths": []
        }

        for email in emails:
            try:
                metadata = self.gmail_integration.process_incoming_email(email)
                if metadata.holocron_reference:
                    results["synced"] += 1
                    results["holocron_paths"].append(metadata.holocron_reference)
            except Exception as e:
                logger.error(f"Error syncing email {email.get('id', 'unknown')}: {e}")
                results["errors"] += 1

        logger.info(f"✓ Synced {results['synced']}/{results['total']} email(s) to Holocron")
        return results


def main():
    try:
        """Main function for CLI usage."""
        import argparse

        parser = argparse.ArgumentParser(description="Admin SME Secretarial Workflows")
        parser.add_argument("--project-root", type=Path,
                           default=Path(__file__).parent.parent.parent,
                           help="Project root directory")
        parser.add_argument("--process-incoming", action="store_true",
                           help="Process incoming emails")
        parser.add_argument("--organize", action="store_true",
                           help="Categorize and organize emails")
        parser.add_argument("--sync-holocron", action="store_true",
                           help="Sync emails to Holocron/Jedi Archives")
        parser.add_argument("--search", type=str,
                           help="Search query")
        parser.add_argument("--category", type=str,
                           help="Filter by category")
        parser.add_argument("--priority", type=str,
                           help="Filter by priority")

        args = parser.parse_args()

        workflows = AdminSMESecretarialWorkflows(args.project_root)

        if args.process_incoming:
            processed = workflows.process_incoming_emails()
            print(f"\n✓ Processed {len(processed)} incoming email(s)")

        if args.organize:
            results = workflows.categorize_and_organize_emails()
            print(f"\n✓ Organized {results['total_processed']} email(s)")
            print(f"  Categories: {results['by_category']}")
            print(f"  Priorities: {results['by_priority']}")

        if args.sync_holocron:
            results = workflows.sync_to_holocron()
            print(f"\n✓ Synced {results['synced']}/{results['total']} email(s) to Holocron")

        if args.search:
            category = EmailCategory[args.category.upper()] if args.category else None
            priority = EmailPriority[args.priority.upper()] if args.priority else None

            emails = workflows.search_and_filter_emails(args.search, category, priority)
            print(f"\n✓ Found {len(emails)} email(s)")
            for email in emails[:10]:
                print(f"  - {email.get('subject', 'No subject')[:60]}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()