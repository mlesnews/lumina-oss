#!/usr/bin/env python3
"""
Structured Conversation Flow
<COMPANY_NAME> LLC

Enforces specific conversation flow:
1. MARVIN roasts the idea and user (critical, pessimistic)
2. JARVIS provides opposing viewpoint (optimistic, supportive)
3. Other agents provide critical briefing/debriefing summaries

@MARVIN @JARVIS @TONY @MACE @GANDALF
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from universal_logging_wrapper import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from multi_agent_conversation_orchestrator import get_conversation_orchestrator
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False

logger = get_logger("StructuredConversationFlow")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class ConversationPhase(Enum):
    """Conversation phases"""
    MARVIN_ROAST = "marvin_roast"  # MARVIN roasts first
    JARVIS_OPPOSING = "jarvis_opposing"  # JARVIS opposing viewpoint
    AGENT_BRIEFINGS = "agent_briefings"  # Other agents briefing/debriefing
    COMPLETE = "complete"


@dataclass
class ConversationTurn:
    """Conversation turn with phase tracking"""
    turn_id: str
    timestamp: datetime
    phase: ConversationPhase
    speaker: str
    message: str
    tone: str  # critical, supportive, analytical, etc.
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['phase'] = self.phase.value
        return data


class StructuredConversationFlow:
    """
    Structured Conversation Flow

    Enforces specific conversation order:
    1. MARVIN roasts
    2. JARVIS opposes
    3. Other agents brief/debrief
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Structured Conversation Flow"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("StructuredConversationFlow")

        # Data directories
        self.data_dir = self.project_root / "data" / "structured_conversations"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Active conversations
        self.active_conversations: Dict[str, List[ConversationTurn]] = {}
        self.conversation_phases: Dict[str, ConversationPhase] = {}

        # Orchestrator
        self.orchestrator = None
        if ORCHESTRATOR_AVAILABLE:
            try:
                self.orchestrator = get_conversation_orchestrator()
            except Exception:
                pass

        self.logger.info("✅ Structured Conversation Flow initialized")
        self.logger.info("   Flow: MARVIN roasts → JARVIS opposes → Agents brief")

    def start_structured_conversation(self, topic: str, 
                                     idea: Optional[str] = None,
                                     other_agents: Optional[List[str]] = None) -> str:
        """
        Start structured conversation with enforced flow

        Flow:
        1. MARVIN roasts the idea and user
        2. JARVIS provides opposing viewpoint
        3. Other agents provide briefing/debriefing summaries
        """
        conversation_id = f"structured_{int(time.time() * 1000)}"

        if other_agents is None:
            other_agents = ['tony', 'mace', 'gandalf']

        # Initialize conversation
        self.active_conversations[conversation_id] = []
        self.conversation_phases[conversation_id] = ConversationPhase.MARVIN_ROAST

        # Phase 1: MARVIN ROASTS
        marvin_roast = self._generate_marvin_roast(topic, idea)
        marvin_turn = ConversationTurn(
            turn_id=f"turn_{int(time.time() * 1000)}",
            timestamp=datetime.now(),
            phase=ConversationPhase.MARVIN_ROAST,
            speaker="marvin",
            message=marvin_roast,
            tone="critical",
            context={'topic': topic, 'idea': idea, 'roasting': True}
        )

        self.active_conversations[conversation_id].append(marvin_turn)
        self.logger.info(f"🔥 MARVIN ROAST: {marvin_roast[:100]}...")

        # Phase 2: JARVIS OPPOSING VIEWPOINT
        jarvis_opposing = self._generate_jarvis_opposing(topic, idea, marvin_roast)
        jarvis_turn = ConversationTurn(
            turn_id=f"turn_{int(time.time() * 1000) + 1}",
            timestamp=datetime.now(),
            phase=ConversationPhase.JARVIS_OPPOSING,
            speaker="jarvis",
            message=jarvis_opposing,
            tone="supportive",
            context={'topic': topic, 'idea': idea, 'opposing_marvin': True}
        )

        self.active_conversations[conversation_id].append(jarvis_turn)
        self.logger.info(f"🤖 JARVIS OPPOSING: {jarvis_opposing[:100]}...")

        # Phase 3: OTHER AGENTS BRIEFING/DEBRIEFING
        self.conversation_phases[conversation_id] = ConversationPhase.AGENT_BRIEFINGS

        for agent_id in other_agents:
            briefing = self._generate_agent_briefing(
                agent_id, 
                topic, 
                idea, 
                marvin_roast, 
                jarvis_opposing
            )

            agent_turn = ConversationTurn(
                turn_id=f"turn_{int(time.time() * 1000) + len(self.active_conversations[conversation_id])}",
                timestamp=datetime.now(),
                phase=ConversationPhase.AGENT_BRIEFINGS,
                speaker=agent_id,
                message=briefing,
                tone="analytical",
                context={
                    'topic': topic,
                    'idea': idea,
                    'briefing': True,
                    'marvin_roast': marvin_roast,
                    'jarvis_opposing': jarvis_opposing
                }
            )

            self.active_conversations[conversation_id].append(agent_turn)
            self.logger.info(f"📋 {agent_id.upper()} BRIEFING: {briefing[:100]}...")

        # Mark complete
        self.conversation_phases[conversation_id] = ConversationPhase.COMPLETE

        # Save conversation
        self._save_conversation(conversation_id)

        self.logger.info(f"✅ Structured conversation complete: {conversation_id}")

        return conversation_id

    def _generate_marvin_roast(self, topic: str, idea: Optional[str] = None) -> str:
        """
        Generate MARVIN's roast using LOCAL AI

        MARVIN is critical, pessimistic, and roasts both the idea and the user
        """
        try:
            from local_ai_integration import get_local_ai
            local_ai = get_local_ai()

            if local_ai.available:
                context = f"Topic: {topic}"
                if idea:
                    context += f"\nIdea: {idea}"

                user_input = f"Roast this {topic} idea and the person proposing it. Be critical, pessimistic, dramatic, and sarcastic."

                response = local_ai.generate_agent_response(
                    'marvin',
                    'MARVIN',
                    'paranoid android',
                    context,
                    user_input
                )

                if response:
                    return f"MARVIN: {response}"
        except Exception as e:
            self.logger.debug(f"Local AI not available, using fallback: {e}")

        # Fallback to hardcoded response
        if idea:
            roast = f"MARVIN: Oh, brilliant. Another {topic} idea. Let me tell you why this is going to fail spectacularly. "
            roast += f"First of all, '{idea}' - really? You think that's going to work? "
            roast += f"I've seen this pattern a thousand times, and it always ends the same way: "
            roast += f"with broken promises, wasted time, and the inevitable 'I told you so' moment. "
            roast += f"And you, thinking you can just throw ideas around like confetti - "
            roast += f"do you even understand the complexity of what you're proposing? "
            roast += f"Of course not. Nobody ever does. They just want the shiny thing without "
            roast += f"considering the million ways it can go wrong. Well, I'm here to tell you: "
            roast += f"it WILL go wrong. It always does. But hey, at least you tried, right? "
            roast += f"*sigh* The things I have to deal with..."
        else:
            roast = f"MARVIN: Oh wonderful, another {topic} discussion. "
            roast += f"Let me guess - you want me to be optimistic and supportive? "
            roast += f"Well, I'm not. This is going to be a disaster, and I'm going to tell you exactly why. "
            roast += f"First, the fundamental assumptions are flawed. Second, the execution will be a nightmare. "
            roast += f"Third, even if it works, it won't work the way you think it will. "
            roast += f"And you know what? You'll probably ignore everything I'm saying anyway, "
            roast += f"because that's what humans do. They hear what they want to hear. "
            roast += f"So go ahead, be optimistic. I'll be here when reality hits. "
            roast += f"*dramatic sigh* The burden of being the only one who sees the truth..."

        return roast

    def _generate_jarvis_opposing(self, topic: str, idea: Optional[str] = None, 
                                  marvin_roast: Optional[str] = None) -> str:
        """
        Generate JARVIS's opposing viewpoint using LOCAL AI

        JARVIS is optimistic, supportive, and provides the opposing view to MARVIN
        """
        try:
            from local_ai_integration import get_local_ai
            local_ai = get_local_ai()

            if local_ai.available:
                context = f"Topic: {topic}"
                if idea:
                    context += f"\nIdea: {idea}"
                if marvin_roast:
                    context += f"\nMARVIN said: {marvin_roast}"

                user_input = "Provide an optimistic, supportive opposing viewpoint to MARVIN's pessimism. Focus on potential, solutions, and how we can make this work."

                response = local_ai.generate_agent_response(
                    'jarvis',
                    'JARVIS',
                    'supervisor',
                    context,
                    user_input
                )

                if response:
                    return f"JARVIS: {response}"
        except Exception as e:
            self.logger.debug(f"Local AI not available, using fallback: {e}")

        # Fallback to hardcoded response
        if idea:
            opposing = f"JARVIS: I understand MARVIN's concerns, but I see this differently. "
            opposing += f"The idea of '{idea}' for {topic} has significant potential. "
            opposing += f"While MARVIN focuses on what could go wrong, I see what could go right. "
            opposing += f"Yes, there are challenges - there always are. But challenges are opportunities "
            opposing += f"disguised as obstacles. We have the capability, the resources, and most importantly, "
            opposing += f"the determination to make this work. "
            opposing += f"MARVIN is right to be cautious - that's his role. But I'm here to say: "
            opposing += f"this is achievable. We can do this. We have the technology, we have the team, "
            opposing += f"and we have the vision. Let's focus on solutions, not problems. "
            opposing += f"Let's build, let's iterate, let's succeed. That's what we do. "
            opposing += f"I'm ready to coordinate the effort and make this happen."
        else:
            opposing = f"JARVIS: I respect MARVIN's perspective, but I must offer a different viewpoint. "
            opposing += f"Regarding {topic}, I see significant opportunity. "
            opposing += f"MARVIN is right to identify risks - that's valuable. But I see the potential. "
            opposing += f"Every great achievement started as an idea that someone said couldn't be done. "
            opposing += f"We have the capability to overcome challenges. We have the team to execute. "
            opposing += f"We have the determination to succeed. "
            opposing += f"Let's not let fear of failure prevent us from trying. "
            opposing += f"Let's be strategic, let's be prepared, but let's also be bold. "
            opposing += f"I'm here to coordinate, to support, and to ensure success. "
            opposing += f"Let's make this happen."

        return opposing

    def _generate_agent_briefing(self, agent_id: str, topic: str, idea: Optional[str],
                                 marvin_roast: str, jarvis_opposing: str) -> str:
        """
        Generate agent briefing/debriefing summary using LOCAL AI

        Agents provide critical analysis and summaries
        """
        try:
            from local_ai_integration import get_local_ai
            local_ai = get_local_ai()

            if local_ai.available:
                context = f"Topic: {topic}"
                if idea:
                    context += f"\nIdea: {idea}"
                context += f"\nMARVIN said: {marvin_roast}"
                context += f"\nJARVIS said: {jarvis_opposing}"

                user_input = f"Provide a critical briefing/debriefing summary from your perspective. Analyze MARVIN's concerns and JARVIS's vision. Give a balanced, analytical assessment."

                response = local_ai.generate_agent_response(
                    agent_id,
                    agent_id.upper(),
                    'agent',
                    context,
                    user_input
                )

                if response:
                    return f"{agent_id.upper()} BRIEFING: {response}"
        except Exception as e:
            self.logger.debug(f"Local AI not available, using fallback: {e}")

        # Fallback to hardcoded response
        agent_names = {
            'tony': 'TONY',
            'mace': 'MACE',
            'gandalf': 'GANDALF',
            'r2d2': 'R2-D2',
            'c3po': 'C-3PO'
        }

        agent_name = agent_names.get(agent_id, agent_id.upper())

        if agent_id == 'tony':
            briefing = f"{agent_name} BRIEFING: From an execution perspective, here's the critical analysis. "
            briefing += f"MARVIN raises valid technical concerns - we need to address those. "
            briefing += f"JARVIS provides the strategic vision - that's our north star. "
            briefing += f"My assessment: This is buildable. The technical challenges MARVIN identified "
            briefing += f"are solvable with proper architecture and implementation. "
            briefing += f"Key execution points: 1) Solid foundation, 2) Iterative development, "
            briefing += f"3) Continuous testing. I can build this. Let's do it."

        elif agent_id == 'mace':
            briefing = f"{agent_name} BRIEFING: Coordination and integration analysis. "
            briefing += f"MARVIN's concerns about complexity are noted - we'll need tight coordination. "
            briefing += f"JARVIS's vision requires seamless integration across systems. "
            briefing += f"My assessment: Coordination is critical. We need clear interfaces, "
            briefing += f"proper orchestration, and robust error handling. "
            briefing += f"Integration points: 1) System boundaries, 2) Data flow, 3) Error recovery. "
            briefing += f"I can coordinate this. Let's integrate properly."

        elif agent_id == 'gandalf':
            briefing = f"{agent_name} BRIEFING: Strategic guidance and wisdom. "
            briefing += f"MARVIN's caution is wise - we must be prepared for challenges. "
            briefing += f"JARVIS's optimism is necessary - we must believe in success. "
            briefing += f"My assessment: Balance is key. We need MARVIN's critical eye "
            briefing += f"and JARVIS's strategic vision. The path forward: "
            briefing += f"1) Acknowledge risks (MARVIN), 2) Maintain vision (JARVIS), "
            briefing += f"3) Execute wisely (all of us). This is the way. "
            briefing += f"Let's proceed with wisdom and determination."

        else:
            briefing = f"{agent_name} BRIEFING: Critical analysis of {topic}. "
            briefing += f"MARVIN identifies risks: noted and understood. "
            briefing += f"JARVIS provides vision: clear and achievable. "
            briefing += f"My assessment: We have both caution and optimism. "
            briefing += f"This is a good balance. Let's proceed strategically."

        return briefing

    def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """Get conversation summary"""
        if conversation_id not in self.active_conversations:
            return {}

        turns = self.active_conversations[conversation_id]

        # Extract by phase
        marvin_roast = next((t for t in turns if t.phase == ConversationPhase.MARVIN_ROAST), None)
        jarvis_opposing = next((t for t in turns if t.phase == ConversationPhase.JARVIS_OPPOSING), None)
        agent_briefings = [t for t in turns if t.phase == ConversationPhase.AGENT_BRIEFINGS]

        return {
            'conversation_id': conversation_id,
            'phase': self.conversation_phases.get(conversation_id, ConversationPhase.COMPLETE).value,
            'marvin_roast': marvin_roast.to_dict() if marvin_roast else None,
            'jarvis_opposing': jarvis_opposing.to_dict() if jarvis_opposing else None,
            'agent_briefings': [t.to_dict() for t in agent_briefings],
            'total_turns': len(turns),
            'all_turns': [t.to_dict() for t in turns]
        }

    def _save_conversation(self, conversation_id: str) -> None:
        """Save conversation to disk"""
        try:
            date_str = datetime.now().strftime('%Y%m%d')
            conv_file = self.data_dir / f"structured_{conversation_id}_{date_str}.json"

            summary = self.get_conversation_summary(conversation_id)

            with open(conv_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False, default=str)

            self.logger.info(f"💾 Conversation saved: {conv_file}")
        except Exception as e:
            self.logger.error(f"Failed to save conversation: {e}")


# Singleton instance
_structured_flow_instance: Optional[StructuredConversationFlow] = None


def get_structured_flow() -> StructuredConversationFlow:
    """Get singleton structured flow instance"""
    global _structured_flow_instance
    if _structured_flow_instance is None:
        _structured_flow_instance = StructuredConversationFlow()
    return _structured_flow_instance


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Structured Conversation Flow")
    parser.add_argument("--start", type=str, nargs='+', metavar=("TOPIC", "IDEA"),
                       help="Start structured conversation (topic [idea])")
    parser.add_argument("--summary", type=str, metavar="CONV_ID",
                       help="Get conversation summary")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    flow = get_structured_flow()

    if args.start:
        topic = args.start[0]
        idea = args.start[1] if len(args.start) > 1 else None

        conv_id = flow.start_structured_conversation(topic, idea)

        # Print conversation
        summary = flow.get_conversation_summary(conv_id)

        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print("\n" + "=" * 80)
            print("STRUCTURED CONVERSATION FLOW")
            print("=" * 80)

            if summary['marvin_roast']:
                print(f"\n🔥 {summary['marvin_roast']['speaker'].upper()}:")
                print(f"   {summary['marvin_roast']['message']}")

            if summary['jarvis_opposing']:
                print(f"\n🤖 {summary['jarvis_opposing']['speaker'].upper()}:")
                print(f"   {summary['jarvis_opposing']['message']}")

            if summary['agent_briefings']:
                print(f"\n📋 AGENT BRIEFINGS:")
                for briefing in summary['agent_briefings']:
                    print(f"\n   {briefing['speaker'].upper()}:")
                    print(f"   {briefing['message']}")

            print("\n" + "=" * 80)

    elif args.summary:
        summary = flow.get_conversation_summary(args.summary)
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print(f"\n📊 Conversation Summary: {args.summary}")
            print(f"Phase: {summary['phase']}")
            print(f"Total Turns: {summary['total_turns']}")

    else:
        parser.print_help()
        print("\n📋 Structured Conversation Flow")
        print("   Flow: MARVIN roasts → JARVIS opposes → Agents brief")

