#!/usr/bin/env python3
"""
<COMPANY_ABBR> Command Center Supervisor
<COMPANY_NAME> LLC - Agent Management & Command Center

@MARVIN @JARVIS @TONY @MACE @GANDALF

Comprehensive supervision and management of ALL agents for <COMPANY_ABBR> LLC operations:
- All registered agents (c3po, r2d2, k2so, 2-1b, ig88, mousedroid, uatu, chat agents)
- Chat agent connection management integration
- Status reporting and information aggregation
- Command center operations support
- Agent health monitoring and supervision
- Resource allocation and load balancing

"Marvin, you have a lot of agents underneath you that you need to manage and supervise.
And they also need to provide the information necessary for you to run the command center."
"""

import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_unified_logger import get_unified_logger
    logger = get_unified_logger("Application", "CFSCommandCenter")
except ImportError:
    try:
        from lumina_logger import get_logger
        logger = get_logger("CFSCommandCenterSupervisor")
    except ImportError:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("CFSCommandCenterSupervisor")

# Import agent connection manager
try:
    from chat_agent_connection_manager import (
        ChatAgentConnectionManager,
        ChatAgentConnection,
        AgentConnectionState
    )
    CHAT_AGENT_MANAGER_AVAILABLE = True
except ImportError:
    CHAT_AGENT_MANAGER_AVAILABLE = False
    ChatAgentConnectionManager = None

# Import error operations center
try:
    from enterprise_error_operations_center import (
        EnterpriseErrorOperationsCenter,
        ErrorSeverity,
        ErrorCategory
    )
    ERROR_OPS_AVAILABLE = True
except ImportError:
    ERROR_OPS_AVAILABLE = False
    EnterpriseErrorOperationsCenter = None



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class AgentType(Enum):
    """Agent types"""
    CHAT_AGENT = "chat_agent"  # LLM chat agents
    SYSTEM_AGENT = "system_agent"  # System agents (c3po, r2d2, etc.)
    MONITORING_AGENT = "monitoring_agent"  # Monitoring agents
    AUTOMATION_AGENT = "automation_agent"  # Automation agents


class AgentStatus(Enum):
    """Agent status"""
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    DEGRADED = "degraded"
    FAILED = "failed"
    REPAIRING = "repairing"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


class ShiftManager(Enum):
    """Shift managers for command center"""
    TONY = "tony"      # Shift 1: 00:00-08:00 (Midnight to 8 AM)
    MACE = "mace"      # Shift 2: 08:00-16:00 (8 AM to 4 PM)
    GANDALF = "gandalf"  # Shift 3: 16:00-00:00 (4 PM to Midnight)


class Team(Enum):
    """Agent teams for rotation"""
    TEAM_A = "team_a"  # System agents (c3po, r2d2, k2so, etc.)
    TEAM_B = "team_b"  # Chat agents and LLM services
    TEAM_C = "team_c"  # Automation and workflow agents


@dataclass
class ShiftInfo:
    """Current shift information"""
    shift_manager: ShiftManager
    shift_name: str
    start_time: datetime
    end_time: datetime
    shift_number: int

    def is_active(self, current_time: Optional[datetime] = None) -> bool:
        """Check if this shift is currently active"""
        if current_time is None:
            current_time = datetime.now()
        return self.start_time <= current_time < self.end_time

    def time_remaining(self, current_time: Optional[datetime] = None) -> timedelta:
        """Get time remaining in shift"""
        if current_time is None:
            current_time = datetime.now()
        if not self.is_active(current_time):
            return timedelta(0)
        return self.end_time - current_time

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "shift_manager": self.shift_manager.value,
            "shift_name": self.shift_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "shift_number": self.shift_number,
            "is_active": self.is_active(),
            "time_remaining_seconds": self.time_remaining().total_seconds()
        }


@dataclass
class AgentInfo:
    """Agent information for command center"""
    agent_id: str
    agent_name: str
    agent_type: AgentType
    status: AgentStatus
    capabilities: List[str]
    connection_state: Optional[str] = None  # For chat agents

    # Health metrics
    health_score: float = 100.0  # 0-100
    last_heartbeat: Optional[datetime] = None
    uptime_seconds: float = 0.0

    # Performance metrics
    request_count: int = 0
    success_count: int = 0
    error_count: int = 0
    success_rate: float = 100.0
    avg_response_time_ms: float = 0.0

    # Resource usage
    cpu_usage: float = 0.0
    memory_usage_mb: float = 0.0
    active_tasks: int = 0

    # Operational data
    last_status_update: Optional[datetime] = None
    last_alert: Optional[datetime] = None
    alerts_count: int = 0

    # Command center data
    operational_data: Dict[str, Any] = field(default_factory=dict)
    recent_activities: List[str] = field(default_factory=list)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['agent_type'] = self.agent_type.value
        data['status'] = self.status.value
        if self.last_heartbeat:
            data['last_heartbeat'] = self.last_heartbeat.isoformat()
        if self.last_status_update:
            data['last_status_update'] = self.last_status_update.isoformat()
        if self.last_alert:
            data['last_alert'] = self.last_alert.isoformat()
        return data

    def is_healthy(self) -> bool:
        """Check if agent is healthy"""
        return (self.status in [AgentStatus.ACTIVE, AgentStatus.IDLE, AgentStatus.BUSY] and
                self.health_score >= 70.0 and
                self.success_rate >= 80.0)

    def needs_attention(self) -> bool:
        """Check if agent needs attention"""
        return (self.status in [AgentStatus.DEGRADED, AgentStatus.FAILED, AgentStatus.REPAIRING] or
                self.health_score < 70.0 or
                self.success_rate < 80.0 or
                self.error_count > 10)


@dataclass
class CommandCenterStatus:
    """Command center status report"""
    timestamp: datetime
    total_agents: int
    healthy_agents: int
    degraded_agents: int
    failed_agents: int
    repairing_agents: int

    # System health
    overall_health_score: float
    system_uptime_seconds: float

    # Operational metrics
    total_requests: int
    total_errors: int
    overall_success_rate: float

    # Resource usage
    total_cpu_usage: float
    total_memory_usage_mb: float

    # Critical alerts
    critical_alerts: List[str]
    recent_events: List[Dict[str, Any]]

    # Agent details
    agents: Dict[str, AgentInfo]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['agents'] = {k: v.to_dict() for k, v in self.agents.items()}
        return data


class CFSCommandCenterSupervisor:
    """
    <COMPANY_ABBR> Command Center Supervisor

    Manages and supervises ALL agents for <COMPANY_NAME> LLC.
    Provides comprehensive command center operations support.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize <COMPANY_ABBR> Command Center Supervisor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        try:
            from lumina_unified_logger import get_unified_logger
            self.logger = get_unified_logger("Application", "CFSCommandCenter")
        except ImportError:
            try:
                from lumina_logger import get_logger
                self.logger = get_logger("CFSCommandCenterSupervisor")
            except ImportError:
                logging.basicConfig(level=logging.INFO)
                self.logger = logging.getLogger("CFSCommandCenterSupervisor")

        # Data directories
        self.data_dir = self.project_root / "data" / "command_center"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Agent registry
        self.agent_registry_path = self.project_root / "config" / "agent_communication" / "agents.json"
        self.registered_agents: Dict[str, Dict[str, Any]] = {}
        self.agent_info: Dict[str, AgentInfo] = {}

        # Chat agent connection manager
        self.chat_agent_manager: Optional[ChatAgentConnectionManager] = None
        if CHAT_AGENT_MANAGER_AVAILABLE:
            try:
                self.chat_agent_manager = ChatAgentConnectionManager(project_root)
                self.logger.info("✅ Integrated with Chat Agent Connection Manager")
            except Exception as e:
                self.logger.warning(f"Could not initialize chat agent manager: {e}")

        # Error operations center
        self.error_ops: Optional[EnterpriseErrorOperationsCenter] = None
        if ERROR_OPS_AVAILABLE:
            try:
                # Initialize error ops if needed
                self.logger.info("✅ Error Operations Center available")
            except Exception as e:
                self.logger.warning(f"Could not initialize error ops: {e}")

        # Monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.start_time = datetime.now()

        # Shift management
        self.current_shift: Optional[ShiftInfo] = None
        self.shift_history: List[ShiftInfo] = []
        self._update_shift()

        # Team rotation management (6-8 week cycle, independent of shift rotation)
        self.team_assignments: Dict[Team, ShiftManager] = {}
        self.team_rotation_week = 0
        self._update_team_assignments()

        # Command center data
        self.command_center_data: Dict[str, Any] = {
            "system_status": "operational",
            "last_full_report": None,
            "critical_issues": [],
            "operational_metrics": {},
            "current_shift_manager": self.current_shift.shift_manager.value if self.current_shift else None,
            "team_assignments": {team.value: manager.value for team, manager in self.team_assignments.items()}
        }

        # Load agent registry
        self._load_agent_registry()

        # Initialize all agents
        self._initialize_all_agents()

        # Start monitoring
        self.start_monitoring()

        self.logger.info("✅ <COMPANY_ABBR> Command Center Supervisor initialized")
        self.logger.info(f"   Managing {len(self.agent_info)} agents")
        self.logger.info("   Command center operations: ACTIVE")
        if self.current_shift:
            # Calculate rotation week for display
            rotation_start_date = datetime(2026, 1, 1)
            days_since_start = (datetime.now().date() - rotation_start_date.date()).days
            rotation_week = (days_since_start // 7) % 3
            rotation_week_names = ["Week 1", "Week 2", "Week 3"]

            self.logger.info(f"   Current Shift Manager: {self.current_shift.shift_manager.value.upper()} ({self.current_shift.shift_name})")
            self.logger.info(f"   Shift: {self.current_shift.start_time.strftime('%H:%M')} - {self.current_shift.end_time.strftime('%H:%M')}")
            self.logger.info(f"   Rotation: {rotation_week_names[rotation_week]} of 3-week cycle (HR Recommended Schedule)")
            self.logger.info("   Schedule: 8-hour shifts with 3-week rotation")

            # Log team assignments
            team_assignments = self.get_team_assignments()
            self.logger.info("   Team Assignments (6-week rotation):")
            for team, manager in team_assignments.items():
                self.logger.info(f"     {team.value.upper()}: {manager.value.upper()}")

    def _update_shift(self) -> None:
        """
        Update current shift based on time and 3-week rotation schedule.

        Rotation Schedule (HR Recommended):
        Week 1: Night=Tony, Day=Mace, Evening=Gandalf
        Week 2: Night=Mace, Day=Gandalf, Evening=Tony
        Week 3: Night=Gandalf, Day=Tony, Evening=Mace
        """
        now = datetime.now()
        current_hour = now.hour

        # Calculate which week of the 3-week rotation we're in
        # Use a fixed start date (e.g., January 1, 2026) to calculate rotation week
        rotation_start_date = datetime(2026, 1, 1)  # Start of rotation cycle
        days_since_start = (now.date() - rotation_start_date.date()).days
        rotation_week = (days_since_start // 7) % 3  # 0, 1, or 2 (Week 1, 2, or 3)

        # Determine shift time slot based on hour
        if 0 <= current_hour < 8:
            shift_name = "Night Shift"
            shift_number = 1
            # Start at midnight today
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            # End at 8 AM today
            end_time = now.replace(hour=8, minute=0, second=0, microsecond=0)

            # Assign manager based on rotation week
            if rotation_week == 0:  # Week 1
                shift_manager = ShiftManager.TONY
            elif rotation_week == 1:  # Week 2
                shift_manager = ShiftManager.MACE
            else:  # Week 3
                shift_manager = ShiftManager.GANDALF

        elif 8 <= current_hour < 16:
            shift_name = "Day Shift"
            shift_number = 2
            # Start at 8 AM today
            start_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
            # End at 4 PM today
            end_time = now.replace(hour=16, minute=0, second=0, microsecond=0)

            # Assign manager based on rotation week
            if rotation_week == 0:  # Week 1
                shift_manager = ShiftManager.MACE
            elif rotation_week == 1:  # Week 2
                shift_manager = ShiftManager.GANDALF
            else:  # Week 3
                shift_manager = ShiftManager.TONY

        else:  # 16 <= current_hour < 24
            shift_name = "Evening Shift"
            shift_number = 3
            # Start at 4 PM today
            start_time = now.replace(hour=16, minute=0, second=0, microsecond=0)
            # End at midnight tomorrow
            end_time = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

            # Assign manager based on rotation week
            if rotation_week == 0:  # Week 1
                shift_manager = ShiftManager.GANDALF
            elif rotation_week == 1:  # Week 2
                shift_manager = ShiftManager.TONY
            else:  # Week 3
                shift_manager = ShiftManager.MACE

        # Check if shift changed
        shift_changed = False
        if self.current_shift is None or self.current_shift.shift_manager != shift_manager:
            shift_changed = True
            if self.current_shift:
                # Log shift handoff
                self.logger.info(f"🔄 SHIFT HANDOFF: {self.current_shift.shift_manager.value.upper()} → {shift_manager.value.upper()}")
                self.shift_history.append(self.current_shift)
                # Keep only last 24 shifts (8 days)
                if len(self.shift_history) > 24:
                    self.shift_history.pop(0)

        # Determine rotation week name for logging
        rotation_week_names = ["Week 1", "Week 2", "Week 3"]
        rotation_week_name = rotation_week_names[rotation_week]

        self.current_shift = ShiftInfo(
            shift_manager=shift_manager,
            shift_name=shift_name,
            start_time=start_time,
            end_time=end_time,
            shift_number=shift_number
        )

        if shift_changed:
            self.logger.info(f"👔 Shift Manager {shift_manager.value.upper()} now on duty ({rotation_week_name})")
            self.logger.info(f"   Shift: {shift_name} ({start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')})")
            self.logger.info(f"   Rotation: {rotation_week_name} of 3-week cycle")

    def get_current_shift_manager(self) -> ShiftManager:
        """Get current shift manager"""
        self._update_shift()  # Ensure shift is up to date
        return self.current_shift.shift_manager if self.current_shift else ShiftManager.TONY

    def get_shift_info(self) -> Optional[ShiftInfo]:
        """Get current shift information"""
        self._update_shift()  # Ensure shift is up to date
        return self.current_shift

    def _update_team_assignments(self) -> None:
        """
        Update team assignments based on 6-week rotation cycle.

        Team Rotation Schedule (HR Recommended):
        Weeks 1-2: Team A→Tony, Team B→Mace, Team C→Gandalf
        Weeks 3-4: Team A→Mace, Team B→Gandalf, Team C→Tony
        Weeks 5-6: Team A→Gandalf, Team B→Tony, Team C→Mace
        """
        now = datetime.now()

        # Calculate which 2-week period of the 6-week rotation we're in
        # Use a fixed start date (e.g., January 1, 2026) to calculate rotation
        rotation_start_date = datetime(2026, 1, 1)
        days_since_start = (now.date() - rotation_start_date.date()).days
        weeks_since_start = days_since_start // 7
        rotation_period = (weeks_since_start // 2) % 3  # 0, 1, or 2 (each period is 2 weeks)

        # Assign teams based on rotation period
        if rotation_period == 0:  # Weeks 1-2
            self.team_assignments = {
                Team.TEAM_A: ShiftManager.TONY,
                Team.TEAM_B: ShiftManager.MACE,
                Team.TEAM_C: ShiftManager.GANDALF
            }
            self.team_rotation_week = 1
        elif rotation_period == 1:  # Weeks 3-4
            self.team_assignments = {
                Team.TEAM_A: ShiftManager.MACE,
                Team.TEAM_B: ShiftManager.GANDALF,
                Team.TEAM_C: ShiftManager.TONY
            }
            self.team_rotation_week = 3
        else:  # Weeks 5-6
            self.team_assignments = {
                Team.TEAM_A: ShiftManager.GANDALF,
                Team.TEAM_B: ShiftManager.TONY,
                Team.TEAM_C: ShiftManager.MACE
            }
            self.team_rotation_week = 5

        # Update command center data
        self.command_center_data["team_assignments"] = {
            team.value: manager.value for team, manager in self.team_assignments.items()
        }
        self.command_center_data["team_rotation_week"] = self.team_rotation_week

    def get_team_assignments(self) -> Dict[Team, ShiftManager]:
        """Get current team assignments"""
        self._update_team_assignments()  # Ensure assignments are up to date
        return self.team_assignments.copy()

    def get_manager_teams(self, manager: ShiftManager) -> List[Team]:
        """Get teams assigned to a specific manager"""
        assignments = self.get_team_assignments()
        return [team for team, mgr in assignments.items() if mgr == manager]

    def get_rotation_schedule(self) -> Dict[str, Any]:
        """Get the full rotation schedules (shift and team)"""
        schedule = {
            "shift_rotation": {
                "rotation_type": "3-week rotation (HR Recommended)",
                "shift_duration": "8 hours",
                "schedule": {
                    "week_1": {
                        "night_shift_00_08": "Tony",
                        "day_shift_08_16": "Mace",
                        "evening_shift_16_00": "Gandalf"
                    },
                    "week_2": {
                        "night_shift_00_08": "Mace",
                        "day_shift_08_16": "Gandalf",
                        "evening_shift_16_00": "Tony"
                    },
                    "week_3": {
                        "night_shift_00_08": "Gandalf",
                        "day_shift_08_16": "Tony",
                        "evening_shift_16_00": "Mace"
                    }
                },
                "benefits": [
                    "Fair distribution of all shifts",
                    "Everyone experiences each shift type",
                    "Better work-life balance",
                    "Optimal coverage with 3-person team",
                    "Weekend coverage included in rotation"
                ]
            },
            "team_rotation": {
                "rotation_type": "6-week rotation (HR Recommended)",
                "rotation_cycle": "2 weeks per assignment",
                "schedule": {
                    "weeks_1_2": {
                        "team_a": "Tony",
                        "team_b": "Mace",
                        "team_c": "Gandalf"
                    },
                    "weeks_3_4": {
                        "team_a": "Mace",
                        "team_b": "Gandalf",
                        "team_c": "Tony"
                    },
                    "weeks_5_6": {
                        "team_a": "Gandalf",
                        "team_b": "Tony",
                        "team_c": "Mace"
                    }
                },
                "team_descriptions": {
                    "team_a": "System agents (c3po, r2d2, k2so, etc.)",
                    "team_b": "Chat agents and LLM services",
                    "team_c": "Automation and workflow agents"
                },
                "benefits": [
                    "Cross-training across all teams",
                    "Knowledge sharing between managers",
                    "Better operational resilience",
                    "Reduced single points of failure",
                    "Flexibility for reassignments"
                ]
            },
            "hr_recommendation": "Dual rotation: 3-week shift rotation + 6-week team rotation (independent cycles)"
        }
        return schedule

    def _load_agent_registry(self) -> None:
        """Load agent registry from config"""
        if self.agent_registry_path.exists():
            try:
                with open(self.agent_registry_path, 'r') as f:
                    self.registered_agents = json.load(f)
                self.logger.info(f"📋 Loaded {len(self.registered_agents)} registered agents")
            except Exception as e:
                self.logger.error(f"Failed to load agent registry: {e}")
        else:
            self.logger.warning(f"Agent registry not found: {self.agent_registry_path}")

    def _initialize_all_agents(self) -> None:
        """Initialize all registered agents"""
        # Initialize system agents from registry
        for agent_id, agent_data in self.registered_agents.items():
            if not agent_data.get('active', True):
                continue

            agent_info = AgentInfo(
                agent_id=agent_id,
                agent_name=agent_data.get('agent_name', agent_id),
                agent_type=AgentType.SYSTEM_AGENT,
                status=AgentStatus.ACTIVE,
                capabilities=agent_data.get('capabilities', []),
                last_heartbeat=datetime.now(),
                last_status_update=datetime.now(),
                metadata={
                    'registered_at': agent_data.get('registered_at'),
                    'message_types': agent_data.get('message_types', [])
                }
            )

            self.agent_info[agent_id] = agent_info
            self.logger.info(f"📝 Initialized agent: {agent_info.agent_name} ({agent_id})")

        # Initialize chat agents from connection manager
        if self.chat_agent_manager:
            for agent_id, connection in self.chat_agent_manager.connections.items():
                agent_info = AgentInfo(
                    agent_id=agent_id,
                    agent_name=f"Chat Agent {agent_id}",
                    agent_type=AgentType.CHAT_AGENT,
                    status=self._map_connection_state_to_status(connection.state),
                    connection_state=connection.state.value,
                    capabilities=["llm_chat", "conversation", "code_assistance"],
                    health_score=self._calculate_health_from_connection(connection),
                    last_heartbeat=connection.last_activity,
                    success_rate=connection.success_rate,
                    error_count=connection.error_count,
                    request_count=connection.request_count,
                    avg_response_time_ms=connection.avg_response_time_ms,
                    cpu_usage=connection.cpu_usage,
                    memory_usage_mb=connection.memory_usage_mb,
                    active_tasks=connection.active_requests,
                    metadata={
                        'connection_type': connection.connection_type,
                        'repair_status': connection.repair_status.value,
                        'disconnect_count': connection.disconnect_count,
                        'reconnect_count': connection.reconnect_count
                    }
                )

                self.agent_info[agent_id] = agent_info
                self.logger.info(f"📝 Initialized chat agent: {agent_id}")

    def _map_connection_state_to_status(self, state: AgentConnectionState) -> AgentStatus:
        """Map connection state to agent status"""
        mapping = {
            AgentConnectionState.CONNECTED: AgentStatus.ACTIVE,
            AgentConnectionState.CONNECTING: AgentStatus.BUSY,
            AgentConnectionState.DISCONNECTED: AgentStatus.OFFLINE,
            AgentConnectionState.DISCONNECTING: AgentStatus.DEGRADED,
            AgentConnectionState.RECONNECTING: AgentStatus.REPAIRING,
            AgentConnectionState.STALLED: AgentStatus.DEGRADED,
            AgentConnectionState.REPAIRING: AgentStatus.REPAIRING,
            AgentConnectionState.DEGRADED: AgentStatus.DEGRADED,
            AgentConnectionState.FAILED: AgentStatus.FAILED
        }
        return mapping.get(state, AgentStatus.UNKNOWN)

    def _calculate_health_from_connection(self, connection: ChatAgentConnection) -> float:
        """Calculate health score from connection"""
        base_score = 100.0

        # Deduct for errors
        if connection.error_count > 0:
            base_score -= min(30.0, connection.error_count * 2.0)

        # Deduct for low success rate
        if connection.success_rate < 100.0:
            base_score -= (100.0 - connection.success_rate) * 0.3

        # Deduct for disconnects
        if connection.disconnect_count > 0:
            base_score -= min(20.0, connection.disconnect_count * 5.0)

        # Deduct for repair status
        if connection.repair_status.value == "in_progress":
            base_score -= 10.0
        elif connection.repair_status.value == "failed":
            base_score -= 30.0

        return max(0.0, min(100.0, base_score))

    def update_agent_status(self, agent_id: str, status_data: Dict[str, Any]) -> bool:
        """Update agent status from agent report"""
        if agent_id not in self.agent_info:
            # Auto-register if not found
            self.logger.info(f"Auto-registering agent: {agent_id}")
            agent_info = AgentInfo(
                agent_id=agent_id,
                agent_name=status_data.get('agent_name', agent_id),
                agent_type=AgentType.SYSTEM_AGENT,
                status=AgentStatus.ACTIVE,
                capabilities=status_data.get('capabilities', [])
            )
            self.agent_info[agent_id] = agent_info

        agent_info = self.agent_info[agent_id]

        # Update status
        if 'status' in status_data:
            try:
                agent_info.status = AgentStatus(status_data['status'])
            except ValueError:
                pass

        # Update metrics
        if 'health_score' in status_data:
            agent_info.health_score = float(status_data['health_score'])
        if 'success_rate' in status_data:
            agent_info.success_rate = float(status_data['success_rate'])
        if 'error_count' in status_data:
            agent_info.error_count = int(status_data['error_count'])
        if 'request_count' in status_data:
            agent_info.request_count = int(status_data['request_count'])
        if 'cpu_usage' in status_data:
            agent_info.cpu_usage = float(status_data['cpu_usage'])
        if 'memory_usage_mb' in status_data:
            agent_info.memory_usage_mb = float(status_data['memory_usage_mb'])
        if 'active_tasks' in status_data:
            agent_info.active_tasks = int(status_data['active_tasks'])

        # Update operational data
        if 'operational_data' in status_data:
            agent_info.operational_data.update(status_data['operational_data'])

        # Update heartbeat
        agent_info.last_heartbeat = datetime.now()
        agent_info.last_status_update = datetime.now()

        # Update uptime
        if agent_info.last_heartbeat:
            agent_info.uptime_seconds = (datetime.now() - self.start_time).total_seconds()

        return True

    def get_agent_status(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent status"""
        return self.agent_info.get(agent_id)

    def get_all_agents_status(self) -> Dict[str, AgentInfo]:
        """Get status of all agents"""
        return self.agent_info.copy()

    def get_command_center_status(self) -> CommandCenterStatus:
        """Get comprehensive command center status"""
        # Update chat agent statuses from connection manager
        if self.chat_agent_manager:
            for agent_id, connection in self.chat_agent_manager.connections.items():
                if agent_id in self.agent_info:
                    agent_info = self.agent_info[agent_id]
                    agent_info.status = self._map_connection_state_to_status(connection.state)
                    agent_info.health_score = self._calculate_health_from_connection(connection)
                    agent_info.success_rate = connection.success_rate
                    agent_info.error_count = connection.error_count
                    agent_info.request_count = connection.request_count
                    agent_info.last_heartbeat = connection.last_activity

        # Calculate aggregate metrics
        total_agents = len(self.agent_info)
        healthy_agents = sum(1 for a in self.agent_info.values() if a.is_healthy())
        degraded_agents = sum(1 for a in self.agent_info.values() 
                            if a.status == AgentStatus.DEGRADED)
        failed_agents = sum(1 for a in self.agent_info.values() 
                          if a.status == AgentStatus.FAILED)
        repairing_agents = sum(1 for a in self.agent_info.values() 
                             if a.status == AgentStatus.REPAIRING)

        # Calculate overall health
        if total_agents > 0:
            overall_health = (healthy_agents / total_agents) * 100.0
        else:
            overall_health = 0.0

        # Aggregate metrics
        total_requests = sum(a.request_count for a in self.agent_info.values())
        total_errors = sum(a.error_count for a in self.agent_info.values())
        total_success = sum(a.success_count for a in self.agent_info.values())

        if total_requests > 0:
            overall_success_rate = (total_success / total_requests) * 100.0
        else:
            overall_success_rate = 100.0

        total_cpu = sum(a.cpu_usage for a in self.agent_info.values())
        total_memory = sum(a.memory_usage_mb for a in self.agent_info.values())

        # Critical alerts
        critical_alerts = []
        for agent_id, agent_info in self.agent_info.items():
            if agent_info.needs_attention():
                critical_alerts.append(
                    f"{agent_info.agent_name} ({agent_id}): "
                    f"Status={agent_info.status.value}, "
                    f"Health={agent_info.health_score:.1f}%, "
                    f"Success={agent_info.success_rate:.1f}%"
                )

        # Recent events
        recent_events = []
        for agent_id, agent_info in self.agent_info.items():
            if agent_info.recent_activities:
                recent_events.append({
                    "agent_id": agent_id,
                    "agent_name": agent_info.agent_name,
                    "activities": agent_info.recent_activities[-5:]  # Last 5 activities
                })

        return CommandCenterStatus(
            timestamp=datetime.now(),
            total_agents=total_agents,
            healthy_agents=healthy_agents,
            degraded_agents=degraded_agents,
            failed_agents=failed_agents,
            repairing_agents=repairing_agents,
            overall_health_score=overall_health,
            system_uptime_seconds=(datetime.now() - self.start_time).total_seconds(),
            total_requests=total_requests,
            total_errors=total_errors,
            overall_success_rate=overall_success_rate,
            total_cpu_usage=total_cpu,
            total_memory_usage_mb=total_memory,
            critical_alerts=critical_alerts,
            recent_events=recent_events,
            agents=self.agent_info.copy()
        )

    def get_command_center_report(self) -> Dict[str, Any]:
        """Get comprehensive command center report for <COMPANY_ABBR> LLC operations"""
        status = self.get_command_center_status()

        # Agent summaries by type
        agents_by_type: Dict[str, List[Dict[str, Any]]] = {}
        for agent_id, agent_info in self.agent_info.items():
            agent_type = agent_info.agent_type.value
            if agent_type not in agents_by_type:
                agents_by_type[agent_type] = []

            agents_by_type[agent_type].append({
                "agent_id": agent_id,
                "agent_name": agent_info.agent_name,
                "status": agent_info.status.value,
                "health_score": agent_info.health_score,
                "success_rate": agent_info.success_rate,
                "capabilities": agent_info.capabilities
            })

        # Operational readiness
        operational_readiness = {
            "all_systems_operational": status.overall_health_score >= 90.0,
            "degraded_systems": status.degraded_agents > 0,
            "failed_systems": status.failed_agents > 0,
            "requires_attention": len(status.critical_alerts) > 0
        }

        # Resource utilization
        resource_utilization = {
            "total_cpu_percent": status.total_cpu_usage,
            "total_memory_mb": status.total_memory_usage_mb,
            "average_cpu_per_agent": status.total_cpu_usage / max(1, status.total_agents),
            "average_memory_per_agent": status.total_memory_usage_mb / max(1, status.total_agents)
        }

        # Performance metrics
        performance_metrics = {
            "total_requests": status.total_requests,
            "total_errors": status.total_errors,
            "overall_success_rate": status.overall_success_rate,
            "system_uptime_hours": status.system_uptime_seconds / 3600.0
        }

        # Get current shift info
        shift_info = self.get_shift_info()
        team_assignments = self.get_team_assignments()

        report = {
            "report_timestamp": datetime.now().isoformat(),
            "command_center": "<COMPANY_NAME> LLC",
            "shift_management": {
                "current_shift_manager": shift_info.shift_manager.value if shift_info else None,
                "shift_name": shift_info.shift_name if shift_info else None,
                "shift_number": shift_info.shift_number if shift_info else None,
                "shift_start": shift_info.start_time.isoformat() if shift_info else None,
                "shift_end": shift_info.end_time.isoformat() if shift_info else None,
                "time_remaining_seconds": shift_info.time_remaining().total_seconds() if shift_info else None
            },
            "team_management": {
                "team_rotation_week": self.team_rotation_week,
                "team_assignments": {team.value: manager.value for team, manager in team_assignments.items()},
                "rotation_cycle": "6-week team rotation (HR Recommended)"
            },
            "system_status": status.to_dict(),
            "operational_readiness": operational_readiness,
            "resource_utilization": resource_utilization,
            "performance_metrics": performance_metrics,
            "agents_by_type": agents_by_type,
            "critical_alerts": status.critical_alerts,
            "recommendations": self._generate_recommendations(status),
            "integrations": {
                "chat_agent_manager": CHAT_AGENT_MANAGER_AVAILABLE and self.chat_agent_manager is not None,
                "error_operations_center": ERROR_OPS_AVAILABLE and self.error_ops is not None
            }
        }

        return report

    def _generate_recommendations(self, status: CommandCenterStatus) -> List[str]:
        """Generate recommendations based on status"""
        recommendations = []

        if status.failed_agents > 0:
            recommendations.append(f"URGENT: {status.failed_agents} agent(s) failed - immediate attention required")

        if status.degraded_agents > 0:
            recommendations.append(f"WARNING: {status.degraded_agents} agent(s) degraded - investigate and repair")

        if status.overall_health_score < 80.0:
            recommendations.append("System health below optimal - review agent configurations")

        if status.overall_success_rate < 90.0:
            recommendations.append("Success rate below target - investigate error patterns")

        if len(status.critical_alerts) > 0:
            recommendations.append(f"{len(status.critical_alerts)} critical alert(s) require attention")

        if status.repairing_agents > 0:
            recommendations.append(f"{status.repairing_agents} agent(s) currently repairing - monitor progress")

        if not recommendations:
            recommendations.append("All systems operational - no action required")

        return recommendations

    def start_monitoring(self) -> None:
        """Start command center monitoring"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()

        self.logger.info("✅ Command center monitoring started")

    def _monitoring_loop(self) -> None:
        """Monitoring loop"""
        while self.monitoring_active:
            try:
                # Update shift (check for shift changes)
                previous_shift = self.current_shift.shift_manager if self.current_shift else None
                self._update_shift()
                if self.current_shift and previous_shift != self.current_shift.shift_manager:
                    # Shift changed - log it
                    self.logger.info(f"🔄 Shift rotation detected - {self.current_shift.shift_manager.value.upper()} now on duty")

                # Update team assignments (check for team rotation changes)
                previous_team_week = self.team_rotation_week
                previous_assignments = self.team_assignments.copy()
                self._update_team_assignments()
                if self.team_rotation_week != previous_team_week:
                    # Team rotation changed - log it
                    self.logger.info(f"👥 Team rotation detected - Week {self.team_rotation_week} of 6-week cycle")
                    self.logger.info("   New Team Assignments:")
                    for team, manager in self.team_assignments.items():
                        if team not in previous_assignments or previous_assignments[team] != manager:
                            self.logger.info(f"     {team.value.upper()}: {manager.value.upper()}")

                # Update agent statuses
                self._update_all_agent_statuses()

                # Generate and save report
                report = self.get_command_center_report()
                self._save_report(report)

                # Check for critical issues
                self._check_critical_issues()

                time.sleep(30)  # Update every 30 seconds
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(30)

    def _update_all_agent_statuses(self) -> None:
        """Update all agent statuses"""
        # Update from chat agent manager
        if self.chat_agent_manager:
            for agent_id, connection in self.chat_agent_manager.connections.items():
                if agent_id in self.agent_info:
                    agent_info = self.agent_info[agent_id]
                    agent_info.status = self._map_connection_state_to_status(connection.state)
                    agent_info.health_score = self._calculate_health_from_connection(connection)
                    agent_info.success_rate = connection.success_rate
                    agent_info.error_count = connection.error_count
                    agent_info.request_count = connection.request_count
                    agent_info.last_heartbeat = connection.last_activity

    def _check_critical_issues(self) -> None:
        """Check for critical issues"""
        status = self.get_command_center_status()

        if status.failed_agents > 0 or len(status.critical_alerts) > 0:
            self.logger.warning(f"⚠️  Critical issues detected: {status.failed_agents} failed, {len(status.critical_alerts)} alerts")

    def _save_report(self, report: Dict[str, Any]) -> None:
        """Save command center report"""
        report_file = self.data_dir / f"command_center_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)

            # Keep only last 100 reports
            reports = sorted(self.data_dir.glob("command_center_report_*.json"))
            if len(reports) > 100:
                for old_report in reports[:-100]:
                    old_report.unlink()
        except Exception as e:
            self.logger.debug(f"Could not save report: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="<COMPANY_ABBR> Command Center Supervisor",
        epilog="""
NOTE: This command should be executed through JARVIS CLI Orchestrator.
Direct execution is allowed for backward compatibility, but JARVIS orchestration
is recommended for proper escalation and decisioning tree integration.

Use: python jarvis_cli_orchestrator.py execute command_center_status
        """
    )
    parser.add_argument("--status", action="store_true", help="Get command center status")
    parser.add_argument("--report", action="store_true", help="Get full command center report")
    parser.add_argument("--agent", type=str, help="Get specific agent status")
    parser.add_argument("--shift", action="store_true", help="Get current shift information")
    parser.add_argument("--schedule", action="store_true", help="Show full rotation schedule")
    parser.add_argument("--teams", action="store_true", help="Show current team assignments")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--jarvis-orchestrated", action="store_true", 
                       help="Flag indicating JARVIS orchestration (internal use)")

    args = parser.parse_args()

    # Log if not orchestrated by JARVIS
    if not args.jarvis_orchestrated:
        logger.warning("⚠️  Command executed directly - consider using JARVIS CLI Orchestrator")
        logger.warning("   Use: python jarvis_cli_orchestrator.py execute command_center_status")

    supervisor = CFSCommandCenterSupervisor()

    if args.teams:
        team_assignments = supervisor.get_team_assignments()
        if args.json:
            print(json.dumps({
                team.value: manager.value for team, manager in team_assignments.items()
            }, indent=2))
        else:
            print("\n👥 Current Team Assignments (6-Week Rotation)")
            print("=" * 60)
            print(f"Rotation Week: {supervisor.team_rotation_week} of 6-week cycle")
            print("\nTeam Assignments:")
            for team, manager in team_assignments.items():
                team_desc = {
                    Team.TEAM_A: "System agents (c3po, r2d2, k2so, etc.)",
                    Team.TEAM_B: "Chat agents and LLM services",
                    Team.TEAM_C: "Automation and workflow agents"
                }.get(team, "")
                print(f"  {team.value.upper()}: {manager.value.upper()}")
                if team_desc:
                    print(f"    └─ {team_desc}")
            print("\n💡 Benefits of Team Rotation:")
            print("  • Cross-training across all teams")
            print("  • Knowledge sharing between managers")
            print("  • Better operational resilience")
            print("  • Reduced single points of failure")

    elif args.schedule:
        schedule = supervisor.get_rotation_schedule()
        if args.json:
            print(json.dumps(schedule, indent=2))
        else:
            print("\n📅 Complete Rotation Schedules (HR Recommended)")
            print("=" * 60)

            # Shift rotation
            shift_rot = schedule['shift_rotation']
            print("\n🕐 SHIFT ROTATION (3-Week Cycle)")
            print(f"Rotation Type: {shift_rot['rotation_type']}")
            print(f"Shift Duration: {shift_rot['shift_duration']}")
            print("\nWeek 1:")
            print(f"  Night (00:00-08:00):   {shift_rot['schedule']['week_1']['night_shift_00_08']}")
            print(f"  Day (08:00-16:00):     {shift_rot['schedule']['week_1']['day_shift_08_16']}")
            print(f"  Evening (16:00-00:00): {shift_rot['schedule']['week_1']['evening_shift_16_00']}")
            print("\nWeek 2:")
            print(f"  Night (00:00-08:00):   {shift_rot['schedule']['week_2']['night_shift_00_08']}")
            print(f"  Day (08:00-16:00):     {shift_rot['schedule']['week_2']['day_shift_08_16']}")
            print(f"  Evening (16:00-00:00): {shift_rot['schedule']['week_2']['evening_shift_16_00']}")
            print("\nWeek 3:")
            print(f"  Night (00:00-08:00):   {shift_rot['schedule']['week_3']['night_shift_00_08']}")
            print(f"  Day (08:00-16:00):     {shift_rot['schedule']['week_3']['day_shift_08_16']}")
            print(f"  Evening (16:00-00:00): {shift_rot['schedule']['week_3']['evening_shift_16_00']}")

            # Team rotation
            team_rot = schedule['team_rotation']
            print("\n👥 TEAM ROTATION (6-Week Cycle)")
            print(f"Rotation Type: {team_rot['rotation_type']}")
            print(f"Rotation Cycle: {team_rot['rotation_cycle']}")
            print("\nWeeks 1-2:")
            print(f"  Team A: {team_rot['schedule']['weeks_1_2']['team_a']} ({team_rot['team_descriptions']['team_a']})")
            print(f"  Team B: {team_rot['schedule']['weeks_1_2']['team_b']} ({team_rot['team_descriptions']['team_b']})")
            print(f"  Team C: {team_rot['schedule']['weeks_1_2']['team_c']} ({team_rot['team_descriptions']['team_c']})")
            print("\nWeeks 3-4:")
            print(f"  Team A: {team_rot['schedule']['weeks_3_4']['team_a']}")
            print(f"  Team B: {team_rot['schedule']['weeks_3_4']['team_b']}")
            print(f"  Team C: {team_rot['schedule']['weeks_3_4']['team_c']}")
            print("\nWeeks 5-6:")
            print(f"  Team A: {team_rot['schedule']['weeks_5_6']['team_a']}")
            print(f"  Team B: {team_rot['schedule']['weeks_5_6']['team_b']}")
            print(f"  Team C: {team_rot['schedule']['weeks_5_6']['team_c']}")

            print("\n✅ Benefits:")
            print("  Shift Rotation:")
            for benefit in shift_rot['benefits']:
                print(f"    • {benefit}")
            print("  Team Rotation:")
            for benefit in team_rot['benefits']:
                print(f"    • {benefit}")

    elif args.shift:
        shift_info = supervisor.get_shift_info()
        if shift_info:
            if args.json:
                print(json.dumps(shift_info.to_dict(), indent=2))
            else:
                print("\n👔 Current Shift Information")
                print("=" * 60)
                print(f"Shift Manager: {shift_info.shift_manager.value.upper()}")
                print(f"Shift Name: {shift_info.shift_name}")
                print(f"Shift Number: {shift_info.shift_number}")
                print(f"Start Time: {shift_info.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"End Time: {shift_info.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
                time_remaining = shift_info.time_remaining()
                hours = int(time_remaining.total_seconds() // 3600)
                minutes = int((time_remaining.total_seconds() % 3600) // 60)
                print(f"Time Remaining: {hours}h {minutes}m")
                print(f"Active: {shift_info.is_active()}")
                print("\n📋 Shift Times:")
                print("  • Night:   00:00 - 08:00")
                print("  • Day:     08:00 - 16:00")
                print("  • Evening: 16:00 - 00:00")
                print("\n💡 Use --schedule to see full 3-week rotation")
        else:
            print("No shift information available")

    elif args.agent:
        agent_info = supervisor.get_agent_status(args.agent)
        if agent_info:
            if args.json:
                print(json.dumps(agent_info.to_dict(), indent=2))
            else:
                print(f"\n🤖 Agent Status: {agent_info.agent_name} ({args.agent})")
                print(f"   Status: {agent_info.status.value}")
                print(f"   Health: {agent_info.health_score:.1f}%")
                print(f"   Success Rate: {agent_info.success_rate:.1f}%")
                print(f"   Requests: {agent_info.request_count}, Errors: {agent_info.error_count}")
        else:
            print(f"Agent not found: {args.agent}")

    elif args.report:
        report = supervisor.get_command_center_report()
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("\n🏢 <COMPANY_ABBR> Command Center Report")
            print("=" * 60)
            if 'shift_management' in report and report['shift_management']['current_shift_manager']:
                shift = report['shift_management']
                print(f"👔 Shift Manager: {shift['current_shift_manager'].upper()} ({shift['shift_name']})")
                if shift.get('time_remaining_seconds'):
                    hours = int(shift['time_remaining_seconds'] // 3600)
                    minutes = int((shift['time_remaining_seconds'] % 3600) // 60)
                    print(f"   Time Remaining: {hours}h {minutes}m")
            print(f"Total Agents: {report['system_status']['total_agents']}")
            print(f"Healthy Agents: {report['system_status']['healthy_agents']}")
            print(f"Overall Health: {report['system_status']['overall_health_score']:.1f}%")
            print(f"Success Rate: {report['performance_metrics']['overall_success_rate']:.1f}%")
            print(f"\nCritical Alerts: {len(report['critical_alerts'])}")
            for alert in report['critical_alerts'][:5]:
                print(f"  ⚠️  {alert}")
            print(f"\nRecommendations:")
            for rec in report['recommendations']:
                print(f"  • {rec}")

    elif args.status:
        status = supervisor.get_command_center_status()
        if args.json:
            print(json.dumps(status.to_dict(), indent=2))
        else:
            shift_info = supervisor.get_shift_info()
            print("\n🏢 <COMPANY_ABBR> Command Center Status")
            print("=" * 60)
            if shift_info:
                print(f"👔 Shift Manager: {shift_info.shift_manager.value.upper()} ({shift_info.shift_name})")
                print(f"   Shift: {shift_info.start_time.strftime('%H:%M')} - {shift_info.end_time.strftime('%H:%M')}")
                time_remaining = shift_info.time_remaining()
                hours = int(time_remaining.total_seconds() // 3600)
                minutes = int((time_remaining.total_seconds() % 3600) // 60)
                print(f"   Time Remaining: {hours}h {minutes}m")
            print(f"Total Agents: {status.total_agents}")
            print(f"Healthy: {status.healthy_agents}, Degraded: {status.degraded_agents}, Failed: {status.failed_agents}")
            print(f"Overall Health: {status.overall_health_score:.1f}%")
            print(f"Success Rate: {status.overall_success_rate:.1f}%")

    else:
        parser.print_help()
        print("\n🏢 <COMPANY_ABBR> Command Center Supervisor")
        print("   Managing all agents for <COMPANY_NAME> LLC")

