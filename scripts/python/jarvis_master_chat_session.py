#!/usr/bin/env python3
"""
JARVIS Master Chat Session - Unified Agent Consolidation

Collates and condenses all agents into a single, permanently pinned master JARVIS chat session.
All agent interactions, coordination, and collaboration flow through this unified interface.

Tags: #JARVIS #MASTER #CHAT #COLLATE #CONDENSE #PINNED #CTO #SUPERAGENT
@JARVIS @TEAM @COOR @COLAB @CTO
"""

from __future__ import annotations

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
import logging

# Add project root to sys.path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISMasterChat")

# Import agent coordination systems
try:
    from coordinate_agent_sessions import AgentSessionCoordinator
    COORDINATION_AVAILABLE = True
except ImportError:
    COORDINATION_AVAILABLE = False
    logger.warning("Agent session coordination not available")

try:
    from jarvis_va_chat_coordinator import VAChatCoordinator
    VA_COORDINATION_AVAILABLE = True
except ImportError:
    VA_COORDINATION_AVAILABLE = False
    logger.warning("VA chat coordination not available")


@dataclass
class AgentMessage:
    """Message from an agent in the master chat session"""
    agent_id: str
    agent_name: str
    message: str
    timestamp: str
    message_type: str = "chat"  # chat, coordination, collaboration, decision
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MasterChatSession:
    """Master JARVIS chat session consolidating all agents"""
    session_id: str = "jarvis_master_chat"
    session_name: str = "JARVIS Master Chat - All Agents"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_activity: str = field(default_factory=lambda: datetime.now().isoformat())
    pinned: bool = True
    permanent: bool = True
    consolidated_agents: List[str] = field(default_factory=list)
    messages: List[AgentMessage] = field(default_factory=list)
    agent_contexts: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    coordination_data: Dict[str, Any] = field(default_factory=dict)
    collaboration_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "session_id": self.session_id,
            "session_name": self.session_name,
            "created_at": self.created_at,
            "last_activity": self.last_activity,
            "pinned": self.pinned,
            "permanent": self.permanent,
            "consolidated_agents": self.consolidated_agents,
            "messages": [
                {
                    "agent_id": msg.agent_id,
                    "agent_name": msg.agent_name,
                    "message": msg.message,
                    "timestamp": msg.timestamp,
                    "message_type": msg.message_type,
                    "metadata": msg.metadata
                }
                for msg in self.messages
            ],
            "agent_contexts": self.agent_contexts,
            "coordination_data": self.coordination_data,
            "collaboration_data": self.collaboration_data
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MasterChatSession:
        """Create from dictionary"""
        messages = [
            AgentMessage(
                agent_id=msg["agent_id"],
                agent_name=msg["agent_name"],
                message=msg["message"],
                timestamp=msg["timestamp"],
                message_type=msg.get("message_type", "chat"),
                metadata=msg.get("metadata", {})
            )
            for msg in data.get("messages", [])
        ]

        return cls(
            session_id=data.get("session_id", "jarvis_master_chat"),
            session_name=data.get("session_name", "JARVIS Master Chat - All Agents"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            last_activity=data.get("last_activity", datetime.now().isoformat()),
            pinned=data.get("pinned", True),
            permanent=data.get("permanent", True),
            consolidated_agents=data.get("consolidated_agents", []),
            messages=messages,
            agent_contexts=data.get("agent_contexts", {}),
            coordination_data=data.get("coordination_data", {}),
            collaboration_data=data.get("collaboration_data", {})
        )


class JARVISMasterChatSession:
    """
    Master JARVIS Chat Session Manager

    Consolidates all agents (C-3PO, R2-D2, K-2SO, IMVA, ACVA, etc.) into a single
    unified chat session that is permanently pinned and always available.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize master chat session manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "jarvis_master_chat"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.session_file = self.data_dir / "master_session.json"
        self.config_file = self.data_dir / "master_config.json"

        # Initialize coordination systems
        self.session_coordinator = None
        if COORDINATION_AVAILABLE:
            try:
                self.session_coordinator = AgentSessionCoordinator(project_root=self.project_root)
                logger.info("✅ Agent session coordinator initialized")
            except Exception as e:
                logger.warning(f"⚠️  Agent session coordinator not available: {e}")

        self.va_coordinator = None
        if VA_COORDINATION_AVAILABLE:
            try:
                self.va_coordinator = VAChatCoordinator(project_root=self.project_root)
                logger.info("✅ VA chat coordinator initialized")
            except Exception as e:
                logger.warning(f"⚠️  VA chat coordinator not available: {e}")

        # Load or create master session
        self.master_session = self._load_or_create_session()

        logger.info("✅ JARVIS Master Chat Session initialized")
        logger.info(f"   Session ID: {self.master_session.session_id}")
        logger.info(f"   Pinned: {self.master_session.pinned}")
        logger.info(f"   Permanent: {self.master_session.permanent}")

    def _load_or_create_session(self) -> MasterChatSession:
        """Load existing session or create new one"""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    session = MasterChatSession.from_dict(data)
                    logger.info(f"✅ Loaded existing master session: {session.session_id}")
                    return session
            except Exception as e:
                logger.warning(f"⚠️  Error loading session, creating new: {e}")

        # Create new master session
        session = MasterChatSession()
        self._save_session(session)
        logger.info("✅ Created new master session")
        return session

    def _save_session(self, session: Optional[MasterChatSession] = None):
        """Save master session to disk"""
        if session is None:
            session = self.master_session

        try:
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
            logger.debug(f"💾 Saved master session: {session.session_id}")
        except Exception as e:
            logger.error(f"❌ Error saving master session: {e}")

    def consolidate_all_agents(self) -> Dict[str, Any]:
        """
        Collate and condense all agents into the master session

        Discovers all agent sessions, coordinates them, and consolidates their
        context into the master JARVIS chat session. All agent interactions
        are collapsed into this single unified interface.
        """
        logger.info("🔄 Collating and condensing all agents into master session...")

        consolidated_agents = []
        agent_contexts = {}
        coordination_data = {}
        collaboration_data = {}
        condensed_messages = []

        # Load known droid agents from config
        droids_config = self.project_root / "config" / "helpdesk" / "droids.json"
        known_droids = []
        if droids_config.exists():
            try:
                with open(droids_config, 'r', encoding='utf-8') as f:
                    droids_data = json.load(f)
                    known_droids = [
                        {
                            "agent_id": droid_id,
                            "agent_name": droid_data.get("name", droid_id),
                            "type": "droid",
                            "capabilities": droid_data.get("capabilities", []),
                            "active": droid_data.get("active", False)
                        }
                        for droid_id, droid_data in droids_data.items()
                    ]
                logger.info(f"📋 Loaded {len(known_droids)} known droid agents from config")
            except Exception as e:
                logger.warning(f"⚠️  Error loading droids config: {e}")

        # Add known droids to consolidated list
        for droid in known_droids:
            if droid.get("active", False):
                agent_name = droid["agent_name"]
                if agent_name not in consolidated_agents:
                    consolidated_agents.append(agent_name)
                agent_contexts[agent_name] = {
                    "agent_id": droid["agent_id"],
                    "type": "droid",
                    "capabilities": droid.get("capabilities", []),
                    "active": True
                }

        # Discover and consolidate agent sessions
        if self.session_coordinator:
            try:
                sessions = self.session_coordinator.discover_agent_sessions()
                logger.info(f"📋 Discovered {len(sessions)} agent sessions")

                for session in sessions:
                    # Handle both dict and string agent formats
                    agent_data = session.get('agent', {})
                    if isinstance(agent_data, dict):
                        agent_name = agent_data.get('name', 'Unknown')
                    elif isinstance(agent_data, str):
                        agent_name = agent_data
                    else:
                        agent_name = 'Unknown'
                    session_id = session.get('session_id') or session.get('file_name', 'unknown')

                    if agent_name not in consolidated_agents:
                        consolidated_agents.append(agent_name)

                    # Extract and condense agent messages
                    session_messages = session.get('messages', [])
                    if session_messages:
                        # Condense: take last 5 messages as summary
                        recent_messages = session_messages[-5:] if len(session_messages) > 5 else session_messages
                        condensed_summary = self._condense_messages(agent_name, recent_messages)
                        if condensed_summary:
                            condensed_messages.append(condensed_summary)

                    # Extract agent context
                    if agent_name not in agent_contexts:
                        agent_contexts[agent_name] = {}

                    agent_contexts[agent_name].update({
                        "session_id": session_id,
                        "context": session.get('context', {}),
                        "message_count": len(session_messages),
                        "last_activity": session.get('last_activity', session.get('created_at', 'unknown'))
                    })

                # Coordinate sessions
                coordination_result = self.session_coordinator.coordinate_sessions()
                coordination_data = {
                    "timestamp": datetime.now().isoformat(),
                    "sessions_found": coordination_result.get("sessions_found", 0),
                    "coordinated": coordination_result.get("coordinated", 0),
                    "coordination_results": coordination_result.get("coordination_results", [])
                }
            except Exception as e:
                logger.error(f"❌ Error consolidating agent sessions: {e}")

        # Consolidate VA agents
        if self.va_coordinator:
            try:
                # VA agents are already registered in the coordinator
                va_agents = ["imva", "acva", "jarvis_va"]
                for agent_id in va_agents:
                    agent_name = f"VA-{agent_id.upper()}"
                    if agent_name not in consolidated_agents:
                        consolidated_agents.append(agent_name)

                    # Get agent capabilities safely
                    capabilities = []
                    if hasattr(self.va_coordinator, 'colab') and hasattr(self.va_coordinator.colab, 'agents'):
                        agent = self.va_coordinator.colab.agents.get(agent_id)
                        if agent and hasattr(agent, 'capabilities'):
                            capabilities = agent.capabilities
                        elif agent and isinstance(agent, dict):
                            capabilities = agent.get("capabilities", [])

                    agent_contexts[agent_name] = {
                        "agent_id": agent_id,
                        "type": "virtual_assistant",
                        "capabilities": capabilities
                    }
            except Exception as e:
                logger.warning(f"⚠️  Error consolidating VA agents: {e}")

        # Add JARVIS as master agent
        if "JARVIS" not in consolidated_agents:
            consolidated_agents.insert(0, "JARVIS (CTO Superagent)")
            agent_contexts["JARVIS (CTO Superagent)"] = {
                "agent_id": "jarvis",
                "type": "superagent",
                "role": "CTO Superagent",
                "capabilities": ["orchestration", "coordination", "escalation", "decision_making", "workflow_management"]
            }

        # Update master session
        self.master_session.consolidated_agents = consolidated_agents
        self.master_session.agent_contexts = agent_contexts
        self.master_session.coordination_data = coordination_data
        self.master_session.collaboration_data = {
            **collaboration_data,
            "condensed_messages": condensed_messages,
            "condensed_at": datetime.now().isoformat()
        }
        self.master_session.last_activity = datetime.now().isoformat()

        # Add condensed messages to master session
        for msg in condensed_messages:
            self.master_session.messages.append(msg)

        # Add consolidation message
        self.add_message(
            agent_id="jarvis",
            agent_name="JARVIS (CTO Superagent)",
            message=f"✅ Collated and condensed {len(consolidated_agents)} agents into master session. All agent interactions now flow through this unified interface.",
            message_type="coordination",
            metadata={
                "consolidated_count": len(consolidated_agents),
                "agents": consolidated_agents,
                "condensed_messages": len(condensed_messages),
                "permanently_pinned": True
            }
        )

        self._save_session()

        result = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "consolidated_agents": consolidated_agents,
            "agent_count": len(consolidated_agents),
            "condensed_messages": len(condensed_messages),
            "coordination_data": coordination_data,
            "permanently_pinned": True
        }

        logger.info(f"✅ Collated and condensed {len(consolidated_agents)} agents into master session")
        logger.info(f"   Condensed {len(condensed_messages)} message summaries")
        return result

    def _condense_messages(self, agent_name: str, messages: List[Dict[str, Any]]) -> Optional[AgentMessage]:
        """
        Condense multiple messages from an agent into a single summary message

        Args:
            agent_name: Name of the agent
            messages: List of message dictionaries

        Returns:
            Condensed AgentMessage or None
        """
        if not messages:
            return None

        # Extract key information from messages
        message_contents = []
        for msg in messages:
            content = msg.get('content', '') or msg.get('message', '')
            if content:
                # Truncate long messages
                if len(content) > 200:
                    content = content[:200] + "..."
                message_contents.append(content)

        if not message_contents:
            return None

        # Create condensed summary
        if len(message_contents) == 1:
            condensed_text = f"[{agent_name}] {message_contents[0]}"
        else:
            condensed_text = f"[{agent_name}] Recent activity ({len(messages)} messages): " + " | ".join(message_contents[:3])

        return AgentMessage(
            agent_id=agent_name.lower().replace(" ", "_").replace("-", "_"),
            agent_name=agent_name,
            message=condensed_text,
            timestamp=datetime.now().isoformat(),
            message_type="condensed",
            metadata={
                "original_message_count": len(messages),
                "condensed_at": datetime.now().isoformat()
            }
        )

    def add_message(
        self,
        agent_id: str,
        agent_name: str,
        message: str,
        message_type: str = "chat",
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentMessage:
        """
        Add a message to the master chat session

        Args:
            agent_id: ID of the agent sending the message
            agent_name: Display name of the agent
            message: Message content
            message_type: Type of message (chat, coordination, collaboration, decision)
            metadata: Optional metadata

        Returns:
            Created AgentMessage
        """
        agent_message = AgentMessage(
            agent_id=agent_id,
            agent_name=agent_name,
            message=message,
            timestamp=datetime.now().isoformat(),
            message_type=message_type,
            metadata=metadata or {}
        )

        self.master_session.messages.append(agent_message)
        self.master_session.last_activity = datetime.now().isoformat()

        # Keep last 1000 messages (prevent unbounded growth)
        if len(self.master_session.messages) > 1000:
            self.master_session.messages = self.master_session.messages[-1000:]

        self._save_session()

        logger.debug(f"💬 Message added from {agent_name}: {message[:50]}...")
        return agent_message

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of master chat session"""
        return {
            "session_id": self.master_session.session_id,
            "session_name": self.master_session.session_name,
            "pinned": self.master_session.pinned,
            "permanent": self.master_session.permanent,
            "created_at": self.master_session.created_at,
            "last_activity": self.master_session.last_activity,
            "consolidated_agents": self.master_session.consolidated_agents,
            "agent_count": len(self.master_session.consolidated_agents),
            "message_count": len(self.master_session.messages),
            "recent_messages": [
                {
                    "agent": msg.agent_name,
                    "message": msg.message[:100] + "..." if len(msg.message) > 100 else msg.message,
                    "timestamp": msg.timestamp,
                    "type": msg.message_type
                }
                for msg in self.master_session.messages[-10:]
            ]
        }

    def ensure_pinned(self) -> bool:
        """Ensure master session is permanently pinned"""
        if not self.master_session.pinned:
            self.master_session.pinned = True
            self._save_session()
            logger.info("📌 Master session pinned")

        if not self.master_session.permanent:
            self.master_session.permanent = True
            self._save_session()
            logger.info("🔒 Master session set as permanent")

        return True

    def get_cursor_config(self) -> Dict[str, Any]:
        """Get Cursor IDE configuration for pinned master session"""
        return {
            "cursor.chat.pinnedSessions": [
                {
                    "sessionId": self.master_session.session_id,
                    "sessionName": self.master_session.session_name,
                    "pinned": True,
                    "permanent": True,
                    "autoOpen": True,
                    "model": "ULTRON",
                    "description": "Master JARVIS chat session consolidating all agents"
                }
            ],
            "cursor.chat.defaultSession": self.master_session.session_id,
            "cursor.chat.alwaysOpenPinned": True
        }


def main():
    try:
        """Main execution - Initialize and consolidate master chat session"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Master Chat Session Manager")
        parser.add_argument("--consolidate", action="store_true", help="Consolidate all agents into master session")
        parser.add_argument("--summary", action="store_true", help="Show session summary")
        parser.add_argument("--pin", action="store_true", help="Ensure session is pinned")
        parser.add_argument("--config", action="store_true", help="Show Cursor IDE configuration")

        args = parser.parse_args()

        print("\n" + "=" * 80)
        print("🤖 JARVIS MASTER CHAT SESSION - Unified Agent Consolidation")
        print("=" * 80 + "\n")

        manager = JARVISMasterChatSession()

        if args.consolidate:
            print("🔄 Consolidating all agents...")
            result = manager.consolidate_all_agents()
            print(f"✅ Consolidated {result['agent_count']} agents")
            print(f"   Agents: {', '.join(result['consolidated_agents'])}")
            print()

        if args.pin:
            print("📌 Ensuring session is pinned...")
            manager.ensure_pinned()
            print("✅ Session is permanently pinned")
            print()

        if args.summary:
            print("📋 Master Session Summary:")
            print("-" * 80)
            summary = manager.get_session_summary()
            print(json.dumps(summary, indent=2))
            print()

        if args.config:
            print("⚙️  Cursor IDE Configuration:")
            print("-" * 80)
            config = manager.get_cursor_config()
            print(json.dumps(config, indent=2))
            print()

        if not any([args.consolidate, args.summary, args.pin, args.config]):
            # Default: consolidate and pin
            print("🔄 Consolidating all agents...")
            result = manager.consolidate_all_agents()
            print(f"✅ Consolidated {result['agent_count']} agents")
            print()

            print("📌 Ensuring session is pinned...")
            manager.ensure_pinned()
            print("✅ Session is permanently pinned")
            print()

            print("📋 Session Summary:")
            print("-" * 80)
            summary = manager.get_session_summary()
            print(f"Session ID: {summary['session_id']}")
            print(f"Session Name: {summary['session_name']}")
            print(f"Pinned: {summary['pinned']}")
            print(f"Permanent: {summary['permanent']}")
            print(f"Agents: {summary['agent_count']}")
            print(f"Messages: {summary['message_count']}")
            print()

        print("=" * 80)
        print("✅ JARVIS Master Chat Session Ready")
        print("=" * 80 + "\n")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()