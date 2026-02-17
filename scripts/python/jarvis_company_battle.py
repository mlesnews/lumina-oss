#!/usr/bin/env python3
"""
JARVIS: Company Battle
Start company-wide battles with @hr @team members

@JARVIS @TEAM @hr @team @va
"""

import sys
import argparse
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cfservices.services.jarvis_core.va_combat_hr_integration import create_hr_combat_integration

def main():
    """Start company battle"""
    parser = argparse.ArgumentParser(description="Company-wide battle")
    parser.add_argument("--members", nargs="+", required=True,
                       help="Team member names")
    parser.add_argument("--mode", choices=["ffa", "debate", "team"],
                       default="ffa",
                       help="Combat mode")
    parser.add_argument("--topic", help="Debate topic (for debate mode)")

    args = parser.parse_args()

    print("=" * 70)
    print("⚔️  JARVIS: Company Battle")
    print("=" * 70)
    print()

    # Create HR integration
    hr_combat = create_hr_combat_integration(project_root)

    # Start battle
    if args.mode == "debate" and args.topic:
        print(f"🗣️  Resolving debate: '{args.topic}'")
        print(f"   Participants: {', '.join(args.members)}")
        print()
        result = hr_combat.resolve_team_disagreement(args.topic, args.members)
    else:
        print(f"⚔️  Starting {args.mode.upper()} battle")
        print(f"   Participants: {', '.join(args.members)}")
        print()
        result = hr_combat.start_company_battle(args.members, mode=args.mode)

    # Show results
    print("=" * 70)
    print("📊 RESULTS:")
    print("=" * 70)
    print(f"  🏆 Winner: {result.get('winner', 'No winner')}")
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