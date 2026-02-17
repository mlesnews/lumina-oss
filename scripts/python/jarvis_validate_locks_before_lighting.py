#!/usr/bin/env python3
"""
JARVIS Validate: Locks Before Lighting

Validates that locks are fixed FIRST before lighting operations.
Prevents energy and effort from going to /dev/null.

@JARVIS @VALIDATE @LOCKS_BEFORE_LIGHTING @PREVENT_WASTE
"""

import sys
from pathlib import Path
from typing import Dict, Any

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ValidateLocksBeforeLighting")


class LocksBeforeLightingValidator:
    """
    Validates that locks are fixed FIRST before lighting operations.

    Rule: LOCKS BEFORE LIGHTING
    Otherwise: Energy and effort → /dev/null
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = get_logger("LocksBeforeLightingValidator")

        self.logger.info("=" * 70)
        self.logger.info("✅ LOCKS BEFORE LIGHTING VALIDATOR")
        self.logger.info("   Rule: Fix locks FIRST, then lighting")
        self.logger.info("   Else: Energy and effort → /dev/null")
        self.logger.info("=" * 70)
        self.logger.info("")

    def validate_smart_lighting_order(self) -> Dict[str, Any]:
        """Validate that smart lighting fixes locks FIRST"""
        self.logger.info("   🔍 Validating smart lighting order...")

        try:
            from scripts.python.jarvis_smart_lighting_day_night_sync import SmartLightingDayNightSync

            # Check if fix_locks_first method exists
            sync = SmartLightingDayNightSync(self.project_root)

            if not hasattr(sync, 'fix_locks_first'):
                return {
                    "valid": False,
                    "error": "fix_locks_first() method not found",
                    "message": "❌ LOCKS NOT FIXED FIRST - Energy and effort → /dev/null"
                }

            # Check if setup_smart_lighting calls fix_locks_first first
            import inspect
            setup_source = inspect.getsource(sync.setup_smart_lighting)

            # Check order: fix_locks_first should be called BEFORE other operations
            fix_locks_idx = setup_source.find('fix_locks_first')
            re_enable_idx = setup_source.find('re_enable_services')
            disable_lighting_idx = setup_source.find('disable_display_keyboard_lighting')
            apply_settings_idx = setup_source.find('apply_day_night_settings')

            if fix_locks_idx == -1:
                return {
                    "valid": False,
                    "error": "fix_locks_first() not called in setup_smart_lighting()",
                    "message": "❌ LOCKS NOT FIXED FIRST - Energy and effort → /dev/null"
                }

            # Validate order
            order_valid = True
            issues = []

            if re_enable_idx != -1 and fix_locks_idx > re_enable_idx:
                order_valid = False
                issues.append("re_enable_services() called BEFORE fix_locks_first()")

            if disable_lighting_idx != -1 and fix_locks_idx > disable_lighting_idx:
                order_valid = False
                issues.append("disable_display_keyboard_lighting() called BEFORE fix_locks_first()")

            if apply_settings_idx != -1 and fix_locks_idx > apply_settings_idx:
                order_valid = False
                issues.append("apply_day_night_settings() called BEFORE fix_locks_first()")

            if not order_valid:
                return {
                    "valid": False,
                    "error": "Order violation: Lighting operations before locks fix",
                    "issues": issues,
                    "message": "❌ LOCKS NOT FIXED FIRST - Energy and effort → /dev/null"
                }

            # Order is correct
            return {
                "valid": True,
                "message": "✅ LOCKS FIXED FIRST - Energy and effort preserved",
                "order": "correct",
                "fix_locks_position": "FIRST (STEP 0)",
                "lighting_operations": "AFTER locks fix"
            }

        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "message": "❌ Validation failed - Energy and effort → /dev/null"
            }

    def validate_all_systems(self) -> Dict[str, Any]:
        """Validate all systems follow locks-before-lighting rule"""
        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("🔍 VALIDATING ALL SYSTEMS")
        self.logger.info("=" * 70)
        self.logger.info("")

        results = {}

        # Validate smart lighting
        results["smart_lighting"] = self.validate_smart_lighting_order()

        # Summary
        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("📊 VALIDATION SUMMARY")
        self.logger.info("=" * 70)

        all_valid = True
        for system, result in results.items():
            valid = result.get("valid", False)
            all_valid = all_valid and valid

            icon = "✅" if valid else "❌"
            self.logger.info(f"   {icon} {system}: {result.get('message', 'Unknown')}")

            if not valid and result.get("issues"):
                for issue in result["issues"]:
                    self.logger.info(f"      ⚠️  {issue}")

        self.logger.info("")
        if all_valid:
            self.logger.info("✅ ALL SYSTEMS VALID")
            self.logger.info("   LOCKS FIXED FIRST - Energy and effort preserved")
        else:
            self.logger.error("❌ VALIDATION FAILED")
            self.logger.error("   LOCKS NOT FIXED FIRST - Energy and effort → /dev/null")

        self.logger.info("=" * 70)
        self.logger.info("")

        return {
            "all_valid": all_valid,
            "results": results
        }


def main():
    try:
        """Main execution"""
        project_root = Path(__file__).parent.parent.parent
        validator = LocksBeforeLightingValidator(project_root)
        results = validator.validate_all_systems()

        print()
        print("=" * 70)
        print("✅ LOCKS BEFORE LIGHTING VALIDATION")
        print("=" * 70)
        print(f"   All Systems Valid: {'✅ YES' if results['all_valid'] else '❌ NO'}")
        print()

        if results['all_valid']:
            print("   ✅ LOCKS FIXED FIRST")
            print("   ✅ Energy and effort preserved")
        else:
            print("   ❌ LOCKS NOT FIXED FIRST")
            print("   ❌ Energy and effort → /dev/null")

        print()
        print("=" * 70)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()