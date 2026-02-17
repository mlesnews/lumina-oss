#!/usr/bin/env python3
"""
JARVIS VA Combat Demo - Mortal Kombat Style
Demonstrates multi-character combat with Marvel/Jedi abilities

@JARVIS @TEAM @VA @ACTORS @ACTING @VOICE-ACTING @HR @COMPANY
"""

import sys
import time
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent))

from va_combat_system import VACombatSystem, CombatMode, Character, CharacterType, Ability, AbilityType

def main():
    """Demo the VA combat system"""
    print("=" * 70)
    print("⚔️  JARVIS VA Combat System - Mortal Kombat Style")
    print("=" * 70)
    print()

    # Initialize combat system
    combat = VACombatSystem()

    # Show available characters
    print("📋 Available Characters:")
    print("-" * 70)
    for key, char in combat.characters.items():
        print(f"  ✅ {char.name} ({char.character_type.value})")
        print(f"     Health: {char.max_health} | Energy: {char.max_energy}")
        print(f"     Abilities: {len(char.abilities)}")
        for ability in char.abilities:
            print(f"       - {ability.name}: {ability.damage} damage, {ability.cooldown}s cooldown")
        print()

    # Demo 1: 1v1 Combat (Iron Man vs Mace Windu)
    print("=" * 70)
    print("🎮 DEMO 1: 1v1 Combat - Iron Man vs Mace Windu")
    print("=" * 70)
    print()

    result = combat.start_combat(
        ["Iron Man", "Mace Windu"],
        mode=CombatMode.ONE_VS_ONE
    )

    if not result["success"]:
        print(f"❌ Failed to start combat: {result.get('error')}")
        return

    print(f"✅ {result['message']}")
    print()

    # Simulate combat turns
    turn = 0
    max_turns = 20

    while turn < max_turns:
        status = combat.get_combat_status()
        if not status["active"]:
            break

        alive_count = status["alive_count"]
        if alive_count <= 1:
            break

        turn += 1
        print(f"--- Turn {turn} ---")

        # Get alive characters
        alive_chars = [
            (k, c) for k, c in combat.active_combat["characters"].items()
            if c.is_alive()
        ]

        if len(alive_chars) < 2:
            break

        # Attacker and target
        attacker_key, attacker = alive_chars[0]
        target_key, target = alive_chars[1]

        # Choose random ability
        available_abilities = [
            a for a in attacker.abilities
            if attacker.current_energy >= a.energy_cost
        ]

        if not available_abilities:
            # Regenerate energy
            attacker.regenerate_energy(10.0)
            print(f"  {attacker.name} regenerating energy...")
            continue

        ability = available_abilities[0]

        # Execute action
        action_result = combat.execute_action(
            attacker.name,
            ability.name,
            target.name
        )

        if action_result.success:
            print(f"  {action_result.message}")
            if action_result.voice_line:
                print(f"    💬 {attacker.name}: \"{action_result.voice_line}\"")
        else:
            print(f"  ❌ {action_result.error}")

        # Show status
        for key, char in alive_chars:
            health_pct = (char.current_health / char.max_health) * 100
            print(f"    {char.name}: {char.current_health:.1f}/{char.max_health:.1f} HP ({health_pct:.0f}%) | {char.current_energy:.1f} Energy")

        print()
        time.sleep(0.5)

    # End combat
    result = combat.end_combat()
    print("=" * 70)
    print("🏁 Combat Ended")
    print("=" * 70)
    print(f"  Winners: {', '.join(result['winners'])}")
    print(f"  Duration: {result['duration']:.1f} seconds")
    print(f"  Total Turns: {result['turns']}")
    print()

    # Demo 2: FFA Mode
    print("=" * 70)
    print("🎮 DEMO 2: Free For All Mode - Iron Man vs Mace Windu vs Gandalf")
    print("=" * 70)
    print()

    result = combat.start_combat(
        ["Iron Man", "Mace Windu", "Gandalf"],
        mode=CombatMode.FREE_FOR_ALL
    )

    if not result["success"]:
        print(f"❌ Failed to start combat: {result.get('error')}")
        return

    print(f"✅ {result['message']}")
    print()

    # Simulate FFA combat
    turn = 0
    max_turns = 30

    while turn < max_turns:
        status = combat.get_combat_status()
        if not status["active"]:
            break

        alive_count = status["alive_count"]
        if alive_count <= 1:
            break

        turn += 1
        print(f"--- Turn {turn} ---")

        # Get alive characters
        alive_chars = [
            (k, c) for k, c in combat.active_combat["characters"].items()
            if c.is_alive()
        ]

        if len(alive_chars) < 2:
            break

        # Random attacker
        attacker_key, attacker = random.choice(alive_chars)

        # Choose random ability
        available_abilities = [
            a for a in attacker.abilities
            if attacker.current_energy >= a.energy_cost
        ]

        if not available_abilities:
            attacker.regenerate_energy(10.0)
            print(f"  {attacker.name} regenerating energy...")
            continue

        ability = random.choice(available_abilities)

        # Execute action (FFA mode - target chosen automatically)
        action_result = combat.execute_action(
            attacker.name,
            ability.name
        )

        if action_result.success:
            print(f"  {action_result.message}")
            if action_result.voice_line:
                print(f"    💬 {attacker.name}: \"{action_result.voice_line}\"")
        else:
            print(f"  ❌ {action_result.error}")

        # Show status
        for key, char in alive_chars:
            health_pct = (char.current_health / char.max_health) * 100
            print(f"    {char.name}: {char.current_health:.1f}/{char.max_health:.1f} HP ({health_pct:.0f}%) | {char.current_energy:.1f} Energy")

        print()
        time.sleep(0.5)

    # End combat
    result = combat.end_combat()
    print("=" * 70)
    print("🏁 FFA Combat Ended")
    print("=" * 70)
    print(f"  Winners: {', '.join(result['winners'])}")
    print(f"  Duration: {result['duration']:.1f} seconds")
    print(f"  Total Turns: {result['turns']}")
    print()

    print("=" * 70)
    print("✅ Demo Complete!")
    print("=" * 70)
    print()
    print("💡 Features:")
    print("  ✅ Multiple characters with unique abilities")
    print("  ✅ Marvel superhero abilities (Iron Man)")
    print("  ✅ Jedi lightsaber combat (Mace Windu)")
    print("  ✅ Wizard magic (Gandalf)")
    print("  ✅ 1v1 and FFA modes")
    print("  ✅ Voice acting support")
    print("  ✅ Energy and cooldown systems")
    print("=" * 70)

if __name__ == "__main__":
    import random


    main()