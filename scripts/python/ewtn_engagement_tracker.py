#!/usr/bin/env python3
"""
EWTN Engagement Tracker

Weekly status tracking, reporting, and AI/JARVIS validation for EWTN engagement.
Automates follow-up, status reports, and validation requests.

Usage:
    python ewtn_engagement_tracker.py --status
    python ewtn_engagement_tracker.py --report
    python ewtn_engagement_tracker.py --validate
    python ewtn_engagement_tracker.py --weekly-check
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
logger = get_logger("ewtn_engagement_tracker")


try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)


@dataclass
class EngagementStatus:
    """Status of EWTN engagement"""
    current_phase: str = "initial_contact"
    last_contact_date: Optional[str] = None
    last_response_date: Optional[str] = None
    next_followup_date: Optional[str] = None
    contact_count: int = 0
    response_received: bool = False
    meeting_scheduled: bool = False
    partnership_status: str = "pending"
    notes: List[str] = field(default_factory=list)
    actions_taken: List[str] = field(default_factory=list)
    validation_requests: List[Dict] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ValidationRequest:
    """AI/JARVIS validation request"""
    request_id: str
    request_type: str  # "status_review", "strategy_validation", "next_steps"
    question: str
    context: Dict
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    response: Optional[Dict] = None
    validated: bool = False


class EWTNEngagementTracker:
    """Track EWTN engagement status and generate reports"""

    EWTN_CONTACT = {
        "email": "ewtnmissionaries@ewtn.com",
        "phone": "205-795-5771",
        "address": "5817 Old Leeds Road, Irondale, AL 35210"
    }

    PHASES = [
        "initial_contact",
        "proposal_sent",
        "awaiting_response",
        "meeting_scheduled",
        "partnership_discussion",
        "agreement_negotiation",
        "partnership_active",
        "on_hold",
        "declined"
    ]

    def __init__(self, project_root: Path, data_dir: Path = None):
        """
        Initialize EWTN Engagement Tracker.

        Args:
            project_root: Project root directory
            data_dir: Data directory for tracking data
        """
        self.project_root = Path(project_root)
        self.data_dir = data_dir or (self.project_root / "data" / "ewtn_engagement")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger = get_logger("EWTNEngagementTracker")

        # Status file
        self.status_file = self.data_dir / "engagement_status.json"
        self.status: EngagementStatus = EngagementStatus()

        # Validation requests file
        self.validation_file = self.data_dir / "validation_requests.json"
        self.validation_requests: List[Dict] = []

        # Reports directory
        self.reports_dir = self.data_dir / "reports"
        self.reports_dir.mkdir(exist_ok=True)

        # Load existing data
        self.load_status()
        self.load_validations()

    def load_status(self) -> None:
        """Load engagement status"""
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.status = EngagementStatus(**data)
            except Exception as e:
                self.logger.warning(f"Failed to load status: {e}")

    def save_status(self) -> None:
        """Save engagement status"""
        try:
            self.status.updated_at = datetime.now().isoformat()
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.status), f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save status: {e}")

    def load_validations(self) -> None:
        """Load validation requests"""
        if self.validation_file.exists():
            try:
                with open(self.validation_file, 'r', encoding='utf-8') as f:
                    self.validation_requests = json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load validations: {e}")

    def save_validations(self) -> None:
        """Save validation requests"""
        try:
            with open(self.validation_file, 'w', encoding='utf-8') as f:
                json.dump(self.validation_requests, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save validations: {e}")

    def update_status(
        self,
        phase: Optional[str] = None,
        note: Optional[str] = None,
        action: Optional[str] = None,
        response_received: Optional[bool] = None,
        meeting_scheduled: Optional[bool] = None
    ) -> None:
        """
        Update engagement status.

        Args:
            phase: Current phase
            note: Note to add
            action: Action taken
            response_received: Whether response was received
            meeting_scheduled: Whether meeting was scheduled
        """
        if phase:
            if phase in self.PHASES:
                self.status.current_phase = phase
            else:
                self.logger.warning(f"Unknown phase: {phase}")

        if note:
            self.status.notes.append(f"{datetime.now().isoformat()}: {note}")

        if action:
            self.status.actions_taken.append(f"{datetime.now().isoformat()}: {action}")

        if response_received is not None:
            self.status.response_received = response_received
            if response_received:
                self.status.last_response_date = datetime.now().isoformat()

        if meeting_scheduled is not None:
            self.status.meeting_scheduled = meeting_scheduled

        # Update last contact if phase changed
        if phase and phase in ["initial_contact", "proposal_sent"]:
            self.status.last_contact_date = datetime.now().isoformat()
            self.status.contact_count += 1

        # Calculate next follow-up (1 week from last contact)
        if self.status.last_contact_date:
            last_contact = datetime.fromisoformat(self.status.last_contact_date)
            next_followup = last_contact + timedelta(days=7)
            self.status.next_followup_date = next_followup.isoformat()

        self.save_status()

    def get_status(self) -> Dict:
        """Get current status"""
        return {
            "current_phase": self.status.current_phase,
            "partnership_status": self.status.partnership_status,
            "last_contact": self.status.last_contact_date,
            "last_response": self.status.last_response_date,
            "next_followup": self.status.next_followup_date,
            "contact_count": self.status.contact_count,
            "response_received": self.status.response_received,
            "meeting_scheduled": self.status.meeting_scheduled,
            "days_since_last_contact": self._days_since(self.status.last_contact_date),
            "days_until_followup": self._days_until(self.status.next_followup_date),
            "recent_notes": self.status.notes[-5:] if self.status.notes else [],
            "recent_actions": self.status.actions_taken[-5:] if self.status.actions_taken else []
        }

    def _days_since(self, date_str: Optional[str]) -> Optional[int]:
        """Calculate days since date"""
        if not date_str:
            return None
        try:
            date = datetime.fromisoformat(date_str)
            return (datetime.now() - date).days
        except Exception:
            return None

    def _days_until(self, date_str: Optional[str]) -> Optional[int]:
        """Calculate days until date"""
        if not date_str:
            return None
        try:
            date = datetime.fromisoformat(date_str)
            return (date - datetime.now()).days
        except Exception:
            return None

    def generate_weekly_report(self) -> str:
        """Generate weekly status report"""
        status = self.get_status()

        report = f"""
=== EWTN Engagement Weekly Status Report ===
Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

CURRENT STATUS:
  Phase: {status['current_phase'].replace('_', ' ').title()}
  Partnership Status: {status['partnership_status'].title()}
  Contact Count: {status['contact_count']}
  Response Received: {'Yes' if status['response_received'] else 'No'}
  Meeting Scheduled: {'Yes' if status['meeting_scheduled'] else 'No'}

TIMELINE:
  Last Contact: {status['last_contact'] or 'Never'}
  Days Since Last Contact: {status['days_since_last_contact'] or 'N/A'}
  Last Response: {status['last_response'] or 'None'}
  Next Follow-up: {status['next_followup'] or 'Not scheduled'}
  Days Until Follow-up: {status['days_until_followup'] or 'N/A'}

RECENT ACTIVITY:
"""
        if status['recent_actions']:
            for action in status['recent_actions']:
                report += f"  - {action}\n"
        else:
            report += "  No recent actions\n"

        report += f"\nRECENT NOTES:\n"
        if status['recent_notes']:
            for note in status['recent_notes']:
                report += f"  - {note}\n"
        else:
            report += "  No recent notes\n"

        report += f"\nNEXT STEPS:\n"
        next_steps = self._get_next_steps(status)
        for i, step in enumerate(next_steps, 1):
            report += f"  {i}. {step}\n"

        report += f"\nEWTN CONTACT:\n"
        report += f"  Email: {self.EWTN_CONTACT['email']}\n"
        report += f"  Phone: {self.EWTN_CONTACT['phone']}\n"
        report += f"  Address: {self.EWTN_CONTACT['address']}\n"

        return report

    def _get_next_steps(self, status: Dict) -> List[str]:
        """Get recommended next steps based on status"""
        steps = []

        phase = status['current_phase']
        days_since = status['days_since_last_contact'] or 0
        response_received = status['response_received']

        if phase == "initial_contact" and days_since == 0:
            steps.append("Send initial contact email with proposal")
            steps.append("Follow up with phone call if no response in 3 days")

        elif phase == "proposal_sent" and not response_received:
            if days_since >= 7:
                steps.append("Send follow-up email (1 week since proposal)")
                steps.append("Consider phone follow-up")
            elif days_since >= 14:
                steps.append("Send second follow-up email")
                steps.append("Schedule phone call")
            else:
                steps.append(f"Wait for response (sent {days_since} days ago)")

        elif response_received:
            steps.append("Schedule meeting to discuss proposal")
            steps.append("Prepare detailed presentation")
            steps.append("Review EWTN's needs and customize offer")

        elif phase == "meeting_scheduled":
            steps.append("Prepare for meeting")
            steps.append("Review proposal and prepare answers")
            steps.append("Prepare technology demos")

        else:
            steps.append("Review current status and adjust strategy")
            steps.append("Request AI/JARVIS validation")

        return steps

    def request_validation(
        self,
        request_type: str,
        question: str,
        context: Dict
    ) -> str:
        """
        Request AI/JARVIS validation.

        Args:
            request_type: Type of validation request
            question: Question to ask
            context: Context information

        Returns:
            Validation request ID
        """
        request_id = f"val_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        validation = {
            "request_id": request_id,
            "request_type": request_type,
            "question": question,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
            "response": None
        }

        self.validation_requests.append(validation)
        self.save_validations()

        # Add to status
        self.status.validation_requests.append({
            "request_id": request_id,
            "type": request_type,
            "question": question,
            "timestamp": datetime.now().isoformat()
        })
        self.save_status()

        self.logger.info(f"Created validation request: {request_id}")
        return request_id

    def generate_validation_questions(self) -> List[Dict]:
        """Generate standard validation questions for weekly check"""
        status = self.get_status()

        questions = []

        # Status review question
        questions.append({
            "type": "status_review",
            "question": f"Review current engagement status. Phase: {status['current_phase']}, "
                       f"Days since last contact: {status['days_since_last_contact']}. "
                       f"Is our approach appropriate? Should we adjust strategy?",
            "context": status
        })

        # Next steps validation
        next_steps = self._get_next_steps(status)
        questions.append({
            "type": "next_steps_validation",
            "question": f"Validate recommended next steps: {', '.join(next_steps)}. "
                       f"Are these appropriate? Any additional recommendations?",
            "context": {"next_steps": next_steps, "status": status}
        })

        # Strategy validation
        questions.append({
            "type": "strategy_validation",
            "question": "Review our overall engagement strategy. Is our three-part offer "
                       "(Asynchronous Affiliation, Volunteer Support, Cross-Promotion) still appropriate? "
                       "Any adjustments needed?",
            "context": {"status": status, "offer": "three_part"}
        })

        return questions

    def weekly_check(self) -> Dict:
        try:
            """Perform weekly check: status, report, validation"""
            self.logger.info("Performing weekly EWTN engagement check...")

            # Get current status
            status = self.get_status()

            # Generate report
            report = self.generate_weekly_report()

            # Generate validation questions
            validation_questions = self.generate_validation_questions()

            # Create validation requests
            validation_ids = []
            for q in validation_questions:
                request_id = self.request_validation(
                    request_type=q["type"],
                    question=q["question"],
                    context=q["context"]
                )
                validation_ids.append(request_id)

            # Save report
            report_file = self.reports_dir / f"weekly_report_{datetime.now().strftime('%Y%m%d')}.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)

            # Save validation questions
            validation_file = self.reports_dir / f"validation_questions_{datetime.now().strftime('%Y%m%d')}.json"
            with open(validation_file, 'w', encoding='utf-8') as f:
                json.dump(validation_questions, f, indent=2, ensure_ascii=False)

            result = {
                "timestamp": datetime.now().isoformat(),
                "status": status,
                "report_file": str(report_file),
                "validation_questions": validation_questions,
                "validation_ids": validation_ids,
                "summary": {
                    "phase": status['current_phase'],
                    "days_since_contact": status['days_since_last_contact'],
                    "response_received": status['response_received'],
                    "followup_needed": status['days_until_followup'] is not None and status['days_until_followup'] <= 0
                }
            }

            self.logger.info(f"Weekly check complete. Report: {report_file}")
            return result


        except Exception as e:
            self.logger.error(f"Error in weekly_check: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        parser = argparse.ArgumentParser(description="EWTN Engagement Tracker")
        parser.add_argument(
            "--status",
            action="store_true",
            help="Show current status"
        )
        parser.add_argument(
            "--report",
            action="store_true",
            help="Generate weekly report"
        )
        parser.add_argument(
            "--validate",
            action="store_true",
            help="Generate validation questions"
        )
        parser.add_argument(
            "--weekly-check",
            action="store_true",
            help="Perform complete weekly check (status + report + validation)"
        )
        parser.add_argument(
            "--update-phase",
            type=str,
            help="Update current phase"
        )
        parser.add_argument(
            "--add-note",
            type=str,
            help="Add a note"
        )
        parser.add_argument(
            "--add-action",
            type=str,
            help="Record an action taken"
        )
        parser.add_argument(
            "--response-received",
            action="store_true",
            help="Mark response as received"
        )
        parser.add_argument(
            "--meeting-scheduled",
            action="store_true",
            help="Mark meeting as scheduled"
        )
        parser.add_argument(
            "--project-root",
            type=Path,
            default=Path(__file__).parent.parent.parent,
            help="Project root directory"
        )

        args = parser.parse_args()

        tracker = EWTNEngagementTracker(project_root=args.project_root)

        if args.weekly_check:
            result = tracker.weekly_check()
            print(json.dumps(result, indent=2))
            print(f"\n📊 Report saved to: {result['report_file']}")
            print(f"❓ Validation questions: {len(result['validation_questions'])}")

        elif args.status:
            status = tracker.get_status()
            print(json.dumps(status, indent=2))

        elif args.report:
            report = tracker.generate_weekly_report()
            print(report)

        elif args.validate:
            questions = tracker.generate_validation_questions()
            print(json.dumps(questions, indent=2))

        elif args.update_phase:
            tracker.update_status(phase=args.update_phase)
            print(f"✅ Updated phase to: {args.update_phase}")

        elif args.add_note:
            tracker.update_status(note=args.add_note)
            print(f"✅ Added note: {args.add_note}")

        elif args.add_action:
            tracker.update_status(action=args.add_action)
            print(f"✅ Recorded action: {args.add_action}")

        elif args.response_received:
            tracker.update_status(response_received=True)
            print("✅ Marked response as received")

        elif args.meeting_scheduled:
            tracker.update_status(meeting_scheduled=True)
            print("✅ Marked meeting as scheduled")

        else:
            # Show current status
            status = tracker.get_status()
            print("EWTN Engagement Tracker")
            print(f"  Phase: {status['current_phase']}")
            print(f"  Days Since Last Contact: {status['days_since_last_contact']}")
            print(f"  Response Received: {status['response_received']}")
            print(f"\nUse --help for available commands")
            print(f"\nQuick commands:")
            print(f"  --weekly-check    : Complete weekly check")
            print(f"  --status          : Show current status")
            print(f"  --report          : Generate report")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()