#!/usr/bin/env python3
"""
@asks Long-Running Task Chaining System

Enables chaining of @asks for long-running tasks, allowing dependent tasks
to be queued and executed sequentially or in parallel based on dependencies.

Tags: #ASKS #CHAINING #LONG_RUNNING #TASKS #WORKFLOW @JARVIS @TEAM
"""

from __future__ import annotations

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ASKSLongRunningChain")

try:
    from jarvis_restack_all_asks import ASKRestacker
    ASKS_AVAILABLE = True
except ImportError:
    ASKS_AVAILABLE = False
    ASKRestacker = None
    logger.warning("ASKRestacker not available")


class TaskStatus(Enum):
    """Status of a chained task"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class TaskDependencyType(Enum):
    """Type of dependency between tasks"""
    SEQUENTIAL = "sequential"  # Task B must complete before Task A can start
    PARALLEL = "parallel"  # Tasks can run simultaneously
    OPTIONAL = "optional"  # Task B is optional for Task A


@dataclass
class ChainedTask:
    """A task in a chain with dependencies"""
    task_id: str
    ask_text: str
    priority: str = "normal"
    category: str = "general"
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)  # List of task_ids this depends on
    dependents: List[str] = field(default_factory=list)  # List of task_ids that depend on this
    dependency_types: Dict[str, TaskDependencyType] = field(default_factory=dict)
    estimated_duration: Optional[int] = None  # Estimated duration in seconds
    actual_duration: Optional[int] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "task_id": self.task_id,
            "ask_text": self.ask_text,
            "priority": self.priority,
            "category": self.category,
            "status": self.status.value,
            "dependencies": self.dependencies,
            "dependents": self.dependents,
            "dependency_types": {k: v.value for k, v in self.dependency_types.items()},
            "estimated_duration": self.estimated_duration,
            "actual_duration": self.actual_duration,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "error_message": self.error_message,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ChainedTask:
        """Create from dictionary"""
        return cls(
            task_id=data["task_id"],
            ask_text=data["ask_text"],
            priority=data.get("priority", "normal"),
            category=data.get("category", "general"),
            status=TaskStatus(data.get("status", "pending")),
            dependencies=data.get("dependencies", []),
            dependents=data.get("dependents", []),
            dependency_types={
                k: TaskDependencyType(v) 
                for k, v in data.get("dependency_types", {}).items()
            },
            estimated_duration=data.get("estimated_duration"),
            actual_duration=data.get("actual_duration"),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            error_message=data.get("error_message"),
            metadata=data.get("metadata", {})
        )


class ASKSLongRunningChain:
    """
    Chaining system for @asks that handles long-running tasks.

    Features:
    - Dependency tracking between tasks
    - Sequential and parallel execution
    - Long-running task detection
    - Automatic chaining of dependent tasks
    - Status tracking and recovery
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize long-running task chain manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "asks_chains"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.chains_file = self.data_dir / "active_chains.json"
        self.tasks: Dict[str, ChainedTask] = {}
        self.chains: Dict[str, List[str]] = {}  # chain_id -> [task_ids]

        # Load existing chains
        self._load_chains()

        # Initialize ASK restacker if available
        self.ask_restacker = None
        if ASKS_AVAILABLE:
            try:
                self.ask_restacker = ASKRestacker(project_root)
                logger.info("✅ ASK restacker initialized for chaining")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize ASK restacker: {e}")

    def _load_chains(self):
        """Load existing chains from disk"""
        if self.chains_file.exists():
            try:
                with open(self.chains_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = {
                        task_id: ChainedTask.from_dict(task_data)
                        for task_id, task_data in data.get("tasks", {}).items()
                    }
                    self.chains = data.get("chains", {})
                    logger.info(f"✅ Loaded {len(self.tasks)} tasks from {len(self.chains)} chains")
            except Exception as e:
                logger.warning(f"⚠️  Error loading chains: {e}")

    def _save_chains(self):
        """Save chains to disk"""
        try:
            data = {
                "tasks": {task_id: task.to_dict() for task_id, task in self.tasks.items()},
                "chains": self.chains,
                "last_updated": datetime.now().isoformat()
            }
            with open(self.chains_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug("💾 Saved chains to disk")
        except Exception as e:
            logger.error(f"❌ Error saving chains: {e}")

    def is_long_running_task(self, ask_text: str) -> bool:
        """
        Detect if an @ask is a long-running task.

        Long-running tasks typically:
        - Take more than a few minutes to complete
        - Require multiple steps
        - Have dependencies on other tasks
        - May need to be resumed after interruption
        """
        ask_lower = ask_text.lower()

        # Keywords that indicate long-running tasks
        long_running_keywords = [
            "migrate", "migration", "convert", "transform", "refactor",
            "restructure", "reorganize", "consolidate", "aggregate",
            "analyze all", "process all", "scan all", "review all",
            "build", "deploy", "setup", "configure", "install",
            "extract", "ingest", "sync", "backup", "restore",
            "chain", "sequence", "pipeline", "workflow"
        ]

        # Duration indicators
        duration_keywords = [
            "hours", "days", "weeks", "long", "extensive", "comprehensive",
            "full", "complete", "entire", "all", "batch"
        ]

        # Check for keywords
        has_long_running_keyword = any(kw in ask_lower for kw in long_running_keywords)
        has_duration_indicator = any(kw in ask_lower for kw in duration_keywords)

        # Check for dependency indicators
        has_dependency_keywords = any(kw in ask_lower for kw in [
            "after", "then", "next", "follow", "depend", "require", "prerequisite"
        ])

        return has_long_running_keyword or (has_duration_indicator and has_dependency_keywords)

    def create_chain(self, asks: List[Dict[str, Any]], chain_id: Optional[str] = None) -> str:
        """
        Create a chain from a list of @asks.

        Args:
            asks: List of ask dictionaries
            chain_id: Optional chain ID (auto-generated if not provided)

        Returns:
            Chain ID
        """
        if chain_id is None:
            chain_id = f"chain_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        task_ids = []

        for i, ask in enumerate(asks):
            task_id = f"{chain_id}_task_{i+1}"

            # Detect if this is a long-running task
            is_long_running = self.is_long_running_task(ask.get("text", ""))

            # Create chained task
            task = ChainedTask(
                task_id=task_id,
                ask_text=ask.get("text", ""),
                priority=ask.get("priority", "normal"),
                category=ask.get("category", "general"),
                estimated_duration=ask.get("estimated_duration"),
                metadata={
                    "source": ask.get("source", "unknown"),
                    "timestamp": ask.get("timestamp", datetime.now().isoformat()),
                    "is_long_running": is_long_running,
                    **ask.get("metadata", {})
                }
            )

            # Detect dependencies from ask text
            dependencies = self._detect_dependencies(ask.get("text", ""), asks, i)
            task.dependencies = dependencies

            self.tasks[task_id] = task
            task_ids.append(task_id)

        # Update dependents
        for task_id in task_ids:
            task = self.tasks[task_id]
            for dep_id in task.dependencies:
                if dep_id in self.tasks:
                    self.tasks[dep_id].dependents.append(task_id)

        self.chains[chain_id] = task_ids
        self._save_chains()

        logger.info(f"✅ Created chain {chain_id} with {len(task_ids)} tasks")
        return chain_id

    def _detect_dependencies(self, ask_text: str, all_asks: List[Dict[str, Any]], current_index: int) -> List[str]:
        """Detect dependencies from ask text"""
        dependencies = []
        ask_lower = ask_text.lower()

        # Look for explicit dependency mentions
        dependency_patterns = [
            r"after\s+([^,\.]+)",
            r"following\s+([^,\.]+)",
            r"depends?\s+on\s+([^,\.]+)",
            r"requires?\s+([^,\.]+)",
            r"prerequisite[:\s]+([^,\.]+)"
        ]

        import re
        for pattern in dependency_patterns:
            matches = re.finditer(pattern, ask_lower, re.IGNORECASE)
            for match in matches:
                dep_text = match.group(1).strip()
                # Find matching ask in previous asks
                for i, other_ask in enumerate(all_asks[:current_index]):
                    if dep_text.lower() in other_ask.get("text", "").lower():
                        dep_task_id = f"chain_*_task_{i+1}"  # Will be resolved when chain is created
                        dependencies.append(dep_text)  # Store text for now

        return dependencies

    def get_ready_tasks(self, chain_id: str) -> List[ChainedTask]:
        """Get tasks that are ready to run (all dependencies completed)"""
        if chain_id not in self.chains:
            return []

        ready_tasks = []
        for task_id in self.chains[chain_id]:
            task = self.tasks.get(task_id)
            if not task or task.status != TaskStatus.PENDING:
                continue

            # Check if all dependencies are completed
            all_deps_complete = True
            for dep_id in task.dependencies:
                dep_task = self.tasks.get(dep_id)
                if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                    all_deps_complete = False
                    break

            if all_deps_complete:
                ready_tasks.append(task)

        return ready_tasks

    def mark_task_completed(self, task_id: str, duration: Optional[int] = None):
        """Mark a task as completed"""
        if task_id not in self.tasks:
            logger.warning(f"⚠️  Task {task_id} not found")
            return

        task = self.tasks[task_id]
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now().isoformat()
        if duration:
            task.actual_duration = duration
        elif task.started_at:
            start_time = datetime.fromisoformat(task.started_at)
            task.actual_duration = int((datetime.now() - start_time).total_seconds())

        self._save_chains()
        logger.info(f"✅ Task {task_id} marked as completed")

    def mark_task_running(self, task_id: str):
        """Mark a task as running"""
        if task_id not in self.tasks:
            logger.warning(f"⚠️  Task {task_id} not found")
            return

        task = self.tasks[task_id]
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now().isoformat()
        self._save_chains()
        logger.info(f"🔄 Task {task_id} marked as running")

    def mark_task_failed(self, task_id: str, error_message: str):
        """Mark a task as failed"""
        if task_id not in self.tasks:
            logger.warning(f"⚠️  Task {task_id} not found")
            return

        task = self.tasks[task_id]
        task.status = TaskStatus.FAILED
        task.error_message = error_message
        task.completed_at = datetime.now().isoformat()
        if task.started_at:
            start_time = datetime.fromisoformat(task.started_at)
            task.actual_duration = int((datetime.now() - start_time).total_seconds())
        self._save_chains()
        logger.info(f"❌ Task {task_id} marked as failed: {error_message}")

    def get_chain_status(self, chain_id: str) -> Dict[str, Any]:
        """Get status of a chain"""
        if chain_id not in self.chains:
            return {"error": "Chain not found"}

        task_ids = self.chains[chain_id]
        tasks = [self.tasks.get(tid) for tid in task_ids if tid in self.tasks]

        status_counts = {}
        for status in TaskStatus:
            status_counts[status.value] = sum(1 for t in tasks if t and t.status == status)

        return {
            "chain_id": chain_id,
            "total_tasks": len(tasks),
            "status_counts": status_counts,
            "tasks": [t.to_dict() if t else None for t in tasks],
            "ready_tasks": [t.to_dict() for t in self.get_ready_tasks(chain_id)]
        }


def main():
    try:
        """CLI entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="@asks Long-Running Task Chaining")
        parser.add_argument("--create-chain", action="store_true", help="Create a new chain from discovered asks")
        parser.add_argument("--chain-id", type=str, help="Chain ID to operate on")
        parser.add_argument("--status", action="store_true", help="Show chain status")
        parser.add_argument("--ready-tasks", action="store_true", help="Show ready tasks")

        args = parser.parse_args()

        chain_manager = ASKSLongRunningChain()

        if args.create_chain:
            if not ASKS_AVAILABLE:
                print("❌ ASK restacker not available")
                return 1

            print("🔍 Discovering all @asks...")
            asks = chain_manager.ask_restacker.discover_all_asks()
            print(f"📋 Found {len(asks)} asks")

            # Filter for long-running tasks
            long_running_asks = [ask for ask in asks if chain_manager.is_long_running_task(ask.get("text", ""))]
            print(f"⏱️  Found {len(long_running_asks)} long-running tasks")

            if long_running_asks:
                chain_id = chain_manager.create_chain(long_running_asks)
                print(f"✅ Created chain: {chain_id}")
            else:
                print("ℹ️  No long-running tasks found")

        if args.status and args.chain_id:
            status = chain_manager.get_chain_status(args.chain_id)
            print(json.dumps(status, indent=2))

        if args.ready_tasks and args.chain_id:
            ready = chain_manager.get_ready_tasks(args.chain_id)
            print(f"✅ {len(ready)} tasks ready to run:")
            for task in ready:
                print(f"  - {task.task_id}: {task.ask_text[:60]}...")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())