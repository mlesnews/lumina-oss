"""
Search Gmail for HVAC Contractor Bids
Searches for Fletcher's Plumbing, Therapy/Thermal Energy Services, and 4-inch contractor.

#JARVIS #LUMINA
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from hvac_gmail_bid_search import HVACGmailBidSearcher
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def main():
    """Search for the three contractor bids."""
    project_root = Path(__file__).parent.parent.parent

    print("="*80)
    print("SEARCHING GMAIL FOR HVAC CONTRACTOR BIDS")
    print("="*80)
    print("\nSearching for:")
    print("  1. Fletcher's Plumbing")
    print("  2. Therapy/Thermal Energy Services (Croquine)")
    print("  3. 4-inch contractor")
    print()

    searcher = HVACGmailBidSearcher(project_root)

    # Build search queries - flexible to catch variations
    search_queries = [
        # Fletcher's Plumbing
        "from:fletcher",
        "subject:fletcher",
        "fletcher plumbing",

        # Therapy/Thermal Energy Services
        "therapy energy",
        "thermal energy",
        "croquine",
        "energy services",

        # 4-inch contractor
        "4 inch",
        "four inch",
        "4\"",

        # General HVAC bid terms
        "subject:bid",
        "subject:quote",
        "subject:proposal",
        "subject:hvac",
        "subject:furnace",
        "oil furnace",
        "furnace replacement"
    ]

    print("Search queries:")
    for q in search_queries[:10]:  # Show first 10
        print(f"  - {q}")
    print("  ... (and more)")
    print()

    # Search Gmail
    emails = searcher.search_gmail_via_n8n(search_queries, days_back=60)

    if not emails:
        print("\n⚠ No emails found via n8n/Gmail API.")
        print("\nAlternative options:")
        print("1. Check if n8n is running and Gmail is configured")
        print("2. Manually download attachments and use:")
        print("   python scripts/python/hvac_bid_extractor.py --auto-import <files>")
        print("3. Use interactive entry:")
        print("   python scripts/python/hvac_bid_importer.py --interactive")
        return

    print(f"\n✓ Found {len(emails)} email(s)")

    # Process and extract bids
    print("\nExtracting bid information from attachments...")
    bids = searcher.process_bid_emails(emails)

    if not bids:
        print("\n⚠ No bids extracted. Checking attachments...")
        total_attachments = sum(len(email.get('attachments', [])) for email in emails)
        print(f"  Found {total_attachments} attachment(s) total")

        if total_attachments > 0:
            print("\nAttachments found but extraction failed. Trying manual extraction...")
            # List attachments for manual processing
            for email in emails:
                print(f"\nEmail: {email.get('subject', 'No subject')}")
                print(f"From: {email.get('from', 'Unknown')}")
                for att in email.get('attachments', []):
                    print(f"  - {att.get('filename', 'Unknown')} ({att.get('path', 'N/A')})")
        return

    print(f"\n✓ Extracted {len(bids)} bid(s)")

    # Save bids
    from hvac_bid_extractor import BidExtractor
    extractor = BidExtractor(project_root)
    saved_files = extractor.save_extracted_bids(bids)

    print(f"\n✓ Saved bids:")
    for file_path in saved_files:
        print(f"    {file_path}")

    # Generate comparison
    print("\n" + "="*80)
    print("BID COMPARISON")
    print("="*80)

    from hvac_bid_comparison import HVACBidComparator
    comparator = HVACBidComparator(project_root)
    comparator.set_budget(20000)  # Max budget

    for bid in bids:
        comparator.import_bid_from_dict(bid)

    comparator.save_bids()
    comparator.print_summary()

    # Generate financial plan
    print("\n" + "="*80)
    print("GENERATING FINANCIAL PLAN")
    print("="*80)

    plan = searcher.create_financial_plan(
        bids,
        budget_range=(10000, 20000),
        liquidity_sources=None  # User can add this later
    )

    # Save plan
    from datetime import datetime
    plan_file = searcher.data_dir / f"financial_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    import json
    with open(plan_file, 'w') as f:
        json.dump(plan, f, indent=2, default=str)

    print(f"\n✓ Financial plan saved: {plan_file}")

    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("1. Review extracted bids in: data/hvac_bids/")
    print("2. Check comparison report for detailed analysis")
    print("3. Add liquidity sources to: data/hvac_bids/liquidity_sources.json")
    print("4. Review financial plan for funding strategy")

if __name__ == "__main__":


    main()