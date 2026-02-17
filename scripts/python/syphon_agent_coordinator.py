#!/usr/bin/env python3
"""
SYPHON Agent & Subagent Coordinator
Routes SYPHON-extracted intelligence to appropriate agents and subagents

SYPHON extracts intelligence (actionable items, tasks, decisions, general intelligence)
and this coordinator routes it to the right agents/subagents for execution.

Tags: #SYPHON #AGENTS #SUBAGENTS #COORDINATION #INTELLIGENCE #ROUTING @JARVIS @TEAM
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SyphonAgentCoordinator")

try:
    from syphon import SYPHONSystem, SYPHONConfig, DataSourceType, SyphonData
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None
    SYPHONConfig = None
    DataSourceType = None
    SyphonData = None

try:
    from jarvis_fulltime_super_agent import JARVISFullTimeSuperAgent
    JARVIS_AVAILABLE = True
except ImportError:
    JARVIS_AVAILABLE = False
    JARVISFullTimeSuperAgent = None

try:
    from dynamic_subagent_spawner import DynamicSubagentSpawner, SubagentType
    SUBAGENT_SPAWNER_AVAILABLE = True
except ImportError:
    SUBAGENT_SPAWNER_AVAILABLE = False
    DynamicSubagentSpawner = None
    SubagentType = None

try:
    from droid_actor_system import DroidActorSystem
    DROID_ACTOR_AVAILABLE = True
except ImportError:
    DROID_ACTOR_AVAILABLE = False
    DroidActorSystem = None


class IntelligenceType(Enum):
    """Types of intelligence extracted by SYPHON"""
    ACTIONABLE_ITEM = "actionable_item"
    TASK = "task"
    DECISION = "decision"
    GENERAL_INTELLIGENCE = "general_intelligence"
    IDE_NOTIFICATION = "ide_notification"
    WORKFLOW_PATTERN = "workflow_pattern"
    ERROR_PATTERN = "error_pattern"


class AgentCapability(Enum):
    """Agent capabilities for routing intelligence"""
    WORKFLOW_EXECUTION = "workflow_execution"
    TASK_MANAGEMENT = "task_management"
    DECISION_MAKING = "decision_making"
    MONITORING = "monitoring"
    OPTIMIZATION = "optimization"
    SECURITY = "security"
    TECHNICAL = "technical"
    MEDICAL = "medical"
    COMMUNICATION = "communication"
    KNOWLEDGE = "knowledge"
    ANALYSIS = "analysis"
    AUTOMATION = "automation"


@dataclass
class IntelligenceRouting:
    """Intelligence routing decision"""
    intelligence_id: str
    intelligence_type: IntelligenceType
    source_data: Dict[str, Any]
    target_agent: str
    target_subagent: Optional[str] = None
    routing_reason: str = ""
    priority: int = 5  # 1-10, 10 is highest
    routed_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["intelligence_type"] = self.intelligence_type.value
        data["routed_at"] = self.routed_at.isoformat()
        return data


@dataclass
class AgentProfile:
    """Profile of an agent's capabilities"""
    agent_id: str
    agent_name: str
    capabilities: List[AgentCapability]
    keywords: List[str] = field(default_factory=list)
    priority_threshold: int = 5  # Only route high-priority items (>= threshold)
    max_concurrent_tasks: int = 5
    current_tasks: int = 0

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["capabilities"] = [c.value for c in self.capabilities]
        return data


class SyphonAgentCoordinator:
    """
    SYPHON Agent & Subagent Coordinator

    Routes SYPHON-extracted intelligence to appropriate agents and subagents
    based on intelligence type, content, and agent capabilities.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize SYPHON-Agent coordinator"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # SYPHON integration
        self.syphon: Optional[SYPHONSystem] = None
        if SYPHON_AVAILABLE:
            try:
                config = SYPHONConfig(project_root=self.project_root, enable_regex_tools=True)
                self.syphon = SYPHONSystem(config)
                logger.info("✅ SYPHON system initialized")
            except Exception as e:
                logger.warning(f"⚠️  SYPHON not available: {e}")

        # JARVIS integration
        self.jarvis: Optional[JARVISFullTimeSuperAgent] = None
        if JARVIS_AVAILABLE:
            try:
                self.jarvis = JARVISFullTimeSuperAgent(self.project_root)
                logger.info("✅ JARVIS Superagent initialized")
            except Exception as e:
                logger.warning(f"⚠️  JARVIS not available: {e}")

        # Subagent spawner
        self.subagent_spawner: Optional[DynamicSubagentSpawner] = None
        if SUBAGENT_SPAWNER_AVAILABLE:
            try:
                self.subagent_spawner = DynamicSubagentSpawner(self.project_root)
                logger.info("✅ Subagent spawner initialized")
            except Exception as e:
                logger.warning(f"⚠️  Subagent spawner not available: {e}")

        # Droid actor system
        self.droid_actor: Optional[DroidActorSystem] = None
        if DROID_ACTOR_AVAILABLE:
            try:
                self.droid_actor = DroidActorSystem(self.project_root)
                logger.info("✅ Droid actor system initialized")
            except Exception as e:
                logger.warning(f"⚠️  Droid actor system not available: {e}")

        # Agent profiles (capabilities mapping)
        self.agent_profiles: Dict[str, AgentProfile] = {}
        self._initialize_agent_profiles()

        # Routing history
        self.routing_history: List[IntelligenceRouting] = []
        self.max_history = 1000

        logger.info("✅ SYPHON Agent Coordinator initialized")

    def _initialize_agent_profiles(self):
        """Initialize agent capability profiles"""
        # JARVIS - Master coordinator
        self.agent_profiles["jarvis"] = AgentProfile(
            agent_id="jarvis",
            agent_name="JARVIS",
            capabilities=[
                AgentCapability.WORKFLOW_EXECUTION,
                AgentCapability.TASK_MANAGEMENT,
                AgentCapability.DECISION_MAKING,
                AgentCapability.MONITORING,
                AgentCapability.OPTIMIZATION
            ],
            keywords=["coordinate", "orchestrate", "manage", "execute", "decision"],
            priority_threshold=7,  # High priority items only
            max_concurrent_tasks=10
        )

        # Droid agents (from droid actor system)
        droid_capabilities = {
            "r2d2": [AgentCapability.TECHNICAL, AgentCapability.WORKFLOW_EXECUTION],
            "k2so": [AgentCapability.SECURITY, AgentCapability.MONITORING],
            "2-1b": [AgentCapability.MEDICAL, AgentCapability.MONITORING],
            "c3po": [AgentCapability.COMMUNICATION, AgentCapability.TASK_MANAGEMENT],
            "ig88": [AgentCapability.SECURITY, AgentCapability.DECISION_MAKING],
            "mousedroid": [AgentCapability.AUTOMATION, AgentCapability.WORKFLOW_EXECUTION],
            "r5": [AgentCapability.KNOWLEDGE, AgentCapability.ANALYSIS],
            "marvin": [AgentCapability.ANALYSIS, AgentCapability.DECISION_MAKING]
        }

        for droid_id, capabilities in droid_capabilities.items():
            self.agent_profiles[droid_id] = AgentProfile(
                agent_id=droid_id,
                agent_name=droid_id.upper(),
                capabilities=capabilities,
                keywords=[droid_id],
                priority_threshold=5,
                max_concurrent_tasks=3
            )

        # Subagent types
        if SUBAGENT_SPAWNER_AVAILABLE and SubagentType:
            subagent_capabilities = {
                SubagentType.WORKFLOW_EXECUTOR: [AgentCapability.WORKFLOW_EXECUTION],
                SubagentType.RESOURCE_MANAGER: [AgentCapability.OPTIMIZATION, AgentCapability.MONITORING],
                SubagentType.QUALITY_ASSURANCE: [AgentCapability.MONITORING, AgentCapability.OPTIMIZATION],
                SubagentType.MONITORING_AGENT: [AgentCapability.MONITORING],
                SubagentType.OPTIMIZATION_AGENT: [AgentCapability.OPTIMIZATION],
                SubagentType.RECOVERY_AGENT: [AgentCapability.WORKFLOW_EXECUTION, AgentCapability.MONITORING],
                SubagentType.COORDINATION_AGENT: [AgentCapability.TASK_MANAGEMENT, AgentCapability.DECISION_MAKING],
                SubagentType.PREDICTION_AGENT: [AgentCapability.ANALYSIS, AgentCapability.DECISION_MAKING]
            }

            for subagent_type, capabilities in subagent_capabilities.items():
                agent_id = f"subagent_{subagent_type.value}"
                self.agent_profiles[agent_id] = AgentProfile(
                    agent_id=agent_id,
                    agent_name=f"Subagent: {subagent_type.value}",
                    capabilities=capabilities,
                    keywords=[subagent_type.value],
                    priority_threshold=5,
                    max_concurrent_tasks=2
                )

    def extract_and_route_intelligence(self, source_type: DataSourceType, content: str, metadata: Optional[Dict[str, Any]] = None) -> List[IntelligenceRouting]:
        """
        Extract intelligence using SYPHON and route to appropriate agents/subagents

        Args:
            source_type: Type of data source (IDE, EMAIL, SMS, etc.)
            content: Content to extract intelligence from
            metadata: Optional metadata about the source

        Returns:
            List of routing decisions
        """
        if not self.syphon:
            logger.warning("SYPHON not available, cannot extract intelligence")
            return []

        # Extract intelligence using SYPHON
        result = self.syphon.extract(source_type, content, metadata=metadata or {})

        if not result.success or not result.data:
            logger.debug("No intelligence extracted")
            return []

        syphon_data = result.data
        routings = []

        # Route actionable items
        if syphon_data.actionable_items:
            for item in syphon_data.actionable_items:
                routing = self._route_intelligence(
                    IntelligenceType.ACTIONABLE_ITEM,
                    item,
                    syphon_data
                )
                if routing:
                    routings.append(routing)

        # Route tasks
        if syphon_data.tasks:
            for task in syphon_data.tasks:
                routing = self._route_intelligence(
                    IntelligenceType.TASK,
                    task,
                    syphon_data
                )
                if routing:
                    routings.append(routing)

        # Route decisions
        if syphon_data.decisions:
            for decision in syphon_data.decisions:
                routing = self._route_intelligence(
                    IntelligenceType.DECISION,
                    decision,
                    syphon_data
                )
                if routing:
                    routings.append(routing)

        # Route general intelligence
        if syphon_data.intelligence:
            for intelligence in syphon_data.intelligence:
                routing = self._route_intelligence(
                    IntelligenceType.GENERAL_INTELLIGENCE,
                    intelligence,
                    syphon_data
                )
                if routing:
                    routings.append(routing)

        # Route IDE notifications
        if source_type == DataSourceType.IDE:
            routing = self._route_intelligence(
                IntelligenceType.IDE_NOTIFICATION,
                content,
                syphon_data
            )
            if routing:
                routings.append(routing)

        # Store routing history
        self.routing_history.extend(routings)
        if len(self.routing_history) > self.max_history:
            self.routing_history = self.routing_history[-self.max_history:]

        logger.info(f"✅ Routed {len(routings)} intelligence items to agents/subagents")

        return routings

    def _route_intelligence(self, intelligence_type: IntelligenceType, content: Any, syphon_data: SyphonData) -> Optional[IntelligenceRouting]:
        """
        Route a single intelligence item to the appropriate agent/subagent

        Args:
            intelligence_type: Type of intelligence
            content: Intelligence content (string or dict)
            syphon_data: Full SYPHON data for context

        Returns:
            Routing decision or None
        """
        # Convert content to string for analysis
        if isinstance(content, dict):
            content_text = content.get("task", content.get("item", content.get("decision", str(content))))
        else:
            content_text = str(content)

        content_lower = content_text.lower()

        # Determine priority
        priority = self._calculate_priority(content_text, intelligence_type, syphon_data)

        # Find matching agents based on capabilities and keywords
        matching_agents = []

        for agent_id, profile in self.agent_profiles.items():
            # Check if agent can handle this priority
            if priority < profile.priority_threshold:
                continue

            # Check if agent is at capacity
            if profile.current_tasks >= profile.max_concurrent_tasks:
                continue

            # Check capabilities match
            capability_match = False
            if intelligence_type == IntelligenceType.ACTIONABLE_ITEM:
                capability_match = AgentCapability.TASK_MANAGEMENT in profile.capabilities
            elif intelligence_type == IntelligenceType.TASK:
                capability_match = AgentCapability.TASK_MANAGEMENT in profile.capabilities or AgentCapability.WORKFLOW_EXECUTION in profile.capabilities
            elif intelligence_type == IntelligenceType.DECISION:
                capability_match = AgentCapability.DECISION_MAKING in profile.capabilities
            elif intelligence_type == IntelligenceType.GENERAL_INTELLIGENCE:
                capability_match = True  # Any agent can handle general intelligence
            elif intelligence_type == IntelligenceType.IDE_NOTIFICATION:
                capability_match = AgentCapability.MONITORING in profile.capabilities or AgentCapability.TECHNICAL in profile.capabilities

            # Check keyword matches
            keyword_match = any(keyword in content_lower for keyword in profile.keywords)

            if capability_match or keyword_match:
                score = priority
                if keyword_match:
                    score += 2  # Boost for keyword match
                matching_agents.append((agent_id, profile, score))

        if not matching_agents:
            # No matching agent found - route to JARVIS as fallback
            if "jarvis" in self.agent_profiles:
                agent_id = "jarvis"
                profile = self.agent_profiles[agent_id]
                routing_reason = "No specific agent match, routed to JARVIS (fallback)"
            else:
                logger.warning(f"No agent available to route {intelligence_type.value}")
                return None
        else:
            # Sort by score (highest first) and select best match
            matching_agents.sort(key=lambda x: x[2], reverse=True)
            agent_id, profile, score = matching_agents[0]
            routing_reason = f"Matched agent {agent_id} (score: {score}, capabilities: {[c.value for c in profile.capabilities]})"

        # Determine if subagent should be spawned
        subagent_id = None
        if self.subagent_spawner and priority >= 8:
            # High priority - consider spawning dedicated subagent
            if intelligence_type == IntelligenceType.TASK:
                subagent_type = SubagentType.WORKFLOW_EXECUTOR
            elif intelligence_type == IntelligenceType.DECISION:
                subagent_type = SubagentType.COORDINATION_AGENT
            else:
                subagent_type = None

            if subagent_type:
                try:
                    spawned = self.subagent_spawner.spawn_subagent(
                        subagent_type=subagent_type,
                        context={"intelligence": content_text, "priority": priority}
                    )
                    if spawned:
                        subagent_id = f"subagent_{subagent_type.value}_{spawned.get('subagent_id', 'unknown')}"
                        routing_reason += f" | Spawned subagent: {subagent_type.value}"
                except Exception as e:
                    logger.debug(f"Subagent spawn failed: {e}")

        # Create routing
        routing = IntelligenceRouting(
            intelligence_id=f"{intelligence_type.value}_{int(time.time())}",
            intelligence_type=intelligence_type,
            source_data={"content": content_text, "priority": priority},
            target_agent=agent_id,
            target_subagent=subagent_id,
            routing_reason=routing_reason,
            priority=priority
        )

        # Update agent task count
        profile.current_tasks += 1

        logger.info(f"📤 Routed {intelligence_type.value} to {agent_id}" + (f" (subagent: {subagent_id})" if subagent_id else ""))

        return routing

    def _calculate_priority(self, content: str, intelligence_type: IntelligenceType, syphon_data: SyphonData) -> int:
        """Calculate priority for intelligence item (1-10)"""
        priority = 5  # Default

        # Base priority by type
        type_priorities = {
            IntelligenceType.ACTIONABLE_ITEM: 6,
            IntelligenceType.TASK: 7,
            IntelligenceType.DECISION: 8,
            IntelligenceType.GENERAL_INTELLIGENCE: 4,
            IntelligenceType.IDE_NOTIFICATION: 6,
            IntelligenceType.WORKFLOW_PATTERN: 5,
            IntelligenceType.ERROR_PATTERN: 9
        }
        priority = type_priorities.get(intelligence_type, 5)

        # Boost for urgent keywords
        urgent_keywords = ["urgent", "critical", "immediate", "asap", "emergency", "error", "fail", "broken"]
        if any(keyword in content.lower() for keyword in urgent_keywords):
            priority = min(10, priority + 2)

        # Boost for high-priority task markers
        if isinstance(content, dict) and content.get("priority") == "high":
            priority = min(10, priority + 2)

        return priority

    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get statistics about intelligence routing"""
        if not self.routing_history:
            return {"total_routed": 0}

        stats = {
            "total_routed": len(self.routing_history),
            "by_type": {},
            "by_agent": {},
            "by_priority": {},
            "recent_routings": [r.to_dict() for r in self.routing_history[-10:]]
        }

        # Count by type
        for routing in self.routing_history:
            type_name = routing.intelligence_type.value
            stats["by_type"][type_name] = stats["by_type"].get(type_name, 0) + 1

        # Count by agent
        for routing in self.routing_history:
            agent = routing.target_agent
            stats["by_agent"][agent] = stats["by_agent"].get(agent, 0) + 1

        # Count by priority
        for routing in self.routing_history:
            priority_range = f"{routing.priority}-{routing.priority}"
            stats["by_priority"][priority_range] = stats["by_priority"].get(priority_range, 0) + 1

        return stats


if __name__ == "__main__":
    # Test the coordinator
    coordinator = SyphonAgentCoordinator()

    print("\n" + "="*80)
    print("SYPHON Agent & Subagent Coordinator Test")
    print("="*80 + "\n")

    # Test intelligence extraction and routing
    test_content = """
    @ask: Fix the critical bug in the authentication system
    @ask: Update documentation for the new API
    Decision: Use cloud storage for backup
    Actionable: Review security logs daily
    """

    print("Extracting and routing intelligence...")
    from syphon.models import DataSourceType

    routings = coordinator.extract_and_route_intelligence(
        DataSourceType.IDE,
        test_content,
        metadata={"source": "test", "test": True}
    )

    print(f"\n✅ Routed {len(routings)} intelligence items")
    print("\nRouting Details:")
    for routing in routings:
        print(f"  - {routing.intelligence_type.value} → {routing.target_agent}")
        if routing.target_subagent:
            print(f"    Subagent: {routing.target_subagent}")
        print(f"    Priority: {routing.priority}, Reason: {routing.routing_reason}")

    # Show statistics
    stats = coordinator.get_routing_statistics()
    print(f"\n📊 Routing Statistics:")
    print(f"  Total Routed: {stats['total_routed']}")
    print(f"  By Type: {stats.get('by_type', {})}")
    print(f"  By Agent: {stats.get('by_agent', {})}")

    print("\n✅ SYPHON Agent Coordinator Test Complete")
