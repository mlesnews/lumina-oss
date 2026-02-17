#!/usr/bin/env python3
"""
MasterFeedbackLoopDaemon - Headless Terminal-less Daemon with Logging

Runs MasterFeedbackLoopAutonomousExecutor as a headless daemon for NAS cron scheduling.
No terminal/TTY required. All output goes to log files.

@DAEMON @NAS @CRON @LOGGING
"""

import sys
import argparse
from pathlib import Path
from typing import Optional
from daemon_template import BaseDaemon

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from master_feedback_loop_autonomous_executor import MasterFeedbackLoopAutonomousExecutor
except ImportError as e:
    import logging
    logging.error(f"Failed to import MasterFeedbackLoopAutonomousExecutor: {e}", exc_info=True)
    sys.exit(1)


class MasterFeedbackLoopDaemon(BaseDaemon):
    """Headless daemon wrapper for MasterFeedbackLoopAutonomousExecutor"""

    def __init__(self, interval: int = 3600, project_root: Optional[Path] = None):
        super().__init__(
            daemon_name="MasterFeedbackLoopDaemon",
            log_subdirectory="master_feedback_loop",
            project_root=project_root,
            interval=interval
        )
        self.executor: Optional[MasterFeedbackLoopAutonomousExecutor] = None

    def _initialize(self):
        """Initialize the target class instance"""
        self.logger.info(f"Initializing MasterFeedbackLoopAutonomousExecutor...")
        try:
            self.executor = MasterFeedbackLoopAutonomousExecutor(project_root=self.project_root)
            self.logger.info(f"MasterFeedbackLoopAutonomousExecutor initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize MasterFeedbackLoopAutonomousExecutor: {e}", exc_info=True)
            raise

    def _run_cycle(self) -> bool:
        """Run one cycle of the daemon's work"""
        if not self.executor:
            self.logger.error("MasterFeedbackLoopAutonomousExecutor not initialized")
            return False

        try:
            # Try different execution methods
            executor = self.executor

            # Check for async execute method
            if hasattr(executor, 'execute_autonomous'):
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(executor.execute_autonomous())
                    return result.get('final_status') != 'failed' if isinstance(result, dict) else result is not False
                finally:
                    loop.close()
            elif hasattr(executor, 'run_cycle'):
                result = executor.run_cycle()
                return result is not False
            elif hasattr(executor, 'execute'):
                result = executor.execute()
                return result is not False
            elif hasattr(executor, 'run'):
                result = executor.run()
                return result is not False
            else:
                self.logger.error("No suitable execution method found in MasterFeedbackLoopAutonomousExecutor")
                return False
        except Exception as e:
            self.logger.error(f"Error executing cycle: {e}", exc_info=True)
            return False

    def _cleanup(self):
        """Cleanup resources"""
        if self.executor:
            if hasattr(self.executor, 'cleanup'):
                try:
                    self.executor.cleanup()
                except Exception as e:
                    self.logger.error(f"Error during cleanup: {e}", exc_info=True)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="MasterFeedbackLoopDaemon")
    parser.add_argument('--cycle', action='store_true', help='Run single cycle and exit')
    parser.add_argument('--interval', type=int, default=3600, help='Cycle interval in seconds')
    parser.add_argument('--project-root', type=str, help='Project root directory')

    args = parser.parse_args()

    project_root = Path(args.project_root) if args.project_root else None

    daemon = MasterFeedbackLoopDaemon(interval=args.interval, project_root=project_root)

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