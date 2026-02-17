"""
JARVIS Conversational TODO Display
Integrates dual TODO lists with conversational flow and auto-collapse.

Author: JARVIS System
Date: 2026-01-09
Tags: #JARVIS @LUMINA #TODO #CONVERSATIONAL  # [ADDRESSED]  # [ADDRESSED]
"""

import time
from pathlib import Path
from typing import Dict, Any, Optional

from jarvis_dual_todo_manager import JARVISDualTODOManager, TODOStatus

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)


class JARVISConversationalTODODisplay:
    """
    Conversational display system for dual TODO lists.

    Features:
    - Always shows both lists (Master + Padawan/OEM)
    - Auto-collapse after timeout
    - Natural conversational integration
    - Context-aware display
    """

    def __init__(self, project_root: Optional[Path] = None, 
                 auto_collapse_timeout: float = 300.0):
        """
        Initialize conversational TODO display.

        Args:
            project_root: Project root directory
            auto_collapse_timeout: Auto-collapse timeout in seconds (default: 5 minutes)
        """
        self.todo_manager = JARVISDualTODOManager(project_root)
        self.todo_manager.set_timeout(auto_collapse_timeout)
        self.last_display_time = 0.0

    def get_conversational_display(self, force_expand: bool = False) -> str:
        """
        Get conversational display of TODO lists.

        Args:
            force_expand: Force expansion even if timeout expired

        Returns:
            Formatted string for chat display
        """
        if force_expand:
            self.todo_manager.expand_lists()

        summary = self.todo_manager.get_display_summary()
        self.last_display_time = time.time()

        return self.todo_manager.format_conversational_display(summary)

    def should_display(self) -> bool:
        """
        Check if TODO lists should be displayed.

        Returns:
            True if should display
        """
        # Always show if there are pending items
        summary = self.todo_manager.get_display_summary()
        has_pending = (summary['master']['pending'] > 0 or 
                      summary['padawan']['pending'] > 0)

        if has_pending:
            return True

        # Show if recently interacted with
        if time.time() - self.last_display_time < 60:  # 1 minute
            return True

        return False

    def handle_conversational_trigger(self, message: str) -> Optional[str]:
        """
        Handle conversational triggers for TODO display.

        Args:
            message: User message

        Returns:
            Display string if triggered, None otherwise
        """
        triggers = [
            "show todos", "show todo", "todos", "todo list",
            "what's pending", "what's next", "tasks",
            "show master", "show padawan", "show oem"
        ]

        message_lower = message.lower().strip()

        for trigger in triggers:
            if trigger in message_lower:
                return self.get_conversational_display(force_expand=True)

        return None

    def get_status_summary(self) -> str:
        """Get brief status summary for conversational context."""
        summary = self.todo_manager.get_display_summary()

        master_pending = summary['master']['pending']
        padawan_pending = summary['padawan']['pending']

        if master_pending == 0 and padawan_pending == 0:
            return "✅ All TODO items completed"

        parts = []
        if master_pending > 0:
            parts.append(f"{master_pending} master")
        if padawan_pending > 0:
            parts.append(f"{padawan_pending} padawan")

        return f"📋 {', '.join(parts)} TODO items pending"


def get_conversational_todo_display(project_root: Optional[Path] = None,
                                   timeout: float = 300.0) -> str:
    """
    Convenience function to get conversational TODO display.

    Args:
        project_root: Project root directory
        timeout: Auto-collapse timeout in seconds

    Returns:
        Formatted TODO display string
    """
    display = JARVISConversationalTODODisplay(project_root, timeout)
    return display.get_conversational_display()


if __name__ == "__main__":
    display = JARVISConversationalTODODisplay()
    print(display.get_conversational_display())
