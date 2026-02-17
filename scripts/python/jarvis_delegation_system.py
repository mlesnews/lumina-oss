#!/usr/bin/env python3
"""
JARVIS Delegation & Subagent Coordination System
@JARVIS @DELEGATE @SUBAGENTS

Manages task delegation and subagent coordination for parallel work streams.

Tags: #JARVIS #DELEGATE #SUBAGENTS #COORDINATION @JARVIS @LUMINA
"""

import sys
import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
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

logger = get_logger("JARVISDelegation")

PROJECT_ROOT = Path(__file__).parent.parent.parent


class TaskStatus(Enum):
    """Task status"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentType(Enum):
    """Agent types"""
    DISCOVERY = "discovery"
    PERFORMANCE = "performance"
    QA = "qa"
    OPTIMIZATION = "optimization"
    TESTING = "testing"
    VALIDATION = "validation"
    COORDINATION = "coordination"


@dataclass
class Task:
    """Task definition"""
    task_id: str
    title: str
    description: str
    agent_type: AgentType
    priority: int = 5  # 1-10, 10 is highest
    status: TaskStatus = TaskStatus.PENDING
    assigned_to: Optional[str] = None
    created_at: str = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()


@dataclass
class Agent:
    """Agent definition"""
    agent_id: str
    agent_type: AgentType
    name: str
    capabilities: List[str]
    current_task: Optional[str] = None
    status: str = "idle"  # idle, busy, error
    tasks_completed: int = 0
    tasks_failed: int = 0


class DelegationSystem:
    """Delegation and task management system"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "jarvis"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.tasks: Dict[str, Task] = {}
        self.agents: Dict[str, Agent] = {}
        self.task_queue: List[str] = []  # Task IDs in priority order

        self.logger = get_logger("DelegationSystem")
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize default agents"""
        agents_config = [
            {
                "agent_id": "discovery_agent",
                "agent_type": AgentType.DISCOVERY,
                "name": "Discovery Agent",
                "capabilities": ["workflow_mapping", "pattern_recognition", "preference_learning"]
            },
            {
                "agent_id": "performance_analyst",
                "agent_type": AgentType.PERFORMANCE,
                "name": "Performance Analyst",
                "capabilities": ["performance_monitoring", "bottleneck_analysis", "optimization"]
            },
            {
                "agent_id": "qa_agent",
                "agent_type": AgentType.QA,
                "name": "QA Agent",
                "capabilities": ["testing", "validation", "quality_assurance"]
            },
            {
                "agent_id": "optimization_agent",
                "agent_type": AgentType.OPTIMIZATION,
                "name": "Optimization Agent",
                "capabilities": ["solution_optimization", "performance_improvement"]
            },
            {
                "agent_id": "test_agent",
                "agent_type": AgentType.TESTING,
                "name": "Test Agent",
                "capabilities": ["automated_testing", "regression_testing", "integration_testing"]
            },
            {
                "agent_id": "validation_agent",
                "agent_type": AgentType.VALIDATION,
                "name": "Validation Agent",
                "capabilities": ["requirement_validation", "user_experience_validation"]
            }
        ]

        for agent_config in agents_config:
            agent = Agent(**agent_config)
            self.agents[agent.agent_id] = agent
            self.logger.info(f"✅ Initialized agent: {agent.name}")

    def create_task(self, title: str, description: str, agent_type: AgentType, priority: int = 5) -> str:
        """Create a new task"""
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        task = Task(
            task_id=task_id,
            title=title,
            description=description,
            agent_type=agent_type,
            priority=priority
        )

        self.tasks[task_id] = task
        self._add_to_queue(task_id)
        self.logger.info(f"📋 Created task: {title} (Priority: {priority})")
        self._save_state()

        return task_id

    def _add_to_queue(self, task_id: str):
        """Add task to queue (sorted by priority)"""
        if task_id not in self.task_queue:
            self.task_queue.append(task_id)
            # Sort by priority (highest first)
            self.task_queue.sort(key=lambda tid: self.tasks[tid].priority, reverse=True)

    def assign_task(self, task_id: str, agent_id: str) -> bool:
        """Assign task to agent"""
        if task_id not in self.tasks:
            self.logger.error(f"❌ Task not found: {task_id}")
            return False

        if agent_id not in self.agents:
            self.logger.error(f"❌ Agent not found: {agent_id}")
            return False

        task = self.tasks[task_id]
        agent = self.agents[agent_id]

        # Check if agent can handle this task type
        if agent.agent_type != task.agent_type:
            self.logger.warning(f"⚠️  Agent {agent_id} type mismatch for task {task_id}")
            # Allow assignment anyway, but log warning

        # Check if agent is available
        if agent.status == "busy" and agent.current_task:
            self.logger.warning(f"⚠️  Agent {agent_id} is busy, but assigning anyway")

        # Assign task
        task.status = TaskStatus.ASSIGNED
        task.assigned_to = agent_id
        agent.current_task = task_id
        agent.status = "busy"

        self.logger.info(f"✅ Assigned task '{task.title}' to {agent.name}")
        self._save_state()

        return True

    def start_task(self, task_id: str) -> bool:
        """Start task execution"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        if task.status != TaskStatus.ASSIGNED:
            self.logger.warning(f"⚠️  Task {task_id} not in ASSIGNED status")
            return False

        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now().isoformat()

        if task.assigned_to:
            agent = self.agents[task.assigned_to]
            agent.status = "busy"

        self.logger.info(f"🚀 Started task: {task.title}")
        self._save_state()

        return True

    def complete_task(self, task_id: str, result: Dict[str, Any] = None) -> bool:
        """Mark task as completed"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now().isoformat()
        task.result = result

        if task.assigned_to:
            agent = self.agents[task.assigned_to]
            agent.current_task = None
            agent.status = "idle"
            agent.tasks_completed += 1

        # Remove from queue
        if task_id in self.task_queue:
            self.task_queue.remove(task_id)

        self.logger.info(f"✅ Completed task: {task.title}")
        self._save_state()

        return True

    def fail_task(self, task_id: str, error: str) -> bool:
        """Mark task as failed"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        task.status = TaskStatus.FAILED
        task.completed_at = datetime.now().isoformat()
        task.error = error

        if task.assigned_to:
            agent = self.agents[task.assigned_to]
            agent.current_task = None
            agent.status = "idle"
            agent.tasks_failed += 1

        # Remove from queue
        if task_id in self.task_queue:
            self.task_queue.remove(task_id)

        self.logger.error(f"❌ Failed task: {task.title} - {error}")
        self._save_state()

        return True

    def auto_assign_tasks(self):
        """Automatically assign tasks from queue to available agents"""
        for task_id in self.task_queue[:]:  # Copy list to avoid modification during iteration
            task = self.tasks[task_id]

            if task.status != TaskStatus.PENDING:
                continue

            # Find available agent for this task type
            available_agent = self._find_available_agent(task.agent_type)

            if available_agent:
                self.assign_task(task_id, available_agent.agent_id)
                self.start_task(task_id)

    def _find_available_agent(self, agent_type: AgentType) -> Optional[Agent]:
        """Find available agent for task type"""
        for agent in self.agents.values():
            if agent.agent_type == agent_type and agent.status == "idle":
                return agent

        # If no idle agent, find least busy agent of correct type
        matching_agents = [a for a in self.agents.values() if a.agent_type == agent_type]
        if matching_agents:
            return min(matching_agents, key=lambda a: (1 if a.status == "busy" else 0, a.tasks_completed))

        return None

    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            "timestamp": datetime.now().isoformat(),
            "tasks": {
                "total": len(self.tasks),
                "pending": sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING),
                "in_progress": sum(1 for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS),
                "completed": sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED),
                "failed": sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
            },
            "agents": {
                agent_id: {
                    "name": agent.name,
                    "status": agent.status,
                    "current_task": agent.current_task,
                    "tasks_completed": agent.tasks_completed,
                    "tasks_failed": agent.tasks_failed
                }
                for agent_id, agent in self.agents.items()
            },
            "queue_length": len(self.task_queue)
        }

    def _save_state(self):
        try:
            """Save system state"""
            state = {
                "timestamp": datetime.now().isoformat(),
                "tasks": {tid: asdict(task) for tid, task in self.tasks.items()},
                "agents": {aid: {
                    "agent_id": agent.agent_id,
                    "agent_type": agent.agent_type.value,
                    "name": agent.name,
                    "capabilities": agent.capabilities,
                    "current_task": agent.current_task,
                    "status": agent.status,
                    "tasks_completed": agent.tasks_completed,
                    "tasks_failed": agent.tasks_failed
                } for aid, agent in self.agents.items()},
                "task_queue": self.task_queue
            }

            state_file = self.data_dir / "delegation_state.json"
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2, default=str)


        except Exception as e:
            self.logger.error(f"Error in _save_state: {e}", exc_info=True)
            raise
def main():
    try:
        """CLI entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Delegation System")
        parser.add_argument('--project-root', type=Path, help='Project root directory')
        parser.add_argument('--status', action='store_true', help='Show system status')

        args = parser.parse_args()

        system = DelegationSystem(project_root=args.project_root or PROJECT_ROOT)

        if args.status:
            status = system.get_status()
            print(json.dumps(status, indent=2))
        else:
            # Example: Create some tasks
            system.create_task(
                "Map user workflow",
                "Discover and map user's actual workflow patterns",
                AgentType.DISCOVERY,
                priority=10
            )

            system.create_task(
                "Monitor performance",
                "Monitor system performance metrics",
                AgentType.PERFORMANCE,
                priority=8
            )

            system.create_task(
                "Test solutions",
                "Test newly developed solutions",
                AgentType.QA,
                priority=9
            )

            # Auto-assign tasks
            system.auto_assign_tasks()

            # Show status
            status = system.get_status()
            print(json.dumps(status, indent=2))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()