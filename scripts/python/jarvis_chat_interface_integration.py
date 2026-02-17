"""
JARVIS Chat Interface Integration
Integrates dual TODO lists and conversational features into the Cursor IDE chat interface.

Terminology:
- "Cursor Agent Chat" / "Cursor Chat" = The Cursor IDE chat interface
- "JARVIS Chat Interface" = When JARVIS is integrated/controlling the chat
- "Agent Chat Sessions" = Individual chat sessions

Author: JARVIS System
Date: 2026-01-09
Tags: #JARVIS @LUMINA #CHAT #INTEGRATION
"""

import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from jarvis_conversational_todo_display import JARVISConversationalTODODisplay
from jarvis_grammarly_oversight import JARVISGrammarlyOversight

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)


class JARVISChatInterface:
    """
    JARVIS Chat Interface Integration.

    Provides:
    - Dual TODO list display (Master + Padawan/OEM)
    - Auto-collapse after timeout
    - Conversational triggers
    - Grammarly oversight
    - Session management
    """

    def __init__(self, project_root: Optional[Path] = None,
                 auto_display_todos: bool = True,
                 auto_collapse_timeout: float = 300.0):
        """
        Initialize JARVIS Chat Interface.

        Args:
            project_root: Project root directory
            auto_display_todos: Auto-display TODO lists at session start
            auto_collapse_timeout: Auto-collapse timeout in seconds
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)

        self.todo_display = JARVISConversationalTODODisplay(
            project_root=project_root,
            auto_collapse_timeout=auto_collapse_timeout
        )
        self.grammarly_oversight = JARVISGrammarlyOversight(project_root=project_root)

        self.auto_display_todos = auto_display_todos
        self.session_start_time = time.time()
        self.last_todo_display = 0.0
        self.message_count = 0

        # Session metadata
        self.session_id = f"jarvis_chat_{int(time.time())}"
        self.session_metadata = {
            'session_id': self.session_id,
            'start_time': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'auto_display_todos': auto_display_todos,
            'timeout': auto_collapse_timeout
        }

    def get_session_startup_message(self) -> str:
        """
        Get startup message for chat session.

        Returns:
            Formatted startup message with TODO lists
        """
        lines = []
        lines.append("🤖 **JARVIS Chat Interface Active**")
        lines.append("")

        if self.auto_display_todos:
            todo_display = self.todo_display.get_conversational_display(force_expand=True)
            lines.append(todo_display)
            self.last_todo_display = time.time()
        else:
            lines.append("💬 Ready for conversation. Say 'show todos' to see task lists.")

        lines.append("")
        lines.append("**Features:**")
        lines.append("- Dual TODO lists (Master + Padawan/OEM)")
        lines.append("- Auto-collapse after timeout")
        lines.append("- Conversational triggers")
        lines.append("- Grammarly oversight")

        return "\n".join(lines)

    def process_message(self, message: str, user_message: bool = True) -> Dict[str, Any]:
        """
        Process a chat message.

        Args:
            message: The message text
            user_message: True if from user, False if from AI

        Returns:
            Dictionary with processing results
        """
        self.message_count += 1

        result = {
            'session_id': self.session_id,
            'message_count': self.message_count,
            'timestamp': datetime.now().isoformat(),
            'todo_display': None,
            'grammarly_review': None,
            'triggers': []
        }

        # Check for TODO display triggers
        if user_message:
            todo_trigger = self.todo_display.handle_conversational_trigger(message)
            if todo_trigger:
                result['todo_display'] = todo_trigger
                result['triggers'].append('todo_display')
                self.last_todo_display = time.time()

        # Check if should auto-display TODOs
        if self.auto_display_todos and user_message:
            time_since_last = time.time() - self.last_todo_display
            if time_since_last > 600:  # 10 minutes
                result['todo_display'] = self.todo_display.get_conversational_display()
                result['triggers'].append('auto_display_todos')
                self.last_todo_display = time.time()

        # Grammarly oversight (if message was corrected)
        # This would be called by Grammarly-CLI integration
        # For now, we just track that oversight is available

        return result

    def get_todo_status_summary(self) -> str:
        """Get brief TODO status summary."""
        return self.todo_display.get_status_summary()

    def should_show_todos(self) -> bool:
        """Check if TODO lists should be displayed."""
        return self.todo_display.should_display()

    def get_chat_context(self) -> Dict[str, Any]:
        """
        Get current chat context for JARVIS.

        Returns:
            Dictionary with chat context
        """
        todo_summary = self.todo_display.todo_manager.get_display_summary()
        grammarly_summary = self.grammarly_oversight.get_oversight_summary()

        return {
            'session': self.session_metadata,
            'todo': {
                'master_pending': todo_summary['master']['pending'],
                'padawan_pending': todo_summary['padawan']['pending'],
                'should_display': self.should_show_todos(),
                'is_expanded': todo_summary['is_expanded']
            },
            'grammarly': {
                'conversational_mode': grammarly_summary['conversational_mode'],
                'total_contributions': grammarly_summary['total_contributions']
            },
            'session_stats': {
                'message_count': self.message_count,
                'session_duration': time.time() - self.session_start_time
            }
        }

    def format_contextual_response(self, base_response: str, 
                                  include_todos: bool = True) -> str:
        """
        Format a response with contextual information.

        Args:
            base_response: Base response text
            include_todos: Include TODO status if relevant

        Returns:
            Formatted response
        """
        lines = [base_response]

        if include_todos and self.should_show_todos():
            todo_status = self.get_todo_status_summary()
            if "completed" not in todo_status.lower():
                lines.append("")
                lines.append(f"📋 {todo_status}")

        return "\n".join(lines)


def get_jarvis_chat_startup(project_root: Optional[Path] = None,
                           auto_display: bool = True) -> str:
    """
    Convenience function to get JARVIS chat startup message.

    Args:
        project_root: Project root directory
        auto_display: Auto-display TODO lists

    Returns:
        Startup message string
    """
    chat = JARVISChatInterface(project_root=project_root, 
                              auto_display_todos=auto_display)
    return chat.get_session_startup_message()


if __name__ == "__main__":
    # Demo
    chat = JARVISChatInterface()
    print(chat.get_session_startup_message())
    print("\n" + "="*60)
    print("\nContext:")
    import json
    print(json.dumps(chat.get_chat_context(), indent=2))
