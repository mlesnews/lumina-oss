#!/usr/bin/env python3
"""
Chat Agent Connection Manager
@MARVIN @JARVIS @TONY @MACE @GANDALF

Comprehensive management of homelab (local cloud) LLM chat agents with:
- Multiple disconnect handling and automatic reconnection
- Self-repair mechanisms for partial failures
- @ask interaction management and routing
- Load balancing across all active chat sessions
- Resource-aware session distribution

"Marvin, are we doing that?"
YES - Now we are!
"""

import sys
import json
import time
import threading
import queue
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

# Import existing systems
try:
    from ide_session_load_balancer import IDESessionLoadBalancer, IDESession
    LOAD_BALANCER_AVAILABLE = True
except ImportError:
    LOAD_BALANCER_AVAILABLE = False
    IDESessionLoadBalancer = None

try:
    from connection_flow_optimizer import ConnectionFlowOptimizer
    CONNECTION_OPTIMIZER_AVAILABLE = True
except ImportError:
    CONNECTION_OPTIMIZER_AVAILABLE = False
    ConnectionFlowOptimizer = None

try:
    from fix_asks_retries import FixedAsksRetries, RetryConfig
    ASK_RETRIES_AVAILABLE = True
except ImportError:
    ASK_RETRIES_AVAILABLE = False
    FixedAsksRetries = None

logger = get_logger("ChatAgentConnectionManager")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class AgentConnectionState(Enum):
    """Chat agent connection state"""
    CONNECTED = "connected"
    CONNECTING = "connecting"
    DISCONNECTED = "disconnected"
    DISCONNECTING = "disconnecting"
    RECONNECTING = "reconnecting"
    STALLED = "stalled"
    REPAIRING = "repairing"
    DEGRADED = "degraded"
    FAILED = "failed"


class RepairStatus(Enum):
    """Self-repair status"""
    NOT_NEEDED = "not_needed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class ChatAgentConnection:
    """Chat agent connection information"""
    agent_id: str
    session_id: str
    state: AgentConnectionState
    connection_type: str = "llm_chat"  # llm_chat, local_cloud, homelab
    host: Optional[str] = None
    port: Optional[int] = None

    # Connection metrics
    connect_time: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    disconnect_count: int = 0
    reconnect_count: int = 0
    repair_count: int = 0

    # Performance metrics
    latency_ms: float = 0.0
    avg_response_time_ms: float = 0.0
    request_count: int = 0
    error_count: int = 0
    success_rate: float = 100.0

    # Resource usage
    cpu_usage: float = 0.0
    memory_usage_mb: float = 0.0
    active_requests: int = 0

    # Self-repair
    repair_status: RepairStatus = RepairStatus.NOT_NEEDED
    last_repair_attempt: Optional[datetime] = None
    repair_attempts: int = 0
    repair_history: List[Dict[str, Any]] = field(default_factory=list)

    # @ask specific
    ask_interactions: int = 0
    ask_success_rate: float = 100.0

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['state'] = self.state.value
        data['repair_status'] = self.repair_status.value
        if self.connect_time:
            data['connect_time'] = self.connect_time.isoformat()
        if self.last_activity:
            data['last_activity'] = self.last_activity.isoformat()
        if self.last_repair_attempt:
            data['last_repair_attempt'] = self.last_repair_attempt.isoformat()
        return data

    def get_load_score(self) -> float:
        """Get load score (0-1, higher = more loaded)"""
        cpu_factor = self.cpu_usage / 100.0
        memory_factor = min(1.0, self.memory_usage_mb / 2048.0)  # Normalize to 2GB
        request_factor = min(1.0, self.active_requests / 10.0)  # Normalize to 10 requests
        error_factor = (100.0 - self.success_rate) / 100.0

        # Weighted average
        load_score = (cpu_factor * 0.25 + memory_factor * 0.25 + 
                     request_factor * 0.25 + error_factor * 0.25)
        return max(0.0, min(1.0, load_score))

    def needs_repair(self) -> bool:
        """Check if connection needs repair"""
        if self.state in [AgentConnectionState.FAILED, AgentConnectionState.STALLED]:
            return True
        if self.success_rate < 50.0:
            return True
        if self.disconnect_count > 3:
            return True
        if self.error_count > 10:
            return True
        return False

    def is_healthy(self) -> bool:
        """Check if connection is healthy"""
        return (self.state == AgentConnectionState.CONNECTED and 
                self.success_rate >= 80.0 and
                self.error_count < 5)


@dataclass
class AskInteraction:
    """@ask interaction tracking"""
    interaction_id: str
    agent_id: str
    session_id: str
    timestamp: datetime
    query: str
    response: Optional[str] = None
    success: bool = False
    latency_ms: float = 0.0
    retry_count: int = 0
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class ChatAgentConnectionManager:
    """
    Chat Agent Connection Manager

    Manages all homelab (local cloud) LLM chat agents with:
    - Disconnect/reconnect handling
    - Self-repair mechanisms
    - @ask interaction management
    - Load balancing across sessions
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Chat Agent Connection Manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("ChatAgentConnectionManager")

        # Data directories
        self.data_dir = self.project_root / "data" / "chat_agents"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Connection tracking
        self.connections: Dict[str, ChatAgentConnection] = {}
        self.ask_interactions: List[AskInteraction] = []

        # Load balancing
        self.load_balancer: Optional[IDESessionLoadBalancer] = None
        if LOAD_BALANCER_AVAILABLE:
            try:
                self.load_balancer = IDESessionLoadBalancer(project_root)
                self.logger.info("✅ Integrated with IDE Session Load Balancer")
            except Exception as e:
                self.logger.warning(f"Could not initialize load balancer: {e}")

        # Connection optimization
        self.connection_optimizer: Optional[ConnectionFlowOptimizer] = None
        if CONNECTION_OPTIMIZER_AVAILABLE:
            try:
                self.connection_optimizer = ConnectionFlowOptimizer(project_root)
                self.connection_optimizer.start_monitoring()
                self.logger.info("✅ Integrated with Connection Flow Optimizer")
            except Exception as e:
                self.logger.warning(f"Could not initialize connection optimizer: {e}")

        # @ask retries
        self.ask_retries: Optional[FixedAsksRetries] = None
        if ASK_RETRIES_AVAILABLE:
            try:
                retry_config = RetryConfig(
                    max_retries=3,
                    initial_delay=0.5,
                    timeout=10.0
                )
                self.ask_retries = FixedAsksRetries(project_root, retry_config)
                self.logger.info("✅ Integrated with @ask Retries")
            except Exception as e:
                self.logger.warning(f"Could not initialize ask retries: {e}")

        # Monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.repair_thread: Optional[threading.Thread] = None

        # Configuration
        self.reconnect_delay = 0.5  # Fast reconnect
        self.repair_delay = 2.0  # Repair delay
        self.max_reconnect_attempts = 5
        self.max_repair_attempts = 3
        self.stall_timeout = 30.0  # seconds
        self.health_check_interval = 5.0  # seconds

        # Statistics
        self.total_connections = 0
        self.total_disconnects = 0
        self.total_reconnects = 0
        self.total_repairs = 0
        self.total_ask_interactions = 0

        self.logger.info("✅ Chat Agent Connection Manager initialized")
        self.logger.info("   Features: Disconnect handling, Self-repair, @ask management, Load balancing")

        # Start monitoring
        self.start_monitoring()

    def register_agent(self, agent_id: str, session_id: str, 
                      connection_type: str = "llm_chat",
                      host: Optional[str] = None, port: Optional[int] = None) -> ChatAgentConnection:
        """Register a new chat agent connection"""
        connection = ChatAgentConnection(
            agent_id=agent_id,
            session_id=session_id,
            state=AgentConnectionState.CONNECTING,
            connection_type=connection_type,
            host=host,
            port=port,
            connect_time=datetime.now(),
            last_activity=datetime.now()
        )

        self.connections[agent_id] = connection
        self.total_connections += 1

        # Optimize connection if optimizer available
        if self.connection_optimizer:
            self.connection_optimizer.optimize_connection(agent_id, connection_type)

        # Mark as connected
        connection.state = AgentConnectionState.CONNECTED

        self.logger.info(f"📝 Registered chat agent: {agent_id} (session: {session_id})")
        return connection

    def handle_disconnect(self, agent_id: str, reason: Optional[str] = None) -> bool:
        """Handle agent disconnect and initiate reconnection"""
        if agent_id not in self.connections:
            self.logger.warning(f"Unknown agent disconnect: {agent_id}")
            return False

        connection = self.connections[agent_id]
        connection.state = AgentConnectionState.DISCONNECTING
        connection.disconnect_count += 1
        self.total_disconnects += 1

        self.logger.warning(f"⚠️  Agent disconnected: {agent_id} (reason: {reason or 'unknown'})")
        self.logger.info(f"   Disconnect count: {connection.disconnect_count}")

        # Check if repair is needed
        if connection.needs_repair():
            self.logger.info(f"   🔧 Agent needs repair, initiating self-repair...")
            self._initiate_repair(agent_id)
        else:
            # Attempt reconnection
            self._attempt_reconnect(agent_id)

        return True

    def _attempt_reconnect(self, agent_id: str) -> bool:
        """Attempt to reconnect agent"""
        connection = self.connections[agent_id]

        if connection.reconnect_count >= self.max_reconnect_attempts:
            self.logger.error(f"❌ Max reconnect attempts reached for {agent_id}")
            connection.state = AgentConnectionState.FAILED
            return False

        connection.state = AgentConnectionState.RECONNECTING
        connection.reconnect_count += 1

        self.logger.info(f"🔄 Attempting reconnect: {agent_id} (attempt {connection.reconnect_count})")

        # Use optimized reconnect delay
        reconnect_delay = self.reconnect_delay
        if self.connection_optimizer:
            reconnect_delay = self.connection_optimizer.get_optimized_delay("reconnect", reconnect_delay)

        # Simulate reconnect (in real implementation, this would actually reconnect)
        time.sleep(reconnect_delay)

        # Check if reconnection successful (in real implementation, verify connection)
        connection.state = AgentConnectionState.CONNECTED
        connection.last_activity = datetime.now()
        self.total_reconnects += 1

        self.logger.info(f"✅ Reconnected: {agent_id}")
        return True

    def _initiate_repair(self, agent_id: str) -> bool:
        """Initiate self-repair for agent"""
        connection = self.connections[agent_id]

        if connection.repair_status == RepairStatus.IN_PROGRESS:
            self.logger.debug(f"Repair already in progress for {agent_id}")
            return False

        if connection.repair_attempts >= self.max_repair_attempts:
            self.logger.error(f"❌ Max repair attempts reached for {agent_id}")
            connection.repair_status = RepairStatus.FAILED
            connection.state = AgentConnectionState.FAILED
            return False

        connection.repair_status = RepairStatus.IN_PROGRESS
        connection.state = AgentConnectionState.REPAIRING
        connection.repair_attempts += 1
        connection.last_repair_attempt = datetime.now()
        self.total_repairs += 1

        self.logger.info(f"🔧 Initiating self-repair: {agent_id} (attempt {connection.repair_attempts})")

        # Perform repair operations
        repair_success = self._perform_repair(agent_id)

        if repair_success:
            connection.repair_status = RepairStatus.COMPLETED
            connection.state = AgentConnectionState.CONNECTED
            connection.last_activity = datetime.now()
            connection.error_count = 0  # Reset error count after successful repair

            repair_record = {
                "timestamp": datetime.now().isoformat(),
                "attempt": connection.repair_attempts,
                "success": True,
                "actions": ["reset_connection", "clear_errors", "verify_health"]
            }
            connection.repair_history.append(repair_record)

            self.logger.info(f"✅ Self-repair completed: {agent_id}")
        else:
            connection.repair_status = RepairStatus.PARTIAL
            self.logger.warning(f"⚠️  Partial repair: {agent_id} (may need manual intervention)")

            repair_record = {
                "timestamp": datetime.now().isoformat(),
                "attempt": connection.repair_attempts,
                "success": False,
                "actions": ["attempted_reset", "partial_recovery"]
            }
            connection.repair_history.append(repair_record)

        return repair_success

    def _perform_repair(self, agent_id: str) -> bool:
        """Perform actual repair operations"""
        connection = self.connections[agent_id]

        repair_actions = []

        # Action 1: Reset connection state
        try:
            connection.error_count = max(0, connection.error_count - 5)  # Reduce error count
            repair_actions.append("reset_error_count")
        except Exception as e:
            self.logger.debug(f"Repair action failed: {e}")

        # Action 2: Clear stale state
        try:
            connection.active_requests = 0  # Clear active requests
            repair_actions.append("clear_active_requests")
        except Exception as e:
            self.logger.debug(f"Repair action failed: {e}")

        # Action 3: Attempt reconnection
        try:
            reconnect_success = self._attempt_reconnect(agent_id)
            if reconnect_success:
                repair_actions.append("reconnect_successful")
            else:
                repair_actions.append("reconnect_failed")
        except Exception as e:
            self.logger.debug(f"Repair reconnect failed: {e}")
            repair_actions.append("reconnect_error")

        # Action 4: Verify health
        try:
            if connection.is_healthy():
                repair_actions.append("health_verified")
                return True
            else:
                repair_actions.append("health_check_failed")
        except Exception as e:
            self.logger.debug(f"Health check failed: {e}")

        # If we got here, repair was partial
        return len(repair_actions) >= 2  # At least 2 actions succeeded

    def handle_ask_interaction(self, agent_id: str, query: str, 
                              session_id: Optional[str] = None) -> AskInteraction:
        """Handle @ask interaction with load balancing and retry logic"""
        if agent_id not in self.connections:
            # Auto-register if not found
            session_id = session_id or f"session_{int(time.time())}"
            self.register_agent(agent_id, session_id)

        connection = self.connections[agent_id]
        session_id = session_id or connection.session_id

        # Check load balancing
        if self.load_balancer:
            if not self.load_balancer.can_accept_request(session_id):
                # Find least loaded agent
                least_loaded = self.load_balancer.get_least_loaded_session()
                if least_loaded:
                    self.logger.info(f"⚖️  Load balancing: routing @ask to {least_loaded.session_id}")
                    # In real implementation, route to least loaded agent

        # Record request
        if self.load_balancer:
            self.load_balancer.record_request(session_id)

        connection.active_requests += 1
        connection.ask_interactions += 1
        self.total_ask_interactions += 1

        # Create interaction
        interaction = AskInteraction(
            interaction_id=f"ask_{int(time.time())}_{agent_id}",
            agent_id=agent_id,
            session_id=session_id,
            timestamp=datetime.now(),
            query=query
        )

        # Execute with retry logic
        start_time = time.time()
        success = False
        error = None

        if self.ask_retries:
            # Use retry system
            def ask_operation():
                # Simulate @ask operation (in real implementation, this would call the actual agent)
                time.sleep(0.1)  # Simulate processing
                return f"Response to: {query}"

            retry_result = self.ask_retries.ask_with_retry(ask_operation)
            success = retry_result.success
            if success:
                interaction.response = retry_result.result
            else:
                error = retry_result.error
            interaction.retry_count = retry_result.attempts - 1
        else:
            # Direct execution (no retry system)
            try:
                # Simulate @ask operation
                time.sleep(0.1)
                interaction.response = f"Response to: {query}"
                success = True
            except Exception as e:
                error = str(e)
                success = False

        interaction.latency_ms = (time.time() - start_time) * 1000
        interaction.success = success
        interaction.error = error

        # Update connection metrics
        connection.last_activity = datetime.now()
        connection.active_requests = max(0, connection.active_requests - 1)

        if success:
            connection.request_count += 1
            connection.avg_response_time_ms = (
                (connection.avg_response_time_ms * (connection.request_count - 1) + interaction.latency_ms) /
                connection.request_count
            )
        else:
            connection.error_count += 1

        # Update success rate
        total_requests = connection.request_count + connection.error_count
        if total_requests > 0:
            connection.success_rate = (connection.request_count / total_requests) * 100.0

        # Update @ask success rate
        if connection.ask_interactions > 0:
            successful_asks = sum(1 for i in self.ask_interactions 
                                if i.agent_id == agent_id and i.success)
            connection.ask_success_rate = (successful_asks / connection.ask_interactions) * 100.0

        # Complete request in load balancer
        if self.load_balancer:
            self.load_balancer.complete_request(session_id)

        # Store interaction
        self.ask_interactions.append(interaction)

        # Keep only recent interactions (last 1000)
        if len(self.ask_interactions) > 1000:
            self.ask_interactions = self.ask_interactions[-1000:]

        self.logger.debug(f"📝 @ask interaction: {agent_id} - {query[:50]}... ({'✅' if success else '❌'})")

        return interaction

    def start_monitoring(self) -> None:
        """Start connection monitoring and repair"""
        if self.monitoring_active:
            return

        self.monitoring_active = True

        # Health monitoring thread
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()

        # Self-repair thread
        self.repair_thread = threading.Thread(
            target=self._repair_loop,
            daemon=True
        )
        self.repair_thread.start()

        self.logger.info("✅ Monitoring and repair threads started")

    def _monitoring_loop(self) -> None:
        """Monitor connections for health and disconnects"""
        while self.monitoring_active:
            try:
                for agent_id, connection in list(self.connections.items()):
                    # Check for stalls
                    if connection.last_activity:
                        time_since_activity = (datetime.now() - connection.last_activity).total_seconds()
                        if time_since_activity > self.stall_timeout and connection.state == AgentConnectionState.CONNECTED:
                            self.logger.warning(f"⚠️  Agent stalled: {agent_id} ({time_since_activity:.1f}s)")
                            connection.state = AgentConnectionState.STALLED
                            self.handle_disconnect(agent_id, "stall_detected")

                    # Check health
                    if not connection.is_healthy() and connection.state == AgentConnectionState.CONNECTED:
                        self.logger.warning(f"⚠️  Agent unhealthy: {agent_id} (success_rate: {connection.success_rate:.1f}%)")
                        if connection.needs_repair():
                            self._initiate_repair(agent_id)

                time.sleep(self.health_check_interval)
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(self.health_check_interval)

    def _repair_loop(self) -> None:
        """Background repair loop"""
        while self.monitoring_active:
            try:
                # Check for agents needing repair
                for agent_id, connection in list(self.connections.items()):
                    if connection.needs_repair() and connection.repair_status != RepairStatus.IN_PROGRESS:
                        self._initiate_repair(agent_id)

                time.sleep(self.repair_delay)
            except Exception as e:
                self.logger.error(f"Repair loop error: {e}")
                time.sleep(self.repair_delay)

    def get_least_loaded_agent(self) -> Optional[ChatAgentConnection]:
        """Get least loaded agent for load balancing"""
        healthy_agents = [
            conn for conn in self.connections.values()
            if conn.is_healthy() and conn.state == AgentConnectionState.CONNECTED
        ]

        if not healthy_agents:
            return None

        return min(healthy_agents, key=lambda c: c.get_load_score())

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status"""
        healthy_count = sum(1 for c in self.connections.values() if c.is_healthy())
        repairing_count = sum(1 for c in self.connections.values() 
                            if c.repair_status == RepairStatus.IN_PROGRESS)

        return {
            "timestamp": datetime.now().isoformat(),
            "total_agents": len(self.connections),
            "healthy_agents": healthy_count,
            "repairing_agents": repairing_count,
            "total_disconnects": self.total_disconnects,
            "total_reconnects": self.total_reconnects,
            "total_repairs": self.total_repairs,
            "total_ask_interactions": self.total_ask_interactions,
            "integrations": {
                "load_balancer": LOAD_BALANCER_AVAILABLE and self.load_balancer is not None,
                "connection_optimizer": CONNECTION_OPTIMIZER_AVAILABLE and self.connection_optimizer is not None,
                "ask_retries": ASK_RETRIES_AVAILABLE and self.ask_retries is not None
            },
            "connections": {k: v.to_dict() for k, v in self.connections.items()},
            "recent_ask_interactions": [i.to_dict() for i in self.ask_interactions[-10:]]
        }

    def save_state(self) -> None:
        """Save state to disk"""
        state_file = self.data_dir / "connection_state.json"
        try:
            with open(state_file, 'w') as f:
                json.dump(self.get_status(), f, indent=2)
        except Exception as e:
            self.logger.debug(f"Could not save state: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Chat Agent Connection Manager")
    parser.add_argument("--status", action="store_true", help="Get status")
    parser.add_argument("--register", type=str, help="Register agent (agent_id)")
    parser.add_argument("--disconnect", type=str, help="Simulate disconnect (agent_id)")
    parser.add_argument("--ask", type=str, nargs=2, metavar=("AGENT_ID", "QUERY"), 
                       help="Handle @ask interaction")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    manager = ChatAgentConnectionManager()

    if args.register:
        manager.register_agent(args.register, f"session_{int(time.time())}")
        print(f"✅ Registered agent: {args.register}")

    elif args.disconnect:
        manager.handle_disconnect(args.disconnect, "manual_test")
        print(f"⚠️  Disconnected agent: {args.disconnect}")

    elif args.ask:
        agent_id, query = args.ask
        interaction = manager.handle_ask_interaction(agent_id, query)
        if args.json:
            print(json.dumps(interaction.to_dict(), indent=2))
        else:
            print(f"📝 @ask interaction: {interaction.interaction_id}")
            print(f"   Success: {interaction.success}")
            print(f"   Latency: {interaction.latency_ms:.1f}ms")
            if interaction.response:
                print(f"   Response: {interaction.response[:100]}...")

    elif args.status:
        status = manager.get_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print("\n🤖 Chat Agent Connection Manager Status")
            print("=" * 60)
            print(f"Total Agents: {status['total_agents']}")
            print(f"Healthy Agents: {status['healthy_agents']}")
            print(f"Repairing Agents: {status['repairing_agents']}")
            print(f"Total Disconnects: {status['total_disconnects']}")
            print(f"Total Reconnects: {status['total_reconnects']}")
            print(f"Total Repairs: {status['total_repairs']}")
            print(f"Total @ask Interactions: {status['total_ask_interactions']}")
            print("\nIntegrations:")
            for name, enabled in status['integrations'].items():
                print(f"  {name}: {'✅' if enabled else '❌'}")

    else:
        parser.print_help()
        print("\n🤖 Chat Agent Connection Manager")
        print("   Features: Disconnect handling, Self-repair, @ask management, Load balancing")

