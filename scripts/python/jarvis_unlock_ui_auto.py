#!/usr/bin/env python3
"""
JARVIS: Unlock Keys via UI Automation (FULL AUTO)
🔓 Automatically navigates Armoury Crate UI to unlock FN and Windows keys
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cfservices.services.jarvis_core.integrations.armoury_crate import create_armoury_crate_integration

async def main():
    """Fully automate unlocking keys via Armoury Crate UI"""
    print("=" * 70)
    print("🔓 JARVIS: Unlock Keys via UI Automation (FULL AUTO)")
    print("=" * 70)
    print()

    integration = create_armoury_crate_integration()

    # Step 1: Open Armoury Crate
    print("🔧 STEP 1: Opening Armoury Crate...")
    print("-" * 70)

    try:
        open_result = await integration.process_request({'action': 'open_app'})
        if open_result.get('success'):
            print("✅ Armoury Crate opened")
            print("   Waiting 5 seconds for full load...")
            await asyncio.sleep(5)
        else:
            print(f"⚠️  Could not open automatically: {open_result.get('message', 'Unknown')}")
            print("   Please open Armoury Crate manually and press Enter when ready...")
            input()
    except Exception as e:
        print(f"⚠️  Error opening Armoury Crate: {e}")
        print("   Please open Armoury Crate manually and press Enter when ready...")
        input()

    print()

    # Step 2: UI Automation
    print("🔧 STEP 2: Automating UI Navigation...")
    print("-" * 70)

    try:
        import pyautogui
        import pygetwindow as gw

        # Safety settings
        pyautogui.PAUSE = 0.5
        pyautogui.FAILSAFE = True

        print("  ✅ UI automation libraries available")

        # Find Armoury Crate window
        print("  🔍 Looking for Armoury Crate window...")
        await asyncio.sleep(1)

        windows = gw.getWindowsWithTitle("Armoury Crate")
        if not windows:
            windows = gw.getWindowsWithTitle("Armoury")
        if not windows:
            # Try partial match
            all_windows = gw.getAllWindows()
            windows = [w for w in all_windows if "armoury" in w.title.lower() or "crate" in w.title.lower()]

        if not windows:
            print("  ❌ Armoury Crate window not found")
            print("  💡 Please make sure Armoury Crate is open and visible")
            return False

        window = windows[0]
        print(f"  ✅ Found window: {window.title}")

        # Activate window
        window.activate()
        await asyncio.sleep(1)

        # Get window bounds
        left = window.left
        top = window.top
        width = window.width
        height = window.height

        print(f"  📍 Window position: {left}, {top}, size: {width}x{height}")

        # Strategy: Try multiple navigation paths
        print()
        print("  🔍 Attempting navigation to Device menu...")

        # Method 1: Click on left sidebar (Device menu area)
        # Typical Armoury Crate layout: Device is usually around 10-15% from left, 20-30% from top
        sidebar_x = left + int(width * 0.12)
        sidebar_y = top + int(height * 0.25)

        print(f"  📍 Clicking Device menu area: ({sidebar_x}, {sidebar_y})")
        pyautogui.click(sidebar_x, sidebar_y)
        await asyncio.sleep(2)

        # Method 2: Try using keyboard navigation
        print("  ⌨️  Trying keyboard navigation (Alt+D for Device)...")
        pyautogui.hotkey('alt', 'd')
        await asyncio.sleep(1)

        # Method 3: Search for "Device" text using screenshot
        print("  🔍 Taking screenshot to locate 'Device' text...")
        screenshot = pyautogui.screenshot(region=(left, top, width, height))

        # Try to find "Device" or "System Configuration" text
        # This is approximate - we'll try clicking common locations

        # Common locations for System Configuration:
        # - After clicking Device, it's usually in the main content area
        # - Around 30-40% from left, 15-25% from top

        config_x = left + int(width * 0.35)
        config_y = top + int(height * 0.20)

        print(f"  📍 Clicking System Configuration area: ({config_x}, {config_y})")
        pyautogui.click(config_x, config_y)
        await asyncio.sleep(2)

        # Method 4: Try scrolling and searching for lock settings
        print("  🔍 Scrolling to find lock settings...")

        # Scroll down to find settings
        scroll_start_y = top + int(height * 0.5)
        scroll_end_y = top + int(height * 0.3)

        pyautogui.moveTo(left + int(width * 0.5), scroll_start_y)
        pyautogui.dragTo(left + int(width * 0.5), scroll_end_y, duration=1, button='left')
        await asyncio.sleep(1)

        # Try clicking on common lock setting locations
        # Lock settings are usually toggles or dropdowns
        lock_positions = [
            (left + int(width * 0.4), top + int(height * 0.35)),  # Function Key Behavior
            (left + int(width * 0.4), top + int(height * 0.40)),  # Windows Key Lock
            (left + int(width * 0.4), top + int(height * 0.45)),  # FN Lock
        ]

        print("  🔍 Trying to click lock setting locations...")
        for i, (x, y) in enumerate(lock_positions, 1):
            print(f"    Position {i}: ({x}, {y})")
            pyautogui.click(x, y)
            await asyncio.sleep(1)

            # Try to toggle if it's a toggle button
            # Sometimes we need to click twice or use space/enter
            pyautogui.press('space')
            await asyncio.sleep(0.5)
            pyautogui.press('enter')
            await asyncio.sleep(1)

        # Method 5: Try using OCR to find text (if available)
        try:
            import pytesseract
            print("  🔍 Using OCR to find 'Function Key' or 'Windows Key' text...")

            # Take screenshot of content area
            content_region = (left + int(width * 0.2), top + int(height * 0.2), 
                            int(width * 0.6), int(height * 0.6))
            content_screenshot = pyautogui.screenshot(region=content_region)

            # OCR to find text
            text = pytesseract.image_to_string(content_screenshot)

            # Look for lock-related keywords
            if 'function' in text.lower() or 'fn' in text.lower():
                print("  ✅ Found 'Function Key' text in UI")
            if 'windows' in text.lower() or 'win' in text.lower():
                print("  ✅ Found 'Windows Key' text in UI")

        except ImportError:
            print("  ⚠️  OCR not available (pytesseract not installed)")
        except Exception as e:
            print(f"  ⚠️  OCR failed: {e}")

        print()
        print("  ✅ UI automation attempts completed")
        print("  ⚠️  Please verify if lock symbols disappeared")
        print("  ⚠️  If not, the settings may be in a different location")

    except ImportError as e:
        print(f"  ❌ UI automation libraries not available: {e}")
        print("  💡 Install: pip install pyautogui pygetwindow")
        return False
    except Exception as e:
        print(f"  ❌ UI automation failed: {e}")
        import traceback
        print(f"  Traceback: {traceback.format_exc()}")
        return False

    print()
    print("=" * 70)
    print("💡 SUMMARY:")
    print("=" * 70)
    print("  UI automation attempted multiple navigation methods:")
    print("  1. Clicked Device menu area")
    print("  2. Used keyboard navigation (Alt+D)")
    print("  3. Clicked System Configuration area")
    print("  4. Scrolled and clicked lock setting locations")
    print("  5. Attempted OCR text detection")
    print()
    print("  ⚠️  Please check if lock symbols disappeared from FN and Windows keys")
    print("  ⚠️  If not, manually navigate in Armoury Crate:")
    print("      Device > System Configuration > Function Key Behavior / Windows Key Lock")
    print("=" * 70)

    return True

if __name__ == "__main__":


    asyncio.run(main())