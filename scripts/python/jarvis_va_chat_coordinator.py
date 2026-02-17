#!/usr/bin/env python3
"""
JARVIS VA Agent Chat Session Coordinator - @COOR @COLAB
Coordinates and assists VA agents in chat sessions with JARVIS oversight

@JARVIS @TEAM @COOR @COLAB @VA #COLLABORATION #AGENTS #CHAT
"""

import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cfservices.services.jarvis_core.agent_collaboration import (
    AgentCollaborationSystem,
    AgentRole
)

logger = logging.getLogger(__name__)


class VAChatCoordinator:
    """
    Coordinates VA agents in chat sessions with JARVIS oversight.
    Assists agents in collaborating on chat-based tasks.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize VA chat coordinator"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.colab = AgentCollaborationSystem(project_root=project_root, jarvis_oversight=True)

        # Register VA agents
        self._register_va_agents()

        logger.info("✅ VA Chat Coordinator initialized")

    def _register_va_agents(self):
        """Register VA agents for chat collaboration"""
        # Register IMVA (Iron Man VA)
        self.colab.register_agent(
            agent_id="imva",
            name="IMVA (Iron Man VA)",
            role=AgentRole.SUBAGENT,
            capabilities=["desktop_companion", "combat", "system_monitoring", "voice_acting"]
        )

        # Register ACVA (Armoury Crate VA)
        self.colab.register_agent(
            agent_id="acva",
            name="ACVA (Armoury Crate VA)",
            role=AgentRole.SUBAGENT,
            capabilities=["system_control", "lighting", "hardware_management"]
        )

        # Register JARVIS VA
        self.colab.register_agent(
            agent_id="jarvis_va",
            name="JARVIS VA",
            role=AgentRole.PRIMARY,
            capabilities=["orchestration", "coordination", "intelligence", "decision_making"]
        )

        logger.info("✅ VA agents registered for chat collaboration")

    def coordinate_chat_session(
        self,
        chat_topic: str,
        participant_agents: Optional[List[str]] = None,
        user_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Coordinate a chat session between VA agents

        Args:
            chat_topic: Topic of the chat session
            participant_agents: List of agent IDs to participate (defaults to all VAs)
            user_message: Optional user message to discuss

        Returns:
            Chat session coordination result
        """
        if participant_agents is None:
            participant_agents = ["imva", "acva", "jarvis_va"]

        # Start collaboration session
        session = self.colab.start_collaboration(
            task_description=f"Chat Session: {chat_topic}",
            agent_ids=participant_agents,
            jarvis_oversight=True,
            oversight_level="standard"
        )

        logger.info(f"💬 Chat session started: {chat_topic}")
        logger.info(f"   Participants: {', '.join([self.colab.agents[aid].name for aid in participant_agents])}")

        # If user message provided, distribute to agents
        if user_message:
            self._distribute_user_message(session.session_id, user_message, participant_agents)

        return {
            "session_id": session.session_id,
            "topic": chat_topic,
            "participants": [self.colab.agents[aid].name for aid in participant_agents],
            "status": "active"
        }

    def _distribute_user_message(
        self,
        session_id: str,
        user_message: str,
        participant_agents: List[str]
    ):
        """Distribute user message to all participating agents"""
        # JARVIS receives message first (coordinator)
        self.colab.agent_communicate(
            session_id=session_id,
            from_agent_id="jarvis",
            to_agent_id="jarvis_va",
            message=f"User message received: {user_message}",
            data={"user_message": user_message}
        )

        # Distribute to other agents
        for agent_id in participant_agents:
            if agent_id != "jarvis_va":
                self.colab.agent_communicate(
                    session_id=session_id,
                    from_agent_id="jarvis_va",
                    to_agent_id=agent_id,
                    message=f"User message for discussion: {user_message}",
                    data={"user_message": user_message, "topic": "user_input"}
                )

    def agent_response(
        self,
        session_id: str,
        agent_id: str,
        response: str,
        data: Optional[Dict[str, Any]] = None
    ):
        """
        Agent provides response in chat session

        Args:
            session_id: Chat session ID
            agent_id: Agent providing response
            response: Agent's response message
            data: Optional response data
        """
        # Agent responds to JARVIS (coordinator)
        self.colab.agent_communicate(
            session_id=session_id,
            from_agent_id=agent_id,
            to_agent_id="jarvis",
            message=response,
            data=data or {}
        )

        logger.info(f"💬 {self.colab.agents[agent_id].name}: {response}")

    def get_chat_log(self, session_id: str) -> List[Dict[str, Any]]:
        """Get chat log for session"""
        if session_id not in self.colab.active_sessions:
            return []

        session = self.colab.active_sessions[session_id]
        return session.communication_log

    def complete_chat_session(
        self,
        session_id: str,
        summary: str,
        success: bool = True
    ):
        """Complete chat session with summary"""
        final_result = {
            "summary": summary,
            "success": success,
            "timestamp": time.time()
        }

        self.colab.complete_collaboration(
            session_id=session_id,
            final_result=final_result,
            success=success
        )

        logger.info(f"✅ Chat session completed: {session_id}")

    def assist_agents(self, session_id: str, assistance_type: str = "general") -> Dict[str, Any]:
        """
        JARVIS assists agents in chat session

        Args:
            session_id: Chat session ID
            assistance_type: Type of assistance (general, coordination, decision, technical)

        Returns:
            Assistance provided
        """
        if session_id not in self.colab.active_sessions:
            return {"error": "Session not found"}

        session = self.colab.active_sessions[session_id]

        assistance_messages = {
            "general": "JARVIS providing general assistance to coordinate discussion",
            "coordination": "JARVIS coordinating agent communication and task distribution",
            "decision": "JARVIS providing decision-making assistance based on agent inputs",
            "technical": "JARVIS providing technical guidance and expertise"
        }

        message = assistance_messages.get(assistance_type, assistance_messages["general"])

        # JARVIS communicates assistance to all agents
        for agent_id in session.task.assigned_agents:
            self.colab.agent_communicate(
                session_id=session_id,
                from_agent_id="jarvis",
                to_agent_id=agent_id,
                message=message,
                data={"assistance_type": assistance_type}
            )

        logger.info(f"🤝 JARVIS assistance provided: {assistance_type}")

        return {
            "assistance_type": assistance_type,
            "message": message,
            "recipients": session.task.assigned_agents
        }

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get chat session status"""
        status = self.colab.get_session_status(session_id)

        if "error" in status:
            return status

        # Add chat-specific info
        chat_log = self.get_chat_log(session_id)
        status["message_count"] = len(chat_log)
        status["recent_messages"] = chat_log[-5:] if chat_log else []

        return status


def main():
    """Demo VA chat coordination"""
    print("=" * 70)
    print("💬 JARVIS VA Chat Session Coordinator - @COOR @COLAB")
    print("=" * 70)
    print()

    coordinator = VAChatCoordinator()

    # Start chat session
    print("📝 Starting Chat Session...")
    print("-" * 70)

    session = coordinator.coordinate_chat_session(
        chat_topic="System Performance Discussion",
        participant_agents=["imva", "acva", "jarvis_va"],
        user_message="How is the system performing today?"
    )

    print(f"✅ Session ID: {session['session_id']}")
    print(f"   Topic: {session['topic']}")
    print(f"   Participants: {', '.join(session['participants'])}")
    print()

    # Simulate agent responses
    print("💬 Agent Responses:")
    print("-" * 70)

    time.sleep(0.5)
    coordinator.agent_response(
        session_id=session["session_id"],
        agent_id="imva",
        response="System performance is optimal. All systems nominal.",
        data={"cpu": 45, "ram": 60, "status": "healthy"}
    )

    time.sleep(0.5)
    coordinator.agent_response(
        session_id=session["session_id"],
        agent_id="acva",
        response="Hardware monitoring shows all components within normal parameters.",
        data={"temperature": 65, "fans": "normal", "status": "stable"}
    )

    time.sleep(0.5)
    coordinator.agent_response(
        session_id=session["session_id"],
        agent_id="jarvis_va",
        response="Based on both reports, system is performing excellently. No action needed.",
        data={"recommendation": "continue_monitoring"}
    )

    print()

    # JARVIS assistance
    print("🤝 JARVIS Assistance:")
    print("-" * 70)

    assistance = coordinator.assist_agents(
        session_id=session["session_id"],
        assistance_type="coordination"
    )

    print(f"   Type: {assistance['assistance_type']}")
    print(f"   Message: {assistance['message']}")
    print()

    # Get chat log
    print("📋 Chat Log:")
    print("-" * 70)

    chat_log = coordinator.get_chat_log(session["session_id"])
    for i, entry in enumerate(chat_log[-10:], 1):
        from_agent = coordinator.colab.agents[entry["from"]].name
        to_agent = coordinator.colab.agents[entry["to"]].name
        print(f"  {i}. {from_agent} → {to_agent}: {entry['message']}")

    print()

    # Complete session
    print("🏁 Completing Chat Session...")
    print("-" * 70)

    coordinator.complete_chat_session(
        session_id=session["session_id"],
        summary="All agents agreed system performance is optimal. No issues detected.",
        success=True
    )

    print()
    print("=" * 70)
    print("✅ Chat Session Coordination Complete!")
    print("=" * 70)

    # Show oversight report
    print()
    print("👁️  JARVIS Oversight Summary:")
    print("-" * 70)

    report = coordinator.colab.get_oversight_report(session_id=session["session_id"])
    print(f"   Total Oversight Actions: {report['total_oversight_actions']}")
    print(f"   Sessions Monitored: {report['sessions_monitored']}")
    print()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)


    main()