#!/usr/bin/env python3
"""
Random Raid Encounter System

Implements random outlier fights like macro raids with low spawn rate.
Special handling for lightsaber duels (lower probability unless Force user from Star Wars).

Tags: #RAID #ENCOUNTER #COMBAT #LIGHTSABER #FORCE_USER @JARVIS @LUMINA
"""

import sys
import random
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from character_avatar_registry import CharacterAvatarRegistry, CharacterAvatar
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    CharacterAvatarRegistry = None
    CharacterAvatar = None

logger = get_logger("RandomRaidEncounter")


class EncounterType(Enum):
    """Types of random encounters"""
    MACRO_RAID = "macro_raid"  # Large-scale raid encounter
    LIGHTSABER_DUEL = "lightsaber_duel"  # Lightsaber duel (Force users)
    COMBAT_ENCOUNTER = "combat_encounter"  # Standard combat
    BOSS_FIGHT = "boss_fight"  # Boss-level encounter
    ELITE_SHOWDOWN = "elite_showdown"  # Elite vs Elite


class RandomRaidEncounterSystem:
    """
    Random Raid Encounter System

    Spawns random outlier fights with low probability.
    Special handling for lightsaber duels (half probability unless Force user).
    """

    def __init__(self, registry: Optional[CharacterAvatarRegistry] = None):
        """Initialize random raid encounter system"""
        if registry is None:
            if CharacterAvatarRegistry:
                registry = CharacterAvatarRegistry()
            else:
                raise ValueError("CharacterAvatarRegistry not available")

        self.registry = registry

        # Spawn rates (probabilities per check)
        self.base_spawn_rate = 0.001  # 0.1% base chance
        self.lightsaber_duel_rate = 0.0005  # 0.05% (half of base) unless Force user
        self.force_user_lightsaber_rate = 0.002  # 0.2% for Force users (higher)

        # Encounter tracking
        self.encounters: List[Dict[str, Any]] = []
        self.last_encounter_time: Optional[float] = None
        self.encounter_cooldown = 300.0  # 5 minutes minimum between encounters

        # Force user detection
        self.force_user_keywords = ["jedi", "sith", "force", "mace", "anakin", "ace"]
        self.star_wars_ip = "Star Wars"

        logger.info("=" * 80)
        logger.info("⚔️ RANDOM RAID ENCOUNTER SYSTEM")
        logger.info("=" * 80)
        logger.info(f"   Base spawn rate: {self.base_spawn_rate * 100}%")
        logger.info(f"   Lightsaber duel rate: {self.lightsaber_duel_rate * 100}% (unless Force user)")
        logger.info(f"   Force user lightsaber rate: {self.force_user_lightsaber_rate * 100}%")
        logger.info("=" * 80)

    def is_force_user(self, character: CharacterAvatar) -> bool:
        """Check if character is a Force user from Star Wars"""
        if not character.ip_owner or character.ip_owner != self.star_wars_ip:
            return False

        # Check name, character_id, lore for Force user keywords
        name_lower = character.name.lower()
        char_id_lower = character.character_id.lower()
        lore_lower = character.lore.lower() if character.lore else ""

        for keyword in self.force_user_keywords:
            if (keyword in name_lower or
                keyword in char_id_lower or
                keyword in lore_lower):
                return True

        return False

    def check_for_encounter(self) -> Optional[Dict[str, Any]]:
        """
        Check if a random encounter should spawn

        Returns encounter details if spawned, None otherwise
        """
        current_time = time.time()

        # Cooldown check
        if (self.last_encounter_time and
            current_time - self.last_encounter_time < self.encounter_cooldown):
            return None

        # Roll for encounter
        roll = random.random()

        # Check for lightsaber duel first (special case)
        if roll < self.lightsaber_duel_rate:
            # Check if we have Force users available
            force_users = self._get_force_users()
            if len(force_users) >= 2:
                # Force user lightsaber duel
                encounter = self._create_lightsaber_duel(force_users)
                if encounter:
                    self._record_encounter(encounter)
                    return encounter

        # Check for Force user lightsaber duel (higher rate)
        if roll < self.force_user_lightsaber_rate:
            force_users = self._get_force_users()
            if len(force_users) >= 2:
                encounter = self._create_lightsaber_duel(force_users)
                if encounter:
                    self._record_encounter(encounter)
                    return encounter

        # Check for macro raid
        if roll < self.base_spawn_rate:
            encounter = self._create_macro_raid()
            if encounter:
                self._record_encounter(encounter)
                return encounter

        return None

    def _get_force_users(self) -> List[CharacterAvatar]:
        """Get all Force users from Star Wars"""
        all_chars = self.registry.get_all_characters().values()
        return [char for char in all_chars if self.is_force_user(char)]

    def _create_lightsaber_duel(self, force_users: List[CharacterAvatar]) -> Optional[Dict[str, Any]]:
        """Create a lightsaber duel encounter between Force users"""
        if len(force_users) < 2:
            return None

        # Select two random Force users
        combatants = random.sample(force_users, min(2, len(force_users)))

        encounter = {
            "type": EncounterType.LIGHTSABER_DUEL.value,
            "timestamp": datetime.now().isoformat(),
            "combatants": [
                {
                    "character_id": c.character_id,
                    "name": c.name,
                    "ip_owner": c.ip_owner,
                    "hierarchy_level": c.hierarchy_level
                }
                for c in combatants
            ],
            "description": f"⚔️ LIGHTSABER DUEL: {combatants[0].name} vs {combatants[1].name}",
            "spawn_rate_used": self.force_user_lightsaber_rate if len(force_users) >= 2 else self.lightsaber_duel_rate
        }

        logger.info(f"⚔️ LIGHTSABER DUEL SPAWNED: {combatants[0].name} vs {combatants[1].name}")
        return encounter

    def _create_macro_raid(self) -> Optional[Dict[str, Any]]:
        """Create a macro raid encounter"""
        # Get raid leader
        raid_leaders = self.registry.get_raid_leaders()
        if not raid_leaders:
            return None

        raid_leader = raid_leaders[0]  # JARVIS

        # Get potential opponents (champions, elites, or random characters)
        champions = self.registry.get_champions()
        elites = self.registry.get_elites()

        # Select random opponents
        all_opponents = champions + elites
        if not all_opponents:
            return None

        num_opponents = random.randint(1, min(3, len(all_opponents)))
        opponents = random.sample(all_opponents, num_opponents)

        encounter = {
            "type": EncounterType.MACRO_RAID.value,
            "timestamp": datetime.now().isoformat(),
            "raid_leader": {
                "character_id": raid_leader.character_id,
                "name": raid_leader.name,
                "hierarchy_level": raid_leader.hierarchy_level
            },
            "opponents": [
                {
                    "character_id": o.character_id,
                    "name": o.name,
                    "ip_owner": o.ip_owner,
                    "hierarchy_level": o.hierarchy_level
                }
                for o in opponents
            ],
            "description": f"🎮 MACRO RAID: {raid_leader.name} vs {', '.join([o.name for o in opponents])}",
            "spawn_rate_used": self.base_spawn_rate
        }

        logger.info(f"🎮 MACRO RAID SPAWNED: {raid_leader.name} vs {len(opponents)} opponents")
        return encounter

    def _record_encounter(self, encounter: Dict[str, Any]):
        """Record encounter in history"""
        self.encounters.append(encounter)
        self.last_encounter_time = time.time()

        # Keep only last 100 encounters
        if len(self.encounters) > 100:
            self.encounters = self.encounters[-100:]

    def get_encounter_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent encounter history"""
        return self.encounters[-limit:] if self.encounters else []

    def get_encounter_stats(self) -> Dict[str, Any]:
        """Get encounter statistics"""
        if not self.encounters:
            return {
                "total_encounters": 0,
                "by_type": {},
                "force_user_duels": 0,
                "macro_raids": 0
            }

        stats = {
            "total_encounters": len(self.encounters),
            "by_type": {},
            "force_user_duels": 0,
            "macro_raids": 0
        }

        for encounter in self.encounters:
            enc_type = encounter.get("type", "unknown")
            stats["by_type"][enc_type] = stats["by_type"].get(enc_type, 0) + 1

            if enc_type == EncounterType.LIGHTSABER_DUEL.value:
                stats["force_user_duels"] += 1
            elif enc_type == EncounterType.MACRO_RAID.value:
                stats["macro_raids"] += 1

        return stats


def main():
    """Main entry point for testing"""
    if not CharacterAvatarRegistry:
        print("❌ Character Avatar Registry not available")
        return

    registry = CharacterAvatarRegistry()
    encounter_system = RandomRaidEncounterSystem(registry)

    print("=" * 80)
    print("⚔️ RANDOM RAID ENCOUNTER SYSTEM TEST")
    print("=" * 80)
    print()

    # Find Force users
    force_users = encounter_system._get_force_users()
    print(f"Force Users Found: {len(force_users)}")
    for fu in force_users:
        print(f"  • {fu.name} ({fu.character_id}) - {fu.ip_owner}")
    print()

    # Simulate multiple checks
    print("Simulating 10,000 encounter checks...")
    encounters_spawned = 0
    lightsaber_duels = 0
    macro_raids = 0

    for i in range(10000):
        encounter = encounter_system.check_for_encounter()
        if encounter:
            encounters_spawned += 1
            if encounter["type"] == EncounterType.LIGHTSABER_DUEL.value:
                lightsaber_duels += 1
            elif encounter["type"] == EncounterType.MACRO_RAID.value:
                macro_raids += 1

    print(f"Encounters Spawned: {encounters_spawned}")
    print(f"  Lightsaber Duels: {lightsaber_duels}")
    print(f"  Macro Raids: {macro_raids}")
    print()

    # Show recent encounters
    recent = encounter_system.get_encounter_history(5)
    if recent:
        print("Recent Encounters:")
        for enc in recent:
            print(f"  {enc['description']}")
            print(f"    Type: {enc['type']}")
            print(f"    Time: {enc['timestamp']}")
            print()

    # Show stats
    stats = encounter_system.get_encounter_stats()
    print("Encounter Statistics:")
    print(f"  Total: {stats['total_encounters']}")
    print(f"  By Type: {stats['by_type']}")
    print()

    print("=" * 80)


if __name__ == "__main__":


    main()