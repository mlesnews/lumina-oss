"""
Get HVAC Bid Attachments from n8n on NAS
Accesses n8n on NAS (<NAS_PRIMARY_IP>:5678) to search Gmail and download bid attachments.

#JARVIS #LUMINA #N8N #NAS
"""

import json
import requests
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("GetHVACBidsFromNASN8N")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("GetHVACBidsFromNASN8N")


class NASN8NBidRetriever:
    """Retrieve HVAC bid attachments from n8n on NAS."""

    def __init__(self, project_root: Path):
        """
        Initialize NAS n8n bid retriever.

        Args:
            project_root: Root path of the LUMINA project
        """
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "hvac_bids"
        self.attachments_dir = self.data_dir / "attachments"
        self.attachments_dir.mkdir(parents=True, exist_ok=True)

        # Load n8n config
        config_file = self.project_root / "config" / "n8n" / "unified_communications_config.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
                self.n8n_url = config.get("n8n_config", {}).get("n8n_url", "http://<NAS_PRIMARY_IP>:5678")
        else:
            self.n8n_url = os.getenv("N8N_URL", "http://<NAS_PRIMARY_IP>:5678")

        logger.info(f"Using n8n at: {self.n8n_url}")

    def check_n8n_connection(self) -> bool:
        """
        Check if n8n is accessible.

        Returns:
            True if n8n is accessible
        """
        try:
            # Try health endpoint
            response = requests.get(f"{self.n8n_url}/healthz", timeout=5)
            if response.status_code == 200:
                logger.info("✓ n8n is accessible")
                return True

            # Try root endpoint
            response = requests.get(self.n8n_url, timeout=5)
            if response.status_code in [200, 302, 401]:  # 401 is OK, means it's there
                logger.info("✓ n8n is accessible")
                return True

        except requests.exceptions.ConnectionError:
            logger.error(f"✗ Cannot connect to n8n at {self.n8n_url}")
            return False
        except Exception as e:
            logger.warning(f"⚠ Error checking n8n: {e}")
            return False

        return False

    def search_gmail_via_n8n_api(self, search_query: str) -> List[Dict[str, Any]]:
        """
        Search Gmail via n8n API.

        Args:
            search_query: Gmail search query

        Returns:
            List of email data
        """
        # Try n8n REST API
        try:
            # First, try to get workflows
            workflows_url = f"{self.n8n_url}/api/v1/workflows"
            response = requests.get(workflows_url, timeout=10)

            if response.status_code == 200:
                workflows = response.json()
                logger.info(f"Found {len(workflows.get('data', []))} workflows")

                # Look for Gmail search workflow
                gmail_workflow = None
                for workflow in workflows.get('data', []):
                    name = workflow.get('name', '').lower()
                    if 'gmail' in name or 'email' in name or 'search' in name:
                        gmail_workflow = workflow
                        break

                if gmail_workflow:
                    logger.info(f"Found workflow: {gmail_workflow.get('name')}")
                    # Try to execute it
                    execute_url = f"{self.n8n_url}/api/v1/workflows/{gmail_workflow['id']}/execute"
                    response = requests.post(
                        execute_url,
                        json={"query": search_query},
                        timeout=30
                    )
                    if response.status_code == 200:
                        return response.json().get('data', [])

        except Exception as e:
            logger.warning(f"n8n API access failed: {e}, trying webhook method")

        return []

    def search_via_webhook(self, search_query: str) -> List[Dict[str, Any]]:
        """
        Search Gmail via n8n webhook.

        Args:
            search_query: Gmail search query

        Returns:
            List of email data
        """
        webhook_paths = [
            "/webhook/gmail-search",
            "/webhook/email-search",
            "/webhook/hvac-bid-search",
            "/webhook/gmail",
            "/webhook"
        ]

        for webhook_path in webhook_paths:
            try:
                url = f"{self.n8n_url}{webhook_path}"
                logger.info(f"Trying webhook: {url}")

                response = requests.post(
                    url,
                    json={"query": search_query, "days": 60},
                    timeout=30
                )

                if response.status_code == 200:
                    logger.info(f"✓ Successfully connected to webhook: {webhook_path}")
                    data = response.json()
                    return data.get("emails", data.get("data", []))
                elif response.status_code == 404:
                    continue  # Try next webhook
                else:
                    logger.warning(f"Webhook returned status {response.status_code}")

            except requests.exceptions.ConnectionError:
                logger.error(f"✗ Cannot connect to {url}")
                break
            except Exception as e:
                logger.debug(f"Webhook {webhook_path} error: {e}")
                continue

        return []

    def download_attachments_from_emails(self, emails: List[Dict[str, Any]]) -> List[Path]:
        """
        Download attachments from email data.

        Args:
            emails: List of email dictionaries with attachment info

        Returns:
            List of downloaded file paths
        """
        downloaded_files = []

        for email in emails:
            attachments = email.get('attachments', [])
            if not attachments:
                # Try to get attachments from email structure
                if 'payload' in email:
                    attachments = self._extract_attachments_from_payload(email['payload'])

            for att in attachments:
                try:
                    # Get attachment data
                    if 'data' in att:
                        # Base64 encoded data
                        import base64
                        file_data = base64.b64decode(att['data'])
                    elif 'path' in att:
                        # Already downloaded, just record path
                        downloaded_files.append(Path(att['path']))
                        continue
                    elif 'url' in att:
                        # Download from URL
                        response = requests.get(att['url'], timeout=30)
                        file_data = response.content
                    else:
                        logger.warning(f"No attachment data found for {att.get('filename', 'unknown')}")
                        continue

                    # Save file
                    filename = att.get('filename', f"attachment_{datetime.now().timestamp()}")
                    file_path = self.attachments_dir / filename

                    # Avoid overwriting
                    counter = 1
                    original_path = file_path
                    while file_path.exists():
                        stem = original_path.stem
                        suffix = original_path.suffix
                        file_path = self.attachments_dir / f"{stem}_{counter}{suffix}"
                        counter += 1

                    with open(file_path, 'wb') as f:
                        f.write(file_data)

                    downloaded_files.append(file_path)
                    logger.info(f"✓ Downloaded: {filename}")

                except Exception as e:
                    logger.error(f"Error downloading attachment: {e}")

        return downloaded_files

    def _extract_attachments_from_payload(self, payload: Dict) -> List[Dict]:
        """Extract attachment info from Gmail payload structure."""
        attachments = []

        def process_part(part):
            if part.get('filename'):
                attachments.append({
                    'filename': part['filename'],
                    'mimeType': part.get('mimeType', ''),
                    'attachmentId': part.get('body', {}).get('attachmentId')
                })
            if 'parts' in part:
                for subpart in part['parts']:
                    process_part(subpart)

        if 'parts' in payload:
            for part in payload['parts']:
                process_part(part)
        else:
            process_part(payload)

        return attachments

    def search_and_download_bids(self) -> List[Path]:
        try:
            """
            Search for HVAC bid emails and download attachments.

            Returns:
                List of downloaded attachment file paths
            """
            print("="*80)
            print("SEARCHING FOR HVAC BID ATTACHMENTS VIA NAS N8N")
            print("="*80)
            print(f"\nn8n URL: {self.n8n_url}")

            # Check connection
            if not self.check_n8n_connection():
                print("\n⚠ Cannot connect to n8n. Please check:")
                print(f"  1. n8n is running on NAS at {self.n8n_url}")
                print("  2. Network connectivity to NAS")
                print("  3. Firewall settings")
                return []

            # Build search query
            search_terms = [
                "fletcher",
                "plumbing",
                "therapy energy",
                "thermal energy",
                "croquine",
                "4 inch",
                "four inch",
                "bid",
                "quote",
                "proposal",
                "hvac",
                "furnace"
            ]

            search_query = " OR ".join(search_terms[:10])  # Limit query length
            search_query += " has:attachment"

            print(f"\nSearch query: {search_query}")
            print("\nSearching Gmail via n8n...")

            # Try API first
            emails = self.search_gmail_via_n8n_api(search_query)

            # Fall back to webhook
            if not emails:
                print("Trying webhook method...")
                emails = self.search_via_webhook(search_query)

            if not emails:
                print("\n⚠ No emails found via n8n.")
                print("\nAlternative: Use n8n web interface to:")
                print("  1. Open n8n at:", self.n8n_url)
                print("  2. Find Gmail workflow")
                print("  3. Manually trigger with search query")
                print("  4. Download attachments to:", self.attachments_dir)
                return []

            print(f"\n✓ Found {len(emails)} email(s)")

            # Download attachments
            print("\nDownloading attachments...")
            downloaded_files = self.download_attachments_from_emails(emails)

            if downloaded_files:
                print(f"\n✓ Downloaded {len(downloaded_files)} attachment(s):")
                for file_path in downloaded_files:
                    print(f"    {file_path}")

                # Save email metadata
                emails_file = self.data_dir / f"found_emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(emails_file, 'w') as f:
                    json.dump(emails, f, indent=2, default=str)
                print(f"\n✓ Saved email metadata to: {emails_file}")
            else:
                print("\n⚠ No attachments downloaded")
                print("Email data structure may be different. Check email metadata file.")

            return downloaded_files


        except Exception as e:
            self.logger.error(f"Error in search_and_download_bids: {e}", exc_info=True)
            raise
def main():
    try:
        """Main function."""
        import argparse

        parser = argparse.ArgumentParser(description="Get HVAC Bids from NAS n8n")
        parser.add_argument("--project-root", type=Path,
                           default=Path(__file__).parent.parent.parent,
                           help="Project root directory")
        parser.add_argument("--n8n-url", type=str,
                           help="n8n URL (default: from config or http://<NAS_PRIMARY_IP>:5678)")
        parser.add_argument("--extract-bids", action="store_true",
                           help="Automatically extract bid info from downloaded files")

        args = parser.parse_args()

        retriever = NASN8NBidRetriever(args.project_root)

        if args.n8n_url:
            retriever.n8n_url = args.n8n_url

        # Search and download
        downloaded_files = retriever.search_and_download_bids()

        # Extract bids if requested
        if args.extract_bids and downloaded_files:
            print("\n" + "="*80)
            print("EXTRACTING BID INFORMATION")
            print("="*80)

            from hvac_bid_extractor import BidExtractor
            extractor = BidExtractor(args.project_root)

            contractor_names = [
                "Fletcher's Plumbing",
                "Therapy Energy Services",
                "4-inch Contractor"
            ]

            bids = []
            for i, file_path in enumerate(downloaded_files[:3]):
                contractor_name = contractor_names[i] if i < len(contractor_names) else None
                bid_data = extractor.extract_from_file(file_path, contractor_name)
                if bid_data:
                    bids.append(bid_data)

            if bids:
                saved_files = extractor.save_extracted_bids(bids)
                print(f"\n✓ Extracted {len(bids)} bid(s)")

                # Compare
                from hvac_bid_comparison import HVACBidComparator
                comparator = HVACBidComparator(args.project_root)
                comparator.set_budget(20000)

                for bid in bids:
                    comparator.import_bid_from_dict(bid)

                comparator.save_bids()
                comparator.print_summary()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()