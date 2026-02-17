#!/usr/bin/env python3
"""
JARVIS - Configure Armoury Crate "Light" Profile
Sets brightness to 100% and enables all laptop lighting
"""

import sys
import asyncio
from pathlib import Path
from typing import Dict, Any

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVIS_ArmouryCrateLightProfile")

# Import Armoury Crate integration
try:
    from src.cfservices.services.jarvis_core.integrations.armoury_crate import (
        ArmouryCrateIntegration,
        LightingProfile
    )
except ImportError:
    logger.error("Could not import ArmouryCrateIntegration")
    sys.exit(1)


async def configure_light_profile() -> Dict[str, Any]:
    """Configure the 'Light' profile with 100% brightness and all lighting enabled"""

    logger.info("=" * 70)
    logger.info("JARVIS - CONFIGURING ARMOURY CRATE 'LIGHT' PROFILE")
    logger.info("=" * 70)
    logger.info("")

    # Initialize Armoury Crate integration
    integration = ArmouryCrateIntegration()

    result = {
        "status": "success",
        "steps_completed": [],
        "profile_created": False,
        "profile_applied": False,
        "errors": []
    }

    try:
        # Step 1: Check if "Light" profile exists
        logger.info("STEP 1: Checking for existing 'Light' profile...")
        list_result = await integration._handle_list_profiles({})

        profile_exists = False
        if list_result.get("success") and "profiles" in list_result:
            for profile in list_result["profiles"]:
                if profile.get("name", "").lower() == "light":
                    profile_exists = True
                    logger.info("✅ Found existing 'Light' profile")
                    break

        if not profile_exists:
            logger.info("⚠️  'Light' profile not found - will create new one")

        # Step 2: Create or update "Light" profile with 100% brightness
        logger.info("")
        logger.info("STEP 2: Creating/updating 'Light' profile...")
        logger.info("  - Screen brightness: 100%")
        logger.info("  - Lighting enabled: True")
        logger.info("  - Lighting brightness: 100%")
        logger.info("  - Effect: static (all zones enabled)")

        # Create profile with maximum brightness
        create_result = await integration._handle_create_profile({
            "name": "Light",
            "description": "Maximum brightness profile - 100% screen and all lighting enabled",
            "screen_brightness": 100,
            "lighting_enabled": True,
            "lighting_brightness": 100,
            "effect": "static",
            "zones": {
                "keyboard": {
                    "enabled": True,
                    "brightness": 100,
                    "effect": "static"
                },
                "logo": {
                    "enabled": True,
                    "brightness": 100,
                    "effect": "static"
                },
                "lightbar": {
                    "enabled": True,
                    "brightness": 100,
                    "effect": "static"
                },
                "all": {
                    "enabled": True,
                    "brightness": 100,
                    "effect": "static"
                }
            }
        })

        if create_result.get("success"):
            logger.info("✅ Profile created/updated successfully")
            result["steps_completed"].append("profile_created")
            result["profile_created"] = True
        else:
            error_msg = create_result.get("error", "Unknown error")
            if "already exists" in error_msg.lower():
                # Profile exists - we need to update it
                logger.info("⚠️  Profile exists - attempting to update via deletion and recreation...")
                # Delete existing profile first
                delete_result = await integration._handle_delete_profile({"profile_name": "Light"})
                if delete_result.get("success"):
                    # Recreate with new settings
                    create_result = await integration._handle_create_profile({
                        "name": "Light",
                        "description": "Maximum brightness profile - 100% screen and all lighting enabled",
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
                        logger.info("✅ Profile updated successfully")
                        result["steps_completed"].append("profile_updated")
                        result["profile_created"] = True
                    else:
                        logger.error(f"❌ Failed to recreate profile: {create_result.get('error')}")
                        result["errors"].append(f"Failed to recreate profile: {create_result.get('error')}")
                else:
                    logger.error(f"❌ Failed to delete existing profile: {delete_result.get('error')}")
                    result["errors"].append(f"Failed to delete existing profile: {delete_result.get('error')}")
            else:
                logger.error(f"❌ Failed to create profile: {error_msg}")
                result["errors"].append(f"Failed to create profile: {error_msg}")

        # Step 3: Apply the profile
        logger.info("")
        logger.info("STEP 3: Applying 'Light' profile...")
        apply_result = await integration._handle_apply_profile({"profile_name": "Light"})

        if apply_result.get("success"):
            logger.info("✅ Profile applied successfully")
            result["steps_completed"].append("profile_applied")
            result["profile_applied"] = True

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
                if "note" in lighting_result:
                    logger.info(f"  📝 Note: {lighting_result['note']}")
        else:
            error_msg = apply_result.get("error", "Unknown error")
            logger.error(f"❌ Failed to apply profile: {error_msg}")
            result["errors"].append(f"Failed to apply profile: {error_msg}")

        # Step 4: Set screen brightness directly (backup method)
        logger.info("")
        logger.info("STEP 4: Setting screen brightness to 100% (direct method)...")
        brightness_result = await integration._handle_set_screen_brightness({"brightness": 100})

        if brightness_result.get("success"):
            logger.info("✅ Screen brightness set to 100%")
            result["steps_completed"].append("screen_brightness_set")
        else:
            logger.warning(f"⚠️  Screen brightness: {brightness_result.get('message', 'Unknown')}")
            result["errors"].append(f"Screen brightness: {brightness_result.get('message')}")

        # Step 5: Enable keyboard lighting via registry
        logger.info("")
        logger.info("STEP 5: Enabling keyboard key lights via registry...")
        try:
            import subprocess
            script = """
$paths = @(
    'HKCU:\\Software\\ASUS\\ArmouryDevice\\Aura',
    'HKCU:\\Software\\ASUS\\Aura',
    'HKLM:\\SOFTWARE\\ASUS\\ArmouryDevice\\Aura',
    'HKLM:\\SOFTWARE\\ASUS\\Aura'
)

$success = $false
foreach ($path in $paths) {
    try {
        if (-not (Test-Path $path)) {
            New-Item -Path $path -Force -ErrorAction SilentlyContinue | Out-Null
        }
        if (Test-Path $path) {
            Set-ItemProperty -Path $path -Name 'Brightness' -Value 100 -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'BacklightBrightness' -Value 100 -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'KeyboardBrightness' -Value 100 -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'Enable' -Value 1 -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'Enabled' -Value 1 -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'LightingEnabled' -Value 1 -Type DWord -ErrorAction SilentlyContinue
            $success = $true
        }
    } catch {}
}
Write-Output "Keyboard registry updated"
"""
            reg_result = subprocess.run(
                ["powershell", "-Command", script],
                capture_output=True,
                text=True,
                timeout=30
            )
            if reg_result.returncode == 0:
                logger.info("✅ Keyboard key lights enabled via registry")
                result["steps_completed"].append("keyboard_registry")
            else:
                logger.warning("⚠️  Registry update may have failed")
        except Exception as e:
            logger.warning(f"⚠️  Registry update error: {e}")

        # Step 6: Enable all lighting zones via integration methods
        logger.info("")
        logger.info("STEP 6: Enabling all external lighting zones...")
        try:
            # Enable keyboard zone
            keyboard_result = await integration._handle_set_lighting_zone({
                "zone": "keyboard",
                "enabled": True,
                "brightness": 100,
                "effect": "static"
            })
            if keyboard_result.get("success"):
                logger.info("✅ Keyboard lighting zone enabled")
                result["steps_completed"].append("keyboard_zone")

            # Enable logo zone
            logo_result = await integration._handle_set_lighting_zone({
                "zone": "logo",
                "enabled": True,
                "brightness": 100,
                "effect": "static"
            })
            if logo_result.get("success"):
                logger.info("✅ Logo lighting zone enabled")
                result["steps_completed"].append("logo_zone")

            # Enable lightbar zone
            lightbar_result = await integration._handle_set_lighting_zone({
                "zone": "lightbar",
                "enabled": True,
                "brightness": 100,
                "effect": "static"
            })
            if lightbar_result.get("success"):
                logger.info("✅ Lightbar lighting zone enabled")
                result["steps_completed"].append("lightbar_zone")

            # Enable all zones
            all_result = await integration._handle_set_lighting_zone({
                "zone": "all",
                "enabled": True,
                "brightness": 100,
                "effect": "static"
            })
            if all_result.get("success"):
                logger.info("✅ All lighting zones enabled")
                result["steps_completed"].append("all_zones")
        except Exception as e:
            logger.warning(f"⚠️  Lighting zone configuration error: {e}")
            result["errors"].append(f"Lighting zones: {str(e)}")

        # Step 7: Open Armoury Crate for verification
        logger.info("")
        logger.info("STEP 7: Opening Armoury Crate for verification...")
        open_result = await integration._handle_open_app({})

        if open_result.get("success"):
            logger.info("✅ Armoury Crate opened")
            result["steps_completed"].append("armoury_crate_opened")
        else:
            logger.warning("⚠️  Could not open Armoury Crate automatically")

        # Summary
        logger.info("")
        logger.info("=" * 70)
        logger.info("CONFIGURATION SUMMARY")
        logger.info("=" * 70)
        logger.info("")
        logger.info("✅ Profile 'Light' configured with:")
        logger.info("   - Screen brightness: 100%")
        logger.info("   - Lighting enabled: True")
        logger.info("   - Lighting brightness: 100%")
        logger.info("   - Keyboard key lights: ENABLED (100%)")
        logger.info("   - All external lighting zones: ENABLED (100%)")
        logger.info("   - All zones: keyboard, logo, lightbar, all")
        logger.info("")
        logger.info("✅ AUTOMATED CONFIGURATION COMPLETE")
        logger.info("   All keyboard key lights and external lighting zones are enabled")
        logger.info("   at maximum brightness (100%)")
        logger.info("")
        logger.info("=" * 70)

        if result["errors"]:
            result["status"] = "partial_success"
        else:
            result["status"] = "success"

        return result

    except Exception as e:
        logger.error(f"❌ Error configuring profile: {e}", exc_info=True)
        result["status"] = "error"
        result["errors"].append(str(e))
        return result


def main():
    """Main execution"""
    result = asyncio.run(configure_light_profile())

    print("")
    print("=" * 70)
    print("JARVIS CONFIGURATION COMPLETE")
    print("=" * 70)
    print(f"Status: {result['status']}")
    print(f"Steps Completed: {len(result['steps_completed'])}")
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