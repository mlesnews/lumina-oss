#!/usr/bin/env python3
"""
JARVIS Combat Arena - Universal Combat System Interface
Mortal Kombat style battles for all VAs and characters

@JARVIS @TEAM #combat #va #characters #actors #voice-acting @hr @team @company
"""

import sys
import asyncio
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cfservices.services.jarvis_core.universal_combat_system import (
    UniversalCombatSystem,
    CombatMode,
    CharacterType,
    CharacterStats,
    CombatAbility
)

def print_combat_status(combat_system: UniversalCombatSystem):
    """Print current combat status"""
    print("\n" + "=" * 70)
    print("⚔️  COMBAT STATUS")
    print("=" * 70)

    if not combat_system.active_combat:
        print("  No active combat")
        return

    print(f"  Mode: {combat_system.combat_mode.value}")
    print(f"  Round: {combat_system.round_number}")
    if combat_system.debate_topic:
        print(f"  Debate Topic: {combat_system.debate_topic}")

    print("\n  Characters:")
    for char_id, char in combat_system.characters.items():
        if char_id in [c.character_id for c in combat_system.characters.values() if c.is_alive]:
            status = combat_system.get_character_status(char_id)
            health_pct = (status["health"] / status["max_health"]) * 100
            print(f"    {char.name}: {status['health']:.1f}/{status['max_health']:.1f} HP ({health_pct:.0f}%) | "
                  f"{status['energy']:.1f}/{status['max_energy']:.1f} Energy | "
                  f"{'ALIVE' if status['is_alive'] else 'DEFEATED'}")

def print_available_characters(combat_system: UniversalCombatSystem):
    """Print available characters"""
    print("\n" + "=" * 70)
    print("👥 AVAILABLE CHARACTERS")
    print("=" * 70)

    by_type = {}
    for char_id, char in combat_system.characters.items():
        if char.character_type.value not in by_type:
            by_type[char.character_type.value] = []
        by_type[char.character_type.value].append(char)

    for char_type, chars in by_type.items():
        print(f"\n  {char_type.upper()}:")
        for char in chars:
            print(f"    - {char.name} ({char.character_id})")
            print(f"      Abilities: {', '.join([ab.name for ab in char.abilities[:3]])}...")

async def main():
    """Main combat arena interface"""
    print("=" * 70)
    print("⚔️  JARVIS COMBAT ARENA")
    print("=" * 70)
    print("Mortal Kombat style battles for all VAs and characters")
    print("Supports: Jedi, Marvel, Fantasy, Droids, FFA Mode, Debate Resolution")
    print()

    combat_system = UniversalCombatSystem(project_root)

    print_available_characters(combat_system)

    print("\n" + "=" * 70)
    print("🎮 COMBAT OPTIONS")
    print("=" * 70)
    print("1. 1v1 Battle")
    print("2. Free-For-All (FFA)")
    print("3. Team Battle")
    print("4. Debate Resolution (for disagreements)")
    print("5. Custom Battle")
    print("0. Exit")
    print()

    choice = input("Select option: ").strip()

    if choice == "1":
        # 1v1 Battle
        print("\n1v1 Battle")
        print_available_characters(combat_system)
        char1 = input("\nEnter first character ID: ").strip()
        char2 = input("Enter second character ID: ").strip()

        result = combat_system.start_combat([char1, char2], CombatMode.ONE_VS_ONE)
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return

        print(f"\n✅ Combat started: {result['participants'][0]} vs {result['participants'][1]}")

        # Run combat rounds
        while combat_system.active_combat:
            round_result = combat_system.execute_combat_round()

            if round_result.get("status") == "ended":
                print(f"\n🏆 Winner: {round_result['winner']}")
                print(f"   Rounds: {round_result['rounds']}")
                break

            print(f"\n--- Round {round_result['round']} ---")
            for action in round_result.get("actions", []):
                print(f"  {action['attacker']} uses {action['ability']} on {action['target']} "
                      f"for {action['damage']:.1f} damage")
                if action.get("result") == "defeated":
                    print(f"  💀 {action['target']} is defeated!")

            print_combat_status(combat_system)
            input("\nPress Enter to continue to next round...")

    elif choice == "2":
        # FFA Mode
        print("\nFree-For-All Mode")
        print_available_characters(combat_system)
        chars_input = input("\nEnter character IDs (comma-separated): ").strip()
        char_ids = [c.strip() for c in chars_input.split(",")]

        result = combat_system.start_combat(char_ids, CombatMode.FREE_FOR_ALL)
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return

        print(f"\n✅ FFA Combat started with {len(result['participants'])} participants")

        # Run combat rounds
        while combat_system.active_combat:
            round_result = combat_system.execute_combat_round()

            if round_result.get("status") == "ended":
                print(f"\n🏆 Winner: {round_result['winner']}")
                break

            print(f"\n--- Round {round_result['round']} ---")
            for action in round_result.get("actions", []):
                print(f"  {action['attacker']} → {action['target']}: {action['ability']} "
                      f"({action['damage']:.1f} damage)")

            print_combat_status(combat_system)
            input("\nPress Enter to continue...")

    elif choice == "4":
        # Debate Resolution
        print("\nDebate Resolution Mode")
        print("Use combat system to resolve disagreements and debates")
        print()
        topic = input("Enter debate topic: ").strip()
        print_available_characters(combat_system)
        chars_input = input("\nEnter character IDs (comma-separated): ").strip()
        char_ids = [c.strip() for c in chars_input.split(",")]

        result = combat_system.resolve_debate(topic, char_ids)

        print("\n" + "=" * 70)
        print("🏆 DEBATE RESOLUTION")
        print("=" * 70)
        print(f"Topic: {result['debate_topic']}")
        print(f"Resolution: {result['resolution']}")
        print(f"Rounds: {result['rounds']}")
        print()
        print("Combat Log:")
        for i, round_log in enumerate(result.get("combat_log", []), 1):
            print(f"\n  Round {i}:")
            for action in round_log.get("actions", []):
                print(f"    {action['attacker']}: {action.get('argument', action['ability'])}")
                if action.get("result") == "defeated":
                    print(f"      → {action['target']} is convinced!")

    else:
        print("Invalid option")

if __name__ == "__main__":

    asyncio.run(main())
"""
JARVIS Combat Arena - Mortal Kombat Style for All VAs & Characters
Interactive combat system with voice acting and debate resolution

@JARVIS @TEAM @VA @ACTORS @VOICE-ACTING @HR @TEAM @COMPANY
#CHARACTERS #ACTING #DEBATES #DISAGREEMENTS
"""

import sys
import asyncio
import random
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cfservices.services.jarvis_core.universal_combat_system import (
    UniversalCombatSystem,
    CombatMode,
    Character,
    CharacterType,
    Ability
)

def print_banner():
    """Print combat arena banner"""
    print("=" * 70)
    print("⚔️  JARVIS COMBAT ARENA - MORTAL KOMBAT STYLE ⚔️")
    print("=" * 70)
    print()
    print("Features:")
    print("  ✅ Jedi lightsaber battles")
    print("  ✅ Marvel superhero abilities")
    print("  ✅ Wizard magic")
    print("  ✅ FFA (Free For All) mode")
    print("  ✅ Debate resolution through combat")
    print("  ✅ Voice acting integration")
    print("  ✅ All @company members can participate")
    print()
    print("=" * 70)
    print()

async def main():
    """Main combat arena interface"""
    print_banner()

    combat_system = UniversalCombatSystem()

    # List available characters
    print("📋 Available Characters:")
    print("-" * 70)
    characters = combat_system.list_characters()
    for i, char in enumerate(characters, 1):
        print(f"  {i}. {char['name']} ({char['type']})")
        if char.get('lightsaber_color'):
            print(f"     Lightsaber: {char['lightsaber_color']}")
        if char.get('voice_actor'):
            print(f"     Voice: {char['voice_actor']}")
        print(f"     Abilities: {', '.join(char['abilities'])}")
        print()

    print("=" * 70)
    print()
    print("🎮 Combat Modes:")
    print("  1. 1v1 Battle")
    print("  2. Free For All (FFA)")
    print("  3. Team Battle")
    print("  4. Debate Resolution")
    print()

    mode_choice = input("Select mode (1-4): ").strip()

    if mode_choice == "1":
        # 1v1 Battle
        print("\n⚔️  1v1 Battle")
        print("-" * 70)
        char1_id = input("Character 1 ID (e.g., iron_man): ").strip()
        char2_id = input("Character 2 ID (e.g., mace_windu): ").strip()

        battle = combat_system.start_battle(
            character_ids=[char1_id, char2_id],
            mode=CombatMode.ONE_VS_ONE
        )

        if "error" in battle:
            print(f"❌ Error: {battle['error']}")
            return

        print(f"\n✅ Battle started: {battle['battle_id']}")
        print(f"   {battle['characters'][char1_id].name} vs {battle['characters'][char2_id].name}")
        print()

        # Simulate battle
        while battle["status"] == "active":
            for char_id in battle["participants"]:
                if battle["characters"][char_id].current_health <= 0:
                    continue

                char = battle["characters"][char_id]
                available_abilities = [
                    ab for ab in char.abilities
                    if char.current_energy >= ab.energy_cost
                ]

                if available_abilities:
                    ability = random.choice(available_abilities)
                    target_id = [cid for cid in battle["participants"] if cid != char_id][0]

                    result = combat_system.execute_ability(
                        battle["battle_id"],
                        char_id,
                        ability.name,
                        target_id
                    )

                    if result.get("success"):
                        action = result["action"]
                        print(f"  {char.name} uses {ability.name}!")
                        if ability.voice_line:
                            print(f"    \"{ability.voice_line}\"")
                        print(f"    Damage: {action['damage']}")
                        print(f"    {battle['characters'][target_id].name} health: {action['target_health']:.1f}")
                        print()

                if battle["status"] == "completed":
                    break

        winner = battle["characters"][battle["winner"]]
        print(f"🏆 Winner: {winner.name}!")
        print()

    elif mode_choice == "2":
        # FFA Mode
        print("\n⚔️  Free For All Mode")
        print("-" * 70)
        char_ids_input = input("Character IDs (comma-separated, e.g., iron_man,mace_windu,gandalf): ").strip()
        char_ids = [cid.strip() for cid in char_ids_input.split(",")]

        battle = combat_system.start_battle(
            character_ids=char_ids,
            mode=CombatMode.FREE_FOR_ALL
        )

        if "error" in battle:
            print(f"❌ Error: {battle['error']}")
            return

        print(f"\n✅ FFA Battle started: {battle['battle_id']}")
        print(f"   Participants: {', '.join([battle['characters'][cid].name for cid in char_ids])}")
        print()

        # Simulate FFA
        import random
        rounds = 0
        while battle["status"] == "active" and rounds < 20:
            rounds += 1
            battle["round"] = rounds

            for char_id in battle["participants"]:
                if battle["characters"][char_id].current_health <= 0:
                    continue

                char = battle["characters"][char_id]
                available_abilities = [
                    ab for ab in char.abilities
                    if char.current_energy >= ab.energy_cost
                ]

                if available_abilities:
                    ability = random.choice(available_abilities)
                    opponents = [cid for cid in battle["participants"] if cid != char_id and battle["characters"][cid].current_health > 0]
                    if opponents:
                        target_id = random.choice(opponents)

                        result = combat_system.execute_ability(
                            battle["battle_id"],
                            char_id,
                            ability.name,
                            target_id
                        )

                        if result.get("success"):
                            action = result["action"]
                            print(f"  Round {rounds}: {char.name} → {battle['characters'][target_id].name}")
                            print(f"    {ability.name}: {action['damage']} damage")
                            if ability.voice_line:
                                print(f"    \"{ability.voice_line}\"")
                            print()

                if battle["status"] == "completed":
                    break

        winner = battle["characters"][battle["winner"]]
        print(f"🏆 FFA Winner: {winner.name}!")
        print()

    elif mode_choice == "4":
        # Debate Resolution
        print("\n💬 Debate Resolution Mode")
        print("-" * 70)
        debate_topic = input("Debate topic: ").strip()
        char_ids_input = input("Character IDs (comma-separated): ").strip()
        char_ids = [cid.strip() for cid in char_ids_input.split(",")]

        result = combat_system.resolve_debate(
            character_ids=char_ids,
            debate_topic=debate_topic,
            rounds=5
        )

        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return

        print(f"\n💬 Debate: {debate_topic}")
        print(f"🏆 Winner: {result['winner_name']}")
        print()
        print("Final Health:")
        for char_id, health in result["final_health"].items():
            char = combat_system.characters[char_id]
            print(f"  {char.name}: {health:.1f}")
        print()

    else:
        print("❌ Invalid mode selection")
        return

    print("=" * 70)
    print("✅ Combat session complete!")
    print("=" * 70)

if __name__ == "__main__":


    asyncio.run(main())