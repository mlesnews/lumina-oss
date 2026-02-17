#!/usr/bin/env python3
"""
Force Daylight Lighting - Emergency Fix
Sets keyboard to 100% brightness immediately via registry
"""

import subprocess
import sys

script = """
$paths = @(
    'HKCU:\\Software\\ASUS\\ArmouryDevice\\Aura',
    'HKCU:\\Software\\ASUS\\Aura',
    'HKLM:\\SOFTWARE\\ASUS\\ArmouryDevice\\Aura',
    'HKLM:\\SOFTWARE\\ASUS\\Aura'
)

$updated = 0
foreach ($path in $paths) {
    try {
        if (-not (Test-Path $path)) {
            New-Item -Path $path -Force -ErrorAction SilentlyContinue | Out-Null
        }
        if (Test-Path $path) {
            Set-ItemProperty -Path $path -Name 'Brightness' -Value 100 -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'KeyboardBrightness' -Value 100 -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'BacklightBrightness' -Value 100 -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'KeyboardEnabled' -Value 1 -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'Enable' -Value 1 -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'ExternalEnabled' -Value 0 -Type DWord -ErrorAction SilentlyContinue
            $updated++
        }
    } catch {
        # Continue
    }
}

if ($updated -gt 0) {
    Write-Output "OK: Updated $updated registry paths"
} else {
    Write-Output "Failed: No paths updated"
}
"""

result = subprocess.run(
    ["powershell", "-ExecutionPolicy", "Bypass", "-Command", script],
    capture_output=True,
    text=True,
    timeout=10,
    check=False
)

if result.returncode == 0 and "OK:" in result.stdout:
    print("✅ Keyboard lighting set to 100% (daylight mode)")
    print(result.stdout.strip())
    sys.exit(0)
else:
    print("❌ Failed to set lighting")
    print(result.stderr)
    sys.exit(1)
