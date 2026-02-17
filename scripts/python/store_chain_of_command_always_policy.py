#!/usr/bin/env python3
"""
Store @ALWAYS Policy: Chain of Command & Delegation

This is @ALWAYS practice/policy/rule/law:
- Track all @ASKS in current session
- Auto-assign to @ACS (Agent Chat Session)
- Summarize session @ASKS automatically
- Enforce chain of command (DOWN only)

Tags: #always_policy #chain_of_command #delegation #jarvis
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger
from jarvis_persistent_memory import MemoryType, MemoryPriority
from prevent_memory_gap_automation import MemoryGapPrevention

logger = get_logger("StoreChainOfCommandAlwaysPolicy")

def main():
    try:
        """Store @ALWAYS policy for chain of command"""
        project_root = Path(__file__).parent.parent.parent
        prevention = MemoryGapPrevention(project_root)

        content = """@ALWAYS POLICY: CHAIN OF COMMAND & DELEGATION

JARVIS sits at the summit as "THE ONE RING"
Chain of Thought / @ASK / #ASKCHAINING flows from JARVIS DOWN

PRINCIPLE: "Fecal matter flows downhill"
- Delegation flows DOWN, not UP
- If forced uphill, there will be CONSEQUENCES for the individual's actions

SESSION TYPES:
- @ACS = Agent Chat Session (NOT @SACS)
- @SACS = Subagent Chat Session

@ALWAYS PRACTICE/POLICY/RULE/LAW:

1. TRACK ALL @ASKS IN CURRENT SESSION
   - Every @ASK must be tracked
   - Include priority, category, timestamp
   - No exceptions

2. AUTO-ASSIGN TO @ACS
   - Automatically assign @ASKS to appropriate Agent Chat Session
   - Use agent capabilities to determine best assignment
   - JARVIS handles directly if no suitable agent found

3. SUMMARIZE SESSION @ASKS
   - Automatically summarize all @ASKS in current session
   - Include assignment statistics
   - Include breakdown by priority, category, status
   - Save summary for record-keeping

4. ENFORCE CHAIN OF COMMAND
   - Delegation flows DOWN only (JARVIS → Master Agents → Agents → Subagents)
   - Uphill delegation is REJECTED
   - System detects and logs violations
   - Consequences for violations

5. AI AUTOMATION FOR @ACS ASSIGNMENT
   - System automatically assigns @ASKS to @ACS
   - Do NOT confuse @ACS with @SACS
   - This is STANDARD @ALWAYS practice

HIERARCHY:
JARVIS (THE ONE RING - Summit)
  ↓
Master Agents (Direct Reports)
  ↓
Agents (@ACS - Agent Chat Sessions)
  ↓
Subagents (@SACS - Subagent Chat Sessions)

DELEGATION RULES:
- DOWN: ✓ Allowed (JARVIS → Agents)
- UP: ❌ REJECTED (Agents → JARVIS)
- Violations logged and flagged

This is @ALWAYS practice - no exceptions. All sessions must follow this policy."""

        result = prevention.store_memory_safely(
            content=content,
            memory_type=MemoryType.LONG_TERM,
            priority=MemoryPriority.CRITICAL,
            context={
                "category": "policy",
                "type": "always_policy",
                "policy_name": "chain_of_command_delegation",
                "enforcement": "mandatory",
                "scope": "all_sessions"
            },
            tags=[
                "always_policy",
                "chain_of_command",
                "delegation",
                "jarvis",
                "one_ring",
                "acs",
                "sacs",
                "ask_tracking",
                "session_summary",
                "mandatory",
                "critical",
                "+++++"
            ],
            source="store_chain_of_command_always_policy.py",
            content_keywords=["chain_of_command", "delegation", "jarvis_one_ring", "acs_assignment", "session_tracking", "fecal_matter_downhill"]
        )

        logger.info("=" * 80)
        logger.info("💾 @ALWAYS POLICY: CHAIN OF COMMAND & DELEGATION")
        logger.info("=" * 80)

        if result['stored']:
            logger.info(f"✅ NEW POLICY STORED")
            logger.info(f"   Memory ID: {result['memory_id']}")
        else:
            logger.info(f"✅ POLICY ALREADY EXISTS")
            logger.info(f"   Existing Memory ID: {result['existing_memory'].get('memory_id')}")
            logger.info("   ✅ DRY Principle Applied - No Duplicate Stored")

        logger.info("")
        logger.info("Policy: @ALWAYS track, assign, and summarize @ASKS")
        logger.info("Principle: Fecal matter flows downhill (delegation DOWN only)")
        logger.info("JARVIS: THE ONE RING at summit")
        logger.info("=" * 80)
        logger.info("")
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise


if __name__ == "__main__":


    main()