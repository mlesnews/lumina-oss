#!/usr/bin/env python3
"""
Kenny Crash Detector - Health Monitoring & Auto-Restart

Detects when Kenny crashes and automatically restarts him.
This is the exit condition for the feedback loop.

Tags: #KENNY #CRASH_DETECTION #HEALTH_MONITOR #AUTO_RESTART @JARVIS @LUMINA
"""

import sys
import os
import time
import psutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

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

logger = get_logger("KennyCrashDetector")


class KennyCrashDetector:
    """
    Monitors Kenny's health and auto-restarts on crash detection.

    This is the exit condition for the feedback loop:
    - If crash detected → restart → continue loop (NOT STAY BENT)
    - If running → continue monitoring (FEEDBACK LOOP)
    """

    def __init__(self, check_interval: float = 5.0, max_no_response: int = 3):
        """
        Initialize crash detector.

        Args:
            check_interval: Seconds between health checks
            max_no_response: Number of failed checks before considering crashed
        """
        self.check_interval = check_interval
        self.max_no_response = max_no_response
        self.failed_checks = 0
        self.last_kenny_pid: Optional[int] = None
        self.kenny_script = script_dir / "kenny_imva_enhanced.py"
        self.running = False

        # SYPHON integration - Intelligence extraction for VA enhancement
        self.syphon = None
        self.syphon_enhancement_interval = 60.0  # Extract intelligence every 60 seconds
        self.last_syphon_enhancement = time.time()
        self.syphon_enhanced_knowledge = []
        if SYPHON_AVAILABLE:
            try:
                syphon_config = SYPHONConfig(project_root=project_root, enable_regex_tools=True)
                self.syphon = SYPHONSystem(syphon_config)
                self.logger.info("✅ SYPHON intelligence extraction integrated for VA enhancement")
            except Exception as e:
                self.logger.warning(f"⚠️  SYPHON integration failed: {e}")

        # R5 Living Context Matrix - Context aggregation
        self.r5 = None
        if R5_AVAILABLE:
            try:
                self.r5 = R5LivingContextMatrix(project_root)
                self.logger.info("✅ R5 context aggregation integrated")
            except Exception as e:
                self.logger.warning(f"⚠️  R5 integration failed: {e}")

    def find_kenny_process(self) -> Optional[psutil.Process]:
        """Find running Kenny process."""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline_list = proc.info.get('cmdline', [])
                cmdline_str = ' '.join(str(c) for c in cmdline_list) if cmdline_list else ''

                if 'kenny_imva_enhanced' in cmdline_str.lower():
                    return psutil.Process(proc.pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            except Exception as e:
                logger.debug(f"Error checking process: {e}")
                continue
        return None

    def is_kenny_alive(self) -> bool:
        """
        Check if Kenny process is alive and responsive.

        Returns:
            True if Kenny is running and responsive, False otherwise
        """
        proc = self.find_kenny_process()
        if proc is None:
            logger.debug("❌ No Kenny process found")
            return False

        try:
            # Check if process is still running
            if not proc.is_running():
                logger.debug(f"❌ Kenny process {proc.pid} is not running")
                return False

            # Check if process is responsive (not zombie)
            status = proc.status()
            if status == psutil.STATUS_ZOMBIE:
                logger.debug(f"❌ Kenny process {proc.pid} is zombie")
                return False

            # Check if process is consuming resources (not hung)
            cpu_percent = proc.cpu_percent(interval=0.1)
            memory_info = proc.memory_info()

            # If process exists but uses no CPU and no memory, might be hung
            # But we'll be lenient - just check if it exists and is not zombie
            self.last_kenny_pid = proc.pid
            logger.debug(f"✅ Kenny process {proc.pid} is alive (CPU: {cpu_percent:.1f}%, Memory: {memory_info.rss / 1024 / 1024:.1f}MB)")
            return True

        except psutil.NoSuchProcess:
            logger.debug(f"❌ Kenny process {proc.pid} no longer exists")
            return False
        except Exception as e:
            logger.warning(f"⚠️ Error checking Kenny health: {e}")
            return False

    def kill_kenny(self) -> bool:
        """Kill all Kenny processes."""
        killed = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline_list = proc.info.get('cmdline', [])
                cmdline_str = ' '.join(str(c) for c in cmdline_list) if cmdline_list else ''

                if 'kenny_imva_enhanced' in cmdline_str.lower():
                    # Don't kill ourselves
                    if proc.pid == os.getpid():
                        continue

                    logger.info(f"🔪 Killing Kenny process {proc.pid}")
                    psutil.Process(proc.pid).terminate()
                    try:
                        psutil.Process(proc.pid).wait(timeout=3)
                    except psutil.TimeoutExpired:
                        psutil.Process(proc.pid).kill()
                    killed = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            except Exception as e:
                logger.warning(f"⚠️ Error killing process: {e}")
                continue

        if killed:
            time.sleep(1)  # Give processes time to die

        return killed

    def restart_kenny(self, args: list = None) -> bool:
        """
        Restart Kenny with optional arguments.

        Args:
            args: Command-line arguments to pass to Kenny

        Returns:
            True if restart successful, False otherwise
        """
        if args is None:
            args = []

        # Kill existing Kenny
        self.kill_kenny()

        # Wait a moment
        time.sleep(1)

        # Start new Kenny
        try:
            cmd = [sys.executable, str(self.kenny_script)] + args
            logger.info(f"🚀 Restarting Kenny: {' '.join(cmd)}")

            # Start in background (detached)
            if sys.platform == 'win32':
                # Windows: use CREATE_NEW_PROCESS_GROUP
                subprocess.Popen(
                    cmd,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                    cwd=str(project_root)
                )
            else:
                # Unix: use setsid
                subprocess.Popen(
                    cmd,
                    start_new_session=True,
                    cwd=str(project_root)
                )

            # Wait a moment for process to start
            time.sleep(2)

            # Verify it started
            if self.is_kenny_alive():
                logger.info(f"✅ Kenny restarted successfully (PID: {self.last_kenny_pid})")
                self.failed_checks = 0  # Reset counter
                return True
            else:
                logger.error(f"❌ Kenny restart failed - process not found")
                return False

        except Exception as e:
            logger.error(f"❌ Error restarting Kenny: {e}", exc_info=True)
            return False

    def check_health(self) -> bool:
        """
        Perform health check.

        Returns:
            True if healthy, False if crash detected
        """
        is_alive = self.is_kenny_alive()

        if is_alive:
            self.failed_checks = 0
            return True
        else:
            self.failed_checks += 1
            logger.warning(f"⚠️ Kenny health check failed ({self.failed_checks}/{self.max_no_response})")

            if self.failed_checks >= self.max_no_response:
                logger.error(f"❌ CRASH DETECTED: Kenny failed {self.failed_checks} consecutive health checks")
                return False

        return True

    def monitor_loop(self, restart_args: list = None):
        """
        Main monitoring loop - the feedback loop with exit condition.

        Exit condition:
        - If crash detected → restart → continue (NOT STAY BENT)
        - If running → continue monitoring (FEEDBACK LOOP)

        Args:
            restart_args: Arguments to pass when restarting Kenny
        """
        if restart_args is None:
            restart_args = []

        self.running = True
        logger.info(f"👀 Starting Kenny crash detector (check every {self.check_interval}s)")

        try:
            while self.running:
                # Health check
                is_healthy = self.check_health()

                if not is_healthy:
                    # CRASH DETECTED - Exit condition triggered
                    logger.error("💥 CRASH DETECTED - Restarting Kenny...")
                    restart_success = self.restart_kenny(restart_args)

                    if restart_success:
                        logger.info("✅ Restart successful - continuing monitoring")
                    else:
                        logger.error("❌ Restart failed - will retry on next check")
                        # Reset counter to retry
                        self.failed_checks = 0

                # Wait before next check
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            logger.info("🛑 Crash detector stopped by user")
        except Exception as e:
            logger.error(f"❌ Error in monitor loop: {e}", exc_info=True)
        finally:
            self.running = False

    def stop(self):
        """Stop monitoring."""
        self.running = False


def main():
    """CLI entry point."""
    import argparse
    import os

# SYPHON integration (@SYPHON) - Intelligence extraction and VA enhancement
try:
    from syphon import SYPHONSystem, SYPHONConfig, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None

# R5 Living Context Matrix integration
try:
    from r5_living_context_matrix import R5LivingContextMatrix
    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False
    R5LivingContextMatrix = None
    SYPHONConfig = None
    DataSourceType = None

    parser = argparse.ArgumentParser(description="Kenny Crash Detector - Health Monitoring & Auto-Restart")
    parser.add_argument('--interval', type=float, default=5.0, help='Health check interval in seconds')
    parser.add_argument('--max-failures', type=int, default=3, help='Max failed checks before crash detection')
    parser.add_argument('--match-ace', action='store_true', help='Pass --match-ace to Kenny on restart')
    parser.add_argument('--check-once', action='store_true', help='Check once and exit (for testing)')

    args = parser.parse_args()

    detector = KennyCrashDetector(
        check_interval=args.interval,
        max_no_response=args.max_failures
    )

    restart_args = []
    if args.match_ace:
        restart_args.append('--match-ace')

    if args.check_once:
        # Single check mode
        is_healthy = detector.check_health()
        if is_healthy:
            print("✅ Kenny is healthy")
            sys.exit(0)
        else:
            print("❌ Kenny crash detected")
            if detector.failed_checks >= detector.max_no_response:
                print("🔄 Restarting Kenny...")
                detector.restart_kenny(restart_args)
            sys.exit(1)
    else:
        # Continuous monitoring
        detector.monitor_loop(restart_args)


if __name__ == "__main__":


    main()