#!/usr/bin/env python3
"""
Jedi Master Outstanding Tracker - B.A.U (Business As Usual)

Scans all workflows, stages, phases, and extracts outstanding items.
Tracks everything on Master Todo List and Standard Todo List.
Integrated with Jedi Master Padawan system and all workflows.
"""

import sys
import json
import importlib
import inspect
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from master_todo_tracker import MasterTodoTracker, TodoItem, TaskStatus, Priority
    from dual_todo_system import DualTodoSystem
    from jarvis_jedi_master import JarvisJediMaster
    from workflow_base import WorkflowBase
except ImportError as e:
    print(f"Import error: {e}")

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JediMasterOutstandingTracker")


@dataclass
class OutstandingItem:
    """Outstanding item from workflow/stage/phase"""
    item_id: str
    title: str
    description: str = ""
    source: str = ""  # workflow name
    source_type: str = ""  # "step", "stage", "phase", "task"
    status: str = "pending"
    priority: str = "medium"
    metadata: Dict[str, Any] = field(default_factory=dict)


class JediMasterOutstandingTracker:
    """
    Jedi Master Outstanding Tracker - B.A.U

    Scans all workflows and extracts outstanding items.
    Tracks on Master Todo List and Standard Todo List.
    Integrated with Jedi Master Padawan system.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "jedi_academy" / "outstanding"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger = get_logger("JediMasterOutstandingTracker")

        # Initialize systems
        self.dual_todo_system = DualTodoSystem(project_root)
        self.master_tracker = self.dual_todo_system.master_tracker

        # Jedi Master (optional, for guidance)
        try:
            self.jedi_master = JarvisJediMaster()
        except Exception as e:
            self.logger.warning(f"Jedi Master not available: {e}")
            self.jedi_master = None

        # Outstanding items
        self.outstanding_items: List[OutstandingItem] = []

    def scan_all_workflows(self) -> List[OutstandingItem]:
        """Scan all workflows for outstanding items"""
        self.logger.info("=" * 70)
        self.logger.info("JEDI MASTER: Scanning All Workflows for Outstanding Items")
        self.logger.info("=" * 70)
        self.logger.info("")

        outstanding_items = []

        # Find all workflow files
        workflows_dir = self.project_root / "scripts" / "python"
        workflow_files = list(workflows_dir.glob("*workflow*.py"))

        self.logger.info(f"Found {len(workflow_files)} workflow files")

        for workflow_file in workflow_files:
            try:
                # Try to load and analyze workflow
                items = self._analyze_workflow_file(workflow_file)
                outstanding_items.extend(items)
                self.logger.info(f"  ✓ {workflow_file.name}: {len(items)} outstanding items")
            except Exception as e:
                self.logger.debug(f"  ⚠ {workflow_file.name}: {e}")

        # Scan workflow data directories
        workflow_data_items = self._scan_workflow_data()
        outstanding_items.extend(workflow_data_items)

        self.outstanding_items = outstanding_items

        self.logger.info("")
        self.logger.info(f"Total outstanding items found: {len(outstanding_items)}")
        self.logger.info("=" * 70)

        return outstanding_items

    def _analyze_workflow_file(self, workflow_file: Path) -> List[OutstandingItem]:
        """Analyze a workflow file for outstanding items"""
        items = []

        try:
            # Read file content
            content = workflow_file.read_text(encoding='utf-8', errors='ignore')

            # Look for TODO comments, pending steps, stages, phases
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                line_lower = line.lower()

                # Check for TODO/FIXME/HACK comments
                if any(marker in line_lower for marker in ['todo', 'fixme', 'hack', 'xxx']):
                    if 'todo' in line_lower or 'fixme' in line_lower:
                        # Extract todo text
                        todo_text = line.split('#')[-1].strip() if '#' in line else line.strip()
                        todo_text = todo_text.replace('TODO:', '').replace('FIXME:', '').strip()

                        if todo_text and len(todo_text) > 5:
                            items.append(OutstandingItem(
                                item_id=f"{workflow_file.stem}_todo_{i}",
                                title=f"TODO: {todo_text[:100]}",
                                description=f"From {workflow_file.name}:{i}",
                                source=workflow_file.stem,
                                source_type="todo_comment",
                                status="pending",
                                priority="medium",
                                metadata={"file": str(workflow_file), "line": i}
                            ))

                # Check for pending/outstanding status
                if any(word in line_lower for word in ['pending', 'outstanding', 'incomplete', 'not done']):
                    # Look for step/stage/phase markers
                    if any(marker in line_lower for marker in ['step', 'stage', 'phase']):
                        items.append(OutstandingItem(
                            item_id=f"{workflow_file.stem}_pending_{i}",
                            title=f"Pending: {line.strip()[:100]}",
                            description=f"From {workflow_file.name}:{i}",
                            source=workflow_file.stem,
                            source_type="pending_item",
                            status="pending",
                            priority="medium",
                            metadata={"file": str(workflow_file), "line": i}
                        ))

        except Exception as e:
            self.logger.debug(f"Error analyzing {workflow_file}: {e}")

        return items

    def _scan_workflow_data(self) -> List[OutstandingItem]:
        """Scan workflow data directories for outstanding items"""
        items = []

        # Scan workflow data directories
        data_dir = self.project_root / "data"

        # Common workflow data patterns
        patterns = [
            "**/workflows/**/*.json",
            "**/workflow_results/**/*.json",
            "**/execution_results/**/*.json",
            "**/pending/**/*.json"
        ]

        for pattern in patterns:
            for data_file in data_dir.glob(pattern):
                try:
                    with open(data_file, 'r') as f:
                        data = json.load(f)

                    # Check for pending/outstanding status
                    if isinstance(data, dict):
                        status = data.get("status", "").lower()
                        workflow_status = data.get("workflow_status", "").lower()

                        if any(s in ["pending", "in_progress", "outstanding", "incomplete"] 
                               for s in [status, workflow_status]):

                            # Extract outstanding items
                            if "steps" in data:
                                for step in data["steps"]:
                                    step_status = step.get("status", "").lower()
                                    if step_status in ["pending", "incomplete", "not_started"]:
                                        items.append(OutstandingItem(
                                            item_id=f"{data_file.stem}_step_{step.get('id', 'unknown')}",
                                            title=f"Outstanding Step: {step.get('name', 'Unknown')}",
                                            description=f"From {data_file.name}",
                                            source=data_file.stem,
                                            source_type="workflow_step",
                                            status="pending",
                                            priority="medium",
                                            metadata={"file": str(data_file), "step": step}
                                        ))

                            # Extract stages/phases
                            if "stages" in data:
                                for stage in data["stages"]:
                                    stage_status = stage.get("status", "").lower()
                                    if stage_status in ["pending", "incomplete"]:
                                        items.append(OutstandingItem(
                                            item_id=f"{data_file.stem}_stage_{stage.get('id', 'unknown')}",
                                            title=f"Outstanding Stage: {stage.get('name', 'Unknown')}",
                                            description=f"From {data_file.name}",
                                            source=data_file.stem,
                                            source_type="workflow_stage",
                                            status="pending",
                                            priority="medium",
                                            metadata={"file": str(data_file), "stage": stage}
                                        ))

                            if "phases" in data:
                                for phase in data["phases"]:
                                    phase_status = phase.get("status", "").lower()
                                    if phase_status in ["pending", "incomplete"]:
                                        items.append(OutstandingItem(
                                            item_id=f"{data_file.stem}_phase_{phase.get('id', 'unknown')}",
                                            title=f"Outstanding Phase: {phase.get('phase', 'Unknown')}",
                                            description=f"From {data_file.name}",
                                            source=data_file.stem,
                                            source_type="workflow_phase",
                                            status="pending",
                                            priority="high",
                                            metadata={"file": str(data_file), "phase": phase}
                                        ))

                except Exception as e:
                    self.logger.debug(f"Error scanning {data_file}: {e}")

        return items

    def track_outstanding_items(self) -> Dict[str, Any]:
        """Track all outstanding items on Master and Standard Todo Lists"""
        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("TRACKING OUTSTANDING ITEMS - B.A.U")
        self.logger.info("=" * 70)
        self.logger.info("")

        if not self.outstanding_items:
            self.scan_all_workflows()

        results = {
            "timestamp": datetime.now().isoformat(),
            "items_scanned": len(self.outstanding_items),
            "items_tracked": 0,
            "items_skipped": 0,
            "master_todos_added": [],
            "standard_todos_added": []
        }

        # Track each outstanding item
        for item in self.outstanding_items:
            try:
                # Determine priority
                priority = Priority.HIGH if item.priority == "high" else (
                    Priority.MEDIUM if item.priority == "medium" else Priority.LOW
                )

                # Add to Master Todo List
                todo_id = self.master_tracker.add_todo(
                    title=item.title,
                    description=item.description,
                    category=f"{item.source_type}_{item.source}",
                    priority=priority,
                    status=TaskStatus.PENDING,
                    tags=[item.source_type, item.source, "outstanding", "jedi_master"],
                    dependencies=[]
                )

                results["items_tracked"] += 1
                results["master_todos_added"].append({
                    "todo_id": todo_id,
                    "title": item.title,
                    "source": item.source,
                    "source_type": item.source_type
                })

                self.logger.info(f"  ✓ Tracked: {item.title[:60]}...")

            except Exception as e:
                self.logger.warning(f"  ⚠ Error tracking {item.item_id}: {e}")
                results["items_skipped"] += 1

        # Save results
        results_file = self.data_dir / f"tracking_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)

        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("TRACKING COMPLETE")
        self.logger.info("=" * 70)
        self.logger.info(f"Items scanned: {results['items_scanned']}")
        self.logger.info(f"Items tracked: {results['items_tracked']}")
        self.logger.info(f"Items skipped: {results['items_skipped']}")
        self.logger.info("=" * 70)

        return results

    def get_outstanding_summary(self) -> Dict[str, Any]:
        """Get summary of outstanding items"""
        if not self.outstanding_items:
            self.scan_all_workflows()

        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_outstanding": len(self.outstanding_items),
            "by_source_type": {},
            "by_source": {},
            "by_priority": {
                "high": len([i for i in self.outstanding_items if i.priority == "high"]),
                "medium": len([i for i in self.outstanding_items if i.priority == "medium"]),
                "low": len([i for i in self.outstanding_items if i.priority == "low"])
            }
        }

        # Group by source type
        for item in self.outstanding_items:
            summary["by_source_type"][item.source_type] = summary["by_source_type"].get(item.source_type, 0) + 1
            summary["by_source"][item.source] = summary["by_source"].get(item.source, 0) + 1

        return summary

    def execute_all_outstanding(self) -> Dict[str, Any]:
        """Execute all outstanding items (B.A.U - Business As Usual)"""
        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("EXECUTING ALL OUTSTANDING ITEMS - B.A.U")
        self.logger.info("=" * 70)
        self.logger.info("")

        if not self.outstanding_items:
            self.scan_all_workflows()

        # Track first
        tracking_results = self.track_outstanding_items()

        execution_results = {
            "timestamp": datetime.now().isoformat(),
            "outstanding_items": len(self.outstanding_items),
            "tracked_on_master_todo": tracking_results["items_tracked"],
            "execution_plan": "All outstanding items tracked on Master Todo List",
            "next_steps": [
                "Review Master Todo List",
                "Prioritize items",
                "Execute high priority items first",
                "Update status as items are completed"
            ]
        }

        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("B.A.U EXECUTION COMPLETE")
        self.logger.info("=" * 70)
        self.logger.info("All outstanding items have been tracked on Master Todo List")
        self.logger.info("Review and execute items from Master Todo List")
        self.logger.info("=" * 70)

        return execution_results


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Jedi Master Outstanding Tracker - B.A.U")
        parser.add_argument(
            "--scan",
            action="store_true",
            help="Scan all workflows for outstanding items"
        )
        parser.add_argument(
            "--track",
            action="store_true",
            help="Track outstanding items on Master Todo List"
        )
        parser.add_argument(
            "--execute",
            action="store_true",
            help="Execute all outstanding items (B.A.U)"
        )
        parser.add_argument(
            "--summary",
            action="store_true",
            help="Show outstanding items summary"
        )

        args = parser.parse_args()

        tracker = JediMasterOutstandingTracker()

        if args.scan:
            items = tracker.scan_all_workflows()
            logger.info(f"Scanned {len(items)} outstanding items")

        if args.track:
            results = tracker.track_outstanding_items()
            logger.info(f"Tracked {results['items_tracked']} items on Master Todo List")

        if args.summary:
            summary = tracker.get_outstanding_summary()
            print(json.dumps(summary, indent=2, ensure_ascii=False))

        if args.execute:
            results = tracker.execute_all_outstanding()
            logger.info("B.A.U execution complete - all items tracked")

        # Default: execute all
        if not any([args.scan, args.track, args.execute, args.summary]):
            results = tracker.execute_all_outstanding()
            logger.info("B.A.U execution complete - all items tracked")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    sys.exit(main())