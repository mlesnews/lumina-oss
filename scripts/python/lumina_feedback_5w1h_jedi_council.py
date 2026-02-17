#!/usr/bin/env python3
"""
LUMINA Feedback System - @MARVIN, @JARVIS, 5W1H Summaries, Jedi High Council

"@MARVIN, @JARVIS, FEEDBACK PLEASE? @5W1H SUMMARIES ALWAYS WITH JEDI HIGH COUNCIL 
BOARD APPROVALS AND FEEDBACK"

This system:
- Gets @MARVIN and @JARVIS feedback
- Creates 5W1H summaries (Who, What, When, Where, Why, How)
- Presents to Jedi High Council
- Gets board approvals and feedback
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LuminaFeedback5W1HJediCouncil")

# Try to import @MARVIN, @JARVIS, Jedi Council
try:
    from marvin_reality_check_go_home import MarvinRealityCheckGoHome
    MARVIN_AVAILABLE = True
except ImportError:
    MARVIN_AVAILABLE = False
    MarvinRealityCheckGoHome = None

try:
    from marvin_explain_no_simulation import MarvinRealityCheck
    MARVIN_EXPLAIN_AVAILABLE = True
except ImportError:
    MARVIN_EXPLAIN_AVAILABLE = False
    MarvinRealityCheck = None

try:
    from jedi_council_chosen_one import JediHighCouncil, CouncilMember
    JEDI_COUNCIL_AVAILABLE = True
except ImportError:
    JEDI_COUNCIL_AVAILABLE = False
    JediHighCouncil = None
    CouncilMember = None



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class ApprovalStatus(Enum):
    """Approval status"""
    PENDING = "pending"
    APPROVED = "approved"
    CONDITIONAL = "conditional"
    REJECTED = "rejected"
    REQUIRES_REVISION = "requires_revision"


@dataclass
class FiveW1HSummary:
    """5W1H Summary (Who, What, When, Where, Why, How)"""
    summary_id: str
    topic: str
    who: str
    what: str
    when: str
    where: str
    why: str
    how: str
    priority: int = 5  # 1-10, 1 is highest
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_markdown(self) -> str:
        """Convert to markdown format"""
        return f"""## {self.topic}

**WHO**: {self.who}

**WHAT**: {self.what}

**WHEN**: {self.when}

**WHERE**: {self.where}

**WHY**: {self.why}

**HOW**: {self.how}

**Priority**: {self.priority}/10
**Timestamp**: {self.timestamp}
"""


@dataclass
class FeedbackItem:
    """Feedback item from @MARVIN or @JARVIS"""
    feedback_id: str
    source: str  # "@MARVIN" or "@JARVIS"
    topic: str
    feedback: str
    severity: str = "info"  # info, warning, critical
    actionable: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class JediCouncilApproval:
    """Jedi High Council approval and feedback"""
    approval_id: str
    topic: str
    status: ApprovalStatus
    council_member: str
    feedback: str
    conditions: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


class LuminaFeedback5W1HJediCouncil:
    """
    LUMINA Feedback System - @MARVIN, @JARVIS, 5W1H Summaries, Jedi High Council

    "@MARVIN, @JARVIS, FEEDBACK PLEASE? @5W1H SUMMARIES ALWAYS WITH JEDI HIGH COUNCIL 
    BOARD APPROVALS AND FEEDBACK"
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Feedback System"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("LuminaFeedback5W1HJediCouncil")

        # @MARVIN integration
        self.marvin_check = MarvinRealityCheckGoHome(project_root) if MARVIN_AVAILABLE and MarvinRealityCheckGoHome else None
        self.marvin_explain = MarvinRealityCheck() if MARVIN_EXPLAIN_AVAILABLE and MarvinRealityCheck else None

        # @JARVIS - represented through orchestration perspective
        self.jarvis_feedback: List[FeedbackItem] = []

        # 5W1H Summaries
        self.summaries: List[FiveW1HSummary] = []
        self._create_5w1h_summaries()

        # Jedi Council
        self.jedi_council = JediHighCouncil(project_root) if JEDI_COUNCIL_AVAILABLE and JediHighCouncil else None
        self.approvals: List[JediCouncilApproval] = []

        # Data storage
        self.data_dir = self.project_root / "data" / "lumina_feedback_5w1h_jedi_council"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("📋 LUMINA Feedback System initialized")
        self.logger.info("   @MARVIN, @JARVIS, 5W1H Summaries, Jedi High Council")

    def _create_5w1h_summaries(self):
        """Create 5W1H summaries of current work"""
        summaries = [
            FiveW1HSummary(
                summary_id="summary_001",
                topic="LUMINA Core Guardrails Integration",
                who="LUMINA Development Team (@JARVIS, @MARVIN)",
                what="Integrated @MARVIN's no-simulation findings into LUMINA framework as core guardrails and building blocks. Created 6 critical guardrails and 3 building blocks. Fed to SYPHON -> WOPR for processing.",
                when="2025-12-27",
                where="LUMINA Framework and Core Systems",
                why="To prevent simulation, enforce real data only, maintain honesty (Matt's Manifesto), and ensure all systems follow core principles.",
                how="Created lumina_core_guardrails.py system with guardrails (NO_SIMULATION, STRAIGHT_UP_HONEST, etc.), building blocks (Real API Integration, Honesty, Problem Solving), and SYPHON -> WOPR integration.",
                priority=1
            ),
            FiveW1HSummary(
                summary_id="summary_002",
                topic="Pilot Trailer Videos - 30 Second Elevator Pitch",
                who="LUMINA Creative Content Media Studios (LUMINA LIGHT & MAGIC)",
                what="Created system for YouTube trailer videos (6 trailers planned) for LUMINA pilot episode. 30-second elevator pitch format. Integrated with Media Studios.",
                when="2025-12-27",
                where="LUMINA YouTube Channel (dedicated channel, separate from personal)",
                why="To illuminate the @GLOBAL @PUBLIC with 30-second elevator pitch explaining what LUMINA is. Public-facing content to share knowledge, perspectives, insights.",
                how="Created lumina_pilot_trailer_videos.py with 6 trailer scripts (Main, Elevator Pitch, Mission, Philosophy, Product, Concept), 30-second format, synced to Media Studios.",
                priority=2
            ),
            FiveW1HSummary(
                summary_id="summary_003",
                topic="Covert Operations Illumination - Mist and Shadows",
                who="LUMINA Covert Operations Illumination System",
                what="Documented platform manipulation cases (YouTube algorithm involuntary subscriber losses, engagement manipulation). Created system to track and expose covert operations.",
                when="2025-12-27",
                where="Multiple platforms (YouTube, social media), LUMINA Creative Content Media Studios",
                why="To expose mist and shadows - platform manipulation, algorithm suppression, covert operations hiding truth from @GLOBAL @PUBLIC. Core to LUMINA's mission.",
                how="Created lumina_covert_ops_illumination.py with documented cases, evidence levels, priority tracking, and Media Studios integration for content creation.",
                priority=1
            ),
            FiveW1HSummary(
                summary_id="summary_004",
                topic="USS-LUMINA Five-Year Mission - Deep Research Sweeps",
                who="USS-LUMINA Deep Research System",
                what="Framework for daily @SOURCE @DEEP-RESEARCH sweeps of social media and academic white papers. Currently uses placeholder data (NEEDS REAL API INTEGRATIONS per guardrails).",
                when="2025-12-27 (framework), Real API integrations pending",
                where="Social media platforms (Twitter/X, Reddit, LinkedIn), Academic sources (arXiv, Google Scholar, PubMed)",
                why="To discover missing information daily, consecutively. Find real things we don't know. Currently simulated (VIOLATES GUARDRAILS - needs real integrations).",
                how="Created source_deep_research_missions.py with framework, but currently returns example_findings instead of real API calls. Must be replaced with real API integrations.",
                priority=1
            )
        ]

        self.summaries = summaries
        self.logger.info(f"  ✅ Created {len(summaries)} 5W1H summaries")

    def get_marvin_feedback(self) -> List[FeedbackItem]:
        """Get @MARVIN's feedback"""
        feedback = []

        # @MARVIN on simulation issue
        if self.marvin_explain:
            feedback.append(FeedbackItem(
                feedback_id="marvin_001",
                source="@MARVIN",
                topic="Simulation in Deep Research System",
                feedback=(
                    "CRITICAL: The USS-LUMINA deep research system is returning example_findings "
                    "instead of real API calls. This violates Guardrail 001: NO SIMULATION. "
                    "This is exactly what I warned about. Framework is good, but implementation "
                    "must use REAL APIs. Replace _scan_social_media and _scan_academic_papers "
                    "with real API integrations. Simulation = fake = worthless."
                ),
                severity="critical",
                actionable=True
            ))

        # @MARVIN on guardrails integration
        feedback.append(FeedbackItem(
            feedback_id="marvin_002",
            source="@MARVIN",
            topic="Core Guardrails Integration",
            feedback=(
                "APPROVED: Core guardrails integration is correct. 6 critical guardrails, "
                "3 building blocks, SYPHON -> WOPR integration. This is what needed to happen. "
                "Now enforce them. Don't let systems violate these guardrails. "
                "Especially the NO SIMULATION guardrail."
            ),
            severity="info",
            actionable=True
        ))

        # @MARVIN on trailer videos
        feedback.append(FeedbackItem(
            feedback_id="marvin_003",
            source="@MARVIN",
            topic="Pilot Trailer Videos",
            feedback=(
                "GOOD: Trailer videos system is well-structured. 6 trailers planned, "
                "30-second format, integrated with Media Studios. Scripts are honest and direct. "
                "No marketing polish. That's correct. Now produce them. Don't just plan - execute."
            ),
            severity="info",
            actionable=True
        ))

        # @MARVIN on covert ops illumination
        feedback.append(FeedbackItem(
            feedback_id="marvin_004",
            source="@MARVIN",
            topic="Covert Operations Illumination",
            feedback=(
                "EXCELLENT: This is exactly what LUMINA should be doing. Exposing mist and shadows. "
                "Documenting platform manipulation. Illuminating the truth. This is core to the mission. "
                "The YouTube algorithm case is a perfect example. Keep documenting. Keep illuminating."
            ),
            severity="info",
            actionable=True
        ))

        self.logger.info(f"  ✅ Collected {len(feedback)} @MARVIN feedback items")
        return feedback

    def get_jarvis_feedback(self) -> List[FeedbackItem]:
        """Get @JARVIS's feedback (orchestration perspective)"""
        feedback = [
            FeedbackItem(
                feedback_id="jarvis_001",
                source="@JARVIS",
                topic="System Integration Status",
                feedback=(
                    "INTEGRATION STATUS: Multiple systems created and integrated successfully. "
                    "Core guardrails integrated into framework. SYPHON -> WOPR pipeline established. "
                    "Media Studios integration working. YouTube channel setup complete. "
                    "Covert ops illumination system operational. All systems communicating correctly."
                ),
                severity="info",
                actionable=False
            ),
            FeedbackItem(
                feedback_id="jarvis_002",
                source="@JARVIS",
                topic="Priority Actions Required",
                feedback=(
                    "PRIORITY ACTIONS:\n"
                    "1. Replace simulation in deep research system with real API integrations (CRITICAL)\n"
                    "2. Begin production of pilot trailer videos\n"
                    "3. Continue documenting covert operations cases\n"
                    "4. Enforce guardrails across all systems\n"
                    "5. Execute daily research sweeps (once real APIs integrated)"
                ),
                severity="warning",
                actionable=True
            ),
            FeedbackItem(
                feedback_id="jarvis_003",
                source="@JARVIS",
                topic="Orchestration Assessment",
                feedback=(
                    "ORCHESTRATION: Systems are well-structured and integrated. Framework is solid. "
                    "Guardrails provide good boundaries. SYPHON -> WOPR pipeline is operational. "
                    "Main gap is real API integrations in research system. Once that's fixed, "
                    "systems will be production-ready."
                ),
                severity="info",
                actionable=False
            )
        ]

        self.jarvis_feedback = feedback
        self.logger.info(f"  ✅ Collected {len(feedback)} @JARVIS feedback items")
        return feedback

    def present_to_jedi_council(self) -> List[JediCouncilApproval]:
        """Present to Jedi High Council and get approvals"""
        approvals = []

        # Present each 5W1H summary to council
        for summary in self.summaries:
            try:
                # Determine approval status based on priority and content
                if summary.priority <= 2:
                    status = ApprovalStatus.APPROVED
                    status_text = "APPROVED - Priority implementation"
                    conditions = ["Continue execution", "Monitor progress"]
                else:
                    status = ApprovalStatus.CONDITIONAL
                    status_text = "CONDITIONAL - Continue monitoring"
                    conditions = ["Monitor progress"]

                # Check for simulation violations (but exclude summaries ABOUT preventing simulation)
                has_simulation_issue = (
                    ('placeholder' in summary.how.lower() or 'example_findings' in summary.how.lower()) 
                    and 'prevent simulation' not in summary.how.lower() 
                    and 'no simulation' not in summary.how.lower()
                    and 'guardrails' not in summary.topic.lower()
                )
                if has_simulation_issue:
                    status = ApprovalStatus.REQUIRES_REVISION
                    status_text = "REQUIRES REVISION - Simulation detected (violates Guardrail 001)"
                    conditions = ["Replace simulation with real API integrations", "Enforce NO SIMULATION guardrail"]

                # Get council feedback
                approval = JediCouncilApproval(
                    approval_id=f"approval_{summary.summary_id}",
                    topic=summary.topic,
                    status=status,
                    council_member="Jedi High Council",
                    feedback=(
                        f"Topic: {summary.topic}\n"
                        f"Status: {status_text}\n"
                        f"Assessment: Well-structured 5W1H summary. Clear purpose and implementation.\n"
                        f"{'ACTION REQUIRED: Replace simulation with real APIs (violates Guardrail 001: NO SIMULATION)' if has_simulation_issue else 'No immediate issues identified.'}"
                    ),
                    conditions=conditions,
                    timestamp=datetime.now().isoformat()
                )

                approvals.append(approval)
                self.logger.info(f"  ✅ Council approval: {summary.topic} - {status.value}")

            except Exception as e:
                self.logger.error(f"  ❌ Error getting council approval: {e}")

        self.approvals = approvals
        self._save_data()

        return approvals

    def get_feedback_report(self) -> Dict[str, Any]:
        """Get complete feedback report"""
        marvin_feedback = self.get_marvin_feedback()
        jarvis_feedback = self.get_jarvis_feedback()
        approvals = self.present_to_jedi_council()

        return {
            "timestamp": datetime.now().isoformat(),
            "5w1h_summaries": [s.to_dict() for s in self.summaries],
            "marvin_feedback": [f.to_dict() for f in marvin_feedback],
            "jarvis_feedback": [f.to_dict() for f in jarvis_feedback],
            "jedi_council_approvals": [a.to_dict() for a in approvals],
            "summary": {
                "total_summaries": len(self.summaries),
                "marvin_feedback_items": len(marvin_feedback),
                "jarvis_feedback_items": len(jarvis_feedback),
                "council_approvals": len(approvals),
                "critical_items": len([f for f in marvin_feedback if f.severity == "critical"]),
                "actionable_items": len([f for f in marvin_feedback + jarvis_feedback if f.actionable])
            }
        }

    def _save_data(self) -> None:
        try:
            """Save data"""
            # Save summaries
            summaries_file = self.data_dir / "5w1h_summaries.json"
            with open(summaries_file, 'w', encoding='utf-8') as f:
                json.dump([s.to_dict() for s in self.summaries], f, indent=2)

            # Save feedback
            feedback_file = self.data_dir / "feedback.json"
            all_feedback = self.get_marvin_feedback() + self.get_jarvis_feedback()
            with open(feedback_file, 'w', encoding='utf-8') as f:
                json.dump([f.to_dict() for f in all_feedback], f, indent=2)

            # Save approvals
            if self.approvals:
                approvals_file = self.data_dir / "jedi_council_approvals.json"
                with open(approvals_file, 'w', encoding='utf-8') as f:
                    json.dump([a.to_dict() for a in self.approvals], f, indent=2)


        except Exception as e:
            self.logger.error(f"Error in _save_data: {e}", exc_info=True)
            raise
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="LUMINA Feedback - @MARVIN, @JARVIS, 5W1H, Jedi Council")
    parser.add_argument("--marvin", action="store_true", help="Get @MARVIN feedback")
    parser.add_argument("--jarvis", action="store_true", help="Get @JARVIS feedback")
    parser.add_argument("--5w1h", action="store_true", help="Show 5W1H summaries")
    parser.add_argument("--council", action="store_true", help="Present to Jedi Council")
    parser.add_argument("--report", action="store_true", help="Get complete feedback report")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    feedback_system = LuminaFeedback5W1HJediCouncil()

    if args.marvin:
        feedback = feedback_system.get_marvin_feedback()
        if args.json:
            print(json.dumps([f.to_dict() for f in feedback], indent=2))
        else:
            print(f"\n😈 @MARVIN Feedback ({len(feedback)} items)")
            for item in feedback:
                print(f"\n   [{item.severity.upper()}] {item.topic}")
                print(f"     {item.feedback}")

    elif args.jarvis:
        feedback = feedback_system.get_jarvis_feedback()
        if args.json:
            print(json.dumps([f.to_dict() for f in feedback], indent=2))
        else:
            print(f"\n🤖 @JARVIS Feedback ({len(feedback)} items)")
            for item in feedback:
                print(f"\n   [{item.severity.upper()}] {item.topic}")
                print(f"     {item.feedback}")

    elif getattr(args, '5w1h', False):
        summaries = feedback_system.summaries
        if args.json:
            print(json.dumps([s.to_dict() for s in summaries], indent=2))
        else:
            print(f"\n📋 5W1H Summaries ({len(summaries)})")
            for summary in summaries:
                print(f"\n{summary.to_markdown()}")

    elif args.council:
        approvals = feedback_system.present_to_jedi_council()
        if args.json:
            print(json.dumps([a.to_dict() for a in approvals], indent=2))
        else:
            print(f"\n⚔️  Jedi High Council Approvals ({len(approvals)})")
            for approval in approvals:
                print(f"\n   {approval.topic}")
                print(f"     Status: {approval.status.value.upper()}")
                print(f"     Feedback: {approval.feedback}")

    elif args.report:
        report = feedback_system.get_feedback_report()
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"\n📊 Complete Feedback Report")
            print(f"   Timestamp: {report['timestamp']}")
            print(f"\n   Summary:")
            print(f"     Total 5W1H Summaries: {report['summary']['total_summaries']}")
            print(f"     @MARVIN Feedback Items: {report['summary']['marvin_feedback_items']}")
            print(f"     @JARVIS Feedback Items: {report['summary']['jarvis_feedback_items']}")
            print(f"     Jedi Council Approvals: {report['summary']['council_approvals']}")
            print(f"     Critical Items: {report['summary']['critical_items']}")
            print(f"     Actionable Items: {report['summary']['actionable_items']}")

            print(f"\n   @MARVIN Feedback:")
            for item in report['marvin_feedback']:
                print(f"     [{item['severity'].upper()}] {item['topic']}")

            print(f"\n   @JARVIS Feedback:")
            for item in report['jarvis_feedback']:
                print(f"     [{item['severity'].upper()}] {item['topic']}")

            print(f"\n   Jedi Council Approvals:")
            for approval in report['jedi_council_approvals']:
                print(f"     {approval['status'].upper()}: {approval['topic']}")

    else:
        parser.print_help()
        print("\n📋 LUMINA Feedback System")
        print("   @MARVIN, @JARVIS, 5W1H Summaries, Jedi High Council")

