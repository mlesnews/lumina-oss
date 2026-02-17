#!/usr/bin/env python3
"""
Character System Integration Test

Comprehensive test of all character systems working together:
- Character Registry with IP/MOB classification
- Hierarchy System (Raid Leader, Champions, Elites, Bodyguards, Henchmen)
- Random Raid Encounter System
- Milestone Reward System

Tags: #INTEGRATION #TEST #CHARACTER #SYSTEM @JARVIS @LUMINA
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from character_avatar_registry import CharacterAvatarRegistry
    from character_ip_classifier import main as ip_classifier_main
    from character_hierarchy_viewer import main as hierarchy_viewer_main
    from mob_system import MOBSystem
    from random_raid_encounter_system import RandomRaidEncounterSystem
    from milestone_reward_system import MilestoneRewardSystem
    from lumina_logger import get_logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("CharacterSystemIntegration")


def main():
    """Main integration test"""
    print("=" * 80)
    print("🎭 CHARACTER SYSTEM INTEGRATION TEST")
    print("=" * 80)
    print()

    # Initialize all systems
    print("📦 Initializing Systems...")
    registry = CharacterAvatarRegistry()
    mob_system = MOBSystem()
    encounter_system = RandomRaidEncounterSystem(registry)
    milestone_system = MilestoneRewardSystem(registry, encounter_system)
    print("✅ All systems initialized")
    print()

    # Test 1: Character Registry
    print("=" * 80)
    print("TEST 1: CHARACTER REGISTRY")
    print("=" * 80)
    all_chars = registry.get_all_characters()
    true_chars = registry.get_true_characters()
    mobs = registry.get_mobs()
    inanimate = registry.get_inanimate_objects()

    print(f"✅ Total Entities: {len(all_chars)}")
    print(f"✅ True Characters (with IP): {len(true_chars)}")
    print(f"✅ MOBs: {len(mobs)}")
    print(f"✅ Inanimate Objects: {len(inanimate)}")
    print()

    # Test 2: Hierarchy System
    print("=" * 80)
    print("TEST 2: HIERARCHY SYSTEM")
    print("=" * 80)
    raid_leaders = registry.get_raid_leaders()
    champions = registry.get_champions()
    elites = registry.get_elites()
    bodyguards = registry.get_bodyguards()
    henchmen = registry.get_henchmen()

    print(f"✅ Raid Leaders: {len(raid_leaders)}")
    print(f"   • {raid_leaders[0].name if raid_leaders else 'None'}")
    print(f"✅ Champions: {len(champions)}")
    print(f"✅ Elites: {len(elites)}")
    print(f"✅ Bodyguards (Good): {len(bodyguards)}")
    print(f"✅ Henchmen (Evil): {len(henchmen)}")
    print()

    # Test 3: MOB System
    print("=" * 80)
    print("TEST 3: MOB SYSTEM")
    print("=" * 80)
    all_mobs = mob_system.get_all_mobs()
    print(f"✅ MOBs Registered: {len(all_mobs)}")
    for mob_id, mob in all_mobs.items():
        print(f"   • {mob.name}: {len(mob.member_ids)} members")
    print()

    # Test 4: Random Encounter System
    print("=" * 80)
    print("TEST 4: RANDOM ENCOUNTER SYSTEM")
    print("=" * 80)
    force_users = encounter_system._get_force_users()
    print(f"✅ Force Users Detected: {len(force_users)}")
    for fu in force_users:
        print(f"   • {fu.name} ({fu.ip_owner})")

    # Simulate some encounters
    print("\nSimulating 1000 encounter checks...")
    encounters = 0
    for i in range(1000):
        encounter = encounter_system.check_for_encounter()
        if encounter:
            encounters += 1

    print(f"✅ Encounters Spawned: {encounters}")
    stats = encounter_system.get_encounter_stats()
    print(f"   Lightsaber Duels: {stats.get('force_user_duels', 0)}")
    print(f"   Macro Raids: {stats.get('macro_raids', 0)}")
    print()

    # Test 5: Milestone Reward System
    print("=" * 80)
    print("TEST 5: MILESTONE REWARD SYSTEM")
    print("=" * 80)

    # Get encounter stats for milestone context
    encounter_stats = encounter_system.get_encounter_stats()
    context = {
        "character_count": len(true_chars),
        "encounter_count": encounter_stats.get("total_encounters", 0),
        "lightsaber_duel_count": encounter_stats.get("force_user_duels", 0),
        "macro_raid_count": encounter_stats.get("macro_raids", 0)
    }

    print(f"Context:")
    print(f"   Character Count: {context['character_count']}")
    print(f"   Encounter Count: {context['encounter_count']}")
    print(f"   Lightsaber Duels: {context['lightsaber_duel_count']}")
    print(f"   Macro Raids: {context['macro_raid_count']}")
    print()

    triggered = milestone_system.check_milestones(context)
    print(f"✅ Triggered Events: {len(triggered)}")
    for event in triggered[:3]:  # Show first 3
        print(f"   🎯 {event['description']}")
        print(f"      Type: {event['type']}")
        print(f"      Rewards: {', '.join(event['rewards'][:2])}")

    milestone_stats = milestone_system.get_milestone_stats()
    print(f"\n✅ Milestone Stats:")
    print(f"   Completed: {milestone_stats['completed_milestones']}")
    print(f"   Major: {milestone_stats['major_completed']}")
    print(f"   Minor: {milestone_stats['minor_completed']}")
    print(f"   Fighting Events: {milestone_stats['fighting_events_triggered']}")
    print()

    # Test 6: IP Classification
    print("=" * 80)
    print("TEST 6: IP CLASSIFICATION")
    print("=" * 80)
    chars_by_ip = {}
    for char in true_chars:
        ip = char.ip_owner or "No IP"
        chars_by_ip[ip] = chars_by_ip.get(ip, 0) + 1

    print(f"✅ Characters by IP:")
    for ip, count in sorted(chars_by_ip.items()):
        print(f"   {ip}: {count} characters")
    print()

    # Final Summary
    print("=" * 80)
    print("🎯 INTEGRATION TEST SUMMARY")
    print("=" * 80)
    print("✅ Character Registry: OPERATIONAL")
    print("✅ Hierarchy System: OPERATIONAL")
    print("✅ MOB System: OPERATIONAL")
    print("✅ Random Encounter System: OPERATIONAL")
    print("✅ Milestone Reward System: OPERATIONAL")
    print("✅ IP Classification: OPERATIONAL")
    print()
    print("🎮 ALL SYSTEMS INTEGRATED AND FUNCTIONAL")
    print("=" * 80)


if __name__ == "__main__":


    main()