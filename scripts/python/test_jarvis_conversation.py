#!/usr/bin/env python3
"""
Test JARVIS Conversation with Clear Speaker Labels

Demonstrates how conversations now clearly distinguish between human and AI messages.

@JARVIS @CONVERSATION @TEST
"""

import sys
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from jarvis_conversation_formatter import ConversationFormatter, Speaker


def main():
    """Test conversation formatting"""
    print("="*80)
    print("JARVIS Conversation Formatter - Clear Speaker Labels")
    print("="*80)
    print()
    print("All conversations now clearly label who is speaking:")
    print("  👤 HUMAN: - Messages from the human user")
    print("  🤖 JARVIS: - Messages from JARVIS AI")
    print("  ⚙️  SYSTEM: - System messages")
    print()
    print("="*80)
    print()

    # Create formatter
    formatter = ConversationFormatter(use_emojis=True, use_timestamps=True)

    # Example conversation
    conversation_turns = [
        ("Hello JARVIS, what's the system status?", 
         "Hello! The system is operating normally. All components are healthy."),
        ("Can you check the CPU usage?", 
         "CPU usage is currently at 15.2%. Memory usage is 29.2%. Disk usage is 89.7% with a warning."),
        ("Thanks!",
         "You're welcome! Is there anything else I can help you with?")
    ]

    print("Example Conversation:")
    print("-"*80)

    for user_input, jarvis_response in conversation_turns:
        messages = formatter.format_conversation_turn(user_input, jarvis_response)
        formatter.print_conversation(messages)
        print()

    print("-"*80)
    print()
    print("✅ As you can see, it's now crystal clear who is speaking!")
    print()
    print("Try the interactive mode:")
    print("  python scripts/python/jarvis_master_command.py --interactive")
    print()


if __name__ == "__main__":


    main()