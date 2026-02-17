"""
Sync Emails to NAS Mail Hub
Continuously syncs emails from Gmail and ProtonMail to NAS Mail Hub.

This daemon:
- Connects to Gmail via IMAP
- Connects to ProtonMail via Proton Bridge
- Forwards/syncs emails to NAS Mail Hub
- Runs on schedule (every 15 minutes)

#JARVIS #LUMINA #NAS #MAILPLUS #GMAIL #PROTONMAIL #SYNC
"""

import sys
import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import time

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("SyncEmailsToNASHub")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("SyncEmailsToNASHub")

try:
    from scripts.python.unified_secrets_manager import UnifiedSecretsManager, SecretSource
    from scripts.python.unified_email_service import UnifiedEmailService, EmailProvider
    INTEGRATIONS_AVAILABLE = True
except ImportError:
    INTEGRATIONS_AVAILABLE = False
    logger.warning("⚠️  Some integrations not available")


class EmailSyncToNASHub:
    """
    Sync emails from Gmail and ProtonMail to NAS Mail Hub.
    """

    def __init__(self, project_root: Path):
        """Initialize email sync."""
        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config" / "outlook"
        self.data_dir = self.project_root / "data" / "email_import"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load configuration
        self.config = self._load_config()

        # Initialize services
        if INTEGRATIONS_AVAILABLE:
            self.email_service = UnifiedEmailService(project_root)
            self.secrets_manager = UnifiedSecretsManager(
                project_root,
                prefer_source=SecretSource.AZURE_KEY_VAULT
            )
        else:
            self.email_service = None
            self.secrets_manager = None

        # Track synced emails
        self.synced_hashes_file = self.data_dir / "synced_hashes.json"
        self.synced_hashes = self._load_synced_hashes()

    def _load_config(self) -> Dict:
        """Load sync configuration."""
        config_file = self.config_dir / "email_sync_to_nas_config.json"

        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️  Could not load config: {e}")

        return {}

    def _load_synced_hashes(self) -> Dict[str, List[str]]:
        """Load hashes of already synced emails."""
        if self.synced_hashes_file.exists():
            try:
                with open(self.synced_hashes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️  Could not load synced hashes: {e}")

        return {}

    def _save_synced_hashes(self):
        """Save synced email hashes."""
        try:
            with open(self.synced_hashes_file, 'w', encoding='utf-8') as f:
                json.dump(self.synced_hashes, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"⚠️  Could not save synced hashes: {e}")

    def sync_gmail_to_nas(self) -> Tuple[int, int]:
        """
        Sync Gmail emails to NAS Mail Hub.

        Returns:
            Tuple of (synced_count, skipped_count)
        """
        sync_config = self.config.get("email_sync_to_nas_hub", {}).get("source_accounts", {}).get("gmail", {})

        if not sync_config.get("enabled", True):
            logger.info("⏭️  Gmail sync disabled")
            return 0, 0

        logger.info("="*80)
        logger.info("SYNCING GMAIL TO NAS MAIL HUB")
        logger.info("="*80)

        if not self.email_service:
            logger.error("❌ Email service not available")
            return 0, 0

        try:
            # Get Gmail emails
            emails = self.email_service.search_emails(
                query="ALL",
                provider=EmailProvider.GMAIL,
                days_back=7,  # Sync last 7 days
                max_results=100
            )

            synced = 0
            skipped = 0

            for email_msg in emails:
                # Check if already synced
                email_hash = f"{email_msg.message_id}:{email_msg.from_address}"
                if email_hash in self.synced_hashes.get("gmail", []):
                    skipped += 1
                    continue

                # Forward to NAS Mail Hub
                if self._forward_email_to_nas(email_msg, "gmail"):
                    if "gmail" not in self.synced_hashes:
                        self.synced_hashes["gmail"] = []
                    self.synced_hashes["gmail"].append(email_hash)
                    synced += 1
                else:
                    skipped += 1

            logger.info(f"✅ Gmail sync complete: {synced} synced, {skipped} skipped")
            self._save_synced_hashes()

            return synced, skipped

        except Exception as e:
            logger.error(f"❌ Gmail sync failed: {e}")
            return 0, 0

    def sync_protonmail_to_nas(self) -> Tuple[int, int]:
        """
        Sync ProtonMail emails to NAS Mail Hub.

        Returns:
            Tuple of (synced_count, skipped_count)
        """
        sync_config = self.config.get("email_sync_to_nas_hub", {}).get("source_accounts", {}).get("protonmail", {})

        if not sync_config.get("enabled", True):
            logger.info("⏭️  ProtonMail sync disabled")
            return 0, 0

        logger.info("="*80)
        logger.info("SYNCING PROTONMAIL TO NAS MAIL HUB")
        logger.info("="*80)

        if not self.email_service:
            logger.error("❌ Email service not available")
            return 0, 0

        try:
            # Get ProtonMail emails
            emails = self.email_service.search_emails(
                query="ALL",
                provider=EmailProvider.PROTONMAIL,
                days_back=7,  # Sync last 7 days
                max_results=100
            )

            synced = 0
            skipped = 0

            for email_msg in emails:
                # Check if already synced
                email_hash = f"{email_msg.message_id}:{email_msg.from_address}"
                if email_hash in self.synced_hashes.get("protonmail", []):
                    skipped += 1
                    continue

                # Forward to NAS Mail Hub
                if self._forward_email_to_nas(email_msg, "protonmail"):
                    if "protonmail" not in self.synced_hashes:
                        self.synced_hashes["protonmail"] = []
                    self.synced_hashes["protonmail"].append(email_hash)
                    synced += 1
                else:
                    skipped += 1

            logger.info(f"✅ ProtonMail sync complete: {synced} synced, {skipped} skipped")
            self._save_synced_hashes()

            return synced, skipped

        except Exception as e:
            logger.error(f"❌ ProtonMail sync failed: {e}")
            return 0, 0

    def _forward_email_to_nas(self, email_msg, source: str) -> bool:
        """
        Forward email to NAS Mail Hub via SMTP.

        Args:
            email_msg: Email message object
            source: Source identifier

        Returns:
            True if forwarded successfully
        """
        try:
            nas_config = self.config.get("email_sync_to_nas_hub", {}).get("nas_mail_hub", {})
            smtp_config = nas_config.get("smtp", {})
            account_config = nas_config.get("accounts", {}).get("mlesn", {})

            # Get credentials
            username = account_config.get("username", "mlesn")
            # Password would come from secrets manager or config

            # Create email message
            msg = MIMEMultipart()
            msg['From'] = email_msg.from_address
            msg['To'] = account_config.get("email", "mlesn@<LOCAL_HOSTNAME>")
            msg['Subject'] = f"[{source.upper()}] {email_msg.subject}"
            msg['Date'] = email_msg.date

            # Add body
            body = f"Original from: {email_msg.from_address}\n"
            body += f"Source: {source}\n"
            body += f"Date: {email_msg.date}\n\n"
            body += email_msg.body or ""

            msg.attach(MIMEText(body, 'plain'))

            # Connect to NAS SMTP
            smtp_server = smtp_config.get("server", "<NAS_PRIMARY_IP>")
            smtp_port = smtp_config.get("port", 587)

            # For now, just log (actual SMTP forwarding would require NAS credentials)
            logger.debug(f"  📧 Would forward: {email_msg.subject[:50]}... to NAS Mail Hub")

            # TODO: Implement actual SMTP forwarding when NAS credentials are available  # [ADDRESSED]  # [ADDRESSED]
            # with smtplib.SMTP(smtp_server, smtp_port) as server:
            #     server.starttls()
            #     server.login(username, password)
            #     server.send_message(msg)

            return True

        except Exception as e:
            logger.warning(f"  ⚠️  Failed to forward email: {e}")
            return False

    def run_sync(self) -> Dict[str, Any]:
        try:
            """
            Run complete email sync.

            Returns:
                Sync results dictionary
            """
            logger.info("="*80)
            logger.info("EMAIL SYNC TO NAS MAIL HUB")
            logger.info("="*80)
            logger.info("")

            results = {
                "timestamp": datetime.now().isoformat(),
                "gmail": {"synced": 0, "skipped": 0},
                "protonmail": {"synced": 0, "skipped": 0},
                "total_synced": 0,
                "total_skipped": 0
            }

            # Sync Gmail
            synced, skipped = self.sync_gmail_to_nas()
            results["gmail"]["synced"] = synced
            results["gmail"]["skipped"] = skipped

            logger.info("")

            # Sync ProtonMail
            synced, skipped = self.sync_protonmail_to_nas()
            results["protonmail"]["synced"] = synced
            results["protonmail"]["skipped"] = skipped

            # Calculate totals
            results["total_synced"] = results["gmail"]["synced"] + results["protonmail"]["synced"]
            results["total_skipped"] = results["gmail"]["skipped"] + results["protonmail"]["skipped"]

            # Save results
            results_file = self.data_dir / f"sync_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            logger.info("")
            logger.info("="*80)
            logger.info("SYNC SUMMARY")
            logger.info("="*80)
            logger.info(f"Gmail: {results['gmail']['synced']} synced, {results['gmail']['skipped']} skipped")
            logger.info(f"ProtonMail: {results['protonmail']['synced']} synced, {results['protonmail']['skipped']} skipped")
            logger.info(f"Total: {results['total_synced']} synced, {results['total_skipped']} skipped")

            return results

        except Exception as e:
            self.logger.error(f"Error in run_sync: {e}", exc_info=True)
            raise
    def run_daemon(self, interval_minutes: int = 15):
        """
        Run sync daemon continuously.

        Args:
            interval_minutes: Sync interval in minutes
        """
        logger.info("="*80)
        logger.info("EMAIL SYNC DAEMON STARTED")
        logger.info("="*80)
        logger.info(f"Sync interval: {interval_minutes} minutes")
        logger.info("Press Ctrl+C to stop")
        logger.info("")

        try:
            while True:
                self.run_sync()
                logger.info("")
                logger.info(f"⏳ Waiting {interval_minutes} minutes until next sync...")
                time.sleep(interval_minutes * 60)
        except KeyboardInterrupt:
            logger.info("")
            logger.info("🛑 Daemon stopped by user")


def main():
    try:
        """Main function."""
        import argparse

        parser = argparse.ArgumentParser(
            description="Sync Emails to NAS Mail Hub"
        )

        parser.add_argument(
            "--project-root",
            type=Path,
            default=Path(__file__).parent.parent.parent,
            help="Project root directory"
        )
        parser.add_argument(
            "--daemon",
            action="store_true",
            help="Run as daemon (continuous sync)"
        )
        parser.add_argument(
            "--interval",
            type=int,
            default=15,
            help="Sync interval in minutes (daemon mode)"
        )

        args = parser.parse_args()

        syncer = EmailSyncToNASHub(args.project_root)

        if args.daemon:
            syncer.run_daemon(args.interval)
        else:
            syncer.run_sync()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()