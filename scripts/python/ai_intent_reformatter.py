#!/usr/bin/env python3
"""
AI Intent Reformatter - Kilo Code Style

Replicates Kilo Code extension's AI-assisted intent instant reformat into AI "SPEAK"
for user review before sending. Ensures intent matches between user and AI.

Features:
- Instant reformatting of user intent
- AI "SPEAK" format preview
- Review and confirm before sending
- Communication optimization
- Intent matching verification

Tags: #INTENT_REFORMAT #KILO_CODE #AI_SPEAK #COMMUNICATION_OPTIMIZATION @JARVIS @LUMINA
"""

import sys
import re
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from analyze_communication_patterns import CommunicationAnalyzer
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    CommunicationAnalyzer = None

logger = get_logger("AIIntentReformatter")


@dataclass
class IntentReformat:
    """Reformatted intent in AI SPEAK format"""
    original: str
    reformatted: str
    action_word: Optional[str] = None
    context: Optional[str] = None
    intent: Optional[str] = None
    confidence: float = 0.0  # 0.0-1.0
    suggestions: list = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AIIntentReformatter:
    """
    AI Intent Reformatter - Kilo Code Style

    Reformats user intent into optimized AI "SPEAK" format for review.
    """

    # Action word mappings
    ACTION_WORDS = {
        "start", "fix", "create", "update", "proceed", "implement",
        "configure", "build", "add", "remove", "change", "run",
        "stop", "restart", "delete", "modify", "improve", "optimize"
    }

    # Context indicators
    CONTEXT_INDICATORS = {
        "since", "because", "so that", "after", "when", "if", "while",
        "due to", "as a result", "in order to"
    }

    # Intent indicators
    INTENT_INDICATORS = {
        "i want", "i need", "i would like", "i'm trying to",
        "my goal is", "i'm aiming to", "the purpose is"
    }

    # Vague patterns to improve
    VAGUE_PATTERNS = [
        (r"can you maybe", "Please"),
        (r"it would be nice if", "I want"),
        (r"i was wondering if", "Please"),
        (r"could you possibly", "Please"),
        (r"do the thing", "Execute the action"),
        (r"make it work", "Fix the issue"),
        (r"the thing that", "The specific component")
    ]

    def __init__(self):
        """Initialize intent reformatter"""
        self.analyzer = CommunicationAnalyzer() if CommunicationAnalyzer else None

        logger.info("=" * 80)
        logger.info("🎯 AI INTENT REFORMATTER (Kilo Code Style)")
        logger.info("=" * 80)
        logger.info("   Ready to reformat intent into AI SPEAK")
        logger.info("=" * 80)

    def reformat_intent(self, user_input: str) -> IntentReformat:
        """
        Reformat user intent into AI SPEAK format

        Returns reformatted version for user review.
        """
        original = user_input.strip()

        # Analyze original
        analysis = self._analyze_input(original)

        # Generate reformatted version
        reformatted = self._generate_reformatted(original, analysis)

        # Extract components
        action_word = analysis.get("action_word")
        context = analysis.get("context")
        intent = analysis.get("intent")

        # Calculate confidence
        confidence = self._calculate_confidence(analysis)

        # Generate suggestions
        suggestions = self._generate_suggestions(original, analysis)

        return IntentReformat(
            original=original,
            reformatted=reformatted,
            action_word=action_word,
            context=context,
            intent=intent,
            confidence=confidence,
            suggestions=suggestions,
            metadata={
                "analysis": analysis,
                "reformatted_at": datetime.now().isoformat()
            }
        )

    def _analyze_input(self, text: str) -> Dict[str, Any]:
        """Analyze input to extract components"""
        text_lower = text.lower()

        analysis = {
            "action_word": None,
            "context": None,
            "intent": None,
            "is_direct": False,
            "is_vague": False,
            "has_action": False,
            "has_context": False,
            "has_intent": False
        }

        # Find action word
        for word in self.ACTION_WORDS:
            if text_lower.startswith(word) or f" {word} " in text_lower:
                analysis["action_word"] = word
                analysis["has_action"] = True
                if text_lower.startswith(word):
                    analysis["is_direct"] = True
                break

        # Find context
        for indicator in self.CONTEXT_INDICATORS:
            if indicator in text_lower:
                # Extract context clause
                parts = re.split(f"\\b{indicator}\\b", text, maxsplit=1, flags=re.IGNORECASE)
                if len(parts) > 1:
                    analysis["context"] = parts[1].strip()
                    analysis["has_context"] = True
                break

        # Find intent
        for indicator in self.INTENT_INDICATORS:
            if indicator in text_lower:
                # Extract intent
                intent_match = re.search(
                    f"\\b{indicator}\\b(.*?)(?:\\.|$|,|\\n)",
                    text_lower,
                    re.IGNORECASE
                )
                if intent_match:
                    analysis["intent"] = intent_match.group(1).strip()
                    analysis["has_intent"] = True
                break

        # Check for vague patterns
        for pattern, _ in self.VAGUE_PATTERNS:
            if re.search(pattern, text_lower):
                analysis["is_vague"] = True
                break

        return analysis

    def _generate_reformatted(self, original: str, analysis: Dict[str, Any]) -> str:
        """Generate reformatted AI SPEAK version"""
        reformatted = original

        # Fix vague patterns first
        for pattern, replacement in self.VAGUE_PATTERNS:
            reformatted = re.sub(pattern, replacement, reformatted, flags=re.IGNORECASE)

        # Handle question format -> command format
        if reformatted.strip().endswith("?"):
            # Remove question mark and question words
            reformatted = re.sub(r"^(can we|can you|could we|could you|would you|will you)\s+", 
                                "", reformatted, flags=re.IGNORECASE)
            reformatted = reformatted.rstrip("?")
            reformatted = reformatted.strip()

        # Remove "please" and make it a direct command
        reformatted = re.sub(r"\bplease\s+", "", reformatted, flags=re.IGNORECASE)

        # Handle "a different way" -> extract the way
        if "different way" in reformatted.lower():
            # This will be handled in _restructure_with_action
            pass

        # If no action word, try to infer and restructure
        if not analysis["has_action"]:
            inferred_action = self._infer_action(original)
            if inferred_action:
                # Smart restructuring: find the object and restructure
                reformatted = self._restructure_with_action(reformatted, inferred_action)
                analysis["action_word"] = inferred_action
                analysis["has_action"] = True
                analysis["is_direct"] = True  # Now it's direct
        elif analysis["action_word"] and not analysis["is_direct"]:
            # Restructure to start with action
            action = analysis["action_word"]
            # Use smart restructuring instead of simple prepend
            reformatted = self._restructure_with_action(reformatted, action)
            analysis["is_direct"] = True

        # Clean up formatting
        reformatted = self._clean_formatting(reformatted)

        return reformatted

    def _restructure_with_action(self, text: str, action: str) -> str:
        """Restructure text to start with action word"""
        text_lower = text.lower()

        # Infer object from context
        object_name = None
        if "service" in text_lower or "process" in text_lower or "watchdog" in text_lower:
            object_name = "the service"
        elif "va" in text_lower or "virtual assistant" in text_lower or "them" in text_lower:
            object_name = "the virtual assistants"
        elif "terminal" in text_lower:
            object_name = "the service"
        else:
            object_name = "it"

        # Extract the key details (what's different/new)
        details = []

        # Look for "different way" or specific requirements
        if "different way" in text_lower or "a different way" in text_lower:
            # Extract what makes it different
            if "headless" in text_lower:
                details.append("as headless service")
            if "watchdog" in text_lower:
                details.append("with watchdog monitoring")
            if "terminal" in text_lower:
                details.append("in headless terminal")
            if "guarded" in text_lower or "process" in text_lower:
                details.append("as guarded process")
        else:
            # Extract specific requirements directly
            if "headless" in text_lower:
                details.append("as headless service")
            if "watchdog" in text_lower:
                details.append("with watchdog monitoring")
            if "guarded" in text_lower or "process" in text_lower:
                details.append("as guarded process")
            if "terminal" in text_lower and "headless" in text_lower:
                details.append("in headless terminal")

        # Build reformatted command
        if details:
            detail_str = " ".join(details)
            result = f"{action.capitalize()} {object_name} {detail_str}"
        else:
            # Fallback: just action + object
            result = f"{action.capitalize()} {object_name}"

        # Clean up any remaining artifacts
        result = re.sub(r"\s+", " ", result).strip()

        return result

    def _infer_action(self, text: str) -> Optional[str]:
        """Infer action word from context"""
        text_lower = text.lower()

        # Common patterns
        if "start" in text_lower or "begin" in text_lower or "launch" in text_lower:
            return "start"
        if "fix" in text_lower or "repair" in text_lower or "resolve" in text_lower:
            return "fix"
        if "create" in text_lower or "make" in text_lower or "build" in text_lower:
            return "create"
        if "update" in text_lower or "modify" in text_lower or "change" in text_lower:
            return "update"
        if "improve" in text_lower or "enhance" in text_lower or "optimize" in text_lower:
            return "improve"

        return None

    def _infer_context(self, text: str) -> Optional[str]:
        """Infer context from text"""
        # Look for temporal references
        if "after" in text.lower() or "since" in text.lower():
            return "temporal context detected"
        if "because" in text.lower() or "due to" in text.lower():
            return "causal context detected"

        return None

    def _clean_formatting(self, text: str) -> str:
        """Clean up formatting"""
        # Remove extra spaces
        text = re.sub(r"\s+", " ", text)
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]
        # Ensure proper punctuation
        if text and not text[-1] in ".!?":
            text += "."

        return text.strip()

    def _calculate_confidence(self, analysis: Dict[str, Any]) -> float:
        """Calculate confidence in reformatting (0.0-1.0)"""
        confidence = 0.5  # Base confidence

        if analysis["has_action"]:
            confidence += 0.2
        if analysis["is_direct"]:
            confidence += 0.15
        if analysis["has_context"]:
            confidence += 0.1
        if analysis["has_intent"]:
            confidence += 0.05

        if analysis["is_vague"]:
            confidence -= 0.2

        return min(max(confidence, 0.0), 1.0)

    def _generate_suggestions(self, original: str, analysis: Dict[str, Any]) -> list:
        """Generate improvement suggestions"""
        suggestions = []

        if not analysis["has_action"]:
            suggestions.append("💡 Add an action word: 'Start', 'Fix', 'Create', etc.")

        if not analysis["has_context"]:
            suggestions.append("💡 Add context: 'Since X', 'Because Y', 'So that Z'")

        if analysis["is_vague"]:
            suggestions.append("⚠️  Remove vague phrases - be direct!")

        if not analysis["is_direct"]:
            suggestions.append("💡 Start with direct command for better clarity")

        if not analysis["has_intent"] and len(original.split()) > 5:
            suggestions.append("💡 Consider adding intent: 'I want to...' or 'My goal is...'")

        return suggestions

    def format_for_review(self, reformat: IntentReformat) -> str:
        """Format reformat result for user review"""
        output = []
        output.append("=" * 80)
        output.append("🎯 INTENT REFORMAT - REVIEW BEFORE SENDING")
        output.append("=" * 80)
        output.append("")
        output.append("📝 ORIGINAL:")
        output.append(f"   {reformat.original}")
        output.append("")
        output.append("✨ AI SPEAK (REFORMATTED):")
        output.append(f"   {reformat.reformatted}")
        output.append("")

        if reformat.action_word:
            output.append(f"🔧 Action: {reformat.action_word}")
        if reformat.context:
            output.append(f"📋 Context: {reformat.context}")
        if reformat.intent:
            output.append(f"🎯 Intent: {reformat.intent}")

        output.append("")
        output.append(f"📊 Confidence: {reformat.confidence:.0%}")
        output.append("")

        if reformat.suggestions:
            output.append("💡 SUGGESTIONS:")
            for suggestion in reformat.suggestions:
                output.append(f"   {suggestion}")
            output.append("")

        output.append("=" * 80)
        output.append("")
        output.append("✅ Does this match your intent?")
        output.append("   [Y]es - Send as reformatted")
        output.append("   [N]o - Keep original")
        output.append("   [E]dit - Modify reformatted version")
        output.append("")

        return "\n".join(output)


def main():
    """Main entry point - Interactive mode"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Intent Reformatter (Kilo Code Style)")
    parser.add_argument("input", nargs="?", help="User input to reformat")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    args = parser.parse_args()

    formatter = AIIntentReformatter()

    if args.interactive or not args.input:
        # Interactive mode
        print("=" * 80)
        print("🎯 AI INTENT REFORMATTER - INTERACTIVE MODE")
        print("=" * 80)
        print("Enter your intent (or 'quit' to exit):")
        print()

        while True:
            try:
                user_input = input("You: ").strip()

                if user_input.lower() in ["quit", "exit", "q"]:
                    break

                if not user_input:
                    continue

                # Reformat
                reformat = formatter.reformat_intent(user_input)

                # Show for review
                print()
                print(formatter.format_for_review(reformat))

                # Get confirmation
                choice = input("Choice [Y/N/E]: ").strip().upper()

                if choice == "Y":
                    print(f"✅ Sending: {reformat.reformatted}")
                elif choice == "N":
                    print(f"✅ Sending original: {reformat.original}")
                elif choice == "E":
                    edited = input("Edit: ").strip()
                    if edited:
                        print(f"✅ Sending edited: {edited}")
                else:
                    print("⚠️  Invalid choice, keeping original")

                print()

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
    else:
        # Single input mode
        reformat = formatter.reformat_intent(args.input)
        print(formatter.format_for_review(reformat))

    return 0


if __name__ == "__main__":


    sys.exit(main())