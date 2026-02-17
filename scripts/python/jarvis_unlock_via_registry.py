#!/usr/bin/env python3
"""
JARVIS: Unlock Keys via Registry
🔓 Attempts to unlock FN and Windows keys by modifying registry settings
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cfservices.services.jarvis_core.integrations.armoury_crate import create_armoury_crate_integration

async def main():
    """Attempt to unlock keys via registry modifications"""
    print("=" * 70)
    print("🔓 JARVIS: Unlock Keys via Registry")
    print("=" * 70)
    print()
    print("💡 Since key combinations didn't work, trying registry method...")
    print()

    integration = create_armoury_crate_integration()

    # Registry paths to check and modify
    registry_paths = [
        (r"HKCU\SOFTWARE\ASUS\AacHal", "AacHal (User)"),
        (r"HKLM\SOFTWARE\ASUS\AacHal", "AacHal (System)"),
        (r"HKCU\SOFTWARE\ASUS\ArmouryDevice", "ArmouryDevice (User)"),
        (r"HKLM\SOFTWARE\ASUS\ArmouryDevice", "ArmouryDevice (System)"),
        (r"HKCU\SOFTWARE\ASUS\ATK", "ATK (User)"),
        (r"HKLM\SOFTWARE\ASUS\ATK", "ATK (System)"),
        (r"HKCU\SOFTWARE\ASUS\ArmouryCrate", "ArmouryCrate (User)"),
        (r"HKLM\SOFTWARE\ASUS\ArmouryCrate", "ArmouryCrate (System)"),
    ]

    print("🔍 STEP 1: Checking registry for lock-related settings...")
    print("-" * 70)

    found_settings = []

    for reg_path, name in registry_paths:
        try:
            # Check if path exists and list all values
            ps_cmd = (
                f"$path = '{reg_path}'; "
                f"if (Test-Path $path) {{ "
                f"  $props = Get-ItemProperty -Path $path -ErrorAction SilentlyContinue; "
                f"  $lockProps = $props.PSObject.Properties | Where-Object {{ "
                f"    $_.Name -like '*Lock*' -or $_.Name -like '*Fn*' -or $_.Name -like '*Win*' -or $_.Name -like '*Key*' "
                f"  }}; "
                f"  if ($lockProps) {{ "
                f"    $lockProps | ForEach-Object {{ Write-Host \"$($_.Name)=$($_.Value)\" }} "
                f"  }} else {{ 'No lock settings found' }} "
                f"}} else {{ 'Path does not exist' }}"
            )
            result = integration._run_powershell(ps_cmd)

            # Handle dict result from _run_powershell
            if isinstance(result, dict):
                output = result.get("stdout", "")
            else:
                output = str(result) if result else ""

            if output and "Path does not exist" not in output and "No lock settings found" not in output:
                print(f"  ✅ {name}: Found lock-related settings")
                for line in output.strip().split('\n'):
                    if line.strip() and '=' in line:
                        print(f"     {line.strip()}")
                        found_settings.append((reg_path, line.strip()))
            elif output and "Path does not exist" not in output:
                print(f"  ⚠️  {name}: Path exists but no lock settings found")
            else:
                print(f"  ❌ {name}: Path does not exist")
        except Exception as e:
            print(f"  ⚠️  {name}: Error - {e}")

    print()

    # Step 2: Try to modify common lock settings
    print("🔧 STEP 2: Attempting to modify lock settings...")
    print("-" * 70)

    # Common registry values that might control locks
    modifications = [
        (r"HKCU\SOFTWARE\ASUS\AacHal", "FnLock", "0", "REG_DWORD"),
        (r"HKCU\SOFTWARE\ASUS\AacHal", "WinLock", "0", "REG_DWORD"),
        (r"HKCU\SOFTWARE\ASUS\ATK", "FnLock", "0", "REG_DWORD"),
        (r"HKCU\SOFTWARE\ASUS\ATK", "WinLock", "0", "REG_DWORD"),
        (r"HKCU\SOFTWARE\ASUS\ArmouryDevice", "FnLock", "0", "REG_DWORD"),
        (r"HKCU\SOFTWARE\ASUS\ArmouryDevice", "WinLock", "0", "REG_DWORD"),
        (r"HKCU\SOFTWARE\ASUS\ArmouryCrate", "FnLock", "0", "REG_DWORD"),
        (r"HKCU\SOFTWARE\ASUS\ArmouryCrate", "WinLock", "0", "REG_DWORD"),
    ]

    modified = []

    for reg_path, value_name, value_data, value_type in modifications:
        try:
            # Try to set the value
            ps_cmd = (
                f"$path = '{reg_path}'; "
                f"if (Test-Path $path) {{ "
                f"  try {{ "
                f"    Set-ItemProperty -Path $path -Name '{value_name}' -Value {value_data} -Type {value_type} -ErrorAction Stop; "
                f"    Write-Host 'SUCCESS' "
                f"  }} catch {{ Write-Host 'FAILED: ' + $_.Exception.Message }} "
                f"}} else {{ "
                f"  try {{ "
                f"    New-Item -Path $path -Force -ErrorAction Stop | Out-Null; "
                f"    Set-ItemProperty -Path $path -Name '{value_name}' -Value {value_data} -Type {value_type} -ErrorAction Stop; "
                f"    Write-Host 'CREATED_AND_SET' "
                f"  }} catch {{ Write-Host 'FAILED: ' + $_.Exception.Message }} "
                f"}}"
            )
            result = integration._run_powershell(ps_cmd)

            # Handle dict result from _run_powershell
            if isinstance(result, dict):
                output = result.get("stdout", "")
            else:
                output = str(result) if result else ""

            if output and ("SUCCESS" in output or "CREATED_AND_SET" in output):
                print(f"  ✅ {reg_path}\\{value_name} = {value_data}")
                modified.append((reg_path, value_name))
            elif output and "FAILED" in output:
                print(f"  ⚠️  {reg_path}\\{value_name}: {output}")
            else:
                print(f"  ⚠️  {reg_path}\\{value_name}: Unknown result ({output[:50] if output else 'None'})")
        except Exception as e:
            print(f"  ⚠️  {reg_path}\\{value_name}: Error - {e}")

    print()

    # Step 3: Restart Armoury Crate processes to apply changes
    if modified:
        print("🔄 STEP 3: Restarting Armoury Crate processes to apply changes...")
        print("-" * 70)

        processes = ["ArmouryCrateControlInterface", "ArmouryCrate"]
        for process in processes:
            try:
                ps_cmd = (
                    f"$proc = Get-Process -Name '{process}' -ErrorAction SilentlyContinue; "
                    f"if ($proc) {{ "
                    f"  Stop-Process -Name '{process}' -Force -ErrorAction SilentlyContinue; "
                    f"  Start-Sleep -Milliseconds 1000; "
                    f"  $path = Get-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\{process}.exe' -ErrorAction SilentlyContinue; "
                    f"  if (-not $path) {{ "
                    f"    $path = 'C:\\Program Files\\ASUS\\ArmouryDevice\\{process}.exe' "
                    f"  }} else {{ "
                    f"    $path = $path.'(default)' "
                    f"  }}; "
                    f"  if (Test-Path $path) {{ "
                    f"    Start-Process -FilePath $path -WindowStyle Hidden -ErrorAction SilentlyContinue; "
                    f"    Write-Host 'RESTARTED' "
                    f"  }} else {{ Write-Host 'PATH_NOT_FOUND' }} "
                    f"}} else {{ Write-Host 'NOT_RUNNING' }}"
                )
                result = integration._run_powershell(ps_cmd)
                if result and "RESTARTED" in result:
                    print(f"  ✅ {process}: Restarted")
                else:
                    print(f"  ⚠️  {process}: {result if result else 'Unknown'}")
            except Exception as e:
                print(f"  ⚠️  {process}: Error - {e}")

    print()
    print("=" * 70)
    print("💡 SUMMARY:")
    print("=" * 70)
    print(f"  Registry modifications attempted: {len(modified)}")
    print()
    print("  If lock symbols still persist:")
    print("  1. Check Armoury Crate UI: Device > System Configuration")
    print("  2. Look for 'Function Key Behavior' or 'Action Key Mode'")
    print("  3. Look for 'Windows Key Lock' setting")
    print("  4. Try BIOS/UEFI: Advanced > System Configuration > Action Key Mode")
    print("  5. Restart computer after registry changes")
    print("=" * 70)

    return True

if __name__ == "__main__":


    asyncio.run(main())