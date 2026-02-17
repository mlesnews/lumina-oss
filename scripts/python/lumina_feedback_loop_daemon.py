#!/usr/bin/env python3
"""
Lumina Feedback Loop Daemon - Headless Terminal-less Daemon with Logging

Runs Lumina Data Mining Feedback Loop as a headless daemon for NAS cron scheduling.
No terminal/TTY required. All output goes to log files.

@LUMINA @FEEDBACK_LOOP @DAEMON @NAS @CRON
"""

import sys
import os
import signal
import time
import logging
import logging.handlers
from pathlib import Path
from typing import Optional
from datetime import datetime

# Disable stdout/stderr if not a TTY (headless mode)
if not sys.stdout.isatty():
    sys.stdout = open(os.devnull, 'w')
if not sys.stderr.isatty():
    sys.stderr = open(os.devnull, 'w')

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

# Project root
project_root = script_dir.parent.parent

# Setup logging BEFORE any imports that might log
log_dir = project_root / "data" / "logs" / "lumina_feedback_loop"
log_dir.mkdir(parents=True, exist_ok=True)

log_file = log_dir / f"lumina_feedback_loop_{datetime.now().strftime('%Y%m%d')}.log"
error_log_file = log_dir / f"lumina_feedback_loop_errors_{datetime.now().strftime('%Y%m%d')}.log"

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Remove existing handlers
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# File handler with rotation
file_handler = logging.handlers.RotatingFileHandler(
    log_file,
    maxBytes=10*1024*1024,  # 10MB
    backupCount=10,
    encoding='utf-8'
)
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(file_formatter)

# Error file handler
error_handler = logging.handlers.RotatingFileHandler(
    error_log_file,
    maxBytes=10*1024*1024,
    backupCount=10,
    encoding='utf-8'
)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(file_formatter)

# Add handlers
root_logger.addHandler(file_handler)
root_logger.addHandler(error_handler)

logger = logging.getLogger("LuminaFeedbackLoopDaemon")

try:
    from lumina_data_mining_feedback_loop import LuminaFeedbackLoop
except ImportError as e:
    logger.error(f"Failed to import LuminaFeedbackLoop: {e}", exc_info=True)
    sys.exit(1)


class LuminaFeedbackLoopDaemon:
    """Headless daemon for Lumina Feedback Loop"""

    def __init__(self, interval: int = 3600, project_root: Optional[Path] = None):
        """
        Initialize daemon

        Args:
            interval: Cycle interval in seconds (default: 3600 = 1 hour)
            project_root: Project root directory
        """
        self.interval = interval
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.running = False
        self.feedback_loop: Optional[LuminaFeedbackLoop] = None

        # PID file
        pid_dir = Path("/tmp") if os.name != 'nt' else Path(os.environ.get('TEMP', 'C:\\temp'))
        pid_dir.mkdir(exist_ok=True)
        self.pid_file = pid_dir / "lumina_feedback_loop_daemon.pid"

        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        if hasattr(signal, 'SIGHUP'):
            signal.signal(signal.SIGHUP, self._signal_handler)

        logger.info("="*80)
        logger.info("Lumina Feedback Loop Daemon initialized")
        logger.info(f"   Interval: {interval}s ({interval/60:.1f} minutes)")
        logger.info(f"   Project root: {self.project_root}")
        logger.info(f"   Log directory: {log_dir}")
        logger.info("="*80)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        signal_name = signal.Signals(signum).name
        logger.info(f"Received {signal_name} signal - shutting down gracefully...")
        self.stop()

    def _write_pid(self):
        """Write PID file"""
        try:
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))
            logger.info(f"PID file written: {self.pid_file}")
        except Exception as e:
            logger.error(f"Failed to write PID file: {e}")

    def _remove_pid(self):
        """Remove PID file"""
        try:
            if self.pid_file.exists():
                self.pid_file.unlink()
                logger.info("PID file removed")
        except Exception as e:
            logger.warning(f"Failed to remove PID file: {e}")

    def start(self):
        """Start the daemon"""
        logger.info("Starting Lumina Feedback Loop daemon...")

        # Check if already running
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    old_pid = int(f.read().strip())
                # Check if process exists
                os.kill(old_pid, 0)
                logger.warning(f"Daemon already running with PID {old_pid}")
                return False
            except (OSError, ValueError):
                # Stale PID file
                logger.info("Removing stale PID file")
                self._remove_pid()

        # Write PID
        self._write_pid()

        # Initialize Feedback Loop
        try:
            logger.info("Initializing Lumina Feedback Loop...")
            self.feedback_loop = LuminaFeedbackLoop(self.project_root)
            logger.info("✅ Lumina Feedback Loop initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Lumina Feedback Loop: {e}", exc_info=True)
            self._remove_pid()
            return False

        # Start running
        self.running = True
        self.run()

        return True

    def stop(self):
        """Stop the daemon"""
        logger.info("Stopping Lumina Feedback Loop daemon...")
        self.running = False
        self._remove_pid()
        logger.info("Daemon stopped")

    def run(self):
        """Run the daemon loop"""
        logger.info("="*80)
        logger.info("🔄 LUMINA FEEDBACK LOOP DAEMON RUNNING")
        logger.info("="*80)

        cycle_count = 0

        while self.running:
            try:
                cycle_count += 1
                logger.info(f"\n{'='*80}")
                logger.info(f"Starting cycle {cycle_count} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"{'='*80}\n")

                # Run cycle
                if self.feedback_loop:
                    try:
                        report = self.feedback_loop.run_feedback_cycle()
                        logger.info(f"✅ Cycle {cycle_count} completed successfully")
                        logger.info(f"   Cycle ID: {report.get('cycle_id', 'N/A')}")
                        logger.info(f"   OTS Analysis: {report.get('ots_analysis', {}).get('total_ots', 0)} entries")
                        logger.info(f"   Recommendations: {len(report.get('recommendations', []))}")
                    except Exception as e:
                        logger.error(f"❌ Error in cycle {cycle_count}: {e}", exc_info=True)

                # Sleep until next cycle
                if self.running:
                    next_cycle = datetime.now().timestamp() + self.interval
                    next_cycle_str = datetime.fromtimestamp(next_cycle).strftime('%Y-%m-%d %H:%M:%S')
                    logger.info(f"\n💤 Sleeping for {self.interval}s until next cycle ({next_cycle_str})")

                    # Sleep in smaller increments to allow quick shutdown
                    slept = 0
                    while self.running and slept < self.interval:
                        time.sleep(min(60, self.interval - slept))  # Sleep in 60s chunks
                        slept += min(60, self.interval - slept)

            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error in daemon loop: {e}", exc_info=True)
                if self.running:
                    logger.info(f"Sleeping 60s before retry...")
                    time.sleep(60)

        logger.info("="*80)
        logger.info("Daemon loop exited")
        logger.info("="*80)


def run_single_cycle():
    """Run a single cycle (for cron one-shot execution)"""
    logger.info("="*80)
    logger.info("Running single Lumina Feedback Loop cycle")
    logger.info("="*80)

    try:
        feedback_loop = LuminaFeedbackLoop(project_root)
        report = feedback_loop.run_feedback_cycle()

        logger.info("="*80)
        logger.info("✅ Single cycle completed")
        logger.info(f"   Cycle ID: {report.get('cycle_id', 'N/A')}")
        logger.info(f"   OTS Analysis: {report.get('ots_analysis', {}).get('total_ots', 0)} entries")
        logger.info(f"   Recommendations: {len(report.get('recommendations', []))}")
        logger.info("="*80)

        return 0
    except Exception as e:
        logger.error(f"❌ Single cycle failed: {e}", exc_info=True)
        return 1


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Lumina Feedback Loop Daemon",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run single cycle (for cron)
  python lumina_feedback_loop_daemon.py --cycle

  # Run as daemon (continuous)
  python lumina_feedback_loop_daemon.py --daemon --interval 3600

  # Stop daemon
  python lumina_feedback_loop_daemon.py --stop
        """
    )

    parser.add_argument("--cycle", action="store_true",
                       help="Run single cycle (for cron one-shot)")
    parser.add_argument("--daemon", action="store_true",
                       help="Run as continuous daemon")
    parser.add_argument("--stop", action="store_true",
                       help="Stop running daemon")
    parser.add_argument("--interval", type=int, default=3600,
                       help="Cycle interval in seconds (default: 3600 = 1 hour)")
    parser.add_argument("--project-root", type=Path,
                       help="Project root directory (auto-detected if not provided)")

    args = parser.parse_args()

    if args.cycle:
        # Single cycle mode
        sys.exit(run_single_cycle())

    elif args.stop:
        # Stop daemon
        pid_file = Path("/tmp/lumina_feedback_loop_daemon.pid") if os.name != 'nt' else Path(os.environ.get('TEMP', 'C:\\temp')) / "lumina_feedback_loop_daemon.pid"

        if not pid_file.exists():
            logger.error("PID file not found - daemon may not be running")
            sys.exit(1)

        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())

            logger.info(f"Sending SIGTERM to daemon (PID: {pid})...")
            os.kill(pid, signal.SIGTERM)

            # Wait for graceful shutdown
            for _ in range(30):
                time.sleep(1)
                try:
                    os.kill(pid, 0)
                except OSError:
                    logger.info("✅ Daemon stopped")
                    sys.exit(0)

            # Force kill if still running
            logger.warning("Daemon did not stop gracefully, force killing...")
            os.kill(pid, signal.SIGKILL)
            logger.info("✅ Daemon force killed")

        except Exception as e:
            logger.error(f"Failed to stop daemon: {e}", exc_info=True)
            sys.exit(1)

    elif args.daemon:
        # Daemon mode
        daemon = LuminaFeedbackLoopDaemon(
            interval=args.interval,
            project_root=args.project_root
        )
        daemon.start()

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":


    main()