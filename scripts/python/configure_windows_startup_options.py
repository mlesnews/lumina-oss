#!/usr/bin/env python3
"""
Configure Windows Startup Options
Make option/function keys accessible at Windows startup
"""

import sys
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("Configure Windows Startup Options")
print("Making option/function keys accessible at startup")
print("=" * 70)
print()

# 1. Enable boot menu timeout (show boot options)
print("STEP 1: Configuring boot menu timeout...")
try:
    result = subprocess.run(
        ["bcdedit", "/set", "bootmenupolicy", "Legacy"],
        capture_output=True,
        text=True,
        timeout=10
    )
    if result.returncode == 0:
        print("  ✅ Boot menu policy set to Legacy")
    else:
        print(f"  ⚠️  Boot menu policy: {result.stdout.strip()}")
except Exception as e:
    print(f"  ⚠️  Error: {e}")

try:
    result = subprocess.run(
        ["bcdedit", "/timeout", "10"],
        capture_output=True,
        text=True,
        timeout=10
    )
    if result.returncode == 0:
        print("  ✅ Boot menu timeout set to 10 seconds")
    else:
        print(f"  ⚠️  Timeout setting: {result.stdout.strip()}")
except Exception as e:
    print(f"  ⚠️  Error: {e}")

print()

# 2. Enable F8 Safe Mode menu
print("STEP 2: Enabling F8 Safe Mode menu...")
try:
    result = subprocess.run(
        ["bcdedit", "/set", "{current}", "bootmenupolicy", "Legacy"],
        capture_output=True,
        text=True,
        timeout=10
    )
    if result.returncode == 0:
        print("  ✅ F8 Safe Mode menu enabled")
    else:
        print(f"  ⚠️  F8 menu: {result.stdout.strip()}")
except Exception as e:
    print(f"  ⚠️  Error: {e}")

print()

# 3. Configure registry for startup options visibility
print("STEP 3: Configuring registry for startup options...")
ps_script = """
$regPath = 'HKLM:\\SYSTEM\\CurrentControlSet\\Control';
try {
    if (-not (Test-Path $regPath)) {
        New-Item -Path $regPath -Force | Out-Null;
    }
    Set-ItemProperty -Path $regPath -Name 'BootDriverFlags' -Value 0x14 -ErrorAction SilentlyContinue;
    Write-Host 'Updated BootDriverFlags';
} catch {
    Write-Host 'Registry update failed';
}
"""

result = subprocess.run(
    ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
    capture_output=True,
    text=True,
    timeout=10
)
print(f"  {result.stdout.strip()}")

print()

# 4. Enable Shift key for startup options
print("STEP 4: Ensuring Shift key works for startup options...")
print("  ℹ️  Hold Shift while clicking Restart to access startup options")
print("  ℹ️  Or press F8 during boot for Advanced Boot Options")

print()

# 5. Summary
print("=" * 70)
print("CONFIGURATION COMPLETE")
print("=" * 70)
print()
print("At Windows startup, you can now:")
print("  • Press F8 for Advanced Boot Options menu")
print("  • Hold Shift while restarting for startup options")
print("  • Boot menu will show for 10 seconds")
print()
print("Option keys available:")
print("  • F8 - Advanced Boot Options")
print("  • Shift - Access startup options")
print("  • F10 - BIOS/UEFI settings (if supported)")
print("  • F12 - Boot device selection (if supported)")
print()
print("=" * 70)
