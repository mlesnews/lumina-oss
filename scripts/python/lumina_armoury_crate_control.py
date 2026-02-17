#!/usr/bin/env python3
"""
Lumina Armoury Crate Control - Manual Control Interface
Provides easy access to Armoury Crate controls through Lumina
"""

import sys
import json
import asyncio
from pathlib import Path

# Add workspace root to path for imports
workspace_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace_root))

from src.cfservices.services.jarvis_core.integrations.armoury_crate import (
    ArmouryCrateIntegration,
    create_armoury_crate_integration
)


async def main():
    """Main control interface"""
    print("=" * 70)
    print("🎨 LUMINA ARMOURY CRATE CONTROL - Manual Control Interface")
    print("=" * 70)
    print()

    # Initialize integration
    integration = create_armoury_crate_integration()
    capabilities = integration.get_capabilities()

    print("Available Actions:")
    for i, action in enumerate(capabilities["available_actions"], 1):
        print(f"  {i}. {action}")
    print()

    # Show menu
    while True:
        print("\n" + "-" * 70)
        print("Select an action (or 'q' to quit):")
        print("\n📱 MANUAL CONTROL:")
        print("  1. Open Armoury Crate App")
        print("  2. Disable VUE Lighting (Complete)")
        print("  3. Get Lighting Status")
        print("  4. Stop Lighting Service")
        print("  5. Set Screen Brightness")
        print("  6. Get Full Status")
        print("  7. Show Manual Control Guide")
        print("\n🤖 AUTOMATION:")
        print("  8. Apply Profile")
        print("  9. List Profiles")
        print("  10. Create Profile")
        print("  11. List Automation Rules")
        print("  12. Create Automation Rule")
        print("  13. Check Automation Triggers")
        print("  14. Run Automation")
        print("\n  q. Quit")
        print("-" * 70)

        choice = input("Choice: ").strip().lower()

        if choice == 'q':
            print("\nExiting...")
            break

        try:
            if choice == '1':
                result = await integration.process_request({"action": "open_app"})
                print("\n" + json.dumps(result, indent=2))

            elif choice == '2':
                print("\nDisabling VUE lighting...")
                result = await integration.process_request({"action": "disable_vue_lighting"})
                print("\n" + json.dumps(result, indent=2))
                if result.get("success"):
                    print("\n✅ VUE lighting disabled!")
                    print("Please complete manual configuration in Armoury Crate if it opened.")

            elif choice == '3':
                result = await integration.process_request({"action": "get_lighting_status"})
                print("\n" + json.dumps(result, indent=2))

            elif choice == '4':
                result = await integration.process_request({"action": "stop_lighting_service"})
                print("\n" + json.dumps(result, indent=2))

            elif choice == '5':
                brightness = input("Enter brightness (0-100): ").strip()
                try:
                    brightness = int(brightness)
                    result = await integration.process_request({
                        "action": "set_screen_brightness",
                        "brightness": brightness
                    })
                    print("\n" + json.dumps(result, indent=2))
                except ValueError:
                    print("Invalid brightness value")

            elif choice == '6':
                result = await integration.process_request({"action": "get_status"})
                print("\n" + json.dumps(result, indent=2))

            elif choice == '7':
                result = await integration.process_request({"action": "manual_control_guide"})
                print("\n" + "=" * 70)
                print("MANUAL CONTROL GUIDE")
                print("=" * 70)
                for step in result.get("guide", []):
                    print(step)
                print("=" * 70)

            elif choice == '8':
                profiles_result = await integration.process_request({"action": "list_profiles"})
                profiles = profiles_result.get("profiles", [])
                print("\nAvailable Profiles:")
                for i, p in enumerate(profiles, 1):
                    print(f"  {i}. {p['name']} - {p['description']}")
                profile_name = input("\nEnter profile name to apply: ").strip()
                if profile_name:
                    result = await integration.process_request({
                        "action": "apply_profile",
                        "profile_name": profile_name
                    })
                    print("\n" + json.dumps(result, indent=2))

            elif choice == '9':
                result = await integration.process_request({"action": "list_profiles"})
                print("\n" + json.dumps(result, indent=2))

            elif choice == '10':
                name = input("Profile name: ").strip()
                desc = input("Description: ").strip()
                brightness = input("Screen brightness (0-100): ").strip()
                lighting = input("Enable lighting? (y/n): ").strip().lower() == 'y'
                if name:
                    result = await integration.process_request({
                        "action": "create_profile",
                        "name": name,
                        "description": desc,
                        "screen_brightness": int(brightness) if brightness.isdigit() else 0,
                        "lighting_enabled": lighting
                    })
                    print("\n" + json.dumps(result, indent=2))

            elif choice == '11':
                result = await integration.process_request({"action": "list_automation_rules"})
                print("\n" + json.dumps(result, indent=2))

            elif choice == '12':
                name = input("Rule name: ").strip()
                trigger_type = input("Trigger type (time/screen_brightness): ").strip()
                profile_name = input("Profile to apply: ").strip()
                if name and trigger_type and profile_name:
                    trigger_config = {}
                    if trigger_type == "time":
                        time_str = input("Time (HH:MM): ").strip()
                        trigger_config = {"time": time_str}
                    elif trigger_type == "screen_brightness":
                        brightness = input("Target brightness (0-100): ").strip()
                        trigger_config = {"brightness": int(brightness) if brightness.isdigit() else 0}

                    result = await integration.process_request({
                        "action": "create_automation_rule",
                        "name": name,
                        "trigger_type": trigger_type,
                        "trigger_config": trigger_config,
                        "profile_name": profile_name
                    })
                    print("\n" + json.dumps(result, indent=2))

            elif choice == '13':
                result = await integration.process_request({"action": "check_automation_triggers"})
                print("\n" + json.dumps(result, indent=2))

            elif choice == '14':
                result = await integration.process_request({"action": "run_automation"})
                print("\n" + json.dumps(result, indent=2))

            else:
                print("Invalid choice. Please try again.")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":


    asyncio.run(main())