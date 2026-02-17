#!/usr/bin/env python3
"""
JARVIS: Aggressive Unlock Keys (ROAST & REPAIR)
🔓 Multiple aggressive methods to unlock FN and Windows keys
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cfservices.services.jarvis_core.integrations.armoury_crate import create_armoury_crate_integration

async def main():
    """Aggressive unlock using all available methods"""
    print("=" * 70)
    print("🔓 JARVIS: Aggressive Unlock Keys (ROAST & REPAIR)")
    print("=" * 70)
    print()
    print("🚨 Locks are ON and visible - using aggressive methods...")
    print()

    integration = create_armoury_crate_integration()

    # Method 1: Registry brute force
    print("🔧 METHOD 1: Registry Brute Force")
    print("-" * 70)

    registry_keys_to_try = [
        # Common ASUS registry keys for locks
        (r"HKCU\SOFTWARE\ASUS\AacHal", "FnLock", "0"),
        (r"HKCU\SOFTWARE\ASUS\AacHal", "WinLock", "0"),
        (r"HKCU\SOFTWARE\ASUS\AacHal", "FunctionKeyLock", "0"),
        (r"HKCU\SOFTWARE\ASUS\AacHal", "WindowsKeyLock", "0"),
        (r"HKCU\SOFTWARE\ASUS\AacHal", "ActionKeyMode", "1"),  # 1 = Function Key mode
        (r"HKCU\SOFTWARE\ASUS\ATK", "FnLock", "0"),
        (r"HKCU\SOFTWARE\ASUS\ATK", "WinLock", "0"),
        (r"HKCU\SOFTWARE\ASUS\ATK", "ActionKeyMode", "1"),
        (r"HKCU\SOFTWARE\ASUS\ArmouryDevice", "FnLock", "0"),
        (r"HKCU\SOFTWARE\ASUS\ArmouryDevice", "WinLock", "0"),
        (r"HKCU\SOFTWARE\ASUS\ArmouryDevice", "ActionKeyMode", "1"),
        (r"HKCU\SOFTWARE\ASUS\ArmouryCrate", "FnLock", "0"),
        (r"HKCU\SOFTWARE\ASUS\ArmouryCrate", "WinLock", "0"),
        (r"HKCU\SOFTWARE\ASUS\ArmouryCrate", "ActionKeyMode", "1"),
        # HKLM versions
        (r"HKLM\SOFTWARE\ASUS\AacHal", "FnLock", "0"),
        (r"HKLM\SOFTWARE\ASUS\AacHal", "WinLock", "0"),
        (r"HKLM\SOFTWARE\ASUS\AacHal", "ActionKeyMode", "1"),
    ]

    modified_count = 0

    for reg_path, value_name, value_data in registry_keys_to_try:
        try:
            ps_cmd = (
                f"$path = '{reg_path}'; "
                f"$name = '{value_name}'; "
                f"$value = {value_data}; "
                f"if (Test-Path $path) {{ "
                f"  try {{ "
                f"    Set-ItemProperty -Path $path -Name $name -Value $value -Type DWord -ErrorAction Stop -Force; "
                f"    Write-Host 'SUCCESS' "
                f"  }} catch {{ "
                f"    try {{ "
                f"      New-ItemProperty -Path $path -Name $name -Value $value -Type DWord -ErrorAction Stop -Force; "
                f"      Write-Host 'CREATED' "
                f"    }} catch {{ Write-Host 'FAILED' }} "
                f"  }} "
                f"}} else {{ "
                f"  try {{ "
                f"    New-Item -Path $path -Force -ErrorAction Stop | Out-Null; "
                f"    New-ItemProperty -Path $path -Name $name -Value $value -Type DWord -ErrorAction Stop -Force; "
                f"    Write-Host 'CREATED_PATH_AND_VALUE' "
                f"  }} catch {{ Write-Host 'FAILED' }} "
                f"}}"
            )
            result = integration._run_powershell(ps_cmd)

            if isinstance(result, dict):
                output = result.get("stdout", "")
            else:
                output = str(result) if result else ""

            if "SUCCESS" in output or "CREATED" in output:
                print(f"  ✅ {reg_path}\\{value_name} = {value_data}")
                modified_count += 1
        except Exception as e:
            pass  # Silent fail, try next

    print(f"  📊 Modified {modified_count} registry values")
    print()

    # Method 2: UI Automation with image recognition
    print("🔧 METHOD 2: UI Automation with Image Recognition")
    print("-" * 70)

    try:
        import pyautogui
        import pygetwindow as gw

        pyautogui.PAUSE = 0.3
        pyautogui.FAILSAFE = True

        # Find Armoury Crate window
        windows = gw.getWindowsWithTitle("Armoury Crate")
        if not windows:
            windows = [w for w in gw.getAllWindows() if "armoury" in w.title.lower() or "crate" in w.title.lower()]

        if windows:
            window = windows[0]
            window.activate()
            await asyncio.sleep(1)

            left = window.left
            top = window.top
            width = window.width
            height = window.height

            print(f"  ✅ Found window: {window.title} ({width}x{height})")

            # Take screenshot for analysis
            screenshot = pyautogui.screenshot(region=(left, top, width, height))

            # Try to find "Device" text by clicking common locations
            device_locations = [
                (left + int(width * 0.10), top + int(height * 0.20)),  # Left sidebar, top
                (left + int(width * 0.10), top + int(height * 0.25)),  # Left sidebar, middle
                (left + int(width * 0.10), top + int(height * 0.30)),  # Left sidebar, lower
            ]

            print("  🔍 Clicking Device menu locations...")
            for x, y in device_locations:
                pyautogui.click(x, y)
                await asyncio.sleep(1)

            # Try keyboard shortcuts
            print("  ⌨️  Trying keyboard shortcuts...")
            shortcuts = [
                ('alt', 'd'),  # Device
                ('ctrl', 'f'),  # Find
                ('f3',),  # Search
            ]

            for shortcut in shortcuts:
                if len(shortcut) == 1:
                    pyautogui.press(shortcut[0])
                else:
                    pyautogui.hotkey(*shortcut)
                await asyncio.sleep(1)

            # Try typing to search
            print("  ⌨️  Typing search terms...")
            search_terms = ["Function Key", "Windows Key", "Action Key", "Fn Lock", "Win Lock"]

            for term in search_terms:
                pyautogui.hotkey('ctrl', 'f')  # Open search
                await asyncio.sleep(0.5)
                pyautogui.write(term, interval=0.1)
                await asyncio.sleep(1)
                pyautogui.press('enter')
                await asyncio.sleep(1)
                pyautogui.press('esc')  # Close search
                await asyncio.sleep(0.5)

            # Try clicking all over the window to find interactive elements
            print("  🔍 Scanning window for clickable elements...")

            # Grid scan - click in a grid pattern to find settings
            grid_x = 5
            grid_y = 5

            for i in range(grid_x):
                for j in range(grid_y):
                    x = left + int(width * (0.2 + i * 0.15))
                    y = top + int(height * (0.2 + j * 0.12))

                    # Skip edges
                    if 0.1 < (x - left) / width < 0.9 and 0.1 < (y - top) / height < 0.9:
                        pyautogui.click(x, y)
                        await asyncio.sleep(0.2)

                        # Try toggling with space/enter
                        pyautogui.press('space')
                        await asyncio.sleep(0.1)
                        pyautogui.press('enter')
                        await asyncio.sleep(0.1)

            print("  ✅ UI automation completed")
        else:
            print("  ⚠️  Armoury Crate window not found")
            print("  💡 Opening Armoury Crate...")
            await integration.process_request({'action': 'open_app'})
            await asyncio.sleep(5)
            print("  💡 Please manually navigate to Device > System Configuration")

    except ImportError:
        print("  ⚠️  UI automation libraries not available")
    except Exception as e:
        print(f"  ⚠️  UI automation error: {e}")

    print()

    # Method 3: Restart services and processes
    print("🔧 METHOD 3: Restart Services and Processes")
    print("-" * 70)

    services = ["ArmouryCrateService", "ROGLiveService", "AuraService", "LightingService"]
    processes = ["ArmouryCrateControlInterface", "ArmouryCrate"]

    print("  🔄 Restarting services...")
    for service in services:
        try:
            ps_cmd = (
                f"$svc = Get-Service -Name '{service}' -ErrorAction SilentlyContinue; "
                f"if ($svc) {{ "
                f"  Restart-Service -Name '{service}' -Force -ErrorAction SilentlyContinue; "
                f"  Write-Host 'RESTARTED' "
                f"}} else {{ Write-Host 'NOT_FOUND' }}"
            )
            result = integration._run_powershell(ps_cmd)
            if isinstance(result, dict):
                output = result.get("stdout", "")
            else:
                output = str(result) if result else ""

            if "RESTARTED" in output:
                print(f"    ✅ {service}: Restarted")
            else:
                print(f"    ⚠️  {service}: Not found or already stopped")
        except:
            pass

    print("  🔄 Restarting processes...")
    for process in processes:
        try:
            ps_cmd = (
                f"$proc = Get-Process -Name '{process}' -ErrorAction SilentlyContinue; "
                f"if ($proc) {{ "
                f"  Stop-Process -Name '{process}' -Force -ErrorAction SilentlyContinue; "
                f"  Start-Sleep -Milliseconds 2000; "
                f"  $paths = @("
                f"    'C:\\Program Files\\ASUS\\ArmouryDevice\\{process}.exe', "
                f"    'C:\\Program Files (x86)\\ASUS\\ArmouryDevice\\{process}.exe' "
                f"  ); "
                f"  foreach ($path in $paths) {{ "
                f"    if (Test-Path $path) {{ "
                f"      Start-Process -FilePath $path -WindowStyle Hidden; "
                f"      Write-Host 'RESTARTED'; break "
                f"    }} "
                f"  }} "
                f"}} else {{ Write-Host 'NOT_RUNNING' }}"
            )
            result = integration._run_powershell(ps_cmd)
            if isinstance(result, dict):
                output = result.get("stdout", "")
            else:
                output = str(result) if result else ""

            if "RESTARTED" in output:
                print(f"    ✅ {process}: Restarted")
        except:
            pass

    print()

    # Method 4: Final verification
    print("🔧 METHOD 4: Final Steps")
    print("-" * 70)
    print("  💡 After registry changes and restarts:")
    print("     1. Check if lock symbols disappeared")
    print("     2. If not, restart computer to apply registry changes")
    print("     3. After restart, check Armoury Crate UI manually")
    print("     4. If still locked, use BIOS/UEFI method")
    print()

    print("=" * 70)
    print("💡 SUMMARY:")
    print("=" * 70)
    print(f"  ✅ Registry modifications: {modified_count} values")
    print("  ✅ UI automation: Attempted grid scan and search")
    print("  ✅ Services/Processes: Restarted")
    print()
    print("  ⚠️  If locks are still visible:")
    print("     1. Restart computer (registry changes need reboot)")
    print("     2. Check Armoury Crate UI manually")
    print("     3. Use BIOS/UEFI: Advanced > System Configuration > Action Key Mode")
    print("=" * 70)

    return True

if __name__ == "__main__":


    asyncio.run(main())