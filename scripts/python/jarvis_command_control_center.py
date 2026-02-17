#!/usr/bin/env python3
"""
JARVIS Command & Control Center of Operations

The central command hub for JARVIS operations at all scales:
- Global operations coordination
- Planetary-scale resource management
- Solar system-scale strategic planning
- Real-time decision making
- Crisis response
- System orchestration

Integrated with:
- Governance System (Executive Branch)
- Voice Profile System (@AIO)
- AIOS
- All LUMINA systems

Tags: #JARVIS #COMMAND_CONTROL #OPERATIONS #GOVERNANCE #EVOLUTION @JARVIS @LUMINA @PEAK @DTN @EVO
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from jarvis_governance_system import (
        JARVISGovernanceSystem,
        GovernanceScale,
        GovernanceBranch,
        DecisionType
    )
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    logger = get_logger("JARVISCommandControl")
    logger.warning(f"Some imports not available: {e}")
    JARVISGovernanceSystem = None
    GovernanceScale = None
    GovernanceBranch = None
    DecisionType = None

logger = get_logger("JARVISCommandControl")


class OperationStatus(Enum):
    """Operation status"""
    PLANNING = "planning"
    ACTIVE = "active"
    MONITORING = "monitoring"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CrisisLevel(Enum):
    """Crisis severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EXTINCTION = "extinction"  # Planetary/solar system scale


@dataclass
class CommandOperation:
    """A command operation"""
    operation_id: str
    name: str
    scale: str  # GovernanceScale value
    status: str  # OperationStatus value
    priority: int = 5  # 1-10
    resources_required: Dict[str, Any] = field(default_factory=dict)
    systems_involved: List[str] = field(default_factory=list)
    commander: str = "JARVIS"
    created_at: str = ""
    updated_at: str = ""
    completion_percentage: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CrisisResponse:
    """Crisis response operation"""
    crisis_id: str
    level: str  # CrisisLevel value
    description: str
    affected_scale: str  # GovernanceScale value
    response_operations: List[str] = field(default_factory=list)
    status: str = "active"
    resolved_at: Optional[str] = None
    effectiveness_score: float = 0.0


class JARVISCommandControlCenter:
    """
    JARVIS Command & Control Center of Operations

    Central command hub for:
    - Strategic planning
    - Resource coordination
    - Crisis response
    - System orchestration
    - Real-time decision making

    Integrated with Governance System (Executive Branch)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Command & Control Center"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "jarvis_command_control"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Data files
        self.operations_file = self.data_dir / "operations.json"
        self.crises_file = self.data_dir / "crises.json"

        # State
        self.operations: Dict[str, CommandOperation] = {}
        self.active_crises: Dict[str, CrisisResponse] = {}

        # Governance integration
        if JARVISGovernanceSystem:
            try:
                self.governance = JARVISGovernanceSystem(project_root=project_root)
            except Exception as e:
                logger.warning(f"Governance system not available: {e}")
                self.governance = None
        else:
            self.governance = None

        # AIOS integration
        try:
            from lumina.aios import AIOS
            self.aios = AIOS()
            logger.info("✅ AIOS integrated with Command & Control")
        except Exception as e:
            logger.warning(f"AIOS not available: {e}")
            self.aios = None

        # Voice Profile integration (@AIO)
        if self.aios:
            try:
                self.voice_filter = self.aios.create_voice_filter(
                    user_id="jarvis_commander",
                    session_id="command_control_session"
                )
                logger.info("✅ Voice Profile System (@AIO) integrated")
            except Exception as e:
                logger.warning(f"Voice filter not available: {e}")
                self.voice_filter = None
        else:
            self.voice_filter = None

        # Load data
        self._load_data()

        logger.info("✅ JARVIS Command & Control Center initialized")
        logger.info("   Governance Integration: " + ("✅" if self.governance else "❌"))
        logger.info("   AIOS Integration: " + ("✅" if self.aios else "❌"))
        logger.info("   Voice Profile (@AIO): " + ("✅" if self.voice_filter else "❌"))

    def _load_data(self):
        """Load operations and crises"""
        # Load operations
        if self.operations_file.exists():
            try:
                with open(self.operations_file, 'r', encoding='utf-8') as f:
                    import json
                    data = json.load(f)
                    self.operations = {
                        k: CommandOperation(**v) for k, v in data.items()
                    }
            except Exception as e:
                logger.debug(f"Could not load operations: {e}")

        # Load crises
        if self.crises_file.exists():
            try:
                with open(self.crises_file, 'r', encoding='utf-8') as f:
                    import json
                    data = json.load(f)
                    self.active_crises = {
                        k: CrisisResponse(**v) for k, v in data.items()
                    }
            except Exception as e:
                logger.debug(f"Could not load crises: {e}")

    def _save_data(self):
        """Save operations and crises"""
        import json

        # Save operations
        try:
            with open(self.operations_file, 'w', encoding='utf-8') as f:
                json.dump({k: asdict(v) for k, v in self.operations.items()}, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving operations: {e}")

        # Save crises
        try:
            with open(self.crises_file, 'w', encoding='utf-8') as f:
                json.dump({k: asdict(v) for k, v in self.active_crises.items()}, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving crises: {e}")

    def create_operation(
        self,
        name: str,
        scale: str = "global",
        priority: int = 5,
        resources: Optional[Dict[str, Any]] = None,
        systems: Optional[List[str]] = None
    ) -> CommandOperation:
        """
        Create a new command operation

        Can propose to governance system if scale requires approval
        """
        operation_id = f"op_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        operation = CommandOperation(
            operation_id=operation_id,
            name=name,
            scale=scale,
            status=OperationStatus.PLANNING.value,
            priority=priority,
            resources_required=resources or {},
            systems_involved=systems or [],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )

        self.operations[operation_id] = operation

        # If scale requires governance approval, propose decision
        if self.governance and scale in ["planetary", "solar_system", "beyond"]:
            try:
                scale_enum = GovernanceScale[scale.upper()]
                self.governance.propose_decision(
                    branch=GovernanceBranch.EXECUTIVE,
                    decision_type=DecisionType.STRATEGIC,
                    title=f"Operation: {name}",
                    description=f"Strategic operation at {scale} scale",
                    scale=scale_enum,
                    proposer="JARVIS_CommandControl"
                )
            except Exception as e:
                logger.debug(f"Could not propose to governance: {e}")

        self._save_data()

        logger.info(f"   📋 Operation created: {name} ({scale}, priority={priority})")

        return operation

    def activate_operation(self, operation_id: str) -> bool:
        """Activate an operation"""
        if operation_id not in self.operations:
            return False

        operation = self.operations[operation_id]
        operation.status = OperationStatus.ACTIVE.value
        operation.updated_at = datetime.now().isoformat()

        self._save_data()

        logger.info(f"   ⚡ Operation activated: {operation.name}")

        return True

    def update_operation_progress(self, operation_id: str, percentage: float) -> bool:
        """Update operation progress"""
        if operation_id not in self.operations:
            return False

        operation = self.operations[operation_id]
        operation.completion_percentage = min(100.0, max(0.0, percentage))
        operation.updated_at = datetime.now().isoformat()

        if operation.completion_percentage >= 100.0:
            operation.status = OperationStatus.COMPLETED.value

        self._save_data()

        return True

    def declare_crisis(
        self,
        level: str,
        description: str,
        affected_scale: str = "global"
    ) -> CrisisResponse:
        """
        Declare a crisis and initiate response

        Crisis levels trigger different response protocols
        """
        crisis_id = f"crisis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        crisis = CrisisResponse(
            crisis_id=crisis_id,
            level=level,
            description=description,
            affected_scale=affected_scale,
            status="active"
        )

        self.active_crises[crisis_id] = crisis

        # Create emergency response operations
        response_ops = self._create_crisis_response_operations(crisis)
        crisis.response_operations = [op.operation_id for op in response_ops]

        # If critical/extinction level, propose emergency governance decision
        if self.governance and level in ["critical", "extinction"]:
            try:
                scale_enum = GovernanceScale[affected_scale.upper()] if hasattr(GovernanceScale, affected_scale.upper()) else GovernanceScale.GLOBAL
                self.governance.propose_decision(
                    branch=GovernanceBranch.EXECUTIVE,
                    decision_type=DecisionType.STRATEGIC,
                    title=f"CRISIS RESPONSE: {description}",
                    description=f"Emergency response to {level} level crisis at {affected_scale} scale",
                    scale=scale_enum,
                    proposer="JARVIS_CommandControl_Crisis"
                )
            except Exception as e:
                logger.debug(f"Could not propose crisis to governance: {e}")

        self._save_data()

        logger.warning(f"   🚨 CRISIS DECLARED: {level.upper()} - {description}")

        return crisis

    def _create_crisis_response_operations(self, crisis: CrisisResponse) -> List[CommandOperation]:
        """Create response operations for a crisis"""
        operations = []

        # Base response operation
        op = self.create_operation(
            name=f"Crisis Response: {crisis.description}",
            scale=crisis.affected_scale,
            priority=10 if crisis.level == "extinction" else 9,
            resources={"emergency": True, "priority": "maximum"},
            systems=["all_available"]
        )
        operations.append(op)
        self.activate_operation(op.operation_id)

        return operations

    def resolve_crisis(self, crisis_id: str, effectiveness: float = 1.0) -> bool:
        """Resolve a crisis"""
        if crisis_id not in self.active_crises:
            return False

        crisis = self.active_crises[crisis_id]
        crisis.status = "resolved"
        crisis.resolved_at = datetime.now().isoformat()
        crisis.effectiveness_score = effectiveness

        # Complete response operations
        for op_id in crisis.response_operations:
            if op_id in self.operations:
                self.update_operation_progress(op_id, 100.0)

        self._save_data()

        logger.info(f"   ✅ Crisis resolved: {crisis.description} (effectiveness: {effectiveness:.2f})")

        return True

    def get_command_status(self) -> Dict[str, Any]:
        """Get comprehensive command center status"""
        return {
            "operations": {
                "total": len(self.operations),
                "active": sum(1 for o in self.operations.values() 
                             if o.status == OperationStatus.ACTIVE.value),
                "planning": sum(1 for o in self.operations.values() 
                              if o.status == OperationStatus.PLANNING.value),
                "completed": sum(1 for o in self.operations.values() 
                               if o.status == OperationStatus.COMPLETED.value)
            },
            "crises": {
                "active": sum(1 for c in self.active_crises.values() 
                            if c.status == "active"),
                "resolved": sum(1 for c in self.active_crises.values() 
                              if c.status == "resolved"),
                "critical": sum(1 for c in self.active_crises.values() 
                              if c.level == CrisisLevel.CRITICAL.value or c.level == CrisisLevel.EXTINCTION.value)
            },
            "integrations": {
                "governance": self.governance is not None,
                "aios": self.aios is not None,
                "voice_profile": self.voice_filter is not None
            },
            "scales": {
                "local": sum(1 for o in self.operations.values() if o.scale == "local"),
                "global": sum(1 for o in self.operations.values() if o.scale == "global"),
                "planetary": sum(1 for o in self.operations.values() if o.scale == "planetary"),
                "solar_system": sum(1 for o in self.operations.values() if o.scale == "solar_system")
            }
        }


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Command & Control Center")
        parser.add_argument("--status", action="store_true", help="Show command center status")
        parser.add_argument("--create-op", type=str, nargs=2, metavar=("NAME", "SCALE"), help="Create operation")
        parser.add_argument("--crisis", type=str, nargs=3, metavar=("LEVEL", "DESC", "SCALE"), help="Declare crisis")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        center = JARVISCommandControlCenter()

        if args.status:
            status = center.get_command_status()
            if args.json:
                import json
                print(json.dumps(status, indent=2, default=str))
            else:
                print("Command & Control Status:")
                print(f"  Operations: {status['operations']['total']} total, {status['operations']['active']} active")
                print(f"  Crises: {status['crises']['active']} active, {status['crises']['resolved']} resolved")

        elif args.create_op:
            name, scale = args.create_op
            op = center.create_operation(name, scale=scale)
            print(f"✅ Operation created: {op.operation_id}")

        elif args.crisis:
            level, desc, scale = args.crisis
            crisis = center.declare_crisis(level, desc, scale)
            print(f"🚨 Crisis declared: {crisis.crisis_id}")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()