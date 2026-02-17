#!/usr/bin/env python3
"""
Migrate Host-Level Tasks to NAS Kron
<COMPANY_NAME> LLC

Migrates host-level scheduled tasks to NAS Kron cron scheduler:
- Windows Task Scheduler tasks (Lumina, Jocasta, etc.)
- Identified schedulable scripts
- Creates cron entries for migration

@JARVIS @MARVIN @SYPHON
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from nas_kron_daemon_manager import NASKronDaemonManager

logger = None
try:
    from universal_logging_wrapper import get_logger
    logger = get_logger("MigrateHostTasksToNAS")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("MigrateHostTasksToNAS")


def get_jocasta_task_details() -> Dict[str, Any]:
    """Get details of Jocasta Nu DailyOps task"""
    try:
        result = subprocess.run(
            ["powershell", "-Command",
             "$task = Get-ScheduledTask -TaskName 'Lumina_JocastaNu_DailyOps'; "
             "$info = Get-ScheduledTaskInfo -TaskName 'Lumina_JocastaNu_DailyOps'; "
             "$triggers = $task.Triggers; "
             "$actions = $task.Actions; "
             "[PSCustomObject]@{"
             "  TaskName = $task.TaskName;"
             "  Description = $task.Description;"
             "  NextRunTime = $info.NextRunTime;"
             "  LastRunTime = $info.LastRunTime;"
             "  TriggerType = $triggers[0].CimClass.CimClassName;"
             "  DaysInterval = $triggers[0].DaysInterval;"
             "  StartBoundary = $triggers[0].StartBoundary;"
             "  Repetition = $triggers[0].Repetition;"
             "  Execute = $actions[0].Execute;"
             "  Arguments = $actions[0].Arguments;"
             "} | ConvertTo-Json -Depth 10"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        logger.error(f"Error getting Jocasta task details: {e}")

    return {}


def windows_trigger_to_cron(trigger: Dict[str, Any]) -> str:
    """Convert Windows trigger to cron format"""
    trigger_type = trigger.get('TriggerType', '')
    start_boundary = trigger.get('StartBoundary', '')

    # Daily trigger
    if 'Daily' in trigger_type:
        # Parse time from StartBoundary (format: YYYY-MM-DDTHH:MM:SS)
        if start_boundary:
            try:
                dt = datetime.fromisoformat(start_boundary.replace('Z', '+00:00'))
                hour = dt.hour
                minute = dt.minute
                return f"{minute} {hour} * * *"
            except Exception:
                pass
        # Default to midnight
        return "0 0 * * *"

    # Weekly trigger
    elif 'Weekly' in trigger_type:
        days_of_week = trigger.get('DaysOfWeek', 1)  # 1 = Sunday, 2 = Monday, etc.
        if start_boundary:
            try:
                dt = datetime.fromisoformat(start_boundary.replace('Z', '+00:00'))
                hour = dt.hour
                minute = dt.minute
                # Convert days_of_week (bitmask) to cron day
                # Windows: 1=Sun, 2=Mon, 4=Tue, 8=Wed, 16=Thu, 32=Fri, 64=Sat
                # Cron: 0=Sun, 1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat
                day = 0  # Default Sunday
                if days_of_week & 2:  # Monday
                    day = 1
                elif days_of_week & 4:  # Tuesday
                    day = 2
                elif days_of_week & 8:  # Wednesday
                    day = 3
                elif days_of_week & 16:  # Thursday
                    day = 4
                elif days_of_week & 32:  # Friday
                    day = 5
                elif days_of_week & 64:  # Saturday
                    day = 6
                return f"{minute} {hour} * * {day}"
            except Exception:
                pass
        return "0 0 * * 1"  # Default Monday

    # Monthly trigger
    elif 'Monthly' in trigger_type:
        days_of_month = trigger.get('DaysOfMonth', [1])
        day = days_of_month[0] if days_of_month else 1
        if start_boundary:
            try:
                dt = datetime.fromisoformat(start_boundary.replace('Z', '+00:00'))
                hour = dt.hour
                minute = dt.minute
                return f"{minute} {hour} {day} * *"
            except Exception:
                pass
        return f"0 0 {day} * *"

    # Default: daily at midnight
    return "0 0 * * *"


def create_migration_cron_entries(project_root: Path) -> List[Path]:
    """Create cron entries for tasks to migrate"""
    cron_files = []

    # 1. Jocasta Nu DailyOps
    jocasta_details = get_jocasta_task_details()

    if jocasta_details:
        # Convert Windows path to NAS path
        script_path = jocasta_details.get('Arguments', '').strip('"')
        # Assume script is in Dropbox, will be accessible from NAS
        # Convert to NAS path format
        nas_script_path = script_path.replace('C:\\Users\\mlesn\\Dropbox', '/volume1/docker/jarvis/Dropbox')
        nas_script_path = nas_script_path.replace('\\', '/')

        # Get schedule
        trigger = {
            'TriggerType': jocasta_details.get('TriggerType', 'MSFT_TaskDailyTrigger'),
            'StartBoundary': jocasta_details.get('StartBoundary', ''),
            'DaysInterval': jocasta_details.get('DaysInterval', 1)
        }
        cron_schedule = windows_trigger_to_cron(trigger)

        cron_content = f"""# Jocasta Nu - Head Librarian Daily Operations
# Migrated from Windows Task Scheduler: Lumina_JocastaNu_DailyOps
# Description: Scan, classify, catalog holocrons (Jupyter Notebooks)
# Original schedule: {jocasta_details.get('StartBoundary', 'Daily')}
{cron_schedule} cd {project_root} && python {nas_script_path} >> logs/jocasta_daily_ops.log 2>&1
"""

        cron_file = project_root / "data" / "tasks" / "nas_kron" / "jocasta_nu_daily_ops.cron"
        cron_file.parent.mkdir(parents=True, exist_ok=True)

        with open(cron_file, 'w', encoding='utf-8') as f:
            f.write(cron_content)

        cron_files.append(cron_file)
        logger.info(f"✅ Created: {cron_file.name}")

    # 2. Cursor Workspace Sync (if not already scheduled)
    cursor_sync_cron = project_root / "data" / "tasks" / "nas_kron" / "cursor_workspace_sync.cron"
    if not cursor_sync_cron.exists():
        cron_content = f"""# Cursor Workspace Sync
# Syncs workspace settings between workspace and non-workspace modes
# Run every 6 hours
0 */6 * * * cd {project_root} && python scripts/python/cursor_workspace_sync_cron.py >> logs/cursor_workspace_sync.log 2>&1
"""

        with open(cursor_sync_cron, 'w', encoding='utf-8') as f:
            f.write(cron_content)

        cron_files.append(cursor_sync_cron)
        logger.info(f"✅ Created: {cursor_sync_cron.name}")

    # 3. Scheduled Diagnostics (if exists)
    diagnostics_script = project_root / "scripts" / "python" / "run_scheduled_diagnostics.py"
    if diagnostics_script.exists():
        diagnostics_cron = project_root / "data" / "tasks" / "nas_kron" / "scheduled_diagnostics.cron"
        if not diagnostics_cron.exists():
            cron_content = f"""# Scheduled System Diagnostics
# Runs memory integrity and event viewer diagnostics
# Run daily at 2 AM
0 2 * * * cd {project_root} && python scripts/python/run_scheduled_diagnostics.py >> logs/scheduled_diagnostics.log 2>&1
"""

            with open(diagnostics_cron, 'w', encoding='utf-8') as f:
                f.write(cron_content)

            cron_files.append(diagnostics_cron)
            logger.info(f"✅ Created: {diagnostics_cron.name}")

    return cron_files


def main():
    try:
        """Migrate host tasks to NAS Kron"""
        project_root = Path(__file__).parent.parent.parent

        print("=" * 80)
        print("MIGRATE HOST-LEVEL TASKS TO NAS KRON")
        print("=" * 80)
        print()

        # Load audit results
        audit_file = project_root / "data" / "tasks" / "nas_kron" / "host_tasks_audit.json"

        if not audit_file.exists():
            print("❌ Audit file not found. Run audit_host_scheduled_tasks.py first.")
            return 1

        with open(audit_file, 'r', encoding='utf-8') as f:
            audit_data = json.load(f)

        migration_candidates = audit_data.get('migration_candidates', [])

        print(f"Found {len(migration_candidates)} task(s) to migrate:")
        for candidate in migration_candidates:
            print(f"  - {candidate['name']} ({candidate['priority']} priority)")
        print()

        # Create cron entries
        print("📝 Creating cron entries...")
        cron_files = create_migration_cron_entries(project_root)

        print()
        print("=" * 80)
        print("MIGRATION COMPLETE")
        print("=" * 80)
        print(f"Cron files created: {len(cron_files)}")
        for cron_file in cron_files:
            print(f"  ✓ {cron_file.name}")
        print()
        print("Next steps:")
        print("1. Review cron files in: data/tasks/nas_kron/")
        print("2. Deploy to NAS Kron:")
        print("   python scripts/python/deploy_all_cron_to_nas.py")
        print("3. Disable Windows scheduled tasks after successful migration")
        print("=" * 80)

        return 0

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":






    sys.exit(main())