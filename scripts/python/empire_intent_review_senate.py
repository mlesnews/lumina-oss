#!/usr/bin/env python3
"""
@empire Intent Review - Intergalactic Senate Analysis

The Intergalactic Senate reviews all user @intents and provides strategic guidance
for @empire to address unfinished work and overlooked intents.

Tags: #EMPIRE #INTENT #SENATE #BRAINTRUST #STRATEGIC_GUIDANCE @empire @braintrust
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import logging

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("EmpireIntentReview")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("EmpireIntentReview")

try:
    from scripts.python.ai_panel_scientist_review import IntergalacticSenate
    SENATE_AVAILABLE = True
except ImportError:
    SENATE_AVAILABLE = False
    logger.warning("Intergalactic Senate not available")


@dataclass
class IntentReview:
    """Review of a user @intent by the Intergalactic Senate"""
    intent_id: str
    intent_text: str
    repetition_count: int
    priority: str = "medium"  # low, medium, high, critical
    status: str = "unknown"  # unknown, overlooked, pending, in_progress, fulfilled
    senate_rating: float = 0.0
    strategic_guidance: List[str] = field(default_factory=list)
    critical_issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    related_asks: List[str] = field(default_factory=list)
    related_tickets: List[str] = field(default_factory=list)
    senate_consensus: Optional[str] = None


class EmpireIntentReview:
    """
    @empire Intent Review System

    Uses the Intergalactic Senate to review all user @intents and provide
    strategic guidance for addressing unfinished work.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.intents_file = self.project_root / "data" / "user_intents" / "all_intents_extraction_report.json"
        self.reviews_dir = self.project_root / "data" / "intergalactic_senate" / "intent_reviews"
        self.reviews_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Intergalactic Senate
        self.senate: Optional[IntergalacticSenate] = None
        if SENATE_AVAILABLE:
            try:
                self.senate = IntergalacticSenate(project_root)
                logger.info("✅ Intergalactic Senate initialized for @empire intent review")
            except Exception as e:
                logger.warning(f"Senate initialization failed: {e}")

        logger.info("="*80)
        logger.info("🌟 @empire INTENT REVIEW - INTERGALACTIC SENATE")
        logger.info("="*80)
        logger.info("   Reviewing all user @intents for strategic guidance")
        logger.info("")

    def review_all_intents(self) -> Dict[str, Any]:
        try:
            """Review all user @intents with the Intergalactic Senate"""
            if not self.intents_file.exists():
                logger.error(f"Intents file not found: {self.intents_file}")
                return {}

            # Load intents
            with open(self.intents_file, 'r', encoding='utf-8') as f:
                intents_data = json.load(f)

            logger.info(f"📋 Found {intents_data.get('total_intents_found', 0)} total intents")
            logger.info(f"   Unique: {intents_data.get('unique_intents', 0)}")
            logger.info(f"   Duplicates: {len(intents_data.get('duplicates', []))}")
            logger.info("")

            # Get all unique intents
            all_intents = intents_data.get('unique_intents_list', [])
            if not all_intents:
                # Extract from consolidated_intents
                all_intents = intents_data.get('consolidated_intents', [])
            if not all_intents:
                # Extract from the structure
                all_intents = self._extract_intents_from_data(intents_data)

            logger.info(f"🔍 Reviewing {len(all_intents)} unique intents with Intergalactic Senate...")
            logger.info("")

            # Review each intent
            reviews = []
            for intent in all_intents:
                review = self._review_intent(intent, intents_data)
                reviews.append(review)

            # Generate strategic summary
            summary = self._generate_strategic_summary(reviews, intents_data)

            # Save reviews
            review_file = self.reviews_dir / f"empire_intent_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(review_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "review_date": datetime.now().isoformat(),
                    "total_intents": len(all_intents),
                    "reviews": [self._review_to_dict(r) for r in reviews],
                    "strategic_summary": summary,
                    "empire": "@empire",
                    "braintrust": "@braintrust"
                }, f, indent=2, ensure_ascii=False)

            logger.info("="*80)
            logger.info("✅ @empire INTENT REVIEW COMPLETE")
            logger.info("="*80)
            logger.info(f"   Intents Reviewed: {len(reviews)}")
            logger.info(f"   Strategic Summary: {review_file}")
            logger.info("")

            return {
                "reviews": reviews,
                "strategic_summary": summary,
                "review_file": review_file
            }

        except Exception as e:
            self.logger.error(f"Error in review_all_intents: {e}", exc_info=True)
            raise
    def _extract_intents_from_data(self, intents_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract unique intents from the data structure"""
        intents = []

        # Check for unique_intents_list
        if 'unique_intents_list' in intents_data:
            return intents_data['unique_intents_list']

        # Extract from intents_by_source if available
        if 'intents_by_source' in intents_data:
            seen = set()
            for source, source_intents in intents_data['intents_by_source'].items():
                for intent in source_intents:
                    intent_text = intent.get('intent_text', '').strip()
                    if intent_text and intent_text not in seen:
                        seen.add(intent_text)
                        intents.append(intent)

        return intents

    def _review_intent(self, intent: Dict[str, Any], intents_data: Dict[str, Any]) -> IntentReview:
        """Review a single intent with the Intergalactic Senate"""
        intent_id = intent.get('intent_id', 'unknown')
        intent_text = intent.get('intent_text', '').strip()
        repetition_count = intent.get('repetition_count', 1)

        # Skip empty or invalid intents
        if not intent_text or intent_text == "**" or len(intent_text) < 3:
            return IntentReview(
                intent_id=intent_id,
                intent_text=intent_text,
                repetition_count=repetition_count,
                status="invalid",
                senate_consensus="Invalid intent - skipped"
            )

        review = IntentReview(
            intent_id=intent_id,
            intent_text=intent_text,
            repetition_count=repetition_count
        )

        # Determine priority based on repetition
        if repetition_count >= 10:
            review.priority = "critical"
        elif repetition_count >= 5:
            review.priority = "high"
        elif repetition_count >= 2:
            review.priority = "medium"
        else:
            review.priority = "low"

        # Determine status
        if repetition_count > 5:
            review.status = "overlooked"
        else:
            review.status = "unknown"

        # Get Senate review if available
        if self.senate:
            try:
                # Create a temporary report for Senate review
                temp_report = self._create_intent_report(intent_text, intent)
                senate_feedback = self.senate.review_report(temp_report)

                review.senate_rating = senate_feedback.overall_rating
                review.senate_consensus = senate_feedback.senate_consensus
                review.critical_issues = senate_feedback.critical_issues[:3]
                review.recommendations = senate_feedback.recommendations[:3]
                review.strategic_guidance = senate_feedback.strategic_guidance[:3]
            except Exception as e:
                logger.warning(f"Senate review failed for {intent_id}: {e}")
                review.senate_consensus = f"Senate review unavailable: {e}"
        else:
            # Fallback analysis
            review.senate_rating = 0.5
            review.senate_consensus = "Senate not available - using fallback analysis"
            review.recommendations = ["Review intent manually", "Check for related work"]

        # Check for related asks/tickets
        review.related_asks = self._find_related_asks(intent_text)
        review.related_tickets = self._find_related_tickets(intent_text)

        return review

    def _create_intent_report(self, intent_text: str, intent_data: Dict[str, Any]) -> Path:
        try:
            """Create a temporary report file for Senate review"""
            temp_dir = self.reviews_dir / "temp_reports"
            temp_dir.mkdir(parents=True, exist_ok=True)

            intent_id = intent_data.get('intent_id', 'unknown')
            report_file = temp_dir / f"intent_{intent_id}.md"

            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(f"# User Intent: {intent_id}\n\n")
                f.write(f"**Intent Text:** {intent_text}\n\n")
                f.write(f"**Repetition Count:** {intent_data.get('repetition_count', 1)}\n\n")
                f.write(f"**Sources:** {', '.join(intent_data.get('sources', []))}\n\n")
                f.write(f"**Status:** {intent_data.get('fulfillment_status', 'unknown')}\n\n")
                f.write("## Review Request\n\n")
                f.write("The Intergalactic Senate is requested to review this user intent and provide strategic guidance for @empire.\n")

            return report_file

        except Exception as e:
            self.logger.error(f"Error in _create_intent_report: {e}", exc_info=True)
            raise
    def _find_related_asks(self, intent_text: str) -> List[str]:
        """Find related @asks (PM + 9 digits)"""
        asks_file = self.project_root / "data" / "ask_database" / "implementation_plan_tasks.json"
        if not asks_file.exists():
            return []

        try:
            with open(asks_file, 'r', encoding='utf-8') as f:
                asks_data = json.load(f)

            related = []
            asks = asks_data.get('asks', [])
            intent_lower = intent_text.lower()

            for ask in asks:
                ask_text = json.dumps(ask).lower()
                if any(word in ask_text for word in intent_lower.split()[:5] if len(word) > 3):
                    related.append(ask.get('ask_id', ''))

            return related[:5]  # Limit to 5
        except Exception as e:
            logger.warning(f"Error finding related asks: {e}")
            return []

    def _find_related_tickets(self, intent_text: str) -> List[str]:
        """Find related help desk tickets"""
        tickets_dir = self.project_root / "data" / "helpdesk" / "tickets"
        if not tickets_dir.exists():
            return []

        related = []
        intent_lower = intent_text.lower()

        try:
            for ticket_file in tickets_dir.glob("*.json"):
                try:
                    with open(ticket_file, 'r', encoding='utf-8') as f:
                        ticket = json.load(f)

                    ticket_text = json.dumps(ticket).lower()
                    if any(word in ticket_text for word in intent_lower.split()[:5] if len(word) > 3):
                        related.append(ticket.get('ticket_id', ''))
                except:
                    continue

            return related[:5]  # Limit to 5
        except Exception as e:
            logger.warning(f"Error finding related tickets: {e}")
            return []

    def _generate_strategic_summary(self, reviews: List[IntentReview], intents_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate strategic summary for @empire"""
        # Categorize by priority
        critical = [r for r in reviews if r.priority == "critical"]
        high = [r for r in reviews if r.priority == "high"]
        medium = [r for r in reviews if r.priority == "medium"]
        low = [r for r in reviews if r.priority == "low"]

        # Categorize by status
        overlooked = [r for r in reviews if r.status == "overlooked"]
        unknown = [r for r in reviews if r.status == "unknown"]

        # Top issues
        all_issues = []
        for review in reviews:
            all_issues.extend(review.critical_issues)

        # Top recommendations
        all_recommendations = []
        for review in reviews:
            all_recommendations.extend(review.recommendations)

        # Strategic guidance
        all_guidance = []
        for review in reviews:
            all_guidance.extend(review.strategic_guidance)

        summary = {
            "total_intents_reviewed": len(reviews),
            "by_priority": {
                "critical": len(critical),
                "high": len(high),
                "medium": len(medium),
                "low": len(low)
            },
            "by_status": {
                "overlooked": len(overlooked),
                "unknown": len(unknown),
                "other": len(reviews) - len(overlooked) - len(unknown)
            },
            "top_critical_intents": [
                {
                    "intent_id": r.intent_id,
                    "intent_text": r.intent_text[:100] + "..." if len(r.intent_text) > 100 else r.intent_text,
                    "repetition_count": r.repetition_count,
                    "senate_rating": r.senate_rating
                }
                for r in sorted(critical, key=lambda x: x.repetition_count, reverse=True)[:10]
            ],
            "top_overlooked_intents": [
                {
                    "intent_id": r.intent_id,
                    "intent_text": r.intent_text[:100] + "..." if len(r.intent_text) > 100 else r.intent_text,
                    "repetition_count": r.repetition_count,
                    "senate_rating": r.senate_rating
                }
                for r in sorted(overlooked, key=lambda x: x.repetition_count, reverse=True)[:10]
            ],
            "top_critical_issues": list(set(all_issues))[:10],
            "top_recommendations": list(set(all_recommendations))[:10],
            "strategic_guidance": list(set(all_guidance))[:10],
            "empire": "@empire",
            "braintrust": "@braintrust"
        }

        return summary

    def _review_to_dict(self, review: IntentReview) -> Dict[str, Any]:
        """Convert review to dictionary"""
        return {
            "intent_id": review.intent_id,
            "intent_text": review.intent_text,
            "repetition_count": review.repetition_count,
            "priority": review.priority,
            "status": review.status,
            "senate_rating": review.senate_rating,
            "senate_consensus": review.senate_consensus,
            "critical_issues": review.critical_issues,
            "recommendations": review.recommendations,
            "strategic_guidance": review.strategic_guidance,
            "related_asks": review.related_asks,
            "related_tickets": review.related_tickets
        }


def main():
    try:
        """Main execution - Review all @intents for @empire"""
        import argparse

        parser = argparse.ArgumentParser(description="@empire Intent Review - Intergalactic Senate")
        parser.add_argument("--intents-file", help="Path to intents file")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        reviewer = EmpireIntentReview(project_root)

        if args.intents_file:
            reviewer.intents_file = Path(args.intents_file)

        results = reviewer.review_all_intents()

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())