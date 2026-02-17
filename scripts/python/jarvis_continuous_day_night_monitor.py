#!/usr/bin/env python3
"""
JARVIS Continuous Day/Night Monitor

Continuous monitoring system that adjusts lighting and screen brightness
based on day/night cycles. Runs in background and adjusts automatically.

@JARVIS @CONTINUOUS @DAY_NIGHT @MONITOR
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

from scripts.python.jarvis_smart_lighting_day_night_sync import (
    SmartLightingDayNightSync,
    DayNightConfig
)

logger = get_logger("ContinuousDayNightMonitor")


class ContinuousDayNightMonitor:
    """
    Continuous Day/Night Monitor

    Monitors time and adjusts lighting/screen brightness automatically.
    """

    def __init__(self, project_root: Path, check_interval: int = 60):
        self.project_root = project_root
        self.check_interval = check_interval  # seconds
        self.logger = get_logger("ContinuousDayNightMonitor")
        self.sync = SmartLightingDayNightSync(project_root)
        self.running = False
        self.last_period = None

        self.logger.info("=" * 70)
        self.logger.info("🌓 CONTINUOUS DAY/NIGHT MONITOR")
        self.logger.info("   Automatic lighting and screen brightness adjustment")
        self.logger.info("=" * 70)
        self.logger.info("")

    def run_once(self) -> Dict[str, Any]:
        """Run one check and adjustment cycle"""
        current_period = self.sync.get_current_period()

        # Only adjust if period changed
        if current_period != self.last_period:
            self.logger.info(f"   🌓 Period changed: {self.last_period} → {current_period}")
            result = self.sync.apply_day_night_settings()
            self.last_period = current_period
            return {
                "adjusted": True,
                "period": current_period,
                "result": result
            }
        else:
            return {
                "adjusted": False,
                "period": current_period
            }

    def run_continuous(self, duration: Optional[int] = None):
        """Run continuously"""
        self.running = True
        start_time = datetime.now()

        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("🔄 STARTING CONTINUOUS MONITORING")
        self.logger.info(f"   Check interval: {self.check_interval} seconds")
        if duration:
            self.logger.info(f"   Duration: {duration} seconds")
        else:
            self.logger.info("   Duration: Infinite (Ctrl+C to stop)")
        self.logger.info("=" * 70)
        self.logger.info("")

        # Initial setup
        self.logger.info("   🚀 Initial setup...")
        self.sync.setup_smart_lighting()
        self.last_period = self.sync.get_current_period()

        try:
            while self.running:
                result = self.run_once()

                if result.get("adjusted"):
                    self.logger.info(f"      ✅ Adjusted to {result['period']} settings")

                time.sleep(self.check_interval)

                # Check duration
                if duration:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    if elapsed >= duration:
                        self.logger.info("")
                        self.logger.info(f"   ⏰ Duration reached ({duration} seconds)")
                        break
        except KeyboardInterrupt:
            self.logger.info("")
            self.logger.info("   ⏹️  Stopped by user (Ctrl+C)")

        self.running = False

        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("✅ CONTINUOUS MONITORING STOPPED")
        self.logger.info("=" * 70)
        self.logger.info("")


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Continuous Day/Night Monitor")
        parser.add_argument("--interval", type=int, default=60, help="Check interval in seconds (default: 60)")
        parser.add_argument("--duration", type=int, default=None, help="Duration in seconds (default: infinite)")
        parser.add_argument("--once", action="store_true", help="Run once and exit")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        monitor = ContinuousDayNightMonitor(project_root, check_interval=args.interval)

        if args.once:
            result = monitor.run_once()
            print()
            print("=" * 70)
            print("🌓 DAY/NIGHT MONITOR (ONE-TIME)")
            print("=" * 70)
            if result.get("adjusted"):
                print(f"   ✅ Adjusted to {result['period']} settings")
            else:
                print(f"   ℹ️  Period unchanged: {result['period']}")
            print("=" * 70)
        else:
            monitor.run_continuous(duration=args.duration)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()