#!/usr/bin/env python3
"""
Infrastructure Orchestrator

Start/stop/restart services and infrastructure components.
Part of Phase 2: Infrastructure Orchestration

Provides unified interface for managing:
- Windows services
- NAS services
- Applications/processes
- Network services
- Docker containers (if available)
"""

import sys
import json
import logging
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from jarvis_lumina_master_orchestrator import SubAgent


script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("InfrastructureOrchestrator")


class ServiceType(Enum):
    """Types of services/components"""
    WINDOWS_SERVICE = "windows_service"
    NAS_SERVICE = "nas_service"
    APPLICATION = "application"
    PROCESS = "process"
    NETWORK_SERVICE = "network_service"
    DOCKER_CONTAINER = "docker_container"


class ServiceStatus(Enum):
    """Service status"""
    RUNNING = "running"
    STOPPED = "stopped"
    STARTING = "starting"
    STOPPING = "stopping"
    UNKNOWN = "unknown"
    ERROR = "error"


@dataclass
class ServiceDefinition:
    """Definition of a service/component"""
    service_id: str
    service_type: ServiceType
    name: str
    description: str
    start_command: Optional[str] = None
    stop_command: Optional[str] = None
    restart_command: Optional[str] = None
    status_command: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 30  # seconds
    retry_count: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationResult:
    """Result of an orchestration operation"""
    operation_id: str
    service_id: str
    operation: str  # start, stop, restart, status
    success: bool
    message: str
    status: Optional[ServiceStatus] = None
    duration: float = 0.0
    errors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class InfrastructureOrchestrator:
    """
    Infrastructure Orchestrator

    Unified interface for managing services and infrastructure components.
    """

    def __init__(self, project_root: Path):
        """Initialize infrastructure orchestrator"""
        self.project_root = Path(project_root)
        self.services: Dict[str, ServiceDefinition] = {}
        self.operation_history: List[OrchestrationResult] = []
        self.is_windows = platform.system() == "Windows"

        # Initialize service definitions
        self._initialize_service_definitions()

        logger.info("Infrastructure Orchestrator initialized")

        # SubAgent registry (Puppetmaster delegation via @SUBAGENTS)
        self.subagents = {}
        self._init_subagents()

    def _init_subagents(self) -> None:
        """Initialize subagents"""
        # Placeholder for subagent initialization
        pass

    def _initialize_service_definitions(self) -> None:
        """Initialize default service definitions"""
        # Windows services
        if self.is_windows:
            # Example Windows services
            self.services["windows_update"] = ServiceDefinition(
                service_id="windows_update",
                service_type=ServiceType.WINDOWS_SERVICE,
                name="Windows Update",
                description="Windows Update service",
                start_command="sc start wuauserv",
                stop_command="sc stop wuauserv",
                status_command="sc query wuauserv",
                timeout=60
            )

        # NAS services (placeholder - would integrate with NAS API)
        self.services["nas_dsm"] = ServiceDefinition(
            service_id="nas_dsm",
            service_type=ServiceType.NAS_SERVICE,
            name="NAS DSM",
            description="Synology DiskStation Manager",
            start_command="nas_api_start_dsm",
            stop_command="nas_api_stop_dsm",
            status_command="nas_api_status_dsm",
            timeout=120
        )

        # Applications
        self.services["cursor_ide"] = ServiceDefinition(
            service_id="cursor_ide",
            service_type=ServiceType.APPLICATION,
            name="Cursor IDE",
            description="Cursor IDE application",
            start_command="cursor",
            stop_command="taskkill /F /IM Cursor.exe" if self.is_windows else "pkill -f Cursor",
            timeout=30
        )

        # Iron Legion Docker Containers (KAIJU_NO_8 - <NAS_IP>)
        iron_legion_containers = [
            ("iron-legion-router", 3000, "Iron Legion Main Router"),
            ("iron-legion-mark-1", 3001, "Mark I - Code Expert"),
            ("iron-legion-mark-2", 3002, "Mark II - General Purpose"),
            ("iron-legion-mark-3", 3003, "Mark III - Quick Response"),
            ("iron-legion-mark-4", 3004, "Mark IV - Balanced Expert"),
            ("iron-legion-mark-5", 3005, "Mark V - Reasoning Expert"),
            ("iron-legion-mark-6", 3006, "Mark VI - Complex Expert"),
            ("iron-legion-mark-7", 3007, "Mark VII - Fallback Expert"),
        ]

        for container_id, port, description in iron_legion_containers:
            self.services[container_id] = ServiceDefinition(
                service_id=container_id,
                service_type=ServiceType.DOCKER_CONTAINER,
                name=container_id,
                description=description,
                start_command=f"ssh user@<NAS_IP> 'docker start {container_id}'",
                stop_command=f"ssh user@<NAS_IP> 'docker stop {container_id}'",
                restart_command=f"ssh user@<NAS_IP> 'docker restart {container_id}'",
                status_command=f"ssh user@<NAS_IP> 'docker ps --filter name={container_id} --format \"{{{{.Status}}}}\"'",
                timeout=60,
                metadata={"host": "<NAS_IP>", "port": port}
            )

        logger.info(f"Initialized {len(self.services)} service definitions")

    def register_service(self, service: ServiceDefinition) -> None:
        """Register a new service definition"""
        self.services[service.service_id] = service
        logger.info(f"Registered service: {service.service_id}")

    def start_service(self, service_id: str) -> OrchestrationResult:
        """
        Start a service

        Args:
            service_id: ID of service to start

        Returns:
            OrchestrationResult with success status
        """
        start_time = datetime.now()
        operation_id = f"start_{service_id}_{int(start_time.timestamp())}"

        try:
            service = self.services.get(service_id)
            if not service:
                return OrchestrationResult(
                    operation_id=operation_id,
                    service_id=service_id,
                    operation="start",
                    success=False,
                    message=f"Service not found: {service_id}",
                    errors=[f"Service {service_id} not registered"]
                )

            # Check dependencies
            for dep_id in service.dependencies:
                dep_status = self.get_service_status(dep_id)
                if dep_status.status != ServiceStatus.RUNNING:
                    logger.info(f"Starting dependency: {dep_id}")
                    dep_result = self.start_service(dep_id)
                    if not dep_result.success:
                        return OrchestrationResult(
                            operation_id=operation_id,
                            service_id=service_id,
                            operation="start",
                            success=False,
                            message=f"Dependency {dep_id} failed to start",
                            errors=[f"Dependency start failed: {dep_result.message}"]
                        )

            # Execute start command
            if service.start_command:
                success, message, errors = self._execute_command(
                    service.start_command,
                    service.service_type,
                    service.timeout
                )
            else:
                success, message, errors = self._start_by_type(service)

            duration = (datetime.now() - start_time).total_seconds()

            # Get status after start
            status_result = self.get_service_status(service_id)

            result = OrchestrationResult(
                operation_id=operation_id,
                service_id=service_id,
                operation="start",
                success=success and status_result.status == ServiceStatus.RUNNING,
                message=message,
                status=status_result.status,
                duration=duration,
                errors=errors
            )

            self.operation_history.append(result)
            return result

        except Exception as e:
            logger.error(f"Error starting service {service_id}: {e}", exc_info=True)
            duration = (datetime.now() - start_time).total_seconds()
            return OrchestrationResult(
                operation_id=operation_id,
                service_id=service_id,
                operation="start",
                success=False,
                message=f"Error: {str(e)}",
                duration=duration,
                errors=[str(e)]
            )

    def stop_service(self, service_id: str) -> OrchestrationResult:
        """
        Stop a service

        Args:
            service_id: ID of service to stop

        Returns:
            OrchestrationResult with success status
        """
        start_time = datetime.now()
        operation_id = f"stop_{service_id}_{int(start_time.timestamp())}"

        try:
            service = self.services.get(service_id)
            if not service:
                return OrchestrationResult(
                    operation_id=operation_id,
                    service_id=service_id,
                    operation="stop",
                    success=False,
                    message=f"Service not found: {service_id}",
                    errors=[f"Service {service_id} not registered"]
                )

            # Execute stop command
            if service.stop_command:
                success, message, errors = self._execute_command(
                    service.stop_command,
                    service.service_type,
                    service.timeout
                )
            else:
                success, message, errors = self._stop_by_type(service)

            duration = (datetime.now() - start_time).total_seconds()

            # Get status after stop
            status_result = self.get_service_status(service_id)

            result = OrchestrationResult(
                operation_id=operation_id,
                service_id=service_id,
                operation="stop",
                success=success and status_result.status == ServiceStatus.STOPPED,
                message=message,
                status=status_result.status,
                duration=duration,
                errors=errors
            )

            self.operation_history.append(result)
            return result

        except Exception as e:
            logger.error(f"Error stopping service {service_id}: {e}", exc_info=True)
            duration = (datetime.now() - start_time).total_seconds()
            return OrchestrationResult(
                operation_id=operation_id,
                service_id=service_id,
                operation="stop",
                success=False,
                message=f"Error: {str(e)}",
                duration=duration,
                errors=[str(e)]
            )

    def restart_service(self, service_id: str) -> OrchestrationResult:
        """
        Restart a service

        Args:
            service_id: ID of service to restart

        Returns:
            OrchestrationResult with success status
        """
        # Stop first
        stop_result = self.stop_service(service_id)
        if not stop_result.success:
            return OrchestrationResult(
                operation_id=f"restart_{service_id}_{int(datetime.now().timestamp())}",
                service_id=service_id,
                operation="restart",
                success=False,
                message=f"Failed to stop service: {stop_result.message}",
                errors=stop_result.errors
            )

        # Wait a moment
        import time
        time.sleep(2)

        # Start
        start_result = self.start_service(service_id)

        # Combined result
        return OrchestrationResult(
            operation_id=f"restart_{service_id}_{int(datetime.now().timestamp())}",
            service_id=service_id,
            operation="restart",
            success=start_result.success,
            message=f"Restart: stop={stop_result.success}, start={start_result.success}",
            status=start_result.status,
            duration=stop_result.duration + start_result.duration,
            errors=stop_result.errors + start_result.errors
        )

    def get_service_status(self, service_id: str) -> OrchestrationResult:
        """
        Get status of a service

        Args:
            service_id: ID of service to check

        Returns:
            OrchestrationResult with status
        """
        try:
            service = self.services.get(service_id)
            if not service:
                return OrchestrationResult(
                    operation_id=f"status_{service_id}_{int(datetime.now().timestamp())}",
                    service_id=service_id,
                    operation="status",
                    success=False,
                    message=f"Service not found: {service_id}",
                    status=ServiceStatus.UNKNOWN
                )

            # Check status by type
            status = self._check_status_by_type(service)

            return OrchestrationResult(
                operation_id=f"status_{service_id}_{int(datetime.now().timestamp())}",
                service_id=service_id,
                operation="status",
                success=True,
                message=f"Status: {status.value}",
                status=status
            )

        except Exception as e:
            logger.error(f"Error getting status for {service_id}: {e}")
            return OrchestrationResult(
                operation_id=f"status_{service_id}_{int(datetime.now().timestamp())}",
                service_id=service_id,
                operation="status",
                success=False,
                message=f"Error: {str(e)}",
                status=ServiceStatus.ERROR
            )

    def _execute_command(self, command: str, service_type: ServiceType, timeout: int) -> Tuple[bool, str, List[str]]:
        """Execute a command"""
        try:
            if self.is_windows:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
            else:
                result = subprocess.run(
                    command.split(),
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )

            success = result.returncode == 0
            message = result.stdout.strip() if success else result.stderr.strip()
            errors = [] if success else [result.stderr.strip()] if result.stderr else []

            return success, message, errors

        except subprocess.TimeoutExpired:
            return False, f"Command timed out after {timeout}s", ["Timeout"]
        except Exception as e:
            return False, f"Command execution failed: {str(e)}", [str(e)]

    def _start_by_type(self, service: ServiceDefinition) -> Tuple[bool, str, List[str]]:
        """Start service based on type"""
        if service.service_type == ServiceType.WINDOWS_SERVICE:
            return self._start_windows_service(service)
        elif service.service_type == ServiceType.APPLICATION:
            return self._start_application(service)
        else:
            return False, f"Unsupported service type: {service.service_type}", ["Unsupported type"]

    def _stop_by_type(self, service: ServiceDefinition) -> Tuple[bool, str, List[str]]:
        """Stop service based on type"""
        if service.service_type == ServiceType.WINDOWS_SERVICE:
            return self._stop_windows_service(service)
        elif service.service_type == ServiceType.APPLICATION:
            return self._stop_application(service)
        else:
            return False, f"Unsupported service type: {service.service_type}", ["Unsupported type"]

    def _check_status_by_type(self, service: ServiceDefinition) -> ServiceStatus:
        """Check status based on type"""
        if service.service_type == ServiceType.WINDOWS_SERVICE:
            return self._check_windows_service_status(service)
        elif service.service_type == ServiceType.APPLICATION:
            return self._check_application_status(service)
        else:
            return ServiceStatus.UNKNOWN

    def _start_windows_service(self, service: ServiceDefinition) -> Tuple[bool, str, List[str]]:
        """Start Windows service"""
        if not self.is_windows:
            return False, "Not on Windows", ["Platform mismatch"]

        command = f'sc start "{service.name}"'
        return self._execute_command(command, service.service_type, service.timeout)

    def _stop_windows_service(self, service: ServiceDefinition) -> Tuple[bool, str, List[str]]:
        """Stop Windows service"""
        if not self.is_windows:
            return False, "Not on Windows", ["Platform mismatch"]

        command = f'sc stop "{service.name}"'
        return self._execute_command(command, service.service_type, service.timeout)

    def _check_windows_service_status(self, service: ServiceDefinition) -> ServiceStatus:
        """Check Windows service status"""
        if not self.is_windows:
            return ServiceStatus.UNKNOWN

        try:
            command = f'sc query "{service.name}"'
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )

            if "RUNNING" in result.stdout:
                return ServiceStatus.RUNNING
            elif "STOPPED" in result.stdout:
                return ServiceStatus.STOPPED
            else:
                return ServiceStatus.UNKNOWN
        except Exception:
            return ServiceStatus.UNKNOWN

    def _start_application(self, service: ServiceDefinition) -> Tuple[bool, str, List[str]]:
        """Start application"""
        if service.start_command:
            return self._execute_command(service.start_command, service.service_type, service.timeout)
        return False, "No start command defined", ["No command"]

    def _stop_application(self, service: ServiceDefinition) -> Tuple[bool, str, List[str]]:
        """Stop application"""
        if service.stop_command:
            return self._execute_command(service.stop_command, service.service_type, service.timeout)
        return False, "No stop command defined", ["No command"]

    def _check_application_status(self, service: ServiceDefinition) -> ServiceStatus:
        """Check application status"""
        try:
            if self.is_windows:
                command = f'tasklist /FI "IMAGENAME eq {service.name}.exe"'
            else:
                command = f'pgrep -f "{service.name}"'

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 and result.stdout.strip():
                return ServiceStatus.RUNNING
            else:
                return ServiceStatus.STOPPED
        except Exception:
            return ServiceStatus.UNKNOWN

    def list_services(self) -> List[Dict[str, Any]]:
        """List all registered services"""
        return [
            {
                "service_id": svc.service_id,
                "name": svc.name,
                "type": svc.service_type.value,
                "description": svc.description,
                "status": self.get_service_status(svc.service_id).status.value
            }
            for svc in self.services.values()
        ]

    def get_operation_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get operation history"""
        recent = self.operation_history[-limit:]
        return [
            {
                "operation_id": r.operation_id,
                "service_id": r.service_id,
                "operation": r.operation,
                "success": r.success,
                "message": r.message,
                "status": r.status.value if r.status else None,
                "duration": r.duration,
                "timestamp": r.timestamp.isoformat()
            }
            for r in recent
        ]


def main():
    try:
        """CLI interface for Infrastructure Orchestrator"""
        import argparse

        parser = argparse.ArgumentParser(description="Infrastructure Orchestrator")
        parser.add_argument("--service", help="Service ID")
        parser.add_argument("--action", choices=["start", "stop", "restart", "status"], help="Action")
        parser.add_argument("--list", action="store_true", help="List all services")
        parser.add_argument("--history", type=int, help="Show operation history (limit)")

        args = parser.parse_args()

        orchestrator = InfrastructureOrchestrator(project_root)

        if args.list:
            services = orchestrator.list_services()
            print(json.dumps(services, indent=2))
            return

        if args.history:
            history = orchestrator.get_operation_history(args.history)
            print(json.dumps(history, indent=2))
            return

        # Execute operation (requires both service and action)
        if not args.service or not args.action:
            parser.print_help()
            return

        if args.action == "start":
            result = orchestrator.start_service(args.service)
        elif args.action == "stop":
            result = orchestrator.stop_service(args.service)
        elif args.action == "restart":
            result = orchestrator.restart_service(args.service)
        elif args.action == "status":
            result = orchestrator.get_service_status(args.service)
        else:
            parser.print_help()
            return

        print(json.dumps({
            "operation_id": result.operation_id,
            "service_id": result.service_id,
            "operation": result.operation,
            "success": result.success,
            "message": result.message,
            "status": result.status.value if result.status else None,
            "duration": result.duration,
            "errors": result.errors
        }, indent=2))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise

if __name__ == "__main__":

    main()