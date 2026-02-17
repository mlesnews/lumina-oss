#!/usr/bin/env python3
"""
EMERGENCY: Turn Off All Lights
Quick script to turn off all RGB lighting immediately
"""

import sys
import subprocess
import time
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("🔴 EMERGENCY: TURNING OFF ALL LIGHTS")
print("=" * 70)
print()

# Step 1: Kill all lighting processes
print("STEP 1: Killing all lighting processes...")
ps_script = """
$procs = @('AacAmbientLighting', 'LightingService', 'AuraWallpaperService', 'ArmouryCrateService', 'ArmouryCrateControlInterface');
$killed = 0;
foreach ($p in $procs) {
    $found = Get-Process -Name $p -ErrorAction SilentlyContinue;
    if ($found) {
        $found | Stop-Process -Force -ErrorAction SilentlyContinue;
        $killed += $found.Count;
    }
}
Write-Host "Killed:$killed"
"""

result = subprocess.run(
    ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
    capture_output=True,
    text=True,
    timeout=30
)
print(f"  {result.stdout.strip()}")

# Step 2: Stop and disable services
print("\nSTEP 2: Stopping and disabling lighting services...")
ps_script = """
$services = @('LightingService', 'ArmouryCrateService');
$stopped = 0;
$disabled = 0;
foreach ($svc in $services) {
    $service = Get-Service -Name $svc -ErrorAction SilentlyContinue;
    if ($service) {
        if ($service.Status -eq 'Running') {
            Stop-Service -Name $svc -Force -ErrorAction SilentlyContinue;
            $stopped++;
        }
        Set-Service -Name $svc -StartupType Disabled -ErrorAction SilentlyContinue;
        $disabled++;
    }
}
Write-Host "Stopped:$stopped;Disabled:$disabled"
"""

result = subprocess.run(
    ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
    capture_output=True,
    text=True,
    timeout=30
)
print(f"  {result.stdout.strip()}")

# Step 3: Set registry to disable lighting
print("\nSTEP 3: Setting registry to disable lighting...")
ps_script = """
$regPaths = @(
    'HKCU:\\Software\\ASUS\\AURA',
    'HKLM:\\SOFTWARE\\ASUS\\AURA',
    'HKCU:\\Software\\ASUS\\ArmouryDevice',
    'HKLM:\\SOFTWARE\\ASUS\\ArmouryDevice'
);
$updated = 0;
foreach ($path in $regPaths) {
    if (Test-Path $path) {
        try {
            Set-ItemProperty -Path $path -Name 'Enable' -Value 0 -ErrorAction SilentlyContinue;
            Set-ItemProperty -Path $path -Name 'Enabled' -Value 0 -ErrorAction SilentlyContinue;
            Set-ItemProperty -Path $path -Name 'Lighting' -Value 0 -ErrorAction SilentlyContinue;
            Set-ItemProperty -Path $path -Name 'Brightness' -Value 0 -ErrorAction SilentlyContinue;
            $updated++;
        } catch {}
    }
}
Write-Host "Updated:$updated"
"""

result = subprocess.run(
    ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
    capture_output=True,
    text=True,
    timeout=30
)
print(f"  {result.stdout.strip()}")

# Step 4: Final kill check
print("\nSTEP 4: Final verification...")
time.sleep(2)
ps_script = """
$procs = Get-Process -Name 'AacAmbientLighting' -ErrorAction SilentlyContinue;
if ($procs) {
    Write-Host "StillRunning:" + $procs.Count
} else {
    Write-Host "AllOff"
}
"""

result = subprocess.run(
    ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
    capture_output=True,
    text=True,
    timeout=30
)

if "AllOff" in result.stdout:
    print("  ✅ All lighting processes are OFF")
else:
    print(f"  ⚠️  Some processes may still be running: {result.stdout.strip()}")

print()
print("=" * 70)
print("✅ EMERGENCY LIGHTING SHUTDOWN COMPLETE")
print("=" * 70)
print()
print("If lights are STILL ON:")
print("  1. Try pressing Fn+F4 (may need to unlock FN key first: Fn+Esc)")
print("  2. Check if external RGB devices need to be unplugged")
print("  3. May need to disable in BIOS/UEFI")
print("=" * 70)
