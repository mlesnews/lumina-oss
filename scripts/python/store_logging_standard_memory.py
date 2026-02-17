#!/usr/bin/env python3
"""
Store Critical Memory: Always Use Standard Logging Module

This script stores a persistent, critical memory about always using
the standard logging module (lumina_logger) in all scripts.

Importance: 5/5 (CRITICAL) - This is a fundamental requirement
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger
from jarvis_persistent_memory import JARVISPersistentMemory, MemoryType, MemoryPriority

logger = get_logger("StoreLoggingStandardMemory")

def main():
    """Store the critical memory about standard logging"""
    try:
        project_root = Path(__file__).parent.parent.parent
        memory = JARVISPersistentMemory(project_root)

        content = """CRITICAL REQUIREMENT: Always use the standard logging module (lumina_logger) in all scripts.

Standard Pattern:
    from lumina_logger import get_logger
    logger = get_logger("ModuleName")

NEVER use:
    - import logging; logging.basicConfig()  # WRONG
    - logging.getLogger() directly  # WRONG
    - Any fallback logging patterns  # WRONG

The standard module (lumina_logger.py) provides:
    - Consistent formatting across all components
    - Colorized output (when available)
    - Centralized configuration
    - File logging support
    - Proper logger naming

All scripts in the .lumina project MUST use lumina_logger.get_logger().
This ensures consistent logging behavior across the entire ecosystem.

If lumina_logger is not available, the script should fail gracefully
with a clear error message, NOT fall back to basic logging."""

        memory_id = memory.store_memory(
            content=content,
            memory_type=MemoryType.LONG_TERM,
            priority=MemoryPriority.CRITICAL,
            context={
                "category": "coding_standards",
                "module": "lumina_logger",
                "importance": "5/5",
                "applies_to": "all_scripts",
                "enforcement": "mandatory"
            },
            tags=[
                "logging",
                "standard",
                "lumina_logger",
                "coding_standards",
                "critical",
                "mandatory",
                "5/5",
                "+++++"
            ],
            source="store_logging_standard_memory.py"
            )

        logger.info("=" * 80)
        logger.info("💾 CRITICAL MEMORY STORED")
        logger.info("=" * 80)
        logger.info(f"Memory ID: {memory_id}")
        logger.info("Content: Always use standard logging module (lumina_logger)")
        logger.info("Priority: CRITICAL (5/5)")
        logger.info("Type: LONG_TERM")
        logger.info("=" * 80)
        logger.info("")
        logger.info("✅ This memory will persist across all sessions")
        logger.info("✅ JARVIS will remember this critical requirement")
        logger.info("✅ All future scripts must use lumina_logger.get_logger()")
        logger.info("")
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()