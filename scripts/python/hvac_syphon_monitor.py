"""
HVAC Bid @SYPHON Monitor
Continuously monitors and extracts all HVAC-related intelligence using @SYPHON,
focusing on the other two contractors (besides Brian Fletcher).

#JARVIS #LUMINA #SYPHON #HVAC #MONITORING
"""

import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("HVACSyphonMonitor")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("HVACSyphonMonitor")

try:
    from syphon import SYPHONSystem, SYPHONConfig, SubscriptionTier, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    logger.warning("SYPHON system not available")

from lumina_gmail_integration_system import LUMINAGmailIntegration
from unified_email_service import UnifiedEmailService, EmailProvider
from hvac_bid_extractor import BidExtractor
from hvac_bid_comparison import HVACBidComparator


class HVACSyphonMonitor:
    """
    Continuous HVAC bid monitoring using @SYPHON.

    Monitors emails from:
    - Carl-King| Griffet Energy Services
    - Third contractor (TBD)

    Excludes: Brian Fletcher (already processed)
    """

    def __init__(self, project_root: Path):
        """
        Initialize HVAC SYPHON Monitor.

        Args:
            project_root: Root path of LUMINA project
        """
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "hvac_bids"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.syphon_data_dir = self.data_dir / "syphon_extracted"
        self.syphon_data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize SYPHON
        if SYPHON_AVAILABLE:
            syphon_config = SYPHONConfig(
                project_root=self.project_root,
                subscription_tier=SubscriptionTier.ENTERPRISE,
                enable_self_healing=True
            )
            self.syphon = SYPHONSystem(syphon_config)
        else:
            self.syphon = None
            logger.warning("SYPHON not available, using basic extraction")

        # Initialize unified email service (Gmail + ProtonMail)
        self.email_service = UnifiedEmailService(self.project_root)
        # Keep Gmail system for backward compatibility
        self.gmail_system = LUMINAGmailIntegration(self.project_root)

        # Initialize comprehensive @SYPHON system
        try:
            from scripts.python.lumina_comprehensive_syphon_system import LuminaComprehensiveSyphonSystem
            self.comprehensive_syphon = LuminaComprehensiveSyphonSystem(self.project_root)
            logger.info("✅ Comprehensive @SYPHON System initialized")
        except Exception as e:
            self.comprehensive_syphon = None
            logger.warning(f"⚠️  Comprehensive @SYPHON System not available: {e}")

        # Initialize bid systems
        self.bid_extractor = BidExtractor(self.project_root)
        self.bid_comparator = HVACBidComparator(self.project_root)
        self.bid_comparator.set_budget(20000)

        # Contractors to monitor (excluding Brian Fletcher)
        self.contractors_to_monitor = [
            "Carl-King| Griffet Energy Services",
            "Carl-King",
            "Griffet Energy Services",
            "Griffet",
            "Energy Services"
        ]

        # Third contractor (will be identified)
        self.third_contractor_patterns = [
            "4 inch",
            "four inch",
            "4\""
        ]

        logger.info("✅ HVAC SYPHON Monitor initialized")
        logger.info(f"Monitoring contractors: {', '.join(self.contractors_to_monitor)}")

    def syphon_hvac_emails(self, days_back: int = 60) -> List[Dict[str, Any]]:
        """
        @SYPHON all HVAC-related emails.

        Args:
            days_back: Days to search back

        Returns:
            List of SYPHON-extracted data
        """
        logger.info("="*80)
        logger.info("@SYPHON: EXTRACTING ALL HVAC INTELLIGENCE")
        logger.info("="*80)

        # Build search queries (excluding Brian Fletcher)
        search_queries = [
            # Carl-King| Griffet Energy Services
            "from:carl OR from:king OR from:griffet",
            "subject:\"Carl-King\" OR subject:\"Griffet\" OR subject:\"Energy Services\"",
            "carl-king OR griffet energy",

            # Third contractor
            "4 inch OR four inch OR 4\"",

            # HVAC general terms
            "subject:\"HVAC Company Bids for Furnace/AC replacement\"",
            "subject:\"Furnace/AC replacement\"",
            "hvac OR furnace OR \"air conditioning\"",
            "oil furnace replacement",
            "furnace replacement",

            # Request ID
            "c1fa7198-7bf3-46ae-8865-2a67f0085988",

            # Exclude Brian Fletcher
            "-from:fletcher -subject:fletcher"
        ]

        all_syphon_data = []

        for query in search_queries:
            logger.info(f"@SYPHON searching: {query}")

            # Search unified email service (Gmail + ProtonMail)
            unified_emails = self.email_service.search_emails(
                query=query,
                provider=EmailProvider.UNIFIED,  # Search both Gmail and ProtonMail
                days_back=days_back,
                max_results=50
            )

            # Also search Gmail directly for backward compatibility
            gmail_emails = self.gmail_system.search_gmail(query, max_results=50, days_back=days_back)

            # Combine results (unified emails are already from both providers)
            all_emails = unified_emails

            # Process unified emails
            for unified_email in all_emails:
                # Skip if from Brian Fletcher
                if "fletcher" in unified_email.from_address.lower():
                    continue

                # @SYPHON extract intelligence
                if self.syphon:
                    try:
                        # Get full email data
                        email_data = {
                            "id": unified_email.message_id,
                            "subject": unified_email.subject,
                            "from": unified_email.from_address,
                            "to": unified_email.to_address,
                            "date": unified_email.date,
                            "body": unified_email.body or "",
                            "provider": unified_email.provider.value
                        }

                        # Extract with SYPHON
                        result = self.syphon.extract_email(
                            email_id=unified_email.message_id,
                            subject=unified_email.subject,
                            body=email_data.get("body", ""),
                            from_address=unified_email.from_address,
                            to_address=unified_email.to_address,
                            metadata={
                                "category": unified_email.category or "information",
                                "priority": unified_email.priority,
                                "provider": unified_email.provider.value,
                                "tags": []
                            }
                        )

                        if result.success and result.data:
                            syphon_entry = {
                                "email_id": unified_email.message_id,
                                "provider": unified_email.provider.value,
                                "subject": unified_email.subject,
                                "from": unified_email.from_address,
                                "date": unified_email.date,
                                "syphon_data": result.data.to_dict(),
                                "actionable_items": len(result.data.actionable_items),
                                "tasks": len(result.data.tasks),
                                "decisions": len(result.data.decisions),
                                "intelligence": len(result.data.intelligence),
                                "extracted_at": datetime.now().isoformat()
                            }

                            all_syphon_data.append(syphon_entry)

                            # Save SYPHON data
                            self._save_syphon_data(syphon_entry)

                            logger.info(f"✓ @SYPHON extracted: {email_metadata.subject[:50]}... "
                                      f"({len(result.data.actionable_items)} actionable, "
                                      f"{len(result.data.tasks)} tasks, "
                                      f"{len(result.data.intelligence)} intelligence)")
                    except Exception as e:
                        logger.error(f"Error @SYPHON extracting {email_metadata.email_id}: {e}")

                # Also extract bid information
                self._extract_bid_from_email(email_metadata, email_data)

        logger.info(f"\n✓ @SYPHON extracted intelligence from {len(all_syphon_data)} email(s)")
        return all_syphon_data

    def _save_syphon_data(self, syphon_entry: Dict[str, Any]) -> None:
        try:
            """Save SYPHON-extracted data."""
            entry_file = self.syphon_data_dir / f"syphon_{syphon_entry['email_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(entry_file, 'w') as f:
                json.dump(syphon_entry, f, indent=2, default=str)

        except Exception as e:
            self.logger.error(f"Error in _save_syphon_data: {e}", exc_info=True)
            raise
    def _extract_bid_from_email(self, email_metadata, email_data: Dict[str, Any]) -> None:
        """Extract bid information from email."""
        # Try to identify contractor
        contractor_name = None
        from_addr = email_metadata.from_address.lower()

        if any(term in from_addr for term in ["carl", "king", "griffet", "energy"]):
            contractor_name = "Carl-King| Griffet Energy Services"
        elif any(term in email_metadata.subject.lower() for term in self.third_contractor_patterns):
            contractor_name = "Third Contractor (4-inch)"

        # Extract bid data
        if email_data.get("body"):
            bid_data = self.bid_extractor.extract_from_text(
                email_data["body"],
                contractor_name
            )

            if bid_data and bid_data.get("total_cost"):
                # Add email metadata
                bid_data["source_email"] = email_metadata.from_address
                bid_data["email_subject"] = email_metadata.subject
                bid_data["email_date"] = email_metadata.date
                bid_data["request_id"] = email_metadata.request_id

                # Import into comparison system
                self.bid_comparator.import_bid_from_dict(bid_data)
                logger.info(f"✓ Extracted bid from {contractor_name or 'Unknown'}: ${bid_data.get('total_cost', 0):,.2f}")

    def start_continuous_monitoring(self, check_interval_minutes: int = 15) -> None:
        """
        Start continuous monitoring for new emails.

        Args:
            check_interval_minutes: Minutes between checks
        """
        logger.info("="*80)
        logger.info("STARTING CONTINUOUS HVAC EMAIL MONITORING")
        logger.info("="*80)
        logger.info(f"Monitoring contractors: {', '.join(self.contractors_to_monitor)}")
        logger.info(f"Check interval: {check_interval_minutes} minutes")
        logger.info("Excluding: Brian Fletcher (already processed)")
        logger.info("\nMonitoring started. Press Ctrl+C to stop.")

        last_check = datetime.now()

        try:
            while True:
                # Check for new emails
                time_since_last_check = (datetime.now() - last_check).total_seconds() / 60

                if time_since_last_check >= check_interval_minutes:
                    logger.info(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking for new emails...")

                    # @SYPHON new emails
                    new_data = self.syphon_hvac_emails(days_back=1)  # Check last 24 hours

                    if new_data:
                        logger.info(f"✓ Found {len(new_data)} new email(s) with HVAC intelligence")

                        # Save updated comparison
                        self.bid_comparator.save_bids()

                        # Generate updated report if we have bids
                        if len(self.bid_comparator.bids) >= 2:
                            report_path = self.bid_comparator.generate_report()
                            logger.info(f"✓ Updated comparison report: {report_path}")
                    else:
                        logger.info("  No new emails found")

                    last_check = datetime.now()

                # Sleep for 1 minute before checking again
                time.sleep(60)

        except KeyboardInterrupt:
            logger.info("\n\nMonitoring stopped by user")
            self._save_monitoring_status()

    def _save_monitoring_status(self) -> None:
        try:
            """Save monitoring status."""
            status = {
                "last_check": datetime.now().isoformat(),
                "contractors_monitored": self.contractors_to_monitor,
                "total_bids": len(self.bid_comparator.bids),
                "status": "monitoring_active"
            }

            status_file = self.data_dir / "monitoring_status.json"
            with open(status_file, 'w') as f:
                json.dump(status, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_monitoring_status: {e}", exc_info=True)
            raise
    def syphon_all_existing_hvac(self) -> Dict[str, Any]:
        try:
            """
            @SYPHON all existing HVAC emails (one-time extraction).

            Returns:
                Summary of extracted data
            """
            logger.info("="*80)
            logger.info("@SYPHON: EXTRACTING ALL EXISTING HVAC INTELLIGENCE")
            logger.info("="*80)

            # Extract all HVAC emails
            syphon_data = self.syphon_hvac_emails(days_back=90)

            # Save summary
            summary = {
                "extraction_date": datetime.now().isoformat(),
                "total_emails_syphoned": len(syphon_data),
                "contractors_monitored": self.contractors_to_monitor,
                "total_actionable_items": sum(d.get("actionable_items", 0) for d in syphon_data),
                "total_tasks": sum(d.get("tasks", 0) for d in syphon_data),
                "total_decisions": sum(d.get("decisions", 0) for d in syphon_data),
                "total_intelligence": sum(d.get("intelligence", 0) for d in syphon_data),
                "bids_extracted": len(self.bid_comparator.bids),
                "syphon_entries": syphon_data
            }

            summary_file = self.data_dir / f"syphon_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2, default=str)

            logger.info(f"\n✓ @SYPHON Summary saved: {summary_file}")
            logger.info(f"  Total emails: {len(syphon_data)}")
            logger.info(f"  Total actionable items: {summary['total_actionable_items']}")
            logger.info(f"  Total tasks: {summary['total_tasks']}")
            logger.info(f"  Total decisions: {summary['total_decisions']}")
            logger.info(f"  Total intelligence: {summary['total_intelligence']}")
            logger.info(f"  Bids extracted: {summary['bids_extracted']}")

            # Generate comparison if we have bids
            if len(self.bid_comparator.bids) >= 2:
                logger.info("\nGenerating bid comparison...")
                self.bid_comparator.save_bids()
                self.bid_comparator.print_summary()

                report_path = self.bid_comparator.generate_report()
                logger.info(f"\n✓ Comparison report: {report_path}")

            return summary


        except Exception as e:
            self.logger.error(f"Error in syphon_all_existing_hvac: {e}", exc_info=True)
            raise
def main():
    try:
        """Main function for CLI usage."""
        import argparse

        parser = argparse.ArgumentParser(description="HVAC @SYPHON Monitor")
        parser.add_argument("--project-root", type=Path,
                           default=Path(__file__).parent.parent.parent,
                           help="Project root directory")
        parser.add_argument("--syphon-all", action="store_true",
                           help="@SYPHON all existing HVAC emails")
        parser.add_argument("--monitor", action="store_true",
                           help="Start continuous monitoring")
        parser.add_argument("--check-interval", type=int, default=15,
                           help="Check interval in minutes (default: 15)")
        parser.add_argument("--days-back", type=int, default=60,
                           help="Days to search back (default: 60)")

        args = parser.parse_args()

        monitor = HVACSyphonMonitor(args.project_root)

        if args.syphon_all:
            summary = monitor.syphon_all_existing_hvac()
            print(f"\n✓ @SYPHON complete: {summary['total_emails_syphoned']} emails processed")

        if args.monitor:
            monitor.start_continuous_monitoring(args.check_interval)

        if not args.syphon_all and not args.monitor:
            # Default: syphon all
            summary = monitor.syphon_all_existing_hvac()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()