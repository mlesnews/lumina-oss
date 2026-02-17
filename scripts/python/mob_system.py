#!/usr/bin/env python3
"""
MOB System

Manages MOBs (groups/gangs) - NOT avatars, NOT NPCs.
MOBs are collections of entities that work together.

Tags: #MOB #GROUP #GANG #NOT_AVATAR #NOT_NPC @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MOBSystem")


class MOBType(Enum):
    """MOB type classification"""
    STT_SYSTEM = "stt_system"  # Speech-to-Text systems (e.g., Dragon and bad bois)
    COMBAT_GROUP = "combat_group"  # Combat-oriented groups
    SERVICE_CLUSTER = "service_cluster"  # Service groups
    SYSTEM_GROUP = "system_group"  # System groups


@dataclass
class MOB:
    """MOB (group/gang) configuration - NOT an avatar, NOT an NPC"""
    mob_id: str
    name: str
    mob_type: MOBType
    leader_id: Optional[str] = None  # Leader of the MOB
    member_ids: List[str] = field(default_factory=list)  # Members (bad bois)
    description: str = ""
    role: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["mob_type"] = self.mob_type.value
        return data


class MOBSystem:
    """
    MOB System

    Manages MOBs (groups/gangs) - NOT avatars, NOT NPCs.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize MOB system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "mobs"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.mobs_file = self.data_dir / "mobs_registry.json"

        # MOB registry
        self.mobs: Dict[str, MOB] = {}

        # Load existing MOBs
        self._load_mobs()

        # Initialize default MOBs if empty
        if not self.mobs:
            self._initialize_default_mobs()
            self._save_mobs()

        logger.info("=" * 80)
        logger.info("👥 MOB SYSTEM")
        logger.info("=" * 80)
        logger.info(f"   MOBs registered: {len(self.mobs)}")
        logger.info("=" * 80)

    def _initialize_default_mobs(self):
        """Initialize default MOBs"""

        # Dragon MOB - Dragon and his bad bois (STT System)
        dragon_mob = MOB(
            mob_id="dragon_mob",
            name="Dragon MOB",
            mob_type=MOBType.STT_SYSTEM,
            leader_id="dragon_stt_core",
            member_ids=[
                "dragon_stt_core",  # Leader
                "dragon_voice_engine",  # Bad boi 1
                "dragon_command_processor",  # Bad boi 2
                "dragon_audio_interface",  # Bad boi 3
                "dragon_recognition_engine"  # Bad boi 4
            ],
            description="Dragon NaturallySpeaking and his bad bois - STT System MOB",
            role="Speech-to-Text Recognition & Command Processing MOB"
        )
        self.mobs["dragon_mob"] = dragon_mob

        logger.info(f"✅ Initialized {len(self.mobs)} MOBs")

    def get_mob(self, mob_id: str) -> Optional[MOB]:
        """Get MOB by ID"""
        return self.mobs.get(mob_id)

    def get_all_mobs(self) -> Dict[str, MOB]:
        """Get all MOBs"""
        return self.mobs.copy()

    def add_mob(self, mob: MOB) -> bool:
        """Add a new MOB"""
        if mob.mob_id in self.mobs:
            logger.warning(f"MOB already exists: {mob.mob_id}")
            return False

        self.mobs[mob.mob_id] = mob
        self._save_mobs()
        return True

    def add_member_to_mob(self, mob_id: str, member_id: str) -> bool:
        """Add a member to a MOB"""
        mob = self.get_mob(mob_id)
        if not mob:
            return False

        if member_id not in mob.member_ids:
            mob.member_ids.append(member_id)
            self._save_mobs()
        return True

    def _load_mobs(self):
        """Load MOBs from file"""
        if self.mobs_file.exists():
            try:
                with open(self.mobs_file, 'r', encoding='utf-8') as f:
                    import json
                    data = json.load(f)
                    for mob_id, mob_data in data.items():
                        mob_data["mob_type"] = MOBType(mob_data["mob_type"])
                        self.mobs[mob_id] = MOB(**mob_data)
                logger.info(f"✅ Loaded {len(self.mobs)} MOBs from registry")
            except Exception as e:
                logger.error(f"❌ Error loading MOBs: {e}")

    def _save_mobs(self):
        """Save MOBs to file"""
        try:
            import json
            data = {mob_id: mob.to_dict() for mob_id, mob in self.mobs.items()}
            with open(self.mobs_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Saved {len(self.mobs)} MOBs to registry")
        except Exception as e:
            logger.error(f"❌ Error saving MOBs: {e}")


def main():
    """Main entry point"""
    mob_system = MOBSystem()

    print("=" * 80)
    print("👥 MOB SYSTEM")
    print("=" * 80)
    print(f"Total MOBs: {len(mob_system.mobs)}")
    print()

    for mob_id, mob in mob_system.mobs.items():
        print(f"  {mob.name} ({mob_id})")
        print(f"    Type: {mob.mob_type.value}")
        print(f"    Leader: {mob.leader_id}")
        print(f"    Members: {len(mob.member_ids)}")
        print(f"    Role: {mob.role}")
        print()

    print("=" * 80)


if __name__ == "__main__":


    main()