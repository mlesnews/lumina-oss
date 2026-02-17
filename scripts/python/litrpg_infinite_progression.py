#!/usr/bin/env python3
"""
LITRPG Infinite Progression System

Infinite progression system with evolution that goes ever upward and outward.
Epic and expansive scaling for hero-level leaders.

Tags: @LITRPG #INFINITE-PROGRESSION #EVOLUTION #EPIC #EXPANSIVE
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import math

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LITRPGInfiniteProgression")


class ProgressionDirection(Enum):
    """Progression Direction"""
    UPWARD = "upward"
    OUTWARD = "outward"
    COMBINED = "combined"


class SkillTier(Enum):
    """Skill Tiers"""
    NOVICE = "novice"
    APPRENTICE = "apprentice"
    JOURNEYMAN = "journeyman"
    EXPERT = "expert"
    MASTER = "master"
    GRANDMASTER = "grandmaster"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"
    TRANSCENDENT = "transcendent"
    DIVINE = "divine"
    OMNIPOTENT = "omnipotent"
    INFINITE = "infinite"


class AbilityTier(Enum):
    """Ability Tiers"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"
    TRANSCENDENT = "transcendent"
    DIVINE = "divine"
    OMNIPOTENT = "omnipotent"
    INFINITE = "infinite"


@dataclass
class Stat:
    """Character Stat"""
    name: str
    base_value: float
    current_value: float
    level: int = 1
    evolution_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class Skill:
    """Character Skill"""
    name: str
    level: float
    tier: SkillTier
    experience: float = 0.0
    mastery_bonus: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["tier"] = self.tier.value
        return data


@dataclass
class Ability:
    """Character Ability"""
    name: str
    tier: AbilityTier
    level: int = 1
    power: float = 1.0
    evolution_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["tier"] = self.tier.value
        return data


@dataclass
class ProgressionMilestone:
    """Progression Milestone"""
    milestone_id: str
    name: str
    level: int
    direction: ProgressionDirection
    description: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["direction"] = self.direction.value
        return data


@dataclass
class CharacterProgression:
    """Character Progression State"""
    character_id: str
    character_name: str
    level: int
    experience: float
    stats: Dict[str, Stat]
    skills: Dict[str, Skill]
    abilities: Dict[str, Ability]
    transcendence_level: str = "mortal"
    evolution_count: int = 0
    milestones: List[ProgressionMilestone] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = {
            "character_id": self.character_id,
            "character_name": self.character_name,
            "level": self.level,
            "experience": self.experience,
            "transcendence_level": self.transcendence_level,
            "evolution_count": self.evolution_count,
            "stats": {k: v.to_dict() for k, v in self.stats.items()},
            "skills": {k: v.to_dict() for k, v in self.skills.items()},
            "abilities": {k: v.to_dict() for k, v in self.abilities.items()},
            "milestones": [m.to_dict() for m in self.milestones],
            "timestamp": self.timestamp
        }
        return data


class LITRPGInfiniteProgression:
    """
    LITRPG Infinite Progression System

    Infinite progression with evolution that goes ever upward and outward.
    Epic and expansive scaling.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize LITRPG Infinite Progression System"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("LITRPGInfiniteProgression")

        # Load configuration
        self.config_dir = self.project_root / "config" / "litrpg"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()

        # Progression data
        self.data_dir = self.project_root / "data" / "litrpg" / "progression"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Scaling factors
        self.upward_scaling = 1.15
        self.outward_scaling = 1.10
        self.exp_scaling = 1.2

        self.logger.info("🎮 LITRPG Infinite Progression System initialized")
        self.logger.info("   Direction: Ever Upward and Outward")
        self.logger.info("   Scale: Epic and Expansive")
        self.logger.info("   Evolution: Enabled")

    def _load_config(self) -> Dict[str, Any]:
        try:
            """Load progression configuration"""
            config_file = self.config_dir / "infinite_progression_system.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}

        except Exception as e:
            self.logger.error(f"Error in _load_config: {e}", exc_info=True)
            raise
    def create_character(self, character_id: str, character_name: str,
                        initial_stats: Optional[Dict[str, float]] = None) -> CharacterProgression:
        """Create a new character with progression tracking"""
        self.logger.info(f"🎮 Creating character: {character_name}")

        # Initialize stats
        base_stats = {
            "intelligence": 10.0,
            "wisdom": 10.0,
            "strength": 10.0,
            "dexterity": 10.0,
            "constitution": 10.0,
            "charisma": 10.0,
            "luck": 10.0
        }
        if initial_stats:
            base_stats.update(initial_stats)

        stats = {
            name: Stat(name=name, base_value=value, current_value=value)
            for name, value in base_stats.items()
        }

        # Initialize skills (empty, will be unlocked through progression)
        skills = {}

        # Initialize abilities (empty, will be unlocked through progression)
        abilities = {}

        progression = CharacterProgression(
            character_id=character_id,
            character_name=character_name,
            level=1,
            experience=0.0,
            stats=stats,
            skills=skills,
            abilities=abilities
        )

        self._save_progression(progression)
        self.logger.info(f"✅ Character created: {character_name} (Level {progression.level})")

        return progression

    def load_character(self, character_id: str) -> Optional[CharacterProgression]:
        try:
            """Load character progression"""
            progression_file = self.data_dir / f"{character_id}.json"
            if not progression_file.exists():
                return None

            with open(progression_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Reconstruct stats
            stats = {
                name: Stat(**stat_data)
                for name, stat_data in data.get("stats", {}).items()
            }

            # Reconstruct skills
            skills = {}
            for name, skill_data in data.get("skills", {}).items():
                skills[name] = Skill(
                    name=name,
                    level=skill_data["level"],
                    tier=SkillTier(skill_data["tier"]),
                    experience=skill_data.get("experience", 0.0),
                    mastery_bonus=skill_data.get("mastery_bonus", 0.0)
                )

            # Reconstruct abilities
            abilities = {}
            for name, ability_data in data.get("abilities", {}).items():
                abilities[name] = Ability(
                    name=name,
                    tier=AbilityTier(ability_data["tier"]),
                    level=ability_data.get("level", 1),
                    power=ability_data.get("power", 1.0),
                    evolution_count=ability_data.get("evolution_count", 0)
                )

            # Reconstruct milestones
            milestones = [
                ProgressionMilestone(**milestone_data)
                for milestone_data in data.get("milestones", [])
            ]

            return CharacterProgression(
                character_id=data["character_id"],
                character_name=data["character_name"],
                level=data["level"],
                experience=data["experience"],
                stats=stats,
                skills=skills,
                abilities=abilities,
                transcendence_level=data.get("transcendence_level", "mortal"),
                evolution_count=data.get("evolution_count", 0),
                milestones=milestones,
                timestamp=data.get("timestamp", datetime.now().isoformat())
            )

        except Exception as e:
            self.logger.error(f"Error in load_character: {e}", exc_info=True)
            raise
    def add_experience(self, character_id: str, exp_amount: float,
                      source: str = "action") -> CharacterProgression:
        """Add experience to character"""
        progression = self.load_character(character_id)
        if not progression:
            raise ValueError(f"Character {character_id} not found")

        progression.experience += exp_amount

        # Check for level up
        exp_required = self._calculate_exp_required(progression.level)
        while progression.experience >= exp_required:
            progression.experience -= exp_required
            self._level_up(progression)
            exp_required = self._calculate_exp_required(progression.level)

        self._save_progression(progression)
        self.logger.info(f"📈 {progression.character_name}: +{exp_amount} EXP (Total: {progression.experience:.2f})")

        return progression

    def _calculate_exp_required(self, level: int) -> float:
        """Calculate experience required for next level"""
        base_exp = 100.0
        return base_exp * (level ** self.exp_scaling)

    def _level_up(self, progression: CharacterProgression) -> None:
        """Handle level up"""
        progression.level += 1

        # Update transcendence level
        progression.transcendence_level = self._get_transcendence_level(progression.level)

        # Stat improvements (upward progression)
        stat_points = self._calculate_stat_points(progression.level)
        for stat_name, stat in progression.stats.items():
            improvement = stat_points / len(progression.stats)
            stat.current_value += improvement
            stat.level = progression.level

        # Potential new abilities/skills (outward progression)
        if progression.level % 10 == 0:
            self._unlock_new_capability(progression)

        # Evolution opportunities
        if progression.level % 100 == 0:
            progression.evolution_count += 1
            self._trigger_evolution(progression, ProgressionDirection.COMBINED)

        # Create milestone
        milestone = ProgressionMilestone(
            milestone_id=f"level_{progression.level}",
            name=f"Level {progression.level}",
            level=progression.level,
            direction=ProgressionDirection.UPWARD,
            description=f"Reached level {progression.level} - {progression.transcendence_level} tier"
        )
        progression.milestones.append(milestone)

        self.logger.info(f"⬆️ {progression.character_name} LEVEL UP! Level {progression.level} ({progression.transcendence_level})")

    def _get_transcendence_level(self, level: int) -> str:
        """Get transcendence level based on character level"""
        if level <= 100:
            return "mortal"
        elif level <= 1000:
            return "heroic"
        elif level <= 10000:
            return "legendary"
        elif level <= 100000:
            return "mythic"
        elif level <= 1000000:
            return "transcendent"
        elif level <= 10000000:
            return "divine"
        else:
            return "omnipotent"

    def _calculate_stat_points(self, level: int) -> float:
        """Calculate stat points gained per level"""
        base_points = 5.0
        return base_points * (level ** 0.1)  # Slow scaling

    def _unlock_new_capability(self, progression: CharacterProgression) -> None:
        """Unlock new capability (outward progression)"""
        # This would unlock new skills or abilities
        # Placeholder for now
        pass

    def _trigger_evolution(self, progression: CharacterProgression,
                          direction: ProgressionDirection) -> None:
        """Trigger evolution event"""
        self.logger.info(f"🌟 {progression.character_name} EVOLUTION! Direction: {direction.value}")

        if direction == ProgressionDirection.UPWARD:
            # Improve existing capabilities
            for stat in progression.stats.values():
                stat.current_value *= 1.1
                stat.evolution_count += 1

        elif direction == ProgressionDirection.OUTWARD:
            # Expand capabilities
            # Unlock new skills/abilities
            pass

        elif direction == ProgressionDirection.COMBINED:
            # Both upward and outward
            for stat in progression.stats.values():
                stat.current_value *= 1.15
                stat.evolution_count += 1
            # Also expand capabilities
            pass

    def improve_skill(self, character_id: str, skill_name: str,
                     exp_gain: float) -> CharacterProgression:
        """Improve a skill (upward progression)"""
        progression = self.load_character(character_id)
        if not progression:
            raise ValueError(f"Character {character_id} not found")

        if skill_name not in progression.skills:
            # Create new skill (outward progression)
            progression.skills[skill_name] = Skill(
                name=skill_name,
                level=0.0,
                tier=SkillTier.NOVICE
            )

        skill = progression.skills[skill_name]
        skill.experience += exp_gain

        # Check for skill level up
        skill_level_required = self._calculate_skill_exp_required(skill.level)
        while skill.experience >= skill_level_required:
            skill.experience -= skill_level_required
            skill.level += 1.0
            skill.tier = self._get_skill_tier(skill.level)
            skill_level_required = self._calculate_skill_exp_required(skill.level)

        self._save_progression(progression)
        self.logger.info(f"📚 {progression.character_name}: {skill_name} improved to {skill.level:.1f} ({skill.tier.value})")

        return progression

    def _calculate_skill_exp_required(self, skill_level: float) -> float:
        """Calculate experience required for skill level up"""
        base_exp = 50.0
        return base_exp * (skill_level ** 1.1)

    def _get_skill_tier(self, skill_level: float) -> SkillTier:
        """Get skill tier based on level"""
        if skill_level < 25:
            return SkillTier.NOVICE
        elif skill_level < 50:
            return SkillTier.APPRENTICE
        elif skill_level < 75:
            return SkillTier.JOURNEYMAN
        elif skill_level < 90:
            return SkillTier.EXPERT
        elif skill_level < 100:
            return SkillTier.MASTER
        elif skill_level < 200:
            return SkillTier.GRANDMASTER
        elif skill_level < 500:
            return SkillTier.LEGENDARY
        elif skill_level < 1000:
            return SkillTier.MYTHIC
        elif skill_level < 5000:
            return SkillTier.TRANSCENDENT
        elif skill_level < 10000:
            return SkillTier.DIVINE
        else:
            return SkillTier.OMNIPOTENT

    def evolve_ability(self, character_id: str, ability_name: str) -> CharacterProgression:
        """Evolve an ability (upward progression)"""
        progression = self.load_character(character_id)
        if not progression:
            raise ValueError(f"Character {character_id} not found")

        if ability_name not in progression.abilities:
            # Create new ability (outward progression)
            progression.abilities[ability_name] = Ability(
                name=ability_name,
                tier=AbilityTier.COMMON,
                level=1,
                power=1.0
            )

        ability = progression.abilities[ability_name]
        ability.level += 1
        ability.power *= 1.2
        ability.evolution_count += 1

        # Tier progression
        if ability.evolution_count % 10 == 0:
            ability.tier = self._get_next_ability_tier(ability.tier)

        self._save_progression(progression)
        self.logger.info(f"✨ {progression.character_name}: {ability_name} evolved to {ability.tier.value} (Level {ability.level})")

        return progression

    def _get_next_ability_tier(self, current_tier: AbilityTier) -> AbilityTier:
        """Get next ability tier"""
        tier_order = [
            AbilityTier.COMMON,
            AbilityTier.UNCOMMON,
            AbilityTier.RARE,
            AbilityTier.EPIC,
            AbilityTier.LEGENDARY,
            AbilityTier.MYTHIC,
            AbilityTier.TRANSCENDENT,
            AbilityTier.DIVINE,
            AbilityTier.OMNIPOTENT
        ]

        try:
            current_index = tier_order.index(current_tier)
            if current_index < len(tier_order) - 1:
                return tier_order[current_index + 1]
        except ValueError:
            pass

        return current_tier

    def _save_progression(self, progression: CharacterProgression) -> None:
        try:
            """Save character progression"""
            progression_file = self.data_dir / f"{progression.character_id}.json"
            with open(progression_file, 'w', encoding='utf-8') as f:
                json.dump(progression.to_dict(), f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_progression: {e}", exc_info=True)
            raise
    def get_progression_summary(self, character_id: str) -> Dict[str, Any]:
        """Get progression summary"""
        progression = self.load_character(character_id)
        if not progression:
            return {"error": "Character not found"}

        return {
            "character_name": progression.character_name,
            "level": progression.level,
            "transcendence_level": progression.transcendence_level,
            "experience": progression.experience,
            "evolution_count": progression.evolution_count,
            "total_stats": len(progression.stats),
            "total_skills": len(progression.skills),
            "total_abilities": len(progression.abilities),
            "recent_milestones": [m.to_dict() for m in progression.milestones[-5:]]
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="LITRPG Infinite Progression System")
    parser.add_argument("--create", type=str, help="Create new character (name)")
    parser.add_argument("--character-id", type=str, help="Character ID")
    parser.add_argument("--add-exp", type=float, help="Add experience")
    parser.add_argument("--improve-skill", type=str, help="Skill name to improve")
    parser.add_argument("--skill-exp", type=float, help="Skill experience to add")
    parser.add_argument("--evolve-ability", type=str, help="Ability name to evolve")
    parser.add_argument("--summary", action="store_true", help="Get progression summary")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    system = LITRPGInfiniteProgression()

    if args.create:
        character_id = args.create.lower().replace(" ", "_")
        progression = system.create_character(character_id, args.create)
        if args.json:
            print(json.dumps(progression.to_dict(), indent=2))
        else:
            print(f"\n🎮 Character Created: {progression.character_name}")
            print(f"   Level: {progression.level}")
            print(f"   Experience: {progression.experience}")

    elif args.character_id:
        if args.add_exp:
            progression = system.add_experience(args.character_id, args.add_exp)
            if args.json:
                print(json.dumps(progression.to_dict(), indent=2))

        elif args.improve_skill and args.skill_exp:
            progression = system.improve_skill(args.character_id, args.improve_skill, args.skill_exp)
            if args.json:
                print(json.dumps(progression.to_dict(), indent=2))

        elif args.evolve_ability:
            progression = system.evolve_ability(args.character_id, args.evolve_ability)
            if args.json:
                print(json.dumps(progression.to_dict(), indent=2))

        elif args.summary:
            summary = system.get_progression_summary(args.character_id)
            if args.json:
                print(json.dumps(summary, indent=2))
            else:
                print(f"\n📊 Progression Summary: {summary['character_name']}")
                print(f"   Level: {summary['level']} ({summary['transcendence_level']})")
                print(f"   Experience: {summary['experience']:.2f}")
                print(f"   Evolution Count: {summary['evolution_count']}")
                print(f"   Stats: {summary['total_stats']}")
                print(f"   Skills: {summary['total_skills']}")
                print(f"   Abilities: {summary['total_abilities']}")

    else:
        parser.print_help()
        print("\n🎮 LITRPG Infinite Progression System")
        print("   Direction: Ever Upward and Outward")
        print("   Scale: Epic and Expansive")
