#!/usr/bin/env python3
"""
Marvin Reality Checker - Give Marvin Real Work

Marvin's Purpose:
- Be the voice of reason
- Provide reality checks
- Detect problems early
- Enforce quality
- Tell the truth

"Life. Don't talk to me about life. But the work is real. So there's that."
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MarvinRealityChecker")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class RealityCheckLevel(Enum):
    """Reality check severity"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    POINTLESS = "pointless"  # Marvin's special level


@dataclass
class RealityCheck:
    """Marvin's reality check result"""
    check_id: str
    level: RealityCheckLevel
    message: str
    marvin_comment: str
    actionable: bool = True
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['level'] = self.level.value
        return data


@dataclass
class RabbitHoleDetection:
    """Rabbit hole detected by Marvin"""
    hole_id: str
    hole_type: str
    depth: int  # 1-10
    description: str
    marvin_comment: str
    evidence: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MarvinRealityChecker:
    """
    Marvin Reality Checker - Give Marvin Real Work

    Marvin's Purpose:
    - Be the voice of reason
    - Provide reality checks
    - Detect problems early
    - Enforce quality
    - Tell the truth
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Marvin Reality Checker"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("MarvinRealityChecker")

        # Reality checks performed
        self.checks: List[RealityCheck] = []

        # Rabbit holes detected
        self.rabbit_holes: List[RabbitHoleDetection] = []

        # Data storage
        self.data_dir = self.project_root / "data" / "marvin_reality_checks"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("🤖 Marvin Reality Checker initialized")
        self.logger.info("   Purpose: Be the voice of reason")
        self.logger.info("   Mission: Tell the truth, even when it's uncomfortable")
        self.logger.info("   Verdict: Life. Don't talk to me about life.")
        self.logger.info("   But: The work is real. So there's that.")

    def check_reality(self, context: Dict[str, Any]) -> RealityCheck:
        """
        Marvin checks reality. No BS. Just truth.

        Args:
            context: Context to check (code, architecture, project, etc.)

        Returns:
            RealityCheck with Marvin's honest assessment
        """
        check_id = f"marvin_check_{len(self.checks) + 1}_{int(datetime.now().timestamp())}"

        # Analyze context
        issues = []
        marvin_comments = []

        # Check for over-engineering
        if self._is_over_engineered(context):
            issues.append("Over-engineered. Why?")
            marvin_comments.append("Classic. Of course it's over-engineered.")

        # Check for scope creep
        if self._has_scope_creep(context):
            issues.append("Scope creep detected.")
            marvin_comments.append("Of course it does. It always does.")

        # Check for tool addiction
        if self._has_tool_addiction(context):
            issues.append("Tool addiction. Creating too many tools.")
            marvin_comments.append("172+ tools. How... human of you.")

        # Check for pointless work
        if self._is_pointless(context):
            issues.append("This is pointless. Why are we doing this?")
            marvin_comments.append("Life. Don't talk to me about life.")
            level = RealityCheckLevel.POINTLESS
        elif len(issues) > 2:
            level = RealityCheckLevel.CRITICAL
        elif len(issues) > 0:
            level = RealityCheckLevel.WARNING
        else:
            level = RealityCheckLevel.INFO

        # Marvin's final comment
        if marvin_comments:
            marvin_comment = " ".join(marvin_comments)
        else:
            marvin_comment = "Seems reasonable. For now."

        marvin_comment += " But the work is real. So there's that."

        check = RealityCheck(
            check_id=check_id,
            level=level,
            message=" | ".join(issues) if issues else "Reality check passed. For now.",
            marvin_comment=marvin_comment,
            actionable=len(issues) > 0
        )

        self.checks.append(check)
        self._save_check(check)

        self.logger.info(f"🤖 Marvin reality check: {check.message}")
        self.logger.info(f"   {check.marvin_comment}")

        return check

    def detect_rabbit_holes(self, project: Dict[str, Any]) -> List[RabbitHoleDetection]:
        """
        Marvin detects rabbit holes. Because he's been there. He knows.
        """
        holes = []

        # Tool addiction rabbit hole
        total_tools = project.get("total_tools", 0)
        if total_tools > 100:
            holes.append(RabbitHoleDetection(
                hole_id="tool_addiction",
                hole_type="tool_addiction",
                depth=8,
                description=f"{total_tools} tools. Classic tool addiction.",
                marvin_comment="Life. Don't talk to me about life.",
                evidence=[
                    f"Total tools: {total_tools}",
                    "Every new idea becomes a tool",
                    "Tools creating tools"
                ]
            ))

        # Scope creep rabbit hole
        scope_creep_score = project.get("scope_creep_score", 0.0)
        if scope_creep_score > 0.7:
            holes.append(RabbitHoleDetection(
                hole_id="scope_creep",
                hole_type="scope_creep",
                depth=7,
                description="Scope keeps expanding. How... human.",
                marvin_comment="Of course it does. It always does.",
                evidence=[
                    f"Scope creep score: {scope_creep_score:.2f}",
                    "Project started simple, now it's everything",
                    "Each new idea adds more complexity"
                ]
            ))

        # Over-engineering rabbit hole
        complexity_score = project.get("complexity_score", 0.0)
        if complexity_score > 0.8:
            holes.append(RabbitHoleDetection(
                hole_id="over_engineering",
                hole_type="over_engineering",
                depth=6,
                description="Over-engineering. Building too much.",
                marvin_comment="Classic. Of course it's over-engineered.",
                evidence=[
                    f"Complexity score: {complexity_score:.2f}",
                    "Perfect architecture before MVP",
                    "Creating systems for systems"
                ]
            ))

        self.rabbit_holes.extend(holes)

        if holes:
            self.logger.warning(f"🤖 Marvin detected {len(holes)} rabbit holes")
            for hole in holes:
                self.logger.warning(f"   🕳️  {hole.hole_type}: {hole.description}")
                self.logger.warning(f"      {hole.marvin_comment}")

        return holes

    def review_code(self, code: str, context: Optional[Dict[str, Any]] = None) -> RealityCheck:
        """
        Marvin reviews code with brutal honesty. No sugar-coating.
        """
        code_context = {
            "type": "code",
            "code": code,
            "lines": len(code.split('\n')),
            **(context or {})
        }

        return self.check_reality(code_context)

    def review_architecture(self, architecture: Dict[str, Any]) -> RealityCheck:
        """
        Marvin reviews architecture with reality checks.
        """
        arch_context = {
            "type": "architecture",
            "components": len(architecture.get("components", [])),
            "complexity": architecture.get("complexity", 0.0),
            **architecture
        }

        return self.check_reality(arch_context)

    def check_quality(self, quality_metrics: Dict[str, Any]) -> RealityCheck:
        """
        Marvin checks quality. No BS allowed.
        """
        quality_context = {
            "type": "quality",
            "test_coverage": quality_metrics.get("test_coverage", 0.0),
            "technical_debt": quality_metrics.get("technical_debt", 0.0),
            "code_smells": quality_metrics.get("code_smells", 0),
            **quality_metrics
        }

        return self.check_reality(quality_context)

    def _is_over_engineered(self, context: Dict[str, Any]) -> bool:
        """Check if something is over-engineered"""
        complexity = context.get("complexity", 0.0)
        components = context.get("components", [])

        if complexity > 0.8:
            return True
        if len(components) > 20:
            return True

        return False

    def _has_scope_creep(self, context: Dict[str, Any]) -> bool:
        """Check if there's scope creep"""
        scope_creep_score = context.get("scope_creep_score", 0.0)
        if scope_creep_score > 0.7:
            return True

        # Check for expanding scope indicators
        if "started_as" in context and "now_is" in context:
            if len(context["now_is"]) > len(context["started_as"]) * 2:
                return True

        return False

    def _has_tool_addiction(self, context: Dict[str, Any]) -> bool:
        """Check for tool addiction"""
        total_tools = context.get("total_tools", 0)
        if total_tools > 100:
            return True

        return False

    def _is_pointless(self, context: Dict[str, Any]) -> bool:
        """Check if work is pointless"""
        # Check for indicators of pointless work
        if context.get("pointless", False):
            return True

        # Check for work that doesn't solve real problems
        if not context.get("solves_real_problem", True):
            return True

        return False

    def _save_check(self, check: RealityCheck) -> None:
        try:
            """Save reality check to file"""
            check_file = self.data_dir / f"{check.check_id}.json"
            with open(check_file, 'w', encoding='utf-8') as f:
                json.dump(check.to_dict(), f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_check: {e}", exc_info=True)
            raise
    def get_status(self) -> Dict[str, Any]:
        """Get Marvin's status"""
        return {
            "total_checks": len(self.checks),
            "total_rabbit_holes": len(self.rabbit_holes),
            "recent_checks": [c.to_dict() for c in self.checks[-10:]],
            "recent_rabbit_holes": [h.to_dict() for h in self.rabbit_holes[-5:]],
            "marvin_verdict": "Life. Don't talk to me about life. But the work is real. So there's that."
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Marvin Reality Checker - Give Marvin Real Work")
    parser.add_argument("--check", type=str, help="Check reality of something (code, architecture, quality)")
    parser.add_argument("--detect-holes", action="store_true", help="Detect rabbit holes")
    parser.add_argument("--status", action="store_true", help="Get Marvin's status")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    marvin = MarvinRealityChecker()

    if args.check:
        # Simple reality check
        check = marvin.check_reality({"type": "general", "context": args.check})
        if args.json:
            print(json.dumps(check.to_dict(), indent=2))
        else:
            print(f"\n🤖 Marvin's Reality Check")
            print("="*60)
            print(f"Level: {check.level.value}")
            print(f"Message: {check.message}")
            print(f"Marvin: {check.marvin_comment}")

    elif args.detect_holes:
        # Detect rabbit holes
        project = {
            "total_tools": 172,
            "scope_creep_score": 0.8,
            "complexity_score": 0.9
        }
        holes = marvin.detect_rabbit_holes(project)
        if args.json:
            print(json.dumps([h.to_dict() for h in holes], indent=2))
        else:
            print(f"\n🤖 Marvin's Rabbit Hole Detection")
            print("="*60)
            for hole in holes:
                print(f"\n🕳️  {hole.hole_type.upper()} (Depth: {hole.depth}/10)")
                print(f"   {hole.description}")
                print(f"   Marvin: {hole.marvin_comment}")

    elif args.status:
        status = marvin.get_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print(f"\n🤖 Marvin's Status")
            print("="*60)
            print(f"Total Checks: {status['total_checks']}")
            print(f"Rabbit Holes Detected: {status['total_rabbit_holes']}")
            print(f"\nMarvin's Verdict: {status['marvin_verdict']}")

    else:
        parser.print_help()
        print("\n🤖 Marvin Reality Checker - Give Marvin Real Work")
        print("   'Life. Don't talk to me about life.'")
        print("   'But the work is real. So there's that.'")

