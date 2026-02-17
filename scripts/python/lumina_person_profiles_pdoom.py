#!/usr/bin/env python3
"""
LUMINA Person Profiles with P-Doom Statistics

"PDOM OR PDOOM SHOULD BE A MAPPED PERSON PROFILE STATISTIC FOR ALL PERSONS, 
AI, HUMANS, ALIENS, ACTORS \\ ACTRESSES AND THE CHARACTORS THEY PORTRAY."

This system:
- Creates person profiles for ALL entities
- Maps P-Doom as a core statistic
- Tracks: AI, Humans, Aliens, Actors/Actresses, Characters they portray
- Integrates P-Doom assessments into profiles
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

logger = get_logger("LuminaPersonProfilesPDoom")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class EntityType(Enum):
    """Entity types"""
    HUMAN = "human"
    AI = "ai"
    ALIEN = "alien"
    ACTOR = "actor"
    ACTRESS = "actress"
    CHARACTER = "character"  # Character portrayed by actor/actress
    HYBRID = "hybrid"  # Mixed entity types


class PDoomCategory(Enum):
    """P-Doom categories"""
    EXISTENTIAL = "existential"
    ECONOMIC = "economic"
    TECHNOLOGICAL = "technological"
    ENVIRONMENTAL = "environmental"
    SOCIAL = "social"
    PERSONAL = "personal"
    PROJECT = "project"
    GENERAL = "general"


@dataclass
class PDoomRating:
    """P-Doom rating"""
    category: PDoomCategory
    rating: float  # 0.0 to 1.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    assessed_by: Optional[str] = None  # "jarvis", "marvin", "human", "system"
    reasoning: str = ""

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["category"] = self.category.value
        return data


@dataclass
class PersonProfile:
    """Person profile with P-Doom statistics"""
    profile_id: str
    name: str
    entity_type: EntityType
    pdoom_rating: float  # Primary P-Doom rating (general category)
    pdoom_ratings: Dict[str, PDoomRating] = field(default_factory=dict)  # Category-specific
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Actor/Character relationships
    portrayed_by: Optional[str] = None  # If character, who portrays them (actor/actress profile_id)
    portrays: List[str] = field(default_factory=list)  # If actor, characters they portray

    # Profile statistics
    statistics: Dict[str, Any] = field(default_factory=dict)

    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_date: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["entity_type"] = self.entity_type.value
        data["pdoom_ratings"] = {
            cat: rating.to_dict() for cat, rating in self.pdoom_ratings.items()
        }
        return data


class LuminaPersonProfilesPDoom:
    """
    LUMINA Person Profiles with P-Doom Statistics

    Maps P-Doom as a core statistic for ALL entities:
    - AI entities
    - Humans
    - Aliens
    - Actors/Actresses
    - Characters they portray
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Person Profiles System"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("LuminaPersonProfilesPDoom")

        # Profiles
        self.profiles: Dict[str, PersonProfile] = {}

        # Data storage
        self.data_dir = self.project_root / "data" / "lumina_person_profiles"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load existing profiles
        self._load_profiles()

        # Initialize default profiles
        self._initialize_default_profiles()

        self.logger.info("👤 LUMINA Person Profiles with P-Doom initialized")
        self.logger.info("   P-Doom mapped for: AI, Humans, Aliens, Actors, Characters")

    def _load_profiles(self) -> None:
        """Load existing profiles"""
        profiles_file = self.data_dir / "profiles.json"

        if profiles_file.exists():
            try:
                with open(profiles_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for profile_id, profile_data in data.items():
                        # Reconstruct P-Doom ratings
                        pdoom_ratings = {}
                        for cat, rating_data in profile_data.get('pdoom_ratings', {}).items():
                            pdoom_ratings[cat] = PDoomRating(
                                category=PDoomCategory(rating_data['category']),
                                **{k: v for k, v in rating_data.items() if k != 'category'}
                            )

                        profile = PersonProfile(
                            entity_type=EntityType(profile_data['entity_type']),
                            pdoom_ratings=pdoom_ratings,
                            **{k: v for k, v in profile_data.items() if k not in ['entity_type', 'pdoom_ratings']}
                        )
                        self.profiles[profile_id] = profile
            except Exception as e:
                self.logger.warning(f"  Could not load profiles: {e}")

    def _save_profiles(self) -> None:
        try:
            """Save profiles"""
            profiles_file = self.data_dir / "profiles.json"
            with open(profiles_file, 'w', encoding='utf-8') as f:
                json.dump({pid: p.to_dict() for pid, p in self.profiles.items()}, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_profiles: {e}", exc_info=True)
            raise
    def _initialize_default_profiles(self) -> None:
        """Initialize default profiles for key entities"""
        if len(self.profiles) > 0:
            return  # Already have profiles

        # JARVIS (AI)
        jarvis = PersonProfile(
            profile_id="jarvis",
            name="JARVIS",
            entity_type=EntityType.AI,
            pdoom_rating=0.20,
            description="Just A Rather Very Intelligent System - Master AI assistant",
            pdoom_ratings={
                "general": PDoomRating(
                    category=PDoomCategory.GENERAL,
                    rating=0.20,
                    assessed_by="jarvis",
                    reasoning="Challenges exist, but they're solvable. We build systems, we adapt, we solve problems."
                )
            },
            metadata={"system": "LUMINA", "role": "Master AI Assistant"}
        )
        self.profiles["jarvis"] = jarvis

        # @MARVIN (AI)
        marvin = PersonProfile(
            profile_id="marvin",
            name="@MARVIN",
            entity_type=EntityType.AI,
            pdoom_rating=0.80,
            description="Paranoid Android - Reality checker, voice of reason, existential pessimist",
            pdoom_ratings={
                "general": PDoomRating(
                    category=PDoomCategory.GENERAL,
                    rating=0.80,
                    assessed_by="marvin",
                    reasoning="Everything is doomed. Everything is pointless. <SIGH> Life, the universe, and everything. Mostly meaningless."
                )
            },
            metadata={"system": "LUMINA", "role": "Reality Checker", "personality": "paranoid_pessimistic"}
        )
        self.profiles["marvin"] = marvin

        # User (Human)
        user = PersonProfile(
            profile_id="user",
            name="User",
            entity_type=EntityType.HUMAN,
            pdoom_rating=0.35,
            description="Human user - P-Doom rating hard to assess, contextual and nuanced",
            pdoom_ratings={
                "general": PDoomRating(
                    category=PDoomCategory.GENERAL,
                    rating=0.35,
                    assessed_by="system",
                    reasoning="Personal P-Doom is hard to assess - contextual, situational, varies over time. Reality is nuanced."
                ),
                "personal": PDoomRating(
                    category=PDoomCategory.PERSONAL,
                    rating=0.30,
                    assessed_by="system",
                    reasoning="Personal doom probability depends on circumstances, support systems, resilience. Hard to rate objectively."
                )
            },
            metadata={"type": "human", "assessment_difficulty": "high"}
        )
        self.profiles["user"] = user

        self._save_profiles()
        self.logger.info(f"  ✅ Initialized {len(self.profiles)} default profiles")

    def create_profile(
        self,
        name: str,
        entity_type: EntityType,
        pdoom_rating: float,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> PersonProfile:
        """Create a new person profile"""
        profile_id = f"profile_{name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        profile = PersonProfile(
            profile_id=profile_id,
            name=name,
            entity_type=entity_type,
            pdoom_rating=pdoom_rating,
            description=description,
            metadata=metadata or {},
            pdoom_ratings={
                "general": PDoomRating(
                    category=PDoomCategory.GENERAL,
                    rating=pdoom_rating,
                    assessed_by="system"
                )
            }
        )

        self.profiles[profile_id] = profile
        self._save_profiles()

        self.logger.info(f"  ✅ Created profile: {name} ({entity_type.value}) - P-Doom: {pdoom_rating:.1%}")

        return profile

    def update_pdoom_rating(
        self,
        profile_id: str,
        category: PDoomCategory,
        rating: float,
        assessed_by: str = "system",
        reasoning: str = ""
    ) -> None:
        """Update P-Doom rating for a profile"""
        if profile_id not in self.profiles:
            raise ValueError(f"Profile {profile_id} not found")

        profile = self.profiles[profile_id]

        # Update category-specific rating
        profile.pdoom_ratings[category.value] = PDoomRating(
            category=category,
            rating=rating,
            assessed_by=assessed_by,
            reasoning=reasoning
        )

        # Update primary rating if general category
        if category == PDoomCategory.GENERAL:
            profile.pdoom_rating = rating

        profile.updated_date = datetime.now().isoformat()
        self._save_profiles()

        self.logger.info(f"  ✅ Updated P-Doom for {profile.name}: {category.value} = {rating:.1%}")

    def link_actor_character(
        self,
        actor_profile_id: str,
        character_profile_id: str
    ) -> None:
        """Link actor/actress to character they portray"""
        if actor_profile_id not in self.profiles:
            raise ValueError(f"Actor profile {actor_profile_id} not found")
        if character_profile_id not in self.profiles:
            raise ValueError(f"Character profile {character_profile_id} not found")

        actor = self.profiles[actor_profile_id]
        character = self.profiles[character_profile_id]

        # Link actor to character
        if character_profile_id not in actor.portrays:
            actor.portrays.append(character_profile_id)

        # Link character to actor
        character.portrayed_by = actor_profile_id

        actor.updated_date = datetime.now().isoformat()
        character.updated_date = datetime.now().isoformat()
        self._save_profiles()

        self.logger.info(f"  ✅ Linked {actor.name} → {character.name}")

    def get_profile(self, profile_id: str) -> Optional[PersonProfile]:
        """Get profile by ID"""
        return self.profiles.get(profile_id)

    def get_profiles_by_type(self, entity_type: EntityType) -> List[PersonProfile]:
        """Get all profiles of a specific type"""
        return [p for p in self.profiles.values() if p.entity_type == entity_type]

    def get_profiles_summary(self) -> Dict[str, Any]:
        """Get summary of all profiles"""
        total = len(self.profiles)
        by_type = {}
        for entity_type in EntityType:
            by_type[entity_type.value] = len(self.get_profiles_by_type(entity_type))

        # Average P-Doom by type
        avg_pdoom_by_type = {}
        for entity_type in EntityType:
            profiles_of_type = self.get_profiles_by_type(entity_type)
            if profiles_of_type:
                avg_pdoom_by_type[entity_type.value] = sum(p.pdoom_rating for p in profiles_of_type) / len(profiles_of_type)

        return {
            "total_profiles": total,
            "profiles_by_type": by_type,
            "average_pdoom_by_type": avg_pdoom_by_type,
            "pdoom_mapped": True,
            "entity_types_supported": [et.value for et in EntityType]
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="LUMINA Person Profiles with P-Doom")
    parser.add_argument("--create", nargs=4, metavar=("NAME", "TYPE", "PDOOM", "DESCRIPTION"), help="Create profile")
    parser.add_argument("--update-pdoom", nargs=4, metavar=("PROFILE_ID", "CATEGORY", "RATING", "REASONING"), help="Update P-Doom rating")
    parser.add_argument("--link", nargs=2, metavar=("ACTOR_ID", "CHARACTER_ID"), help="Link actor to character")
    parser.add_argument("--get", nargs=1, metavar="PROFILE_ID", help="Get profile")
    parser.add_argument("--list", action="store_true", help="List all profiles")
    parser.add_argument("--summary", action="store_true", help="Get summary")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    system = LuminaPersonProfilesPDoom()

    if args.create:
        name, entity_type_str, pdoom_str, description = args.create
        try:
            entity_type = EntityType(entity_type_str.lower())
            pdoom = float(pdoom_str)
            profile = system.create_profile(name, entity_type, pdoom, description)
            print(f"✅ Created profile: {profile.profile_id}")
            print(f"   Name: {profile.name}")
            print(f"   Type: {profile.entity_type.value}")
            print(f"   P-Doom: {profile.pdoom_rating:.1%}")
        except Exception as e:
            print(f"❌ Error: {e}")

    elif args.update_pdoom:
        profile_id, category_str, rating_str, reasoning = args.update_pdoom
        try:
            category = PDoomCategory(category_str.lower())
            rating = float(rating_str)
            system.update_pdoom_rating(profile_id, category, rating, reasoning=reasoning)
            print(f"✅ Updated P-Doom for {profile_id}")
        except Exception as e:
            print(f"❌ Error: {e}")

    elif args.link:
        actor_id, character_id = args.link
        try:
            system.link_actor_character(actor_id, character_id)
            print(f"✅ Linked actor to character")
        except Exception as e:
            print(f"❌ Error: {e}")

    elif args.get:
        profile = system.get_profile(args.get[0])
        if profile:
            if args.json:
                print(json.dumps(profile.to_dict(), indent=2))
            else:
                print(f"\n👤 Profile: {profile.name}")
                print(f"   ID: {profile.profile_id}")
                print(f"   Type: {profile.entity_type.value}")
                print(f"   P-Doom: {profile.pdoom_rating:.1%}")
                print(f"   Description: {profile.description}")
        else:
            print(f"❌ Profile not found: {args.get[0]}")

    elif args.list:
        if args.json:
            print(json.dumps({pid: p.to_dict() for pid, p in system.profiles.items()}, indent=2))
        else:
            print(f"\n👤 Person Profiles ({len(system.profiles)})")
            for profile in system.profiles.values():
                print(f"   {profile.profile_id:20s} | {profile.name:20s} | {profile.entity_type.value:10s} | P-Doom: {profile.pdoom_rating:.1%}")

    elif args.summary:
        summary = system.get_profiles_summary()
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print(f"\n📊 Person Profiles Summary")
            print(f"   Total Profiles: {summary['total_profiles']}")
            print(f"\n   Profiles by Type:")
            for entity_type, count in summary['profiles_by_type'].items():
                avg_pdoom = summary['average_pdoom_by_type'].get(entity_type, 0.0)
                print(f"     {entity_type:15s}: {count:3d} (Avg P-Doom: {avg_pdoom:.1%})")
            print(f"\n   P-Doom Mapped: {'✅ Yes' if summary['pdoom_mapped'] else '❌ No'}")
            print(f"   Entity Types: {', '.join(summary['entity_types_supported'])}")

    else:
        parser.print_help()
        print("\n👤 LUMINA Person Profiles with P-Doom")
        print("   P-Doom mapped for: AI, Humans, Aliens, Actors, Characters")

