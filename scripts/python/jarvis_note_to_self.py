#!/usr/bin/env python3
"""
JARVIS Note to Self System

JARVIS can remember notes, reminders, and tasks for future execution.
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
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISNoteToSelf")


class JARVISNoteToSelf:
    """
    JARVIS Note to Self system

    Stores notes, reminders, and tasks for future execution
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        self.notes_dir = project_root / "data" / "jarvis_notes"
        self.notes_dir.mkdir(parents=True, exist_ok=True)

        self.notes_file = self.notes_dir / "notes.json"
        self.notes = self._load_notes()

    def _load_notes(self) -> List[Dict[str, Any]]:
        """Load existing notes"""
        if self.notes_file.exists():
            try:
                with open(self.notes_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_notes(self):
        """Save notes"""
        try:
            with open(self.notes_file, 'w') as f:
                json.dump(self.notes, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save notes: {e}")

    def add_note(self, note: str, priority: str = "normal",
                 category: str = "general", action: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a note to self

        Args:
            note: The note/reminder text
            priority: high, normal, low
            category: Category of note
            action: Optional action to take
        """
        note_entry = {
            'note_id': f"note_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'note': note,
            'priority': priority,
            'category': category,
            'action': action,
            'created_at': datetime.now().isoformat(),
            'status': 'pending',
            'completed_at': None
        }

        self.notes.append(note_entry)
        self._save_notes()

        self.logger.info(f"📝 Note added: {note[:50]}...")

        return note_entry

    def get_pending_notes(self, priority: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get pending notes"""
        pending = [n for n in self.notes if n.get('status') == 'pending']

        if priority:
            pending = [n for n in pending if n.get('priority') == priority]

        return sorted(pending, key=lambda x: {
            'high': 0, 'normal': 1, 'low': 2
        }.get(x.get('priority', 'normal'), 1))

    def complete_note(self, note_id: str):
        """Mark a note as completed"""
        for note in self.notes:
            if note.get('note_id') == note_id:
                note['status'] = 'completed'
                note['completed_at'] = datetime.now().isoformat()
                self._save_notes()
                return True
        return False


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Note to Self")
        parser.add_argument("--add", type=str, help="Add a note")
        parser.add_argument("--priority", type=str, choices=['high', 'normal', 'low'], default='normal')
        parser.add_argument("--category", type=str, default='general')
        parser.add_argument("--action", type=str, help="Action to take")
        parser.add_argument("--list", action="store_true", help="List pending notes")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        notes = JARVISNoteToSelf(project_root)

        if args.add:
            note = notes.add_note(args.add, args.priority, args.category, args.action)
            print(f"\n✅ Note added: {note['note_id']}")
            print(f"   {note['note']}")

        elif args.list:
            pending = notes.get_pending_notes()
            print(f"\n📝 Pending Notes: {len(pending)}")
            for note in pending:
                print(f"\n  [{note['priority'].upper()}] {note['note']}")
                print(f"    Category: {note['category']}")
                if note.get('action'):
                    print(f"    Action: {note['action']}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()