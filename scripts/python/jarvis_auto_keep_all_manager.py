#!/usr/bin/env python3
"""
JARVIS Auto Keep All Manager

Automatically manages the "KEEP ALL" automation service.
- Starts automatically on JARVIS initialization
- Monitors and restarts if needed
- Ensures it's always active
"""

import logging
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict, Optional

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISAutoKeepAllManager")


class JARVISAutoKeepAllManager:
    """
    Automatically manages JARVIS "KEEP ALL" service

    Ensures it's always running and active
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Try new auto-accept monitor first, fallback to original
        self.script_path = project_root / "scripts" / "python" / "jarvis_auto_accept_monitor.py"
        if not self.script_path.exists():
            self.script_path = project_root / "scripts" / "python" / "jarvis_auto_accept_all.py"
        self.process: Optional[subprocess.Popen] = None
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None

        self.logger.info("JARVIS Auto Keep All Manager initialized")

    def is_running(self) -> bool:
        """Check if the service is running"""
        # Method 1: Check self.process
        if self.process is not None:
            if self.process.poll() is None:
                return True
            self.process = None

        # Method 2: Check for existing processes by name (singleton check)
        # This handles cases where the process was started by another instance
        try:
            import psutil

            script_name = self.script_path.name
            for proc in psutil.process_iter(["name", "cmdline"]):
                try:
                    if proc.info["name"] and "python" in proc.info["name"].lower():
                        cmdline = proc.info.get("cmdline") or []
                        cmdline_str = " ".join(cmdline).lower()
                        if script_name.lower() in cmdline_str:
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except ImportError:
            pass

        return False

    def start(self) -> Dict[str, Any]:
        """Start the KEEP ALL service automatically"""
        if self.is_running():
            self.logger.info("✅ KEEP ALL service already running")
            return {
                "success": True,
                "message": "Service already running",
                "pid": self.process.pid if self.process else None,
            }

        self.logger.info("🚀 Starting JARVIS KEEP ALL service...")

        try:
            # Start in background
            self.process = subprocess.Popen(
                [sys.executable, str(self.script_path), "--background"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )

            # Give it a moment to start
            time.sleep(1)

            if self.is_running():
                self.logger.info(f"✅ KEEP ALL service started (PID: {self.process.pid})")

                # Start monitoring
                self.start_monitoring()

                return {
                    "success": True,
                    "message": "KEEP ALL service started",
                    "pid": self.process.pid,
                }
            else:
                return {
                    "success": False,
                    "message": "Service started but immediately terminated",
                    "error": "Process failed to start",
                }

        except Exception as e:
            self.logger.error(f"❌ Failed to start KEEP ALL service: {e}")
            return {
                "success": False,
                "message": f"Failed to start service: {str(e)}",
                "error": str(e),
            }

    def stop(self) -> Dict[str, Any]:
        """Stop the KEEP ALL service"""
        if not self.is_running():
            return {"success": True, "message": "Service not running"}

        self.logger.info("🛑 Stopping KEEP ALL service...")

        try:
            self.process.terminate()
            self.process.wait(timeout=5)
            self.process = None

            self.logger.info("✅ KEEP ALL service stopped")
            return {"success": True, "message": "Service stopped"}

        except Exception as e:
            self.logger.error(f"❌ Failed to stop service: {e}")
            return {
                "success": False,
                "message": f"Failed to stop service: {str(e)}",
                "error": str(e),
            }

    def restart(self) -> Dict[str, Any]:
        """Restart the KEEP ALL service"""
        self.logger.info("🔄 Restarting KEEP ALL service...")
        self.stop()
        time.sleep(1)
        return self.start()

    def start_monitoring(self):
        """Start monitoring the service to ensure it stays active"""
        if self.monitoring:
            return

        self.monitoring = True

        def monitor_loop():
            while self.monitoring:
                try:
                    if not self.is_running():
                        logger.warning("⚠️ KEEP ALL service stopped, restarting...")
                        self.start()

                    time.sleep(30)  # Check every 30 seconds

                except Exception as e:
                    logger.error(f"Error in monitor loop: {e}")
                    time.sleep(30)

        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()

        self.logger.info("✅ Monitoring started")

    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("✅ Monitoring stopped")

    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        return {
            "running": self.is_running(),
            "pid": self.process.pid if self.process else None,
            "monitoring": self.monitoring,
            "script_path": str(self.script_path),
        }


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Auto Keep All Manager")
    parser.add_argument("--start", action="store_true", help="Start KEEP ALL service")
    parser.add_argument("--stop", action="store_true", help="Stop KEEP ALL service")
    parser.add_argument("--restart", action="store_true", help="Restart KEEP ALL service")
    parser.add_argument("--status", action="store_true", help="Get status")
    parser.add_argument("--auto-start", action="store_true", help="Auto-start on initialization")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    manager = JARVISAutoKeepAllManager(project_root)

    if args.start:
        result = manager.start()
        if result.get("success"):
            print(f"✅ KEEP ALL service started (PID: {result.get('pid')})")
        else:
            print(f"❌ Failed: {result.get('error', 'unknown')}")

    elif args.stop:
        result = manager.stop()
        if result.get("success"):
            print("✅ KEEP ALL service stopped")
        else:
            print(f"❌ Failed: {result.get('error', 'unknown')}")

    elif args.restart:
        result = manager.restart()
        if result.get("success"):
            print(f"✅ KEEP ALL service restarted (PID: {result.get('pid')})")
        else:
            print(f"❌ Failed: {result.get('error', 'unknown')}")

    elif args.status:
        status = manager.get_status()
        print("\n" + "=" * 80)
        print("JARVIS KEEP ALL STATUS")
        print("=" * 80)
        print(f"Running: {'✅ Yes' if status['running'] else '❌ No'}")
        print(f"PID: {status['pid'] or 'N/A'}")
        print(f"Monitoring: {'✅ Active' if status['monitoring'] else '❌ Inactive'}")
        print(f"Script: {status['script_path']}")
        print("=" * 80)

    elif args.auto_start:
        # Auto-start mode - start and keep running
        print("🚀 Auto-starting JARVIS KEEP ALL service...")
        result = manager.start()
        if result.get("success"):
            print("✅ Service started and monitoring active")
            print("Press Ctrl+C to stop")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping...")
                manager.stop()
                manager.stop_monitoring()
        else:
            print(f"❌ Failed to start: {result.get('error', 'unknown')}")

    else:
        # Default: auto-start
        print("🚀 Auto-starting JARVIS KEEP ALL service...")
        result = manager.start()
        if result.get("success"):
            print("✅ Service started and monitoring active")
            print("Press Ctrl+C to stop")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping...")
                manager.stop()
                manager.stop_monitoring()


if __name__ == "__main__":
    main()
