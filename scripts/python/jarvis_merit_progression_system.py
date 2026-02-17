#!/usr/bin/env python3
"""
JARVIS Merit Progression System

TTRPG/LitRPG themed merit-based progression:
- Hard times breed strong men/women
- Exercise & apply merit system of scoring individuals
- TTRPG/LitRPG themed progression, skills & equipment advancement
- Work becomes passion, entertainment, calling, art form
- Promote artistic-musical-medical-scientific-educational meritorious actions
- Physical, mental, spiritual welfare
- Humanitarian global oversight
- "If work is fun, entertaining, and educational, then one may never work a day in their life"
- Quality of Life (QOL) focus

Tags: #MERIT #TTRPG #LITRPG #PROGRESSION #QOL #WORK_AS_ART #HUMANITARIAN @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVISMerit")
except ImportError:
    try:
        from lumina_logger import get_logger
        logger = get_logger("JARVISMerit")
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("JARVISMerit")

# Import SYPHON system
try:
    from syphon_system import SYPHONSystem, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    try:
        from scripts.python.syphon_system import SYPHONSystem, DataSourceType
        SYPHON_AVAILABLE = True
    except ImportError:
        SYPHON_AVAILABLE = False
        logger.warning("SYPHON system not available")


class MeritCategory(Enum):
    """Merit categories"""
    ARTISTIC = "artistic"
    MUSICAL = "musical"
    MEDICAL = "medical"
    SCIENTIFIC = "scientific"
    EDUCATIONAL = "educational"
    PHYSICAL = "physical"
    MENTAL = "mental"
    SPIRITUAL = "spiritual"
    HUMANITARIAN = "humanitarian"


class MeritProgressionSystem:
    """Merit-based TTRPG/LitRPG progression system"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "merit_progression"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.profiles_file = self.data_dir / "profiles.jsonl"
        self.merits_file = self.data_dir / "merits.jsonl"
        self.skills_file = self.data_dir / "skills.jsonl"
        self.equipment_file = self.data_dir / "equipment.jsonl"
        self.qol_file = self.data_dir / "quality_of_life.jsonl"

        # Initialize SYPHON system
        if SYPHON_AVAILABLE:
            try:
                self.syphon = SYPHONSystem(project_root)
                logger.info("✅ SYPHON system initialized for merit progression")
            except Exception as e:
                logger.warning(f"SYPHON initialization failed: {e}")
                self.syphon = None
        else:
            self.syphon = None

        # Core principles
        self.core_principles = {
            "hard_times_breed_strong": "Hard times breed strong men/women",
            "work_as_passion": "Work becomes passion, entertainment, calling, art form",
            "never_work_a_day": "If work is fun, entertaining, and educational, then one may never work a day in their life",
            "qol_focus": "Quality of Life (QOL) is paramount"
        }

        # Merit categories
        self.merit_categories = {
            "artistic": "Artistic meritorious actions and values",
            "musical": "Musical meritorious actions and values",
            "medical": "Medical meritorious actions and values",
            "scientific": "Scientific meritorious actions and values",
            "educational": "Educational meritorious actions and values",
            "physical": "Physical welfare and advancement",
            "mental": "Mental welfare and advancement",
            "spiritual": "Spiritual welfare and advancement",
            "humanitarian": "Humanitarian global oversight and actions"
        }

    def create_profile(
        self,
        individual_id: str,
        name: str,
        initial_level: int = 1
    ) -> Dict[str, Any]:
        """Create TTRPG/LitRPG profile for individual"""
        profile = {
            "profile_id": f"profile_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "individual_id": individual_id,
            "name": name,
            "level": initial_level,
            "experience_points": 0,
            "merit_score": 0,
            "skills": {},
            "equipment": {},
            "qol_metrics": {
                "physical": 50,
                "mental": 50,
                "spiritual": 50,
                "overall": 50
            },
            "work_as_passion": True,
            "work_as_entertainment": True,
            "work_as_art": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        # Save profile
        try:
            with open(self.profiles_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(profile) + '\n')
        except Exception as e:
            logger.error(f"Error saving profile: {e}")

        logger.info(f"📊 Profile created: {name} (Level {initial_level})")

        return profile

    def award_merit(
        self,
        individual_id: str,
        category: MeritCategory,
        action_description: str,
        merit_points: int,
        qol_impact: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Award merit points for meritorious action"""
        merit = {
            "merit_id": f"merit_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "individual_id": individual_id,
            "category": category.value,
            "action_description": action_description,
            "merit_points": merit_points,
            "qol_impact": qol_impact or {},
            "viable": True,
            "actionable": True,
            "promotes_welfare": True,
            "syphon_intelligence": {},
            "status": "awarded"
        }

        # Use SYPHON to extract intelligence
        if self.syphon:
            try:
                content = f"Merit Action: {action_description}\nCategory: {category.value}\nPoints: {merit_points}"
                syphon_result = self._syphon_extract_merit_intelligence(content)
                if syphon_result:
                    merit["syphon_intelligence"] = syphon_result
            except Exception as e:
                logger.warning(f"SYPHON merit extraction failed: {e}")

        # Save merit
        try:
            with open(self.merits_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(merit) + '\n')
        except Exception as e:
            logger.error(f"Error saving merit: {e}")

        logger.info(f"⭐ Merit awarded: {merit_points} points for {category.value}")

        return merit

    def advance_skill(
        self,
        individual_id: str,
        skill_name: str,
        skill_category: str,
        experience_gained: int
    ) -> Dict[str, Any]:
        """Advance skill (TTRPG/LitRPG style)"""
        skill_advancement = {
            "advancement_id": f"skill_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "individual_id": individual_id,
            "skill_name": skill_name,
            "skill_category": skill_category,
            "experience_gained": experience_gained,
            "work_as_passion": True,
            "work_as_entertainment": True,
            "work_as_art": True,
            "status": "advanced"
        }

        # Save skill advancement
        try:
            with open(self.skills_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(skill_advancement) + '\n')
        except Exception as e:
            logger.error(f"Error saving skill advancement: {e}")

        logger.info(f"📈 Skill advanced: {skill_name} (+{experience_gained} XP)")

        return skill_advancement

    def upgrade_equipment(
        self,
        individual_id: str,
        equipment_name: str,
        equipment_type: str,
        upgrade_level: int
    ) -> Dict[str, Any]:
        """Upgrade equipment (TTRPG/LitRPG style)"""
        equipment = {
            "equipment_id": f"equip_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "individual_id": individual_id,
            "equipment_name": equipment_name,
            "equipment_type": equipment_type,
            "upgrade_level": upgrade_level,
            "status": "upgraded"
        }

        # Save equipment
        try:
            with open(self.equipment_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(equipment) + '\n')
        except Exception as e:
            logger.error(f"Error saving equipment: {e}")

        logger.info(f"⚔️  Equipment upgraded: {equipment_name} (Level {upgrade_level})")

        return equipment

    def update_qol(
        self,
        individual_id: str,
        physical: int = None,
        mental: int = None,
        spiritual: int = None
    ) -> Dict[str, Any]:
        """Update Quality of Life metrics"""
        qol = {
            "qol_id": f"qol_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "individual_id": individual_id,
            "physical": physical,
            "mental": mental,
            "spiritual": spiritual,
            "overall": None,
            "qol_focus": True,
            "status": "updated"
        }

        # Calculate overall QOL
        metrics = [m for m in [physical, mental, spiritual] if m is not None]
        if metrics:
            qol["overall"] = sum(metrics) / len(metrics)

        # Save QOL
        try:
            with open(self.qol_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(qol) + '\n')
        except Exception as e:
            logger.error(f"Error saving QOL: {e}")

        logger.info(f"💚 QOL updated: Physical={physical}, Mental={mental}, Spiritual={spiritual}")

        return qol

    def _syphon_extract_merit_intelligence(self, content: str) -> Dict[str, Any]:
        """Extract intelligence using SYPHON system"""
        if not self.syphon:
            return {}

        try:
            syphon_data = self.syphon.syphon_generic(
                content=content,
                source_type=DataSourceType.OTHER,
                source_id=f"merit_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                metadata={"merit_progression": True, "qol": True}
            )

            return {
                "actionable_items": syphon_data.actionable_items,
                "tasks": syphon_data.tasks,
                "decisions": syphon_data.decisions,
                "intelligence": [item for item in syphon_data.intelligence]
            }
        except Exception as e:
            logger.error(f"SYPHON merit extraction error: {e}")
            return {}

    def get_system_status(self) -> Dict[str, Any]:
        """Get merit progression system status"""
        return {
            "core_principles": self.core_principles,
            "merit_categories": len(self.merit_categories),
            "status": "operational",
            "work_as_passion": True,
            "work_as_entertainment": True,
            "work_as_art": True,
            "qol_focus": True
        }


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Merit Progression System")
        parser.add_argument("--create-profile", type=str, nargs=2, metavar=("ID", "NAME"),
                           help="Create TTRPG/LitRPG profile")
        parser.add_argument("--award-merit", type=str, nargs=4, metavar=("ID", "CATEGORY", "ACTION", "POINTS"),
                           help="Award merit points")
        parser.add_argument("--advance-skill", type=str, nargs=4, metavar=("ID", "SKILL", "CATEGORY", "XP"),
                           help="Advance skill")
        parser.add_argument("--status", action="store_true", help="Get system status")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        merit_system = MeritProgressionSystem(project_root)

        if args.create_profile:
            profile = merit_system.create_profile(args.create_profile[0], args.create_profile[1])
            print("=" * 80)
            print("📊 PROFILE CREATED")
            print("=" * 80)
            print(json.dumps(profile, indent=2, default=str))

        elif args.award_merit:
            category = MeritCategory(args.award_merit[1])
            merit = merit_system.award_merit(
                args.award_merit[0],
                category,
                args.award_merit[2],
                int(args.award_merit[3])
            )
            print("=" * 80)
            print("⭐ MERIT AWARDED")
            print("=" * 80)
            print(json.dumps(merit, indent=2, default=str))

        elif args.advance_skill:
            skill = merit_system.advance_skill(
                args.advance_skill[0],
                args.advance_skill[1],
                args.advance_skill[2],
                int(args.advance_skill[3])
            )
            print("=" * 80)
            print("📈 SKILL ADVANCED")
            print("=" * 80)
            print(json.dumps(skill, indent=2, default=str))

        elif args.status:
            status = merit_system.get_system_status()
            print(json.dumps(status, indent=2, default=str))

        else:
            print("=" * 80)
            print("⭐ JARVIS MERIT PROGRESSION SYSTEM")
            print("=" * 80)
            print("Hard times breed strong men/women")
            print("Work as passion, entertainment, calling, art form")
            print("If work is fun, you never work a day in your life")
            print("Quality of Life (QOL) focus")
            print("=" * 80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()