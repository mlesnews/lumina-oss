#!/usr/bin/env python3
"""
Military & Civilian Principles System

Air Force: UCMJ enforcement, double jeopardy, "ignorance is not an excuse"
Post-military (Banking & IT): "perception drives reality"

These principles guide decision-making and behavior in the system.

Tags: #MILITARY #UCMJ #DOUBLE_JEOPARDY #PERCEPTION_REALITY #BANKING #IT #PRINCIPLES
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MilitaryCivilianPrinciples")


class PrincipleDomain(Enum):
    """Domain where principle applies"""
    MILITARY = "military"  # Air Force, UCMJ
    CIVILIAN = "civilian"  # Banking, IT
    BOTH = "both"  # Applies to both


@dataclass
class Principle:
    """A principle that guides behavior"""
    name: str
    domain: PrincipleDomain
    statement: str
    enforcement: str
    consequences: str
    applies_to: List[str]  # What this applies to


@dataclass
class PrincipleViolation:
    """A violation of a principle"""
    principle: Principle
    violation_description: str
    context: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    consequences_applied: bool = False


class MilitaryCivilianPrinciplesSystem:
    """
    Military & Civilian Principles System

    Air Force: UCMJ enforcement, double jeopardy, "ignorance is not an excuse"
    Post-military (Banking & IT): "perception drives reality"

    These principles guide all decision-making and behavior.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Military & Civilian Principles System"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Define principles
        self.principles = self._initialize_principles()

        # Violation tracking
        self.violations: List[PrincipleViolation] = []

        logger.info("✅ Military & Civilian Principles System initialized")
        logger.info("   ⚖️  UCMJ: Ignorance is not an excuse")
        logger.info("   👁️  Perception drives reality")

    def _initialize_principles(self) -> Dict[str, Principle]:
        """Initialize principles"""
        principles = {}

        # Military Principles (Air Force, UCMJ)
        military_principles = [
            Principle(
                name="UCMJ Enforcement",
                domain=PrincipleDomain.MILITARY,
                statement="Uniform Code of Military Justice enforced",
                enforcement="Military judicial system",
                consequences="Double jeopardy - military AND civilian consequences",
                applies_to=["military_personnel", "enlisted", "officers"]
            ),
            Principle(
                name="Double Jeopardy",
                domain=PrincipleDomain.MILITARY,
                statement="Break a law while enlisted - face both military AND civilian consequences",
                enforcement="Both UCMJ and civilian judicial systems",
                consequences="Punishment in both systems - no protection from double jeopardy",
                applies_to=["military_personnel", "legal_violations"]
            ),
            Principle(
                name="Ignorance is Not an Excuse",
                domain=PrincipleDomain.MILITARY,
                statement="Not knowing the law/rules is not a valid defense",
                enforcement="UCMJ and military regulations",
                consequences="Punishment regardless of knowledge",
                applies_to=["all_actions", "all_decisions", "all_commands"]
            ),
        ]

        # Civilian Principles (Banking & IT)
        civilian_principles = [
            Principle(
                name="Perception Drives Reality",
                domain=PrincipleDomain.CIVILIAN,
                statement="How things are perceived is more important than how they actually are",
                enforcement="Business, banking, IT industry standards",
                consequences="Reputation, trust, business outcomes",
                applies_to=["banking", "it", "business", "reputation", "trust"]
            ),
            Principle(
                name="Reality Follows Perception",
                domain=PrincipleDomain.CIVILIAN,
                statement="What people believe becomes reality",
                enforcement="Market forces, customer trust, stakeholder confidence",
                consequences="Business success or failure based on perception",
                applies_to=["business_decisions", "customer_relations", "stakeholder_management"]
            ),
        ]

        # Add all principles
        for principle in military_principles + civilian_principles:
            principles[principle.name.lower().replace(" ", "_")] = principle

        logger.info(f"   ⚖️  Initialized {len(military_principles)} Military principles")
        logger.info(f"   👁️  Initialized {len(civilian_principles)} Civilian principles")

        return principles

    def check_principle_compliance(
        self,
        action: str,
        context: Optional[Dict[str, Any]] = None,
        domain: Optional[PrincipleDomain] = None
    ) -> Dict[str, Any]:
        """
        Check if action complies with principles

        Args:
            action: Action to check
            context: Additional context
            domain: Domain (military, civilian, or both)

        Returns:
            Compliance check result
        """
        context = context or {}
        violations = []
        warnings = []

        # Check all applicable principles
        for principle_name, principle in self.principles.items():
            # Check if principle applies
            if domain and principle.domain != domain and principle.domain != PrincipleDomain.BOTH:
                continue

            # Check for violations
            violation = self._check_principle_violation(principle, action, context)
            if violation:
                violations.append(violation)
                warnings.append(f"⚠️  {principle.name}: {violation.violation_description}")

        # Determine compliance
        is_compliant = len(violations) == 0

        result = {
            "compliant": is_compliant,
            "violations": len(violations),
            "warnings": warnings,
            "principles_checked": len(self.principles),
            "domain": domain.value if domain else "both"
        }

        if not is_compliant:
            logger.warning(f"   ⚠️  Principle violations detected: {len(violations)}")
            for violation in violations:
                logger.warning(f"      - {violation.principle.name}: {violation.violation_description}")
        else:
            logger.info(f"   ✅ Action compliant with principles")

        return result

    def _check_principle_violation(
        self,
        principle: Principle,
        action: str,
        context: Dict[str, Any]
    ) -> Optional[PrincipleViolation]:
        """Check if action violates a specific principle"""

        # UCMJ: Ignorance is not an excuse
        if principle.name == "Ignorance is Not an Excuse":
            # Check if action shows ignorance of rules
            if "didn't know" in action.lower() or "wasn't aware" in action.lower():
                return PrincipleViolation(
                    principle=principle,
                    violation_description="Ignorance claimed as excuse",
                    context=context
                )

        # Double Jeopardy
        if principle.name == "Double Jeopardy":
            # Check if action might violate both military and civilian law
            if context.get("military_context") and context.get("civilian_law_applies"):
                return PrincipleViolation(
                    principle=principle,
                    violation_description="Action may violate both military and civilian law",
                    context=context
                )

        # Perception Drives Reality
        if principle.name == "Perception Drives Reality":
            # Check if action might create negative perception
            if context.get("negative_perception_risk"):
                return PrincipleViolation(
                    principle=principle,
                    violation_description="Action may create negative perception",
                    context=context
                )

        return None  # No violation

    def apply_principle(
        self,
        action: str,
        domain: PrincipleDomain = PrincipleDomain.BOTH,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Apply principles to action

        This ensures actions comply with:
        - Military principles (UCMJ, double jeopardy, ignorance)
        - Civilian principles (perception drives reality)
        """
        context = context or {}

        # Check compliance
        compliance = self.check_principle_compliance(action, context, domain)

        # Apply principles
        guidance = []

        # Military principles
        if domain in [PrincipleDomain.MILITARY, PrincipleDomain.BOTH]:
            guidance.append("⚖️  UCMJ: Ignorance is not an excuse - know the rules")
            guidance.append("⚖️  Double Jeopardy: Military AND civilian consequences apply")

        # Civilian principles
        if domain in [PrincipleDomain.CIVILIAN, PrincipleDomain.BOTH]:
            guidance.append("👁️  Perception drives reality - consider how this will be perceived")
            guidance.append("👁️  What people believe becomes reality - manage perception")

        result = {
            "action": action,
            "domain": domain.value,
            "compliant": compliance["compliant"],
            "violations": compliance["violations"],
            "warnings": compliance["warnings"],
            "guidance": guidance,
            "principles_applied": len(self.principles)
        }

        logger.info(f"   ⚖️  Principles applied: {domain.value}")
        logger.info(f"   ✅ Compliance: {compliance['compliant']}")

        return result

    def get_principle_guidance(
        self,
        situation: str,
        domain: Optional[PrincipleDomain] = None
    ) -> List[str]:
        """
        Get principle-based guidance for a situation

        Args:
            situation: The situation needing guidance
            domain: Domain (military, civilian, or both)

        Returns:
            List of guidance statements
        """
        guidance = []

        applicable_principles = [
            p for p in self.principles.values()
            if not domain or p.domain == domain or p.domain == PrincipleDomain.BOTH
        ]

        for principle in applicable_principles:
            if domain == PrincipleDomain.MILITARY:
                if principle.name == "Ignorance is Not an Excuse":
                    guidance.append("⚖️  Know the rules - ignorance is not an excuse")
                elif principle.name == "Double Jeopardy":
                    guidance.append("⚖️  Military violations face both UCMJ and civilian consequences")

            if domain == PrincipleDomain.CIVILIAN or domain == PrincipleDomain.BOTH:
                if principle.name == "Perception Drives Reality":
                    guidance.append("👁️  Consider how this will be perceived - perception drives reality")

        return guidance


# Global instance
_principles_system_instance = None


def get_principles_system() -> MilitaryCivilianPrinciplesSystem:
    """Get or create global Military & Civilian Principles System"""
    global _principles_system_instance
    if _principles_system_instance is None:
        _principles_system_instance = MilitaryCivilianPrinciplesSystem()
        logger.info("✅ Military & Civilian Principles System initialized")
        logger.info("   ⚖️  UCMJ: Ignorance is not an excuse")
        logger.info("   👁️  Perception drives reality")
    return _principles_system_instance


def apply_principles(
    action: str,
    domain: PrincipleDomain = PrincipleDomain.BOTH
) -> Dict[str, Any]:
    """Apply principles to action"""
    system = get_principles_system()
    return system.apply_principle(action, domain)


if __name__ == "__main__":
    # Test
    system = get_principles_system()

    # Test military principle
    print("\n⚖️  Testing Military Principle...")
    result = system.apply_principle(
        "I didn't know that was against the rules",
        domain=PrincipleDomain.MILITARY
    )
    print(f"   Compliant: {result['compliant']}")
    print(f"   Violations: {result['violations']}")
    if result['warnings']:
        for warning in result['warnings']:
            print(f"   {warning}")

    # Test civilian principle
    print("\n👁️  Testing Civilian Principle...")
    result = system.apply_principle(
        "This might look bad to customers",
        domain=PrincipleDomain.CIVILIAN,
        context={"negative_perception_risk": True}
    )
    print(f"   Compliant: {result['compliant']}")
    print(f"   Guidance: {result['guidance']}")
