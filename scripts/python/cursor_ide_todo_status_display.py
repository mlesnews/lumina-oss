#!/usr/bin/env python3
"""
Cursor IDE Todo Status Display System

Provides real-time status tracking and display for:
- @AGENT@MASTER.TODOLIST
- @SUBAGENT@PADAWAN.LIST

Quantifies with @PEAK percentages and displays in Cursor IDE UI/UX.

Features:
- Real-time status calculation
- Percentage tracking (@PEAK)
- Status file generation for Cursor IDE
- Webview panel support
- Status bar integration
"""

import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from lumina_logger import get_logger

logger = get_logger(__name__)


class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    CANCELLED = "cancelled"


@dataclass
class TodoStatusMetrics:
    """Metrics for todo status tracking"""
    total: int = 0
    pending: int = 0
    in_progress: int = 0
    complete: int = 0
    cancelled: int = 0
    percentage_complete: float = 0.0
    percentage_in_progress: float = 0.0
    high_priority: int = 0
    medium_priority: int = 0
    low_priority: int = 0
    critical_priority: int = 0


@dataclass
class MasterTodoStatus:
    """Master todo list status"""
    metrics: TodoStatusMetrics
    last_updated: str
    total_todos: int
    active_todos: int
    completed_todos: int
    peak_percentage: float  # @PEAK quantification


@dataclass
class PadawanTodoStatus:
    """Padawan/Subagent todo list status"""
    metrics: TodoStatusMetrics
    last_updated: str
    total_todos: int
    active_todos: int
    completed_todos: int
    peak_percentage: float  # @PEAK quantification
    padawan_assignments: Dict[str, int]  # Padawan -> count


@dataclass
class CursorIDEStatus:
    """Complete status for Cursor IDE display"""
    master: MasterTodoStatus
    padawan: PadawanTodoStatus
    overall_percentage: float
    timestamp: str
    status_summary: str


class CursorIDETodoStatusDisplay:
    """Cursor IDE Todo Status Display System"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.master_todos_path = self.project_root / "data" / "todo" / "master_todos.json"
        self.padawan_todos_path = self.project_root / "data" / "ask_database" / "master_padawan_todos.json"
        self.status_output_path = self.project_root / "data" / "cursor_ide_status" / "todo_status.json"
        self.status_output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info("Cursor IDE Todo Status Display initialized")
        logger.info(f"  Master todos: {self.master_todos_path}")
        logger.info(f"  Padawan todos: {self.padawan_todos_path}")
        logger.info(f"  Status output: {self.status_output_path}")

    def load_master_todos(self) -> Dict[str, Any]:
        """Load master todos from JSON"""
        try:
            if not self.master_todos_path.exists():
                logger.warning(f"Master todos file not found: {self.master_todos_path}")
                return {}

            with open(self.master_todos_path, encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading master todos: {e}")
            return {}

    def load_padawan_todos(self) -> Dict[str, Any]:
        """Load padawan todos from JSON"""
        try:
            if not self.padawan_todos_path.exists():
                logger.warning(f"Padawan todos file not found: {self.padawan_todos_path}")
                return {}

            with open(self.padawan_todos_path, encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading padawan todos: {e}")
            return {}

    def calculate_metrics(self, todos: Dict[str, Any]) -> TodoStatusMetrics:
        """Calculate metrics from todos"""
        metrics = TodoStatusMetrics()

        for todo_id, todo in todos.items():
            metrics.total += 1

            status = todo.get("status", "pending").lower()
            if status == "complete":
                metrics.complete += 1
            elif status == "in_progress":
                metrics.in_progress += 1
            elif status == "cancelled":
                metrics.cancelled += 1
            else:
                metrics.pending += 1

            priority = todo.get("priority", "medium").lower()
            if priority == "critical":
                metrics.critical_priority += 1
            elif priority == "high":
                metrics.high_priority += 1
            elif priority == "low":
                metrics.low_priority += 1
            else:
                metrics.medium_priority += 1

        # Calculate percentages
        if metrics.total > 0:
            metrics.percentage_complete = (metrics.complete / metrics.total) * 100
            metrics.percentage_in_progress = (metrics.in_progress / metrics.total) * 100

        return metrics

    def calculate_master_status(self) -> MasterTodoStatus:
        """Calculate master todo list status"""
        todos = self.load_master_todos()
        metrics = self.calculate_metrics(todos)

        # @PEAK quantification: weighted percentage
        # Complete = 100%, In Progress = 50%, Pending = 0%
        peak_percentage = (
            (metrics.complete * 100) +
            (metrics.in_progress * 50) +
            (metrics.pending * 0)
        ) / metrics.total if metrics.total > 0 else 0.0

        active_todos = metrics.in_progress + metrics.pending
        completed_todos = metrics.complete

        return MasterTodoStatus(
            metrics=metrics,
            last_updated=datetime.now().isoformat(),
            total_todos=metrics.total,
            active_todos=active_todos,
            completed_todos=completed_todos,
            peak_percentage=round(peak_percentage, 2)
        )

    def calculate_padawan_status(self) -> PadawanTodoStatus:
        """Calculate padawan/subagent todo list status"""
        todos = self.load_padawan_todos()
        metrics = self.calculate_metrics(todos)

        # Count padawan assignments
        padawan_assignments = {}
        for todo_id, todo in todos.items():
            padawan_assignee = todo.get("padawan_assignee")
            if padawan_assignee:
                padawan_assignments[padawan_assignee] = padawan_assignments.get(padawan_assignee, 0) + 1

        # @PEAK quantification
        peak_percentage = (
            (metrics.complete * 100) +
            (metrics.in_progress * 50) +
            (metrics.pending * 0)
        ) / metrics.total if metrics.total > 0 else 0.0

        active_todos = metrics.in_progress + metrics.pending
        completed_todos = metrics.complete

        return PadawanTodoStatus(
            metrics=metrics,
            last_updated=datetime.now().isoformat(),
            total_todos=metrics.total,
            active_todos=active_todos,
            completed_todos=completed_todos,
            peak_percentage=round(peak_percentage, 2),
            padawan_assignments=padawan_assignments
        )

    def generate_status_summary(self, master: MasterTodoStatus, padawan: PadawanTodoStatus) -> str:
        """Generate human-readable status summary"""
        summary_parts = []

        # Master status
        summary_parts.append(f"@AGENT@MASTER: {master.peak_percentage}% @PEAK")
        summary_parts.append(f"  Total: {master.total_todos} | Active: {master.active_todos} | Complete: {master.completed_todos}")

        # Padawan status
        summary_parts.append(f"@SUBAGENT@PADAWAN: {padawan.peak_percentage}% @PEAK")
        summary_parts.append(f"  Total: {padawan.total_todos} | Active: {padawan.active_todos} | Complete: {padawan.completed_todos}")

        # Overall
        overall = (master.peak_percentage + padawan.peak_percentage) / 2 if (master.total_todos + padawan.total_todos) > 0 else 0.0
        summary_parts.append(f"OVERALL: {overall:.1f}% @PEAK")

        return "\n".join(summary_parts)

    def get_current_status(self) -> CursorIDEStatus:
        """Get current status for Cursor IDE display"""
        master = self.calculate_master_status()
        padawan = self.calculate_padawan_status()

        # Overall percentage (weighted by total todos)
        total_todos = master.total_todos + padawan.total_todos
        if total_todos > 0:
            overall_percentage = (
                (master.peak_percentage * master.total_todos) +
                (padawan.peak_percentage * padawan.total_todos)
            ) / total_todos
        else:
            overall_percentage = 0.0

        status_summary = self.generate_status_summary(master, padawan)

        return CursorIDEStatus(
            master=master,
            padawan=padawan,
            overall_percentage=round(overall_percentage, 2),
            timestamp=datetime.now().isoformat(),
            status_summary=status_summary
        )

    def save_status_file(self, status: CursorIDEStatus) -> Path:
        """Save status to JSON file for Cursor IDE"""
        try:
            # Convert dataclasses to dicts
            status_dict = {
                "master": {
                    "metrics": asdict(status.master.metrics),
                    "last_updated": status.master.last_updated,
                    "total_todos": status.master.total_todos,
                    "active_todos": status.master.active_todos,
                    "completed_todos": status.master.completed_todos,
                    "peak_percentage": status.master.peak_percentage
                },
                "padawan": {
                    "metrics": asdict(status.padawan.metrics),
                    "last_updated": status.padawan.last_updated,
                    "total_todos": status.padawan.total_todos,
                    "active_todos": status.padawan.active_todos,
                    "completed_todos": status.padawan.completed_todos,
                    "peak_percentage": status.padawan.peak_percentage,
                    "padawan_assignments": status.padawan.padawan_assignments
                },
                "overall_percentage": status.overall_percentage,
                "timestamp": status.timestamp,
                "status_summary": status.status_summary
            }

            with open(self.status_output_path, 'w', encoding='utf-8') as f:
                json.dump(status_dict, f, indent=2, ensure_ascii=False)

            logger.info(f"Status saved to: {self.status_output_path}")
            return self.status_output_path
        except Exception as e:
            logger.error(f"Error saving status file: {e}")
            raise

    def generate_cursor_ide_status_bar_text(self, status: CursorIDEStatus) -> str:
        """Generate status bar text for Cursor IDE"""
        return f"@MASTER: {status.master.peak_percentage}% | @PADAWAN: {status.padawan.peak_percentage}% | @PEAK: {status.overall_percentage}%"

    def update_status(self) -> CursorIDEStatus:
        """Update and save current status"""
        status = self.get_current_status()
        self.save_status_file(status)

        # PROJECT MANAGER: Generate JSONC files as part of permanent workflow
        try:
            from generate_todolist_jsonc import TodoListJSONCGenerator
            jsonc_generator = TodoListJSONCGenerator(self.project_root)
            jsonc_generator.sync_all_todolists()
            logger.info("✅ JSONC files generated as part of permanent workflow")
        except Exception as e:
            logger.warning(f"⚠️  JSONC generation skipped: {e}")

        # Print status summary
        print("=" * 80)
        print("📊 CURSOR IDE TODO STATUS")
        print("=" * 80)
        print(status.status_summary)
        print("=" * 80)
        print(f"Status file: {self.status_output_path}")
        print(f"Status bar text: {self.generate_cursor_ide_status_bar_text(status)}")
        print("=" * 80)

        return status


def main():
    try:
        """Main entry point"""
        project_root = Path(__file__).parent.parent.parent
        display = CursorIDETodoStatusDisplay(project_root)
        status = display.update_status()

        return status


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()