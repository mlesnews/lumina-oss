#!/usr/bin/env python3
"""
Setup Auto-Sync - Configure automatic extension syncing

Sets up automatic syncing of all coding assistant extensions
with minimal extension usage - features incorporated instead.
"""

from pathlib import Path
import json
import subprocess
import sys


def setup_windows_task():
    """Set up Windows Task Scheduler for auto-sync"""
    try:
        project_root = Path(__file__).parent.parent.parent
        script_path = project_root / "scripts" / "python" / "coding_assistant_auto_sync.py"

        # Create task XML
        task_xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-01-18T02:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Actions>
    <Exec>
      <Command>python</Command>
      <Arguments>"{script_path}" --sync-all</Arguments>
    </Exec>
  </Actions>
</Task>'''

        task_file = project_root / "data" / "auto_sync" / "sync_task.xml"
        task_file.parent.mkdir(parents=True, exist_ok=True)

        with open(task_file, 'w', encoding='utf-16') as f:
            f.write(task_xml)

        print(f"✅ Task XML created: {task_file}")
        print(f"   To install: schtasks /create /tn 'JarvisExtensionSync' /xml '{task_file}'")

        return task_file
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in setup_windows_task: {e}", exc_info=True)
        raise


def setup_cron_job():
    try:
        """Set up cron job for auto-sync (Linux/Mac)"""
        project_root = Path(__file__).parent.parent.parent
        script_path = project_root / "scripts" / "python" / "coding_assistant_auto_sync.py"

        # Daily at 2 AM
        cron_entry = f"0 2 * * * cd {project_root} && python {script_path} --sync-all >> {project_root}/data/auto_sync/sync.log 2>&1\n"

        cron_file = project_root / "data" / "auto_sync" / "sync.cron"
        cron_file.parent.mkdir(parents=True, exist_ok=True)

        with open(cron_file, 'w') as f:
            f.write(cron_entry)

        print(f"✅ Cron entry created: {cron_file}")
        print(f"   To install: crontab {cron_file}")

        return cron_file
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in setup_cron_job: {e}", exc_info=True)
        raise


def create_sync_config():
    """Create sync configuration"""
    try:
        project_root = Path(__file__).parent.parent.parent
        config = {
            "auto_sync_enabled": True,
            "sync_interval_hours": 24,
            "check_on_startup": True,
            "notify_on_updates": True,
            "minimal_extensions": True,
            "feature_integration": True,
            "full_accreditation": True,
            "accreditation_updates": True,
            "version_tracking": True
        }

        config_file = project_root / "config" / "auto_sync_config.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)

        print(f"✅ Sync config created: {config_file}")
        return config_file
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in create_sync_config: {e}", exc_info=True)
        raise
def main():
    """Setup auto-sync"""
    print("=" * 80)
    print("🔧 SETTING UP AUTO-SYNC")
    print("=" * 80)
    print()

    print("📋 Configuration:")
    print("   - Minimal extensions: Features incorporated instead")
    print("   - Full accreditation: All original authors credited")
    print("   - Automatic updates: Syncs when originals update")
    print("   - Version tracking: Complete version history")
    print()

    # Create config
    config_file = create_sync_config()

    # Setup scheduled tasks
    import platform
    if platform.system() == "Windows":
        task_file = setup_windows_task()
    else:
        cron_file = setup_cron_job()

    print()
    print("✅ Auto-sync setup complete!")
    print()
    print("🚀 To start syncing:")
    print("   python scripts/python/coding_assistant_auto_sync.py --sync-all")
    print()
    print("🤖 To run as daemon:")
    print("   python scripts/python/coding_assistant_auto_sync.py --daemon")
    print()
    print("=" * 80)


if __name__ == "__main__":

    main()