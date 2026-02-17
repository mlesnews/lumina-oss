"""
Search for Specific HVAC Bid Emails
Targeted search for:
1. Brian Fletcher - Fletcher's Heating & Plumbing
2. Carl-King| Griffet Energy Services
3. Third contractor (TBD)
Subject: "HVAC Company Bids for Furnace/AC replacement"

#JARVIS #LUMINA #N8N
"""

import json
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import logging
logger = logging.getLogger("search_specific_hvac_bids")


def create_n8n_search_queries() -> List[str]:
    """Create specific search queries for the three contractors."""
    queries = [
        # Brian Fletcher - Fletcher's Heating & Plumbing
        "from:brian.fletcher OR from:fletcher",
        "subject:\"Fletcher\" OR subject:\"Heating\" OR subject:\"Plumbing\"",
        "brian fletcher",
        "fletcher's heating",
        "fletcher's plumbing",

        # Carl-King| Griffet Energy Services
        "from:carl OR from:king OR from:griffet",
        "subject:\"Carl-King\" OR subject:\"Griffet\" OR subject:\"Energy Services\"",
        "carl-king",
        "griffet energy",

        # Specific subject line
        "subject:\"HVAC Company Bids for Furnace/AC replacement\"",
        "subject:\"Furnace/AC replacement\"",

        # Request ID
        "c1fa7198-7bf3-46ae-8865-2a67f0085988",

        # General HVAC terms
        "subject:bid OR subject:quote OR subject:proposal",
        "hvac OR furnace OR \"air conditioning\"",
        "has:attachment"
    ]
    return queries

def search_via_n8n_webhook(queries: List[str], n8n_url: str = "http://<NAS_PRIMARY_IP>:5678") -> List[Dict[str, Any]]:
    """Search via n8n webhook."""
    # Combine queries
    combined_query = " OR ".join([f"({q})" for q in queries[:15]])  # Limit length
    combined_query += " has:attachment"

    webhook_paths = [
        "/webhook/hvac-bid-search",
        "/webhook/gmail-search",
        "/webhook/email-search",
        "/webhook"
    ]

    for webhook_path in webhook_paths:
        try:
            url = f"{n8n_url}{webhook_path}"
            print(f"Trying webhook: {url}")

            response = requests.post(
                url,
                json={
                    "query": combined_query,
                    "subject": "HVAC Company Bids for Furnace/AC replacement",
                    "request_id": "c1fa7198-7bf3-46ae-8865-2a67f0085988",
                    "contractors": [
                        "Brian Fletcher - Fletcher's Heating & Plumbing",
                        "Carl-King| Griffet Energy Services"
                    ]
                },
                timeout=30
            )

            if response.status_code == 200:
                print(f"✓ Successfully connected to webhook: {webhook_path}")
                data = response.json()
                return data.get("emails", data.get("data", []))
            elif response.status_code == 404:
                continue
            else:
                print(f"⚠ Webhook returned status {response.status_code}")

        except requests.exceptions.ConnectionError:
            print(f"✗ Cannot connect to {url}")
            break
        except Exception as e:
            print(f"⚠ Error with webhook {webhook_path}: {e}")
            continue

    return []

def main():
    try:
        """Main search function."""
        project_root = Path(__file__).parent.parent.parent
        data_dir = project_root / "data" / "hvac_bids"
        data_dir.mkdir(parents=True, exist_ok=True)
        attachments_dir = data_dir / "attachments"
        attachments_dir.mkdir(parents=True, exist_ok=True)

        print("="*80)
        print("SEARCHING FOR SPECIFIC HVAC BID EMAILS")
        print("="*80)
        print("\nSearching for:")
        print("  1. Brian Fletcher - Fletcher's Heating & Plumbing")
        print("  2. Carl-King| Griffet Energy Services")
        print("  3. Third contractor (TBD)")
        print("\nSubject: 'HVAC Company Bids for Furnace/AC replacement'")
        print("Request ID: c1fa7198-7bf3-46ae-8865-2a67f0085988")
        print()

        queries = create_n8n_search_queries()

        print("Search queries:")
        for i, q in enumerate(queries[:10], 1):
            print(f"  {i}. {q}")
        print(f"  ... (total: {len(queries)} queries)")
        print()

        # Try n8n webhook
        print("Attempting to search via n8n on NAS...")
        emails = search_via_n8n_webhook(queries)

        if emails:
            print(f"\n✓ Found {len(emails)} email(s)")

            # Save email list
            emails_file = data_dir / f"found_emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(emails_file, 'w') as f:
                json.dump(emails, f, indent=2, default=str)
            print(f"✓ Saved email list to: {emails_file}")

            # Process emails
            print("\nProcessing emails and downloading attachments...")
            from hvac_gmail_bid_search import HVACGmailBidSearcher
            searcher = HVACGmailBidSearcher(project_root)
            downloaded_files = searcher.download_attachments_from_emails(emails)

            if downloaded_files:
                print(f"\n✓ Downloaded {len(downloaded_files)} attachment(s)")

                # Extract bids
                print("\nExtracting bid information...")
                bids = searcher.process_bid_emails(emails)

                if bids:
                    from hvac_bid_extractor import BidExtractor
                    extractor = BidExtractor(project_root)
                    saved_files = extractor.save_extracted_bids(bids)

                    print(f"\n✓ Extracted {len(bids)} bid(s)")

                    # Compare
                    from hvac_bid_comparison import HVACBidComparator
                    comparator = HVACBidComparator(project_root)
                    comparator.set_budget(20000)

                    for bid in bids:
                        comparator.import_bid_from_dict(bid)

                    comparator.save_bids()
                    comparator.print_summary()
            else:
                print("\n⚠ No attachments downloaded")
        else:
            print("\n⚠ No emails found via n8n webhook")
            print("\n" + "="*80)
            print("MANUAL SEARCH INSTRUCTIONS")
            print("="*80)
            print("\nSince n8n webhook isn't accessible, please:")
            print("\n1. Access Gmail directly or via n8n web interface")
            print("2. Search for:")
            print("   - From: brian.fletcher OR fletcher")
            print("   - From: carl OR king OR griffet")
            print("   - Subject: 'HVAC Company Bids for Furnace/AC replacement'")
            print("   - Request ID: c1fa7198-7bf3-46ae-8865-2a67f0085988")
            print("\n3. Download the bid attachments")
            print("4. Save to: data/hvac_bids/attachments/")
            print("\n5. Then run:")
            print("   python scripts/python/hvac_bid_extractor.py --auto-import \\")
            print("     data/hvac_bids/attachments/*.pdf \\")
            print("     --contractor-names \\")
            print("       \"Brian Fletcher - Fletcher's Heating & Plumbing\" \\")
            print("       \"Carl-King| Griffet Energy Services\" \\")
            print("       \"Third Contractor\"")

            # Update template files with correct names
            print("\n" + "="*80)
            print("UPDATING CONTRACTOR TEMPLATES")
            print("="*80)

            # Update Fletcher's template
            fletchers_file = data_dir / "fletchers_plumbing_bid.json"
            if fletchers_file.exists():
                with open(fletchers_file, 'r') as f:
                    data = json.load(f)
                data["contractor_name"] = "Brian Fletcher - Fletcher's Heating & Plumbing"
                with open(fletchers_file, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"✓ Updated: {fletchers_file.name}")

            # Update Energy Services template
            energy_file = data_dir / "energy_services_bid.json"
            if energy_file.exists():
                with open(energy_file, 'r') as f:
                    data = json.load(f)
                data["contractor_name"] = "Carl-King| Griffet Energy Services"
                with open(energy_file, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"✓ Updated: {energy_file.name}")

            print("\nTemplate files updated with correct contractor names!")

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()