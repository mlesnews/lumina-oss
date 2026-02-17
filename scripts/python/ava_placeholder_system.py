#!/usr/bin/env python3
"""
AVA (Any Virtual Assistant) Placeholder System

Manages placeholder VAs for concurrent battles and multiple encounters.
AVA can be instantiated multiple times for different battle instances.

Tags: #AVA #PLACEHOLDER #CONCURRENT_BATTLES #VIRTUAL_ASSISTANT @JARVIS @LUMINA
"""

import sys
import random
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from character_avatar_registry import CharacterAvatarRegistry, CharacterAvatar, CharacterType
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    CharacterAvatarRegistry = None
    CharacterAvatar = None
    CharacterType = None

logger = get_logger("AVAPlaceholder")


class AVAInstanceType(Enum):
    """Types of AVA instances"""
    BATTLE_INSTANCE = "battle_instance"  # For concurrent battles
    ENCOUNTER_INSTANCE = "encounter_instance"  # For random encounters
    MILESTONE_EVENT = "milestone_event"  # For milestone rewards
    BACKUP_VA = "backup_va"  # Backup VA when primary is busy


class AVAPlaceholderSystem:
    """
    AVA (Any Virtual Assistant) Placeholder System

    Manages placeholder VAs for multiple concurrent battles and encounters.
    """

    def __init__(self, registry: Optional[CharacterAvatarRegistry] = None):
        """Initialize AVA placeholder system"""
        if registry is None:
            if CharacterAvatarRegistry:
                registry = CharacterAvatarRegistry()
            else:
                raise ValueError("CharacterAvatarRegistry not available")

        self.registry = registry

        # AVA base template
        self.ava_base = self.registry.get_character("ava")
        if not self.ava_base:
            logger.warning("AVA base character not found in registry")

        # Active AVA instances
        self.active_instances: Dict[str, Dict[str, Any]] = {}
        self.instance_counter = 0

        logger.info("=" * 80)
        logger.info("🤖 AVA PLACEHOLDER SYSTEM")
        logger.info("=" * 80)
        logger.info("   Ready for concurrent battle instances")
        logger.info("=" * 80)

    def create_ava_instance(self, instance_type: AVAInstanceType, 
                           battle_id: Optional[str] = None,
                           custom_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new AVA instance for a battle/encounter

        Returns instance configuration
        """
        self.instance_counter += 1
        instance_id = f"ava_{self.instance_counter}_{battle_id or 'battle'}"

        # Generate instance name
        if custom_name:
            instance_name = custom_name
        else:
            instance_name = f"AVA-{self.instance_counter}"

        instance = {
            "instance_id": instance_id,
            "name": instance_name,
            "type": instance_type.value,
            "battle_id": battle_id,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "base_character_id": "ava",
            "customizations": {
                "primary_color": self._generate_color(),
                "secondary_color": self._generate_color(),
                "avatar_style": self._select_avatar_style(),
                "catchphrase": self._generate_catchphrase(instance_type)
            }
        }

        self.active_instances[instance_id] = instance

        logger.info(f"🤖 Created AVA instance: {instance_name} ({instance_id}) for {instance_type.value}")
        return instance

    def _generate_color(self) -> str:
        """Generate a random color for AVA instance"""
        colors = [
            "#888888", "#aaaaaa", "#cccccc", "#666666",
            "#ff6600", "#00ccff", "#ffcc00", "#cc00ff",
            "#00ff88", "#ff3366", "#3366ff", "#ff9933"
        ]
        return random.choice(colors)

    def _select_avatar_style(self) -> str:
        """Select avatar style for AVA instance"""
        styles = [
            "generic", "bobblehead", "widget", "ace_humanoid",
            "iron_man", "system", "ai"
        ]
        return random.choice(styles)

    def _generate_catchphrase(self, instance_type: AVAInstanceType) -> str:
        """Generate catchphrase based on instance type"""
        catchphrases = {
            AVAInstanceType.BATTLE_INSTANCE: [
                "AVA ready for battle.",
                "AVA combat protocols engaged.",
                "AVA standing by for combat assignment."
            ],
            AVAInstanceType.ENCOUNTER_INSTANCE: [
                "AVA monitoring encounter.",
                "AVA ready for random encounter.",
                "AVA encounter protocols active."
            ],
            AVAInstanceType.MILESTONE_EVENT: [
                "AVA milestone event support active.",
                "AVA ready for milestone reward.",
                "AVA event protocols engaged."
            ],
            AVAInstanceType.BACKUP_VA: [
                "AVA backup mode activated.",
                "AVA standing by as backup.",
                "AVA backup protocols ready."
            ]
        }
        return random.choice(catchphrases.get(instance_type, ["AVA ready."]))

    def get_ava_for_battle(self, battle_id: str) -> Dict[str, Any]:
        """Get or create AVA instance for a specific battle"""
        # Check if AVA already exists for this battle
        for instance_id, instance in self.active_instances.items():
            if instance.get("battle_id") == battle_id and instance["status"] == "active":
                return instance

        # Create new AVA instance for this battle
        return self.create_ava_instance(AVAInstanceType.BATTLE_INSTANCE, battle_id)

    def get_ava_for_encounter(self, encounter_id: str) -> Dict[str, Any]:
        """Get or create AVA instance for a specific encounter"""
        # Check if AVA already exists for this encounter
        for instance_id, instance in self.active_instances.items():
            if instance.get("battle_id") == encounter_id and instance["status"] == "active":
                return instance

        # Create new AVA instance for this encounter
        return self.create_ava_instance(AVAInstanceType.ENCOUNTER_INSTANCE, encounter_id)

    def release_ava_instance(self, instance_id: str):
        """Release an AVA instance (mark as inactive)"""
        if instance_id in self.active_instances:
            self.active_instances[instance_id]["status"] = "inactive"
            self.active_instances[instance_id]["released_at"] = datetime.now().isoformat()
            logger.info(f"🤖 Released AVA instance: {instance_id}")

    def get_active_instances(self) -> List[Dict[str, Any]]:
        """Get all active AVA instances"""
        return [inst for inst in self.active_instances.values() if inst["status"] == "active"]

    def get_instance_count(self) -> int:
        """Get count of active AVA instances"""
        return len(self.get_active_instances())

    def clear_inactive_instances(self):
        """Clear inactive AVA instances"""
        inactive = [inst_id for inst_id, inst in self.active_instances.items() 
                    if inst["status"] == "inactive"]
        for inst_id in inactive:
            del self.active_instances[inst_id]
        logger.info(f"🤖 Cleared {len(inactive)} inactive AVA instances")


def main():
    """Main entry point for testing"""
    if not CharacterAvatarRegistry:
        print("❌ Character Avatar Registry not available")
        return

    registry = CharacterAvatarRegistry()
    ava_system = AVAPlaceholderSystem(registry)

    print("=" * 80)
    print("🤖 AVA PLACEHOLDER SYSTEM TEST")
    print("=" * 80)
    print()

    # Test: Create AVA for concurrent battles
    print("Creating AVA instances for concurrent battles...")
    battle1_ava = ava_system.get_ava_for_battle("battle_001")
    battle2_ava = ava_system.get_ava_for_battle("battle_002")
    battle3_ava = ava_system.get_ava_for_battle("battle_003")

    print(f"✅ Created {ava_system.get_instance_count()} AVA instances")
    print()

    # Show active instances
    active = ava_system.get_active_instances()
    print("Active AVA Instances:")
    for inst in active:
        print(f"  • {inst['name']} ({inst['instance_id']})")
        print(f"    Type: {inst['type']}")
        print(f"    Battle ID: {inst.get('battle_id', 'N/A')}")
        print(f"    Catchphrase: {inst['customizations']['catchphrase']}")
        print()

    # Test: Release an instance
    print("Releasing battle_001 AVA...")
    ava_system.release_ava_instance(battle1_ava['instance_id'])
    print(f"✅ Active instances: {ava_system.get_instance_count()}")
    print()

    # Test: Create for encounter
    print("Creating AVA for encounter...")
    encounter_ava = ava_system.get_ava_for_encounter("encounter_001")
    print(f"✅ Created: {encounter_ava['name']}")
    print()

    print("=" * 80)


if __name__ == "__main__":


    main()