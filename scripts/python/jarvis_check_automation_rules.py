#!/usr/bin/env python3
"""
JARVIS: Check Automation Rules
Check for automation rules that might be causing repeated screen brightness changes

@JARVIS #FIX #SCREEN #BRIGHTNESS
"""

import sys
import asyncio
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cfservices.services.jarvis_core.integrations.armoury_crate import create_armoury_crate_integration

async def main():
    """Check for automation rules that might cause screen dimming"""
    print("=" * 70)
    print("🔍 JARVIS: Checking Automation Rules")
    print("=" * 70)
    print()

    integration = create_armoury_crate_integration()

    # Check automation rules
    print("📋 Checking automation rules...")
    print("-" * 70)

    rules_result = await integration.process_request({
        'action': 'list_automation_rules'
    })

    if rules_result.get('success'):
        rules = rules_result.get('rules', [])

        if not rules:
            print("✅ No automation rules found - screen dimming should not be triggered")
        else:
            print(f"⚠️  Found {len(rules)} automation rule(s):")
            print()

            problematic_rules = []

            for rule in rules:
                rule_name = rule.get('name', 'Unknown')
                enabled = rule.get('enabled', False)
                trigger_type = rule.get('trigger_type', 'unknown')
                profile = rule.get('profile_name', 'Unknown')

                print(f"  Rule: {rule_name}")
                print(f"    Enabled: {'✅ Yes' if enabled else '❌ No'}")
                print(f"    Trigger: {trigger_type}")
                print(f"    Profile: {profile}")

                # Check if this rule might cause screen dimming
                if trigger_type == "screen_brightness" and enabled:
                    print(f"    ⚠️  WARNING: This rule triggers on screen brightness changes!")
                    problematic_rules.append(rule_name)

                # Check if profile has screen brightness set to 0
                if profile:
                    profile_result = await integration.process_request({
                        'action': 'get_lighting_profile',
                        'profile_name': profile
                    })

                    if profile_result.get('success'):
                        profile_data = profile_result.get('profile', {})
                        screen_brightness = profile_data.get('screen_brightness', None)

                        if screen_brightness == 0:
                            print(f"    ⚠️  WARNING: Profile sets screen brightness to 0!")
                            problematic_rules.append(rule_name)

                print()

            if problematic_rules:
                print("=" * 70)
                print("⚠️  PROBLEMATIC RULES DETECTED:")
                print("=" * 70)
                print()
                print("The following rules might be causing screen dimming:")
                for rule_name in problematic_rules:
                    print(f"  - {rule_name}")
                print()
                print("💡 To disable a rule, use:")
                print("   python scripts/python/jarvis_disable_automation_rule.py <rule_name>")
                print()
            else:
                print("✅ No problematic automation rules found")
        print()
    else:
        print("⚠️  Could not check automation rules")
        print()

    print("=" * 70)
    print("✅ Automation Rules Check Complete")
    print("=" * 70)
    print()
    print("💡 Note: Screen brightness control has been disabled in")
    print("   disable_all_lighting to prevent dimming cycles.")
    print()

if __name__ == "__main__":


    asyncio.run(main())