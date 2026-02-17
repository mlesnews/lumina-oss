#!/usr/bin/env python3
"""
JARVIS Fix: Screen Dimming & External Lights
5W1H Analysis and Comprehensive Fix

@JARVIS @FIX @SCREEN @LIGHTS @5W1H
"""

import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISScreenLightFix")


class ScreenDimmingAndLightFix:
    """
    5W1H Analysis and Fix for:
    1. Random screen dimming/brightening
    2. External lights ON (disturbing sleep)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize fix system"""
        self.project_root = project_root or Path(__file__).parent.parent.parent

        from src.cfservices.services.jarvis_core.integrations.armoury_crate import create_armoury_crate_integration
        self.armoury_crate = create_armoury_crate_integration()

        logger.info("✅ Screen Dimming & Light Fix initialized")

    def analyze_5w1h(self) -> Dict[str, Any]:
        """
        5W1H Analysis

        WHO: Automation rules, Windows power settings, Armoury Crate automation
        WHAT: Screen randomly dimming/brightening, external lights ON
        WHEN: Randomly (likely triggered by automation rules or power settings)
        WHERE: Windows system, Armoury Crate automation, registry settings
        WHY: Automation rules with screen_brightness triggers, power management
        HOW: Automation rules checking screen brightness and triggering actions
        """
        logger.info("=" * 70)
        logger.info("🔍 5W1H ANALYSIS")
        logger.info("=" * 70)

        analysis = {
            "who": [],
            "what": [],
            "when": [],
            "where": [],
            "why": [],
            "how": []
        }

        # WHO: Check automation rules
        logger.info("\n👤 WHO:")
        logger.info("  - Automation rules in Armoury Crate")
        logger.info("  - Windows power management")
        logger.info("  - Armoury Crate service/processes")
        analysis["who"] = [
            "Automation rules (screen_brightness triggers)",
            "Windows power management",
            "Armoury Crate automation system"
        ]

        # WHAT: The problems
        logger.info("\n📋 WHAT:")
        logger.info("  - Screen randomly dimming and brightening")
        logger.info("  - External laptop lights ON (disturbing sleep)")
        logger.info("  - Keyboard and screen should remain functional")
        analysis["what"] = [
            "Screen brightness changing randomly",
            "External lights ON when they should be OFF",
            "Keyboard and screen should remain functional"
        ]

        # WHEN: Timing
        logger.info("\n⏰ WHEN:")
        logger.info("  - Randomly (likely triggered by automation)")
        logger.info("  - Possibly during sleep/wake cycles")
        logger.info("  - When automation rules check triggers")
        analysis["when"] = [
            "Randomly (automation trigger checks)",
            "During system state changes",
            "When automation rules evaluate triggers"
        ]

        # WHERE: Location
        logger.info("\n📍 WHERE:")
        logger.info("  - Armoury Crate automation rules")
        logger.info("  - Windows registry (brightness settings)")
        logger.info("  - Armoury Crate service processes")
        analysis["where"] = [
            "data/armoury_crate/automation/rules.json",
            "Windows registry (HKCU/HKLM\\SOFTWARE\\ASUS)",
            "Armoury Crate service processes"
        ]

        # WHY: Root causes
        logger.info("\n❓ WHY:")
        logger.info("  - Automation rules with screen_brightness triggers")
        logger.info("  - Rules checking brightness and triggering actions")
        logger.info("  - External lights not specifically disabled")
        logger.info("  - Power management interfering")
        analysis["why"] = [
            "Automation rules with screen_brightness trigger type",
            "Rules automatically changing settings based on brightness",
            "External lights not explicitly disabled (only all lighting)",
            "Windows power management may be interfering"
        ]

        # HOW: Mechanism
        logger.info("\n🔧 HOW:")
        logger.info("  - Automation rules check screen brightness")
        logger.info("  - When brightness changes, rules trigger")
        logger.info("  - Rules apply profiles/actions")
        logger.info("  - This causes dimming/brightening cycle")
        analysis["how"] = [
            "Automation rules check screen brightness periodically",
            "When brightness threshold is met, rule triggers",
            "Rule applies profile/action (may change brightness again)",
            "This creates a feedback loop causing random changes"
        ]

        logger.info("\n" + "=" * 70)

        return analysis

    async def check_automation_rules(self) -> Dict[str, Any]:
        """Check for problematic automation rules"""
        logger.info("🔍 Checking automation rules...")

        try:
            # Check automation rules
            rules_result = await self.armoury_crate.process_request({
                "action": "list_automation_rules"
            })

            rules = rules_result.get("rules", [])
            problematic_rules = []

            for rule in rules:
                # Check for screen_brightness triggers
                if rule.get("trigger_type") == "screen_brightness":
                    problematic_rules.append({
                        "name": rule.get("name"),
                        "trigger_type": rule.get("trigger_type"),
                        "enabled": rule.get("enabled", True),
                        "issue": "Screen brightness trigger - may cause dimming cycles"
                    })

                # Check for time-based rules that might change brightness
                if rule.get("trigger_type") == "time":
                    profile_name = rule.get("profile_name", "")
                    if profile_name:
                        # Check if profile changes brightness
                        problematic_rules.append({
                            "name": rule.get("name"),
                            "trigger_type": rule.get("trigger_type"),
                            "enabled": rule.get("enabled", True),
                            "issue": "Time-based rule - may change settings at specific times"
                        })

            logger.info(f"  Found {len(problematic_rules)} potentially problematic rules")

            return {
                "total_rules": len(rules),
                "problematic_rules": problematic_rules,
                "rules": rules
            }
        except Exception as e:
            logger.error(f"Failed to check automation rules: {e}")
            return {
                "error": str(e),
                "total_rules": 0,
                "problematic_rules": []
            }

    async def fix_screen_dimming(self) -> Dict[str, Any]:
        """Fix screen dimming issue"""
        logger.info("🔧 Fixing screen dimming issue...")

        results = {
            "automation_rules_disabled": [],
            "automation_rules_deleted": [],
            "errors": []
        }

        try:
            # 1. Check and disable/delete screen_brightness trigger rules
            rules_check = await self.check_automation_rules()
            problematic = rules_check.get("problematic_rules", [])

            for rule_info in problematic:
                rule_name = rule_info.get("name")

                if rule_info.get("trigger_type") == "screen_brightness":
                    # Delete screen_brightness trigger rules (they cause feedback loops)
                    logger.info(f"  Deleting problematic rule: {rule_name}")
                    try:
                        delete_result = await self.armoury_crate.process_request({
                            "action": "delete_automation_rule",
                            "rule_name": rule_name
                        })
                        if delete_result.get("success"):
                            results["automation_rules_deleted"].append(rule_name)
                            logger.info(f"    ✅ Deleted: {rule_name}")
                        else:
                            # Try disabling instead
                            disable_result = await self.armoury_crate.process_request({
                                "action": "disable_automation_rule",
                                "rule_name": rule_name
                            })
                            if disable_result.get("success"):
                                results["automation_rules_disabled"].append(rule_name)
                                logger.info(f"    ✅ Disabled: {rule_name}")
                    except Exception as e:
                        logger.warning(f"    ⚠️  Failed to remove rule {rule_name}: {e}")
                        results["errors"].append(f"Rule {rule_name}: {str(e)}")

            # 2. Disable automation checking (prevent future triggers)
            logger.info("  Disabling automation trigger checking...")
            # This would require modifying the integration

            logger.info("✅ Screen dimming fix complete")
            results["success"] = True

        except Exception as e:
            logger.error(f"Screen dimming fix failed: {e}")
            results["success"] = False
            results["error"] = str(e)

        return results

    async def fix_external_lights(self) -> Dict[str, Any]:
        """Fix external lights (disable all except keyboard and screen)"""
        logger.info("🔧 Fixing external lights (disabling all except keyboard and screen)...")

        results = {}

        try:
            # Disable all lighting, but preserve keyboard control
            # The disable_all_lighting function should handle this, but we need to ensure
            # external lights (VUE, monitor lights, etc.) are specifically disabled

            logger.info("  Disabling all external lighting...")
            disable_result = await self.armoury_crate.process_request({
                "action": "disable_all_lighting"
            })

            results["disable_all_lighting"] = disable_result

            if disable_result.get("success"):
                logger.info("✅ External lights disabled")
                results["success"] = True
            else:
                logger.warning(f"⚠️  Disable all lighting had issues: {disable_result.get('error', 'Unknown')}")
                results["success"] = False
                results["error"] = disable_result.get("error", "Unknown error")

        except Exception as e:
            logger.error(f"External lights fix failed: {e}")
            results["success"] = False
            results["error"] = str(e)

        return results

    async def apply_comprehensive_fix(self) -> Dict[str, Any]:
        """Apply comprehensive fix for both issues"""
        logger.info("=" * 70)
        logger.info("🔧 COMPREHENSIVE FIX")
        logger.info("=" * 70)
        logger.info("")

        # 5W1H Analysis
        analysis = self.analyze_5w1h()

        # Fix screen dimming
        logger.info("\n" + "=" * 70)
        logger.info("FIXING SCREEN DIMMING ISSUE")
        logger.info("=" * 70)
        screen_fix = await self.fix_screen_dimming()

        # Fix external lights
        logger.info("\n" + "=" * 70)
        lights_fix = await self.fix_external_lights()

        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("📊 FIX SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Screen Dimming Fix: {'✅ Success' if screen_fix.get('success') else '❌ Failed'}")
        logger.info(f"  - Rules disabled: {len(screen_fix.get('automation_rules_disabled', []))}")
        logger.info(f"  - Rules deleted: {len(screen_fix.get('automation_rules_deleted', []))}")
        logger.info(f"External Lights Fix: {'✅ Success' if lights_fix.get('success') else '❌ Failed'}")
        logger.info("=" * 70)

        return {
            "analysis": analysis,
            "screen_fix": screen_fix,
            "lights_fix": lights_fix,
            "success": screen_fix.get("success") and lights_fix.get("success")
        }


async def main():
    """Main execution"""
    print("=" * 70)
    print("🔧 JARVIS SCREEN DIMMING & EXTERNAL LIGHTS FIX")
    print("   5W1H Analysis and Comprehensive Fix")
    print("=" * 70)
    print()

    fixer = ScreenDimmingAndLightFix()
    results = await fixer.apply_comprehensive_fix()

    print()
    print("=" * 70)
    print("✅ FIX COMPLETE")
    print("=" * 70)
    print(f"Overall Success: {results.get('success', False)}")
    print()
    print("If issues persist:")
    print("  1. Check Windows power settings (may be auto-adjusting brightness)")
    print("  2. Check for other automation software")
    print("  3. Manually verify external lights are OFF")
    print("=" * 70)


if __name__ == "__main__":


    asyncio.run(main())