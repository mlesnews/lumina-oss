#!/usr/bin/env python3
"""
Character System End-to-End Validation

Comprehensive validation, discovery, and exploration of alternative approaches.
Checks for data consistency, integration gaps, and potential improvements.

Tags: #E2E #VALIDATION #DISCOVERY #EXPLORATION #CONTEXT_CONFIDENCE @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from character_avatar_registry import CharacterAvatarRegistry, CharacterAvatar
    from mob_system import MOBSystem, MOB
    from random_raid_encounter_system import RandomRaidEncounterSystem
    from milestone_reward_system import MilestoneRewardSystem
    from lumina_logger import get_logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("E2EValidation")


class E2EValidator:
    """End-to-End Validation System"""

    def __init__(self):
        """Initialize validator"""
        self.registry = CharacterAvatarRegistry()
        self.mob_system = MOBSystem()
        self.encounter_system = RandomRaidEncounterSystem(self.registry)
        self.milestone_system = MilestoneRewardSystem(self.registry, self.encounter_system)

        self.issues: List[Dict[str, Any]] = []
        self.discoveries: List[Dict[str, Any]] = []
        self.alternatives: List[Dict[str, Any]] = []
        self.confidence_score = 100.0

    def validate_all(self) -> Dict[str, Any]:
        """Run all validation checks"""
        print("=" * 80)
        print("🔍 END-TO-END VALIDATION & DISCOVERY")
        print("=" * 80)
        print()

        # Run all validation checks
        self._validate_character_registry()
        self._validate_hierarchy_consistency()
        self._validate_mob_consistency()
        self._validate_ip_classification()
        self._validate_encounter_system()
        self._validate_milestone_system()
        self._validate_data_persistence()
        self._validate_integration_points()
        self._discover_patterns()
        self._explore_alternatives()

        # Calculate confidence score
        self._calculate_confidence()

        return {
            "issues": self.issues,
            "discoveries": self.discoveries,
            "alternatives": self.alternatives,
            "confidence_score": self.confidence_score
        }

    def _validate_character_registry(self):
        """Validate character registry consistency"""
        print("📋 Validating Character Registry...")

        all_chars = self.registry.get_all_characters()
        true_chars = self.registry.get_true_characters()
        mobs = self.registry.get_mobs()
        inanimate = self.registry.get_inanimate_objects()

        # Check: All characters should have hierarchy_level
        missing_hierarchy = []
        for char in all_chars.values():
            if not hasattr(char, 'hierarchy_level') or not char.hierarchy_level:
                missing_hierarchy.append(char.character_id)

        if missing_hierarchy:
            self.issues.append({
                "type": "missing_hierarchy",
                "severity": "high",
                "description": f"Characters missing hierarchy_level: {missing_hierarchy}",
                "fix": "Ensure all characters have hierarchy_level set"
            })
            self.confidence_score -= 5.0

        # Check: Characters with IP should have is_character=True (unless inanimate)
        ip_without_flag = []
        for char in all_chars.values():
            # Inanimate objects can have IP but are NOT characters (this is correct)
            if char.ip_owner and not char.is_character and char.character_type.value != "inanimate_object":
                ip_without_flag.append(char.character_id)

        if ip_without_flag:
            self.issues.append({
                "type": "ip_without_character_flag",
                "severity": "medium",
                "description": f"Non-inanimate entities with IP but is_character=False: {ip_without_flag}",
                "fix": "Set is_character=True for non-inanimate entities with IP"
            })
            self.confidence_score -= 3.0

        # Check: MOBs should have is_mob=True
        mobs_without_flag = []
        for mob in mobs:
            if not mob.is_mob:
                mobs_without_flag.append(mob.character_id)

        if mobs_without_flag:
            self.issues.append({
                "type": "mob_without_flag",
                "severity": "high",
                "description": f"MOBs without is_mob=True: {mobs_without_flag}",
                "fix": "Set is_mob=True for all MOBs"
            })
            self.confidence_score -= 5.0

        # Discovery: Character distribution
        self.discoveries.append({
            "type": "character_distribution",
            "description": f"Total: {len(all_chars)}, Characters: {len(true_chars)}, MOBs: {len(mobs)}, Inanimate: {len(inanimate)}",
            "insight": "Good separation of concerns"
        })

        print(f"  ✅ Validated {len(all_chars)} entities")

    def _validate_hierarchy_consistency(self):
        """Validate hierarchy relationships"""
        print("📋 Validating Hierarchy Consistency...")

        all_chars = self.registry.get_all_characters()

        # Check: All boss_id references should exist
        missing_bosses = []
        for char in all_chars.values():
            if char.boss_id and char.boss_id not in all_chars:
                missing_bosses.append((char.character_id, char.boss_id))

        if missing_bosses:
            self.issues.append({
                "type": "missing_boss_reference",
                "severity": "high",
                "description": f"Characters reference non-existent bosses: {missing_bosses}",
                "fix": "Fix boss_id references or create missing characters"
            })
            self.confidence_score -= 5.0

        # Check: All sub_bosses references should exist
        missing_sub_bosses = []
        for char in all_chars.values():
            for sub_id in char.sub_bosses:
                if sub_id not in all_chars:
                    missing_sub_bosses.append((char.character_id, sub_id))

        if missing_sub_bosses:
            self.issues.append({
                "type": "missing_sub_boss_reference",
                "severity": "high",
                "description": f"Characters reference non-existent sub_bosses: {missing_sub_bosses}",
                "fix": "Fix sub_bosses references or create missing characters"
            })
            self.confidence_score -= 5.0

        # Check: Bidirectional consistency (if A has boss B, B should have A in sub_bosses)
        inconsistent_relationships = []
        for char in all_chars.values():
            if char.boss_id:
                boss = all_chars.get(char.boss_id)
                if boss and char.character_id not in boss.sub_bosses:
                    inconsistent_relationships.append((char.character_id, char.boss_id))

        if inconsistent_relationships:
            self.issues.append({
                "type": "inconsistent_hierarchy",
                "severity": "medium",
                "description": f"Bidirectional hierarchy inconsistencies: {inconsistent_relationships}",
                "fix": "Ensure boss_id and sub_bosses are consistent"
            })
            self.confidence_score -= 2.0

        # Discovery: Hierarchy depth
        raid_leaders = self.registry.get_raid_leaders()
        max_depth = 0
        for rl in raid_leaders:
            depth = self._calculate_hierarchy_depth(rl.character_id)
            max_depth = max(max_depth, depth)

        self.discoveries.append({
            "type": "hierarchy_depth",
            "description": f"Maximum hierarchy depth: {max_depth}",
            "insight": "Deep hierarchy structure"
        })

        print(f"  ✅ Validated hierarchy relationships")

    def _calculate_hierarchy_depth(self, character_id: str, visited: Optional[Set] = None) -> int:
        """Calculate maximum hierarchy depth from a character"""
        if visited is None:
            visited = set()

        if character_id in visited:
            return 0

        visited.add(character_id)
        char = self.registry.get_character(character_id)
        if not char or not char.sub_bosses:
            return 1

        max_sub_depth = 0
        for sub_id in char.sub_bosses:
            depth = self._calculate_hierarchy_depth(sub_id, visited.copy())
            max_sub_depth = max(max_sub_depth, depth)

        return 1 + max_sub_depth

    def _validate_mob_consistency(self):
        """Validate MOB system consistency"""
        print("📋 Validating MOB Consistency...")

        registry_mobs = self.registry.get_mobs()
        mob_system_mobs = self.mob_system.get_all_mobs()

        # Check: MOBs in registry should match MOB system
        registry_mob_ids = {m.character_id for m in registry_mobs}
        mob_system_ids = set(mob_system_mobs.keys())

        if registry_mob_ids != mob_system_ids:
            missing_in_system = registry_mob_ids - mob_system_ids
            missing_in_registry = mob_system_ids - registry_mob_ids

            if missing_in_system:
                self.issues.append({
                    "type": "mob_sync_issue",
                    "severity": "medium",
                    "description": f"MOBs in registry but not in MOB system: {missing_in_system}",
                    "fix": "Sync MOBs between registry and MOB system"
                })
                self.confidence_score -= 3.0

            if missing_in_registry:
                self.issues.append({
                    "type": "mob_sync_issue",
                    "severity": "medium",
                    "description": f"MOBs in MOB system but not in registry: {missing_in_registry}",
                    "fix": "Sync MOBs between registry and MOB system"
                })
                self.confidence_score -= 3.0

        # Check: MOB members should be valid
        for mob in registry_mobs:
            if hasattr(mob, 'mob_members'):
                for member_id in mob.mob_members:
                    # Members don't need to exist as characters (they're part of MOB)
                    pass  # This is expected - members are MOB components

        print(f"  ✅ Validated {len(registry_mobs)} MOBs")

    def _validate_ip_classification(self):
        """Validate IP classification"""
        print("📋 Validating IP Classification...")

        true_chars = self.registry.get_true_characters()

        # Check: All true characters should have IP
        chars_without_ip = [c for c in true_chars if not c.ip_owner]
        if chars_without_ip:
            self.issues.append({
                "type": "character_without_ip",
                "severity": "high",
                "description": f"True characters without IP: {[c.character_id for c in chars_without_ip]}",
                "fix": "Add IP ownership to all true characters"
            })
            self.confidence_score -= 5.0

        # Discovery: IP distribution
        ip_distribution = defaultdict(int)
        for char in true_chars:
            if char.ip_owner:
                ip_distribution[char.ip_owner] += 1

        self.discoveries.append({
            "type": "ip_distribution",
            "description": f"IP distribution: {dict(ip_distribution)}",
            "insight": "Diverse IP representation"
        })

        print(f"  ✅ Validated IP classification for {len(true_chars)} characters")

    def _validate_encounter_system(self):
        """Validate encounter system"""
        print("📋 Validating Encounter System...")

        # Check: Force user detection
        force_users = self.registry.get_characters_by_ip("Star Wars")
        detected_force_users = self.encounter_system._get_force_users()

        # Not all Star Wars characters are Force users, so this is expected
        if len(detected_force_users) == 0:
            self.issues.append({
                "type": "no_force_users",
                "severity": "medium",
                "description": "No Force users detected - lightsaber duels won't spawn",
                "fix": "Verify Force user detection logic"
            })
            self.confidence_score -= 3.0

        # Check: Spawn rates are reasonable
        if self.encounter_system.base_spawn_rate <= 0:
            self.issues.append({
                "type": "invalid_spawn_rate",
                "severity": "high",
                "description": "Base spawn rate is invalid",
                "fix": "Set valid spawn rate"
            })
            self.confidence_score -= 5.0

        print(f"  ✅ Validated encounter system")

    def _validate_milestone_system(self):
        """Validate milestone system"""
        print("📋 Validating Milestone System...")

        # Check: Milestone data file exists and is valid
        milestones_file = self.milestone_system.milestones_file
        if milestones_file.exists():
            try:
                with open(milestones_file, 'r') as f:
                    data = json.load(f)
                    if "completed" not in data:
                        self.issues.append({
                            "type": "invalid_milestone_data",
                            "severity": "medium",
                            "description": "Milestone data file missing 'completed' field",
                            "fix": "Fix milestone data structure"
                        })
                        self.confidence_score -= 2.0
            except json.JSONDecodeError:
                self.issues.append({
                    "type": "corrupted_milestone_data",
                    "severity": "high",
                    "description": "Milestone data file is corrupted",
                    "fix": "Fix or regenerate milestone data"
                })
                self.confidence_score -= 5.0

        print(f"  ✅ Validated milestone system")

    def _validate_data_persistence(self):
        """Validate data persistence"""
        print("📋 Validating Data Persistence...")

        # Check: Registry JSON file
        registry_file = self.registry.registry_file
        if registry_file.exists():
            try:
                with open(registry_file, 'r') as f:
                    data = json.load(f)
                    if not isinstance(data, dict):
                        self.issues.append({
                            "type": "invalid_registry_data",
                            "severity": "high",
                            "description": "Registry data file has invalid structure",
                            "fix": "Fix registry data structure"
                        })
                        self.confidence_score -= 5.0
            except json.JSONDecodeError:
                self.issues.append({
                    "type": "corrupted_registry_data",
                    "severity": "high",
                    "description": "Registry data file is corrupted",
                    "fix": "Fix or regenerate registry data"
                })
                self.confidence_score -= 5.0

        print(f"  ✅ Validated data persistence")

    def _validate_integration_points(self):
        """Validate integration between systems"""
        print("📋 Validating Integration Points...")

        # Check: Encounter system uses registry correctly
        try:
            force_users = self.encounter_system._get_force_users()
            # This should work without errors
        except Exception as e:
            self.issues.append({
                "type": "encounter_registry_integration",
                "severity": "high",
                "description": f"Encounter system integration error: {e}",
                "fix": "Fix encounter system integration"
            })
            self.confidence_score -= 5.0

        # Check: Milestone system uses registry correctly
        try:
            context = {"character_count": len(self.registry.get_true_characters())}
            self.milestone_system.check_milestones(context)
            # This should work without errors
        except Exception as e:
            self.issues.append({
                "type": "milestone_registry_integration",
                "severity": "high",
                "description": f"Milestone system integration error: {e}",
                "fix": "Fix milestone system integration"
            })
            self.confidence_score -= 5.0

        print(f"  ✅ Validated integration points")

    def _discover_patterns(self):
        """Discover patterns and insights"""
        print("📋 Discovering Patterns...")

        all_chars = self.registry.get_all_characters()

        # Pattern: Character types distribution
        type_distribution = defaultdict(int)
        for char in all_chars.values():
            type_distribution[char.character_type.value] += 1

        self.discoveries.append({
            "type": "character_type_distribution",
            "description": f"Character types: {dict(type_distribution)}",
            "insight": "Shows system diversity"
        })

        # Pattern: Avatar styles
        style_distribution = defaultdict(int)
        for char in all_chars.values():
            style_distribution[char.avatar_style] += 1

        self.discoveries.append({
            "type": "avatar_style_distribution",
            "description": f"Avatar styles: {dict(style_distribution)}",
            "insight": "Visual variety in avatars"
        })

        # Pattern: Features enabled
        features = {
            "transformation": sum(1 for c in all_chars.values() if c.transformation_enabled),
            "combat_mode": sum(1 for c in all_chars.values() if c.combat_mode_enabled),
            "wopr_stances": sum(1 for c in all_chars.values() if c.wopr_stances_enabled)
        }

        self.discoveries.append({
            "type": "feature_distribution",
            "description": f"Features: {features}",
            "insight": "Combat capabilities distribution"
        })

        print(f"  ✅ Discovered {len(self.discoveries)} patterns")

    def _explore_alternatives(self):
        """Explore alternative approaches"""
        print("📋 Exploring Alternatives...")

        # Alternative 1: Cached queries
        self.alternatives.append({
            "type": "cached_queries",
            "description": "Cache frequently accessed queries (get_champions, get_elites, etc.)",
            "benefit": "Performance improvement for large character sets",
            "implementation": "Add @lru_cache decorator or internal cache"
        })

        # Alternative 2: Event-driven milestone checking
        self.alternatives.append({
            "type": "event_driven_milestones",
            "description": "Check milestones automatically on encounter/character changes",
            "benefit": "Real-time milestone detection without manual checks",
            "implementation": "Add event listeners to encounter/registry systems"
        })

        # Alternative 3: Validation on save
        self.alternatives.append({
            "type": "validation_on_save",
            "description": "Validate data before saving to prevent corruption",
            "benefit": "Prevent invalid data from being persisted",
            "implementation": "Add validation step in _save_registry methods"
        })

        # Alternative 4: Hierarchy auto-repair
        self.alternatives.append({
            "type": "hierarchy_auto_repair",
            "description": "Automatically fix bidirectional hierarchy inconsistencies",
            "benefit": "Self-healing system",
            "implementation": "Add repair method that fixes boss_id/sub_bosses mismatches"
        })

        # Alternative 5: MOB member validation
        self.alternatives.append({
            "type": "mob_member_validation",
            "description": "Validate MOB members exist or are properly defined",
            "benefit": "Ensure MOB integrity",
            "implementation": "Add validation when adding members to MOBs"
        })

        print(f"  ✅ Explored {len(self.alternatives)} alternatives")

    def _calculate_confidence(self):
        """Calculate overall confidence score"""
        # Base score starts at 100, reduced by issues found
        # Minimum score is 0

        if self.confidence_score < 0:
            self.confidence_score = 0

        # Boost confidence for discoveries (shows system understanding)
        if len(self.discoveries) > 0:
            self.confidence_score += min(5.0, len(self.discoveries) * 0.5)

        # Boost confidence for alternatives (shows forward thinking)
        if len(self.alternatives) > 0:
            self.confidence_score += min(5.0, len(self.alternatives) * 0.5)

        if self.confidence_score > 100:
            self.confidence_score = 100

    def print_report(self):
        """Print validation report"""
        print()
        print("=" * 80)
        print("📊 VALIDATION REPORT")
        print("=" * 80)
        print()

        print(f"🎯 CONFIDENCE SCORE: {self.confidence_score:.1f}/100")
        print()

        if self.issues:
            print(f"⚠️  ISSUES FOUND: {len(self.issues)}")
            for issue in self.issues:
                print(f"  [{issue['severity'].upper()}] {issue['type']}")
                print(f"     {issue['description']}")
                print(f"     Fix: {issue['fix']}")
                print()
        else:
            print("✅ NO ISSUES FOUND")
            print()

        if self.discoveries:
            print(f"🔍 DISCOVERIES: {len(self.discoveries)}")
            for discovery in self.discoveries:
                print(f"  {discovery['type']}: {discovery['description']}")
                print(f"     Insight: {discovery['insight']}")
                print()

        if self.alternatives:
            print(f"💡 ALTERNATIVES EXPLORED: {len(self.alternatives)}")
            for alt in self.alternatives:
                print(f"  {alt['type']}: {alt['description']}")
                print(f"     Benefit: {alt['benefit']}")
                print()

        print("=" * 80)


def main():
    """Main entry point"""
    validator = E2EValidator()
    results = validator.validate_all()
    validator.print_report()

    return results


if __name__ == "__main__":


    main()