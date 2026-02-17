#!/usr/bin/env python3
"""
JARVIS Windows Service Manager

Manages Windows services for JARVIS self-healing system.
Provides service start, stop, restart, and status checking capabilities.

Tags: #JARVIS #SERVICE_MANAGEMENT #WINDOWS #SELF_HEALING @JARVIS @LUMINA @DOIT
"""

import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISWindowsServiceManager")

# Try to import win32service (optional, falls back to subprocess)
try:
    import win32service
    import win32serviceutil
    import win32api
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    logger.warning("⚠️  win32service not available - using subprocess fallback")


class ServiceStatus(Enum):
    """Windows service status"""
    STOPPED = "STOPPED"
    START_PENDING = "START_PENDING"
    STOP_PENDING = "STOP_PENDING"
    RUNNING = "RUNNING"
    CONTINUE_PENDING = "CONTINUE_PENDING"
    PAUSE_PENDING = "PAUSE_PENDING"
    PAUSED = "PAUSED"
    UNKNOWN = "UNKNOWN"
    NOT_FOUND = "NOT_FOUND"


@dataclass
class ServiceInfo:
    """Service information"""
    name: str
    display_name: str
    status: ServiceStatus
    pid: Optional[int] = None
    start_type: Optional[str] = None
    description: Optional[str] = None


class JARVISWindowsServiceManager:
    """
    Windows Service Manager for JARVIS

    Manages Windows services using win32service or subprocess fallback.
    """

    def __init__(self):
        self.logger = logger
        self.use_win32 = WIN32_AVAILABLE

        if self.use_win32:
            self.logger.info("✅ Using win32service for service management")
        else:
            self.logger.info("⚠️  Using subprocess (sc.exe) for service management")

        # Service name mappings (common names to Windows service names)
        self.service_mappings: Dict[str, str] = {
            "ollama": "Ollama",  # May need adjustment based on actual service name
            "n8n": "n8n",  # May need adjustment
            "docker": "com.docker.service",
            "docker_desktop": "com.docker.service",
        }

    def get_service_status(self, service_name: str) -> Tuple[ServiceStatus, Optional[ServiceInfo]]:
        """
        Get service status

        Args:
            service_name: Service name or mapped name

        Returns:
            Tuple of (ServiceStatus, Optional[ServiceInfo])
        """
        # Resolve service name
        actual_name = self.service_mappings.get(service_name.lower(), service_name)

        try:
            if self.use_win32:
                return self._get_status_win32(actual_name)
            else:
                return self._get_status_subprocess(actual_name)
        except Exception as e:
            self.logger.warning(f"⚠️  Error getting service status for {service_name}: {e}")
            return (ServiceStatus.UNKNOWN, None)

    def _get_status_win32(self, service_name: str) -> Tuple[ServiceStatus, Optional[ServiceInfo]]:
        """Get service status using win32service"""
        try:
            # Query service status
            hscm = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_CONNECT)
            try:
                hservice = win32service.OpenService(
                    hscm,
                    service_name,
                    win32service.SERVICE_QUERY_STATUS
                )
                try:
                    status = win32service.QueryServiceStatus(hservice)
                    status_code = status[1]

                    # Map status code to ServiceStatus
                    status_map = {
                        win32service.SERVICE_STOPPED: ServiceStatus.STOPPED,
                        win32service.SERVICE_START_PENDING: ServiceStatus.START_PENDING,
                        win32service.SERVICE_STOP_PENDING: ServiceStatus.STOP_PENDING,
                        win32service.SERVICE_RUNNING: ServiceStatus.RUNNING,
                        win32service.SERVICE_CONTINUE_PENDING: ServiceStatus.CONTINUE_PENDING,
                        win32service.SERVICE_PAUSE_PENDING: ServiceStatus.PAUSE_PENDING,
                        win32service.SERVICE_PAUSED: ServiceStatus.PAUSED,
                    }

                    service_status = status_map.get(status_code, ServiceStatus.UNKNOWN)

                    # Get service info
                    service_info = ServiceInfo(
                        name=service_name,
                        display_name=service_name,
                        status=service_status,
                        pid=status[4] if status[4] else None
                    )

                    return (service_status, service_info)

                finally:
                    win32service.CloseServiceHandle(hservice)
            finally:
                win32service.CloseServiceHandle(hscm)

        except win32service.error as e:
            if e.winerror == 1060:  # Service does not exist
                return (ServiceStatus.NOT_FOUND, None)
            else:
                self.logger.warning(f"⚠️  win32service error: {e}")
                return (ServiceStatus.UNKNOWN, None)
        except Exception as e:
            self.logger.warning(f"⚠️  Error querying service: {e}")
            return (ServiceStatus.UNKNOWN, None)

    def _get_status_subprocess(self, service_name: str) -> Tuple[ServiceStatus, Optional[ServiceInfo]]:
        """Get service status using subprocess (sc.exe)"""
        try:
            result = subprocess.run(
                ["sc", "query", service_name],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if result.returncode != 0:
                if "does not exist" in result.stderr.lower() or "1060" in result.stderr:
                    return (ServiceStatus.NOT_FOUND, None)
                else:
                    return (ServiceStatus.UNKNOWN, None)

            # Parse output
            output = result.stdout
            status_line = None
            for line in output.split('\n'):
                if 'STATE' in line.upper():
                    status_line = line
                    break

            if not status_line:
                return (ServiceStatus.UNKNOWN, None)

            # Parse status
            if 'RUNNING' in status_line.upper():
                status = ServiceStatus.RUNNING
            elif 'STOPPED' in status_line.upper():
                status = ServiceStatus.STOPPED
            elif 'START_PENDING' in status_line.upper():
                status = ServiceStatus.START_PENDING
            elif 'STOP_PENDING' in status_line.upper():
                status = ServiceStatus.STOP_PENDING
            else:
                status = ServiceStatus.UNKNOWN

            service_info = ServiceInfo(
                name=service_name,
                display_name=service_name,
                status=status
            )

            return (status, service_info)

        except FileNotFoundError:
            self.logger.warning("⚠️  sc.exe not found - cannot query services")
            return (ServiceStatus.UNKNOWN, None)
        except subprocess.TimeoutExpired:
            self.logger.warning(f"⚠️  Timeout querying service {service_name}")
            return (ServiceStatus.UNKNOWN, None)
        except Exception as e:
            self.logger.warning(f"⚠️  Error querying service: {e}")
            return (ServiceStatus.UNKNOWN, None)

    def start_service(self, service_name: str, timeout: int = 30) -> Tuple[bool, str]:
        """
        Start a Windows service

        Args:
            service_name: Service name or mapped name
            timeout: Timeout in seconds

        Returns:
            Tuple of (success: bool, message: str)
        """
        # Resolve service name
        actual_name = self.service_mappings.get(service_name.lower(), service_name)

        # Check current status
        status, info = self.get_service_status(actual_name)

        if status == ServiceStatus.RUNNING:
            return (True, f"Service {actual_name} is already running")

        if status == ServiceStatus.NOT_FOUND:
            return (False, f"Service {actual_name} not found")

        try:
            if self.use_win32:
                return self._start_service_win32(actual_name, timeout)
            else:
                return self._start_service_subprocess(actual_name, timeout)
        except Exception as e:
            self.logger.warning(f"⚠️  Error starting service {service_name}: {e}")
            return (False, f"Error starting service: {str(e)}")

    def _start_service_win32(self, service_name: str, timeout: int) -> Tuple[bool, str]:
        """Start service using win32service"""
        try:
            # Start service
            win32serviceutil.StartService(service_name)

            # Wait for service to start
            start_time = time.time()
            while time.time() - start_time < timeout:
                status, _ = self._get_status_win32(service_name)
                if status == ServiceStatus.RUNNING:
                    return (True, f"Service {service_name} started successfully")
                elif status == ServiceStatus.STOPPED:
                    # Service failed to start
                    return (False, f"Service {service_name} failed to start")
                time.sleep(1)

            # Timeout
            return (False, f"Service {service_name} start timeout after {timeout}s")

        except win32service.error as e:
            if e.winerror == 1056:  # Service already running
                return (True, f"Service {service_name} is already running")
            elif e.winerror == 1060:  # Service does not exist
                return (False, f"Service {service_name} not found")
            else:
                return (False, f"Error starting service: {e}")
        except Exception as e:
            return (False, f"Error starting service: {str(e)}")

    def _start_service_subprocess(self, service_name: str, timeout: int) -> Tuple[bool, str]:
        """Start service using subprocess (sc.exe)"""
        try:
            # Start service
            result = subprocess.run(
                ["sc", "start", service_name],
                capture_output=True,
                text=True,
                timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if result.returncode == 0:
                # Wait for service to start
                start_time = time.time()
                while time.time() - start_time < timeout:
                    status, _ = self.get_service_status(service_name)
                    if status == ServiceStatus.RUNNING:
                        return (True, f"Service {service_name} started successfully")
                    elif status == ServiceStatus.STOPPED:
                        return (False, f"Service {service_name} failed to start")
                    time.sleep(1)

                # Check final status
                status, _ = self.get_service_status(service_name)
                if status == ServiceStatus.RUNNING:
                    return (True, f"Service {service_name} started successfully")
                else:
                    return (False, f"Service {service_name} start timeout or failed")
            else:
                error_msg = result.stderr or result.stdout
                if "already running" in error_msg.lower():
                    return (True, f"Service {service_name} is already running")
                elif "does not exist" in error_msg.lower() or "1060" in error_msg:
                    return (False, f"Service {service_name} not found")
                else:
                    return (False, f"Error starting service: {error_msg}")

        except subprocess.TimeoutExpired:
            return (False, f"Service {service_name} start timeout after {timeout}s")
        except FileNotFoundError:
            return (False, "sc.exe not found - cannot start services")
        except Exception as e:
            return (False, f"Error starting service: {str(e)}")

    def stop_service(self, service_name: str, timeout: int = 30) -> Tuple[bool, str]:
        """
        Stop a Windows service

        Args:
            service_name: Service name or mapped name
            timeout: Timeout in seconds

        Returns:
            Tuple of (success: bool, message: str)
        """
        # Resolve service name
        actual_name = self.service_mappings.get(service_name.lower(), service_name)

        # Check current status
        status, info = self.get_service_status(actual_name)

        if status == ServiceStatus.STOPPED:
            return (True, f"Service {actual_name} is already stopped")

        if status == ServiceStatus.NOT_FOUND:
            return (False, f"Service {actual_name} not found")

        try:
            if self.use_win32:
                return self._stop_service_win32(actual_name, timeout)
            else:
                return self._stop_service_subprocess(actual_name, timeout)
        except Exception as e:
            self.logger.warning(f"⚠️  Error stopping service {service_name}: {e}")
            return (False, f"Error stopping service: {str(e)}")

    def _stop_service_win32(self, service_name: str, timeout: int) -> Tuple[bool, str]:
        """Stop service using win32service"""
        try:
            # Stop service
            win32serviceutil.StopService(service_name)

            # Wait for service to stop
            start_time = time.time()
            while time.time() - start_time < timeout:
                status, _ = self._get_status_win32(service_name)
                if status == ServiceStatus.STOPPED:
                    return (True, f"Service {service_name} stopped successfully")
                time.sleep(1)

            return (False, f"Service {service_name} stop timeout after {timeout}s")

        except win32service.error as e:
            if e.winerror == 1062:  # Service already stopped
                return (True, f"Service {service_name} is already stopped")
            else:
                return (False, f"Error stopping service: {e}")
        except Exception as e:
            return (False, f"Error stopping service: {str(e)}")

    def _stop_service_subprocess(self, service_name: str, timeout: int) -> Tuple[bool, str]:
        """Stop service using subprocess (sc.exe)"""
        try:
            result = subprocess.run(
                ["sc", "stop", service_name],
                capture_output=True,
                text=True,
                timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            if result.returncode == 0:
                # Wait for service to stop
                start_time = time.time()
                while time.time() - start_time < timeout:
                    status, _ = self.get_service_status(service_name)
                    if status == ServiceStatus.STOPPED:
                        return (True, f"Service {service_name} stopped successfully")
                    time.sleep(1)

                return (False, f"Service {service_name} stop timeout after {timeout}s")
            else:
                error_msg = result.stderr or result.stdout
                if "already stopped" in error_msg.lower():
                    return (True, f"Service {service_name} is already stopped")
                else:
                    return (False, f"Error stopping service: {error_msg}")

        except subprocess.TimeoutExpired:
            return (False, f"Service {service_name} stop timeout after {timeout}s")
        except FileNotFoundError:
            return (False, "sc.exe not found - cannot stop services")
        except Exception as e:
            return (False, f"Error stopping service: {str(e)}")

    def restart_service(self, service_name: str, timeout: int = 60) -> Tuple[bool, str]:
        """
        Restart a Windows service

        Args:
            service_name: Service name or mapped name
            timeout: Total timeout in seconds (for stop + start)

        Returns:
            Tuple of (success: bool, message: str)
        """
        # Resolve service name
        actual_name = self.service_mappings.get(service_name.lower(), service_name)

        self.logger.info(f"   Restarting service {actual_name}...")

        # Stop service
        stop_success, stop_msg = self.stop_service(actual_name, timeout // 2)
        if not stop_success and "already stopped" not in stop_msg.lower():
            return (False, f"Failed to stop service: {stop_msg}")

        # Wait a moment
        time.sleep(2)

        # Start service
        start_success, start_msg = self.start_service(actual_name, timeout // 2)
        if not start_success:
            return (False, f"Failed to start service: {start_msg}")

        return (True, f"Service {actual_name} restarted successfully")

    def add_service_mapping(self, alias: str, service_name: str):
        """Add a service name mapping"""
        self.service_mappings[alias.lower()] = service_name
        self.logger.info(f"   Added service mapping: {alias} -> {service_name}")

    def list_services(self, pattern: Optional[str] = None) -> List[ServiceInfo]:
        """
        List services (limited - requires admin or specific permissions)

        Args:
            pattern: Optional pattern to filter services

        Returns:
            List of ServiceInfo
        """
        # This is a simplified version - full implementation would query all services
        # For now, return services we know about
        services = []

        for alias, service_name in self.service_mappings.items():
            status, info = self.get_service_status(service_name)
            if info:
                if not pattern or pattern.lower() in service_name.lower() or pattern.lower() in alias.lower():
                    services.append(info)

        return services


def main():
    """CLI entry point for testing"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Windows Service Manager")
    parser.add_argument('action', choices=['status', 'start', 'stop', 'restart', 'list'],
                       help='Action to perform')
    parser.add_argument('service', nargs='?', help='Service name')
    parser.add_argument('--timeout', type=int, default=30, help='Timeout in seconds')

    args = parser.parse_args()

    manager = JARVISWindowsServiceManager()

    if args.action == 'status':
        if not args.service:
            print("Error: Service name required for status")
            return 1
        status, info = manager.get_service_status(args.service)
        print(f"Service: {args.service}")
        print(f"Status: {status.value}")
        if info:
            print(f"PID: {info.pid}")
        return 0

    elif args.action == 'start':
        if not args.service:
            print("Error: Service name required for start")
            return 1
        success, msg = manager.start_service(args.service, args.timeout)
        print(msg)
        return 0 if success else 1

    elif args.action == 'stop':
        if not args.service:
            print("Error: Service name required for stop")
            return 1
        success, msg = manager.stop_service(args.service, args.timeout)
        print(msg)
        return 0 if success else 1

    elif args.action == 'restart':
        if not args.service:
            print("Error: Service name required for restart")
            return 1
        success, msg = manager.restart_service(args.service, args.timeout)
        print(msg)
        return 0 if success else 1

    elif args.action == 'list':
        services = manager.list_services(args.service)
        print(f"Found {len(services)} services:")
        for service in services:
            print(f"  {service.name}: {service.status.value}")
        return 0

    return 0


if __name__ == "__main__":


    sys.exit(main())