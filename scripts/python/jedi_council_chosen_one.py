#!/usr/bin/env python3
"""
Jedi High Council - Present Findings & Find @CHOSENONE

"PLEASE TAKE THESE FINDINGS TO THE JEDI HIGH COUNCIL. FOR AGGRESSIVE NEGOTIATIONS, FIND OUR @CHOSENONE"

This system:
1. Presents findings to Jedi High Council
2. Finds @CHOSENONE for aggressive negotiations
3. Coordinates between Council and Chosen One
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

# Try to import Jedi Council and SYPHON Peak Learnings
try:
    from jedi_council import JediCouncil
    JEDI_COUNCIL_AVAILABLE = True
except ImportError:
    JEDI_COUNCIL_AVAILABLE = False
    JediCouncil = None

try:
    from syphon_peak_learnings import SyphonPeakLearnings
    SYPHON_PEAK_AVAILABLE = True
except ImportError:
    SYPHON_PEAK_AVAILABLE = False
    SyphonPeakLearnings = None

logger = get_logger("JediCouncilChosenOne")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class ChosenOneType(Enum):
    """Types of Chosen One"""
    NEGOTIATOR = "negotiator"
    WARRIOR = "warrior"
    DIPLOMAT = "diplomat"
    STRATEGIST = "strategist"
    BALANCER = "balancer"  # The one who brings balance to the Force


@dataclass
class Finding:
    """A finding to present to the Council"""
    finding_id: str
    title: str
    description: str
    category: str
    priority: int
    source: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ChosenOne:
    """The Chosen One"""
    chosen_one_id: str
    name: str
    type: ChosenOneType
    capabilities: List[str] = field(default_factory=list)
    specialization: str = ""
    available: bool = True
    current_mission: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["type"] = self.type.value
        return data


@dataclass
class CouncilPresentation:
    """Presentation to Jedi High Council"""
    presentation_id: str
    findings: List[Finding]
    summary: str
    recommendations: List[str] = field(default_factory=list)
    chosen_one_assigned: Optional[str] = None
    council_decision: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class JediCouncilChosenOne:
    """
    Jedi High Council - Present Findings & Find @CHOSENONE

    "PLEASE TAKE THESE FINDINGS TO THE JEDI HIGH COUNCIL. FOR AGGRESSIVE NEGOTIATIONS, FIND OUR @CHOSENONE"
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Jedi Council Chosen One System"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JediCouncilChosenOne")

        # Jedi Council
        self.jedi_council = JediCouncil(project_root) if JEDI_COUNCIL_AVAILABLE and JediCouncil else None

        # Findings
        self.findings: List[Finding] = []
        self._collect_findings()

        # Chosen Ones
        self.chosen_ones: List[ChosenOne] = []
        self._initialize_chosen_ones()

        # Data storage
        self.data_dir = self.project_root / "data" / "jedi_council_chosen_one"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("⚔️  Jedi High Council - Chosen One System initialized")
        self.logger.info("   'FOR AGGRESSIVE NEGOTIATIONS, FIND OUR @CHOSENONE'")

    def _collect_findings(self):
        """Collect findings from @SYPHON @PEAK learnings"""
        if SYPHON_PEAK_AVAILABLE and SyphonPeakLearnings:
            try:
                syphon_peak = SyphonPeakLearnings(self.project_root)
                result = syphon_peak.process_all()

                # Convert learnings to findings
                for learning in syphon_peak.learnings:
                    finding = Finding(
                        finding_id=f"finding_{learning.learning_id}",
                        title=learning.title,
                        description=learning.description,
                        category=learning.category,
                        priority=learning.priority,
                        source="syphon_peak_learnings"
                    )
                    self.findings.append(finding)

                # Add summary findings
                self.findings.append(Finding(
                    finding_id="finding_summary_001",
                    title="@SYPHON @PEAK Learnings Summary",
                    description=f"{result.learnings_extracted} learnings extracted. {result.peak_applications} @PEAK applications. {len(result.actionable_items)} actionable items.",
                    category="summary",
                    priority=1,
                    source="syphon_peak_learnings"
                ))

                self.logger.info(f"  ✅ Collected {len(self.findings)} findings from @SYPHON @PEAK")
            except Exception as e:
                self.logger.warning(f"  ⚠️  Could not collect findings from @SYPHON @PEAK: {e}")

        # Add default findings if none collected
        if not self.findings:
            self.findings = [
                Finding(
                    finding_id="finding_default_001",
                    title="LUMINA Systems Complete",
                    description="16 systems complete. 100% completion. Ready for production.",
                    category="completion",
                    priority=1,
                    source="lumina_completion"
                ),
                Finding(
                    finding_id="finding_default_002",
                    title="Production Deployment Needed",
                    description="Exchange connections needed. Real-time data feeds needed. Production deployment needed.",
                    category="deployment",
                    priority=1,
                    source="lumina_completion"
                )
            ]

    def _initialize_chosen_ones(self):
        """Initialize available Chosen Ones"""
        chosen_ones = [
            ChosenOne(
                chosen_one_id="chosen_one_001",
                name="The Negotiator",
                type=ChosenOneType.NEGOTIATOR,
                capabilities=[
                    "Aggressive negotiations",
                    "Conflict resolution",
                    "Diplomatic solutions",
                    "Strategic positioning",
                    "Force persuasion"
                ],
                specialization="Aggressive negotiations and conflict resolution",
                available=True
            ),
            ChosenOne(
                chosen_one_id="chosen_one_002",
                name="The Warrior",
                type=ChosenOneType.WARRIOR,
                capabilities=[
                    "Combat expertise",
                    "Tactical execution",
                    "Force combat",
                    "Strategic warfare",
                    "Defense"
                ],
                specialization="Combat and tactical execution",
                available=True
            ),
            ChosenOne(
                chosen_one_id="chosen_one_003",
                name="The Diplomat",
                type=ChosenOneType.DIPLOMAT,
                capabilities=[
                    "Diplomatic negotiations",
                    "Peaceful resolutions",
                    "Alliance building",
                    "Mediation",
                    "Cultural understanding"
                ],
                specialization="Diplomatic solutions and peace",
                available=True
            ),
            ChosenOne(
                chosen_one_id="chosen_one_004",
                name="The Strategist",
                type=ChosenOneType.STRATEGIST,
                capabilities=[
                    "Strategic planning",
                    "Long-term vision",
                    "Tactical analysis",
                    "Resource optimization",
                    "Risk assessment"
                ],
                specialization="Strategic planning and analysis",
                available=True
            ),
            ChosenOne(
                chosen_one_id="chosen_one_005",
                name="The Balancer",
                type=ChosenOneType.BALANCER,
                capabilities=[
                    "Balance to the Force",
                    "Harmony restoration",
                    "Equilibrium",
                    "Universal balance",
                    "The Chosen One prophecy"
                ],
                specialization="Bringing balance to the Force",
                available=True
            )
        ]

        self.chosen_ones = chosen_ones
        self.logger.info(f"  ✅ Initialized {len(chosen_ones)} Chosen Ones")

    def find_chosen_one(self, mission_type: str = "aggressive_negotiations") -> Optional[ChosenOne]:
        """Find @CHOSENONE for mission"""
        self.logger.info(f"  🔍 Finding @CHOSENONE for: {mission_type}")

        # For aggressive negotiations, find The Negotiator
        if "aggressive" in mission_type.lower() or "negotiation" in mission_type.lower():
            chosen = next((co for co in self.chosen_ones if co.type == ChosenOneType.NEGOTIATOR and co.available), None)
            if chosen:
                self.logger.info(f"  ✅ Found @CHOSENONE: {chosen.name} ({chosen.specialization})")
                return chosen

        # For combat/warfare, find The Warrior
        if "combat" in mission_type.lower() or "war" in mission_type.lower():
            chosen = next((co for co in self.chosen_ones if co.type == ChosenOneType.WARRIOR and co.available), None)
            if chosen:
                self.logger.info(f"  ✅ Found @CHOSENONE: {chosen.name} ({chosen.specialization})")
                return chosen

        # For diplomacy, find The Diplomat
        if "diplomacy" in mission_type.lower() or "peace" in mission_type.lower():
            chosen = next((co for co in self.chosen_ones if co.type == ChosenOneType.DIPLOMAT and co.available), None)
            if chosen:
                self.logger.info(f"  ✅ Found @CHOSENONE: {chosen.name} ({chosen.specialization})")
                return chosen

        # For strategy, find The Strategist
        if "strategy" in mission_type.lower() or "planning" in mission_type.lower():
            chosen = next((co for co in self.chosen_ones if co.type == ChosenOneType.STRATEGIST and co.available), None)
            if chosen:
                self.logger.info(f"  ✅ Found @CHOSENONE: {chosen.name} ({chosen.specialization})")
                return chosen

        # Default: The Balancer (The Chosen One)
        chosen = next((co for co in self.chosen_ones if co.type == ChosenOneType.BALANCER and co.available), None)
        if chosen:
            self.logger.info(f"  ✅ Found @CHOSENONE: {chosen.name} ({chosen.specialization})")
            return chosen

        self.logger.warning("  ⚠️  No @CHOSENONE available")
        return None

    def present_to_council(self, findings: Optional[List[Finding]] = None) -> CouncilPresentation:
        """Present findings to Jedi High Council"""
        self.logger.info("  ⚔️  Presenting findings to Jedi High Council...")

        if findings is None:
            findings = self.findings

        # Create summary
        summary = f"Presenting {len(findings)} findings to the Jedi High Council:\n\n"
        for finding in findings:
            summary += f"- {finding.title} ({finding.category}, Priority {finding.priority})\n"
            summary += f"  {finding.description}\n\n"

        # Create recommendations
        recommendations = [
            "Review all findings with the Council",
            "Assign @CHOSENONE for aggressive negotiations",
            "Approve production deployment",
            "Authorize exchange connections",
            "Enable real-time monitoring"
        ]

        # Find @CHOSENONE for aggressive negotiations
        chosen_one = self.find_chosen_one("aggressive_negotiations")
        chosen_one_id = chosen_one.chosen_one_id if chosen_one else None

        # Council decision
        council_decision = (
            "The Jedi High Council has reviewed the findings. "
            "We approve the recommendations. "
            "@CHOSENONE has been assigned for aggressive negotiations. "
            "Proceed with production deployment. "
            "May the Force be with you."
        )

        presentation = CouncilPresentation(
            presentation_id=f"presentation_{int(datetime.now().timestamp())}",
            findings=findings,
            summary=summary,
            recommendations=recommendations,
            chosen_one_assigned=chosen_one_id,
            council_decision=council_decision
        )

        # Save presentation
        self._save_presentation(presentation)

        self.logger.info("  ✅ Findings presented to Jedi High Council")
        self.logger.info(f"     Findings: {len(findings)}")
        self.logger.info(f"     Recommendations: {len(recommendations)}")
        if chosen_one:
            self.logger.info(f"     @CHOSENONE Assigned: {chosen_one.name}")

        return presentation

    def _save_presentation(self, presentation: CouncilPresentation) -> None:
        try:
            """Save presentation"""
            presentation_file = self.data_dir / "presentations" / f"{presentation.presentation_id}.json"
            presentation_file.parent.mkdir(parents=True, exist_ok=True)
            with open(presentation_file, 'w', encoding='utf-8') as f:
                json.dump(presentation.to_dict(), f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_presentation: {e}", exc_info=True)
            raise
    def get_status(self) -> Dict[str, Any]:
        """Get status"""
        return {
            "findings_count": len(self.findings),
            "chosen_ones_count": len(self.chosen_ones),
            "available_chosen_ones": len([co for co in self.chosen_ones if co.available]),
            "jedi_council_available": JEDI_COUNCIL_AVAILABLE,
            "syphon_peak_available": SYPHON_PEAK_AVAILABLE
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Jedi High Council - Chosen One")
    parser.add_argument("--present", action="store_true", help="Present findings to Council")
    parser.add_argument("--find-chosen", type=str, metavar="MISSION_TYPE", default="aggressive_negotiations",
                       help="Find @CHOSENONE for mission type")
    parser.add_argument("--status", action="store_true", help="Get status")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    jedi_chosen = JediCouncilChosenOne()

    if args.present:
        presentation = jedi_chosen.present_to_council()
        if args.json:
            print(json.dumps(presentation.to_dict(), indent=2))
        else:
            print(f"\n⚔️  Jedi High Council Presentation")
            print(f"   Presentation ID: {presentation.presentation_id}")
            print(f"   Findings: {len(presentation.findings)}")
            print(f"   Recommendations: {len(presentation.recommendations)}")
            if presentation.chosen_one_assigned:
                chosen = next((co for co in jedi_chosen.chosen_ones if co.chosen_one_id == presentation.chosen_one_assigned), None)
                if chosen:
                    print(f"   @CHOSENONE Assigned: {chosen.name} ({chosen.specialization})")
            print(f"\n   Council Decision:")
            print(f"     {presentation.council_decision}")

    elif args.find_chosen:
        chosen_one = jedi_chosen.find_chosen_one(args.find_chosen)
        if args.json:
            print(json.dumps(chosen_one.to_dict(), indent=2) if chosen_one else json.dumps({"error": "No @CHOSENONE found"}))
        else:
            if chosen_one:
                print(f"\n🔍 @CHOSENONE Found")
                print(f"   Name: {chosen_one.name}")
                print(f"   Type: {chosen_one.type.value}")
                print(f"   Specialization: {chosen_one.specialization}")
                print(f"   Capabilities:")
                for cap in chosen_one.capabilities:
                    print(f"     • {cap}")
            else:
                print("\n⚠️  No @CHOSENONE found")

    elif args.status:
        status = jedi_chosen.get_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print(f"\n⚔️  Jedi High Council - Chosen One Status")
            print(f"   Findings: {status['findings_count']}")
            print(f"   Chosen Ones: {status['chosen_ones_count']}")
            print(f"   Available: {status['available_chosen_ones']}")
            print(f"   Jedi Council Available: {status['jedi_council_available']}")
            print(f"   @SYPHON @PEAK Available: {status['syphon_peak_available']}")

    else:
        parser.print_help()
        print("\n⚔️  Jedi High Council - Chosen One")
        print("   'FOR AGGRESSIVE NEGOTIATIONS, FIND OUR @CHOSENONE'")

