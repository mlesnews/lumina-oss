#!/usr/bin/env python3
"""
JARVIS: Unlock Keys via Armoury Crate UI
🔓 Opens Armoury Crate and navigates to key lock settings
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cfservices.services.jarvis_core.integrations.armoury_crate import create_armoury_crate_integration

async def main():
    """Open Armoury Crate and guide user to key lock settings"""
    print("=" * 70)
    print("🔓 JARVIS: Unlock Keys via Armoury Crate UI")
    print("=" * 70)
    print()
    print("💡 The lock symbols are likely controlled by Armoury Crate settings.")
    print("   This script will open Armoury Crate and guide you to the settings.")
    print()

    integration = create_armoury_crate_integration()

    # Step 1: Open Armoury Crate
    print("🔧 STEP 1: Opening Armoury Crate...")
    print("-" * 70)
    open_result = await integration.process_request({
        'action': 'open_app'
    })

    if open_result.get('success'):
        print("✅ Armoury Crate opened")
    else:
        print(f"⚠️  Could not open Armoury Crate: {open_result.get('message', 'Unknown')}")
        print("   Please open Armoury Crate manually")
    print()

    # Step 2: Instructions
    print("🔧 STEP 2: Navigate to Key Lock Settings")
    print("-" * 70)
    print("📋 MANUAL STEPS (follow these in Armoury Crate):")
    print()
    print("   Option A: System Configuration")
    print("   1. In Armoury Crate, click 'Device' (left sidebar)")
    print("   2. Click 'System Configuration' or 'System'")
    print("   3. Look for 'Function Key Behavior' or 'Action Key Mode'")
    print("   4. Change it to 'Function Key' mode (disables FN lock)")
    print("   5. Look for 'Windows Key Lock' or 'Win Key' setting")
    print("   6. Disable/toggle Windows Key Lock")
    print()
    print("   Option B: Keyboard Settings")
    print("   1. In Armoury Crate, click 'Device' > 'Keyboard'")
    print("   2. Look for 'Function Key Lock' or 'FN Lock'")
    print("   3. Toggle it OFF")
    print("   4. Look for 'Windows Key Lock'")
    print("   5. Toggle it OFF")
    print()
    print("   Option C: Advanced Settings")
    print("   1. In Armoury Crate, click 'Device' > 'Advanced' or 'Settings'")
    print("   2. Look for keyboard-related settings")
    print("   3. Find and disable key locks")
    print()

    # Step 3: Alternative - BIOS
    print("🔧 STEP 3: If Armoury Crate doesn't have the setting, use BIOS/UEFI")
    print("-" * 70)
    print("📋 BIOS/UEFI METHOD:")
    print("   1. Restart your computer")
    print("   2. Press F2 or Del repeatedly during startup (before Windows loads)")
    print("   3. Navigate to 'Advanced' tab")
    print("   4. Find 'System Configuration' or 'Keyboard' section")
    print("   5. Look for 'Action Key Mode' or 'Function Key Behavior'")
    print("   6. Change to 'Function Key' mode (this disables FN lock)")
    print("   7. Look for 'Windows Key Lock' setting")
    print("   8. Disable it")
    print("   9. Press F10 to Save and Exit")
    print("   10. Restart computer")
    print()

    # Step 4: Check registry for any settings we can modify
    print("🔧 STEP 4: Checking registry for modifiable settings...")
    print("-" * 70)

    # Try to find and read registry values that might control locks
    registry_checks = [
        (r"HKCU\SOFTWARE\ASUS\AacHal", "AacHal User"),
        (r"HKLM\SOFTWARE\ASUS\AacHal", "AacHal System"),
        (r"HKCU\SOFTWARE\ASUS\ArmouryDevice", "ArmouryDevice User"),
        (r"HKLM\SOFTWARE\ASUS\ArmouryDevice", "ArmouryDevice System"),
    ]

    for reg_path, name in registry_checks:
        try:
            # List all properties
            ps_cmd = (
                f"$path = '{reg_path}'; "
                f"if (Test-Path $path) {{ "
                f"  $props = Get-ItemProperty -Path $path -ErrorAction SilentlyContinue; "
                f"  $props.PSObject.Properties.Name | Where-Object {{ $_ -like '*Lock*' -or $_ -like '*Fn*' -or $_ -like '*Win*' -or $_ -like '*Key*' }} | "
                f"  ForEach-Object {{ Write-Host \"$_ = $($props.$_)\" }} "
                f"}}"
            )
            result = integration._run_powershell(ps_cmd)
            if result and result.strip():
                print(f"  ✅ {name}: Found lock-related settings:")
                for line in result.strip().split('\n'):
                    if line.strip():
                        print(f"     {line.strip()}")
        except Exception as e:
            pass

    print()
    print("=" * 70)
    print("💡 SUMMARY:")
    print("  The lock symbols are controlled by:")
    print("  1. Armoury Crate software settings (most likely)")
    print("  2. BIOS/UEFI 'Action Key Mode' setting")
    print("  3. Registry settings (may require admin)")
    print()
    print("  Key combinations (Fn+Esc, Win+Esc) only work if the locks")
    print("  are enabled at the hardware/BIOS level, not software level.")
    print("=" * 70)

    return True

if __name__ == "__main__":


    asyncio.run(main())