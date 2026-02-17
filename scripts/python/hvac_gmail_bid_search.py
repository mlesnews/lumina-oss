"""
HVAC Bid Gmail Search via n8n
Searches Gmail for contractor bid emails with attachments, extracts bids,
and creates a financial plan for the $10-20k HVAC project.

#JARVIS #LUMINA #PEAK
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal

# Setup logging
try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("HVACGmailBidSearch")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("HVACGmailBidSearch")


class HVACGmailBidSearcher:
    """Search Gmail for HVAC bid emails and process them."""

    def __init__(self, project_root: Path):
        """
        Initialize the Gmail bid searcher.

        Args:
            project_root: Root path of the LUMINA project
        """
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "hvac_bids"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.attachments_dir = self.data_dir / "attachments"
        self.attachments_dir.mkdir(parents=True, exist_ok=True)

    def search_gmail_via_n8n(self, 
                             search_queries: List[str],
                             days_back: int = 30) -> List[Dict[str, Any]]:
        """
        Search Gmail via n8n API for bid emails.

        Args:
            search_queries: List of Gmail search queries (e.g., ["from:contractor1@email.com", "subject:bid"])
            days_back: Number of days to search back

        Returns:
            List of email data dictionaries
        """
        # Check if n8n is available
        n8n_url = os.getenv("N8N_URL", "http://localhost:5678")

        logger.info(f"Searching Gmail via n8n at {n8n_url}")
        logger.info(f"Search queries: {search_queries}")

        # Try to use n8n API if available
        try:
            import requests

            # Check if n8n is running
            try:
                response = requests.get(f"{n8n_url}/healthz", timeout=5)
                if response.status_code != 200:
                    logger.warning("n8n not responding, will use alternative method")
                    return self._search_gmail_alternative(search_queries, days_back)
            except Exception as e:
                logger.warning(f"n8n not available: {e}, using alternative method")
                return self._search_gmail_alternative(search_queries, days_back)

            # Use n8n webhook to search Gmail
            # This would require a configured n8n workflow
            logger.info("n8n is available, but Gmail search workflow needs to be configured")
            logger.info("Falling back to alternative search method")
            return self._search_gmail_alternative(search_queries, days_back)

        except ImportError:
            logger.warning("requests library not available, using alternative method")
            return self._search_gmail_alternative(search_queries, days_back)

    def _search_gmail_alternative(self, 
                                  search_queries: List[str],
                                  days_back: int) -> List[Dict[str, Any]]:
        """
        Alternative Gmail search using Gmail API directly.

        Args:
            search_queries: List of search queries
            days_back: Days to search back

        Returns:
            List of email data
        """
        logger.info("Using Gmail API directly (requires credentials)")

        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            import pickle

            SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
            creds = None
            token_file = self.project_root / "config" / "gmail_token.pickle"
            credentials_file = self.project_root / "config" / "gmail_credentials.json"

            # Load existing token
            if token_file.exists():
                with open(token_file, 'rb') as token:
                    creds = pickle.load(token)

            # If no valid credentials, need to authenticate
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not credentials_file.exists():
                        logger.error(f"Gmail credentials not found at {credentials_file}")
                        logger.info("Please download credentials from Google Cloud Console")
                        return []
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(credentials_file), SCOPES)
                    creds = flow.run_local_server(port=0)

                # Save credentials
                token_file.parent.mkdir(parents=True, exist_ok=True)
                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)

            # Build Gmail service
            service = build('gmail', 'v1', credentials=creds)

            # Search for emails
            all_emails = []
            cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')

            for query in search_queries:
                full_query = f"{query} after:{cutoff_date} has:attachment"
                logger.info(f"Searching: {full_query}")

                try:
                    results = service.users().messages().list(
                        userId='me',
                        q=full_query,
                        maxResults=50
                    ).execute()

                    messages = results.get('messages', [])
                    logger.info(f"Found {len(messages)} emails for query: {query}")

                    for msg in messages:
                        email_data = self._get_email_details(service, msg['id'])
                        if email_data:
                            all_emails.append(email_data)

                except Exception as e:
                    logger.error(f"Error searching with query '{query}': {e}")

            return all_emails

        except ImportError:
            logger.error("Google API libraries not installed")
            logger.info("Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
            return []
        except Exception as e:
            logger.error(f"Error accessing Gmail API: {e}")
            return []

    def _get_email_details(self, service, message_id: str) -> Optional[Dict[str, Any]]:
        """Get full email details including attachments."""
        try:
            message = service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            # Extract email data
            headers = message['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            from_addr = next((h['value'] for h in headers if h['name'] == 'From'), '')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), '')

            # Get body
            body = self._extract_body(message['payload'])

            # Get attachments
            attachments = self._extract_attachments(service, message_id, message['payload'])

            return {
                'id': message_id,
                'subject': subject,
                'from': from_addr,
                'date': date,
                'body': body,
                'attachments': attachments
            }
        except Exception as e:
            logger.error(f"Error getting email details: {e}")
            return None

    def _extract_body(self, payload: Dict) -> str:
        """Extract email body text."""
        body = ""

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data')
                    if data:
                        import base64
                        body += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        else:
            if payload.get('mimeType') == 'text/plain':
                data = payload['body'].get('data')
                if data:
                    import base64
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

        return body

    def _extract_attachments(self, service, message_id: str, payload: Dict) -> List[Dict[str, Any]]:
        """Extract and download attachments."""
        attachments = []

        def extract_from_parts(parts):
            for part in parts:
                if part.get('filename'):
                    att_id = part['body'].get('attachmentId')
                    if att_id:
                        try:
                            att = service.users().messages().attachments().get(
                                userId='me',
                                messageId=message_id,
                                id=att_id
                            ).execute()

                            import base64
                            file_data = base64.urlsafe_b64decode(att['data'])

                            filename = part['filename']
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

                            attachments.append({
                                'filename': filename,
                                'path': str(file_path),
                                'size': len(file_data),
                                'mimeType': part.get('mimeType', '')
                            })

                            logger.info(f"Downloaded attachment: {filename}")

                        except Exception as e:
                            logger.error(f"Error downloading attachment: {e}")

                if 'parts' in part:
                    extract_from_parts(part['parts'])

        if 'parts' in payload:
            extract_from_parts(payload['parts'])

        return attachments

    def process_bid_emails(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        try:
            """
            Process bid emails and extract bid information.

            Args:
                emails: List of email data dictionaries

            Returns:
                List of extracted bid data
            """
            from hvac_bid_extractor import BidExtractor

            extractor = BidExtractor(self.project_root)
            bids = []

            for email in emails:
                logger.info(f"Processing email: {email.get('subject', 'No subject')}")

                # Try to extract contractor name from email
                contractor_name = self._extract_contractor_name(email)

                # Process attachments
                for attachment in email.get('attachments', []):
                    file_path = Path(attachment['path'])
                    if file_path.suffix.lower() in ['.pdf', '.docx', '.doc', '.txt']:
                        logger.info(f"Extracting bid from: {file_path.name}")
                        bid_data = extractor.extract_from_file(file_path, contractor_name)

                        if bid_data:
                            # Add email metadata
                            bid_data['source_email'] = email.get('from')
                            bid_data['email_subject'] = email.get('subject')
                            bid_data['email_date'] = email.get('date')
                            bids.append(bid_data)

                # Also try to extract from email body if no attachments
                if not email.get('attachments') and email.get('body'):
                    logger.info("No attachments found, extracting from email body")
                    bid_data = extractor.extract_from_text(email['body'], contractor_name)
                    if bid_data:
                        bid_data['source_email'] = email.get('from')
                        bid_data['email_subject'] = email.get('subject')
                        bid_data['email_date'] = email.get('date')
                        bids.append(bid_data)

            return bids

        except Exception as e:
            self.logger.error(f"Error in process_bid_emails: {e}", exc_info=True)
            raise
    def _extract_contractor_name(self, email: Dict[str, Any]) -> Optional[str]:
        """Extract contractor name from email."""
        from_addr = email.get('from', '')
        subject = email.get('subject', '')

        # Try to extract from "From" field
        match = re.search(r'"?([^"<]+)"?\s*<', from_addr)
        if match:
            return match.group(1).strip()

        # Try to extract from subject
        patterns = [
            r'from\s+([A-Z][A-Za-z\s&,\.]+?)(?:\s|$)',
            r'([A-Z][A-Za-z\s&,\.]+?)\s+(?:bid|quote|proposal)',
        ]
        for pattern in patterns:
            match = re.search(pattern, subject, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def create_financial_plan(self, 
                            bids: List[Dict[str, Any]],
                            budget_range: tuple = (10000, 20000),
                            liquidity_sources: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Create a financial plan for the HVAC project.

        Args:
            bids: List of bid data dictionaries
            budget_range: Tuple of (min_budget, max_budget)
            liquidity_sources: Optional list of liquidity sources with amounts

        Returns:
            Financial plan dictionary
        """
        from hvac_bid_comparison import HVACBidComparator

        comparator = HVACBidComparator(self.project_root)
        comparator.set_budget(budget_range[1])  # Use max budget

        # Import bids
        for bid in bids:
            comparator.import_bid_from_dict(bid)

        # Get comparison
        comparison = comparator.compare_bids()

        # Calculate costs
        costs = [Decimal(str(bid.get('total_cost', 0))) for bid in bids if bid.get('total_cost')]
        min_cost = min(costs) if costs else Decimal('0')
        max_cost = max(costs) if costs else Decimal('0')
        avg_cost = sum(costs) / len(costs) if costs else Decimal('0')

        # Financial analysis
        financial_plan = {
            "project_summary": {
                "total_bids": len(bids),
                "budget_range": {
                    "min": float(budget_range[0]),
                    "max": float(budget_range[1])
                },
                "cost_analysis": {
                    "lowest_bid": float(min_cost),
                    "highest_bid": float(max_cost),
                    "average_bid": float(avg_cost),
                    "cost_range": float(max_cost - min_cost)
                }
            },
            "liquidity_analysis": {
                "required_funding": float(max_cost),
                "available_sources": liquidity_sources or [],
                "funding_gap": None
            },
            "recommendations": [],
            "bid_comparison": comparison
        }

        # Calculate funding gap
        if liquidity_sources:
            total_available = sum(source.get('amount', 0) for source in liquidity_sources)
            financial_plan["liquidity_analysis"]["total_available"] = total_available
            financial_plan["liquidity_analysis"]["funding_gap"] = float(max_cost) - total_available

        # Generate recommendations
        if min_cost <= budget_range[1]:
            financial_plan["recommendations"].append({
                "type": "cost_optimization",
                "priority": "high",
                "message": f"Lowest bid (${min_cost:,.2f}) is within budget range",
                "action": "Consider negotiating with lowest bidder for better terms"
            })

        if max_cost > budget_range[1]:
            financial_plan["recommendations"].append({
                "type": "budget_management",
                "priority": "critical",
                "message": f"Highest bid (${max_cost:,.2f}) exceeds max budget",
                "action": "Negotiate price reduction or consider financing options"
            })

        if liquidity_sources:
            total_available = sum(s.get('amount', 0) for s in liquidity_sources)
            if total_available < max_cost:
                financial_plan["recommendations"].append({
                    "type": "financing",
                    "priority": "high",
                    "message": f"Funding gap of ${max_cost - total_available:,.2f}",
                    "action": "Consider financing options, payment plans, or phased installation"
                })

        return financial_plan


def main():
    try:
        """Main function for CLI usage."""
        import argparse

        parser = argparse.ArgumentParser(description="Search Gmail for HVAC Bid Emails")
        parser.add_argument("--project-root", type=Path,
                           default=Path(__file__).parent.parent.parent,
                           help="Project root directory")
        parser.add_argument("--search-queries", nargs="+",
                           help="Gmail search queries (e.g., 'from:contractor@email.com' 'subject:bid')")
        parser.add_argument("--contractor-emails", nargs="+",
                           help="Contractor email addresses to search for")
        parser.add_argument("--days-back", type=int, default=30,
                           help="Number of days to search back")
        parser.add_argument("--budget-min", type=float, default=10000,
                           help="Minimum budget")
        parser.add_argument("--budget-max", type=float, default=20000,
                           help="Maximum budget")
        parser.add_argument("--liquidity-file", type=Path,
                           help="JSON file with liquidity sources")
        parser.add_argument("--auto-extract", action="store_true",
                           help="Automatically extract bids from attachments")
        parser.add_argument("--generate-plan", action="store_true",
                           help="Generate financial plan")

        args = parser.parse_args()

        searcher = HVACGmailBidSearcher(args.project_root)

        # Build search queries
        if args.contractor_emails:
            search_queries = [f"from:{email}" for email in args.contractor_emails]
            search_queries.extend([f"subject:bid", "subject:quote", "subject:proposal", "subject:hvac"])
        elif args.search_queries:
            search_queries = args.search_queries
        else:
            # Default search
            search_queries = ["subject:bid", "subject:quote", "subject:proposal", "subject:hvac", "subject:furnace"]

        # Search Gmail
        print("="*80)
        print("SEARCHING GMAIL FOR HVAC BID EMAILS")
        print("="*80)
        emails = searcher.search_gmail_via_n8n(search_queries, args.days_back)

        if not emails:
            print("\n⚠ No emails found. You may need to:")
            print("  1. Configure Gmail API credentials")
            print("  2. Set up n8n Gmail workflow")
            print("  3. Check search queries")
            return

        print(f"\n✓ Found {len(emails)} email(s) with attachments")

        # Process bids
        if args.auto_extract:
            print("\nExtracting bid information...")
            bids = searcher.process_bid_emails(emails)

            if bids:
                print(f"✓ Extracted {len(bids)} bid(s)")

                # Save extracted bids
                from hvac_bid_extractor import BidExtractor
                extractor = BidExtractor(args.project_root)
                saved_files = extractor.save_extracted_bids(bids)

                print(f"\n✓ Saved bids to:")
                for file_path in saved_files:
                    print(f"    {file_path}")

                # Generate financial plan
                if args.generate_plan:
                    print("\n" + "="*80)
                    print("GENERATING FINANCIAL PLAN")
                    print("="*80)

                    # Load liquidity sources if provided
                    liquidity_sources = None
                    if args.liquidity_file and args.liquidity_file.exists():
                        with open(args.liquidity_file, 'r') as f:
                            liquidity_data = json.load(f)
                            liquidity_sources = liquidity_data.get('sources', [])

                    plan = searcher.create_financial_plan(
                        bids,
                        budget_range=(args.budget_min, args.budget_max),
                        liquidity_sources=liquidity_sources
                    )

                    # Save plan
                    plan_file = searcher.data_dir / f"financial_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(plan_file, 'w') as f:
                        json.dump(plan, f, indent=2, default=str)

                    print(f"\n✓ Financial plan saved to: {plan_file}")

                    # Print summary
                    print("\nFINANCIAL SUMMARY:")
                    print(f"  Lowest Bid: ${plan['project_summary']['cost_analysis']['lowest_bid']:,.2f}")
                    print(f"  Highest Bid: ${plan['project_summary']['cost_analysis']['highest_bid']:,.2f}")
                    print(f"  Average Bid: ${plan['project_summary']['cost_analysis']['average_bid']:,.2f}")

                    if plan['liquidity_analysis'].get('funding_gap'):
                        print(f"  Funding Gap: ${plan['liquidity_analysis']['funding_gap']:,.2f}")

                    if plan['recommendations']:
                        print("\nRECOMMENDATIONS:")
                        for rec in plan['recommendations']:
                            priority = "🔴" if rec['priority'] == 'critical' else "🟡" if rec['priority'] == 'high' else "🟢"
                            print(f"  {priority} {rec['message']}")
                            print(f"     Action: {rec.get('action', 'N/A')}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()