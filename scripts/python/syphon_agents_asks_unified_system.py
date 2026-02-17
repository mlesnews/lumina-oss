#!/usr/bin/env python3
"""
SYPHON + Agents/Subagents + VAs + @asks Unified System

Unified integration of:
- @SYPHON: Intelligence extraction system
- @AGENTS/@SUBAGENTS: Agent coordination and spawning
- @VAs: Virtual Assistants (IMVA, JARVIS VA)
- @ASK @RESTACK @TIMELINE: Ask processing and timeline management

This system creates a unified intelligence pipeline where:
1. SYPHON extracts intelligence from all sources
2. Agents/Subagents/VAs consume and act on SYPHON intelligence
3. @asks are extracted, restacked, and managed via timeline
4. All systems coordinate through JARVIS superagent

Tags: #SYPHON #AGENTS #SUBAGENTS #VAS #ASKS #RESTACK #TIMELINE @JARVIS @TEAM
"""

import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SYPHONAgentsAsksUnifiedSystem")

# SYPHON integration
try:
    from syphon import SYPHONSystem, SYPHONConfig, DataSourceType, SyphonData
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None
    SYPHONConfig = None
    DataSourceType = None
    SyphonData = None

# @asks integration
try:
    from jarvis_restack_all_asks import ASKRestacker
    ASKS_AVAILABLE = True
except ImportError:
    ASKS_AVAILABLE = False
    ASKRestacker = None

# Agent coordination
try:
    from coordinate_agent_sessions import AgentSessionCoordinator
    AGENT_COORDINATION_AVAILABLE = True
except ImportError:
    AGENT_COORDINATION_AVAILABLE = False
    AgentSessionCoordinator = None

# JARVIS Superagent
try:
    from jarvis_fulltime_super_agent import JARVISFullTimeSuperAgent
    JARVIS_SUPERAGENT_AVAILABLE = True
except ImportError:
    JARVIS_SUPERAGENT_AVAILABLE = False
    JARVISFullTimeSuperAgent = None

# Unified @asks processor
try:
    from unified_ask_processor import UnifiedAskProcessor
    UNIFIED_ASK_PROCESSOR_AVAILABLE = True
except ImportError:
    UNIFIED_ASK_PROCESSOR_AVAILABLE = False
    UnifiedAskProcessor = None


@dataclass
class IntelligenceFeed:
    """Intelligence feed from SYPHON to agents/VAs"""
    actionable_items: List[str] = field(default_factory=list)
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    intelligence: List[str] = field(default_factory=list)
    ide_notifications: List[str] = field(default_factory=list)
    extracted_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['extracted_at'] = self.extracted_at.isoformat()
        return data


@dataclass
class AgentIntelligenceState:
    """Intelligence state for an agent/VA"""
    agent_id: str
    agent_type: str  # "agent", "subagent", "va"
    last_intelligence_update: datetime = field(default_factory=datetime.now)
    actionable_items: List[str] = field(default_factory=list)
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    intelligence: List[str] = field(default_factory=list)
    asks_processed: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['last_intelligence_update'] = self.last_intelligence_update.isoformat()
        return data


class SYPHONAgentsAsksUnifiedSystem:
    """
    Unified System: SYPHON + Agents/Subagents + VAs + @asks

    Creates a unified intelligence pipeline where:
    1. SYPHON continuously extracts intelligence
    2. Intelligence is distributed to agents/subagents/VAs
    3. @asks are extracted, restacked, and managed
    4. All systems coordinate through JARVIS
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize unified system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.intelligence_dir = self.data_dir / "intelligence"
        self.intelligence_dir.mkdir(parents=True, exist_ok=True)

        # SYPHON system
        self.syphon = None
        if SYPHON_AVAILABLE:
            try:
                syphon_config = SYPHONConfig(project_root=self.project_root, enable_regex_tools=True)
                self.syphon = SYPHONSystem(syphon_config)
                logger.info("✅ SYPHON system initialized")
            except Exception as e:
                logger.warning(f"⚠️  SYPHON not available: {e}")

        # @asks system
        self.ask_restacker = None
        if ASKS_AVAILABLE:
            try:
                self.ask_restacker = ASKRestacker(project_root=self.project_root)
                logger.info("✅ @asks restacker initialized")
            except Exception as e:
                logger.warning(f"⚠️  @asks restacker not available: {e}")

        # Unified @asks processor
        self.unified_ask_processor = None
        if UNIFIED_ASK_PROCESSOR_AVAILABLE:
            try:
                self.unified_ask_processor = UnifiedAskProcessor(
                    project_root=self.project_root,
                    ask_restacker=self.ask_restacker
                )
                logger.info("✅ Unified @asks processor initialized")
            except Exception as e:
                logger.warning(f"⚠️  Unified @asks processor not available: {e}")

        # Agent coordination
        self.agent_coordinator = None
        if AGENT_COORDINATION_AVAILABLE:
            try:
                self.agent_coordinator = AgentSessionCoordinator(project_root=self.project_root)
                logger.info("✅ Agent coordinator initialized")
            except Exception as e:
                logger.warning(f"⚠️  Agent coordinator not available: {e}")

        # JARVIS Superagent
        self.jarvis_superagent = None
        if JARVIS_SUPERAGENT_AVAILABLE:
            try:
                self.jarvis_superagent = JARVISFullTimeSuperAgent(project_root=self.project_root)
                logger.info("✅ JARVIS Superagent initialized")
            except Exception as e:
                logger.warning(f"⚠️  JARVIS Superagent not available: {e}")

        # Intelligence state tracking
        self.agent_intelligence_states: Dict[str, AgentIntelligenceState] = {}
        self.global_intelligence_feed = IntelligenceFeed()

        # Processing intervals
        self.syphon_extraction_interval = 60.0  # Extract every 60 seconds
        self.intelligence_distribution_interval = 30.0  # Distribute every 30 seconds
        self.ask_processing_interval = 120.0  # Process @asks every 2 minutes

        # Threading
        self.running = False
        self.processing_thread = None

        logger.info("✅ SYPHON + Agents + VAs + @asks Unified System initialized")

    def start(self):
        """Start the unified system"""
        if self.running:
            logger.warning("System already running")
            return

        self.running = True
        self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
        self.processing_thread.start()
        logger.info("🚀 Unified System Started")

    def stop(self):
        """Stop the unified system"""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5.0)
        logger.info("🛑 Unified System Stopped")

    def _processing_loop(self):
        """Main processing loop"""
        last_syphon_extraction = time.time()
        last_intelligence_distribution = time.time()
        last_ask_processing = time.time()

        while self.running:
            try:
                current_time = time.time()

                # SYPHON extraction
                if current_time - last_syphon_extraction >= self.syphon_extraction_interval:
                    self._extract_intelligence_with_syphon()
                    last_syphon_extraction = current_time

                # Intelligence distribution
                if current_time - last_intelligence_distribution >= self.intelligence_distribution_interval:
                    self._distribute_intelligence_to_agents()
                    last_intelligence_distribution = current_time

                # @asks processing
                if current_time - last_ask_processing >= self.ask_processing_interval:
                    self._process_asks()
                    last_ask_processing = current_time

                time.sleep(5.0)  # Check every 5 seconds

            except Exception as e:
                logger.error(f"Error in processing loop: {e}", exc_info=True)
                time.sleep(30.0)

    def _extract_intelligence_with_syphon(self):
        """Extract intelligence using SYPHON"""
        if not self.syphon:
            return

        try:
            # Get recent SYPHON data
            storage = self.syphon.storage
            if not storage:
                return

            recent_data = storage.get_all()
            cutoff_time = datetime.now() - timedelta(hours=24)
            recent_data = [d for d in recent_data if d.extracted_at >= cutoff_time]

            # Aggregate intelligence
            feed = IntelligenceFeed()

            for data in recent_data:
                if data.actionable_items:
                    feed.actionable_items.extend(data.actionable_items)
                if data.tasks:
                    feed.tasks.extend(data.tasks)
                if data.decisions:
                    feed.decisions.extend(data.decisions)
                if data.intelligence:
                    feed.intelligence.extend(data.intelligence)
                if data.source_type.value == "ide":
                    feed.ide_notifications.append(data.content)

            # Update global feed
            self.global_intelligence_feed = feed

            logger.debug(f"SYPHON: Extracted {len(feed.actionable_items)} actionable items, "
                        f"{len(feed.tasks)} tasks, {len(feed.decisions)} decisions, "
                        f"{len(feed.intelligence)} intelligence items")

        except Exception as e:
            logger.error(f"Error extracting intelligence: {e}", exc_info=True)

    def _distribute_intelligence_to_agents(self):
        """Distribute intelligence to all agents/subagents/VAs"""
        if not self.global_intelligence_feed:
            return

        try:
            # Discover active agents
            agents = self._discover_all_agents()

            for agent_id, agent_info in agents.items():
                # Get or create intelligence state
                if agent_id not in self.agent_intelligence_states:
                    self.agent_intelligence_states[agent_id] = AgentIntelligenceState(
                        agent_id=agent_id,
                        agent_type=agent_info.get("type", "agent")
                    )

                state = self.agent_intelligence_states[agent_id]

                # Update intelligence
                state.actionable_items = self.global_intelligence_feed.actionable_items[:10]
                state.tasks = self.global_intelligence_feed.tasks[:10]
                state.decisions = self.global_intelligence_feed.decisions[:10]
                state.intelligence = self.global_intelligence_feed.intelligence[:20]
                state.last_intelligence_update = datetime.now()

                logger.debug(f"Distributed intelligence to {agent_id} ({agent_info.get('type', 'agent')})")

            logger.debug(f"Distributed intelligence to {len(agents)} agents/subagents/VAs")

        except Exception as e:
            logger.error(f"Error distributing intelligence: {e}", exc_info=True)

    def _discover_all_agents(self) -> Dict[str, Dict[str, Any]]:
        """Discover all agents/subagents/VAs"""
        agents = {}

        # Discover agent sessions
        if self.agent_coordinator:
            try:
                sessions = self.agent_coordinator.discover_agent_sessions()
                for session in sessions:
                    agents[session.get("session_id", "unknown")] = {
                        "type": "agent",
                        "name": session.get("agent", "Unknown"),
                        "session": session
                    }
            except Exception as e:
                logger.debug(f"Error discovering agent sessions: {e}")

        # Add VAs (IMVA, JARVIS VA)
        agents["@imva"] = {
            "type": "va",
            "name": "Iron Man Virtual Assistant",
            "va_type": "ironman"
        }
        agents["@jarvis_va"] = {
            "type": "va",
            "name": "JARVIS Virtual Assistant",
            "va_type": "jarvis"
        }

        # Add JARVIS Superagent
        if self.jarvis_superagent:
            agents["@jarvis"] = {
                "type": "superagent",
                "name": "JARVIS Full-Time Super Agent",
                "role": "coordinator"
            }

        return agents

    def _process_asks(self):
        """Process @asks: extract, restack, and manage timeline"""
        if not self.ask_restacker:
            return

        try:
            # Discover all @asks
            all_asks = self.ask_restacker.discover_all_asks()

            if not all_asks:
                return

            # Restack @asks in chronological order
            restacked_asks = self.ask_restacker.restack_asks(all_asks)

            # Create timeline
            timeline = self.ask_restacker.create_timeline(restacked_asks)

            # Save timeline
            timeline_file = self.intelligence_dir / "asks_timeline.json"
            with open(timeline_file, 'w', encoding='utf-8') as f:
                json.dump(timeline, f, indent=2, default=str, ensure_ascii=False)

            # Extract @asks using SYPHON for intelligence
            if self.syphon and self.unified_ask_processor:
                ask_text = "\n".join([ask.get("text", "") for ask in restacked_asks[:50]])
                if ask_text.strip():
                    result = self.syphon.extract(
                        DataSourceType.IDE,
                        ask_text,
                        metadata={"source": "asks_timeline", "unified_system": True}
                    )

                    if result.success and result.data:
                        # Add extracted intelligence to feed
                        if result.data.actionable_items:
                            self.global_intelligence_feed.actionable_items.extend(result.data.actionable_items)
                        if result.data.tasks:
                            self.global_intelligence_feed.tasks.extend(result.data.tasks)

            logger.info(f"✅ Processed {len(restacked_asks)} @asks, timeline saved")

        except Exception as e:
            logger.error(f"Error processing @asks: {e}", exc_info=True)

    def get_intelligence_for_agent(self, agent_id: str) -> Optional[AgentIntelligenceState]:
        """Get intelligence state for a specific agent"""
        return self.agent_intelligence_states.get(agent_id)

    def get_asks_timeline(self) -> List[Dict[str, Any]]:
        """Get @asks timeline"""
        timeline_file = self.intelligence_dir / "asks_timeline.json"
        if not timeline_file.exists():
            return []

        try:
            with open(timeline_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading timeline: {e}", exc_info=True)
            return []

    def get_system_status(self) -> Dict[str, Any]:
        """Get unified system status"""
        return {
            "timestamp": datetime.now().isoformat(),
            "syphon_available": self.syphon is not None,
            "asks_available": self.ask_restacker is not None,
            "agent_coordination_available": self.agent_coordinator is not None,
            "jarvis_superagent_available": self.jarvis_superagent is not None,
            "unified_ask_processor_available": self.unified_ask_processor is not None,
            "agents_tracked": len(self.agent_intelligence_states),
            "global_intelligence": {
                "actionable_items": len(self.global_intelligence_feed.actionable_items),
                "tasks": len(self.global_intelligence_feed.tasks),
                "decisions": len(self.global_intelligence_feed.decisions),
                "intelligence": len(self.global_intelligence_feed.intelligence),
                "ide_notifications": len(self.global_intelligence_feed.ide_notifications)
            },
            "running": self.running
        }


if __name__ == "__main__":
    print("\n" + "="*80)
    print("SYPHON + Agents/Subagents + VAs + @asks Unified System")
    print("="*80 + "\n")

    system = SYPHONAgentsAsksUnifiedSystem()

    # Get status
    status = system.get_system_status()
    print("System Status:")
    print(json.dumps(status, indent=2, default=str))

    # Start system
    print("\n🚀 Starting Unified System...")
    system.start()

    # Run for a bit
    import time
    time.sleep(5)

    # Get updated status
    status = system.get_system_status()
    print("\nUpdated Status:")
    print(f"  Agents Tracked: {status['agents_tracked']}")
    print(f"  Global Intelligence:")
    print(f"    Actionable Items: {status['global_intelligence']['actionable_items']}")
    print(f"    Tasks: {status['global_intelligence']['tasks']}")
    print(f"    Decisions: {status['global_intelligence']['decisions']}")
    print(f"    Intelligence: {status['global_intelligence']['intelligence']}")

    # Get timeline
    timeline = system.get_asks_timeline()
    print(f"\n  @asks Timeline: {len(timeline)} entries")

    # Stop system
    system.stop()

    print("\n✅ Unified System Test Complete")
    print("="*80 + "\n")
