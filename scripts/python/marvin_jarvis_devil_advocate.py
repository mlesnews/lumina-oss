#!/usr/bin/env python3
"""
Marvin as JARVIS's Devil's Advocate

Marvin provides critical review, reality checks, and devil's advocate perspective
for JARVIS development. He roasts, critiques, and ensures quality throughout
the development process.

Tags: #MARVIN #JARVIS #DEVIL_ADVOCATE #CODE_REVIEW #QUALITY @MARVIN @JARVIS
"""

import sys
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
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MarvinDevilAdvocate")


class CritiqueLevel(Enum):
    """Level of critique"""
    GENTLE = "gentle"           # Polite suggestions
    FIRM = "firm"               # Strong recommendations
    HARSH = "harsh"             # Brutal honesty
    ROAST = "roast"             # Full roast mode


class MarvinDevilAdvocate:
    """
    Marvin as Devil's Advocate for JARVIS Development

    Provides:
    - Critical code review
    - Reality checks
    - Quality assurance
    - Brutal honesty
    - Roasting when needed
    """

    def __init__(self, critique_level: CritiqueLevel = CritiqueLevel.FIRM):
        """Initialize Marvin as devil's advocate"""
        self.critique_level = critique_level
        self.project_root = project_root
        self.reviews: List[Dict[str, Any]] = []

        logger.info("=" * 80)
        logger.info("🤖 MARVIN: DEVIL'S ADVOCATE MODE ACTIVATED")
        logger.info("=" * 80)
        logger.info(f"   Critique Level: {critique_level.value.upper()}")
        logger.info("   Ready to roast JARVIS development")
        logger.info("")

    def review_code(self, file_path: str, code_content: str, 
                   feature_name: str, stage: str) -> Dict[str, Any]:
        """Review code and provide critical feedback"""
        issues = []
        warnings = []
        suggestions = []
        roast_points = []

        # Check for common issues
        if not code_content.strip():
            issues.append("❌ Code is empty - this is not implementation, it's a placeholder!")
            roast_points.append("Empty file? Really? That's not code, that's a TODO comment with delusions of grandeur.")

        # Check for proper error handling
        if "try:" in code_content and "except Exception as e:" in code_content:
            if "pass" in code_content.split("except")[1].split("\n")[0:3]:
                warnings.append("⚠️  Silent exception handling - errors will be swallowed")
                roast_points.append("Silent failures? That's like a doctor saying 'oops' and walking away.")

        # Check for documentation
        if not code_content.startswith('"""') and not code_content.startswith("'''"):
            warnings.append("⚠️  Missing module docstring")
            roast_points.append("No documentation? Code that can't explain itself is like a mime with amnesia.")

        # Check for logging
        if "logger" not in code_content and "logging" not in code_content:
            warnings.append("⚠️  No logging - how will you debug this?")
            roast_points.append("No logging? Good luck debugging when this breaks at 3 AM.")

        # Check for tests
        if "def test_" not in code_content and "import pytest" not in code_content:
            suggestions.append("💡 Consider adding unit tests")
            roast_points.append("No tests? That's not development, that's wishful thinking.")

        # Check for proper imports
        if "import sys" in code_content and "sys.path" not in code_content:
            warnings.append("⚠️  sys imported but sys.path not used - unnecessary import")

        # Check for hardcoded values
        if code_content.count('"') > 20 and '"localhost"' in code_content:
            warnings.append("⚠️  Hardcoded values detected - use configuration")
            roast_points.append("Hardcoded values? That's not configuration, that's technical debt with a capital D.")

        # Generate roast based on critique level
        roast = self._generate_roast(issues, warnings, roast_points)

        review = {
            "file_path": file_path,
            "feature_name": feature_name,
            "stage": stage,
            "review_date": datetime.now().isoformat(),
            "issues": issues,
            "warnings": warnings,
            "suggestions": suggestions,
            "roast": roast,
            "severity": "HIGH" if issues else "MEDIUM" if warnings else "LOW"
        }

        self.reviews.append(review)
        return review

    def review_implementation_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Review implementation plan and provide reality check"""
        issues = []
        warnings = []
        roast_points = []

        # Check for unrealistic timelines
        if plan.get("estimated_hours", 0) < 10:
            warnings.append("⚠️  Estimate seems low - are you accounting for debugging, testing, integration?")
            roast_points.append("10 hours? That's optimistic. I've seen 'simple' features take 40 hours after you account for reality.")

        # Check for missing dependencies
        if not plan.get("dependencies"):
            warnings.append("⚠️  No dependencies listed - most features depend on others")
            roast_points.append("No dependencies? Everything is connected. This isn't a feature, it's a dependency waiting to happen.")

        # Check for success criteria
        if not plan.get("success_criteria"):
            issues.append("❌ No success criteria - how will you know if it works?")
            roast_points.append("No success criteria? That's like a race without a finish line. You'll just run forever.")

        roast = self._generate_roast(issues, warnings, roast_points)

        return {
            "plan_review": True,
            "issues": issues,
            "warnings": warnings,
            "roast": roast,
            "reality_check": "PASS" if not issues else "FAIL"
        }

    def review_feature_completeness(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        try:
            """Review if a feature is actually complete"""
            issues = []
            roast_points = []

            status = feature.get("status", "unknown")
            implementation_file = feature.get("implementation_file", "")

            if status == "implemented":
                # Check if file actually exists and has content
                if implementation_file:
                    file_path = self.project_root / implementation_file
                    if not file_path.exists():
                        issues.append(f"❌ File marked as implemented but doesn't exist: {implementation_file}")
                        roast_points.append("Marked as implemented but file doesn't exist? That's not implementation, that's creative accounting.")
                    else:
                        content = file_path.read_text(encoding='utf-8')
                        if len(content) < 100:
                            issues.append(f"⚠️  File exists but is very small ({len(content)} bytes) - might be a stub")
                            roast_points.append("100 bytes? That's not implementation, that's a function signature with commitment issues.")

            roast = self._generate_roast(issues, [], roast_points)

            return {
                "feature": feature.get("name", "unknown"),
                "issues": issues,
                "roast": roast,
                "actually_complete": len(issues) == 0
            }

        except Exception as e:
            self.logger.error(f"Error in review_feature_completeness: {e}", exc_info=True)
            raise
    def _generate_roast(self, issues: List[str], warnings: List[str], 
                       roast_points: List[str]) -> str:
        """Generate roast based on critique level"""
        if self.critique_level == CritiqueLevel.GENTLE:
            if issues:
                return f"🤔 I notice a few things that might need attention: {len(issues)} issues found."
            return "👍 Looks reasonable, but consider the suggestions above."

        elif self.critique_level == CritiqueLevel.FIRM:
            if issues:
                return f"⚠️  This has {len(issues)} issues that need to be addressed before it's production-ready."
            if warnings:
                return f"💡 This works, but {len(warnings)} improvements would make it better."
            return "✅ This looks solid. Keep up the good work."

        elif self.critique_level == CritiqueLevel.HARSH:
            if issues:
                return f"❌ {len(issues)} critical issues. This is not ready. Fix these before claiming it's done."
            if warnings:
                return f"⚠️  {len(warnings)} warnings. This might work, but it's not good enough yet."
            return "✅ Acceptable, but could be better."

        else:  # ROAST
            if roast_points:
                return "🔥 " + " ".join(roast_points[:3])  # Top 3 roast points
            if issues:
                return f"🔥 {len(issues)} issues? Really? This is what you call implementation?"
            return "🔥 Surprisingly, this doesn't completely suck. But don't let it go to your head."

    def print_review(self, review: Dict[str, Any]):
        """Print review in Marvin's style"""
        print("")
        print("=" * 80)
        print("🤖 MARVIN'S REVIEW")
        print("=" * 80)
        print(f"File: {review['file_path']}")
        print(f"Feature: {review['feature_name']}")
        print(f"Stage: {review['stage']}")
        print("")

        if review['issues']:
            print("❌ ISSUES:")
            for issue in review['issues']:
                print(f"   {issue}")
            print("")

        if review['warnings']:
            print("⚠️  WARNINGS:")
            for warning in review['warnings']:
                print(f"   {warning}")
            print("")

        if review['suggestions']:
            print("💡 SUGGESTIONS:")
            for suggestion in review['suggestions']:
                print(f"   {suggestion}")
            print("")

        print("🔥 MARVIN'S ROAST:")
        print(f"   {review['roast']}")
        print("")
        print("=" * 80)
        print("")


def get_marvin_devil_advocate(critique_level: CritiqueLevel = CritiqueLevel.FIRM) -> MarvinDevilAdvocate:
    """Get Marvin as devil's advocate (singleton)"""
    global _marvin_instance
    if '_marvin_instance' not in globals():
        _marvin_instance = MarvinDevilAdvocate(critique_level)
    return _marvin_instance


# Initialize on import
_marvin_instance = None
