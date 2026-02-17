#!/usr/bin/env python3
"""
Dynamic Subagent Spawner - Anticipatory Agent Creation System

This system uses psychohistory predictions to anticipate needs and spawn subagents
before they're explicitly requested. It embodies the Dune AI concept of prescience
by predicting what agents will be needed and creating them proactively.

Key Features:
1. Predictive Agent Spawning - Creates agents based on predicted needs
2. Resource Anticipation - Allocates resources before demand spikes
3. Proactive Problem Solving - Addresses issues before they become critical
4. Adaptive Scaling - Scales agent populations based on predicted workload
5. Prescience-Driven Coordination - Coordinates agents based on future scenarios
"""

import json
import time
import asyncio
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
    from master_workflow_orchestrator import MasterWorkflowOrchestrator, SubSessionStatus
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False

try:
    from master_session_manager import MasterSessionManager
    MASTER_SESSION_AVAILABLE = True
except ImportError:
    MASTER_SESSION_AVAILABLE = False


class AnticipationTrigger(Enum):
    """Types of triggers that cause anticipatory spawning"""
    WORKLOAD_SPIKE = "workload_spike"          # Predicted workload increase
    RESOURCE_SHORTAGE = "resource_shortage"    # Predicted resource constraints
    FAILURE_PROBABILITY = "failure_probability" # High failure risk prediction
    COMPLEXITY_INCREASE = "complexity_increase" # Predicted complexity rise
    PATTERN_RECOGNITION = "pattern_recognition" # Recognized behavioral patterns
    TEMPORAL_CYCLE = "temporal_cycle"          # Time-based cyclical needs
    CORRELATION_TRIGGER = "correlation_trigger" # Correlated variable changes


class SubagentType(Enum):
    """Types of subagents that can be spawned"""
    WORKFLOW_EXECUTOR = "workflow_executor"     # Executes workflows
    RESOURCE_MANAGER = "resource_manager"       # Manages resources
    QUALITY_ASSURANCE = "quality_assurance"     # Ensures quality
    MONITORING_AGENT = "monitoring_agent"       # Monitors systems
    OPTIMIZATION_AGENT = "optimization_agent"   # Optimizes performance
    RECOVERY_AGENT = "recovery_agent"           # Handles failures
    COORDINATION_AGENT = "coordination_agent"   # Coordinates other agents
    PREDICTION_AGENT = "prediction_agent"       # Makes predictions


@dataclass
class AnticipationSignal:
    """A signal that triggers anticipatory action"""
    signal_id: str
    trigger_type: AnticipationTrigger
    confidence: float  # 0.0 to 1.0
    urgency: int  # 1-10, 10 is most urgent
    description: str
    predicted_impact: Dict[str, Any]  # Expected impact if not addressed
    recommended_actions: List[str]
    time_to_impact: int  # minutes until impact
    detected_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["trigger_type"] = self.trigger_type.value
        data["detected_at"] = self.detected_at.isoformat()
        return data


@dataclass
class SpawnedSubagent:
    """A dynamically spawned subagent"""
    agent_id: str
    agent_type: SubagentType
    trigger_signal: str  # ID of signal that triggered spawning
    spawned_at: datetime
    expected_lifetime: int  # minutes
    assigned_tasks: List[str] = field(default_factory=list)
    resources_allocated: Dict[str, float] = field(default_factory=dict)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    status: str = "active"  # active, completed, terminated
    termination_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["agent_type"] = self.agent_type.value
        data["spawned_at"] = self.spawned_at.isoformat()
        return data


@dataclass
class AnticipationModel:
    """Model for predicting when to spawn subagents"""
    model_id: str
    trigger_type: AnticipationTrigger
    variables: List[str]  # Variables that trigger this model
    threshold_conditions: Dict[str, Any]  # When to trigger
    confidence_threshold: float
    historical_accuracy: float = 0.0
    times_triggered: int = 0
    successful_spawns: int = 0
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["trigger_type"] = self.trigger_type.value
        data["created_at"] = self.created_at.isoformat()
        return data


class DynamicSubagentSpawner:
    """
    Dynamic Subagent Spawner

    Uses psychohistory predictions to anticipate needs and spawn subagents proactively.
    This embodies the prescience of Dune AI - knowing what agents are needed before they're requested.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Data directories
        self.data_dir = self.project_root / "data" / "subagent_spawner"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.agents_dir = self.data_dir / "active_agents"
        self.agents_dir.mkdir(parents=True, exist_ok=True)

        # Files
        self.signals_file = self.data_dir / "anticipation_signals.json"
        self.agents_file = self.data_dir / "spawned_agents.json"
        self.models_file = self.data_dir / "anticipation_models.json"

        # State
        self.anticipation_signals: Dict[str, AnticipationSignal] = {}
        self.spawned_agents: Dict[str, SpawnedSubagent] = {}
        self.anticipation_models: Dict[str, AnticipationModel] = {}

        # Configuration
        self.monitoring_interval = 60  # seconds
        self.max_concurrent_agents = 10
        self.resource_limits = {
            "cpu": 80.0,  # Max 80% CPU
            "memory": 85.0,  # Max 85% memory
            "api_calls": 1000  # Max 1000 API calls per hour
        }

        # Integration
        self.psychohistory_engine = None
        self.dune_interface = None
        self.workflow_orchestrator = None
        self.master_session_manager = None

        if PSYCHOHISTORY_AVAILABLE:
            try:
                self.psychohistory_engine = PsychohistoryEngine(project_root=self.project_root)
                self.logger.info("✅ Psychohistory Engine integrated")
            except Exception as e:
                self.logger.warning(f"Psychohistory Engine not available: {e}")

        if DUNE_INTERFACE_AVAILABLE:
            try:
                self.dune_interface = DuneAIInterface(project_root=self.project_root)
                self.logger.info("✅ Dune AI Interface integrated")
            except Exception as e:
                self.logger.warning(f"Dune AI Interface not available: {e}")

        if ORCHESTRATOR_AVAILABLE:
            try:
                self.workflow_orchestrator = MasterWorkflowOrchestrator(project_root=self.project_root)
                self.logger.info("✅ Workflow Orchestrator integrated")
            except Exception as e:
                self.logger.warning(f"Workflow Orchestrator not available: {e}")

        if MASTER_SESSION_AVAILABLE:
            try:
                self.master_session_manager = MasterSessionManager(project_root=self.project_root)
                self.logger.info("✅ Master Session Manager integrated")
            except Exception as e:
                self.logger.warning(f"Master Session Manager not available: {e}")

        self.logger = get_logger("DynamicSubagentSpawner")
        self._load_state()
        self._initialize_anticipation_models()

        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()

    def _load_state(self):
        """Load spawner state"""
        # Load signals
        if self.signals_file.exists():
            try:
                with open(self.signals_file, 'r', encoding='utf-8') as f:
                    signals_data = json.load(f)
                    for signal_id, signal_data in signals_data.items():
                        signal_data["trigger_type"] = AnticipationTrigger(signal_data["trigger_type"])
                        signal_data["detected_at"] = datetime.fromisoformat(signal_data["detected_at"])
                        self.anticipation_signals[signal_id] = AnticipationSignal(**signal_data)
            except Exception as e:
                self.logger.warning(f"Could not load signals: {e}")

        # Load agents
        if self.agents_file.exists():
            try:
                with open(self.agents_file, 'r', encoding='utf-8') as f:
                    agents_data = json.load(f)
                    for agent_id, agent_data in agents_data.items():
                        agent_data["agent_type"] = SubagentType(agent_data["agent_type"])
                        agent_data["spawned_at"] = datetime.fromisoformat(agent_data["spawned_at"])
                        self.spawned_agents[agent_id] = SpawnedSubagent(**agent_data)
            except Exception as e:
                self.logger.warning(f"Could not load agents: {e}")

        # Load models
        if self.models_file.exists():
            try:
                with open(self.models_file, 'r', encoding='utf-8') as f:
                    models_data = json.load(f)
                    for model_id, model_data in models_data.items():
                        model_data["trigger_type"] = AnticipationTrigger(model_data["trigger_type"])
                        model_data["created_at"] = datetime.fromisoformat(model_data["created_at"])
                        self.anticipation_models[model_id] = AnticipationModel(**model_data)
            except Exception as e:
                self.logger.warning(f"Could not load models: {e}")

    def _save_state(self):
        try:
            """Save spawner state"""
            # Save signals
            signals_data = {sid: signal.to_dict() for sid, signal in self.anticipation_signals.items()}
            with open(self.signals_file, 'w', encoding='utf-8') as f:
                json.dump(signals_data, f, indent=2, ensure_ascii=False)

            # Save agents
            agents_data = {aid: agent.to_dict() for aid, agent in self.spawned_agents.items()}
            with open(self.agents_file, 'w', encoding='utf-8') as f:
                json.dump(agents_data, f, indent=2, ensure_ascii=False)

            # Save models
            models_data = {mid: model.to_dict() for mid, model in self.anticipation_models.items()}
            with open(self.models_file, 'w', encoding='utf-8') as f:
                json.dump(models_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _save_state: {e}", exc_info=True)
            raise
    def _initialize_anticipation_models(self):
        """Initialize default anticipation models"""
        default_models = [
            {
                "model_id": "workload_spike_detector",
                "trigger_type": AnticipationTrigger.WORKLOAD_SPIKE,
                "variables": ["session_complexity", "time_of_day"],
                "threshold_conditions": {
                    "session_complexity": {"operator": ">", "value": 0.8},
                    "time_of_day": {"operator": "between", "value": [0.3, 0.7]}  # Peak hours
                },
                "confidence_threshold": 0.7
            },
            {
                "model_id": "resource_shortage_predictor",
                "trigger_type": AnticipationTrigger.RESOURCE_SHORTAGE,
                "variables": ["resource_availability", "workflow_success_rate"],
                "threshold_conditions": {
                    "resource_availability": {"operator": "<", "value": 0.3},
                    "workflow_success_rate": {"operator": "<", "value": 0.7}
                },
                "confidence_threshold": 0.8
            },
            {
                "model_id": "failure_probability_monitor",
                "trigger_type": AnticipationTrigger.FAILURE_PROBABILITY,
                "variables": ["workflow_success_rate", "system_stability"],
                "threshold_conditions": {
                    "workflow_success_rate": {"operator": "<", "value": 0.6},
                    "system_stability": {"operator": "<", "value": 0.7}
                },
                "confidence_threshold": 0.75
            },
            {
                "model_id": "temporal_cycle_anticipator",
                "trigger_type": AnticipationTrigger.TEMPORAL_CYCLE,
                "variables": ["time_of_day", "agent_experience"],
                "threshold_conditions": {
                    "time_of_day": {"operator": "in", "value": [0.25, 0.75]},  # Business hours
                    "agent_experience": {"operator": ">", "value": 0.5}
                },
                "confidence_threshold": 0.6
            }
        ]

        for model_config in default_models:
            model_id = model_config["model_id"]
            if model_id not in self.anticipation_models:
                self.anticipation_models[model_id] = AnticipationModel(**model_config)

        self._save_state()

    def _monitoring_loop(self):
        """Main monitoring loop for anticipatory spawning"""
        while True:
            try:
                # Scan for anticipation signals
                self._scan_for_anticipation_signals()

                # Process active signals
                self._process_anticipation_signals()

                # Clean up expired agents
                self._cleanup_expired_agents()

                # Update agent performance
                self._update_agent_performance()

                time.sleep(self.monitoring_interval)

            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(30)  # Retry sooner on error

    def _scan_for_anticipation_signals(self):
        """Scan various sources for anticipation signals"""
        self.logger.debug("🔍 Scanning for anticipation signals...")

        signals_found = []

        # Scan psychohistory predictions
        if self.psychohistory_engine:
            try:
                prescience_report = self.psychohistory_engine.generate_prescience_report()
                psychohistory_signals = self._extract_signals_from_psychohistory(prescience_report)
                signals_found.extend(psychohistory_signals)
            except Exception as e:
                self.logger.debug(f"Psychohistory signal extraction failed: {e}")

        # Scan Dune AI interface insights
        if self.dune_interface:
            try:
                dashboard = self.dune_interface.get_prescience_dashboard()
                dune_signals = self._extract_signals_from_dune_interface(dashboard)
                signals_found.extend(dune_signals)
            except Exception as e:
                self.logger.debug(f"Dune interface signal extraction failed: {e}")

        # Scan workflow orchestrator status
        if self.workflow_orchestrator:
            try:
                orchestrator_data = self.workflow_orchestrator.get_orchestrator_summary()
                workflow_signals = self._extract_signals_from_orchestrator(orchestrator_data)
                signals_found.extend(workflow_signals)
            except Exception as e:
                self.logger.debug(f"Orchestrator signal extraction failed: {e}")

        # Apply anticipation models to generate additional signals
        model_signals = self._apply_anticipation_models()
        signals_found.extend(model_signals)

        # Add new signals
        for signal in signals_found:
            if signal.signal_id not in self.anticipation_signals:
                self.anticipation_signals[signal.signal_id] = signal
                self.logger.info(f"🚨 Detected anticipation signal: {signal.description} (confidence: {signal.confidence:.1%})")

        self._save_state()

    def _extract_signals_from_psychohistory(self, prescience_report: Dict[str, Any]) -> List[AnticipationSignal]:
        """Extract anticipation signals from psychohistory predictions"""
        signals = []

        for prediction_data in prescience_report.get("top_predictions", []):
            confidence = float(prediction_data["probability"].strip('%').strip()) / 100.0
            probability = float(prediction_data["probability"].strip('%').strip()) / 100.0

            # Create signal based on prediction content
            if "success" in prediction_data["prediction"].lower() and probability < 0.7:
                signal = AnticipationSignal(
                    signal_id=f"psychohistory_success_risk_{int(datetime.now().timestamp() * 1000)}",
                    trigger_type=AnticipationTrigger.FAILURE_PROBABILITY,
                    confidence=confidence,
                    urgency=7,
                    description=f"Psychohistory predicts low workflow success rate: {prediction_data['prediction']}",
                    predicted_impact={
                        "type": "workflow_failure",
                        "severity": "high" if probability < 0.5 else "medium",
                        "affected_workflows": "multiple"
                    },
                    recommended_actions=[
                        "Spawn additional workflow executor agents",
                        "Increase resource allocation",
                        "Prepare contingency workflows"
                    ],
                    time_to_impact=int(prediction_data["time_horizon"].strip('h')) * 60
                )
                signals.append(signal)

            elif "resource" in prediction_data["prediction"].lower() and probability < 0.6:
                signal = AnticipationSignal(
                    signal_id=f"psychohistory_resource_risk_{int(datetime.now().timestamp() * 1000)}",
                    trigger_type=AnticipationTrigger.RESOURCE_SHORTAGE,
                    confidence=confidence,
                    urgency=8,
                    description=f"Psychohistory predicts resource constraints: {prediction_data['prediction']}",
                    predicted_impact={
                        "type": "resource_shortage",
                        "severity": "high",
                        "affected_systems": "resource_management"
                    },
                    recommended_actions=[
                        "Spawn resource manager agents",
                        "Optimize current resource usage",
                        "Prepare resource scaling procedures"
                    ],
                    time_to_impact=int(prediction_data["time_horizon"].strip('h')) * 60
                )
                signals.append(signal)

        return signals

    def _extract_signals_from_dune_interface(self, dashboard: Dict[str, Any]) -> List[AnticipationSignal]:
        """Extract anticipation signals from Dune AI interface"""
        signals = []

        # Check risk levels
        risk_level = dashboard.get("summary", {}).get("overall_risk_level", "low")
        if risk_level in ["high", "medium"]:
            signal = AnticipationSignal(
                signal_id=f"dune_risk_signal_{int(datetime.now().timestamp())}",
                trigger_type=AnticipationTrigger.FAILURE_PROBABILITY,
                confidence=0.8 if risk_level == "high" else 0.6,
                urgency=9 if risk_level == "high" else 6,
                description=f"Dune AI interface detects {risk_level} system risk level",
                predicted_impact={
                    "type": "system_risk",
                    "severity": risk_level,
                    "affected_components": "multiple"
                },
                recommended_actions=[
                    "Spawn monitoring agents for risk areas",
                    "Implement preventive measures",
                    "Prepare emergency response protocols"
                ],
                time_to_impact=60  # 1 hour
            )
            signals.append(signal)

        # Check immediate action requirements
        immediate_actions = dashboard.get("summary", {}).get("immediate_action_required", 0)
        if immediate_actions > 0:
            signal = AnticipationSignal(
                signal_id=f"dune_immediate_action_{int(datetime.now().timestamp())}",
                trigger_type=AnticipationTrigger.WORKLOAD_SPIKE,
                confidence=0.9,
                urgency=10,
                description=f"Dune AI interface requires {immediate_actions} immediate actions",
                predicted_impact={
                    "type": "urgent_workload",
                    "severity": "critical",
                    "time_sensitivity": "immediate"
                },
                recommended_actions=[
                    "Spawn coordination agents immediately",
                    "Prioritize urgent tasks",
                    "Reallocate resources to critical areas"
                ],
                time_to_impact=15  # 15 minutes
            )
            signals.append(signal)

        return signals

    def _extract_signals_from_orchestrator(self, orchestrator_data: Dict[str, Any]) -> List[AnticipationSignal]:
        """Extract anticipation signals from workflow orchestrator"""
        signals = []

        # Check balance
        current_balance = orchestrator_data.get("current_balance", 0.0)
        if current_balance < -5.0:  # Significant negative balance
            signal = AnticipationSignal(
                signal_id=f"orchestrator_balance_risk_{int(datetime.now().timestamp())}",
                trigger_type=AnticipationTrigger.RESOURCE_SHORTAGE,
                confidence=0.85,
                urgency=8,
                description=f"Workflow orchestrator shows critical balance: ${current_balance:.2f}",
                predicted_impact={
                    "type": "financial_risk",
                    "severity": "high",
                    "monetary_impact": abs(current_balance)
                },
                recommended_actions=[
                    "Spawn resource optimization agents",
                    "Review and cancel low-ROI workflows",
                    "Implement cost control measures"
                ],
                time_to_impact=30  # 30 minutes
            )
            signals.append(signal)

        # Check pending vs running sessions
        pending_sessions = orchestrator_data.get("pending_sessions", 0)
        running_sessions = orchestrator_data.get("running_sessions", 0)

        if pending_sessions > running_sessions * 2:  # Too many pending
            signal = AnticipationSignal(
                signal_id=f"orchestrator_backlog_{int(datetime.now().timestamp())}",
                trigger_type=AnticipationTrigger.WORKLOAD_SPIKE,
                confidence=0.75,
                urgency=7,
                description=f"Workflow backlog detected: {pending_sessions} pending vs {running_sessions} running",
                predicted_impact={
                    "type": "processing_backlog",
                    "severity": "medium",
                    "delayed_workflows": pending_sessions
                },
                recommended_actions=[
                    "Spawn additional workflow executor agents",
                    "Optimize current agent utilization",
                    "Prioritize high-value pending workflows"
                ],
                time_to_impact=45  # 45 minutes
            )
            signals.append(signal)

        return signals

    def _apply_anticipation_models(self) -> List[AnticipationSignal]:
        """Apply anticipation models to generate signals"""
        signals = []

        # This would use the psychohistory mathematics to evaluate conditions
        # For now, using simplified logic

        for model in self.anticipation_models.values():
            # Evaluate model conditions (simplified)
            condition_met = self._evaluate_model_conditions(model)

            if condition_met and model.confidence_threshold > 0.5:  # Model is active
                signal = AnticipationSignal(
                    signal_id=f"model_trigger_{model.model_id}_{int(datetime.now().timestamp())}",
                    trigger_type=model.trigger_type,
                    confidence=model.confidence_threshold,
                    urgency=6,
                    description=f"Anticipation model '{model.model_id}' triggered based on {model.trigger_type.value}",
                    predicted_impact={
                        "type": model.trigger_type.value,
                        "severity": "medium",
                        "model_based": True
                    },
                    recommended_actions=self._get_model_recommended_actions(model),
                    time_to_impact=60  # 1 hour default
                )
                signals.append(signal)

        return signals

    def _evaluate_model_conditions(self, model: AnticipationModel) -> bool:
        """Evaluate if model conditions are met (simplified)"""
        # This would use actual variable values from psychohistory
        # For now, using random evaluation based on model confidence

        import random
        return random.random() < model.historical_accuracy if model.historical_accuracy > 0 else random.random() < 0.3

    def _get_model_recommended_actions(self, model: AnticipationModel) -> List[str]:
        """Get recommended actions for a triggered model"""
        actions_map = {
            AnticipationTrigger.WORKLOAD_SPIKE: [
                "Spawn workflow executor agents",
                "Scale up processing capacity",
                "Optimize task distribution"
            ],
            AnticipationTrigger.RESOURCE_SHORTAGE: [
                "Spawn resource manager agents",
                "Implement resource optimization",
                "Monitor resource usage closely"
            ],
            AnticipationTrigger.FAILURE_PROBABILITY: [
                "Spawn quality assurance agents",
                "Implement additional verification steps",
                "Prepare failure recovery procedures"
            ],
            AnticipationTrigger.TEMPORAL_CYCLE: [
                "Spawn agents for predicted busy period",
                "Pre-allocate resources for peak time",
                "Prepare workload distribution plan"
            ]
        }

        return actions_map.get(model.trigger_type, ["Monitor situation closely", "Prepare contingency plans"])

    def _process_anticipation_signals(self):
        """Process active anticipation signals and spawn agents as needed"""
        # Filter high-priority signals
        high_priority_signals = [
            signal for signal in self.anticipation_signals.values()
            if signal.confidence > 0.7 and signal.urgency >= 7 and signal.time_to_impact <= 60
        ]

        # Sort by urgency and confidence
        high_priority_signals.sort(key=lambda s: (s.urgency, s.confidence), reverse=True)

        # Check resource limits
        current_agent_count = len([a for a in self.spawned_agents.values() if a.status == "active"])
        if current_agent_count >= self.max_concurrent_agents:
            self.logger.warning(f"⚠️ At maximum concurrent agents ({self.max_concurrent_agents}), cannot spawn more")
            return

        # Process signals
        agents_spawned = 0
        for signal in high_priority_signals[:3]:  # Process top 3 signals
            if self._should_spawn_agent_for_signal(signal):
                agent_type = self._determine_agent_type_for_signal(signal)
                if agent_type:
                    agent_id = self._spawn_subagent(signal, agent_type)
                    if agent_id:
                        agents_spawned += 1
                        self.logger.info(f"🤖 Anticipatory spawn: {agent_type.value} agent for signal {signal.signal_id}")

        if agents_spawned > 0:
            self.logger.info(f"✅ Spawned {agents_spawned} anticipatory agents")

    def _should_spawn_agent_for_signal(self, signal: AnticipationSignal) -> bool:
        """Determine if we should spawn an agent for this signal"""
        # Check if we already have agents for this signal
        existing_agents = [a for a in self.spawned_agents.values()
                          if a.trigger_signal == signal.signal_id and a.status == "active"]

        if existing_agents:
            self.logger.debug(f"Agent already exists for signal {signal.signal_id}")
            return False

        # Check resource availability (simplified)
        # In practice, would check actual system resources

        # Check if signal is still relevant (not too old)
        signal_age = (datetime.now() - signal.detected_at).total_seconds() / 60  # minutes
        if signal_age > signal.time_to_impact:
            self.logger.debug(f"Signal {signal.signal_id} is too old ({signal_age:.0f} minutes)")
            return False

        return True

    def _determine_agent_type_for_signal(self, signal: AnticipationSignal) -> Optional[SubagentType]:
        """Determine what type of agent to spawn for this signal"""
        type_map = {
            AnticipationTrigger.WORKLOAD_SPIKE: SubagentType.WORKFLOW_EXECUTOR,
            AnticipationTrigger.RESOURCE_SHORTAGE: SubagentType.RESOURCE_MANAGER,
            AnticipationTrigger.FAILURE_PROBABILITY: SubagentType.QUALITY_ASSURANCE,
            AnticipationTrigger.COMPLEXITY_INCREASE: SubagentType.OPTIMIZATION_AGENT,
            AnticipationTrigger.PATTERN_RECOGNITION: SubagentType.MONITORING_AGENT,
            AnticipationTrigger.TEMPORAL_CYCLE: SubagentType.COORDINATION_AGENT,
            AnticipationTrigger.CORRELATION_TRIGGER: SubagentType.PREDICTION_AGENT
        }

        return type_map.get(signal.trigger_type)

    def _spawn_subagent(self, signal: AnticipationSignal, agent_type: SubagentType) -> Optional[str]:
        """Spawn a new subagent"""
        agent_id = f"agent_{agent_type.value}_{int(datetime.now().timestamp())}"

        # Determine expected lifetime based on signal
        lifetime_map = {
            SubagentType.WORKFLOW_EXECUTOR: 120,  # 2 hours
            SubagentType.RESOURCE_MANAGER: 90,    # 1.5 hours
            SubagentType.QUALITY_ASSURANCE: 180,  # 3 hours
            SubagentType.MONITORING_AGENT: 60,    # 1 hour
            SubagentType.OPTIMIZATION_AGENT: 150, # 2.5 hours
            SubagentType.RECOVERY_AGENT: 240,     # 4 hours
            SubagentType.COORDINATION_AGENT: 180, # 3 hours
            SubagentType.PREDICTION_AGENT: 120    # 2 hours
        }

        expected_lifetime = lifetime_map.get(agent_type, 60)

        # Allocate resources (simplified)
        resource_allocation = self._allocate_resources_for_agent(agent_type)

        agent = SpawnedSubagent(
            agent_id=agent_id,
            agent_type=agent_type,
            trigger_signal=signal.signal_id,
            spawned_at=datetime.now(),
            expected_lifetime=expected_lifetime,
            resources_allocated=resource_allocation,
            assigned_tasks=signal.recommended_actions.copy()
        )

        self.spawned_agents[agent_id] = agent

        # Log to master session if available
        if self.master_session_manager:
            try:
                self.master_session_manager.add_to_master_session(
                    agent="DynamicSpawner",
                    message=f"Anticipatory spawn: {agent_type.value} agent ({agent_id}) for signal: {signal.description}",
                    context={
                        "agent_id": agent_id,
                        "signal_id": signal.signal_id,
                        "trigger_type": signal.trigger_type.value,
                        "confidence": signal.confidence
                    }
                )
            except Exception as e:
                self.logger.debug(f"Could not log to master session: {e}")

        self._save_state()

        return agent_id

    def _allocate_resources_for_agent(self, agent_type: SubagentType) -> Dict[str, float]:
        """Allocate resources for the new agent (simplified)"""
        base_allocation = {
            SubagentType.WORKFLOW_EXECUTOR: {"cpu": 10.0, "memory": 5.0, "api_calls": 50.0},
            SubagentType.RESOURCE_MANAGER: {"cpu": 5.0, "memory": 3.0, "api_calls": 25.0},
            SubagentType.QUALITY_ASSURANCE: {"cpu": 8.0, "memory": 4.0, "api_calls": 40.0},
            SubagentType.MONITORING_AGENT: {"cpu": 3.0, "memory": 2.0, "api_calls": 15.0},
            SubagentType.OPTIMIZATION_AGENT: {"cpu": 12.0, "memory": 6.0, "api_calls": 60.0},
            SubagentType.RECOVERY_AGENT: {"cpu": 15.0, "memory": 8.0, "api_calls": 75.0},
            SubagentType.COORDINATION_AGENT: {"cpu": 7.0, "memory": 4.0, "api_calls": 35.0},
            SubagentType.PREDICTION_AGENT: {"cpu": 6.0, "memory": 3.0, "api_calls": 30.0}
        }

        return base_allocation.get(agent_type, {"cpu": 5.0, "memory": 2.0, "api_calls": 20.0})

    def _cleanup_expired_agents(self):
        """Clean up agents that have exceeded their expected lifetime"""
        current_time = datetime.now()
        expired_agents = []

        for agent_id, agent in self.spawned_agents.items():
            if agent.status == "active":
                lifetime_minutes = (current_time - agent.spawned_at).total_seconds() / 60
                if lifetime_minutes > agent.expected_lifetime:
                    agent.status = "terminated"
                    agent.termination_reason = "lifetime_expired"
                    expired_agents.append(agent_id)
                    self.logger.info(f"🧹 Terminated expired agent: {agent_id} (lifetime: {lifetime_minutes:.0f} minutes)")

        if expired_agents:
            self._save_state()

    def _update_agent_performance(self):
        """Update performance metrics for active agents"""
        # This would collect actual performance data
        # For now, using simulated updates

        for agent in self.spawned_agents.values():
            if agent.status == "active":
                # Simulate performance updates
                agent.performance_metrics["tasks_completed"] = agent.performance_metrics.get("tasks_completed", 0) + 1
                agent.performance_metrics["last_update"] = datetime.now().isoformat()

        self._save_state()

    def get_spawner_status(self) -> Dict[str, Any]:
        """Get dynamic spawner status"""
        active_agents = [a for a in self.spawned_agents.values() if a.status == "active"]
        active_signals = list(self.anticipation_signals.values())

        return {
            "active_agents": len(active_agents),
            "active_signals": len(active_signals),
            "anticipation_models": len(self.anticipation_models),
            "agents_by_type": self._count_agents_by_type(active_agents),
            "signals_by_trigger": self._count_signals_by_trigger(active_signals),
            "resource_utilization": self._calculate_resource_utilization(),
            "spawn_success_rate": self._calculate_spawn_success_rate(),
            "last_scan": datetime.now().isoformat()
        }

    def _count_agents_by_type(self, agents: List[SpawnedSubagent]) -> Dict[str, int]:
        """Count agents by type"""
        counts = {}
        for agent in agents:
            agent_type = agent.agent_type.value
            counts[agent_type] = counts.get(agent_type, 0) + 1
        return counts

    def _count_signals_by_trigger(self, signals: List[AnticipationSignal]) -> Dict[str, int]:
        """Count signals by trigger type"""
        counts = {}
        for signal in signals:
            trigger_type = signal.trigger_type.value
            counts[trigger_type] = counts.get(trigger_type, 0) + 1
        return counts

    def _calculate_resource_utilization(self) -> Dict[str, float]:
        """Calculate current resource utilization"""
        active_agents = [a for a in self.spawned_agents.values() if a.status == "active"]

        total_resources = {"cpu": 0.0, "memory": 0.0, "api_calls": 0.0}

        for agent in active_agents:
            for resource, amount in agent.resources_allocated.items():
                total_resources[resource] += amount

        # Calculate percentages
        utilization = {}
        for resource, used in total_resources.items():
            limit = self.resource_limits.get(resource, 100.0)
            utilization[resource] = min((used / limit) * 100, 100.0)

        return utilization

    def _calculate_spawn_success_rate(self) -> float:
        """Calculate spawn success rate"""
        total_models = len(self.anticipation_models)
        if total_models == 0:
            return 0.0

        successful_spawns = sum(model.successful_spawns for model in self.anticipation_models.values())
        total_triggers = sum(model.times_triggered for model in self.anticipation_models.values())

        return successful_spawns / total_triggers if total_triggers > 0 else 0.0

    def force_spawn_agent(self, agent_type: SubagentType, reason: str = "manual") -> Optional[str]:
        """
        Manually force spawn an agent (for testing or emergency situations)

        This bypasses the normal anticipation logic for immediate needs.
        """
        # Create a synthetic signal
        signal = AnticipationSignal(
            signal_id=f"forced_spawn_{int(datetime.now().timestamp())}",
            trigger_type=AnticipationTrigger.WORKLOAD_SPIKE,
            confidence=1.0,
            urgency=10,
            description=f"Forced spawn: {reason}",
            predicted_impact={"type": "manual_spawn", "severity": "high"},
            recommended_actions=[f"Execute {agent_type.value} tasks"],
            time_to_impact=5  # 5 minutes
        )

        agent_id = self._spawn_subagent(signal, agent_type)
        if agent_id:
            self.logger.info(f"🔧 Force spawned {agent_type.value} agent: {agent_id} (reason: {reason})")

        return agent_id


def main():
    """Main execution"""
    spawner = DynamicSubagentSpawner()

    print("🚀 Dynamic Subagent Spawner - Anticipatory Agent Creation")
    print("=" * 80)
    print("")

    # Get status
    status = spawner.get_spawner_status()
    print("📊 Spawner Status:")
    print(f"   Active Agents: {status['active_agents']}")
    print(f"   Active Signals: {status['active_signals']}")
    print(f"   Anticipation Models: {status['anticipation_models']}")
    print("")

    print("🤖 Agents by Type:")
    for agent_type, count in status['agents_by_type'].items():
        print(f"   {agent_type}: {count}")
    print("")

    print("🚨 Signals by Trigger:")
    for trigger_type, count in status['signals_by_trigger'].items():
        print(f"   {trigger_type}: {count}")
    print("")

    print("💾 Resource Utilization:")
    for resource, utilization in status['resource_utilization'].items():
        print(f"   {resource}: {utilization:.1f}%")
    print("")

    # Force spawn a test agent
    test_agent_id = spawner.force_spawn_agent(
        SubagentType.WORKFLOW_EXECUTOR,
        "Testing anticipatory spawning system"
    )

    if test_agent_id:
        print(f"✅ Force spawned test agent: {test_agent_id}")

    # Wait a bit for monitoring
    print("")
    print("⏳ Monitoring for anticipation signals...")
    time.sleep(5)

    # Get updated status
    updated_status = spawner.get_spawner_status()
    print(f"📈 Updated active agents: {updated_status['active_agents']}")

    print("")
    print("🔮 Anticipatory spawning active: Agents created before they're needed.")


if __name__ == "__main__":


    main()