#!/usr/bin/env python3
"""
JARVIS Coordination Framework

Coordinate multiple systems, manage workflows, allocate resources.
Part of Phase 3 (Child → Adolescent).

Tags: #JARVIS #COORDINATION #PHASE3 @JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISCoordinationFramework")


@dataclass
class CoordinatedTask:
    """A task in a coordinated workflow"""
    task_id: str
    system_id: str
    action: str
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, executing, completed, failed
    result: Optional[Any] = None


@dataclass
class Workflow:
    """A coordinated workflow"""
    workflow_id: str
    goal: str
    tasks: List[CoordinatedTask]
    status: str = "pending"
    created_time: str = field(default_factory=lambda: datetime.now().isoformat())


class JARVISCoordinationFramework:
    """
    Coordination framework for multiple systems

    Capabilities:
    - Coordinate multiple systems
    - Manage workflows
    - Allocate resources
    - Handle dependencies
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize coordination framework"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "jarvis_coordination"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.workflows_file = self.data_dir / "workflows.json"
        self.workflows: List[Workflow] = []
        self.active_workflows: Dict[str, Workflow] = {}

        self._load_data()

        logger.info("=" * 80)
        logger.info("🎯 JARVIS COORDINATION FRAMEWORK")
        logger.info("=" * 80)
        logger.info("   Coordinate multiple systems, manage workflows")
        logger.info("")

    def create_workflow(self, goal: str, tasks: List[Dict[str, str]]) -> str:
        """Create a coordinated workflow"""
        workflow_id = f"workflow_{int(time.time() * 1000)}"

        coordinated_tasks = [
            CoordinatedTask(
                task_id=task["task_id"],
                system_id=task["system_id"],
                action=task["action"],
                dependencies=task.get("dependencies", [])
            )
            for task in tasks
        ]

        workflow = Workflow(
            workflow_id=workflow_id,
            goal=goal,
            tasks=coordinated_tasks
        )

        self.workflows.append(workflow)
        self._save_data()

        logger.info(f"🎯 Created workflow: {goal} ({len(tasks)} tasks)")
        return workflow_id

    def execute_workflow(self, workflow_id: str) -> bool:
        """Execute a workflow"""
        workflow = next((w for w in self.workflows if w.workflow_id == workflow_id), None)
        if not workflow:
            return False

        workflow.status = "executing"
        self.active_workflows[workflow_id] = workflow
        self._save_data()

        # Get execution order
        execution_order = self._get_execution_order(workflow)

        success = True
        for task_id in execution_order:
            task = next(t for t in workflow.tasks if t.task_id == task_id)
            task.status = "executing"
            self._save_data()

            # Execute task (placeholder)
            task.status = "completed"
            task.result = {"status": "completed"}

            if not success:
                break

        workflow.status = "completed" if success else "failed"
        if workflow_id in self.active_workflows:
            del self.active_workflows[workflow_id]

        self._save_data()
        logger.info(f"🎯 Workflow {workflow_id}: {'completed' if success else 'failed'}")
        return success

    def _get_execution_order(self, workflow: Workflow) -> List[str]:
        """Get execution order (topological sort)"""
        in_degree = {task.task_id: len(task.dependencies) for task in workflow.tasks}
        queue = [tid for tid, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            current = queue.pop(0)
            result.append(current)

            for task in workflow.tasks:
                if current in task.dependencies:
                    in_degree[task.task_id] -= 1
                    if in_degree[task.task_id] == 0:
                        queue.append(task.task_id)

        remaining = [t.task_id for t in workflow.tasks if t.task_id not in result]
        result.extend(remaining)
        return result

    def _load_data(self):
        """Load workflows from disk"""
        try:
            if self.workflows_file.exists():
                with open(self.workflows_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.workflows = [
                        Workflow(
                            **{
                                **wf_data,
                                "tasks": [CoordinatedTask(**t) for t in wf_data["tasks"]]
                            }
                        )
                        for wf_data in data.get("workflows", [])
                    ]
        except Exception as e:
            logger.debug(f"Could not load workflow data: {e}")

    def _save_data(self):
        """Save workflows to disk"""
        try:
            data = {
                "workflows": [asdict(wf) for wf in self.workflows],
                "last_updated": datetime.now().isoformat()
            }
            with open(self.workflows_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Could not save workflow data: {e}")


# Singleton
_coordination_instance: Optional[JARVISCoordinationFramework] = None

def get_jarvis_coordination_framework(project_root: Optional[Path] = None) -> JARVISCoordinationFramework:
    global _coordination_instance
    if _coordination_instance is None:
        _coordination_instance = JARVISCoordinationFramework(project_root)
    return _coordination_instance
