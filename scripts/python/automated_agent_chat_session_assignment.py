#!/usr/bin/env python3
"""
Automated Agent Chat Session Assignment System

@ACS = Agent Chat Session (not @SACS = Subagent Chat Session)

@ALWAYS practice/policy/rule/law:
- Automatically assign @ASKS to appropriate agent chat sessions
- Track all @ASKS in current session
- Summarize session @ASKS automatically

Tags: #automation #acs #sacs #agent_assignment #always_policy
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger
from jarvis_chain_of_command_delegation import JARVISChainOfCommand, AgentLevel, SessionType

logger = get_logger("AutomatedAgentChatSessionAssignment")


class AutomatedAgentAssignment:
    """
    Automated Agent Chat Session Assignment

    @ALWAYS practice: Automatically assign @ASKS to appropriate @ACS
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize automated assignment system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "agent_sessions"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.coc = JARVISChainOfCommand(project_root)

        # Agent capability mapping
        self.agent_capabilities = self._initialize_agent_capabilities()

        logger.info("=" * 80)
        logger.info("🤖 AUTOMATED AGENT CHAT SESSION ASSIGNMENT")
        logger.info("=" * 80)
        logger.info("   @ACS = Agent Chat Session")
        logger.info("   @SACS = Subagent Chat Session")
        logger.info("   @ALWAYS: Automatic assignment policy")
        logger.info("=" * 80)
        logger.info("")

    def _initialize_agent_capabilities(self) -> Dict[str, List[str]]:
        """Initialize agent capability mapping"""
        return {
            "JARVIS": ["all", "command_control", "delegation"],
            "development_agent": ["development", "coding", "scripts", "fixes"],
            "testing_agent": ["testing", "qa", "validation"],
            "documentation_agent": ["documentation", "docs", "markdown"],
            "system_agent": ["system", "infrastructure", "deployment"],
            "ai_agent": ["ai", "llm", "intelligence", "analytics"]
        }

    def auto_assign_ask(
        self,
        ask_text: str,
        priority: str = "normal",
        category: str = "general"
    ) -> Dict[str, Any]:
        """Automatically assign @ASK to appropriate @ACS"""
        # Track ask
        ask_id = self.coc.track_session_ask(ask_text, priority, category)

        # Determine best agent based on category and capabilities
        assigned_agent = self._determine_best_agent(category, ask_text)

        # Assign
        if assigned_agent and assigned_agent != "JARVIS":
            self.coc.delegate_ask(ask_id, assigned_agent, "JARVIS")

        result = {
            "ask_id": ask_id,
            "ask_text": ask_text,
            "assigned_to": assigned_agent or "JARVIS",
            "session_type": "ACS" if assigned_agent else "JARVIS_DIRECT",
            "priority": priority,
            "category": category,
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"🤖 Auto-assigned @ASK to {assigned_agent or 'JARVIS'}")

        return result

    def _determine_best_agent(self, category: str, ask_text: str) -> Optional[str]:
        """Determine best agent for @ASK"""
        text_lower = ask_text.lower()
        category_lower = category.lower()

        # Check agent capabilities
        for agent_id, capabilities in self.agent_capabilities.items():
            if agent_id == "JARVIS":
                continue

            for capability in capabilities:
                if capability in category_lower or capability in text_lower:
                    return agent_id

        # Default: JARVIS handles it
        return None

    def summarize_current_session(self) -> Dict[str, Any]:
        """Summarize all @ASKS in current session"""
        summary = self.coc.get_session_summary()

        # Add assignment statistics
        assignment_stats = {
            "total_auto_assigned": len([a for a in self.coc.session_asks if a.assigned_to != "JARVIS"]),
            "jarvis_direct": len([a for a in self.coc.session_asks if a.assigned_to == "JARVIS"]),
            "assignments_by_agent": {}
        }

        for ask in self.coc.session_asks:
            agent = ask.assigned_to or "JARVIS"
            if agent not in assignment_stats["assignments_by_agent"]:
                assignment_stats["assignments_by_agent"][agent] = 0
            assignment_stats["assignments_by_agent"][agent] += 1

        summary["assignment_statistics"] = assignment_stats

        return summary

    def save_session_summary(self):
        try:
            """Save session summary"""
            summary = self.summarize_current_session()

            summary_file = self.data_dir / f"session_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, default=str)

            logger.info(f"💾 Session summary saved: {summary_file}")
            return summary_file


        except Exception as e:
            self.logger.error(f"Error in save_session_summary: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Automated Agent Chat Session Assignment")
    parser.add_argument('--assign', nargs=3, metavar=('TEXT', 'PRIORITY', 'CATEGORY'),
                       help='Auto-assign @ASK to @ACS')
    parser.add_argument('--summarize', action='store_true', help='Summarize current session')
    parser.add_argument('--save', action='store_true', help='Save session summary')

    args = parser.parse_args()

    auto = AutomatedAgentAssignment()

    if args.assign:
        text, priority, category = args.assign
        result = auto.auto_assign_ask(text, priority, category)
        print("\n" + "=" * 80)
        print("🤖 AUTO-ASSIGNMENT RESULT")
        print("=" * 80)
        print(f"@ASK ID: {result['ask_id']}")
        print(f"Assigned To: {result['assigned_to']}")
        print(f"Session Type: {result['session_type']}")
        print(f"Category: {result['category']}")
        print(f"Priority: {result['priority']}")
        print("=" * 80)
        print("")

        if args.save:
            auto.save_session_summary()

    elif args.summarize:
        summary = auto.summarize_current_session()
        print("\n" + "=" * 80)
        print("📋 CURRENT SESSION SUMMARY - ALL @ASKS")
        print("=" * 80)
        print(f"Total @ASKS: {summary['total_asks']}")
        print(f"Session Date: {summary['session_date']}")
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
        print("")

        if args.save:
            auto.save_session_summary()

    else:
        print("\n" + "=" * 80)
        print("🤖 AUTOMATED AGENT CHAT SESSION ASSIGNMENT")
        print("=" * 80)
        print("   @ACS = Agent Chat Session")
        print("   @SACS = Subagent Chat Session")
        print("   @ALWAYS: Automatic assignment policy")
        print("")
        print("Use --assign to auto-assign @ASK to @ACS")
        print("Use --summarize to summarize current session")
        print("=" * 80)
        print("")

    if args.save:
        auto.save_session_summary()


if __name__ == "__main__":


    main()