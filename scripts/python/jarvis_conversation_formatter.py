#!/usr/bin/env python3
"""
JARVIS Conversation Formatter

Formats conversations with clear speaker labels so you can easily distinguish
between human and AI/JARVIS messages.

@JARVIS @CONVERSATION @FORMATTER
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Speaker(Enum):
    """Conversation speaker types"""
    HUMAN = "human"
    JARVIS = "jarvis"
    SYSTEM = "system"


@dataclass
class FormattedMessage:
    """Formatted message with clear speaker identification"""
    speaker: Speaker
    content: str
    timestamp: datetime
    formatted: str  # Pre-formatted display string

    def __str__(self) -> str:
        return self.formatted


class ConversationFormatter:
    """
    Formats conversations with clear speaker labels.

    Ensures you can always tell who is speaking (human vs AI/JARVIS).
    """

    # Visual indicators
    HUMAN_PREFIX = "👤 HUMAN:"
    JARVIS_PREFIX = "🤖 JARVIS:"
    SYSTEM_PREFIX = "⚙️  SYSTEM:"

    # Alternative text-only prefixes
    HUMAN_PREFIX_TEXT = "HUMAN:"
    JARVIS_PREFIX_TEXT = "JARVIS:"
    SYSTEM_PREFIX_TEXT = "SYSTEM:"

    def __init__(self, use_emojis: bool = True, use_timestamps: bool = True,
                 use_colors: bool = False):
        """
        Initialize formatter

        Args:
            use_emojis: Use emoji prefixes (👤, 🤖, ⚙️)
            use_timestamps: Include timestamps in formatted messages
            use_colors: Use ANSI color codes (for terminals that support it)
        """
        self.use_emojis = use_emojis
        self.use_timestamps = use_timestamps
        self.use_colors = use_colors

    def format_message(self, speaker: Speaker, content: str, 
                      timestamp: Optional[datetime] = None) -> FormattedMessage:
        """
        Format a single message with clear speaker identification

        Args:
            speaker: Who is speaking
            content: Message content
            timestamp: When the message was sent (current time if None)

        Returns:
            FormattedMessage with formatted display string
        """
        if timestamp is None:
            timestamp = datetime.now()

        # Select prefix based on speaker
        if speaker == Speaker.HUMAN:
            prefix = self.HUMAN_PREFIX if self.use_emojis else self.HUMAN_PREFIX_TEXT
        elif speaker == Speaker.JARVIS:
            prefix = self.JARVIS_PREFIX if self.use_emojis else self.JARVIS_PREFIX_TEXT
        else:  # SYSTEM
            prefix = self.SYSTEM_PREFIX if self.use_emojis else self.SYSTEM_PREFIX_TEXT

        # Build formatted string
        parts = [prefix]

        if self.use_timestamps:
            time_str = timestamp.strftime("%H:%M:%S")
            parts.append(f"[{time_str}]")

        parts.append(content)

        formatted_str = " ".join(parts)

        # Apply colors if enabled
        if self.use_colors:
            if speaker == Speaker.HUMAN:
                formatted_str = f"\033[36m{formatted_str}\033[0m"  # Cyan
            elif speaker == Speaker.JARVIS:
                formatted_str = f"\033[33m{formatted_str}\033[0m"  # Yellow
            else:  # SYSTEM
                formatted_str = f"\033[90m{formatted_str}\033[0m"  # Gray

        return FormattedMessage(
            speaker=speaker,
            content=content,
            timestamp=timestamp,
            formatted=formatted_str
        )

    def format_conversation(self, messages: List[Dict[str, Any]]) -> List[FormattedMessage]:
        """
        Format a list of conversation messages

        Args:
            messages: List of message dicts with 'speaker' and 'content' keys
                     Can also have 'timestamp' key

        Returns:
            List of FormattedMessage objects
        """
        formatted_messages = []

        for msg in messages:
            # Determine speaker
            speaker_str = msg.get('speaker', '').lower()
            if speaker_str in ['human', 'user', 'you']:
                speaker = Speaker.HUMAN
            elif speaker_str in ['jarvis', 'ai', 'assistant', 'bot']:
                speaker = Speaker.JARVIS
            else:
                speaker = Speaker.SYSTEM

            # Get content
            content = msg.get('content', msg.get('text', msg.get('message', '')))

            # Get timestamp
            timestamp = None
            if 'timestamp' in msg:
                ts = msg['timestamp']
                if isinstance(ts, str):
                    timestamp = datetime.fromisoformat(ts)
                elif isinstance(ts, datetime):
                    timestamp = ts

            formatted_msg = self.format_message(speaker, content, timestamp)
            formatted_messages.append(formatted_msg)

        return formatted_messages

    def format_conversation_turn(self, user_input: str, jarvis_response: str,
                                 user_timestamp: Optional[datetime] = None,
                                 jarvis_timestamp: Optional[datetime] = None) -> List[FormattedMessage]:
        """
        Format a conversation turn (user input + JARVIS response)

        Args:
            user_input: What the human said
            jarvis_response: What JARVIS responded
            user_timestamp: When the human spoke
            jarvis_timestamp: When JARVIS responded

        Returns:
            List of 2 FormattedMessage objects (human, then JARVIS)
        """
        messages = []

        # Human message
        messages.append(self.format_message(
            Speaker.HUMAN,
            user_input,
            user_timestamp
        ))

        # JARVIS message
        messages.append(self.format_message(
            Speaker.JARVIS,
            jarvis_response,
            jarvis_timestamp
        ))

        return messages

    def print_conversation(self, messages: List[FormattedMessage], separator: str = "\n"):
        """
        Print formatted conversation to stdout

        Args:
            messages: List of FormattedMessage objects
            separator: Separator between messages (default: newline)
        """
        for msg in messages:
            print(msg.formatted, end=separator)

    def format_for_display(self, messages: List[FormattedMessage]) -> str:
        """
        Format conversation as a single string for display

        Args:
            messages: List of FormattedMessage objects

        Returns:
            Formatted string with all messages
        """
        return "\n".join(msg.formatted for msg in messages)

    def create_conversation_markdown(self, messages: List[FormattedMessage]) -> str:
        """
        Create markdown-formatted conversation

        Args:
            messages: List of FormattedMessage objects

        Returns:
            Markdown-formatted conversation
        """
        lines = []
        for msg in messages:
            if msg.speaker == Speaker.HUMAN:
                lines.append(f"**👤 Human:** {msg.content}")
            elif msg.speaker == Speaker.JARVIS:
                lines.append(f"**🤖 JARVIS:** {msg.content}")
            else:
                lines.append(f"**⚙️ System:** {msg.content}")

            if self.use_timestamps:
                time_str = msg.timestamp.strftime("%H:%M:%S")
                lines[-1] += f" *[{time_str}]*"

        return "\n\n".join(lines)


# Convenience functions
def format_human_message(content: str, timestamp: Optional[datetime] = None) -> str:
    """Quick format human message"""
    formatter = ConversationFormatter()
    return formatter.format_message(Speaker.HUMAN, content, timestamp).formatted


def format_jarvis_message(content: str, timestamp: Optional[datetime] = None) -> str:
    """Quick format JARVIS message"""
    formatter = ConversationFormatter()
    return formatter.format_message(Speaker.JARVIS, content, timestamp).formatted


def format_conversation_turn(user_input: str, jarvis_response: str) -> str:
    """Quick format a conversation turn"""
    formatter = ConversationFormatter()
    messages = formatter.format_conversation_turn(user_input, jarvis_response)
    return formatter.format_for_display(messages)


if __name__ == "__main__":
    # Example usage
    formatter = ConversationFormatter(use_emojis=True, use_timestamps=True)

    # Example conversation
    messages = formatter.format_conversation_turn(
        "What's the system status?",
        "The system is operating normally. All components are healthy."
    )

    print("Example Conversation:")
    print("=" * 80)
    formatter.print_conversation(messages)
    print("=" * 80)

    # Example with multiple turns
    print("\n\nMulti-turn Conversation:")
    print("=" * 80)

    conversation = [
        {"speaker": "human", "content": "Hello JARVIS", "timestamp": datetime.now()},
        {"speaker": "jarvis", "content": "Hello! How can I assist you today?", "timestamp": datetime.now()},
        {"speaker": "human", "content": "What's the weather like?", "timestamp": datetime.now()},
        {"speaker": "jarvis", "content": "I don't have access to weather data at the moment.", "timestamp": datetime.now()},
    ]

    formatted = formatter.format_conversation(conversation)
    formatter.print_conversation(formatted)
    print("=" * 80)
