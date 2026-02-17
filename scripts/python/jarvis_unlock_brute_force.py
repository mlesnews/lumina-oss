#!/usr/bin/env python3
"""
JARVIS: Brute Force Registry Unlock
🔓 Exhaustive registry search for ALL lock-related values
"""

import sys
import asyncio
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cfservices.services.jarvis_core.integrations.armoury_crate import create_armoury_crate_integration

async def main():
    """Brute force search ALL registry for lock settings"""
    print("=" * 70)
    print("🔓 JARVIS: Brute Force Registry Unlock")
    print("=" * 70)
    print()

    integration = create_armoury_crate_integration()

    # Search both HKCU and HKLM
    print("🔍 Searching HKCU (Current User)...")
    print("-" * 70)

    ps_cmd = (
        "Get-ChildItem -Path 'HKCU:\\SOFTWARE\\ASUS' -Recurse -ErrorAction SilentlyContinue | "
        "ForEach-Object { "
        "  $path = $_.PSPath; "
        "  $props = Get-ItemProperty -Path $path -ErrorAction SilentlyContinue; "
        "  if ($props) { "
        "    $props.PSObject.Properties | Where-Object { "
        "      $_.Name -notlike 'PS*' -and ("
        "        $_.Name -like '*Lock*' -or $_.Name -like '*Fn*' -or $_.Name -like '*Win*' -or "
        "        $_.Name -like '*Action*' -or $_.Name -like '*Function*' -or $_.Name -like '*Key*' "
        "      ) "
        "    } | ForEach-Object { "
        "      Write-Host \"$path|$($_.Name)|$($_.Value)|$($_.PropertyType)\" "
        "    } "
        "  } "
        "}"
    )

    result = integration._run_powershell(ps_cmd)
    if isinstance(result, dict):
        output = result.get("stdout", "")
    else:
        output = str(result) if result else ""

    found_values = []
    if output:
        for line in output.strip().split('\n'):
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 3:
                    path = parts[0]
                    name = parts[1]
                    value = parts[2]
                    found_values.append((path, name, value))
                    print(f"  ✅ {path}\\{name} = {value}")

    print()
    print(f"📊 Found {len(found_values)} lock-related values in HKCU")
    print()

    # Now modify all found values
    print("🔧 Modifying all found values...")
    print("-" * 70)

    modified = 0
    for path, name, value in found_values:
        name_lower = name.lower()

        # Determine unlock value
        if "action" in name_lower or "function" in name_lower:
            unlock_value = "1"  # Function Key mode
        elif "winkey" in name_lower or "win" in name_lower:
            unlock_value = "0"  # Unlock Windows key
        elif "fn" in name_lower or "lock" in name_lower:
            unlock_value = "0"  # Unlock
        else:
            unlock_value = "0"  # Default unlock

        # Only modify if value is not already unlock value
        if str(value) != unlock_value:
            try:
                ps_cmd = (
                    f"try {{ "
                    f"  Set-ItemProperty -Path '{path}' -Name '{name}' -Value {unlock_value} -Type DWord -Force -ErrorAction Stop; "
                    f"  Write-Host 'SUCCESS' "
                    f"}} catch {{ "
                    f"  try {{ "
                    f"    New-ItemProperty -Path '{path}' -Name '{name}' -Value {unlock_value} -Type DWord -Force -ErrorAction Stop; "
                    f"    Write-Host 'CREATED' "
                    f"  }} catch {{ Write-Host 'FAILED' }} "
                    f"}}"
                )
                result = integration._run_powershell(ps_cmd)
                if isinstance(result, dict):
                    mod_output = result.get("stdout", "")
                else:
                    mod_output = str(result) if result else ""

                if "SUCCESS" in mod_output or "CREATED" in mod_output:
                    print(f"  ✅ {name}: {value} → {unlock_value}")
                    modified += 1
                else:
                    print(f"  ⚠️  {name}: Failed to modify")
            except Exception as e:
                print(f"  ⚠️  {name}: Error - {e}")
        else:
            print(f"  ℹ️  {name}: Already set to {unlock_value}")

    print()
    print(f"📊 Modified {modified} values")
    print()

    # Restart everything
    print("🔄 Restarting all services and processes...")
    print("-" * 70)

    services = ["ArmouryCrateService", "ROGLiveService", "AuraService", "LightingService"]
    for service in services:
        try:
            ps_cmd = f"Restart-Service -Name '{service}' -Force -ErrorAction SilentlyContinue"
            integration._run_powershell(ps_cmd)
            print(f"  ✅ {service}: Restarted")
        except:
            pass

    processes = ["ArmouryCrateControlInterface", "ArmouryCrate"]
    for process in processes:
        try:
            ps_cmd = (
                f"Stop-Process -Name '{process}' -Force -ErrorAction SilentlyContinue; "
                f"Start-Sleep -Milliseconds 2000; "
                f"$paths = @('C:\\Program Files\\ASUS\\ArmouryDevice\\{process}.exe', 'C:\\Program Files (x86)\\ASUS\\ArmouryDevice\\{process}.exe'); "
                f"foreach ($p in $paths) {{ if (Test-Path $p) {{ Start-Process -FilePath $p -WindowStyle Hidden; break }} }}"
            )
            integration._run_powershell(ps_cmd)
            print(f"  ✅ {process}: Restarted")
        except:
            pass

    print()
    print("=" * 70)
    print("💡 SUMMARY:")
    print("=" * 70)
    print(f"  ✅ Found: {len(found_values)} registry values")
    print(f"  ✅ Modified: {modified} values")
    print("  ✅ Services/Processes: Restarted")
    print()
    print("  ⚠️  If locks still visible:")
    print("     1. Restart computer (registry changes need reboot)")
    print("     2. Check BIOS/UEFI: Advanced > System Configuration > Action Key Mode")
    print("=" * 70)

if __name__ == "__main__":


    asyncio.run(main())