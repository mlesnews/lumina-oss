#!/usr/bin/env python3
"""
Setup Joint Review BAU Schedule

Sets up the Jarvis & Marvin joint review as a regular BAU workflow.
Can be scheduled via cron, task scheduler, or workflow system.

Tags: #BAU #SCHEDULE #WORKFLOW #AUTOMATION @LUMINA
"""

import sys
from pathlib import Path
import json

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from jarvis_marvin_joint_review_bau import run_bau_workflow
import logging
logger = logging.getLogger("setup_joint_review_bau_schedule")



def setup_cron_schedule():
    """Setup cron schedule for BAU workflow"""
    cron_entry = f"""
# Jarvis & Marvin Joint Review BAU Workflow
# Runs daily at 2 AM
0 2 * * * cd {project_root} && python scripts/python/jarvis_marvin_joint_review_bau.py >> data/joint_reviews/bau_log.txt 2>&1

# Or run after each significant session (manual trigger)
# python scripts/python/jarvis_marvin_joint_review_bau.py
"""
    return cron_entry


def setup_windows_task_scheduler():
    """Setup Windows Task Scheduler entry"""
    task_xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <DailyTrigger>
      <StartBoundary>2026-01-18T02:00:00</StartBoundary>
      <Enabled>true</Enabled>
    </DailyTrigger>
  </Triggers>
  <Actions>
    <Exec>
      <Command>python</Command>
      <Arguments>"{project_root}\\scripts\\python\\jarvis_marvin_joint_review_bau.py"</Arguments>
      <WorkingDirectory>{project_root}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""
    return task_xml


def main():
    try:
        """Setup BAU schedule"""
        print("=" * 80)
        print("🔧 SETTING UP JOINT REVIEW BAU SCHEDULE")
        print("=" * 80)
        print()

        # Generate schedule files
        cron_entry = setup_cron_schedule()
        task_xml = setup_windows_task_scheduler()

        # Save to files
        cron_file = project_root / "data" / "joint_reviews" / "bau_cron.txt"
        task_file = project_root / "data" / "joint_reviews" / "bau_task_scheduler.xml"

        cron_file.parent.mkdir(parents=True, exist_ok=True)

        with open(cron_file, 'w') as f:
            f.write(cron_entry)

        with open(task_file, 'w', encoding='utf-16') as f:
            f.write(task_xml)

        print("✅ Schedule files created:")
        print(f"   Cron: {cron_file}")
        print(f"   Task Scheduler: {task_file}")
        print()
        print("📋 To activate:")
        print("   Linux/Mac: Add cron entry from bau_cron.txt")
        print("   Windows: Import bau_task_scheduler.xml to Task Scheduler")
        print()
        print("💡 Or run manually:")
        print("   python scripts/python/jarvis_marvin_joint_review_bau.py")
        print()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()