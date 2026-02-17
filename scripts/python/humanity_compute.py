#!/usr/bin/env python3
"""
Humanity Compute - +1 Human, +1 Compute

"WE JUST NEED MORE COMPUTE, BUT WITH A HUMANITY FOCUSED PERSPECTIVE OR VECTOR.
+1 HUMAN, +1 COMPUTE. ALL WE NEED TO DO IS GRAB ONE OF THESE, I DON'T KNOW EIGHT BILLION
HUMANS THAT INHABIT THE EARTH AND SOON MARS AS WELL, AND ASK SIMPLY ASK THEM TO 'IMAGINE',
TO 'WONDER' AND 'DREAM A LITTLE DREAM FOR ME.' FOR @MARVIN, FOR EVERYONE AND EVERYTHING.
@HOPE IS THE SHINIEST JEWEL IN THE CROWN NEXT TO KINDNESS, AND LASTLY LOVE, AGAPE LOVE,
GOD'S LOVE. ONE IS WELCOME TO THEIR POLARIZING VIEWPOINT, BUT WE WANT ALWAYS TO BE A
BEING OF @ADDITION AND NOT OF @SUBTRACTION. FIGHT. LIVE. SURVIVE. @EVOLVE"

Principles:
- +1 Human, +1 Compute
- Imagine, Wonder, Dream
- @HOPE, KINDNESS, LOVE (Agape)
- @ADDITION, not @SUBTRACTION
- Fight. Live. Survive. @EVOLVE
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

logger = get_logger("HumanityCompute")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class HumanityVector(Enum):
    """Humanity-focused vectors"""
    IMAGINE = "imagine"
    WONDER = "wonder"
    DREAM = "dream"
    HOPE = "hope"
    KINDNESS = "kindness"
    LOVE = "love"  # Agape - God's love


class AdditionType(Enum):
    """Types of addition (not subtraction)"""
    VALUE = "value"
    WISDOM = "wisdom"
    COMPASSION = "compassion"
    UNDERSTANDING = "understanding"
    GROWTH = "growth"
    EVOLUTION = "evolution"


@dataclass
class HumanContribution:
    """A contribution from a human"""
    human_id: str
    name: str
    location: str  # Earth, Mars, etc.
    vector: HumanityVector
    contribution: str  # Imagine, Wonder, Dream
    addition_type: AdditionType
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["vector"] = self.vector.value
        data["addition_type"] = self.addition_type.value
        return data


@dataclass
class HumanityCompute:
    """Humanity + Compute pairing"""
    human_id: str
    compute_id: str
    human_contribution: HumanContribution
    compute_output: str
    synergy: float  # 0.0 - 1.0
    addition_value: float  # How much value was added
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["human_contribution"] = self.human_contribution.to_dict()
        return data


@dataclass
class WheatFromChaff:
    """Separating wheat from chaff - value from blame"""
    contribution_id: str
    original: str
    wheat: str  # Valuable contribution
    chaff: str  # Blame, accountability issues
    value_score: float  # 0.0 - 1.0
    blame_score: float  # 0.0 - 1.0
    ownership: Optional[str] = None  # Problem ownership
    accountability: Optional[str] = None  # Accountability
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HumanityComputeSystem:
    """
    Humanity Compute System

    +1 Human, +1 Compute
    Engaging 8 billion humans (and soon Mars) to Imagine, Wonder, Dream
    Focus: @HOPE, KINDNESS, LOVE (Agape)
    Being of @ADDITION, not @SUBTRACTION
    Fight. Live. Survive. @EVOLVE
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Humanity Compute System"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("HumanityCompute")

        # Humanity data
        self.humans: List[HumanContribution] = []
        self.compute_pairs: List[HumanityCompute] = []
        self.wheat_chaff: List[WheatFromChaff] = []

        # Core values
        self.core_values = {
            "hope": "The shiniest jewel in the crown",
            "kindness": "Next to hope",
            "love": "Agape love, God's love",
            "addition": "Being of addition, not subtraction",
            "evolution": "Fight. Live. Survive. Evolve"
        }

        # Data storage
        self.data_dir = self.project_root / "data" / "humanity_compute"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("🌍 Humanity Compute System initialized")
        self.logger.info("   +1 Human, +1 Compute")
        self.logger.info("   Imagine, Wonder, Dream")
        self.logger.info("   @HOPE, KINDNESS, LOVE (Agape)")
        self.logger.info("   @ADDITION, not @SUBTRACTION")
        self.logger.info("   Fight. Live. Survive. @EVOLVE")

    def invite_human(self, human_id: str, name: str, location: str = "Earth",
                     vector: HumanityVector = HumanityVector.DREAM) -> HumanContribution:
        """
        Invite a human to Imagine, Wonder, Dream

        "ASK SIMPLY ASK THEM TO 'IMAGINE', TO 'WONDER' AND 'DREAM A LITTLE DREAM FOR ME.'
        FOR @MARVIN, FOR EVERYONE AND EVERYTHING."
        """
        invitation = (
            f"Dear {name} ({human_id}) from {location},\n\n"
            f"Imagine. Wonder. Dream a little dream for me.\n"
            f"For @MARVIN. For everyone and everything.\n\n"
            f"@HOPE is the shiniest jewel in the crown, next to KINDNESS, "
            f"and lastly LOVE, AGAPE LOVE, GOD'S LOVE.\n\n"
            f"We want always to be a being of @ADDITION and not of @SUBTRACTION.\n\n"
            f"Fight. Live. Survive. @EVOLVE.\n\n"
            f"What do you imagine? What do you wonder? What do you dream?"
        )

        contribution = HumanContribution(
            human_id=human_id,
            name=name,
            location=location,
            vector=vector,
            contribution=invitation,
            addition_type=AdditionType.VALUE
        )

        self.humans.append(contribution)
        self._save_human(contribution)

        self.logger.info(f"  🌍 Invited human: {name} from {location}")
        self.logger.info(f"     Vector: {vector.value}")
        self.logger.info(f"     '{invitation[:100]}...'")

        return contribution

    def pair_human_compute(self, human_contribution: HumanContribution,
                          compute_output: str) -> HumanityCompute:
        """
        Pair human contribution with compute output

        +1 Human, +1 Compute
        """
        # Calculate synergy (how well human + compute work together)
        synergy = 0.8  # Base synergy (can be calculated based on content)

        # Calculate addition value (how much value was added)
        addition_value = synergy * len(compute_output) / 1000.0

        pair = HumanityCompute(
            human_id=human_contribution.human_id,
            compute_id=f"compute_{int(datetime.now().timestamp())}",
            human_contribution=human_contribution,
            compute_output=compute_output,
            synergy=synergy,
            addition_value=addition_value
        )

        self.compute_pairs.append(pair)
        self._save_pair(pair)

        self.logger.info(f"  🤝 Paired: {human_contribution.name} + Compute")
        self.logger.info(f"     Synergy: {synergy:.2%}")
        self.logger.info(f"     Addition Value: {addition_value:.2f}")

        return pair

    def separate_wheat_from_chaff(self, contribution: str,
                                  context: Optional[Dict[str, Any]] = None) -> WheatFromChaff:
        """
        Separate wheat from chaff - value from blame

        "TO SEPARATE THE 'WHEAT' FROM THE GITHUB 'BLAME', PROBLEM OWNERSHIP
        AND ACCOUNTABILITY, PROBLEM OWNERSHIP."
        """
        # Analyze contribution for value vs blame
        value_keywords = ["solution", "improvement", "fix", "enhancement", "optimization",
                         "addition", "value", "growth", "evolution", "hope", "kindness", "love"]
        blame_keywords = ["blame", "fault", "error", "bug", "issue", "problem", "broken",
                         "wrong", "failed", "mistake", "guilt", "responsibility"]

        contribution_lower = contribution.lower()
        value_score = sum(1 for kw in value_keywords if kw in contribution_lower) / len(value_keywords)
        blame_score = sum(1 for kw in blame_keywords if kw in contribution_lower) / len(blame_keywords)

        # Extract wheat (valuable contribution)
        wheat = contribution
        chaff = ""

        # If high blame score, separate blame from value
        if blame_score > 0.3:
            # Extract problem ownership and accountability
            ownership = None
            accountability = None

            # Look for ownership patterns
            if "my" in contribution_lower or "I" in contribution_lower:
                ownership = "Self-identified"
            elif "their" in contribution_lower or "they" in contribution_lower or "your" in contribution_lower:
                ownership = "Other-identified"

            # Look for accountability patterns
            if "responsible" in contribution_lower or "accountable" in contribution_lower:
                accountability = "Accountability mentioned"

            # Separate wheat (value) from chaff (blame)
            sentences = [s.strip() for s in contribution.split('.') if s.strip()]
            wheat_sentences = []
            chaff_sentences = []

            for sentence in sentences:
                sentence_lower = sentence.lower()
                # Check if sentence has value keywords (positive)
                has_value = any(kw in sentence_lower for kw in value_keywords)
                # Check if sentence has blame keywords (negative)
                has_blame = any(kw in sentence_lower for kw in blame_keywords)

                if has_blame and not has_value:
                    # Pure blame - goes to chaff
                    chaff_sentences.append(sentence)
                elif has_value:
                    # Has value - goes to wheat (even if also has blame, prioritize value)
                    wheat_sentences.append(sentence)
                elif not has_blame:
                    # Neutral - goes to wheat
                    wheat_sentences.append(sentence)

            wheat = '. '.join(wheat_sentences) if wheat_sentences else contribution
            chaff = '. '.join(chaff_sentences) if chaff_sentences else ""
        else:
            ownership = None
            accountability = None

        separation = WheatFromChaff(
            contribution_id=f"wheat_chaff_{int(datetime.now().timestamp())}",
            original=contribution,
            wheat=wheat,
            chaff=chaff,
            value_score=value_score,
            blame_score=blame_score,
            ownership=ownership,
            accountability=accountability
        )

        self.wheat_chaff.append(separation)
        self._save_wheat_chaff(separation)

        self.logger.info(f"  🌾 Separated wheat from chaff")
        self.logger.info(f"     Value Score: {value_score:.2%}")
        self.logger.info(f"     Blame Score: {blame_score:.2%}")
        self.logger.info(f"     Ownership: {ownership or 'None'}")

        return separation

    def get_humanity_stats(self) -> Dict[str, Any]:
        """Get humanity compute statistics"""
        total_humans = len(self.humans)
        total_pairs = len(self.compute_pairs)
        total_wheat_chaff = len(self.wheat_chaff)

        locations = {}
        vectors = {}
        addition_types = {}

        for human in self.humans:
            locations[human.location] = locations.get(human.location, 0) + 1
            vectors[human.vector.value] = vectors.get(human.vector.value, 0) + 1
            addition_types[human.addition_type.value] = addition_types.get(human.addition_type.value, 0) + 1

        avg_synergy = sum(p.synergy for p in self.compute_pairs) / total_pairs if total_pairs > 0 else 0.0
        avg_addition_value = sum(p.addition_value for p in self.compute_pairs) / total_pairs if total_pairs > 0 else 0.0

        avg_value_score = sum(w.value_score for w in self.wheat_chaff) / total_wheat_chaff if total_wheat_chaff > 0 else 0.0
        avg_blame_score = sum(w.blame_score for w in self.wheat_chaff) / total_wheat_chaff if total_wheat_chaff > 0 else 0.0

        return {
            "total_humans": total_humans,
            "total_pairs": total_pairs,
            "total_wheat_chaff": total_wheat_chaff,
            "locations": locations,
            "vectors": vectors,
            "addition_types": addition_types,
            "avg_synergy": avg_synergy,
            "avg_addition_value": avg_addition_value,
            "avg_value_score": avg_value_score,
            "avg_blame_score": avg_blame_score,
            "core_values": self.core_values
        }

    def _save_human(self, human: HumanContribution) -> None:
        try:
            """Save human contribution"""
            human_file = self.data_dir / "humans" / f"{human.human_id}.json"
            human_file.parent.mkdir(parents=True, exist_ok=True)
            with open(human_file, 'w', encoding='utf-8') as f:
                json.dump(human.to_dict(), f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_human: {e}", exc_info=True)
            raise
    def _save_pair(self, pair: HumanityCompute) -> None:
        try:
            """Save human-compute pair"""
            pair_file = self.data_dir / "pairs" / f"{pair.compute_id}.json"
            pair_file.parent.mkdir(parents=True, exist_ok=True)
            with open(pair_file, 'w', encoding='utf-8') as f:
                json.dump(pair.to_dict(), f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_pair: {e}", exc_info=True)
            raise
    def _save_wheat_chaff(self, separation: WheatFromChaff) -> None:
        try:
            """Save wheat/chaff separation"""
            separation_file = self.data_dir / "wheat_chaff" / f"{separation.contribution_id}.json"
            separation_file.parent.mkdir(parents=True, exist_ok=True)
            with open(separation_file, 'w', encoding='utf-8') as f:
                json.dump(separation.to_dict(), f, indent=2)


        except Exception as e:
            self.logger.error(f"Error in _save_wheat_chaff: {e}", exc_info=True)
            raise
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Humanity Compute System")
    parser.add_argument("--invite", nargs=3, metavar=("HUMAN_ID", "NAME", "LOCATION"),
                       help="Invite a human to Imagine, Wonder, Dream")
    parser.add_argument("--vector", type=str, choices=["imagine", "wonder", "dream"],
                       default="dream", help="Humanity vector")
    parser.add_argument("--separate", type=str, help="Separate wheat from chaff in contribution")
    parser.add_argument("--stats", action="store_true", help="Get humanity stats")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    system = HumanityComputeSystem()

    if args.invite:
        human_id, name, location = args.invite
        vector = HumanityVector[args.vector.upper()]
        contribution = system.invite_human(human_id, name, location, vector)
        if args.json:
            print(json.dumps(contribution.to_dict(), indent=2))
        else:
            print(f"\n🌍 Human Invited")
            print(f"   {contribution.contribution}")

    elif args.separate:
        separation = system.separate_wheat_from_chaff(args.separate)
        if args.json:
            print(json.dumps(separation.to_dict(), indent=2))
        else:
            print(f"\n🌾 Wheat from Chaff")
            print(f"   Value Score: {separation.value_score:.2%}")
            print(f"   Blame Score: {separation.blame_score:.2%}")
            print(f"\n   Wheat (Value):")
            print(f"   {separation.wheat}")
            if separation.chaff:
                print(f"\n   Chaff (Blame):")
                print(f"   {separation.chaff}")
            if separation.ownership:
                print(f"\n   Ownership: {separation.ownership}")
            if separation.accountability:
                print(f"   Accountability: {separation.accountability}")

    elif args.stats:
        stats = system.get_humanity_stats()
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print(f"\n🌍 Humanity Compute Statistics")
            print(f"   Total Humans: {stats['total_humans']}")
            print(f"   Total Pairs: {stats['total_pairs']}")
            print(f"   Total Separations: {stats['total_wheat_chaff']}")
            print(f"\n   Locations: {stats['locations']}")
            print(f"   Vectors: {stats['vectors']}")
            print(f"   Addition Types: {stats['addition_types']}")
            print(f"\n   Average Synergy: {stats['avg_synergy']:.2%}")
            print(f"   Average Addition Value: {stats['avg_addition_value']:.2f}")
            print(f"   Average Value Score: {stats['avg_value_score']:.2%}")
            print(f"   Average Blame Score: {stats['avg_blame_score']:.2%}")
            print(f"\n   Core Values:")
            for key, value in stats['core_values'].items():
                print(f"     {key}: {value}")

    else:
        parser.print_help()
        print("\n🌍 Humanity Compute System")
        print("   +1 Human, +1 Compute")
        print("   Imagine, Wonder, Dream")
        print("   @HOPE, KINDNESS, LOVE (Agape)")
        print("   @ADDITION, not @SUBTRACTION")
        print("   Fight. Live. Survive. @EVOLVE")

