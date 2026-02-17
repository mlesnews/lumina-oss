#!/usr/bin/env python3
"""
Keyboard Lighting Auto-Adjust Daemon
Single lighting system: JARVIS Smart Lighting Day/Night Sync.

USER POLICY: Keyboard always 100%; external ON during day (6 AM–8 PM EST), off at night.
Calls JARVIS apply_day_night_settings when period changes (no separate MANUS time logic).
"""

import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_unified_logger import get_unified_logger

    logger = get_unified_logger("Application", "KeyboardLighting")
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("KeyboardLightingAutoDaemon")

# Single lighting system: JARVIS Smart Lighting
try:
    from scripts.python.jarvis_smart_lighting_day_night_sync import SmartLightingDayNightSync

    JARVIS_SYNC_AVAILABLE = True
except ImportError:
    logger.warning("JARVIS Smart Lighting not available, using fallback")
    JARVIS_SYNC_AVAILABLE = False
    try:
        from scripts.python.toggle_keyboard_lighting import auto_adjust_brightness_by_time
    except ImportError:
        logger.error("Could not import lighting functions")
        sys.exit(1)


def get_est_time():
    """Get current time in EST timezone"""
    est = timezone(timedelta(hours=-5))
    return datetime.now(est)


def run_auto_adjust_daemon(check_interval_minutes: int = 15):
    """
    Run auto-adjust daemon that checks and adjusts brightness periodically

    Args:
        check_interval_minutes: How often to check and adjust (default: 15 minutes)
    """
    logger.info("=" * 70)
    logger.info("KEYBOARD LIGHTING AUTO-ADJUST DAEMON (EST TIMEZONE)")
    logger.info("=" * 70)
    logger.info("")
    logger.info(f"Check interval: {check_interval_minutes} minutes")
    logger.info("Brightness schedule (USER POLICY — keyboard never dim, external on by day):")
    logger.info("  - Keyboard: always 100%")
    logger.info("  - External: ON during day (6 AM–8 PM EST), off at night")
    logger.info("")
    logger.info("Control: JARVIS Smart Lighting (single lighting system)")
    logger.info("Daemon started. Press Ctrl+C to stop.")
    logger.info("=" * 70)
    logger.info("")

    check_interval_seconds = check_interval_minutes * 60
    last_period = None
    sync = SmartLightingDayNightSync(project_root) if JARVIS_SYNC_AVAILABLE else None

    try:
        while True:
            current_time_est = get_est_time()

            if JARVIS_SYNC_AVAILABLE and sync is not None:
                current_period = sync.get_current_period()
                # Apply when period changes (day/night/night_shift) so screen + keyboard + external stay in sync
                if current_period != last_period:
                    logger.info(
                        "[%s EST] Period: %s → applying JARVIS Smart Lighting",
                        current_time_est.strftime("%H:%M:%S"),
                        current_period,
                    )
                    result = sync.apply_day_night_settings()
                    if result.get("keyboard_external_success"):
                        logger.info(
                            "  ✅ Applied: keyboard %s%%, external %s%%",
                            result.get("keyboard_brightness", 100),
                            result.get("external_lighting", 0),
                        )
                    else:
                        logger.warning("  ⚠️  Registry apply had issues")
                    last_period = current_period
            elif not JARVIS_SYNC_AVAILABLE:
                result = auto_adjust_brightness_by_time()
                if result.get("success"):
                    logger.info("  ✅ Adjusted to %s%% (fallback)", result.get("brightness", 100))

            # Wait before next check
            time.sleep(check_interval_seconds)

    except KeyboardInterrupt:
        logger.info("")
        logger.info("=" * 70)
        logger.info("Daemon stopped by user")
        logger.info("=" * 70)
    except Exception as e:
        logger.error(f"Daemon error: {e}", exc_info=True)
        raise


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Keyboard lighting auto-adjust daemon")
    parser.add_argument(
        "--interval", type=int, default=15, help="Check interval in minutes (default: 15)"
    )
    parser.add_argument("--once", action="store_true", help="Run once and exit (don't daemonize)")

    args = parser.parse_args()

    if args.once:
        # Single-run guard: skip if lighting already ran recently (avoids duplicate from headless + unified)
        try:
            from lighting_startup_guard import (
                mark_lighting_startup_done,
                should_skip_lighting_startup,
            )

            if should_skip_lighting_startup(project_root):
                logger.info("Lighting already run recently (single-run guard); skipping.")
                return 0
            mark_lighting_startup_done(project_root)
        except ImportError:
            pass
        # Run once and exit
        logger.info("Running auto-adjust once (JARVIS Smart Lighting)...")
        if JARVIS_SYNC_AVAILABLE:
            sync_once = SmartLightingDayNightSync(project_root)
            result = sync_once.apply_day_night_settings()
            if result.get("keyboard_external_success"):
                print(
                    "✅ Lighting applied: keyboard %s%%, external %s%% (period: %s)"
                    % (
                        result.get("keyboard_brightness", 100),
                        result.get("external_lighting", 0),
                        result.get("period", "unknown"),
                    )
                )
                return 0
            print("⚠️  JARVIS Smart Lighting registry apply had issues")
            return 1
        result = auto_adjust_brightness_by_time()
        if result.get("success"):
            time_period = result.get("time_period", "unknown")
            if result.get("changed", False):
                print(
                    "✅ Keyboard brightness adjusted to %s%% (%s)"
                    % (result["brightness"], time_period)
                )
            else:
                print(
                    "✅ Keyboard brightness already at %s%% (%s)"
                    % (result["brightness"], time_period)
                )
            return 0
        print("⚠️  Auto-adjust may not have been fully successful")
        return 1
    else:
        # Run as daemon
        run_auto_adjust_daemon(check_interval_minutes=args.interval)
        return 0


if __name__ == "__main__":
    sys.exit(main())
