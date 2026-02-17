#!/usr/bin/env python3
"""
Verify Critical Memory: Standard Logging Module

Verifies that the critical memory about always using lumina_logger is stored
and retrievable. This ensures JARVIS remembers this 5/5 importance requirement.
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger
from jarvis_persistent_memory import JARVISPersistentMemory

logger = get_logger("VerifyLoggingStandardMemory")

def main():
    try:
        """Verify the critical memory is stored"""
        project_root = Path(__file__).parent.parent.parent
        memory = JARVISPersistentMemory(project_root)

        # Search for the logging standard memory
        results = memory.search_memories(
            query="lumina_logger standard logging",
            limit=10
        )

        logger.info("=" * 80)
        logger.info("🔍 VERIFYING CRITICAL MEMORY: Standard Logging Module")
        logger.info("=" * 80)
        logger.info("")

        if results:
            logger.info(f"✅ Found {len(results)} memory/ies about logging standard")
            logger.info("")

            for mem in results:
                logger.info(f"Memory ID: {mem.memory_id}")
                logger.info(f"Priority: {mem.priority.value}")
                logger.info(f"Type: {mem.memory_type.value}")
                logger.info(f"Tags: {', '.join(mem.tags)}")
                logger.info(f"Content preview: {mem.content[:100]}...")
                logger.info("")

                # Check if it's the critical one
                if "CRITICAL" in mem.priority.value.upper() or "5/5" in mem.content or "+++++" in mem.tags:
                    logger.info("✅ CRITICAL MEMORY CONFIRMED (5/5 importance)")
                    logger.info("")
        else:
            logger.warning("⚠️  No memories found about logging standard!")
            logger.warning("   The critical memory may not be stored correctly.")
            logger.info("")
            logger.info("   Run: python scripts/python/store_logging_standard_memory.py")
            logger.info("")

        # Also search by tags
        tag_results = memory.search_memories(
            query="",
            tags=["lumina_logger", "critical", "5/5"],
            limit=10
        )

        if tag_results:
            logger.info(f"✅ Found {len(tag_results)} memories with critical logging tags")
            logger.info("")

        logger.info("=" * 80)
        logger.info("📋 MEMORY VERIFICATION COMPLETE")
        logger.info("=" * 80)
        logger.info("")
        logger.info("CRITICAL REQUIREMENT REMINDER:")
        logger.info("  • ALWAYS use: from lumina_logger import get_logger")
        logger.info("  • NEVER use: import logging; logging.basicConfig()")
        logger.info("  • This is a 5/5 (+++++) importance requirement")
        logger.info("")

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()