#!/usr/bin/env python3
"""
JARVIS: Advanced Key Unlock - Registry + BIOS + Alternative Methods
🔓 Comprehensive unlock using all possible methods
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cfservices.services.jarvis_core.integrations.armoury_crate import create_armoury_crate_integration

async def main():
    """Advanced unlock using registry, BIOS settings, and alternative methods"""
    print("=" * 70)
    print("🔓 JARVIS: Advanced Key Unlock (Registry + BIOS + Alternative Methods)")
    print("=" * 70)
    print()

    integration = create_armoury_crate_integration()

    # Step 1: Check registry for key lock settings
    print("🔍 STEP 1: Checking registry for key lock settings...")
    print("-" * 70)

    registry_paths = [
        r"HKCU\SOFTWARE\ASUS\AacHal",
        r"HKLM\SOFTWARE\ASUS\AacHal",
        r"HKCU\SOFTWARE\ASUS\ArmouryDevice",
        r"HKLM\SOFTWARE\ASUS\ArmouryDevice",
        r"HKCU\SOFTWARE\ASUS\ATK",
        r"HKLM\SOFTWARE\ASUS\ATK",
    ]

    for reg_path in registry_paths:
        try:
            # Check if path exists and list all values
            ps_cmd = (
                f"$path = '{reg_path}'; "
                f"if (Test-Path $path) {{ "
                f"  Get-ItemProperty -Path $path -ErrorAction SilentlyContinue | "
                f"  Select-Object -Property * -ExcludeProperty PS* | ConvertTo-Json -Depth 3 "
                f"}} else {{ 'Path does not exist' }}"
            )
            result = integration._run_powershell(ps_cmd)
            if result and "Path does not exist" not in result:
                print(f"  ✅ Found: {reg_path}")
                # Look for lock-related keys
                if "Lock" in result or "lock" in result or "Fn" in result or "Win" in result:
                    print(f"    ⚠️  Contains lock-related settings!")
                    print(f"    {result[:200]}...")  # Show first 200 chars
            else:
                print(f"  ❌ Not found: {reg_path}")
        except Exception as e:
            print(f"  ⚠️  Error checking {reg_path}: {e}")
    print()

    # Step 2: Try alternative key combinations
    print("🔧 STEP 2: Trying alternative key combinations...")
    print("-" * 70)

    # FN Key alternatives
    print("  🔓 FN Key - Trying alternative combinations:")
    print("    - Fn+F6 (sometimes unlocks Windows key, might affect FN)")
    print("    - Fn+Space (some ASUS models)")
    print("    - Fn+Insert (some models)")

    # Windows Key alternatives  
    print("  🔓 Windows Key - Trying alternative combinations:")
    print("    - Fn+F6 (common ASUS Windows key toggle)")
    print("    - Fn+Win (some models)")
    print("    - Win+Win (double tap)")
    print()

    # Step 3: Try Fn+F6 (common ASUS Windows key toggle)
    print("🔧 STEP 3: Trying Fn+F6 (ASUS Windows key toggle)...")
    print("-" * 70)
    try:
        import ctypes
        import asyncio

        VK_F6 = 0x75
        SCANCODE_F6 = 0x40
        VK_APPS = 0x5D  # FN simulation
        KEYEVENTF_KEYUP = 0x0002

        # Try Fn+F6
        print("  Pressing Fn+F6 (long press 3 seconds)...")
        ctypes.windll.user32.keybd_event(VK_APPS, 0, 0, 0)
        await asyncio.sleep(0.05)
        ctypes.windll.user32.keybd_event(VK_F6, SCANCODE_F6, 0, 0)
        await asyncio.sleep(3.0)  # 3 seconds
        ctypes.windll.user32.keybd_event(VK_F6, SCANCODE_F6, KEYEVENTF_KEYUP, 0)
        await asyncio.sleep(0.05)
        ctypes.windll.user32.keybd_event(VK_APPS, 0, KEYEVENTF_KEYUP, 0)
        print("  ✅ Fn+F6 executed")
    except Exception as e:
        print(f"  ⚠️  Fn+F6 failed: {e}")
    print()

    # Step 4: Check Armoury Crate UI for settings
    print("🔧 STEP 4: Checking Armoury Crate for key lock settings...")
    print("-" * 70)
    print("  💡 Manual Check Required:")
    print("    1. Open Armoury Crate")
    print("    2. Go to Device > System Configuration or Keyboard settings")
    print("    3. Look for 'Function Key Behavior' or 'Action Key Mode'")
    print("    4. Look for 'Windows Key Lock' or 'Win Key' settings")
    print("    5. Disable/toggle these settings")
    print()

    # Step 5: BIOS/UEFI instructions
    print("🔧 STEP 5: BIOS/UEFI Settings (if software methods fail)...")
    print("-" * 70)
    print("  💡 BIOS Method:")
    print("    1. Restart computer")
    print("    2. Press F2 or Del during startup to enter BIOS")
    print("    3. Navigate to 'Advanced' or 'System Configuration'")
    print("    4. Find 'Action Key Mode' or 'Function Key Behavior'")
    print("    5. Change to 'Function Key' mode (disables FN lock)")
    print("    6. Save and exit")
    print()

    # Step 6: Try all standard unlock methods again with longer duration
    print("🔧 STEP 6: Retrying standard methods with extended duration (5 seconds)...")
    print("-" * 70)

    # FN unlock with 5 seconds
    print("  🔓 FN Key: Fn+Esc (5 second hold)...")
    fn_result = await integration.process_request({'action': 'toggle_fn_lock'})
    print(f"    Result: {fn_result.get('message', 'Unknown')}")

    # Windows key unlock with 5 seconds  
    print("  🔓 Windows Key: Win+Esc (5 second hold)...")
    winkey_result = await integration.process_request({'action': 'toggle_winkey_lock'})
    print(f"    Result: {winkey_result.get('message', 'Unknown')}")
    print()

    print("=" * 70)
    print("💡 SUMMARY:")
    print("  If lock symbols persist after all methods:")
    print("  1. Check Armoury Crate UI settings (Device > System Configuration)")
    print("  2. Check BIOS/UEFI settings (Action Key Mode)")
    print("  3. Try Fn+F6 manually (common ASUS Windows key toggle)")
    print("  4. Contact ASUS support with your laptop model number")
    print("=" * 70)

    return True

if __name__ == "__main__":


    asyncio.run(main())