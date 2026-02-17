#!/usr/bin/env python3
"""
JARVIS Headless Startup System

Starts JARVIS and all services headlessly (no visible windows) on system reboot.
All processes run headless and log to Luminous system log.

Features:
- Headless startup (no CMD/PowerShell windows)
- All processes log to Luminous system log
- Automatic startup on system reboot
- Process monitoring and management

Tags: #HEADLESS #STARTUP #REBOOT #LUMINOUS_LOG #JARVIS @JARVIS @LUMINA
"""

import sys
import os
import json
import subprocess
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        def get_logger(name):
            return logging.getLogger(name)

logger = get_logger("JARVISHeadlessStartup")

# Import Luminous system log
try:
    from luminous_system_log_aggregator import get_luminous_log
    LUMINOUS_LOG_AVAILABLE = True
except ImportError:
    LUMINOUS_LOG_AVAILABLE = False
    logger.warning("⚠️  Luminous system log not available")


@dataclass
class StartupProcess:
    """Startup process configuration"""
    name: str
    command: List[str]
    working_dir: Optional[Path] = None
    environment: Optional[Dict[str, str]] = None
    delay_seconds: float = 0.0
    required: bool = True
    retry_count: int = 3


class JARVISHeadlessStartup:
    """
    JARVIS Headless Startup System

    Starts all JARVIS services headlessly on system reboot.
    All processes run without visible windows and log to Luminous system log.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize headless startup system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Luminous system log
        self.luminous_log = None
        if LUMINOUS_LOG_AVAILABLE:
            try:
                self.luminous_log = get_luminous_log(self.project_root)
                logger.info("✅ Luminous system log integrated")
            except Exception as e:
                logger.warning(f"⚠️  Luminous log unavailable: {e}")

        # Running processes
        self.running_processes: Dict[str, subprocess.Popen] = {}

        # Startup processes configuration
        self.startup_processes = self._load_startup_configuration()

        logger.info("✅ JARVIS Headless Startup System initialized")
        logger.info("   🚀 All processes will start headlessly")
        logger.info("   📝 All logs will go to Luminous system log")

    def _load_startup_configuration(self) -> List[StartupProcess]:
        """Load startup processes configuration"""
        processes = []

        # JARVIS Core
        processes.append(StartupProcess(
            name="JARVIS",
            command=["python", str(self.project_root / "scripts" / "python" / "jarvis_core.py")],
            working_dir=self.project_root,
            required=True
        ))

        # NAS Logging Watchdog
        processes.append(StartupProcess(
            name="NASLoggingWatchdog",
            command=["python", str(self.project_root / "scripts" / "python" / "nas_logging_watchdog.py"), "--daemon"],
            working_dir=self.project_root,
            delay_seconds=2.0,
            required=True
        ))

        # Live Interaction Capture
        processes.append(StartupProcess(
            name="LiveInteractionCapture",
            command=["python", str(self.project_root / "scripts" / "python" / "jarvis_live_interaction_capture.py")],
            working_dir=self.project_root,
            delay_seconds=5.0,
            required=False
        ))

        # ACE (Iron Man) Avatar - starts automatically on Windows startup
        processes.append(StartupProcess(
            name="ACE",
            command=["python", str(self.project_root / "scripts" / "python" / "ironman_animated_va.py")],
            working_dir=self.project_root,
            delay_seconds=3.0,
            required=True
        ))

        # JARVIS Narrator Avatar
        processes.append(StartupProcess(
            name="JARVISNarrator",
            command=["python", str(self.project_root / "scripts" / "python" / "jarvis_narrator_avatar.py")],
            working_dir=self.project_root,
            delay_seconds=4.0,
            required=True
        ))

        # VA Desktop Widgets Renderer
        processes.append(StartupProcess(
            name="VARenderer",
            command=["python", str(self.project_root / "scripts" / "python" / "render_va_desktop_widgets.py")],
            working_dir=self.project_root,
            delay_seconds=6.0,
            required=True
        ))

        # Add more processes as needed

        return processes

    def _log_to_luminous(self, source: str, level: str, message: str, metadata: Optional[Dict[str, Any]] = None):
        """Log to Luminous system log"""
        if self.luminous_log:
            try:
                self.luminous_log.log(source, level, message, metadata)
            except Exception as e:
                logger.debug(f"Failed to log to Luminous: {e}")

        # Also log to standard logger
        getattr(logger, level.lower())(message)

    def start_process_headless(self, process: StartupProcess) -> bool:
        """
        Start a process headlessly (no visible window)

        Args:
            process: Startup process configuration

        Returns:
            True if started successfully, False otherwise
        """
        try:
            # Prepare environment
            env = process.environment or {}
            env.update(os.environ)

            # Prepare creation flags for headless (Windows)
            creation_flags = 0
            if sys.platform == 'win32':
                # CREATE_NO_WINDOW: No console window
                # DETACHED_PROCESS: Detached from console
                creation_flags = subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS

            # Start process headlessly
            proc = subprocess.Popen(
                process.command,
                cwd=str(process.working_dir) if process.working_dir else None,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=creation_flags if sys.platform == 'win32' else 0,
                start_new_session=True if sys.platform != 'win32' else False
            )

            self.running_processes[process.name] = proc

            # Start log monitoring thread
            self._start_log_monitoring(process.name, proc)

            self._log_to_luminous(
                "JARVISHeadlessStartup",
                "INFO",
                f"Started {process.name} (headless)",
                {"pid": proc.pid, "command": " ".join(process.command)}
            )

            return True

        except Exception as e:
            self._log_to_luminous(
                "JARVISHeadlessStartup",
                "ERROR",
                f"Failed to start {process.name}: {e}",
                {"process": process.name, "error": str(e)}
            )
            return False

    def _start_log_monitoring(self, name: str, proc: subprocess.Popen):
        """Start monitoring process output and log to Luminous"""
        def monitor_output():
            try:
                # Monitor stdout
                if proc.stdout:
                    for line in iter(proc.stdout.readline, b''):
                        if line:
                            line_str = line.decode('utf-8', errors='ignore').strip()
                            if line_str:
                                self._log_to_luminous(
                                    name,
                                    "INFO",
                                    line_str
                                )

                # Monitor stderr
                if proc.stderr:
                    for line in iter(proc.stderr.readline, b''):
                        if line:
                            line_str = line.decode('utf-8', errors='ignore').strip()
                            if line_str:
                                self._log_to_luminous(
                                    name,
                                    "ERROR",
                                    line_str
                                )
            except Exception as e:
                self._log_to_luminous(
                    "JARVISHeadlessStartup",
                    "ERROR",
                    f"Log monitoring error for {name}: {e}"
                )

        # Start monitoring thread
        thread = threading.Thread(
            target=monitor_output,
            name=f"LogMonitor_{name}",
            daemon=True
        )
        thread.start()

    def start_all(self) -> Dict[str, Any]:
        """
        Start all configured processes headlessly

        Returns:
            Startup results
        """
        self._log_to_luminous(
            "JARVISHeadlessStartup",
            "INFO",
            "Starting JARVIS headless startup sequence"
        )

        results = {
            "started": [],
            "failed": [],
            "total": len(self.startup_processes)
        }

        for process in self.startup_processes:
            # Delay if specified
            if process.delay_seconds > 0:
                time.sleep(process.delay_seconds)

            # Start process
            success = self.start_process_headless(process)

            if success:
                results["started"].append(process.name)
            else:
                results["failed"].append(process.name)
                if process.required:
                    self._log_to_luminous(
                        "JARVISHeadlessStartup",
                        "ERROR",
                        f"Required process {process.name} failed to start"
                    )

        self._log_to_luminous(
            "JARVISHeadlessStartup",
            "INFO",
            f"Startup complete: {len(results['started'])}/{results['total']} started",
            results
        )

        return results

    def stop_all(self):
        """Stop all running processes"""
        self._log_to_luminous(
            "JARVISHeadlessStartup",
            "INFO",
            "Stopping all JARVIS processes"
        )

        for name, proc in self.running_processes.items():
            try:
                proc.terminate()
                proc.wait(timeout=5.0)
                self._log_to_luminous(
                    "JARVISHeadlessStartup",
                    "INFO",
                    f"Stopped {name}"
                )
            except Exception as e:
                try:
                    proc.kill()
                except:
                    pass
                self._log_to_luminous(
                    "JARVISHeadlessStartup",
                    "WARNING",
                    f"Force stopped {name}: {e}"
                )

        self.running_processes.clear()

    def get_status(self) -> Dict[str, Any]:
        """Get startup system status"""
        status = {
            "running_processes": {},
            "total_processes": len(self.startup_processes),
            "running_count": len(self.running_processes)
        }

        for name, proc in self.running_processes.items():
            status["running_processes"][name] = {
                "pid": proc.pid,
                "alive": proc.poll() is None
            }

        return status


if __name__ == "__main__":
    # Test headless startup
    print("=" * 80)
    print("JARVIS Headless Startup System")
    print("=" * 80)
    print()

    startup = JARVISHeadlessStartup()

    # Start all processes
    results = startup.start_all()

    print(f"✅ Started: {len(results['started'])}/{results['total']}")
    print(f"❌ Failed: {len(results['failed'])}")
    print()

    # Get status
    status = startup.get_status()
    print("Status:")
    print(json.dumps(status, indent=2, default=str))

    # Keep running
    try:
        while True:
            time.sleep(60)
            status = startup.get_status()
            print(f"Running processes: {status['running_count']}/{status['total_processes']}")
    except KeyboardInterrupt:
        print("\n🛑 Stopping all processes...")
        startup.stop_all()
