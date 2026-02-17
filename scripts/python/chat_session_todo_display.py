#!/usr/bin/env python3
"""
Chat Session To-Do List Display

Displays dual to-do lists in chat sessions:
1. Master To-Do List (collapsible) - Everything from beginning, master blueprint, Jupiter notebook
2. Session To-Do List - Current session tasks

Tags: #CHAT #TODO #SESSION #DISPLAY #DUAL_LIST @JARVIS @LUMINA  # [ADDRESSED]  # [ADDRESSED]
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
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

logger = get_logger("ChatSessionTodoDisplay")


class ChatSessionTodoDisplay:
    """
    Chat Session To-Do List Display

    Displays dual to-do lists in chat sessions.
    """

    def __init__(self, project_root: Optional[Path] = None, session_id: Optional[str] = None):
        """Initialize chat session to-do display"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")

        # Load master to-do tracker
        try:
            from master_todo_tracker import MasterTodoTracker
            self.master_tracker = MasterTodoTracker(self.project_root)
        except Exception as e:
            logger.warning(f"   ⚠️  Master tracker not available: {e}")
            self.master_tracker = None

        # Session to-do list
        self.session_data_dir = self.project_root / "data" / "chat_sessions" / self.session_id
        self.session_data_dir.mkdir(parents=True, exist_ok=True)
        self.session_todos_file = self.session_data_dir / "session_todos.json"
        self.session_todos: List[Dict[str, Any]] = []

        # Load session todos
        self._load_session_todos()

        logger.info("✅ Chat Session To-Do Display initialized")
        logger.info(f"   Session ID: {self.session_id}")

    def _load_session_todos(self):
        """Load session to-do list"""
        if self.session_todos_file.exists():
            try:
                with open(self.session_todos_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.session_todos = data.get("todos", [])
            except Exception as e:
                logger.warning(f"   ⚠️  Could not load session todos: {e}")
                self.session_todos = []
        else:
            self.session_todos = []

    def _save_session_todos(self):
        """Save session to-do list"""
        try:
            data = {
                "session_id": self.session_id,
                "last_updated": datetime.now().isoformat(),
                "todos": self.session_todos
            }
            with open(self.session_todos_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"   ❌ Error saving session todos: {e}")

    def add_session_todo(self, title: str, description: str = "", priority: str = "medium"):
        """Add todo to session list"""
        todo = {
            "id": f"session_{len(self.session_todos) + 1}",
            "title": title,
            "description": description,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        self.session_todos.append(todo)
        self._save_session_todos()
        logger.info(f"   ✅ Added session todo: {title}")

    def get_master_todos_display(self, collapsed: bool = False) -> str:
        """Get master to-do list display (collapsible)"""
        if not self.master_tracker:
            return "📋 Master To-Do List: Not available"

        todos = self.master_tracker.get_todos()
        stats = self.master_tracker.get_stats()

        if collapsed:
            return f"📋 Master To-Do List (Collapsed) - {stats['total']} total, {stats['complete']} complete ({stats['completion_rate']:.1f}%)"

        lines = []
        lines.append("📋 **Master To-Do List** (Click to expand/collapse)")
        lines.append(f"   Total: {stats['total']} | Complete: {stats['complete']} ({stats['completion_rate']:.1f}%) | In Progress: {stats['in_progress']} | Pending: {stats['pending']}")
        lines.append("")

        # Group by status
        in_progress = [t for t in todos if t.status.value == "in_progress"]
        pending = [t for t in todos if t.status.value == "pending"]

        if in_progress:
            lines.append("**In Progress:**")
            for todo in in_progress[:10]:  # Limit to 10
                lines.append(f"  • [{todo.priority.value.upper()}] {todo.title}")
            if len(in_progress) > 10:
                lines.append(f"  ... and {len(in_progress) - 10} more")
            lines.append("")

        if pending:
            lines.append("**Pending (High Priority):**")
            high_priority = [t for t in pending if t.priority.value == "high"][:5]
            for todo in high_priority:
                lines.append(f"  • {todo.title}")
            if len(pending) > 5:
                lines.append(f"  ... and {len(pending) - 5} more pending")

        return "\n".join(lines)

    def get_session_todos_display(self) -> str:
        """Get session to-do list display"""
        if not self.session_todos:
            return "📝 Session To-Do List: No tasks yet"

        lines = []
        lines.append("📝 **Session To-Do List**")
        lines.append("")

        for todo in self.session_todos:
            status_icon = "✅" if todo.get("status") == "complete" else "⏳"
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(todo.get("priority", "medium"), "🟡")
            lines.append(f"{status_icon} {priority_icon} {todo.get('title', 'Untitled')}")
            if todo.get("description"):
                lines.append(f"   {todo.get('description')}")

        return "\n".join(lines)

    def get_dual_display(self, master_collapsed: bool = False) -> str:
        """Get dual to-do list display"""
        lines = []
        lines.append("=" * 80)
        lines.append("📋 DUAL TO-DO LIST DISPLAY")
        lines.append("=" * 80)
        lines.append("")
        lines.append(self.get_master_todos_display(collapsed=master_collapsed))
        lines.append("")
        lines.append("-" * 80)
        lines.append("")
        lines.append(self.get_session_todos_display())
        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)

    def format_for_chat(self, master_collapsed: bool = False) -> Dict[str, Any]:
        """Format for chat display"""
        return {
            "master_todos": {
                "collapsed": master_collapsed,
                "content": self.get_master_todos_display(collapsed=master_collapsed),
                "stats": self.master_tracker.get_stats() if self.master_tracker else None
            },
            "session_todos": {
                "content": self.get_session_todos_display(),
                "count": len(self.session_todos)
            },
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat()
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Chat Session To-Do Display")
        parser.add_argument("--session-id", help="Session ID")
        parser.add_argument("--display", action="store_true", help="Display dual lists")
        parser.add_argument("--add-session", nargs=2, metavar=("TITLE", "DESCRIPTION"),
                           help="Add todo to session list")
        parser.add_argument("--collapsed", action="store_true", help="Show master list collapsed")
        parser.add_argument("--json", action="store_true", help="JSON output")

        args = parser.parse_args()

        display = ChatSessionTodoDisplay(session_id=args.session_id)

        if args.add_session:
            title, description = args.add_session
            display.add_session_todo(title, description)
            if args.json:
                print(json.dumps({"added": True, "title": title}, indent=2))
            else:
                print(f"✅ Added session todo: {title}")

        elif args.display or not args.add_session:
            if args.json:
                result = display.format_for_chat(master_collapsed=args.collapsed)
                print(json.dumps(result, indent=2))
            else:
                print(display.get_dual_display(master_collapsed=args.collapsed))

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()