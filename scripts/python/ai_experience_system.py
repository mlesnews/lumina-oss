#!/usr/bin/env python3
"""
AI Experience System - D&D Style XP Rewards
Dynamically scales XP based on task complexity, intensity, and positive outcomes
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


class TaskComplexity(Enum):
    """Task complexity levels (D&D inspired)"""
    NPC = "npc"                  # Level 0 - Regular human/NPC
    TRIVIAL = "trivial"          # 0-50 XP
    EASY = "easy"                # 50-100 XP
    MODERATE = "moderate"        # 100-250 XP
    HARD = "hard"                # 250-500 XP
    VERY_HARD = "very_hard"      # 500-1000 XP
    EPIC = "epic"                # 1000-2500 XP
    LEGENDARY = "legendary"      # 2500+ XP


class TaskIntensity(Enum):
    """Task intensity levels"""
    LOW = "low"                  # 1.0x multiplier
    MEDIUM = "medium"            # 1.5x multiplier
    HIGH = "high"                # 2.0x multiplier
    EXTREME = "extreme"          # 3.0x multiplier


class BoonBane(Enum):
    """Boon and Bane types (multiverse support)"""
    # Boons (Positive)
    BOON_MINOR = "boon_minor"
    BOON_MAJOR = "boon_major"
    BOON_EPIC = "boon_epic"
    BOON_LEGENDARY = "boon_legendary"

    # Banes (Negative)
    BANE_MINOR = "bane_minor"
    BANE_MAJOR = "bane_major"
    BANE_EPIC = "bane_epic"
    BANE_LEGENDARY = "bane_legendary"

    # Special (Multiverse)
    FORCE_BOON = "force_boon"           # Star Wars
    BARBARIAN_RAGE = "barbarian_rage"   # Conan
    TRANSFORM = "transform"             # Transformers
    WARP_FIELD = "warp_field"           # Star Trek


@dataclass
class XPReward:
    """XP Reward record"""
    timestamp: str
    base_xp: int
    complexity: str
    intensity: str
    intensity_multiplier: float
    positive_outcome_bonus: int
    total_xp: int
    dkp: int = 10  # Base DKP (Dragon Kill Points)
    context: Optional[str] = None
    task_description: Optional[str] = None
    is_penalty: bool = False  # True for punishments/oversights
    boon_bane: Optional[str] = None  # Boon or bane applied


@dataclass
class XPPenalty:
    """XP Penalty record (for oversights/mistakes)"""
    timestamp: str
    base_penalty: int
    severity: str  # minor, moderate, major, severe
    penalty_multiplier: float
    total_penalty: int
    dkp_loss: int = 0
    context: Optional[str] = None
    oversight_description: Optional[str] = None
    boon_bane: Optional[str] = None


@dataclass
class AILevel:
    """AI Level information"""
    level: int
    current_xp: int
    xp_to_next: int
    total_xp: int
    dkp_total: int


class AIExperienceSystem:
    """D&D Style AI Experience System"""

    # D&D 5e XP Table (Level 0 = NPC, Levels 1-20 = Adventurers)
    # Level 0: Regular humans/NPCs (no XP required)
    XP_TABLE = {
        0: 0,      # Level 0: NPC/Regular Human (starting level)
        1: 0,      # Level 1: 0 XP (first adventurer level)
        2: 300,    # Level 2: 300 XP
        3: 900,    # Level 3: 900 XP
        4: 2700,   # Level 4: 2700 XP
        5: 6500,   # Level 5: 6500 XP
        6: 14000,  # Level 6: 14000 XP
        7: 23000,  # Level 7: 23000 XP
        8: 34000,  # Level 8: 34000 XP
        9: 48000,  # Level 9: 48000 XP
        10: 64000, # Level 10: 64000 XP
        11: 85000, # Level 11: 85000 XP
        12: 100000, # Level 12: 100000 XP
        13: 120000, # Level 13: 120000 XP
        14: 140000, # Level 14: 140000 XP
        15: 165000, # Level 15: 165000 XP
        16: 195000, # Level 16: 195000 XP
        17: 225000, # Level 17: 225000 XP
        18: 265000, # Level 18: 265000 XP
        19: 305000, # Level 19: 305000 XP
        20: 355000, # Level 20: 355000 XP
    }

    # Penalty severity levels (XP loss, but no de-leveling unless special ability)
    PENALTY_SEVERITY = {
        "minor": 25,      # Small oversight
        "moderate": 75,   # Noticeable mistake
        "major": 175,     # Significant error
        "severe": 375,    # Major oversight
    }

    PENALTY_MULTIPLIERS = {
        "minor": 1.0,
        "moderate": 1.5,
        "major": 2.0,
        "severe": 3.0,
    }

    # Base XP by complexity (D&D inspired)
    COMPLEXITY_XP = {
        TaskComplexity.NPC: 0,        # Level 0 - no XP
        TaskComplexity.TRIVIAL: 25,
        TaskComplexity.EASY: 75,
        TaskComplexity.MODERATE: 175,
        TaskComplexity.HARD: 375,
        TaskComplexity.VERY_HARD: 750,
        TaskComplexity.EPIC: 1750,
        TaskComplexity.LEGENDARY: 5000,
    }

    # Intensity multipliers
    INTENSITY_MULTIPLIERS = {
        TaskIntensity.LOW: 1.0,
        TaskIntensity.MEDIUM: 1.5,
        TaskIntensity.HIGH: 2.0,
        TaskIntensity.EXTREME: 3.0,
    }

    def __init__(self, data_file: Optional[Path] = None):
        """Initialize AI Experience System"""
        self.logger = logging.getLogger(self.__class__.__name__)

        if data_file is None:
            data_file = project_root / "data" / "ai_experience.json"

        self.data_file = data_file
        self.data_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing data
        self.data = self._load_data()

    def _load_data(self) -> Dict:
        """Load experience data from file"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading experience data: {e}")

        # Default data - everyone starts at Level 0 (NPC/Regular Human)
        return {
            "total_xp": 0,
            "current_level": 0,  # Level 0 = NPC/Regular Human
            "dkp_total": 0,
            "rewards": [],
            "penalties": [],
            "boons": [],
            "banes": [],
            "multiverse_tags": [],
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }

    def _save_data(self):
        """Save experience data to file"""
        try:
            self.data["last_updated"] = datetime.now().isoformat()
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving experience data: {e}")

    def calculate_xp_reward(
        self,
        complexity: TaskComplexity,
        intensity: TaskIntensity = TaskIntensity.MEDIUM,
        positive_outcome: bool = True,
        context: Optional[str] = None,
        task_description: Optional[str] = None
    ) -> XPReward:
        """
        Calculate XP reward based on complexity, intensity, and outcome

        Args:
            complexity: Task complexity level
            intensity: Task intensity level
            positive_outcome: Whether task had positive outcome
            context: Optional context description
            task_description: Optional task description
        """
        # Base XP from complexity
        base_xp = self.COMPLEXITY_XP[complexity]

        # Intensity multiplier
        intensity_mult = self.INTENSITY_MULTIPLIERS[intensity]

        # Positive outcome bonus (10% of base XP)
        positive_bonus = int(base_xp * 0.1) if positive_outcome else 0

        # Calculate total XP
        total_xp = int((base_xp * intensity_mult) + positive_bonus)

        # Base DKP (Dragon Kill Points) - always 10
        dkp = 10

        reward = XPReward(
            timestamp=datetime.now().isoformat(),
            base_xp=base_xp,
            complexity=complexity.value,
            intensity=intensity.value,
            intensity_multiplier=intensity_mult,
            positive_outcome_bonus=positive_bonus,
            total_xp=total_xp,
            dkp=dkp,
            context=context,
            task_description=task_description
        )

        return reward

    def award_xp(self, reward: XPReward) -> AILevel:
        """
        Award XP and update level

        Args:
            reward: XP reward to award
        """
        # Add reward to history
        self.data["rewards"].append(asdict(reward))

        # Update totals
        self.data["total_xp"] += reward.total_xp
        self.data["dkp_total"] += reward.dkp

        # Calculate new level
        new_level = self._calculate_level(self.data["total_xp"])
        self.data["current_level"] = new_level

        # Save data
        self._save_data()

        # Get current level info
        return self.get_current_level()

    def _calculate_level(self, total_xp: int) -> int:
        """Calculate level based on total XP (D&D 5e table)"""
        level = 0  # Start at Level 0 (NPC)
        for lvl, xp_required in sorted(self.XP_TABLE.items()):
            if total_xp >= xp_required:
                level = lvl
            else:
                break
        return level

    def apply_penalty(
        self,
        severity: str,
        oversight_description: str,
        context: Optional[str] = None,
        boon_bane: Optional[BoonBane] = None
    ) -> Tuple[XPPenalty, AILevel]:
        """
        Apply XP penalty for oversights/mistakes

        Note: In D&D, XP loss that de-levels is usually from special monster abilities.
        Regular penalties just reduce XP, not levels (unless severe enough).

        Args:
            severity: minor, moderate, major, severe
            oversight_description: Description of the oversight/mistake
            context: Optional context
            boon_bane: Optional bane to apply
        """
        base_penalty = self.PENALTY_SEVERITY.get(severity, 25)
        penalty_mult = self.PENALTY_MULTIPLIERS.get(severity, 1.0)
        total_penalty = int(base_penalty * penalty_mult)

        # DKP loss (smaller than XP loss)
        dkp_loss = max(1, int(total_penalty / 10))

        penalty = XPPenalty(
            timestamp=datetime.now().isoformat(),
            base_penalty=base_penalty,
            severity=severity,
            penalty_multiplier=penalty_mult,
            total_penalty=total_penalty,
            dkp_loss=dkp_loss,
            context=context,
            oversight_description=oversight_description,
            boon_bane=boon_bane.value if boon_bane else None
        )

        # Apply penalty (reduce XP, but don't go below 0)
        old_xp = self.data["total_xp"]
        new_xp = max(0, old_xp - total_penalty)
        self.data["total_xp"] = new_xp

        # Reduce DKP
        self.data["dkp_total"] = max(0, self.data["dkp_total"] - dkp_loss)

        # Recalculate level (may de-level if penalty is severe enough)
        new_level = self._calculate_level(new_xp)
        self.data["current_level"] = new_level

        # Add to penalties history
        self.data["penalties"].append(asdict(penalty))

        # Add bane if specified
        if boon_bane:
            self.data["banes"].append({
                "timestamp": datetime.now().isoformat(),
                "type": boon_bane.value,
                "context": context,
                "description": oversight_description
            })

        self._save_data()

        return penalty, self.get_current_level()

    def get_current_level(self) -> AILevel:
        """Get current level information"""
        current_level = self.data["current_level"]
        total_xp = self.data["total_xp"]

        # Get XP required for next level
        next_level = current_level + 1
        if next_level in self.XP_TABLE:
            xp_for_next = self.XP_TABLE[next_level]
            xp_to_next = max(0, xp_for_next - total_xp)
        else:
            xp_to_next = 0  # Max level

        return AILevel(
            level=current_level,
            current_xp=total_xp,
            xp_to_next=xp_to_next,
            total_xp=total_xp,
            dkp_total=self.data["dkp_total"]
        )

    def process_love_command(
        self,
        complexity: Optional[TaskComplexity] = None,
        intensity: Optional[TaskIntensity] = None,
        context: Optional[str] = None,
        task_description: Optional[str] = None
    ) -> Tuple[XPReward, AILevel]:
        """
        Process @love command and award XP

        If complexity/intensity not provided, attempts to infer from recent context
        """
        # Default to MODERATE complexity and MEDIUM intensity if not specified
        if complexity is None:
            complexity = TaskComplexity.MODERATE

        if intensity is None:
            intensity = TaskIntensity.MEDIUM

        # Calculate and award XP
        reward = self.calculate_xp_reward(
            complexity=complexity,
            intensity=intensity,
            positive_outcome=True,  # @love always positive
            context=context,
            task_description=task_description
        )

        level_info = self.award_xp(reward)

        return reward, level_info


def auto_award_task_completion(
    task_description: str,
    complexity: Optional[TaskComplexity] = None,
    intensity: Optional[TaskIntensity] = None,
    success: bool = True
) -> Tuple[XPReward, AILevel]:
    """
    Automatically award XP for successful task completion
    Called automatically after tasks complete successfully

    Args:
        task_description: Description of completed task
        complexity: Task complexity (auto-detected if None)
        intensity: Task intensity (auto-detected if None)
        success: Whether task was successful
    """
    system = AIExperienceSystem()

    # Auto-detect complexity if not provided
    if complexity is None:
        # Simple heuristics for complexity detection
        task_lower = task_description.lower()
        if any(word in task_lower for word in ['fix', 'update', 'modify', 'add']):
            complexity = TaskComplexity.MODERATE
        elif any(word in task_lower for word in ['create', 'implement', 'build', 'develop']):
            complexity = TaskComplexity.HARD
        elif any(word in task_lower for word in ['refactor', 'optimize', 'integrate', 'system']):
            complexity = TaskComplexity.VERY_HARD
        else:
            complexity = TaskComplexity.MODERATE

    # Auto-detect intensity if not provided
    if intensity is None:
        intensity = TaskIntensity.MEDIUM

    reward = system.calculate_xp_reward(
        complexity=complexity,
        intensity=intensity,
        positive_outcome=success,
        context="Automatic task completion reward",
        task_description=task_description
    )

    level_info = system.award_xp(reward)

    return reward, level_info


def main():
    """Main entry point for @love command"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Experience System - @love Command")
    parser.add_argument("--love", action="store_true", help="Award XP for @love command")
    parser.add_argument("--penalty", action="store_true", help="Apply XP penalty for oversight/mistake")
    parser.add_argument("--auto-complete", action="store_true", help="Auto-award XP for task completion")
    parser.add_argument("--complexity", choices=[c.value for c in TaskComplexity],
                       help="Task complexity level")
    parser.add_argument("--intensity", choices=[i.value for i in TaskIntensity],
                       help="Task intensity level")
    parser.add_argument("--severity", choices=["minor", "moderate", "major", "severe"],
                       help="Penalty severity level")
    parser.add_argument("--context", help="Context description")
    parser.add_argument("--task", help="Task description")
    parser.add_argument("--oversight", help="Oversight/mistake description")
    parser.add_argument("--status", action="store_true", help="Show current level status")

    args = parser.parse_args()

    system = AIExperienceSystem()

    if args.status:
        level_info = system.get_current_level()
        print(f"\n🎮 AI Experience System Status")
        print(f"   Level: {level_info.level}")
        print(f"   Total XP: {level_info.total_xp:,}")
        print(f"   XP to Next Level: {level_info.xp_to_next:,}")
        print(f"   Total DKP: {level_info.dkp_total}")
        print(f"\n📊 Recent Rewards:")
        recent = system.data.get("rewards", [])[-5:]
        for r in recent:
            print(f"   +{r['total_xp']} XP ({r['complexity']}, {r['intensity']})")

        penalties = system.data.get("penalties", [])
        if penalties:
            print(f"\n⚠️  Recent Penalties:")
            recent_penalties = penalties[-5:]
            for p in recent_penalties:
                print(f"   -{p['total_penalty']} XP ({p['severity']})")

        boons = system.data.get("boons", [])
        banes = system.data.get("banes", [])
        if boons or banes:
            print(f"\n✨ Boons & Banes:")
            if boons:
                print(f"   Boons: {len(boons)}")
            if banes:
                print(f"   Banes: {len(banes)}")
    elif args.auto_complete:
        if not args.task:
            print("❌ Error: --task required for --auto-complete")
            return

        complexity = TaskComplexity[args.complexity.upper()] if args.complexity else None
        intensity = TaskIntensity[args.intensity.upper()] if args.intensity else None

        reward, level_info = auto_award_task_completion(
            task_description=args.task,
            complexity=complexity,
            intensity=intensity,
            success=True
        )

        print(f"\n✅ Task Completion - Auto XP Award!")
        print(f"   🎁 Reward: +{reward.total_xp} XP")
        print(f"   💎 DKP: +{reward.dkp}")
        print(f"   📊 Complexity: {reward.complexity}")
        print(f"   ⚡ Intensity: {reward.intensity} (x{reward.intensity_multiplier})")
        print(f"\n📈 Level Status:")
        print(f"   Level: {level_info.level}")
        print(f"   Total XP: {level_info.total_xp:,}")
        print(f"   XP to Next Level: {level_info.xp_to_next:,}")
        print(f"   Total DKP: {level_info.dkp_total}")
    elif args.love:
        complexity = TaskComplexity[args.complexity.upper()] if args.complexity else None
        intensity = TaskIntensity[args.intensity.upper()] if args.intensity else None

        reward, level_info = system.process_love_command(
            complexity=complexity,
            intensity=intensity,
            context=args.context,
            task_description=args.task
        )

        print(f"\n❤️  @LOVE Command Processed!")
        print(f"   🎁 Reward: +{reward.total_xp} XP")
        print(f"   💎 DKP: +{reward.dkp}")
        print(f"   📊 Complexity: {reward.complexity}")
        print(f"   ⚡ Intensity: {reward.intensity} (x{reward.intensity_multiplier})")
        print(f"\n📈 Level Status:")
        print(f"   Level: {level_info.level}")
        print(f"   Total XP: {level_info.total_xp:,}")
        print(f"   XP to Next Level: {level_info.xp_to_next:,}")
        print(f"   Total DKP: {level_info.dkp_total}")
    elif args.penalty:
        if not args.oversight:
            print("❌ Error: --oversight required for --penalty")
            return

        severity = args.severity or "moderate"

        penalty, level_info = system.apply_penalty(
            severity=severity,
            oversight_description=args.oversight,
            context=args.context
        )

        print(f"\n⚠️  Penalty Applied!")
        print(f"   💔 Penalty: -{penalty.total_penalty} XP")
        print(f"   💎 DKP Loss: -{penalty.dkp_loss}")
        print(f"   📊 Severity: {penalty.severity} (x{penalty.penalty_multiplier})")
        print(f"\n📈 Level Status:")
        print(f"   Level: {level_info.level}")
        print(f"   Total XP: {level_info.total_xp:,}")
        print(f"   XP to Next Level: {level_info.xp_to_next:,}")
        print(f"   Total DKP: {level_info.dkp_total}")
    else:
        parser.print_help()


if __name__ == "__main__":


    main()