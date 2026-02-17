#!/usr/bin/env python3
"""
Summarize All @ASKS in Current Session

Tracks and summarizes all @ASKS from the current AI agent chat session.
Automatically assigns to @ACS (Agent Chat Session) or @SACS (Subagent Chat Session).

@ALWAYS practice: This should be standard practice for all sessions.

Tags: #session_summary #ask_tracking #acs #sacs #always_policy
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger
from automated_agent_chat_session_assignment import AutomatedAgentAssignment

logger = get_logger("SummarizeCurrentSessionAsks")


def summarize_current_session_asks() -> Dict[str, Any]:
    """
    Summarize all @ASKS from current session

    This session's @ASKS:
    1. "THIS IS CURRENTLY OUR BEST WORKFLOW ENHANCEMENT. ALL MANTRAS WILL BECOME STATIC..."
    2. "SO PLEASE WALK THE ASK STACK ALL THE WAY BACK, THAT'S A FACT, JACK."
    3. "ARE WE DELEGATING? TO WHOM FROM JARVIS ON DOWN, THIS IS THE 'CHAIN OF COMMAND'..."
    """

    auto = AutomatedAgentAssignment()

    # Track all @ASKS from this session
    session_asks = [
        {
            "text": "THIS IS CURRENTLY OUR BEST WORKFLOW ENHANCEMENT. ALL MANTRAS WILL BECOME STATIC AT SOME STAGE DUE TO US BEING AT 100% UTILIZATION OR CAPPED OUT AT A MAXIMUM FOR A PARTICULAR SITUATION(S).",
            "priority": "high",
            "category": "workflow_philosophy"
        },
        {
            "text": "SO PLEASE WALK THE ASK STACK ALL THE WAY BACK, THAT'S A FACT, JACK.",
            "priority": "high",
            "category": "ask_stack_trace"
        },
        {
            "text": "ARE WE DELEGATING? TO WHOM FROM JARVIS ON DOWN, THIS IS THE 'CHAIN OF COMMAND', REALLY A 'CHAIN OF THOUGHT/@ASK/#ASKCHAINING', AND JARVIS SITS AT THE SUMMIT AS 'THE ONE RING.' AND YES, FECAL MATTER, LIKE WATER, FLOWS DOWNHILL. IF FORCED UPHILL, THERE WILL BE CONSEQUENCES FOR THE INDIVIDUAL'S ACTIONS. PLEASE SUMMARIZE ALL OF THE ASKS IN THIS CURRENT SESSION, AI AUTOMATION TO ASSIGN AN AGENT CHAT SESSION, '@ACS' WHICH SHOULD NOT BE CONFUSED WITH '@SACS' FOR 'SUBAGENT CHAT SESSION(S).' MAKE THIS STANDARD '@ALWAYS' PRACTICE/POLICY/RULE/LAW.",
            "priority": "critical",
            "category": "chain_of_command"
        }
    ]

    # Auto-assign all @ASKS
    assignments = []
    for ask in session_asks:
        result = auto.auto_assign_ask(
            ask["text"],
            ask["priority"],
            ask["category"]
        )
        assignments.append(result)

    # Get summary
    summary = auto.summarize_current_session()

    # Add session metadata
    summary["session_metadata"] = {
        "session_id": f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "session_date": datetime.now().isoformat(),
        "session_type": "ACS",  # Agent Chat Session
        "total_asks_tracked": len(session_asks),
        "policy": "@ALWAYS - Automatic @ASK tracking and @ACS assignment"
    }

    return summary


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Summarize Current Session @ASKS")
    parser.add_argument('--save', action='store_true', help='Save summary')
    parser.add_argument('--print', action='store_true', help='Print summary')

    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("📋 SUMMARIZING CURRENT SESSION @ASKS")
    logger.info("=" * 80)
    logger.info("   @ALWAYS practice: Automatic tracking and @ACS assignment")
    logger.info("=" * 80)
    logger.info("")

    summary = summarize_current_session_asks()

    if args.print or not args.save:
        print("\n" + "=" * 80)
        print("📋 CURRENT SESSION SUMMARY")
        print("=" * 80)
        print(f"Session ID: {summary['session_metadata']['session_id']}")
        print(f"Session Date: {summary['session_metadata']['session_date']}")
        print(f"Session Type: {summary['session_metadata']['session_type']} (@ACS)")
        print(f"Total @ASKS: {summary['session_metadata']['total_asks_tracked']}")
        print("")
        print("Assignment Statistics:")
        stats = summary['assignment_statistics']
        print(f"   Auto-Assigned: {stats['total_auto_assigned']}")
        print(f"   JARVIS Direct: {stats['jarvis_direct']}")
        print("")
        print("By Agent:")
        for agent, count in stats['assignments_by_agent'].items():
            print(f"   {agent}: {count}")
        print("")
        print("By Priority:")
        for priority, count in summary['asks_by_priority'].items():
            print(f"   {priority}: {count}")
        print("")
        print("By Category:")
        for category, count in summary['asks_by_category'].items():
            print(f"   {category}: {count}")
        print("")
        print("=" * 80)
        print("✅ SUMMARY COMPLETE")
        print("=" * 80)
        print("")

    if args.save:
        auto = AutomatedAgentAssignment()
        auto.save_session_summary()
        logger.info("💾 Session summary saved")


if __name__ == "__main__":


    main()