#!/usr/bin/env python3
"""
Audit Host-Level Scheduled Tasks
<COMPANY_NAME> LLC

Audits all host-level scheduled tasks and identifies which should be migrated to NAS Kron:
- Windows Task Scheduler tasks
- Custom recurring tasks
- Scripts designed for scheduling

@JARVIS @MARVIN @SYPHON
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from universal_logging_wrapper import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("HostScheduledTasksAudit")


def get_windows_scheduled_tasks() -> List[Dict[str, Any]]:
    """Get all Windows scheduled tasks"""
    tasks = []

    try:
        # Get all tasks
        result = subprocess.run(
            ["powershell", "-Command", 
             "Get-ScheduledTask | Where-Object {$_.State -eq 'Ready' -or $_.State -eq 'Running'} | "
             "Select-Object TaskName, State, TaskPath, @{Name='Actions';Expression={$_.Actions.Execute}}, "
             "@{Name='Arguments';Expression={$_.Actions.Arguments}}, "
             "@{Name='Triggers';Expression={$_.Triggers}} | ConvertTo-Json -Depth 10"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            tasks_data = json.loads(result.stdout)
            if isinstance(tasks_data, dict):
                tasks_data = [tasks_data]

            for task in tasks_data:
                # Filter for Lumina/custom tasks
                task_name = task.get('TaskName', '')
                if any(keyword in task_name.lower() for keyword in 
                       ['lumina', 'jocasta', 'jarvis', 'syphon', 'r5', 'cursor', 'dropbox', 'wopr']):
                    tasks.append({
                        "name": task_name,
                        "state": task.get('State', 'Unknown'),
                        "path": task.get('TaskPath', ''),
                        "actions": task.get('Actions', []),
                        "arguments": task.get('Arguments', []),
                        "triggers": task.get('Triggers', []),
                        "source": "Windows Task Scheduler"
                    })
    except Exception as e:
        logger.error(f"Error getting Windows tasks: {e}")

    return tasks


def find_schedulable_scripts(project_root: Path) -> List[Dict[str, Any]]:
    """Find scripts that should be scheduled"""
    scripts = []

    schedulable_keywords = [
        "cron", "scheduled", "recurring", "daily", "weekly", "monthly",
        "periodic", "automation", "daemon", "sync", "backup", "cleanup"
    ]

    scripts_dir = project_root / "scripts" / "python"

    if not scripts_dir.exists():
        return scripts

    for script_file in scripts_dir.glob("*.py"):
        try:
            with open(script_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

                # Check for scheduling indicators
                has_keywords = any(keyword in content.lower() for keyword in schedulable_keywords)
                has_schedule_comment = re.search(r'schedule[:\s]+(.+)', content, re.IGNORECASE)
                has_cron_comment = '# cron' in content.lower() or '# scheduled' in content.lower()

                if has_keywords or has_schedule_comment or has_cron_comment:
                    schedule = None
                    if has_schedule_comment:
                        schedule = has_schedule_comment.group(1).strip()

                    scripts.append({
                        "script": script_file.name,
                        "path": str(script_file),
                        "schedule_hint": schedule,
                        "indicators": {
                            "has_keywords": has_keywords,
                            "has_schedule_comment": bool(has_schedule_comment),
                            "has_cron_comment": has_cron_comment
                        }
                    })
        except Exception:
            pass

    return scripts


def analyze_task_for_migration(task: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze if task should be migrated to NAS Kron"""
    should_migrate = False
    reason = ""
    priority = "low"

    name = task.get("name", "").lower()
    path = task.get("path", "").lower()

    # Check if it's a Lumina/custom task
    if any(keyword in name for keyword in ['lumina', 'jocasta', 'jarvis', 'syphon', 'r5']):
        should_migrate = True
        reason = "Lumina system task - should be centralized"
        priority = "high"

    # Check if it's a development/maintenance task
    elif any(keyword in name for keyword in ['cursor', 'workspace', 'sync', 'backup', 'cleanup']):
        should_migrate = True
        reason = "Development/maintenance task - should be centralized"
        priority = "medium"

    # Check if it's a system task (probably shouldn't migrate)
    elif 'microsoft' in path or 'windows' in path:
        should_migrate = False
        reason = "Windows system task - keep on host"
        priority = "low"

    return {
        "should_migrate": should_migrate,
        "reason": reason,
        "priority": priority
    }


def main():
    try:
        """Audit host-level scheduled tasks"""
        project_root = Path(__file__).parent.parent.parent

        print("=" * 80)
        print("HOST-LEVEL SCHEDULED TASKS AUDIT")
        print("=" * 80)
        print()

        # 1. Get Windows Scheduled Tasks
        print("📋 Windows Task Scheduler Tasks:")
        print("-" * 80)
        windows_tasks = get_windows_scheduled_tasks()

        migration_candidates = []

        for task in windows_tasks:
            analysis = analyze_task_for_migration(task)

            print(f"\n✓ {task['name']}")
            print(f"  State: {task['state']}")
            print(f"  Path: {task['path']}")
            if task.get('actions'):
                print(f"  Action: {task['actions']}")
            if task.get('arguments'):
                print(f"  Arguments: {task['arguments']}")

            if analysis['should_migrate']:
                print(f"  ⚠️  MIGRATION CANDIDATE: {analysis['reason']}")
                print(f"  Priority: {analysis['priority']}")
                migration_candidates.append({
                    **task,
                    **analysis
                })
            else:
                print(f"  ℹ️  Keep on host: {analysis['reason']}")

        if not windows_tasks:
            print("  No custom Windows scheduled tasks found")

        print()

        # 2. Find schedulable scripts
        print("📜 Scripts Designed for Scheduling:")
        print("-" * 80)
        schedulable_scripts = find_schedulable_scripts(project_root)

        for script in schedulable_scripts[:20]:  # Show first 20
            print(f"\n✓ {script['script']}")
            print(f"  Path: {script['path']}")
            if script.get('schedule_hint'):
                print(f"  Schedule hint: {script['schedule_hint']}")
            print(f"  Indicators: {script['indicators']}")

        if not schedulable_scripts:
            print("  No schedulable scripts found")

        print()

        # 3. Summary
        print("=" * 80)
        print("MIGRATION SUMMARY")
        print("=" * 80)
        print(f"Windows tasks found: {len(windows_tasks)}")
        print(f"Migration candidates: {len(migration_candidates)}")
        print(f"Schedulable scripts: {len(schedulable_scripts)}")
        print()

        if migration_candidates:
            print("🚨 TASKS TO MIGRATE TO NAS KRON:")
            print("-" * 80)
            for candidate in migration_candidates:
                print(f"\n  {candidate['name']}")
                print(f"    Priority: {candidate['priority']}")
                print(f"    Reason: {candidate['reason']}")
                print(f"    Action: {candidate.get('actions', 'N/A')}")
                print(f"    Arguments: {candidate.get('arguments', 'N/A')}")

        # Save report
        report = {
            "audit_date": datetime.now().isoformat(),
            "windows_tasks": windows_tasks,
            "migration_candidates": migration_candidates,
            "schedulable_scripts": schedulable_scripts
        }

        report_file = project_root / "data" / "tasks" / "nas_kron" / "host_tasks_audit.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)

        print()
        print(f"✅ Audit report saved: {report_file}")
        print("=" * 80)

        return 0 if len(migration_candidates) == 0 else 1

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":






    sys.exit(main())