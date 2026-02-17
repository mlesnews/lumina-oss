#!/usr/bin/env python3
"""
Lighting registry helper + CLI (single system: JARVIS decides, this module applies).

- set_lighting_via_manus(keyboard_brightness, external_enabled): applies to registry (used by JARVIS).
- CLI with no args: delegates to JARVIS Smart Lighting (single source of truth).
- CLI --brightness / --daylight / --night: set once (no time logic here).

Do not add time-based logic here; JARVIS Smart Lighting Day/Night Sync is the single lighting system.
"""

import asyncio
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict

# Project setup
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from lumina_unified_logger import LuminaUnifiedLogger

    logger = LuminaUnifiedLogger("System", "MANUSLighting")
    _logger = logger.get_logger()
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    _logger = logging.getLogger("MANUSLighting")


def _get_est_time() -> datetime:
    """Get current time in EST"""
    est = timezone(timedelta(hours=-5))
    return datetime.now(est)


def _is_daylight_hours_est() -> bool:
    """Check if daylight hours (6 AM - 8 PM EST)"""
    est_time = _get_est_time()
    return 6 <= est_time.hour < 20


def _run_powershell(script: str) -> Dict[str, Any]:
    """Run PowerShell script and return result"""
    try:
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", script],
            capture_output=True,
            text=True,
            timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def set_keyboard_brightness_via_registry(
    brightness: int, enabled: bool = True
) -> Dict[str, Any]:
    """Set keyboard brightness via registry (fast method)"""
    script = f"""
$paths = @(
    'HKCU:\\Software\\ASUS\\ArmouryDevice\\Aura',
    'HKCU:\\Software\\ASUS\\Aura',
    'HKLM:\\SOFTWARE\\ASUS\\ArmouryDevice\\Aura',
    'HKLM:\\SOFTWARE\\ASUS\\Aura'
)

$brightness = {brightness}
$enabled = {1 if enabled else 0}

$updated = 0
foreach ($path in $paths) {{
    try {{
        if (-not (Test-Path $path)) {{
            New-Item -Path $path -Force -ErrorAction SilentlyContinue | Out-Null
        }}
        if (Test-Path $path) {{
            Set-ItemProperty -Path $path -Name 'Brightness' -Value $brightness -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'KeyboardBrightness' -Value $brightness -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'BacklightBrightness' -Value $brightness -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'KeyboardEnabled' -Value $enabled -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'Enable' -Value $enabled -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'ExternalEnabled' -Value 0 -Type DWord -ErrorAction SilentlyContinue
            $updated++
        }}
    }} catch {{
        # Continue to next path
    }}
}}

if ($updated -gt 0) {{
    Write-Output "OK:$updated"
}} else {{
    Write-Output "Failed"
}}
"""
    result = _run_powershell(script)
    if result["success"] and "OK:" in result["stdout"]:
        return {"success": True, "message": result["stdout"]}
    return {"success": False, "message": result.get("stdout", result.get("error", "Failed"))}


async def set_lighting_via_manus(
    keyboard_brightness: int, external_enabled: bool = False
) -> Dict[str, Any]:
    """
    Set lighting using @MANUS (comprehensive method with fallbacks)

    USER POLICY: Keyboard always 100%; external ON during day, off at night.

    Args:
        keyboard_brightness: 0-100 (policy: always 100%)
        external_enabled: True during daytime (6 AM–8 PM EST), False at night
    """
    _logger.info(
        f"@MANUS: Setting lighting (keyboard: {keyboard_brightness}%, external: {'ON' if external_enabled else 'OFF'})"
    )

    result = {"success": False, "method": None, "steps_completed": [], "errors": []}

    # Method 1: Registry (fast, always works)
    try:
        reg_result = await set_keyboard_brightness_via_registry(
            keyboard_brightness, enabled=(keyboard_brightness > 0)
        )
        if reg_result["success"]:
            result["success"] = True
            result["method"] = "registry"
            result["steps_completed"].append("registry")
            _logger.info(f"✅ Registry method: {reg_result['message']}")
        else:
            result["errors"].append(f"Registry: {reg_result['message']}")
    except Exception as e:
        result["errors"].append(f"Registry error: {e}")

    # Method 2: Try @MANUS full automation if keyboard brightness is 100% (daylight)
    # Only use full automation for maximum brightness to avoid UI overhead
    if keyboard_brightness == 100 and not result["success"]:
        try:
            from scripts.python.manus_enable_all_lighting_automated import (
                enable_keyboard_via_registry as manus_registry,
            )

            manus_result = await manus_registry()
            if manus_result.get("success"):
                result["success"] = True
                result["method"] = "manus_registry"
                result["steps_completed"].append("manus_registry")
                _logger.info("✅ @MANUS registry method")
        except ImportError:
            _logger.debug("@MANUS full automation not available")
        except Exception as e:
            result["errors"].append(f"@MANUS registry: {e}")

    # Method 3: External lighting per user policy (ON during day, OFF at night)
    try:
        ext_val = 1 if external_enabled else 0
        ext_script = f"""
$paths = @(
    'HKCU:\\Software\\ASUS\\ArmouryDevice\\Aura',
    'HKLM:\\SOFTWARE\\ASUS\\ArmouryDevice\\Aura'
)
$extVal = {ext_val}
foreach ($path in $paths) {{
    try {{
        if (Test-Path $path) {{
            Set-ItemProperty -Path $path -Name 'ExternalEnabled' -Value $extVal -Type DWord -ErrorAction SilentlyContinue
        }}
    }} catch {{}}
}}
Write-Output "OK"
"""
        ext_result = _run_powershell(ext_script)
        if ext_result["success"]:
            result["steps_completed"].append("external_" + ("on" if external_enabled else "off"))
    except Exception as e:
        result["errors"].append(f"External lighting: {e}")

    return result


def apply_time_based_lighting_sync() -> Dict[str, Any]:
    """
    Delegate to JARVIS Smart Lighting (single lighting system).
    Kept for backward compatibility; prefer calling JARVIS apply_day_night_settings directly.
    """
    from scripts.python.jarvis_smart_lighting_day_night_sync import SmartLightingDayNightSync

    sync = SmartLightingDayNightSync(PROJECT_ROOT)
    return sync.apply_day_night_settings()


def main():
    """CLI entry point. Default (no args) delegates to JARVIS Smart Lighting (single system)."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Lighting control — default: JARVIS Smart Lighting; --brightness/--daylight/--night: set once"
    )
    parser.add_argument("--brightness", type=int, help="Set specific keyboard brightness (0-100)")
    parser.add_argument(
        "--daylight", action="store_true", help="Force daylight (100% keyboard, external ON)"
    )
    parser.add_argument(
        "--night", action="store_true", help="Force night (100% keyboard, external OFF)"
    )

    args = parser.parse_args()

    # No args: delegate to JARVIS (single lighting system)
    if args.brightness is None and not args.daylight and not args.night:
        result = apply_time_based_lighting_sync()
        if result.get("keyboard_external_success"):
            print(
                "✅ Lighting applied: keyboard %s%%, external %s%% (period: %s)"
                % (
                    result.get("keyboard_brightness", 100),
                    result.get("external_lighting", 0),
                    result.get("period", "unknown"),
                )
            )
            sys.exit(0)
        print("❌ JARVIS Smart Lighting apply had issues")
        sys.exit(1)

    # Explicit args: set once via registry helper (no time logic)
    async def run_once():
        if args.brightness is not None:
            return await set_lighting_via_manus(args.brightness, False)
        if args.daylight:
            return await set_lighting_via_manus(100, True)
        return await set_lighting_via_manus(100, False)  # night: 100% kb, external OFF

    result = asyncio.run(run_once())
    if result.get("success"):
        print("✅ Lighting set: Keyboard %s percent" % result.get("keyboard_brightness", "N/A"))
        sys.exit(0)
    print("❌ Failed: %s" % result.get("errors", "Unknown error"))
    sys.exit(1)


if __name__ == "__main__":
    main()
