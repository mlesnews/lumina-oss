#!/usr/bin/env python3
"""
Test: MAGIS AI + JARVIS Chat History Processing

Demonstrates adding chat history items to unified queue
that are automatically processed by MAGIS AI + JARVIS async processor.

Usage:
    python scripts/python/test_magis_jarvis_chat_history.py
"""

import sys
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

from unified_queue_adapter import UnifiedQueueAdapter

def main():
    """Test chat history processing"""
    print("=" * 80)
    print("🧪 Testing MAGIS AI + JARVIS Chat History Processing")
    print("=" * 80)
    print()

    # Initialize adapter (starts MAGIS AI + JARVIS processor)
    adapter = UnifiedQueueAdapter()

    # Add test chat history items
    print("➕ Adding chat history items to queue...")
    print()

    # Test item 1
    item1_id = adapter.add_chat_history(
        session_id="test_session_001",
        agent_name="Cursor Agent",
        title="Code Review Session",
        description="Reviewing Python code for improvements",
        message_count=15,
        priority="high"
    )
    print(f"   ✅ Added: {item1_id}")

    # Test item 2
    item2_id = adapter.add_chat_history(
        session_id="test_session_002",
        agent_name="JARVIS",
        title="System Configuration",
        description="Configuring unified queue system",
        message_count=8,
        priority="normal"
    )
    print(f"   ✅ Added: {item2_id}")

    # Test item 3
    item3_id = adapter.add_chat_history(
        session_id="test_session_003",
        agent_name="MAGIS AI",
        title="Intelligence Extraction",
        description="Extracting intelligence from chat session",
        message_count=22,
        priority="high"
    )
    print(f"   ✅ Added: {item3_id}")

    print()
    print("📊 Queue Summary:")
    adapter.print_queue_summary()

    print()
    print("⏳ MAGIS AI + JARVIS will process these items asynchronously...")
    print("   Check queue status in IDE footer or run:")
    print("   python scripts/python/unified_queue_viewer.py")
    print()
    print("=" * 80)

if __name__ == "__main__":


    main()