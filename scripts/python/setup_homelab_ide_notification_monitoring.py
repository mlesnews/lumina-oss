#!/usr/bin/env python3
"""
Setup @homelab IDE Notification Monitoring
USS Lumina - @scotty (Windows Systems Architect)

Sets up automatic monitoring and handling of all IDE/VS Code/Cursor notifications
"""

import sys
import subprocess
from pathlib import Path
from typing import Dict, Any

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SetupHomelabIDENotifications")


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


def create_scheduled_task() -> Dict[str, Any]:
    """Create scheduled task for IDE notification monitoring"""
    logger.info("Creating scheduled task for IDE notification monitoring...")

    script_path = project_root / "scripts" / "python" / "jarvis_homelab_ide_notification_handler.py"
    python_exe = sys.executable

    task_name = "JARVIS_HomelabIDENotificationMonitor"

    # Remove existing task if it exists
    _run_powershell(f"Unregister-ScheduledTask -TaskName '{task_name}' -Confirm:$false -ErrorAction SilentlyContinue")

    # Create task XML
    task_xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>2026-01-16T00:00:00</Date>
    <Author>JARVIS @scotty - USS Lumina</Author>
    <Description>@homelab IDE Notification Monitor - Automatically handles all IDE/VS Code/Cursor notifications including large file dialogs, performance warnings, and Git notifications.</Description>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
    <TimeTrigger>
      <Repetition>
        <Interval>PT1M</Interval>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
      <StartBoundary>2026-01-16T00:00:00</StartBoundary>
      <Enabled>true</Enabled>
    </TimeTrigger>
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
      <Arguments>"{script_path}" --handle-large-file</Arguments>
    </Exec>
  </Actions>
</Task>"""

    # Save XML to temp file
    xml_file = project_root / "data" / "homelab_ide_notification_task.xml"
    xml_file.parent.mkdir(parents=True, exist_ok=True)
    xml_file.write_text(task_xml, encoding='utf-16')

    # Register task (requires admin)
    script = f"""
$xml = Get-Content '{xml_file}' -Raw -Encoding UTF16
Register-ScheduledTask -TaskName '{task_name}' -Xml $xml -Force
Write-Output "Task created: {task_name}"
"""

    result = _run_powershell(script)
    if result["success"]:
        logger.info(f"✅ Scheduled task created: {task_name}")
        logger.info("   • Runs on logon")
        logger.info("   • Runs every 1 minute")
        logger.info("   • Handles large file dialogs automatically")
        logger.info("   • Handles all IDE notifications")
        return {"success": True, "task_name": task_name}
    else:
        logger.error(f"❌ Failed to create task: {result.get('error', 'Unknown')}")
        logger.info("   ⚠️  You may need to run as administrator")
        return {"success": False, "error": result.get("error", "Unknown")}


def main():
    """Main execution"""
    logger.info("=" * 70)
    logger.info("SETUP @homelab IDE NOTIFICATION MONITORING")
    logger.info("USS Lumina - @scotty (Windows Systems Architect)")
    logger.info("=" * 70)
    logger.info("")

    # Create scheduled task
    result = create_scheduled_task()

    # Summary
    logger.info("")
    logger.info("=" * 70)
    logger.info("SETUP SUMMARY")
    logger.info("=" * 70)
    logger.info("")
    if result.get("success"):
        logger.info("✅ IDE notification monitoring configured")
        logger.info("")
        logger.info("📋 Monitored Notifications:")
        logger.info("   • Large file dialogs (tokenization, wrapping, folding disabled)")
        logger.info("   • Performance warnings")
        logger.info("   • Extension updates")
        logger.info("   • Git notifications")
        logger.info("   • All IDE/VS Code/Cursor notifications")
        logger.info("")
        logger.info("🔧 Actions:")
        logger.info("   • Large file dialog: 'Don't Show Again' (default)")
        logger.info("   • Git notifications: Auto-handled")
        logger.info("   • Performance warnings: Dismissed or optimized")
        logger.info("")
    else:
        logger.info("❌ Setup failed - may need administrator privileges")
        logger.info("")
    logger.info("=" * 70)

    return 0 if result.get("success") else 1


if __name__ == "__main__":


    sys.exit(main())