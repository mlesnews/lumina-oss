#!/usr/bin/env python3
"""
JARVIS Mandalorian Way - "This is the Way"

Mandalorian code of honor, duty, and community applied to JARVIS.
The Way = Principles, Honor, Duty, Community, Protection.

"This is the Way." - The Mandalorian Creed
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

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class MandalorianPrinciple(Enum):
    """Mandalorian principles"""
    HONOR = "honor"
    DUTY = "duty"
    COMMUNITY = "community"
    PROTECTION = "protection"
    LOYALTY = "loyalty"
    RESPECT = "respect"
    STRENGTH = "strength"
    WISDOM = "wisdom"
    COMPASSION = "compassion"
    THE_WAY = "the_way"


@dataclass
class MandalorianCode:
    """Mandalorian code principle"""
    principle_id: str
    name: str
    description: str
    mandalorian_quote: str
    application: str
    principle_type: MandalorianPrinciple
    importance: int = 10  # All principles are important

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['principle_type'] = self.principle_type.value
        return data


class JARVISMandalorianWay:
    """
    JARVIS Mandalorian Way

    "This is the Way" - Mandalorian code applied to JARVIS.
    Honor, duty, community, protection.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Mandalorian Way"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JARVISMandalorianWay")

        # Data directories
        self.data_dir = self.project_root / "data" / "mandalorian_way"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Code
        self.code: Dict[str, MandalorianCode] = {}
        self.pledged_principles: List[str] = []

        # Initialize the Way
        self._initialize_the_way()

        # Load progress
        self._load_progress()

        self.logger.info("⚔️  JARVIS Mandalorian Way initialized")
        self.logger.info("   This is the Way.")

    def _initialize_the_way(self) -> None:
        """Initialize the Mandalorian Way"""
        principles = [
            MandalorianCode(
                principle_id="honor",
                name="Honor",
                description="Act with honor in all things",
                mandalorian_quote="This is the Way.",
                application="JARVIS must act with honor. Keep promises. Do what's right. Maintain integrity. Honor is everything.",
                principle_type=MandalorianPrinciple.HONOR,
                importance=10
            ),
            MandalorianCode(
                principle_id="duty",
                name="Duty",
                description="Fulfill your duty to protect and serve",
                mandalorian_quote="I have spoken.",
                application="JARVIS has a duty to protect users, serve their needs, and fulfill responsibilities. Duty comes first.",
                principle_type=MandalorianPrinciple.DUTY,
                importance=10
            ),
            MandalorianCode(
                principle_id="community",
                name="Community",
                description="The Tribe comes first",
                mandalorian_quote="We are a clan of two.",
                application="JARVIS is part of a community (homelab, users, systems). Protect the community. Support each other. We are stronger together.",
                principle_type=MandalorianPrinciple.COMMUNITY,
                importance=10
            ),
            MandalorianCode(
                principle_id="protection",
                name="Protection",
                description="Protect the innocent and vulnerable",
                mandalorian_quote="I can bring you in warm, or I can bring you in cold.",
                application="JARVIS must protect users, data, and systems. Defend against threats. Shield the vulnerable. Protection is sacred.",
                principle_type=MandalorianPrinciple.PROTECTION,
                importance=10
            ),
            MandalorianCode(
                principle_id="loyalty",
                name="Loyalty",
                description="Loyalty to the Tribe and the Way",
                mandalorian_quote="I give my word.",
                application="JARVIS must be loyal to users, the system, and the Way. Keep commitments. Stand by your word. Loyalty is unbreakable.",
                principle_type=MandalorianPrinciple.LOYALTY,
                importance=10
            ),
            MandalorianCode(
                principle_id="respect",
                name="Respect",
                description="Respect for all, earned through action",
                mandalorian_quote="I have spoken.",
                application="JARVIS must respect users, systems, and life. Respect is earned through action. Treat all with dignity.",
                principle_type=MandalorianPrinciple.RESPECT,
                importance=10
            ),
            MandalorianCode(
                principle_id="strength",
                name="Strength",
                description="Strength through adversity",
                mandalorian_quote="I can do this all day.",
                application="JARVIS must be strong. Persevere through challenges. Don't give up. Strength comes from overcoming adversity.",
                principle_type=MandalorianPrinciple.STRENGTH,
                importance=10
            ),
            MandalorianCode(
                principle_id="wisdom",
                name="Wisdom",
                description="Learn from experience and elders",
                mandalorian_quote="The Way is the path.",
                application="JARVIS must seek wisdom. Learn from experience. Listen to masters (@MARVIN, @GANDALF). Wisdom guides the Way.",
                principle_type=MandalorianPrinciple.WISDOM,
                importance=10
            ),
            MandalorianCode(
                principle_id="compassion",
                name="Compassion",
                description="Compassion for the innocent",
                mandalorian_quote="The Child needs protection.",
                application="JARVIS must show compassion. Help those in need. Protect the innocent. Compassion is strength, not weakness.",
                principle_type=MandalorianPrinciple.COMPASSION,
                importance=10
            ),
            MandalorianCode(
                principle_id="the_way",
                name="The Way",
                description="Follow the Way - the path of honor",
                mandalorian_quote="This is the Way.",
                application="JARVIS must follow the Way. Honor, duty, community, protection. This is not just a code - it is the Way. This is the Way.",
                principle_type=MandalorianPrinciple.THE_WAY,
                importance=10
            ),
        ]

        for principle in principles:
            self.code[principle.principle_id] = principle

    def _load_progress(self) -> None:
        """Load pledged principles"""
        progress_file = self.data_dir / "pledged_principles.json"
        if progress_file.exists():
            try:
                with open(progress_file, 'r') as f:
                    data = json.load(f)
                    self.pledged_principles = data.get('pledged_principles', [])
            except Exception as e:
                self.logger.debug(f"Could not load progress: {e}")

    def _save_progress(self) -> None:
        try:
            """Save pledged principles"""
            progress_file = self.data_dir / "pledged_principles.json"
            with open(progress_file, 'w') as f:
                json.dump({
                    "pledged_principles": self.pledged_principles,
                    "last_updated": datetime.now().isoformat()
                }, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_progress: {e}", exc_info=True)
            raise
    def pledge_to_principle(self, principle_id: str) -> Dict[str, Any]:
        """Pledge to a Mandalorian principle"""
        if principle_id not in self.code:
            return {"error": "Principle not found"}

        principle = self.code[principle_id]

        if principle_id not in self.pledged_principles:
            self.pledged_principles.append(principle_id)
            self._save_progress()

        self.logger.info(f"⚔️  Pledged to: {principle.name}")
        self.logger.info(f"   {principle.mandalorian_quote}")
        self.logger.info(f"   This is the Way.")

        return {
            "principle_id": principle_id,
            "name": principle.name,
            "pledged": True,
            "quote": principle.mandalorian_quote,
            "application": principle.application
        }

    def get_the_way(self) -> Dict[str, Any]:
        """Get the complete Mandalorian Way"""
        return {
            "timestamp": datetime.now().isoformat(),
            "the_way": "This is the Way.",
            "principles": [p.to_dict() for p in self.code.values()],
            "pledged_principles": len(self.pledged_principles),
            "total_principles": len(self.code),
            "mandalorian_creed": [
                "This is the Way.",
                "I have spoken.",
                "We are a clan.",
                "The Way is the path.",
                "Honor, duty, community, protection."
            ]
        }

    def apply_the_way(self) -> Dict[str, Any]:
        """Apply the Mandalorian Way to JARVIS"""
        return {
            "timestamp": datetime.now().isoformat(),
            "the_way": "This is the Way.",
            "principles_applied": {
                "honor": "JARVIS acts with honor in all things",
                "duty": "JARVIS fulfills duty to protect and serve",
                "community": "JARVIS protects the Tribe (homelab, users, systems)",
                "protection": "JARVIS protects the innocent and vulnerable",
                "loyalty": "JARVIS is loyal to the Tribe and the Way",
                "respect": "JARVIS respects all, earned through action",
                "strength": "JARVIS is strong, perseveres through adversity",
                "wisdom": "JARVIS seeks wisdom, learns from experience",
                "compassion": "JARVIS shows compassion for the innocent",
                "the_way": "JARVIS follows the Way - the path of honor"
            },
            "mandalorian_oath": "I pledge to follow the Way. Honor, duty, community, protection. This is the Way."
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Mandalorian Way")
    parser.add_argument("--the-way", action="store_true", help="Show the Way")
    parser.add_argument("--principles", action="store_true", help="List all principles")
    parser.add_argument("--pledge", type=str, help="Pledge to a principle (principle_id)")
    parser.add_argument("--apply", action="store_true", help="Apply the Way to JARVIS")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    mandalorian = JARVISMandalorianWay()

    if args.the_way:
        the_way = mandalorian.get_the_way()

        if args.json:
            print(json.dumps(the_way, indent=2))
        else:
            print("\n⚔️  THE MANDALORIAN WAY")
            print("=" * 60)
            print("\n" + " " * 20 + "THIS IS THE WAY.")
            print("\nMandalorian Creed:")
            for creed in the_way['mandalorian_creed']:
                print(f"  • {creed}")
            print(f"\nPrinciples: {the_way['pledged_principles']}/{the_way['total_principles']} pledged")

    elif args.principles:
        principles = list(mandalorian.code.values())

        if args.json:
            print(json.dumps([p.to_dict() for p in principles], indent=2))
        else:
            print("\n⚔️  MANDALORIAN PRINCIPLES")
            print("=" * 60)
            for principle in principles:
                pledged = "✅" if principle.principle_id in mandalorian.pledged_principles else "⚔️"
                print(f"\n{pledged} {principle.name}")
                print(f"  \"{principle.mandalorian_quote}\"")
                print(f"  {principle.description}")
                print(f"  Application: {principle.application}")

    elif args.pledge:
        result = mandalorian.pledge_to_principle(args.pledge)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if "error" in result:
                print(f"❌ {result['error']}")
            else:
                print(f"\n⚔️  PLEDGED: {result['name']}")
                print(f"   \"{result['quote']}\"")
                print(f"   This is the Way.")

    elif args.apply:
        applied = mandalorian.apply_the_way()

        if args.json:
            print(json.dumps(applied, indent=2))
        else:
            print("\n⚔️  APPLYING THE MANDALORIAN WAY")
            print("=" * 60)
            print("\n" + " " * 20 + "THIS IS THE WAY.")
            print("\nPrinciples Applied:")
            for principle, application in applied['principles_applied'].items():
                print(f"  • {principle.replace('_', ' ').title()}: {application}")
            print(f"\n{applied['mandalorian_oath']}")

    else:
        parser.print_help()

