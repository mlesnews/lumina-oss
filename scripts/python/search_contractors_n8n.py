"""
Search for HVAC contractor bids via n8n webhook or manual entry.
Simplified version that works with existing n8n setup.

#JARVIS #LUMINA #N8N
"""

import json
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
logger = logging.getLogger("search_contractors_n8n")


def search_via_n8n_webhook(contractor_names: List[str], n8n_url: str = "http://localhost:5678") -> List[Dict[str, Any]]:
    """
    Search Gmail via n8n webhook.

    Args:
        contractor_names: List of contractor names/email domains
        n8n_url: n8n instance URL

    Returns:
        List of found emails
    """
    # Build search query
    queries = []
    for name in contractor_names:
        queries.append(f'"{name}"')
        # Also try variations
        if "fletcher" in name.lower():
            queries.extend(["fletcher", "plumbing"])
        if "energy" in name.lower() or "therapy" in name.lower() or "thermal" in name.lower():
            queries.extend(["energy", "services", "therapy", "thermal"])
        if "4" in name or "four" in name.lower():
            queries.extend(["4 inch", "four inch", "4\""])

    # Add general HVAC terms
    queries.extend(["bid", "quote", "proposal", "hvac", "furnace"])

    search_query = " OR ".join(queries[:20])  # Limit query length
    search_query += " has:attachment"

    print(f"Search query: {search_query[:100]}...")

    # Try n8n webhook
    webhook_paths = [
        "/webhook/gmail-search",
        "/webhook/email-search",
        "/webhook/hvac-bid-search",
        "/webhook"
    ]

    for webhook_path in webhook_paths:
        try:
            url = f"{n8n_url}{webhook_path}"
            response = requests.post(
                url,
                json={"query": search_query, "days": 60},
                timeout=10
            )

            if response.status_code == 200:
                print(f"✓ Connected to n8n webhook: {webhook_path}")
                return response.json().get("emails", [])
            elif response.status_code == 404:
                continue  # Try next webhook
            else:
                print(f"⚠ n8n returned status {response.status_code}")

        except requests.exceptions.ConnectionError:
            print(f"✗ Cannot connect to n8n at {n8n_url}")
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

        print("="*80)
        print("SEARCHING FOR HVAC CONTRACTOR BIDS")
        print("="*80)
        print("\nContractors:")
        print("  1. Fletcher's Plumbing")
        print("  2. Therapy/Thermal Energy Services (Croquine)")
        print("  3. 4-inch contractor")
        print()

        contractor_names = [
            "Fletcher's Plumbing",
            "Fletcher Plumbing",
            "Therapy Energy Services",
            "Thermal Energy Services",
            "Croquine",
            "4 inch",
            "four inch"
        ]

        # Try n8n first
        print("Attempting to search via n8n...")
        emails = search_via_n8n_webhook(contractor_names)

        if emails:
            print(f"\n✓ Found {len(emails)} email(s) via n8n")

            # Save email list
            emails_file = data_dir / f"found_emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(emails_file, 'w') as f:
                json.dump(emails, f, indent=2, default=str)

            print(f"✓ Saved email list to: {emails_file}")
            print("\nNext: Process these emails to extract bids")
            print("Run: python scripts/python/hvac_bid_extractor.py --process-emails <file>")

        else:
            print("\n⚠ Could not find emails via n8n webhook")
            print("\n" + "="*80)
            print("ALTERNATIVE OPTIONS")
            print("="*80)
            print("\nOption 1: If you have the bid attachments downloaded:")
            print("  python scripts/python/hvac_bid_extractor.py --auto-import \\")
            print("    \"path/to/fletcher_bid.pdf\" \\")
            print("    \"path/to/energy_services_bid.pdf\" \\")
            print("    \"path/to/4inch_bid.pdf\"")
            print("\nOption 2: Enter bids interactively:")
            print("  python scripts/python/hvac_bid_importer.py --interactive")
            print("\nOption 3: Check n8n workflow directly:")
            print("  1. Open n8n interface")
            print("  2. Look for Gmail search workflow")
            print("  3. Manually trigger with search: 'fletcher OR energy OR 4 inch'")
            print("  4. Download attachments to: data/hvac_bids/attachments/")
            print("  5. Then run Option 1 above")

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()