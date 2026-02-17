#!/usr/bin/env python3
"""
Scheduled Windows System Diagnostics Runner

Runs both Memory Integrity and Event Viewer diagnostics on a schedule,
saving timestamped reports for historical tracking.

Author: <COMPANY_NAME> LLC
Date: 2025-01-XX
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/scheduled_diagnostics.log'),
            logging.StreamHandler()
        ]
    )
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ScheduledDiagnostics")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def ensure_logs_directory() -> Path:
    try:
        """Ensure logs directory exists"""
        log_dir = Path("logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        return log_dir


    except Exception as e:
        logger.error(f"Error in ensure_logs_directory: {e}", exc_info=True)
        raise
def ensure_data_directory() -> Path:
    try:
        """Ensure data directory exists"""
        data_dir = Path("data")
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir


    except Exception as e:
        logger.error(f"Error in ensure_data_directory: {e}", exc_info=True)
        raise
def run_memory_integrity_diagnostic(hours_back: int = 24) -> Dict[str, Any]:
    """
    Run Memory Integrity diagnostic.

    Args:
        hours_back: Number of hours to look back

    Returns:
        Dictionary with diagnostic results
    """
    logger.info("Running Memory Integrity diagnostic...")

    try:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/python/diagnose_windows_memory_integrity.py",
                "--report", "NUL"  # Suppress file output, we'll handle it
            ],
            capture_output=True,
            text=True,
            check=False,
            cwd=Path.cwd()
        )

        if result.returncode == 0:
            logger.info("Memory Integrity diagnostic completed successfully")
            return {
                "status": "success",
                "output": result.stdout,
                "error": None
            }
        else:
            logger.warning(f"Memory Integrity diagnostic returned code {result.returncode}")
            return {
                "status": "warning",
                "output": result.stdout,
                "error": result.stderr
            }

    except Exception as e:
        logger.error(f"Error running Memory Integrity diagnostic: {e}")
        return {
            "status": "error",
            "output": None,
            "error": str(e)
        }


def run_event_viewer_monitor(hours_back: int = 24) -> Dict[str, Any]:
    """
    Run Event Viewer monitoring diagnostic.

    Args:
        hours_back: Number of hours to look back

    Returns:
        Dictionary with diagnostic results
    """
    logger.info(f"Running Event Viewer monitor (last {hours_back} hours)...")

    try:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/python/monitor_windows_events.py",
                "--hours", str(hours_back),
                "--report", "NUL"  # Suppress file output, we'll handle it
            ],
            capture_output=True,
            text=True,
            check=False,
            cwd=Path.cwd()
        )

        if result.returncode == 0:
            logger.info("Event Viewer monitor completed successfully")
            return {
                "status": "success",
                "output": result.stdout,
                "error": None
            }
        else:
            logger.warning(f"Event Viewer monitor returned code {result.returncode}")
            return {
                "status": "warning",
                "output": result.stdout,
                "error": result.stderr
            }

    except Exception as e:
        logger.error(f"Error running Event Viewer monitor: {e}")
        return {
            "status": "error",
            "output": None,
            "error": str(e)
        }


def load_diagnostic_report(report_path: Path) -> Dict[str, Any]:
    """Load diagnostic report from JSON file"""
    try:
        if report_path.exists():
            with open(report_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Could not load report from {report_path}: {e}")
    return {}


def generate_summary_report(
    memory_integrity_report: Path,
    event_viewer_report: Path,
    memory_result: Dict[str, Any],
    event_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate summary report combining both diagnostics.

    Args:
        memory_integrity_report: Path to Memory Integrity report
        event_viewer_report: Path to Event Viewer report
        memory_result: Memory Integrity diagnostic result
        event_result: Event Viewer diagnostic result

    Returns:
        Combined summary report
    """
    timestamp = datetime.now().isoformat()

    # Load reports if available
    memory_data = load_diagnostic_report(memory_integrity_report)
    event_data = load_diagnostic_report(event_viewer_report)

    # Extract summary information
    summary = {
        "timestamp": timestamp,
        "memory_integrity": {
            "status": memory_result["status"],
            "report_loaded": bool(memory_data),
            "diagnostic": memory_data.get("diagnostic", {}) if memory_data else {},
        },
        "event_viewer": {
            "status": event_result["status"],
            "report_loaded": bool(event_data),
            "summary": event_data.get("summary", {}) if event_data else {},
            "critical_events_count": len(event_data.get("critical_events", [])) if event_data else 0,
            "memory_integrity_blocks": len(event_data.get("memory_integrity_issues", [])) if event_data else 0,
        },
        "overall_status": "healthy"
    }

    # Determine overall status
    issues_found = 0

    # Check Memory Integrity issues
    if memory_data and memory_data.get("diagnostic", {}).get("errors"):
        issues_found += len(memory_data["diagnostic"]["errors"])

    # Check Event Viewer issues
    if event_data:
        summary_count = event_data.get("summary", {})
        if summary_count:
            issues_found += summary_count.get("critical_errors", 0)
            issues_found += summary_count.get("memory_integrity_blocks", 0)
            issues_found += summary_count.get("hardware_issues", 0)
            issues_found += summary_count.get("driver_issues", 0)

    if issues_found > 0:
        if issues_found > 10:
            summary["overall_status"] = "critical"
        elif issues_found > 5:
            summary["overall_status"] = "warning"
        else:
            summary["overall_status"] = "minor_issues"

    summary["total_issues_found"] = issues_found

    return summary


def run_scheduled_diagnostics(hours_back: int = 24) -> int:
    try:
        """
        Run scheduled diagnostics and save reports.

        Args:
            hours_back: Number of hours to look back for events

        Returns:
            Exit code (0 = success, 1 = error)
        """
        timestamp = datetime.now()
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")

        logger.info("="*80)
        logger.info(f"Starting scheduled diagnostics at {timestamp.isoformat()}")
        logger.info("="*80)

        # Ensure directories exist
        ensure_logs_directory()
        data_dir = ensure_data_directory()

        # Create timestamped report directory
        report_dir = data_dir / "diagnostic_reports" / timestamp_str
        report_dir.mkdir(parents=True, exist_ok=True)

        # Run Memory Integrity diagnostic
        memory_result = run_memory_integrity_diagnostic(hours_back=hours_back)

        # Run with actual report file
        memory_report_path = report_dir / "memory_integrity_diagnostic.json"
        memory_result2 = subprocess.run(
            [
                sys.executable,
                "scripts/python/diagnose_windows_memory_integrity.py",
                "--report", str(memory_report_path)
            ],
            capture_output=True,
            text=True,
            check=False,
            cwd=Path.cwd()
        )

        # Run Event Viewer monitor
        event_result = run_event_viewer_monitor(hours_back=hours_back)

        # Run with actual report file
        event_report_path = report_dir / "event_viewer_health_report.json"
        event_result2 = subprocess.run(
            [
                sys.executable,
                "scripts/python/monitor_windows_events.py",
                "--hours", str(hours_back),
                "--report", str(event_report_path)
            ],
            capture_output=True,
            text=True,
            check=False,
            cwd=Path.cwd()
        )

        # Generate summary report
        summary = generate_summary_report(
            memory_report_path,
            event_report_path,
            memory_result,
            event_result
        )

        # Save summary report
        summary_path = report_dir / "summary_report.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Reports saved to: {report_dir}")
        logger.info(f"Overall Status: {summary['overall_status'].upper()}")
        logger.info(f"Total Issues Found: {summary['total_issues_found']}")

        # Log summary to console
        print("\n" + "="*80)
        print("SCHEDULED DIAGNOSTICS SUMMARY")
        print("="*80)
        print(f"Timestamp: {summary['timestamp']}")
        print(f"Overall Status: {summary['overall_status'].upper()}")
        print(f"Total Issues: {summary['total_issues_found']}")
        print(f"\nMemory Integrity Status: {summary['memory_integrity']['status']}")
        print(f"Event Viewer Status: {summary['event_viewer']['status']}")
        print(f"Memory Integrity Blocks: {summary['event_viewer']['memory_integrity_blocks']}")
        print(f"Critical Events: {summary['event_viewer']['critical_events_count']}")
        print(f"\nReports saved to: {report_dir}")
        print("="*80 + "\n")

        # Return error code if critical issues found
        if summary["overall_status"] == "critical":
            return 1
        elif summary["overall_status"] == "warning":
            return 0  # Warning is not an error, but should be reviewed
        else:
            return 0


    except Exception as e:
        logger.error(f"Error in run_scheduled_diagnostics: {e}", exc_info=True)
        raise
def main() -> int:
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run scheduled Windows system diagnostics"
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Number of hours to look back for events (default: 24)"
    )

    args = parser.parse_args()

    try:
        return run_scheduled_diagnostics(hours_back=args.hours)
    except KeyboardInterrupt:
        logger.info("Diagnostics interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error running diagnostics: {e}", exc_info=True)
        return 1


if __name__ == "__main__":



    sys.exit(main())