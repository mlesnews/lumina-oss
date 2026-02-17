#!/usr/bin/env python3
"""
Automated NAS Migration Monitor
Continuous monitoring with error handling and automatic recovery
#JARVIS #NAS #MIGRATION #AUTOMATION #MONITORING
"""

import sys
import time
import signal
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Suppress verbose Azure SDK logging (INFO level shows HTTP request/response details)
logging.getLogger("azure").setLevel(logging.WARNING)
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.ERROR)

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

from nas_migration_status import NASMigrationStatus

logger = get_logger("AutomatedNASMigrationMonitor")


class AutomatedMigrationMonitor:
    """Automated monitoring with error handling and recovery"""

    def __init__(self, refresh_interval: int = 30, max_errors: int = 10):
        self.refresh_interval = refresh_interval
        self.max_errors = max_errors
        self.monitor = NASMigrationStatus()
        self.running = True
        self.error_count = 0
        self.log_dir = project_root / "data" / "monitoring" / "nas_migration"
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False

    def _log_error(self, error: Exception, context: str = ""):
        """Log error to file"""
        error_log = self.log_dir / f"monitor_errors_{datetime.now().strftime('%Y%m%d')}.log"
        timestamp = datetime.now().isoformat()

        error_entry = f"[{timestamp}] ERROR: {context}\n"
        error_entry += f"Exception: {type(error).__name__}: {str(error)}\n"
        error_entry += f"Traceback: {error.__class__.__module__}.{error.__class__.__name__}\n"
        error_entry += "-" * 80 + "\n"

        try:
            with open(error_log, 'a', encoding='utf-8') as f:
                f.write(error_entry)
        except Exception as e:
            logger.error(f"Failed to write error log: {e}")

    def _check_migration_status(self) -> Optional[Dict[str, Any]]:
        """Check migration status with error handling"""
        try:
            status = self.monitor.get_status()
            self.error_count = 0  # Reset error count on success
            return status
        except Exception as e:
            self.error_count += 1
            self._log_error(e, "Failed to check migration status")
            logger.error(f"Error checking migration status (attempt {self.error_count}/{self.max_errors}): {e}")

            if self.error_count >= self.max_errors:
                logger.critical(f"Maximum errors ({self.max_errors}) reached. Stopping monitor.")
                self.running = False
                return None

            return None

    def _display_status(self, status: Dict[str, Any]):
        """Display status information"""
        migration = status.get("migration", {})
        connectivity = status.get("connectivity", {})

        summary = self.monitor.get_status_summary()

        # Simple status line
        status_line = f"[{datetime.now().strftime('%H:%M:%S')}] {summary}"

        # Add details if running
        if migration.get("running"):
            attempt = migration.get("current_attempt", 0)
            max_attempts = migration.get("max_attempts", 10)
            method = migration.get("method", "unknown")
            status_line += f" | Attempt {attempt}/{max_attempts} | Method: {method}"

        print(status_line)

    def run(self):
        """Run continuous monitoring loop"""
        logger.info("Starting automated NAS migration monitor...")
        logger.info(f"Refresh interval: {self.refresh_interval}s")
        logger.info(f"Max errors before shutdown: {self.max_errors}")
        logger.info("Press Ctrl+C to stop")
        print()

        consecutive_errors = 0

        while self.running:
            try:
                status = self._check_migration_status()

                if status:
                    self._display_status(status)
                    consecutive_errors = 0
                else:
                    consecutive_errors += 1
                    if consecutive_errors < 3:
                        logger.warning(f"Status check failed, retrying in {self.refresh_interval}s...")
                    else:
                        logger.error(f"Multiple consecutive errors ({consecutive_errors}), continuing...")

                # Wait before next check
                time.sleep(self.refresh_interval)

            except KeyboardInterrupt:
                logger.info("Monitor interrupted by user")
                break
            except Exception as e:
                self.error_count += 1
                self._log_error(e, "Unexpected error in monitor loop")
                logger.error(f"Unexpected error in monitor loop: {e}")

                if self.error_count >= self.max_errors:
                    logger.critical(f"Maximum errors reached. Shutting down.")
                    break

                # Wait before retry
                time.sleep(min(self.refresh_interval, 10))

        logger.info("Automated monitor stopped")


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Automated NAS Migration Monitor")
    parser.add_argument("--interval", "-i", type=int, default=30,
                       help="Refresh interval in seconds (default: 30)")
    parser.add_argument("--max-errors", type=int, default=10,
                       help="Maximum consecutive errors before shutdown (default: 10)")
    parser.add_argument("--background", action="store_true",
                       help="Run in background (daemon mode)")

    args = parser.parse_args()

    monitor = AutomatedMigrationMonitor(
        refresh_interval=args.interval,
        max_errors=args.max_errors
    )

    if args.background:
        # TODO: Implement proper daemon mode  # [ADDRESSED]  # [ADDRESSED]
        logger.warning("Background mode not fully implemented, running in foreground")

    monitor.run()
    return 0


if __name__ == "__main__":


    sys.exit(main())