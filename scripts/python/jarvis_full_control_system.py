#!/usr/bin/env python3
"""
JARVIS Full Control System
🤖 MASTER CONTROL OVER ALL ENVIRONMENT & ECOSYSTEM

Unified master control system for JARVIS to manage:
- Environment: Hardware, lighting, power, system settings, services
- Ecosystem: AI systems, applications, network, storage, automation
- Integration: MANUS, Unified API, AI Actions, all control systems

This is the single point of control for JARVIS to manage everything.

#JARVIS #FULL_CONTROL #ENVIRONMENT #ECOSYSTEM #MASTER_CONTROL
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISFullControl")


class ControlDomain(Enum):
    """Control domains for full environment/ecosystem control"""
    # Environment Control
    HARDWARE = "hardware"  # Hardware control (lighting, power, peripherals)
    SYSTEM = "system"  # System settings, services, processes
    NETWORK = "network"  # Network configuration, connectivity
    STORAGE = "storage"  # Storage management, backups

    # Ecosystem Control
    AI_SYSTEMS = "ai_systems"  # All AI systems (LLMs, agents, assistants)
    APPLICATIONS = "applications"  # Application control (browsers, IDEs, tools)
    AUTOMATION = "automation"  # Automation workflows, scripts
    DATA = "data"  # Data management, lifecycle

    # Integration Control
    MANUS = "manus"  # MANUS unified control
    UNIFIED_API = "unified_api"  # JARVIS Unified API
    AI_ACTIONS = "ai_actions"  # AI Actions (Synology, Unified AI)


@dataclass
class ControlCommand:
    """A control command"""
    command_id: str
    domain: ControlDomain
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5  # 1-10, higher is more urgent
    timeout: int = 300  # seconds
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ControlResult:
    """Result of a control command"""
    command_id: str
    success: bool
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    duration: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class JARVISFullControlSystem:
    """
    JARVIS Full Control System

    Master control system for complete environment and ecosystem management.
    Integrates all control systems into a single unified interface.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize JARVIS Full Control System"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.controllers: Dict[ControlDomain, Any] = {}
        self.command_history: List[ControlResult] = []
        self.health_status: Dict[str, Any] = {}

        # Initialize all controllers
        self._initialize_controllers()

        logger.info("🤖 JARVIS Full Control System initialized")
        logger.info(f"   Control domains: {len(self.controllers)}/{len(ControlDomain)}")

    def _initialize_controllers(self) -> None:
        """Initialize controllers for each control domain"""

        # MANUS Unified Control
        try:
            from manus_unified_control import MANUSUnifiedControl
            manus_control = MANUSUnifiedControl(self.project_root)
            self.controllers[ControlDomain.MANUS] = manus_control
            logger.info("✅ MANUS Unified Control initialized")
        except Exception as e:
            logger.warning(f"⚠️  MANUS Unified Control not available: {e}")
            self.controllers[ControlDomain.MANUS] = None

        # JARVIS Unified API
        try:
            from jarvis_unified_api import JARVISUnifiedAPI
            unified_api = JARVISUnifiedAPI(self.project_root)
            self.controllers[ControlDomain.UNIFIED_API] = unified_api
            logger.info("✅ JARVIS Unified API initialized")
        except Exception as e:
            logger.warning(f"⚠️  JARVIS Unified API not available: {e}")
            self.controllers[ControlDomain.UNIFIED_API] = None

        # AI Actions (Synology, Unified AI)
        try:
            from jarvis_synology_ai_actions import JARVISSynologyAIActions
            from jarvis_unified_ai_actions import JARVISUnifiedAIActions
            synology_ai = JARVISSynologyAIActions()
            unified_ai = JARVISUnifiedAIActions(self.project_root)
            self.controllers[ControlDomain.AI_ACTIONS] = {
                "synology": synology_ai,
                "unified_ai": unified_ai
            }
            logger.info("✅ AI Actions initialized (Synology + Unified AI)")
        except Exception as e:
            logger.warning(f"⚠️  AI Actions not available: {e}")
            self.controllers[ControlDomain.AI_ACTIONS] = None

        # Hardware Control (Lighting, Power, Peripherals)
        try:
            # Try to import hardware control systems
            hardware_controllers = {}

            # Armoury Crate / Lighting Control
            try:
                from armoury_crate_manager import ArmouryCrateManager
                hardware_controllers["lighting"] = ArmouryCrateManager()
                logger.info("   ✓ Lighting control available")
            except:
                pass

            # GPU Control
            try:
                from jarvis_gpu_balance_controller import JARVISGPUBalanceController
                hardware_controllers["gpu"] = JARVISGPUBalanceController()
                logger.info("   ✓ GPU control available")
            except:
                pass

            if hardware_controllers:
                self.controllers[ControlDomain.HARDWARE] = hardware_controllers
                logger.info("✅ Hardware Control initialized")
            else:
                self.controllers[ControlDomain.HARDWARE] = None
        except Exception as e:
            logger.warning(f"⚠️  Hardware Control not available: {e}")
            self.controllers[ControlDomain.HARDWARE] = None

        # System Control (Services, Processes, Settings)
        try:
            from manus_workstation_controller import MANUSWorkstationController
            workstation_controller = MANUSWorkstationController(self.project_root)
            self.controllers[ControlDomain.SYSTEM] = workstation_controller
            logger.info("✅ System Control initialized (Workstation Controller)")
        except Exception as e:
            logger.warning(f"⚠️  System Control not available: {e}")
            self.controllers[ControlDomain.SYSTEM] = None

        # Network Control
        try:
            # Network monitoring and control
            network_controllers = {}

            # Try to import network control systems
            try:
                from infrastructure_orchestrator import InfrastructureOrchestrator
                network_controllers["orchestration"] = InfrastructureOrchestrator(self.project_root)
                logger.info("   ✓ Network orchestration available")
            except:
                pass

            if network_controllers:
                self.controllers[ControlDomain.NETWORK] = network_controllers
                logger.info("✅ Network Control initialized")
            else:
                self.controllers[ControlDomain.NETWORK] = None
        except Exception as e:
            logger.warning(f"⚠️  Network Control not available: {e}")
            self.controllers[ControlDomain.NETWORK] = None

        # Storage Control
        try:
            from syphon.core import SYPHONConfig, SubscriptionTier
            from syphon.storage import SyphonStorage
            from data_lifecycle_manager import DataLifecycleManager
            storage_config = SYPHONConfig(
                project_root=self.project_root,
                subscription_tier=SubscriptionTier.ENTERPRISE,
                enable_self_healing=True
            )
            storage = SyphonStorage(storage_config)
            lifecycle = DataLifecycleManager(self.project_root)
            self.controllers[ControlDomain.STORAGE] = {
                "storage": storage,
                "lifecycle": lifecycle
            }
            logger.info("✅ Storage Control initialized")
        except Exception as e:
            logger.warning(f"⚠️  Storage Control not available: {e}")
            self.controllers[ControlDomain.STORAGE] = None

        # AI Systems Control
        try:
            from jarvis_unified_ai_actions import JARVISUnifiedAIActions
            unified_ai = JARVISUnifiedAIActions(self.project_root)
            self.controllers[ControlDomain.AI_SYSTEMS] = unified_ai
            logger.info("✅ AI Systems Control initialized")
        except Exception as e:
            logger.warning(f"⚠️  AI Systems Control not available: {e}")
            self.controllers[ControlDomain.AI_SYSTEMS] = None

        # Applications Control (Browsers, IDEs, Tools)
        try:
            from manus_unified_control import MANUSUnifiedControl, ControlArea
            manus_control = self.controllers.get(ControlDomain.MANUS)
            if manus_control:
                # Use MANUS IDE control for applications
                self.controllers[ControlDomain.APPLICATIONS] = manus_control
                logger.info("✅ Applications Control initialized (via MANUS)")
            else:
                self.controllers[ControlDomain.APPLICATIONS] = None
        except Exception as e:
            logger.warning(f"⚠️  Applications Control not available: {e}")
            self.controllers[ControlDomain.APPLICATIONS] = None

        # Automation Control
        try:
            from manus_unified_control import MANUSUnifiedControl, ControlArea
            manus_control = self.controllers.get(ControlDomain.MANUS)
            if manus_control:
                # Use MANUS automation control
                self.controllers[ControlDomain.AUTOMATION] = manus_control
                logger.info("✅ Automation Control initialized (via MANUS)")
            else:
                self.controllers[ControlDomain.AUTOMATION] = None
        except Exception as e:
            logger.warning(f"⚠️  Automation Control not available: {e}")
            self.controllers[ControlDomain.AUTOMATION] = None

        # Data Control (same as storage, but for data operations)
        self.controllers[ControlDomain.DATA] = self.controllers.get(ControlDomain.STORAGE)
        if self.controllers[ControlDomain.DATA]:
            logger.info("✅ Data Control initialized (via Storage)")

    def execute_command(self, command: ControlCommand) -> ControlResult:
        """
        Execute a control command

        Args:
            command: Control command to execute

        Returns:
            ControlResult with success status and details
        """
        start_time = datetime.now()

        try:
            controller = self.controllers.get(command.domain)
            if controller is None:
                return ControlResult(
                    command_id=command.command_id,
                    success=False,
                    message=f"Controller for {command.domain.value} not available",
                    errors=[f"Controller not initialized for {command.domain.value}"]
                )

            # Route to appropriate controller method
            result = self._route_command(command, controller)

            duration = (datetime.now() - start_time).total_seconds()
            result.duration = duration
            result.command_id = command.command_id

            # Record in history
            self.command_history.append(result)
            if len(self.command_history) > 1000:
                self.command_history = self.command_history[-1000:]

            return result

        except Exception as e:
            logger.error(f"Error executing command {command.command_id}: {e}", exc_info=True)
            duration = (datetime.now() - start_time).total_seconds()
            return ControlResult(
                command_id=command.command_id,
                success=False,
                message=f"Command failed: {str(e)}",
                errors=[str(e)],
                duration=duration
            )

    def _route_command(self, command: ControlCommand, controller: Any) -> ControlResult:
        """Route command to appropriate controller method"""
        domain = command.domain
        action = command.action

        # Route by domain
        if domain == ControlDomain.MANUS:
            return self._handle_manus_command(command, controller)
        elif domain == ControlDomain.UNIFIED_API:
            return self._handle_unified_api_command(command, controller)
        elif domain == ControlDomain.AI_ACTIONS:
            return self._handle_ai_actions_command(command, controller)
        elif domain == ControlDomain.HARDWARE:
            return self._handle_hardware_command(command, controller)
        elif domain == ControlDomain.SYSTEM:
            return self._handle_system_command(command, controller)
        elif domain == ControlDomain.NETWORK:
            return self._handle_network_command(command, controller)
        elif domain == ControlDomain.STORAGE:
            return self._handle_storage_command(command, controller)
        elif domain == ControlDomain.AI_SYSTEMS:
            return self._handle_ai_systems_command(command, controller)
        elif domain == ControlDomain.APPLICATIONS:
            return self._handle_applications_command(command, controller)
        elif domain == ControlDomain.AUTOMATION:
            return self._handle_automation_command(command, controller)
        elif domain == ControlDomain.DATA:
            return self._handle_data_command(command, controller)
        else:
            return ControlResult(
                command_id=command.command_id,
                success=False,
                message=f"Unknown control domain: {domain}",
                errors=[f"Unsupported domain: {domain.value}"]
            )

    def _handle_manus_command(self, command: ControlCommand, controller: Any) -> ControlResult:
        """Handle MANUS control commands"""
        from manus_unified_control import ControlArea, ControlOperation

        try:
            # Convert to MANUS operation
            area_str = command.parameters.get("area", "ide_control")
            try:
                area = ControlArea(area_str)
            except ValueError:
                return ControlResult(
                    command_id=command.command_id,
                    success=False,
                    message=f"Invalid MANUS area: {area_str}",
                    errors=[f"Unknown area: {area_str}"]
                )

            operation = ControlOperation(
                operation_id=command.command_id,
                area=area,
                action=command.action,
                parameters=command.parameters.get("params", {}),
                priority=command.priority,
                timeout=command.timeout
            )

            result = controller.execute_operation(operation)

            return ControlResult(
                command_id=command.command_id,
                success=result.success,
                message=result.message,
                data=result.data,
                errors=result.errors,
                duration=result.duration
            )
        except Exception as e:
            return ControlResult(
                command_id=command.command_id,
                success=False,
                message=f"MANUS command failed: {str(e)}",
                errors=[str(e)]
            )

    def _handle_unified_api_command(self, command: ControlCommand, controller: Any) -> ControlResult:
        """Handle Unified API commands"""
        from jarvis_unified_api import RequestType

        try:
            request_type_str = command.parameters.get("request_type", "command")
            try:
                request_type = RequestType(request_type_str)
            except ValueError:
                return ControlResult(
                    command_id=command.command_id,
                    success=False,
                    message=f"Invalid request type: {request_type_str}",
                    errors=[f"Unknown request type: {request_type_str}"]
                )

            request_id = controller.send_request(
                request_type=request_type,
                source="jarvis_full_control",
                target=command.parameters.get("target"),
                payload=command.parameters.get("payload", {}),
                priority=command.priority
            )

            # Get response
            response = controller.get_response(request_id, timeout=command.timeout)

            if response:
                return ControlResult(
                    command_id=command.command_id,
                    success=response.success,
                    message=response.data.get("message", "Unified API command executed"),
                    data=response.data,
                    errors=[response.error] if response.error else []
                )
            else:
                return ControlResult(
                    command_id=command.command_id,
                    success=False,
                    message="Unified API command timeout",
                    errors=["Response timeout"]
                )
        except Exception as e:
            return ControlResult(
                command_id=command.command_id,
                success=False,
                message=f"Unified API command failed: {str(e)}",
                errors=[str(e)]
            )

    def _handle_ai_actions_command(self, command: ControlCommand, controller: Any) -> ControlResult:
        """Handle AI Actions commands"""
        try:
            ai_type = command.parameters.get("ai_type", "unified_ai")  # or "synology"

            if ai_type == "synology":
                ai_controller = controller.get("synology")
            elif ai_type == "unified_ai":
                ai_controller = controller.get("unified_ai")
            else:
                return ControlResult(
                    command_id=command.command_id,
                    success=False,
                    message=f"Unknown AI type: {ai_type}",
                    errors=[f"Unknown AI type: {ai_type}"]
                )

            if not ai_controller:
                return ControlResult(
                    command_id=command.command_id,
                    success=False,
                    message=f"AI controller not available: {ai_type}",
                    errors=[f"Controller not initialized: {ai_type}"]
                )

            # Execute action
            result = ai_controller.execute_action(
                command.action,
                **command.parameters.get("kwargs", {})
            )

            return ControlResult(
                command_id=command.command_id,
                success=result.get("success", False),
                message=result.get("message", "AI action executed"),
                data=result,
                errors=[result.get("error")] if result.get("error") else []
            )
        except Exception as e:
            return ControlResult(
                command_id=command.command_id,
                success=False,
                message=f"AI Actions command failed: {str(e)}",
                errors=[str(e)]
            )

    def _handle_hardware_command(self, command: ControlCommand, controller: Any) -> ControlResult:
        """Handle hardware control commands"""
        try:
            if not isinstance(controller, dict):
                return ControlResult(
                    command_id=command.command_id,
                    success=False,
                    message="Hardware controller not properly initialized",
                    errors=["Controller structure invalid"]
                )

            hardware_type = command.parameters.get("hardware_type", "lighting")
            hw_controller = controller.get(hardware_type)

            if not hw_controller:
                return ControlResult(
                    command_id=command.command_id,
                    success=False,
                    message=f"Hardware controller not available: {hardware_type}",
                    errors=[f"Controller not initialized: {hardware_type}"]
                )

            # Route to specific hardware controller
            if hardware_type == "lighting":
                if command.action == "disable_all":
                    # Disable all lighting
                    result = hw_controller.disable_all_lighting() if hasattr(hw_controller, 'disable_all_lighting') else {}
                    return ControlResult(
                        command_id=command.command_id,
                        success=result.get("success", False),
                        message=result.get("message", "Lighting disabled"),
                        data=result
                    )
                elif command.action == "get_status":
                    status = hw_controller.get_status() if hasattr(hw_controller, 'get_status') else {}
                    return ControlResult(
                        command_id=command.command_id,
                        success=True,
                        message="Hardware status retrieved",
                        data=status
                    )

            return ControlResult(
                command_id=command.command_id,
                success=False,
                message=f"Unknown hardware action: {command.action}",
                errors=[f"Unsupported action: {command.action}"]
            )
        except Exception as e:
            return ControlResult(
                command_id=command.command_id,
                success=False,
                message=f"Hardware command failed: {str(e)}",
                errors=[str(e)]
            )

    def _handle_system_command(self, command: ControlCommand, controller: Any) -> ControlResult:
        """Handle system control commands"""
        try:
            # Use MANUS workstation controller
            if command.action == "get_status":
                status = controller.get_complete_status() if hasattr(controller, 'get_complete_status') else {}
                return ControlResult(
                    command_id=command.command_id,
                    success=True,
                    message="System status retrieved",
                    data=status
                )
            elif command.action == "start_service":
                service_name = command.parameters.get("service_name")
                result = controller.start_service(service_name) if hasattr(controller, 'start_service') else {}
                return ControlResult(
                    command_id=command.command_id,
                    success=result.get("success", False),
                    message=f"Service {service_name} started",
                    data=result
                )
            elif command.action == "stop_service":
                service_name = command.parameters.get("service_name")
                result = controller.stop_service(service_name) if hasattr(controller, 'stop_service') else {}
                return ControlResult(
                    command_id=command.command_id,
                    success=result.get("success", False),
                    message=f"Service {service_name} stopped",
                    data=result
                )
            else:
                return ControlResult(
                    command_id=command.command_id,
                    success=False,
                    message=f"Unknown system action: {command.action}",
                    errors=[f"Unsupported action: {command.action}"]
                )
        except Exception as e:
            return ControlResult(
                command_id=command.command_id,
                success=False,
                message=f"System command failed: {str(e)}",
                errors=[str(e)]
            )

    def _handle_network_command(self, command: ControlCommand, controller: Any) -> ControlResult:
        """Handle network control commands"""
        try:
            if not isinstance(controller, dict):
                return ControlResult(
                    command_id=command.command_id,
                    success=False,
                    message="Network controller not properly initialized",
                    errors=["Controller structure invalid"]
                )

            orchestration = controller.get("orchestration")
            if orchestration and command.action == "get_status":
                services = orchestration.list_services() if hasattr(orchestration, 'list_services') else []
                return ControlResult(
                    command_id=command.command_id,
                    success=True,
                    message="Network status retrieved",
                    data={"services": services, "count": len(services)}
                )

            return ControlResult(
                command_id=command.command_id,
                success=False,
                message=f"Unknown network action: {command.action}",
                errors=[f"Unsupported action: {command.action}"]
            )
        except Exception as e:
            return ControlResult(
                command_id=command.command_id,
                success=False,
                message=f"Network command failed: {str(e)}",
                errors=[str(e)]
            )

    def _handle_storage_command(self, command: ControlCommand, controller: Any) -> ControlResult:
        """Handle storage control commands"""
        try:
            if not isinstance(controller, dict):
                return ControlResult(
                    command_id=command.command_id,
                    success=False,
                    message="Storage controller not properly initialized",
                    errors=["Controller structure invalid"]
                )

            storage = controller.get("storage")
            lifecycle = controller.get("lifecycle")

            if command.action == "get_status":
                status = {
                    "storage_type": "syphon",
                    "available": storage is not None,
                    "data_count": len(storage.extracted_data) if storage and hasattr(storage, 'extracted_data') else 0,
                    "lifecycle_rules": lifecycle.get_statistics() if lifecycle and hasattr(lifecycle, 'get_statistics') else {}
                }
                return ControlResult(
                    command_id=command.command_id,
                    success=True,
                    message="Storage status retrieved",
                    data=status
                )

            return ControlResult(
                command_id=command.command_id,
                success=False,
                message=f"Unknown storage action: {command.action}",
                errors=[f"Unsupported action: {command.action}"]
            )
        except Exception as e:
            return ControlResult(
                command_id=command.command_id,
                success=False,
                message=f"Storage command failed: {str(e)}",
                errors=[str(e)]
            )

    def _handle_ai_systems_command(self, command: ControlCommand, controller: Any) -> ControlResult:
        """Handle AI systems control commands"""
        try:
            result = controller.execute_action(
                command.action,
                **command.parameters.get("kwargs", {})
            )

            return ControlResult(
                command_id=command.command_id,
                success=result.get("success", False),
                message=result.get("message", "AI systems command executed"),
                data=result,
                errors=[result.get("error")] if result.get("error") else []
            )
        except Exception as e:
            return ControlResult(
                command_id=command.command_id,
                success=False,
                message=f"AI systems command failed: {str(e)}",
                errors=[str(e)]
            )

    def _handle_applications_command(self, command: ControlCommand, controller: Any) -> ControlResult:
        """Handle applications control commands"""
        # Use MANUS IDE control
        return self._handle_manus_command(command, controller)

    def _handle_automation_command(self, command: ControlCommand, controller: Any) -> ControlResult:
        """Handle automation control commands"""
        # Use MANUS automation control
        return self._handle_manus_command(command, controller)

    def _handle_data_command(self, command: ControlCommand, controller: Any) -> ControlResult:
        """Handle data control commands"""
        # Use storage control
        return self._handle_storage_command(command, controller)

    def get_full_status(self) -> Dict[str, Any]:
        """Get full status of all control domains"""
        status = {}

        for domain in ControlDomain:
            controller = self.controllers.get(domain)
            status[domain.value] = {
                "available": controller is not None,
                "status": "operational" if controller is not None else "not_available"
            }

        return {
            "timestamp": datetime.now().isoformat(),
            "domains": status,
            "total_domains": len(ControlDomain),
            "available": sum(1 for s in status.values() if s["available"]),
            "command_history_size": len(self.command_history),
            "status": "operational"
        }

    def get_command_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get command history"""
        recent = self.command_history[-limit:]
        return [
            {
                "command_id": r.command_id,
                "domain": "unknown",  # Would need to track this
                "success": r.success,
                "message": r.message,
                "duration": r.duration,
                "timestamp": r.timestamp.isoformat()
            }
            for r in recent
        ]


def main():
    try:
        """CLI interface for JARVIS Full Control System"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Full Control System")
        parser.add_argument("--domain", choices=[d.value for d in ControlDomain], help="Control domain")
        parser.add_argument("--action", help="Action to execute")
        parser.add_argument("--params", type=json.loads, default={}, help="Parameters (JSON)")
        parser.add_argument("--status", action="store_true", help="Get full status")
        parser.add_argument("--history", type=int, help="Show command history (limit)")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        control = JARVISFullControlSystem()

        if args.status:
            status = control.get_full_status()
            if args.json:
                print(json.dumps(status, indent=2))
            else:
                print("\n🤖 JARVIS Full Control System Status")
                print("="*70)
                print(f"Available Domains: {status['available']}/{status['total_domains']}")
                print(f"Command History: {status['command_history_size']} commands")
                print("\nDomain Status:")
                for domain, info in status['domains'].items():
                    icon = "✅" if info['available'] else "❌"
                    print(f"  {icon} {domain}: {info['status']}")
            return

        if args.history:
            history = control.get_command_history(args.history)
            if args.json:
                print(json.dumps(history, indent=2))
            else:
                print(f"\n📜 Command History (last {args.history})")
                print("="*70)
                for cmd in history:
                    icon = "✅" if cmd['success'] else "❌"
                    print(f"{icon} {cmd['command_id']}: {cmd['message']} ({cmd['duration']:.2f}s)")
            return

        # Execute command (requires both domain and action)
        if not args.domain or not args.action:
            parser.print_help()
            return

        command = ControlCommand(
            command_id=f"cmd_{uuid.uuid4().hex[:8]}",
            domain=ControlDomain(args.domain),
            action=args.action,
            parameters=args.params
        )

        result = control.execute_command(command)

        if args.json:
            print(json.dumps({
                "command_id": result.command_id,
                "success": result.success,
                "message": result.message,
                "data": result.data,
                "errors": result.errors,
                "duration": result.duration
            }, indent=2))
        else:
            icon = "✅" if result.success else "❌"
            print(f"\n{icon} {result.message}")
            if result.data:
                print(f"Data: {json.dumps(result.data, indent=2)}")
            if result.errors:
                print(f"Errors: {result.errors}")
            print(f"Duration: {result.duration:.2f}s")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()