#!/usr/bin/env python3
"""
Install VA Startup Task

Installs Windows Task Scheduler task to start Virtual Assistants on system boot.

Tags: #INSTALL #SERVICE #AUTO_START #VA @JARVIS @LUMINA
"""

import sys
import subprocess
from pathlib import Path

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

logger = get_logger("InstallVAStartupTask")


def create_va_startup_task():
    """Create Windows Task Scheduler task for VA orchestrator"""
    import subprocess

    orchestrator_script = project_root / "scripts" / "python" / "ai_managed_va_orchestrator.py"
    python_exe = sys.executable

    # Create task XML
    task_xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
      <Delay>PT1M</Delay>
    </BootTrigger>
    <LogonTrigger>
      <Enabled>true</Enabled>
      <Delay>PT30S</Delay>
    </LogonTrigger>
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
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>"{python_exe}"</Command>
      <Arguments>"{orchestrator_script}" --start --daemon</Arguments>
      <WorkingDirectory>"{project_root}"</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''

    # Save XML
    xml_file = project_root / "data" / "lumina_va_startup_task.xml"
    xml_file.parent.mkdir(parents=True, exist_ok=True)
    with open(xml_file, 'w', encoding='utf-16') as f:
        f.write(task_xml)

    logger.info(f"✅ Task XML created: {xml_file}")

    # Create task
    try:
        result = subprocess.run(
            ["schtasks", "/Create", "/TN", "LuminaVAOrchestrator", "/XML", str(xml_file), "/F"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("✅ Windows Task Scheduler task created: LuminaVAOrchestrator")
        logger.info("   Task will start VAs on system boot and user logon")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to create task: {e.stderr}")
        return False


def check_existing_task():
    """Check if task already exists"""
    try:
        result = subprocess.run(
            ["schtasks", "/Query", "/TN", "LuminaVAOrchestrator"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            logger.info("✅ Task 'LuminaVAOrchestrator' already exists")
            return True
        return False
    except Exception:
        return False


def main():
    """Main execution"""
    import platform

    print("=" * 80)
    print("🔧 INSTALL VA STARTUP TASK")
    print("=" * 80)
    print()

    if platform.system() != "Windows":
        print(f"⚠️  Unsupported system: {platform.system()}")
        print("   This script is for Windows only")
        return

    # Check if task exists
    if check_existing_task():
        print("Task 'LuminaVAOrchestrator' already exists.")
        response = input("Do you want to recreate it? (y/n): ")
        if response.lower() != 'y':
            print("Skipping task creation.")
            return
        # Delete existing task
        try:
            subprocess.run(
                ["schtasks", "/Delete", "/TN", "LuminaVAOrchestrator", "/F"],
                capture_output=True,
                text=True,
                check=True
            )
            print("✅ Existing task deleted")
        except Exception as e:
            print(f"⚠️  Could not delete existing task: {e}")

    print("Creating Windows Task Scheduler task...")
    if create_va_startup_task():
        print()
        print("✅ VA Startup Task installed successfully!")
        print()
        print("Task Details:")
        print("  Name: LuminaVAOrchestrator")
        print("  Triggers:")
        print("    - System Boot (1 minute delay)")
        print("    - User Logon (30 second delay)")
        print("  Action: Starts AI-Managed VA Orchestrator")
        print("  Result: All VAs will auto-start on boot")
        print()
        print("To verify:")
        print("  schtasks /Query /TN LuminaVAOrchestrator")
        print()
        print("To test immediately:")
        print("  schtasks /Run /TN LuminaVAOrchestrator")
    else:
        print("❌ Failed to install VA startup task")
        print("   You may need to run as Administrator")


if __name__ == "__main__":


    main()