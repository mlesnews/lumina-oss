#!/usr/bin/env python3
"""
JARVIS: Use ASUS Function Manager to Unlock FN Keys
Found via #syphon analysis: AsusXUserFunctionManager.exe

@JARVIS @ASUS @FUNCTION_MANAGER @FN_UNLOCK
"""

import sys
import subprocess
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

logger = get_logger("JARVIS_ASUS_FunctionManager")


def main():
    """Use ASUS Function Manager to unlock FN keys"""
    print("=" * 70)
    print("🔓 JARVIS: Using ASUS Function Manager to Unlock FN Keys")
    print("=" * 70)
    print()

    # Found via #syphon analysis
    function_manager_paths = [
        r"C:\Program Files\ASUS\AsusScreenXpert\AsusXUserFunctionManager.exe",
        r"C:\Program Files\ASUS\AsusScreenXpert\Arm\AsusXUserFunctionManager.exe"
    ]

    found_path = None
    for path in function_manager_paths:
        if Path(path).exists():
            found_path = path
            logger.info(f"✅ Found ASUS Function Manager: {path}")
            break

    if not found_path:
        print("❌ ASUS Function Manager not found at expected locations")
        print("   Expected locations:")
        for path in function_manager_paths:
            print(f"     - {path}")
        return

    print(f"\n📋 Attempting to use: {found_path}")
    print()
    print("METHOD 1: Try to run with unlock parameters...")

    # Method 1: Try running with command-line parameters
    # Common parameters for function key managers: /unlock, /toggle, /fnlock
    unlock_params = ["/unlock", "/toggle", "/fnlock", "-unlock", "-toggle"]

    for param in unlock_params:
        try:
            print(f"  Trying: {found_path} {param}")
            result = subprocess.run(
                [found_path, param],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"  ✅ Success with parameter: {param}")
            else:
                print(f"  ⚠️  Exit code: {result.returncode}")
        except Exception as e:
            print(f"  ❌ Error: {e}")

    print()
    print("METHOD 2: Open ASUS Function Manager GUI...")
    try:
        # Just open it - user can interact with GUI
        subprocess.Popen([found_path], shell=True)
        print(f"  ✅ Opened ASUS Function Manager")
        print("  → Look for 'Function Key Lock' or 'Hotkey Mode' toggle")
        print("  → Toggle it OFF to unlock FN keys")
    except Exception as e:
        print(f"  ❌ Error opening: {e}")

    print()
    print("METHOD 3: Check if we can control it via registry...")
    try:
        ps_command = """
        # ASUS ScreenXpert registry paths
        $regPaths = @(
            'HKCU:\\Software\\ASUS\\ScreenXpert',
            'HKCU:\\Software\\ASUS\\AsusScreenXpert',
            'HKLM:\\SOFTWARE\\ASUS\\ScreenXpert',
            'HKLM:\\SOFTWARE\\ASUS\\AsusScreenXpert'
        );
        $found = @();
        foreach ($path in $regPaths) {
            if (Test-Path $path) {
                $props = Get-ItemProperty -Path $path -ErrorAction SilentlyContinue;
                $fnKeys = $props | Get-Member -MemberType NoteProperty | Where-Object {
                    $_.Name -like '*FN*' -or $_.Name -like '*Function*' -or $_.Name -like '*Hotkey*'
                };
                if ($fnKeys) {
                    foreach ($key in $fnKeys) {
                        $val = $props.$($key.Name);
                        $found += "$path\\$($key.Name)=$val";
                    }
                }
            }
        }
        if ($found.Count -gt 0) {
            $found -join '|'
        } else {
            'NoScreenXpertRegKeys'
        }
        """

        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
            capture_output=True,
            text=True,
            timeout=10
        )

        if "NoScreenXpertRegKeys" not in result.stdout:
            print(f"  ✅ Found registry keys:")
            for key in result.stdout.strip().split('|'):
                print(f"     {key}")
        else:
            print("  ⚠️  No ScreenXpert registry keys found")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    print()
    print("=" * 70)
    print("📋 MANUAL STEPS:")
    print("=" * 70)
    print("1. The ASUS Function Manager should now be open")
    print("2. Look for 'Function Key Lock' or 'Hotkey Mode' setting")
    print("3. Toggle it OFF to unlock FN keys")
    print("4. Once unlocked, try Fn+F4 to control lighting")
    print("5. If not visible, check System Tray for ASUS icons")
    print()
    print("ALTERNATIVE: Open Armoury Crate → Device → Keyboard → Settings")
    print("  → Look for 'Function Key Behavior' or 'Hotkey Mode'")
    print("=" * 70)


if __name__ == "__main__":


    main()