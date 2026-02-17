#!/usr/bin/env python3
"""
Master Feedback Loop Autonomous Executor Daemon - Headless Terminal-less Daemon with Logging

Runs Master Feedback Loop Autonomous Executor as a headless daemon for NAS cron scheduling.
No terminal/TTY required. All output goes to log files.

@MASTER_FEEDBACK_LOOP @DAEMON @NAS @CRON @LOGGING
"""

import sys
import asyncio
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
    """Headless daemon wrapper for Master Feedback Loop Autonomous Executor"""

    def __init__(self, interval: int = 3600, project_root: Optional[Path] = None):
        super().__init__(
            daemon_name="MasterFeedbackLoopDaemon",
            log_subdirectory="master_feedback_loop",
            project_root=project_root,
            interval=interval
        )
        self.executor: Optional[MasterFeedbackLoopAutonomousExecutor] = None

    def _initialize(self):
        """Initialize the executor instance"""
        self.logger.info("Initializing Master Feedback Loop Autonomous Executor...")
        try:
            self.executor = MasterFeedbackLoopAutonomousExecutor(project_root=self.project_root)
            self.logger.info("Master Feedback Loop Autonomous Executor initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize executor: {e}", exc_info=True)
            raise

    def _run_cycle(self) -> bool:
        """Run one cycle of the daemon's work"""
        if not self.executor:
            self.logger.error("Executor not initialized")
            return False

        try:
            # Run the autonomous executor
            # This is async, so we need to handle it properly
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(self.executor.execute_autonomous())
                self.logger.info(f"Cycle completed with status: {result.get('final_status', 'unknown')}")
                return result.get('final_status') != 'failed'
            finally:
                loop.close()
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
    parser = argparse.ArgumentParser(description="Master Feedback Loop Autonomous Executor Daemon")
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