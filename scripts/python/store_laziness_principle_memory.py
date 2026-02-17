#!/usr/bin/env python3
"""
Store Memory: Laziness Principle & DRY Rule

"Laziness is the prime attribute of a successful programmer"
"We hate doing anything more than twice, if we don't script it first"

ROOT CAUSE IDENTIFIED: Persistent memory gaps causing repetitive work.

Tags: #memory #laziness #DRY #automation #efficiency #programming_philosophy
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger
from jarvis_persistent_memory import MemoryType, MemoryPriority
from prevent_memory_gap_automation import MemoryGapPrevention

logger = get_logger("StoreLazinessPrincipleMemory")

def main():
    """Store the laziness principle memory (using gap prevention)"""
    try:
        project_root = Path(__file__).parent.parent.parent
        prevention = MemoryGapPrevention(project_root)

        content = """PROGRAMMING PHILOSOPHY: LAZINESS PRINCIPLE

"Laziness is the prime attribute of a successful programmer"

This is a fundamental principle that drives efficiency and automation.

COROLLARY RULE:
"We hate doing anything more than twice, if we don't script it first"

This means:
- First time: Do it manually (learn the process)
- Second time: Do it manually (confirm the process)
- Third time: AUTOMATE IT (script it, delegate it, eliminate repetition)

ROOT CAUSE IDENTIFIED:
Persistent memory gaps cause us to:
- Store the same memories multiple times
- Repeat the same tasks repeatedly
- Forget what we've already done
- Waste time on repetitive work

SOLUTION:
- Always check if memory exists before storing
- Automate memory gap prevention
- Script repetitive tasks immediately
- Apply DRY (Don't Repeat Yourself) principle

This principle applies to:
- Memory storage (check before storing)
- Task automation (script after second time)
- Code reuse (don't duplicate logic)
- Process automation (delegate repetitive work)

The "laziness" here is not about being unproductive - it's about:
- Efficiency through automation
- Eliminating waste
- Scaling through delegation
- Smart work over hard work

This aligns with the IT/Testing mantra: "DELEGATE, DELEGATE, DELEGATE"
Automation is the ultimate form of delegation."""

        result = prevention.store_memory_safely(
        content=content,
        memory_type=MemoryType.LONG_TERM,
        priority=MemoryPriority.HIGH,
        context={
            "category": "programming_philosophy",
            "principle": "laziness",
            "rule": "dont_repeat_more_than_twice",
            "root_cause": "persistent_memory_gaps"
        },
        tags=[
            "laziness",
            "DRY",
            "automation",
            "efficiency",
            "programming_philosophy",
            "dont_repeat_yourself",
            "memory_gaps",
            "root_cause"
        ],
        source="store_laziness_principle_memory.py",
        content_keywords=["laziness", "prime", "attribute", "successful", "programmer", "hate", "twice", "script"]
    )

        logger.info("=" * 80)
        logger.info("💾 LAZINESS PRINCIPLE MEMORY")
        logger.info("=" * 80)

        if result['stored']:
            logger.info(f"✅ NEW MEMORY STORED")
            logger.info(f"   Memory ID: {result['memory_id']}")
        else:
            logger.info(f"✅ MEMORY ALREADY EXISTS")
            logger.info(f"   Existing Memory ID: {result['existing_memory'].get('memory_id')}")
            logger.info("   ✅ DRY Principle Applied - No Duplicate Stored")

        logger.info("")
        logger.info("Principle: Laziness is the prime attribute of a successful programmer")
        logger.info("Rule: We hate doing anything more than twice, if we don't script it first")
        logger.info("Root Cause: Persistent memory gaps")
        logger.info("=" * 80)
        logger.info("")
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()