#!/usr/bin/env python3
"""
Prevent Memory Gap Automation

"Laziness is the prime attribute of a successful programmer"
"We hate doing anything more than twice, if we don't script it first"

ROOT CAUSE: Persistent memory gaps causing repetitive work.

This system:
- Checks if memories already exist before storing
- Prevents duplicate memory storage
- Automates memory gap detection
- Applies DRY principle (Don't Repeat Yourself)

Tags: #automation #memory_gaps #DRY #laziness #efficiency
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger
from jarvis_persistent_memory import JARVISPersistentMemory, MemoryType, MemoryPriority

logger = get_logger("PreventMemoryGapAutomation")


class MemoryGapPrevention:
    """
    Memory Gap Prevention System

    Prevents storing duplicate memories by checking existing ones first.
    Applies DRY principle: "We hate doing anything more than twice"
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize memory gap prevention"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.memory = JARVISPersistentMemory(project_root)

        logger.info("=" * 80)
        logger.info("🛡️  MEMORY GAP PREVENTION SYSTEM")
        logger.info("=" * 80)
        logger.info("   Principle: Laziness is the prime attribute of a successful programmer")
        logger.info("   Rule: We hate doing anything more than twice, if we don't script it first")
        logger.info("   Goal: Prevent persistent memory gaps")
        logger.info("=" * 80)
        logger.info("")

    def check_memory_exists(
        self,
        content_keywords: List[str],
        tags: Optional[List[str]] = None,
        category: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Check if a memory with similar content already exists

        Returns existing memory if found, None otherwise
        """
        # Search by tags first (most efficient)
        if tags:
            results = self.memory.search_memories(query="", tags=tags, limit=50)
            if results:
                logger.info(f"✅ Found {len(results)} existing memories with tags: {tags}")
                return results[0].to_dict()

        # Search by content keywords
        for keyword in content_keywords:
            results = self.memory.search_memories(query=keyword, limit=20)
            if results:
                # Check if any match the keywords
                for result in results:
                    content_lower = result.content.lower()
                    if any(kw.lower() in content_lower for kw in content_keywords):
                        logger.info(f"✅ Found existing memory matching keyword: {keyword}")
                        return result.to_dict()

        return None

    def store_memory_safely(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.LONG_TERM,
        priority: MemoryPriority = MemoryPriority.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        source: str = "",
        content_keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Store memory only if it doesn't already exist

        Returns dict with 'stored' (bool) and 'memory_id' or 'existing_memory'
        """
        # Extract keywords from content if not provided
        if content_keywords is None:
            # Simple keyword extraction (first few significant words)
            words = content.split()[:10]
            content_keywords = [w for w in words if len(w) > 4]

        # Check if memory already exists
        existing = self.check_memory_exists(
            content_keywords=content_keywords,
            tags=tags,
            category=context.get('category') if context else None
        )

        if existing:
            logger.warning("")
            logger.warning("⚠️  MEMORY ALREADY EXISTS - NOT STORING DUPLICATE")
            logger.warning("=" * 80)
            logger.warning(f"   Existing Memory ID: {existing.get('memory_id', 'unknown')}")
            logger.warning(f"   Priority: {existing.get('priority', 'unknown')}")
            logger.warning(f"   Type: {existing.get('memory_type', 'unknown')}")
            logger.warning(f"   Content preview: {existing.get('content', '')[:100]}...")
            logger.warning("")
            logger.warning("   ✅ DRY Principle Applied: Don't Repeat Yourself")
            logger.warning("   ✅ Laziness Principle: We hate doing anything more than twice")
            logger.warning("")

            return {
                "stored": False,
                "existing_memory": existing,
                "reason": "Memory already exists"
            }

        # Memory doesn't exist, store it
        memory_id = self.memory.store_memory(
            content=content,
            memory_type=memory_type,
            priority=priority,
            context=context or {},
            tags=tags or [],
            source=source
        )

        logger.info("")
        logger.info("✅ NEW MEMORY STORED")
        logger.info(f"   Memory ID: {memory_id}")
        logger.info("")

        return {
            "stored": True,
            "memory_id": memory_id,
            "reason": "New memory stored"
        }


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Prevent Memory Gap Automation")
    parser.add_argument('--check', type=str, help='Check if memory exists (provide keyword)')
    parser.add_argument('--test', action='store_true', help='Test memory gap prevention')

    args = parser.parse_args()

    prevention = MemoryGapPrevention()

    if args.check:
        existing = prevention.check_memory_exists(content_keywords=[args.check])
        if existing:
            print(f"\n✅ Memory exists: {existing.get('memory_id', 'unknown')}")
            print(f"   Content: {existing.get('content', '')[:200]}...")
        else:
            print(f"\n❌ No existing memory found for: {args.check}")

    elif args.test:
        # Test: Try to store a memory that likely already exists
        logger.info("🧪 Testing memory gap prevention...")
        logger.info("")

        result = prevention.store_memory_safely(
            content="LOGGING = DOCUMENTING - They share the same principal intention.",
            memory_type=MemoryType.LONG_TERM,
            priority=MemoryPriority.CRITICAL,
            tags=["logging", "documentation", "standard"],
            content_keywords=["logging", "documenting", "principal", "intention"]
        )

        print("\n" + "=" * 80)
        print("🧪 TEST RESULT")
        print("=" * 80)
        print(f"Stored: {result['stored']}")
        print(f"Reason: {result['reason']}")
        if result.get('existing_memory'):
            print(f"Existing Memory ID: {result['existing_memory'].get('memory_id')}")
        elif result.get('memory_id'):
            print(f"New Memory ID: {result['memory_id']}")
        print("=" * 80)
        print("")

    else:
        print("\n" + "=" * 80)
        print("🛡️  MEMORY GAP PREVENTION SYSTEM")
        print("=" * 80)
        print("   Principle: Laziness is the prime attribute of a successful programmer")
        print("   Rule: We hate doing anything more than twice, if we don't script it first")
        print("")
        print("Use --check <keyword> to check if memory exists")
        print("Use --test to test the prevention system")
        print("")


if __name__ == "__main__":


    main()