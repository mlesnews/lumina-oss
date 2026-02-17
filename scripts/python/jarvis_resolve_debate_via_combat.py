#!/usr/bin/env python3
"""
JARVIS: Resolve Debate via Combat
Use combat system to resolve disagreements and debates

@JARVIS @TEAM @va #debates #disagreements
"""

import sys
import argparse
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cfservices.services.jarvis_core.universal_va_combat_system import (
    create_combat_system,
    CombatMode
)

def main():
    """Resolve a debate via combat"""
    parser = argparse.ArgumentParser(description="Resolve debate via combat")
    parser.add_argument("topic", help="Debate topic")
    parser.add_argument("--characters", nargs="+", 
                       default=["iron_man", "mace_windu", "gandalf"],
                       help="Character templates to use")
    parser.add_argument("--mode", choices=["debate", "ffa", "1v1"],
                       default="debate",
                       help="Combat mode")

    args = parser.parse_args()

    print("=" * 70)
    print("🗣️  JARVIS: Resolve Debate via Combat")
    print("=" * 70)
    print()
    print(f"Topic: {args.topic}")
    print(f"Characters: {', '.join(args.characters)}")
    print(f"Mode: {args.mode}")
    print()

    # Create combat system
    combat = create_combat_system(project_root)

    # Create characters
    character_ids = []
    for i, char_template in enumerate(args.characters):
        char_id = f"{char_template}_{i}"
        combat.create_character_from_template(char_template, char_id)
        character_ids.append(char_id)

    # Determine mode
    mode_map = {
        "debate": CombatMode.DEBATE,
        "ffa": CombatMode.FFA,
        "1v1": CombatMode.ONE_VS_ONE
    }
    mode = mode_map[args.mode]

    # Resolve debate
    if mode == CombatMode.DEBATE:
        result = combat.resolve_debate(args.topic, character_ids)
    else:
        combat.start_combat(character_ids, mode=mode)

        # Wait for completion
        import time
        while combat.active_combat:
            time.sleep(0.5)

        winner_char = combat.characters[combat.winner] if combat.winner else None
        result = {
            "winner": winner_char.name if winner_char else None,
            "rounds": combat.round_number,
            "combat_log": combat.combat_log
        }

    # Show results
    print("=" * 70)
    print("📊 RESULTS:")
    print("=" * 70)
    print(f"  🏆 Winner: {result['winner']}")
    print(f"  ⚔️  Rounds: {result.get('rounds', 'N/A')}")
    print()

    if result.get('combat_log'):
        print("  📝 Combat Log (last 5 actions):")
        for entry in result['combat_log'][-5:]:
            print(f"    - {entry['attacker']} -> {entry['defender']}: {entry['ability']} ({entry['damage']:.1f} damage)")

    print()
    print("=" * 70)

if __name__ == "__main__":


    main()