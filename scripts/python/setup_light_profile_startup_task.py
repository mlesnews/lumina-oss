#!/usr/bin/env python3
"""
JARVIS - Setup Light Profile Startup Task
USS Lumina - @scotty (Windows Systems Architect)

Creates a scheduled task to apply the "Light" profile on system boot/logon
and periodically to ensure lighting stays enabled.

@JARVIS @LIGHTING @STARTUP @AUTOMATION @LUMINA
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVIS_LightProfileStartup")


def create_startup_task() -> Dict[str, Any]:
    """Create scheduled task to apply Light profile on boot and periodically"""

    logger.info("=" * 70)
    logger.info("JARVIS - SETTING UP LIGHT PROFILE STARTUP TASK")
    logger.info("USS Lumina - @scotty (Windows Systems Architect)")
    logger.info("=" * 70)
    logger.info("")

    script_path = project_root / "scripts" / "python" / "apply_light_profile_on_startup.py"
    python_exe = sys.executable

    # Create task XML
    task_xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}</Date>
    <Author>JARVIS @scotty - USS Lumina</Author>
    <Description>JARVIS Light Profile Startup - Applies Light profile on boot and periodically to ensure lighting stays enabled</Description>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
      <Delay>PT30S</Delay>
    </LogonTrigger>
    <TimeTrigger>
      <Repetition>
        <Interval>PT15M</Interval>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
      <StartBoundary>{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}</StartBoundary>
      <Enabled>true</Enabled>
    </TimeTrigger>
    <BootTrigger>
      <Enabled>true</Enabled>
      <Delay>PT1M</Delay>
    </BootTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-18</UserId>
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
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <DeleteExpiredTaskAfter>PT0S</DeleteExpiredTaskAfter>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>"{python_exe}"</Command>
      <Arguments>"{script_path}"</Arguments>
      <WorkingDirectory>"{project_root}"</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""

    # Save task XML to file
    xml_file = project_root / "data" / "light_profile_startup_task.xml"
    xml_file.parent.mkdir(parents=True, exist_ok=True)
    xml_file.write_text(task_xml, encoding='utf-16')

    # Use PowerShell Register-ScheduledTask (more reliable)
    def _run_powershell(script: str) -> Dict[str, Any]:
        """Run PowerShell script and return result"""
        try:
            result = subprocess.run(
                ["powershell", "-Command", script],
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    try:
        # Delete existing task if it exists
        logger.info("STEP 1: Removing existing task (if any)...")
        _run_powershell('Unregister-ScheduledTask -TaskName "JARVIS-Light-Profile-Startup" -Confirm:$false -ErrorAction SilentlyContinue')

        # Create new task using PowerShell
        logger.info("STEP 2: Creating startup task...")
        task_name = "JARVIS-Light-Profile-Startup"
        script = f"""
$xml = Get-Content '{xml_file}' -Raw -Encoding UTF16
Register-ScheduledTask -TaskName '{task_name}' -Xml $xml -Force
Write-Output "Task created: {task_name}"
"""
        result = _run_powershell(script)

        if result["success"]:
            logger.info("✅ Startup task created successfully")
            logger.info("")
            logger.info("Task Details:")
            logger.info("  - Name: JARVIS-Light-Profile-Startup")
            logger.info("  - Triggers:")
            logger.info("    • On logon (30s delay)")
            logger.info("    • On boot (1m delay)")
            logger.info("    • Every 15 minutes")
            logger.info("  - Run Level: Highest Available")
            logger.info("  - Script: apply_light_profile_on_startup.py (enhanced with retry logic)")
            logger.info("")
            logger.info("✅ Light profile will now be applied automatically on boot and every 15 minutes")

            return {
                "success": True,
                "task_name": task_name,
                "message": "Startup task created successfully"
            }
        else:
            error_msg = result.get("stderr") or result.get("stdout") or "Unknown error"
            logger.error(f"❌ Failed to create task: {error_msg}")
            logger.info("   ⚠️  You may need to run as administrator")
            return {
                "success": False,
                "error": error_msg
            }

    except Exception as e:
        logger.error(f"❌ Error creating startup task: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


def verify_task() -> Dict[str, Any]:
    """Verify the startup task exists and is enabled"""
    logger.info("")
    logger.info("STEP 3: Verifying task...")

    try:
        result = subprocess.run(
            'schtasks /Query /TN "JARVIS-Light-Profile-Startup" /FO LIST /V',
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            logger.info("✅ Task verified and exists")
            logger.info("")
            logger.info("Task Status:")
            for line in result.stdout.split('\n'):
                if any(keyword in line for keyword in ['Task Name', 'Status', 'Next Run', 'Triggers']):
                    logger.info(f"  {line.strip()}")
            return {"success": True, "verified": True}
        else:
            logger.warning("⚠️  Task not found or not accessible")
            return {"success": False, "verified": False}

    except Exception as e:
        logger.warning(f"⚠️  Could not verify task: {e}")
        return {"success": False, "error": str(e)}


def main():
    """Main execution"""
    result = create_startup_task()

    if result.get("success"):
        verify_result = verify_task()

        logger.info("")
        logger.info("=" * 70)
        logger.info("SETUP COMPLETE")
        logger.info("=" * 70)
        logger.info("")
        logger.info("✅ Light profile startup task configured")
        logger.info("")
        logger.info("The Light profile will be automatically applied:")
        logger.info("  • On system boot (1 minute delay)")
        logger.info("  • On user logon (30 second delay)")
        logger.info("  • Every 15 minutes (to ensure persistence)")
        logger.info("")
        logger.info("This ensures lighting stays enabled even after reboot.")
        logger.info("=" * 70)

        return 0
    else:
        logger.error("")
        logger.error("=" * 70)
        logger.error("SETUP FAILED")
        logger.error("=" * 70)
        logger.error(f"Error: {result.get('error', 'Unknown error')}")
        logger.error("=" * 70)
        return 1


if __name__ == "__main__":


    sys.exit(main())