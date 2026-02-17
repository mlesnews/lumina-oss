#!/usr/bin/env python3
"""
Dynamic Scaling Migration Status Updates

Intelligently adjusts update frequency based on:
- Time remaining (closer to completion = more frequent updates)
- Progress percentage (higher progress = more frequent)
- Migration activity (active migration = more frequent)

Starts with hourly updates, then scales dynamically.

Tags: #MIGRATION #DYNAMIC-SCALING #ADAPTIVE #JARVIS @LUMINA
"""

import json
import sys
import time
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from jarvis_migration_status_reporter import JARVISMigrationStatusReporter
from jarvis_migration_status_updates import send_status_update

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DynamicScalingUpdates")


class DynamicScalingUpdateScheduler:
    """Dynamically adjusts update frequency based on migration progress"""

    def __init__(self, base_interval_hours: float = 1.0):
        self.base_interval_hours = base_interval_hours
        self.reporter = JARVISMigrationStatusReporter(project_root)

        # Scaling thresholds
        self.min_interval_minutes = 15  # Minimum: 15 minutes (when very close)
        self.max_interval_hours = 3.0   # Maximum: 3 hours (when far away)

    def calculate_optimal_interval(self) -> float:
        """
        Calculate optimal update interval based on:
        - Progress percentage
        - Time remaining
        - Migration activity
        """
        status = self.reporter.get_current_status()

        if "error" in status:
            # Error getting status, use base interval
            return self.base_interval_hours

        progress = status["migration_progress"]
        eta = status["eta"]

        progress_percent = progress.get("progress_percent", 0)
        remaining_gb = progress.get("remaining_gb", 0)

        # Base scaling factor from progress
        # 0% progress = max interval (3 hours)
        # 100% progress = min interval (15 minutes)
        if progress_percent >= 100:
            # Complete or nearly complete - check every 15 minutes
            return self.min_interval_minutes / 60.0

        # Calculate interval based on progress
        # Linear scaling: more progress = shorter interval
        progress_factor = progress_percent / 100.0
        interval_hours = self.max_interval_hours * (1.0 - progress_factor * 0.8)  # Scale from 3h to 0.6h

        # Adjust based on time remaining
        if eta.get("status") == "complete":
            return self.min_interval_minutes / 60.0

        estimated_hours = eta.get("estimated_hours", 24)

        # Time-based scaling
        if estimated_hours <= 1:
            # Less than 1 hour remaining - update every 15 minutes
            interval_hours = self.min_interval_minutes / 60.0
        elif estimated_hours <= 2:
            # 1-2 hours remaining - update every 30 minutes
            interval_hours = 0.5
        elif estimated_hours <= 4:
            # 2-4 hours remaining - update every hour
            interval_hours = 1.0
        elif estimated_hours <= 8:
            # 4-8 hours remaining - update every 1.5 hours
            interval_hours = 1.5
        elif estimated_hours <= 24:
            # 8-24 hours remaining - update every 2 hours
            interval_hours = 2.0
        else:
            # More than 24 hours - update every 3 hours
            interval_hours = 3.0

        # Ensure within bounds
        min_interval = self.min_interval_minutes / 60.0
        max_interval = self.max_interval_hours
        interval_hours = max(min_interval, min(max_interval, interval_hours))

        return interval_hours

    def get_interval_info(self) -> dict:
        """Get current interval and scaling information"""
        interval_hours = self.calculate_optimal_interval()
        interval_minutes = interval_hours * 60

        status = self.reporter.get_current_status()
        progress = status.get("migration_progress", {})
        eta = status.get("eta", {})

        return {
            "interval_hours": round(interval_hours, 2),
            "interval_minutes": round(interval_minutes, 0),
            "progress_percent": progress.get("progress_percent", 0),
            "estimated_hours_remaining": eta.get("estimated_hours", 0),
            "scaling_reason": self._get_scaling_reason(interval_hours, progress, eta),
        }

    def _get_scaling_reason(self, interval_hours: float, progress: dict, eta: dict) -> str:
        """Get human-readable reason for current interval"""
        progress_percent = progress.get("progress_percent", 0)
        estimated_hours = eta.get("estimated_hours", 0)

        if progress_percent >= 95:
            return "Near completion (95%+ progress)"
        elif estimated_hours <= 1:
            return f"Less than 1 hour remaining ({estimated_hours:.1f}h)"
        elif estimated_hours <= 2:
            return f"1-2 hours remaining ({estimated_hours:.1f}h)"
        elif progress_percent >= 50:
            return f"Over 50% complete ({progress_percent:.1f}%)"
        elif progress_percent >= 25:
            return f"Over 25% complete ({progress_percent:.1f}%)"
        else:
            return f"Early stage ({progress_percent:.1f}% complete)"

    def run_dynamic_updates(self, max_updates: Optional[int] = None):
        """Run updates with dynamically adjusted intervals"""
        logger.info("Starting dynamic scaling status updates")
        logger.info(f"Base interval: {self.base_interval_hours} hours")
        logger.info(f"Interval range: {self.min_interval_minutes} minutes - {self.max_interval_hours} hours")

        update_count = 0
        last_interval_info = None

        try:
            while True:
                # Calculate optimal interval
                interval_info = self.get_interval_info()
                interval_hours = interval_info["interval_hours"]
                interval_seconds = interval_hours * 3600

                # Log interval change if it changed
                if last_interval_info and last_interval_info["interval_hours"] != interval_hours:
                    logger.info(
                        f"📊 Interval adjusted: {last_interval_info['interval_hours']:.2f}h → "
                        f"{interval_hours:.2f}h ({interval_info['scaling_reason']})"
                    )

                # Send status update
                send_status_update(self.reporter, interval_hours)
                update_count += 1

                # Log current interval info
                logger.info(
                    f"⏱️  Next update in {interval_info['interval_minutes']:.0f} minutes "
                    f"({interval_info['scaling_reason']})"
                )

                if max_updates and update_count >= max_updates:
                    logger.info(f"Reached max updates ({max_updates}), stopping")
                    break

                # Wait for next interval
                time.sleep(interval_seconds)
                last_interval_info = interval_info

        except KeyboardInterrupt:
            logger.info("Dynamic updates stopped by user")
        except Exception as e:
            logger.error(f"Error in dynamic updates: {e}", exc_info=True)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Dynamic Scaling Migration Status Updates"
    )
    parser.add_argument(
        "--base-interval",
        type=float,
        default=1.0,
        help="Base interval in hours (default: 1.0 hour)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Show current interval calculation and exit"
    )
    parser.add_argument(
        "--max-updates",
        type=int,
        help="Maximum number of updates to send (default: unlimited)"
    )

    args = parser.parse_args()

    scheduler = DynamicScalingUpdateScheduler(args.base_interval)

    if args.once:
        # Show interval calculation
        interval_info = scheduler.get_interval_info()
        print("\n" + "=" * 80)
        print("📊 DYNAMIC SCALING INTERVAL CALCULATION")
        print("=" * 80)
        print(f"Current Interval: {interval_info['interval_hours']:.2f} hours ({interval_info['interval_minutes']:.0f} minutes)")
        print(f"Progress: {interval_info['progress_percent']:.1f}%")
        print(f"Estimated Hours Remaining: {interval_info['estimated_hours_remaining']:.1f}")
        print(f"Scaling Reason: {interval_info['scaling_reason']}")
        print("=" * 80 + "\n")
    else:
        # Run dynamic updates
        scheduler.run_dynamic_updates(args.max_updates)


if __name__ == "__main__":

    main()