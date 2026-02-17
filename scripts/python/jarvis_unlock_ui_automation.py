#!/usr/bin/env python3
"""
JARVIS: Unlock Keys via UI Automation
🔓 Opens Armoury Crate and attempts to navigate to lock settings
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cfservices.services.jarvis_core.integrations.armoury_crate import create_armoury_crate_integration

async def main():
    """Open Armoury Crate and guide user to lock settings"""
    print("=" * 70)
    print("🔓 JARVIS: Unlock Keys via UI Automation")
    print("=" * 70)
    print()
    print("💡 Since key combinations didn't work, we'll use Armoury Crate UI")
    print()

    integration = create_armoury_crate_integration()

    # Step 1: Open Armoury Crate
    print("🔧 STEP 1: Opening Armoury Crate...")
    print("-" * 70)

    try:
        open_result = await integration.process_request({'action': 'open_app'})
        if open_result.get('success'):
            print("✅ Armoury Crate opened")
            print("   Waiting 3 seconds for it to load...")
            await asyncio.sleep(3)
        else:
            print(f"⚠️  Could not open automatically: {open_result.get('message', 'Unknown')}")
            print("   Please open Armoury Crate manually")
    except Exception as e:
        print(f"⚠️  Error opening Armoury Crate: {e}")
        print("   Please open Armoury Crate manually")

    print()

    # Step 2: Instructions for navigation
    print("🔧 STEP 2: Navigate to Lock Settings (MANUAL STEPS)")
    print("-" * 70)
    print()
    print("📋 FOLLOW THESE STEPS IN ARMOURY CRATE:")
    print()
    print("   METHOD A: System Configuration")
    print("   ──────────────────────────────")
    print("   1. In Armoury Crate, look for 'Device' in the left sidebar")
    print("   2. Click 'Device'")
    print("   3. Look for 'System Configuration' or 'System' tab")
    print("   4. Find 'Function Key Behavior' or 'Action Key Mode'")
    print("      → Change to 'Function Key' mode (disables FN lock)")
    print("   5. Look for 'Windows Key Lock' or 'Win Key' setting")
    print("      → Toggle it OFF")
    print()
    print("   METHOD B: Keyboard Settings")
    print("   ────────────────────────────")
    print("   1. In Armoury Crate, click 'Device' > 'Keyboard'")
    print("   2. Look for 'Function Key Lock' or 'FN Lock'")
    print("      → Toggle it OFF")
    print("   3. Look for 'Windows Key Lock'")
    print("      → Toggle it OFF")
    print()
    print("   METHOD C: Advanced/Settings")
    print("   ────────────────────────────")
    print("   1. In Armoury Crate, click 'Device' > 'Advanced' or 'Settings'")
    print("   2. Look for keyboard-related settings")
    print("   3. Find and disable key locks")
    print()

    # Step 3: Try UI automation if available
    print("🔧 STEP 3: Attempting UI Automation (if available)...")
    print("-" * 70)

    try:
        # Check if pyautogui is available
        try:
            import pyautogui
            import pygetwindow as gw

            print("  ✅ UI automation libraries available")
            print("  🔍 Looking for Armoury Crate window...")

            # Find Armoury Crate window
            windows = gw.getWindowsWithTitle("Armoury Crate")
            if not windows:
                windows = gw.getWindowsWithTitle("Armoury")

            if windows:
                window = windows[0]
                print(f"  ✅ Found window: {window.title}")
                window.activate()
                await asyncio.sleep(1)

                # Try to click on Device menu (approximate position)
                # Note: This is approximate and may need adjustment
                print("  🔍 Attempting to navigate to Device menu...")
                print("  ⚠️  UI automation is approximate - please verify manually")

                # Get window center
                center_x = window.left + window.width // 2
                center_y = window.top + window.height // 2

                # Try clicking on left sidebar area (where Device usually is)
                sidebar_x = window.left + 100
                sidebar_y = window.top + 200

                print(f"  📍 Clicking approximate Device menu location...")
                pyautogui.click(sidebar_x, sidebar_y)
                await asyncio.sleep(1)

                print("  ⚠️  Please verify if Device menu opened")
                print("  ⚠️  If not, follow the manual steps above")
            else:
                print("  ⚠️  Armoury Crate window not found")
                print("  💡 Make sure Armoury Crate is open and visible")
        except ImportError:
            print("  ⚠️  UI automation libraries not available")
            print("  💡 Install pyautogui and pygetwindow for UI automation")
        except Exception as e:
            print(f"  ⚠️  UI automation failed: {e}")
            print("  💡 Please use manual steps above")
    except Exception as e:
        print(f"  ⚠️  Error: {e}")

    print()

    # Step 4: Alternative - BIOS method
    print("🔧 STEP 4: Alternative - BIOS/UEFI Method")
    print("-" * 70)
    print()
    print("📋 If Armoury Crate doesn't have the settings, use BIOS:")
    print()
    print("   1. Restart your computer")
    print("   2. Press F2 or Del repeatedly during startup")
    print("   3. Navigate to 'Advanced' tab")
    print("   4. Find 'System Configuration' or 'Keyboard' section")
    print("   5. Look for 'Action Key Mode' or 'Function Key Behavior'")
    print("   6. Change to 'Function Key' mode (disables FN lock)")
    print("   7. Look for 'Windows Key Lock' setting")
    print("   8. Disable it")
    print("   9. Press F10 to Save and Exit")
    print("   10. Restart computer")
    print()

    print("=" * 70)
    print("💡 SUMMARY:")
    print("=" * 70)
    print("  Since key combinations (Fn+Esc, Win+Esc) didn't work,")
    print("  the locks are controlled by software (Armoury Crate) or BIOS.")
    print()
    print("  Next steps:")
    print("  1. Check Armoury Crate UI (follow steps above)")
    print("  2. If not found, check BIOS/UEFI settings")
    print("  3. Restart computer after making changes")
    print("=" * 70)

    return True

if __name__ == "__main__":


    asyncio.run(main())