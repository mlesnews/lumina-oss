#!/usr/bin/env python3
"""
Dropbox Optimized Processor Daemon
<COMPANY_NAME> LLC

Daemon version of Dropbox optimized processor for NAS Kron scheduler:
- Runs continuously as background daemon
- Processes Dropbox files with caching
- Resource-aware, utilization-balanced processing
- Managed by NAS Kron scheduler

@JARVIS @MARVIN @SYPHON
"""

import sys
import os
import time
import signal
from pathlib import Path
from typing import Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from universal_logging_wrapper import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

from dropbox_optimized_processor import DropboxOptimizedProcessor, ProcessingConfig

logger = get_logger("DropboxOptimizedDaemon")


class DropboxOptimizedDaemon:
    """Daemon for Dropbox optimized processing"""

    def __init__(self, dropbox_path: Path, config: Optional[ProcessingConfig] = None, 
                 interval_minutes: int = 60, pid_file: Optional[Path] = None):
        """Initialize daemon"""
        self.dropbox_path = dropbox_path
        self.config = config or ProcessingConfig()
        self.interval_minutes = interval_minutes
        self.pid_file = pid_file or Path("/tmp/dropbox_optimized_daemon.pid")

        self.running = False
        self.processor = None
        self.logger = logger

        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        self.logger.info("✅ Dropbox Optimized Daemon initialized")
        self.logger.info(f"   Dropbox path: {self.dropbox_path}")
        self.logger.info(f"   Interval: {self.interval_minutes} minutes")
        self.logger.info(f"   PID file: {self.pid_file}")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False

    def _write_pid(self):
        """Write PID file"""
        try:
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))
            self.logger.info(f"PID written to {self.pid_file}")
        except Exception as e:
            self.logger.error(f"Failed to write PID file: {e}")

    def _remove_pid(self):
        """Remove PID file"""
        try:
            if self.pid_file.exists():
                self.pid_file.unlink()
                self.logger.info(f"PID file removed: {self.pid_file}")
        except Exception as e:
            self.logger.error(f"Failed to remove PID file: {e}")

    def _is_running(self) -> bool:
        """Check if daemon is already running"""
        if not self.pid_file.exists():
            return False

        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())

            # Check if process exists
            os.kill(pid, 0)  # Signal 0 just checks if process exists
            return True
        except (ValueError, OSError):
            # PID file exists but process doesn't
            self._remove_pid()
            return False

    def start(self):
        """Start daemon"""
        if self._is_running():
            self.logger.error(f"Daemon already running (PID file: {self.pid_file})")
            return False

        self.logger.info("🚀 Starting Dropbox Optimized Daemon...")

        # Write PID
        self._write_pid()

        # Initialize processor
        self.processor = DropboxOptimizedProcessor(self.dropbox_path, self.config)

        # Start main loop
        self.running = True
        self._run()

        return True

    def stop(self):
        """Stop daemon"""
        if not self.pid_file.exists():
            self.logger.warning("PID file not found - daemon may not be running")
            return False

        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())

            self.logger.info(f"Stopping daemon (PID: {pid})...")
            os.kill(pid, signal.SIGTERM)

            # Wait for process to stop
            time.sleep(2)

            # Remove PID file
            self._remove_pid()

            self.logger.info("✅ Daemon stopped")
            return True
        except (ValueError, OSError) as e:
            self.logger.error(f"Error stopping daemon: {e}")
            return False

    def _run(self):
        """Main daemon loop"""
        self.logger.info("🔄 Daemon running...")

        iteration = 0

        while self.running:
            iteration += 1
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Iteration {iteration} - {time.strftime('%Y-%m-%d %H:%M:%S')}")
            self.logger.info(f"{'='*60}")

            try:
                # Process Dropbox files (limit to reasonable batch for daemon)
                results = list(self.processor.process_dropbox_optimized(max_files=10000))

                # Summary
                total = len(results)
                cached = sum(1 for r in results if r.get("cached"))
                processed = sum(1 for r in results if r.get("processed"))
                errors = sum(1 for r in results if r.get("error"))

                self.logger.info(f"\n📊 Iteration {iteration} Summary:")
                self.logger.info(f"   Total files: {total}")
                self.logger.info(f"   Cached (skipped): {cached} ({cached/total*100:.1f}% if total > 0 else 0)")
                self.logger.info(f"   Processed: {processed} ({processed/total*100:.1f}% if total > 0 else 0)")
                self.logger.info(f"   Errors: {errors}")

                if cached > 0:
                    self.logger.info(f"   ✅ Caching saved {cached} re-processes!")

            except Exception as e:
                self.logger.error(f"Error in processing iteration: {e}", exc_info=True)

            # Wait for next interval (unless stopping)
            if self.running:
                self.logger.info(f"⏰ Waiting {self.interval_minutes} minutes until next run...")
                for _ in range(self.interval_minutes * 60):
                    if not self.running:
                        break
                    time.sleep(1)

        # Cleanup
        self._remove_pid()
        self.logger.info("👋 Daemon stopped")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Dropbox Optimized Processor Daemon")
    parser.add_argument("action", choices=["start", "stop", "status"], help="Daemon action")
    parser.add_argument("--path", type=str, default="C:\\Users\\mlesn\\Dropbox", help="Dropbox path")
    parser.add_argument("--interval", type=int, default=60, help="Interval in minutes (default: 60)")
    parser.add_argument("--pid-file", type=str, help="PID file path")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch size")
    parser.add_argument("--max-workers", type=int, default=4, help="Max workers")
    parser.add_argument("--no-cache", action="store_true", help="Disable caching")
    parser.add_argument("--no-energy-save", action="store_true", help="Disable energy save")

    args = parser.parse_args()

    config = ProcessingConfig(
        batch_size=args.batch_size,
        max_workers=args.max_workers,
        cache_enabled=not args.no_cache,
        energy_save_mode=not args.no_energy_save
    )

    pid_file = Path(args.pid_file) if args.pid_file else None
    daemon = DropboxOptimizedDaemon(
        dropbox_path=Path(args.path),
        config=config,
        interval_minutes=args.interval,
        pid_file=pid_file
    )

    if args.action == "start":
        daemon.start()
    elif args.action == "stop":
        daemon.stop()
    elif args.action == "status":
        if daemon._is_running():
            print("✅ Daemon is running")
        else:
            print("❌ Daemon is not running")

