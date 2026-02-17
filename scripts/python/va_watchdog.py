#!/usr/bin/env python3
"""
VA Watchdog - Monitors and restarts VA service

Watches the headless VA service and automatically restarts it if it crashes.
Part of watchdog-guarded processes.

Tags: #WATCHDOG #MONITORING #RESTART #GUARDED_PROCESSES @JARVIS @LUMINA
"""

import sys
import time
import subprocess
import signal
from pathlib import Path
from datetime import datetime

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

logger = get_logger("VAWatchdog")


class VAWatchdog:
    """Watchdog process that monitors and restarts VA service"""

    def __init__(self):
        """Initialize watchdog"""
        self.running = False
        self.shutdown_requested = False
        self.service_process = None
        self.restart_count = 0
        self.max_restarts = 10  # Max restarts per hour
        self.restart_window_start = time.time()

        # Service script path
        self.service_script = script_dir / "va_headless_service.py"

        logger.info("=" * 80)
        logger.info("🐕 VA WATCHDOG INITIALIZED")
        logger.info("=" * 80)
        logger.info(f"   Monitoring: {self.service_script}")
        logger.info("   Watchdog ready")
        logger.info("=" * 80)

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"📡 Watchdog received signal {signum}, shutting down...")
        self.shutdown_requested = True
        if self.service_process:
            self.service_process.terminate()

    def start_service(self):
        """Start the VA service"""
        if self.service_process and self.service_process.poll() is None:
            logger.warning("⚠️  Service already running")
            return True

        try:
            logger.info("🚀 Starting VA service...")

            # Start service process
            self.service_process = subprocess.Popen(
                [sys.executable, str(self.service_script)],
                cwd=str(project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            logger.info(f"  ✅ Service started (PID: {self.service_process.pid})")
            return True

        except Exception as e:
            logger.error(f"  ❌ Failed to start service: {e}")
            return False

    def check_service(self):
        """Check if service is running"""
        if not self.service_process:
            return False

        # Check if process is still alive
        if self.service_process.poll() is not None:
            # Process has terminated
            return_code = self.service_process.returncode
            logger.warning(f"⚠️  Service process terminated (exit code: {return_code})")

            # Get any error output
            if self.service_process.stderr:
                try:
                    stderr_output = self.service_process.stderr.read()
                    if stderr_output:
                        logger.error(f"Service stderr: {stderr_output}")
                except:
                    pass

            return False

        return True

    def restart_service(self):
        """Restart the VA service"""
        current_time = time.time()

        # Reset restart window if more than an hour has passed
        if current_time - self.restart_window_start > 3600:
            self.restart_count = 0
            self.restart_window_start = current_time

        # Check restart limit
        if self.restart_count >= self.max_restarts:
            logger.error(f"❌ Max restarts ({self.max_restarts}) reached in last hour")
            logger.error("   Watchdog stopping to prevent restart loop")
            return False

        self.restart_count += 1
        logger.info(f"🔄 Restarting service (attempt {self.restart_count}/{self.max_restarts})...")

        # Wait a bit before restarting
        time.sleep(5)

        return self.start_service()

    def run(self):
        """Run the watchdog"""
        logger.info("=" * 80)
        logger.info("🐕 STARTING VA WATCHDOG")
        logger.info("=" * 80)
        logger.info()

        self.running = True

        # Start service initially
        if not self.start_service():
            logger.error("❌ Failed to start service initially")
            return 1

        logger.info("Watchdog monitoring service...")
        logger.info("Press Ctrl+C to stop")
        logger.info()

        last_check = time.time()
        check_interval = 10  # Check every 10 seconds

        try:
            while self.running and not self.shutdown_requested:
                current_time = time.time()

                # Check service status
                if current_time - last_check >= check_interval:
                    if not self.check_service():
                        # Service crashed, restart it
                        logger.warning("⚠️  Service not running, attempting restart...")
                        if not self.restart_service():
                            logger.error("❌ Failed to restart service, watchdog stopping")
                            break

                    last_check = current_time

                # Sleep briefly
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("📡 Keyboard interrupt received")
            self.shutdown_requested = True

        # Shutdown
        logger.info()
        logger.info("=" * 80)
        logger.info("🛑 SHUTTING DOWN VA WATCHDOG")
        logger.info("=" * 80)

        if self.service_process:
            logger.info("Terminating service process...")
            self.service_process.terminate()
            try:
                self.service_process.wait(timeout=10)
                logger.info("  ✅ Service terminated")
            except subprocess.TimeoutExpired:
                logger.warning("  ⚠️  Service didn't terminate, killing...")
                self.service_process.kill()

        self.running = False
        logger.info("✅ Watchdog stopped")
        logger.info("=" * 80)

        return 0


def main():
    """Main entry point"""
    try:
        watchdog = VAWatchdog()
        return watchdog.run()
    except Exception as e:
        logger.error(f"❌ Watchdog failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":


    sys.exit(main())