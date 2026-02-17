"""
HVAC @SYPHON Monitor Daemon
Continuous monitoring daemon for HVAC bid emails from other contractors.
Runs as a background service, checking for new emails periodically.

#JARVIS #LUMINA #SYPHON #HVAC #DAEMON #MONITORING
"""

import json
import time
import signal
import sys
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("HVACSyphonMonitorDaemon")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("HVACSyphonMonitorDaemon")

from hvac_syphon_monitor import HVACSyphonMonitor


class HVACSyphonMonitorDaemon:
    """Daemon for continuous HVAC email monitoring."""

    def __init__(self, project_root: Path, check_interval_minutes: int = 15):
        """
        Initialize monitoring daemon.

        Args:
            project_root: Project root directory
            check_interval_minutes: Minutes between checks
        """
        self.project_root = Path(project_root)
        self.check_interval = check_interval_minutes * 60  # Convert to seconds
        self.monitor = HVACSyphonMonitor(project_root)
        self.running = False

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"\nReceived signal {signum}, shutting down gracefully...")
        self.running = False

    def run(self):
        """Run the monitoring daemon."""
        self.running = True

        logger.info("="*80)
        logger.info("HVAC @SYPHON MONITOR DAEMON STARTED")
        logger.info("="*80)
        logger.info(f"Monitoring contractors: Carl-King| Griffet Energy Services + Third Contractor")
        logger.info(f"Excluding: Brian Fletcher (already processed)")
        logger.info(f"Check interval: {self.check_interval // 60} minutes")
        logger.info(f"Daemon PID: {os.getpid()}")
        logger.info("\nMonitoring active. Press Ctrl+C to stop.\n")

        last_check = datetime.now()
        check_count = 0

        try:
            while self.running:
                current_time = datetime.now()
                time_since_last = (current_time - last_check).total_seconds()

                if time_since_last >= self.check_interval:
                    check_count += 1
                    logger.info(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] "
                              f"Check #{check_count} - Searching for new HVAC emails...")

                    try:
                        # @SYPHON new emails (last 24 hours)
                        new_data = self.monitor.syphon_hvac_emails(days_back=1)

                        if new_data:
                            logger.info(f"✓ Found {len(new_data)} new email(s) with HVAC intelligence")

                            # Save updated bids
                            self.monitor.bid_comparator.save_bids()

                            # Generate report if we have multiple bids
                            if len(self.monitor.bid_comparator.bids) >= 2:
                                report_path = self.monitor.bid_comparator.generate_report()
                                logger.info(f"✓ Updated comparison report: {report_path}")

                                # Print summary
                                self.monitor.bid_comparator.print_summary()
                        else:
                            logger.info("  No new emails found")

                    except Exception as e:
                        logger.error(f"Error during check: {e}", exc_info=True)

                    last_check = current_time

                    # Save status
                    self._save_status(check_count, last_check)

                # Sleep for 1 minute before checking again
                time.sleep(60)

        except KeyboardInterrupt:
            logger.info("\n\nDaemon stopped by user")
        finally:
            self._save_status(check_count, datetime.now(), stopped=True)
            logger.info("Daemon shutdown complete")

    def _save_status(self, check_count: int, last_check: datetime, stopped: bool = False) -> None:
        try:
            """Save daemon status."""
            status = {
                "daemon_status": "stopped" if stopped else "running",
                "check_count": check_count,
                "last_check": last_check.isoformat(),
                "check_interval_minutes": self.check_interval // 60,
                "contractors_monitored": self.monitor.contractors_to_monitor,
                "total_bids": len(self.monitor.bid_comparator.bids),
                "updated_at": datetime.now().isoformat()
            }

            status_file = self.monitor.data_dir / "monitoring_daemon_status.json"
            with open(status_file, 'w') as f:
                json.dump(status, f, indent=2)

            if not stopped:
                logger.debug(f"Status saved: {check_count} checks, last: {last_check.strftime('%H:%M:%S')}")


        except Exception as e:
            self.logger.error(f"Error in _save_status: {e}", exc_info=True)
            raise
def main():
    """Main function."""
    import argparse
    import os

    parser = argparse.ArgumentParser(description="HVAC @SYPHON Monitor Daemon")
    parser.add_argument("--project-root", type=Path,
                       default=Path(__file__).parent.parent.parent,
                       help="Project root directory")
    parser.add_argument("--check-interval", type=int, default=15,
                       help="Check interval in minutes (default: 15)")
    parser.add_argument("--daemon", action="store_true",
                       help="Run as background daemon")
    parser.add_argument("--pid-file", type=Path,
                       help="PID file for daemon")

    args = parser.parse_args()

    daemon = HVACSyphonMonitorDaemon(args.project_root, args.check_interval)

    if args.daemon:
        # Run as background daemon
        if args.pid_file:
            with open(args.pid_file, 'w') as f:
                f.write(str(os.getpid()))

        try:
            daemon.run()
        finally:
            if args.pid_file and args.pid_file.exists():
                args.pid_file.unlink()
    else:
        # Run in foreground
        daemon.run()


if __name__ == "__main__":
    import os


    main()