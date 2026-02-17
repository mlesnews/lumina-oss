#!/usr/bin/env python3
"""
Milestone Reward System

Triggers action fighting game events as rewards when reaching major/minor milestones.

Tags: #MILESTONE #REWARD #ACTION_FIGHTING #EVENT @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from character_avatar_registry import CharacterAvatarRegistry
    from random_raid_encounter_system import RandomRaidEncounterSystem, EncounterType
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    CharacterAvatarRegistry = None
    RandomRaidEncounterSystem = None
    EncounterType = None

logger = get_logger("MilestoneReward")


class MilestoneType(Enum):
    """Types of milestones"""
    MAJOR = "major"  # Major milestones
    MINOR = "minor"  # Minor milestones


class ActionFightingEventType(Enum):
    """Types of action fighting game events"""
    BOSS_RUSH = "boss_rush"  # Fight multiple bosses in sequence
    SURVIVAL_MODE = "survival_mode"  # Endless waves of enemies
    TOURNAMENT = "tournament"  # Tournament bracket
    TAG_TEAM = "tag_team"  # Tag team battle
    FINAL_BOSS = "final_boss"  # Final boss encounter
    COMBO_CHALLENGE = "combo_challenge"  # Combo execution challenge
    TIME_ATTACK = "time_attack"  # Speed challenge
    ULTIMATE_SHOWDOWN = "ultimate_showdown"  # Ultimate battle


class MilestoneRewardSystem:
    """
    Milestone Reward System

    Tracks milestones and triggers action fighting game events as rewards.
    """

    def __init__(self, registry: Optional[CharacterAvatarRegistry] = None,
                 encounter_system: Optional[RandomRaidEncounterSystem] = None):
        """Initialize milestone reward system"""
        if registry is None:
            if CharacterAvatarRegistry:
                registry = CharacterAvatarRegistry()
            else:
                raise ValueError("CharacterAvatarRegistry not available")

        self.registry = registry
        self.encounter_system = encounter_system

        # Data directory
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "milestones"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.milestones_file = self.data_dir / "milestones.json"

        # Milestone tracking
        self.milestones: Dict[str, Any] = {}
        self.completed_milestones: List[str] = []
        self.milestone_counters: Dict[str, int] = {}

        # Action fighting event history
        self.fighting_events: List[Dict[str, Any]] = []

        # Load existing data
        self._load_milestones()

        # Define milestone thresholds
        self.major_milestones = {
            "character_count_10": 10,
            "character_count_20": 20,
            "character_count_50": 50,
            "encounter_count_10": 10,
            "encounter_count_50": 50,
            "encounter_count_100": 100,
            "lightsaber_duel_5": 5,
            "lightsaber_duel_10": 10,
            "macro_raid_5": 5,
            "macro_raid_10": 10,
        }

        self.minor_milestones = {
            "character_count_5": 5,
            "character_count_15": 15,
            "encounter_count_5": 5,
            "encounter_count_25": 5,
            "lightsaber_duel_1": 1,
            "lightsaber_duel_3": 3,
            "macro_raid_1": 1,
            "macro_raid_3": 3,
        }

        logger.info("=" * 80)
        logger.info("🎯 MILESTONE REWARD SYSTEM")
        logger.info("=" * 80)
        logger.info(f"   Major milestones: {len(self.major_milestones)}")
        logger.info(f"   Minor milestones: {len(self.minor_milestones)}")
        logger.info(f"   Completed: {len(self.completed_milestones)}")
        logger.info("=" * 80)

    def _load_milestones(self):
        """Load milestone data from file"""
        if self.milestones_file.exists():
            try:
                with open(self.milestones_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.completed_milestones = data.get("completed", [])
                    self.milestone_counters = data.get("counters", {})
                    self.fighting_events = data.get("fighting_events", [])
                logger.info(f"✅ Loaded milestone data: {len(self.completed_milestones)} completed")
            except Exception as e:
                logger.error(f"❌ Error loading milestones: {e}")

    def _save_milestones(self):
        """Save milestone data to file"""
        try:
            data = {
                "completed": self.completed_milestones,
                "counters": self.milestone_counters,
                "fighting_events": self.fighting_events[-100:],  # Keep last 100
                "last_updated": datetime.now().isoformat()
            }
            with open(self.milestones_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug("✅ Saved milestone data")
        except Exception as e:
            logger.error(f"❌ Error saving milestones: {e}")

    def check_milestones(self, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Check for milestone completions and trigger rewards

        Returns list of triggered fighting events
        """
        if context is None:
            context = {}

        triggered_events = []

        # Update counters from context
        if "character_count" in context:
            self.milestone_counters["character_count"] = context["character_count"]

        if "encounter_count" in context:
            self.milestone_counters["encounter_count"] = context.get("encounter_count", 0)

        if "lightsaber_duel_count" in context:
            self.milestone_counters["lightsaber_duel_count"] = context.get("lightsaber_duel_count", 0)

        if "macro_raid_count" in context:
            self.milestone_counters["macro_raid_count"] = context.get("macro_raid_count", 0)

        # Check minor milestones
        for milestone_id, threshold in self.minor_milestones.items():
            if milestone_id in self.completed_milestones:
                continue

            # Determine counter name from milestone_id
            if "character_count" in milestone_id:
                counter_name = "character_count"
            elif "encounter_count" in milestone_id:
                counter_name = "encounter_count"
            elif "lightsaber_duel" in milestone_id:
                counter_name = "lightsaber_duel_count"
            elif "macro_raid" in milestone_id:
                counter_name = "macro_raid_count"
            else:
                continue

            counter_value = self.milestone_counters.get(counter_name, 0)

            # Extract number from milestone_id (threshold is already the number)
            if counter_value >= threshold:
                event = self._trigger_milestone_reward(milestone_id, MilestoneType.MINOR)
                if event:
                    triggered_events.append(event)
                    self.completed_milestones.append(milestone_id)

        # Check major milestones
        for milestone_id, threshold in self.major_milestones.items():
            if milestone_id in self.completed_milestones:
                continue

            # Determine counter name from milestone_id
            if "character_count" in milestone_id:
                counter_name = "character_count"
            elif "encounter_count" in milestone_id:
                counter_name = "encounter_count"
            elif "lightsaber_duel" in milestone_id:
                counter_name = "lightsaber_duel_count"
            elif "macro_raid" in milestone_id:
                counter_name = "macro_raid_count"
            else:
                continue

            counter_value = self.milestone_counters.get(counter_name, 0)

            # Extract number from milestone_id (threshold is already the number)
            if counter_value >= threshold:
                event = self._trigger_milestone_reward(milestone_id, MilestoneType.MAJOR)
                if event:
                    triggered_events.append(event)
                    self.completed_milestones.append(milestone_id)

        if triggered_events:
            self._save_milestones()

        return triggered_events

    def _extract_number_from_milestone(self, milestone_id: str) -> int:
        """Extract number from milestone ID"""
        parts = milestone_id.split("_")
        for part in reversed(parts):
            if part.isdigit():
                return int(part)
        return 0

    def _trigger_milestone_reward(self, milestone_id: str, milestone_type: MilestoneType) -> Optional[Dict[str, Any]]:
        """Trigger action fighting game event as reward"""

        # Select event type based on milestone
        if milestone_type == MilestoneType.MAJOR:
            event_type = self._select_major_event_type(milestone_id)
        else:
            event_type = self._select_minor_event_type(milestone_id)

        # Create fighting event
        event = self._create_action_fighting_event(event_type, milestone_id, milestone_type)

        if event:
            self.fighting_events.append(event)
            logger.info(f"🎯 MILESTONE REWARD: {milestone_type.value.upper()} - {milestone_id}")
            logger.info(f"   Event: {event_type.value} - {event.get('description', '')}")

        return event

    def _select_major_event_type(self, milestone_id: str) -> ActionFightingEventType:
        """Select event type for major milestone"""
        if "character_count" in milestone_id:
            return ActionFightingEventType.BOSS_RUSH
        elif "encounter_count" in milestone_id:
            return ActionFightingEventType.SURVIVAL_MODE
        elif "lightsaber_duel" in milestone_id:
            return ActionFightingEventType.TOURNAMENT
        elif "macro_raid" in milestone_id:
            return ActionFightingEventType.FINAL_BOSS
        else:
            return ActionFightingEventType.ULTIMATE_SHOWDOWN

    def _select_minor_event_type(self, milestone_id: str) -> ActionFightingEventType:
        """Select event type for minor milestone"""
        if "character_count" in milestone_id:
            return ActionFightingEventType.TAG_TEAM
        elif "encounter_count" in milestone_id:
            return ActionFightingEventType.COMBO_CHALLENGE
        elif "lightsaber_duel" in milestone_id:
            return ActionFightingEventType.TIME_ATTACK
        elif "macro_raid" in milestone_id:
            return ActionFightingEventType.TAG_TEAM
        else:
            return ActionFightingEventType.COMBO_CHALLENGE

    def _create_action_fighting_event(self, event_type: ActionFightingEventType,
                                     milestone_id: str, milestone_type: MilestoneType) -> Dict[str, Any]:
        """Create action fighting game event"""

        event = {
            "type": event_type.value,
            "milestone_id": milestone_id,
            "milestone_type": milestone_type.value,
            "timestamp": datetime.now().isoformat(),
            "description": "",
            "combatants": [],
            "rewards": []
        }

        # Get characters for event
        all_chars = list(self.registry.get_all_characters().values())
        champions = self.registry.get_champions()
        elites = self.registry.get_elites()
        raid_leaders = self.registry.get_raid_leaders()

        if event_type == ActionFightingEventType.BOSS_RUSH:
            # Fight multiple bosses in sequence
            event["description"] = "🎮 BOSS RUSH: Fight multiple bosses in sequence!"
            event["combatants"] = [{"character_id": c.character_id, "name": c.name}
                                  for c in (champions[:3] + elites[:2])[:5]]
            event["rewards"] = ["XP Bonus", "Unlock New Character", "Special Title"]

        elif event_type == ActionFightingEventType.SURVIVAL_MODE:
            # Endless waves
            event["description"] = "🌊 SURVIVAL MODE: Endless waves of enemies!"
            event["combatants"] = [{"character_id": c.character_id, "name": c.name}
                                  for c in elites[:5]]
            event["rewards"] = ["Survival Badge", "Combo Multiplier", "Extra Lives"]

        elif event_type == ActionFightingEventType.TOURNAMENT:
            # Tournament bracket
            event["description"] = "🏆 TOURNAMENT: Fight in tournament bracket!"
            event["combatants"] = [{"character_id": c.character_id, "name": c.name}
                                  for c in champions[:8]]
            event["rewards"] = ["Tournament Trophy", "Champion Title", "Exclusive Skin"]

        elif event_type == ActionFightingEventType.TAG_TEAM:
            # Tag team battle
            event["description"] = "👥 TAG TEAM: Team up for battle!"
            event["combatants"] = [{"character_id": c.character_id, "name": c.name}
                                  for c in (champions[:2] + elites[:2])[:4]]
            event["rewards"] = ["Team Bonus", "Synergy Boost", "Tag Combo Unlock"]

        elif event_type == ActionFightingEventType.FINAL_BOSS:
            # Final boss encounter
            event["description"] = "👹 FINAL BOSS: Ultimate challenge!"
            if raid_leaders:
                event["combatants"] = [{"character_id": rl.character_id, "name": rl.name}
                                      for rl in raid_leaders[:1]]
            event["rewards"] = ["Final Boss Trophy", "Legendary Title", "Ultimate Unlock"]

        elif event_type == ActionFightingEventType.COMBO_CHALLENGE:
            # Combo execution
            event["description"] = "💥 COMBO CHALLENGE: Execute perfect combos!"
            event["combatants"] = [{"character_id": c.character_id, "name": c.name}
                                  for c in elites[:3]]
            event["rewards"] = ["Combo Master Badge", "Style Points", "Combo Unlock"]

        elif event_type == ActionFightingEventType.TIME_ATTACK:
            # Speed challenge
            event["description"] = "⏱️ TIME ATTACK: Beat the clock!"
            event["combatants"] = [{"character_id": c.character_id, "name": c.name}
                                  for c in elites[:4]]
            event["rewards"] = ["Speed Demon Badge", "Time Bonus", "Quick Draw Unlock"]

        elif event_type == ActionFightingEventType.ULTIMATE_SHOWDOWN:
            # Ultimate battle
            event["description"] = "⚡ ULTIMATE SHOWDOWN: The ultimate battle!"
            event["combatants"] = [{"character_id": c.character_id, "name": c.name}
                                  for c in (raid_leaders + champions[:2])[:3]]
            event["rewards"] = ["Ultimate Badge", "Legendary Status", "All Unlocks"]

        return event

    def get_fighting_event_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent fighting event history"""
        return self.fighting_events[-limit:] if self.fighting_events else []

    def get_milestone_stats(self) -> Dict[str, Any]:
        """Get milestone statistics"""
        return {
            "completed_milestones": len(self.completed_milestones),
            "major_completed": len([m for m in self.completed_milestones if any(mm in m for mm in self.major_milestones.keys())]),
            "minor_completed": len([m for m in self.completed_milestones if any(mm in m for mm in self.minor_milestones.keys())]),
            "fighting_events_triggered": len(self.fighting_events),
            "counters": self.milestone_counters.copy()
        }


def main():
    """Main entry point for testing"""
    if not CharacterAvatarRegistry:
        print("❌ Character Avatar Registry not available")
        return

    registry = CharacterAvatarRegistry()
    encounter_system = RandomRaidEncounterSystem(registry) if RandomRaidEncounterSystem else None
    milestone_system = MilestoneRewardSystem(registry, encounter_system)

    print("=" * 80)
    print("🎯 MILESTONE REWARD SYSTEM TEST")
    print("=" * 80)
    print()

    # Simulate milestone progress
    print("Simulating milestone progress...")

    # Check milestones with context
    context = {
        "character_count": 21,  # Current character count
        "encounter_count": 5,
        "lightsaber_duel_count": 2,
        "macro_raid_count": 1
    }

    triggered = milestone_system.check_milestones(context)

    print(f"Triggered Events: {len(triggered)}")
    for event in triggered:
        print(f"  🎯 {event['description']}")
        print(f"     Type: {event['type']}")
        print(f"     Milestone: {event['milestone_id']}")
        print(f"     Rewards: {', '.join(event['rewards'])}")
        print()

    # Show stats
    stats = milestone_system.get_milestone_stats()
    print("Milestone Statistics:")
    print(f"  Completed: {stats['completed_milestones']}")
    print(f"  Major: {stats['major_completed']}")
    print(f"  Minor: {stats['minor_completed']}")
    print(f"  Fighting Events: {stats['fighting_events_triggered']}")
    print()

    # Show recent events
    recent = milestone_system.get_fighting_event_history(5)
    if recent:
        print("Recent Fighting Events:")
        for event in recent:
            print(f"  {event['description']}")
            print(f"    Type: {event['type']}")
            print(f"    Time: {event['timestamp']}")
            print()

    print("=" * 80)


if __name__ == "__main__":


    main()