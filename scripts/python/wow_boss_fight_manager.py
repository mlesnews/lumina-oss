#!/usr/bin/env python3
"""
WoW-Style Boss Fight Manager
World of Warcraft-style boss fights and epic monsters for VA combat

Features:
- Multiple difficulty levels (LFR, Normal, Heroic, Mythic)
- Phase-based combat mechanics
- Cast bars with warnings
- Enrage timers
- Ability cooldowns and damage scaling
- Epic monster announcements

Tags: #WOW #BOSS #FIGHT #EPIC #MONSTER #COMBAT @JARVIS @TEAM
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

logger = get_logger("WoWBossFightManager")


@dataclass
class BossAbility:
    """Boss ability configuration"""
    name: str
    damage: float
    cooldown: float
    ability_type: str  # melee, aoe, special, ultimate
    cast_bar: bool = False
    cast_time: float = 0.0
    warning: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BossPhase:
    """Boss phase configuration"""
    name: str
    health_percentage_start: float
    health_percentage_end: float
    abilities: List[BossAbility] = field(default_factory=list)
    enrage: bool = False
    enrage_damage_multiplier: float = 1.0
    enrage_attack_speed_multiplier: float = 1.0
    cast_times: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['abilities'] = [a.to_dict() for a in self.abilities]
        return data


@dataclass
class Boss:
    """Boss configuration"""
    boss_name: str
    boss_id: str
    difficulty: str
    max_health: float
    phases: Dict[str, BossPhase] = field(default_factory=dict)
    enrage_timer: float = 600.0
    enrage_message: str = "BOSS HAS ENRAGED!"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['phases'] = {k: v.to_dict() for k, v in self.phases.items()}
        return data


class WoWBossFightManager:
    """
    WoW-Style Boss Fight Manager

    Manages World of Warcraft-style boss fights with phases, abilities, cast bars,
    enrage timers, and epic monster mechanics.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize boss fight manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_file = self.project_root / "config" / "wow_boss_fight_config.json"

        self.bosses: Dict[str, Boss] = {}
        self.current_boss: Optional[Boss] = None
        self.current_phase: Optional[BossPhase] = None
        self.current_phase_name: Optional[str] = None

        # Combat state
        self.boss_health: float = 0.0
        self.boss_max_health: float = 0.0
        self.fight_start_time: Optional[float] = None
        self.enrage_time: Optional[float] = None
        self.is_enraged: bool = False

        # Ability tracking
        self.ability_cooldowns: Dict[str, float] = {}  # ability_name -> last_used_time
        self.current_cast: Optional[Dict[str, Any]] = None  # Current ability being cast
        self.cast_start_time: Optional[float] = None

        self._load_config()

        logger.info("✅ WoW Boss Fight Manager initialized")

    def _load_config(self):
        """Load boss fight configuration"""
        if not self.config_file.exists():
            logger.warning(f"Config file not found: {self.config_file}")
            return

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            boss_config = config_data.get("wow_boss_fight_system", {})
            bosses_config = boss_config.get("bosses", {})

            for boss_id, boss_data in bosses_config.items():
                # Load phases
                phases = {}
                for phase_id, phase_data in boss_data.get("phases", {}).items():
                    # Load abilities
                    abilities = []
                    for ability_data in phase_data.get("abilities", []):
                        ability = BossAbility(
                            name=ability_data["name"],
                            damage=ability_data["damage"],
                            cooldown=ability_data["cooldown"],
                            ability_type=ability_data["type"],
                            cast_bar=ability_data.get("cast_bar", False),
                            cast_time=ability_data.get("cast_time", 0.0),
                            warning=ability_data.get("warning")
                        )
                        abilities.append(ability)

                    phase = BossPhase(
                        name=phase_data["name"],
                        health_percentage_start=phase_data["health_percentage_start"],
                        health_percentage_end=phase_data["health_percentage_end"],
                        abilities=abilities,
                        enrage=phase_data.get("enrage", False),
                        enrage_damage_multiplier=phase_data.get("enrage_damage_multiplier", 1.0),
                        enrage_attack_speed_multiplier=phase_data.get("enrage_attack_speed_multiplier", 1.0),
                        cast_times=phase_data.get("cast_times", {})
                    )
                    phases[phase_id] = phase

                boss = Boss(
                    boss_name=boss_data["boss_name"],
                    boss_id=boss_id,
                    difficulty=boss_data["difficulty"],
                    max_health=boss_data["max_health"],
                    phases=phases,
                    enrage_timer=boss_data.get("enrage_timer", 600.0),
                    enrage_message=boss_data.get("enrage_message", "BOSS HAS ENRAGED!")
                )
                self.bosses[boss_id] = boss

            logger.info(f"✅ Loaded {len(self.bosses)} boss configurations")

        except Exception as e:
            logger.error(f"Error loading boss config: {e}", exc_info=True)

    def start_boss_fight(self, boss_id: str) -> bool:
        """
        Start a boss fight

        Args:
            boss_id: Boss ID to fight

        Returns:
            True if fight started successfully
        """
        if boss_id not in self.bosses:
            logger.warning(f"Boss not found: {boss_id}")
            return False

        self.current_boss = self.bosses[boss_id]
        self.boss_max_health = self.current_boss.max_health
        self.boss_health = self.boss_max_health
        self.fight_start_time = time.time()
        self.enrage_time = self.fight_start_time + self.current_boss.enrage_timer
        self.is_enraged = False
        self.ability_cooldowns = {}
        self.current_cast = None
        self.cast_start_time = None

        # Set initial phase
        self._update_phase()

        logger.info(f"⚔️  Boss Fight Started: {self.current_boss.boss_name} ({self.current_boss.difficulty})")
        logger.info(f"   Health: {self.boss_health:,.0f} / {self.boss_max_health:,.0f}")
        logger.info(f"   Phase: {self.current_phase_name}")

        return True

    def _update_phase(self):
        """Update current phase based on boss health percentage"""
        if not self.current_boss:
            return

        health_percentage = (self.boss_health / self.boss_max_health) * 100

        # Find current phase
        for phase_id, phase in self.current_boss.phases.items():
            if phase.health_percentage_start >= health_percentage >= phase.health_percentage_end:
                if self.current_phase_name != phase_id:
                    # Phase transition
                    self.current_phase_name = phase_id
                    self.current_phase = phase
                    logger.info(f"📢 PHASE TRANSITION: {phase.name}")

                    if phase.enrage:
                        self.is_enraged = True
                        logger.warning(f"⚠️  {self.current_boss.enrage_message}")
                break

    def apply_damage_to_boss(self, damage: float) -> Tuple[float, bool]:
        """
        Apply damage to boss

        Args:
            damage: Damage amount

        Returns:
            (new_health, phase_changed)
        """
        if not self.current_boss:
            return 0.0, False

        old_health_percent = (self.boss_health / self.boss_max_health) * 100

        self.boss_health = max(0.0, self.boss_health - damage)

        new_health_percent = (self.boss_health / self.boss_max_health) * 100

        # Check for phase transition
        phase_changed = False
        if int(old_health_percent) != int(new_health_percent):
            self._update_phase()
            phase_changed = True

        return self.boss_health, phase_changed

    def get_boss_attack(self) -> Optional[Dict[str, Any]]:
        """
        Get next boss attack based on current phase

        Returns:
            Attack dictionary with name, damage, cast info, or None
        """
        if not self.current_boss or not self.current_phase:
            return None

        current_time = time.time()

        # Check if currently casting
        if self.current_cast and self.cast_start_time:
            cast_duration = current_time - self.cast_start_time
            if cast_duration < self.current_cast["cast_time"]:
                # Still casting
                return {
                    "casting": True,
                    "ability": self.current_cast["name"],
                    "cast_time": self.current_cast["cast_time"],
                    "cast_progress": cast_duration / self.current_cast["cast_time"],
                    "warning": self.current_cast.get("warning")
                }
            else:
                # Cast complete, execute attack
                attack = {
                    "name": self.current_cast["name"],
                    "damage": self.current_cast["damage"],
                    "type": self.current_cast["type"],
                    "warning": self.current_cast.get("warning")
                }

                # Apply enrage multipliers
                if self.current_phase.enrage:
                    attack["damage"] *= self.current_phase.enrage_damage_multiplier

                # Clear cast
                self.current_cast = None
                self.cast_start_time = None
                self.ability_cooldowns[attack["name"]] = current_time

                return attack

        # Check for available abilities (off cooldown)
        available_abilities = []
        for ability in self.current_phase.abilities:
            last_used = self.ability_cooldowns.get(ability.name, 0.0)
            cooldown_elapsed = current_time - last_used

            # Apply enrage attack speed multiplier
            effective_cooldown = ability.cooldown
            if self.current_phase.enrage:
                effective_cooldown /= self.current_phase.enrage_attack_speed_multiplier

            if cooldown_elapsed >= effective_cooldown:
                available_abilities.append(ability)

        if not available_abilities:
            return None

        # Select random available ability (weighted towards ultimates at low health)
        if self.boss_health / self.boss_max_health < 0.25:
            # Low health: prefer ultimate abilities
            ultimate_abilities = [a for a in available_abilities if a.ability_type == "ultimate"]
            if ultimate_abilities:
                selected_ability = random.choice(ultimate_abilities)
            else:
                selected_ability = random.choice(available_abilities)
        else:
            selected_ability = random.choice(available_abilities)

        # Start cast if needed
        if selected_ability.cast_bar and selected_ability.cast_time > 0:
            self.current_cast = {
                "name": selected_ability.name,
                "damage": selected_ability.damage,
                "type": selected_ability.ability_type,
                "cast_time": selected_ability.cast_time,
                "warning": selected_ability.warning
            }
            self.cast_start_time = current_time

            return {
                "casting": True,
                "ability": selected_ability.name,
                "cast_time": selected_ability.cast_time,
                "cast_progress": 0.0,
                "warning": selected_ability.warning
            }
        else:
            # Instant cast
            attack = {
                "name": selected_ability.name,
                "damage": selected_ability.damage,
                "type": selected_ability.ability_type,
                "warning": selected_ability.warning
            }

            # Apply enrage multipliers
            if self.current_phase.enrage:
                attack["damage"] *= self.current_phase.enrage_damage_multiplier

            self.ability_cooldowns[selected_ability.name] = current_time

            return attack

    def check_enrage_timer(self) -> Tuple[bool, Optional[str]]:
        """
        Check if boss has enraged due to timer

        Returns:
            (is_enraged, warning_message)
        """
        if not self.current_boss or not self.fight_start_time:
            return False, None

        current_time = time.time()
        time_until_enrage = self.enrage_time - current_time

        if time_until_enrage <= 0 and not self.is_enraged:
            self.is_enraged = True
            logger.warning(f"⏰ {self.current_boss.enrage_message}")
            return True, self.current_boss.enrage_message

        # Warn at intervals
        if time_until_enrage > 0 and time_until_enrage <= 60:
            if int(time_until_enrage) % 10 == 0:  # Warn every 10 seconds
                return False, f"BOSS WILL ENRAGE IN {int(time_until_enrage)} SECONDS!"

        return False, None

    def is_boss_defeated(self) -> bool:
        """Check if boss is defeated"""
        return self.boss_health <= 0.0

    def get_boss_status(self) -> Dict[str, Any]:
        """Get current boss fight status"""
        if not self.current_boss:
            return {}

        health_percentage = (self.boss_health / self.boss_max_health) * 100

        return {
            "boss_name": self.current_boss.boss_name,
            "difficulty": self.current_boss.difficulty,
            "health": self.boss_health,
            "max_health": self.boss_max_health,
            "health_percentage": health_percentage,
            "phase": self.current_phase_name,
            "phase_name": self.current_phase.name if self.current_phase else None,
            "is_enraged": self.is_enraged,
            "fight_duration": time.time() - self.fight_start_time if self.fight_start_time else 0.0,
            "time_until_enrage": max(0.0, self.enrage_time - time.time()) if self.enrage_time else 0.0,
            "casting": self.current_cast is not None,
            "cast_info": self.current_cast if self.current_cast else None
        }

    def stop_boss_fight(self):
        """Stop current boss fight"""
        self.current_boss = None
        self.current_phase = None
        self.current_phase_name = None
        self.boss_health = 0.0
        self.boss_max_health = 0.0
        self.fight_start_time = None
        self.enrage_time = None
        self.is_enraged = False
        self.ability_cooldowns = {}
        self.current_cast = None
        self.cast_start_time = None

        logger.info("⚔️  Boss Fight Ended")


if __name__ == "__main__":
    # Test the manager
    manager = WoWBossFightManager()

    print("\n" + "="*80)
    print("WoW Boss Fight Manager Test")
    print("="*80 + "\n")

    # List available bosses
    print("Available Bosses:")
    for boss_id, boss in manager.bosses.items():
        print(f"  - {boss.boss_name} ({boss.difficulty}) - {boss.max_health:,.0f} HP")
        print(f"    Phases: {len(boss.phases)}")

    # Test boss fight
    print("\n" + "-"*80)
    print("Testing LFR Boss Fight:")
    print("-"*80 + "\n")

    manager.start_boss_fight("lfr_boss")
    status = manager.get_boss_status()
    print(f"Boss: {status['boss_name']} ({status['difficulty']})")
    print(f"Health: {status['health']:,.0f} / {status['max_health']:,.0f} ({status['health_percentage']:.1f}%)")
    print(f"Phase: {status['phase_name']}")

    # Simulate some attacks
    print("\nSimulating boss attacks:")
    for i in range(5):
        attack = manager.get_boss_attack()
        if attack:
            if attack.get("casting"):
                print(f"  {attack['ability']} (casting {attack['cast_time']:.1f}s)")
                if attack.get("warning"):
                    print(f"    ⚠️  {attack['warning']}")
            else:
                print(f"  {attack['name']}: {attack['damage']:,.0f} damage ({attack['type']})")
        time.sleep(0.1)

    print("\n✅ Test Complete")
