#!/usr/bin/env python3
"""
Diagnose Auto-Accept "Keep All" Button Issues

Quick diagnostic tool to check why auto-accept isn't working.

Tags: #DIAGNOSTICS #AUTO_ACCEPT #TROUBLESHOOTING
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print("\n" + "="*80)
print("🔍 Auto-Accept 'Keep All' Button Diagnostic")
print("="*80 + "\n")

# Check 1: Import
print("1. Checking imports...")
try:
    from cursor_ide_auto_accept import CursorIDEAutoAccept
    print("   ✅ Auto-accept module imported")
except Exception as e:
    print(f"   ❌ Failed to import: {e}")
    sys.exit(1)

# Check 2: Initialize
print("\n2. Initializing auto-accept...")
try:
    auto_accept = CursorIDEAutoAccept()
    print("   ✅ Auto-accept initialized")
except Exception as e:
    print(f"   ❌ Failed to initialize: {e}")
    sys.exit(1)

# Check 3: Cursor IDE running
print("\n3. Checking if Cursor IDE is running...")
is_running = auto_accept._is_cursor_running()
if is_running:
    print("   ✅ Cursor IDE is running")
else:
    print("   ⚠️  Cursor IDE not detected")
    print("   💡 Make sure Cursor IDE is open")

# Check 4: Libraries
print("\n4. Checking required libraries...")
libs_ok = True

try:
    import keyboard
    print("   ✅ keyboard library available")
except ImportError:
    print("   ❌ keyboard library NOT available")
    print("   💡 Install: pip install keyboard")
    libs_ok = False

if auto_accept.ui_available:
    print("   ✅ pyautogui/pywinauto available")
else:
    print("   ⚠️  pyautogui/pywinauto NOT available")
    print("   💡 Install: pip install pyautogui pywinauto")
    print("   ⚠️  Will only use keyboard shortcuts")

# Check 5: Full-time monitoring
print("\n5. Checking full-time monitoring service...")
try:
    from full_time_monitoring_service import get_full_time_monitoring_service
    service = get_full_time_monitoring_service()
    stats = service.get_stats()

    auto_accept_stats = stats.get("systems", {}).get("auto_accept", {})
    if auto_accept_stats.get("active"):
        print("   ✅ Auto-accept is active in monitoring service")
        thread_alive = auto_accept_stats.get("thread_alive", False)
        if thread_alive:
            print("   ✅ Monitoring thread is alive")
        else:
            print("   ⚠️  Monitoring thread is NOT alive")
            print("   💡 Thread may have died - check logs")

        cursor_running = auto_accept_stats.get("cursor_running", False)
        if cursor_running:
            print("   ✅ Cursor IDE detected by monitoring service")
        else:
            print("   ⚠️  Cursor IDE not detected by monitoring service")

        accept_count = auto_accept_stats.get("acceptance_count", 0)
        print(f"   📊 Acceptance count: {accept_count}")

        last_acceptance = auto_accept_stats.get("last_acceptance")
        if last_acceptance:
            print(f"   📅 Last acceptance: {last_acceptance}")
        else:
            print("   ⚠️  No acceptances recorded yet")
    else:
        print("   ⚠️  Auto-accept NOT active in monitoring service")
        print("   💡 Full-time monitoring may not be running")
except Exception as e:
    print(f"   ⚠️  Could not check monitoring service: {e}")

# Check 6: Test detection
print("\n6. Testing detection (verbose mode)...")
print("   💡 If a 'Keep All' dialog is open, it should be detected now")
print()

try:
    result = auto_accept.detect_and_accept_changes(verbose=True)
    if result:
        print("\n   ✅ SUCCESS: Changes were accepted!")
    else:
        print("\n   ⚠️  No dialog detected or acceptance failed")
        print("   💡 Make sure:")
        print("      - A 'Keep All' / 'Accept All Changes' dialog is open")
        print("      - Cursor IDE window is focused")
        print("      - The dialog is visible on screen")
except Exception as e:
    print(f"\n   ❌ Error during detection: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "="*80)
print("📊 Diagnostic Summary")
print("="*80)
print(f"   Cursor IDE Running: {'✅' if is_running else '❌'}")
print(f"   Required Libraries: {'✅' if libs_ok else '❌'}")
print(f"   UI Automation: {'✅' if auto_accept.ui_available else '⚠️'}")
print("\n💡 To test manually:")
print("   1. Open Cursor IDE")
print("   2. Trigger a 'Keep All' / 'Accept All Changes' dialog")
print("   3. Run: python cursor_ide_auto_accept.py --test")
print("   4. Or check full-time monitoring logs")
print("="*80 + "\n")
