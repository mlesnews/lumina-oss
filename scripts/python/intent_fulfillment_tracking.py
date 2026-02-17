#!/usr/bin/env python3
"""
Intent Fulfillment Tracking System - @empire

Tracks fulfillment status of all user @intents, cross-references with
implementation work (@asks, tickets), and provides @empire strategic oversight.

Tags: #EMPIRE #INTENT #FULFILLMENT #TRACKING @empire @braintrust
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("IntentFulfillmentTracking")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("IntentFulfillmentTracking")


class FulfillmentStatus(Enum):
    """Intent fulfillment status"""
    UNKNOWN = "unknown"
    OVERLOOKED = "overlooked"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    FULFILLED = "fulfilled"
    PARTIALLY_FULFILLED = "partially_fulfilled"
    BLOCKED = "blocked"


@dataclass
class IntentFulfillment:
    """Intent fulfillment tracking record"""
    intent_id: str
    intent_text: str
    repetition_count: int
    fulfillment_status: str = FulfillmentStatus.UNKNOWN.value
    implementation_status: str = "unknown"
    related_asks: List[str] = field(default_factory=list)
    related_tickets: List[str] = field(default_factory=list)
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    last_updated: Optional[str] = None
    fulfillment_evidence: List[str] = field(default_factory=list)
    notes: str = ""
    priority: str = "medium"


class IntentFulfillmentTracker:
    """
    Intent Fulfillment Tracking System for @empire

    Tracks all user @intents, their fulfillment status, and relationships
    to implementation work (@asks, tickets).
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.intents_file = self.project_root / "data" / "user_intents" / "all_intents_extraction_report.json"
        self.fulfillment_db = self.project_root / "data" / "user_intents" / "intent_fulfillment_database.json"
        self.asks_file = self.project_root / "data" / "ask_database" / "implementation_plan_tasks.json"
        self.tickets_dir = self.project_root / "data" / "helpdesk" / "tickets"

        # Load or initialize database
        self.fulfillments: Dict[str, IntentFulfillment] = {}
        self._load_database()

        logger.info("="*80)
        logger.info("📊 INTENT FULFILLMENT TRACKING - @empire")
        logger.info("="*80)
        logger.info(f"   Tracking: {len(self.fulfillments)} intents")
        logger.info("")

    def _load_database(self):
        """Load fulfillment database"""
        if self.fulfillment_db.exists():
            try:
                with open(self.fulfillment_db, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for intent_id, intent_data in data.get('fulfillments', {}).items():
                        self.fulfillments[intent_id] = IntentFulfillment(**intent_data)
                logger.info(f"✅ Loaded {len(self.fulfillments)} intent fulfillments from database")
            except Exception as e:
                logger.warning(f"Error loading database: {e}")
                self.fulfillments = {}
        else:
            logger.info("📝 Creating new fulfillment database")
            self._initialize_from_intents()

    def _initialize_from_intents(self):
        """Initialize database from intents extraction report"""
        if not self.intents_file.exists():
            logger.warning(f"Intents file not found: {self.intents_file}")
            return

        try:
            with open(self.intents_file, 'r', encoding='utf-8') as f:
                intents_data = json.load(f)

            consolidated = intents_data.get('consolidated_intents', [])
            for intent in consolidated:
                intent_id = intent.get('intent_id', 'unknown')
                fulfillment = IntentFulfillment(
                    intent_id=intent_id,
                    intent_text=intent.get('intent_text', '').strip(),
                    repetition_count=intent.get('repetition_count', 1),
                    fulfillment_status=intent.get('fulfillment_status', FulfillmentStatus.UNKNOWN.value),
                    implementation_status=intent.get('implementation_status', 'unknown'),
                    first_seen=intent.get('first_seen'),
                    last_seen=intent.get('last_seen'),
                    last_updated=datetime.now().isoformat()
                )

                # Set priority based on repetition
                if fulfillment.repetition_count >= 10:
                    fulfillment.priority = "critical"
                elif fulfillment.repetition_count >= 5:
                    fulfillment.priority = "high"
                elif fulfillment.repetition_count >= 2:
                    fulfillment.priority = "medium"
                else:
                    fulfillment.priority = "low"

                # Mark as overlooked if high repetition
                if fulfillment.repetition_count > 5:
                    fulfillment.fulfillment_status = FulfillmentStatus.OVERLOOKED.value

                self.fulfillments[intent_id] = fulfillment

            logger.info(f"✅ Initialized {len(self.fulfillments)} intents from extraction report")
        except Exception as e:
            logger.error(f"Error initializing from intents: {e}")

    def update_fulfillment(self, intent_id: str, status: Optional[str] = None,
                          evidence: Optional[List[str]] = None, notes: Optional[str] = None):
        """Update fulfillment status for an intent"""
        if intent_id not in self.fulfillments:
            logger.warning(f"Intent {intent_id} not found in database")
            return

        fulfillment = self.fulfillments[intent_id]

        if status:
            fulfillment.fulfillment_status = status
        if evidence:
            fulfillment.fulfillment_evidence.extend(evidence)
        if notes:
            fulfillment.notes = notes

        fulfillment.last_updated = datetime.now().isoformat()

        logger.info(f"✅ Updated {intent_id}: {fulfillment.fulfillment_status}")

    def link_to_ask(self, intent_id: str, ask_id: str):
        """Link intent to an @ask (PM + 9 digits)"""
        if intent_id not in self.fulfillments:
            logger.warning(f"Intent {intent_id} not found")
            return

        if ask_id not in self.fulfillments[intent_id].related_asks:
            self.fulfillments[intent_id].related_asks.append(ask_id)
            self.fulfillments[intent_id].last_updated = datetime.now().isoformat()
            logger.info(f"✅ Linked {intent_id} to @ask {ask_id}")

    def link_to_ticket(self, intent_id: str, ticket_id: str):
        """Link intent to a help desk ticket (T + 9 digits)"""
        if intent_id not in self.fulfillments:
            logger.warning(f"Intent {intent_id} not found")
            return

        if ticket_id not in self.fulfillments[intent_id].related_tickets:
            self.fulfillments[intent_id].related_tickets.append(ticket_id)
            self.fulfillments[intent_id].last_updated = datetime.now().isoformat()
            logger.info(f"✅ Linked {intent_id} to ticket {ticket_id}")

    def auto_link_work_items(self):
        """Automatically link intents to related @asks and tickets"""
        logger.info("🔗 Auto-linking intents to work items...")

        # Load @asks
        asks = {}
        if self.asks_file.exists():
            try:
                with open(self.asks_file, 'r', encoding='utf-8') as f:
                    asks_data = json.load(f)
                    asks = asks_data.get('asks', {})
            except Exception as e:
                logger.warning(f"Error loading @asks: {e}")

        # Load tickets
        tickets = {}
        if self.tickets_dir.exists():
            for ticket_file in self.tickets_dir.glob("*.json"):
                try:
                    with open(ticket_file, 'r', encoding='utf-8') as f:
                        ticket = json.load(f)
                        tickets[ticket.get('ticket_id', '')] = ticket
                except:
                    continue

        # Link intents to work items
        linked_count = 0
        for intent_id, fulfillment in self.fulfillments.items():
            intent_text_lower = fulfillment.intent_text.lower()
            intent_words = [w for w in intent_text_lower.split() if len(w) > 3]

            # Link to @asks
            for ask_id, ask in asks.items():
                ask_text = json.dumps(ask).lower()
                if any(word in ask_text for word in intent_words[:5]):
                    self.link_to_ask(intent_id, ask_id)
                    linked_count += 1

            # Link to tickets
            for ticket_id, ticket in tickets.items():
                ticket_text = json.dumps(ticket).lower()
                if any(word in ticket_text for word in intent_words[:5]):
                    self.link_to_ticket(intent_id, ticket_id)
                    linked_count += 1

        logger.info(f"✅ Auto-linked {linked_count} intent-work item relationships")

    def check_fulfillment_status(self):
        """Check and update fulfillment status based on related work items"""
        logger.info("🔍 Checking fulfillment status from work items...")

        # Load @asks status
        asks_status = {}
        if self.asks_file.exists():
            try:
                with open(self.asks_file, 'r', encoding='utf-8') as f:
                    asks_data = json.load(f)
                    for ask_id, ask in asks_data.get('asks', {}).items():
                        asks_status[ask_id] = ask.get('status', 'unknown')
            except:
                pass

        # Load ticket status
        tickets_status = {}
        if self.tickets_dir.exists():
            for ticket_file in self.tickets_dir.glob("*.json"):
                try:
                    with open(ticket_file, 'r', encoding='utf-8') as f:
                        ticket = json.load(f)
                        tickets_status[ticket.get('ticket_id', '')] = ticket.get('status', 'unknown')
                except:
                    continue

        # Update fulfillment status
        updated_count = 0
        for intent_id, fulfillment in self.fulfillments.items():
            # Check related @asks
            for ask_id in fulfillment.related_asks:
                ask_status = asks_status.get(ask_id, 'unknown')
                if ask_status == 'completed':
                    if fulfillment.fulfillment_status == FulfillmentStatus.UNKNOWN.value:
                        fulfillment.fulfillment_status = FulfillmentStatus.FULFILLED.value
                        fulfillment.implementation_status = 'completed'
                        fulfillment.fulfillment_evidence.append(f"@ask {ask_id} completed")
                        updated_count += 1
                elif ask_status == 'in_progress':
                    if fulfillment.fulfillment_status == FulfillmentStatus.UNKNOWN.value:
                        fulfillment.fulfillment_status = FulfillmentStatus.IN_PROGRESS.value
                        fulfillment.implementation_status = 'in_progress'
                        updated_count += 1

            # Check related tickets
            for ticket_id in fulfillment.related_tickets:
                ticket_status = tickets_status.get(ticket_id, 'unknown')
                if ticket_status == 'closed' or ticket_status == 'resolved':
                    if fulfillment.fulfillment_status == FulfillmentStatus.UNKNOWN.value:
                        fulfillment.fulfillment_status = FulfillmentStatus.FULFILLED.value
                        fulfillment.implementation_status = 'completed'
                        fulfillment.fulfillment_evidence.append(f"Ticket {ticket_id} closed")
                        updated_count += 1
                elif ticket_status == 'in_progress':
                    if fulfillment.fulfillment_status == FulfillmentStatus.UNKNOWN.value:
                        fulfillment.fulfillment_status = FulfillmentStatus.IN_PROGRESS.value
                        fulfillment.implementation_status = 'in_progress'
                        updated_count += 1

        logger.info(f"✅ Updated {updated_count} fulfillment statuses")

    def get_overlooked_intents(self) -> List[IntentFulfillment]:
        """Get all overlooked intents"""
        overlooked = [
            f for f in self.fulfillments.values()
            if f.fulfillment_status == FulfillmentStatus.OVERLOOKED.value
            or (f.repetition_count > 5 and f.fulfillment_status == FulfillmentStatus.UNKNOWN.value)
        ]
        return sorted(overlooked, key=lambda x: x.repetition_count, reverse=True)

    def get_critical_intents(self) -> List[IntentFulfillment]:
        """Get all critical priority intents"""
        critical = [
            f for f in self.fulfillments.values()
            if f.priority == "critical"
        ]
        return sorted(critical, key=lambda x: x.repetition_count, reverse=True)

    def generate_report(self) -> Dict[str, Any]:
        """Generate fulfillment status report for @empire"""
        total = len(self.fulfillments)
        by_status = {}
        by_priority = {}

        for fulfillment in self.fulfillments.values():
            status = fulfillment.fulfillment_status
            priority = fulfillment.priority

            by_status[status] = by_status.get(status, 0) + 1
            by_priority[priority] = by_priority.get(priority, 0) + 1

        overlooked = self.get_overlooked_intents()
        critical = self.get_critical_intents()

        report = {
            "report_date": datetime.now().isoformat(),
            "total_intents": total,
            "by_status": by_status,
            "by_priority": by_priority,
            "overlooked_count": len(overlooked),
            "critical_count": len(critical),
            "top_overlooked": [
                {
                    "intent_id": f.intent_id,
                    "intent_text": f.intent_text[:100] + "..." if len(f.intent_text) > 100 else f.intent_text,
                    "repetition_count": f.repetition_count,
                    "related_asks": f.related_asks,
                    "related_tickets": f.related_tickets
                }
                for f in overlooked[:10]
            ],
            "top_critical": [
                {
                    "intent_id": f.intent_id,
                    "intent_text": f.intent_text[:100] + "..." if len(f.intent_text) > 100 else f.intent_text,
                    "repetition_count": f.repetition_count,
                    "fulfillment_status": f.fulfillment_status
                }
                for f in critical[:10]
            ],
            "empire": "@empire",
            "braintrust": "@braintrust"
        }

        return report

    def save_database(self):
        try:
            """Save fulfillment database"""
            data = {
                "last_updated": datetime.now().isoformat(),
                "fulfillments": {
                    intent_id: asdict(fulfillment)
                    for intent_id, fulfillment in self.fulfillments.items()
                },
                "empire": "@empire",
                "braintrust": "@braintrust"
            }

            with open(self.fulfillment_db, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Saved fulfillment database: {len(self.fulfillments)} intents")


        except Exception as e:
            self.logger.error(f"Error in save_database: {e}", exc_info=True)
            raise
def main():
    try:
        """Main execution - Initialize and update intent fulfillment tracking"""
        import argparse

        parser = argparse.ArgumentParser(description="Intent Fulfillment Tracking - @empire")
        parser.add_argument("--auto-link", action="store_true", help="Auto-link intents to work items")
        parser.add_argument("--check-status", action="store_true", help="Check fulfillment status from work items")
        parser.add_argument("--report", action="store_true", help="Generate fulfillment report")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        tracker = IntentFulfillmentTracker(project_root)

        if args.auto_link:
            tracker.auto_link_work_items()
            tracker.save_database()

        if args.check_status:
            tracker.check_fulfillment_status()
            tracker.save_database()

        if args.report:
            report = tracker.generate_report()
            report_file = project_root / "data" / "user_intents" / f"fulfillment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Report saved: {report_file}")

        # Always save at end
        tracker.save_database()

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())