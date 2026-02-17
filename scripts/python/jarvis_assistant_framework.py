#!/usr/bin/env python3
"""
JARVIS Assistant Framework

Recognizes that AI-to-AI delegation is essentially an "assistant" framework.
Each AI agent is an assistant to others, and the system is a network of assistants.

Tags: #ASSISTANT #AI2AI #DELEGATION #FRAMEWORK @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVISAssistantFramework")
except ImportError:
    try:
        from lumina_logger import get_logger
        logger = get_logger("JARVISAssistantFramework")
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("JARVISAssistantFramework")

# Import AI Identity and Delegation
try:
    from jarvis_ai_identity_self_awareness import DelegationManager, AIIdentity, AgentRole
    IDENTITY_AVAILABLE = True
except ImportError:
    IDENTITY_AVAILABLE = False
    logger.warning("AI Identity system not available")

# Import AI-to-AI Message Bus
try:
    from jarvis_ai_to_ai_message_bus import JARVISAIToAIMessageBus
    MESSAGE_BUS_AVAILABLE = True
except ImportError:
    MESSAGE_BUS_AVAILABLE = False
    logger.warning("AI-to-AI Message Bus not available")


class AssistantFramework:
    """
    Assistant Framework - Recognizing that AI-to-AI is essentially assistants helping assistants

    Insight: "They called it an 'assistant,' but isn't that almost the same thing? AI2AI - Same thing we have been working on..."
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "assistant_framework"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Core insight
        self.insight = {
            "realization": "AI-to-AI delegation is essentially an assistant framework",
            "pattern": "Each AI agent is an assistant to others",
            "network": "The system is a network of assistants (AI2AI)",
            "connection": "Same thing we have been working on - just called 'assistant'"
        }

        # Initialize components
        self.delegation_manager = None
        self.message_bus = None

        if IDENTITY_AVAILABLE:
            try:
                self.delegation_manager = DelegationManager(project_root)
                logger.info("✅ Assistant Framework: Delegation Manager initialized")
            except Exception as e:
                logger.debug(f"Delegation Manager not available: {e}")

        if MESSAGE_BUS_AVAILABLE:
            try:
                self.message_bus = JARVISAIToAIMessageBus(project_root)
                logger.info("✅ Assistant Framework: AI-to-AI Message Bus initialized")
            except Exception as e:
                logger.debug(f"Message Bus not available: {e}")

    def recognize_assistant_pattern(self) -> Dict[str, Any]:
        """Recognize and document the assistant pattern in our system"""
        pattern = {
            "insight": self.insight,
            "assistant_network": {
                "primary_assistant": "JARVIS (Primary Assistant)",
                "specialist_assistants": [],
                "delegation_chain": "Primary → Specialist Assistants",
                "communication": "AI-to-AI Message Bus (Assistant-to-Assistant)"
            },
            "assistant_capabilities": {
                "task_assistance": "Assist with task execution",
                "delegation_assistance": "Assist by delegating to specialists",
                "coordination_assistance": "Assist in coordinating multiple assistants",
                "knowledge_assistance": "Assist with knowledge sharing"
            },
            "recognized_at": datetime.now().isoformat()
        }

        # Get assistant network from delegation manager
        if self.delegation_manager:
            breakdown = self.delegation_manager.get_breakdown()
            pattern["assistant_network"]["assistants"] = [
                {
                    "name": agent.get("who_i_am", "Unknown"),
                    "role": agent.get("my_role", "unknown"),
                    "tasks": len(agent.get("what_im_doing", [])),
                    "delegated": len(agent.get("what_ive_delegated", []))
                }
                for agent in breakdown.get("all_agents", [])
            ]
            pattern["assistant_network"]["total_assistants"] = breakdown.get("total_agents", 0)

        return pattern

    def create_assistant(self, assistant_name: str, assistant_type: str = "specialist", capabilities: List[str] = None) -> Dict[str, Any]:
        """Create a new assistant in the framework"""
        if not self.delegation_manager:
            return {"error": "Delegation Manager not available"}

        # Map assistant types to agent roles
        role_map = {
            "specialist": AgentRole.SPECIALIST,
            "coordinator": AgentRole.COORDINATOR,
            "delegate": AgentRole.DELEGATE
        }

        role = role_map.get(assistant_type, AgentRole.DELEGATE)

        assistant_agent = self.delegation_manager.create_delegate(
            agent_name=assistant_name,
            role=role,
            capabilities=capabilities or []
        )

        assistant_info = {
            "assistant_id": assistant_agent.agent_id,
            "assistant_name": assistant_agent.agent_name,
            "assistant_type": assistant_type,
            "role": role.value,
            "capabilities": assistant_agent.identity.get("my_capabilities", []),
            "created_at": datetime.now().isoformat(),
            "insight": "This assistant is part of the AI2AI assistant network"
        }

        logger.info(f"🤖 Created assistant: {assistant_name} ({assistant_type})")

        return assistant_info

    def assign_to_assistant(self, task: Dict[str, Any], assistant_name: str = None) -> Dict[str, Any]:
        """Assign task to an assistant"""
        if not self.delegation_manager:
            return {"error": "Delegation Manager not available"}

        # Find assistant if name provided
        target_agent = None
        if assistant_name:
            for agent in self.delegation_manager.agents.values():
                if agent.agent_name == assistant_name:
                    target_agent = agent
                    break

        # Assign or delegate
        if target_agent:
            result = self.delegation_manager.delegate_task(task, to_agent=target_agent)
        else:
            result = self.delegation_manager.assign_task(task)

        result["assistant_framework"] = True
        result["insight"] = "Task assigned through assistant framework (AI2AI)"

        return result

    def get_assistant_network(self) -> Dict[str, Any]:
        """Get the complete assistant network"""
        network = {
            "framework_insight": self.insight,
            "assistants": [],
            "communication": {
                "message_bus_available": self.message_bus is not None,
                "delegation_available": self.delegation_manager is not None
            },
            "networked_at": datetime.now().isoformat()
        }

        if self.delegation_manager:
            breakdown = self.delegation_manager.get_breakdown()
            network["assistants"] = breakdown.get("all_agents", [])
            network["total_assistants"] = breakdown.get("total_agents", 0)
            network["total_tasks"] = breakdown.get("total_tasks", 0)

        return network

    def get_assistant_breakdown(self) -> Dict[str, Any]:
        """Get breakdown showing assistant network"""
        breakdown = {
            "framework": "Assistant Framework (AI2AI)",
            "insight": "AI-to-AI delegation = Network of Assistants",
            "primary_assistant": None,
            "specialist_assistants": [],
            "assistant_network": {}
        }

        if self.delegation_manager:
            full_breakdown = self.delegation_manager.get_breakdown()
            primary = full_breakdown.get("primary_agent", {})

            breakdown["primary_assistant"] = {
                "who_i_am": primary.get("who_i_am", "JARVIS"),
                "what_im_doing": primary.get("what_im_doing", []),
                "what_ive_delegated": primary.get("what_ive_delegated", [])
            }

            breakdown["specialist_assistants"] = [
                {
                    "assistant_name": agent.get("who_i_am", "Unknown"),
                    "role": agent.get("my_role", "unknown"),
                    "tasks": agent.get("what_im_doing", []),
                    "delegated": agent.get("what_ive_delegated", [])
                }
                for agent in full_breakdown.get("all_agents", [])
                if agent.get("my_role") != "primary"
            ]

            breakdown["assistant_network"] = full_breakdown

        return breakdown


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Assistant Framework")
        parser.add_argument("--recognize", action="store_true", help="Recognize assistant pattern")
        parser.add_argument("--network", action="store_true", help="Show assistant network")
        parser.add_argument("--breakdown", action="store_true", help="Show assistant breakdown")
        parser.add_argument("--create", type=str, help="Create assistant (name)")
        parser.add_argument("--type", type=str, default="specialist", help="Assistant type (specialist/coordinator/delegate)")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        framework = AssistantFramework(project_root)

        if args.recognize:
            pattern = framework.recognize_assistant_pattern()
            print("=" * 80)
            print("ASSISTANT FRAMEWORK RECOGNITION")
            print("=" * 80)
            print(f"\nInsight: {pattern['insight']['realization']}")
            print(f"Pattern: {pattern['insight']['pattern']}")
            print(f"Network: {pattern['insight']['network']}")
            print(f"\nAssistant Network:")
            print(f"  Primary: {pattern['assistant_network']['primary_assistant']}")
            print(f"  Total Assistants: {pattern['assistant_network'].get('total_assistants', 0)}")
            print("=" * 80)
            print(json.dumps(pattern, indent=2, default=str))

        elif args.network:
            network = framework.get_assistant_network()
            print(json.dumps(network, indent=2, default=str))

        elif args.breakdown:
            breakdown = framework.get_assistant_breakdown()
            print("=" * 80)
            print("ASSISTANT FRAMEWORK BREAKDOWN")
            print("=" * 80)
            print(f"\nFramework: {breakdown['framework']}")
            print(f"Insight: {breakdown['insight']}")
            print(f"\nPrimary Assistant: {breakdown['primary_assistant'].get('who_i_am') if breakdown['primary_assistant'] else 'N/A'}")
            print(f"Specialist Assistants: {len(breakdown['specialist_assistants'])}")
            print("=" * 80)
            print(json.dumps(breakdown, indent=2, default=str))

        elif args.create:
            assistant = framework.create_assistant(args.create, args.type)
            print(json.dumps(assistant, indent=2, default=str))

        else:
            # Default: recognize pattern
            pattern = framework.recognize_assistant_pattern()
            print(json.dumps(pattern, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()