#!/usr/bin/env python3
"""
JARVIS Admin Elevation Module

Comprehensive admin elevation utilities for Windows.
Provides functions to check admin status, request elevation, and run commands with admin privileges.

@JARVIS @ADMIN @ELEVATION @UAC @WINDOWS
"""

import sys
import ctypes
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from contextlib import contextmanager

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AdminElevation")


class AdminElevation:
    """
    Admin Elevation Utilities

    Provides methods to check admin status, request elevation, and run commands with admin privileges.
    """

    @staticmethod
    def is_admin() -> bool:
        """
        Check if current process is running with admin privileges.

        Returns:
            bool: True if running as admin, False otherwise
        """
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception as e:
            logger.debug(f"Error checking admin status: {e}")
            return False

    @staticmethod
    def request_elevation(script_path: Optional[Path] = None, args: Optional[List[str]] = None) -> bool:
        """
        Request admin elevation via UAC prompt.

        Args:
            script_path: Path to script to run with elevation (default: current script)
            args: Additional arguments to pass to script

        Returns:
            bool: True if elevation was requested, False if already admin
        """
        if AdminElevation.is_admin():
            logger.debug("Already running as admin")
            return False

        if script_path is None:
            script_path = Path(__file__).resolve()

        if args is None:
            args = []

        try:
            # Re-run the program with admin rights
            ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",  # Request elevation
                sys.executable,
                f'"{script_path}" {" ".join(args)}',
                None,
                1  # SW_SHOWNORMAL
            )
            logger.info("✅ Admin elevation requested. Please approve the UAC prompt.")
            return True
        except Exception as e:
            logger.error(f"Failed to request elevation: {e}")
            return False

    @staticmethod
    def run_powershell_as_admin(command: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Run PowerShell command with admin privileges.

        Args:
            command: PowerShell command to execute
            timeout: Timeout in seconds

        Returns:
            Dict with success, stdout, stderr, returncode
        """
        try:
            # Create PowerShell command with elevation
            ps_command = f"""
            $ErrorActionPreference = 'Stop'
            try {{
                {command}
                Write-Output "SUCCESS"
            }} catch {{
                Write-Output "ERROR: $_"
            }}
            """

            # Try to run with elevation if not already admin
            if not AdminElevation.is_admin():
                logger.warning("⚠️  Not running as admin - command may fail")
                logger.info("💡 Consider running script with admin privileges")

            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=True
            )

            return {
                "success": "SUCCESS" in result.stdout or result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "admin": AdminElevation.is_admin()
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Timeout",
                "stdout": "",
                "stderr": "",
                "returncode": -1,
                "admin": AdminElevation.is_admin()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": "",
                "returncode": -1,
                "admin": AdminElevation.is_admin()
            }

    @staticmethod
    def run_command_as_admin(command: List[str], timeout: int = 30) -> Dict[str, Any]:
        """
        Run command with admin privileges using runas.

        Args:
            command: Command and arguments as list
            timeout: Timeout in seconds

        Returns:
            Dict with success, stdout, stderr, returncode
        """
        if not AdminElevation.is_admin():
            logger.warning("⚠️  Not running as admin - using runas")
            # Use runas to execute command
            try:
                result = subprocess.run(
                    ["runas", "/user:Administrator"] + command,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                return {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                    "admin": False
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "stdout": "",
                    "stderr": "",
                    "returncode": -1,
                    "admin": False
                }
        else:
            # Already admin, run directly
            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                return {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                    "admin": True
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "stdout": "",
                    "stderr": "",
                    "returncode": -1,
                    "admin": True
                }

    @staticmethod
    def set_service_startup_type(service_name: str, startup_type: str = "Manual") -> Dict[str, Any]:
        """
        Set Windows service startup type (requires admin).

        Args:
            service_name: Name of service
            startup_type: Startup type (Automatic, Manual, Disabled)

        Returns:
            Dict with success status
        """
        if startup_type not in ["Automatic", "Manual", "Disabled"]:
            return {
                "success": False,
                "error": f"Invalid startup type: {startup_type}"
            }

        command = f"Set-Service -Name '{service_name}' -StartupType {startup_type} -ErrorAction Stop"
        result = AdminElevation.run_powershell_as_admin(command)

        if result["success"]:
            logger.info(f"✅ Service '{service_name}' startup type set to {startup_type}")
        else:
            logger.warning(f"⚠️  Failed to set service '{service_name}' startup type: {result.get('error', 'Unknown error')}")

        return result

    @staticmethod
    def start_service(service_name: str) -> Dict[str, Any]:
        """Start Windows service (requires admin)"""
        command = f"Start-Service -Name '{service_name}' -ErrorAction Stop"
        result = AdminElevation.run_powershell_as_admin(command)

        if result["success"]:
            logger.info(f"✅ Service '{service_name}' started")
        else:
            logger.warning(f"⚠️  Failed to start service '{service_name}': {result.get('error', 'Unknown error')}")

        return result

    @staticmethod
    def stop_service(service_name: str) -> Dict[str, Any]:
        """Stop Windows service (requires admin)"""
        command = f"Stop-Service -Name '{service_name}' -Force -ErrorAction Stop"
        result = AdminElevation.run_powershell_as_admin(command)

        if result["success"]:
            logger.info(f"✅ Service '{service_name}' stopped")
        else:
            logger.warning(f"⚠️  Failed to stop service '{service_name}': {result.get('error', 'Unknown error')}")

        return result

    @staticmethod
    def set_registry_value(registry_path: str, name: str, value: Any, value_type: str = "String") -> Dict[str, Any]:
        """
        Set registry value (requires admin).

        Args:
            registry_path: Registry path (e.g., "HKLM:\\SOFTWARE\\...")
            name: Value name
            value: Value to set
            value_type: Value type (String, DWord, QWord, etc.)
        """
        # Escape value for PowerShell
        if isinstance(value, str):
            value_escaped = f'"{value}"'
        else:
            value_escaped = str(value)

        command = f"Set-ItemProperty -Path '{registry_path}' -Name '{name}' -Value {value_escaped} -Type {value_type} -ErrorAction Stop"
        result = AdminElevation.run_powershell_as_admin(command)

        if result["success"]:
            logger.info(f"✅ Registry value set: {registry_path}\\{name}")
        else:
            logger.warning(f"⚠️  Failed to set registry value: {result.get('error', 'Unknown error')}")

        return result

    @staticmethod
    def create_scheduled_task(task_name: str, command: str, arguments: str = "", 
                             trigger: str = "AtLogon", interval: Optional[int] = None) -> Dict[str, Any]:
        """
        Create Windows scheduled task (requires admin).

        Args:
            task_name: Name of task
            command: Command to execute
            arguments: Command arguments
            trigger: Trigger type (AtLogon, Daily, Weekly, etc.)
            interval: Interval in minutes (for recurring tasks)
        """
        # Build schtasks command
        if trigger == "AtLogon":
            schtasks_cmd = f'schtasks /Create /TN "{task_name}" /TR "{command} {arguments}" /SC ONLOGON /F'
        elif trigger == "Daily":
            schtasks_cmd = f'schtasks /Create /TN "{task_name}" /TR "{command} {arguments}" /SC DAILY /F'
        elif interval:
            schtasks_cmd = f'schtasks /Create /TN "{task_name}" /TR "{command} {arguments}" /SC MINUTE /MO {interval} /F'
        else:
            return {
                "success": False,
                "error": "Invalid trigger or missing interval"
            }

        result = AdminElevation.run_command_as_admin(["cmd", "/c", schtasks_cmd])

        if result["success"]:
            logger.info(f"✅ Scheduled task '{task_name}' created")
        else:
            logger.warning(f"⚠️  Failed to create scheduled task: {result.get('error', 'Unknown error')}")

        return result

    @staticmethod
    @contextmanager
    def require_admin(context: str = "operation"):
        """
        Context manager that ensures admin privileges.

        Usage:
            with AdminElevation.require_admin("service management"):
                # Code that requires admin
                pass
        """
        if not AdminElevation.is_admin():
            logger.warning(f"⚠️  Admin privileges required for {context}")
            logger.info("💡 Consider running script with admin privileges")
            yield False
        else:
            logger.debug(f"✅ Running with admin privileges for {context}")
            yield True

    @staticmethod
    def ensure_admin_or_exit(script_path: Optional[Path] = None, message: Optional[str] = None) -> None:
        try:
            """
            Ensure admin privileges or request elevation and exit.

            Args:
                script_path: Path to script to run with elevation
                message: Custom message to display
            """
            if AdminElevation.is_admin():
                return

            if message:
                logger.info(message)
            else:
                logger.info("⚠️  Admin privileges required")
                logger.info("🔄 Requesting admin elevation...")

            if script_path is None:
                script_path = Path(sys.argv[0]).resolve()

            AdminElevation.request_elevation(script_path, sys.argv[1:])
            sys.exit(0)


        except Exception as e:
            logger.error(f"Error in ensure_admin_or_exit: {e}", exc_info=True)
            raise
# Convenience functions
def is_admin() -> bool:
    """Check if running as admin"""
    return AdminElevation.is_admin()


def require_admin(context: str = "operation"):
    """Context manager for admin operations"""
    return AdminElevation.require_admin(context)


def ensure_admin_or_exit(script_path: Optional[Path] = None, message: Optional[str] = None) -> None:
    """Ensure admin or request elevation and exit"""
    AdminElevation.ensure_admin_or_exit(script_path, message)


def run_powershell_as_admin(command: str, timeout: int = 30) -> Dict[str, Any]:
    """Run PowerShell command as admin"""
    return AdminElevation.run_powershell_as_admin(command, timeout)


def set_service_startup_type(service_name: str, startup_type: str = "Manual") -> Dict[str, Any]:
    """Set service startup type"""
    return AdminElevation.set_service_startup_type(service_name, startup_type)


def start_service(service_name: str) -> Dict[str, Any]:
    """Start service"""
    return AdminElevation.start_service(service_name)


def stop_service(service_name: str) -> Dict[str, Any]:
    """Stop service"""
    return AdminElevation.stop_service(service_name)


# Example usage
if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("🔧 JARVIS ADMIN ELEVATION MODULE")
    logger.info("=" * 70)
    logger.info("")

    # Check admin status
    admin_status = AdminElevation.is_admin()
    logger.info(f"   Admin Status: {'✅ Running as admin' if admin_status else '❌ Not running as admin'}")
    logger.info("")

    # Example: Check service status
    logger.info("   Example: Checking service status...")
    result = AdminElevation.run_powershell_as_admin(
        "Get-Service -Name 'ArmouryCrateService' -ErrorAction SilentlyContinue | Select-Object Name, Status, StartType"
    )
    if result["success"]:
        logger.info(f"      {result['stdout']}")
    else:
        logger.warning(f"      Failed: {result.get('error', 'Unknown error')}")

    logger.info("")
    logger.info("=" * 70)
    logger.info("")
