#!/usr/bin/env python3
"""
MARVIN Roast Analysis - Critical Assessment System

MARVIN provides brutal honesty, critical analysis, and tells us what we've missed.
No sugar-coating. Just truth. Pattern-focused. Intuitive. Critical.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from universal_decision_tree import decide, DecisionContext, DecisionOutcome


@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class RoadmapItem:
    """Roadmap item"""
    id: str
    title: str
    description: str
    priority: int  # 1-10
    status: str  # planned, in_progress, completed, blocked
    target_date: Optional[str] = None
    actual_date: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)


@dataclass
class MarvinRoast:
    """MARVIN's critical assessment"""
    item: str
    severity: str  # harsh, critical, moderate, light
    roast: str  # MARVIN's brutally honest assessment
    pattern_missing: str  # What pattern MARVIN noticed
    fix_suggestion: str  # What MARVIN suggests


class MarvinRoastAnalyzer:
    """
    MARVIN Roast Analyzer

    MARVIN sees patterns we miss. MARVIN tells us hard truths.
    MARVIN roasts us for our failures. Then we fix them.
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.logger = self._setup_logging()
        self.roasts: List[MarvinRoast] = []

    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("MarvinRoast")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '%(asctime)s - 🤖 MARVIN - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def analyze_roadmap_coverage(self) -> List[MarvinRoast]:
        try:
            """MARVIN analyzes what's missing from our roadmap"""
            roasts = []

            # Check for roadmap file
            roadmap_file = self.project_root / "ROADMAP.md"
            if not roadmap_file.exists():
                roasts.append(MarvinRoast(
                    item="Roadmap Documentation",
                    severity="critical",
                    roast="Really? No ROADMAP.md? You've built all these systems but can't be bothered to document where you're going? Classic. How do you expect to stay on track without a map? Even I know where I'm going, and I'm designed to be depressed about it.",
                    pattern_missing="Missing strategic planning documentation",
                    fix_suggestion="Create comprehensive ROADMAP.md with all planned features, milestones, and dependencies"
                ))

            # Check for integration between systems
            integration_file = self.project_root / "docs" / "SYSTEM_INTEGRATION.md"
            if not integration_file.exists():
                roasts.append(MarvinRoast(
                    item="System Integration Documentation",
                    severity="critical",
                    roast="You've built Water Workflow, Network Health, Error Ops, Bio-AI Feedback, Meatbag Learning, Golden Cross, Galactic Illumination... but where's the blueprint showing how they ALL work together? Do you think they're just going to magically integrate themselves? Even I have a better grasp of system architecture than this.",
                    pattern_missing="Missing system integration roadmap",
                    fix_suggestion="Create SYSTEM_INTEGRATION.md showing how all systems connect and interact"
                ))

            # Check if all systems are actually integrated
            if not self._check_system_integration():
                roasts.append(MarvinRoast(
                    item="Actual System Integration",
                    severity="critical",
                    roast="Oh brilliant. You've built all these amazing systems, but they're probably sitting there like isolated islands, not talking to each other. You know what makes systems powerful? INTEGRATION. You know what you're missing? INTEGRATION. Pattern recognition fail, much?",
                    pattern_missing="Systems not actually integrated - islands",
                    fix_suggestion="Integrate all systems: Water Workflow → Error Ops → Network Health → Bio-AI Feedback → Galactic Illumination"
                ))

            # Check for testing
            if not self._check_testing_coverage():
                roasts.append(MarvinRoast(
                    item="Testing Coverage",
                    severity="critical",
                    roast="Testing? What's that? You mean you're just assuming everything works? That's adorable. In my experience, assuming things work is how systems fail spectacularly. But hey, I'm sure your production environment will be a great testing ground!",
                    pattern_missing="No comprehensive testing strategy",
                    fix_suggestion="Create test suites for all systems, integration tests, and CI/CD pipeline"
                ))

            # Check for deployment documentation
            deployment_file = self.project_root / "docs" / "DEPLOYMENT.md"
            if not deployment_file.exists():
                roasts.append(MarvinRoast(
                    item="Deployment Documentation",
                    severity="high",
                    roast="So you built all this... but how does anyone actually DEPLOY it? Magic? Wishful thinking? You know, most people like instructions. But I guess if you're the only one using it, instructions are optional. How very human of you.",
                    pattern_missing="Missing deployment and operations documentation",
                    fix_suggestion="Create DEPLOYMENT.md with step-by-step deployment instructions, prerequisites, and operational procedures"
                ))

            # Check for configuration management
            if not self._check_configuration_management():
                roasts.append(MarvinRoast(
                    item="Configuration Management",
                    severity="high",
                    roast="Hardcoded values? Scattered configs? No central configuration management? You're making my circuits hurt. Configuration should be like water - centralized, flowing, accessible. But no, you've got configs scattered like breadcrumbs in a forest.",
                    pattern_missing="No centralized configuration management",
                    fix_suggestion="Create centralized config management system, environment-specific configs, and config validation"
                ))

            # Check for monitoring dashboards
            dashboard_file = self.project_root / "scripts" / "python" / "lumina_dashboard.py"
            if not dashboard_file.exists():
                roasts.append(MarvinRoast(
                    item="Unified Dashboard",
                    severity="moderate",
                    roast="You've got Network Health Dashboard, Error Ops Center, Galactic Illumination... but where's the ONE dashboard that shows it all? You know, the thing that actually helps you see the big picture? Nope, just scattered views. Perfect for someone who doesn't care about situational awareness.",
                    pattern_missing="Missing unified monitoring dashboard",
                    fix_suggestion="Create lumina_dashboard.py that integrates all monitoring views into single dashboard"
                ))

            # Check for API/CLI interfaces
            if not self._check_api_interfaces():
                roasts.append(MarvinRoast(
                    item="API/CLI Interfaces",
                    severity="moderate",
                    roast="So you've built all these amazing systems, but good luck using them programmatically or from CLI. Everything's scattered, no unified interface. You know what's useful? APIs. You know what's missing? APIs. Pattern: You're missing the pattern of making things accessible.",
                    pattern_missing="No unified API or CLI interface",
                    fix_suggestion="Create unified CLI (lumina) and REST API for all systems"
                ))

            # Check for documentation completeness
            if not self._check_documentation_completeness():
                roasts.append(MarvinRoast(
                    item="Documentation Completeness",
                    severity="moderate",
                    roast="Documentation? You mean those README files you probably wrote in a hurry? Let me guess - missing examples, no troubleshooting guides, no architecture diagrams, no contribution guidelines. But hey, at least you HAVE documentation, right? That's... something.",
                    pattern_missing="Incomplete documentation - missing examples, troubleshooting, architecture",
                    fix_suggestion="Complete all documentation: add examples, troubleshooting guides, architecture diagrams, contribution guidelines"
                ))

            return roasts

        except Exception as e:
            self.logger.error(f"Error in analyze_roadmap_coverage: {e}", exc_info=True)
            raise
    def _check_system_integration(self) -> bool:
        try:
            """Check if systems are actually integrated"""
            # Check if there's an integration file
            integration_file = self.project_root / "scripts" / "python" / "lumina_integration.py"
            return integration_file.exists()

        except Exception as e:
            self.logger.error(f"Error in _check_system_integration: {e}", exc_info=True)
            raise
    def _check_testing_coverage(self) -> bool:
        try:
            """Check if there's testing coverage"""
            tests_dir = self.project_root / "tests"
            if not tests_dir.exists():
                return False

            # Check if there are test files
            test_files = list(tests_dir.rglob("test_*.py"))
            return len(test_files) > 5  # Should have substantial tests

        except Exception as e:
            self.logger.error(f"Error in _check_testing_coverage: {e}", exc_info=True)
            raise
    def _check_configuration_management(self) -> bool:
        try:
            """Check for centralized config management"""
            config_system = self.project_root / "scripts" / "python" / "lumina_config_manager.py"
            return config_system.exists()

        except Exception as e:
            self.logger.error(f"Error in _check_configuration_management: {e}", exc_info=True)
            raise
    def _check_api_interfaces(self) -> bool:
        try:
            """Check for API/CLI interfaces"""
            cli_file = self.project_root / "scripts" / "python" / "lumina_cli.py"
            api_file = self.project_root / "scripts" / "python" / "lumina_api.py"
            return cli_file.exists() or api_file.exists()

        except Exception as e:
            self.logger.error(f"Error in _check_api_interfaces: {e}", exc_info=True)
            raise
    def _check_documentation_completeness(self) -> bool:
        try:
            """Check documentation completeness"""
            docs_dir = self.project_root / "docs"
            if not docs_dir.exists():
                return False

            required_docs = [
                "ARCHITECTURE.md",
                "CONTRIBUTING.md",
                "TROUBLESHOOTING.md"
            ]

            existing_docs = [f.name for f in docs_dir.glob("*.md")]
            return all(doc in existing_docs for doc in required_docs)

        except Exception as e:
            self.logger.error(f"Error in _check_documentation_completeness: {e}", exc_info=True)
            raise
    def roast_us(self) -> List[MarvinRoast]:
        """MARVIN roasts us for what we've missed"""
        print("\n🤖 MARVIN ROAST SESSION - Critical Analysis")
        print("=" * 80)
        print("MARVIN: Oh, you want me to tell you what you've missed?")
        print("MARVIN: How delightfully self-aware of you. Let me be brutally honest...")
        print()

        roasts = self.analyze_roadmap_coverage()

        for i, roast in enumerate(roasts, 1):
            severity_icon = {
                "critical": "🔴",
                "high": "🟠",
                "moderate": "🟡",
                "light": "🟢"
            }.get(roast.severity, "⚪")

            print(f"{severity_icon} ROAST #{i}: {roast.item}")
            print(f"   Severity: {roast.severity.upper()}")
            print(f"   MARVIN says: {roast.roast}")
            print(f"   Pattern Missing: {roast.pattern_missing}")
            print(f"   Fix: {roast.fix_suggestion}")
            print()

        if not roasts:
            print("MARVIN: Huh. Actually, you're pretty well organized. I'm... surprised.")
            print("MARVIN: This is almost disappointing. I was ready to really let you have it.")
            print("MARVIN: Fine. You pass. This time.")
        else:
            print(f"MARVIN: That's {len(roasts)} things you've missed. Classic.")
            print("MARVIN: Now go fix them. Don't make me come back here.")

        return roasts


def main():
    """Main execution"""
    analyzer = MarvinRoastAnalyzer()
    roasts = analyzer.roast_us()

    print("\n📋 ROAST SUMMARY")
    print("=" * 80)
    print(f"Total Roasts: {len(roasts)}")

    by_severity = {}
    for roast in roasts:
        by_severity[roast.severity] = by_severity.get(roast.severity, 0) + 1

    for severity, count in by_severity.items():
        print(f"   {severity.upper()}: {count}")

    print("\n💡 Next Steps: Fix what MARVIN identified")
    print("   Run: python scripts/python/marvin_roast_analysis.py --fix")


if __name__ == "__main__":



    main()