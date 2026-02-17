#!/usr/bin/env python3
"""
Mental TODO Preservation System

Preserves "mental TODOs" - those tasks that both the user and AI need to remember
but might forget. This system ensures nothing falls through the cracks.

Tags: #MENTAL_TODO #PRESERVATION #MEMORY #TASKS @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MentalTodoPreservation")


class MentalTodoPreservation:
    """
    Mental TODO Preservation System

    Preserves mental TODOs that both user and AI might forget.
    This is a boon/bane we both share - the need to preserve important tasks.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Mental TODO Preservation system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "mental_todos"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.todos_file = self.data_dir / "mental_todos.json"
        self.archive_dir = self.data_dir / "archive"
        self.archive_dir.mkdir(exist_ok=True)

        self.todos: Dict[str, Any] = {
            "version": "1.0.0",
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "todos": {},
            "metadata": {
            "description": "Mental TODOs that both user and AI need to remember",
            "boon_bane": "We both have this - the need to preserve important tasks",
            "preservation_strategy": "automatic_capture_and_reminder"
            }
        }

        self._load_todos()
        logger.info("✅ Mental TODO Preservation System initialized")

    def _load_todos(self):
        """Load existing mental TODOs"""
        try:
            if self.todos_file.exists():
                with open(self.todos_file, 'r', encoding='utf-8') as f:
                    self.todos = json.load(f)
                logger.info(f"   ✅ Loaded {len(self.todos.get('todos', {}))} mental TODOs")
        except Exception as e:
            logger.warning(f"   ⚠️  Could not load mental TODOs: {e}")

    def _save_todos(self):
        """Save mental TODOs"""
        try:
            self.todos["last_updated"] = datetime.now().isoformat()
            with open(self.todos_file, 'w', encoding='utf-8') as f:
                json.dump(self.todos, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"   ❌ Error saving mental TODOs: {e}")

    def add_mental_todo(
        self,
        title: str,
        description: str,
        priority: str = "normal",
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        source: str = "user",
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a mental TODO

        Args:
            title: TODO title
            description: TODO description
            priority: Priority level (low, normal, high, critical)
            category: TODO category
            tags: List of tags
            source: Source of TODO (user, ai, system)
            context: Additional context

        Returns:
            TODO ID
        """
        import uuid

        todo_id = str(uuid.uuid4())[:16]

        todo = {
            "id": todo_id,
            "title": title,
            "description": description,
            "priority": priority,
            "category": category or "general",
            "tags": tags or [],
            "source": source,
            "status": "pending",
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "reminders": [],
            "context": context or {},
            "metadata": {
                "preserved": True,
                "preservation_reason": "Mental TODO - both user and AI need to remember"
            }
        }

        self.todos["todos"][todo_id] = todo
        self._save_todos()

        logger.info(f"   ✅ Mental TODO added: {title} (ID: {todo_id})")

        return todo_id

    def get_pending_todos(self, priority: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get pending mental TODOs"""
        todos = []
        for todo_id, todo in self.todos.get("todos", {}).items():
            if todo.get("status") == "pending":
                if priority is None or todo.get("priority") == priority:
                    todos.append(todo)

        return sorted(todos, key=lambda x: {
            "critical": 0,
            "high": 1,
            "normal": 2,
            "low": 3
        }.get(x.get("priority", "normal"), 2))

    def mark_complete(self, todo_id: str, notes: Optional[str] = None):
        """Mark a mental TODO as complete"""
        if todo_id in self.todos.get("todos", {}):
            todo = self.todos["todos"][todo_id]
            todo["status"] = "complete"
            todo["completed"] = datetime.now().isoformat()
            todo["updated"] = datetime.now().isoformat()
            if notes:
                todo["completion_notes"] = notes

            self._save_todos()
            logger.info(f"   ✅ Mental TODO completed: {todo.get('title')}")
        else:
            logger.warning(f"   ⚠️  TODO not found: {todo_id}")

    def add_reminder(self, todo_id: str, reminder_text: str):
        """Add a reminder to a mental TODO"""
        if todo_id in self.todos.get("todos", {}):
            todo = self.todos["todos"][todo_id]
            if "reminders" not in todo:
                todo["reminders"] = []

            todo["reminders"].append({
                "text": reminder_text,
                "created": datetime.now().isoformat()
            })
            todo["updated"] = datetime.now().isoformat()

            self._save_todos()
            logger.info(f"   ✅ Reminder added to: {todo.get('title')}")
        else:
            logger.warning(f"   ⚠️  TODO not found: {todo_id}")

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of mental TODOs"""
        todos = self.todos.get("todos", {})

        summary = {
            "total": len(todos),
            "pending": len([t for t in todos.values() if t.get("status") == "pending"]),
            "complete": len([t for t in todos.values() if t.get("status") == "complete"]),
            "by_priority": {
                "critical": len([t for t in todos.values() if t.get("priority") == "critical" and t.get("status") == "pending"]),
                "high": len([t for t in todos.values() if t.get("priority") == "high" and t.get("status") == "pending"]),
                "normal": len([t for t in todos.values() if t.get("priority") == "normal" and t.get("status") == "pending"]),
                "low": len([t for t in todos.values() if t.get("priority") == "low" and t.get("status") == "pending"])
            },
            "by_category": {},
            "recent": []
        }

        # Count by category
        for todo in todos.values():
            category = todo.get("category", "general")
            if category not in summary["by_category"]:
                summary["by_category"][category] = 0
            if todo.get("status") == "pending":
                summary["by_category"][category] += 1

        # Get recent TODOs (last 10)
        recent = sorted(
            todos.values(),
            key=lambda x: x.get("created", ""),
            reverse=True
        )[:10]
        summary["recent"] = [{"id": t["id"], "title": t["title"], "status": t["status"]} for t in recent]

        return summary

    def preserve_from_conversation(self, conversation_text: str):
        """
        Automatically extract and preserve mental TODOs from conversation

        Looks for patterns like:
        - "PLEASE SET THIS UP"
        - "DON'T FORGET"
        - "WE NEED TO"
        - "OMG... [task]"
        """
        import re

        # Patterns that indicate mental TODOs
        patterns = [
            r"PLEASE\s+(?:SET\s+UP|CONFIGURE|INSTALL|SETUP)\s+([^.!?]+)",
            r"DON'T\s+FORGET\s+(?:TO\s+)?([^.!?]+)",
            r"WE\s+NEED\s+TO\s+([^.!?]+)",
            r"OMG\.\.\.\s+([^.!?]+)",
            r"FOR\s+THE\s+UMPTEENTH\s+TIME[!.]?\s*([^.!?]+)",
        ]

        found_todos = []

        for pattern in patterns:
            matches = re.finditer(pattern, conversation_text, re.IGNORECASE)
            for match in matches:
                todo_text = match.group(1).strip()
                if len(todo_text) > 10:  # Only if substantial
                    found_todos.append(todo_text)

        for todo_text in found_todos:
            self.add_mental_todo(
                title=todo_text[:100],
                description=f"Extracted from conversation: {todo_text}",
                priority="high",
                category="conversation_extraction",
                tags=["#AUTO_EXTRACTED", "#CONVERSATION"],
                source="ai"
            )

        if found_todos:
            logger.info(f"   ✅ Preserved {len(found_todos)} mental TODOs from conversation")

        return found_todos


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Mental TODO Preservation System")
    parser.add_argument("--add", action="store_true", help="Add a mental TODO")
    parser.add_argument("--title", help="TODO title")
    parser.add_argument("--description", help="TODO description")
    parser.add_argument("--priority", default="normal", choices=["low", "normal", "high", "critical"], help="Priority")
    parser.add_argument("--category", help="TODO category")
    parser.add_argument("--list", action="store_true", help="List pending TODOs")
    parser.add_argument("--summary", action="store_true", help="Show summary")
    parser.add_argument("--complete", help="Mark TODO as complete (ID)")
    parser.add_argument("--notes", help="Completion notes (use with --complete)")
    parser.add_argument("--preserve-conversation", help="Extract TODOs from conversation text")

    args = parser.parse_args()

    system = MentalTodoPreservation()

    if args.add:
        if not args.title:
            print("Error: --title is required when using --add")
            return 1

        todo_id = system.add_mental_todo(
            title=args.title,
            description=args.description or "",
            priority=args.priority,
            category=args.category
        )
        print(f"✅ Mental TODO added: {todo_id}")

    elif args.list:
        todos = system.get_pending_todos()
        print(f"\n📋 Pending Mental TODOs: {len(todos)}\n")
        for todo in todos:
            print(f"  [{todo['priority'].upper()}] {todo['title']}")
            print(f"      ID: {todo['id']}")
            print(f"      Category: {todo.get('category', 'general')}")
            if todo.get('description'):
                print(f"      {todo['description']}")
            print()

    elif args.summary:
        summary = system.get_summary()
        print("\n📊 Mental TODO Summary\n")
        print(f"Total: {summary['total']}")
        print(f"Pending: {summary['pending']}")
        print(f"Complete: {summary['complete']}")
        print(f"\nBy Priority:")
        for priority, count in summary['by_priority'].items():
            if count > 0:
                print(f"  {priority}: {count}")
        print(f"\nBy Category:")
        for category, count in summary['by_category'].items():
            print(f"  {category}: {count}")

    elif args.complete:
        system.mark_complete(args.complete, notes=args.notes)
        print(f"✅ TODO marked as complete: {args.complete}")

    elif args.preserve_conversation:
        found = system.preserve_from_conversation(args.preserve_conversation)
        print(f"✅ Preserved {len(found)} mental TODOs from conversation")
        for todo in found:
            print(f"  - {todo}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":


    sys.exit(main())