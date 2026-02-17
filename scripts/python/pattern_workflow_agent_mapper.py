#!/usr/bin/env python3
"""
Pattern → Workflow → Agent Mapper

When patterns are discovered/updated:
1. Create key-value pairs matching patterns
2. Map patterns to workflows
3. Each workflow gets its own AI agent
4. All agents in same sub-agent chat session
5. Hook and trace track everything
6. Analytics, metrics, performance tracking
7. Improve flow rate per second
"""

import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from sub_ask_todo_manager import SubAskTodoManager, SubAgentChatSession, SubAgentChatStatus
    SUB_ASK_AVAILABLE = True
except ImportError:
    SUB_ASK_AVAILABLE = False
    SubAskTodoManager = None


class PatternType(Enum):
    """Pattern type"""
    NEW = "new"  # Newly discovered pattern
    UPDATED = "updated"  # Existing pattern updated
    IMPROVED = "improved"  # Pattern improved upon


class AgentStatus(Enum):
    """Agent status"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    TRACKING = "tracking"  # Being tracked for analytics


@dataclass
class PatternKeyValue:
    """Key-value pair matching a pattern"""
    key: str
    value: Any
    pattern_id: str
    confidence: float  # 0.0 to 1.0
    created_at: str = ""
    updated_at: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PatternWorkflowMapping:
    """Mapping from pattern to workflow"""
    pattern_id: str
    workflow_id: str
    workflow_name: str
    confidence: float  # 0.0 to 1.0
    created_at: str = ""
    updated_at: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WorkflowAgent:
    """AI agent for a workflow"""
    agent_id: str
    workflow_id: str
    workflow_name: str
    agent_name: str
    status: AgentStatus
    chat_session_id: Optional[str] = None
    created_at: str = ""
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    flow_rate_per_second: float = 0.0
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass
class FlowTrace:
    """Trace entry for flow tracking"""
    trace_id: str
    timestamp: str
    pattern_id: Optional[str] = None
    workflow_id: Optional[str] = None
    agent_id: Optional[str] = None
    event_type: str = ""  # pattern_discovered, workflow_matched, agent_created, agent_started, agent_completed, etc.
    flow_rate: float = 0.0  # Flow rate at this point
    performance_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PerformanceMetrics:
    """Performance metrics for analytics"""
    pattern_id: Optional[str] = None
    workflow_id: Optional[str] = None
    agent_id: Optional[str] = None
    flow_rate_per_second: float = 0.0
    total_flow_time: float = 0.0
    agent_count: int = 0
    workflow_count: int = 0
    pattern_count: int = 0
    success_rate: float = 0.0
    average_flow_rate: float = 0.0
    peak_flow_rate: float = 0.0
    timestamp: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PatternWorkflowAgentMapper:
    """
    Maps patterns to workflows to agents with full tracking and analytics
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("PatternWorkflowAgentMapper")

        # Directories
        self.data_dir = self.project_root / "data" / "pattern_workflow_agent"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.patterns_dir = self.data_dir / "patterns"
        self.patterns_dir.mkdir(parents=True, exist_ok=True)

        self.workflows_dir = self.data_dir / "workflows"
        self.workflows_dir.mkdir(parents=True, exist_ok=True)

        self.agents_dir = self.data_dir / "agents"
        self.agents_dir.mkdir(parents=True, exist_ok=True)

        self.traces_dir = self.data_dir / "traces"
        self.traces_dir.mkdir(parents=True, exist_ok=True)

        self.analytics_dir = self.data_dir / "analytics"
        self.analytics_dir.mkdir(parents=True, exist_ok=True)

        # Files
        self.patterns_file = self.data_dir / "patterns.json"
        self.key_values_file = self.data_dir / "pattern_key_values.json"
        self.workflow_mappings_file = self.data_dir / "workflow_mappings.json"
        self.agents_file = self.data_dir / "agents.json"
        self.traces_file = self.data_dir / "traces.jsonl"
        self.performance_file = self.data_dir / "performance_metrics.json"

        # Sub-Ask Manager for chat sessions
        self.sub_ask_manager = None
        if SUB_ASK_AVAILABLE and SubAskTodoManager:
            try:
                self.sub_ask_manager = SubAskTodoManager(project_root=self.project_root)
                self.logger.info("✅ Sub-Ask Manager initialized")
            except Exception as e:
                self.logger.warning(f"Sub-Ask Manager not available: {e}")

        # State
        self.patterns: Dict[str, Dict[str, Any]] = {}  # pattern_id -> pattern data
        self.pattern_key_values: Dict[str, List[PatternKeyValue]] = defaultdict(list)  # pattern_id -> key-values
        self.workflow_mappings: Dict[str, List[PatternWorkflowMapping]] = defaultdict(list)  # pattern_id -> workflows
        self.workflow_agents: Dict[str, List[WorkflowAgent]] = defaultdict(list)  # workflow_id -> agents
        self.flow_traces: List[FlowTrace] = []
        self.performance_metrics: List[PerformanceMetrics] = []

        # Flow rate tracking
        self.flow_rate_history: List[Tuple[float, float]] = []  # (timestamp, flow_rate)
        self.current_flow_rate: float = 0.0

        # Load state
        self._load_state()

    def _load_state(self):
        """Load state from files"""
        # Load patterns
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    self.patterns = json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading patterns: {e}")

        # Load key-values
        if self.key_values_file.exists():
            try:
                with open(self.key_values_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for pattern_id, kv_list in data.items():
                        self.pattern_key_values[pattern_id] = [
                            PatternKeyValue(**kv) for kv in kv_list
                        ]
            except Exception as e:
                self.logger.error(f"Error loading key-values: {e}")

        # Load workflow mappings
        if self.workflow_mappings_file.exists():
            try:
                with open(self.workflow_mappings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for pattern_id, mapping_list in data.items():
                        self.workflow_mappings[pattern_id] = [
                            PatternWorkflowMapping(**m) for m in mapping_list
                        ]
            except Exception as e:
                self.logger.error(f"Error loading workflow mappings: {e}")

        # Load agents
        if self.agents_file.exists():
            try:
                with open(self.agents_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for workflow_id, agent_list in data.items():
                        self.workflow_agents[workflow_id] = [
                            WorkflowAgent(**a) for a in agent_list
                        ]
            except Exception as e:
                self.logger.error(f"Error loading agents: {e}")

        # Load traces
        if self.traces_file.exists():
            try:
                with open(self.traces_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            trace_data = json.loads(line)
                            self.flow_traces.append(FlowTrace(**trace_data))
            except Exception as e:
                self.logger.error(f"Error loading traces: {e}")

    def _save_state(self):
        try:
            """Save state to files"""
            # Save patterns
            with open(self.patterns_file, 'w', encoding='utf-8') as f:
                json.dump(self.patterns, f, indent=2, ensure_ascii=False)

            # Save key-values
            key_values_data = {
                pattern_id: [kv.to_dict() for kv in kv_list]
                for pattern_id, kv_list in self.pattern_key_values.items()
            }
            with open(self.key_values_file, 'w', encoding='utf-8') as f:
                json.dump(key_values_data, f, indent=2, ensure_ascii=False)

            # Save workflow mappings
            mappings_data = {
                pattern_id: [m.to_dict() for m in mapping_list]
                for pattern_id, mapping_list in self.workflow_mappings.items()
            }
            with open(self.workflow_mappings_file, 'w', encoding='utf-8') as f:
                json.dump(mappings_data, f, indent=2, ensure_ascii=False)

            # Save agents
            agents_data = {
                workflow_id: [a.to_dict() for a in agent_list]
                for workflow_id, agent_list in self.workflow_agents.items()
            }
            with open(self.agents_file, 'w', encoding='utf-8') as f:
                json.dump(agents_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _save_state: {e}", exc_info=True)
            raise
    def _trace_event(
        self,
        event_type: str,
        pattern_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        performance_data: Optional[Dict[str, Any]] = None
    ):
        """Trace an event for flow tracking"""
        trace = FlowTrace(
            trace_id=f"trace_{int(datetime.now().timestamp() * 1000)}",
            timestamp=datetime.now().isoformat(),
            pattern_id=pattern_id,
            workflow_id=workflow_id,
            agent_id=agent_id,
            event_type=event_type,
            flow_rate=self.current_flow_rate,
            performance_data=performance_data or {},
            metadata={"flow_tracking": True}
        )

        self.flow_traces.append(trace)

        # Save to file (append)
        with open(self.traces_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(trace.to_dict()) + '\n')

        # Update flow rate
        self._update_flow_rate()

    def _update_flow_rate(self):
        """Update current flow rate per second"""
        # Calculate flow rate based on recent traces
        now = time.time()
        recent_traces = [
            t for t in self.flow_traces
            if (now - datetime.fromisoformat(t.timestamp).timestamp()) < 60  # Last 60 seconds
        ]

        if recent_traces:
            self.current_flow_rate = len(recent_traces) / 60.0  # Traces per second
        else:
            self.current_flow_rate = 0.0

        # Store in history
        self.flow_rate_history.append((now, self.current_flow_rate))

        # Keep only last 1000 entries
        if len(self.flow_rate_history) > 1000:
            self.flow_rate_history = self.flow_rate_history[-1000:]

    def discover_or_update_pattern(
        self,
        pattern_id: str,
        pattern_data: Dict[str, Any],
        pattern_type: PatternType = PatternType.NEW
    ) -> str:
        """
        Discover new pattern or update existing pattern

        Returns pattern_id
        """
        now = datetime.now().isoformat()

        if pattern_type == PatternType.NEW:
            self.patterns[pattern_id] = {
                **pattern_data,
                "pattern_id": pattern_id,
                "created_at": now,
                "updated_at": now,
                "pattern_type": pattern_type.value
            }
            self.logger.info(f"🔍 Discovered new pattern: {pattern_id}")
        else:
            if pattern_id in self.patterns:
                self.patterns[pattern_id].update({
                    **pattern_data,
                    "updated_at": now,
                    "pattern_type": pattern_type.value
                })
                self.logger.info(f"🔄 Updated pattern: {pattern_id} ({pattern_type.value})")
            else:
                self.logger.warning(f"Pattern not found for update: {pattern_id}, creating as new")
                self.patterns[pattern_id] = {
                    **pattern_data,
                    "pattern_id": pattern_id,
                    "created_at": now,
                    "updated_at": now,
                    "pattern_type": PatternType.NEW.value
                }

        # Trace event
        self._trace_event(
            "pattern_discovered" if pattern_type == PatternType.NEW else "pattern_updated",
            pattern_id=pattern_id
        )

        self._save_state()

        return pattern_id

    def add_pattern_key_value(
        self,
        pattern_id: str,
        key: str,
        value: Any,
        confidence: float = 1.0
    ) -> PatternKeyValue:
        """
        Add key-value pair matching a pattern

        Each pattern must have key-value pairs that match it
        """
        now = datetime.now().isoformat()

        kv = PatternKeyValue(
            key=key,
            value=value,
            pattern_id=pattern_id,
            confidence=confidence,
            created_at=now,
            updated_at=now
        )

        self.pattern_key_values[pattern_id].append(kv)

        self.logger.info(f"🔑 Added key-value to pattern {pattern_id}: {key}={value}")

        # Trace event
        self._trace_event("pattern_key_value_added", pattern_id=pattern_id)

        self._save_state()

        return kv

    def map_pattern_to_workflow(
        self,
        pattern_id: str,
        workflow_id: str,
        workflow_name: str,
        confidence: float = 1.0
    ) -> PatternWorkflowMapping:
        """
        Map pattern to workflow

        Patterns can match one or more workflows
        """
        now = datetime.now().isoformat()

        mapping = PatternWorkflowMapping(
            pattern_id=pattern_id,
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            confidence=confidence,
            created_at=now,
            updated_at=now
        )

        self.workflow_mappings[pattern_id].append(mapping)

        self.logger.info(f"🗺️ Mapped pattern {pattern_id} to workflow {workflow_id} ({workflow_name})")

        # Trace event
        self._trace_event("pattern_workflow_mapped", pattern_id=pattern_id, workflow_id=workflow_id)

        self._save_state()

        return mapping

    def create_agent_for_workflow(
        self,
        workflow_id: str,
        workflow_name: str,
        agent_name: Optional[str] = None,
        chat_session_id: Optional[str] = None
    ) -> WorkflowAgent:
        """
        Create AI agent for a workflow

        Each workflow gets its own AI agent
        All agents can be in the same sub-agent chat session
        """
        now = datetime.now().isoformat()
        agent_id = f"agent_{int(datetime.now().timestamp() * 1000)}"
        agent_name = agent_name or f"Agent-{workflow_name}"

        # If no chat session provided, create or use existing
        if not chat_session_id and self.sub_ask_manager:
            # Try to find existing chat session for this workflow
            existing_chats = [
                chat for chat in self.sub_ask_manager.chat_sessions.values()
                if chat.workflow_completed == False and chat.chat_status == SubAgentChatStatus.ACTIVE
            ]

            if existing_chats:
                # Use existing active chat session
                chat_session_id = existing_chats[0].session_id
                self.logger.info(f"📱 Using existing chat session: {chat_session_id}")
            else:
                # Create new chat session via sub-ask manager
                try:
                    sub_ask = self.sub_ask_manager.create_sub_ask(
                        parent_ask_id=f"pattern_workflow_{workflow_id}",
                        sub_ask_text=f"Execute workflow: {workflow_name}",
                        agent_name=agent_name,
                        workflow_id=workflow_id
                    )
                    chat_session_id = sub_ask.chat_session.session_id
                    self.logger.info(f"📱 Created new chat session: {chat_session_id}")
                except Exception as e:
                    self.logger.warning(f"Could not create chat session: {e}")

        agent = WorkflowAgent(
            agent_id=agent_id,
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            agent_name=agent_name,
            status=AgentStatus.PENDING,
            chat_session_id=chat_session_id,
            created_at=now,
            flow_rate_per_second=self.current_flow_rate
        )

        self.workflow_agents[workflow_id].append(agent)

        self.logger.info(f"🤖 Created agent {agent_id} for workflow {workflow_id} ({workflow_name})")

        # Trace event
        self._trace_event("agent_created", workflow_id=workflow_id, agent_id=agent_id)

        self._save_state()

        return agent

    def start_agent(self, agent_id: str) -> bool:
        """Start an agent (begin tracking)"""
        agent = self._find_agent(agent_id)
        if not agent:
            return False

        agent.status = AgentStatus.ACTIVE
        agent.started_at = datetime.now().isoformat()
        agent.flow_rate_per_second = self.current_flow_rate

        # Trace event
        self._trace_event("agent_started", workflow_id=agent.workflow_id, agent_id=agent_id)

        self._save_state()

        return True

    def complete_agent(self, agent_id: str, success: bool = True) -> bool:
        """Complete an agent (end tracking)"""
        agent = self._find_agent(agent_id)
        if not agent:
            return False

        agent.status = AgentStatus.COMPLETED if success else AgentStatus.FAILED
        agent.completed_at = datetime.now().isoformat()

        # Calculate final flow rate
        if agent.started_at:
            start_time = datetime.fromisoformat(agent.started_at)
            end_time = datetime.fromisoformat(agent.completed_at)
            duration = (end_time - start_time).total_seconds()
            if duration > 0:
                agent.flow_rate_per_second = 1.0 / duration  # Workflows per second

        # Trace event
        self._trace_event(
            "agent_completed" if success else "agent_failed",
            workflow_id=agent.workflow_id,
            agent_id=agent_id,
            performance_data={"flow_rate": agent.flow_rate_per_second, "success": success}
        )

        # Update performance metrics
        self._update_performance_metrics(agent)

        self._save_state()

        return True

    def _find_agent(self, agent_id: str) -> Optional[WorkflowAgent]:
        """Find agent by ID"""
        for agents in self.workflow_agents.values():
            for agent in agents:
                if agent.agent_id == agent_id:
                    return agent
        return None

    def _update_performance_metrics(self, agent: WorkflowAgent):
        try:
            """Update performance metrics for analytics"""
            metrics = PerformanceMetrics(
                workflow_id=agent.workflow_id,
                agent_id=agent.agent_id,
                flow_rate_per_second=agent.flow_rate_per_second,
                agent_count=1,
                workflow_count=1,
                success_rate=1.0 if agent.status == AgentStatus.COMPLETED else 0.0,
                average_flow_rate=agent.flow_rate_per_second,
                peak_flow_rate=agent.flow_rate_per_second,
                timestamp=datetime.now().isoformat()
            )

            self.performance_metrics.append(metrics)

            # Save to file
            metrics_file = self.analytics_dir / f"metrics_{datetime.now().strftime('%Y%m%d')}.json"
            metrics_data = [m.to_dict() for m in self.performance_metrics[-100:]]  # Last 100
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(metrics_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _update_performance_metrics: {e}", exc_info=True)
            raise
    def process_pattern_to_agents(
        self,
        pattern_id: str,
        pattern_data: Dict[str, Any],
        pattern_type: PatternType = PatternType.NEW,
        key_values: Optional[List[Tuple[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Complete flow: Pattern → Key-Values → Workflows → Agents

        Returns mapping of pattern to agents
        """
        self.logger.info(f"🔄 Processing pattern to agents: {pattern_id}")

        # 1. Discover/update pattern
        self.discover_or_update_pattern(pattern_id, pattern_data, pattern_type)

        # 2. Add key-values
        if key_values:
            for key, value in key_values:
                self.add_pattern_key_value(pattern_id, key, value)

        # 3. Map to workflows (get workflows that match this pattern)
        workflows = self._get_workflows_for_pattern(pattern_id)

        # 4. Create agents for each workflow (all in same chat session)
        agents = []
        chat_session_id = None

        for workflow in workflows:
            agent = self.create_agent_for_workflow(
                workflow_id=workflow.workflow_id,
                workflow_name=workflow.workflow_name,
                chat_session_id=chat_session_id  # Reuse same chat session
            )
            agents.append(agent)

            # Use same chat session for all agents
            if not chat_session_id and agent.chat_session_id:
                chat_session_id = agent.chat_session_id

        # Trace event
        self._trace_event(
            "pattern_to_agents_complete",
            pattern_id=pattern_id,
            performance_data={
                "workflow_count": len(workflows),
                "agent_count": len(agents),
                "flow_rate": self.current_flow_rate
            }
        )

        return {
            "pattern_id": pattern_id,
            "workflows": [w.to_dict() for w in workflows],
            "agents": [a.to_dict() for a in agents],
            "chat_session_id": chat_session_id,
            "flow_rate": self.current_flow_rate
        }

    def _get_workflows_for_pattern(self, pattern_id: str) -> List[PatternWorkflowMapping]:
        """Get workflows that match a pattern"""
        return self.workflow_mappings.get(pattern_id, [])

    def get_flow_rate_per_second(self) -> float:
        """Get current flow rate per second"""
        return self.current_flow_rate

    def get_performance_analytics(
        self,
        pattern_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        time_range_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get performance analytics

        Returns metrics for flow rate, performance, etc.
        """
        cutoff_time = datetime.now() - timedelta(hours=time_range_hours)

        # Filter traces
        relevant_traces = [
            t for t in self.flow_traces
            if datetime.fromisoformat(t.timestamp) >= cutoff_time
            and (not pattern_id or t.pattern_id == pattern_id)
            and (not workflow_id or t.workflow_id == workflow_id)
        ]

        # Filter agents
        relevant_agents = []
        for agents in self.workflow_agents.values():
            for agent in agents:
                if (not workflow_id or agent.workflow_id == workflow_id):
                    if agent.started_at and datetime.fromisoformat(agent.started_at) >= cutoff_time:
                        relevant_agents.append(agent)

        # Calculate metrics
        total_flow_time = sum(
            (datetime.fromisoformat(agent.completed_at) - datetime.fromisoformat(agent.started_at)).total_seconds()
            for agent in relevant_agents
            if agent.started_at and agent.completed_at
        )

        flow_rates = [agent.flow_rate_per_second for agent in relevant_agents if agent.flow_rate_per_second > 0]
        avg_flow_rate = sum(flow_rates) / len(flow_rates) if flow_rates else 0.0
        peak_flow_rate = max(flow_rates) if flow_rates else 0.0

        success_count = sum(1 for agent in relevant_agents if agent.status == AgentStatus.COMPLETED)
        success_rate = success_count / len(relevant_agents) if relevant_agents else 0.0

        return {
            "time_range_hours": time_range_hours,
            "pattern_id": pattern_id,
            "workflow_id": workflow_id,
            "total_traces": len(relevant_traces),
            "total_agents": len(relevant_agents),
            "successful_agents": success_count,
            "success_rate": success_rate,
            "total_flow_time": total_flow_time,
            "average_flow_rate_per_second": avg_flow_rate,
            "peak_flow_rate_per_second": peak_flow_rate,
            "current_flow_rate_per_second": self.current_flow_rate,
            "flow_rate_history": self.flow_rate_history[-100:]  # Last 100
        }


def main():
    """Main execution for testing"""
    mapper = PatternWorkflowAgentMapper()

    print("=" * 80)
    print("🔄 PATTERN → WORKFLOW → AGENT MAPPER")
    print("=" * 80)

    # Test: Discover pattern and create agents
    result = mapper.process_pattern_to_agents(
        pattern_id="pattern_test_123",
        pattern_data={"name": "Test Pattern", "description": "Test pattern for workflow mapping"},
        pattern_type=PatternType.NEW,
        key_values=[("test_key", "test_value"), ("confidence", 0.95)]
    )

    print(f"\n✅ Pattern processed:")
    print(f"   Pattern ID: {result['pattern_id']}")
    print(f"   Workflows: {len(result['workflows'])}")
    print(f"   Agents: {len(result['agents'])}")
    print(f"   Chat Session: {result.get('chat_session_id', 'N/A')}")
    print(f"   Flow Rate: {result['flow_rate']:.4f} per second")

    # Get analytics
    analytics = mapper.get_performance_analytics()
    print(f"\n📊 Performance Analytics:")
    print(f"   Current Flow Rate: {analytics['current_flow_rate_per_second']:.4f} per second")
    print(f"   Average Flow Rate: {analytics['average_flow_rate_per_second']:.4f} per second")
    print(f"   Peak Flow Rate: {analytics['peak_flow_rate_per_second']:.4f} per second")


if __name__ == "__main__":



    main()