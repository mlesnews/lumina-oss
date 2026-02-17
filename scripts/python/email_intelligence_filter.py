#!/usr/bin/env python3
"""
Email Intelligence Filter - Separate Wheat from Chaff

Walks through email hub data files and filters out:
- Advertising emails
- Junk mail
- Spam
- Phishing emails

Protects intelligence gathering system from bad actors injecting false information.

Tags: #EMAIL_FILTER #SPAM_DETECTION #PHISHING #INTELLIGENCE #SECURITY @JARVIS @LUMINA
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field, asdict
from collections import Counter

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

logger = get_logger("EmailIntelligenceFilter")


@dataclass
class EmailClassification:
    """Email classification result"""
    email_id: str
    classification: str  # wheat, advertising, junk, spam, phishing, suspicious
    confidence: float
    reasons: List[str] = field(default_factory=list)
    risk_score: float = 0.0
    is_trusted: bool = False
    is_compromised: bool = False


@dataclass
class FilterResults:
    """Email filtering results"""
    total_emails: int = 0
    wheat_emails: int = 0
    chaff_emails: int = 0
    advertising: int = 0
    junk: int = 0
    spam: int = 0
    phishing: int = 0
    suspicious: int = 0
    classifications: List[EmailClassification] = field(default_factory=list)


class EmailIntelligenceFilter:
    """
    Email Intelligence Filter

    Separates wheat from chaff:
    - Wheat: Legitimate, valuable emails
    - Chaff: Advertising, junk, spam, phishing, compromised sources
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize email intelligence filter"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.email_hub_dir = self.project_root / "data" / "email_syphon"
        self.encrypted_dir = self.project_root / "data" / "email_encrypted_local"
        self.filtered_dir = self.project_root / "data" / "email_filtered"
        self.filtered_dir.mkdir(parents=True, exist_ok=True)

        # Load patterns and rules
        self.patterns = self._load_filtering_patterns()
        self.trusted_sources = self._load_trusted_sources()
        self.compromised_sources = self._load_compromised_sources()

        # Initialize AI Scorer
        try:
            from lumina_ai_intelligence_scorer import LuminaAIIntelligenceScorer
            self.ai_scorer = LuminaAIIntelligenceScorer(self.project_root)
            logger.info("✅ AI Intelligence Scorer integrated")
        except ImportError:
            self.ai_scorer = None
            logger.warning("⚠️  AI Intelligence Scorer not available")

        logger.info("✅ Email Intelligence Filter initialized")
        logger.info("   🛡️  Protecting intelligence gathering from bad actors")

    def _load_filtering_patterns(self) -> Dict[str, List[str]]:
        """Load filtering patterns for different email types"""
        return {
            "advertising": [
                r"unsubscribe",
                r"click here",
                r"limited time offer",
                r"special promotion",
                r"act now",
                r"buy now",
                r"discount",
                r"coupon",
                r"deal",
                r"save \d+%",
                r"free shipping",
                r"order now",
                r"shop now",
                r"advertisement",
                r"marketing",
                r"newsletter",
                r"promotional"
            ],
            "junk": [
                r"^re: re: re:",
                r"fwd: fwd:",
                r"^>\s*>",
                r"chain letter",
                r"forward this",
                r"pass it on"
            ],
            "spam": [
                r"viagra",
                r"cialis",
                r"weight loss",
                r"make money",
                r"work from home",
                r"get rich",
                r"nigerian prince",
                r"lottery winner",
                r"inheritance",
                r"urgent action required",
                r"verify your account",
                r"suspended account",
                r"click to verify"
            ],
            "phishing": [
                r"verify your account",
                r"update your information",
                r"account suspended",
                r"security alert",
                r"unauthorized access",
                r"click here to verify",
                r"confirm your identity",
                r"update payment",
                r"billing issue",
                r"suspicious activity",
                r"verify email",
                r"account locked",
                r"password reset",
                r"urgent: verify",
                r"action required",
                r"immediate action",
                r"your account will be closed"
            ],
            "suspicious": [
                r"bitcoin",
                r"cryptocurrency",
                r"investment opportunity",
                r"guaranteed return",
                r"no risk",
                r"act fast",
                r"limited spots",
                r"exclusive offer",
                r"secret method",
                r"hidden secret"
            ]
        }

    def _load_trusted_sources(self) -> List[str]:
        """Load list of trusted email sources"""
        trusted_file = self.project_root / "config" / "trusted_email_sources.json"

        if trusted_file.exists():
            try:
                with open(trusted_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("trusted_sources", [])
            except Exception as e:
                logger.warning(f"⚠️  Error loading trusted sources: {e}")

        # Default trusted sources
        return [
            "<LOCAL_HOSTNAME>",
            "protonmail.com",
            "gmail.com",
            "outlook.com",
            "office365.com"
        ]

    def _load_compromised_sources(self) -> List[str]:
        """Load list of known compromised sources (bad actors)"""
        compromised_file = self.project_root / "config" / "compromised_email_sources.json"

        if compromised_file.exists():
            try:
                with open(compromised_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("compromised_sources", [])
            except Exception as e:
                logger.warning(f"⚠️  Error loading compromised sources: {e}")

        return []

    def _extract_email_domain(self, email_address: str) -> str:
        """Extract domain from email address"""
        if '@' in email_address:
            return email_address.split('@')[1].lower()
        return email_address.lower()

    def _check_source_trust(self, from_address: str) -> Tuple[bool, bool]:
        """
        Check if email source is trusted or compromised

        Returns:
            (is_trusted, is_compromised)
        """
        domain = self._extract_email_domain(from_address)

        # Check compromised sources first (highest priority)
        for compromised in self.compromised_sources:
            if compromised.lower() in domain:
                return False, True

        # Check trusted sources
        for trusted in self.trusted_sources:
            if trusted.lower() in domain:
                return True, False

        return False, False

    def _classify_email(self, email_data: Dict[str, Any], use_ai: bool = True) -> EmailClassification:
        """
        Classify email as wheat or chaff
        """
        email_id = email_data.get('message_id', email_data.get('email_id', 'unknown'))
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()
        from_address = email_data.get('from', email_data.get('from_address', ''))

        # Combine subject and body for pattern matching
        text = f"{subject} {body}"

        # Check source trust
        is_trusted, is_compromised = self._check_source_trust(from_address)

        # If compromised source, mark as phishing immediately
        if is_compromised:
            return EmailClassification(
                email_id=email_id,
                classification="phishing",
                confidence=1.0,
                reasons=["Known compromised source - bad actor"],
                risk_score=1.0,
                is_trusted=False,
                is_compromised=True
            )

        # AI Scoring (Smart Filtering)
        if use_ai and self.ai_scorer:
            ai_result = self.ai_scorer.score_item(text, f"Email: {from_address}", {"subject": subject})

            # Use AI results to influence classification
            if ai_result.get("category") == "CRITICAL":
                return EmailClassification(
                    email_id=email_id,
                    classification="wheat",
                    confidence=0.95,
                    reasons=[f"AI classified as CRITICAL: {ai_result.get('summary')}"],
                    risk_score=0.0,
                    is_trusted=is_trusted,
                    is_compromised=False
                )
            elif ai_result.get("category") == "NOISE":
                return EmailClassification(
                    email_id=email_id,
                    classification="junk",
                    confidence=0.9,
                    reasons=[f"AI classified as NOISE: {ai_result.get('summary')}"],
                    risk_score=0.8,
                    is_trusted=is_trusted,
                    is_compromised=False
                )

        # Check patterns
        classifications = []
        reasons = []
        risk_score = 0.0

        # Check each category
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    classifications.append(category)
                    reasons.append(f"Matched {category} pattern: {pattern}")
                    risk_score += 0.2

        # Determine final classification
        if classifications:
            # Count occurrences
            classification_counts = Counter(classifications)
            primary_classification = classification_counts.most_common(1)[0][0]
            confidence = min(0.9, 0.5 + (len(classifications) * 0.1))

            # Phishing is highest priority
            if "phishing" in classifications:
                primary_classification = "phishing"
                confidence = min(1.0, confidence + 0.2)
                risk_score = min(1.0, risk_score + 0.3)

            return EmailClassification(
                email_id=email_id,
                classification=primary_classification,
                confidence=confidence,
                reasons=reasons,
                risk_score=min(1.0, risk_score),
                is_trusted=is_trusted,
                is_compromised=False
            )

        # If no patterns matched and source is trusted, it's wheat
        if is_trusted:
            return EmailClassification(
                email_id=email_id,
                classification="wheat",
                confidence=0.8,
                reasons=["Trusted source, no suspicious patterns"],
                risk_score=0.0,
                is_trusted=True,
                is_compromised=False
            )

        # Unknown - mark as suspicious
        return EmailClassification(
            email_id=email_id,
            classification="suspicious",
            confidence=0.3,
            reasons=["Unknown source, no clear classification"],
            risk_score=0.2,
            is_trusted=False,
            is_compromised=False
        )

    def _load_email_data(self, email_file: Path) -> Optional[Dict[str, Any]]:
        """Load email data from file"""
        try:
            if email_file.suffix == '.json':
                with open(email_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            elif email_file.suffix == '.encrypted':
                # Try to decrypt if encrypted storage available
                try:
                    from ai_encrypted_email_storage import AIEncryptedEmailStorage
                    storage = AIEncryptedEmailStorage()
                    email_id = email_file.stem
                    return storage.retrieve_encrypted_email(email_id)
                except Exception as e:
                    logger.debug(f"Could not decrypt {email_file}: {e}")
                    return None
        except Exception as e:
            logger.warning(f"⚠️  Error loading email file {email_file}: {e}")
            return None

        return None

    def walk_email_hub(self, directory: Optional[Path] = None) -> FilterResults:
        try:
            """
            Walk through email hub data files and filter emails

            Args:
                directory: Directory to walk (default: email_hub_dir)

            Returns:
                FilterResults object
            """
            if directory is None:
                directory = self.email_hub_dir

            logger.info("=" * 80)
            logger.info("🔍 Walking Email Hub - Separating Wheat from Chaff")
            logger.info("=" * 80)
            logger.info("")
            logger.info(f"📁 Scanning directory: {directory}")

            results = FilterResults()

            # Find all email files
            email_files = []
            if directory.exists():
                email_files.extend(directory.rglob("*.json"))
                email_files.extend(directory.rglob("*.encrypted"))

            # Also check encrypted directory
            if self.encrypted_dir.exists():
                email_files.extend(self.encrypted_dir.rglob("*.encrypted"))
                email_files.extend(self.encrypted_dir.rglob("*.json"))

            results.total_emails = len(email_files)
            logger.info(f"📧 Found {results.total_emails} email files")
            logger.info("")

            # Classify each email
            wheat_emails = []
            chaff_emails = []

            for email_file in email_files:
                email_data = self._load_email_data(email_file)
                if not email_data:
                    continue

                # Classify email
                classification = self._classify_email(email_data)
                results.classifications.append(classification)

                # Categorize
                if classification.classification == "wheat":
                    results.wheat_emails += 1
                    wheat_emails.append((email_file, email_data, classification))
                else:
                    results.chaff_emails += 1
                    chaff_emails.append((email_file, email_data, classification))

                    # Count by type
                    if classification.classification == "advertising":
                        results.advertising += 1
                    elif classification.classification == "junk":
                        results.junk += 1
                    elif classification.classification == "spam":
                        results.spam += 1
                    elif classification.classification == "phishing":
                        results.phishing += 1
                    elif classification.classification == "suspicious":
                        results.suspicious += 1

            # Save filtered results
            self._save_filtered_results(results, wheat_emails, chaff_emails)

            # Print summary
            self._print_summary(results)

            return results

        except Exception as e:
            self.logger.error(f"Error in walk_email_hub: {e}", exc_info=True)
            raise
    def _save_filtered_results(self, results: FilterResults, wheat_emails: List, chaff_emails: List):
        try:
            """Save filtered email results"""
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            # Save wheat emails (legitimate)
            wheat_dir = self.filtered_dir / "wheat"
            wheat_dir.mkdir(parents=True, exist_ok=True)

            wheat_file = wheat_dir / f"wheat_emails_{timestamp}.json"
            with open(wheat_file, 'w', encoding='utf-8') as f:
                json.dump([
                    {
                        "email": email_data,
                        "classification": asdict(classification)
                    }
                    for _, email_data, classification in wheat_emails
                ], f, indent=2, ensure_ascii=False)

            # Save chaff emails (filtered out)
            chaff_dir = self.filtered_dir / "chaff"
            chaff_dir.mkdir(parents=True, exist_ok=True)

            chaff_file = chaff_dir / f"chaff_emails_{timestamp}.json"
            with open(chaff_file, 'w', encoding='utf-8') as f:
                json.dump([
                    {
                        "email": email_data,
                        "classification": asdict(classification)
                    }
                    for _, email_data, classification in chaff_emails
                ], f, indent=2, ensure_ascii=False)

            # Save summary
            summary_file = self.filtered_dir / f"filter_summary_{timestamp}.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": timestamp,
                    "total_emails": results.total_emails,
                    "wheat_emails": results.wheat_emails,
                    "chaff_emails": results.chaff_emails,
                    "advertising": results.advertising,
                    "junk": results.junk,
                    "spam": results.spam,
                    "phishing": results.phishing,
                    "suspicious": results.suspicious
                }, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Filtered results saved:")
            logger.info(f"   Wheat: {wheat_file}")
            logger.info(f"   Chaff: {chaff_file}")
            logger.info(f"   Summary: {summary_file}")

        except Exception as e:
            self.logger.error(f"Error in _save_filtered_results: {e}", exc_info=True)
            raise
    def _print_summary(self, results: FilterResults):
        """Print filtering summary"""
        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 FILTERING SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Emails: {results.total_emails}")
        logger.info(f"✅ Wheat (Legitimate): {results.wheat_emails}")
        logger.info(f"❌ Chaff (Filtered): {results.chaff_emails}")
        logger.info("")
        logger.info("Chaff Breakdown:")
        logger.info(f"   📢 Advertising: {results.advertising}")
        logger.info(f"   🗑️  Junk: {results.junk}")
        logger.info(f"   📧 Spam: {results.spam}")
        logger.info(f"   🎣 Phishing: {results.phishing}")
        logger.info(f"   ⚠️  Suspicious: {results.suspicious}")
        logger.info("")
        logger.info("=" * 80)
        logger.info("🛡️  Intelligence gathering protected from bad actors")
        logger.info("=" * 80)


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Email Intelligence Filter - Separate Wheat from Chaff")
    parser.add_argument("--directory", type=Path, help="Email directory to scan (default: email_hub_dir)")
    parser.add_argument("--output", type=Path, help="Output directory for filtered results")

    args = parser.parse_args()

    filter_system = EmailIntelligenceFilter()

    if args.directory:
        results = filter_system.walk_email_hub(args.directory)
    else:
        results = filter_system.walk_email_hub()

    logger.info("")
    logger.info("✅ Email filtering complete")
    logger.info("   🛡️  Intelligence system protected from bad data sources")


if __name__ == "__main__":


    main()