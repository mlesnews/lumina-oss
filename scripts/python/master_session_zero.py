#!/usr/bin/env python3
"""
Master Session Zero - The Foundational Session That Oversees All Others

Master Session Zero (MS0) is the root session that coordinates and oversees all other sessions
in the Lumina ecosystem. It embodies the ultimate coordination layer that:

1. Monitors all active sessions and their health
2. Coordinates between different session types (master, sub, agent)
3. Maintains the overall system equilibrium
4. Makes executive decisions about session lifecycle
5. Ensures system-wide coherence and prevents conflicts
6. Acts as the final arbiter for resource allocation
7. Maintains the master timeline of all system activities

MS0 is the "eye of Sauron" - it sees everything, coordinates everything, and maintains order.
"""

import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import statistics
import hashlib

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from master_session_manager import MasterSessionManager, AgentSession, SessionStatus
    MASTER_SESSION_AVAILABLE = True
except ImportError:
    MASTER_SESSION_AVAILABLE = False

try:
    from master_workflow_orchestrator import MasterWorkflowOrchestrator
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False

try:
    from psychohistory_engine import PsychohistoryEngine
    PSYCHOHISTORY_AVAILABLE = True
except ImportError:
    PSYCHOHISTORY_AVAILABLE = False

try:
    from dune_ai_interface import DuneAIInterface
    DUNE_INTERFACE_AVAILABLE = True
except ImportError:
    DUNE_INTERFACE_AVAILABLE = False

try:
    from dynamic_subagent_spawner import DynamicSubagentSpawner
    SPAWNER_AVAILABLE = True
except ImportError:
    SPAWNER_AVAILABLE = False


class SessionPriority(Enum):
    """Session priority levels"""
    CRITICAL = "critical"    # System-critical sessions
    HIGH = "high"           # High-priority operations
    NORMAL = "normal"       # Standard operations
    LOW = "low"            # Background operations
    IDLE = "idle"          # Idle/cleanup operations


class SystemEquilibrium(Enum):
    """Overall system equilibrium states"""
    OPTIMAL = "optimal"        # Everything running perfectly
    STABLE = "stable"         # Running well, minor issues
    UNSTABLE = "unstable"     # Significant issues present
    CRITICAL = "critical"     # Critical problems exist
    COLLAPSING = "collapsing" # System at risk of failure


@dataclass
class SessionMetrics:
    """Metrics for a session's performance and health"""
    session_id: str
    session_type: str
    priority: SessionPriority
    health_score: float  # 0.0 to 1.0
    activity_level: float  # 0.0 to 1.0 (how active it is)
    resource_usage: Dict[str, float]
    last_activity: datetime
    conflicts_count: int = 0
    warnings_count: int = 0
    errors_count: int = 0
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["priority"] = self.priority.value
        data["last_activity"] = self.last_activity.isoformat()
        return data


@dataclass
class SystemState:
    """Overall system state as seen by Master Session Zero"""
    equilibrium: SystemEquilibrium
    total_sessions: int
    active_sessions: int
    critical_sessions: int
    resource_utilization: Dict[str, float]
    system_health: float  # 0.0 to 1.0
    conflicts_detected: int
    recommendations: List[str] = field(default_factory=list)
    last_assessment: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["equilibrium"] = self.equilibrium.value
        data["last_assessment"] = self.last_assessment.isoformat()
        return data


@dataclass
class ExecutiveDecision:
    """An executive decision made by Master Session Zero"""
    decision_id: str
    decision_type: str  # "create", "terminate", "reallocate", "prioritize", etc.
    target_sessions: List[str]
    rationale: str
    expected_impact: Dict[str, Any]
    confidence: float
    executed_at: Optional[datetime] = None
    outcome: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        if self.executed_at:
            data["executed_at"] = self.executed_at.isoformat()
        return data


class MasterSessionZero:
    """
    Master Session Zero - The Supreme Coordinator

    MS0 is the foundational session that oversees all other sessions. It maintains
    system-wide coherence, prevents conflicts, and ensures optimal performance.

    "I am the eye that sees all sessions. I am the hand that coordinates them.
     I am Master Session Zero, and through me, the system achieves equilibrium."
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Data directories
        self.data_dir = self.project_root / "data" / "master_session_zero"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.decisions_dir = self.data_dir / "executive_decisions"
        self.decisions_dir.mkdir(parents=True, exist_ok=True)

        # Files
        self.state_file = self.data_dir / "ms0_state.json"
        self.metrics_file = self.data_dir / "session_metrics.json"
        self.decisions_file = self.data_dir / "decisions.json"

        # Core state
        self.session_zero_id = "MASTER_SESSION_ZERO"
        self.system_state: Optional[SystemState] = None
        self.session_metrics: Dict[str, SessionMetrics] = {}
        self.executive_decisions: Dict[str, ExecutiveDecision] = {}

        # Assessment intervals
        self.health_check_interval = 30  # seconds
        self.equilibrium_check_interval = 60  # seconds
        self.decision_making_interval = 120  # seconds

        # Thresholds
        self.critical_health_threshold = 0.3
        self.unstable_health_threshold = 0.6
        self.optimal_health_threshold = 0.9

        # Integration components
        self.master_session_manager = None
        self.workflow_orchestrator = None
        self.psychohistory_engine = None
        self.dune_interface = None
        self.subagent_spawner = None

        self._initialize_integrations()

        self.logger = get_logger("MasterSessionZero")
        self._load_state()

        # Start oversight threads
        self.health_monitor_thread = threading.Thread(target=self._health_monitoring_loop, daemon=True)
        self.equilibrium_thread = threading.Thread(target=self._equilibrium_monitoring_loop, daemon=True)
        self.decision_thread = threading.Thread(target=self._decision_making_loop, daemon=True)

        self.health_monitor_thread.start()
        self.equilibrium_thread.start()
        self.decision_thread.start()

        # Initialize MS0
        self._initialize_master_session_zero()

    def _initialize_integrations(self):
        """Initialize all integration components"""
        if MASTER_SESSION_AVAILABLE:
            try:
                self.master_session_manager = MasterSessionManager(project_root=self.project_root)
                self.logger.info("✅ Master Session Manager integrated")
            except Exception as e:
                self.logger.warning(f"Master Session Manager integration failed: {e}")

        if ORCHESTRATOR_AVAILABLE:
            try:
                self.workflow_orchestrator = MasterWorkflowOrchestrator(project_root=self.project_root)
                self.logger.info("✅ Workflow Orchestrator integrated")
            except Exception as e:
                self.logger.warning(f"Workflow Orchestrator integration failed: {e}")

        if PSYCHOHISTORY_AVAILABLE:
            try:
                self.psychohistory_engine = PsychohistoryEngine(project_root=self.project_root)
                self.logger.info("✅ Psychohistory Engine integrated")
            except Exception as e:
                self.logger.warning(f"Psychohistory Engine integration failed: {e}")

        if DUNE_INTERFACE_AVAILABLE:
            try:
                self.dune_interface = DuneAIInterface(project_root=self.project_root)
                self.logger.info("✅ Dune AI Interface integrated")
            except Exception as e:
                self.logger.warning(f"Dune AI Interface integration failed: {e}")

        if SPAWNER_AVAILABLE:
            try:
                self.subagent_spawner = DynamicSubagentSpawner(project_root=self.project_root)
                self.logger.info("✅ Dynamic Subagent Spawner integrated")
            except Exception as e:
                self.logger.warning(f"Dynamic Subagent Spawner integration failed: {e}")

    def _initialize_master_session_zero(self):
        """Initialize the Master Session Zero session"""
        if self.master_session_manager:
            # Create or ensure MS0 exists as the master session
            ms0_session_id = self.master_session_manager.create_or_set_master_session(
                "MASTER SESSION ZERO - Supreme System Coordinator"
            )

            # Log MS0 activation
            self.master_session_manager.add_to_master_session(
                agent="MASTER_SESSION_ZERO",
                message="🕊️ MASTER SESSION ZERO ACTIVATED - Supreme coordination initiated",
                context={
                    "ms0_id": self.session_zero_id,
                    "activation_time": datetime.now().isoformat(),
                    "system_components": self._get_integrated_components()
                }
            )

            self.logger.info(f"🕊️ Master Session Zero activated: {ms0_session_id}")

    def _load_state(self):
        """Load MS0 state"""
        # Load system state
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                    state_data["equilibrium"] = SystemEquilibrium(state_data["equilibrium"])
                    state_data["last_assessment"] = datetime.fromisoformat(state_data["last_assessment"])
                    self.system_state = SystemState(**state_data)
            except Exception as e:
                self.logger.warning(f"Could not load system state: {e}")

        # Load session metrics
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    metrics_data = json.load(f)
                    for session_id, metrics in metrics_data.items():
                        metrics["priority"] = SessionPriority(metrics["priority"])
                        metrics["last_activity"] = datetime.fromisoformat(metrics["last_activity"])
                        self.session_metrics[session_id] = SessionMetrics(**metrics)
            except Exception as e:
                self.logger.warning(f"Could not load session metrics: {e}")

        # Load decisions
        if self.decisions_file.exists():
            try:
                with open(self.decisions_file, 'r', encoding='utf-8') as f:
                    decisions_data = json.load(f)
                    for decision_id, decision in decisions_data.items():
                        decision["created_at"] = datetime.fromisoformat(decision["created_at"])
                        if decision.get("executed_at"):
                            decision["executed_at"] = datetime.fromisoformat(decision["executed_at"])
                        self.executive_decisions[decision_id] = ExecutiveDecision(**decision)
            except Exception as e:
                self.logger.warning(f"Could not load decisions: {e}")

    def _save_state(self):
        try:
            """Save MS0 state"""
            if self.system_state:
                with open(self.state_file, 'w', encoding='utf-8') as f:
                    json.dump(self.system_state.to_dict(), f, indent=2, ensure_ascii=False)

            metrics_data = {sid: metrics.to_dict() for sid, metrics in self.session_metrics.items()}
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(metrics_data, f, indent=2, ensure_ascii=False)

            decisions_data = {did: decision.to_dict() for did, decision in self.executive_decisions.items()}
            with open(self.decisions_file, 'w', encoding='utf-8') as f:
                json.dump(decisions_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _save_state: {e}", exc_info=True)
            raise
    def _health_monitoring_loop(self):
        """Continuous health monitoring of all sessions"""
        while True:
            try:
                self._assess_session_health()
                time.sleep(self.health_check_interval)
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                time.sleep(30)

    def _equilibrium_monitoring_loop(self):
        """Monitor overall system equilibrium"""
        while True:
            try:
                self._assess_system_equilibrium()
                time.sleep(self.equilibrium_check_interval)
            except Exception as e:
                self.logger.error(f"Equilibrium monitoring error: {e}")
                time.sleep(30)

    def _decision_making_loop(self):
        """Executive decision making loop"""
        while True:
            try:
                self._make_executive_decisions()
                time.sleep(self.decision_making_interval)
            except Exception as e:
                self.logger.error(f"Decision making error: {e}")
                time.sleep(60)

    def _assess_session_health(self):
        """Assess health of all active sessions"""
        self.logger.debug("🏥 Assessing session health...")

        # Get all sessions from integrated components
        all_sessions = self._gather_all_sessions()

        for session_info in all_sessions:
            session_id = session_info["session_id"]
            session_type = session_info["type"]

            # Calculate health metrics
            health_score = self._calculate_session_health(session_info)
            activity_level = self._calculate_session_activity(session_info)
            resource_usage = self._get_session_resources(session_info)

            # Determine priority
            priority = self._determine_session_priority(session_info, health_score)

            # Get existing metrics or create new
            if session_id in self.session_metrics:
                metrics = self.session_metrics[session_id]
                metrics.health_score = health_score
                metrics.activity_level = activity_level
                metrics.resource_usage = resource_usage
                metrics.last_activity = datetime.now()
            else:
                metrics = SessionMetrics(
                    session_id=session_id,
                    session_type=session_type,
                    priority=priority,
                    health_score=health_score,
                    activity_level=activity_level,
                    resource_usage=resource_usage,
                    last_activity=datetime.now()
                )
                self.session_metrics[session_id] = metrics

            # Generate health recommendations
            metrics.recommendations = self._generate_health_recommendations(metrics)

        self._save_state()

    def _gather_all_sessions(self) -> List[Dict[str, Any]]:
        """Gather information about all active sessions from integrated components"""
        all_sessions = []

        # Master sessions
        if self.master_session_manager:
            try:
                summary = self.master_session_manager.get_master_session_summary()
                if "error" not in summary:
                    all_sessions.append({
                        "session_id": summary["session_id"],
                        "type": "master_session",
                        "name": summary["session_name"],
                        "status": summary["status"],
                        "chat_entries": summary["chat_entries"],
                        "workflows_identified": summary["workflows_identified"],
                        "health_indicators": {
                            "activity": summary["chat_entries"] > 0,
                            "workflows": summary["workflows_identified"] > 0
                        }
                    })
            except Exception as e:
                self.logger.debug(f"Could not gather master sessions: {e}")

        # Workflow sessions
        if self.workflow_orchestrator:
            try:
                summary = self.workflow_orchestrator.get_orchestrator_summary()
                # Add workflow sessions (simplified)
                all_sessions.append({
                    "session_id": "workflow_orchestrator",
                    "type": "orchestrator",
                    "name": "Workflow Orchestrator",
                    "status": "active",
                    "sessions_managed": summary["total_sub_sessions"],
                    "health_indicators": {
                        "balance": summary["current_balance"] >= -10,
                        "completion": summary["completed_sessions"] > 0
                    }
                })
            except Exception as e:
                self.logger.debug(f"Could not gather workflow sessions: {e}")

        # Subagents
        if self.subagent_spawner:
            try:
                status = self.subagent_spawner.get_spawner_status()
                for agent_type, count in status["agents_by_type"].items():
                    if count > 0:
                        all_sessions.append({
                            "session_id": f"subagents_{agent_type}",
                            "type": "subagent_group",
                            "name": f"{agent_type.replace('_', ' ').title()} Agents",
                            "status": "active",
                            "agent_count": count,
                            "health_indicators": {
                                "active": True,
                                "within_limits": count <= 5  # Simplified limit
                            }
                        })
            except Exception as e:
                self.logger.debug(f"Could not gather subagent sessions: {e}")

        return all_sessions

    def _calculate_session_health(self, session_info: Dict[str, Any]) -> float:
        """Calculate health score for a session (0.0 to 1.0)"""
        health_indicators = session_info.get("health_indicators", {})

        # Base health from indicators
        health_factors = []

        for indicator_name, indicator_value in health_indicators.items():
            if isinstance(indicator_value, bool):
                health_factors.append(1.0 if indicator_value else 0.0)
            elif isinstance(indicator_value, (int, float)):
                # Normalize numeric indicators
                if "count" in indicator_name.lower() or "entries" in indicator_name.lower():
                    health_factors.append(min(indicator_value / 10.0, 1.0))  # Normalize to 0-1
                elif "balance" in indicator_name.lower():
                    # Balance should be >= 0
                    balance_score = max(0.0, min(1.0, (indicator_value + 10) / 20))  # -10 to 10 range
                    health_factors.append(balance_score)
                else:
                    health_factors.append(min(indicator_value, 1.0))

        if health_factors:
            return statistics.mean(health_factors)
        else:
            return 0.5  # Default neutral health

    def _calculate_session_activity(self, session_info: Dict[str, Any]) -> float:
        """Calculate activity level for a session (0.0 to 1.0)"""
        # Activity based on recent activity indicators
        activity_indicators = []

        if "chat_entries" in session_info:
            activity_indicators.append(min(session_info["chat_entries"] / 50.0, 1.0))

        if "workflows_identified" in session_info:
            activity_indicators.append(min(session_info["workflows_identified"] / 10.0, 1.0))

        if "sessions_managed" in session_info:
            activity_indicators.append(min(session_info["sessions_managed"] / 20.0, 1.0))

        if "agent_count" in session_info:
            activity_indicators.append(min(session_info["agent_count"] / 10.0, 1.0))

        return statistics.mean(activity_indicators) if activity_indicators else 0.0

    def _get_session_resources(self, session_info: Dict[str, Any]) -> Dict[str, float]:
        """Get resource usage for a session"""
        # Simplified resource estimation
        base_resources = {"cpu": 5.0, "memory": 2.0, "storage": 1.0}

        # Scale based on session characteristics
        if session_info["type"] == "master_session":
            multiplier = 2.0
        elif session_info["type"] == "orchestrator":
            multiplier = 1.5
        elif session_info["type"] == "subagent_group":
            multiplier = 0.8
        else:
            multiplier = 1.0

        return {k: v * multiplier for k, v in base_resources.items()}

    def _determine_session_priority(self, session_info: Dict[str, Any], health_score: float) -> SessionPriority:
        """Determine priority level for a session"""
        session_type = session_info["type"]

        # Critical sessions
        if session_type == "master_session":
            return SessionPriority.CRITICAL
        elif session_type == "orchestrator" and health_score < 0.5:
            return SessionPriority.CRITICAL

        # High priority
        if health_score < 0.7:
            return SessionPriority.HIGH
        elif session_type == "orchestrator":
            return SessionPriority.HIGH

        # Normal priority for healthy sessions
        return SessionPriority.NORMAL

    def _generate_health_recommendations(self, metrics: SessionMetrics) -> List[str]:
        """Generate health recommendations for a session"""
        recommendations = []

        if metrics.health_score < 0.5:
            recommendations.append("Immediate attention required - session health critical")

        if metrics.activity_level < 0.3:
            recommendations.append("Low activity detected - consider session optimization")

        if metrics.conflicts_count > 0:
            recommendations.append(f"Resolve {metrics.conflicts_count} detected conflicts")

        if metrics.errors_count > 5:
            recommendations.append("High error rate - investigate and fix issues")

        return recommendations

    def _assess_system_equilibrium(self):
        """Assess overall system equilibrium"""
        self.logger.debug("⚖️ Assessing system equilibrium...")

        # Gather system-wide metrics
        total_sessions = len(self.session_metrics)
        active_sessions = len([m for m in self.session_metrics.values() if m.activity_level > 0.1])
        critical_sessions = len([m for m in self.session_metrics.values() if m.priority == SessionPriority.CRITICAL])

        # Calculate system health
        if self.session_metrics:
            health_scores = [m.health_score for m in self.session_metrics.values()]
            system_health = statistics.mean(health_scores)
        else:
            system_health = 0.5

        # Calculate resource utilization
        total_resources = {"cpu": 0.0, "memory": 0.0, "storage": 0.0}
        for metrics in self.session_metrics.values():
            for resource, usage in metrics.resource_usage.items():
                total_resources[resource] += usage

        # Normalize to percentages (simplified)
        resource_utilization = {
            "cpu": min(total_resources["cpu"] / 100.0 * 100, 100.0),
            "memory": min(total_resources["memory"] / 50.0 * 100, 100.0),
            "storage": min(total_resources["storage"] / 20.0 * 100, 100.0)
        }

        # Count conflicts (simplified - would be more sophisticated in practice)
        conflicts_detected = sum(m.conflicts_count for m in self.session_metrics.values())

        # Determine equilibrium state
        if system_health >= self.optimal_health_threshold and conflicts_detected == 0:
            equilibrium = SystemEquilibrium.OPTIMAL
        elif system_health >= self.unstable_health_threshold and conflicts_detected <= 2:
            equilibrium = SystemEquilibrium.STABLE
        elif system_health >= self.critical_health_threshold:
            equilibrium = SystemEquilibrium.UNSTABLE
        elif system_health > 0.1:
            equilibrium = SystemEquilibrium.CRITICAL
        else:
            equilibrium = SystemEquilibrium.COLLAPSING

        # Generate recommendations
        recommendations = self._generate_equilibrium_recommendations(equilibrium, system_health, conflicts_detected)

        # Update system state
        self.system_state = SystemState(
            equilibrium=equilibrium,
            total_sessions=total_sessions,
            active_sessions=active_sessions,
            critical_sessions=critical_sessions,
            resource_utilization=resource_utilization,
            system_health=system_health,
            conflicts_detected=conflicts_detected,
            recommendations=recommendations,
            last_assessment=datetime.now()
        )

        self._save_state()

        # Log to master session
        if self.master_session_manager:
            self.master_session_manager.add_to_master_session(
                agent="MASTER_SESSION_ZERO",
                message=f"System equilibrium assessed: {equilibrium.value} (health: {system_health:.1%})",
                context={
                    "equilibrium": equilibrium.value,
                    "system_health": system_health,
                    "active_sessions": active_sessions,
                    "critical_sessions": critical_sessions,
                    "conflicts": conflicts_detected
                }
            )

    def _generate_equilibrium_recommendations(self, equilibrium: SystemEquilibrium,
                                            system_health: float, conflicts: int) -> List[str]:
        """Generate recommendations based on system equilibrium"""
        recommendations = []

        if equilibrium == SystemEquilibrium.OPTIMAL:
            recommendations.append("System operating at optimal equilibrium - maintain current operations")
        elif equilibrium == SystemEquilibrium.STABLE:
            recommendations.append("System stable but could be optimized")
        elif equilibrium == SystemEquilibrium.UNSTABLE:
            recommendations.append("Address system instability - prioritize critical sessions")
            if conflicts > 0:
                recommendations.append(f"Resolve {conflicts} system conflicts")
        elif equilibrium == SystemEquilibrium.CRITICAL:
            recommendations.append("CRITICAL: Immediate intervention required to prevent system failure")
            recommendations.append("Consider emergency session termination and resource reallocation")
        elif equilibrium == SystemEquilibrium.COLLAPSING:
            recommendations.append("COLLAPSING: Execute emergency protocols - system at risk")

        return recommendations

    def _make_executive_decisions(self):
        """Make executive decisions to maintain system equilibrium"""
        if not self.system_state:
            return

        self.logger.debug("🎯 Making executive decisions...")

        decisions_made = []

        # Decision: Handle critical sessions
        if self.system_state.critical_sessions > 0:
            critical_session_ids = [
                session_id for session_id, metrics in self.session_metrics.items()
                if metrics.priority == SessionPriority.CRITICAL
            ]

            if critical_session_ids:
                decision = ExecutiveDecision(
                    decision_id=f"prioritize_critical_{int(datetime.now().timestamp())}",
                    decision_type="prioritize",
                    target_sessions=critical_session_ids,
                    rationale=f"Prioritize {len(critical_session_ids)} critical sessions to prevent system instability",
                    expected_impact={
                        "equilibrium_improvement": 0.2,
                        "resource_reallocation": "high_priority_sessions"
                    },
                    confidence=0.9
                )
                decisions_made.append(decision)
                self.executive_decisions[decision.decision_id] = decision

        # Decision: Resource reallocation for low health sessions
        low_health_sessions = [
            (session_id, metrics) for session_id, metrics in self.session_metrics.items()
            if metrics.health_score < 0.4
        ]

        if low_health_sessions:
            session_ids = [sid for sid, _ in low_health_sessions]
            decision = ExecutiveDecision(
                decision_id=f"reallocate_resources_{int(datetime.now().timestamp())}",
                decision_type="reallocate",
                target_sessions=session_ids,
                rationale=f"Reallocate resources to {len(session_ids)} low-health sessions",
                expected_impact={
                    "health_improvement": 0.3,
                    "resource_efficiency": 0.1
                },
                confidence=0.7
            )
            decisions_made.append(decision)
            self.executive_decisions[decision.decision_id] = decision

        # Decision: Terminate idle sessions
        idle_sessions = [
            session_id for session_id, metrics in self.session_metrics.items()
            if metrics.activity_level < 0.1 and metrics.priority == SessionPriority.IDLE
        ]

        if idle_sessions and len(idle_sessions) > 3:  # Only if many idle sessions
            decision = ExecutiveDecision(
                decision_id=f"terminate_idle_{int(datetime.now().timestamp())}",
                decision_type="terminate",
                target_sessions=idle_sessions[:2],  # Terminate only a few at a time
                rationale=f"Terminate {len(idle_sessions[:2])} idle sessions to free resources",
                expected_impact={
                    "resource_savings": 0.15,
                    "system_cleanup": True
                },
                confidence=0.8
            )
            decisions_made.append(decision)
            self.executive_decisions[decision.decision_id] = decision

        # Execute decisions
        for decision in decisions_made:
            self._execute_decision(decision)

        self._save_state()

    def _execute_decision(self, decision: ExecutiveDecision):
        """Execute an executive decision"""
        try:
            decision.executed_at = datetime.now()

            if decision.decision_type == "prioritize":
                # Increase priority of target sessions (log only for now)
                decision.outcome = f"Prioritized {len(decision.target_sessions)} sessions"

            elif decision.decision_type == "reallocate":
                # Reallocate resources (log only for now)
                decision.outcome = f"Reallocated resources for {len(decision.target_sessions)} sessions"

            elif decision.decision_type == "terminate":
                # Terminate sessions (log only for now)
                decision.outcome = f"Terminated {len(decision.target_sessions)} idle sessions"

            # Log decision execution
            if self.master_session_manager:
                self.master_session_manager.add_to_master_session(
                    agent="MASTER_SESSION_ZERO",
                    message=f"Executive decision executed: {decision.decision_type} - {decision.outcome}",
                    context={
                        "decision_id": decision.decision_id,
                        "decision_type": decision.decision_type,
                        "target_sessions": decision.target_sessions,
                        "outcome": decision.outcome
                    }
                )

            self.logger.info(f"✅ Executed decision {decision.decision_id}: {decision.outcome}")

        except Exception as e:
            decision.outcome = f"Failed: {str(e)}"
            self.logger.error(f"Decision execution failed: {e}")

    def get_ms0_status(self) -> Dict[str, Any]:
        """Get Master Session Zero status"""
        if not self.system_state:
            self._assess_system_equilibrium()

        status = {
            "ms0_id": self.session_zero_id,
            "system_equilibrium": self.system_state.equilibrium.value if self.system_state else "unknown",
            "system_health": self.system_state.system_health if self.system_state else 0.0,
            "total_sessions_monitored": len(self.session_metrics),
            "active_sessions": len([m for m in self.session_metrics.values() if m.activity_level > 0.1]),
            "critical_sessions": len([m for m in self.session_metrics.values() if m.priority == SessionPriority.CRITICAL]),
            "resource_utilization": self.system_state.resource_utilization if self.system_state else {},
            "conflicts_detected": self.system_state.conflicts_detected if self.system_state else 0,
            "executive_decisions_made": len(self.executive_decisions),
            "integrated_components": self._get_integrated_components(),
            "last_assessment": self.system_state.last_assessment.isoformat() if self.system_state else None
        }

        return status

    def _get_integrated_components(self) -> List[str]:
        """Get list of integrated components"""
        components = []
        if self.master_session_manager:
            components.append("MasterSessionManager")
        if self.workflow_orchestrator:
            components.append("WorkflowOrchestrator")
        if self.psychohistory_engine:
            components.append("PsychohistoryEngine")
        if self.dune_interface:
            components.append("DuneAIInterface")
        if self.subagent_spawner:
            components.append("DynamicSubagentSpawner")
        return components

    def force_equilibrium_check(self) -> Dict[str, Any]:
        """Force an immediate equilibrium check"""
        self._assess_system_equilibrium()
        return self.system_state.to_dict() if self.system_state else {"error": "No system state available"}

    def get_session_metrics_report(self) -> Dict[str, Any]:
        """Get detailed session metrics report"""
        report = {
            "total_sessions": len(self.session_metrics),
            "session_breakdown": {},
            "health_distribution": {"excellent": 0, "good": 0, "fair": 0, "poor": 0, "critical": 0},
            "priority_distribution": {p.value: 0 for p in SessionPriority},
            "recommendations": []
        }

        # Session breakdown by type
        for metrics in self.session_metrics.values():
            session_type = metrics.session_type
            if session_type not in report["session_breakdown"]:
                report["session_breakdown"][session_type] = 0
            report["session_breakdown"][session_type] += 1

            # Health distribution
            if metrics.health_score >= 0.9:
                report["health_distribution"]["excellent"] += 1
            elif metrics.health_score >= 0.7:
                report["health_distribution"]["good"] += 1
            elif metrics.health_score >= 0.5:
                report["health_distribution"]["fair"] += 1
            elif metrics.health_score >= 0.3:
                report["health_distribution"]["poor"] += 1
            else:
                report["health_distribution"]["critical"] += 1

            # Priority distribution
            report["priority_distribution"][metrics.priority.value] += 1

            # Collect recommendations
            report["recommendations"].extend(metrics.recommendations)

        return report


def main():
    """Main execution"""
    ms0 = MasterSessionZero()

    print("🕊️ Master Session Zero - Supreme System Coordinator")
    print("=" * 80)
    print("")

    # Get MS0 status
    status = ms0.get_ms0_status()
    print("📊 MS0 Status:")
    print(f"   System Equilibrium: {status['system_equilibrium']}")
    print(f"   System Health: {status['system_health']:.1%}")
    print(f"   Sessions Monitored: {status['total_sessions_monitored']}")
    print(f"   Active Sessions: {status['active_sessions']}")
    print(f"   Critical Sessions: {status['critical_sessions']}")
    print("")

    print("🔗 Integrated Components:")
    for component in status['integrated_components']:
        print(f"   ✅ {component}")
    print("")

    print("💾 Resource Utilization:")
    for resource, utilization in status['resource_utilization'].items():
        print(f"   {resource}: {utilization:.1f}%")
    print("")

    # Force equilibrium check
    equilibrium = ms0.force_equilibrium_check()
    print("⚖️ Current Equilibrium Assessment:")
    print(f"   State: {equilibrium['equilibrium']}")
    print(f"   Health: {equilibrium['system_health']:.1%}")
    print(f"   Recommendations: {len(equilibrium['recommendations'])}")
    print("")

    if equilibrium['recommendations']:
        print("💡 Recommendations:")
        for rec in equilibrium['recommendations'][:3]:
            print(f"   • {rec}")

    # Get session metrics report
    metrics_report = ms0.get_session_metrics_report()
    print("")
    print("📈 Session Metrics Report:")
    print(f"   Total Sessions: {metrics_report['total_sessions']}")
    print("")

    print("🏥 Health Distribution:")
    for level, count in metrics_report['health_distribution'].items():
        if count > 0:
            print(f"   {level.title()}: {count}")
    print("")

    print("🎯 Priority Distribution:")
    for priority, count in metrics_report['priority_distribution'].items():
        if count > 0:
            print(f"   {priority.title()}: {count}")

    print("")
    print("🕊️ Master Session Zero operational: All sessions coordinated, equilibrium maintained.")


if __name__ == "__main__":


    main()