"""
Trigger n8n on NAS to search Gmail for HVAC bid attachments.
Provides multiple methods to access n8n on the NAS.

#JARVIS #LUMINA #N8N #NAS
"""

import json
import requests
import subprocess
from pathlib import Path
from typing import Optional
import logging
logger = logging.getLogger("trigger_nas_n8n_bid_search")


def trigger_via_webhook(n8n_url: str = "http://<NAS_PRIMARY_IP>:5678") -> bool:
    """Try to trigger n8n webhook."""
    search_query = "fletcher OR plumbing OR energy OR services OR therapy OR thermal OR croquine OR \"4 inch\" OR \"four inch\" OR bid OR quote OR proposal OR hvac OR furnace has:attachment"

    webhook_url = f"{n8n_url}/webhook/hvac-bid-search"

    try:
        response = requests.post(
            webhook_url,
            json={"query": search_query},
            timeout=30
        )

        if response.status_code == 200:
            print(f"✓ Successfully triggered n8n workflow")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"⚠ n8n returned status {response.status_code}")
            print(f"Response: {response.text[:200]}")

    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to n8n at {n8n_url}")
        print("  This is normal if n8n requires authentication or is behind a firewall")
    except Exception as e:
        print(f"⚠ Error: {e}")

    return False

def provide_manual_instructions():
    """Provide instructions for manual n8n access."""
    print("\n" + "="*80)
    print("MANUAL N8N ACCESS INSTRUCTIONS")
    print("="*80)
    print("\nSince n8n on NAS may not be directly accessible, here are your options:\n")

    print("OPTION 1: Access n8n Web Interface")
    print("  1. Open browser and go to: http://<NAS_PRIMARY_IP>:5678")
    print("  2. Log in to n8n")
    print("  3. Import workflow from: config/n8n/hvac_bid_gmail_search_workflow.json")
    print("  4. Configure Gmail OAuth2 credentials in n8n")
    print("  5. Activate the workflow")
    print("  6. Trigger it manually or set up a schedule")
    print()

    print("OPTION 2: Use n8n CLI (if available on NAS)")
    print("  SSH into NAS and run:")
    print("    n8n execute --workflow=config/n8n/hvac_bid_gmail_search_workflow.json")
    print()

    print("OPTION 3: Access via NAS DSM")
    print("  1. Log into DSM: https://<NAS_PRIMARY_IP>:5001")
    print("  2. Open Docker package")
    print("  3. Find n8n container")
    print("  4. Access container terminal or logs")
    print()

    print("OPTION 4: Download Attachments Manually")
    print("  1. Access Gmail directly")
    print("  2. Search for: fletcher OR plumbing OR energy OR \"4 inch\" OR bid")
    print("  3. Download the three bid attachments")
    print("  4. Save to: data/hvac_bids/attachments/")
    print("  5. Then run:")
    print("     python scripts/python/hvac_bid_extractor.py --auto-import \\")
    print("       data/hvac_bids/attachments/*.pdf")

def main():
    try:
        """Main function."""
        print("="*80)
        print("TRIGGERING NAS N8N FOR HVAC BID SEARCH")
        print("="*80)
        print("\nn8n URL: http://<NAS_PRIMARY_IP>:5678")
        print("\nAttempting to trigger workflow...")

        # Try webhook
        success = trigger_via_webhook()

        if not success:
            provide_manual_instructions()

            # Also check if we can access the workflow file
            workflow_file = Path(__file__).parent.parent.parent / "config" / "n8n" / "hvac_bid_gmail_search_workflow.json"
            if workflow_file.exists():
                print(f"\n✓ Workflow configuration file ready: {workflow_file}")
                print("  You can import this into n8n web interface")

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()