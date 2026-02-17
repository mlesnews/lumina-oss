#!/usr/bin/env python3
"""
JARVIS Migration Status Updates - Scheduled Reporting

Runs status updates at specified intervals (hourly or every 2-3 hours).
Can be run as a scheduled task or background service.

Usage:
    # Hourly updates
    python jarvis_migration_status_updates.py --interval 1

    # Every 2 hours
    python jarvis_migration_status_updates.py --interval 2

    # Every 3 hours
    python jarvis_migration_status_updates.py --interval 3

Tags: #MIGRATION #STATUS #SCHEDULED #JARVIS #NOTIFICATIONS @LUMINA
"""

import json
import sys
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from jarvis_migration_status_reporter import JARVISMigrationStatusReporter

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISMigrationUpdates")


def send_status_update(reporter: JARVISMigrationStatusReporter, interval_hours: float):
    """Send status update notification"""
    status = reporter.get_current_status()

    if "error" in status:
        logger.error(f"Error getting status: {status['error']}")
        return

    disk = status["disk_status"]
    progress = status["migration_progress"]
    eta = status["eta"]

    # Generate concise update message
    update_lines = []
    update_lines.append("📊 JARVIS Migration Status Update")
    update_lines.append(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    update_lines.append("")
    update_lines.append(f"Progress: {progress['progress_percent']:.1f}% ({progress['total_migrated_gb']:.2f} GB migrated)")
    update_lines.append(f"Remaining: {progress['remaining_gb']:.2f} GB")
    update_lines.append(f"Disk Usage: {disk['percent_used']:.1f}% (Target: {disk['target_percent']}%)")
    update_lines.append("")

    if eta["status"] == "complete":
        update_lines.append("✅ Migration Complete!")
    else:
        update_lines.append(f"⏱️  ETA: {eta['estimated_hours']:.1f} hours ({eta['estimated_days']:.2f} days)")
        if eta.get("estimated_completion"):
            completion = datetime.fromisoformat(eta["estimated_completion"])
            update_lines.append(f"   Completion: {completion.strftime('%Y-%m-%d %H:%M:%S')}")
        update_lines.append(f"   Transfer Rate: {eta['transfer_rate_gb_per_hour']:.2f} GB/hour")

    update_message = "\n".join(update_lines)

    # Print to console (can be redirected to log file or notification system)
    print("\n" + "=" * 80)
    print(update_message)
    print("=" * 80 + "\n")

    logger.info(f"Status update sent (interval: {interval_hours}h)")

    # Save to status update log
    update_log_file = reporter.data_dir / "status_updates.jsonl"
    update_entry = {
        "timestamp": datetime.now().isoformat(),
        "interval_hours": interval_hours,
        "status": status,
    }
    try:
        with open(update_log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(update_entry) + "\n")
    except Exception as e:
        logger.debug(f"Could not save update log: {e}")


def run_scheduled_updates(interval_hours: float = 1.0, max_updates: Optional[int] = None):
    """Run scheduled status updates"""
    reporter = JARVISMigrationStatusReporter(project_root)

    logger.info(f"Starting scheduled status updates (interval: {interval_hours} hours)")

    update_count = 0
    interval_seconds = interval_hours * 3600

    try:
        while True:
            # Send initial update
            send_status_update(reporter, interval_hours)
            update_count += 1

            if max_updates and update_count >= max_updates:
                logger.info(f"Reached max updates ({max_updates}), stopping")
                break

            # Wait for next interval
            logger.info(f"Waiting {interval_hours} hours until next update...")
            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        logger.info("Status updates stopped by user")
    except Exception as e:
        logger.error(f"Error in scheduled updates: {e}", exc_info=True)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="JARVIS Migration Status Updates - Scheduled Reporting"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Update interval in hours (default: 1.0, use 2.0 or 3.0 for less frequent)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Send one update and exit (for testing or manual runs)"
    )
    parser.add_argument(
        "--max-updates",
        type=int,
        help="Maximum number of updates to send (default: unlimited)"
    )

    args = parser.parse_args()

    reporter = JARVISMigrationStatusReporter(project_root)

    if args.once:
        # Send single update
        send_status_update(reporter, args.interval)
    else:
        # Run scheduled updates
        run_scheduled_updates(args.interval, args.max_updates)


if __name__ == "__main__":

    main()