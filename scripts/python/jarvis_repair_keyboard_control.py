#!/usr/bin/env python3
"""
JARVIS REPAIR: Restore Keyboard Control (fn+F4)
Fixes keyboard shortcut functionality that was broken by previous automation attempts
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cfservices.services.jarvis_core.integrations.armoury_crate import create_armoury_crate_integration

async def main():
    """Repair keyboard control"""
    print("=" * 70)
    print("🔧 JARVIS REPAIR: Restoring Keyboard Control (fn+F4)")
    print("=" * 70)
    print()
    print("This will restore keyboard shortcut functionality that may have been")
    print("broken by previous automation attempts.")
    print()

    integration = create_armoury_crate_integration()

    # Execute repair
    result = await integration.process_request({
        'action': 'repair_keyboard_control'
    })

    # Display results
    print("REPAIR RESULTS:")
    print("-" * 70)
    print(f"✅ Success: {result.get('success', False)}")
    print(f"📢 Message: {result.get('message', 'Unknown')}")
    print()

    # Show repair summary
    summary = result.get('repair_summary', {})
    if summary:
        print("REPAIR SUMMARY:")
        print("-" * 70)
        print(f"🔄 Services Repaired: {'✅ Yes' if summary.get('services_repaired') else '❌ No'}")
        print(f"⚙️  Processes Running: {'✅ Yes' if summary.get('processes_running') else '❌ No'}")
        print(f"📝 Registry Restored: {'✅ Yes' if summary.get('registry_restored') else '❌ No'}")
        print()

    # Show verification
    verification = result.get('repair_summary', {}).get('verification', 'Unknown')
    if verification and verification != 'Unknown':
        print("VERIFICATION:")
        print("-" * 70)
        try:
            import json
            verif_data = json.loads(verification)
            for key, value in verif_data.items():
                if isinstance(value, dict):
                    status_icon = "✅" if value.get('Status') == "Running" else "❌"
                    print(f"  {status_icon} {key}: {value.get('Status', 'Unknown')} (StartType: {value.get('StartType', 'Unknown')})")
                else:
                    status_icon = "✅" if value == "Running" else "❌"
                    print(f"  {status_icon} {key}: {value}")
        except:
            print(f"  {verification}")
        print()

    # Show instructions
    instructions = result.get('instructions', '')
    if instructions:
        print("INSTRUCTIONS:")
        print("-" * 70)
        print(f"  {instructions}")
        print()

    if result.get('success'):
        print("🎉 REPAIR COMPLETE!")
        print()
        print("TEST: Press fn+F4 (AURA F4) to verify keyboard shortcut works.")
        print("      It should cycle through lighting modes: off→dim→medium→bright→off")
    else:
        print("⚠️  Repair completed with warnings. Check details above.")

    print("=" * 70)

    return result.get('success', False)

if __name__ == "__main__":
    sys.exit(0 if success else 1)


    success = asyncio.run(main())