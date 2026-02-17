#!/usr/bin/env python3
"""
JARVIS Kill Ambient Lighting Process
Targeted fix: Kill AacAmbientLighting and prevent restart

@JARVIS @KILL @AMBIENT_LIGHTING @AacAmbientLighting
"""

import sys
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, Any

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISKillAmbientLighting")


def run_powershell(command: str) -> Dict[str, Any]:
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


async def kill_ambient_lighting():
    """Kill AacAmbientLighting and prevent restart"""
    print("=" * 70)
    print("🔴 KILL AMBIENT LIGHTING PROCESS")
    print("   Targeting: AacAmbientLighting")
    print("=" * 70)
    print()

    # Step 1: Kill AacAmbientLighting process
    print("STEP 1: Killing AacAmbientLighting process...")
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
    killed_count = 0
    if "Killed:" in result.get("stdout", ""):
        try:
            killed_count = int(result.get("stdout", "").split(":")[1].strip())
        except:
            pass

    if killed_count > 0:
        print(f"  ✅ Killed {killed_count} AacAmbientLighting process(es)")
    else:
        print("  ⚠️  AacAmbientLighting process not found (may already be stopped)")

    await asyncio.sleep(2)

    # Step 2: Kill all lighting-related processes
    print("\nSTEP 2: Killing all lighting-related processes...")
    command = """
    $processes = @('AacAmbientLighting', 'LightingService', 'AuraWallpaperService', 'AuraWallpaper');
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
    killed_count = 0
    if "Killed:" in result.get("stdout", ""):
        try:
            killed_count = int(result.get("stdout", "").split(":")[1].strip())
        except:
            pass

    print(f"  ✅ Killed {killed_count} lighting process(es)")

    await asyncio.sleep(2)

    # Step 3: Stop and disable LightingService
    print("\nSTEP 3: Stopping and disabling LightingService...")
    command = """
    $stopped = 0;
    $disabled = 0;
    try {
        $service = Get-Service -Name 'LightingService' -ErrorAction SilentlyContinue;
        if ($service) {
            if ($service.Status -eq 'Running') {
                Stop-Service -Name 'LightingService' -Force -ErrorAction SilentlyContinue;
                $stopped = 1;
            }
            Set-Service -Name 'LightingService' -StartupType Disabled -ErrorAction SilentlyContinue;
            $disabled = 1;
        }
    } catch {}
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

    print(f"  ✅ Service stopped: {stopped}, disabled: {disabled}")

    await asyncio.sleep(2)

    # Step 4: Set registry to prevent restart
    print("\nSTEP 4: Setting registry to prevent restart...")
    command = """
    $paths = @(
        'HKCU:\\Software\\ASUS\\ARMOURY CRATE Service',
        'HKLM:\\SOFTWARE\\ASUS\\ARMOURY CRATE Service'
    );
    $updated = 0;
    foreach ($path in $paths) {
        if (Test-Path $path) {
            Set-ItemProperty -Path $path -Name 'AuraEnabled' -Value 0 -Type DWord -ErrorAction SilentlyContinue;
            Set-ItemProperty -Path $path -Name 'LightingEnabled' -Value 0 -Type DWord -ErrorAction SilentlyContinue;
            Set-ItemProperty -Path $path -Name 'RGBEnabled' -Value 0 -Type DWord -ErrorAction SilentlyContinue;
            Set-ItemProperty -Path $path -Name 'BacklightBrightness' -Value 0 -Type DWord -ErrorAction SilentlyContinue;
            $updated++;
        }
    }
    "Updated:$updated"
    """

    result = run_powershell(command)
    updated = 0
    if "Updated:" in result.get("stdout", ""):
        try:
            updated = int(result.get("stdout", "").split(":")[1].strip())
        except:
            pass

    print(f"  ✅ Registry updated: {updated} path(s)")

    await asyncio.sleep(2)

    # Step 5: Verify process is dead
    print("\nSTEP 5: Verifying process is killed...")
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
        print("  ✅ AacAmbientLighting is KILLED")
        success = True
    else:
        print(f"  ⚠️  AacAmbientLighting may still be running: {stdout}")
        success = False

    print()
    print("=" * 70)
    print("✅ KILL COMPLETE")
    print("=" * 70)
    print(f"Success: {success}")
    print()
    print("If lights are STILL ON:")
    print("  1. Check if AacAmbientLighting restarted (run diagnostic again)")
    print("  2. May need to disable in BIOS")
    print("  3. May need to unplug/replug external lighting devices")
    print("=" * 70)

    return {"success": success}


if __name__ == "__main__":
    asyncio.run(kill_ambient_lighting())
