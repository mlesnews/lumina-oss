#!/usr/bin/env python3
"""
Character IP Classifier

Classifies characters by IP ownership and distinguishes:
- Characters (must have IP)
- MOBs (groups/gangs - NOT avatars, NOT NPCs)
- Inanimate objects (static systems)

Tags: #CHARACTER #IP #MOB #CLASSIFIER @JARVIS @LUMINA
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
    from mob_system import MOBSystem
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    CharacterAvatarRegistry = None
    MOBSystem = None

logger = get_logger("CharacterIPClassifier")


def main():
    """Main entry point"""
    if not CharacterAvatarRegistry:
        logger.error("Character Avatar Registry not available")
        return

    registry = CharacterAvatarRegistry()
    mob_system = MOBSystem() if MOBSystem else None

    print("=" * 80)
    print("🎭 CHARACTER IP CLASSIFIER")
    print("=" * 80)
    print()

    # Get classifications
    true_characters = registry.get_true_characters()
    mobs = registry.get_mobs()
    inanimate = registry.get_inanimate_objects()

    print("CLASSIFICATION SUMMARY:")
    print(f"  ✅ True Characters (with IP): {len(true_characters)}")
    print(f"  👥 MOBs (groups/gangs): {len(mobs)}")
    print(f"  🔧 Inanimate Objects: {len(inanimate)}")
    print()
    print("=" * 80)
    print()

    # True Characters by IP
    print("TRUE CHARACTERS BY IP:")
    print()
    ip_groups: Dict[str, List[Any]] = {}
    for char in true_characters:
        ip = char.ip_owner or "No IP"
        if ip not in ip_groups:
            ip_groups[ip] = []
        ip_groups[ip].append(char)

    for ip, chars in sorted(ip_groups.items()):
        print(f"  {ip}: {len(chars)} characters")
        for char in chars:
            print(f"    • {char.name} ({char.character_id})")
        print()

    # MOBs
    if mobs:
        print("MOBs (NOT Avatars, NOT NPCs):")
        print()
        for mob in mobs:
            print(f"  👥 {mob.name} ({mob.character_id})")
            print(f"     Type: {mob.character_type.value}")
            print(f"     Members: {len(mob.mob_members)}")
            if mob.mob_members:
                for member_id in mob.mob_members:
                    print(f"       • {member_id}")
            print()

    # Inanimate Objects
    if inanimate:
        print("INANIMATE OBJECTS (NOT Characters):")
        print()
        for obj in inanimate:
            ip_note = f" (IP: {obj.ip_owner})" if obj.ip_owner else ""
            print(f"  🔧 {obj.name} ({obj.character_id}){ip_note}")
            print(f"     Type: {obj.character_type.value}")
            print(f"     Role: {obj.role}")
            print()

    print("=" * 80)
    print()
    print("RULES:")
    print("  1. Characters MUST have IP")
    print("  2. MOBs are NOT avatars, NOT NPCs")
    print("  3. Inanimate objects are NOT characters")
    print("  4. Systems/services are NOT characters")
    print("=" * 80)


if __name__ == "__main__":


    main()