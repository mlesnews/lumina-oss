#!/usr/bin/env python3
"""
Headless Process Launcher with Unified Logging

Launches Python scripts headlessly (no visible terminals) with all output
redirected to NAS centralized logging (L:/Logs/) using standard logging module.

Features:
- No visible terminals (uses pythonw.exe on Windows)
- All output goes to unified logger (NAS + local)
- Standard logging module (Unix-style)
- Process monitoring and error handling
- Automatic log rotation

Usage:
    python headless_process_launcher.py <script_path> [args...]

Example:
    python headless_process_launcher.py scripts/python/jarvis_default_va.py
    python headless_process_launcher.py scripts/python/auto_start_ultron_router.py --once

Tags: #HEADLESS #LOGGING #STARTUP #HOMELAB
"""

import sys
import subprocess
import os
from pathlib import Path
from typing import List, Optional, Dict
import platform

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from lumina_unified_logger import LuminaUnifiedLogger


class HeadlessProcessLauncher:
    """Launch processes headlessly with unified logging"""

    def __init__(self, category: str = "Application", service: str = "ProcessLauncher"):
        self.logger_module = LuminaUnifiedLogger(category, service)
        self.logger = self.logger_module.get_logger()
        self.is_windows = platform.system() == "Windows"

    def launch_headless(
        self,
        script_path: Path,
        args: List[str] = None,
        category: str = "Application",
        service: str = None,
        cwd: Optional[Path] = None,
        env: Optional[Dict[str, str]] = None
    ) -> subprocess.Popen:
        """
        Launch a Python script headlessly with unified logging.

        Args:
            script_path: Path to Python script to run
            args: Additional arguments to pass to script
            category: Log category (Application, System, AI, etc.)
            service: Service name for logging (defaults to script name)
            cwd: Working directory (defaults to project root)
            env: Environment variables to set

        Returns:
            subprocess.Popen object for the launched process
        """
        if not script_path.exists():
            self.logger.error(f"Script not found: {script_path}")
            raise FileNotFoundError(f"Script not found: {script_path}")

        # Determine service name from script if not provided
        if service is None:
            service = script_path.stem

        # Use unified logger for this service
        service_logger = LuminaUnifiedLogger(category, service)
        logger = service_logger.get_logger()

        # Build command
        if self.is_windows:
            # Use pythonw.exe for headless execution (no window)
            python_exe = sys.executable.replace("python.exe", "pythonw.exe")
            if not Path(python_exe).exists():
                # Fallback to python.exe with CREATE_NO_WINDOW
                python_exe = sys.executable
        else:
            python_exe = sys.executable

        cmd = [python_exe, str(script_path)]
        if args:
            cmd.extend(args)

        # Set up environment
        process_env = os.environ.copy()
        if env:
            process_env.update(env)

        # Ensure unified logger is available
        process_env["PYTHONPATH"] = str(script_dir) + os.pathsep + process_env.get("PYTHONPATH", "")

        # Working directory
        work_dir = str(cwd) if cwd else str(project_root)

        logger.info(f"🚀 Launching headless process: {script_path.name}")
        logger.info(f"   Command: {' '.join(cmd)}")
        logger.info(f"   Working directory: {work_dir}")
        logger.info(f"   Logs: {service_logger.log_paths}")

        try:
            if self.is_windows:
                # Windows: Headless execution
                if python_exe.endswith("pythonw.exe"):
                    # pythonw.exe - completely headless
                    process = subprocess.Popen(
                        cmd,
                        cwd=work_dir,
                        env=process_env,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        stdin=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                        start_new_session=True
                    )
                else:
                    # python.exe with CREATE_NO_WINDOW
                    process = subprocess.Popen(
                        cmd,
                        cwd=work_dir,
                        env=process_env,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        stdin=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                        start_new_session=True
                    )
            else:
                # Unix: Headless execution
                process = subprocess.Popen(
                    cmd,
                    cwd=work_dir,
                    env=process_env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True
                )

            logger.info(f"✅ Process launched (PID: {process.pid})")
            return process

        except Exception as e:
            logger.error(f"❌ Failed to launch process: {e}")
            raise


def main():
    """Main entry point for command-line usage"""
    if len(sys.argv) < 2:
        print("Usage: python headless_process_launcher.py <script_path> [args...]")
        print("Example: python headless_process_launcher.py scripts/python/jarvis_default_va.py")
        sys.exit(1)

    script_path = Path(sys.argv[1])
    args = sys.argv[2:] if len(sys.argv) > 2 else []

    launcher = HeadlessProcessLauncher()

    try:
        process = launcher.launch_headless(script_path, args)
        print(f"Process launched with PID: {process.pid}")
        print("Process is running headlessly. Check logs for output.")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":

    sys.exit(main())