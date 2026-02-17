#!/usr/bin/env python3
"""
Validate and Mirror - Unified Command

One command to:
1. Run blueprint virtual simulator
2. Validate state
3. Check environment mirroring
4. Generate comprehensive report
"""

import sys
from pathlib import Path
from blueprint_state_validator import BlueprintStateValidator
from cross_environment_mirror import CrossEnvironmentMirror
from git_time_travel import GitTimeTravel
import logging
logger = logging.getLogger("validate_and_mirror")


def main():
    try:
        """Unified validation and mirroring"""
        project_root = Path(__file__).parent.parent.parent

        print("\n" + "=" * 80)
        print("🔬 VALIDATE & MIRROR - UNIFIED COMMAND")
        print("=" * 80)
        print()

        # 1. Blueprint State Validation
        print("Step 1: Blueprint State Validation...")
        validator = BlueprintStateValidator(project_root)
        validation = validator.validate_complete_state()

        print(f"   Status: {validation['overall_status']}")
        print(f"   Alignment: {validation['blueprint_simulation']['alignment']:.1f}%")
        print()

        # 2. Environment Mirroring Check
        print("Step 2: Environment Mirroring Check...")
        mirror = CrossEnvironmentMirror(project_root)
        env_comparison = mirror.compare_environments()

        print(f"   Synchronized: {'✅ Yes' if env_comparison['synchronized'] else '❌ No'}")
        print(f"   Differences: {env_comparison['differences']}")
        print()

        # 3. Git State
        print("Step 3: Git State Check...")
        time_travel = GitTimeTravel(project_root)
        current_commit = time_travel.get_current_commit()

        if current_commit:
            print(f"   Current Commit: {current_commit['hash'][:8]}")
            print(f"   Branch: {time_travel.run_git_command(['branch', '--show-current'])[1]}")
        print()

        # 4. Generate Report
        print("Step 4: Generating Comprehensive Report...")
        report = validator.generate_validation_report(validation)

        # Save report
        output_dir = project_root / "data" / "blueprint_validations"
        output_dir.mkdir(parents=True, exist_ok=True)

        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = output_dir / f"comprehensive_validation_{timestamp}.md"

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"   ✅ Report saved: {report_path}")
        print()

        # 5. Summary
        print("=" * 80)
        print("📊 SUMMARY")
        print("=" * 80)
        print(f"Overall Status: {validation['overall_status'].upper().replace('_', ' ')}")
        print(f"Blueprint Alignment: {validation['blueprint_simulation']['alignment']:.1f}%")
        print(f"Environments Synchronized: {'✅' if env_comparison['synchronized'] else '❌'}")
        print(f"Issues Detected: {len(validation.get('issues', []))}")
        print()

        if validation.get('recommendations'):
            print("💡 Recommendations:")
            for rec in validation['recommendations']:
                print(f"   • {rec}")
            print()

        print("=" * 80)
        print()

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()