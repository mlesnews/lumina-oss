"""
Check HVAC Email Status
Comprehensive check for HVAC bid emails from all contractors.

#JARVIS #LUMINA #HVAC #EMAIL-STATUS
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("CheckHVACEmailStatus")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("CheckHVACEmailStatus")

from scripts.python.unified_email_service import UnifiedEmailService, EmailProvider


class HVACEmailStatusChecker:
    """Check status of HVAC bid emails."""

    def __init__(self, project_root: Path):
        """Initialize email status checker."""
        self.project_root = Path(project_root)
        self.email_service = UnifiedEmailService(self.project_root)
        self.data_dir = self.project_root / "data" / "hvac_bids"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def check_all_contractors(self, days_back: int = 90) -> Dict[str, Any]:
        """
        Check for emails from all contractors.

        Args:
            days_back: Days to search back

        Returns:
            Status report
        """
        print("\n" + "="*80)
        print("HVAC BID EMAIL STATUS CHECK")
        print("="*80)
        print(f"Searching last {days_back} days...")
        print()

        contractors = {
            "Brian Fletcher - Fletcher's Heating & Plumbing": [
                "from:fletcher OR from:brian.fletcher",
                "subject:fletcher OR subject:heating OR subject:plumbing",
                "brian fletcher",
                "fletcher's heating",
                "fletcher's plumbing"
            ],
            "Carl-King| Griffet Energy Services": [
                "from:carl OR from:king OR from:griffet",
                "subject:\"Carl-King\" OR subject:\"Griffet\" OR subject:\"Energy Services\"",
                "carl-king",
                "griffet energy"
            ],
            "Third Contractor (4-inch)": [
                "4 inch",
                "four inch",
                "4\""
            ]
        }

        # General HVAC searches
        general_searches = [
            "subject:\"HVAC Company Bids for Furnace/AC replacement\"",
            "subject:\"Furnace/AC replacement\"",
            "hvac OR furnace OR \"air conditioning\"",
            "oil furnace replacement",
            "furnace replacement",
            "c1fa7198-7bf3-46ae-8865-2a67f0085988"  # Request ID
        ]

        status_report = {
            "check_date": datetime.now().isoformat(),
            "days_searched": days_back,
            "contractors": {},
            "general_searches": {},
            "summary": {
                "total_emails_found": 0,
                "contractors_with_emails": [],
                "contractors_without_emails": [],
                "attachments_found": 0
            }
        }

        # Check each contractor
        print("Checking contractors...")
        print("-" * 80)

        for contractor_name, queries in contractors.items():
            print(f"\n📧 {contractor_name}")

            contractor_status = {
                "contractor": contractor_name,
                "queries": queries,
                "emails_found": [],
                "total_count": 0,
                "attachments": []
            }

            for query in queries:
                try:
                    # Search Gmail
                    gmail_results = self.email_service.search_emails(
                        query=query,
                        provider=EmailProvider.GMAIL,
                        days=days_back
                    )

                    # Search ProtonMail
                    proton_results = self.email_service.search_emails(
                        query=query,
                        provider=EmailProvider.PROTONMAIL,
                        days=days_back
                    )

                    # Combine results
                    all_emails = gmail_results + proton_results

                    if all_emails:
                        contractor_status["emails_found"].extend(all_emails)
                        contractor_status["total_count"] += len(all_emails)
                        print(f"  ✅ Found {len(all_emails)} email(s) with query: {query[:50]}...")

                        # Check for attachments
                        for email in all_emails:
                            if email.get('attachments') or email.get('has_attachment'):
                                contractor_status["attachments"].append({
                                    "subject": email.get('subject', ''),
                                    "from": email.get('from', ''),
                                    "date": email.get('date', '')
                                })
                                status_report["summary"]["attachments_found"] += 1
                    else:
                        print(f"  ⚪ No emails with query: {query[:50]}...")

                except Exception as e:
                    logger.warning(f"Query '{query}' failed: {e}")
                    print(f"  ⚠️  Error with query: {e}")

            # Deduplicate emails
            seen_ids = set()
            unique_emails = []
            for email in contractor_status["emails_found"]:
                email_id = email.get('id') or email.get('message_id') or email.get('subject', '')
                if email_id not in seen_ids:
                    seen_ids.add(email_id)
                    unique_emails.append(email)

            contractor_status["emails_found"] = unique_emails
            contractor_status["total_count"] = len(unique_emails)

            status_report["contractors"][contractor_name] = contractor_status
            status_report["summary"]["total_emails_found"] += contractor_status["total_count"]

            if contractor_status["total_count"] > 0:
                status_report["summary"]["contractors_with_emails"].append(contractor_name)
                print(f"  ✅ Total: {contractor_status['total_count']} email(s), {len(contractor_status['attachments'])} with attachments")
            else:
                status_report["summary"]["contractors_without_emails"].append(contractor_name)
                print(f"  ❌ No emails found")

        # Check general searches
        print("\n" + "-" * 80)
        print("Checking general HVAC searches...")
        print("-" * 80)

        for query in general_searches:
            try:
                gmail_results = self.email_service.search_emails(
                    query=query,
                    provider=EmailProvider.GMAIL,
                    days=days_back
                )

                proton_results = self.email_service.search_emails(
                    query=query,
                    provider=EmailProvider.PROTONMAIL,
                    days=days_back
                )

                all_emails = gmail_results + proton_results

                status_report["general_searches"][query] = {
                    "count": len(all_emails),
                    "emails": all_emails[:5]  # First 5 for preview
                }

                if all_emails:
                    print(f"  ✅ '{query[:50]}...': {len(all_emails)} email(s)")
                else:
                    print(f"  ⚪ '{query[:50]}...': No emails")

            except Exception as e:
                logger.warning(f"General search '{query}' failed: {e}")
                print(f"  ⚠️  Error: {e}")

        # Print summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Total emails found: {status_report['summary']['total_emails_found']}")
        print(f"Attachments found: {status_report['summary']['attachments_found']}")
        print()

        if status_report["summary"]["contractors_with_emails"]:
            print("✅ Contractors with emails:")
            for contractor in status_report["summary"]["contractors_with_emails"]:
                count = status_report["contractors"][contractor]["total_count"]
                print(f"   - {contractor}: {count} email(s)")

        if status_report["summary"]["contractors_without_emails"]:
            print("\n❌ Contractors without emails:")
            for contractor in status_report["summary"]["contractors_without_emails"]:
                print(f"   - {contractor}")

        # Save report
        report_file = self.data_dir / f"email_status_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(status_report, f, indent=2, ensure_ascii=False, default=str)

        print(f"\n📄 Full report saved to: {report_file}")

        return status_report


def main():
    try:
        """Main function."""
        import argparse

        parser = argparse.ArgumentParser(description="Check HVAC Email Status")
        parser.add_argument("--project-root", type=Path, default=Path(__file__).parent.parent.parent)
        parser.add_argument("--days", type=int, default=90, help="Days to search back")

        args = parser.parse_args()

        checker = HVACEmailStatusChecker(args.project_root)
        checker.check_all_contractors(args.days)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()