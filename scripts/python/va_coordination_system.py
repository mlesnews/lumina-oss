#!/usr/bin/env python3
"""
Multi-VA Coordination System

Enables Virtual Assistants to communicate, delegate tasks, share context, and coordinate operations.

Tags: #VIRTUAL_ASSISTANT #COORDINATION #MULTI_VA #TASK_DELEGATION @JARVIS @LUMINA
"""

import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from character_avatar_registry import (CharacterAvatarRegistry,
                                           CharacterType)
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    CharacterAvatarRegistry = None
    CharacterType = None

logger = get_logger("VACoordination")


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(Enum):
    """Task status"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    DELEGATED = "delegated"


@dataclass
class VATask:
    """Task for Virtual Assistant"""
    task_id: str
    task_type: str
    description: str
    priority: TaskPriority
    assigned_va: Optional[str] = None
    delegated_to: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    context: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["priority"] = self.priority.value
        data["status"] = self.status.value
        return data


@dataclass
class VAMessage:
    """Message between Virtual Assistants"""
    message_id: str
    from_va: str
    to_va: str
    message_type: str  # "task_delegation", "context_share", "status_update", "request"
    content: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    acknowledged: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class VACoordinationSystem:
    """
    Multi-VA Coordination System

    Enables VAs to:
    - Communicate with each other
    - Delegate tasks
    - Share context
    - Load balance
    - Failover
    """

    def __init__(self, registry: Optional[CharacterAvatarRegistry] = None):
        """Initialize VA coordination system"""
        if registry is None:
            if CharacterAvatarRegistry:
                registry = CharacterAvatarRegistry()
            else:
                raise ValueError("CharacterAvatarRegistry not available")

        self.registry = registry
        self.vas = self.registry.get_characters_by_type(CharacterType.VIRTUAL_ASSISTANT)

        # Task management
        self.tasks: Dict[str, VATask] = {}
        self.task_counter = 0

        # Message queue
        self.messages: Dict[str, List[VAMessage]] = {va.character_id: [] for va in self.vas}

        # Context sharing
        self.shared_context: Dict[str, Any] = {}

        # VA status
        self.va_status: Dict[str, Dict[str, Any]] = {
            va.character_id: {
                "available": True,
                "current_tasks": 0,
                "max_tasks": 10,
                "last_activity": datetime.now().isoformat()
            }
            for va in self.vas
        }

        # Load balancing
        self.load_balancing_enabled = True

        # Data persistence
        self.data_dir = project_root / "data" / "va_coordination"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 80)
        logger.info("🤝 MULTI-VA COORDINATION SYSTEM")
        logger.info("=" * 80)
        logger.info(f"   VAs Registered: {len(self.vas)}")
        logger.info("   Ready for coordination")
        logger.info("=" * 80)

    def create_task(self, task_type: str, description: str,
                   priority: TaskPriority = TaskPriority.MEDIUM,
                   context: Optional[Dict[str, Any]] = None,
                   dependencies: Optional[List[str]] = None) -> VATask:
        """Create a new task"""
        self.task_counter += 1
        task_id = f"task_{self.task_counter:06d}"

        task = VATask(
            task_id=task_id,
            task_type=task_type,
            description=description,
            priority=priority,
            context=context or {},
            dependencies=dependencies or []
        )

        self.tasks[task_id] = task
        logger.info(f"📋 Created task: {task_id} - {description}")

        return task

    def assign_task(self, task_id: str, va_id: str, auto_assign: bool = False) -> bool:
        """Assign task to a VA"""
        if task_id not in self.tasks:
            logger.warning(f"Task {task_id} not found")
            return False

        task = self.tasks[task_id]

        # Check if VA exists
        va = self.registry.get_character(va_id)
        if not va or va.character_type != CharacterType.VIRTUAL_ASSISTANT:
            logger.warning(f"VA {va_id} not found or not a VA")
            return False

        # Check VA availability
        if not self.va_status[va_id]["available"]:
            if auto_assign:
                # Find alternative VA
                alternative = self._find_available_va(task)
                if alternative:
                    va_id = alternative
                    logger.info(f"VA {task.assigned_va} unavailable, using {va_id}")
                else:
                    logger.warning(f"No available VA for task {task_id}")
                    return False
            else:
                logger.warning(f"VA {va_id} not available")
                return False

        # Check task dependencies
        if task.dependencies:
            for dep_id in task.dependencies:
                if dep_id not in self.tasks:
                    logger.warning(f"Dependency {dep_id} not found")
                    return False
                dep_task = self.tasks[dep_id]
                if dep_task.status != TaskStatus.COMPLETED:
                    logger.warning(f"Dependency {dep_id} not completed")
                    return False

        # Assign task
        task.assigned_va = va_id
        task.status = TaskStatus.ASSIGNED
        task.updated_at = datetime.now().isoformat()

        # Update VA status
        self.va_status[va_id]["current_tasks"] += 1
        self.va_status[va_id]["last_activity"] = datetime.now().isoformat()

        logger.info(f"✅ Assigned task {task_id} to {va_id}")
        return True

    def delegate_task(self, task_id: str, from_va: str, to_va: str, reason: str = "") -> bool:
        """Delegate task from one VA to another"""
        if task_id not in self.tasks:
            logger.warning(f"Task {task_id} not found")
            return False

        task = self.tasks[task_id]

        if task.assigned_va != from_va:
            logger.warning(f"Task {task_id} not assigned to {from_va}")
            return False

        # Check if target VA exists and is available
        target_va = self.registry.get_character(to_va)
        if not target_va or target_va.character_type != CharacterType.VIRTUAL_ASSISTANT:
            logger.warning(f"Target VA {to_va} not found")
            return False

        if not self.va_status[to_va]["available"]:
            logger.warning(f"Target VA {to_va} not available")
            return False

        # Delegate task
        task.delegated_to = to_va
        task.assigned_va = to_va
        task.status = TaskStatus.DELEGATED
        task.updated_at = datetime.now().isoformat()

        # Update VA statuses
        self.va_status[from_va]["current_tasks"] -= 1
        self.va_status[to_va]["current_tasks"] += 1
        self.va_status[to_va]["last_activity"] = datetime.now().isoformat()

        # Send delegation message
        self.send_message(
            from_va=from_va,
            to_va=to_va,
            message_type="task_delegation",
            content={
                "task_id": task_id,
                "reason": reason,
                "task_description": task.description
            }
        )

        logger.info(f"🔄 Delegated task {task_id} from {from_va} to {to_va}")
        return True

    def send_message(self, from_va: str, to_va: str, message_type: str,
                    content: Dict[str, Any]) -> str:
        """Send message between VAs"""
        message_id = f"msg_{datetime.now().timestamp()}"

        message = VAMessage(
            message_id=message_id,
            from_va=from_va,
            to_va=to_va,
            message_type=message_type,
            content=content
        )

        if to_va not in self.messages:
            self.messages[to_va] = []

        self.messages[to_va].append(message)

        logger.info(f"📨 Message sent from {from_va} to {to_va}: {message_type}")
        return message_id

    def share_context(self, from_va: str, context: Dict[str, Any],
                     target_vas: Optional[List[str]] = None):
        """Share context with other VAs"""
        if target_vas is None:
            target_vas = [va.character_id for va in self.vas if va.character_id != from_va]

        # Store in shared context
        context_key = f"{from_va}_{datetime.now().timestamp()}"
        self.shared_context[context_key] = {
            "from_va": from_va,
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "shared_with": target_vas
        }

        # Send context messages
        for target_va in target_vas:
            self.send_message(
                from_va=from_va,
                to_va=target_va,
                message_type="context_share",
                content={"context_key": context_key, "context": context}
            )

        logger.info(f"📤 {from_va} shared context with {len(target_vas)} VAs")

    def get_shared_context(self, va_id: str) -> Dict[str, Any]:
        """Get shared context for a VA"""
        relevant_context = {}

        for key, ctx in self.shared_context.items():
            if va_id in ctx.get("shared_with", []):
                relevant_context[key] = ctx

        return relevant_context

    def _find_available_va(self, task: Optional[VATask] = None) -> Optional[str]:
        """Find available VA for task (load balancing)"""
        available_vas = [
            va_id for va_id, status in self.va_status.items()
            if status["available"] and status["current_tasks"] < status["max_tasks"]
        ]

        if not available_vas:
            return None

        if self.load_balancing_enabled:
            # Select VA with least current tasks
            return min(available_vas, key=lambda va_id: self.va_status[va_id]["current_tasks"])
        else:
            # Select first available
            return available_vas[0]

    def auto_assign_task(self, task_id: str) -> Optional[str]:
        """Automatically assign task to best available VA"""
        if task_id not in self.tasks:
            return None

        task = self.tasks[task_id]
        va_id = self._find_available_va(task)

        if va_id:
            self.assign_task(task_id, va_id, auto_assign=True)
            return va_id

        return None

    def complete_task(self, task_id: str, result: Optional[Dict[str, Any]] = None) -> bool:
        """Mark task as completed"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now().isoformat()
        task.result = result
        task.updated_at = datetime.now().isoformat()

        # Update VA status
        if task.assigned_va:
            self.va_status[task.assigned_va]["current_tasks"] -= 1
            self.va_status[task.assigned_va]["last_activity"] = datetime.now().isoformat()

        logger.info(f"✅ Task {task_id} completed by {task.assigned_va}")
        return True

    def get_va_status(self, va_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a VA"""
        if va_id not in self.va_status:
            return None

        va = self.registry.get_character(va_id)
        if not va:
            return None

        status = self.va_status[va_id].copy()
        status["va_name"] = va.name
        status["va_role"] = va.role
        status["pending_messages"] = len(self.messages.get(va_id, []))
        status["assigned_tasks"] = [
            task_id for task_id, task in self.tasks.items()
            if task.assigned_va == va_id and task.status != TaskStatus.COMPLETED
        ]

        return status

    def get_all_va_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all VAs"""
        return {va_id: self.get_va_status(va_id) for va_id in self.va_status.keys()}

    def set_va_availability(self, va_id: str, available: bool):
        """Set VA availability"""
        if va_id in self.va_status:
            self.va_status[va_id]["available"] = available
            logger.info(f"{'✅' if available else '❌'} VA {va_id} availability: {available}")

    def _save_state(self):
        try:
            """Save coordination state to disk"""
            state_file = self.data_dir / "coordination_state.json"

            state = {
                "tasks": {task_id: task.to_dict() for task_id, task in self.tasks.items()},
                "messages": {
                    va_id: [msg.to_dict() for msg in msgs]
                    for va_id, msgs in self.messages.items()
                },
                "shared_context": self.shared_context,
                "va_status": self.va_status,
                "task_counter": self.task_counter,
                "timestamp": datetime.now().isoformat()
            }

            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)

            logger.info(f"💾 Saved coordination state to {state_file}")

        except Exception as e:
            self.logger.error(f"Error in _save_state: {e}", exc_info=True)
            raise
    def _load_state(self):
        """Load coordination state from disk"""
        state_file = self.data_dir / "coordination_state.json"

        if not state_file.exists():
            return

        try:
            with open(state_file, encoding='utf-8') as f:
                state = json.load(f)

            # Load tasks
            for task_id, task_data in state.get("tasks", {}).items():
                task = VATask(**task_data)
                task.priority = TaskPriority(task_data["priority"])
                task.status = TaskStatus(task_data["status"])
                self.tasks[task_id] = task

            # Load messages
            for va_id, msgs_data in state.get("messages", {}).items():
                self.messages[va_id] = [
                    VAMessage(**msg_data) for msg_data in msgs_data
                ]

            # Load shared context
            self.shared_context = state.get("shared_context", {})

            # Load VA status
            self.va_status.update(state.get("va_status", {}))

            # Load task counter
            self.task_counter = state.get("task_counter", 0)

            logger.info(f"📂 Loaded coordination state from {state_file}")
        except Exception as e:
            logger.warning(f"Error loading state: {e}")


def main():
    """Main entry point for testing"""
    if not CharacterAvatarRegistry:
        print("❌ Character Avatar Registry not available")
        return

    registry = CharacterAvatarRegistry()
    coord_system = VACoordinationSystem(registry)

    print("=" * 80)
    print("🤝 MULTI-VA COORDINATION SYSTEM TEST")
    print("=" * 80)
    print()

    # Test: Create task
    print("Creating task...")
    task = coord_system.create_task(
        task_type="automation",
        description="Automate workflow execution",
        priority=TaskPriority.HIGH
    )
    print(f"✅ Created task: {task.task_id}")
    print()

    # Test: Auto-assign task
    print("Auto-assigning task...")
    assigned_va = coord_system.auto_assign_task(task.task_id)
    if assigned_va:
        print(f"✅ Task assigned to: {assigned_va}")
    print()

    # Test: Send message
    print("Sending message between VAs...")
    if len(coord_system.vas) >= 2:
        va1 = coord_system.vas[0].character_id
        va2 = coord_system.vas[1].character_id
        msg_id = coord_system.send_message(
            from_va=va1,
            to_va=va2,
            message_type="status_update",
            content={"status": "ready", "tasks": 0}
        )
        print(f"✅ Message sent: {msg_id}")
    print()

    # Test: Share context
    print("Sharing context...")
    if len(coord_system.vas) >= 2:
        va1 = coord_system.vas[0].character_id
        coord_system.share_context(
            from_va=va1,
            context={"workflow_id": "test_workflow", "status": "running"}
        )
        print("✅ Context shared")
    print()

    # Test: Get VA status
    print("VA Status:")
    for va in coord_system.vas:
        status = coord_system.get_va_status(va.character_id)
        if status:
            print(f"  • {status['va_name']} ({va.character_id})")
            print(f"    Available: {status['available']}")
            print(f"    Current Tasks: {status['current_tasks']}")
            print(f"    Pending Messages: {status['pending_messages']}")
            print()

    # Save state
    coord_system._save_state()

    print("=" * 80)


if __name__ == "__main__":


    main()