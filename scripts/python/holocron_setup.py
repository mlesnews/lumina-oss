#!/usr/bin/env python3
"""
Holocron Archive Setup Script

Sets up the Holocron Archive for use, including:
- Verifying file structure
- Testing threat monitor
- Creating initial status reports
- Setting up monitoring

Author: Rogue AI Defense Intelligence Team
Date: 2025-01-XX
Classification: ROGUE AI DEFENSE INTELLIGENCE
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
logger = get_logger("holocron_setup")


try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def verify_archive_structure(holocron_path: Path) -> tuple[bool, list[str]]:
    try:
        """
        Verify Holocron Archive structure is complete.

        Returns:
            Tuple of (is_valid, missing_files)
        """
        required_files = [
            "HOLOCRON_INDEX.md",
            "README.md",
            "QUICK_START.md",
            "ACTION_PLAN.md",
            "quick_reference_card.md",
            "executive_summary_ai_agent_threats.md",
            "ai_intelligence_report_2025_01_ai_agent_advancements.md",
            "threat_matrix_ai_agents_2025_01.md",
            "containment_protocols_critical_systems.md",
            "defense_checklist_immediate_actions.md",
            "threat_intelligence_feed.json",
        ]

        missing = []
        for file in required_files:
            if not (holocron_path / file).exists():
                missing.append(file)

        return len(missing) == 0, missing


    except Exception as e:
        logger.error(f"Error in verify_archive_structure: {e}", exc_info=True)
        raise
def test_threat_monitor(holocron_path: Path) -> bool:
    """Test that threat monitor can be imported and initialized."""
    try:
        sys.path.insert(0, str(holocron_path.parent.parent))
        from scripts.python.holocron_threat_monitor import HolocronThreatMonitor

        monitor = HolocronThreatMonitor(holocron_path=holocron_path)
        return True
    except Exception as e:
        print(f"Error testing threat monitor: {e}")
        return False


def create_initial_status(holocron_path: Path) -> None:
    try:
        """Create initial implementation status file."""
        status_file = holocron_path / "IMPLEMENTATION_STATUS.md"
        if not status_file.exists():
            # Status file should already exist, but verify
            print(f"Implementation status file: {status_file.exists()}")


    except Exception as e:
        logger.error(f"Error in create_initial_status: {e}", exc_info=True)
        raise
def generate_setup_report(holocron_path: Path) -> dict:
    """Generate setup verification report."""
    is_valid, missing = verify_archive_structure(holocron_path)
    monitor_works = test_threat_monitor(holocron_path)

    report = {
        "setup_date": "2025-01-XX",
        "archive_path": str(holocron_path),
        "structure_valid": is_valid,
        "missing_files": missing,
        "threat_monitor_works": monitor_works,
        "ready_for_use": is_valid and monitor_works,
        "next_steps": [],
    }

    if not is_valid:
        report["next_steps"].append("Complete missing files in archive")
    if not monitor_works:
        report["next_steps"].append("Fix threat monitor script")
    if is_valid and monitor_works:
        report["next_steps"].extend([
            "Read QUICK_START.md",
            "Print quick_reference_card.md",
            "Begin implementation per ACTION_PLAN.md",
        ])

    return report


def main() -> None:
    try:
        """Main setup function."""
        import argparse

        parser = argparse.ArgumentParser(description="Holocron Archive Setup")
        parser.add_argument(
            "--holocron-path",
            type=Path,
            default=Path("data/holocron"),
            help="Path to Holocron Archive directory",
        )
        parser.add_argument(
            "--verify-only",
            action="store_true",
            help="Only verify structure, don't create files",
        )

        args = parser.parse_args()

        holocron_path = args.holocron_path.resolve()

        if not holocron_path.exists():
            print(f"ERROR: Holocron Archive not found at {holocron_path}")
            print("Please ensure the archive is in the correct location.")
            sys.exit(1)

        print("=" * 60)
        print("Holocron Archive Setup")
        print("=" * 60)
        print(f"Archive path: {holocron_path}\n")

        # Verify structure
        print("Verifying archive structure...")
        is_valid, missing = verify_archive_structure(holocron_path)
        if is_valid:
            print("[OK] Archive structure is complete")
        else:
            print(f"[WARNING] Missing files: {', '.join(missing)}")

        # Test threat monitor
        print("\nTesting threat monitor...")
        if test_threat_monitor(holocron_path):
            print("[OK] Threat monitor is functional")
        else:
            print("[WARNING] Threat monitor has issues (may be expected if dependencies missing)")

        # Generate report
        print("\nGenerating setup report...")
        report = generate_setup_report(holocron_path)

        # Save report
        report_file = holocron_path / "setup_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"[OK] Setup report saved to {report_file}")

        # Print summary
        print("\n" + "=" * 60)
        print("Setup Summary")
        print("=" * 60)
        print(f"Structure valid: {report['structure_valid']}")
        print(f"Threat monitor works: {report['threat_monitor_works']}")
        print(f"Ready for use: {report['ready_for_use']}")

        if report["next_steps"]:
            print("\nNext steps:")
            for i, step in enumerate(report["next_steps"], 1):
                print(f"  {i}. {step}")

        print("\n" + "=" * 60)
        print("Quick Start:")
        print("  1. Read: data/holocron/QUICK_START.md")
        print("  2. Print: data/holocron/quick_reference_card.md")
        print("  3. Follow: data/holocron/ACTION_PLAN.md")
        print("=" * 60)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()