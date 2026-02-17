#!/usr/bin/env python3
"""
Cursor IDE Master Todo List Display
Displays @AGENT@MASTER.TODOLIST in Cursor IDE chat window

Integrates with existing session-scoped (OEM/Padawan) todo list display.
Shows master todos alongside session todos in the chat UI.

Tags: #CURSOR #IDE #UI #UX #MASTER #TODO #DISPLAY  # [ADDRESSED]  # [ADDRESSED]
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
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
    # Fallback if tracker not available
    MasterPadawanTracker = None

logger = get_logger("CursorIDEMasterTodo")


class CursorIDEMasterTodoDisplay:
    """
    Cursor IDE Master Todo List Display

    Displays master todo list in Cursor IDE chat window.
    Integrates with existing session-scoped todo list.
    """

    def __init__(self, project_root: Path):
        """Initialize display system"""
        self.project_root = project_root
        self.logger = logger

        # Initialize tracker
        if MasterPadawanTracker:
            self.tracker = MasterPadawanTracker(project_root)
        else:
            self.tracker = None
            self.logger.warning("⚠️  MasterPadawanTracker not available")

        self.logger.info("💬 Cursor IDE Master Todo Display initialized")

    def get_master_todo_markdown(self, include_completed: bool = False) -> str:
        """
        Get master todo list formatted for Cursor IDE chat markdown display

        Returns markdown formatted string that can be displayed in chat window.
        """
        if not self.tracker:
            return "⚠️ Master Padawan Tracker not available"

        # Get master todos
        master_todos = self.tracker.master_todos.get("todos", [])

        # Filter by status
        if not include_completed:
            master_todos = [t for t in master_todos if t.get("status") != "completed"]

        # Get stats
        stats = {
            "total": self.tracker.master_todos.get("total", 0),
            "pending": self.tracker.master_todos.get("pending", 0),
            "in_progress": self.tracker.master_todos.get("in_progress", 0),
            "completed": self.tracker.master_todos.get("completed", 0)
        }

        # Build markdown
        markdown = []
        markdown.append("## 📋 @AGENT@MASTER.TODOLIST")
        markdown.append("")
        markdown.append(f"**Status:** {stats['in_progress']} in progress | {stats['pending']} pending | {stats['completed']} completed")
        markdown.append("")

        # Group by status
        pending_todos = [t for t in master_todos if t.get("status") == "pending"]
        in_progress_todos = [t for t in master_todos if t.get("status") == "in_progress"]
        completed_todos = [t for t in master_todos if t.get("status") == "completed"] if include_completed else []

        # In Progress
        if in_progress_todos:
            markdown.append("### 🔄 In Progress")
            markdown.append("")
            for todo in in_progress_todos:
                todo_id = todo.get("id", "unknown")
                todo_content = todo.get("content", "No description")
                priority = todo.get("priority", "medium")
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")
                markdown.append(f"- {priority_emoji} **{todo_id}:** {todo_content}")
            markdown.append("")

        # Pending
        if pending_todos:
            markdown.append("### ⏳ Pending")
            markdown.append("")
            for todo in pending_todos:
                todo_id = todo.get("id", "unknown")
                todo_content = todo.get("content", "No description")
                priority = todo.get("priority", "medium")
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")
                markdown.append(f"- {priority_emoji} **{todo_id}:** {todo_content}")
            markdown.append("")

        # Completed (if included)
        if completed_todos:
            markdown.append("### ✅ Completed")
            markdown.append("")
            for todo in completed_todos[-10:]:  # Show last 10 completed
                todo_id = todo.get("id", "unknown")
                todo_content = todo.get("content", "No description")
                markdown.append(f"- ✅ **{todo_id}:** {todo_content}")
            markdown.append("")

        # Empty state
        if not pending_todos and not in_progress_todos and not completed_todos:
            markdown.append("*No master todos found. Add todos to track master agent tasks.*")
            markdown.append("")

        # Footer with last updated
        last_updated = self.tracker.master_todos.get("last_updated", "unknown")
        markdown.append(f"*Last updated: {last_updated}*")

        return "\n".join(markdown)

    def get_combined_display(self, include_session_todos: bool = True) -> str:
        """
        Get combined display: Master todos + Session todos (OEM/Padawan)

        Shows both lists side-by-side or stacked for comparison.
        """
        markdown = []

        # Master Todo List
        markdown.append(self.get_master_todo_markdown())
        markdown.append("")
        markdown.append("---")
        markdown.append("")

        # Session Todo List (OEM/Padawan) - if available
        if include_session_todos:
            markdown.append("## 🧙 Session-Scoped Todo List (OEM/Padawan)")
            markdown.append("")
            markdown.append("*This is your current chat session's todo list.*")
            markdown.append("")
            markdown.append("*(Session todos are managed automatically by Cursor IDE)*")
            markdown.append("")

        return "\n".join(markdown)

    def display_in_chat(self, include_completed: bool = False):
        """
        Display master todo list in Cursor IDE chat window

        This function outputs markdown that Cursor IDE will render in the chat.
        """
        markdown = self.get_master_todo_markdown(include_completed=include_completed)
        print(markdown)
        return markdown

    def get_json_output(self) -> Dict[str, Any]:
        """Get JSON output for programmatic access"""
        if not self.tracker:
            return {"error": "Tracker not available"}

        return {
            "timestamp": datetime.now().isoformat(),
            "master_todos": self.tracker.master_todos,
            "dashboard": self.tracker.get_cursor_ide_dashboard() if self.tracker else {}
        }


def main():
    try:
        """CLI interface for displaying master todos in Cursor IDE"""
        import argparse

        parser = argparse.ArgumentParser(description="Cursor IDE Master Todo Display")
        parser.add_argument("--display", action="store_true", help="Display in chat format")
        parser.add_argument("--combined", action="store_true", help="Show combined master + session todos")
        parser.add_argument("--include-completed", action="store_true", help="Include completed todos")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        display = CursorIDEMasterTodoDisplay(project_root)

        if args.json:
            output = display.get_json_output()
            print(json.dumps(output, indent=2, default=str))
        elif args.combined:
            markdown = display.get_combined_display()
            print(markdown)
        else:
            markdown = display.display_in_chat(include_completed=args.include_completed)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()