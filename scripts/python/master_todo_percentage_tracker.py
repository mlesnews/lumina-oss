#!/usr/bin/env python3
"""
Master Todo Percentage Tracker

Updates master_todos.json with live percentage (0-100%) tracking.
Provides real-time progress updates for all todos.

Tags: #TODO #PERCENTAGE #TRACKING #LIVE #REQUIRED @JARVIS @LUMINA @DOIT  # [ADDRESSED]  # [ADDRESSED]
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

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

logger = get_logger("MasterTodoPercentageTracker")


class MasterTodoPercentageTracker:
    """
    Track and update percentage (0-100%) for todos in master_todos.json
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize percentage tracker"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.master_todos_file = self.project_root / "data" / "todo" / "master_todos.json"

        logger.info("=" * 80)
        logger.info("📊 MASTER TODO PERCENTAGE TRACKER")
        logger.info("=" * 80)
        logger.info("   Live percentage (0-100%) tracking for all todos")
        logger.info("=" * 80)

    def load_todos(self) -> Dict[str, Any]:
        try:
            """Load master todos"""
            if not self.master_todos_file.exists():
                logger.warning(f"⚠️  Master todos file not found: {self.master_todos_file}")
                return {}

            with open(self.master_todos_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            self.logger.error(f"Error in load_todos: {e}", exc_info=True)
            raise
    def save_todos(self, todos: Dict[str, Any]):
        try:
            """Save master todos"""
            with open(self.master_todos_file, 'w', encoding='utf-8') as f:
                json.dump(todos, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in save_todos: {e}", exc_info=True)
            raise
    def update_percentage(
        self,
        todo_id: str,
        percentage: float,
        notes: Optional[str] = None
    ) -> bool:
        """
        Update percentage for a todo

        Args:
            todo_id: Todo ID
            percentage: Percentage (0-100)
            notes: Optional notes about the update

        Returns:
            True if updated successfully
        """
        if percentage < 0 or percentage > 100:
            logger.error(f"❌ Invalid percentage: {percentage}. Must be 0-100")
            return False

        todos = self.load_todos()

        if todo_id not in todos:
            logger.warning(f"⚠️  Todo not found: {todo_id}")
            return False

        todo = todos[todo_id]

        # Update percentage
        todo['percentage'] = round(percentage, 2)
        todo['updated_date'] = datetime.now().isoformat()

        # Update status based on percentage
        if percentage >= 100:
            todo['status'] = 'complete'
            if not todo.get('completed_date'):
                todo['completed_date'] = datetime.now().isoformat()
        elif percentage > 0:
            todo['status'] = 'in_progress'
        else:
            todo['status'] = 'pending'

        # Add note if provided
        if notes:
            if 'notes' not in todo:
                todo['notes'] = []
            todo['notes'].append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {notes} (Progress: {percentage}%)")

        # Save
        self.save_todos(todos)

        logger.info(f"✅ Updated todo {todo_id}: {percentage}%")
        return True

    def get_percentage(self, todo_id: str) -> Optional[float]:
        """Get current percentage for a todo"""
        todos = self.load_todos()

        if todo_id not in todos:
            return None

        return todos[todo_id].get('percentage', 0.0)

    def calculate_percentage_from_status(self, todo_id: str) -> float:
        """
        Calculate percentage based on todo status

        Returns:
            Calculated percentage (0-100)
        """
        todos = self.load_todos()

        if todo_id not in todos:
            return 0.0

        todo = todos[todo_id]
        status = todo.get('status', 'pending')

        if status == 'complete':
            return 100.0
        elif status == 'in_progress':
            # If already has percentage, use it; otherwise estimate
            if 'percentage' in todo:
                return todo['percentage']
            return 50.0  # Default for in_progress
        else:
            return 0.0

    def add_todo_with_percentage(
        self,
        title: str,
        description: str,
        percentage: float = 0.0,
        priority: str = "medium",
        category: str = "system_integration",
        tags: Optional[list] = None
    ) -> str:
        """
        Add a new todo with percentage tracking

        Returns:
            Todo ID
        """
        import hashlib

        # Generate ID from title
        todo_id = hashlib.md5(title.encode()).hexdigest()[:16]

        todos = self.load_todos()

        # Check if already exists
        for existing_id, existing_todo in todos.items():
            if existing_todo.get('title') == title:
                logger.info(f"ℹ️  Todo already exists: {existing_id}")
                return existing_id

        # Create new todo
        new_todo = {
            "id": todo_id,
            "title": title,
            "description": description,
            "status": "pending" if percentage == 0 else "in_progress",
            "priority": priority,
            "category": category,
            "created_date": datetime.now().isoformat(),
            "updated_date": datetime.now().isoformat(),
            "completed_date": None if percentage < 100 else datetime.now().isoformat(),
            "assignee": None,
            "tags": tags or [],
            "dependencies": [],
            "notes": [],
            "metadata": {},
            "percentage": round(percentage, 2)
        }

        todos[todo_id] = new_todo
        self.save_todos(todos)

        logger.info(f"✅ Added todo: {todo_id} ({title}) - {percentage}%")
        return todo_id


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Master Todo Percentage Tracker")
    parser.add_argument("--todo-id", type=str, help="Todo ID to update")
    parser.add_argument("--percentage", type=float, help="Percentage (0-100)")
    parser.add_argument("--notes", type=str, help="Notes about the update")
    parser.add_argument("--add", action="store_true", help="Add new todo")
    parser.add_argument("--title", type=str, help="Todo title (for --add)")
    parser.add_argument("--description", type=str, help="Todo description (for --add)")
    args = parser.parse_args()

    tracker = MasterTodoPercentageTracker()

    if args.add:
        if not args.title:
            logger.error("❌ --title required for --add")
            sys.exit(1)

        todo_id = tracker.add_todo_with_percentage(
            title=args.title,
            description=args.description or "",
            percentage=args.percentage or 0.0
        )
        logger.info(f"✅ Created todo: {todo_id}")
    elif args.todo_id and args.percentage is not None:
        tracker.update_percentage(args.todo_id, args.percentage, args.notes)
    else:
        logger.error("❌ Must provide --todo-id and --percentage, or --add with --title")
