#!/usr/bin/env python3
"""
Verify Administrative Access Memory

Verifies that the critical administrative access memory is stored and accessible.
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from jarvis_persistent_memory import JARVISPersistentMemory, MemoryPriority, MemoryType
    from lumina_logger import get_logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("VerifyAdminAccessMemory")


def verify_memory():
    """Verify administrative access memory is stored"""
    print("=" * 80)
    print("🔍 VERIFYING ADMINISTRATIVE ACCESS MEMORY")
    print("=" * 80)
    print()

    memory_system = JARVISPersistentMemory(project_root)

    # Search for administrative access memory
    memories = memory_system.search_memories(
        query="administrative access",
        memory_type=MemoryType.LONG_TERM,
        tags=["administrative_access"],
        limit=10
    )

    # Filter by CRITICAL priority
    memories = [m for m in memories if m.priority == MemoryPriority.CRITICAL]

    if memories:
        print(f"✅ Found {len(memories)} administrative access memory(ies)")
        print()

        for memory in memories:
            print(f"Memory ID: {memory.memory_id}")
            print(f"Priority: {memory.priority.value} ({memory.priority.to_importance_rating()}/5)")
            print(f"Type: {memory.memory_type.value}")
            print(f"Content Preview: {memory.content[:200]}...")
            print(f"Tags: {', '.join(memory.tags)}")
            print(f"Context: {memory.context}")
            print()
            print("=" * 80)
    else:
        print("❌ Administrative access memory not found")
        print("   Please run: python scripts/python/store_administrative_access_memory.py")
        print()

    # Also check all CRITICAL memories
    all_memories = memory_system.retrieve_all_memories()
    all_critical = [m for m in all_memories if m.priority == MemoryPriority.CRITICAL]

    print(f"📊 Total CRITICAL memories: {len(all_critical)}")
    print()


if __name__ == "__main__":
    verify_memory()
