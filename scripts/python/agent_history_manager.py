#!/usr/bin/env python3
"""
Agent/Sub-Agent History Manager

Each chat = ask = workflow = pattern = sub-agent history

Agent vs Sub-Agent:
- Agent → Master to-do list
- Sub-Agent → Standard/PDIWN to-do list

Agent histories need statuses and proper tracking.
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
    from master_todo_tracker import MasterTodoTracker
    TODO_TRACKER_AVAILABLE = True
except ImportError:
    TODO_TRACKER_AVAILABLE = False
    MasterTodoTracker = None


class AgentType(Enum):
    """Agent type"""
    AGENT = "agent"  # Belongs to master to-do list
    SUB_AGENT = "sub_agent"  # Belongs to standard/PDIWN to-do list


class HistoryStatus(Enum):
    """Agent history status"""
    NEW = "new"
    ACTIVE = "active"
    UPDATED = "updated"
    ARCHIVED = "archived"
    NEEDS_REVISIT = "needs_revisit"
    NEEDS_UPDATE = "needs_update"
    NEEDS_FOLLOWUP = "needs_followup"


@dataclass
class AgentHistory:
    """Agent/Sub-Agent history"""
    history_id: str
    agent_type: AgentType
    agent_name: str
    chat_id: Optional[str] = None
    ask_id: Optional[str] = None
    workflow_id: Optional[str] = None
    pattern_id: Optional[str] = None
    sub_agent_history_id: Optional[str] = None  # If this is a sub-agent history
    status: HistoryStatus = HistoryStatus.NEW
    created_at: str = ""
    updated_at: str = ""
    last_accessed: str = ""
    todo_list_id: Optional[str] = None  # Master or standard/PDIWN to-do list
    pinned: bool = False  # Pin/unpin status
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["agent_type"] = self.agent_type.value
        data["status"] = self.status.value
        return data


class AgentHistoryManager:
    """
    Manages agent/sub-agent histories

    Each chat = ask = workflow = pattern = sub-agent history
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("AgentHistoryManager")

        # Directories
        self.data_dir = self.project_root / "data" / "agent_histories"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Files
        self.histories_file = self.data_dir / "agent_histories.json"

        # Todo tracker  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
        self.todo_tracker = MasterTodoTracker(project_root) if TODO_TRACKER_AVAILABLE else None

        # State
        self.histories: Dict[str, AgentHistory] = {}

        # Load state
        self._load_state()

    def _load_state(self):
        """Load agent histories"""
        if self.histories_file.exists():
            try:
                with open(self.histories_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for history_id, history_data in data.items():
                        history = AgentHistory(**history_data)
                        history.agent_type = AgentType(history_data["agent_type"])
                        history.status = HistoryStatus(history_data["status"])
                        self.histories[history_id] = history
            except Exception as e:
                self.logger.error(f"Error loading histories: {e}")

    def _save_state(self):
        try:
            """Save agent histories"""
            histories_data = {
                history_id: history.to_dict()
                for history_id, history in self.histories.items()
            }
            with open(self.histories_file, 'w', encoding='utf-8') as f:
                json.dump(histories_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _save_state: {e}", exc_info=True)
            raise
    def create_agent_history(
        self,
        agent_type: AgentType,
        agent_name: str,
        chat_id: Optional[str] = None,
        ask_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        pattern_id: Optional[str] = None
    ) -> AgentHistory:
        """
        Create agent/sub-agent history

        Each chat = ask = workflow = pattern = sub-agent history
        """
        now = datetime.now().isoformat()
        history_id = f"history_{int(datetime.now().timestamp() * 1000)}"

        # Determine todo list type
        todo_list_id = None
        if agent_type == AgentType.AGENT:
            # Agent → Master to-do list
            todo_list_id = "master_todo_list"
        elif agent_type == AgentType.SUB_AGENT:
            # Sub-Agent → Standard/PDIWN to-do list
            todo_list_id = "standard_todo_list"

        history = AgentHistory(
            history_id=history_id,
            agent_type=agent_type,
            agent_name=agent_name,
            chat_id=chat_id,
            ask_id=ask_id,
            workflow_id=workflow_id,
            pattern_id=pattern_id,
            status=HistoryStatus.NEW,
            created_at=now,
            updated_at=now,
            last_accessed=now,
            todo_list_id=todo_list_id
        )

        self.histories[history_id] = history

        self.logger.info(f"✅ Created {agent_type.value} history: {history_id} ({agent_name})")

        self._save_state()

        return history

    def update_history_status(
        self,
        history_id: str,
        status: HistoryStatus,
        reason: Optional[str] = None
    ) -> bool:
        """Update history status"""
        if history_id not in self.histories:
            self.logger.error(f"History not found: {history_id}")
            return False

        history = self.histories[history_id]
        history.status = status
        history.updated_at = datetime.now().isoformat()
        history.last_accessed = datetime.now().isoformat()

        if reason:
            history.metadata["status_change_reason"] = reason

        self._save_state()

        self.logger.info(f"✅ Updated history {history_id} status: {status.value}")

        return True

    def link_chat_ask_workflow_pattern(
        self,
        history_id: str,
        chat_id: Optional[str] = None,
        ask_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        pattern_id: Optional[str] = None
    ) -> bool:
        """
        Link chat = ask = workflow = pattern to history

        Each chat = ask = workflow = pattern = sub-agent history
        """
        if history_id not in self.histories:
            self.logger.error(f"History not found: {history_id}")
            return False

        history = self.histories[history_id]

        if chat_id:
            history.chat_id = chat_id
        if ask_id:
            history.ask_id = ask_id
        if workflow_id:
            history.workflow_id = workflow_id
        if pattern_id:
            history.pattern_id = pattern_id

        history.updated_at = datetime.now().isoformat()

        self._save_state()

        self.logger.info(f"✅ Linked chat/ask/workflow/pattern to history {history_id}")

        return True

    def get_histories_by_type(self, agent_type: AgentType) -> List[AgentHistory]:
        """Get histories by agent type"""
        return [
            history for history in self.histories.values()
            if history.agent_type == agent_type
        ]

    def get_histories_needing_attention(self) -> List[AgentHistory]:
        """Get histories that need revisit/update/follow-up"""
        return [
            history for history in self.histories.values()
            if history.status in [
                HistoryStatus.NEEDS_REVISIT,
                HistoryStatus.NEEDS_UPDATE,
                HistoryStatus.NEEDS_FOLLOWUP
            ]
        ]

    def pin_history(self, history_id: str) -> bool:
        """Pin an agent history"""
        if history_id not in self.histories:
            self.logger.error(f"History not found: {history_id}")
            return False

        history = self.histories[history_id]
        history.pinned = True
        history.updated_at = datetime.now().isoformat()
        history.last_accessed = datetime.now().isoformat()

        if "pin_history" not in history.metadata:
            history.metadata["pin_history"] = []
        history.metadata["pin_history"].append({
            "pinned_at": datetime.now().isoformat(),
            "action": "pin"
        })

        self._save_state()
        self.logger.info(f"✅ Pinned history: {history_id}")

        return True

    def unpin_history(self, history_id: str) -> bool:
        """Unpin an agent history"""
        if history_id not in self.histories:
            self.logger.error(f"History not found: {history_id}")
            return False

        history = self.histories[history_id]
        history.pinned = False
        history.updated_at = datetime.now().isoformat()
        history.last_accessed = datetime.now().isoformat()

        if "pin_history" not in history.metadata:
            history.metadata["pin_history"] = []
        history.metadata["pin_history"].append({
            "unpinned_at": datetime.now().isoformat(),
            "action": "unpin"
        })

        self._save_state()
        self.logger.info(f"✅ Unpinned history: {history_id}")

        return True

    def get_pinned_histories(self) -> List[AgentHistory]:
        """Get all pinned histories"""
        return [
            history for history in self.histories.values()
            if history.pinned
        ]

    def search_histories(
        self,
        keyword: str,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search agent histories by keyword with pagination

        Args:
            keyword: Search keyword
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            Dictionary with items, total, and hasMore
        """
        keyword_lower = keyword.lower()
        matching_histories = []

        for history in self.histories.values():
            # Search in agent name, chat_id, ask_id, workflow_id, pattern_id
            searchable_fields = [
                history.agent_name,
                history.chat_id or "",
                history.ask_id or "",
                history.workflow_id or "",
                history.pattern_id or "",
                history.status.value
            ]

            # Also search in metadata if it contains text
            metadata_text = json.dumps(history.metadata, ensure_ascii=False).lower()

            if (any(keyword_lower in str(field).lower() for field in searchable_fields) or
                keyword_lower in metadata_text):
                matching_histories.append(history)

        # Sort by last_accessed (most recent first)
        matching_histories.sort(
            key=lambda h: h.last_accessed or h.created_at,
            reverse=True
        )

        total = len(matching_histories)
        paginated_results = matching_histories[offset:offset + limit]
        has_more = (offset + limit) < total

        return {
            "items": [h.to_dict() for h in paginated_results],
            "total": total,
            "hasMore": has_more,
            "offset": offset,
            "limit": limit
        }

    def get_history_by_id(self, history_id: str) -> Optional[AgentHistory]:
        """Get agent history by ID"""
        if history_id not in self.histories:
            self.logger.warning(f"History not found: {history_id}")
            return None

        history = self.histories[history_id]
        history.last_accessed = datetime.now().isoformat()
        self._save_state()

        return history


def main():
    """Main execution for testing"""
    manager = AgentHistoryManager()

    print("=" * 80)
    print("📚 AGENT HISTORY MANAGER")
    print("=" * 80)

    # Create agent history (master to-do list)
    agent_history = manager.create_agent_history(
        agent_type=AgentType.AGENT,
        agent_name="Master Agent",
        chat_id="chat_123",
        ask_id="ask_456",
        workflow_id="workflow_789",
        pattern_id="pattern_abc"
    )

    print(f"\n✅ Created agent history:")
    print(f"   History ID: {agent_history.history_id}")
    print(f"   Agent Type: {agent_history.agent_type.value}")
    print(f"   Todo List: {agent_history.todo_list_id}")
    print(f"   Status: {agent_history.status.value}")

    # Create sub-agent history (standard to-do list)
    sub_agent_history = manager.create_agent_history(
        agent_type=AgentType.SUB_AGENT,
        agent_name="Sub-Agent",
        chat_id="chat_123",  # Same chat
        ask_id="ask_456",
        workflow_id="workflow_789",
        pattern_id="pattern_abc"
    )

    print(f"\n✅ Created sub-agent history:")
    print(f"   History ID: {sub_agent_history.history_id}")
    print(f"   Agent Type: {sub_agent_history.agent_type.value}")
    print(f"   Todo List: {sub_agent_history.todo_list_id}")
    print(f"   Status: {sub_agent_history.status.value}")


if __name__ == "__main__":



    main()