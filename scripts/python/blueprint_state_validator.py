#!/usr/bin/env python3
"""
Blueprint State Validator

Integrates Blueprint Virtual Simulator with Git Time Travel and Cross-Environment Mirroring
to provide comprehensive state validation and consistency checking.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys

from blueprint_virtual_simulator import BlueprintVirtualSimulator
from git_time_travel import GitTimeTravel
from cross_environment_mirror import CrossEnvironmentMirror

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - ✅ BlueprintValidator - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BlueprintStateValidator:
    """
    Comprehensive Blueprint State Validator

    Combines:
    - Blueprint Virtual Simulator
    - Git Time Travel
    - Cross-Environment Mirroring
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.simulator = BlueprintVirtualSimulator(project_root)
        self.time_travel = GitTimeTravel(project_root)
        self.mirror = CrossEnvironmentMirror(project_root)

    def validate_complete_state(self) -> Dict[str, Any]:
        """Complete state validation"""
        logger.info("🔬 Starting complete state validation...")

        validation = {
            "timestamp": datetime.now().isoformat(),
            "blueprint_simulation": {},
            "git_state": {},
            "environment_mirroring": {},
            "overall_status": "unknown",
            "recommendations": []
        }

        # 1. Blueprint Simulation
        logger.info("  Running blueprint simulation...")
        blueprint_comparison = self.simulator.compare_blueprint_to_state()
        validation["blueprint_simulation"] = {
            "status": blueprint_comparison["overall_status"],
            "alignment": blueprint_comparison["metrics"]["alignment_percentage"],
            "missing": blueprint_comparison["metrics"]["missing_count"],
            "inconsistencies": blueprint_comparison["metrics"]["inconsistencies_count"]
        }

        # 2. Git State
        logger.info("  Checking git state...")
        current_commit = self.time_travel.get_current_commit()
        validation["git_state"] = {
            "current_commit": current_commit["hash"] if current_commit else None,
            "current_branch": self.time_travel.run_git_command(["branch", "--show-current"])[1],
            "has_changes": len(self.time_travel.run_git_command(["status", "--porcelain"])[1]) > 0
        }

        # 3. Environment Mirroring
        logger.info("  Checking environment mirroring...")
        env_comparison = self.mirror.compare_environments()
        validation["environment_mirroring"] = {
            "synchronized": env_comparison["synchronized"],
            "differences": len(env_comparison["differences"])
        }

        # Overall status
        issues = []
        if validation["blueprint_simulation"]["alignment"] < 90:
            issues.append("Blueprint alignment below 90%")
        if validation["blueprint_simulation"]["missing"] > 0:
            issues.append(f"{validation['blueprint_simulation']['missing']} missing components")
        if validation["blueprint_simulation"]["inconsistencies"] > 0:
            issues.append(f"{validation['blueprint_simulation']['inconsistencies']} design inconsistencies")
        if not validation["environment_mirroring"]["synchronized"]:
            issues.append("Environments not synchronized")

        if len(issues) == 0:
            validation["overall_status"] = "healthy"
        elif len(issues) <= 2:
            validation["overall_status"] = "needs_attention"
        else:
            validation["overall_status"] = "requires_action"

        validation["issues"] = issues

        # Generate recommendations
        if validation["blueprint_simulation"]["missing"] > 0:
            validation["recommendations"].append("Run blueprint sync to update missing components")
        if validation["blueprint_simulation"]["inconsistencies"] > 0:
            validation["recommendations"].append("Review and fix design inconsistencies")
        if not validation["environment_mirroring"]["synchronized"]:
            validation["recommendations"].append("Sync all environments to the same commit")

        logger.info(f"✅ Validation complete - Status: {validation['overall_status']}")

        return validation

    def generate_validation_report(self, validation: Optional[Dict[str, Any]] = None) -> str:
        """Generate comprehensive validation report"""
        if validation is None:
            validation = self.validate_complete_state()

        report_lines = [
            "=" * 80,
            "✅ BLUEPRINT STATE VALIDATION REPORT",
            "=" * 80,
            "",
            f"Timestamp: {validation['timestamp']}",
            f"Overall Status: {validation['overall_status'].upper().replace('_', ' ')}",
            "",
            "BLUEPRINT SIMULATION",
            "-" * 80,
            f"Status: {validation['blueprint_simulation']['status']}",
            f"Alignment: {validation['blueprint_simulation']['alignment']:.1f}%",
            f"Missing Components: {validation['blueprint_simulation']['missing']}",
            f"Design Inconsistencies: {validation['blueprint_simulation']['inconsistencies']}",
            "",
            "GIT STATE",
            "-" * 80,
            f"Current Commit: {validation['git_state']['current_commit'][:8] if validation['git_state']['current_commit'] else 'N/A'}",
            f"Current Branch: {validation['git_state']['current_branch'] or 'N/A'}",
            f"Uncommitted Changes: {'⚠️ Yes' if validation['git_state']['has_changes'] else '✅ No'}",
            "",
            "ENVIRONMENT MIRRORING",
            "-" * 80,
            f"Synchronized: {'✅ Yes' if validation['environment_mirroring']['synchronized'] else '❌ No'}",
            f"Differences: {validation['environment_mirroring']['differences']}",
            ""
        ]

        if validation.get("issues"):
            report_lines.extend([
                "ISSUES DETECTED",
                "-" * 80
            ])
            for issue in validation["issues"]:
                report_lines.append(f"  ⚠️ {issue}")
            report_lines.append("")

        if validation.get("recommendations"):
            report_lines.extend([
                "RECOMMENDATIONS",
                "-" * 80
            ])
            for rec in validation["recommendations"]:
                report_lines.append(f"  💡 {rec}")
            report_lines.append("")

        report_lines.append("=" * 80)

        return "\n".join(report_lines)


def main():
    try:
        """CLI entry point"""
        validator = BlueprintStateValidator()

        print("\n" + "=" * 80)
        print("✅ BLUEPRINT STATE VALIDATOR")
        print("=" * 80)
        print()

        # Run validation
        validation = validator.validate_complete_state()

        # Generate and print report
        report = validator.generate_validation_report(validation)
        print(report)

        # Save results
        output_dir = validator.project_root / "data" / "blueprint_validations"
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = output_dir / f"validation_{timestamp}.json"
        report_path = output_dir / f"validation_report_{timestamp}.md"

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(validation, f, indent=2)

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n✅ Results saved:")
        print(f"   JSON: {json_path}")
        print(f"   Report: {report_path}")
        print()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()