#!/usr/bin/env python3
"""
JARVIS Combat Integration - Connect Universal Combat System to All VAs
Integrates combat system with IMVA, voice acting, and HR/team members

@JARVIS @TEAM @VA @ACTORS @VOICE-ACTING @HR @TEAM @COMPANY
#CHARACTERS #ACTING #DEBATES #DISAGREEMENTS
"""

import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cfservices.services.jarvis_core.universal_combat_system import (
    UniversalCombatSystem,
    CombatMode,
    Character,
    CharacterType,
    Ability
)

# Try to import IMVA for integration
try:
    from ironman_virtual_assistant import IRONMANVirtualAssistant
    IMVA_AVAILABLE = True
except ImportError:
    IMVA_AVAILABLE = False

# Try to import voice acting system
try:
    # Voice acting integration would go here
    VOICE_ACTING_AVAILABLE = False
except ImportError:
    VOICE_ACTING_AVAILABLE = False


class CombatIntegration:
    """Integration layer between combat system and VAs/characters"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize combat integration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.combat_system = UniversalCombatSystem(project_root)
        self.va_instances: Dict[str, Any] = {}

        # Register IMVA if available
        if IMVA_AVAILABLE:
            self._register_imva()

        logger.info("✅ Combat Integration initialized")

    def _register_imva(self):
        """Register Iron Man VA in combat system"""
        # IMVA is already registered as "iron_man" in default characters
        # But we can enhance it with live VA instance
        if "iron_man" in self.combat_system.characters:
            logger.info("✅ IMVA registered for combat")

    def register_va_character(
        self,
        va_instance: Any,
        character_id: str,
        name: str,
        abilities: Optional[List[Ability]] = None
    ) -> bool:
        """
        Register a VA instance for combat participation.

        Args:
            va_instance: VA instance (e.g., IMVA)
            character_id: Unique character ID
            name: Character name
            abilities: Optional custom abilities

        Returns:
            True if registered successfully
        """
        # Create character from VA
        character = Character(
            character_id=character_id,
            name=name,
            character_type=CharacterType.VA,
            abilities=abilities or []
        )

        # Store VA instance
        self.va_instances[character_id] = va_instance

        # Register in combat system
        self.combat_system.register_character(character)

        logger.info(f"✅ VA registered: {name} ({character_id})")
        return True

    def start_va_battle(
        self,
        va_character_ids: List[str],
        mode: CombatMode = CombatMode.ONE_VS_ONE
    ) -> Dict[str, Any]:
        """
        Start a battle between VA instances.

        Args:
            va_character_ids: List of VA character IDs
            mode: Combat mode

        Returns:
            Battle information
        """
        # Ensure all VAs are registered
        for char_id in va_character_ids:
            if char_id not in self.combat_system.characters:
                return {"error": f"VA {char_id} not registered"}

        battle = self.combat_system.start_battle(
            character_ids=va_character_ids,
            mode=mode
        )

        # Notify VA instances of battle start
        for char_id in va_character_ids:
            if char_id in self.va_instances:
                va = self.va_instances[char_id]
                if hasattr(va, 'start_lightsaber_fight'):
                    va.start_lightsaber_fight()

        return battle

    def resolve_team_debate(
        self,
        team_members: List[str],
        debate_topic: str,
        rounds: int = 5
    ) -> Dict[str, Any]:
        """
        Resolve a team debate through combat.
        Useful for @hr @team decision-making.

        Args:
            team_members: List of team member character IDs
            debate_topic: Topic of debate
            rounds: Number of combat rounds

        Returns:
            Debate resolution result
        """
        result = self.combat_system.resolve_debate(
            character_ids=team_members,
            debate_topic=debate_topic,
            rounds=rounds
        )

        logger.info(f"💬 Team debate resolved: {debate_topic}")
        logger.info(f"🏆 Winner: {result.get('winner_name', 'Unknown')}")

        return result


async def main():
    """Example usage"""
    print("=" * 70)
    print("⚔️  JARVIS Combat Integration")
    print("=" * 70)
    print()

    integration = CombatIntegration()

    # Example: Resolve a debate
    print("💬 Example: Resolving a team debate...")
    print("-" * 70)

    result = integration.resolve_team_debate(
        team_members=["iron_man", "mace_windu", "gandalf"],
        debate_topic="Should we use Python or JavaScript for the new project?",
        rounds=5
    )

    print(f"\n💬 Debate: {result['debate_topic']}")
    print(f"🏆 Winner: {result['winner_name']}")
    print("\nFinal Health:")
    for char_id, health in result["final_health"].items():
        char = integration.combat_system.characters[char_id]
        print(f"  {char.name}: {health:.1f}")

    print()
    print("=" * 70)

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


    asyncio.run(main())