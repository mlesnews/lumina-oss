#!/usr/bin/env python3
"""
Search Emails for Credentials
Searches email accounts for emails from Stripe, Plaid, or Vlad to find API credentials

Tags: #EMAIL #CREDENTIALS #STRIPE #PLAID #SEARCH
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("EmailCredentialSearch")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("EmailCredentialSearch")

try:
    from scripts.python.unified_email_service import UnifiedEmailService, EmailProvider, UnifiedEmailMessage
    UNIFIED_EMAIL_AVAILABLE = True
except ImportError:
    UNIFIED_EMAIL_AVAILABLE = False
    logger.warning("Unified Email Service not available")

try:
    from scripts.python.lumina_gmail_integration import LUMINAGmailIntegration
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False


class EmailCredentialSearcher:
    """Search emails for credential information"""

    def __init__(self, project_root: Path):
        """Initialize email searcher"""
        self.project_root = Path(project_root)
        self.results_dir = self.project_root / "data" / "email_credential_search"
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Initialize email services
        self.unified_service = None
        self.gmail_service = None

        if UNIFIED_EMAIL_AVAILABLE:
            try:
                self.unified_service = UnifiedEmailService(self.project_root)
                logger.info("✅ Unified Email Service initialized")
            except Exception as e:
                logger.warning(f"Could not initialize Unified Email Service: {e}")

        if GMAIL_AVAILABLE:
            try:
                self.gmail_service = LUMINAGmailIntegration(self.project_root)
                logger.info("✅ Gmail Integration initialized")
            except Exception as e:
                logger.warning(f"Could not initialize Gmail Integration: {e}")

        logger.info("✅ Email Credential Searcher initialized")

    def search_for_stripe(self, days_back: int = 365) -> List[Dict[str, Any]]:
        """Search for emails from Stripe"""
        logger.info(f"🔍 Searching for Stripe emails (last {days_back} days)...")

        results = []

        # Search queries
        queries = [
            "from:stripe.com",
            "from:noreply@stripe.com",
            "from:notifications@stripe.com",
            "subject:stripe",
            "stripe API",
            "stripe key",
            "stripe credentials"
        ]

        if self.unified_service:
            for query in queries:
                try:
                    emails = self.unified_service.search_emails(
                        query=query,
                        provider=EmailProvider.UNIFIED,
                        days_back=days_back,
                        max_results=50
                    )
                    for email in emails:
                        results.append({
                            "provider": email.provider.value,
                            "subject": email.subject,
                            "from": email.from_address,
                            "date": email.date,
                            "snippet": email.body[:200] if email.body else "",
                            "query": query
                        })
                except Exception as e:
                    logger.debug(f"Error searching with query '{query}': {e}")

        logger.info(f"📧 Found {len(results)} Stripe-related emails")
        return results

    def search_for_plaid(self, days_back: int = 365) -> List[Dict[str, Any]]:
        """Search for emails from Plaid"""
        logger.info(f"🔍 Searching for Plaid emails (last {days_back} days)...")

        results = []

        # Search queries
        queries = [
            "from:plaid.com",
            "from:noreply@plaid.com",
            "from:notifications@plaid.com",
            "subject:plaid",
            "plaid API",
            "plaid key",
            "plaid credentials",
            "plaid client"
        ]

        if self.unified_service:
            for query in queries:
                try:
                    emails = self.unified_service.search_emails(
                        query=query,
                        provider=EmailProvider.UNIFIED,
                        days_back=days_back,
                        max_results=50
                    )
                    for email in emails:
                        results.append({
                            "provider": email.provider.value,
                            "subject": email.subject,
                            "from": email.from_address,
                            "date": email.date,
                            "snippet": email.body[:200] if email.body else "",
                            "query": query
                        })
                except Exception as e:
                    logger.debug(f"Error searching with query '{query}': {e}")

        logger.info(f"📧 Found {len(results)} Plaid-related emails")
        return results

    def search_for_vlad(self, days_back: int = 365) -> List[Dict[str, Any]]:
        """Search for emails from Vlad"""
        logger.info(f"🔍 Searching for emails from Vlad (last {days_back} days)...")

        results = []

        # Search queries
        queries = [
            "from:vlad",
            "subject:vlad",
            "vlad"
        ]

        if self.unified_service:
            for query in queries:
                try:
                    emails = self.unified_service.search_emails(
                        query=query,
                        provider=EmailProvider.UNIFIED,
                        days_back=days_back,
                        max_results=50
                    )
                    for email in emails:
                        results.append({
                            "provider": email.provider.value,
                            "subject": email.subject,
                            "from": email.from_address,
                            "date": email.date,
                            "snippet": email.body[:200] if email.body else "",
                            "query": query
                        })
                except Exception as e:
                    logger.debug(f"Error searching with query '{query}': {e}")

        logger.info(f"📧 Found {len(results)} Vlad-related emails")
        return results

    def extract_credentials_from_email(self, email_body: str) -> Dict[str, Any]:
        """Extract potential credentials from email body"""
        credentials = {
            "api_keys": [],
            "client_ids": [],
            "secrets": [],
            "tokens": []
        }

        import re

        # Stripe patterns
        stripe_pk_pattern = r'pk_(live|test)_[a-zA-Z0-9]{24,}'
        stripe_sk_pattern = r'sk_(live|test)_[a-zA-Z0-9]{24,}'

        # Plaid patterns
        plaid_client_id_pattern = r'[a-f0-9]{32}'
        plaid_secret_pattern = r'[a-zA-Z0-9]{32,}'

        # Find Stripe keys
        stripe_pk = re.findall(stripe_pk_pattern, email_body)
        stripe_sk = re.findall(stripe_sk_pattern, email_body)
        if stripe_pk:
            credentials["api_keys"].extend(stripe_pk)
        if stripe_sk:
            credentials["secrets"].extend(stripe_sk)

        # Find Plaid credentials (more generic, might have false positives)
        # This is a basic pattern - would need more context

        return credentials

    def search_all(self, days_back: int = 365) -> Dict[str, List[Dict[str, Any]]]:
        try:
            """Search for all relevant emails"""
            logger.info("🔍 Searching all email accounts...")

            results = {
                "stripe": self.search_for_stripe(days_back),
                "plaid": self.search_for_plaid(days_back),
                "vlad": self.search_for_vlad(days_back)
            }

            # Save results
            results_file = self.results_dir / f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            import json
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)

            logger.info(f"💾 Results saved to: {results_file}")

            return results

        except Exception as e:
            self.logger.error(f"Error in search_all: {e}", exc_info=True)
            raise
    def print_results(self, results: Dict[str, List[Dict[str, Any]]]):
        """Print search results in a readable format"""
        print("\n" + "="*80)
        print("📧 EMAIL SEARCH RESULTS")
        print("="*80)

        for search_type, emails in results.items():
            print(f"\n{'─'*80}")
            print(f"🔍 {search_type.upper()} ({len(emails)} emails found)")
            print(f"{'─'*80}")

            if not emails:
                print("   No emails found")
                continue

            for i, email in enumerate(emails, 1):
                print(f"\n{i}. Subject: {email['subject']}")
                print(f"   From: {email['from']}")
                print(f"   Date: {email['date']}")
                print(f"   Provider: {email['provider']}")
                if email['snippet']:
                    print(f"   Snippet: {email['snippet']}...")

        print("\n" + "="*80)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Search emails for credentials")
    parser.add_argument("--stripe", action="store_true", help="Search for Stripe emails")
    parser.add_argument("--plaid", action="store_true", help="Search for Plaid emails")
    parser.add_argument("--vlad", action="store_true", help="Search for Vlad emails")
    parser.add_argument("--all", action="store_true", help="Search for all")
    parser.add_argument("--days", type=int, default=365, help="Days to search back (default: 365)")

    args = parser.parse_args()

    searcher = EmailCredentialSearcher(project_root)

    if args.all or (not args.stripe and not args.plaid and not args.vlad):
        # Search all by default
        results = searcher.search_all(args.days)
        searcher.print_results(results)
    else:
        results = {}
        if args.stripe:
            results["stripe"] = searcher.search_for_stripe(args.days)
        if args.plaid:
            results["plaid"] = searcher.search_for_plaid(args.days)
        if args.vlad:
            results["vlad"] = searcher.search_for_vlad(args.days)

        searcher.print_results(results)


if __name__ == "__main__":


    main()