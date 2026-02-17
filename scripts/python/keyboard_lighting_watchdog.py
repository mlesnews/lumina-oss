#!/usr/bin/env python3
"""
Keyboard Lighting Auto-Adjust Watchdog
Monitors keyboard lighting auto-adjustment and barks/alerts if it fails
"""

import sys
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("KeyboardLightingWatchdog")

# Import the toggle functions
try:
    from scripts.python.toggle_keyboard_lighting import (
        auto_adjust_brightness_by_time,
        get_time_based_brightness,
        get_current_state,
        load_state
    )
except ImportError:
    logger.error("Could not import toggle_keyboard_lighting functions")
    sys.exit(1)

# Watchdog state file
WATCHDOG_STATE_FILE = project_root / "data" / "keyboard_lighting_watchdog_state.json"


def load_watchdog_state() -> Dict[str, Any]:
    """Load watchdog state"""
    default_state = {
        "last_check": None,
        "last_success": None,
        "failure_count": 0,
        "last_failure": None,
        "alerts_sent": []
    }

    if WATCHDOG_STATE_FILE.exists():
        try:
            with open(WATCHDOG_STATE_FILE, 'r', encoding='utf-8') as f:
                import json
                state = json.load(f)
                return {**default_state, **state}
        except Exception as e:
            logger.warning(f"Could not load watchdog state: {e}")

    return default_state


def save_watchdog_state(state: Dict[str, Any]):
    """Save watchdog state"""
    WATCHDOG_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        import json
        with open(WATCHDOG_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        logger.error(f"Could not save watchdog state: {e}")


def bark_alert(message: str, severity: str = "warning"):
    """
    Bark/alert if keyboard lighting auto-adjust fails

    Args:
        message: Alert message
        severity: Alert severity (warning, error, critical)
    """
    logger.warning("=" * 70)
    logger.warning("🐕 WATCHDOG BARK - KEYBOARD LIGHTING ISSUE")
    logger.warning("=" * 70)
    logger.warning(f"Severity: {severity.upper()}")
    logger.warning(f"Message: {message}")
    logger.warning("=" * 70)

    # Try to use R2-D2 sound system for audible alert
    try:
        from scripts.python.r2d2_sound_system import get_r2d2_sound_system, R2D2SoundType
        r2d2 = get_r2d2_sound_system()

        if severity == "critical":
            r2d2.play_alert()
            r2d2.play_warning()
        elif severity == "error":
            r2d2.play_warning()
        else:
            r2d2.play_attention()

        logger.info("🔊 Audible alert played (R2-D2)")
    except Exception as e:
        logger.debug(f"Could not play audible alert: {e}")

    # Try to use JARVIS alert system if available
    try:
        from scripts.python.jarvis_reverse_stoplight_alerts import (
            JARVISReverseStoplightAlerts,
            AlertLevel
        )

        # Map severity to alert level
        level_map = {
            "warning": AlertLevel.WARNING,
            "error": AlertLevel.WARNING,
            "critical": AlertLevel.CRITICAL
        }
        alert_level = level_map.get(severity, AlertLevel.WARNING)

        # Note: This would need a canvas instance, so we'll just log for now
        logger.info(f"📢 Alert level: {alert_level.value}")
    except Exception as e:
        logger.debug(f"Could not use JARVIS alert system: {e}")

    # Print to console (always works)
    print("")
    print("🐕 WATCHDOG BARK!")
    print(f"⚠️  {message}")
    print("")


def check_keyboard_lighting_health() -> Dict[str, Any]:
    """
    Check if keyboard lighting auto-adjust is working correctly

    Returns:
        Dict with health status
    """
    current_time = datetime.now()
    current_hour = current_time.hour

    # Get expected brightness for current time
    expected_brightness = get_time_based_brightness()
    time_period = "night (past midnight)" if 0 <= current_hour < 6 else "daytime"

    # Get actual brightness
    current_state = get_current_state()
    actual_brightness = current_state.get("brightness", 0)
    is_on = current_state.get("is_on", False)

    # Check if brightness matches expected
    brightness_match = actual_brightness == expected_brightness

    # Check if lighting is on (should always be on, just brightness varies)
    lighting_on = is_on

    # Determine health status
    if brightness_match and lighting_on:
        health_status = "healthy"
        message = f"✅ Keyboard lighting is correct: {actual_brightness}% ({time_period})"
    elif not lighting_on:
        health_status = "error"
        message = f"❌ Keyboard lighting is OFF (should be ON at {expected_brightness}%)"
    elif not brightness_match:
        health_status = "warning"
        message = f"⚠️  Brightness mismatch: {actual_brightness}% (expected {expected_brightness}% for {time_period})"
    else:
        health_status = "unknown"
        message = "❓ Unknown keyboard lighting state"

    return {
        "health_status": health_status,
        "message": message,
        "expected_brightness": expected_brightness,
        "actual_brightness": actual_brightness,
        "is_on": lighting_on,
        "time_period": time_period,
        "timestamp": current_time.isoformat()
    }


def attempt_fix() -> bool:
    """Attempt to fix keyboard lighting by running auto-adjust"""
    logger.info("🔧 Attempting to fix keyboard lighting...")

    try:
        result = auto_adjust_brightness_by_time()
        if result.get("success", False):
            logger.info("✅ Fix attempt successful")
            return True
        else:
            logger.warning("⚠️  Fix attempt may not have been fully successful")
            return False
    except Exception as e:
        logger.error(f"❌ Fix attempt failed: {e}")
        return False


def run_watchdog_check(check_interval_minutes: int = 15, auto_fix: bool = True):
    """
    Run watchdog check loop

    Args:
        check_interval_minutes: How often to check (default: 15 minutes)
        auto_fix: Whether to automatically attempt fixes (default: True)
    """
    logger.info("=" * 70)
    logger.info("🐕 KEYBOARD LIGHTING WATCHDOG")
    logger.info("=" * 70)
    logger.info("")
    logger.info(f"Check interval: {check_interval_minutes} minutes")
    logger.info(f"Auto-fix: {'Enabled' if auto_fix else 'Disabled'}")
    logger.info("")
    logger.info("Watchdog started. Will bark if keyboard lighting fails!")
    logger.info("=" * 70)
    logger.info("")

    check_interval_seconds = check_interval_minutes * 60
    consecutive_failures = 0
    max_consecutive_failures = 3  # Bark after 3 consecutive failures

    try:
        while True:
            current_time = datetime.now()

            # Run health check
            health = check_keyboard_lighting_health()

            logger.info(f"[{current_time.strftime('%H:%M:%S')}] Health check: {health['health_status']}")
            logger.info(f"  {health['message']}")

            # Update watchdog state
            watchdog_state = load_watchdog_state()
            watchdog_state["last_check"] = current_time.isoformat()

            # If healthy, reset failure count
            if health["health_status"] == "healthy":
                if consecutive_failures > 0:
                    logger.info(f"✅ Recovered after {consecutive_failures} failures")
                consecutive_failures = 0
                watchdog_state["last_success"] = current_time.isoformat()
                watchdog_state["failure_count"] = 0
            else:
                # Not healthy - increment failure count
                consecutive_failures += 1
                watchdog_state["failure_count"] = watchdog_state.get("failure_count", 0) + 1
                watchdog_state["last_failure"] = current_time.isoformat()

                # Attempt auto-fix if enabled
                if auto_fix:
                    logger.info("  🔧 Attempting auto-fix...")
                    fix_success = attempt_fix()

                    if fix_success:
                        # Re-check after fix
                        time.sleep(2)
                        health_after_fix = check_keyboard_lighting_health()

                        if health_after_fix["health_status"] == "healthy":
                            logger.info("  ✅ Auto-fix successful!")
                            consecutive_failures = 0
                            watchdog_state["last_success"] = current_time.isoformat()
                            watchdog_state["failure_count"] = 0
                        else:
                            logger.warning(f"  ⚠️  Auto-fix attempted but still unhealthy: {health_after_fix['message']}")
                    else:
                        logger.warning("  ⚠️  Auto-fix failed")

                # Bark if too many consecutive failures
                if consecutive_failures >= max_consecutive_failures:
                    severity = "critical" if consecutive_failures >= 5 else "error"
                    bark_alert(
                        f"Keyboard lighting auto-adjust has failed {consecutive_failures} times consecutively. "
                        f"Current: {health['actual_brightness']}%, Expected: {health['expected_brightness']}% ({health['time_period']}). "
                        f"Auto-fix: {'Failed' if auto_fix else 'Disabled'}",
                        severity=severity
                    )

            save_watchdog_state(watchdog_state)

            # Wait before next check
            logger.debug(f"  Next check in {check_interval_minutes} minutes...")
            time.sleep(check_interval_seconds)

    except KeyboardInterrupt:
        logger.info("")
        logger.info("=" * 70)
        logger.info("Watchdog stopped by user")
        logger.info("=" * 70)
    except Exception as e:
        logger.error(f"Watchdog error: {e}", exc_info=True)
        bark_alert(f"Watchdog crashed: {e}", severity="critical")
        raise


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Keyboard lighting auto-adjust watchdog")
    parser.add_argument(
        "--interval",
        type=int,
        default=15,
        help="Check interval in minutes (default: 15)"
    )
    parser.add_argument(
        "--no-auto-fix",
        action="store_true",
        help="Disable automatic fix attempts"
    )
    parser.add_argument(
        "--check-once",
        action="store_true",
        help="Run one check and exit"
    )

    args = parser.parse_args()

    if args.check_once:
        # Run one check
        health = check_keyboard_lighting_health()
        print("")
        print("=" * 70)
        print("KEYBOARD LIGHTING HEALTH CHECK")
        print("=" * 70)
        print(f"Status: {health['health_status'].upper()}")
        print(f"Message: {health['message']}")
        print(f"Expected: {health['expected_brightness']}%")
        print(f"Actual: {health['actual_brightness']}%")
        print(f"Time period: {health['time_period']}")
        print("=" * 70)
        print("")

        if health["health_status"] != "healthy":
            bark_alert(health["message"], severity="warning")
            return 1
        return 0
    else:
        # Run as watchdog daemon
        run_watchdog_check(
            check_interval_minutes=args.interval,
            auto_fix=not args.no_auto_fix
        )
        return 0


if __name__ == "__main__":

    sys.exit(main())