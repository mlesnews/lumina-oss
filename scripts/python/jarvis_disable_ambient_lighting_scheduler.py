#!/usr/bin/env python3
"""
JARVIS Disable Ambient Lighting in Task Scheduler
Disable auto-start tasks that restart AacAmbientLighting

@JARVIS @TASK_SCHEDULER @AMBIENT_LIGHTING
"""

import sys
import subprocess
import asyncio
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISTaskSchedulerFix")


def run_powershell(command: str) -> dict:
    """Execute PowerShell command"""
    try:
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", command],
            capture_output=True,
            text=True,
            timeout=60
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def disable_task_scheduler_tasks():
    """Disable Task Scheduler tasks that restart ambient lighting"""
    print("=" * 70)
    print("🔴 DISABLE TASK SCHEDULER TASKS")
    print("   Prevent AacAmbientLighting from auto-starting")
    print("=" * 70)
    print()

    # Step 1: Find all ASUS/lighting tasks
    print("STEP 1: Finding ASUS/lighting tasks in Task Scheduler...")
    command = """
    $tasks = Get-ScheduledTask | Where-Object {
        $_.TaskName -like '*ASUS*' -or
        $_.TaskName -like '*Aura*' -or
        $_.TaskName -like '*Lighting*' -or
        $_.TaskName -like '*Armoury*' -or
        $_.TaskName -like '*Ambient*'
    } | Select-Object TaskName, State, TaskPath | ConvertTo-Json
    """

    result = run_powershell(command)
    tasks_found = []
    if result.get("success"):
        import json
        try:
            tasks_found = json.loads(result.get("stdout", "[]"))
            print(f"  Found {len(tasks_found)} ASUS/lighting tasks:")
            for task in tasks_found:
                print(f"     {task.get('TaskPath', '')}{task.get('TaskName', '')} - {task.get('State', '')}")
        except:
            print(f"   Output: {result.get('stdout', '')[:500]}")

    await asyncio.sleep(1)

    # Step 2: Disable all found tasks
    print(f"\nSTEP 2: Disabling {len(tasks_found)} tasks...")
    disabled_count = 0
    for task in tasks_found:
        task_name = task.get('TaskName', '')
        task_path = task.get('TaskPath', '')
        full_path = f"{task_path}{task_name}"

        command = f"""
        try {{
            Disable-ScheduledTask -TaskName '{task_name}' -TaskPath '{task_path}' -ErrorAction SilentlyContinue;
            'Disabled'
        }} catch {{
            'Failed'
        }}
        """

        result = run_powershell(command)
        if "Disabled" in result.get("stdout", ""):
            print(f"  ✅ Disabled: {full_path}")
            disabled_count += 1
        else:
            print(f"  ⚠️  Failed: {full_path}")

    print(f"\n  ✅ Disabled {disabled_count} task(s)")
    await asyncio.sleep(2)

    # Step 3: Kill process one more time
    print("\nSTEP 3: Final kill of AacAmbientLighting...")
    command = """
    $killed = 0;
    $procs = Get-Process -Name 'AacAmbientLighting' -ErrorAction SilentlyContinue;
    if ($procs) {
        $procs | Stop-Process -Force -ErrorAction SilentlyContinue;
        $killed = $procs.Count;
    }
    "Killed:$killed"
    """

    result = run_powershell(command)
    killed = 0
    if "Killed:" in result.get("stdout", ""):
        try:
            killed = int(result.get("stdout", "").split(":")[1].strip())
        except:
            pass

    print(f"  ✅ Killed {killed} process(es)")
    await asyncio.sleep(5)  # Wait longer to see if it restarts

    # Step 4: Final verification
    print("\nSTEP 4: Final verification (after 5 second wait)...")
    command = """
    $procs = Get-Process -Name 'AacAmbientLighting' -ErrorAction SilentlyContinue;
    if ($procs) {
        "StillRunning:" + $procs.Count
    } else {
        "Killed"
    }
    """

    result = run_powershell(command)
    stdout = result.get("stdout", "").strip()

    if "Killed" in stdout:
        print("  ✅ AacAmbientLighting is DEAD")
        success = True
    else:
        print(f"  ⚠️  AacAmbientLighting restarted: {stdout}")
        success = False

    print()
    print("=" * 70)
    print("✅ TASK SCHEDULER DISABLE COMPLETE")
    print("=" * 70)
    print(f"Success: {success}")
    print(f"Tasks disabled: {disabled_count}")
    print()

    if not success:
        print("⚠️  Process still restarting. Final options:")
        print("  1. PHYSICALLY DISCONNECT external lighting devices")
        print("  2. Disable in BIOS/UEFI settings")
        print("  3. Uninstall Armoury Crate (nuclear option)")
        print("  4. Use electrical tape to cover lights (temporary)")

    print("=" * 70)

    return {"success": success, "tasks_disabled": disabled_count}


if __name__ == "__main__":
    asyncio.run(disable_task_scheduler_tasks())
