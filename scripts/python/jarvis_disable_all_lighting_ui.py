#!/usr/bin/env python3
"""
JARVIS UI AUTOMATION: Disable ALL Hardware Lighting
Fully automated UI control - no manual steps required
"""

import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cfservices.services.jarvis_core.integrations.armoury_crate import create_armoury_crate_integration

async def main():
    """Automated UI disable all lighting"""
    print("=" * 70)
    print("🤖 JARVIS UI AUTOMATION: Disabling ALL Hardware Lighting")
    print("=" * 70)
    print()
    print("This will:")
    print("  1. Open Armoury Crate")
    print("  2. Navigate to Lighting section")
    print("  3. Turn OFF all lighting zones")
    print("  4. Save settings")
    print("  5. Also disable services")
    print()
    print("Starting automation...")
    print()

    integration = create_armoury_crate_integration()

    # Execute UI automation
    result = await integration.process_request({
        'action': 'disable_all_lighting_ui'
    })

    # Display results
    print("UI AUTOMATION RESULTS:")
    print("-" * 70)
    print(f"✅ Success: {result.get('success', False)}")
    print(f"📢 Message: {result.get('message', 'Unknown')}")

    if result.get('ui_automation'):
        print(f"🖱️  UI Automation: Enabled")
        print(f"🎯 Zones Disabled: {result.get('zones_disabled', 0)}")
        print(f"💾 Settings Saved: {result.get('settings_saved', False)}")

    if result.get('error'):
        print(f"❌ Error: {result.get('error')}")
        print()
        print("FALLBACK OPTIONS:")
        print("  1. Use 'disable_all_lighting' for service-based automation")
        print("  2. Do one-time manual setup (see docs)")
        if result.get('manual_steps'):
            print()
            print("Manual Steps:")
            for step in result.get('manual_steps', []):
                print(f"  {step}")

    print()
    if result.get('success'):
        print("🎉 ALL HARDWARE LIGHTING DISABLED VIA UI AUTOMATION!")
    else:
        print("⚠️  UI automation had issues. Check error message above.")
        print("   Try manual setup or service-based automation as fallback.")

    print("=" * 70)

    return result.get('success', False)

if __name__ == "__main__":
    sys.exit(0 if success else 1)


    success = asyncio.run(main())