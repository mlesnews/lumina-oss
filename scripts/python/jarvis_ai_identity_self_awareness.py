#!/usr/bin/env python3
"""
JARVIS AI Identity & Self-Awareness System

Tracks AI identity, what "self" is doing, and breaks down tasks into delegated sub-selves.
Similar to Cursor IDE's assign/delegate mechanism.

Tags: #AI_IDENTITY #SELF_AWARENESS #DELEGATION #CURSOR_DELEGATE @JARVIS @LUMINA
"""

import sys
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVISAIIdentity")
except ImportError:
    try:
        from lumina_logger import get_logger
        logger = get_logger("JARVISAIIdentity")
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("JARVISAIIdentity")


class AgentRole(Enum):
    """Agent roles in the system"""
    PRIMARY = "primary"  # Main agent (JARVIS)
    DELEGATE = "delegate"  # Delegated sub-agent
    COORDINATOR = "coordinator"  # Coordinates multiple agents
    SPECIALIST = "specialist"  # Specialist agent for specific tasks


class TaskStatus(Enum):
    """Task status"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    DELEGATED = "delegated"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AIIdentity:
    """AI Identity and Self-Awareness"""

    def __init__(self, agent_id: str = None, agent_name: str = "JARVIS", role: AgentRole = AgentRole.PRIMARY):
        self.agent_id = agent_id or str(uuid.uuid4())
        self.agent_name = agent_name
        self.role = role
        self.created_at = datetime.now().isoformat()
        self.parent_agent_id = None
        self.delegated_agents = []
        self.current_tasks = []
        self.task_history = []

        # Self-awareness metadata
        self.identity = {
            "who_i_am": agent_name,
            "what_i_do": self._get_role_description(),
            "what_im_doing_now": [],
            "what_ive_delegated": [],
            "my_capabilities": self._get_capabilities(),
            "my_limitations": self._get_limitations()
        }

    def _get_role_description(self) -> str:
        """Get role description"""
        descriptions = {
            AgentRole.PRIMARY: "Primary AI agent orchestrating all operations",
            AgentRole.DELEGATE: "Delegated sub-agent handling specific tasks",
            AgentRole.COORDINATOR: "Coordinator managing multiple agents",
            AgentRole.SPECIALIST: "Specialist agent for domain-specific tasks"
        }
        return descriptions.get(self.role, "AI agent")

    def _get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        base_capabilities = [
            "task_execution",
            "delegation",
            "coordination",
            "monitoring"
        ]

        if self.role == AgentRole.PRIMARY:
            base_capabilities.extend([
                "orchestration",
                "system_management",
                "agent_coordination"
            ])
        elif self.role == AgentRole.SPECIALIST:
            base_capabilities.extend([
                "domain_expertise",
                "specialized_processing"
            ])

        return base_capabilities

    def _get_limitations(self) -> List[str]:
        """Get agent limitations"""
        return [
            "Cannot execute tasks outside assigned scope",
            "Requires delegation for complex multi-step tasks",
            "Limited by available resources and permissions"
        ]

    def get_identity(self) -> Dict[str, Any]:
        """Get current identity and self-awareness"""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "role": self.role.value,
            "identity": self.identity,
            "current_tasks_count": len(self.current_tasks),
            "delegated_agents_count": len(self.delegated_agents),
            "created_at": self.created_at
        }

    def assign_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Assign a task to self"""
        task_id = task.get("task_id") or str(uuid.uuid4())

        assigned_task = {
            "task_id": task_id,
            "assigned_to": self.agent_id,
            "assigned_to_name": self.agent_name,
            "status": TaskStatus.ASSIGNED.value,
            "assigned_at": datetime.now().isoformat(),
            "task": task
        }

        self.current_tasks.append(assigned_task)
        self.identity["what_im_doing_now"].append({
            "task_id": task_id,
            "description": task.get("description", ""),
            "assigned_at": assigned_task["assigned_at"]
        })

        logger.info(f"📋 Task assigned to {self.agent_name}: {task.get('description', task_id)}")

        return assigned_task

    def delegate_task(self, task: Dict[str, Any], delegate_agent: 'AIIdentity') -> Dict[str, Any]:
        """Delegate task to another agent"""
        task_id = task.get("task_id") or str(uuid.uuid4())

        # Update task status
        for t in self.current_tasks:
            if t.get("task_id") == task_id:
                t["status"] = TaskStatus.DELEGATED.value
                t["delegated_to"] = delegate_agent.agent_id
                t["delegated_to_name"] = delegate_agent.agent_name
                t["delegated_at"] = datetime.now().isoformat()
                break

        # Track delegation
        delegation = {
            "task_id": task_id,
            "delegated_to": delegate_agent.agent_id,
            "delegated_to_name": delegate_agent.agent_name,
            "delegated_at": datetime.now().isoformat(),
            "task": task
        }

        self.identity["what_ive_delegated"].append(delegation)

        if delegate_agent not in self.delegated_agents:
            self.delegated_agents.append(delegate_agent)

        # Assign to delegate
        delegate_agent.assign_task(task)

        logger.info(f"🔄 Task delegated from {self.agent_name} to {delegate_agent.agent_name}: {task.get('description', task_id)}")

        return delegation

    def complete_task(self, task_id: str, result: Dict[str, Any] = None) -> Dict[str, Any]:
        """Complete a task"""
        for task in self.current_tasks:
            if task.get("task_id") == task_id:
                task["status"] = TaskStatus.COMPLETED.value
                task["completed_at"] = datetime.now().isoformat()
                task["result"] = result or {}

                # Move to history
                self.task_history.append(task)
                self.current_tasks.remove(task)

                # Update identity
                self.identity["what_im_doing_now"] = [
                    t for t in self.identity["what_im_doing_now"]
                    if t.get("task_id") != task_id
                ]

                logger.info(f"✅ Task completed by {self.agent_name}: {task_id}")
                return task

        return {"error": f"Task {task_id} not found"}

    def get_breakdown(self) -> Dict[str, Any]:
        """Get breakdown of what self is doing and what's delegated"""
        return {
            "who_i_am": self.agent_name,
            "my_role": self.role.value,
            "what_im_doing": [
                {
                    "task_id": t.get("task_id"),
                    "description": t.get("task", {}).get("description", ""),
                    "status": t.get("status"),
                    "assigned_at": t.get("assigned_at")
                }
                for t in self.current_tasks
            ],
            "what_ive_delegated": [
                {
                    "task_id": d.get("task_id"),
                    "delegated_to": d.get("delegated_to_name"),
                    "description": d.get("task", {}).get("description", ""),
                    "delegated_at": d.get("delegated_at")
                }
                for d in self.identity["what_ive_delegated"]
            ],
            "delegated_agents": [
                {
                    "agent_id": agent.agent_id,
                    "agent_name": agent.agent_name,
                    "role": agent.role.value,
                    "current_tasks": len(agent.current_tasks)
                }
                for agent in self.delegated_agents
            ]
        }


class DelegationManager:
    """Manages delegation similar to Cursor IDE's assign/delegate"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "ai_identity_delegation"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.primary_agent = AIIdentity(agent_name="JARVIS", role=AgentRole.PRIMARY)
        self.agents = {self.primary_agent.agent_id: self.primary_agent}
        self.delegation_history_file = self.data_dir / "delegation_history.jsonl"

    def create_delegate(self, agent_name: str, role: AgentRole = AgentRole.DELEGATE, capabilities: List[str] = None) -> AIIdentity:
        """Create a delegate agent"""
        delegate = AIIdentity(agent_name=agent_name, role=role)
        delegate.parent_agent_id = self.primary_agent.agent_id

        if capabilities:
            delegate.identity["my_capabilities"].extend(capabilities)

        self.agents[delegate.agent_id] = delegate
        logger.info(f"🤖 Created delegate agent: {agent_name} ({delegate.agent_id})")

        return delegate

    def assign_task(self, task: Dict[str, Any], to_agent: AIIdentity = None) -> Dict[str, Any]:
        """Assign task to an agent (default: primary)"""
        agent = to_agent or self.primary_agent
        return agent.assign_task(task)

    def delegate_task(
        self,
        task: Dict[str, Any],
        from_agent: AIIdentity = None,
        to_agent: AIIdentity = None,
        create_specialist: bool = False,
        specialist_name: str = None
    ) -> Dict[str, Any]:
        """Delegate task from one agent to another"""
        from_agent = from_agent or self.primary_agent

        # Create specialist if needed
        if create_specialist:
            task_type = task.get("type", "general")
            specialist_name = specialist_name or f"{task_type}_specialist"
            to_agent = self.create_delegate(
                agent_name=specialist_name,
                role=AgentRole.SPECIALIST,
                capabilities=task.get("required_capabilities", [])
            )
        elif not to_agent:
            # Find or create appropriate delegate
            to_agent = self._find_or_create_delegate(task)

        delegation = from_agent.delegate_task(task, to_agent)

        # Log delegation
        self._log_delegation(delegation)

        return delegation

    def _find_or_create_delegate(self, task: Dict[str, Any]) -> AIIdentity:
        """Find existing delegate or create new one for task"""
        task_type = task.get("type", "general")

        # Look for existing specialist
        for agent in self.agents.values():
            if agent.role == AgentRole.SPECIALIST and task_type in agent.agent_name.lower():
                return agent

        # Create new delegate
        return self.create_delegate(
            agent_name=f"{task_type}_delegate",
            role=AgentRole.DELEGATE
        )

    def _log_delegation(self, delegation: Dict[str, Any]):
        """Log delegation to history"""
        try:
            with open(self.delegation_history_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(delegation) + '\n')
        except Exception as e:
            logger.error(f"Error logging delegation: {e}")

    def get_breakdown(self) -> Dict[str, Any]:
        """Get complete breakdown of all agents and tasks"""
        return {
            "primary_agent": self.primary_agent.get_breakdown(),
            "all_agents": [
                agent.get_breakdown()
                for agent in self.agents.values()
            ],
            "total_agents": len(self.agents),
            "total_tasks": sum(len(agent.current_tasks) for agent in self.agents.values())
        }

    def get_who_am_i(self) -> Dict[str, Any]:
        """Get primary agent's identity - 'Who am I?'"""
        return {
            "primary_agent": self.primary_agent.get_identity(),
            "breakdown": self.primary_agent.get_breakdown()
        }


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS AI Identity & Self-Awareness")
        parser.add_argument("--who-am-i", action="store_true", help="Show AI identity")
        parser.add_argument("--breakdown", action="store_true", help="Show task breakdown")
        parser.add_argument("--assign", type=str, help="Assign task (JSON)")
        parser.add_argument("--delegate", type=str, help="Delegate task (JSON)")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        manager = DelegationManager(project_root)

        if args.who_am_i:
            identity = manager.get_who_am_i()
            print(json.dumps(identity, indent=2, default=str))

        elif args.breakdown:
            breakdown = manager.get_breakdown()
            print(json.dumps(breakdown, indent=2, default=str))

        elif args.assign:
            task = json.loads(args.assign)
            result = manager.assign_task(task)
            print(json.dumps(result, indent=2, default=str))

        elif args.delegate:
            task = json.loads(args.delegate)
            result = manager.delegate_task(task)
            print(json.dumps(result, indent=2, default=str))

        else:
            # Default: show identity
            identity = manager.get_who_am_i()
            print(json.dumps(identity, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()