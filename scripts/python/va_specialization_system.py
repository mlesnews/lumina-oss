#!/usr/bin/env python3
"""
VA Specialization System

Defines specialized roles, capabilities, and skill-based routing for VAs.

Tags: #VIRTUAL_ASSISTANT #SPECIALIZATION #ROLES #SKILLS @JARVIS @LUMINA
"""

import sys
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from character_avatar_registry import (CharacterAvatarRegistry,
                                           CharacterType)
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    CharacterAvatarRegistry = None
    CharacterType = None

logger = get_logger("VASpecialization")


class SpecializationDomain(Enum):
    """Specialization domains"""
    AUTOMATION = "automation"
    COMBAT = "combat"
    UI_UX = "ui_ux"
    SECURITY = "security"
    SYSTEM_MANAGEMENT = "system_management"
    DATA_ANALYSIS = "data_analysis"
    WORKFLOW_ORCHESTRATION = "workflow_orchestration"
    GENERAL_PURPOSE = "general_purpose"


@dataclass
class VASpecialization:
    """VA specialization definition"""
    va_id: str
    primary_domain: SpecializationDomain
    secondary_domains: List[SpecializationDomain] = field(default_factory=list)
    skill_level: int = 5  # 1-10 scale
    capabilities: List[str] = field(default_factory=list)
    workflows: List[str] = field(default_factory=list)
    expertise_areas: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["primary_domain"] = self.primary_domain.value
        data["secondary_domains"] = [d.value for d in self.secondary_domains]
        return data


class VASpecializationSystem:
    """
    VA Specialization System

    Features:
    - Specialized role definitions
    - Domain expertise mapping
    - Skill-based task routing
    - Capability matrix
    - Workflow assignment
    """

    def __init__(self, registry: Optional[CharacterAvatarRegistry] = None):
        """Initialize VA specialization system"""
        if registry is None:
            if CharacterAvatarRegistry:
                registry = CharacterAvatarRegistry()
            else:
                raise ValueError("CharacterAvatarRegistry not available")

        self.registry = registry
        self.vas = self.registry.get_characters_by_type(CharacterType.VIRTUAL_ASSISTANT)

        # Specializations
        self.specializations: Dict[str, VASpecialization] = {}

        # Initialize default specializations
        self._initialize_default_specializations()

        logger.info("=" * 80)
        logger.info("🎯 VA SPECIALIZATION SYSTEM")
        logger.info("=" * 80)
        logger.info(f"   VAs Registered: {len(self.vas)}")
        logger.info("   Specializations initialized")
        logger.info("=" * 80)

    def _initialize_default_specializations(self):
        """Initialize default specializations for all VAs"""
        for va in self.vas:
            if va.character_id == "jarvis_va":
                spec = VASpecialization(
                    va_id=va.character_id,
                    primary_domain=SpecializationDomain.AUTOMATION,
                    secondary_domains=[
                        SpecializationDomain.SYSTEM_MANAGEMENT,
                        SpecializationDomain.WORKFLOW_ORCHESTRATION
                    ],
                    skill_level=9,
                    capabilities=["automation", "system_management", "coordination"],
                    workflows=["automation_workflow", "system_maintenance"],
                    expertise_areas=["Iron Man systems", "Desktop automation", "Workflow orchestration"]
                )
            elif va.character_id == "imva":
                spec = VASpecialization(
                    va_id=va.character_id,
                    primary_domain=SpecializationDomain.UI_UX,
                    secondary_domains=[SpecializationDomain.GENERAL_PURPOSE],
                    skill_level=7,
                    capabilities=["ui_interaction", "user_experience", "visualization"],
                    workflows=["ui_workflow", "display_management"],
                    expertise_areas=["User interface", "Visual feedback", "Bobblehead interactions"]
                )
            elif va.character_id == "ace":
                spec = VASpecialization(
                    va_id=va.character_id,
                    primary_domain=SpecializationDomain.COMBAT,
                    secondary_domains=[
                        SpecializationDomain.SECURITY,
                        SpecializationDomain.DATA_ANALYSIS
                    ],
                    skill_level=10,
                    capabilities=["combat", "security", "defense", "wopr_stances"],
                    workflows=["combat_workflow", "security_scan", "threat_analysis"],
                    expertise_areas=["Combat systems", "Security protocols", "ACE's Armory Crate"]
                )
            elif va.character_id == "ava":
                spec = VASpecialization(
                    va_id=va.character_id,
                    primary_domain=SpecializationDomain.GENERAL_PURPOSE,
                    secondary_domains=[
                        SpecializationDomain.AUTOMATION,
                        SpecializationDomain.COMBAT
                    ],
                    skill_level=6,
                    capabilities=["concurrent_operations", "task_handling", "battle_management"],
                    workflows=["concurrent_battle", "multi_task"],
                    expertise_areas=["Concurrent battles", "Placeholder operations", "Scalable tasks"]
                )
            else:
                spec = VASpecialization(
                    va_id=va.character_id,
                    primary_domain=SpecializationDomain.GENERAL_PURPOSE,
                    skill_level=5
                )

            self.specializations[va.character_id] = spec
            logger.info(f"🎯 Specialized {va.name}: {spec.primary_domain.value} (Level {spec.skill_level})")

    def define_specialization(self, va_id: str, primary_domain: SpecializationDomain,
                             secondary_domains: Optional[List[SpecializationDomain]] = None,
                             skill_level: int = 5) -> VASpecialization:
        """Define or update VA specialization"""
        va = self.registry.get_character(va_id)
        if not va or va.character_type != CharacterType.VIRTUAL_ASSISTANT:
            raise ValueError(f"VA {va_id} not found")

        spec = VASpecialization(
            va_id=va_id,
            primary_domain=primary_domain,
            secondary_domains=secondary_domains or [],
            skill_level=skill_level
        )

        self.specializations[va_id] = spec
        logger.info(f"🎯 Defined specialization for {va_id}: {primary_domain.value}")
        return spec

    def route_by_specialization(self, task_domain: SpecializationDomain,
                               required_skill_level: int = 5) -> List[str]:
        """Route task to VAs based on specialization"""
        candidates = []

        for va_id, spec in self.specializations.items():
            # Check primary domain
            if spec.primary_domain == task_domain and spec.skill_level >= required_skill_level:
                candidates.append((va_id, spec.skill_level, True))  # True = primary match
            # Check secondary domains
            elif task_domain in spec.secondary_domains and spec.skill_level >= required_skill_level:
                candidates.append((va_id, spec.skill_level, False))  # False = secondary match

        # Sort by primary match first, then skill level
        candidates.sort(key=lambda x: (not x[2], -x[1]))

        return [va_id for va_id, _, _ in candidates]

    def get_specialization(self, va_id: str) -> Optional[VASpecialization]:
        """Get specialization for a VA"""
        return self.specializations.get(va_id)

    def capability_matrix(self) -> Dict[str, Any]:
        """Generate capability matrix for all VAs"""
        matrix = {
            "domains": [domain.value for domain in SpecializationDomain],
            "vas": []
        }

        for va_id, spec in self.specializations.items():
            va = self.registry.get_character(va_id)
            if not va:
                continue

            va_capabilities = {}
            for domain in SpecializationDomain:
                if spec.primary_domain == domain:
                    va_capabilities[domain.value] = spec.skill_level
                elif domain in spec.secondary_domains:
                    va_capabilities[domain.value] = spec.skill_level - 2  # Secondary is lower
                else:
                    va_capabilities[domain.value] = 0

            matrix["vas"].append({
                "va_id": va_id,
                "name": va.name,
                "capabilities": va_capabilities,
                "primary_domain": spec.primary_domain.value,
                "skill_level": spec.skill_level
            })

        return matrix

    def skill_assessment(self, va_id: str) -> Dict[str, Any]:
        """Assess VA skills"""
        spec = self.specializations.get(va_id)
        if not spec:
            return {}

        return {
            "va_id": va_id,
            "primary_domain": spec.primary_domain.value,
            "skill_level": spec.skill_level,
            "capabilities": spec.capabilities,
            "workflows": spec.workflows,
            "expertise_areas": spec.expertise_areas,
            "secondary_domains": [d.value for d in spec.secondary_domains]
        }


def main():
    """Main entry point for testing"""
    if not CharacterAvatarRegistry:
        print("❌ Character Avatar Registry not available")
        return

    registry = CharacterAvatarRegistry()
    spec_system = VASpecializationSystem(registry)

    print("=" * 80)
    print("🎯 VA SPECIALIZATION SYSTEM TEST")
    print("=" * 80)
    print()

    # Test: Get specializations
    print("VA Specializations:")
    for va in spec_system.vas:
        spec = spec_system.get_specialization(va.character_id)
        if spec:
            print(f"  • {va.name} ({va.character_id})")
            print(f"    Primary: {spec.primary_domain.value}")
            print(f"    Skill Level: {spec.skill_level}")
            print(f"    Capabilities: {', '.join(spec.capabilities)}")
            print()

    # Test: Route by specialization
    print("Routing tasks by specialization:")
    test_domains = [
        SpecializationDomain.AUTOMATION,
        SpecializationDomain.COMBAT,
        SpecializationDomain.UI_UX
    ]

    for domain in test_domains:
        routed_vas = spec_system.route_by_specialization(domain)
        print(f"  {domain.value}: {', '.join(routed_vas)}")
    print()

    # Test: Capability matrix
    print("Capability Matrix:")
    matrix = spec_system.capability_matrix()
    for va_info in matrix["vas"]:
        print(f"  • {va_info['name']}: Primary={va_info['primary_domain']}, Level={va_info['skill_level']}")
    print()

    print("=" * 80)


if __name__ == "__main__":


    main()