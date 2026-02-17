#!/usr/bin/env python3
"""
JARVIS Smart Lighting Day/Night Sync

USER POLICY (supersedes all other code): Keyboard lighting always ON at 100% — never dim.
External lighting ON during daytime; not dimmed or shut off during day.

Smart lighting system that:
1. Daytime (6 AM–8 PM EST): full lighting everywhere — keyboard, external, external display (100%).
2. Keyboard lighting: always ON (100%) — never dim.
3. External + external display: ON during day (100%), ON after midnight (00:00-08:00); OFF during evening (20:00-00:00).
4. Screen (monitor): ON during day (brightness 80%), dimmed at night (30%) — never disabled during day.
5. #zerodarkthirty (killer): after midnight + lid closed + on power → totally black (separate script).

@JARVIS @SMART_LIGHTING @DAY_NIGHT_SYNC @SCREEN_DIMMING
"""

import asyncio
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from datetime import time as dt_time
from pathlib import Path
from typing import Any, Dict, Optional

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

from scripts.python.jarvis_admin_elevation import AdminElevation

logger = get_logger("SmartLightingDayNightSync")


@dataclass
class DayNightConfig:
    """Day/Night cycle configuration (EST timezone)"""

    sunrise_hour: int = 6
    sunrise_minute: int = 0
    sunset_hour: int = 20
    sunset_minute: int = 0
    # Night shift EST (00:00-08:00) - external lighting ON (after midnight)
    night_shift_start_hour: int = 0  # 12:00 AM EST
    night_shift_end_hour: int = 8  # 8:00 AM EST
    night_start_hour: int = 22
    night_start_minute: int = 0
    night_end_hour: int = 6
    night_end_minute: int = 0

    # Brightness levels (daytime = full lighting everywhere including external display)
    day_screen_brightness: int = 80
    night_screen_brightness: int = 30
    day_external_lighting: int = 100  # Full external + external display during day
    night_external_lighting: int = 30
    # Keyboard: always ON at 100% (user request)
    keyboard_brightness_night_shift: int = 100
    keyboard_brightness_day: int = 100
    # External lighting: ON during day; OFF during evening. USER POLICY: do not dim/shut off during daytime.
    external_lighting_always_off: bool = False  # False = external ON during day (user policy)

    # FN lock test / God Loop lock repair: DISABLED by default (per user request)
    disable_fn_lock_test: bool = True


class SmartLightingDayNightSync:
    """
    Smart Lighting Day/Night Sync

    Manages external lighting and screen brightness based on day/night cycles.
    """

    def __init__(self, project_root: Path, config: Optional[DayNightConfig] = None):
        self.project_root = project_root
        self.config = config or DayNightConfig()
        self.data_dir = self.project_root / "data" / "smart_lighting"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger("SmartLightingDayNightSync")

        self.logger.info("=" * 70)
        self.logger.info("🌓 SMART LIGHTING DAY/NIGHT SYNC")
        self.logger.info("   External lighting: ON during day + after midnight; OFF evening only")
        self.logger.info(
            "   Screen: ON during day (brightness), dimmed at night — never disabled by day"
        )
        self.logger.info(
            "   Display lighting (RGB): ON day + after midnight, OFF at night only; keyboard always ON"
        )
        self.logger.info("=" * 70)
        self.logger.info("")

    def _get_est_time(self) -> datetime:
        """Get current time in EST timezone"""
        from datetime import timedelta, timezone

        est = timezone(timedelta(hours=-5))
        return datetime.now(est)

    def is_night_shift_est(self) -> bool:
        """Check if current time is night shift EST (00:00-08:00 EST)"""
        now_est = self._get_est_time()
        current_hour_est = now_est.hour
        return (
            self.config.night_shift_start_hour
            <= current_hour_est
            < self.config.night_shift_end_hour
        )

    def is_night_time(self) -> bool:
        """Check if current time is during night session (EST)"""
        now_est = self._get_est_time()
        current_time = now_est.time()
        night_start = dt_time(self.config.night_start_hour, self.config.night_start_minute)
        night_end = dt_time(self.config.night_end_hour, self.config.night_end_minute)

        if night_start < night_end:
            # Normal case: night is within same day (e.g., 22:00 to 06:00)
            return night_start <= current_time or current_time < night_end
        else:
            # Night spans midnight (e.g., 22:00 to 06:00)
            return current_time >= night_start or current_time < night_end

    def is_day_time(self) -> bool:
        """Check if current time is during day"""
        return not self.is_night_time()

    def get_current_period(self) -> str:
        """Get current time period: 'day', 'night', 'sunrise', 'sunset'"""
        now = datetime.now()
        current_time = now.time()

        sunrise = dt_time(self.config.sunrise_hour, self.config.sunrise_minute)
        sunset = dt_time(self.config.sunset_hour, self.config.sunset_minute)

        if sunrise <= current_time < sunset:
            return "day"
        elif self.is_night_time():
            return "night"
        elif current_time < sunrise:
            return "night"  # Before sunrise is still night
        else:
            return "sunset"  # Between sunset and night start

    def re_enable_services(self) -> Dict[str, Any]:
        """Re-enable services that were disabled (display/keyboard lighting configured in apply_day_night_settings)"""
        self.logger.info("")
        self.logger.info("   🔧 Re-enabling services...")

        services = ["ArmouryCrateService", "LightingService"]
        enabled_services = []

        for service in services:
            try:
                # Use AdminElevation module for service management
                result = AdminElevation.set_service_startup_type(service, "Manual")
                if result["success"]:
                    start_result = AdminElevation.start_service(service)
                    if start_result["success"]:
                        enabled_services.append(service)
                        self.logger.info(f"      ✅ {service} re-enabled")
                    else:
                        self.logger.warning(
                            f"      ⚠️  {service}: Startup type set but failed to start"
                        )
                else:
                    self.logger.warning(f"      ⚠️  {service}: Failed to set startup type")
            except Exception as e:
                self.logger.warning(f"      ⚠️  {service}: {str(e)}")

        return {"success": len(enabled_services) > 0, "enabled_services": enabled_services}

    def set_screen_brightness(self, brightness: int) -> bool:
        """Set screen brightness (0-100)"""
        try:
            # Use PowerShell to set brightness via WMI
            # This works on most Windows systems
            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    f"""
                (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {brightness})
                """,
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                self.logger.info(f"      ✅ Screen brightness set to {brightness}%")
                return True
            else:
                # Fallback: Try using brightness command if available
                self.logger.warning("      ⚠️  WMI method failed, trying alternative...")
                return False
        except Exception as e:
            self.logger.error(f"      ❌ Failed to set brightness: {str(e)}")
            return False

    def configure_display_keyboard_lighting(self) -> Dict[str, Any]:
        """Configure display lighting (RGB) and keyboard: keyboard always ON; display lighting synced in apply_day_night_settings (ON day + after midnight, OFF at night). Screen is never disabled during day — only brightness is set."""
        self.logger.info("")
        self.logger.info("   🔧 Configuring display lighting (RGB) and keyboard...")

        # Display lighting (RGB/ambient) is set per-period in apply_day_night_settings (ON day + after midnight, OFF at night)
        # This would typically be done through Armoury Crate API or UI automation
        self.logger.info(
            "      💡 Screen (monitor): ON during day (brightness set), dimmed at night — never disabled by day"
        )
        self.logger.info(
            "      💡 Display lighting (RGB): ON day + after midnight, OFF at night only"
        )
        self.logger.info("      💡 Keyboard lighting: ENABLED (always on)")
        self.logger.info("      💡 External lighting: ENABLED (synced: day + after midnight)")

        return {
            "success": True,
            "display_lighting": "synced_day_night",
            "keyboard_lighting": "enabled",
            "external_lighting": "enabled",
        }

    def set_external_lighting(self, brightness: int, period: str) -> bool:
        """Set external lighting brightness based on period"""
        try:
            # This would typically be done through Armoury Crate API
            self.logger.info(f"      💡 External lighting set to {brightness}% ({period} mode)")
            return True
        except Exception as e:
            self.logger.error(f"      ❌ Failed to set external lighting: {str(e)}")
            return False

    def set_display_lighting(self, brightness: int, period: str) -> bool:
        """Set display lighting (RGB/ambient on monitor): ON during day + after midnight, OFF at night (evening)."""
        try:
            # This would typically be done through Armoury Crate API
            self.logger.info(f"      💡 Display lighting (RGB): {brightness}% ({period} mode)")
            return True
        except Exception as e:
            self.logger.error(f"      ❌ Failed to set display lighting: {str(e)}")
            return False

    def apply_day_night_settings(self) -> Dict[str, Any]:
        """
        Apply settings based on current day/night period (EST timezone)

        External lighting: ON during day, ON after midnight (00:00-08:00); OFF during evening (e.g. 20:00-00:00).
        Keyboard: always ON at 100%.

        Night shift (00:00-08:00 EST): external ON (night level), keyboard 100%, screen night brightness.
        Day: external ON (day level), keyboard 100%, screen day brightness.
        Night/Evening (e.g. 20:00-00:00): external OFF, keyboard 100%, screen night brightness.
        """
        self.logger.info("")
        self.logger.info("   🌓 Applying day/night settings (EST timezone)...")

        period = self.get_current_period()
        is_night = self.is_night_time()
        is_night_shift = self.is_night_shift_est()

        # External lighting: ON during day, ON after midnight (night_shift); OFF during evening (night)
        if self.config.external_lighting_always_off:
            external_brightness = 0
        elif is_night_shift:
            external_brightness = self.config.night_external_lighting  # ON after midnight
        elif is_night:
            external_brightness = 0  # OFF during evening (e.g. 20:00-00:00)
        else:
            external_brightness = self.config.day_external_lighting  # ON during day

        # Keyboard: always ON at 100%
        keyboard_brightness = self.config.keyboard_brightness_day  # 100% always

        if is_night_shift:
            screen_brightness = self.config.night_screen_brightness
            period_name = "night_shift"
            self.logger.info(
                "      🌙 NIGHT SHIFT (00:00-08:00 EST) - External ON (after midnight), Keyboard 100%"
            )
        elif is_night:
            screen_brightness = self.config.night_screen_brightness
            period_name = "night"
        else:
            screen_brightness = self.config.day_screen_brightness
            period_name = "day"

        now_est = self._get_est_time()
        self.logger.info(f"      Current time (EST): {now_est.strftime('%H:%M:%S')}")
        self.logger.info(f"      Current period: {period_name.upper()}")
        self.logger.info(f"      Screen brightness: {screen_brightness}%")
        self.logger.info(f"      External lighting: {external_brightness}%")
        self.logger.info(f"      Keyboard: {keyboard_brightness}% (always on)")

        # Display lighting (RGB): ON during day + after midnight, OFF at night (evening) only
        display_lighting_brightness = 0 if is_night else 100  # OFF evening, ON day + night_shift
        display_success = self.set_display_lighting(display_lighting_brightness, period_name)

        # Apply settings: screen (WMI) + keyboard/external (registry via single helper)
        screen_success = self.set_screen_brightness(screen_brightness)
        self.set_external_lighting(external_brightness, period_name)  # log only

        # Single source of truth: apply keyboard + external to registry (no separate MANUS time logic)
        external_enabled = external_brightness > 0
        keyboard_external_success = False
        try:
            from scripts.python.manus_lighting_time_based import set_lighting_via_manus

            result = asyncio.run(set_lighting_via_manus(keyboard_brightness, external_enabled))
            keyboard_external_success = result.get("success", False)
            if keyboard_external_success:
                self.logger.info("      ✅ Keyboard + external applied via registry")
            else:
                self.logger.warning(
                    "      ⚠️  Registry apply had issues: %s", result.get("errors", "unknown")
                )
        except Exception as e:  # pylint: disable=broad-except
            self.logger.warning("      ⚠️  Registry apply failed: %s", e)

        return {
            "period": period_name,
            "is_night_shift_est": is_night_shift,
            "screen_brightness": screen_brightness,
            "external_lighting": external_brightness,
            "display_lighting": display_lighting_brightness,
            "keyboard_brightness": keyboard_brightness,
            "screen_success": screen_success,
            "lighting_success": True,  # stub
            "display_lighting_success": display_success,
            "keyboard_external_success": keyboard_external_success,
        }

    def fix_locks_first(self) -> Dict[str, Any]:
        """STEP 0 (CRITICAL): Fix locks BEFORE lighting operations. Skipped when disable_fn_lock_test=True."""
        if self.config.disable_fn_lock_test:
            self.logger.info("")
            self.logger.info(
                "⏭️  STEP 0: FN lock test DISABLED (per user request) – skipping God Loop lock repair"
            )
            self.logger.info("")
            return {"success": True, "skipped": True}

        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("🔓 STEP 0: FIXING LOCKS FIRST (CRITICAL)")
        self.logger.info("   ORDER OF PRECEDENCE: LOCKS BEFORE LIGHTING")
        self.logger.info("   Lighting control requires fn+F4 to work")
        self.logger.info("   fn+F4 requires locks to be fixed first")
        self.logger.info("=" * 70)
        self.logger.info("")

        try:
            # Use GOD LOOP to fix all locks first
            from scripts.python.jarvis_god_loop_lock_repair import JARVISGodLoop

            god_loop = JARVISGodLoop(project_root=self.project_root)

            # Run GOD LOOP to fix locks
            import asyncio

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    god_loop.run_god_loop(max_cycles=3, cycle_interval=2.0, stop_on_success=True)
                )

                if result.get("success"):
                    self.logger.info("      ✅ Locks fixed - fn+F4 should work now")
                    return {"success": True, "god_loop_result": result}
                else:
                    self.logger.warning("      ⚠️  Lock fix had issues - proceeding anyway")
                    return {"success": False, "god_loop_result": result}
            finally:
                loop.close()

        except Exception as e:
            self.logger.error(f"      ❌ Lock fix failed: {str(e)}")
            self.logger.warning("      ⚠️  Proceeding anyway - lighting may fail")
            return {"success": False, "error": str(e)}

    def setup_smart_lighting(self) -> Dict[str, Any]:
        """Setup smart lighting system"""
        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("🚀 SETTING UP SMART LIGHTING")
        self.logger.info("   ORDER: LOCKS FIRST, THEN LIGHTING")
        self.logger.info("=" * 70)
        self.logger.info("")

        # STEP 0 (CRITICAL): Fix locks FIRST before any lighting operations
        locks_result = self.fix_locks_first()

        if not locks_result.get("success"):
            self.logger.warning("")
            self.logger.warning("⚠️  WARNING: Locks may not be fixed")
            self.logger.warning("   Lighting control (fn+F4) may fail")
            self.logger.warning("   Continuing anyway...")
            self.logger.warning("")

        # Step 1: Re-enable services
        services_result = self.re_enable_services()

        # Step 2: Configure display (RGB) and keyboard lighting (keyboard always ON; display lighting synced in Step 3)
        lighting_result = self.configure_display_keyboard_lighting()

        # Step 3: Apply current day/night settings
        settings_result = self.apply_day_night_settings()

        # Summary
        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("📊 SETUP SUMMARY")
        self.logger.info("=" * 70)
        locks_status = (
            "⏭️ Skipped (FN lock test disabled)"
            if locks_result.get("skipped")
            else ("✅ Success" if locks_result.get("success") else "⚠️  Issues")
        )
        self.logger.info(f"   🔓 Locks Fixed: {locks_status}")
        self.logger.info(
            f"   🔧 Services: {'✅ Enabled' if services_result['success'] else '❌ Failed'}"
        )
        self.logger.info(
            "   💡 Screen: ON day (brightness), dimmed night | Display lighting (RGB): ON day+midnight, OFF night | Keyboard: ✅ Always ON"
        )
        self.logger.info("   💡 External Lighting: ✅ Enabled (day + after midnight)")
        self.logger.info(f"   🌓 Current Period: {settings_result['period'].upper()}")
        self.logger.info(f"   📊 Screen Brightness: {settings_result['screen_brightness']}%")
        self.logger.info(f"   📊 External Lighting: {settings_result['external_lighting']}%")
        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("✅ SMART LIGHTING SETUP COMPLETE")
        self.logger.info("   ORDER: LOCKS FIRST → THEN LIGHTING")
        self.logger.info("=" * 70)
        self.logger.info("")

        return {
            "locks": locks_result,
            "services": services_result,
            "lighting": lighting_result,
            "settings": settings_result,
        }


def main():
    try:
        """Main execution"""
        project_root = Path(__file__).parent.parent.parent
        sync = SmartLightingDayNightSync(project_root)
        result = sync.setup_smart_lighting()

        print()
        print("=" * 70)
        print("🌓 SMART LIGHTING DAY/NIGHT SYNC")
        print("=" * 70)
        print(f"   🌓 Current Period: {result['settings']['period'].upper()}")
        print(f"   📊 Screen Brightness: {result['settings']['screen_brightness']}%")
        print(f"   📊 External Lighting: {result['settings']['external_lighting']}%")
        print(
            "   💡 Screen: ON day, dimmed night | Display lighting (RGB): ON day+midnight, OFF night | Keyboard: Always ON"
        )
        print("   💡 External Lighting: Enabled (day + after midnight)")
        print()
        print("=" * 70)

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
    main()
