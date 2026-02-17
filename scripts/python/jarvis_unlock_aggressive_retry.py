#!/usr/bin/env python3
"""
JARVIS: Aggressive Keyboard Unlock with Retries
🔓 Multiple methods, multiple attempts, maximum aggression
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cfservices.services.jarvis_core.integrations.armoury_crate import create_armoury_crate_integration

async def aggressive_unlock_with_retries(max_attempts=5):
    """Aggressively unlock all keys with multiple retries"""
    print("=" * 70)
    print("🔓 JARVIS: AGGRESSIVE KEYBOARD UNLOCK (MAXIMUM RETRIES)")
    print("=" * 70)
    print()

    integration = create_armoury_crate_integration()

    # Step 1: Diagnose current state
    print("🔍 STEP 1: Diagnosing lock states...")
    print("-" * 70)
    lock_states = await integration.process_request({
        'action': 'spy_keyboard_locks'
    })

    if lock_states.get('success'):
        states = lock_states.get('lock_states', {})
        print("Current Lock States:")
        for lock_name, lock_info in states.items():
            state = lock_info.get('state', 'UNKNOWN')
            icon = "🔒" if state == "ON" else "🔓" if state == "OFF" else "❓"
            print(f"  {icon} {lock_name}: {state}")
    print()

    # Step 2: Aggressive unlock with retries
    print(f"🔥 STEP 2: AGGRESSIVE UNLOCK (Attempting {max_attempts} times per key)...")
    print("-" * 70)

    # Unlock FN key with retries
    print("🔓 Unlocking FN Key (multiple attempts)...")
    fn_success = False
    for attempt in range(1, max_attempts + 1):
        print(f"  Attempt {attempt}/{max_attempts}: Toggling FN lock...")
        fn_result = await integration.process_request({
            'action': 'toggle_fn_lock'
        })
        if fn_result.get('success'):
            print(f"    ✅ Attempt {attempt} succeeded")
            fn_success = True
        else:
            print(f"    ⚠️  Attempt {attempt} had issues: {fn_result.get('message', 'Unknown')}")
        await asyncio.sleep(1)  # Brief pause between attempts
    print()

    # Unlock Windows key with retries
    print("🔓 Unlocking Windows Key (multiple attempts)...")
    winkey_success = False
    for attempt in range(1, max_attempts + 1):
        print(f"  Attempt {attempt}/{max_attempts}: Toggling Windows key lock...")
        winkey_result = await integration.process_request({
            'action': 'toggle_winkey_lock'
        })
        if winkey_result.get('success'):
            print(f"    ✅ Attempt {attempt} succeeded")
            winkey_success = True
        else:
            print(f"    ⚠️  Attempt {attempt} had issues: {winkey_result.get('message', 'Unknown')}")
        await asyncio.sleep(1)  # Brief pause between attempts
    print()

    # Step 3: Final verification
    print("✅ STEP 3: Final Verification")
    print("-" * 70)
    print("💡 Manual Verification Required:")
    print("  1. Check if lock symbols are gone from FN and Windows keys")
    print("  2. Try pressing fn+F4 to verify FN key works")
    print("  3. Try pressing Win key to verify Windows key works")
    print()

    if not fn_success or not winkey_success:
        print("⚠️  Some unlock attempts had issues. If keys are still locked:")
        print("  - FN Key: Press and HOLD Fn+Esc for 2-3 seconds")
        print("  - Windows Key: Press and HOLD Win+Esc (or Win+Win) for 2-3 seconds")
        print()

    print("=" * 70)
    print(f"🔓 Aggressive unlock complete: FN={fn_success}, Win={winkey_success}")
    print("=" * 70)

    return fn_success and winkey_success

if __name__ == "__main__":
    success = asyncio.run(aggressive_unlock_with_retries(max_attempts=5))
    sys.exit(0 if success else 1)
