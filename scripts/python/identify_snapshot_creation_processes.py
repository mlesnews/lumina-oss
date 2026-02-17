#!/usr/bin/env python3
"""
Identify Snapshot Creation Processes

Breadcrumb 1: Identify and disable snapshot creation processes
Part of Tape Library Team Prevention Strategies

Searches for scripts, scheduled tasks, and processes that create snapshots.
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("IdentifySnapshotCreationProcesses")


def search_for_snapshot_references() -> List[Dict[str, Any]]:
    """Search codebase for snapshot creation references"""
    findings = []

    logger.info("Searching for snapshot creation references...")

    # Search Python files
    python_files = list(project_root.rglob("*.py"))
    for py_file in python_files:
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')

            # Check for snapshot-related patterns
            if any(pattern in content.lower() for pattern in [
                "snapshot_main", "time_travel", "create.*snapshot",
                "copytree", "shutil.copytree"
            ]):
                findings.append({
                    "file": str(py_file.relative_to(project_root)),
                    "type": "python",
                    "evidence": _extract_evidence(content, "snapshot"),
                    "action": "review"
                })
        except Exception as e:
            logger.debug(f"Error reading {py_file}: {e}")

    # Search PowerShell files
    ps_files = list(project_root.rglob("*.ps1"))
    for ps_file in ps_files:
        try:
            content = ps_file.read_text(encoding='utf-8', errors='ignore')

            if any(pattern in content.lower() for pattern in [
                "snapshot", "time_travel", "copy-item.*-recurse",
                "copytree"
            ]):
                findings.append({
                    "file": str(ps_file.relative_to(project_root)),
                    "type": "powershell",
                    "evidence": _extract_evidence(content, "snapshot"),
                    "action": "review"
                })
        except Exception as e:
            logger.debug(f"Error reading {ps_file}: {e}")

    return findings


def _extract_evidence(content: str, keyword: str) -> List[str]:
    """Extract lines containing keyword as evidence"""
    lines = content.split('\n')
    evidence = []
    for i, line in enumerate(lines, 1):
        if keyword.lower() in line.lower():
            evidence.append(f"Line {i}: {line.strip()[:100]}")
    return evidence[:5]  # Limit to 5 lines


def check_scheduled_tasks() -> List[Dict[str, Any]]:
    """Check Windows scheduled tasks for snapshot-related tasks"""
    tasks = []

    logger.info("Checking Windows scheduled tasks...")

    try:
        # Get all scheduled tasks
        result = subprocess.run(
            ["schtasks", "/query", "/fo", "csv", "/v"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if any(keyword in line.lower() for keyword in ["snapshot", "backup", "time_travel"]):
                    tasks.append({
                        "type": "scheduled_task",
                        "evidence": line.strip()[:200],
                        "action": "review"
                    })
    except Exception as e:
        logger.debug(f"Error checking scheduled tasks: {e}")

    return tasks


def check_cron_jobs() -> List[Dict[str, Any]]:
    """Check for cron jobs or scheduled scripts"""
    cron_jobs = []

    logger.info("Checking for cron jobs or scheduled scripts...")

    # Check common cron locations (if on Linux/Mac, but we're on Windows)
    # For Windows, check task scheduler instead (already done)

    # Check for any scripts that might be scheduled
    scripts_dir = project_root / "scripts"
    if scripts_dir.exists():
        for script_file in scripts_dir.rglob("*"):
            if script_file.suffix in [".py", ".ps1", ".sh"]:
                try:
                    content = script_file.read_text(encoding='utf-8', errors='ignore')
                    if "cron" in content.lower() or "schedule" in content.lower():
                        if "snapshot" in content.lower() or "time_travel" in content.lower():
                            cron_jobs.append({
                                "file": str(script_file.relative_to(project_root)),
                                "type": "scheduled_script",
                                "evidence": "Contains cron/schedule and snapshot references",
                                "action": "review"
                            })
                except Exception:
                    pass

    return cron_jobs


def identify_snapshot_creation_processes() -> Dict[str, Any]:
    """Identify all snapshot creation processes"""
    logger.info("=" * 70)
    logger.info("IDENTIFYING SNAPSHOT CREATION PROCESSES")
    logger.info("=" * 70)
    logger.info("")

    # Search codebase
    codebase_findings = search_for_snapshot_references()

    # Check scheduled tasks
    scheduled_tasks = check_scheduled_tasks()

    # Check cron jobs
    cron_jobs = check_cron_jobs()

    # Compile results
    result = {
        "timestamp": datetime.now().isoformat(),
        "codebase_findings": codebase_findings,
        "scheduled_tasks": scheduled_tasks,
        "cron_jobs": cron_jobs,
        "total_findings": len(codebase_findings) + len(scheduled_tasks) + len(cron_jobs),
        "recommendations": []
    }

    # Generate recommendations
    if codebase_findings:
        result["recommendations"].append(
            f"Review {len(codebase_findings)} code files that reference snapshots"
        )

    if scheduled_tasks:
        result["recommendations"].append(
            f"Review {len(scheduled_tasks)} scheduled tasks related to snapshots"
        )

    if cron_jobs:
        result["recommendations"].append(
            f"Review {len(cron_jobs)} scheduled scripts related to snapshots"
        )

    if not result["total_findings"]:
        result["recommendations"].append(
            "No obvious snapshot creation processes found - may be manual or external"
        )

    logger.info("")
    logger.info("=" * 70)
    logger.info("RESULTS")
    logger.info("=" * 70)
    logger.info(f"Codebase findings: {len(codebase_findings)}")
    logger.info(f"Scheduled tasks: {len(scheduled_tasks)}")
    logger.info(f"Cron jobs: {len(cron_jobs)}")
    logger.info(f"Total findings: {result['total_findings']}")
    logger.info("")

    if codebase_findings:
        logger.info("Codebase findings:")
        for finding in codebase_findings[:10]:  # Show first 10
            logger.info(f"  - {finding['file']} ({finding['type']})")

    return result


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(
            description="Identify snapshot creation processes"
        )
        parser.add_argument(
            "--output",
            type=str,
            default="data/tape_library_team/snapshot_creation_processes.json",
            help="Output JSON file"
        )

        args = parser.parse_args()

        result = identify_snapshot_creation_processes()

        # Save result
        output_path = project_root / args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        logger.info(f"Results saved to: {output_path}")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    sys.exit(main())