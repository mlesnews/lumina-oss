#!/usr/bin/env python3
"""
VA Task Queue System

Manages and prioritizes tasks across VAs with queuing, scheduling, and load balancing.

Tags: #VIRTUAL_ASSISTANT #TASK_QUEUE #PRIORITY #SCHEDULING @JARVIS @LUMINA
"""

import heapq
import json
import sys
from dataclasses import dataclass, field
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

logger = get_logger("VATaskQueue")


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass
class QueuedTask:
    """Task in queue"""
    task_id: str
    va_id: str
    task_type: str
    description: str
    priority: TaskPriority
    created_at: str
    scheduled_for: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)

    def __lt__(self, other):
        """Comparison for priority queue"""
        if self.priority != other.priority:
            return self.priority.value < other.priority.value
        if self.scheduled_for and other.scheduled_for:
            return self.scheduled_for < other.scheduled_for
        return self.created_at < other.created_at


class VATaskQueue:
    """
    VA Task Queue System

    Features:
    - Priority queuing per VA
    - Task scheduling
    - Load balancing
    - Task delegation
    - Dependency management
    """

    def __init__(self, registry: Optional[CharacterAvatarRegistry] = None):
        """Initialize task queue system"""
        if registry is None:
            if CharacterAvatarRegistry:
                registry = CharacterAvatarRegistry()
            else:
                raise ValueError("CharacterAvatarRegistry not available")

        self.registry = registry
        self.vas = self.registry.get_characters_by_type(CharacterType.VIRTUAL_ASSISTANT)

        # Task queues per VA (priority queues)
        self.queues: Dict[str, List[QueuedTask]] = {va.character_id: [] for va in self.vas}

        # Task registry
        self.tasks: Dict[str, QueuedTask] = {}
        self.task_counter = 0

        # Processing status
        self.processing: Dict[str, QueuedTask] = {}  # va_id -> current task

        # Data persistence
        self.data_dir = project_root / "data" / "va_task_queue"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 80)
        logger.info("📋 VA TASK QUEUE SYSTEM")
        logger.info("=" * 80)
        logger.info(f"   VAs Registered: {len(self.vas)}")
        logger.info("   Task queues initialized")
        logger.info("=" * 80)

    def add_task(self, va_id: str, task_type: str, description: str,
                 priority: TaskPriority = TaskPriority.MEDIUM,
                 scheduled_for: Optional[str] = None,
                 dependencies: Optional[List[str]] = None,
                 context: Optional[Dict[str, Any]] = None) -> QueuedTask:
        """Add task to queue"""
        va = self.registry.get_character(va_id)
        if not va or va.character_type != CharacterType.VIRTUAL_ASSISTANT:
            raise ValueError(f"VA {va_id} not found")

        self.task_counter += 1
        task_id = f"queue_task_{self.task_counter:06d}"

        task = QueuedTask(
            task_id=task_id,
            va_id=va_id,
            task_type=task_type,
            description=description,
            priority=priority,
            created_at=datetime.now().isoformat(),
            scheduled_for=scheduled_for,
            dependencies=dependencies or [],
            context=context or {}
        )

        self.tasks[task_id] = task
        heapq.heappush(self.queues[va_id], task)

        logger.info(f"📋 Added task to {va_id} queue: {task_id} ({priority.name})")
        return task

    def process_queue(self, va_id: str, max_tasks: int = 1) -> List[QueuedTask]:
        """Process tasks from queue"""
        if va_id not in self.queues:
            return []

        processed = []
        queue = self.queues[va_id]

        # Check if VA is already processing
        if va_id in self.processing:
            logger.info(f"⏳ {va_id} already processing task")
            return []

        # Process up to max_tasks
        for _ in range(max_tasks):
            if not queue:
                break

            # Get next task (check dependencies)
            task = None
            temp_tasks = []

            while queue:
                candidate = heapq.heappop(queue)

                # Check dependencies
                if not candidate.dependencies or all(
                    dep_id not in self.tasks or
                    self.tasks[dep_id].va_id != va_id or
                    dep_id not in [t.task_id for t in queue]
                    for dep_id in candidate.dependencies
                ):
                    task = candidate
                    break
                else:
                    temp_tasks.append(candidate)

            # Put back tasks that couldn't be processed
            for t in temp_tasks:
                heapq.heappush(queue, t)

            if not task:
                break

            # Mark as processing
            self.processing[va_id] = task
            processed.append(task)

            logger.info(f"⚙️  Processing task: {task.task_id} on {va_id}")

        return processed

    def complete_task(self, task_id: str):
        """Mark task as completed"""
        task = self.tasks.get(task_id)
        if not task:
            return

        # Remove from processing
        if task.va_id in self.processing and self.processing[task.va_id].task_id == task_id:
            del self.processing[task.va_id]

        logger.info(f"✅ Completed task: {task_id}")

    def delegate_task(self, task_id: str, target_va_id: str) -> bool:
        """Delegate task to another VA"""
        task = self.tasks.get(task_id)
        if not task:
            return False

        # Remove from original queue
        original_queue = self.queues[task.va_id]
        self.queues[task.va_id] = [t for t in original_queue if t.task_id != task_id]
        heapq.heapify(self.queues[task.va_id])

        # Add to target queue
        task.va_id = target_va_id
        heapq.heappush(self.queues[target_va_id], task)

        logger.info(f"🔄 Delegated task {task_id} to {target_va_id}")
        return True

    def load_balance_queues(self) -> Dict[str, int]:
        """Load balance queues across VAs"""
        queue_sizes = {va_id: len(queue) for va_id, queue in self.queues.items()}

        if not queue_sizes:
            return {}

        avg_size = sum(queue_sizes.values()) / len(queue_sizes)

        # Identify overloaded and underloaded VAs
        overloaded = {va_id: size for va_id, size in queue_sizes.items() if size > avg_size * 1.5}
        underloaded = {va_id: size for va_id, size in queue_sizes.items() if size < avg_size * 0.5}

        # Balance by moving tasks
        moved = 0
        for overloaded_va, overloaded_size in overloaded.items():
            if not underloaded:
                break

            # Find most underloaded VA
            target_va = min(underloaded.keys(), key=lambda v: queue_sizes[v])

            # Move tasks (simplified: move one task)
            if self.queues[overloaded_va]:
                task = heapq.heappop(self.queues[overloaded_va])
                task.va_id = target_va
                heapq.heappush(self.queues[target_va], task)
                moved += 1

                queue_sizes[overloaded_va] -= 1
                queue_sizes[target_va] += 1

                if queue_sizes[target_va] >= avg_size * 0.5:
                    del underloaded[target_va]

        if moved > 0:
            logger.info(f"⚖️  Load balanced: moved {moved} tasks")

        return queue_sizes

    def get_queue_status(self, va_id: Optional[str] = None) -> Dict[str, Any]:
        """Get queue status"""
        if va_id:
            return {
                "va_id": va_id,
                "queue_size": len(self.queues.get(va_id, [])),
                "processing": va_id in self.processing,
                "current_task": self.processing.get(va_id).task_id if va_id in self.processing else None
            }
        else:
            return {
                va_id: {
                    "queue_size": len(queue),
                    "processing": va_id in self.processing
                }
                for va_id, queue in self.queues.items()
            }

    def _save_state(self):
        try:
            """Save queue state"""
            state_file = self.data_dir / "queue_state.json"

            state = {
                "queues": {
                    va_id: [task.task_id for task in queue]
                    for va_id, queue in self.queues.items()
                },
                "tasks": {task_id: {
                    "task_id": task.task_id,
                    "va_id": task.va_id,
                    "task_type": task.task_type,
                    "description": task.description,
                    "priority": task.priority.name,
                    "created_at": task.created_at
                } for task_id, task in self.tasks.items()},
                "processing": {va_id: task.task_id for va_id, task in self.processing.items()},
                "task_counter": self.task_counter,
                "timestamp": datetime.now().isoformat()
            }

            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)

            logger.info(f"💾 Saved queue state to {state_file}")


        except Exception as e:
            self.logger.error(f"Error in _save_state: {e}", exc_info=True)
            raise
def main():
    """Main entry point for testing"""
    if not CharacterAvatarRegistry:
        print("❌ Character Avatar Registry not available")
        return

    registry = CharacterAvatarRegistry()
    queue = VATaskQueue(registry)

    print("=" * 80)
    print("📋 VA TASK QUEUE SYSTEM TEST")
    print("=" * 80)
    print()

    # Test: Add tasks
    print("Adding tasks to queues...")
    queue.add_task("jarvis_va", "automation", "Automate workflow", TaskPriority.HIGH)
    queue.add_task("jarvis_va", "system", "System check", TaskPriority.MEDIUM)
    queue.add_task("ace", "combat", "Security scan", TaskPriority.CRITICAL)
    queue.add_task("imva", "ui", "Update display", TaskPriority.LOW)
    print("  ✅ Tasks added")
    print()

    # Test: Queue status
    print("Queue Status:")
    status = queue.get_queue_status()
    for va_id, info in status.items():
        print(f"  • {va_id}: {info['queue_size']} tasks, processing={info['processing']}")
    print()

    # Test: Process queues
    print("Processing queues...")
    for va in queue.vas:
        processed = queue.process_queue(va.character_id)
        if processed:
            print(f"  ✅ {va.name}: Processing {len(processed)} task(s)")
    print()

    # Test: Load balancing
    print("Load balancing...")
    queue_sizes = queue.load_balance_queues()
    print(f"  ✅ Queue sizes: {queue_sizes}")
    print()

    # Save state
    queue._save_state()

    print("=" * 80)


if __name__ == "__main__":


    main()