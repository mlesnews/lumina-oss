#!/usr/bin/env python3
"""
Analyze Actionable Emails - Find Syphon-Worthy Emails

With multiple email accounts, there should be lots of emails.
This script:
1. Fetches emails from all accounts
2. Identifies actionable/syphon-worthy emails
3. Separates wheat from chaff properly
4. Reports on actionable intelligence

Tags: #EMAIL_ANALYSIS #ACTIONABLE #SYPHON #INTELLIGENCE @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

from email_intelligence_filter import EmailIntelligenceFilter, EmailClassification

logger = get_logger("AnalyzeActionableEmails")


class ActionableEmailAnalyzer:
    """
    Analyze emails to find actionable/syphon-worthy content

    With multiple email accounts, there should be lots of emails.
    This identifies which are actionable for intelligence gathering.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize actionable email analyzer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.filter_system = EmailIntelligenceFilter(project_root)

        # Actionable indicators
        self.actionable_patterns = [
            r"action required",
            r"response needed",
            r"please reply",
            r"deadline",
            r"meeting",
            r"appointment",
            r"invoice",
            r"payment",
            r"order",
            r"confirmation",
            r"important",
            r"urgent",
            r"project",
            r"task",
            r"assignment",
            r"follow up",
            r"next steps",
            r"decision",
            r"approval",
            r"contract",
            r"agreement",
            r"proposal",
            r"quote",
            r"bid"
        ]

        logger.info("✅ Actionable Email Analyzer initialized")

    def _is_actionable(self, email_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Determine if email is actionable/syphon-worthy

        Returns:
            (is_actionable, reasons)
        """
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()
        text = f"{subject} {body}"

        reasons = []
        actionable_score = 0

        # Check actionable patterns
        import re
        for pattern in self.actionable_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                reasons.append(f"Contains actionable pattern: {pattern}")
                actionable_score += 1

        # Check if from trusted source (more likely actionable)
        from_address = email_data.get('from', email_data.get('from_address', ''))
        if self.filter_system._check_source_trust(from_address)[0]:
            reasons.append("From trusted source")
            actionable_score += 2

        # Check if has clear subject (not spam)
        if subject and len(subject) > 5 and not subject.startswith('re: re: re:'):
            reasons.append("Clear, non-chain subject")
            actionable_score += 1

        # Check if has body content (not just empty)
        if body and len(body) > 50:
            reasons.append("Has substantial body content")
            actionable_score += 1

        # Actionable if score >= 2
        is_actionable = actionable_score >= 2

        return is_actionable, reasons

    def _is_syphon_worthy(self, email_data: Dict[str, Any], classification: EmailClassification) -> Tuple[bool, List[str]]:
        """
        Determine if email is syphon-worthy for intelligence gathering

        Returns:
            (is_syphon_worthy, reasons)
        """
        reasons = []

        # Must be wheat (not chaff)
        if classification.classification != "wheat":
            return False, ["Not wheat - filtered as chaff"]

        # Must be actionable
        is_actionable, actionable_reasons = self._is_actionable(email_data)
        if not is_actionable:
            return False, ["Not actionable"] + actionable_reasons

        # Must not be compromised
        if classification.is_compromised:
            return False, ["Source is compromised"]

        # Must have low risk score
        if classification.risk_score > 0.5:
            return False, [f"Risk score too high: {classification.risk_score}"]

        reasons.extend(actionable_reasons)
        reasons.append("Syphon-worthy for intelligence gathering")

        return True, reasons

    def analyze_all_emails(self) -> Dict[str, Any]:
        """
        Analyze all emails from all sources

        Returns:
            Analysis results with actionable/syphon-worthy counts
        """
        logger.info("=" * 80)
        logger.info("📧 ANALYZING ALL EMAILS - Finding Actionable/Syphon-Worthy")
        logger.info("=" * 80)
        logger.info("")

        # First, try to fetch emails from all accounts
        logger.info("📥 Fetching emails from all accounts...")

        try:
            from jarvis_syphon_all_emails_nas_hub import JARVISEmailSyphonNASHub
            email_syphon = JARVISEmailSyphonNASHub()
            syphon_results = email_syphon.syphon_all_accounts(days=30)

            logger.info(f"✅ Fetched emails from {syphon_results.get('accounts_processed', 0)} accounts")
            logger.info(f"   Total emails: {syphon_results.get('total_emails', 0)}")
        except Exception as e:
            logger.warning(f"⚠️  Could not fetch fresh emails: {e}")
            logger.info("   Analyzing existing email data...")
            syphon_results = {"total_emails": 0, "accounts_processed": 0}

        # Walk email hub and classify
        logger.info("")
        logger.info("🔍 Walking email hub and classifying...")
        filter_results = self.filter_system.walk_email_hub()

        # Analyze each email
        logger.info("")
        logger.info("📊 Analyzing emails for actionable/syphon-worthy content...")

        actionable_count = 0
        syphon_worthy_count = 0
        actionable_emails = []
        syphon_worthy_emails = []

        # Process classifications
        for classification in filter_results.classifications:
            # Find corresponding email data
            email_data = None
            for email_file in self.filter_system.email_hub_dir.rglob("*.json"):
                try:
                    data = self.filter_system._load_email_data(email_file)
                    if data and data.get('message_id') == classification.email_id:
                        email_data = data
                        break
                except:
                    continue

            if not email_data:
                # Try to reconstruct from classification
                email_data = {
                    "message_id": classification.email_id,
                    "subject": "",
                    "body": "",
                    "from": ""
                }

            # Check if actionable
            is_actionable, actionable_reasons = self._is_actionable(email_data)
            if is_actionable:
                actionable_count += 1
                actionable_emails.append({
                    "email": email_data,
                    "classification": classification,
                    "reasons": actionable_reasons
                })

            # Check if syphon-worthy
            is_syphon_worthy, syphon_reasons = self._is_syphon_worthy(email_data, classification)
            if is_syphon_worthy:
                syphon_worthy_count += 1
                syphon_worthy_emails.append({
                    "email": email_data,
                    "classification": classification,
                    "reasons": syphon_reasons
                })

        # Results
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_emails_found": filter_results.total_emails,
            "wheat_emails": filter_results.wheat_emails,
            "chaff_emails": filter_results.chaff_emails,
            "actionable_emails": actionable_count,
            "syphon_worthy_emails": syphon_worthy_count,
            "actionable_list": actionable_emails,
            "syphon_worthy_list": syphon_worthy_emails,
            "fresh_emails_fetched": syphon_results.get("total_emails", 0),
            "accounts_processed": syphon_results.get("accounts_processed", 0)
        }

        # Print summary
        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 ACTIONABLE EMAIL ANALYSIS")
        logger.info("=" * 80)
        logger.info(f"Total Emails Found: {results['total_emails_found']}")
        logger.info(f"Fresh Emails Fetched: {results['fresh_emails_fetched']}")
        logger.info(f"Accounts Processed: {results['accounts_processed']}")
        logger.info("")
        logger.info(f"✅ Wheat (Legitimate): {results['wheat_emails']}")
        logger.info(f"❌ Chaff (Filtered): {results['chaff_emails']}")
        logger.info("")
        logger.info(f"📋 Actionable Emails: {results['actionable_emails']}")
        logger.info(f"🔍 Syphon-Worthy Emails: {results['syphon_worthy_emails']}")
        logger.info("")

        if results['actionable_emails'] > 0:
            logger.info("📋 ACTIONABLE EMAILS:")
            for i, item in enumerate(actionable_emails[:10], 1):  # Show first 10
                email = item['email']
                subject = email.get('subject', 'No subject')[:50]
                logger.info(f"   {i}. {subject}")
                logger.info(f"      Reasons: {', '.join(item['reasons'][:2])}")

        if results['syphon_worthy_emails'] > 0:
            logger.info("")
            logger.info("🔍 SYPHON-WORTHY EMAILS:")
            for i, item in enumerate(syphon_worthy_emails[:10], 1):  # Show first 10
                email = item['email']
                subject = email.get('subject', 'No subject')[:50]
                logger.info(f"   {i}. {subject}")
                logger.info(f"      Reasons: {', '.join(item['reasons'][:2])}")

        logger.info("")
        logger.info("=" * 80)

        # Save results
        results_file = self.project_root / "data" / "email_filtered" / f"actionable_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"✅ Results saved: {results_file}")

        return results


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze Actionable Emails - Find Syphon-Worthy")
    parser.add_argument("--fetch", action="store_true", help="Fetch fresh emails from all accounts")

    args = parser.parse_args()

    analyzer = ActionableEmailAnalyzer()
    results = analyzer.analyze_all_emails()

    logger.info("")
    logger.info("✅ Analysis complete")
    logger.info(f"   📋 Actionable: {results['actionable_emails']}")
    logger.info(f"   🔍 Syphon-worthy: {results['syphon_worthy_emails']}")


if __name__ == "__main__":


    main()