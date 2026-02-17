#!/usr/bin/env python3
"""
Setup Automated Backup Schedule

Sets up automated backup schedule for local enterprise repository.

Tags: #SCHEDULE #AUTOMATION #BACKUP @JARVIS @LUMINA
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SetupAutomatedBackupSchedule")


def create_windows_task():
    """Create Windows Task Scheduler task for automated backups"""
    script_path = project_root / "scripts" / "python" / "local_enterprise_backup.py"
    python_exe = sys.executable

    # Create task XML
    task_xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-01-07T02:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>"{python_exe}"</Command>
      <Arguments>"{script_path}" --full</Arguments>
      <WorkingDirectory>"{project_root}"</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''

    # Save XML
    xml_file = project_root / "data" / "local_enterprise_backup_task.xml"
    xml_file.parent.mkdir(parents=True, exist_ok=True)
    with open(xml_file, 'w', encoding='utf-16') as f:
        f.write(task_xml)

    # Create task
    try:
        result = subprocess.run(
            ["schtasks", "/Create", "/TN", "LuminaLocalEnterpriseBackup", "/XML", str(xml_file), "/F"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("✅ Windows Task Scheduler task created")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to create task: {e.stderr}")
        return False


def main():
    """Main execution"""
    import platform

    print("=" * 80)
    print("🔧 SETUP AUTOMATED BACKUP SCHEDULE")
    print("=" * 80)
    print()

    system = platform.system()

    if system == "Windows":
        print("Creating Windows Task Scheduler task...")
        if create_windows_task():
            print("✅ Automated backup schedule installed successfully")
            print("   Task Name: LuminaLocalEnterpriseBackup")
            print("   Schedule: Daily at 02:00 UTC")
            print("   Command: python local_enterprise_backup.py --full")
        else:
            print("❌ Failed to install automated backup schedule")
    else:
        print(f"⚠️  Unsupported system: {system}")
        print("   Please manually configure cron or systemd")


if __name__ == "__main__":


    main()