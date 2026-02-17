#!/usr/bin/env python3
"""
Daemon Template - Headless Terminal-less Daemon with Full Logging

Template for creating headless daemons suitable for NAS cron scheduling.
All output goes to log files using Python's logging module.

Usage:
    Inherit from BaseDaemon and implement the _run_cycle() method.

@DAEMON @NAS @CRON @LOGGING
"""

import sys
import os
import signal
import time
import logging
import logging.handlers
from pathlib import Path
from typing import Optional, Callable
from datetime import datetime
from abc import ABC, abstractmethod


class BaseDaemon(ABC):
    """
    Base class for headless daemons with full logging support.

    All daemons inherit from this and implement _run_cycle().
    """

    def __init__(self, daemon_name: str, log_subdirectory: str, 
                 project_root: Optional[Path] = None,
                 interval: int = 3600):
        """
        Initialize daemon

        Args:
            daemon_name: Name of the daemon (for logging and identification)
            log_subdirectory: Subdirectory under data/logs/ for log files
            project_root: Project root directory (auto-detected if None)
            interval: Cycle interval in seconds (default: 3600 = 1 hour)
        """
        self.daemon_name = daemon_name
        self.log_subdirectory = log_subdirectory
        self.interval = interval
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.running = False

        # Setup logging BEFORE any other operations
        self._setup_logging()

        self.logger = logging.getLogger(self.daemon_name)
        self.logger.info(f"Initializing {self.daemon_name} daemon")

        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _setup_logging(self):
        try:
            """Setup comprehensive logging with rotation"""
            # Disable stdout/stderr if not a TTY (headless mode)
            if not sys.stdout.isatty():
                sys.stdout = open(os.devnull, 'w')
            if not sys.stderr.isatty():
                sys.stderr = open(os.devnull, 'w')

            # Log directory
            log_dir = self.project_root / "data" / "logs" / self.log_subdirectory
            log_dir.mkdir(parents=True, exist_ok=True)

            # Log files
            log_file = log_dir / f"{self.log_subdirectory}_{datetime.now().strftime('%Y%m%d')}.log"
            error_log_file = log_dir / f"{self.log_subdirectory}_errors_{datetime.now().strftime('%Y%m%d')}.log"

            # Configure root logger
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.INFO)

            # Remove existing handlers
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)

            # File handler with rotation (10MB, keep 10 backups)
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=10,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.INFO)
            file_formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)

            # Error file handler (separate file for errors only)
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

        except Exception as e:
            self.logger.error(f"Error in _setup_logging: {e}", exc_info=True)
            raise
    def _signal_handler(self, signum, frame):
        """Handle termination signals"""
        signal_name = signal.Signals(signum).name
        self.logger.info(f"Received {signal_name} signal, shutting down gracefully...")
        self.running = False

    @abstractmethod
    def _run_cycle(self) -> bool:
        """
        Run one cycle of the daemon's work.

        Must be implemented by subclasses.

        Returns:
            True if cycle completed successfully, False otherwise
        """
        pass

    def _initialize(self):
        """
        Initialize daemon resources.

        Override in subclasses if needed.
        """
        pass

    def _cleanup(self):
        """
        Cleanup daemon resources.

        Override in subclasses if needed.
        """
        pass

    def run(self):
        """Run daemon main loop"""
        self.logger.info(f"Starting {self.daemon_name} daemon (interval: {self.interval}s)")

        try:
            self._initialize()
            self.running = True

            while self.running:
                try:
                    cycle_start = time.time()
                    self.logger.info(f"Starting cycle at {datetime.now().isoformat()}")

                    success = self._run_cycle()

                    cycle_duration = time.time() - cycle_start
                    if success:
                        self.logger.info(f"Cycle completed successfully in {cycle_duration:.2f}s")
                    else:
                        self.logger.warning(f"Cycle completed with issues in {cycle_duration:.2f}s")

                except Exception as e:
                    self.logger.error(f"Error in cycle: {e}", exc_info=True)
                    # Continue running even if cycle fails

                # Sleep until next cycle (or until interrupted)
                if self.running:
                    self.logger.debug(f"Sleeping for {self.interval}s until next cycle")
                    time.sleep(self.interval)

        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"Fatal error in daemon: {e}", exc_info=True)
        finally:
            self.logger.info(f"Shutting down {self.daemon_name} daemon")
            self._cleanup()
            self.logger.info("Daemon shutdown complete")


def create_daemon_script(target_module: str, target_class: str, daemon_name: str,
                        log_subdirectory: str, interval: int = 3600):
    """
    Create a daemon wrapper script for a target class.

    Args:
        target_module: Module name (e.g., 'master_feedback_loop_autonomous_executor')
        target_class: Class name (e.g., 'MasterFeedbackLoopAutonomousExecutor')
        daemon_name: Daemon name for logging
        log_subdirectory: Log subdirectory name
        interval: Cycle interval in seconds
    """
    script_content = f'''#!/usr/bin/env python3
"""
{daemon_name} Daemon - Headless Terminal-less Daemon with Logging

Runs {target_class} as a headless daemon for NAS cron scheduling.
No terminal/TTY required. All output goes to log files.

@DAEMON @NAS @CRON @LOGGING
"""

import sys
import argparse
from pathlib import Path
from daemon_template import BaseDaemon

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from {target_module} import {target_class}
except ImportError as e:
    import logging
    logging.error(f"Failed to import {target_class}: {{e}}", exc_info=True)
    sys.exit(1)


class {target_class}Daemon(BaseDaemon):
    """Headless daemon wrapper for {target_class}"""

    def __init__(self, interval: int = {interval}, project_root: Optional[Path] = None):
        super().__init__(
            daemon_name="{daemon_name}",
            log_subdirectory="{log_subdirectory}",
            project_root=project_root,
            interval=interval
        )
        self.{target_class.lower()}: Optional[{target_class}] = None

    def _initialize(self):
        """Initialize the target class instance"""
        self.logger.info(f"Initializing {target_class}...")
        try:
            self.{target_class.lower()} = {target_class}(project_root=self.project_root)
            self.logger.info(f"{target_class} initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize {target_class}: {{e}}", exc_info=True)
            raise

    def _run_cycle(self) -> bool:
        """Run one cycle of the daemon's work"""
        if not self.{target_class.lower()}:
            self.logger.error("{target_class} not initialized")
            return False

        try:
            # Call the main execution method
            # Adjust method name based on actual class interface
            if hasattr(self.{target_class.lower()}, 'execute'):
                result = self.{target_class.lower()}.execute()
            elif hasattr(self.{target_class.lower()}, 'run_cycle'):
                result = self.{target_class.lower()}.run_cycle()
            elif hasattr(self.{target_class.lower()}, 'run'):
                result = self.{target_class.lower()}.run()
            else:
                self.logger.error("No suitable execution method found")
                return False

            return result is not False
        except Exception as e:
            self.logger.error(f"Error executing cycle: {{e}}", exc_info=True)
            return False

    def _cleanup(self):
        """Cleanup resources"""
        if self.{target_class.lower()}:
            if hasattr(self.{target_class.lower()}, 'cleanup'):
                try:
                    self.{target_class.lower()}.cleanup()
                except Exception as e:
                    self.logger.error(f"Error during cleanup: {{e}}", exc_info=True)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="{daemon_name} Daemon")
    parser.add_argument('--cycle', action='store_true', help='Run single cycle and exit')
    parser.add_argument('--interval', type=int, default={interval}, help='Cycle interval in seconds')
    parser.add_argument('--project-root', type=str, help='Project root directory')

    args = parser.parse_args()

    project_root = Path(args.project_root) if args.project_root else None

    daemon = {target_class}Daemon(interval=args.interval, project_root=project_root)

    if args.cycle:
        # Single cycle mode (for cron)
        daemon._initialize()
        try:
            success = daemon._run_cycle()
            sys.exit(0 if success else 1)
        finally:
            daemon._cleanup()
    else:
        # Continuous mode
        daemon.run()


if __name__ == "__main__":
    main()
'''
    return script_content
