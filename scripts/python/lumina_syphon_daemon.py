"""
LUMINA @SYPHON Daemon
Continuous @SYPHON extraction daemon running in priority order.

Priority:
1. Filesystems (FIRST PRIORITY)
2. @SOURCES @SYPHON @BAU: Email + Financial Accounts

#JARVIS #LUMINA #SYPHON #DAEMON #<COMPANY>-FINANCIAL-SERVICES-LLC
"""

import sys
import time
import signal
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("LuminaSyphonDaemon")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("LuminaSyphonDaemon")

from scripts.python.lumina_comprehensive_syphon_system import LuminaComprehensiveSyphonSystem
from scripts.python.integrate_hook_trace import hook_trace, OperationType, TraceLevel


class LuminaSyphonDaemon:
    """Continuous @SYPHON extraction daemon."""

    def __init__(self, project_root: Path, interval_hours: int = 24):
        """
        Initialize @SYPHON daemon.

        Args:
            project_root: Project root directory
            interval_hours: Hours between @SYPHON runs
        """
        self.project_root = Path(project_root)
        self.interval = interval_hours * 3600  # Convert to seconds
        self.syphon_system = LuminaComprehensiveSyphonSystem(project_root)
        self.running = False

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"\nReceived signal {signum}, shutting down gracefully...")
        self.running = False

    def run(self):
        """Run the @SYPHON daemon."""
        self.running = True

        logger.info("="*80)
        logger.info("LUMINA @SYPHON DAEMON STARTED")
        logger.info("="*80)
        logger.info("Priority Order:")
        logger.info("  1. Filesystems (FIRST PRIORITY)")
        logger.info("  2. @SOURCES @SYPHON @BAU: Email + Financial Accounts")
        logger.info(f"Company: #<COMPANY>-FINANCIAL-SERVICES-LLC")
        logger.info(f"Interval: {self.interval // 3600} hours")
        logger.info(f"Daemon PID: {os.getpid()}")
        logger.info("\n@SYPHON daemon active. Press Ctrl+C to stop.\n")

        last_run = datetime.now()
        run_count = 0

        try:
            while self.running:
                current_time = datetime.now()
                time_since_last = (current_time - last_run).total_seconds()

                if time_since_last >= self.interval:
                    run_count += 1
                    logger.info(f"[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] "
                              f"@SYPHON Run #{run_count} - Starting comprehensive extraction...")

                    try:
                        # Run comprehensive @SYPHON (priority order maintained)
                        results = self.syphon_system.syphon_all(days_back=30)

                        logger.info(f"✅ @SYPHON Run #{run_count} complete")
                        logger.info(f"   Filesystems: {results.get('filesystems', {}).get('total_sources', 0)} sources")
                        logger.info(f"   Email: {results.get('email', {}).get('total_emails', 0)} emails")
                        logger.info(f"   Financial: {results.get('financial', {}).get('total_accounts', 0)} accounts")

                        hook_trace.trace(
                            operation_type=OperationType.SYPHON,
                            operation_name="syphon_daemon_run",
                            level=TraceLevel.INFO,
                            message=f"@SYPHON daemon run #{run_count} complete",
                            success=True,
                            metadata={
                                "run_count": run_count,
                                "filesystem_sources": results.get('filesystems', {}).get('total_sources', 0),
                                "email_count": results.get('email', {}).get('total_emails', 0),
                                "financial_accounts": results.get('financial', {}).get('total_accounts', 0)
                            }
                        )

                    except Exception as e:
                        logger.error(f"❌ @SYPHON Run #{run_count} failed: {e}", exc_info=True)
                        hook_trace.trace(
                            operation_type=OperationType.SYPHON,
                            operation_name="syphon_daemon_run",
                            level=TraceLevel.ERROR,
                            message=f"@SYPHON daemon run #{run_count} failed",
                            error=str(e)
                        )

                    last_run = current_time

                    # Save status
                    self._save_status(run_count, last_run)

                # Sleep for 1 minute before checking again
                time.sleep(60)

        except KeyboardInterrupt:
            logger.info("\n\n@SYPHON daemon stopped by user")
        finally:
            self._save_status(run_count, datetime.now(), stopped=True)
            hook_trace.flush_buffers()
            logger.info("@SYPHON daemon shutdown complete")

    def _save_status(self, run_count: int, last_run: datetime, stopped: bool = False) -> None:
        try:
            """Save daemon status."""
            import json

            status = {
                "daemon_status": "stopped" if stopped else "running",
                "run_count": run_count,
                "last_run": last_run.isoformat(),
                "interval_hours": self.interval // 3600,
                "company": "#<COMPANY>-FINANCIAL-SERVICES-LLC",
                "priority_order": [
                    "1. Filesystems (FIRST PRIORITY)",
                    "2. @SOURCES @SYPHON @BAU: Email + Financial Accounts"
                ],
                "updated_at": datetime.now().isoformat()
            }

            status_file = self.project_root / "data" / "lumina_syphon" / "daemon_status.json"
            status_file.parent.mkdir(parents=True, exist_ok=True)

            with open(status_file, 'w') as f:
                json.dump(status, f, indent=2)


        except Exception as e:
            self.logger.error(f"Error in _save_status: {e}", exc_info=True)
            raise
def main():
    """Main function."""
    import argparse
    import os

    parser = argparse.ArgumentParser(description="LUMINA @SYPHON Daemon")
    parser.add_argument("--project-root", type=Path,
                       default=Path(__file__).parent.parent.parent,
                       help="Project root directory")
    parser.add_argument("--interval", type=int, default=24,
                       help="Interval between @SYPHON runs in hours (default: 24)")
    parser.add_argument("--daemon", action="store_true",
                       help="Run as background daemon")
    parser.add_argument("--pid-file", type=Path,
                       help="PID file for daemon")
    parser.add_argument("--run-once", action="store_true",
                       help="Run @SYPHON once and exit")

    args = parser.parse_args()

    daemon = LuminaSyphonDaemon(args.project_root, args.interval)

    if args.run_once:
        # Run once and exit
        logger.info("Running @SYPHON once...")
        results = daemon.syphon_system.syphon_all(days_back=30)
        logger.info("✅ @SYPHON complete")
        logger.info(f"   Filesystems: {results.get('filesystems', {}).get('total_sources', 0)} sources")
        logger.info(f"   Email: {results.get('email', {}).get('total_emails', 0)} emails")
        logger.info(f"   Financial: {results.get('financial', {}).get('total_accounts', 0)} accounts")
        return

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