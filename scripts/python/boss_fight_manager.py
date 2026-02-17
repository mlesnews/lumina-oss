#!/usr/bin/env python3
"""
WoW-Style Boss Fight & Epic Monster Manager
Integrates boss fights and epic monsters into VA combat system

Features:
- Boss phases (Normal, Enraged, Desperate)
- Special abilities with cooldowns
- Adds (minions) spawning
- Enrage timers
- Loot drops
- Victory/defeat conditions

Tags: #BOSS #EPIC #MONSTER #WOW #COMBAT #PHASES @COMBAT @JARVIS @TEAM
"""

import sys
import json
import time
import random
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("BossFightManager")


@dataclass
class BossAbility:
    """Boss ability definition"""
    ability_name: str
    cooldown: float
    damage: float
    description: str
    damage_reduction: float = 0.0
    duration: float = 0.0
    adds_spawned: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BossPhase:
    """Boss phase definition"""
    phase_number: int
    phase_name: str
    health_percent_start: float
    health_percent_end: float
    abilities: List[BossAbility] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'phase_number': self.phase_number,
            'phase_name': self.phase_name,
            'health_percent_start': self.health_percent_start,
            'health_percent_end': self.health_percent_end,
            'abilities': [a.to_dict() for a in self.abilities]
        }


@dataclass
class BossStatus:
    """Current boss fight status"""
    boss_id: str
    boss_name: str
    current_health: float
    max_health: float
    current_phase: int
    phase_start_time: float
    ability_cooldowns: Dict[str, float] = field(default_factory=dict)
    active_buffs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    adds: List[Dict[str, Any]] = field(default_factory=list)
    fight_start_time: float = field(default_factory=time.time)
    enrage_timer: float = 0.0

    def get_health_percent(self) -> float:
        """Get current health as percentage"""
        return (self.current_health / self.max_health) * 100.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'boss_id': self.boss_id,
            'boss_name': self.boss_name,
            'current_health': self.current_health,
            'max_health': self.max_health,
            'health_percent': self.get_health_percent(),
            'current_phase': self.current_phase,
            'phase_start_time': self.phase_start_time,
            'ability_cooldowns': self.ability_cooldowns,
            'active_buffs': self.active_buffs,
            'adds_count': len(self.adds),
            'fight_duration': time.time() - self.fight_start_time,
            'enrage_timer': self.enrage_timer
        }


@dataclass
class EpicMonster:
    """Epic monster (add/minion) definition"""
    monster_id: str
    name: str
    monster_type: str
    health_points: float
    max_health: float
    abilities: List[BossAbility] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'monster_id': self.monster_id,
            'name': self.name,
            'monster_type': self.monster_type,
            'health_points': self.health_points,
            'max_health': self.max_health,
            'abilities': [a.to_dict() for a in self.abilities]
        }


class BossFightManager:
    """
    WoW-Style Boss Fight & Epic Monster Manager

    Manages boss fights with phases, abilities, adds, and epic mechanics
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize boss fight manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_file = self.project_root / "config" / "boss_fight_config.json"

        self.bosses: Dict[str, Dict[str, Any]] = {}
        self.epic_monsters: Dict[str, EpicMonster] = {}
        self.combat_mechanics: Dict[str, Any] = {}

        self.active_boss_fight: Optional[BossStatus] = None
        self.active_adds: List[EpicMonster] = []

        self._load_config()

        logger.info("✅ Boss Fight Manager initialized")

    def _load_config(self):
        """Load boss fight configuration"""
        if not self.config_file.exists():
            logger.warning(f"Boss fight config not found: {self.config_file}")
            return

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            boss_config = config_data.get("boss_fight_system", {})
            self.bosses = boss_config.get("bosses", {})
            self.combat_mechanics = boss_config.get("combat_mechanics", {})

            # Load epic monsters
            epic_monsters_config = boss_config.get("epic_monsters", {})
            for monster_id, monster_config in epic_monsters_config.items():
                abilities = []
                for ability_config in monster_config.get("abilities", []):
                    abilities.append(BossAbility(
                        ability_name=ability_config["ability_name"],
                        cooldown=ability_config["cooldown"],
                        damage=ability_config["damage"],
                        description=ability_config["description"]
                    ))

                self.epic_monsters[monster_id] = EpicMonster(
                    monster_id=monster_id,
                    name=monster_config["name"],
                    monster_type=monster_config["monster_type"],
                    health_points=monster_config["health_points"],
                    max_health=monster_config["max_health"],
                    abilities=abilities
                )

            logger.info(f"✅ Loaded {len(self.bosses)} bosses and {len(self.epic_monsters)} epic monsters")

        except Exception as e:
            logger.error(f"Error loading boss fight config: {e}", exc_info=True)

    def start_boss_fight(self, boss_id: str) -> Optional[BossStatus]:
        """
        Start a boss fight

        Args:
            boss_id: ID of the boss to fight

        Returns:
            BossStatus if boss found, None otherwise
        """
        if boss_id not in self.bosses:
            logger.warning(f"Boss not found: {boss_id}")
            return None

        boss_config = self.bosses[boss_id]

        # Create boss status
        self.active_boss_fight = BossStatus(
            boss_id=boss_id,
            boss_name=boss_config["name"],
            current_health=boss_config["health_points"],
            max_health=boss_config["max_health"],
            current_phase=1,
            phase_start_time=time.time(),
            fight_start_time=time.time(),
            enrage_timer=self.combat_mechanics.get("enrage_timer", 300)
        )

        logger.info(f"🔥 BOSS FIGHT STARTED: {self.active_boss_fight.boss_name}")
        logger.info(f"   Health: {self.active_boss_fight.current_health}/{self.active_boss_fight.max_health}")
        logger.info(f"   Phase: {self.active_boss_fight.current_phase}")

        return self.active_boss_fight

    def get_current_phase_config(self, boss_id: str, phase_number: int) -> Optional[BossPhase]:
        """Get phase configuration for a boss"""
        if boss_id not in self.bosses:
            return None

        boss_config = self.bosses[boss_id]
        phases = boss_config.get("phases", [])

        for phase_config in phases:
            if phase_config["phase_number"] == phase_number:
                abilities = []
                for ability_config in phase_config.get("abilities", []):
                    abilities.append(BossAbility(
                        ability_name=ability_config["ability_name"],
                        cooldown=ability_config["cooldown"],
                        damage=ability_config["damage"],
                        description=ability_config["description"],
                        damage_reduction=ability_config.get("damage_reduction", 0.0),
                        duration=ability_config.get("duration", 0.0),
                        adds_spawned=ability_config.get("adds_spawned", 0)
                    ))

                return BossPhase(
                    phase_number=phase_config["phase_number"],
                    phase_name=phase_config["phase_name"],
                    health_percent_start=phase_config["health_percent_start"],
                    health_percent_end=phase_config["health_percent_end"],
                    abilities=abilities
                )

        return None

    def check_phase_transition(self) -> Optional[int]:
        """Check if boss should transition to next phase"""
        if not self.active_boss_fight:
            return None

        boss_config = self.bosses[self.active_boss_fight.boss_id]
        phases = boss_config.get("phases", [])

        health_percent = self.active_boss_fight.get_health_percent()
        current_phase_num = self.active_boss_fight.current_phase

        # Check if we need to transition to next phase
        for phase_config in phases:
            if phase_config["phase_number"] == current_phase_num + 1:
                phase_start = phase_config["health_percent_start"]
                phase_end = phase_config["health_percent_end"]

                if phase_start >= health_percent >= phase_end:
                    return current_phase_num + 1

        return None

    def transition_phase(self, new_phase: int):
        """Transition boss to new phase"""
        if not self.active_boss_fight:
            return

        old_phase = self.active_boss_fight.current_phase
        self.active_boss_fight.current_phase = new_phase
        self.active_boss_fight.phase_start_time = time.time()

        logger.warning(f"⚡ PHASE TRANSITION: {old_phase} → {new_phase}")

        # Get phase config for new phase
        phase_config = self.get_current_phase_config(self.active_boss_fight.boss_id, new_phase)
        if phase_config:
            logger.info(f"   Phase: {phase_config.phase_name}")

    def get_available_abilities(self) -> List[BossAbility]:
        """Get abilities available in current phase"""
        if not self.active_boss_fight:
            return []

        phase_config = self.get_current_phase_config(
            self.active_boss_fight.boss_id,
            self.active_boss_fight.current_phase
        )

        if not phase_config:
            return []

        current_time = time.time()
        available = []

        for ability in phase_config.abilities:
            # Check cooldown
            last_used = self.active_boss_fight.ability_cooldowns.get(ability.ability_name, 0)
            if current_time - last_used >= ability.cooldown:
                available.append(ability)

        return available

    def execute_boss_ability(self, ability: BossAbility) -> Dict[str, Any]:
        """
        Execute a boss ability

        Returns:
            Dict with ability execution results
        """
        if not self.active_boss_fight:
            return {}

        current_time = time.time()
        self.active_boss_fight.ability_cooldowns[ability.ability_name] = current_time

        result = {
            "ability_name": ability.ability_name,
            "damage": ability.damage,
            "description": ability.description,
            "timestamp": current_time
        }

        # Handle damage reduction (shield/buff)
        if ability.damage_reduction > 0 and ability.duration > 0:
            self.active_boss_fight.active_buffs["shield"] = {
                "damage_reduction": ability.damage_reduction,
                "duration": ability.duration,
                "start_time": current_time
            }
            result["buff_applied"] = "shield"
            logger.info(f"🛡️  {ability.ability_name}: Shield activated ({ability.damage_reduction*100}% damage reduction)")

        # Handle adds spawning
        if ability.adds_spawned > 0:
            adds_spawned = []
            for i in range(ability.adds_spawned):
                # Spawn random epic monster
                if self.epic_monsters:
                    monster_id = random.choice(list(self.epic_monsters.keys()))
                    monster = self.epic_monsters[monster_id]
                    self.active_adds.append(monster)
                    adds_spawned.append(monster.name)

            result["adds_spawned"] = adds_spawned
            logger.warning(f"👾 {ability.ability_name}: {ability.adds_spawned} adds spawned!")

        return result

    def apply_damage_to_boss(self, damage: float) -> Dict[str, Any]:
        """
        Apply damage to boss (with damage reduction from active buffs)

        Returns:
            Dict with damage application results
        """
        if not self.active_boss_fight:
            return {}

        current_time = time.time()
        actual_damage = damage

        # Apply damage reduction from active buffs
        if "shield" in self.active_boss_fight.active_buffs:
            shield = self.active_boss_fight.active_buffs["shield"]
            # Check if shield is still active
            if current_time - shield["start_time"] < shield["duration"]:
                damage_reduction = shield["damage_reduction"]
                actual_damage = damage * (1 - damage_reduction)
            else:
                # Shield expired
                del self.active_boss_fight.active_buffs["shield"]

        self.active_boss_fight.current_health = max(0, self.active_boss_fight.current_health - actual_damage)

        # Check for phase transition
        new_phase = self.check_phase_transition()
        if new_phase:
            self.transition_phase(new_phase)

        result = {
            "damage_dealt": actual_damage,
            "current_health": self.active_boss_fight.current_health,
            "health_percent": self.active_boss_fight.get_health_percent(),
            "phase_transition": new_phase is not None,
            "boss_defeated": self.active_boss_fight.current_health <= 0
        }

        return result

    def update_boss_fight(self) -> Dict[str, Any]:
        """
        Update boss fight state (call periodically)

        Returns:
            Dict with update results
        """
        if not self.active_boss_fight:
            return {}

        current_time = time.time()
        update_result = {
            "abilities_executed": [],
            "adds_killed": 0,
            "phase_transition": False
        }

        # Check for enrage
        fight_duration = current_time - self.active_boss_fight.fight_start_time
        if fight_duration >= self.active_boss_fight.enrage_timer:
            logger.critical("⏰ ENRAGE TIMER EXPIRED! Boss is enraged!")
            # Enrage mechanics (e.g., increased damage, faster abilities)
            update_result["enraged"] = True

        # Boss auto-attack / ability execution
        available_abilities = self.get_available_abilities()
        if available_abilities:
            # Randomly execute an ability
            if random.random() < 0.3:  # 30% chance per update cycle
                ability = random.choice(available_abilities)
                execution_result = self.execute_boss_ability(ability)
                update_result["abilities_executed"].append(execution_result)

        # Update active buffs (expire old ones)
        expired_buffs = []
        for buff_name, buff_data in self.active_boss_fight.active_buffs.items():
            if current_time - buff_data["start_time"] >= buff_data["duration"]:
                expired_buffs.append(buff_name)

        for buff_name in expired_buffs:
            del self.active_boss_fight.active_buffs[buff_name]
            logger.info(f"⏱️  Buff expired: {buff_name}")

        # Clean up dead adds
        self.active_adds = [add for add in self.active_adds if add.health_points > 0]

        return update_result

    def is_boss_defeated(self) -> bool:
        """Check if boss is defeated"""
        if not self.active_boss_fight:
            return False
        return self.active_boss_fight.current_health <= 0

    def get_boss_loot(self, boss_id: str) -> List[str]:
        """Get loot drops for defeated boss"""
        if boss_id not in self.bosses:
            return []

        return self.bosses[boss_id].get("loot_drops", [])

    def end_boss_fight(self, victory: bool = False) -> Dict[str, Any]:
        """
        End boss fight

        Args:
            victory: True if boss was defeated

        Returns:
            Dict with end fight results
        """
        if not self.active_boss_fight:
            return {}

        boss_id = self.active_boss_fight.boss_id
        boss_name = self.active_boss_fight.boss_name

        result = {
            "boss_id": boss_id,
            "boss_name": boss_name,
            "victory": victory,
            "fight_duration": time.time() - self.active_boss_fight.fight_start_time,
            "final_phase": self.active_boss_fight.current_phase,
            "loot": []
        }

        if victory:
            result["loot"] = self.get_boss_loot(boss_id)
            boss_config = self.bosses[boss_id]
            result["victory_message"] = boss_config.get("victory_message", f"{boss_name} defeated!")
            logger.info(f"🎉 VICTORY! {boss_name} defeated!")
            logger.info(f"   Loot: {', '.join(result['loot'])}")
        else:
            boss_config = self.bosses[boss_id]
            result["defeat_message"] = boss_config.get("defeat_message", f"{boss_name} victorious!")
            logger.warning(f"💀 DEFEAT! {boss_name} was not defeated!")

        # Clear active fight
        self.active_boss_fight = None
        self.active_adds = []

        return result


if __name__ == "__main__":
    # Test the boss fight manager
    manager = BossFightManager()

    print("\n" + "="*80)
    print("Boss Fight Manager Test")
    print("="*80 + "\n")

    # List available bosses
    print("Available Bosses:")
    for boss_id, boss_config in manager.bosses.items():
        print(f"  - {boss_config['name']} ({boss_id})")
        print(f"    Health: {boss_config['health_points']}")
        print(f"    Phases: {len(boss_config.get('phases', []))}")
        print()

    # Test boss fight
    print("-"*80)
    print("Starting Boss Fight: ULTRON Prime")
    print("-"*80 + "\n")

    boss_status = manager.start_boss_fight("ultron_prime")
    if boss_status:
        print(f"Boss: {boss_status.boss_name}")
        print(f"Health: {boss_status.current_health}/{boss_status.max_health}")
        print(f"Phase: {boss_status.current_phase}")
        print()

        # Simulate some combat
        for i in range(5):
            # Apply damage
            damage_result = manager.apply_damage_to_boss(50)
            print(f"Damage: {damage_result['damage_dealt']:.1f}, Health: {damage_result['current_health']:.1f} ({damage_result['health_percent']:.1f}%)")

            # Update fight
            update_result = manager.update_boss_fight()
            if update_result.get("abilities_executed"):
                for ability_exec in update_result["abilities_executed"]:
                    print(f"  Boss ability: {ability_exec['ability_name']} - {ability_exec['description']}")

            if damage_result.get("phase_transition"):
                print(f"  ⚡ Phase transition!")

            if damage_result.get("boss_defeated"):
                break

            time.sleep(0.1)

        # End fight
        victory = manager.is_boss_defeated()
        end_result = manager.end_boss_fight(victory=victory)
        print(f"\nFight ended: {'VICTORY' if victory else 'DEFEAT'}")
        if end_result.get("loot"):
            print(f"Loot: {', '.join(end_result['loot'])}")
