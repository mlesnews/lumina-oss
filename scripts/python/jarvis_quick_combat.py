#!/usr/bin/env python3
"""
JARVIS Quick Combat - Fast battle examples
Quick examples of famous matchups

@JARVIS @TEAM #combat #va #characters
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cfservices.services.jarvis_core.universal_combat_system import (
    UniversalCombatSystem,
    CombatMode
)

def quick_battle(char1_id: str, char2_id: str, rounds: int = 5):
    """Quick 1v1 battle"""
    combat = UniversalCombatSystem(project_root)

    print(f"\n⚔️  {combat.characters[char1_id].name} vs {combat.characters[char2_id].name}")
    print("=" * 70)

    result = combat.start_combat([char1_id, char2_id], CombatMode.ONE_VS_ONE)

    for _ in range(rounds):
        round_result = combat.execute_combat_round()

        if round_result.get("status") == "ended":
            break

        print(f"\nRound {round_result['round']}:")
        for action in round_result.get("actions", []):
            print(f"  {action['attacker']} → {action['target']}: {action['ability']} "
                  f"({action['damage']:.1f} damage)")
            if action.get("result") == "defeated":
                print(f"  💀 {action['target']} DEFEATED!")

    final = combat._end_combat()
    print(f"\n🏆 Winner: {final['winner']}")
    print(f"   Rounds: {final['rounds']}")

def main():
    """Run quick combat examples"""
    print("=" * 70)
    print("⚔️  JARVIS QUICK COMBAT - Famous Matchups")
    print("=" * 70)

    # Example 1: Iron Man vs Mace Windu
    print("\n1. Iron Man vs Mace Windu")
    quick_battle("iron_man", "mace_windu")

    # Example 2: Gandalf vs Saruman
    print("\n2. Gandalf vs Saruman")
    quick_battle("gandalf", "saruman")

    # Example 3: FFA - All Jedi
    print("\n3. Jedi Free-For-All")
    combat = UniversalCombatSystem(project_root)
    result = combat.start_combat(["mace_windu", "anakin", "yoda"], CombatMode.FREE_FOR_ALL)

    for _ in range(10):
        round_result = combat.execute_combat_round()
        if round_result.get("status") == "ended":
            break

    final = combat._end_combat()
    print(f"\n🏆 FFA Winner: {final['winner']}")

    # Example 4: Debate Resolution
    print("\n4. Debate Resolution Example")
    combat2 = UniversalCombatSystem(project_root)
    debate_result = combat2.resolve_debate(
        "Should we use Python or JavaScript for this project?",
        ["iron_man", "mace_windu", "gandalf"]
    )

    print(f"\n🏆 Debate Winner: {debate_result['winner']}")
    print(f"   Topic: {debate_result['debate_topic']}")
    print(f"   Resolution: {debate_result['resolution']}")

if __name__ == "__main__":


    main()