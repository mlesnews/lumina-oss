#!/usr/bin/env python3
"""
Sub-Ask Todo Manager

Each sub-ask gets:
1. Its own todo list
2. Its own sub-agent chat session
3. Workflow completion tracking
4. Revisit/update/follow-up tracking
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from master_todo_tracker import MasterTodoTracker, TaskStatus, Priority
    TODO_TRACKER_AVAILABLE = True
except ImportError:
    TODO_TRACKER_AVAILABLE = False
    MasterTodoTracker = None


class SubAskStatus(Enum):
    """Sub-ask status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    NEEDS_REVISIT = "needs_revisit"
    NEEDS_UPDATE = "needs_update"
    NEEDS_FOLLOWUP = "needs_followup"
    ARCHIVED = "archived"


class SubAgentChatStatus(Enum):
    """Sub-agent chat session status"""
    NEW = "new"  # New chat session created
    EXISTING = "existing"  # Existing chat session being used
    NEEDS_REVISIT = "needs_revisit"  # Needs to be revisited
    NEEDS_UPDATE = "needs_update"  # Needs to be updated
    NEEDS_FOLLOWUP = "needs_followup"  # Needs follow-up
    ACTIVE = "active"  # Currently active
    ARCHIVED = "archived"  # Completed and archived


@dataclass
class SubAskTodoList:
    """Todo list for a sub-ask"""
    sub_ask_id: str
    todo_list_id: str
    todos: List[Dict[str, Any]] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    completed_count: int = 0
    total_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SubAgentChatSession:
    """Sub-agent chat session"""
    session_id: str
    sub_ask_id: str
    agent_name: str
    chat_status: SubAgentChatStatus
    created_at: str = ""
    updated_at: str = ""
    last_accessed: str = ""
    revisit_reason: Optional[str] = None
    update_reason: Optional[str] = None
    followup_reason: Optional[str] = None
    workflow_completed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["chat_status"] = self.chat_status.value
        return data


@dataclass
class SubAsk:
    """Sub-ask with todo list and chat session"""
    sub_ask_id: str
    parent_ask_id: str
    sub_ask_text: str
    status: SubAskStatus
    todo_list: Optional[SubAskTodoList] = None
    chat_session: Optional[SubAgentChatSession] = None
    workflow_id: Optional[str] = None
    workflow_completed: bool = False
    created_at: str = ""
    updated_at: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        if data.get("todo_list"):
            data["todo_list"] = self.todo_list.to_dict()
        if data.get("chat_session"):
            data["chat_session"] = self.chat_session.to_dict()
        return data


class SubAskTodoManager:
    """
    Manages sub-asks with their own todo lists and sub-agent chat sessions
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("SubAskTodoManager")

        # Directories
        self.data_dir = self.project_root / "data" / "sub_ask_todos"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.sub_asks_dir = self.data_dir / "sub_asks"
        self.sub_asks_dir.mkdir(parents=True, exist_ok=True)

        self.chat_sessions_dir = self.data_dir / "chat_sessions"
        self.chat_sessions_dir.mkdir(parents=True, exist_ok=True)

        # Files
        self.sub_asks_file = self.data_dir / "sub_asks.json"
        self.chat_sessions_file = self.data_dir / "chat_sessions.json"

        # Todo tracker  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
        self.todo_tracker = MasterTodoTracker(project_root) if TODO_TRACKER_AVAILABLE else None

        # State
        self.sub_asks: Dict[str, SubAsk] = {}
        self.chat_sessions: Dict[str, SubAgentChatSession] = {}

        # Load state
        self._load_state()

    def _load_state(self):
        """Load sub-asks and chat sessions"""
        # Load sub-asks
        if self.sub_asks_file.exists():
            try:
                with open(self.sub_asks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for sub_ask_id, sub_ask_data in data.items():
                        # Reconstruct SubAsk
                        todo_list_data = sub_ask_data.get("todo_list")
                        todo_list = None
                        if todo_list_data:
                            todo_list = SubAskTodoList(**todo_list_data)

                        chat_session_data = sub_ask_data.get("chat_session")
                        chat_session = None
                        if chat_session_data:
                            chat_session = SubAgentChatSession(**chat_session_data)
                            chat_session.chat_status = SubAgentChatStatus(chat_session_data["chat_status"])

                        sub_ask = SubAsk(
                            sub_ask_id=sub_ask_data["sub_ask_id"],
                            parent_ask_id=sub_ask_data["parent_ask_id"],
                            sub_ask_text=sub_ask_data["sub_ask_text"],
                            status=SubAskStatus(sub_ask_data["status"]),
                            todo_list=todo_list,
                            chat_session=chat_session,
                            workflow_id=sub_ask_data.get("workflow_id"),
                            workflow_completed=sub_ask_data.get("workflow_completed", False),
                            created_at=sub_ask_data.get("created_at", ""),
                            updated_at=sub_ask_data.get("updated_at", ""),
                            metadata=sub_ask_data.get("metadata", {})
                        )
                        self.sub_asks[sub_ask_id] = sub_ask
            except Exception as e:
                self.logger.error(f"Error loading sub-asks: {e}")

        # Load chat sessions
        if self.chat_sessions_file.exists():
            try:
                with open(self.chat_sessions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for session_id, session_data in data.items():
                        session = SubAgentChatSession(**session_data)
                        session.chat_status = SubAgentChatStatus(session_data["chat_status"])
                        self.chat_sessions[session_id] = session
            except Exception as e:
                self.logger.error(f"Error loading chat sessions: {e}")

    def _save_state(self):
        try:
            """Save sub-asks and chat sessions"""
            # Save sub-asks
            sub_asks_data = {sub_ask_id: sub_ask.to_dict() for sub_ask_id, sub_ask in self.sub_asks.items()}
            with open(self.sub_asks_file, 'w', encoding='utf-8') as f:
                json.dump(sub_asks_data, f, indent=2, ensure_ascii=False)

            # Save chat sessions
            chat_sessions_data = {session_id: session.to_dict() for session_id, session in self.chat_sessions.items()}
            with open(self.chat_sessions_file, 'w', encoding='utf-8') as f:
                json.dump(chat_sessions_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _save_state: {e}", exc_info=True)
            raise
    def create_sub_ask(
        self,
        parent_ask_id: str,
        sub_ask_text: str,
        agent_name: Optional[str] = None,
        workflow_id: Optional[str] = None,
        use_existing_chat: Optional[str] = None
    ) -> SubAsk:
        """
        Create a new sub-ask with its own todo list and chat session

        Args:
            parent_ask_id: Parent ask ID
            sub_ask_text: Sub-ask text
            agent_name: Agent name for chat session (defaults to auto-assigned)
            workflow_id: Associated workflow ID
            use_existing_chat: Use existing chat session ID (if needs revisit/update)
        """
        sub_ask_id = f"sub_ask_{int(datetime.now().timestamp() * 1000)}"
        now = datetime.now().isoformat()

        # Create todo list
        todo_list_id = f"todo_{sub_ask_id}"
        todo_list = SubAskTodoList(
            sub_ask_id=sub_ask_id,
            todo_list_id=todo_list_id,
            created_at=now,
            updated_at=now
        )

        # Create or use existing chat session
        if use_existing_chat and use_existing_chat in self.chat_sessions:
            # Use existing chat session (needs revisit/update)
            chat_session = self.chat_sessions[use_existing_chat]
            chat_session.updated_at = now
            chat_session.last_accessed = now
            if chat_session.chat_status == SubAgentChatStatus.NEEDS_REVISIT:
                chat_session.chat_status = SubAgentChatStatus.ACTIVE
            elif chat_session.chat_status == SubAgentChatStatus.NEEDS_UPDATE:
                chat_session.chat_status = SubAgentChatStatus.ACTIVE
            elif chat_session.chat_status == SubAgentChatStatus.NEEDS_FOLLOWUP:
                chat_session.chat_status = SubAgentChatStatus.ACTIVE
        else:
            # Create new chat session
            session_id = f"chat_{sub_ask_id}"
            agent_name = agent_name or "Sub-Agent"
            chat_session = SubAgentChatSession(
                session_id=session_id,
                sub_ask_id=sub_ask_id,
                agent_name=agent_name,
                chat_status=SubAgentChatStatus.NEW,
                created_at=now,
                updated_at=now,
                last_accessed=now
            )
            self.chat_sessions[session_id] = chat_session

        # Create sub-ask
        sub_ask = SubAsk(
            sub_ask_id=sub_ask_id,
            parent_ask_id=parent_ask_id,
            sub_ask_text=sub_ask_text,
            status=SubAskStatus.PENDING,
            todo_list=todo_list,
            chat_session=chat_session,
            workflow_id=workflow_id,
            created_at=now,
            updated_at=now
        )

        self.sub_asks[sub_ask_id] = sub_ask

        # Create todos in Master Todo Tracker
        if self.todo_tracker:
            self._create_todos_for_sub_ask(sub_ask)

        self._save_state()

        self.logger.info(f"✅ Created sub-ask: {sub_ask_id} with todo list and chat session")

        return sub_ask

    def _create_todos_for_sub_ask(self, sub_ask: SubAsk):
        """Create todos in Master Todo Tracker for sub-ask"""
        if not self.todo_tracker:
            return

        # Create main todo for sub-ask
        self.todo_tracker.add_todo(
            f"Sub-Ask: {sub_ask.sub_ask_text[:50]}...",
            f"Complete sub-ask: {sub_ask.sub_ask_text}",
            category=f"sub_ask_{sub_ask.sub_ask_id}",
            priority=Priority.HIGH,
            status=TaskStatus.PENDING,
            tags=["sub_ask", sub_ask.sub_ask_id, sub_ask.parent_ask_id]
        )

        # Create workflow completion todo if workflow exists
        if sub_ask.workflow_id:
            self.todo_tracker.add_todo(
                f"Complete Workflow: {sub_ask.workflow_id}",
                f"Complete workflow {sub_ask.workflow_id} for sub-ask {sub_ask.sub_ask_id}",
                category=f"sub_ask_{sub_ask.sub_ask_id}",
                priority=Priority.HIGH,
                status=TaskStatus.PENDING,
                tags=["sub_ask", sub_ask.sub_ask_id, "workflow", sub_ask.workflow_id]
            )

    def add_todo_to_sub_ask(self, sub_ask_id: str, todo_title: str, todo_description: str, priority: Priority = Priority.MEDIUM) -> bool:
        """Add a todo to a sub-ask's todo list"""
        if sub_ask_id not in self.sub_asks:
            self.logger.error(f"Sub-ask not found: {sub_ask_id}")
            return False

        sub_ask = self.sub_asks[sub_ask_id]

        if not sub_ask.todo_list:
            self.logger.error(f"Todo list not found for sub-ask: {sub_ask_id}")
            return False

        # Add to Master Todo Tracker
        if self.todo_tracker:
            self.todo_tracker.add_todo(
                todo_title,
                todo_description,
                category=f"sub_ask_{sub_ask_id}",
                priority=priority,
                status=TaskStatus.PENDING,
                tags=["sub_ask", sub_ask_id]
            )

        # Update todo list
        sub_ask.todo_list.todos.append({
            "title": todo_title,
            "description": todo_description,
            "priority": priority.value if hasattr(priority, 'value') else str(priority),
            "created_at": datetime.now().isoformat()
        })
        sub_ask.todo_list.total_count += 1
        sub_ask.todo_list.updated_at = datetime.now().isoformat()
        sub_ask.updated_at = datetime.now().isoformat()

        self._save_state()

        return True

    def mark_chat_needs_revisit(self, session_id: str, reason: str):
        """Mark a chat session as needing revisit"""
        if session_id not in self.chat_sessions:
            self.logger.error(f"Chat session not found: {session_id}")
            return

        chat_session = self.chat_sessions[session_id]
        chat_session.chat_status = SubAgentChatStatus.NEEDS_REVISIT
        chat_session.revisit_reason = reason
        chat_session.updated_at = datetime.now().isoformat()

        # Update associated sub-ask
        for sub_ask in self.sub_asks.values():
            if sub_ask.chat_session and sub_ask.chat_session.session_id == session_id:
                sub_ask.status = SubAskStatus.NEEDS_REVISIT
                sub_ask.updated_at = datetime.now().isoformat()

        self._save_state()
        self.logger.info(f"✅ Marked chat session {session_id} as needs revisit: {reason}")

    def mark_chat_needs_update(self, session_id: str, reason: str):
        """Mark a chat session as needing update"""
        if session_id not in self.chat_sessions:
            self.logger.error(f"Chat session not found: {session_id}")
            return

        chat_session = self.chat_sessions[session_id]
        chat_session.chat_status = SubAgentChatStatus.NEEDS_UPDATE
        chat_session.update_reason = reason
        chat_session.updated_at = datetime.now().isoformat()

        # Update associated sub-ask
        for sub_ask in self.sub_asks.values():
            if sub_ask.chat_session and sub_ask.chat_session.session_id == session_id:
                sub_ask.status = SubAskStatus.NEEDS_UPDATE
                sub_ask.updated_at = datetime.now().isoformat()

        self._save_state()
        self.logger.info(f"✅ Marked chat session {session_id} as needs update: {reason}")

    def mark_chat_needs_followup(self, session_id: str, reason: str):
        """Mark a chat session as needing follow-up"""
        if session_id not in self.chat_sessions:
            self.logger.error(f"Chat session not found: {session_id}")
            return

        chat_session = self.chat_sessions[session_id]
        chat_session.chat_status = SubAgentChatStatus.NEEDS_FOLLOWUP
        chat_session.followup_reason = reason
        chat_session.updated_at = datetime.now().isoformat()

        # Update associated sub-ask
        for sub_ask in self.sub_asks.values():
            if sub_ask.chat_session and sub_ask.chat_session.session_id == session_id:
                sub_ask.status = SubAskStatus.NEEDS_FOLLOWUP
                sub_ask.updated_at = datetime.now().isoformat()

        self._save_state()
        self.logger.info(f"✅ Marked chat session {session_id} as needs follow-up: {reason}")

    def complete_workflow_for_sub_ask(self, sub_ask_id: str):
        """Mark workflow as completed for sub-ask"""
        if sub_ask_id not in self.sub_asks:
            self.logger.error(f"Sub-ask not found: {sub_ask_id}")
            return False

        sub_ask = self.sub_asks[sub_ask_id]
        sub_ask.workflow_completed = True
        sub_ask.updated_at = datetime.now().isoformat()

        if sub_ask.chat_session:
            sub_ask.chat_session.workflow_completed = True
            sub_ask.chat_session.updated_at = datetime.now().isoformat()

        self._save_state()
        self.logger.info(f"✅ Marked workflow as completed for sub-ask: {sub_ask_id}")

        return True

    def get_sub_asks_needing_attention(self) -> List[SubAsk]:
        """Get sub-asks that need revisit, update, or follow-up"""
        return [
            sub_ask for sub_ask in self.sub_asks.values()
            if sub_ask.status in [
                SubAskStatus.NEEDS_REVISIT,
                SubAskStatus.NEEDS_UPDATE,
                SubAskStatus.NEEDS_FOLLOWUP
            ]
        ]

    def get_chat_sessions_needing_attention(self) -> List[SubAgentChatSession]:
        """Get chat sessions that need revisit, update, or follow-up"""
        return [
            session for session in self.chat_sessions.values()
            if session.chat_status in [
                SubAgentChatStatus.NEEDS_REVISIT,
                SubAgentChatStatus.NEEDS_UPDATE,
                SubAgentChatStatus.NEEDS_FOLLOWUP
            ]
        ]


def main():
    """Main execution for testing"""
    manager = SubAskTodoManager()

    print("=" * 80)
    print("🔧 SUB-ASK TODO MANAGER")
    print("=" * 80)

    # Create a test sub-ask
    sub_ask = manager.create_sub_ask(
        parent_ask_id="test_parent",
        sub_ask_text="Test sub-ask: Process outstanding items",
        agent_name="Test Agent",
        workflow_id="test_workflow"
    )

    print(f"\n✅ Created sub-ask: {sub_ask.sub_ask_id}")
    print(f"   Todo List ID: {sub_ask.todo_list.todo_list_id}")
    print(f"   Chat Session ID: {sub_ask.chat_session.session_id}")
    print(f"   Status: {sub_ask.status.value}")

    # Add a todo
    manager.add_todo_to_sub_ask(
        sub_ask.sub_ask_id,
        "Complete workflow execution",
        "Execute the workflow for this sub-ask"
    )

    print(f"\n✅ Added todo to sub-ask")
    print(f"   Total todos: {sub_ask.todo_list.total_count}")


if __name__ == "__main__":



    main()