#!/usr/bin/env python3
"""
Task Daemon Launcher - Headless daemon launcher with comprehensive logging

Launches the Task Daemon Orchestrator as a background service with full logging.
Handles daemon lifecycle, PID management, and signal handling.
"""

import argparse
import atexit
import logging
import logging.handlers
import os
import signal
import sys
import time
import subprocess
from pathlib import Path
from typing import Optional
import threading
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class DaemonLauncher:
    """Launcher for headless daemon processes"""

    def __init__(self, name: str = "lumina-task-daemon", log_dir: str = "data/logs/daemon"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.pid_dir = Path("/tmp") if os.name != 'nt' else Path(os.environ.get('TEMP', 'C:\\temp'))
        self.pid_file = self.pid_dir / f"{name}.pid"
        self.lock_file = self.pid_dir / f"{name}.lock"

        # Setup logging
        self.setup_logging()

    def setup_logging(self):
        """Setup daemon launcher logging"""
        log_file = self.log_dir / "daemon_launcher.log"

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        self.logger = logging.getLogger('DaemonLauncher')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def is_running(self) -> bool:
        """Check if daemon is already running"""
        if not self.pid_file.exists():
            return False

        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())

            # Check if process exists
            os.kill(pid, 0)
            return True
        except (OSError, ValueError, FileNotFoundError):
            # Process doesn't exist or PID file corrupted
            self.cleanup_pid_file()
            return False

    def cleanup_pid_file(self):
        """Clean up stale PID file"""
        try:
            if self.pid_file.exists():
                self.pid_file.unlink()
            if self.lock_file.exists():
                self.lock_file.unlink()
        except Exception as e:
            self.logger.warning(f"Failed to cleanup PID files: {e}")

    def start(self):
        """Start the daemon as a background process"""
        if self.is_running():
            self.logger.error(f"Daemon {self.name} is already running")
            sys.exit(1)

        self.logger.info(f"Starting daemon {self.name}...")

        try:
            # Create PID directory if it doesn't exist
            self.pid_dir.mkdir(exist_ok=True)

            # Start as background process using subprocess
            cmd = [sys.executable, __file__, "run-daemon", "--name", self.name]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True  # Detach from parent
            )

            # Wait a moment and check if process started
            time.sleep(2)
            if process.poll() is None:
                # Process is still running, save PID
                with open(self.pid_file, 'w') as f:
                    f.write(str(process.pid))
                self.logger.info(f"Daemon {self.name} started with PID {process.pid}")
            else:
                self.logger.error(f"Daemon {self.name} failed to start")
                sys.exit(1)

        except Exception as e:
            self.logger.error(f"Failed to start daemon: {e}")
            self.cleanup_pid_file()
            sys.exit(1)

    def run_daemon(self):
        """Run the daemon process"""
        self.logger.info(f"Daemon {self.name} started with PID {os.getpid()}")

        try:
            # Import and run the orchestrator
            from task_daemon_orchestrator import TaskDaemonOrchestrator

            orchestrator = TaskDaemonOrchestrator()
            orchestrator.run()

        except Exception as e:
            self.logger.error(f"Daemon execution failed: {e}")
            raise
        finally:
            self.logger.info(f"Daemon {self.name} stopped")

    def stop(self):
        """Stop the daemon"""
        if not self.is_running():
            self.logger.info(f"Daemon {self.name} is not running")
            return

        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())

            self.logger.info(f"Stopping daemon {self.name} (PID: {pid})...")

            # Send SIGTERM first
            os.kill(pid, signal.SIGTERM)

            # Wait for graceful shutdown
            for _ in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                if not self.is_running():
                    break

            # Force kill if still running
            if self.is_running():
                self.logger.warning(f"Daemon {self.name} did not stop gracefully, force killing...")
                os.kill(pid, signal.SIGKILL)

            self.cleanup_pid_file()
            self.logger.info(f"Daemon {self.name} stopped successfully")

        except Exception as e:
            self.logger.error(f"Failed to stop daemon: {e}")
            sys.exit(1)

    def restart(self):
        """Restart the daemon"""
        self.logger.info(f"Restarting daemon {self.name}...")
        self.stop()
        time.sleep(2)  # Brief pause
        self.start()

    def status(self):
        """Check daemon status"""
        if self.is_running():
            try:
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())

                # Get process info
                proc_info = self.get_process_info(pid)
                print(f"✅ Daemon {self.name} is running (PID: {pid})")
                if proc_info:
                    print(f"   Memory: {proc_info.get('memory_mb', 'N/A')} MB")
                    print(f"   CPU: {proc_info.get('cpu_percent', 'N/A')}%")
                    print(f"   Threads: {proc_info.get('threads', 'N/A')}")
                    print(f"   Started: {proc_info.get('create_time', 'N/A')}")

            except Exception as e:
                print(f"❌ Error getting daemon status: {e}")
        else:
            print(f"❌ Daemon {self.name} is not running")

    def get_process_info(self, pid: int) -> Optional[dict]:
        """Get process information"""
        try:
            import psutil
            proc = psutil.Process(pid)
            return {
                "memory_mb": proc.memory_info().rss / 1024 / 1024,
                "cpu_percent": proc.cpu_percent(),
                "threads": proc.num_threads(),
                "create_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(proc.create_time())),
                "status": proc.status()
            }
        except ImportError:
            return None
        except Exception:
            return None

    def logs(self, lines: int = 50, follow: bool = False):
        """Show daemon logs"""
        log_file = self.log_dir / "task_daemon.log"

        if not log_file.exists():
            print(f"No log file found: {log_file}")
            return

        try:
            if follow:
                # Follow logs
                with open(log_file, 'r') as f:
                    # Show last N lines first
                    lines_content = f.readlines()
                    for line in lines_content[-lines:]:
                        print(line.rstrip())

                    # Continue following
                    while True:
                        line = f.readline()
                        if line:
                            print(line.rstrip())
                        else:
                            time.sleep(0.1)
            else:
                # Show last N lines
                result = subprocess.run(
                    ['tail', f'-{lines}', str(log_file)],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    print(result.stdout)
                else:
                    # Fallback for systems without tail
                    with open(log_file, 'r') as f:
                        lines_content = f.readlines()
                        for line in lines_content[-lines:]:
                            print(line.rstrip())

        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"Error reading logs: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Task Daemon Launcher")
    parser.add_argument('action', choices=['start', 'stop', 'restart', 'status', 'logs', 'run-daemon'],
                       help='Action to perform')
    parser.add_argument('--name', default='lumina-task-daemon',
                       help='Daemon name')
    parser.add_argument('--log-dir', default='data/logs/daemon',
                       help='Log directory')
    parser.add_argument('--lines', type=int, default=50,
                       help='Number of log lines to show')
    parser.add_argument('--follow', action='store_true',
                       help='Follow log output')

    args = parser.parse_args()

    launcher = DaemonLauncher(args.name, args.log_dir)

    try:
        if args.action == 'start':
            launcher.start()
        elif args.action == 'stop':
            launcher.stop()
        elif args.action == 'restart':
            launcher.restart()
        elif args.action == 'status':
            launcher.status()
        elif args.action == 'logs':
            launcher.logs(args.lines, args.follow)
        elif args.action == 'run-daemon':
            # This is called when starting the actual daemon process
            launcher.run_daemon()
    except Exception as e:
        launcher.logger.error(f"Launcher action failed: {e}")
        sys.exit(1)


if __name__ == "__main__":


    main()