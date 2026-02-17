#!/usr/bin/env python3
"""
JARVIS Natural Conversation System

Creates human-like conversations where you can't tell who is AI and who is human.
Natural language generation with personality, context awareness, and conversational flow.

@JARVIS @NATURAL_CONVERSATION @HUMAN_LIKE
"""

import sys
import json
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISNaturalConversation")


class ConversationStyle(Enum):
    """Conversation styles"""
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    TECHNICAL = "technical"
    MIXED = "mixed"  # Natural mix of styles


@dataclass
class ConversationMessage:
    """A message in the conversation"""
    speaker: str  # "human" or "jarvis"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    style_hints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class JARVISNaturalConversation:
    """
    Natural Conversation System for JARVIS

    Makes AI responses indistinguishable from human responses.
    Natural language generation with personality and context awareness.
    """

    def __init__(self, project_root: Optional[Path] = None, 
                 style: ConversationStyle = ConversationStyle.MIXED):
        """Initialize natural conversation system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JARVISNaturalConversation")
        self.style = style

        # Conversation history
        self.conversation_history: List[ConversationMessage] = []

        # Response patterns (natural, human-like)
        self.response_patterns = self._load_response_patterns()

        # Personality traits
        self.personality = {
            "uses_casual_language": True,
            "uses_contractions": True,
            "shows_uncertainty": True,  # "I think", "probably", etc.
            "uses_filler_words": True,  # "well", "hmm", "actually"
            "shows_enthusiasm": True,  # "sure!", "absolutely", "yeah"
            "asks_follow_ups": True,
            "admits_limitations": True,  # "I'm not sure", "let me check"
        }

        # Data storage
        self.data_dir = self.project_root / "data" / "jarvis" / "conversations"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load Core Intelligence for context
        try:
            from jarvis_core_intelligence import JARVISCoreIntelligence
            self.core_intelligence = JARVISCoreIntelligence(self.project_root)
            self.logger.info("   ✅ Core Intelligence loaded for context")
        except Exception as e:
            self.core_intelligence = None
            self.logger.debug(f"   Core Intelligence not available: {e}")

        self.logger.info("💬 JARVIS Natural Conversation initialized")
        self.logger.info(f"   Style: {self.style.value}")
        self.logger.info("   Human-like responses: ✅ Enabled")

    def _load_response_patterns(self) -> Dict[str, List[str]]:
        """Load natural response patterns"""
        return {
            "acknowledgment": [
                "Got it.",
                "Sure thing.",
                "Alright.",
                "Okay.",
                "Right.",
                "Makes sense.",
                "I see.",
            ],
            "agreement": [
                "Yeah, exactly.",
                "That's right.",
                "Absolutely.",
                "Definitely.",
                "For sure.",
                "You bet.",
            ],
            "thinking": [
                "Hmm, let me think...",
                "Well...",
                "Actually,",
                "You know what,",
                "I think",
                "Probably",
                "Maybe",
            ],
            "uncertainty": [
                "I'm not entirely sure, but",
                "I think",
                "It seems like",
                "Probably",
                "Maybe",
                "Could be",
            ],
            "excitement": [
                "Oh, nice!",
                "Cool!",
                "That's great!",
                "Awesome!",
                "Perfect!",
            ],
            "clarification": [
                "What do you mean by",
                "Can you clarify",
                "You mean",
                "So you're saying",
                "Just to make sure",
            ],
            "transition": [
                "So,",
                "Anyway,",
                "By the way,",
                "Also,",
                "Oh, and",
                "Speaking of which,",
            ]
        }

    def _add_natural_touches(self, response: str) -> str:
        """Add natural human touches to response"""
        # Randomly add filler words at start (occasionally)
        if self.personality["uses_filler_words"] and random.random() < 0.2:
            fillers = ["Well, ", "Hmm, ", "Actually, ", "You know, "]
            if not response.startswith(tuple(fillers)):
                response = random.choice(fillers) + response.lower()

        # Add uncertainty markers (occasionally)
        if self.personality["shows_uncertainty"] and random.random() < 0.15:
            uncertainty = ["I think ", "Probably ", "Maybe ", "It seems like "]
            if not any(response.startswith(u) for u in uncertainty):
                response = random.choice(uncertainty) + response.lower()

        # Use contractions (sometimes)
        if self.personality["uses_contractions"]:
            contractions = {
                "I will": "I'll",
                "I am": "I'm",
                "it is": "it's",
                "that is": "that's",
                "you are": "you're",
                "we are": "we're",
                "cannot": "can't",
                "do not": "don't",
                "will not": "won't",
            }
            for formal, casual in contractions.items():
                if random.random() < 0.5:  # 50% chance
                    response = response.replace(formal, casual)

        return response

    def _generate_natural_response(self, user_input: str, 
                                   intent: Optional[Any] = None,
                                   context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a natural, human-like response

        This is where we transform technical/system responses into natural conversation.
        """
        # Start with a base response (could come from LLM or system)
        base_response = self._get_base_response(user_input, intent, context)

        # Make it natural and human-like
        response = self._humanize_response(base_response, user_input, intent)

        return response

    def _get_base_response(self, user_input: str, intent: Optional[Any],
                          context: Optional[Dict[str, Any]]) -> str:
        """
        Get base response from system/LLM

        This would normally call an LLM or system response generator.
        For now, we'll create placeholder logic.
        """
        # In real implementation, this would call JARVIS Master Command
        # or an LLM for actual responses

        # Placeholder - return something that needs humanization
        if intent and hasattr(intent, 'intent_type'):
            if intent.intent_type.value == "question":
                return "I can help with that. Let me check..."
            elif intent.intent_type.value == "command":
                return "Done. The command has been executed."
            elif intent.intent_type.value == "information":
                return "Here is the information you requested."

        return "I understand. How can I help?"

    def _humanize_response(self, base_response: str, user_input: str,
                          intent: Optional[Any]) -> str:
        """
        Humanize a system response to make it natural and conversational
        """
        response = base_response

        # Remove obvious AI patterns
        ai_patterns = [
            ("I understand your question", "Got it"),
            ("Command executed", "Done"),
            ("I can help with that", "Sure"),
            ("Here is the information", "Here's"),
            ("The command has been executed", "Done"),
            ("I'll check that for you", "Let me check"),
        ]

        for pattern, replacement in ai_patterns:
            if pattern.lower() in response.lower():
                response = response.replace(pattern, replacement, 1)
                break

        # Add natural touches
        response = self._add_natural_touches(response)

        # Remove excessive politeness (make it more casual)
        excessive_polite = [
            "Thank you for asking",
            "I'd be happy to",
            "Certainly, I can",
            "Please allow me to",
        ]

        for phrase in excessive_polite:
            response = response.replace(phrase, "", 1).strip()

        # Capitalize first letter
        if response:
            response = response[0].upper() + response[1:] if len(response) > 1 else response.upper()

        return response

    def chat(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Main chat interface - natural conversation

        Args:
            user_input: What the human said
            context: Additional context

        Returns:
            Natural, human-like response
        """
        # Understand intent (if Core Intelligence available)
        intent = None
        if self.core_intelligence:
            intent = self.core_intelligence.understand_intent(user_input)

        # Generate natural response
        response = self._generate_natural_response(user_input, intent, context)

        # Store in conversation history
        human_msg = ConversationMessage(
            speaker="human",
            content=user_input,
            metadata={"intent": intent.to_dict() if intent else None}
        )
        jarvis_msg = ConversationMessage(
            speaker="jarvis",
            content=response,
            metadata={"style": self.style.value}
        )

        self.conversation_history.append(human_msg)
        self.conversation_history.append(jarvis_msg)

        # Process conversation turn
        if self.core_intelligence:
            self.core_intelligence.process_conversation(user_input, response)

        return response

    def get_conversation_summary(self) -> str:
        """Get summary of current conversation"""
        if not self.conversation_history:
            return "No conversation yet."

        summary_parts = []
        for msg in self.conversation_history[-10:]:  # Last 10 messages
            speaker_label = "You" if msg.speaker == "human" else "JARVIS"
            summary_parts.append(f"{speaker_label}: {msg.content}")

        return "\n".join(summary_parts)

    def save_conversation(self, filename: Optional[str] = None):
        try:
            """Save conversation to file"""
            if not self.conversation_history:
                return

            if filename is None:
                filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            filepath = self.data_dir / filename

            conversation_data = {
                "started_at": self.conversation_history[0].timestamp.isoformat() if self.conversation_history else None,
                "ended_at": datetime.now().isoformat(),
                "style": self.style.value,
                "messages": [msg.to_dict() for msg in self.conversation_history]
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, default=str)

            self.logger.info(f"✅ Conversation saved to {filepath}")


        except Exception as e:
            self.logger.error(f"Error in save_conversation: {e}", exc_info=True)
            raise
def main():
    """Interactive chat interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Natural Conversation")
    parser.add_argument("--style", choices=["casual", "professional", "friendly", "technical", "mixed"],
                       default="mixed", help="Conversation style")
    parser.add_argument("--interactive", action="store_true", help="Start interactive chat")

    args = parser.parse_args()

    style = ConversationStyle(args.style)
    conversation = JARVISNaturalConversation(style=style)

    if args.interactive:
        print("💬 JARVIS Natural Conversation")
        print("=" * 60)
        print(f"Style: {style.value}")
        print("Type 'exit' or 'quit' to end")
        print("Type 'summary' to see conversation summary")
        print()

        try:
            while True:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("JARVIS: See you later!")
                    break

                if user_input.lower() == 'summary':
                    print("\n" + conversation.get_conversation_summary() + "\n")
                    continue

                response = conversation.chat(user_input)
                print(f"JARVIS: {response}")
                print()

        except KeyboardInterrupt:
            print("\nJARVIS: Bye!")
        finally:
            conversation.save_conversation()
    else:
        parser.print_help()


if __name__ == "__main__":


    main()