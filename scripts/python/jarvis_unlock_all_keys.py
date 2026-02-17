#!/usr/bin/env python3
"""
JARVIS: Unlock ALL Locked Keys (FN + Windows Key)
🔓 Roast & Repair - Diagnose and fix all key locks
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cfservices.services.jarvis_core.integrations.armoury_crate import create_armoury_crate_integration

async def main():
    """Unlock all locked keys (FN + Windows Key)"""
    print("=" * 70)
    print("🔓 JARVIS: Roast & Repair - Unlocking ALL Locked Keys")
    print("=" * 70)
    print()
    print("🔍 DIAGNOSIS: Checking for locked keys...")
    print("  - FN Key Lock")
    print("  - Windows Key Lock")
    print()

    integration = create_armoury_crate_integration()

    # Step 1: Diagnose - Check lock states
    print("🔍 STEP 1: Diagnosing lock states...")
    print("-" * 70)
    lock_states = await integration.process_request({
        'action': 'spy_keyboard_locks'
    })

    if lock_states.get('success'):
        states = lock_states.get('lock_states', {})
        print("Lock States Detected:")
        for lock_name, lock_info in states.items():
            state = lock_info.get('state', 'UNKNOWN')
            icon = "🔒" if state == "ON" else "🔓" if state == "OFF" else "❓"
            print(f"  {icon} {lock_name}: {state}")
    print()

    # Step 2: ROAST - Identify issues
    print("🔥 STEP 2: ROAST - Identifying locked keys...")
    print("-" * 70)
    issues = []

    # Check FN lock (can't detect directly, but user reported it's locked)
    print("  🔒 FN Key: LOCKED (user reported lock symbol visible)")
    issues.append("FN Key Lock")

    # Check Windows key lock
    print("  🔒 Windows Key: LOCKED (user reported lock symbol visible)")
    issues.append("Windows Key Lock")

    print(f"\n🔥 Issues Found: {len(issues)}")
    for issue in issues:
        print(f"  - {issue}")
    print()

    # Step 3: REPAIR - Unlock all keys
    print("🔧 STEP 3: REPAIR - Unlocking all keys...")
    print("-" * 70)

    # Unlock FN key
    print("🔓 Unlocking FN Key (Fn+Esc long press)...")
    fn_result = await integration.process_request({
        'action': 'toggle_fn_lock'
    })
    if fn_result.get('success'):
        print("  ✅ FN Key unlock attempted")
    else:
        print(f"  ⚠️  FN Key unlock had issues: {fn_result.get('message', 'Unknown')}")
    print()

    # Unlock Windows key
    print("🔓 Unlocking Windows Key (Win+Esc or Win+Win long press)...")
    winkey_result = await integration.process_request({
        'action': 'toggle_winkey_lock'
    })
    if winkey_result.get('success'):
        print("  ✅ Windows Key unlock attempted")
    else:
        print(f"  ⚠️  Windows Key unlock had issues: {winkey_result.get('message', 'Unknown')}")
    print()

    # Step 4: Verify
    print("✅ STEP 4: Verification")
    print("-" * 70)
    print("💡 Manual Verification Required:")
    print("  1. Check if lock symbols are gone from FN and Windows keys")
    print("  2. Try pressing fn+F4 to verify FN key works")
    print("  3. Try pressing Win key to verify Windows key works")
    print()
    print("🔧 If keys are still locked, manually:")
    print("  - FN Key: Press and HOLD Fn+Esc for 2-3 seconds")
    print("  - Windows Key: Press and HOLD Win+Esc (or Win+Win) for 2-3 seconds")
    print()
    print("=" * 70)

    return True

if __name__ == "__main__":


    asyncio.run(main())