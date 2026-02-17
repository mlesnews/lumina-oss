#!/usr/bin/env python3
"""
Neo Browser Default Monitor

Monitors and auto-fixes if Neo browser is not the default browser.
Ensures Neo stays as default.

Tags: #NEO_BROWSER #DEFAULT_BROWSER #MONITORING #AUTO_FIX @JARVIS @LUMINA
"""

import sys
import time
import schedule
from pathlib import Path
from typing import Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("NeoBrowserMonitor")


def monitor_and_fix():
    """Monitor Neo browser default status and fix if needed"""
    try:
        from set_neo_default_browser import NeoDefaultBrowserSetter

        setter = NeoDefaultBrowserSetter()
        status = setter.get_status()

        if not status['is_neo_default']:
            logger.warning("   ⚠️  Neo browser is NOT the default!")
            logger.info("   🔧 Attempting to set Neo as default...")

            # Try to set as default
            success = setter.set_neo_as_default()

            if success:
                logger.info("   ✅ Neo browser set as default")
            else:
                logger.warning("   ⚠️  Could not auto-set - manual intervention may be required")
        else:
            logger.info("   ✅ Neo browser is the default browser")

    except Exception as e:
        logger.error(f"   ❌ Monitoring error: {e}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Neo Browser Default Monitor")
    parser.add_argument("--once", action="store_true", help="Check once and exit")
    parser.add_argument("--schedule", choices=["minute", "5minutes", "hourly"],
                       default="5minutes", help="Monitoring schedule")

    args = parser.parse_args()

    if args.once:
        monitor_and_fix()
        return

    # Set up schedule
    if args.schedule == "minute":
        schedule.every().minute.do(monitor_and_fix)
        logger.info("   ⏰ Scheduled: Every minute")
    elif args.schedule == "hourly":
        schedule.every().hour.do(monitor_and_fix)
        logger.info("   ⏰ Scheduled: Every hour")
    else:  # 5minutes
        schedule.every(5).minutes.do(monitor_and_fix)
        logger.info("   ⏰ Scheduled: Every 5 minutes")

    logger.info("=" * 80)
    logger.info("🔄 NEO BROWSER DEFAULT MONITOR")
    logger.info("=" * 80)
    logger.info("   Monitoring Neo browser default status...")
    logger.info("   Press Ctrl+C to stop")
    logger.info("=" * 80)

    # Run initial check
    monitor_and_fix()

    # Run scheduled monitoring
    try:
        while True:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds
    except KeyboardInterrupt:
        logger.info("\n👋 Monitoring stopped")


if __name__ == "__main__":


    main()