"""
Get Brian Fletcher's Bid from N8N Email Hub
Uses configured N8N on NAS to retrieve Brian's email and attachment.

#JARVIS #LUMINA #N8N #NAS #BRIAN-FLETCHER
"""

import json
import requests
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("GetBrianBidFromN8N")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("GetBrianBidFromN8N")

from scripts.python.integrate_hook_trace import hook_trace, OperationType, TraceLevel


class N8NEmailHubClient:
    """Client for N8N Email Hub on NAS."""

    def __init__(self, project_root: Path):
        """
        Initialize N8N Email Hub client.

        Args:
            project_root: Project root directory
        """
        self.project_root = Path(project_root)
        self.n8n_url = "http://<NAS_PRIMARY_IP>:5678"
        self.data_dir = self.project_root / "data" / "hvac_bids"
        self.attachments_dir = self.data_dir / "attachments"
        self.attachments_dir.mkdir(parents=True, exist_ok=True)

        hook_trace.trace(
            operation_type=OperationType.N8N,
            operation_name="n8n_email_hub_init",
            level=TraceLevel.INFO,
            message="Initialized N8N Email Hub client",
            metadata={"n8n_url": self.n8n_url}
        )

    def search_brian_email(self) -> List[Dict[str, Any]]:
        """
        Search for Brian Fletcher's email via N8N.

        Returns:
            List of email data
        """
        hook_trace.trace(
            operation_type=OperationType.EMAIL,
            operation_name="search_brian_email",
            level=TraceLevel.INFO,
            message="Searching for Brian Fletcher's email via N8N"
        )

        logger.info("="*80)
        logger.info("SEARCHING FOR BRIAN FLETCHER'S EMAIL VIA N8N")
        logger.info("="*80)
        logger.info(f"N8N URL: {self.n8n_url}")
        logger.info("")

        # Search queries for Brian
        search_queries = [
            "from:fletcher OR from:brian.fletcher",
            "subject:fletcher OR subject:heating OR subject:plumbing",
            "brian fletcher",
            "fletcher's heating",
            "fletcher's plumbing",
            "subject:\"HVAC Company Bids for Furnace/AC replacement\"",
            "c1fa7198-7bf3-46ae-8865-2a67f0085988"
        ]

        all_emails = []

        # Try N8N REST API
        try:
            # Get workflows
            workflows_url = f"{self.n8n_url}/api/v1/workflows"
            response = requests.get(workflows_url, timeout=10)

            if response.status_code == 200:
                workflows = response.json()
                logger.info(f"✅ Found {len(workflows.get('data', []))} workflows")

                # Find Gmail/email workflow
                email_workflow = None
                for workflow in workflows.get('data', []):
                    name = workflow.get('name', '').lower()
                    if any(term in name for term in ['gmail', 'email', 'search', 'hvac']):
                        email_workflow = workflow
                        logger.info(f"✅ Found email workflow: {workflow.get('name')}")
                        break

                if email_workflow:
                    # Execute workflow with search query
                    for query in search_queries:
                        try:
                            execute_url = f"{self.n8n_url}/api/v1/workflows/{email_workflow['id']}/execute"
                            response = requests.post(
                                execute_url,
                                json={"query": query, "has_attachment": True},
                                timeout=30
                            )

                            if response.status_code == 200:
                                result = response.json()
                                emails = result.get('data', [])
                                if emails:
                                    all_emails.extend(emails)
                                    logger.info(f"✅ Found {len(emails)} emails with query: {query}")
                        except Exception as e:
                            logger.debug(f"Query '{query}' failed: {e}")

        except Exception as e:
            logger.warning(f"N8N API access failed: {e}, trying webhook method")

        # Try webhook method
        if not all_emails:
            webhook_paths = [
                "/webhook/gmail-search",
                "/webhook/email-search",
                "/webhook/hvac-bid-search",
                "/webhook"
            ]

            for webhook_path in webhook_paths:
                try:
                    url = f"{self.n8n_url}{webhook_path}"
                    logger.info(f"Trying webhook: {url}")

                    response = requests.post(
                        url,
                        json={
                            "query": "from:fletcher OR brian fletcher OR fletcher's heating",
                            "subject": "HVAC Company Bids for Furnace/AC replacement",
                            "has_attachment": True,
                            "request_id": "c1fa7198-7bf3-46ae-8865-2a67f0085988"
                        },
                        timeout=30
                    )

                    if response.status_code == 200:
                        logger.info(f"✅ Successfully connected to webhook: {webhook_path}")
                        data = response.json()
                        all_emails = data.get("emails", data.get("data", []))
                        break
                    elif response.status_code == 404:
                        continue

                except requests.exceptions.ConnectionError:
                    logger.error(f"❌ Cannot connect to {url}")
                    break
                except Exception as e:
                    logger.debug(f"Webhook {webhook_path} error: {e}")
                    continue

        # Filter for Brian's emails
        brian_emails = []
        for email in all_emails:
            from_addr = email.get('from', '').lower()
            subject = email.get('subject', '').lower()

            if any(term in from_addr or term in subject for term in ['fletcher', 'brian']):
                brian_emails.append(email)

        if brian_emails:
            logger.info(f"✅ Found {len(brian_emails)} email(s) from Brian Fletcher")
            hook_trace.trace(
                operation_type=OperationType.EMAIL,
                operation_name="search_brian_email",
                level=TraceLevel.INFO,
                message=f"Found {len(brian_emails)} emails from Brian",
                success=True,
                metadata={"email_count": len(brian_emails)}
            )
        else:
            logger.warning("⚠️  No emails found from Brian Fletcher")
            hook_trace.trace(
                operation_type=OperationType.EMAIL,
                operation_name="search_brian_email",
                level=TraceLevel.WARNING,
                message="No emails found from Brian Fletcher",
                success=False
            )

        return brian_emails

    def download_attachment(self, email: Dict[str, Any]) -> Optional[Path]:
        """
        Download attachment from email.

        Args:
            email: Email data dictionary

        Returns:
            Path to downloaded file or None
        """
        attachments = email.get('attachments', [])
        if not attachments:
            # Try to extract from email structure
            if 'payload' in email:
                attachments = self._extract_attachments_from_payload(email['payload'])

        if not attachments:
            logger.warning("No attachments found in email")
            return None

        # Download first attachment (should be the bid)
        attachment = attachments[0]

        try:
            # Get attachment data
            if 'data' in attachment:
                import base64
                file_data = base64.b64decode(attachment['data'])
            elif 'path' in attachment:
                return Path(attachment['path'])
            elif 'url' in attachment:
                response = requests.get(attachment['url'], timeout=30)
                file_data = response.content
            else:
                logger.error("No attachment data found")
                return None

            # Save file
            filename = attachment.get('filename', f"brian_fletcher_bid_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            file_path = self.attachments_dir / filename

            with open(file_path, 'wb') as f:
                f.write(file_data)

            logger.info(f"✅ Downloaded attachment: {filename}")
            hook_trace.trace(
                operation_type=OperationType.FILE,
                operation_name="download_brian_attachment",
                level=TraceLevel.INFO,
                message=f"Downloaded Brian's bid attachment: {filename}",
                success=True,
                metadata={"filename": filename}
            )

            return file_path

        except Exception as e:
            logger.error(f"Failed to download attachment: {e}")
            hook_trace.trace(
                operation_type=OperationType.FILE,
                operation_name="download_brian_attachment",
                level=TraceLevel.ERROR,
                message="Failed to download attachment",
                error=str(e)
            )
            return None

    def _extract_attachments_from_payload(self, payload: Dict) -> List[Dict]:
        """Extract attachment info from email payload."""
        attachments = []

        def process_part(part):
            if part.get('filename'):
                attachments.append({
                    'filename': part['filename'],
                    'mimeType': part.get('mimeType', ''),
                    'attachmentId': part.get('body', {}).get('attachmentId'),
                    'data': part.get('body', {}).get('data')
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

    def get_brian_bid(self) -> Dict[str, Any]:
        try:
            """
            Get Brian's bid: search email, download attachment, extract data.

            Returns:
                Complete bid data with analysis
            """
            logger.info("="*80)
            logger.info("GETTING BRIAN FLETCHER'S BID FROM N8N EMAIL HUB")
            logger.info("="*80)
            logger.info("")

            # Search for email
            emails = self.search_brian_email()

            if not emails:
                return {
                    "error": "No emails found from Brian Fletcher",
                    "suggestion": "Check N8N web interface or Gmail directly"
                }

            # Get first email (most recent)
            brian_email = emails[0]

            # Extract email summary
            email_summary = {
                "from": brian_email.get('from', ''),
                "subject": brian_email.get('subject', ''),
                "date": brian_email.get('date', ''),
                "body": brian_email.get('body', brian_email.get('textBody', '')),
                "snippet": brian_email.get('snippet', '')
            }

            logger.info("")
            logger.info("EMAIL SUMMARY")
            logger.info("-" * 80)
            logger.info(f"From: {email_summary['from']}")
            logger.info(f"Subject: {email_summary['subject']}")
            logger.info(f"Date: {email_summary['date']}")
            logger.info("")

            # Download attachment
            attachment_path = self.download_attachment(brian_email)

            if not attachment_path:
                return {
                    "email_summary": email_summary,
                    "error": "No attachment found or download failed"
                }

            # Extract bid data
            logger.info("")
            logger.info("EXTRACTING BID DATA FROM ATTACHMENT")
            logger.info("-" * 80)

            from scripts.python.hvac_bid_extractor import BidExtractor
            extractor = BidExtractor(self.project_root)

            bid_data = extractor.extract_from_file(attachment_path, "Brian Fletcher - Fletcher's Heating & Plumbing")

            if not bid_data:
                return {
                    "email_summary": email_summary,
                    "attachment_path": str(attachment_path),
                    "error": "Failed to extract bid data from attachment"
                }

            # Save extracted bid
            bid_file = self.data_dir / "fletchers_plumbing_bid.json"
            with open(bid_file, 'w') as f:
                json.dump(bid_data, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Bid data extracted and saved to: {bid_file}")

            # Analyze with HVAC SME
            logger.info("")
            logger.info("HVAC SME ANALYSIS")
            logger.info("-" * 80)

            from scripts.python.hvac_sme_analysis import HVACSMEAnalyzer
            analyzer = HVACSMEAnalyzer(self.project_root)

            analysis = analyzer.analyze_bid(bid_data, "Brian Fletcher - Fletcher's Heating & Plumbing")

            # Print analysis
            analyzer.print_analysis(analysis)

            # Save analysis
            analysis_file = self.data_dir / f"brian_fletcher_sme_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(analysis_file, 'w') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)

            logger.info(f"📄 Full analysis saved to: {analysis_file}")

            return {
                "email_summary": email_summary,
                "attachment_path": str(attachment_path),
                "bid_data": bid_data,
                "sme_analysis": analysis
            }


        except Exception as e:
            self.logger.error(f"Error in get_brian_bid: {e}", exc_info=True)
            raise
def main():
    try:
        """Main function."""
        import argparse

        parser = argparse.ArgumentParser(description="Get Brian Fletcher's Bid from N8N")
        parser.add_argument("--project-root", type=Path, default=Path(__file__).parent.parent.parent)
        parser.add_argument("--n8n-url", type=str, help="N8N URL (default: http://<NAS_PRIMARY_IP>:5678)")

        args = parser.parse_args()

        client = N8NEmailHubClient(args.project_root)

        if args.n8n_url:
            client.n8n_url = args.n8n_url

        result = client.get_brian_bid()

        if "error" in result:
            print(f"\n❌ Error: {result['error']}")
            if "suggestion" in result:
                print(f"💡 {result['suggestion']}")
        else:
            print("\n✅ Successfully retrieved and analyzed Brian's bid!")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()