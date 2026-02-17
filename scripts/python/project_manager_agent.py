#!/usr/bin/env python3
"""
Project Manager AI Agent
@AGENT@PROJECT-MANAGER

Comprehensive project management agent with roles, responsibilities,
task organization, and @batch processing capabilities.

Tags: #PROJECT-MANAGER #AGENT #BATCH #WORKFLOW #ORGANIZATION
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from master_padawan_tracker import MasterPadawanTracker
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    MasterPadawanTracker = None

logger = get_logger("ProjectManagerAgent")


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(Enum):
    """Task status levels"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class BatchStatus(Enum):
    """Batch processing status"""
    PLANNED = "planned"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ProjectManagerAgent:
    """
    Project Manager AI Agent

    Job Slot: Project Manager
    Responsibilities:
    - Task organization and prioritization
    - Batch processing coordination
    - Workflow cycle management
    - Resource allocation
    - Progress tracking and reporting
    - Risk management
    - Stakeholder communication
    """

    def __init__(self, project_root: Path):
        """Initialize Project Manager Agent"""
        self.project_root = project_root
        self.logger = logger

        # Data paths
        self.data_path = project_root / "data"
        self.agent_data_path = self.data_path / "project_manager"
        self.agent_data_path.mkdir(parents=True, exist_ok=True)

        # Agent configuration
        self.agent_config_file = self.agent_data_path / "agent_config.json"
        self.tasks_file = self.agent_data_path / "tasks.json"
        self.batches_file = self.agent_data_path / "batches.json"
        self.workflow_file = self.agent_data_path / "workflow_cycles.json"

        # Initialize tracker integration
        if MasterPadawanTracker:
            self.tracker = MasterPadawanTracker(project_root)
        else:
            self.tracker = None
            self.logger.warning("⚠️  MasterPadawanTracker not available")

        # Load agent state
        self.agent_config = self._load_agent_config()
        self.tasks = self._load_tasks()
        self.batches = self._load_batches()
        self.workflow_cycles = self._load_workflow_cycles()

        self.logger.info("👔 Project Manager Agent initialized")
        self.logger.info(f"   Agent ID: {self.agent_config.get('agent_id', 'PM-001')}")
        self.logger.info(f"   Status: {self.agent_config.get('status', 'active')}")

    def _load_agent_config(self) -> Dict[str, Any]:
        """Load agent configuration"""
        if self.agent_config_file.exists():
            try:
                with open(self.agent_config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"⚠️  Error loading agent config: {e}")

        # Default configuration
        return {
            "agent_id": "PM-001",
            "agent_name": "Project Manager",
            "agent_type": "project_manager",
            "status": "active",
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "roles": [
                "task_organization",
                "batch_coordination",
                "workflow_management",
                "resource_allocation",
                "progress_tracking",
                "risk_management",
                "stakeholder_communication"
            ],
            "responsibilities": {
                "task_organization": "Organize tasks into cohesive groups and batches",
                "batch_coordination": "Coordinate @batch processing for related task groups",
                "workflow_management": "Manage workflow cycles and execution order",
                "resource_allocation": "Allocate resources to tasks and batches",
                "progress_tracking": "Track progress and update status",
                "risk_management": "Identify and mitigate risks",
                "stakeholder_communication": "Communicate status and updates"
            },
            "capabilities": {
                "task_grouping": True,
                "batch_processing": True,
                "workflow_orchestration": True,
                "priority_management": True,
                "dependency_tracking": True,
                "progress_reporting": True
            }
        }

    def _load_tasks(self) -> Dict[str, Any]:
        """Load tasks"""
        if self.tasks_file.exists():
            try:
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"⚠️  Error loading tasks: {e}")

        return {
            "tasks": [],
            "last_updated": datetime.now().isoformat(),
            "total": 0,
            "by_status": {},
            "by_priority": {},
            "by_batch": {}
        }

    def _load_batches(self) -> Dict[str, Any]:
        """Load batches"""
        if self.batches_file.exists():
            try:
                with open(self.batches_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"⚠️  Error loading batches: {e}")

        return {
            "batches": [],
            "last_updated": datetime.now().isoformat(),
            "total": 0,
            "by_status": {}
        }

    def _load_workflow_cycles(self) -> Dict[str, Any]:
        """Load workflow cycles"""
        if self.workflow_file.exists():
            try:
                with open(self.workflow_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"⚠️  Error loading workflow cycles: {e}")

        return {
            "cycles": [],
            "last_updated": datetime.now().isoformat(),
            "current_cycle": None,
            "total": 0
        }

    def _save_agent_config(self):
        """Save agent configuration"""
        self.agent_config["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.agent_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.agent_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ Error saving agent config: {e}")

    def _save_tasks(self):
        """Save tasks"""
        self.tasks["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ Error saving tasks: {e}")

    def _save_batches(self):
        """Save batches"""
        self.batches["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.batches_file, 'w', encoding='utf-8') as f:
                json.dump(self.batches, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ Error saving batches: {e}")

    def _save_workflow_cycles(self):
        """Save workflow cycles"""
        self.workflow_cycles["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.workflow_file, 'w', encoding='utf-8') as f:
                json.dump(self.workflow_cycles, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ Error saving workflow cycles: {e}")

    def organize_tasks_into_batches(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Organize related task groups into cohesive sections for @batch processing

        Groups tasks by:
        - Related functionality
        - Dependencies
        - Priority
        - Resource requirements
        """
        self.logger.info("📦 Organizing tasks into batches...")

        # Group tasks by category/functionality
        task_groups = {}
        for task in tasks:
            category = task.get("category", "uncategorized")
            if category not in task_groups:
                task_groups[category] = []
            task_groups[category].append(task)

        # Create batches from groups
        batches = []
        batch_id = 1

        for category, group_tasks in task_groups.items():
            # Sort by priority
            group_tasks.sort(key=lambda t: {
                "critical": 0, "high": 1, "medium": 2, "low": 3
            }.get(t.get("priority", "medium"), 2))

            batch = {
                "batch_id": f"BATCH-{batch_id:03d}",
                "category": category,
                "name": f"{category.replace('_', ' ').title()} Batch",
                "tasks": group_tasks,
                "status": BatchStatus.PLANNED.value,
                "priority": self._calculate_batch_priority(group_tasks),
                "created": datetime.now().isoformat(),
                "estimated_duration": self._estimate_batch_duration(group_tasks),
                "dependencies": self._extract_batch_dependencies(group_tasks),
                "resources": self._calculate_batch_resources(group_tasks)
            }

            batches.append(batch)
            batch_id += 1

        # Update batches
        self.batches["batches"] = batches
        self.batches["total"] = len(batches)
        self._save_batches()

        self.logger.info(f"✅ Organized {len(tasks)} tasks into {len(batches)} batches")

        return batches

    def _calculate_batch_priority(self, tasks: List[Dict[str, Any]]) -> str:
        """Calculate batch priority based on task priorities"""
        if not tasks:
            return "medium"

        priorities = [t.get("priority", "medium") for t in tasks]
        if "critical" in priorities:
            return "critical"
        elif "high" in priorities:
            return "high"
        elif "medium" in priorities:
            return "medium"
        else:
            return "low"

    def _estimate_batch_duration(self, tasks: List[Dict[str, Any]]) -> Optional[int]:
        """Estimate batch duration in minutes"""
        total = 0
        for task in tasks:
            duration = task.get("estimated_duration", 0)
            if duration:
                total += duration
        return total if total > 0 else None

    def _extract_batch_dependencies(self, tasks: List[Dict[str, Any]]) -> List[str]:
        """Extract batch dependencies from tasks"""
        dependencies = set()
        for task in tasks:
            task_deps = task.get("dependencies", [])
            if isinstance(task_deps, list):
                dependencies.update(task_deps)
        return list(dependencies)

    def _calculate_batch_resources(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate resource requirements for batch"""
        resources = {
            "agents": set(),
            "systems": set(),
            "tools": set()
        }

        for task in tasks:
            task_resources = task.get("resources", {})
            if isinstance(task_resources, dict):
                if "agents" in task_resources:
                    resources["agents"].update(task_resources["agents"])
                if "systems" in task_resources:
                    resources["systems"].update(task_resources["systems"])
                if "tools" in task_resources:
                    resources["tools"].update(task_resources["tools"])

        # Convert sets to lists
        return {
            "agents": list(resources["agents"]),
            "systems": list(resources["systems"]),
            "tools": list(resources["tools"])
        }

    def create_workflow_cycle(self, batches: List[Dict[str, Any]], cycle_name: str) -> Dict[str, Any]:
        """
        Create a workflow cycle from batches

        Establishes orderly commencement for @batch processing
        """
        self.logger.info(f"🔄 Creating workflow cycle: {cycle_name}")

        # Sort batches by priority and dependencies
        sorted_batches = self._sort_batches_for_execution(batches)

        cycle = {
            "cycle_id": f"CYCLE-{len(self.workflow_cycles.get('cycles', [])) + 1:03d}",
            "cycle_name": cycle_name,
            "batches": sorted_batches,
            "status": "planned",
            "created": datetime.now().isoformat(),
            "started": None,
            "completed": None,
            "total_batches": len(sorted_batches),
            "completed_batches": 0,
            "progress": 0.0
        }

        # Add to workflow cycles
        if "cycles" not in self.workflow_cycles:
            self.workflow_cycles["cycles"] = []
        self.workflow_cycles["cycles"].append(cycle)
        self.workflow_cycles["total"] = len(self.workflow_cycles["cycles"])
        self.workflow_cycles["current_cycle"] = cycle["cycle_id"]

        self._save_workflow_cycles()

        self.logger.info(f"✅ Created workflow cycle: {cycle['cycle_id']}")

        return cycle

    def _sort_batches_for_execution(self, batches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort batches for execution order"""
        # Sort by priority first
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_batches = sorted(
            batches,
            key=lambda b: priority_order.get(b.get("priority", "medium"), 2)
        )

        # Then consider dependencies
        # Simple dependency resolution (can be enhanced)
        result = []
        processed = set()

        for batch in sorted_batches:
            batch_id = batch.get("batch_id")
            dependencies = batch.get("dependencies", [])

            # Check if dependencies are satisfied
            deps_satisfied = all(dep in processed for dep in dependencies)

            if deps_satisfied or not dependencies:
                result.append(batch)
                if batch_id:
                    processed.add(batch_id)

        return result

    def update_master_todos_from_batches(self):
        """Update master todo list from organized batches"""
        if not self.tracker:
            self.logger.warning("⚠️  MasterPadawanTracker not available")
            return

        # Extract all tasks from batches
        all_tasks = []
        for batch in self.batches.get("batches", []):
            batch_tasks = batch.get("tasks", [])
            for task in batch_tasks:
                # Add batch context to task
                task_with_context = task.copy()
                task_with_context["batch_id"] = batch.get("batch_id")
                task_with_context["batch_name"] = batch.get("name")
                all_tasks.append(task_with_context)

        # Update master todos
        self.tracker.update_master_todos(all_tasks)
        self.logger.info(f"✅ Updated master todos: {len(all_tasks)} tasks")

    def get_agent_status(self) -> Dict[str, Any]:
        """Get Project Manager agent status"""
        return {
            "agent_id": self.agent_config.get("agent_id"),
            "agent_name": self.agent_config.get("agent_name"),
            "status": self.agent_config.get("status"),
            "tasks": {
                "total": self.tasks.get("total", 0),
                "by_status": self.tasks.get("by_status", {})
            },
            "batches": {
                "total": self.batches.get("total", 0),
                "by_status": self.batches.get("by_status", {})
            },
            "workflow_cycles": {
                "total": self.workflow_cycles.get("total", 0),
                "current_cycle": self.workflow_cycles.get("current_cycle")
            },
            "last_updated": datetime.now().isoformat()
        }

    def get_batch_summary(self) -> str:
        """Get formatted batch summary for display"""
        batches = self.batches.get("batches", [])
        if not batches:
            return "No batches organized yet."

        summary = []
        summary.append("## 📦 @BATCH Processing Summary")
        summary.append("")
        summary.append(f"**Total Batches:** {len(batches)}")
        summary.append("")

        for batch in batches:
            batch_id = batch.get("batch_id", "unknown")
            batch_name = batch.get("name", "Unnamed")
            status = batch.get("status", "unknown")
            priority = batch.get("priority", "medium")
            task_count = len(batch.get("tasks", []))

            priority_emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢"
            }.get(priority, "⚪")

            status_emoji = {
                "planned": "📋",
                "ready": "✅",
                "in_progress": "🔄",
                "completed": "✅",
                "failed": "❌"
            }.get(status, "❓")

            summary.append(f"### {status_emoji} {priority_emoji} {batch_id}: {batch_name}")
            summary.append(f"- **Status:** {status}")
            summary.append(f"- **Priority:** {priority}")
            summary.append(f"- **Tasks:** {task_count}")
            summary.append("")

        return "\n".join(summary)


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Project Manager AI Agent")
        parser.add_argument("--status", action="store_true", help="Show agent status")
        parser.add_argument("--organize", type=str, help="Organize tasks from JSON file")
        parser.add_argument("--batches", action="store_true", help="Show batch summary")
        parser.add_argument("--create-cycle", type=str, help="Create workflow cycle with name")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        pm_agent = ProjectManagerAgent(project_root)

        if args.status:
            status = pm_agent.get_agent_status()
            print(json.dumps(status, indent=2, default=str))

        elif args.organize:
            # Load tasks from file
            tasks_file = Path(args.organize)
            if tasks_file.exists():
                with open(tasks_file, 'r', encoding='utf-8') as f:
                    tasks = json.load(f)
                batches = pm_agent.organize_tasks_into_batches(tasks)
                print(f"✅ Organized {len(tasks)} tasks into {len(batches)} batches")
                pm_agent.update_master_todos_from_batches()
            else:
                print(f"❌ Tasks file not found: {tasks_file}")

        elif args.batches:
            summary = pm_agent.get_batch_summary()
            print(summary)

        elif args.create_cycle:
            batches = pm_agent.batches.get("batches", [])
            if batches:
                cycle = pm_agent.create_workflow_cycle(batches, args.create_cycle)
                print(f"✅ Created workflow cycle: {cycle['cycle_id']}")
            else:
                print("❌ No batches available. Organize tasks first.")

        else:
            status = pm_agent.get_agent_status()
            print(json.dumps(status, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()