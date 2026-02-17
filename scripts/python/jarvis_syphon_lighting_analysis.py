#!/usr/bin/env python3
"""
JARVIS SYPHON Lighting Issue Analysis
Use SYPHON to extract intelligence about lighting issues and provide solutions

@JARVIS @SYPHON #LIGHTING #TROUBLESHOOTING
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# SYPHON intelligence extraction
try:
    from scripts.python.syphon_system import SYPHONSystem, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    print("⚠️  SYPHON not available")

# Armoury Crate integration
from src.cfservices.services.jarvis_core.integrations.armoury_crate import create_armoury_crate_integration
import asyncio

async def main():
    """Use SYPHON to analyze lighting issues"""
    print("=" * 70)
    print("🔍 JARVIS SYPHON: Lighting Issue Analysis")
    print("=" * 70)
    print()

    # Extract intelligence about lighting issue
    issue_description = """
    LIGHTING IS STILL AN ISSUE

    Problem: External lighting is not being disabled properly
    Requirements:
    - Disable ALL external lighting
    - Preserve fn+F4 keyboard shortcut functionality
    - No screen brightness dimming (already fixed)
    - Full automation required

    Current state:
    - Screen brightness dimming was fixed
    - But lighting control may still have problems
    - Need to ensure lighting is actually OFF
    - Need to verify fn+F4 still works
    """

    print("📝 Issue Description:")
    print("-" * 70)
    print(issue_description)
    print()

    # Use SYPHON to extract actionable intelligence
    if SYPHON_AVAILABLE:
        print("🔍 SYPHON: Extracting actionable intelligence...")
        print("-" * 70)

        syphon = SYPHONSystem(project_root)

        # Extract actionable items
        actionable_items = syphon._extract_actionable_items(issue_description)
        tasks = syphon._extract_tasks(issue_description, "Lighting Issue")
        decisions = syphon._extract_decisions(issue_description)

        print(f"✅ Extracted {len(actionable_items)} actionable items:")
        for i, item in enumerate(actionable_items[:10], 1):
            print(f"   {i}. {item}")
        print()

        if tasks:
            print(f"✅ Extracted {len(tasks)} tasks:")
            for i, task in enumerate(tasks[:5], 1):
                task_text = task.get("text", task) if isinstance(task, dict) else str(task)
                print(f"   {i}. {task_text}")
            print()

    # Check current lighting status
    print("🔍 Checking current lighting status...")
    print("-" * 70)

    integration = create_armoury_crate_integration()

    # Get lighting status
    status_result = await integration.process_request({
        'action': 'get_lighting_status'
    })

    print(f"Status: {status_result.get('message', 'Unknown')}")
    print()

    # Spy on keyboard locks
    print("🔍 Checking keyboard lock states...")
    print("-" * 70)

    lock_result = await integration.process_request({
        'action': 'spy_keyboard_locks'
    })

    if lock_result.get('success'):
        lock_states = lock_result.get('lock_states', {})
        print("Keyboard Lock States:")
        for lock, state in lock_states.items():
            status_icon = "🔒" if state else "🔓"
            print(f"   {status_icon} {lock}: {state}")
    else:
        print(f"⚠️  Could not check lock states: {lock_result.get('error', 'Unknown')}")
    print()

    # Recommendations
    print("💡 SYPHON Recommendations:")
    print("-" * 70)
    print("1. Verify lighting is actually OFF (not just brightness=0)")
    print("2. Check if fn+F4 keyboard shortcut is functional")
    print("3. Ensure all lighting zones are disabled (not just brightness)")
    print("4. Verify Armoury Crate processes are running (required for fn+F4)")
    print("5. Check registry values for lighting enable/disable flags")
    print("6. Test keyboard simulation method (fn+F4 cycling)")
    print("7. Verify UI automation is working if keyboard method fails")
    print()

    # Action plan
    print("🎯 Action Plan:")
    print("-" * 70)
    print("1. Run full disable_all_lighting automation")
    print("2. Verify lighting is OFF visually")
    print("3. Test fn+F4 keyboard shortcut")
    print("4. If still not working, check specific lighting zones")
    print("5. Use SYPHON to extract more intelligence from error messages")
    print()

    print("=" * 70)
    print("✅ SYPHON Lighting Analysis Complete!")
    print("=" * 70)

if __name__ == "__main__":


    asyncio.run(main())