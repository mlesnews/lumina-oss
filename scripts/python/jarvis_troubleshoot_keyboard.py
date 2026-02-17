#!/usr/bin/env python3
"""
JARVIS TROUBLESHOOT: Keyboard Control Diagnostics
🔍 Spy on keyboard lock states and Armoury Crate
🔧 Diagnose issues and make decisions
"""

import sys
import asyncio
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cfservices.services.jarvis_core.integrations.armoury_crate import create_armoury_crate_integration

async def main():
    """Troubleshoot keyboard control issues"""
    print("=" * 70)
    print("🔍 JARVIS TROUBLESHOOT: Keyboard Control Diagnostics")
    print("=" * 70)
    print()

    integration = create_armoury_crate_integration()

    # Step 1: Spy on lock states
    print("🔍 STEP 1: Spying on keyboard lock states...")
    print("-" * 70)
    lock_result = await integration.process_request({
        'action': 'spy_keyboard_locks'
    })

    if lock_result.get('success'):
        lock_states = lock_result.get('lock_states', {})
        print("Lock States Detected:")
        for lock_name, lock_info in lock_states.items():
            state = lock_info.get('state', 'UNKNOWN')
            detectable = lock_info.get('detectable', False)
            icon = "✅" if state == "OFF" else "⚠️" if state == "ON" else "❓"
            print(f"  {icon} {lock_name}: {state} {'(detectable)' if detectable else '(not detectable)'}")
    else:
        print(f"❌ Failed: {lock_result.get('message', 'Unknown error')}")
    print()

    # Step 2: Spy on Armoury Crate state
    print("🔍 STEP 2: Spying on Armoury Crate state...")
    print("-" * 70)
    ac_result = await integration.process_request({
        'action': 'spy_armoury_crate'
    })

    if ac_result.get('success'):
        ac_state = ac_result.get('state', {})

        # Services
        print("Services:")
        services = ac_state.get('services', {})
        for service_name, service_info in services.items():
            status = service_info.get('status', 'Unknown')
            icon = "✅" if status == "Found" else "❌"
            print(f"  {icon} {service_name}: {status}")

        # Processes
        print("\nProcesses:")
        processes = ac_state.get('processes', {})
        for proc_name, proc_info in processes.items():
            status = proc_info.get('status', 'Unknown')
            icon = "✅" if status == "Running" else "❌"
            print(f"  {icon} {proc_name}: {status}")

        # Diagnostics
        diagnostics = ac_state.get('diagnostics', [])
        if diagnostics:
            print("\nDiagnostics:")
            for diag in diagnostics:
                print(f"  ⚠️  {diag}")
    else:
        print(f"❌ Failed: {ac_result.get('message', 'Unknown error')}")
    print()

    # Step 3: Full troubleshooting (spy + diagnose + fix)
    print("🔧 STEP 3: Full troubleshooting (spy + diagnose + auto-fix)...")
    print("-" * 70)
    troubleshoot_result = await integration.process_request({
        'action': 'troubleshoot_keyboard'
    })

    if troubleshoot_result.get('success'):
        diagnostics = troubleshoot_result.get('diagnostics', {})

        # Issues
        issues = diagnostics.get('issues', [])
        if issues:
            print(f"\n⚠️  Issues Found ({len(issues)}):")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("\n✅ No issues found!")

        # Recommendations
        recommendations = diagnostics.get('recommendations', [])
        if recommendations:
            print(f"\n💡 Recommendations ({len(recommendations)}):")
            for rec in recommendations:
                print(f"  - {rec}")

        # Actions taken
        actions = diagnostics.get('actions_taken', [])
        if actions:
            print(f"\n🔧 Actions Taken ({len(actions)}):")
            for action in actions:
                action_name = action.get('action', 'Unknown')
                action_result = action.get('result', {})
                if isinstance(action_result, dict):
                    result_msg = action_result.get('message', 'Completed')
                else:
                    result_msg = str(action_result)
                print(f"  ✅ {action_name}: {result_msg}")

        print(f"\n📊 Summary: {troubleshoot_result.get('message', 'Complete')}")
    else:
        print(f"❌ Troubleshooting failed: {troubleshoot_result.get('message', 'Unknown error')}")

    print()
    print("=" * 70)
    print("💡 Next Steps:")
    print("  1. Review the diagnostics above")
    print("  2. If FN lock is still an issue, manually press and HOLD Fn+Esc for 2-3 seconds")
    print("  3. Run: python scripts/python/jarvis_disable_all_lighting.py")
    print("=" * 70)

if __name__ == "__main__":


    asyncio.run(main())