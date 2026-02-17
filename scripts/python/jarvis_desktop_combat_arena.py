#!/usr/bin/env python3
"""
JARVIS Desktop Combat Arena - Entire PC Desktop as Battleground
LitRPG leveling, XP tracking, random monsters, strategy alliances, epic sounds

@JARVIS @TEAM @VA @ACTORS @VOICE-ACTING @HR @TEAM @COMPANY
#CHARACTERS #LITRPG #XP #LEVELING #MONSTERS #STRATEGY #SOUNDS #DESKTOP
"""

import sys
import time
import random
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cfservices.services.jarvis_core.desktop_combat_integration import DesktopCombatIntegration
from src.cfservices.services.jarvis_core.universal_combat_system import CombatMode

def print_banner():
    """Print combat arena banner"""
    print("=" * 70)
    print("⚔️  JARVIS DESKTOP COMBAT ARENA ⚔️")
    print("=" * 70)
    print()
    print("Features:")
    print("  ✅ Entire PC desktop as battleground")
    print("  ✅ LitRPG XP and leveling system")
    print("  ✅ Win/loss tracking")
    print("  ✅ Random monster spawns")
    print("  ✅ Strategy: 'Enemy of my enemy is my friend'")
    print("  ✅ Epic combat sound effects")
    print("  ✅ Dynamic resource scaling")
    print()
    print("=" * 70)
    print()

def main():
    """Main desktop combat arena"""
    print_banner()

    integration = DesktopCombatIntegration(project_root)

    # List available characters
    if integration.universal_combat:
        print("📋 Available Characters:")
        print("-" * 70)
        characters = integration.universal_combat.list_characters()
        for i, char in enumerate(characters, 1):
            print(f"  {i}. {char['name']} ({char['type']})")
            if integration.enhanced_combat:
                stats = integration.enhanced_combat.get_character_stats(char['character_id'])
                print(f"     Level: {stats['level']} | XP: {stats['xp']:.0f}/{stats['xp_to_next']:.0f} | "
                      f"Wins: {stats['wins']} | Losses: {stats['losses']}")
            print()

    print("=" * 70)
    print()
    print("🎮 Combat Modes:")
    print("  1. Desktop FFA (Free For All)")
    print("  2. Desktop 1v1")
    print("  3. Desktop Battle with Monsters")
    print("  4. Desktop Battle with Alliances")
    print("  5. View Leaderboard")
    print()

    choice = input("Select mode (1-5): ").strip()

    if choice == "1":
        # Desktop FFA
        print("\n⚔️  Desktop FFA Battle")
        print("-" * 70)
        char_ids_input = input("Character IDs (comma-separated): ").strip()
        char_ids = [cid.strip() for cid in char_ids_input.split(",")]

        battle = integration.start_desktop_battle(
            character_ids=char_ids,
            mode=CombatMode.FREE_FOR_ALL,
            enable_monsters=True,
            enable_alliances=True
        )

        if "error" in battle:
            print(f"❌ Error: {battle['error']}")
            return

        print(f"\n✅ Desktop FFA Battle started!")
        print(f"   Characters can move anywhere on desktop")
        print(f"   Random monsters will spawn")
        print(f"   Alliances can form")
        print()

        # Simulate battle
        rounds = 0
        max_rounds = 30

        while integration.active_battle and rounds < max_rounds:
            rounds += 1
            round_result = integration.execute_desktop_combat_round()

            if round_result.get("status") == "ended":
                break

            print(f"\n--- Round {round_result['round']} ---")

            # Show movements
            for movement in round_result.get("movements", []):
                char = integration.universal_combat.characters[movement["character"]]
                target = integration.universal_combat.characters.get(movement.get("target", ""))
                if target:
                    print(f"  {char.name} moves toward {target.name} (distance: {movement['distance']:.0f}px)")

            # Show actions
            for action in round_result.get("actions", []):
                char = integration.universal_combat.characters[action["attacker"]]
                target = integration.universal_combat.characters[action["target"]]
                print(f"  {char.name} → {target.name}: {action['ability']} ({action['damage']:.1f} damage)")
                if action.get("result") == "defeated":
                    print(f"  💀 {target.name} DEFEATED!")

            # Show monsters
            for monster in round_result.get("monsters", []):
                print(f"  👹 {monster['name']} at {monster['position']} (HP: {monster['health']:.1f})")

            # Show status
            status = integration.get_desktop_battle_status()
            print(f"\n  Status:")
            for char_id, char_data in status["characters"].items():
                if char_data["alive"]:
                    health_pct = (char_data["health"] / char_data["max_health"]) * 100
                    print(f"    {char_data['name']}: {char_data['health']:.1f}/{char_data['max_health']:.1f} HP "
                          f"({health_pct:.0f}%) | Level {char_data['level']} | "
                          f"Position: ({char_data['position'][0]:.0f}, {char_data['position'][1]:.0f})")

            # Show alliances
            if status.get("alliances"):
                print(f"\n  Alliances:")
                for alliance in status["alliances"]:
                    char_names = [integration.universal_combat.characters[cid].name for cid in alliance["characters"]]
                    print(f"    {', '.join(char_names)} vs {alliance.get('target', 'common enemy')}")

            time.sleep(2.0)

        # End battle
        result = integration._end_desktop_battle()
        print("\n" + "=" * 70)
        print("🏁 BATTLE ENDED")
        print("=" * 70)
        if result.get("winner"):
            winner = integration.universal_combat.characters[result["winner"]]
            print(f"🏆 Winner: {winner.name}!")

            # Show XP gained
            if integration.enhanced_combat:
                stats = integration.enhanced_combat.get_character_stats(result["winner"])
                print(f"   Level: {stats['level']} | XP: {stats['xp']:.0f}/{stats['xp_to_next']:.0f}")
                print(f"   Total Wins: {stats['wins']} | Total Losses: {stats['losses']}")
        else:
            print("💀 Draw - All characters defeated")
        print("=" * 70)

    elif choice == "5":
        # Leaderboard
        if integration.enhanced_combat:
            print("\n📊 LEADERBOARD")
            print("-" * 70)
            leaderboard = integration.enhanced_combat.get_leaderboard(limit=10)

            for i, entry in enumerate(leaderboard, 1):
                char = integration.universal_combat.characters[entry["character_id"]]
                print(f"  {i}. {char.name}")
                print(f"     Level: {entry['level']} | XP: {entry['total_xp']:.0f}")
                print(f"     Wins: {entry['wins']} | Losses: {entry['losses']} | "
                      f"Win Rate: {entry['win_rate']*100:.1f}%")
                print(f"     Kills: {entry['kills']} | Deaths: {entry['deaths']}")
                print()
        else:
            print("❌ Enhanced combat system not available")

    else:
        print("❌ Invalid option")

if __name__ == "__main__":


    main()