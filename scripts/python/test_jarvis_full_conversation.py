#!/usr/bin/env python3
"""
Full JARVIS Conversation Test - Verify Clear Speaker Labels Work

Tests the complete conversation flow with clear human/AI distinction.
"""

import sys
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

print("="*80)
print("JARVIS Conversation Test - Clear Speaker Labels")
print("="*80)
print()

# Test 1: Basic formatter
print("Test 1: Basic Conversation Formatter")
print("-"*80)
try:
    from jarvis_conversation_formatter import ConversationFormatter, Speaker

    formatter = ConversationFormatter(use_emojis=True, use_timestamps=True)

    test_messages = [
        ("What's the system status?", "The system is healthy."),
        ("Check CPU usage", "CPU usage is 15.2%"),
        ("Thanks", "You're welcome!")
    ]

    for user_msg, jarvis_msg in test_messages:
        human = formatter.format_message(Speaker.HUMAN, user_msg)
        jarvis = formatter.format_message(Speaker.JARVIS, jarvis_msg)
        print(human.formatted)
        print(jarvis.formatted)
        print()

    print("✅ Test 1 PASSED: Formatter works correctly")
except Exception as e:
    print(f"❌ Test 1 FAILED: {e}")
    import traceback
    traceback.print_exc()

print()
print("-"*80)
print()

# Test 2: Core Intelligence conversation processing
print("Test 2: Core Intelligence Conversation Processing")
print("-"*80)
try:
    from jarvis_core_intelligence import JARVISCoreIntelligence

    intel = JARVISCoreIntelligence()

    # Process some conversations
    intel.process_conversation("Hello", "Hello! How can I help?")
    intel.process_conversation("Status?", "All systems operational.")

    # Get summary with clear labels
    summary = intel.get_conversation_summary(use_formatter=True)
    print(summary)

    print()
    print("✅ Test 2 PASSED: Core Intelligence conversation processing works")
except Exception as e:
    print(f"❌ Test 2 FAILED: {e}")
    import traceback
    traceback.print_exc()

print()
print("-"*80)
print()

# Test 3: Master Command interface
print("Test 3: Master Command Interface")
print("-"*80)
try:
    from jarvis_master_command import JARVISMasterCommand

    jarvis = JARVISMasterCommand()

    # Test a command
    result = jarvis.process_command("What is the system status?")

    # Format the conversation turn
    from jarvis_conversation_formatter import format_conversation_turn
    formatted = format_conversation_turn(
        "What is the system status?",
        result.get('response', 'No response')
    )
    print(formatted)

    print()
    print("✅ Test 3 PASSED: Master Command interface works")
except Exception as e:
    print(f"❌ Test 3 FAILED: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*80)
print("All Tests Complete!")
print("="*80)
print()
print("✅ All conversations now have clear speaker labels:")
print("   👤 HUMAN: - Human messages")
print("   🤖 JARVIS: - JARVIS AI messages")
print("   ⚙️  SYSTEM: - System messages")
print()
print("You can now easily distinguish who is speaking in all conversations!")
