#!/usr/bin/env python3
"""
Replace Old Lighting Killer with Smart Lighting Killer
USS Lumina - @scotty (Windows Systems Architect)

Stops old lighting killer processes/tasks and replaces with smart system-mode version
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

logger = get_logger("ReplaceLightingKiller")


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


def stop_old_lighting_killers() -> Dict[str, Any]:
    """Stop any running old lighting killer processes"""
    logger.info("Stopping old lighting killer processes...")

    # Find and kill Python processes running old lighting killer scripts
    script = """
$processes = Get-Process python* -ErrorAction SilentlyContinue | Where-Object {
    $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)").CommandLine
    if ($cmdLine) {
        $cmdLine -match 'jarvis_persistent_lighting_killer|jarvis_lighting_killer_daemon|jarvis_kill_ambient_lighting'
    }
}

$killed = 0
foreach ($proc in $processes) {
    try {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        $killed++
        Write-Output "Killed PID: $($proc.Id)"
    } catch {
        # Continue
    }
}

Write-Output "Total killed: $killed"
"""

    result = _run_powershell(script)
    if result["success"]:
        logger.info(f"✅ Stopped old processes: {result['stdout']}")
        return {"success": True, "killed": result["stdout"]}
    else:
        logger.warning(f"⚠️  Could not stop processes: {result.get('error', 'Unknown')}")
        return {"success": False, "error": result.get("error", "Unknown")}


def remove_old_scheduled_tasks() -> Dict[str, Any]:
    """Remove old lighting killer scheduled tasks"""
    logger.info("Removing old scheduled tasks...")

    task_names = [
        "JARVIS_ExternalLightingKiller",
        "JARVIS_LightingKiller",
        "JARVIS_PersistentLightingKiller"
    ]

    removed = []
    for task_name in task_names:
        script = f"""
$task = Get-ScheduledTask -TaskName '{task_name}' -ErrorAction SilentlyContinue
if ($task) {{
    Unregister-ScheduledTask -TaskName '{task_name}' -Confirm:$false -ErrorAction SilentlyContinue
    Write-Output "Removed: {task_name}"
}} else {{
    Write-Output "Not found: {task_name}"
}}
"""
        result = _run_powershell(script)
        if result["success"] and "Removed" in result["stdout"]:
            removed.append(task_name)
            logger.info(f"  ✅ Removed task: {task_name}")
        else:
            logger.info(f"  ℹ️  Task not found: {task_name}")

    return {"success": True, "removed": removed}


def create_smart_lighting_killer_task() -> Dict[str, Any]:
    """Create scheduled task for smart lighting killer"""
    logger.info("Creating smart lighting killer scheduled task...")

    script_path = project_root / "scripts" / "python" / "jarvis_smart_lighting_killer_system_mode.py"
    python_exe = sys.executable

    task_name = "JARVIS_SmartLightingKiller_SystemMode"

    # Remove existing task if it exists
    _run_powershell(f"Unregister-ScheduledTask -TaskName '{task_name}' -Confirm:$false -ErrorAction SilentlyContinue")

    # Create task XML
    task_xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>2026-01-16T00:00:00</Date>
    <Author>JARVIS @scotty - USS Lumina</Author>
    <Description>Smart Lighting Killer - System Mode Only. Only kills lighting when: DARK mode AND lid closed. Enables lighting when: LIGHT mode OR lid open.</Description>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
    <TimeTrigger>
      <Repetition>
        <Interval>PT5M</Interval>
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
      <Arguments>"{script_path}" --once</Arguments>
    </Exec>
  </Actions>
</Task>"""

    # Save XML to temp file
    xml_file = project_root / "data" / "smart_lighting_killer_task.xml"
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
        logger.info("   • Runs every 5 minutes")
        logger.info("   • Only kills lighting: DARK mode AND lid closed")
        logger.info("   • Enables lighting: LIGHT mode OR lid open")
        return {"success": True, "task_name": task_name}
    else:
        logger.error(f"❌ Failed to create task: {result.get('error', 'Unknown')}")
        logger.info("   ⚠️  You may need to run as administrator")
        return {"success": False, "error": result.get("error", "Unknown")}


def main():
    """Main execution"""
    logger.info("=" * 70)
    logger.info("REPLACE LIGHTING KILLER WITH SMART VERSION")
    logger.info("USS Lumina - @scotty (Windows Systems Architect)")
    logger.info("=" * 70)
    logger.info("")

    # Step 1: Stop old processes
    logger.info("STEP 1: Stopping old lighting killer processes...")
    stop_result = stop_old_lighting_killers()

    # Step 2: Remove old scheduled tasks
    logger.info("")
    logger.info("STEP 2: Removing old scheduled tasks...")
    remove_result = remove_old_scheduled_tasks()

    # Step 3: Create new smart task
    logger.info("")
    logger.info("STEP 3: Creating smart lighting killer scheduled task...")
    create_result = create_smart_lighting_killer_task()

    # Summary
    logger.info("")
    logger.info("=" * 70)
    logger.info("REPLACEMENT SUMMARY")
    logger.info("=" * 70)
    logger.info("")
    logger.info(f"✅ Old processes stopped: {stop_result.get('success', False)}")
    logger.info(f"✅ Old tasks removed: {len(remove_result.get('removed', []))} tasks")
    logger.info(f"✅ New task created: {create_result.get('success', False)}")
    logger.info("")
    logger.info("📋 Smart Lighting Killer Rules:")
    logger.info("   • Only runs in SYSTEM mode")
    logger.info("   • Kills lighting: DARK mode (after midnight) AND lid closed")
    logger.info("   • Enables lighting: LIGHT mode OR lid open")
    logger.info("")
    logger.info("=" * 70)

    return 0 if create_result.get("success") else 1


if __name__ == "__main__":


    sys.exit(main())