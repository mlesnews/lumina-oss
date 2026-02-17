#!/usr/bin/env python3
"""
JARVIS Aggressive Kill Ambient Lighting
Kill AacAmbientLighting AND prevent it from restarting

@JARVIS @AGGRESSIVE @KILL @AMBIENT_LIGHTING
"""

import sys
import subprocess
import asyncio
import time
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISAggressiveKillAmbient")


def run_powershell(command: str) -> dict:
    """Execute PowerShell command"""
    try:
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", command],
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def aggressive_kill_ambient_lighting():
    """Aggressively kill AacAmbientLighting and prevent restart"""
    print("=" * 70)
    print("🔴 AGGRESSIVE KILL AMBIENT LIGHTING")
    print("   Kill process AND stop parent services")
    print("=" * 70)
    print()

    # Step 1: Stop parent services FIRST (prevents restart)
    print("STEP 1: Stopping parent services (prevents restart)...")
    command = """
    $stopped = 0;
    $disabled = 0;
    $services = @('ArmouryCrateService', 'LightingService', 'AuraWallpaperService');
    foreach ($svc in $services) {
        try {
            $service = Get-Service -Name $svc -ErrorAction SilentlyContinue;
            if ($service) {
                if ($service.Status -eq 'Running') {
                    Stop-Service -Name $svc -Force -ErrorAction SilentlyContinue;
                    Start-Sleep -Milliseconds 500;
                    $stopped++;
                }
                Set-Service -Name $svc -StartupType Disabled -ErrorAction SilentlyContinue;
                $disabled++;
            }
        } catch {}
    }
    "Stopped:$stopped;Disabled:$disabled"
    """

    result = run_powershell(command)
    stopped = 0
    disabled = 0
    if "Stopped:" in result.get("stdout", ""):
        try:
            parts = result.get("stdout", "").split(";")
            stopped = int(parts[0].split(":")[1].strip())
            disabled = int(parts[1].split(":")[1].strip())
        except:
            pass

    print(f"  ✅ Services stopped: {stopped}, disabled: {disabled}")
    await asyncio.sleep(3)

    # Step 2: Kill ALL Armoury Crate processes
    print("\nSTEP 2: Killing ALL Armoury Crate processes...")
    command = """
    $processes = @('AacAmbientLighting', 'ArmouryCrateService', 'ArmouryCrateControlInterface', 
                   'LightingService', 'AuraWallpaperService', 'AuraWallpaper');
    $killed = 0;
    foreach ($procName in $processes) {
        $procs = Get-Process -Name $procName -ErrorAction SilentlyContinue;
        if ($procs) {
            $procs | Stop-Process -Force -ErrorAction SilentlyContinue;
            $killed += $procs.Count;
        }
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
    await asyncio.sleep(2)

    # Step 3: Continuous kill loop (kill it 5 times to ensure it stays dead)
    print("\nSTEP 3: Continuous kill loop (5 attempts)...")
    for i in range(5):
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

        if killed > 0:
            print(f"  Attempt {i+1}/5: Killed {killed} process(es)")
        else:
            print(f"  Attempt {i+1}/5: Process not running")

        await asyncio.sleep(1)

    # Step 4: Final verification
    print("\nSTEP 4: Final verification...")
    await asyncio.sleep(3)  # Wait to see if it restarts

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
        print("  ✅ AacAmbientLighting is DEAD and STAYING DEAD")
        success = True
    else:
        print(f"  ⚠️  AacAmbientLighting restarted: {stdout}")
        print("  ⚠️  Something is forcefully restarting it")
        success = False

    print()
    print("=" * 70)
    print("✅ AGGRESSIVE KILL COMPLETE")
    print("=" * 70)
    print(f"Success: {success}")
    print()

    if not success:
        print("If process keeps restarting:")
        print("  1. Check Task Scheduler for auto-start tasks")
        print("  2. Check Windows Startup programs")
        print("  3. May need to disable in BIOS/UEFI")
        print("  4. May need to physically disconnect external lighting")

    print("=" * 70)

    return {"success": success}


if __name__ == "__main__":
    asyncio.run(aggressive_kill_ambient_lighting())
