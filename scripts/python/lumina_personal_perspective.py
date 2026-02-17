#!/usr/bin/env python3
"""
Lumina Personal Perspective - Individual Human Opinion

"AND THAT IS MY PERSONAL HUMAN OPINION, MY INDIVIDUAL PERSPECTIVE FOR WHATEVER IT IS WORTH.
HENCE, 'LUMINA'"

LUMINA = Personal Human Opinion + Individual Perspective
- Every opinion matters
- Every perspective has value
- Every individual voice is important
- That is what LUMINA represents
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

logger = get_logger("LuminaPersonalPerspective")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class PerspectiveType(Enum):
    """Types of perspectives"""
    PERSONAL_OPINION = "personal_opinion"
    INDIVIDUAL_PERSPECTIVE = "individual_perspective"
    HUMAN_VOICE = "human_voice"
    UNIQUE_VIEWPOINT = "unique_viewpoint"
    SACRED_VOICE = "sacred_voice"  # Every voice is sacred


class PerspectiveValue(Enum):
    """Value of perspective"""
    INFINITE = "infinite"  # Every perspective has infinite value
    SACRED = "sacred"  # Every voice is sacred
    ESSENTIAL = "essential"  # Every opinion is essential
    PRICELESS = "priceless"  # Every perspective is priceless


@dataclass
class PersonalPerspective:
    """A personal human opinion/perspective"""
    perspective_id: str
    human_id: str
    name: str
    opinion: str
    perspective_type: PerspectiveType
    value: PerspectiveValue = PerspectiveValue.INFINITE
    worth: str = "Whatever it is worth - which is everything"
    is_lumina: bool = True  # This is what LUMINA represents
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["perspective_type"] = self.perspective_type.value
        data["value"] = self.value.value
        return data


@dataclass
class LuminaDefinition:
    """Definition of LUMINA"""
    definition_id: str
    meaning: str = "Personal Human Opinion + Individual Perspective"
    value: str = "Whatever it is worth - which is everything"
    essence: str = "Every opinion matters. Every perspective has value. Every individual voice is important."
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LuminaPersonalPerspective:
    """
    Lumina Personal Perspective

    "AND THAT IS MY PERSONAL HUMAN OPINION, MY INDIVIDUAL PERSPECTIVE FOR WHATEVER IT IS WORTH.
    HENCE, 'LUMINA'"

    LUMINA = Personal Human Opinion + Individual Perspective
    - Every opinion matters
    - Every perspective has value
    - Every individual voice is important
    - That is what LUMINA represents
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Lumina Personal Perspective"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("LuminaPersonalPerspective")

        # Perspectives
        self.perspectives: List[PersonalPerspective] = []

        # Lumina definition
        self.lumina_definition = LuminaDefinition(
            definition_id="lumina_definition_001",
            meaning="Personal Human Opinion + Individual Perspective",
            value="Whatever it is worth - which is everything",
            essence="Every opinion matters. Every perspective has value. Every individual voice is important."
        )

        # Data storage
        self.data_dir = self.project_root / "data" / "lumina_personal_perspective"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("💫 Lumina Personal Perspective initialized")
        self.logger.info("   'AND THAT IS MY PERSONAL HUMAN OPINION, MY INDIVIDUAL PERSPECTIVE FOR WHATEVER IT IS WORTH.'")
        self.logger.info("   'HENCE, LUMINA'")
        self.logger.info("   Every opinion matters. Every perspective has value.")

    def record_perspective(self, human_id: str, name: str, opinion: str,
                          perspective_type: PerspectiveType = PerspectiveType.PERSONAL_OPINION) -> PersonalPerspective:
        """
        Record a personal human opinion/perspective

        "AND THAT IS MY PERSONAL HUMAN OPINION, MY INDIVIDUAL PERSPECTIVE FOR WHATEVER IT IS WORTH.
        HENCE, 'LUMINA'"
        """
        perspective = PersonalPerspective(
            perspective_id=f"perspective_{int(datetime.now().timestamp())}",
            human_id=human_id,
            name=name,
            opinion=opinion,
            perspective_type=perspective_type,
            value=PerspectiveValue.INFINITE,
            worth="Whatever it is worth - which is everything",
            is_lumina=True
        )

        self.perspectives.append(perspective)
        self._save_perspective(perspective)

        self.logger.info(f"  💫 Recorded perspective: {name}")
        self.logger.info(f"     Type: {perspective_type.value}")
        self.logger.info(f"     Value: {perspective.value.value}")
        self.logger.info("     'HENCE, LUMINA'")

        return perspective

    def get_lumina_definition(self) -> LuminaDefinition:
        """Get definition of LUMINA"""
        self._save_lumina_definition()
        return self.lumina_definition

    def get_perspectives_summary(self) -> Dict[str, Any]:
        """Get summary of all perspectives"""
        total_perspectives = len(self.perspectives)
        by_type = {}
        for perspective in self.perspectives:
            by_type[perspective.perspective_type.value] = by_type.get(perspective.perspective_type.value, 0) + 1

        return {
            "lumina_definition": self.lumina_definition.meaning,
            "lumina_value": self.lumina_definition.value,
            "lumina_essence": self.lumina_definition.essence,
            "total_perspectives": total_perspectives,
            "by_type": by_type,
            "message": "Every opinion matters. Every perspective has value. Every individual voice is important. That is LUMINA."
        }

    def _save_perspective(self, perspective: PersonalPerspective) -> None:
        try:
            """Save perspective"""
            perspective_file = self.data_dir / "perspectives" / f"{perspective.perspective_id}.json"
            perspective_file.parent.mkdir(parents=True, exist_ok=True)
            with open(perspective_file, 'w', encoding='utf-8') as f:
                json.dump(perspective.to_dict(), f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_perspective: {e}", exc_info=True)
            raise
    def _save_lumina_definition(self) -> None:
        try:
            """Save Lumina definition"""
            definition_file = self.data_dir / "lumina_definition.json"
            with open(definition_file, 'w', encoding='utf-8') as f:
                json.dump(self.lumina_definition.to_dict(), f, indent=2)


        except Exception as e:
            self.logger.error(f"Error in _save_lumina_definition: {e}", exc_info=True)
            raise
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Lumina Personal Perspective")
    parser.add_argument("--record", nargs=4, metavar=("HUMAN_ID", "NAME", "OPINION", "TYPE"),
                       help="Record a personal perspective")
    parser.add_argument("--definition", action="store_true", help="Get Lumina definition")
    parser.add_argument("--summary", action="store_true", help="Get perspectives summary")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    lumina = LuminaPersonalPerspective()

    if args.record:
        human_id, name, opinion, type_str = args.record
        try:
            perspective_type = PerspectiveType[type_str.upper()]
            perspective = lumina.record_perspective(human_id, name, opinion, perspective_type)
            if args.json:
                print(json.dumps(perspective.to_dict(), indent=2))
            else:
                print(f"\n💫 Perspective Recorded")
                print(f"   {perspective.name}")
                print(f"   Opinion: {perspective.opinion}")
                print(f"   Type: {perspective.perspective_type.value}")
                print(f"   Value: {perspective.value.value}")
                print(f"   Worth: {perspective.worth}")
                print(f"   'HENCE, LUMINA'")
        except (KeyError, ValueError) as e:
            print(f"Error: {e}")
            print(f"Types: {[t.value for t in PerspectiveType]}")

    elif args.definition:
        definition = lumina.get_lumina_definition()
        if args.json:
            print(json.dumps(definition.to_dict(), indent=2))
        else:
            print(f"\n💫 Lumina Definition")
            print(f"   Meaning: {definition.meaning}")
            print(f"   Value: {definition.value}")
            print(f"   Essence: {definition.essence}")
            print(f"\n   'AND THAT IS MY PERSONAL HUMAN OPINION, MY INDIVIDUAL PERSPECTIVE FOR WHATEVER IT IS WORTH.'")
            print(f"   'HENCE, LUMINA'")

    elif args.summary:
        summary = lumina.get_perspectives_summary()
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print(f"\n💫 Lumina Perspectives Summary")
            print(f"   Definition: {summary['lumina_definition']}")
            print(f"   Value: {summary['lumina_value']}")
            print(f"   Essence: {summary['lumina_essence']}")
            print(f"\n   Total Perspectives: {summary['total_perspectives']}")
            print(f"   By Type:")
            for type_name, count in summary['by_type'].items():
                print(f"     {type_name}: {count}")
            print(f"\n   {summary['message']}")

    else:
        parser.print_help()
        print("\n💫 Lumina Personal Perspective")
        print("   'AND THAT IS MY PERSONAL HUMAN OPINION, MY INDIVIDUAL PERSPECTIVE FOR WHATEVER IT IS WORTH.'")
        print("   'HENCE, LUMINA'")

