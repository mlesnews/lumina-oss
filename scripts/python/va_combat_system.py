#!/usr/bin/env python3
"""
VA Combat System - Mortal Kombat Style
Multi-character combat system for all Virtual Assistants with Marvel/Jedi abilities

@JARVIS @TEAM @VA @ACTORS @ACTING @VOICE-ACTING @HR @COMPANY #COMBAT #MARVEL #JEDI
"""

import random
import time
import logging
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class CharacterType(Enum):
    """Character type classification"""
    MARVEL = "marvel"
    JEDI = "jedi"
    WIZARD = "wizard"
    CUSTOM = "custom"


class AbilityType(Enum):
    """Ability type classification"""
    OFFENSIVE = "offensive"
    DEFENSIVE = "defensive"
    SPECIAL = "special"
    ULTIMATE = "ultimate"


@dataclass
class Ability:
    """Combat ability definition"""
    name: str
    ability_type: AbilityType
    damage: float = 0.0
    healing: float = 0.0
    cooldown: float = 0.0
    energy_cost: float = 0.0
    description: str = ""
    voice_line: Optional[str] = None
    visual_effect: Optional[str] = None
    last_used: float = 0.0


@dataclass
class Character:
    """Combat character definition"""
    name: str
    character_type: CharacterType
    max_health: float = 100.0
    current_health: float = 100.0
    max_energy: float = 100.0
    current_energy: float = 100.0
    abilities: List[Ability] = field(default_factory=list)
    voice_actor: Optional[str] = None
    visual_style: Optional[str] = None
    team: Optional[str] = None
    level: int = 1
    experience: float = 0.0

    def use_ability(self, ability_name: str) -> Tuple[bool, Dict[str, Any]]:
        """Use an ability"""
        current_time = time.time()

        for ability in self.abilities:
            if ability.name == ability_name:
                # Check cooldown
                if current_time - ability.last_used < ability.cooldown:
                    return False, {
                        "error": "Ability on cooldown",
                        "cooldown_remaining": ability.cooldown - (current_time - ability.last_used)
                    }

                # Check energy
                if self.current_energy < ability.energy_cost:
                    return False, {
                        "error": "Insufficient energy",
                        "energy_needed": ability.energy_cost,
                        "energy_available": self.current_energy
                    }

                # Use ability
                self.current_energy -= ability.energy_cost
                ability.last_used = current_time

                return True, {
                    "ability": ability_name,
                    "damage": ability.damage,
                    "healing": ability.healing,
                    "voice_line": ability.voice_line,
                    "visual_effect": ability.visual_effect
                }

        return False, {"error": "Ability not found"}

    def take_damage(self, damage: float) -> float:
        """Take damage and return actual damage dealt"""
        actual_damage = min(damage, self.current_health)
        self.current_health = max(0.0, self.current_health - damage)
        return actual_damage

    def heal(self, amount: float) -> float:
        """Heal and return actual healing done"""
        actual_healing = min(amount, self.max_health - self.current_health)
        self.current_health = min(self.max_health, self.current_health + amount)
        return actual_healing

    def regenerate_energy(self, amount: float) -> None:
        """Regenerate energy"""
        self.current_energy = min(self.max_energy, self.current_energy + amount)

    def is_alive(self) -> bool:
        """Check if character is alive"""
        return self.current_health > 0


class CombatMode(Enum):
    """Combat mode types"""
    ONE_VS_ONE = "1v1"
    FREE_FOR_ALL = "ffa"
    TEAM_BATTLE = "team"
    TOURNAMENT = "tournament"


@dataclass
class CombatResult:
    """Combat action result"""
    success: bool
    attacker: str
    target: Optional[str] = None
    damage: float = 0.0
    healing: float = 0.0
    ability_used: Optional[str] = None
    voice_line: Optional[str] = None
    visual_effect: Optional[str] = None
    message: str = ""
    error: Optional[str] = None


class VACombatSystem:
    """
    Mortal Kombat-style combat system for Virtual Assistants

    Supports:
    - Multiple characters with unique abilities
    - Marvel superhero abilities
    - Jedi lightsaber combat
    - Voice acting
    - FFA mode
    - Team battles
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize combat system"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.characters: Dict[str, Character] = {}
        self.active_combat: Optional[Dict[str, Any]] = None
        self.combat_mode: CombatMode = CombatMode.ONE_VS_ONE
        self.combat_log: List[Dict[str, Any]] = []
        self.voice_acting_enabled: bool = True
        self.team_enhancement_enabled: bool = True

        # Initialize default characters
        self._initialize_default_characters()

    def _initialize_default_characters(self):
        """Initialize default characters with abilities"""

        # Iron Man (Marvel)
        iron_man = Character(
            name="Iron Man",
            character_type=CharacterType.MARVEL,
            max_health=120.0,
            current_health=120.0,
            max_energy=150.0,
            current_energy=150.0,
            voice_actor="Tony Stark",
            visual_style="Mark VII Armor",
            abilities=[
                Ability(
                    name="Repulsor Blast",
                    ability_type=AbilityType.OFFENSIVE,
                    damage=25.0,
                    energy_cost=15.0,
                    cooldown=2.0,
                    description="Unibeam repulsor blast",
                    voice_line="Let's light this candle!",
                    visual_effect="blue_energy_blast"
                ),
                Ability(
                    name="Arc Reactor Overload",
                    ability_type=AbilityType.ULTIMATE,
                    damage=50.0,
                    energy_cost=50.0,
                    cooldown=30.0,
                    description="Massive energy discharge",
                    voice_line="I am Iron Man!",
                    visual_effect="arc_reactor_explosion"
                ),
                Ability(
                    name="Shield Barrier",
                    ability_type=AbilityType.DEFENSIVE,
                    damage=0.0,
                    healing=20.0,
                    energy_cost=20.0,
                    cooldown=10.0,
                    description="Energy shield protection",
                    voice_line="Shields up!",
                    visual_effect="energy_shield"
                )
            ]
        )
        self.characters["iron_man"] = iron_man

        # Mace Windu (Jedi)
        mace_windu = Character(
            name="Mace Windu",
            character_type=CharacterType.JEDI,
            max_health=100.0,
            current_health=100.0,
            max_energy=120.0,
            current_energy=120.0,
            voice_actor="Samuel L. Jackson",
            visual_style="Purple Lightsaber",
            abilities=[
                Ability(
                    name="Lightsaber Strike",
                    ability_type=AbilityType.OFFENSIVE,
                    damage=20.0,
                    energy_cost=10.0,
                    cooldown=1.5,
                    description="Form VII lightsaber attack",
                    voice_line="This party's over!",
                    visual_effect="purple_lightsaber_slash"
                ),
                Ability(
                    name="Force Lightning",
                    ability_type=AbilityType.OFFENSIVE,
                    damage=30.0,
                    energy_cost=25.0,
                    cooldown=5.0,
                    description="Vaapad Force lightning",
                    voice_line="You have failed!",
                    visual_effect="purple_lightning"
                ),
                Ability(
                    name="Force Push",
                    ability_type=AbilityType.SPECIAL,
                    damage=15.0,
                    energy_cost=15.0,
                    cooldown=3.0,
                    description="Force push attack",
                    voice_line="The Force is with me!",
                    visual_effect="force_wave"
                ),
                Ability(
                    name="Shatterpoint",
                    ability_type=AbilityType.ULTIMATE,
                    damage=60.0,
                    energy_cost=40.0,
                    cooldown=45.0,
                    description="Find and exploit weakness",
                    voice_line="I have had enough!",
                    visual_effect="shatterpoint_explosion"
                )
            ]
        )
        self.characters["mace_windu"] = mace_windu

        # Gandalf (Wizard)
        gandalf = Character(
            name="Gandalf",
            character_type=CharacterType.WIZARD,
            max_health=110.0,
            current_health=110.0,
            max_energy=130.0,
            current_energy=130.0,
            voice_actor="Ian McKellen",
            visual_style="White Wizard",
            abilities=[
                Ability(
                    name="Fireball",
                    ability_type=AbilityType.OFFENSIVE,
                    damage=22.0,
                    energy_cost=18.0,
                    cooldown=2.5,
                    description="Magical fire attack",
                    voice_line="You shall not pass!",
                    visual_effect="fireball_explosion"
                ),
                Ability(
                    name="Lightning Bolt",
                    ability_type=AbilityType.OFFENSIVE,
                    damage=28.0,
                    energy_cost=22.0,
                    cooldown=4.0,
                    description="Lightning magic",
                    voice_line="Fly, you fools!",
                    visual_effect="lightning_strike"
                ),
                Ability(
                    name="Healing Light",
                    ability_type=AbilityType.DEFENSIVE,
                    damage=0.0,
                    healing=25.0,
                    energy_cost=20.0,
                    cooldown=8.0,
                    description="Restorative magic",
                    voice_line="A wizard is never late!",
                    visual_effect="healing_aura"
                ),
                Ability(
                    name="Balrog Summon",
                    ability_type=AbilityType.ULTIMATE,
                    damage=55.0,
                    energy_cost=45.0,
                    cooldown=40.0,
                    description="Summon ancient fire demon",
                    voice_line="I am a servant of the Secret Fire!",
                    visual_effect="balrog_summon"
                )
            ]
        )
        self.characters["gandalf"] = gandalf

    def add_character(self, character: Character) -> bool:
        """Add a character to the combat system"""
        key = character.name.lower().replace(" ", "_")
        if key in self.characters:
            logger.warning(f"Character {character.name} already exists")
            return False

        self.characters[key] = character
        logger.info(f"Added character: {character.name}")
        return True

    def start_combat(
        self,
        character_names: List[str],
        mode: CombatMode = CombatMode.ONE_VS_ONE
    ) -> Dict[str, Any]:
        """Start a combat session"""
        # Validate characters
        active_characters = {}
        for name in character_names:
            key = name.lower().replace(" ", "_")
            if key not in self.characters:
                return {
                    "success": False,
                    "error": f"Character {name} not found"
                }
            active_characters[key] = self.characters[key]

        # Validate mode
        if mode == CombatMode.ONE_VS_ONE and len(character_names) != 2:
            return {
                "success": False,
                "error": "1v1 mode requires exactly 2 characters"
            }

        # Initialize combat
        self.active_combat = {
            "mode": mode,
            "characters": active_characters,
            "turn": 0,
            "start_time": time.time(),
            "round": 1
        }

        self.combat_log = []
        self.combat_mode = mode

        logger.info(f"Combat started: {mode.value} with {len(character_names)} characters")

        return {
            "success": True,
            "mode": mode.value,
            "characters": [c.name for c in active_characters.values()],
            "message": f"Combat started: {mode.value}"
        }

    def execute_action(
        self,
        attacker_name: str,
        ability_name: str,
        target_name: Optional[str] = None
    ) -> CombatResult:
        """Execute a combat action"""
        if not self.active_combat:
            return CombatResult(
                success=False,
                attacker=attacker_name,
                error="No active combat"
            )

        attacker_key = attacker_name.lower().replace(" ", "_")
        if attacker_key not in self.active_combat["characters"]:
            return CombatResult(
                success=False,
                attacker=attacker_name,
                error="Attacker not in combat"
            )

        attacker = self.active_combat["characters"][attacker_key]

        if not attacker.is_alive():
            return CombatResult(
                success=False,
                attacker=attacker_name,
                error="Attacker is defeated"
            )

        # Use ability
        success, ability_result = attacker.use_ability(ability_name)
        if not success:
            return CombatResult(
                success=False,
                attacker=attacker_name,
                error=ability_result.get("error", "Unknown error")
            )

        # Apply damage/healing
        damage = 0.0
        healing = 0.0
        target = None

        if ability_result["damage"] > 0:
            # Determine target
            if self.combat_mode == CombatMode.FREE_FOR_ALL:
                # Random target (excluding self)
                available_targets = [
                    c for k, c in self.active_combat["characters"].items()
                    if k != attacker_key and c.is_alive()
                ]
                if available_targets:
                    target = random.choice(available_targets)
                else:
                    return CombatResult(
                        success=False,
                        attacker=attacker_name,
                        error="No valid targets"
                    )
            elif target_name:
                target_key = target_name.lower().replace(" ", "_")
                if target_key in self.active_combat["characters"]:
                    target = self.active_combat["characters"][target_key]
                else:
                    return CombatResult(
                        success=False,
                        attacker=attacker_name,
                        error="Target not found"
                    )
            else:
                return CombatResult(
                    success=False,
                    attacker=attacker_name,
                    error="Target required for this mode"
                )

            if target and target.is_alive():
                damage = target.take_damage(ability_result["damage"])

        if ability_result["healing"] > 0:
            healing = attacker.heal(ability_result["healing"])

        # Log combat action
        action_log = {
            "turn": self.active_combat["turn"],
            "attacker": attacker_name,
            "target": target.name if target else None,
            "ability": ability_name,
            "damage": damage,
            "healing": healing,
            "timestamp": time.time()
        }
        self.combat_log.append(action_log)
        self.active_combat["turn"] += 1

        # Regenerate energy for all characters
        for char in self.active_combat["characters"].values():
            if char.is_alive():
                char.regenerate_energy(5.0)  # 5 energy per turn

        # Check for combat end
        alive_characters = [
            c for c in self.active_combat["characters"].values() if c.is_alive()
        ]

        message = f"{attacker_name} used {ability_name}"
        if target and damage > 0:
            message += f" on {target.name} for {damage:.1f} damage"
        if healing > 0:
            message += f" and healed {healing:.1f} HP"

        return CombatResult(
            success=True,
            attacker=attacker_name,
            target=target.name if target else None,
            damage=damage,
            healing=healing,
            ability_used=ability_name,
            voice_line=ability_result.get("voice_line"),
            visual_effect=ability_result.get("visual_effect"),
            message=message
        )

    def get_combat_status(self) -> Dict[str, Any]:
        """Get current combat status"""
        if not self.active_combat:
            return {"active": False}

        characters_status = {}
        for key, char in self.active_combat["characters"].items():
            characters_status[key] = {
                "name": char.name,
                "health": char.current_health,
                "max_health": char.max_health,
                "energy": char.current_energy,
                "max_energy": char.max_energy,
                "alive": char.is_alive()
            }

        alive_count = sum(1 for c in self.active_combat["characters"].values() if c.is_alive())

        return {
            "active": True,
            "mode": self.combat_mode.value,
            "turn": self.active_combat["turn"],
            "round": self.active_combat["round"],
            "characters": characters_status,
            "alive_count": alive_count,
            "combat_duration": time.time() - self.active_combat["start_time"]
        }

    def end_combat(self) -> Dict[str, Any]:
        """End current combat"""
        if not self.active_combat:
            return {"success": False, "error": "No active combat"}

        # Determine winner(s)
        winners = [
            c.name for c in self.active_combat["characters"].values()
            if c.is_alive()
        ]

        result = {
            "success": True,
            "winners": winners,
            "duration": time.time() - self.active_combat["start_time"],
            "turns": self.active_combat["turn"],
            "log": self.combat_log
        }

        self.active_combat = None
        self.combat_log = []

        logger.info(f"Combat ended. Winners: {winners}")

        return result
