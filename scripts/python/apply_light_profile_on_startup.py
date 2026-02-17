#!/usr/bin/env python3
"""
JARVIS - Apply Light Profile on Startup
USS Lumina - @scotty (Windows Systems Architect)

Enhanced startup script that:
1. Waits for Armoury Crate to be ready
2. Applies the Light profile
3. Ensures registry settings persist
4. Retries if needed

@JARVIS @LIGHTING @STARTUP @AUTOMATION @LUMINA
"""

import sys
import subprocess
import time
import asyncio
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from lumina_unified_logger import get_unified_logger
    logger = get_unified_logger("Application", "LightProfile")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("JARVIS_LightProfileStartup")


def wait_for_armoury_crate(max_wait: int = 60) -> bool:
    """Wait for Armoury Crate service/process to be ready"""
    logger.info("Waiting for Armoury Crate to be ready...")

    for attempt in range(max_wait):
        try:
            # Check if Armoury Crate process is running
            result = subprocess.run(
                ["powershell", "-Command", "Get-Process -Name 'ArmouryCrate*' -ErrorAction SilentlyContinue | Select-Object -First 1"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0 and result.stdout.strip():
                logger.info(f"✅ Armoury Crate detected (attempt {attempt + 1}/{max_wait})")
                time.sleep(5)  # Give it a few more seconds to fully initialize
                return True

            # Also check for service
            service_result = subprocess.run(
                ["powershell", "-Command", "Get-Service -Name 'ArmouryCrateService' -ErrorAction SilentlyContinue | Where-Object {$_.Status -eq 'Running'}"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if service_result.returncode == 0 and service_result.stdout.strip():
                logger.info(f"✅ Armoury Crate service running (attempt {attempt + 1}/{max_wait})")
                time.sleep(5)
                return True

        except Exception as e:
            logger.debug(f"Check attempt {attempt + 1} failed: {e}")

        if attempt < max_wait - 1:
            time.sleep(1)

    logger.warning("⚠️  Armoury Crate not detected, proceeding anyway...")
    return False


def is_daylight_hours_est() -> bool:
    """Check if current time is daylight hours EST (6 AM - 8 PM EST)"""
    from datetime import timezone, timedelta
    est = timezone(timedelta(hours=-5))
    now_est = datetime.now(est)
    return 6 <= now_est.hour < 20


def set_registry_persistence() -> Dict[str, Any]:
    """
    Set registry keys to ensure lighting persists
    - Keyboard: ON (100%) during daylight hours (6 AM - 8 PM EST), ON (5-10%, using 7%) during night-time (8 PM - 6 AM EST)
    - External lighting: Always OFF
    - FN key testing disabled
    """
    logger.info("Setting registry persistence for lighting...")

    # Check if daylight hours (6 AM - 8 PM EST)
    is_daylight = is_daylight_hours_est()
    keyboard_brightness = 100 if is_daylight else 7  # ON (100%) daylight hours, ON (7% - 5-10% range) night-time
    external_enabled = 0  # All external lighting always OFF

    time_period = "ON (100%) - daylight hours (6 AM - 8 PM)" if is_daylight else "ON (5-10%, using 7%) - night-time (8 PM - 6 AM)"
    logger.info(f"   Keyboard: {keyboard_brightness}% ({time_period})")
    logger.info(f"   External lighting: OFF (always OFF)")

    script = f"""
$paths = @(
    'HKCU:\\Software\\ASUS\\ArmouryDevice\\Aura',
    'HKCU:\\Software\\ASUS\\Aura',
    'HKLM:\\SOFTWARE\\ASUS\\ArmouryDevice\\Aura',
    'HKLM:\\SOFTWARE\\ASUS\\Aura'
)

$keyboardBrightness = {keyboard_brightness}
$externalEnabled = {external_enabled}

$success = $false
foreach ($path in $paths) {{
    try {{
        if (-not (Test-Path $path)) {{
            New-Item -Path $path -Force -ErrorAction SilentlyContinue | Out-Null
        }}
        if (Test-Path $path) {{
            # Keyboard brightness - full daytime, dim after midnight EST
            Set-ItemProperty -Path $path -Name 'Brightness' -Value $keyboardBrightness -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'BacklightBrightness' -Value $keyboardBrightness -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'KeyboardBrightness' -Value $keyboardBrightness -Type DWord -ErrorAction SilentlyContinue
            # Keyboard stays enabled
            Set-ItemProperty -Path $path -Name 'KeyboardEnabled' -Value 1 -Type DWord -ErrorAction SilentlyContinue
            # External/other lighting - OFF after midnight EST
            Set-ItemProperty -Path $path -Name 'Enable' -Value $externalEnabled -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'Enabled' -Value $externalEnabled -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'LightingEnabled' -Value $externalEnabled -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'ExternalEnabled' -Value $externalEnabled -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'Profile' -Value 'Light' -Type String -ErrorAction SilentlyContinue
            $success = $true
        }}
    }} catch {{}}
}}
if ($success) {{
    Write-Output "Registry updated"
}} else {{
    Write-Output "Registry update failed"
}}
"""

    try:
        result = subprocess.run(
            ["powershell", "-Command", script],
            capture_output=True,
            text=True,
            timeout=30
        )

        if "Registry updated" in result.stdout:
            logger.info("✅ Registry persistence set")
            return {"success": True}
        else:
            logger.warning("⚠️  Registry update may have failed")
            return {"success": False, "error": result.stderr}

    except Exception as e:
        logger.warning(f"⚠️  Registry update error: {e}")
        return {"success": False, "error": str(e)}


async def apply_light_profile_with_retry(max_retries: int = 3) -> Dict[str, Any]:
    """Apply light profile with retry logic"""
    # Import here to avoid circular imports
    try:
        from scripts.python.configure_armoury_crate_light_profile import configure_light_profile
    except ImportError:
        # Fallback: run the script directly
        logger.warning("⚠️  Could not import configure_light_profile, using direct script execution")
        for attempt in range(max_retries):
            logger.info(f"Attempt {attempt + 1}/{max_retries}: Running configuration script...")
            try:
                result = subprocess.run(
                    [sys.executable, str(project_root / "scripts" / "python" / "configure_armoury_crate_light_profile.py")],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if result.returncode == 0:
                    logger.info("✅ Light profile applied successfully")
                    return {"status": "success"}
                else:
                    logger.warning(f"⚠️  Attempt {attempt + 1} failed")
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 10
                        logger.info(f"Waiting {wait_time}s before retry...")
                        await asyncio.sleep(wait_time)
            except Exception as e:
                logger.error(f"❌ Error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 10
                    await asyncio.sleep(wait_time)
        return {"status": "error", "error": "All retries failed"}

    # Use imported function
    for attempt in range(max_retries):
        logger.info(f"Attempt {attempt + 1}/{max_retries}: Applying Light profile...")

        try:
            result = await configure_light_profile()

            if result.get("status") == "success":
                logger.info("✅ Light profile applied successfully")
                return result
            else:
                logger.warning(f"⚠️  Attempt {attempt + 1} failed: {result.get('errors', ['Unknown'])}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 10  # 10s, 20s, 30s
                    logger.info(f"Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)

        except Exception as e:
            logger.error(f"❌ Error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 10
                logger.info(f"Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)

    logger.error("❌ Failed to apply Light profile after all retries")
    return {"status": "error", "error": "All retries failed"}


async def main_async():
    """Main async execution"""
    logger.info("=" * 70)
    logger.info("JARVIS - APPLYING LIGHT PROFILE ON STARTUP")
    logger.info("USS Lumina - @scotty (Windows Systems Architect)")
    logger.info("=" * 70)
    logger.info("")

    # Step 1: Wait for Armoury Crate
    logger.info("STEP 1: Waiting for Armoury Crate to be ready...")
    armoury_ready = wait_for_armoury_crate(max_wait=60)

    # Step 2: Set registry persistence
    logger.info("")
    logger.info("STEP 2: Setting registry persistence...")
    reg_result = set_registry_persistence()

    # Step 3: Force enable lighting (ensures it actually turns on)
    logger.info("")
    logger.info("STEP 3: Force enabling keyboard lighting...")
    force_result = {"success": False}
    try:
        from ac_force_enable_lighting import force_enable_keyboard_lighting
        # Determine brightness based on time
        keyboard_brightness = 100 if is_daylight_hours_est() else 7
        force_result = await force_enable_keyboard_lighting(keyboard_brightness)
        if force_result.get("success"):
            methods = ", ".join(force_result.get("methods_used", []))
            logger.info(f"✅ Lighting force-enabled via: {methods} ({keyboard_brightness}%)")
        else:
            logger.warning("⚠️  Force enable had issues, but continuing...")
    except ImportError:
        logger.warning("⚠️  ac_force_enable_lighting not available, skipping force-enable")
    except Exception as e:
        logger.warning(f"⚠️  Force enable error: {e}, continuing...")

    # Step 4: Apply Light profile with retry
    logger.info("")
    logger.info("STEP 4: Applying Light profile...")
    profile_result = await apply_light_profile_with_retry(max_retries=3)

    # Summary
    logger.info("")
    logger.info("")
    logger.info("=" * 70)
    logger.info("STARTUP APPLICATION SUMMARY")
    logger.info("=" * 70)
    logger.info(f"  Armoury Crate Ready: {'✅' if armoury_ready else '⚠️'}")
    logger.info(f"  Registry Persistence: {'✅' if reg_result.get('success') else '⚠️'}")
    logger.info(f"  Force Enable Lighting: {'✅' if force_result.get('success') else '⚠️'}")
    logger.info(f"  Profile Applied: {'✅' if profile_result.get('status') == 'success' else '❌'}")
    logger.info("=" * 70)

    return profile_result


def main():
    """Main execution"""
    try:
        result = asyncio.run(main_async())
        return 0 if result.get("status") == "success" else 1
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":


    sys.exit(main())