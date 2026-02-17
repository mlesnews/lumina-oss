#!/usr/bin/env python3
"""
@MANUS - Enable Keyboard Lighting & Switch to Light Mode
USS Lumina - @scotty (Windows Systems Architect) Configuration
Turns on keyboard backlight, enables external lighting, and switches to light mode
"""

import sys
import asyncio
import subprocess
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

logger = get_logger("MANUS_EnableKeyboardLighting")

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

# Import Armoury Crate integration
try:
    from src.cfservices.services.jarvis_core.integrations.armoury_crate import (
        ArmouryCrateIntegration
    )
except ImportError:
    logger.warning("ArmouryCrateIntegration not available")
    ArmouryCrateIntegration = None


def _run_powershell(script: str) -> Dict[str, Any]:
    """Run PowerShell script and return result"""
    try:
        result = subprocess.run(
            ["powershell", "-Command", script],
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def enable_keyboard_lighting() -> Dict[str, Any]:
    """Enable keyboard backlight via registry"""
    logger.info("Enabling keyboard backlight via registry...")

    script = """
$paths = @(
    'HKCU:\\Software\\ASUS\\ArmouryDevice\\Aura',
    'HKCU:\\Software\\ASUS\\Aura',
    'HKLM:\\SOFTWARE\\ASUS\\ArmouryDevice\\Aura',
    'HKLM:\\SOFTWARE\\ASUS\\Aura'
)

$success = $false
$pathsUpdated = 0

foreach ($path in $paths) {
    try {
        if (Test-Path $path) {
            # Set brightness to 100 (maximum)
            Set-ItemProperty -Path $path -Name 'Brightness' -Value 100 -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'LightingBrightness' -Value 100 -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'BacklightBrightness' -Value 100 -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'KeyboardBrightness' -Value 100 -Type DWord -ErrorAction SilentlyContinue

            # Ensure Enable flags are set to 1 (enabled)
            Set-ItemProperty -Path $path -Name 'Enable' -Value 1 -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'Enabled' -Value 1 -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'LightingEnabled' -Value 1 -Type DWord -ErrorAction SilentlyContinue

            $pathsUpdated++
            $success = $true
        }
    } catch {
        # Continue to next path
    }
}

if ($success) {
    Write-Output "Set:$pathsUpdated"
} else {
    Write-Output "Failed"
}
"""

    result = _run_powershell(script)
    if result["success"] and "Set:" in result["stdout"]:
        logger.info(f"✅ Keyboard backlight enabled: {result['stdout']}")
        return {"success": True, "message": result["stdout"]}
    else:
        logger.warning(f"⚠️  Registry method: {result.get('stdout', result.get('error', 'Unknown'))}")
        return {"success": False, "message": result.get("stdout", "Failed")}


async def enable_keyboard_via_fn_f4() -> Dict[str, Any]:
    """Try to enable keyboard via fn+F4 simulation"""
    logger.info("Attempting to enable keyboard via fn+F4 simulation...")

    try:
        import pyautogui
        import time

        # Press fn+F4 to cycle keyboard lighting
        # Note: This cycles through: Off -> Low -> Medium -> High -> Off
        # We'll press it multiple times to get to High
        pyautogui.hotkey('fn', 'f4')
        await asyncio.sleep(0.5)
        pyautogui.hotkey('fn', 'f4')
        await asyncio.sleep(0.5)
        pyautogui.hotkey('fn', 'f4')
        await asyncio.sleep(0.5)
        pyautogui.hotkey('fn', 'f4')

        logger.info("✅ fn+F4 simulation completed")
        return {"success": True, "message": "fn+F4 cycles executed"}
    except ImportError:
        logger.warning("⚠️  PyAutoGUI not available for fn+F4 simulation")
        return {"success": False, "message": "PyAutoGUI not available"}
    except Exception as e:
        logger.warning(f"⚠️  fn+F4 simulation failed: {e}")
        return {"success": False, "message": str(e)}


async def set_lighting_zones(ac_integration: ArmouryCrateIntegration) -> Dict[str, Any]:
    """Set all lighting zones to maximum brightness"""
    logger.info("Setting all lighting zones to maximum brightness...")

    zones = ["keyboard", "logo", "lightbar", "all"]
    results = {}

    for zone in zones:
        try:
            result = await ac_integration._handle_set_lighting_zone({
                "zone": zone,
                "effect": "static",
                "brightness": 100
            })
            results[zone] = result
            logger.info(f"  {zone}: {result.get('message', 'Configured')}")
        except Exception as e:
            logger.warning(f"  {zone}: Error - {e}")
            results[zone] = {"success": False, "error": str(e)}

    return {"success": True, "zones": results}


async def switch_to_light_mode() -> Dict[str, Any]:
    """Switch Windows theme to light mode"""
    logger.info("Switching Windows theme to light mode...")

    script = """
# Set Windows theme to light mode
Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize' -Name 'AppsUseLightTheme' -Value 1 -Type DWord
Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize' -Name 'SystemUsesLightTheme' -Value 1 -Type DWord

# Refresh the theme
$code = @'
[DllImport("user32.dll", CharSet = CharSet.Auto)]
public static extern int SendMessageTimeout(
    IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam,
    uint fuFlags, uint uTimeout, out IntPtr lpdwResult);
'@
$type = Add-Type -MemberDefinition $code -Name Win32SendMessageTimeout -Namespace Win32Functions -PassThru
$HWND_BROADCAST = [IntPtr]0xffff
$WM_WININICHANGE = 0x001A
$result = [IntPtr]::Zero
$type::SendMessageTimeout($HWND_BROADCAST, $WM_WININICHANGE, [IntPtr]::Zero, [IntPtr]::Zero, 0x0002, 5000, [ref]$result)

Write-Output "Light mode enabled"
"""

    result = _run_powershell(script)
    if result["success"]:
        logger.info("✅ Windows theme switched to light mode")
        return {"success": True, "message": "Light mode enabled"}
    else:
        logger.warning(f"⚠️  Theme switch: {result.get('error', 'Unknown')}")
        return {"success": False, "message": result.get("error", "Failed")}


async def enable_keyboard_lighting_and_light_mode() -> Dict[str, Any]:
    """Main function to enable keyboard lighting and switch to light mode"""

    logger.info("=" * 70)
    logger.info("@MANUS - ENABLE KEYBOARD LIGHTING & LIGHT MODE")
    logger.info("USS Lumina - @scotty (Windows Systems Architect)")
    logger.info("=" * 70)
    logger.info("")

    result = {
        "status": "success",
        "steps_completed": [],
        "errors": []
    }

    try:
        # Initialize Armoury Crate integration
        ac_integration = None
        if ArmouryCrateIntegration:
            try:
                ac_integration = ArmouryCrateIntegration()
                logger.info("✅ Armoury Crate Integration initialized")
            except Exception as e:
                logger.warning(f"⚠️  Armoury Crate Integration: {e}")

        # Step 1: Enable keyboard backlight via registry
        logger.info("STEP 1: Enabling keyboard backlight via registry...")
        reg_result = await enable_keyboard_lighting()
        if reg_result["success"]:
            logger.info("✅ Keyboard backlight enabled via registry")
            result["steps_completed"].append("keyboard_registry")
        else:
            logger.warning(f"⚠️  Registry method: {reg_result['message']}")
            result["errors"].append(f"Registry: {reg_result['message']}")

        # Step 2: Try fn+F4 simulation as backup
        logger.info("")
        logger.info("STEP 2: Attempting fn+F4 simulation...")
        fn_result = await enable_keyboard_via_fn_f4()
        if fn_result["success"]:
            logger.info("✅ fn+F4 simulation completed")
            result["steps_completed"].append("keyboard_fn_f4")
        else:
            logger.warning(f"⚠️  fn+F4: {fn_result['message']}")

        # Step 3: Set all lighting zones via Armoury Crate
        if ac_integration:
            logger.info("")
            logger.info("STEP 3: Setting all lighting zones to maximum brightness...")
            zones_result = await set_lighting_zones(ac_integration)
            if zones_result["success"]:
                logger.info("✅ Lighting zones configured")
                result["steps_completed"].append("lighting_zones")
            else:
                logger.warning("⚠️  Some zones may not have been configured")

        # Step 4: Apply "Light" profile
        if ac_integration:
            logger.info("")
            logger.info("STEP 4: Applying 'Light' profile...")
            try:
                apply_result = await ac_integration._handle_apply_profile({"profile_name": "Light"})
                if apply_result.get("success"):
                    logger.info("✅ 'Light' profile applied")
                    result["steps_completed"].append("profile_applied")
                else:
                    logger.warning(f"⚠️  Profile: {apply_result.get('error', 'Unknown')}")
            except Exception as e:
                logger.warning(f"⚠️  Profile application: {e}")

        # Step 5: Switch Windows to light mode
        logger.info("")
        logger.info("STEP 5: Switching Windows theme to light mode...")
        theme_result = await switch_to_light_mode()
        if theme_result["success"]:
            logger.info("✅ Windows theme switched to light mode")
            result["steps_completed"].append("light_mode")
        else:
            logger.warning(f"⚠️  Theme switch: {theme_result['message']}")
            result["errors"].append(f"Theme: {theme_result['message']}")

        # Step 6: Open Armoury Crate for manual verification
        if ac_integration:
            logger.info("")
            logger.info("STEP 6: Opening Armoury Crate for verification...")
            try:
                open_result = await ac_integration._handle_open_app({})
                if open_result.get("success"):
                    logger.info("✅ Armoury Crate opened")
                    result["steps_completed"].append("armoury_opened")
            except Exception as e:
                logger.warning(f"⚠️  Could not open Armoury Crate: {e}")

        # Summary
        logger.info("")
        logger.info("=" * 70)
        logger.info("CONFIGURATION SUMMARY (@MANUS @scotty - USS Lumina)")
        logger.info("=" * 70)
        logger.info("")
        logger.info("✅ Steps Completed:")
        for step in result["steps_completed"]:
            logger.info(f"   • {step}")
        logger.info("")
        if result["errors"]:
            logger.info("⚠️  Errors:")
            for error in result["errors"]:
                logger.info(f"   • {error}")
        logger.info("")
        logger.info("📝 VERIFICATION:")
        logger.info("   1. Check keyboard backlight is ON")
        logger.info("   2. Check Windows theme is in light mode")
        logger.info("   3. In Armoury Crate, verify all lighting zones are enabled")
        logger.info("   4. Check for external lighting (if available)")
        logger.info("")
        logger.info("=" * 70)

        if result["errors"]:
            result["status"] = "partial_success"
        else:
            result["status"] = "success"

        return result

    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        result["status"] = "error"
        result["errors"].append(str(e))
        return result


def main():
    """Main execution"""
    result = asyncio.run(enable_keyboard_lighting_and_light_mode())

    print("")
    print("=" * 70)
    print("@MANUS CONFIGURATION COMPLETE (@scotty - USS Lumina)")
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