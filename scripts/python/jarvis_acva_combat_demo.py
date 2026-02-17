#!/usr/bin/env python3
"""
JARVIS: ACVA Combat Demo - Lightsaber & Superhero Abilities
Demonstrates ACVA's hybrid combat capabilities

@JARVIS @TEAM @ACVA #COMBAT #LIGHTSABER #SUPERHERO
"""

import sys
import time
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cfservices.services.jarvis_core.universal_combat_system import (
    UniversalCombatSystem,
    CombatMode
)

def main():
    """Demo ACVA combat abilities"""
    print("=" * 70)
    print("⚔️  ACVA Combat Demo - Lightsaber & Superhero Abilities")
    print("=" * 70)
    print()

    combat = UniversalCombatSystem(project_root)

    # Check if ACVA exists
    if "acva" not in combat.characters:
        print("❌ ACVA not found in combat system")
        return

    acva = combat.characters["acva"]

    print("📋 ACVA Character Profile:")
    print("-" * 70)
    print(f"  Name: {acva.name}")
    print(f"  Type: {acva.character_type.value}")
    print(f"  Class: {acva.character_class}")
    print(f"  Health: {acva.stats.max_health}")
    print(f"  Attack: {acva.stats.attack_power}")
    print(f"  Defense: {acva.stats.defense}")
    print(f"  Speed: {acva.stats.speed}")
    print(f"  Special Power: {acva.stats.special_power}")
    print()

    print("⚔️  ACVA Combat Abilities:")
    print("-" * 70)
    print()

    # Group abilities by type
    lightsaber_abilities = [ab for ab in acva.abilities if "lightsaber" in ab.name.lower() or "force" in ab.name.lower() or "saber" in ab.name.lower()]
    superhero_abilities = [ab for ab in acva.abilities if ab not in lightsaber_abilities and "fusion" not in ab.name.lower() and "sync" not in ab.name.lower()]
    hybrid_abilities = [ab for ab in acva.abilities if "fusion" in ab.name.lower() or "sync" in ab.name.lower()]

    print("  🔵 Lightsaber Abilities (Jedi Style):")
    for ab in lightsaber_abilities:
        print(f"    - {ab.name}: {ab.damage} damage, {ab.cooldown}s cooldown, {ab.energy_cost} energy")
        print(f"      {ab.description}")
    print()

    print("  🦸 Superhero Abilities (Marvel Style):")
    for ab in superhero_abilities:
        print(f"    - {ab.name}: {ab.damage} damage, {ab.cooldown}s cooldown, {ab.energy_cost} energy")
        print(f"      {ab.description}")
    print()

    print("  ⚡ Hybrid Abilities (Lightsaber + Superhero):")
    for ab in hybrid_abilities:
        print(f"    - {ab.name}: {ab.damage} damage, {ab.cooldown}s cooldown, {ab.energy_cost} energy")
        print(f"      {ab.description}")
    print()

    print("=" * 70)
    print("🎮 Combat Demo: ACVA vs Iron Man")
    print("=" * 70)
    print()

    # Start 1v1 battle
    result = combat.start_combat(
        ["acva", "iron_man"],
        mode=CombatMode.ONE_VS_ONE
    )

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return

    if result.get("status") != "started":
        print(f"⚠️  Unexpected status: {result.get('status')}")
        return

    print(f"✅ Battle started!")
    print(f"   {acva.name} vs {combat.characters['iron_man'].name}")
    print()

    # Simulate combat rounds
    rounds = 0
    max_rounds = 10

    while combat.active_combat and rounds < max_rounds:
        rounds += 1

        round_result = combat.execute_combat_round()

        if round_result.get("status") == "ended":
            break

        print(f"--- Round {round_result['round']} ---")

        for action in round_result.get("actions", []):
            attacker_name = action.get("attacker", "")
            target_name = action.get("target", "")
            ability_name = action.get("ability", "")

            print(f"  {attacker_name} uses {ability_name} on {target_name}!")
            print(f"    Damage: {action.get('damage', 0):.1f}")
            print(f"    {target_name} health: {action.get('target_health', 0):.1f}")

            # Show ability type for ACVA
            if attacker_name == "ACVA (Armoury Crate VA)":
                ability = next((ab for ab in acva.abilities if ab.name == ability_name), None)
                if ability:
                    if ability in lightsaber_abilities:
                        print(f"    🔵 Lightsaber ability!")
                    elif ability in superhero_abilities:
                        print(f"    🦸 Superhero ability!")
                    elif ability in hybrid_abilities:
                        print(f"    ⚡ Hybrid ability!")
            print()

        time.sleep(0.5)

    # Show winner
    final = combat._end_combat()
    if final.get("winner"):
        winner_id = final["winner"]
        winner_name = final.get("winner_name", winner_id)
        if winner_id in combat.characters:
            winner_char = combat.characters[winner_id]
            print(f"🏆 Winner: {winner_char.name}!")
        else:
            print(f"🏆 Winner: {winner_name}!")
        print()

    print("=" * 70)
    print("✅ ACVA Combat Demo Complete!")
    print("=" * 70)
    print()
    print("💡 ACVA Features:")
    print("  ✅ Lightsaber abilities (Jedi style)")
    print("  ✅ Superhero abilities (Marvel style)")
    print("  ✅ Hybrid abilities (combines both)")
    print("  ✅ Enhanced stats (hybrid character)")
    print("=" * 70)

if __name__ == "__main__":


    main()