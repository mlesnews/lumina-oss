#!/usr/bin/env python3
"""
Character Hierarchy Viewer

Visualizes the character hierarchy structure - Bosses, Champions, Elites, Henchmen, Lackeys.

Tags: #CHARACTER #HIERARCHY #VIEWER #BOSS #CHAMPION @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, List, Any

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from character_avatar_registry import CharacterAvatarRegistry
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    CharacterAvatarRegistry = None

logger = get_logger("CharacterHierarchyViewer")


def print_hierarchy_tree(registry: CharacterAvatarRegistry, character_id: str, indent: int = 0, prefix: str = ""):
    """Print hierarchy tree starting from a character"""
    character = registry.get_character(character_id)
    if not character:
        return

    # Print character
    level_icons = {
        "raid_leader": "🎮",
        "boss": "🏆",  # Backward compatibility
        "champion": "⚔️",
        "elite": "🎯",
        "bodyguard": "🛡️",
        "henchman": "🔧",
        "lackey": "📋"
    }
    icon = level_icons.get(character.hierarchy_level, "•")

    print(f"{prefix}{icon} {character.name} ({character.hierarchy_level.upper()})")
    print(f"{prefix}   Role: {character.role}")

    # Print subordinates
    subordinates = registry.get_subordinates(character_id)
    if subordinates:
        for i, sub in enumerate(subordinates):
            is_last = i == len(subordinates) - 1
            sub_prefix = prefix + ("└── " if is_last else "├── ")
            next_prefix = prefix + ("    " if is_last else "│   ")
            print_hierarchy_tree(registry, sub.character_id, indent + 1, next_prefix)


def main():
    """Main entry point"""
    if not CharacterAvatarRegistry:
        logger.error("Character Avatar Registry not available")
        return

    registry = CharacterAvatarRegistry()

    print("=" * 80)
    print("🎭 CHARACTER HIERARCHY VIEWER")
    print("=" * 80)
    print()

    # Get all hierarchy levels
    raid_leaders = registry.get_raid_leaders()
    bosses = registry.get_bosses()  # Alias for backward compatibility
    champions = registry.get_champions()
    elites = registry.get_elites()
    bodyguards = registry.get_bodyguards()
    henchmen = registry.get_henchmen()
    lackeys = registry.get_lackeys()

    print("HIERARCHY SUMMARY:")
    print(f"  🎮 Raid Leaders: {len(raid_leaders)}")
    print(f"  ⚔️  Champions (Superheroes/Villains/Jedi/Sith): {len(champions)}")
    print(f"  🎯 Elites (Heroes/Villains): {len(elites)}")
    print(f"  🛡️  Bodyguards (Good cannon fodder/Padawan): {len(bodyguards)}")
    print(f"  🔧 Henchmen (Evil cannon fodder/Padawan): {len(henchmen)}")
    print(f"  📋 Lackeys: {len(lackeys)}")
    print()
    print("=" * 80)
    print()

    # Print hierarchy trees for all bosses
    print("FULL HIERARCHY TREES:")
    print()

    for raid_leader in raid_leaders:
        print(f"🎮 {raid_leader.name.upper()} (RAID LEADER)")
        print(f"   Role: {raid_leader.role}")
        print()
        subordinates = registry.get_subordinates(raid_leader.character_id)
        if subordinates:
            for sub in subordinates:
                print_hierarchy_tree(registry, sub.character_id, 0, "  ")
        else:
            print("  (No direct subordinates)")
        print()

    # Print independent champions
    independent_champions = [c for c in champions if not c.boss_id]
    if independent_champions:
        print("INDEPENDENT CHAMPIONS:")
        print()
        for champ in independent_champions:
            print(f"⚔️  {champ.name.upper()} (CHAMPION - Independent)")
            print(f"   Role: {champ.role}")
            print()
            subordinates = registry.get_subordinates(champ.character_id)
            for sub in subordinates:
                print_hierarchy_tree(registry, sub.character_id, 0, "  ")
            print()

    print("=" * 80)


if __name__ == "__main__":


    main()