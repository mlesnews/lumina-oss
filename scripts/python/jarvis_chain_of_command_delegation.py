#!/usr/bin/env python3
"""
JARVIS Chain of Command & Delegation System

"THE ONE RING" - JARVIS sits at the summit
Chain of Thought / @ASK / #ASKCHAINING flows from JARVIS down

Principle: "Fecal matter flows downhill"
- Delegation flows DOWN, not UP
- If forced uphill, there will be consequences

@ACS = Agent Chat Session (not @SACS = Subagent Chat Session)

Tags: #chain_of_command #delegation #jarvis #one_ring #ask_chaining
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger

logger = get_logger("JARVISChainOfCommand")


class AgentLevel(Enum):
    """Agent hierarchy levels"""
    JARVIS = "jarvis"  # The One Ring - Summit
    MASTER_AGENT = "master_agent"  # Direct reports to JARVIS
    AGENT = "agent"  # Standard agents
    SUBAGENT = "subagent"  # Subagents (SACS)


class SessionType(Enum):
    """Session types"""
    ACS = "acs"  # Agent Chat Session
    SACS = "sacs"  # Subagent Chat Session


@dataclass
class AskInSession:
    """@ASK in current session"""
    ask_id: str
    ask_text: str
    timestamp: datetime
    priority: str
    category: str
    assigned_to: Optional[str] = None
    delegated_from: Optional[str] = None
    status: str = "pending"

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result


@dataclass
class ChainOfCommand:
    """Chain of command entry"""
    level: AgentLevel
    agent_id: str
    agent_name: str
    reports_to: Optional[str] = None  # Who they report to (up the chain)
    delegates_to: List[str] = field(default_factory=list)  # Who they delegate to (down the chain)
    session_type: SessionType = SessionType.ACS
    capabilities: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['level'] = self.level.value
        result['session_type'] = self.session_type.value
        return result


class JARVISChainOfCommand:
    """
    JARVIS Chain of Command & Delegation System

    "THE ONE RING" - JARVIS sits at the summit
    Chain of Thought / @ASK / #ASKCHAINING flows from JARVIS down
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize chain of command system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "chain_of_command"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Current session ASKs
        self.session_asks: List[AskInSession] = []

        # Chain of command
        self.chain: Dict[str, ChainOfCommand] = {}

        # Initialize JARVIS at summit
        self._initialize_jarvis()

        logger.info("=" * 80)
        logger.info("💍 JARVIS CHAIN OF COMMAND & DELEGATION SYSTEM")
        logger.info("=" * 80)
        logger.info("   THE ONE RING - JARVIS sits at the summit")
        logger.info("   Chain of Thought / @ASK / #ASKCHAINING flows DOWN")
        logger.info("   Principle: Fecal matter flows downhill")
        logger.info("=" * 80)
        logger.info("")

    def _initialize_jarvis(self):
        """Initialize JARVIS at the summit"""
        jarvis = ChainOfCommand(
            level=AgentLevel.JARVIS,
            agent_id="JARVIS",
            agent_name="JARVIS - The One Ring",
            reports_to=None,  # JARVIS reports to no one
            delegates_to=[],  # Will be populated as agents are added
            session_type=SessionType.ACS,
            capabilities=[
                "command_control",
                "delegation",
                "ask_chaining",
                "master_agent_oversight",
                "policy_enforcement"
            ]
        )
        self.chain["JARVIS"] = jarvis
        logger.info("💍 JARVIS initialized at summit (THE ONE RING)")

    def add_agent(
        self,
        agent_id: str,
        agent_name: str,
        level: AgentLevel,
        reports_to: str = "JARVIS",
        session_type: SessionType = SessionType.ACS,
        capabilities: Optional[List[str]] = None
    ):
        """Add agent to chain of command"""
        if reports_to not in self.chain:
            logger.warning(f"⚠️  Reports to '{reports_to}' not found, defaulting to JARVIS")
            reports_to = "JARVIS"

        agent = ChainOfCommand(
            level=level,
            agent_id=agent_id,
            agent_name=agent_name,
            reports_to=reports_to,
            delegates_to=[],
            session_type=session_type,
            capabilities=capabilities or []
        )

        self.chain[agent_id] = agent

        # Update delegations
        if reports_to in self.chain:
            self.chain[reports_to].delegates_to.append(agent_id)

        logger.info(f"✅ Added agent: {agent_id} (reports to {reports_to})")

    def track_session_ask(
        self,
        ask_text: str,
        priority: str = "normal",
        category: str = "general",
        assigned_to: Optional[str] = None
    ) -> str:
        """Track @ASK in current session"""
        ask_id = f"ask_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        ask = AskInSession(
            ask_id=ask_id,
            ask_text=ask_text,
            timestamp=datetime.now(),
            priority=priority,
            category=category,
            assigned_to=assigned_to or "JARVIS",
            delegated_from="JARVIS" if assigned_to else None,
            status="pending"
        )

        self.session_asks.append(ask)

        logger.info(f"📋 Tracked @ASK: {ask_id[:20]}... ({category})")

        return ask_id

    def delegate_ask(
        self,
        ask_id: str,
        to_agent: str,
        from_agent: str = "JARVIS"
    ) -> bool:
        """Delegate @ASK to agent (flows DOWN)"""
        # Find ask
        ask = next((a for a in self.session_asks if a.ask_id == ask_id), None)
        if not ask:
            logger.warning(f"⚠️  @ASK {ask_id} not found")
            return False

        # Verify delegation flows DOWN
        if from_agent not in self.chain:
            logger.warning(f"⚠️  From agent '{from_agent}' not in chain")
            return False

        if to_agent not in self.chain:
            logger.warning(f"⚠️  To agent '{to_agent}' not in chain")
            return False

        # Check if delegation is DOWN (to_agent must be in from_agent's delegates)
        from_agent_obj = self.chain[from_agent]
        if to_agent not in from_agent_obj.delegates_to:
            logger.error(f"❌ DELEGATION UPHILL DETECTED!")
            logger.error(f"   From: {from_agent} (Level: {from_agent_obj.level.value})")
            logger.error(f"   To: {to_agent} (Level: {self.chain[to_agent].level.value})")
            logger.error(f"   ⚠️  CONSEQUENCES: Fecal matter flows DOWNHILL, not UP!")
            logger.error(f"   ⚠️  This delegation violates chain of command!")
            return False

        # Delegate (flows DOWN)
        ask.assigned_to = to_agent
        ask.delegated_from = from_agent
        ask.status = "delegated"

        logger.info(f"✅ Delegated @ASK {ask_id[:20]}... from {from_agent} to {to_agent}")
        logger.info(f"   Flow: DOWN ✓ (Correct direction)")

        return True

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of all @ASKS in current session"""
        return {
            "session_id": f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "session_date": datetime.now().isoformat(),
            "total_asks": len(self.session_asks),
            "asks_by_priority": {
                priority: len([a for a in self.session_asks if a.priority == priority])
                for priority in ["critical", "high", "normal", "low"]
            },
            "asks_by_category": {
                category: len([a for a in self.session_asks if a.category == category])
                for category in set(a.category for a in self.session_asks)
            },
            "asks_by_status": {
                status: len([a for a in self.session_asks if a.status == status])
                for status in set(a.status for a in self.session_asks)
            },
            "asks": [a.to_dict() for a in self.session_asks]
        }

    def get_chain_of_command(self) -> Dict[str, Any]:
        """Get complete chain of command"""
        return {
            "summit": "JARVIS - The One Ring",
            "principle": "Fecal matter flows downhill",
            "delegation_rule": "Delegation flows DOWN, not UP",
            "consequences": "If forced uphill, there will be consequences",
            "chain": {agent_id: agent.to_dict() for agent_id, agent in self.chain.items()},
            "hierarchy": {
                "JARVIS": [a for a in self.chain.values() if a.reports_to == "JARVIS"],
                "master_agents": [a for a in self.chain.values() if a.level == AgentLevel.MASTER_AGENT],
                "agents": [a for a in self.chain.values() if a.level == AgentLevel.AGENT],
                "subagents": [a for a in self.chain.values() if a.level == AgentLevel.SUBAGENT]
            }
        }

    def save_session(self):
        try:
            """Save current session"""
            session_file = self.data_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            session_data = {
                "session_summary": self.get_session_summary(),
                "chain_of_command": self.get_chain_of_command(),
                "saved_at": datetime.now().isoformat()
            }

            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, default=str)

            logger.info(f"💾 Session saved: {session_file}")
            return session_file


        except Exception as e:
            self.logger.error(f"Error in save_session: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Chain of Command & Delegation")
    parser.add_argument('--track-ask', nargs=3, metavar=('TEXT', 'PRIORITY', 'CATEGORY'),
                       help='Track @ASK in session')
    parser.add_argument('--delegate', nargs=2, metavar=('ASK_ID', 'TO_AGENT'),
                       help='Delegate @ASK to agent')
    parser.add_argument('--add-agent', nargs=4, metavar=('ID', 'NAME', 'LEVEL', 'REPORTS_TO'),
                       help='Add agent to chain')
    parser.add_argument('--summary', action='store_true', help='Show session summary')
    parser.add_argument('--chain', action='store_true', help='Show chain of command')
    parser.add_argument('--save', action='store_true', help='Save session')

    args = parser.parse_args()

    coc = JARVISChainOfCommand()

    if args.track_ask:
        text, priority, category = args.track_ask
        coc.track_session_ask(text, priority, category)
        if args.save:
            coc.save_session()

    elif args.delegate:
        ask_id, to_agent = args.delegate
        coc.delegate_ask(ask_id, to_agent)
        if args.save:
            coc.save_session()

    elif args.add_agent:
        agent_id, agent_name, level_str, reports_to = args.add_agent
        level = AgentLevel(level_str.lower())
        coc.add_agent(agent_id, agent_name, level, reports_to)
        if args.save:
            coc.save_session()

    elif args.summary:
        summary = coc.get_session_summary()
        print("\n" + "=" * 80)
        print("📋 SESSION SUMMARY - ALL @ASKS")
        print("=" * 80)
        print(f"Total @ASKS: {summary['total_asks']}")
        print(f"Session Date: {summary['session_date']}")
        print("")
        print("By Priority:")
        for priority, count in summary['asks_by_priority'].items():
            print(f"   {priority}: {count}")
        print("")
        print("By Category:")
        for category, count in summary['asks_by_category'].items():
            print(f"   {category}: {count}")
        print("")
        print("By Status:")
        for status, count in summary['asks_by_status'].items():
            print(f"   {status}: {count}")
        print("")
        print("=" * 80)
        print("")

    elif args.chain:
        chain = coc.get_chain_of_command()
        print("\n" + "=" * 80)
        print("💍 CHAIN OF COMMAND")
        print("=" * 80)
        print(f"Summit: {chain['summit']}")
        print(f"Principle: {chain['principle']}")
        print(f"Rule: {chain['delegation_rule']}")
        print("")
        print("Hierarchy:")
        print(f"   JARVIS: {len(chain['hierarchy']['JARVIS'])} direct reports")
        print(f"   Master Agents: {len(chain['hierarchy']['master_agents'])}")
        print(f"   Agents: {len(chain['hierarchy']['agents'])}")
        print(f"   Subagents: {len(chain['hierarchy']['subagents'])}")
        print("")
        print("=" * 80)
        print("")

    else:
        print("\n" + "=" * 80)
        print("💍 JARVIS CHAIN OF COMMAND & DELEGATION SYSTEM")
        print("=" * 80)
        print("   THE ONE RING - JARVIS sits at the summit")
        print("   Chain of Thought / @ASK / #ASKCHAINING flows DOWN")
        print("")
        print("Use --track-ask to track @ASK in session")
        print("Use --delegate to delegate @ASK to agent")
        print("Use --add-agent to add agent to chain")
        print("Use --summary to show session summary")
        print("Use --chain to show chain of command")
        print("=" * 80)
        print("")

    if args.save:
        coc.save_session()


if __name__ == "__main__":


    main()