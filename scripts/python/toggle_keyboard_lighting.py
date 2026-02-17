#!/usr/bin/env python3
"""
Keyboard Lighting Toggle
Automatically toggles keyboard lighting between ON and OFF states
"""

import sys
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_unified_logger import get_unified_logger
    logger = get_unified_logger("Application", "KeyboardLighting")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("KeyboardLightingToggle")

# State file to track current lighting state
STATE_FILE = project_root / "data" / "keyboard_lighting_state.json"


def load_state() -> Dict[str, Any]:
    """Load current lighting state from file"""
    default_state = {
        "is_on": False,
        "last_toggle": None,
        "brightness": 100
    }

    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
                return {**default_state, **state}
        except Exception as e:
            logger.warning(f"Could not load state: {e}")

    return default_state


def save_state(state: Dict[str, Any]):
    """Save current lighting state to file"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        logger.error(f"Could not save state: {e}")


def set_registry_brightness(brightness: int, enabled: bool):
    """Set keyboard brightness via registry"""
    logger.info(f"Setting registry: brightness={brightness}, enabled={enabled}")

    script = f"""
$paths = @(
    'HKCU:\\Software\\ASUS\\ArmouryDevice\\Aura',
    'HKCU:\\Software\\ASUS\\Aura',
    'HKLM:\\SOFTWARE\\ASUS\\ArmouryDevice\\Aura',
    'HKLM:\\SOFTWARE\\ASUS\\Aura',
    'HKCU:\\Software\\ASUS\\ROG',
    'HKLM:\\SOFTWARE\\ASUS\\ROG'
)

$brightness = {brightness}
$enabled = {1 if enabled else 0}

$values = @{{
    'Brightness' = $brightness
    'BacklightBrightness' = $brightness
    'KeyboardBrightness' = $brightness
    'LightingBrightness' = $brightness
    'KeyBrightness' = $brightness
    'Enable' = $enabled
    'Enabled' = $enabled
    'LightingEnabled' = $enabled
    'BacklightEnabled' = $enabled
    'KeyboardEnabled' = $enabled
    'State' = $enabled
    'On' = $enabled
}}

$updated = 0
foreach ($path in $paths) {{
    try {{
        if (-not (Test-Path $path)) {{
            New-Item -Path $path -Force -ErrorAction SilentlyContinue | Out-Null
        }}
        if (Test-Path $path) {{
            foreach ($key in $values.Keys) {{
                Set-ItemProperty -Path $path -Name $key -Value $values[$key] -Type DWord -ErrorAction SilentlyContinue
            }}
            $updated++
        }}
    }} catch {{}}
}}

Write-Output "Updated $updated paths"
"""

    result = subprocess.run(
        ["powershell", "-Command", script],
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode == 0:
        logger.info(f"✅ Registry updated: {result.stdout.strip()}")
        return True
    else:
        logger.warning(f"⚠️  Registry update: {result.stderr}")
        return False


# REMOVED: press_fn_f4_times function - FN key testing no longer needed
# Keyboard lighting is now controlled via registry and @MANUS only


def toggle_keyboard_lighting(target_state: Optional[bool] = None) -> Dict[str, Any]:
    """
    Toggle keyboard lighting on/off

    Args:
        target_state: If None, toggles from current state. If True/False, sets to that state.

    Returns:
        Dict with success status and new state
    """
    logger.info("=" * 70)
    logger.info("KEYBOARD LIGHTING TOGGLE")
    logger.info("=" * 70)
    logger.info("")

    # Load current state
    state = load_state()
    current_state = state.get("is_on", False)

    # Determine target state
    if target_state is None:
        # Toggle from current state
        new_state = not current_state
        logger.info(f"Current state: {'ON' if current_state else 'OFF'}")
        logger.info(f"Toggling to: {'ON' if new_state else 'OFF'}")
    else:
        # Set to specific state
        new_state = target_state
        if new_state == current_state:
            logger.info(f"Keyboard lighting already {'ON' if new_state else 'OFF'}")
            return {
                "success": True,
                "state": new_state,
                "message": f"Already {'ON' if new_state else 'OFF'}"
            }
        logger.info(f"Setting to: {'ON' if new_state else 'OFF'}")

    # Apply the toggle
    brightness = 100 if new_state else 0

    # Method 1: Use @MANUS for full control (with fallback to registry)
    logger.info("")
    logger.info("METHOD 1: Using @MANUS for lighting control...")
    manus_success = False
    try:
        import asyncio
        from manus_lighting_time_based import set_lighting_via_manus

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        manus_result = loop.run_until_complete(set_lighting_via_manus(brightness, False))
        manus_success = manus_result.get("success", False)
        if manus_success:
            method = manus_result.get("method", "unknown")
            logger.info(f"  ✅ @MANUS control successful (method: {method})")
        else:
            logger.warning(f"  ⚠️  @MANUS had issues, using registry fallback")
    except ImportError:
        logger.info("  ℹ️  @MANUS not available, using registry fallback")
    except Exception as e:
        logger.warning(f"  ⚠️  @MANUS error: {e}, using registry fallback")

    # Method 2: Registry fallback (if @MANUS unavailable or failed)
    if not manus_success:
        logger.info("")
        logger.info("METHOD 2: Updating registry (fallback)...")
        reg_success = set_registry_brightness(brightness, new_state)
        time.sleep(0.5)
    else:
        reg_success = True  # @MANUS already handled registry

    # Method 3: Try Armoury Crate integration if available (additional method)
    ac_success = False
    try:
        from src.cfservices.services.jarvis_core.integrations.armoury_crate import (
            ArmouryCrateIntegration
        )

        logger.info("")
        logger.info("METHOD 3: Armoury Crate integration...")
        integration = ArmouryCrateIntegration()

        if new_state:
            # Enable keyboard zone
            result = asyncio.run(integration._handle_set_lighting_zone({
                "zone": "keyboard",
                "enabled": True,
                "brightness": 100,
                "effect": "static"
            }))
            ac_success = result.get("success", False)
        else:
            # Disable keyboard zone
            result = asyncio.run(integration._handle_set_lighting_zone({
                "zone": "keyboard",
                "enabled": False,
                "brightness": 0,
                "effect": "static"
            }))
            ac_success = result.get("success", False)

        if ac_success:
            logger.info("✅ Armoury Crate integration successful")
        else:
            logger.warning("⚠️  Armoury Crate integration may require manual configuration")
    except Exception as e:
        logger.debug(f"Armoury Crate integration not available: {e}")

    # Update state
    state["is_on"] = new_state
    state["brightness"] = brightness
    state["last_toggle"] = time.strftime("%Y-%m-%d %H:%M:%S")
    save_state(state)

    # Summary
    logger.info("")
    logger.info("=" * 70)
    logger.info("TOGGLE SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Previous state: {'ON' if current_state else 'OFF'}")
    logger.info(f"New state: {'ON' if new_state else 'OFF'}")
    logger.info(f"Brightness: {brightness}%")
    logger.info("")
    logger.info("Methods attempted:")
    logger.info(f"  Registry: {'✅' if reg_success else '❌'}")
    logger.info(f"  Armoury Crate: {'✅' if ac_success else '❌'}")
    logger.info("")
    logger.info("=" * 70)

    return {
        "success": reg_success or ac_success,
        "state": new_state,
        "brightness": brightness,
        "methods": {
            "registry": reg_success,
            "armoury_crate": ac_success
        }
    }


def get_current_state() -> Dict[str, Any]:
    """Get current keyboard lighting state"""
    state = load_state()
    return {
        "is_on": state.get("is_on", False),
        "brightness": state.get("brightness", 0),
        "last_toggle": state.get("last_toggle", "Never")
    }


def get_time_based_brightness() -> int:
    """
    Get keyboard brightness based on daylight hours (EST timezone)
    - Daylight hours (6 AM - 8 PM EST): ON (100% brightness)
    - Night-time (8 PM - 6 AM EST): ON (5-10% brightness, using 7%)

    Note: All external lighting is OFF (always).
    """
    from datetime import timezone, timedelta

    # Get current time in EST (UTC-5)
    est = timezone(timedelta(hours=-5))
    now_est = datetime.now(est)
    current_hour_est = now_est.hour

    # Daylight hours (6 AM - 8 PM EST): ON (100% brightness)
    if 6 <= current_hour_est < 20:
        return 100  # ON - Full brightness during daylight hours

    # Night-time (8 PM - 6 AM EST): ON (5-10% brightness, using 7%)
    else:
        return 7  # ON - Very dim (5-10% range, using 7%) during night-time


def auto_adjust_brightness_by_time() -> Dict[str, Any]:
    """
    Automatically adjust keyboard brightness based on time of day
    - Brightest during daytime
    - Dimmest past 12 AM
    """
    logger.info("=" * 70)
    logger.info("AUTO-ADJUST KEYBOARD BRIGHTNESS BY TIME")
    logger.info("=" * 70)
    logger.info("")

    # Get time-based brightness
    target_brightness = get_time_based_brightness()
    current_hour = datetime.now().hour
    time_period = "night (past midnight)" if 0 <= current_hour < 6 else "daytime"

    logger.info(f"Current time: {datetime.now().strftime('%H:%M:%S')} ({time_period})")
    logger.info(f"Target brightness: {target_brightness}%")
    logger.info("")

    # Load current state
    state = load_state()
    current_brightness = state.get("brightness", 0)
    is_on = state.get("is_on", False)

    # If brightness already matches, no need to change
    if current_brightness == target_brightness and is_on:
        logger.info(f"✅ Brightness already at {target_brightness}% - no change needed")
        return {
            "success": True,
            "brightness": target_brightness,
            "previous_brightness": current_brightness,
            "changed": False,
            "time_period": time_period,
            "message": f"Already at {target_brightness}%"
        }

    # Determine if we need to turn on/off
    # If target is dim (20%), we still want it on but dim
    # If target is bright (100%), we want it on and bright
    new_state = True  # Always keep it on, just adjust brightness

    # Apply the brightness change
    logger.info("METHOD 1: Updating registry...")
    reg_success = set_registry_brightness(target_brightness, new_state)
    time.sleep(0.5)

    # Method 2: Armoury Crate integration
    ac_success = False
    try:
        from src.cfservices.services.jarvis_core.integrations.armoury_crate import (
            ArmouryCrateIntegration
        )
        import asyncio

        logger.info("")
        logger.info("METHOD 2: Armoury Crate integration...")
        integration = ArmouryCrateIntegration()

        result = asyncio.run(integration._handle_set_lighting_zone({
            "zone": "keyboard",
            "enabled": True,
            "brightness": target_brightness,
            "effect": "static"
        }))
        ac_success = result.get("success", False)

        if ac_success:
            logger.info("✅ Armoury Crate integration successful")
        else:
            logger.warning("⚠️  Armoury Crate integration may require manual configuration")
    except Exception as e:
        logger.debug(f"Armoury Crate integration not available: {e}")

    # Update state
    state["is_on"] = new_state
    state["brightness"] = target_brightness
    state["last_toggle"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    state["auto_adjusted"] = True
    save_state(state)

    # Summary
    logger.info("")
    logger.info("=" * 70)
    logger.info("AUTO-ADJUST SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Previous brightness: {current_brightness}%")
    logger.info(f"New brightness: {target_brightness}%")
    logger.info(f"Time period: {time_period}")
    logger.info("")
    logger.info("Methods attempted:")
    logger.info(f"  Registry: {'✅' if reg_success else '❌'}")
    logger.info(f"  Armoury Crate: {'✅' if ac_success else '❌'}")
    logger.info("")
    logger.info("=" * 70)

    return {
        "success": reg_success or ac_success,
        "brightness": target_brightness,
        "previous_brightness": current_brightness,
        "changed": current_brightness != target_brightness,
        "time_period": time_period,
        "methods": {
            "registry": reg_success,
            "armoury_crate": ac_success
        }
    }


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Toggle keyboard lighting")
    parser.add_argument(
        "--on",
        action="store_true",
        help="Turn keyboard lighting ON"
    )
    parser.add_argument(
        "--off",
        action="store_true",
        help="Turn keyboard lighting OFF"
    )
    parser.add_argument(
        "--toggle",
        action="store_true",
        help="Toggle keyboard lighting (default)"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show current status"
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Auto-adjust brightness based on time of day (brightest daytime, dimmest past midnight)"
    )

    args = parser.parse_args()

    if args.auto:
        result = auto_adjust_brightness_by_time()
        if result["success"]:
            print("")
            if result["changed"]:
                print(f"✅ Keyboard brightness adjusted to {result['brightness']}% ({result['time_period']})")
            else:
                print(f"✅ Keyboard brightness already at {result['brightness']}% ({result['time_period']})")
            return 0
        else:
            print("")
            print("⚠️  Auto-adjust may not have been fully successful")
            return 1

    if args.status:
        state = get_current_state()
        print("=" * 70)
        print("KEYBOARD LIGHTING STATUS")
        print("=" * 70)
        print(f"State: {'ON' if state['is_on'] else 'OFF'}")
        print(f"Brightness: {state['brightness']}%")
        print(f"Last toggle: {state['last_toggle']}")
        print("=" * 70)
        return 0

    # Determine target state
    if args.on:
        target_state = True
    elif args.off:
        target_state = False
    else:
        # Default: toggle
        target_state = None

    # Perform toggle
    result = toggle_keyboard_lighting(target_state=target_state)

    if result["success"]:
        print("")
        print(f"✅ Keyboard lighting is now {'ON' if result['state'] else 'OFF'}")
        return 0
    else:
        print("")
        print("⚠️  Toggle may not have been fully successful")
        print("   Check Armoury Crate settings or registry values")
        return 1


if __name__ == "__main__":


    sys.exit(main())