#!/usr/bin/env python3
"""
Setup ULTRON Router Auto-Start

Creates Windows Task Scheduler task to auto-start ULTRON cluster router when Docker Desktop starts.

Tags: #ULTRON #AUTO_START #TASK_SCHEDULER #WINDOWS @JARVIS @LUMINA
"""

import sys
import subprocess
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SetupULTRONRouterAutostart")


def create_task_scheduler_task():
    """Create Windows Task Scheduler task (requires admin)"""
    try:
        python_exe = sys.executable
        auto_start_script = script_dir / "auto_start_ultron_router.py"

        if not auto_start_script.exists():
            logger.error(f"❌ Auto-start script not found: {auto_start_script}")
            return False

        task_name = "LUMINA_ULTRON_Router_AutoStart"

        # Create task XML (simplified, user-level)
        task_xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Auto-start ULTRON Cluster Router API when Docker Desktop starts</Description>
    <Author>LUMINA System</Author>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
      <Delay>PT2M</Delay>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
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
      <Arguments>"{auto_start_script}" --once</Arguments>
      <WorkingDirectory>"{script_dir}"</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''

        # Save XML to project directory
        xml_file = project_root / "scripts" / "ultron_router_autostart_task.xml"

        with open(xml_file, 'w', encoding='utf-16') as f:
            f.write(task_xml)

        logger.info(f"✅ Created task XML: {xml_file}")
        logger.info("")
        logger.info("📋 To create Task Scheduler task (run as Administrator):")
        logger.info("")
        logger.info(f"   schtasks /Create /TN \"{task_name}\" /XML \"{xml_file}\" /F")
        logger.info("")
        logger.info("   Or use Task Scheduler GUI:")
        logger.info("   1. Open Task Scheduler (Win+R → taskschd.msc)")
        logger.info("   2. Action → Import Task")
        logger.info(f"   3. Select: {xml_file}")
        logger.info("   4. Click OK")
        logger.info("")

        # Try to create (may fail without admin)
        try:
            result = subprocess.run(
                ["schtasks", "/Create", "/TN", task_name, "/XML", str(xml_file), "/F"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                logger.info("✅ Task Scheduler task created successfully")
                logger.info(f"   Task Name: {task_name}")
                return True
            else:
                logger.warning(f"⚠️  Could not create task automatically: {result.stderr}")
                logger.info("   Use manual method above (requires admin)")
                return False
        except Exception as e:
            logger.warning(f"⚠️  Could not create task: {e}")
            logger.info("   Use manual method above")
            return False
    except Exception as e:
        logger.error(f"❌ Failed to create task XML: {e}")
        return False


def create_startup_script():
    """Create startup script alternative"""
    startup_script = project_root / "scripts" / "start_ultron_router.bat"
    auto_start_script = script_dir / "auto_start_ultron_router.py"

    bat_content = f'''@echo off
REM Auto-start ULTRON Cluster Router API
REM Waits for Docker Desktop, then starts router

cd /d "{script_dir}"
python "{auto_start_script}" --once
'''

    try:
        with open(startup_script, 'w', encoding='utf-8') as f:
            f.write(bat_content)

        logger.info(f"✅ Created startup script: {startup_script}")
        logger.info("   You can add this to Windows Startup folder if Task Scheduler doesn't work")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create startup script: {e}")
        return False


def main():
    """Main setup"""
    logger.info("=" * 80)
    logger.info("🚀 SETTING UP ULTRON ROUTER AUTO-START")
    logger.info("=" * 80)
    logger.info("")

    # Method 1: Task Scheduler (Recommended)
    logger.info("📋 Method 1: Creating Task Scheduler task...")
    if create_task_scheduler_task():
        logger.info("   ✅ Task Scheduler setup complete")
    else:
        logger.warning("   ⚠️  Task Scheduler setup failed - trying alternative")
        logger.info("")

        # Method 2: Startup script
        logger.info("📋 Method 2: Creating startup script...")
        create_startup_script()
        logger.info("")
        logger.info("   To use startup script:")
        logger.info("   1. Press Win+R")
        logger.info("   2. Type: shell:startup")
        logger.info("   3. Copy start_ultron_router.bat to that folder")

    logger.info("")
    logger.info("=" * 80)
    logger.info("✅ SETUP COMPLETE")
    logger.info("=" * 80)
    logger.info("")
    logger.info("The ULTRON cluster router will now auto-start:")
    logger.info("   - After system login (2 minute delay)")
    logger.info("   - When Docker Desktop starts")
    logger.info("   - Waits for Docker to be ready before starting router")
    logger.info("")
    logger.info("Router will be available at: http://localhost:8080")
    logger.info("")


if __name__ == "__main__":

    main()