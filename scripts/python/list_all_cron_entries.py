#!/usr/bin/env python3
"""
List All Cron Scheduler Entries
<COMPANY_NAME> LLC

Shows all cron scheduler entries:
- Local cron files
- NAS Kron scheduled jobs
- All recurring tasks

@JARVIS @MARVIN @SYPHON
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
import re
from datetime import datetime

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from nas_kron_daemon_manager import NASKronDaemonManager
import logging
logger = logging.getLogger("list_all_cron_entries")


def parse_cron_entry(line: str) -> Dict[str, Any]:
    """Parse a cron entry line"""
    line = line.strip()

    # Skip comments and empty lines
    if not line or line.startswith('#'):
        return None

    # Parse cron format: minute hour day month weekday command
    pattern = r'^(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(.+)$'
    match = re.match(pattern, line)

    if not match:
        return None

    minute, hour, day, month, weekday, command = match.groups()

    # Determine schedule description
    schedule_desc = _describe_schedule(minute, hour, day, month, weekday)

    return {
        "minute": minute,
        "hour": hour,
        "day": day,
        "month": month,
        "weekday": weekday,
        "command": command,
        "schedule": schedule_desc,
        "raw": line
    }

def _describe_schedule(minute: str, hour: str, day: str, month: str, weekday: str) -> str:
    """Describe the schedule in human-readable format"""

    # Every minute
    if minute == "*" and hour == "*" and day == "*" and month == "*" and weekday == "*":
        return "Every minute"

    # Every hour
    if minute != "*" and hour == "*" and day == "*" and month == "*" and weekday == "*":
        return f"Every hour at minute {minute}"

    # Daily
    if minute != "*" and hour != "*" and day == "*" and month == "*" and weekday == "*":
        return f"Daily at {hour}:{minute.zfill(2)}"

    # Weekly
    if minute != "*" and hour != "*" and day == "*" and month == "*" and weekday != "*":
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        if weekday.isdigit():
            day_name = days[int(weekday)] if int(weekday) < 7 else "Unknown"
        else:
            day_name = weekday
        return f"Weekly on {day_name} at {hour}:{minute.zfill(2)}"

    # Monthly
    if minute != "*" and hour != "*" and day != "*" and month == "*" and weekday == "*":
        return f"Monthly on day {day} at {hour}:{minute.zfill(2)}"

    # Custom interval
    if "/" in minute:
        interval = minute.split("/")[1]
        return f"Every {interval} minutes"
    if "/" in hour:
        interval = hour.split("/")[1]
        return f"Every {interval} hours"

    return f"Custom: {minute} {hour} {day} {month} {weekday}"

def list_local_cron_files(project_root: Path) -> List[Dict[str, Any]]:
    """List all local cron files"""
    cron_dir = project_root / "data" / "tasks" / "nas_kron"

    entries = []

    if not cron_dir.exists():
        return entries

    for cron_file in cron_dir.glob("*.cron"):
        try:
            with open(cron_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

                file_entries = []
                description = None

                for line in lines:
                    line = line.strip()

                    # Get description from comment
                    if line.startswith('#'):
                        if '#' in line[1:]:
                            description = line[1:].strip()
                        continue

                    # Parse cron entry
                    entry = parse_cron_entry(line)
                    if entry:
                        entry["file"] = str(cron_file.name)
                        entry["description"] = description
                        file_entries.append(entry)
                        description = None  # Reset after use

                entries.extend(file_entries)
        except Exception as e:
            print(f"Error reading {cron_file}: {e}")

    return entries

def list_nas_cron_jobs(manager: NASKronDaemonManager) -> List[Dict[str, Any]]:
    """List cron jobs from NAS"""
    try:
        jobs = manager.list_nas_cron_jobs()

        entries = []
        for job in jobs:
            entry = parse_cron_entry(job)
            if entry:
                entry["source"] = "NAS"
                entries.append(entry)

        return entries
    except Exception as e:
        print(f"⚠️  Could not list NAS cron jobs: {e}")
        return []

def main():
    try:
        """List all cron entries"""
        project_root = Path(__file__).parent.parent.parent

        print("=" * 80)
        print("CRON SCHEDULER ENTRIES - ALL RECURRING TASKS")
        print("=" * 80)
        print()

        # List local cron files
        print("📁 LOCAL CRON FILES:")
        print("-" * 80)
        local_entries = list_local_cron_files(project_root)

        if local_entries:
            for i, entry in enumerate(local_entries, 1):
                print(f"\n{i}. {entry.get('description', 'No description')}")
                print(f"   Schedule: {entry['schedule']}")
                print(f"   Cron: {entry['minute']} {entry['hour']} {entry['day']} {entry['month']} {entry['weekday']}")
                print(f"   Command: {entry['command'][:100]}...")
                print(f"   File: {entry.get('file', 'N/A')}")
        else:
            print("   No local cron files found")

        print()
        print("=" * 80)
        print("🌐 NAS KRON SCHEDULED JOBS:")
        print("-" * 80)

        # List NAS cron jobs
        manager = NASKronDaemonManager(project_root)
        nas_entries = list_nas_cron_jobs(manager)

        if nas_entries:
            for i, entry in enumerate(nas_entries, 1):
                print(f"\n{i}. {entry.get('description', 'No description')}")
                print(f"   Schedule: {entry['schedule']}")
                print(f"   Cron: {entry['minute']} {entry['hour']} {entry['day']} {entry['month']} {entry['weekday']}")
                print(f"   Command: {entry['command'][:100]}...")
                print(f"   Source: NAS")
        else:
            print("   No NAS cron jobs found (or connection failed)")
            print("   Check NAS SSH configuration if needed")

        # Summary
        print()
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Local cron entries: {len(local_entries)}")
        print(f"NAS cron entries: {len(nas_entries)}")
        print(f"Total recurring tasks: {len(local_entries) + len(nas_entries)}")
        print("=" * 80)

        # Show schedule breakdown
        if local_entries or nas_entries:
            print()
            print("SCHEDULE BREAKDOWN:")
            print("-" * 80)

            all_entries = local_entries + nas_entries
            schedules = {}
            for entry in all_entries:
                schedule = entry['schedule']
                schedules[schedule] = schedules.get(schedule, 0) + 1

            for schedule, count in sorted(schedules.items()):
                print(f"  {schedule}: {count} task(s)")

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()