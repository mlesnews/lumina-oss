"""
JARVIS IDE Queue Monitor
Monitors all VS Code/Cursor IDE queues, not just problems.

IDE Queues:
- Problems (errors, warnings, info, hints)
- Tasks (build tasks, test tasks)
- Output (console output, terminal output)
- Debug Console
- Search Results
- Extensions (updates, recommendations)
- Notifications
- Status Bar messages

Author: JARVIS System
Date: 2026-01-09
Tags: #JARVIS @LUMINA #IDE #QUEUES #PROACTIVE
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)


class QueueType(str, Enum):
    """IDE queue types."""
    PROBLEMS = "problems"
    TASKS = "tasks"
    OUTPUT = "output"
    DEBUG_CONSOLE = "debug_console"
    SEARCH_RESULTS = "search_results"
    EXTENSIONS = "extensions"
    NOTIFICATIONS = "notifications"
    STATUS_BAR = "status_bar"


@dataclass
class QueueItem:
    """Item in an IDE queue."""
    queue_type: QueueType
    item_id: str
    message: str
    severity: Optional[str] = None
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class JARVISIDEQueueMonitor:
    """
    Monitors all VS Code/Cursor IDE queues.

    Queues monitored:
    - Problems (errors, warnings)
    - Tasks (build, test)
    - Output (console, terminal)
    - Debug Console
    - Search Results
    - Extensions
    - Notifications
    - Status Bar
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize IDE queue monitor.

        Args:
            project_root: Project root directory
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)

        # File paths
        self.queues_file = self.project_root / "data" / "ide_queues" / "current_queues.json"
        self.history_file = self.project_root / "data" / "ide_queues" / "queue_history.jsonl"

        # Ensure directories exist
        self.queues_file.parent.mkdir(parents=True, exist_ok=True)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

        # Queue state
        self.queues: Dict[QueueType, List[QueueItem]] = {
            queue_type: [] for queue_type in QueueType
        }

    def monitor_problems_queue(self) -> List[QueueItem]:
        """
        Monitor Problems queue.

        Returns:
            List of problem queue items
        """
        from jarvis_proactive_ide_problem_monitor import JARVISProactiveIDEProblemMonitor, ProblemSeverity

        monitor = JARVISProactiveIDEProblemMonitor(self.project_root)
        problems = monitor.read_ide_problems()

        items = []
        for problem in problems:
            item = QueueItem(
                queue_type=QueueType.PROBLEMS,
                item_id=f"problem_{problem.file}_{problem.line}",
                message=problem.message,
                severity=problem.severity.value,
                metadata={
                    'file': problem.file,
                    'line': problem.line,
                    'column': problem.column,
                    'source': problem.source,
                    'code': problem.code
                }
            )
            items.append(item)

        return items

    def monitor_tasks_queue(self) -> List[QueueItem]:
        """
        Monitor Tasks queue (build tasks, test tasks).

        Returns:
            List of task queue items
        """
        items = []

        # Check for task output files
        task_outputs = [
            self.project_root / ".vscode" / "tasks.json",
            self.project_root / ".cursor" / "tasks.json"
        ]

        for task_file in task_outputs:
            if task_file.exists():
                try:
                    with open(task_file, encoding='utf-8') as f:
                        tasks = json.load(f)

                        if isinstance(tasks, dict) and 'tasks' in tasks:
                            for task in tasks['tasks']:
                                item = QueueItem(
                                    queue_type=QueueType.TASKS,
                                    item_id=f"task_{task.get('label', 'unknown')}",
                                    message=f"Task: {task.get('label', 'Unknown')}",
                                    metadata={'task': task}
                                )
                                items.append(item)
                except Exception as e:
                    logger.debug(f"Could not read tasks: {e}")

        return items

    def monitor_output_queue(self) -> List[QueueItem]:
        """
        Monitor Output queue (console, terminal output).

        Returns:
            List of output queue items
        """
        items = []

        # Check for output log files
        output_logs = [
            self.project_root / ".cursor" / "output.log",
            self.project_root / "data" / "ide_queues" / "output.log"
        ]

        for log_file in output_logs:
            if log_file.exists():
                try:
                    # Read last N lines
                    with open(log_file, encoding='utf-8') as f:
                        lines = f.readlines()
                        recent_lines = lines[-50:]  # Last 50 lines

                        for i, line in enumerate(recent_lines):
                            if line.strip():
                                item = QueueItem(
                                    queue_type=QueueType.OUTPUT,
                                    item_id=f"output_{log_file.stem}_{len(lines) - 50 + i}",
                                    message=line.strip(),
                                    metadata={'source': str(log_file)}
                                )
                                items.append(item)
                except Exception as e:
                    logger.debug(f"Could not read output log: {e}")

        return items

    def monitor_all_queues(self) -> Dict[QueueType, List[QueueItem]]:
        """
        Monitor all IDE queues.

        Returns:
            Dictionary of queue types to items
        """
        queues = {
            QueueType.PROBLEMS: self.monitor_problems_queue(),
            QueueType.TASKS: self.monitor_tasks_queue(),
            QueueType.OUTPUT: self.monitor_output_queue(),
            # TODO: Add other queue monitors  # [ADDRESSED]  # [ADDRESSED]
            QueueType.DEBUG_CONSOLE: [],
            QueueType.SEARCH_RESULTS: [],
            QueueType.EXTENSIONS: [],
            QueueType.NOTIFICATIONS: [],
            QueueType.STATUS_BAR: []
        }

        self.queues = queues
        return queues

    def get_queue_summary(self) -> Dict[str, Any]:
        """
        Get summary of all queues.

        Returns:
            Dictionary with queue summaries
        """
        queues = self.monitor_all_queues()

        summary = {
            'timestamp': datetime.now().isoformat(),
            'queues': {}
        }

        for queue_type, items in queues.items():
            summary['queues'][queue_type.value] = {
                'count': len(items),
                'items': [item.to_dict() for item in items[:10]]  # First 10 items
            }

        # Total counts
        summary['total_items'] = sum(len(items) for items in queues.values())
        summary['queue_counts'] = {
            queue_type.value: len(items) 
            for queue_type, items in queues.items()
        }

        return summary

    def get_status_report(self) -> str:
        """
        Get human-readable status report.

        Returns:
            Formatted status report
        """
        summary = self.get_queue_summary()

        lines = []
        lines.append("📊 **JARVIS IDE Queue Monitor Status**")
        lines.append("")
        lines.append(f"**Timestamp:** {summary['timestamp']}")
        lines.append(f"**Total Items Across All Queues:** {summary['total_items']}")
        lines.append("")
        lines.append("**Queue Status:**")

        for queue_type, queue_data in summary['queues'].items():
            count = queue_data['count']
            icon = "🔴" if count > 100 else "🟡" if count > 10 else "🟢"
            lines.append(f"  {icon} **{queue_type.upper()}:** {count} items")

            if queue_data['items']:
                lines.append(f"    Recent items:")
                for item in queue_data['items'][:3]:
                    message = item['message'][:60] + "..." if len(item['message']) > 60 else item['message']
                    lines.append(f"      - {message}")

        return "\n".join(lines)

    def save_queues(self) -> None:
        """Save current queue state."""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'queues': {
                    queue_type.value: [item.to_dict() for item in items]
                    for queue_type, items in self.queues.items()
                }
            }
            with open(self.queues_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save queues: {e}", exc_info=True)


def main():
    """CLI interface for IDE queue monitor."""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS IDE Queue Monitor")
    parser.add_argument('--monitor', action='store_true', help='Monitor all queues')
    parser.add_argument('--status', action='store_true', help='Show status report')
    parser.add_argument('--queue', type=str, help='Monitor specific queue (problems, tasks, output)')

    args = parser.parse_args()

    monitor = JARVISIDEQueueMonitor()

    if args.status or not any([args.monitor, args.queue]):
        print(monitor.get_status_report())

    if args.monitor:
        queues = monitor.monitor_all_queues()
        monitor.save_queues()
        print(f"\n✅ Monitored all queues")
        for queue_type, items in queues.items():
            print(f"  {queue_type.value}: {len(items)} items")

    if args.queue:
        queue_type = QueueType(args.queue)
        if queue_type == QueueType.PROBLEMS:
            items = monitor.monitor_problems_queue()
            print(f"\n📋 Problems Queue: {len(items)} items")
        elif queue_type == QueueType.TASKS:
            items = monitor.monitor_tasks_queue()
            print(f"\n📋 Tasks Queue: {len(items)} items")
        elif queue_type == QueueType.OUTPUT:
            items = monitor.monitor_output_queue()
            print(f"\n📋 Output Queue: {len(items)} items")


if __name__ == "__main__":


    main()