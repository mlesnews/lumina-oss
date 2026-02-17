#!/usr/bin/env python3
"""
Master To-Do Tracker - Comprehensive Task Management

Tracks all requests, tasks, and progress from development to production.
Integrates with existing systems for comprehensive tracking.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class TaskStatus(Enum):
    """Task status"""
    COMPLETE = "complete"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class Priority(Enum):
    """Task priority"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class TodoItem:
    """To-do item"""
    id: str
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: Priority = Priority.MEDIUM
    category: str = ""
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_date: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_date: Optional[str] = None
    assignee: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        data["priority"] = self.priority.value
        return data


class MasterTodoTracker:
    """
    Master To-Do Tracker

    Comprehensive task tracking from development to production.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "todo"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.todo_file = self.data_dir / "master_todos.json"
        self.items: Dict[str, TodoItem] = {}

        self.logger = self._setup_logging()
        self._load_todos()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("MasterTodoTracker")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - 📋 %(name)s - %(levelname)s - %(message)s'
            ))
            logger.addHandler(handler)

        return logger

    def _load_todos(self):
        """Load todos from file"""
        if self.todo_file.exists():
            try:
                with open(self.todo_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.items = {
                        item_id: TodoItem(
                            **{**item_data, 'status': TaskStatus(item_data['status']), 
                               'priority': Priority(item_data['priority'])}
                        )
                        for item_id, item_data in data.items()
                    }
                self.logger.info(f"✅ Loaded {len(self.items)} todos")
            except Exception as e:
                self.logger.error(f"❌ Error loading todos: {e}")
                self.items = {}
        else:
            self.items = {}
            self.logger.info("📋 Starting fresh todo list")

    def _save_todos(self):
        """Save todos to file"""
        try:
            data = {item_id: item.to_dict() for item_id, item in self.items.items()}
            with open(self.todo_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"💾 Saved {len(self.items)} todos")
        except Exception as e:
            self.logger.error(f"❌ Error saving todos: {e}")

    def add_todo(self, title: str, description: str = "", category: str = "",
                 priority: Priority = Priority.MEDIUM, status: TaskStatus = TaskStatus.PENDING,
                 tags: List[str] = None, dependencies: List[str] = None) -> str:
        """Add a new todo item"""
        import hashlib

        todo_id = hashlib.md5(f"{title}{datetime.now().isoformat()}".encode()).hexdigest()[:16]

        item = TodoItem(
            id=todo_id,
            title=title,
            description=description,
            category=category,
            priority=priority,
            status=status,
            tags=tags or [],
            dependencies=dependencies or []
        )

        self.items[todo_id] = item
        self._save_todos()

        self.logger.info(f"➕ Added todo: {title} ({todo_id})")
        return todo_id

    def update_status(self, todo_id: str, status: TaskStatus):
        """Update todo status"""
        if todo_id not in self.items:
            self.logger.warning(f"⚠️ Todo not found: {todo_id}")
            return

        item = self.items[todo_id]
        item.status = status
        item.updated_date = datetime.now().isoformat()

        if status == TaskStatus.COMPLETE:
            item.completed_date = datetime.now().isoformat()

        self._save_todos()
        self.logger.info(f"🔄 Updated {item.title}: {status.value}")

    def get_todos(self, status: Optional[TaskStatus] = None,
                  category: Optional[str] = None,
                  priority: Optional[Priority] = None) -> List[TodoItem]:
        """Get todos with optional filtering"""
        todos = list(self.items.values())

        if status:
            todos = [t for t in todos if t.status == status]

        if category:
            todos = [t for t in todos if t.category == category]

        if priority:
            todos = [t for t in todos if t.priority == priority]

        # Sort by priority (high first), then by created date
        todos.sort(key=lambda t: (
            {'high': 0, 'medium': 1, 'low': 2}.get(t.priority.value, 3),
            t.created_date
        ))

        return todos

    def get_stats(self) -> Dict[str, Any]:
        """Get todo statistics"""
        total = len(self.items)
        complete = len([t for t in self.items.values() if t.status == TaskStatus.COMPLETE])
        in_progress = len([t for t in self.items.values() if t.status == TaskStatus.IN_PROGRESS])
        pending = len([t for t in self.items.values() if t.status == TaskStatus.PENDING])

        return {
            'total': total,
            'complete': complete,
            'in_progress': in_progress,
            'pending': pending,
            'completion_rate': (complete / total * 100) if total > 0 else 0
        }

    def generate_report(self) -> str:
        """Generate todo report"""
        stats = self.get_stats()

        report = []
        report.append("# Master To-Do Report")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")
        report.append("## Statistics")
        report.append(f"- Total: {stats['total']}")
        report.append(f"- Complete: {stats['complete']} ({stats['completion_rate']:.1f}%)")
        report.append(f"- In Progress: {stats['in_progress']}")
        report.append(f"- Pending: {stats['pending']}")
        report.append("")

        # By status
        for status in TaskStatus:
            todos = self.get_todos(status=status)
            if todos:
                report.append(f"## {status.value.upper().replace('_', ' ')}")
                for todo in todos:
                    report.append(f"- [{todo.priority.value.upper()}] {todo.title}")
                    if todo.description:
                        report.append(f"  - {todo.description}")
                report.append("")

        return "\n".join(report)


def main():
    try:
        """Main execution"""
        tracker = MasterTodoTracker()

        print("📋 Master To-Do Tracker")
        print("=" * 80)

        # Load session requests
        print("\n📋 Loading session todos...")

        # Video Production todos
        tracker.add_todo(
            "Create trailer videos for pilot episode",
            "Created 8 video files using FFmpeg",
            category="video_production",
            status=TaskStatus.COMPLETE,
            priority=Priority.HIGH
        )

        tracker.add_todo(
            "SYPHON video/audio breakdown system",
            "Breaks down videos into building blocks, extracts @ask-requested patterns",
            category="video_production",
            status=TaskStatus.COMPLETE,
            priority=Priority.HIGH
        )

        tracker.add_todo(
            "Enhance video quality",
            "Add visuals, animations, music to trailers",
            category="video_production",
            status=TaskStatus.IN_PROGRESS,
            priority=Priority.HIGH
        )

        tracker.add_todo(
            "Create pilot episode segments",
            "Generate content segments for 40-60 minute episodes",
            category="video_production",
            status=TaskStatus.PENDING,
            priority=Priority.MEDIUM
        )

        tracker.add_todo(
            "Git/GitLens Integration",
            "Complete Git/GitLens configuration and automation",
            category="system_integration",
            status=TaskStatus.COMPLETE,
            priority=Priority.HIGH
        )

        tracker.add_todo(
            "Master To-Do List System",
            "Comprehensive tracking of all requests",
            category="system_integration",
            status=TaskStatus.IN_PROGRESS,
            priority=Priority.HIGH
        )

        # Generate report
        print("\n📊 Statistics:")
        stats = tracker.get_stats()
        print(f"   Total: {stats['total']}")
        print(f"   Complete: {stats['complete']} ({stats['completion_rate']:.1f}%)")
        print(f"   In Progress: {stats['in_progress']}")
        print(f"   Pending: {stats['pending']}")

        # Save report
        report_file = tracker.project_root / "MASTER_TODO_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(tracker.generate_report())

        print(f"\n✅ Report saved to: {report_file}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()