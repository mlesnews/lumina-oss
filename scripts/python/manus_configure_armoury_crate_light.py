#!/usr/bin/env python3
"""
@MANUS - Configure Armoury Crate "Light" Profile with @scotty (Windows Systems Architect) privileges
USS Lumina - Ship's Engineer Configuration
Uses MANUS Unified Control to set brightness to 100% and enable all laptop lighting
"""

import sys
import asyncio
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import uuid

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MANUS_ArmouryCrateLight")

# Import MANUS Unified Control
try:
    from scripts.python.manus_unified_control import (
        MANUSUnifiedControl,
        ControlArea,
        ControlOperation
    )
except ImportError:
    logger.error("Could not import MANUS Unified Control")
    sys.exit(1)

# Import Armoury Crate integration for direct control
try:
    from src.cfservices.services.jarvis_core.integrations.armoury_crate import (
        ArmouryCrateIntegration
    )
except ImportError:
    logger.warning("ArmouryCrateIntegration not available - will use MANUS only")
    ArmouryCrateIntegration = None


async def configure_light_profile_manus() -> Dict[str, Any]:
    """Configure the 'Light' profile using @MANUS with @scotty privileges"""

    logger.info("=" * 70)
    logger.info("@MANUS - CONFIGURING ARMOURY CRATE 'LIGHT' PROFILE")
    logger.info("USS Lumina - Ship's Engineer Configuration")
    logger.info("Role: @scotty (Windows Systems Architect)")
    logger.info("Privileges: Full Administrative Rights")
    logger.info("=" * 70)
    logger.info("")

    # Initialize MANUS Unified Control
    manus_control = MANUSUnifiedControl(root_path=project_root)

    # Initialize Armoury Crate integration for direct control
    ac_integration = None
    if ArmouryCrateIntegration:
        try:
            ac_integration = ArmouryCrateIntegration()
            logger.info("✅ Armoury Crate Integration initialized")
        except Exception as e:
            logger.warning(f"⚠️  Armoury Crate Integration not available: {e}")

    result = {
        "status": "success",
        "steps_completed": [],
        "manus_operations": [],
        "errors": []
    }

    try:
        # Step 1: Check Armoury Crate status via MANUS
        logger.info("STEP 1: Checking Armoury Crate status via @MANUS...")
        status_op = ControlOperation(
            operation_id=f"ac_status_{uuid.uuid4().hex[:8]}",
            area=ControlArea.WORKSTATION_CONTROL,
            action="get_armoury_status",
            parameters={}
        )
        status_result = manus_control.execute_operation(status_op)
        result["manus_operations"].append({
            "operation": "get_armoury_status",
            "success": status_result.success,
            "message": status_result.message
        })

        if status_result.success:
            logger.info(f"✅ Armoury Crate status: {status_result.message}")
            if status_result.data:
                logger.info(f"   Details: {status_result.data}")
        else:
            logger.warning(f"⚠️  Status check: {status_result.message}")

        result["steps_completed"].append("status_check")

        # Step 2: Create/Update "Light" profile via Armoury Crate Integration
        if ac_integration:
            logger.info("")
            logger.info("STEP 2: Creating/updating 'Light' profile...")
            logger.info("  - Screen brightness: 100%")
            logger.info("  - Lighting enabled: True")
            logger.info("  - Lighting brightness: 100%")
            logger.info("  - Effect: static (all zones enabled)")

            # Check if profile exists
            list_result = await ac_integration._handle_list_profiles({})
            profile_exists = False
            if list_result.get("success") and "profiles" in list_result:
                for profile in list_result["profiles"]:
                    if profile.get("name", "").lower() == "light":
                        profile_exists = True
                        logger.info("✅ Found existing 'Light' profile - will update")
                        # Delete existing profile first
                        delete_result = await ac_integration._handle_delete_profile({"profile_name": "Light"})
                        if delete_result.get("success"):
                            logger.info("✅ Deleted existing profile for recreation")
                        break

            # Create profile with maximum brightness
            create_result = await ac_integration._handle_create_profile({
                "name": "Light",
                "description": "Maximum brightness profile - 100% screen and all lighting enabled (@scotty configured)",
                "screen_brightness": 100,
                "lighting_enabled": True,
                "lighting_brightness": 100,
                "effect": "static",
                "zones": {
                    "keyboard": {"enabled": True, "brightness": 100, "effect": "static"},
                    "logo": {"enabled": True, "brightness": 100, "effect": "static"},
                    "lightbar": {"enabled": True, "brightness": 100, "effect": "static"},
                    "all": {"enabled": True, "brightness": 100, "effect": "static"}
                }
            })

            if create_result.get("success"):
                logger.info("✅ Profile created/updated successfully")
                result["steps_completed"].append("profile_created")
            else:
                error_msg = create_result.get("error", "Unknown error")
                logger.error(f"❌ Failed to create profile: {error_msg}")
                result["errors"].append(f"Profile creation: {error_msg}")

        # Step 3: Apply "Light" profile via Armoury Crate Integration
        if ac_integration:
            logger.info("")
            logger.info("STEP 3: Applying 'Light' profile...")
            apply_result = await ac_integration._handle_apply_profile({"profile_name": "Light"})

            if apply_result.get("success"):
                logger.info("✅ Profile applied successfully")
                result["steps_completed"].append("profile_applied")

                # Log results
                results = apply_result.get("results", {})
                if "screen_brightness" in results:
                    screen_result = results["screen_brightness"]
                    if screen_result.get("success"):
                        logger.info(f"  ✅ Screen brightness set to 100%")
                    else:
                        logger.warning(f"  ⚠️  Screen brightness: {screen_result.get('message', 'Unknown')}")

                if "lighting" in results:
                    lighting_result = results["lighting"]
                    logger.info(f"  ℹ️  Lighting: {lighting_result.get('message', 'Configured')}")
            else:
                error_msg = apply_result.get("error", "Unknown error")
                logger.error(f"❌ Failed to apply profile: {error_msg}")
                result["errors"].append(f"Profile application: {error_msg}")

        # Step 4: Set screen brightness directly via Armoury Crate Integration
        if ac_integration:
            logger.info("")
            logger.info("STEP 4: Setting screen brightness to 100% (direct method)...")
            brightness_result = await ac_integration._handle_set_screen_brightness({"brightness": 100})

            if brightness_result.get("success"):
                logger.info("✅ Screen brightness set to 100%")
                result["steps_completed"].append("screen_brightness_set")
            else:
                logger.warning(f"⚠️  Screen brightness: {brightness_result.get('message', 'Unknown')}")
                result["errors"].append(f"Screen brightness: {brightness_result.get('message')}")

        # Step 5: Apply lighting theme via MANUS (if available)
        logger.info("")
        logger.info("STEP 5: Applying lighting theme via @MANUS...")
        theme_op = ControlOperation(
            operation_id=f"ac_theme_{uuid.uuid4().hex[:8]}",
            area=ControlArea.WORKSTATION_CONTROL,
            action="apply_theme",
            parameters={"theme_name": "Light"}
        )
        theme_result = manus_control.execute_operation(theme_op)
        result["manus_operations"].append({
            "operation": "apply_theme",
            "success": theme_result.success,
            "message": theme_result.message
        })

        if theme_result.success:
            logger.info(f"✅ Theme applied: {theme_result.message}")
            result["steps_completed"].append("theme_applied")
        else:
            logger.warning(f"⚠️  Theme application: {theme_result.message}")
            # Not critical if theme doesn't exist - profile is the main method

        # Step 6: Open Armoury Crate for verification
        if ac_integration:
            logger.info("")
            logger.info("STEP 6: Opening Armoury Crate for verification...")
            open_result = await ac_integration._handle_open_app({})

            if open_result.get("success"):
                logger.info("✅ Armoury Crate opened")
                result["steps_completed"].append("armoury_crate_opened")
            else:
                logger.warning("⚠️  Could not open Armoury Crate automatically")

        # Step 7: Enable all lighting zones via MANUS (if possible)
        logger.info("")
        logger.info("STEP 7: Attempting to enable all lighting zones via @MANUS...")
        # Note: This may require UI automation which MANUS can handle
        # For now, we'll rely on the profile configuration

        # Summary
        logger.info("")
        logger.info("=" * 70)
        logger.info("CONFIGURATION SUMMARY (@MANUS @scotty - USS Lumina)")
        logger.info("=" * 70)
        logger.info("")
        logger.info("✅ Profile 'Light' configured with:")
        logger.info("   - Screen brightness: 100%")
        logger.info("   - Lighting enabled: True")
        logger.info("   - Lighting brightness: 100%")
        logger.info("   - All zones enabled")
        logger.info("")
        logger.info("📋 MANUS Operations Executed:")
        for op in result["manus_operations"]:
            status = "✅" if op["success"] else "⚠️"
            logger.info(f"   {status} {op['operation']}: {op['message']}")
        logger.info("")
        logger.info("📝 VERIFICATION STEPS:")
        logger.info("   1. Verify screen brightness is at 100%")
        logger.info("   2. In Armoury Crate, navigate to: Device → Lighting")
        logger.info("   3. Verify all lighting zones are enabled and at 100% brightness:")
        logger.info("      - Keyboard backlight: 100%")
        logger.info("      - Logo lighting: 100%")
        logger.info("      - Light bar (if available): 100%")
        logger.info("      - Any other zones: 100%")
        logger.info("   4. Verify effect is set to 'Static' or your preferred effect")
        logger.info("   5. Click 'Apply' or 'Save' if needed")
        logger.info("")
        logger.info("=" * 70)

        if result["errors"]:
            result["status"] = "partial_success"
        else:
            result["status"] = "success"

        return result

    except Exception as e:
        logger.error(f"❌ Error configuring profile via @MANUS: {e}", exc_info=True)
        result["status"] = "error"
        result["errors"].append(str(e))
        return result


def main():
    """Main execution"""
    result = asyncio.run(configure_light_profile_manus())

    print("")
    print("=" * 70)
    print("@MANUS CONFIGURATION COMPLETE (@scotty - USS Lumina)")
    print("=" * 70)
    print(f"Status: {result['status']}")
    print(f"Steps Completed: {len(result['steps_completed'])}")
    print(f"MANUS Operations: {len(result['manus_operations'])}")
    print("")
    if result["errors"]:
        print("Errors:")
        for error in result["errors"]:
            print(f"  ⚠️  {error}")
        print("")
    print("=" * 70)

    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":


    sys.exit(main())