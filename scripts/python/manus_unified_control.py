#!/usr/bin/env python3
"""
MANUS Unified Control Interface

Single unified interface for all MANUS control operations across:
- IDE Control (Cursor, VS Code)
- Workstation Control (Windows, services, resources)
- Home Lab Infrastructure (NAS, services, network)
- Project Lumina Management (Git, codebase, deployments)
- Automation Control (n8n, workflows, integrations)
- Data Management (storage, lifecycle, backup)
- Security Control (scanning, access, compliance)

This is JARVIS's primary interface for managing the entire home lab and Project Lumina.
"""

import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)

    def get_logger(name: str):
        """Fallback logger factory"""
        return logging.getLogger(name)

logger = get_logger("MANUSUnifiedControl")


class ControlArea(Enum):
    """MANUS control areas"""
    IDE_CONTROL = "ide_control"
    WORKSTATION_CONTROL = "workstation_control"
    HOME_LAB_INFRASTRUCTURE = "home_lab_infrastructure"
    PROJECT_LUMINA_MANAGEMENT = "project_lumina_management"
    AUTOMATION_CONTROL = "automation_control"
    DATA_MANAGEMENT = "data_management"
    SECURITY_CONTROL = "security_control"
    TRIAD_SECRET_CONTROL = "triad_secret_control"  # @TRIAD Password Manager System
    RDP_CAPTURE = "rdp_capture"  # RDP screenshot/video capture


@dataclass
class ControlOperation:
    """A control operation request"""
    operation_id: str
    area: ControlArea
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1
    timeout: int = 300  # seconds
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class OperationResult:
    """Result of a control operation"""
    operation_id: str
    success: bool
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    duration: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class MANUSUnifiedControl:
    """
    Unified MANUS Control Interface

    Single point of control for all MANUS operations across the home lab
    and Project Lumina. JARVIS uses this interface to manage everything.
    """

    def __init__(self, root_path: Path):
        """Initialize unified control interface"""
        self.project_root = Path(root_path)
        self.controllers: Dict[ControlArea, Any] = {}
        self.operation_history: List[OperationResult] = []
        self.health_status: Dict[str, Any] = {}

        # Initialize area controllers
        self._initialize_controllers()

        # Initialize System Fuckery Eliminator
        self.fuckery_eliminator = None
        try:
            from jarvis_system_fuckery_eliminator import (FuckeryType,
                                                           get_fuckery_eliminator)
            self.fuckery_eliminator = get_fuckery_eliminator(self.project_root)
            logger.info("✅ System Fuckery Eliminator integrated")
        except Exception as e:
            logger.warning("⚠️  System Fuckery Eliminator not available: %s", e)

        logger.info("MANUS Unified Control Interface initialized")

    def _initialize_controllers(self) -> None:
        """Initialize controllers for each control area"""
        # RDP Screenshot Capture
        try:
            from manus_rdp_screenshot_capture import MANUSRDPScreenshotCapture
            rdp_capture = MANUSRDPScreenshotCapture()
            self.controllers[ControlArea.RDP_CAPTURE] = rdp_capture
            logger.info("✓ RDP Screenshot Capture initialized")
        except Exception as e:
            logger.warning("RDP Screenshot Capture not available: %s", e)
            self.controllers[ControlArea.RDP_CAPTURE] = None

        # IDE Control
        try:
            from complete_ide_control import CompleteIDEControl
            from manus_cursor_controller import ManusCursorController
            cursor_controller = ManusCursorController()
            ide_control = CompleteIDEControl(self.project_root)
            ide_control.cursor_controller = cursor_controller
            ide_controllers = {
                "cursor": cursor_controller,
                "complete": ide_control
            }

            # Add chat automation
            try:
                from manus_cursor_chat_automation import \
                    MANUSCursorChatAutomation
                chat_automation = MANUSCursorChatAutomation(self.project_root)
                ide_controllers["chat_automation"] = chat_automation
                logger.info("✓ IDE Control: cursor + complete + chat automation")
            except ImportError:
                logger.warning("Chat automation not available")

            self.controllers[ControlArea.IDE_CONTROL] = ide_controllers
            logger.info("✓ IDE Control: cursor + complete state")
        except Exception as e:
            logger.warning("IDE Control not available: %s", e)
            self.controllers[ControlArea.IDE_CONTROL] = None

        # Workstation Control
        try:
            from manus_workstation_controller import MANUSWorkstationController
            workstation_controller = MANUSWorkstationController(self.project_root)
            self.controllers[ControlArea.WORKSTATION_CONTROL] = workstation_controller
            logger.info("✓ Workstation Control initialized (complete laptop control)")
        except Exception as e:
            logger.warning("Workstation Control not available: %s", e)
            self.controllers[ControlArea.WORKSTATION_CONTROL] = None

        # Home Lab Infrastructure
        try:
            from infrastructure_orchestrator import InfrastructureOrchestrator
            from unified_monitoring_system import UnifiedMonitoringSystem
            # Combine monitoring and orchestration
            monitoring = UnifiedMonitoringSystem(self.project_root)
            orchestration = InfrastructureOrchestrator(self.project_root)
            self.controllers[ControlArea.HOME_LAB_INFRASTRUCTURE] = {
                "monitoring": monitoring,
                "orchestration": orchestration
            }
            logger.info("✓ Home Lab Infrastructure: monitoring + orchestration")
        except Exception as e:
            logger.warning("Home Lab Infrastructure not available: %s", e)
            self.controllers[ControlArea.HOME_LAB_INFRASTRUCTURE] = None

        # Project Lumina Management
        try:
            from scripts.python.jarvis_helpdesk_integration import JARVISHelpdeskIntegration
            lumina_mgmt = JARVISHelpdeskIntegration(self.project_root)
            self.controllers[ControlArea.PROJECT_LUMINA_MANAGEMENT] = lumina_mgmt
            logger.info("✓ Project Lumina Management initialized")
        except Exception as e:
            logger.warning("Project Lumina Management not available: %s", e)
            self.controllers[ControlArea.PROJECT_LUMINA_MANAGEMENT] = None

        # Automation Control
        try:
            # Neo Browser Workflow Integration
            try:
                from manus_neo_workflow_integration import \
                    MANUSNEOWorkflowController
                neo_controller = MANUSNEOWorkflowController(self.project_root)
                self.controllers[ControlArea.AUTOMATION_CONTROL] = {
                    "neo_browser": neo_controller
                }
                logger.info("✓ Automation Control: Neo browser workflows")
            except Exception as e:
                logger.warning("Neo browser workflows not available: %s", e)
                self.controllers[ControlArea.AUTOMATION_CONTROL] = None
            logger.info("⚠ Automation Control: Partially available")
        except Exception as e:
            logger.warning("Automation Control not available: %s", e)
            self.controllers[ControlArea.AUTOMATION_CONTROL] = None

        # Data Management
        try:
            from data_lifecycle_manager import DataLifecycleManager
            from syphon.core import SubscriptionTier, SYPHONConfig
            from syphon.storage import SyphonStorage
            storage_config = SYPHONConfig(
                project_root=self.project_root,
                subscription_tier=SubscriptionTier.ENTERPRISE,
                enable_self_healing=True
            )
            storage = SyphonStorage(storage_config)
            lifecycle = DataLifecycleManager(self.project_root)
            self.controllers[ControlArea.DATA_MANAGEMENT] = {
                "storage": storage,
                "lifecycle": lifecycle
            }
            logger.info("✓ Data Management initialized (storage + lifecycle)")
        except Exception as e:
            logger.warning("Data Management not available: %s", e)
            self.controllers[ControlArea.DATA_MANAGEMENT] = None

        # Security Control
        try:
            from security_scanning_automation import SecurityScanningAutomation
            security_ctrl = SecurityScanningAutomation(self.project_root)
            self.controllers[ControlArea.SECURITY_CONTROL] = security_ctrl
            logger.info("✓ Security Control initialized (scanning automation)")
        except Exception as e:
            logger.warning("Security Control not available: %s", e)
            self.controllers[ControlArea.SECURITY_CONTROL] = None

        # Triad Secret Control
        try:
            from unified_secrets_manager import UnifiedSecretsManager
            triad_ctrl = UnifiedSecretsManager(self.project_root)
            self.controllers[ControlArea.TRIAD_SECRET_CONTROL] = triad_ctrl
            logger.info("✓ Triad Secret Control initialized (@TRIAD System)")
        except Exception as e:
            logger.warning("Triad Secret Control not available: %s", e)
            self.controllers[ControlArea.TRIAD_SECRET_CONTROL] = None

    def execute_operation(self, operation: ControlOperation) -> OperationResult:
        """
        Execute a control operation

        Args:
            operation: Control operation to execute

        Returns:
            OperationResult with success status and details
        """
        start_time = datetime.now()

        # @RECURSIVE_EXPERIMENT_DETECTOR
        try:
            from jarvis_recursive_experiment_detector import \
                get_experiment_detector

            experiment_detector = get_experiment_detector(self.project_root)

            # Determine target based on operation area
            if operation.area == ControlArea.IDE_CONTROL:
                target = "cursor_ide"
            elif "windows" in operation.area.value.lower():
                target = "windows_os"
            else:
                target = "system"

            # Assess for recursive/experimental behavior
            blocked, transgression, penalty = experiment_detector.assess_and_penalize(
                action=operation.action,
                target=target,
                context={
                    "operation_id": operation.operation_id,
                    "area": operation.area.value,
                    "parameters": operation.parameters
                }
            )

            if blocked and transgression:
                logger.error(
                    "🚫 RECURSIVE/EXPERIMENTAL BEHAVIOR BLOCKED: %s - "
                    "Action: %s - Target: %s - Penalty: -%s - Frequency: %s",
                    transgression.pattern_type,
                    operation.action,
                    target,
                    penalty,
                    transgression.metadata.get('frequency', 1)
                )

                msg_r = (f"Recursive/experimental behavior blocked: "
                         f"{transgression.metadata.get('reason', 'Unauthorized')} "
                         f"(-{penalty} penalty)")
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=False,
                    message=msg_r,
                    errors=[f"{transgression.pattern_type}: {transgression.action}"],
                    duration=0.0
                )
        except Exception as e:
            logger.debug("Recursive experiment detector check failed: %s", e)

        # @BLACKLIST: Prevent AI from using MANUS CONTROL when operator is active
        try:
            from jarvis_blacklist_restriction_enforcer import (
                RestrictionType, get_blacklist_enforcer)
            from operator_idleness_restriction import \
                get_operator_idleness_restriction

            idleness_restriction = get_operator_idleness_restriction(self.project_root)
            blacklist_enforcer = get_blacklist_enforcer(self.project_root)

            # Check if operator is active (not idle)
            operator_is_active = idleness_restriction.is_action_allowed("manus_action")

            if operator_is_active:
                # Operator is actively working - block ALL MANUS operations
                action_lower = operation.action.lower()
                is_self_test = any(keyword in action_lower for keyword in [
                    'test', 'testing', 'self_test', 'self-test', 'verify', 'validation',
                    'test_manus', 'test_control', 'manus_test', 'control_test'
                ])

                # Block self-tests when operator is active
                if is_self_test:
                    blacklist_enforcer.enforce_restriction(
                        restriction_type=RestrictionType.MANUS_SELF_TEST_BLOCKED,
                        action="manus_self_test",
                        value=operation.action,
                        check_func=lambda *a, **k: (False, "Blocked: Operator active")
                    )

                    logger.error(
                        "🚫 BLOCKED: MANUS self-test while operator active - "
                        "Operation: %s - Penalty: -2 DKP, -XP",
                        operation.action
                    )

                    msg_s = "AI self-testing MANUS blocked when operator active (-2 DKP, -XP)"
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=False,
                        message=msg_s,
                        errors=["Self-testing blocked: Operator active"],
                        duration=0.0
                    )

                # Also block any MANUS operation on IDE_CONTROL when operator is active
                if operation.area == ControlArea.IDE_CONTROL:
                    blacklist_enforcer.enforce_restriction(
                        restriction_type=RestrictionType.MANUS_SELF_TEST_BLOCKED,
                        action="manus_ide_control",
                        value=operation.action,
                        check_func=lambda *a, **k: (False, "Blocked: Operator active")
                    )

                    logger.error(
                        "🚫 BLOCKED: AI/JARVIS attempted MANUS IDE control while active - "
                        "Operation: %s - Penalty: -2 DKP, -XP",
                        operation.action
                    )

                    msg_i = "AI MANUS IDE control blocked when operator active (-2 DKP, -XP)"
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=False,
                        message=msg_i,
                        errors=["IDE control blocked: Operator active"],
                        duration=0.0
                    )
        except Exception as e:
            logger.debug("MANUS restriction check failed: %s", e)

        # @SYSTEM_FUCKERY
        try:
            from jarvis_system_fuckery_eliminator import (FuckeryType,
                                                           get_fuckery_eliminator)
            fuckery_eliminator = get_fuckery_eliminator(self.project_root)

            # Detect MANUS interference if operator is active
            if operation.area == ControlArea.IDE_CONTROL:
                fuckery_eliminator.detect_fuckery(
                    FuckeryType.MANUS_INTERFERENCE,
                    f"MANUS attempting {operation.action} on Cursor IDE",
                    severity="high",
                    metadata={"operation": operation.action, "area": operation.area.value}
                )
        except Exception as e:
            logger.debug("System Fuckery Eliminator not available: %s", e)

        # @BLACKLIST: Check for Cursor IDE menu/clipboard restrictions
        try:
            from jarvis_blacklist_restriction_enforcer import (
                RestrictionType, get_blacklist_enforcer)
            blacklist_enforcer = get_blacklist_enforcer(self.project_root)

            # Check for Cursor IDE menu interactions
            if operation.area == ControlArea.IDE_CONTROL:
                action_lower = operation.action.lower()

                # Check menu interactions
                allowed, reason = blacklist_enforcer.check_cursor_menu_interaction(
                    operation.action
                )
                if not allowed:
                    # @SYSTEM_FUCKERY: Detect menu popup fuckery
                    try:
                        from jarvis_system_fuckery_eliminator import (
                            FuckeryType, get_fuckery_eliminator)
                        fuckery_eliminator = get_fuckery_eliminator(self.project_root)
                        fuckery_eliminator.detect_fuckery(
                            FuckeryType.MENU_POPUP_UNEXPECTED,
                            f"MANUS attempted menu interaction: {operation.action}",
                            severity="high",
                            metadata={"operation": operation.action, "blocked": True}
                        )
                    except Exception:
                        pass
                    blacklist_enforcer.enforce_restriction(
                        restriction_type=RestrictionType.CURSOR_MENU_INTERACTION,
                        action=operation.action,
                        value=operation.action,
                        check_func=lambda a: blacklist_enforcer.check_cursor_menu_interaction(a)
                    )
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=False,
                        message=f"Cursor IDE menu interaction blocked: {reason}",
                        errors=[reason],
                        duration=0.0
                    )

                # Check right-click operations
                right_click_keys = ['right_click', 'button-3', 'context_menu']
                if any(kw in action_lower for kw in right_click_keys):
                    allowed, reason = blacklist_enforcer.check_cursor_right_click(
                        operation.action
                    )
                    if not allowed:
                        blacklist_enforcer.enforce_restriction(
                            restriction_type=RestrictionType.CURSOR_RIGHT_CLICK,
                            action=operation.action,
                            value=operation.action,
                            check_func=lambda a: blacklist_enforcer.check_cursor_right_click(a)
                        )
                        return OperationResult(
                            operation_id=operation.operation_id,
                            success=False,
                            message=f"Cursor IDE right-click blocked: {reason}",
                            errors=[reason],
                            duration=0.0
                        )

                # Check clipboard operations
                cb_keys = ['clipboard', 'copy', 'cut', 'paste', 'ctrl+c', 'ctrl+x', 'ctrl+v']
                if any(kw in action_lower for kw in cb_keys):
                    allowed, reason = blacklist_enforcer.check_cursor_clipboard(
                        operation.action
                    )
                    if not allowed:
                        blacklist_enforcer.enforce_restriction(
                            restriction_type=RestrictionType.CURSOR_CLIPBOARD_OPERATION,
                            action=operation.action,
                            value=operation.action,
                            check_func=lambda a: blacklist_enforcer.check_cursor_clipboard(a)
                        )
                        return OperationResult(
                            operation_id=operation.operation_id,
                            success=False,
                            message=f"Cursor IDE clipboard operation blocked: {reason}",
                            errors=[reason],
                            duration=0.0
                        )
        except ImportError:
            logger.warning("⚠️  Blacklist enforcer not available - proceeding")
        except Exception as e:
            logger.warning("⚠️  Blacklist check failed: %s - proceeding", e)

        # @LIVE LIST CHECK: Check if action is blacklisted
        try:
            from jarvis_live_list_manager import ListType, get_live_list_manager
            live_list_manager = get_live_list_manager(self.project_root)

            # Check for Cursor IDE interaction restrictions
            action_lower = operation.action.lower()
            menu_keys = ['menu', 'right_click', 'context_menu', 'popup', 'dialog']
            if any(kw in action_lower for kw in menu_keys):
                allowed, reason, _ = live_list_manager.check_value(
                    "cursor_menu_interaction", "ide_interaction"
                )
                if not allowed:
                    logger.error("🚫 BLACKLISTED: MANUS action '%s' blocked: %s",
                                 operation.action, reason)
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=False,
                        message=f"Operation blacklisted: {reason}",
                        errors=[f"Blacklist violation: {reason}"],
                        duration=0.0
                    )

            if 'right_click' in action_lower or 'context' in action_lower:
                allowed, reason, _ = live_list_manager.check_value(
                    "cursor_right_click", "ide_interaction"
                )
                if not allowed:
                    logger.error("🚫 BLACKLISTED: MANUS action '%s' blocked: %s",
                                 operation.action, reason)
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=False,
                        message=f"Operation blacklisted: {reason}",
                        errors=[f"Blacklist violation: {reason}"],
                        duration=0.0
                    )

            clipboard_keys = ['cut', 'paste', 'copy', 'clipboard']
            if any(kw in action_lower for kw in clipboard_keys):
                allowed, reason, _ = live_list_manager.check_value(
                    "cursor_clipboard_cut_paste", "ide_interaction"
                )
                if not allowed:
                    logger.error("🚫 BLACKLISTED: MANUS action '%s' blocked: %s",
                                 operation.action, reason)
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=False,
                        message=f"Operation blacklisted: {reason}",
                        errors=[f"Blacklist violation: {reason}"],
                        duration=0.0
                    )
        except ImportError:
            logger.debug("⚠️  Live list manager not available - skipping")
        except Exception as e:
            logger.warning("⚠️  Live list check failed: %s - proceeding", e)

        # @OP #IDLENESS RESTRICTION: Check if operator is idle
        try:
            from operator_idleness_restriction import \
                get_operator_idleness_restriction
            idleness_restriction = get_operator_idleness_restriction(self.project_root)
            emergency = operation.parameters.get('emergency', False)

            if not idleness_restriction.is_action_allowed("manus_action", emergency=emergency):
                idle_duration = idleness_restriction._get_idle_duration()

                # @PENALTY: Record violation and apply -xp penalty (unless emergency)
                if not emergency:
                    try:
                        from jarvis_policy_violation_penalty import (
                            PolicyType, ViolationSeverity, get_penalty_system)
                        penalty_system = get_penalty_system(self.project_root)
                        violation = penalty_system.record_violation(
                            policy_type=PolicyType.MANUS_ACTION_VIOLATION,
                            action=operation.action,
                            description=(f"MANUS '{operation.action}' while operator "
                                         f"idle {idle_duration:.0f}s"),
                            severity=ViolationSeverity.MODERATE,
                            blocked=True,
                            metadata={
                                "operation_id": operation.operation_id,
                                "area": operation.area.value,
                                "idle_duration": idle_duration,
                                "threshold": idleness_restriction.restriction.idle_timeout_seconds
                            }
                        )
                        logger.error(
                            "🚫 POLICY VIOLATION: MANUS '%s' blocked - "
                            "Operator idle %.0fs - Penalty: %s XP",
                            operation.action,
                            idle_duration,
                            violation.xp_penalty
                        )
                    except Exception as e:
                        logger.warning("⚠️  Penalty system unavailable: %s", e)

                logger.warning(
                    "🚫 BLOCKED: MANUS '%s' - Operator idle %.0fs (threshold: %ss)",
                    operation.action,
                    idle_duration,
                    idleness_restriction.restriction.idle_timeout_seconds
                )
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=False,
                    message=f"Operator idle {idle_duration:.0f}s - MANUS restricted",
                    errors=[f"Idleness restriction: {idle_duration:.0f}s idle"],
                    duration=0.0
                )
        except ImportError:
            logger.warning("⚠️  Operator idleness restriction not available")
        except Exception as e:
            logger.warning("⚠️  Operator idleness check failed: %s", e)

        try:
            controller = self.controllers.get(operation.area)
            if controller is None:
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=False,
                    message=f"Controller for {operation.area.value} not available",
                    errors=[f"Controller not initialized for {operation.area.value}"]
                )

            # Route to appropriate controller method
            result = self._route_operation(operation, controller)

            duration = (datetime.now() - start_time).total_seconds()
            result.duration = duration
            result.operation_id = operation.operation_id

            # Record in history
            self.operation_history.append(result)

            return result

        except Exception as e:
            logger.error("Error executing operation %s: %s",
                         operation.operation_id, e, exc_info=True)
            duration = (datetime.now() - start_time).total_seconds()
            return OperationResult(
                operation_id=operation.operation_id,
                success=False,
                message=f"Operation failed: {str(e)}",
                errors=[str(e)],
                duration=duration
            )

    def _route_operation(self, operation: ControlOperation, controller: Any) -> OperationResult:
        """Route operation to appropriate controller method"""
        area = operation.area

        # IDE Control routing
        if area == ControlArea.IDE_CONTROL:
            return self._handle_ide_operation(operation, controller)

        # Workstation Control routing
        elif area == ControlArea.WORKSTATION_CONTROL:
            return self._handle_workstation_operation(operation, controller)

        # Home Lab Infrastructure routing
        elif area == ControlArea.HOME_LAB_INFRASTRUCTURE:
            return self._handle_infrastructure_operation(operation, controller)

        # Project Lumina Management routing
        elif area == ControlArea.PROJECT_LUMINA_MANAGEMENT:
            return self._handle_lumina_operation(operation, controller)

        # Automation Control routing
        elif area == ControlArea.AUTOMATION_CONTROL:
            return self._handle_automation_operation(operation, controller)

        # Data Management routing
        elif area == ControlArea.DATA_MANAGEMENT:
            return self._handle_data_operation(operation, controller)

        # Security Control routing
        elif area == ControlArea.SECURITY_CONTROL:
            return self._handle_security_operation(operation, controller)

        # Triad Secret Control routing
        elif area == ControlArea.TRIAD_SECRET_CONTROL:
            return self._handle_triad_operation(operation, controller)

        # RDP Capture routing
        elif area == ControlArea.RDP_CAPTURE:
            return self._handle_rdp_capture_operation(operation, controller)

        else:
            return OperationResult(
                operation_id=operation.operation_id,
                success=False,
                message=f"Unknown control area: {area}",
                errors=[f"Unsupported area: {area.value}"]
            )

    def _handle_ide_operation(self, operation: ControlOperation, controller: Any) -> OperationResult:
        """Handle IDE control operations"""
        action = operation.action

        try:
            # Controller is now a dict with cursor and complete
            if not isinstance(controller, dict):
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=False,
                    message="IDE controller not properly initialized",
                    errors=["Controller structure invalid"]
                )

            cursor_controller = controller.get("cursor")
            complete_control = controller.get("complete")

            if action == "connect":
                if cursor_controller:
                    connected = cursor_controller.connect_to_cursor()
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=connected,
                        message="IDE connected" if connected else "Failed to connect",
                        data={"connected": connected}
                    )

            elif action == "monitor":
                if cursor_controller:
                    cursor_controller.start_monitoring()
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=True,
                        message="IDE monitoring started",
                        data={"monitoring": True}
                    )

            elif action == "get_complete_state":
                if complete_control:
                    state = complete_control.get_complete_state()
                    msg = "Complete IDE state retrieved"
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=True,
                        message=msg,
                        data={
                            "windows": len(state.windows),
                            "tabs": len(state.tabs),
                            "editors": len(state.editors),
                            "terminals": len(state.terminals),
                            "active_window": state.active_window,
                            "active_tab": state.active_tab
                        }
                    )

            elif action == "control_window":
                if complete_control:
                    window_id = operation.parameters.get("window_id", "main")
                    window_action = operation.parameters.get("window_action")
                    success = complete_control.control_window(
                        window_id, window_action, **operation.parameters
                    )
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=success,
                        message=f"Window {window_action} executed",
                        data={"window_id": window_id, "action": window_action}
                    )

            elif action == "control_tab":
                if complete_control:
                    file_path = operation.parameters.get("file_path")
                    tab_action = operation.parameters.get("tab_action")
                    success = complete_control.control_tab(
                        file_path, tab_action, **operation.parameters
                    )
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=success,
                        message=f"Tab {tab_action} executed",
                        data={"file_path": file_path, "action": tab_action}
                    )

            elif action == "get_state":
                if cursor_controller:
                    state = {
                        "window_title": (cursor_controller.cursor_window.title
                                        if cursor_controller.cursor_window else None),
                        "monitoring_active": cursor_controller.monitoring_active,
                        "current_state": {
                            "window_title": cursor_controller.current_state.window_title,
                            "active_file": cursor_controller.current_state.active_file,
                            "diagnostics_count": len(cursor_controller.current_state.diagnostics),
                            "problems_count": len(cursor_controller.current_state.problems)
                        }
                    }
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=True,
                        message="IDE state retrieved",
                        data={"state": state}
                    )

            elif action == "send_chat_message":
                chat_automation = controller.get("chat_automation")
                if not chat_automation:
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=False,
                        message="Chat automation not available",
                        errors=["Chat automation not initialized"]
                    )

                message = operation.parameters.get("message", "")
                result = chat_automation.send_chat_message(message)

                return OperationResult(
                    operation_id=operation.operation_id,
                    success=result.get("success", False),
                    message=result.get("message", "Chat message sent"),
                    data=result
                )

            else:
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=False,
                    message=f"Unknown IDE action: {action}",
                    errors=[f"Unsupported action: {action}"]
                )

        except Exception as e:
            return OperationResult(
                operation_id=operation.operation_id,
                success=False,
                message=f"IDE operation failed: {str(e)}",
                errors=[str(e)]
            )

    def _handle_infrastructure_operation(self, operation: ControlOperation, controller: Any) -> OperationResult:
        """Handle infrastructure operations"""
        action = operation.action

        try:
            # Controller is now a dict with monitoring and orchestration
            if not isinstance(controller, dict):
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=False,
                    message="Infrastructure controller not properly initialized",
                    errors=["Controller structure invalid"]
                )

            monitoring = controller.get("monitoring")
            orchestration = controller.get("orchestration")

            # Monitoring operations
            if action == "start_monitoring":
                if monitoring:
                    monitoring.start_monitoring()
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=True,
                        message="Infrastructure monitoring started",
                        data={"monitoring_active": True}
                    )

            elif action == "stop_monitoring":
                if monitoring:
                    monitoring.stop_monitoring()
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=True,
                        message="Infrastructure monitoring stopped",
                        data={"monitoring_active": False}
                    )

            elif action == "get_monitoring_status":
                if monitoring:
                    status = monitoring.get_health_status()
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=True,
                        message="Monitoring status retrieved",
                        data=status
                    )

            elif action == "get_issues":
                if monitoring:
                    limit = operation.parameters.get("limit", 100)
                    issues = monitoring.get_issues(limit=limit)
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=True,
                        message="Issues retrieved",
                        data={"issues": issues, "count": len(issues)}
                    )

            elif action == "set_remediation_callback":
                if monitoring:
                    try:
                        from automated_remediation_engine import \
                            AutomatedRemediationEngine
                        rem_engine = AutomatedRemediationEngine(self.project_root)
                        monitoring.set_remediation_callback(rem_engine.remediate_issue)
                        return OperationResult(
                            operation_id=operation.operation_id,
                            success=True,
                            message="Remediation callback set",
                            data={"remediation_integrated": True}
                        )
                    except Exception as e:
                        return OperationResult(
                            operation_id=operation.operation_id,
                            success=False,
                            message=f"Failed to set remediation: {str(e)}",
                            errors=[str(e)]
                        )

            # Orchestration operations
            elif action == "start_service":
                if orchestration:
                    service_id = operation.parameters.get("service_id")
                    if not service_id:
                        return OperationResult(
                            operation_id=operation.operation_id,
                            success=False,
                            message="service_id parameter required",
                            errors=["Missing service_id"]
                        )
                    result = orchestration.start_service(service_id)
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=result.success,
                        message=result.message,
                        data={
                            "service_id": result.service_id,
                            "status": result.status.value if result.status else None,
                            "duration": result.duration
                        },
                        errors=result.errors
                    )

            elif action == "stop_service":
                if orchestration:
                    service_id = operation.parameters.get("service_id")
                    if not service_id:
                        return OperationResult(
                            operation_id=operation.operation_id,
                            success=False,
                            message="service_id parameter required",
                            errors=["Missing service_id"]
                        )
                    result = orchestration.stop_service(service_id)
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=result.success,
                        message=result.message,
                        data={
                            "service_id": result.service_id,
                            "status": result.status.value if result.status else None,
                            "duration": result.duration
                        },
                        errors=result.errors
                    )

            elif action == "restart_service":
                if orchestration:
                    service_id = operation.parameters.get("service_id")
                    if not service_id:
                        return OperationResult(
                            operation_id=operation.operation_id,
                            success=False,
                            message="service_id parameter required",
                            errors=["Missing service_id"]
                        )
                    result = orchestration.restart_service(service_id)
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=result.success,
                        message=result.message,
                        data={
                            "service_id": result.service_id,
                            "status": result.status.value if result.status else None,
                            "duration": result.duration
                        },
                        errors=result.errors
                    )

            elif action == "get_service_status":
                if orchestration:
                    service_id = operation.parameters.get("service_id")
                    if not service_id:
                        return OperationResult(
                            operation_id=operation.operation_id,
                            success=False,
                            message="service_id parameter required",
                            errors=["Missing service_id"]
                        )
                    result = orchestration.get_service_status(service_id)
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=result.success,
                        message=result.message,
                        data={
                            "service_id": result.service_id,
                            "status": result.status.value if result.status else None
                        }
                    )

            elif action == "list_services":
                if orchestration:
                    services = orchestration.list_services()
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=True,
                        message="Services listed",
                        data={"services": services, "count": len(services)}
                    )

            # Combined status
            elif action == "get_status":
                status_data = {}
                if monitoring:
                    status_data["monitoring"] = monitoring.get_health_status()
                if orchestration:
                    status_data["orchestration"] = {
                        "services": orchestration.list_services(),
                        "total_services": len(orchestration.services)
                    }
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=True,
                    message="Infrastructure status retrieved",
                    data=status_data
                )

            else:
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=False,
                    message=f"Unknown infrastructure action: {action}",
                    errors=[f"Unsupported action: {action}"]
                )

        except Exception as e:
            return OperationResult(
                operation_id=operation.operation_id,
                success=False,
                message=f"Infrastructure operation failed: {str(e)}",
                errors=[str(e)]
            )

    def _handle_lumina_operation(self, operation: ControlOperation, controller: Any) -> OperationResult:
        """Handle Project Lumina management operations"""
        action = operation.action

        try:
            if action == "verify_workflow":
                workflow_data = operation.parameters.get("workflow_data", {})
                passed, results = controller.verify_workflow_before_execution(workflow_data)
                msg = "Workflow verified" if passed else "Verification failed"
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=passed,
                    message=msg,
                    data=results
                )

            elif action == "get_status":
                # Get system status
                status = {
                    "helpdesk": "active",
                    "droids": "operational",
                    "integration": "connected"
                }
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=True,
                    message="System status retrieved",
                    data=status
                )

            else:
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=False,
                    message=f"Unknown Lumina action: {action}",
                    errors=[f"Unsupported action: {action}"]
                )

        except Exception as e:
            return OperationResult(
                operation_id=operation.operation_id,
                success=False,
                message=f"Lumina operation failed: {str(e)}",
                errors=[str(e)]
            )

    def _handle_data_operation(self, operation: ControlOperation, controller: Any) -> OperationResult:
        """Handle data management operations"""
        action = operation.action

        try:
            # Controller is now a dict with storage and lifecycle
            if not isinstance(controller, dict):
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=False,
                    message="Data controller not properly initialized",
                    errors=["Controller structure invalid"]
                )

            storage = controller.get("storage")
            lifecycle = controller.get("lifecycle")

            if action == "get_status":
                status = {
                    "storage_type": "syphon",
                    "available": storage is not None,
                    "data_count": (len(storage.extracted_data) if storage and
                                  hasattr(storage, 'extracted_data') else 0),
                    "lifecycle_rules": lifecycle.get_statistics() if lifecycle else {}
                }
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=True,
                    message="Data management status retrieved",
                    data=status
                )

            elif action == "process_lifecycle":
                if lifecycle:
                    directory = Path(operation.parameters.get(
                        "directory", self.project_root / "data"
                    ))
                    dry_run = operation.parameters.get("dry_run", False)
                    actions = lifecycle.process_files(directory, dry_run=dry_run)
                    msg = f"Lifecycle complete: {len(actions)} actions"
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=True,
                        message=msg,
                        data={
                            "actions": len(actions),
                            "archived": sum(1 for a in actions if a.action == "archive")
                        }
                    )

            else:
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=False,
                    message=f"Unknown data action: {action}",
                    errors=[f"Unsupported action: {action}"]
                )

        except Exception as e:
            return OperationResult(
                operation_id=operation.operation_id,
                success=False,
                message=f"Data operation failed: {str(e)}",
                errors=[str(e)]
            )

    def _handle_workstation_operation(self, operation: ControlOperation, controller: Any) -> OperationResult:
        """Handle workstation control operations"""
        action = operation.action

        try:
            if not controller:
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=False,
                    message="Workstation controller not available",
                    errors=["Controller not initialized"]
                )

            # Get complete status
            if action == "get_status":
                status = controller.get_complete_status()
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=True,
                    message="Workstation status retrieved",
                    data=status
                )

            # Armoury Crate operations
            elif action == "get_armoury_status":
                status = controller.get_armoury_crate_status()
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=status.get("available", False),
                    message="Armoury Crate status retrieved",
                    data=status
                )

            elif action == "fix_armoury":
                result = controller.fix_armoury_crate()
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=result.get("success", False),
                    message=result.get("message", "Armoury Crate fix attempted"),
                    data=result
                )

            elif action == "apply_theme":
                theme_name = operation.parameters.get("theme_name")
                if not theme_name:
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=False,
                        message="theme_name parameter required",
                        errors=["Missing theme_name"]
                    )
                result = controller.apply_lighting_theme(theme_name)
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=result.get("success", False),
                    message=f"Theme {theme_name} applied",
                    data=result
                )

            elif action == "fix_f4_button":
                result = controller.fix_f4_aura_button()
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=result.get("success", False),
                    message="F4-AURA button fix attempted",
                    data=result
                )

            # Power management operations
            elif action == "configure_power":
                result = controller.configure_power_settings()
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=result.get("success", False),
                    message="Power settings configured",
                    data=result
                )

            elif action == "check_power":
                result = controller.check_power_settings()
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=result.get("success", False),
                    message="Power settings checked",
                    data=result
                )

            # Service management operations
            elif action == "get_service_status":
                service_name = operation.parameters.get("service_name")
                if not service_name:
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=False,
                        message="service_name parameter required",
                        errors=["Missing service_name"]
                    )
                result = controller.get_service_status(service_name)
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=result.get("success", False),
                    message=f"Service {service_name} status retrieved",
                    data=result
                )

            elif action == "start_service":
                service_name = operation.parameters.get("service_name")
                if not service_name:
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=False,
                        message="service_name parameter required",
                        errors=["Missing service_name"]
                    )
                result = controller.start_service(service_name)
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=result.get("success", False),
                    message=f"Service {service_name} start attempted",
                    data=result
                )

            elif action == "set_service_automatic":
                service_name = operation.parameters.get("service_name")
                if not service_name:
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=False,
                        message="service_name parameter required",
                        errors=["Missing service_name"]
                    )
                result = controller.set_service_automatic(service_name)
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=result.get("success", False),
                    message=f"Service {service_name} auto-startup configured",
                    data=result
                )

            else:
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=False,
                    message=f"Unknown workstation action: {action}",
                    errors=[f"Unsupported action: {action}"]
                )

        except Exception as e:
            return OperationResult(
                operation_id=operation.operation_id,
                success=False,
                message=f"Workstation operation failed: {str(e)}",
                errors=[str(e)]
            )

    def _handle_automation_operation(self, operation: ControlOperation, controller: Any) -> OperationResult:
        """Handle automation control operations (Neo browser workflows)"""
        if controller is None:
            return OperationResult(
                operation_id=operation.operation_id,
                success=False,
                message="Automation control not available",
                errors=["Automation controller not initialized"]
            )

        action = operation.action
        params = operation.parameters

        try:
            # Neo browser workflow operations
            action_l = action.lower()
            if ("neo" in action_l or "browser" in action_l or
                action in ["execute_workflow", "elevenlabs_setup"]):
                neo_controller = controller.get("neo_browser")
                if not neo_controller:
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=False,
                        message="Neo browser controller not available",
                        errors=["Neo browser workflows not initialized"]
                    )

                # Execute workflow
                if action == "execute_workflow" or action == "run_workflow":
                    workflow = params.get("workflow", {})
                    result = neo_controller.execute_workflow(workflow)
                    msg = (f"Workflow executed: {result.get('steps_completed', 0)}/"
                           f"{result.get('steps_total', 0)} steps")
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=result.get("success", False),
                        message=msg,
                        data=result
                    )

                # ElevenLabs setup workflow
                elif action == "elevenlabs_setup":
                    workflow = neo_controller.create_elevenlabs_setup_workflow()
                    result = neo_controller.execute_workflow(workflow)
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=result.get("success", False),
                        message="ElevenLabs setup workflow executed",
                        data=result
                    )

                # Get workflow status
                elif action == "get_workflow_status":
                    workflow_id = params.get("workflow_id")
                    status = neo_controller.get_workflow_status(workflow_id)
                    msg = "Workflow status retrieved" if status else "Not found"
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=status is not None,
                        message=msg,
                        data={"status": status} if status else {}
                    )

            # Unknown automation action
            return OperationResult(
                operation_id=operation.operation_id,
                success=False,
                message=f"Unknown automation action: {action}",
                errors=[f"No handler for automation action: {action}"]
            )

        except Exception as e:
            logger.error("Error in automation operation: %s", e, exc_info=True)
            return OperationResult(
                operation_id=operation.operation_id,
                success=False,
                message=f"Automation operation failed: {str(e)}",
                errors=[str(e)]
            )

    def _handle_rdp_capture_operation(self, operation: ControlOperation, controller: Any) -> OperationResult:
        """Handle RDP screenshot/video capture operations"""
        action = operation.action
        params = operation.parameters

        try:
            if action == "screenshot":
                filename = params.get("filename")
                screenshot_path = controller.capture_screenshot(filename=filename)
                if screenshot_path:
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=True,
                        message=f"Screenshot captured: {screenshot_path}",
                        data={"screenshot_path": str(screenshot_path)}
                    )
                else:
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=False,
                        message="Screenshot capture failed",
                        errors=["Failed to capture screenshot"]
                    )

            elif action == "capture_with_context":
                description = params.get("description", "Automatic capture")
                metadata = controller.capture_with_context(description, auto_capture=True)
                msg = f"Context capture: {metadata.get('screenshot_path', 'N/A')}"
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=True,
                    message=msg,
                    data=metadata
                )

            elif action == "start_video":
                filename = params.get("filename")
                video_path = controller.start_video_recording(filename=filename)
                if video_path:
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=True,
                        message=f"Video recording started: {video_path}",
                        data={"video_path": str(video_path)}
                    )
                else:
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=False,
                        message="Video recording failed to start",
                        errors=["Failed to start video recording"]
                    )

            elif action == "list_captures":
                captures = controller.list_captures()
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=True,
                    message=f"Found {len(captures)} captures",
                    data={"captures": captures}
                )

            else:
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=False,
                    message=f"Unknown RDP capture action: {action}",
                    errors=[f"Unsupported action: {action}"]
                )

        except Exception as e:
            logger.error("Error in RDP capture operation: %s", e, exc_info=True)
            return OperationResult(
                operation_id=operation.operation_id,
                success=False,
                message=f"RDP capture operation failed: {str(e)}",
                errors=[str(e)]
            )

    def _handle_security_operation(self, operation: ControlOperation, controller: Any) -> OperationResult:
        """Handle security control operations"""
        action = operation.action

        try:
            if action == "scan":
                scan_type = operation.parameters.get("scan_type", "full")
                dir_path = Path(operation.parameters.get("directory", self.project_root))

                if scan_type == "full":
                    results = controller.run_full_scan(dir_path)
                    total_iss = sum(len(r.issues) for r in results)
                    crit = sum(sum(1 for i in r.issues if i.severity.value == "critical")
                              for r in results)
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=True,
                        message=f"Full security scan complete: {len(results)} types",
                        data={
                            "scans": len(results),
                            "total_issues": total_iss,
                            "critical": crit
                        }
                    )
                elif scan_type == "secrets":
                    result = controller.scan_secrets(dir_path)
                    high = sum(1 for i in result.issues if i.severity.value == "high")
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=True,
                        message=f"Secrets scan complete: {len(result.issues)} issues",
                        data={"issues": len(result.issues), "high": high}
                    )

            elif action == "get_summary":
                summary = controller.get_scan_summary()
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=True,
                    message="Security scan summary retrieved",
                    data=summary
                )

            else:
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=False,
                    message=f"Unknown security action: {action}",
                    errors=[f"Unsupported action: {action}"]
                )

        except Exception as e:
            return OperationResult(
                operation_id=operation.operation_id,
                success=False,
                message=f"Security operation failed: {str(e)}",
                errors=[str(e)]
            )

    def _handle_triad_operation(self, operation: ControlOperation, controller: Any) -> OperationResult:
        """Handle Triad Password Manager operations"""
        action = operation.action
        params = operation.parameters

        try:
            if action == "compare_vaults":
                # Create result from comparison
                try:
                    from scripts.python.triad_vault_comparison import compare_vaults
                    compare_vaults()
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=True,
                        message="Triad vault comparison executed successfully",
                        data={"action": "compare_vaults"}
                    )
                except Exception as e:
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=False,
                        message=f"Vault comparison failed: {str(e)}",
                        errors=[str(e)]
                    )

            elif action == "sync_secrets":
                direction = params.get("direction", "azure_to_proton")
                try:
                    from scripts.python.password_manager_sync import PasswordManagerSync
                    sync_manager = PasswordManagerSync(project_root=self.project_root)

                    if direction == "azure_to_proton":
                        secrets = controller.list_secrets(source=None)
                        azure_secrets = secrets.get("azure_key_vault", [])

                        synced_count = 0
                        errors = []

                        for secret_name in azure_secrets:
                            val = controller.get_secret(secret_name, source=None)
                            if val:
                                if controller.set_secret(secret_name, val, source=None):
                                    synced_count += 1
                                else:
                                    errors.append(f"Failed to set {secret_name}")

                        return OperationResult(
                            operation_id=operation.operation_id,
                            success=synced_count > 0,
                            message=f"Synced {synced_count} secrets to Proton",
                            data={"synced_count": synced_count},
                            errors=errors
                        )
                    else:
                        return OperationResult(
                            operation_id=operation.operation_id,
                            success=False,
                            message=f"Unsupported sync direction: {direction}",
                            errors=[f"Unsupported direction: {direction}"]
                        )
                except Exception as e:
                    return OperationResult(
                        operation_id=operation.operation_id,
                        success=False,
                        message=f"Secret sync failed: {str(e)}",
                        errors=[str(e)]
                    )

            elif action == "get_status":
                status = controller.get_status()
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=True,
                    message="Triad status retrieved",
                    data=status
                )

            else:
                return OperationResult(
                    operation_id=operation.operation_id,
                    success=False,
                    message=f"Unknown Triad action: {action}",
                    errors=[f"Unsupported action: {action}"]
                )

        except Exception as e:
            return OperationResult(
                operation_id=operation.operation_id,
                success=False,
                message=f"Triad operation failed: {str(e)}",
                errors=[str(e)]
            )

    def _check_operator_active_block(self, method_name: str = "operation") -> Optional[str]:
        """Check if operator is active and block MANUS operations if so."""
        try:
            from operator_idleness_restriction import \
                get_operator_idleness_restriction
            from jarvis_blacklist_restriction_enforcer import (
                RestrictionType, get_blacklist_enforcer)

            idleness_restriction = get_operator_idleness_restriction(self.project_root)
            blacklist_enforcer = get_blacklist_enforcer(self.project_root)

            # Check if operator is active (not idle)
            operator_is_active = idleness_restriction.is_action_allowed("manus_action")

            if operator_is_active:
                # Operator is actively working - block MANUS operations
                blacklist_enforcer.enforce_restriction(
                    restriction_type=RestrictionType.MANUS_SELF_TEST_BLOCKED,
                    action=f"manus_{method_name}",
                    value=method_name,
                    check_func=lambda *a, **k: (False, f"MANUS {method_name} blocked")
                )

                logger.error("🚫 BLOCKED: MANUS %s while operator active", method_name)

                return f"MANUS {method_name} blocked when operator active (-2 DKP, -XP)"
        except Exception as e:
            logger.debug("Operator active block check failed: %s", e)

        return None

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all controllers"""
        # @BLACKLIST: Block health checks when operator is active
        block_error = self._check_operator_active_block("health_check")
        if block_error:
            return {
                "overall_status": "blocked",
                "error": block_error,
                "controllers": {}
            }

        status = {}
        for area in ControlArea:
            controller = self.controllers.get(area)
            status[area.value] = {
                "available": controller is not None,
                "status": "operational" if controller is not None else "not_implemented"
            }

        return {
            "timestamp": datetime.now().isoformat(),
            "areas": status,
            "total_areas": len(ControlArea),
            "implemented": sum(1 for s in status.values() if s["available"]),
            "status": "operational"
        }

    def get_operation_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get operation history"""
        recent = self.operation_history[-limit:]
        return [
            {
                "operation_id": r.operation_id,
                "success": r.success,
                "message": r.message,
                "duration": r.duration,
                "timestamp": r.timestamp.isoformat()
            }
            for r in recent
        ]


def main():
    try:
        import argparse

        parser = argparse.ArgumentParser(description="MANUS Unified Control Interface")
        parser.add_argument("--area", choices=[a.value for a in ControlArea])
        parser.add_argument("--action", help="Action to execute")
        parser.add_argument("--params", type=json.loads, default={})
        parser.add_argument("--health", action="store_true")
        parser.add_argument("--history", type=int)

        args = parser.parse_args()

        control = MANUSUnifiedControl(project_root)

        if args.health:
            status = control.get_health_status()
            print(json.dumps(status, indent=2))
            return

        if args.history:
            history = control.get_operation_history(args.history)
            print(json.dumps(history, indent=2))
            return

        # Execute operation (requires both area and action)
        if not args.area or not args.action:
            parser.print_help()
            return

        operation = ControlOperation(
            operation_id=f"op_{datetime.now().timestamp()}",
            area=ControlArea(args.area),
            action=args.action,
            parameters=args.params
        )

        result = control.execute_operation(operation)
        print(json.dumps({
            "operation_id": result.operation_id,
            "success": result.success,
            "message": result.message,
            "data": result.data,
            "errors": result.errors,
            "duration": result.duration
        }, indent=2))

    except Exception as e:
        logger.error("Error in main: %s", e, exc_info=True)
        raise


if __name__ == "__main__":


    main()