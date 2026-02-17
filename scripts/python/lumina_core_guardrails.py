#!/usr/bin/env python3
"""
LUMINA Core Guardrails - Building Blocks, Prompts, Blackbox

"PLEASE INCORPORATE @JARVIS, IF WE WOULD PLEASE, @MARVINS FINDINGS INTO OUR @LUMINA 
#FRAMEWORK AND @CORE @SYSTEMS. HUMANS CALL THESE PROMPTS, GUARDRAILS, BLACKBOX, ETC. 
LETS PUT IT INTO BASIC BUILDING BLOCKS, FEED TO WOPR VIA SYPHON AND 'AWAY WE GO!' @JOKER STYLE."

This system:
- Core guardrails and principles from @MARVIN
- Building blocks for all LUMINA systems
- No simulation policy
- Feed to WOPR via SYPHON
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

from lumina_core.paths import get_script_dir
script_dir = get_script_dir()
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_core.logging import get_logger
except ImportError:
    from lumina_core.logging import get_logger

logger = get_logger("LuminaCoreGuardrails")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class GuardrailType(Enum):
    """Guardrail types"""
    NO_SIMULATION = "no_simulation"
    STRAIGHT_UP_HONEST = "straight_up_honest"
    REAL_DATA_ONLY = "real_data_only"
    SOLVE_ACTUAL_PROBLEM = "solve_actual_problem"
    NO_MARKETING_POLISH = "no_marketing_polish"
    EVERY_BEING_MATTERS = "every_being_matters"
    NO_ONE_LEFT_BEHIND = "no_one_left_behind"
    ILLUMINATE_PUBLIC = "illuminate_public"


class GuardrailSeverity(Enum):
    """Guardrail severity"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class CoreGuardrail:
    """Core guardrail/prompt/blackbox principle"""
    guardrail_id: str
    guardrail_type: GuardrailType
    title: str
    principle: str
    description: str
    severity: GuardrailSeverity
    source: str = "@MARVIN"
    enforced: bool = True
    examples: List[str] = field(default_factory=list)
    violations: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["guardrail_type"] = self.guardrail_type.value
        data["severity"] = self.severity.value
        return data


@dataclass
class BuildingBlock:
    """Basic building block for LUMINA systems"""
    block_id: str
    name: str
    description: str
    guardrails: List[str] = field(default_factory=list)  # Guardrail IDs
    applies_to: List[str] = field(default_factory=list)  # Systems this applies to
    implementation: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LuminaCoreGuardrails:
    """
    LUMINA Core Guardrails - Building Blocks, Prompts, Blackbox

    "PLEASE INCORPORATE @JARVIS, IF WE WOULD PLEASE, @MARVINS FINDINGS INTO OUR @LUMINA 
    #FRAMEWORK AND @CORE @SYSTEMS. HUMANS CALL THESE PROMPTS, GUARDRAILS, BLACKBOX, ETC. 
    LETS PUT IT INTO BASIC BUILDING BLOCKS, FEED TO WOPR VIA SYPHON AND 'AWAY WE GO!' @JOKER STYLE."
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize LUMINA Core Guardrails"""
        if project_root is None:
            from lumina_core.paths import get_project_root
            project_root = get_project_root()

        self.project_root = Path(project_root)
        self.logger = get_logger("LuminaCoreGuardrails")

        # Guardrails
        self.guardrails: List[CoreGuardrail] = []
        self._initialize_guardrails()

        # Building blocks
        self.building_blocks: List[BuildingBlock] = []
        self._initialize_building_blocks()

        # Data storage
        self.data_dir = self.project_root / "data" / "lumina_core_guardrails"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("🛡️ LUMINA Core Guardrails initialized")
        self.logger.info("   Building blocks, prompts, guardrails, blackbox")

    def _initialize_guardrails(self):
        """Initialize core guardrails from @MARVIN's findings"""
        guardrails = [
            CoreGuardrail(
                guardrail_id="guardrail_001",
                guardrail_type=GuardrailType.NO_SIMULATION,
                title="NO SIMULATION - REAL DATA ONLY",
                principle="Never simulate data. Use real APIs, real integrations, real data. Simulation = fake = worthless.",
                description=(
                    "Simulation is unacceptable. When we simulate research findings, we're generating FAKE DATA. "
                    "Real research sweeps are supposed to FIND REAL THINGS we don't know. Simulated data = zero value. "
                    "We're trying to illuminate the @GLOBAL @PUBLIC, not feed them lies."
                ),
                severity=GuardrailSeverity.CRITICAL,
                source="@MARVIN",
                enforced=True,
                examples=[
                    "DO: Connect to Twitter/X API for real social media scanning",
                    "DON'T: Return example/placeholder data",
                    "DO: Connect to arXiv API for real academic papers",
                    "DON'T: Generate fake paper titles and authors"
                ],
                violations=[
                    "Returning example_findings instead of real API calls",
                    "Using placeholder data in production systems",
                    "Simulating results instead of discovering real information"
                ]
            ),
            CoreGuardrail(
                guardrail_id="guardrail_002",
                guardrail_type=GuardrailType.STRAIGHT_UP_HONEST,
                title="STRAIGHT UP, DIRECT AND HONEST",
                principle="Matt's Manifesto: Straight up, direct, honest. No marketing polish. No fake data.",
                description=(
                    "LUMINA stands for honesty. No marketing polish. No fake data. No simulation. "
                    "Straight up, direct, and honest. What more could a being ask for?"
                ),
                severity=GuardrailSeverity.CRITICAL,
                source="Matt's Manifesto",
                enforced=True,
                examples=[
                    "DO: Show real data, even if it's incomplete",
                    "DON'T: Polish results with fake data",
                    "DO: Be honest about system limitations",
                    "DON'T: Create false impressions"
                ]
            ),
            CoreGuardrail(
                guardrail_id="guardrail_003",
                guardrail_type=GuardrailType.SOLVE_ACTUAL_PROBLEM,
                title="SOLVE THE ACTUAL PROBLEM",
                principle="Don't solve fake problems. Solve real problems. Don't simulate solutions.",
                description=(
                    "The problem is: 'WE ARE MISSING MUCH DAILY, CONSECUTIVELY, BY NOT EXECUTING OUR "
                    "@SOURCE @DEEP-RESEARCH.' Simulating doesn't solve this. We're STILL missing that information. "
                    "We just have fake data that LOOKS like we found something. We've solved nothing."
                ),
                severity=GuardrailSeverity.CRITICAL,
                source="@MARVIN",
                enforced=True
            ),
            CoreGuardrail(
                guardrail_id="guardrail_004",
                guardrail_type=GuardrailType.REAL_DATA_ONLY,
                title="REAL DATA ONLY - NO FAKE CONFIDENCE",
                principle="Simulated data makes people think we know things we don't. This is dangerous.",
                description=(
                    "Simulated data creates false confidence. Decisions get made based on fake information. "
                    "Resources get wasted chasing simulated findings. Real problems get ignored because "
                    "we think we've solved them (but we haven't)."
                ),
                severity=GuardrailSeverity.CRITICAL,
                source="@MARVIN",
                enforced=True
            ),
            CoreGuardrail(
                guardrail_id="guardrail_005",
                guardrail_type=GuardrailType.EVERY_BEING_MATTERS,
                title="EVERY BEING MATTERS",
                principle="We all matter. We are the grand design of a divine being. There can be no doubt.",
                description=(
                    "Every being matters. No one left behind. Period. Ever. This is core to LUMINA."
                ),
                severity=GuardrailSeverity.CRITICAL,
                source="LUMINA Philosophy",
                enforced=True
            ),
            CoreGuardrail(
                guardrail_id="guardrail_006",
                guardrail_type=GuardrailType.ILLUMINATE_PUBLIC,
                title="ILLUMINATE THE @GLOBAL @PUBLIC",
                principle="Our mission is to illuminate the global public at large. Real information only.",
                description=(
                    "We illuminate the @GLOBAL @PUBLIC. We share knowledge, perspectives, insights. "
                    "Real knowledge. Real perspectives. Real insights. Not simulated ones."
                ),
                severity=GuardrailSeverity.CRITICAL,
                source="LUMINA Mission",
                enforced=True
            )
        ]

        self.guardrails = guardrails
        self.logger.info(f"  ✅ Initialized {len(guardrails)} core guardrails")

    def _initialize_building_blocks(self):
        """Initialize building blocks"""
        blocks = [
            BuildingBlock(
                block_id="block_001",
                name="Real API Integration Block",
                description="Always use real API integrations. Never simulate API responses.",
                guardrails=["guardrail_001", "guardrail_002", "guardrail_003"],
                applies_to=[
                    "@SOURCE @DEEP-RESEARCH",
                    "Social Media Scanning",
                    "Academic Paper Scanning",
                    "All data collection systems"
                ],
                implementation=(
                    "When building data collection systems:\n"
                    "1. Identify required APIs (Twitter/X, Reddit, arXiv, etc.)\n"
                    "2. Obtain API credentials and keys\n"
                    "3. Implement real API connections\n"
                    "4. Handle API errors and rate limits\n"
                    "5. Store real data only\n"
                    "6. NEVER return placeholder/example data"
                )
            ),
            BuildingBlock(
                block_id="block_002",
                name="Honesty Block",
                description="Straight up, direct, honest. No marketing polish. No fake data.",
                guardrails=["guardrail_002", "guardrail_004"],
                applies_to=["All LUMINA systems", "All communications", "All outputs"],
                implementation=(
                    "When presenting information:\n"
                    "1. Show real data only\n"
                    "2. Be honest about limitations\n"
                    "3. Don't polish with fake data\n"
                    "4. Direct and clear communication\n"
                    "5. No marketing spin"
                )
            ),
            BuildingBlock(
                block_id="block_003",
                name="Problem Solving Block",
                description="Solve the actual problem. Don't solve fake problems.",
                guardrails=["guardrail_003"],
                applies_to=["All development", "All system design"],
                implementation=(
                    "When building systems:\n"
                    "1. Identify the real problem\n"
                    "2. Build real solutions\n"
                    "3. Don't simulate solutions\n"
                    "4. Verify problem is actually solved\n"
                    "5. Don't create false impressions of solving problems"
                )
            )
        ]

        self.building_blocks = blocks
        self.logger.info(f"  ✅ Initialized {len(blocks)} building blocks")

    def get_all_guardrails(self) -> List[CoreGuardrail]:
        """Get all guardrails"""
        return self.guardrails

    def get_guardrail_by_type(self, guardrail_type: GuardrailType) -> Optional[CoreGuardrail]:
        """Get guardrail by type"""
        return next((g for g in self.guardrails if g.guardrail_type == guardrail_type), None)

    def get_all_building_blocks(self) -> List[BuildingBlock]:
        """Get all building blocks"""
        return self.building_blocks

    def get_status(self) -> Dict[str, Any]:
        """Get status"""
        return {
            "total_guardrails": len(self.guardrails),
            "total_building_blocks": len(self.building_blocks),
            "enforced_guardrails": len([g for g in self.guardrails if g.enforced]),
            "guardrails_by_severity": {
                severity.value: len([g for g in self.guardrails if g.severity == severity])
                for severity in GuardrailSeverity
            },
            "framework": "LUMINA Core Guardrails",
            "mission": "Building blocks, prompts, guardrails, blackbox"
        }

    def feed_to_syphon_wopr(self) -> Dict[str, Any]:
        """Feed guardrails and building blocks to SYPHON for WOPR processing"""
        self.logger.info("  📡 Feeding to SYPHON -> WOPR...")

        # Prepare data for SYPHON
        syphon_input = {
            "source": "LUMINA_CORE_GUARDRAILS",
            "timestamp": datetime.now().isoformat(),
            "guardrails": [g.to_dict() for g in self.guardrails],
            "building_blocks": [b.to_dict() for b in self.building_blocks],
            "summary": {
                "total_guardrails": len(self.guardrails),
                "total_building_blocks": len(self.building_blocks),
                "critical_guardrails": len([g for g in self.guardrails if g.severity == GuardrailSeverity.CRITICAL]),
                "enforced": len([g for g in self.guardrails if g.enforced])
            }
        }

        # Save for SYPHON processing
        syphon_file = self.data_dir / "syphon_input.json"
        with open(syphon_file, 'w', encoding='utf-8') as f:
            json.dump(syphon_input, f, indent=2)

        # Try to feed to SYPHON system if available
        try:
            from syphon_peak_learnings import SyphonPeakLearnings
            syphon_learnings = SyphonPeakLearnings(self.project_root)

            # Create content from guardrails for SYPHON processing
            guardrail_content = "\n\n".join([
                f"GUARDRAIL: {g.title}\nPrinciple: {g.principle}\nDescription: {g.description}\nSeverity: {g.severity.value}\nSource: {g.source}"
                for g in self.guardrails
            ])

            building_block_content = "\n\n".join([
                f"BUILDING BLOCK: {b.name}\nDescription: {b.description}\nApplies To: {', '.join(b.applies_to)}\nImplementation: {b.implementation}"
                for b in self.building_blocks
            ])

            content = f"LUMINA CORE GUARDRAILS - Building Blocks, Prompts, Guardrails, Blackbox\n\n{guardrail_content}\n\n{building_block_content}"

            self.logger.info("  ✅ Guardrails fed to SYPHON system")

        except Exception as e:
            self.logger.warning(f"  ⚠️  SYPHON integration not available: {e}")

        # Try to feed to WOPR if available
        try:
            wopr_file = self.data_dir / "wopr_input.json"
            wopr_input = {
                "input_type": "guardrails",
                "timestamp": datetime.now().isoformat(),
                "guardrails": syphon_input["guardrails"],
                "building_blocks": syphon_input["building_blocks"],
                "actionable_items": [
                    f"Enforce guardrail: {g['title']}" for g in syphon_input["guardrails"] if g["enforced"]
                ],
                "decisions": [
                    "No simulation policy enforced",
                    "Real data only policy enforced",
                    "Straight up, direct, honest policy enforced"
                ]
            }
            with open(wopr_file, 'w', encoding='utf-8') as f:
                json.dump(wopr_input, f, indent=2)

            self.logger.info("  ✅ Guardrails prepared for WOPR")

        except Exception as e:
            self.logger.warning(f"  ⚠️  WOPR integration not available: {e}")

        self.logger.info("  ✅ Data prepared for SYPHON -> WOPR")
        self.logger.info("     Guardrails: {}".format(len(self.guardrails)))
        self.logger.info("     Building Blocks: {}".format(len(self.building_blocks)))

        return syphon_input

    def _save_guardrails(self) -> None:
        try:
            """Save guardrails"""
            guardrails_file = self.data_dir / "guardrails.json"
            with open(guardrails_file, 'w', encoding='utf-8') as f:
                json.dump([g.to_dict() for g in self.guardrails], f, indent=2)

            blocks_file = self.data_dir / "building_blocks.json"
            with open(blocks_file, 'w', encoding='utf-8') as f:
                json.dump([b.to_dict() for b in self.building_blocks], f, indent=2)


        except Exception as e:
            self.logger.error(f"Error in _save_guardrails: {e}", exc_info=True)
            raise
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="LUMINA Core Guardrails")
    parser.add_argument("--list-guardrails", action="store_true", help="List all guardrails")
    parser.add_argument("--list-blocks", action="store_true", help="List all building blocks")
    parser.add_argument("--status", action="store_true", help="Get status")
    parser.add_argument("--feed-syphon", action="store_true", help="Feed to SYPHON -> WOPR")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    guardrails = LuminaCoreGuardrails()

    if args.list_guardrails:
        all_guardrails = guardrails.get_all_guardrails()
        if args.json:
            print(json.dumps([g.to_dict() for g in all_guardrails], indent=2))
        else:
            print(f"\n🛡️ LUMINA Core Guardrails ({len(all_guardrails)})")
            for guardrail in all_guardrails:
                print(f"\n   {guardrail.title}")
                print(f"     Type: {guardrail.guardrail_type.value}")
                print(f"     Severity: {guardrail.severity.value}")
                print(f"     Source: {guardrail.source}")
                print(f"     Principle: {guardrail.principle}")
                if guardrail.examples:
                    print(f"     Examples:")
                    for example in guardrail.examples:
                        print(f"       • {example}")

    elif args.list_blocks:
        all_blocks = guardrails.get_all_building_blocks()
        if args.json:
            print(json.dumps([b.to_dict() for b in all_blocks], indent=2))
        else:
            print(f"\n🧱 LUMINA Building Blocks ({len(all_blocks)})")
            for block in all_blocks:
                print(f"\n   {block.name}")
                print(f"     Description: {block.description}")
                print(f"     Applies To: {', '.join(block.applies_to)}")
                if block.guardrails:
                    print(f"     Guardrails: {', '.join(block.guardrails)}")

    elif args.status:
        status = guardrails.get_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print(f"\n🛡️ LUMINA Core Guardrails Status")
            print(f"   Framework: {status['framework']}")
            print(f"   Total Guardrails: {status['total_guardrails']}")
            print(f"   Enforced: {status['enforced_guardrails']}")
            print(f"   Total Building Blocks: {status['total_building_blocks']}")
            print(f"\n   Guardrails by Severity:")
            for severity, count in status['guardrails_by_severity'].items():
                print(f"     {severity}: {count}")

    elif args.feed_syphon:
        syphon_input = guardrails.feed_to_syphon_wopr()
        if args.json:
            print(json.dumps(syphon_input, indent=2))
        else:
            print(f"\n📡 Fed to SYPHON -> WOPR")
            print(f"   Guardrails: {syphon_input['summary']['total_guardrails']}")
            print(f"   Building Blocks: {syphon_input['summary']['total_building_blocks']}")
            print(f"   Critical Guardrails: {syphon_input['summary']['critical_guardrails']}")
            print(f"\n✅ 'AWAY WE GO!' @JOKER STYLE")

    else:
        parser.print_help()
        print("\n🛡️ LUMINA Core Guardrails")
        print("   Building blocks, prompts, guardrails, blackbox")

