"""
JARVIS Dual TODO List Manager
Manages both Master TODO list and Padawan/OEM (session-specific) TODO list
with auto-collapse timeout and conversational integration.

Author: JARVIS System
Date: 2026-01-09
Tags: #JARVIS @LUMINA #TODO #CONVERSATIONAL  # [ADDRESSED]  # [ADDRESSED]
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)


class TODOStatus(str, Enum):
    """TODO status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class TODOItem:
    """Individual TODO item."""
    id: str
    content: str
    status: TODOStatus
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    completed_at: Optional[str] = None
    priority: Optional[int] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        if isinstance(data.get('status'), TODOStatus):
            data['status'] = data['status'].value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TODOItem':
        """Create from dictionary."""
        if isinstance(data.get('status'), str):
            data['status'] = TODOStatus(data['status'])
        return cls(**data)


@dataclass
class TODODisplayState:
    """Display state for TODO lists with auto-collapse."""
    is_expanded: bool = True
    last_interaction: Optional[float] = None
    auto_collapse_timeout: float = 300.0  # 5 minutes default
    display_count: int = 0

    def should_collapse(self) -> bool:
        """Check if list should auto-collapse."""
        if not self.is_expanded:
            return True
        if self.last_interaction is None:
            return False
        elapsed = time.time() - self.last_interaction
        return elapsed > self.auto_collapse_timeout

    def touch(self) -> None:
        """Update last interaction time."""
        self.last_interaction = time.time()
        self.is_expanded = True
        self.display_count += 1


class JARVISDualTODOManager:
    """
    Manages both Master TODO list and Padawan/OEM (session-specific) TODO list.

    Features:
    - Dual list management (Master + Session)
    - Auto-collapse after timeout
    - Conversational integration
    - Persistent storage
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize the dual TODO manager.

        Args:
            project_root: Project root directory. Defaults to current directory.
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)

        # File paths
        self.master_todo_file = self.project_root / "data" / "todo" / "master_todos.json"
        self.padawan_todo_file = self.project_root / "data" / "ask_database" / "master_padawan_todos.json"
        self.display_state_file = self.project_root / "data" / "todo" / "display_state.json"

        # Ensure directories exist
        self.master_todo_file.parent.mkdir(parents=True, exist_ok=True)
        self.padawan_todo_file.parent.mkdir(parents=True, exist_ok=True)
        self.display_state_file.parent.mkdir(parents=True, exist_ok=True)

        # Load state
        self.master_todos: List[TODOItem] = []
        self.padawan_todos: List[TODOItem] = []
        self.display_state = TODODisplayState()

        self._load_all()

    def _load_all(self) -> None:
        """Load all TODO lists and display state."""
        # Load master TODO list
        if self.master_todo_file.exists():
            try:
                with open(self.master_todo_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.master_todos = [
                        TODOItem.from_dict(item) for item in data.get('todos', [])
                    ]
            except Exception as e:
                logger.error(f"Failed to load master TODO list: {e}", exc_info=True)
                self.master_todos = []
        else:
            self.master_todos = []

        # Load Padawan/OEM TODO list
        if self.padawan_todo_file.exists():
            try:
                with open(self.padawan_todo_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.padawan_todos = [
                        TODOItem.from_dict(item) for item in data.get('todos', [])
                    ]
            except Exception as e:
                logger.error(f"Failed to load Padawan TODO list: {e}", exc_info=True)
                self.padawan_todos = []
        else:
            self.padawan_todos = []

        # Load display state
        if self.display_state_file.exists():
            try:
                with open(self.display_state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.display_state = TODODisplayState(**data)
            except Exception as e:
                logger.error(f"Failed to load display state: {e}", exc_info=True)
                self.display_state = TODODisplayState()

    def _save_master(self) -> None:
        """Save master TODO list and sync with One Ring Blueprint."""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'description': 'Master TODO List - The One Ring Blueprint (Living Document)',
                'todos': [item.to_dict() for item in self.master_todos]
            }
            with open(self.master_todo_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Sync with One Ring Blueprint, Holocron, and Database
            try:
                from jarvis_master_todo_one_ring_sync import JARVISMasterTODOOneRingSync
                sync_system = JARVISMasterTODOOneRingSync(self.project_root)
                sync_system.sync_all(data['todos'])
                logger.info("Synced Master TODO list with One Ring Blueprint, Holocron, and Database")
            except Exception as e:
                logger.warning(f"One Ring sync not available: {e}")
        except Exception as e:
            logger.error(f"Failed to save master TODO list: {e}", exc_info=True)

    def _save_padawan(self) -> None:
        """Save Padawan/OEM TODO list."""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'description': 'Padawan/OEM TODO List - Session-specific',
                'todos': [item.to_dict() for item in self.padawan_todos]
            }
            with open(self.padawan_todo_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save Padawan TODO list: {e}", exc_info=True)

    def _save_display_state(self) -> None:
        """Save display state."""
        try:
            data = {
                'is_expanded': self.display_state.is_expanded,
                'last_interaction': self.display_state.last_interaction,
                'auto_collapse_timeout': self.display_state.auto_collapse_timeout,
                'display_count': self.display_state.display_count
            }
            with open(self.display_state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save display state: {e}", exc_info=True)

    def get_master_todos(self, status_filter: Optional[TODOStatus] = None) -> List[TODOItem]:
        """Get master TODO items, optionally filtered by status."""
        if status_filter:
            return [t for t in self.master_todos if t.status == status_filter]
        return self.master_todos.copy()

    def get_padawan_todos(self, status_filter: Optional[TODOStatus] = None) -> List[TODOItem]:
        """Get Padawan/OEM TODO items, optionally filtered by status."""
        if status_filter:
            return [t for t in self.padawan_todos if t.status == status_filter]
        return self.padawan_todos.copy()

    def add_master_todo(self, content: str, priority: Optional[int] = None, 
                       tags: Optional[List[str]] = None) -> str:
        """Add a TODO to the master list."""
        todo_id = f"master_{int(time.time() * 1000)}"
        todo = TODOItem(
            id=todo_id,
            content=content,
            status=TODOStatus.PENDING,
            created_at=datetime.now().isoformat(),
            priority=priority,
            tags=tags or []
        )
        self.master_todos.append(todo)
        self._save_master()
        self.display_state.touch()
        self._save_display_state()
        return todo_id

    def add_padawan_todo(self, content: str, priority: Optional[int] = None,
                        tags: Optional[List[str]] = None) -> str:
        """Add a TODO to the Padawan/OEM list."""
        todo_id = f"padawan_{int(time.time() * 1000)}"
        todo = TODOItem(
            id=todo_id,
            content=content,
            status=TODOStatus.PENDING,
            created_at=datetime.now().isoformat(),
            priority=priority,
            tags=tags or []
        )
        self.padawan_todos.append(todo)
        self._save_padawan()
        self.display_state.touch()
        self._save_display_state()
        return todo_id

    def update_todo_status(self, todo_id: str, status: TODOStatus, 
                          list_type: str = "auto") -> bool:
        """
        Update TODO status.

        Args:
            todo_id: TODO item ID
            status: New status
            list_type: "master", "padawan", or "auto" (searches both)
        """
        updated = False

        if list_type in ("auto", "master"):
            for todo in self.master_todos:
                if todo.id == todo_id:
                    todo.status = status
                    todo.updated_at = datetime.now().isoformat()
                    if status == TODOStatus.COMPLETED:
                        todo.completed_at = datetime.now().isoformat()
                    updated = True
                    self._save_master()
                    break

        if not updated and list_type in ("auto", "padawan"):
            for todo in self.padawan_todos:
                if todo.id == todo_id:
                    todo.status = status
                    todo.updated_at = datetime.now().isoformat()
                    if status == TODOStatus.COMPLETED:
                        todo.completed_at = datetime.now().isoformat()
                    updated = True
                    self._save_padawan()
                    break

        if updated:
            self.display_state.touch()
            self._save_display_state()

        return updated

    def get_display_summary(self, auto_collapse: bool = True) -> Dict[str, Any]:
        """
        Get conversational display summary of both TODO lists.

        Args:
            auto_collapse: Whether to check auto-collapse timeout

        Returns:
            Dictionary with display information
        """
        # Check auto-collapse
        if auto_collapse and self.display_state.should_collapse():
            self.display_state.is_expanded = False
            self._save_display_state()

        # Get pending and in-progress items
        master_pending = [t for t in self.master_todos 
                         if t.status in (TODOStatus.PENDING, TODOStatus.IN_PROGRESS)]
        padawan_pending = [t for t in self.padawan_todos 
                          if t.status in (TODOStatus.PENDING, TODOStatus.IN_PROGRESS)]

        master_completed = len([t for t in self.master_todos 
                               if t.status == TODOStatus.COMPLETED])
        padawan_completed = len([t for t in self.padawan_todos 
                                if t.status == TODOStatus.COMPLETED])

        return {
            'is_expanded': self.display_state.is_expanded,
            'master': {
                'total': len(self.master_todos),
                'pending': len(master_pending),
                'completed': master_completed,
                'items': master_pending if self.display_state.is_expanded else []
            },
            'padawan': {
                'total': len(self.padawan_todos),
                'pending': len(padawan_pending),
                'completed': padawan_completed,
                'items': padawan_pending if self.display_state.is_expanded else []
            },
            'last_interaction': self.display_state.last_interaction,
            'timeout_seconds': self.display_state.auto_collapse_timeout
        }

    def format_conversational_display(self, summary: Optional[Dict[str, Any]] = None) -> str:
        """
        Format TODO lists for conversational display.

        Returns:
            Formatted string for chat display
        """
        if summary is None:
            summary = self.get_display_summary()

        lines = []
        lines.append("## 📋 TODO Lists")

        # Master TODO List
        master = summary['master']
        padawan = summary['padawan']

        if summary['is_expanded']:
            lines.append(f"\n### 🎯 Master TODO List ({master['pending']} pending, {master['completed']} completed)")
            if master['items']:
                for i, item in enumerate(master['items'], 1):
                    status_icon = "🔄" if item.status == TODOStatus.IN_PROGRESS else "⏳"
                    lines.append(f"{i}. {status_icon} {item.content}")
            else:
                lines.append("   *No pending items*")

            lines.append(f"\n### 📝 Padawan/OEM TODO List ({padawan['pending']} pending, {padawan['completed']} completed)")
            if padawan['items']:
                for i, item in enumerate(padawan['items'], 1):
                    status_icon = "🔄" if item.status == TODOStatus.IN_PROGRESS else "⏳"
                    lines.append(f"{i}. {status_icon} {item.content}")
            else:
                lines.append("   *No pending items*")
        else:
            lines.append(f"\n*Lists collapsed (timeout: {summary['timeout_seconds']}s)*")
            lines.append(f"**Master:** {master['pending']} pending, {master['completed']} completed")
            lines.append(f"**Padawan/OEM:** {padawan['pending']} pending, {padawan['completed']} completed")
            lines.append("\n*Say 'show todos' or interact to expand*")

        return "\n".join(lines)

    def expand_lists(self) -> None:
        """Manually expand TODO lists."""
        self.display_state.touch()
        self._save_display_state()

    def set_timeout(self, seconds: float) -> None:
        """Set auto-collapse timeout in seconds."""
        self.display_state.auto_collapse_timeout = seconds
        self._save_display_state()


def main():
    """CLI interface for dual TODO manager."""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Dual TODO Manager")
    parser.add_argument('--show', action='store_true', help='Show TODO lists')
    parser.add_argument('--expand', action='store_true', help='Expand lists')
    parser.add_argument('--add-master', type=str, help='Add to master list')
    parser.add_argument('--add-padawan', type=str, help='Add to Padawan list')
    parser.add_argument('--complete', type=str, help='Mark TODO as complete (ID)')
    parser.add_argument('--timeout', type=float, help='Set auto-collapse timeout (seconds)')

    args = parser.parse_args()

    manager = JARVISDualTODOManager()

    if args.expand:
        manager.expand_lists()
        print("✅ Lists expanded")

    if args.timeout:
        manager.set_timeout(args.timeout)
        print(f"✅ Timeout set to {args.timeout} seconds")

    if args.add_master:
        todo_id = manager.add_master_todo(args.add_master)
        print(f"✅ Added to master list: {todo_id}")

    if args.add_padawan:
        todo_id = manager.add_padawan_todo(args.add_padawan)
        print(f"✅ Added to Padawan list: {todo_id}")

    if args.complete:
        if manager.update_todo_status(args.complete, TODOStatus.COMPLETED):
            print(f"✅ Marked {args.complete} as complete")
        else:
            print(f"❌ TODO {args.complete} not found")

    if args.show or not any([args.expand, args.timeout, args.add_master, 
                            args.add_padawan, args.complete]):
        summary = manager.get_display_summary()
        print(manager.format_conversational_display(summary))


if __name__ == "__main__":


    main()