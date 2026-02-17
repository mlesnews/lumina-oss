#!/usr/bin/env python3
"""
JARVIS MANUS Administrative Orchestrator
Enables JARVIS to perform administrative operations on Windows.

Tags: #MANUS #ADMIN #WINDOWS #ELEVATION @AUTO @MANUS
"""

import sys
import ctypes
import subprocess
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISManusAdmin")


class JARVISManusAdminOrchestrator:
    """
    Orchestrates administrative tasks for JARVIS on Windows.
    """

    def __init__(self):
        self.logger = logger
        self.logger.info("✅ JARVIS MANUS Admin Orchestrator initialized")

    @staticmethod
    def is_admin() -> bool:
        """Check if the current process has administrative privileges"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except AttributeError:
            return os.getuid() == 0 if hasattr(os, 'getuid') else False

    def run_as_admin(self, executable: str, params: str = "") -> bool:
        """Relaunch the process or another command with administrative privileges"""
        if self.is_admin():
            self.logger.info("ℹ️ Already running with admin privileges")
            return True

        self.logger.info(f"🚀 Requesting elevation for: {executable} {params}")

        try:
            # Use ShellExecuteEx to request elevation (UAC prompt)
            ret = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", str(executable), str(params), None, 1
            )

            if ret > 32:
                self.logger.info("✅ Elevation request successful")
                return True
            else:
                self.logger.error(f"❌ Elevation request failed with error code: {ret}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Elevation error: {e}", exc_info=True)
            return False

    def execute_admin_command(self, command: str) -> Dict[str, Any]:
        """Execute a single command with administrative privileges using PowerShell"""
        if not self.is_admin():
            self.logger.warning("⚠️ Not running as admin. Command may fail or trigger UAC.")
            # We can use powershell Start-Process with -Verb RunAs
            ps_command = f"Start-Process powershell -ArgumentList '-Command \"{command}\"' -Verb RunAs -Wait"
            try:
                result = subprocess.run(["powershell", "-Command", ps_command], capture_output=True, text=True)
                return {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "elevated_via_ps": True
                }
            except Exception as e:
                return {"success": False, "error": str(e)}
        else:
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                return {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "already_admin": True
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

    def manage_system_service(self, service_name: str, action: str) -> Dict[str, Any]:
        """Manage Windows services (start, stop, restart)"""
        actions = {
            "start": "Start-Service",
            "stop": "Stop-Service",
            "restart": "Restart-Service",
            "status": "Get-Service"
        }

        if action not in actions:
            return {"success": False, "error": f"Invalid action: {action}"}

        cmd = f"{actions[action]} -Name {service_name}"
        return self.execute_admin_command(cmd)


def main():
    try:
        """CLI interface for testing"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS MANUS Admin Orchestrator")
        parser.add_argument("--check", action="store_true", help="Check if running as admin")
        parser.add_argument("--elevate", action="store_true", help="Relaunch current script as admin")
        parser.add_argument("--command", type=str, help="Execute a command as admin")

        args = parser.parse_args()
        orchestrator = JARVISManusAdminOrchestrator()

        if args.check:
            print(f"Is Admin: {orchestrator.is_admin()}")
        elif args.elevate:
            orchestrator.run_as_admin(sys.executable, " ".join(sys.argv))
        elif args.command:
            result = orchestrator.execute_admin_command(args.command)
            print(json.dumps(result, indent=2))
        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()