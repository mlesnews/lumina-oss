#!/usr/bin/env python3
"""
Show All Scheduled Tasks
<COMPANY_NAME> LLC

Comprehensive view of ALL scheduled/recurring tasks:
- Cron scheduler entries (local and NAS)
- Documented scheduled tasks
- Automation tasks
- Recurring workflows

@JARVIS @MARVIN @SYPHON
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
import json
import re

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from list_all_cron_entries import list_local_cron_files, list_nas_cron_jobs, parse_cron_entry
from nas_kron_daemon_manager import NASKronDaemonManager
import logging
logger = logging.getLogger("show_all_scheduled_tasks")


def find_documented_tasks(project_root: Path) -> List[Dict[str, Any]]:
    try:
        """Find documented scheduled tasks"""
        tasks = []

        # Check WOPR automation
        wopr_file = project_root / "data" / "wopr_plans" / "WOPR_AUTOMATION.md"
        if wopr_file.exists():
            with open(wopr_file, 'r', encoding='utf-8') as f:
                content = f.read()

                # Extract scheduled tasks
                daily_pattern = r'- \*\*(\d{2}:\d{2})\*\*: (.+)'
                weekly_pattern = r'- \*\*(\w+day \d{2}:\d{2})\*\*: (.+)'
                monthly_pattern = r'- \*\*(\w+ of month)\*\*: (.+)'

                for match in re.finditer(daily_pattern, content):
                    time, task = match.groups()
                    tasks.append({
                        "type": "documented",
                        "schedule": f"Daily at {time}",
                        "task": task,
                        "source": "WOPR_AUTOMATION.md",
                        "category": "WOPR"
                    })

                for match in re.finditer(weekly_pattern, content):
                    schedule, task = match.groups()
                    tasks.append({
                        "type": "documented",
                        "schedule": f"Weekly on {schedule}",
                        "task": task,
                        "source": "WOPR_AUTOMATION.md",
                        "category": "WOPR"
                    })

                for match in re.finditer(monthly_pattern, content):
                    schedule, task = match.groups()
                    tasks.append({
                        "type": "documented",
                        "schedule": f"Monthly: {schedule}",
                        "task": task,
                        "source": "WOPR_AUTOMATION.md",
                        "category": "WOPR"
                    })

        return tasks

    except Exception as e:
        logger.error(f"Error in find_documented_tasks: {e}", exc_info=True)
        raise
def find_automation_scripts(project_root: Path) -> List[Dict[str, Any]]:
    """Find automation scripts that might be scheduled"""
    scripts_dir = project_root / "scripts" / "python"

    tasks = []

    automation_keywords = [
        "automation", "scheduled", "cron", "daemon", "recurring",
        "daily", "weekly", "monthly", "hourly", "periodic"
    ]

    if scripts_dir.exists():
        for script_file in scripts_dir.glob("*.py"):
            try:
                with open(script_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                    # Check for automation indicators
                    if any(keyword in content.lower() for keyword in automation_keywords):
                        # Try to extract schedule info
                        schedule_match = re.search(r'schedule[:\s]+(.+)', content, re.IGNORECASE)
                        schedule = schedule_match.group(1).strip() if schedule_match else "Unknown"

                        tasks.append({
                            "type": "script",
                            "script": script_file.name,
                            "schedule": schedule,
                            "path": str(script_file),
                            "category": "Automation"
                        })
            except Exception:
                pass

    return tasks

def main():
    try:
        """Show all scheduled tasks"""
        project_root = Path(__file__).parent.parent.parent

        print("=" * 80)
        print("ALL SCHEDULED / RECURRING TASKS - COMPREHENSIVE VIEW")
        print("=" * 80)
        print()

        all_tasks = []

        # 1. Local Cron Files
        print("📁 LOCAL CRON FILES:")
        print("-" * 80)
        local_entries = list_local_cron_files(project_root)

        for entry in local_entries:
            all_tasks.append({
                "type": "cron_local",
                "schedule": entry['schedule'],
                "cron": f"{entry['minute']} {entry['hour']} {entry['day']} {entry['month']} {entry['weekday']}",
                "command": entry['command'],
                "description": entry.get('description', 'No description'),
                "file": entry.get('file', 'N/A')
            })
            print(f"✓ {entry.get('description', 'Cron job')}")
            print(f"  Schedule: {entry['schedule']}")
            print(f"  Cron: {entry['minute']} {entry['hour']} {entry['day']} {entry['month']} {entry['weekday']}")
            print(f"  File: {entry.get('file', 'N/A')}")
            print()

        if not local_entries:
            print("  No local cron files found")
            print()

        # 2. NAS Kron Jobs
        print("🌐 NAS KRON SCHEDULED JOBS:")
        print("-" * 80)
        manager = NASKronDaemonManager(project_root)
        nas_entries = list_nas_cron_jobs(manager)

        for entry in nas_entries:
            all_tasks.append({
                "type": "cron_nas",
                "schedule": entry['schedule'],
                "cron": f"{entry['minute']} {entry['hour']} {entry['day']} {entry['month']} {entry['weekday']}",
                "command": entry['command'],
                "description": entry.get('description', 'No description'),
                "source": "NAS"
            })
            print(f"✓ {entry.get('description', 'NAS Cron job')}")
            print(f"  Schedule: {entry['schedule']}")
            print(f"  Cron: {entry['minute']} {entry['hour']} {entry['day']} {entry['month']} {entry['weekday']}")
            print()

        if not nas_entries:
            print("  No NAS cron jobs found (or connection failed)")
            print("  Note: NAS SSH authentication may need configuration")
            print()

        # 3. Documented Tasks
        print("📋 DOCUMENTED SCHEDULED TASKS:")
        print("-" * 80)
        documented_tasks = find_documented_tasks(project_root)

        for task in documented_tasks:
            all_tasks.append(task)
            print(f"✓ {task['task']}")
            print(f"  Schedule: {task['schedule']}")
            print(f"  Source: {task['source']}")
            print(f"  Category: {task['category']}")
            print()

        if not documented_tasks:
            print("  No documented scheduled tasks found")
            print()

        # 4. Automation Scripts
        print("🤖 AUTOMATION SCRIPTS (Potential Scheduled Tasks):")
        print("-" * 80)
        automation_scripts = find_automation_scripts(project_root)

        # Filter to most relevant
        relevant_scripts = [s for s in automation_scripts if any(
            keyword in s['script'].lower() for keyword in 
            ['daemon', 'cron', 'scheduled', 'automation', 'recurring']
        )]

        for script in relevant_scripts[:10]:  # Show first 10
            all_tasks.append(script)
            print(f"✓ {script['script']}")
            print(f"  Schedule: {script['schedule']}")
            print(f"  Category: {script['category']}")
            print()

        if not relevant_scripts:
            print("  No automation scripts found")
            print()

        # Summary
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total scheduled/recurring tasks: {len(all_tasks)}")
        print(f"  - Local cron entries: {len(local_entries)}")
        print(f"  - NAS cron entries: {len(nas_entries)}")
        print(f"  - Documented tasks: {len(documented_tasks)}")
        print(f"  - Automation scripts: {len(relevant_scripts)}")
        print("=" * 80)

        # Schedule breakdown
        if all_tasks:
            print()
            print("SCHEDULE BREAKDOWN:")
            print("-" * 80)

            schedules = {}
            for task in all_tasks:
                schedule = task.get('schedule', 'Unknown')
                schedules[schedule] = schedules.get(schedule, 0) + 1

            for schedule, count in sorted(schedules.items(), key=lambda x: x[1], reverse=True):
                print(f"  {schedule}: {count} task(s)")

        # Save to JSON
        output_file = project_root / "data" / "tasks" / "nas_kron" / "all_scheduled_tasks.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "generated_at": datetime.now().isoformat(),
                "total_tasks": len(all_tasks),
                "tasks": all_tasks
            }, f, indent=2, default=str)

        print()
        print(f"✅ Full task list saved to: {output_file}")

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    from datetime import datetime



    main()