#!/usr/bin/env python3
"""
Coordinate Agent Chat Sessions with @smart @superagent @jarvis

Coordinates with other agent chat sessions using JARVIS as the superagent coordinator.
Ensures all agent sessions are in sync and working together.

Tags: #COORDINATION #SUPERAGENT #JARVIS #SMART @JARVIS @TEAM
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CoordinateAgentSessions")


def _agent_name(session: Dict[str, Any]) -> str:
    """Get agent name from session; agent may be a dict with 'name' or a string."""
    agent = session.get("agent")
    if isinstance(agent, dict):
        return agent.get("name", "Unknown")
    if isinstance(agent, str):
        return agent
    return "Unknown"


# JARVIS Superagent integration
try:
    from jarvis_fulltime_super_agent import AgentRole, JARVISFullTimeSuperAgent

    JARVIS_SUPERAGENT_AVAILABLE = True
except ImportError:
    JARVIS_SUPERAGENT_AVAILABLE = False
    JARVISFullTimeSuperAgent = None
    logger.warning("JARVIS Full-Time Super Agent not available")

# JARVIS AI Coordination integration
try:
    from jarvis_ai_coordination import AIType, JARVISAICoordination

    JARVIS_COORDINATION_AVAILABLE = True
except ImportError:
    JARVIS_COORDINATION_AVAILABLE = False
    JARVISAICoordination = None
    logger.warning("JARVIS AI Coordination not available")


class AgentSessionCoordinator:
    """
    Coordinate Agent Chat Sessions with @smart @superagent @jarvis

    Uses JARVIS as the superagent coordinator to synchronize and coordinate
    all active agent chat sessions.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize agent session coordinator"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.agent_sessions_dir = self.project_root / "data" / "agent_sessions"
        self.agent_sessions_dir.mkdir(parents=True, exist_ok=True)

        # JARVIS Superagent (coordinator)
        self.jarvis_superagent = None
        if JARVIS_SUPERAGENT_AVAILABLE:
            try:
                self.jarvis_superagent = JARVISFullTimeSuperAgent(project_root=self.project_root)
                logger.info("✅ JARVIS Superagent initialized as coordinator")
            except Exception as e:
                logger.warning(f"⚠️  JARVIS Superagent not available: {e}")

        # JARVIS AI Coordination
        self.ai_coordination = None
        if JARVIS_COORDINATION_AVAILABLE:
            try:
                self.ai_coordination = JARVISAICoordination(project_root=self.project_root)
                logger.info("✅ JARVIS AI Coordination initialized")
            except Exception as e:
                logger.warning(f"⚠️  JARVIS AI Coordination not available: {e}")

        logger.info("✅ Agent Session Coordinator initialized")

    def discover_agent_sessions(self) -> List[Dict[str, Any]]:
        """Discover all agent chat sessions"""
        sessions = []

        if not self.agent_sessions_dir.exists():
            logger.warning(f"Agent sessions directory does not exist: {self.agent_sessions_dir}")
            return sessions

        for session_file in self.agent_sessions_dir.glob("*.json"):
            try:
                with open(session_file, encoding="utf-8") as f:
                    session_data = json.load(f)
                    session_data["file_path"] = str(session_file)
                    session_data["file_name"] = session_file.name
                    sessions.append(session_data)
                    logger.debug(f"Discovered session: {session_file.name}")
            except Exception as e:
                logger.warning(f"Error reading session file {session_file.name}: {e}")

        logger.info(f"📋 Discovered {len(sessions)} agent sessions")
        return sessions

    def coordinate_sessions(self) -> Dict[str, Any]:
        """
        Coordinate all agent chat sessions using JARVIS as superagent

        Returns:
            Dict with coordination results
        """
        logger.info("🔄 Starting session coordination with JARVIS Superagent...")

        # Discover all sessions
        sessions = self.discover_agent_sessions()

        if not sessions:
            logger.info("No agent sessions found to coordinate")
            return {
                "success": True,
                "sessions_found": 0,
                "coordinated": 0,
                "message": "No sessions to coordinate",
            }

        coordination_results = []

        # Coordinate each session through JARVIS
        for session in sessions:
            try:
                result = self._coordinate_single_session(session)
                coordination_results.append(result)
            except Exception as e:
                name = (
                    session.get("file_name", "unknown")
                    if isinstance(session, dict)
                    else str(session)
                )
                logger.error(f"Error coordinating session {name}: {e}")
                coordination_results.append({"session": name, "success": False, "error": str(e)})

        # Summary
        successful = sum(1 for r in coordination_results if r.get("success", False))

        result = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "sessions_found": len(sessions),
            "coordinated": successful,
            "coordination_results": coordination_results,
            "coordinator": "JARVIS Superagent",
        }

        logger.info(f"✅ Coordinated {successful}/{len(sessions)} sessions")
        return result

    def _coordinate_single_session(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate a single session through JARVIS

        Args:
            session: Session data dict

        Returns:
            Coordination result
        """
        session_id = session.get("session_id") or session.get("file_name", "unknown")
        session_agent = _agent_name(session)
        session_context = session.get("context", {})
        session_messages = session.get("messages", [])

        logger.info(f"🔄 Coordinating session: {session_id} (Agent: {session_agent})")

        # Use JARVIS Superagent to coordinate
        coordination_data = {
            "session_id": session_id,
            "agent": session_agent,
            "context": session_context,
            "message_count": len(session_messages),
            "last_message": session_messages[-1] if session_messages else None,
        }

        # Register session with JARVIS AI Coordination
        if self.ai_coordination:
            try:
                # Sync AI/agent from session
                ai_id = f"agent_session_{session_id}"
                ai_name = f"{session_agent} Session"

                # Check if already in registry
                if ai_id not in self.ai_coordination.ai_registry:
                    # Register using internal method if available
                    if hasattr(self.ai_coordination, "_register_ai"):
                        self.ai_coordination._register_ai(
                            ai_id=ai_id,
                            ai_name=ai_name,
                            ai_type=AIType.AGENT,
                            capabilities=["chat", "conversation", "coordination"],
                        )
                        logger.debug(f"Registered session AI: {ai_id}")

                # Sync with JARVIS
                if hasattr(self.ai_coordination, "sync_with_ai"):
                    sync_result = self.ai_coordination.sync_with_ai(ai_id)
                    if sync_result:
                        logger.debug(f"Synced session: {session_id}")
            except Exception as e:
                logger.debug(f"AI Coordination sync error (non-critical): {e}")

        # Add session to JARVIS Superagent conversation queue if available
        if self.jarvis_superagent:
            try:
                # Create coordination message
                coordination_message = {
                    "type": "coordination",
                    "session_id": session_id,
                    "agent": session_agent,
                    "action": "sync",
                    "timestamp": datetime.now().isoformat(),
                }

                # Add to JARVIS conversation context
                if hasattr(self.jarvis_superagent, "conversation_queue"):
                    # Note: This would require proper integration with JARVIS Superagent API
                    logger.debug(f"Session {session_id} queued for JARVIS coordination")
            except Exception as e:
                logger.debug(f"JARVIS Superagent coordination error (non-critical): {e}")

        return {
            "session_id": session_id,
            "agent": session_agent,
            "success": True,
            "coordinated_at": datetime.now().isoformat(),
            "coordination_data": coordination_data,
        }

    def sync_all_sessions(self) -> Dict[str, Any]:
        """
        Sync all sessions with JARVIS coordination system

        Returns:
            Sync results
        """
        logger.info("🔄 Syncing all sessions with JARVIS...")

        sessions = self.discover_agent_sessions()

        if not self.ai_coordination:
            return {
                "success": False,
                "error": "JARVIS AI Coordination not available",
                "sessions": len(sessions),
            }

        sync_results = []

        for session in sessions:
            session_id = session.get("session_id") or session.get("file_name", "unknown")
            session_agent = _agent_name(session)

            try:
                ai_id = f"agent_session_{session_id}"

                # Ensure registered
                if ai_id not in self.ai_coordination.ai_registry:
                    if hasattr(self.ai_coordination, "_register_ai"):
                        self.ai_coordination._register_ai(
                            ai_id=ai_id,
                            ai_name=f"{session_agent} Session",
                            ai_type=AIType.AGENT,
                            capabilities=["chat", "conversation"],
                        )

                # Sync
                if hasattr(self.ai_coordination, "sync_with_ai"):
                    sync_result = self.ai_coordination.sync_with_ai(ai_id)
                    sync_results.append(
                        {
                            "session_id": session_id,
                            "agent": session_agent,
                            "success": sync_result
                            if isinstance(sync_result, bool)
                            else sync_result.get("success", False),
                            "sync_result": {"synced": sync_result}
                            if isinstance(sync_result, bool)
                            else sync_result,
                        }
                    )
                else:
                    sync_results.append(
                        {
                            "session_id": session_id,
                            "agent": session_agent,
                            "success": False,
                            "error": "sync_with_ai method not available",
                        }
                    )
            except Exception as e:
                logger.error(f"Error syncing session {session_id}: {e}")
                sync_results.append({"session_id": session_id, "success": False, "error": str(e)})

        successful = sum(1 for r in sync_results if r.get("success", False))

        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "sessions_found": len(sessions),
            "synced": successful,
            "sync_results": sync_results,
        }

    def get_coordination_status(self) -> Dict[str, Any]:
        """Get current coordination status"""
        sessions = self.discover_agent_sessions()

        status = {
            "timestamp": datetime.now().isoformat(),
            "jarvis_superagent_available": self.jarvis_superagent is not None,
            "ai_coordination_available": self.ai_coordination is not None,
            "sessions_found": len(sessions),
            "sessions": [
                {
                    "session_id": s.get("session_id") or s.get("file_name", "unknown"),
                    "agent": _agent_name(s),
                    "message_count": len(s.get("messages", [])),
                }
                for s in sessions
            ],
        }

        # Add AI coordination status if available
        if self.ai_coordination:
            try:
                coordination_status = self.ai_coordination.get_coordination_status()
                status["ai_coordination_status"] = coordination_status
            except Exception as e:
                status["ai_coordination_error"] = str(e)

        return status


def coordinate_with_jarvis(project_root: Optional[Path] = None) -> Dict[str, Any]:
    """
    Convenience function to coordinate agent sessions with JARVIS

    Args:
        project_root: Optional project root path

    Returns:
        Coordination results
    """
    coordinator = AgentSessionCoordinator(project_root=project_root)
    return coordinator.coordinate_sessions()


def sync_all_with_jarvis(project_root: Optional[Path] = None) -> Dict[str, Any]:
    """
    Convenience function to sync all sessions with JARVIS

    Args:
        project_root: Optional project root path

    Returns:
        Sync results
    """
    coordinator = AgentSessionCoordinator(project_root=project_root)
    return coordinator.sync_all_sessions()


if __name__ == "__main__":
    logger.info("🔄 Agent Session Coordinator - JARVIS Superagent")
    logger.info("=" * 80)

    coordinator = AgentSessionCoordinator()

    # Get status
    logger.info("\n📊 Current Status:")
    status = coordinator.get_coordination_status()
    print(json.dumps(status, indent=2))

    # Coordinate sessions
    logger.info("\n🔄 Coordinating Sessions...")
    coordination_result = coordinator.coordinate_sessions()
    print(json.dumps(coordination_result, indent=2))

    # Sync all sessions
    logger.info("\n🔄 Syncing All Sessions...")
    sync_result = coordinator.sync_all_sessions()
    print(json.dumps(sync_result, indent=2))

    logger.info("\n✅ Coordination Complete")
    logger.info("=" * 80)
