#!/usr/bin/env python3
"""
Analyze Communication Patterns - Track and optimize AI-human communication

Helps identify what communication patterns work best for improving context and courage.

Tags: #COMMUNICATION #OPTIMIZATION #CONTEXT #COURAGE @JARVIS @LUMINA
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from collections import Counter
from typing import List, Dict, Any

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CommAnalysis")


class CommunicationAnalyzer:
    """Analyze communication patterns for optimization"""

    # High-value action words
    ACTION_WORDS = {
        "start", "fix", "create", "update", "proceed", "implement",
        "configure", "build", "add", "remove", "change", "run"
    }

    # High-value context words
    CONTEXT_WORDS = {
        "because", "since", "so that", "instead of", "as part of",
        "after", "before", "when", "if", "while"
    }

    # Direct command patterns
    DIRECT_PATTERNS = [
        r"^(start|fix|create|update|proceed|go ahead|do it)",
        r"^(please )?(start|fix|create|update)",
        r"^(yes|yep|yeah|proceed|go ahead)"
    ]

    # Vague patterns (less effective)
    VAGUE_PATTERNS = [
        r"can you maybe",
        r"it would be nice",
        r"i was wondering",
        r"could you possibly"
    ]

    def __init__(self):
        """Initialize analyzer"""
        self.data_dir = project_root / "data" / "communication_analysis"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.patterns_file = self.data_dir / "patterns.json"
        self.load_patterns()

    def load_patterns(self):
        try:
            """Load saved patterns"""
            if self.patterns_file.exists():
                with open(self.patterns_file, 'r') as f:
                    self.patterns = json.load(f)
            else:
                self.patterns = {
                    "total_inputs": 0,
                    "action_words_used": Counter(),
                    "context_words_used": Counter(),
                    "direct_commands": 0,
                    "vague_requests": 0,
                    "successful_patterns": [],
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            self.logger.error(f"Error in load_patterns: {e}", exc_info=True)
            raise
    def save_patterns(self):
        try:
            """Save patterns"""
            self.patterns["timestamp"] = datetime.now().isoformat()
            # Convert Counter to dict for JSON
            patterns_dict = {
                **self.patterns,
                "action_words_used": dict(self.patterns["action_words_used"]),
                "context_words_used": dict(self.patterns["context_words_used"])
            }
            with open(self.patterns_file, 'w') as f:
                json.dump(patterns_dict, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in save_patterns: {e}", exc_info=True)
            raise
    def analyze_input(self, text: str) -> Dict[str, Any]:
        """Analyze a single input"""
        text_lower = text.lower()

        analysis = {
            "text": text,
            "length": len(text),
            "word_count": len(text.split()),
            "has_action_word": False,
            "has_context_word": False,
            "is_direct_command": False,
            "is_vague": False,
            "action_words_found": [],
            "context_words_found": [],
            "score": 0
        }

        # Check for action words
        for word in self.ACTION_WORDS:
            if word in text_lower:
                analysis["has_action_word"] = True
                analysis["action_words_found"].append(word)
                analysis["score"] += 2

        # Check for context words
        for word in self.CONTEXT_WORDS:
            if word in text_lower:
                analysis["has_context_word"] = True
                analysis["context_words_found"].append(word)
                analysis["score"] += 1

        # Check for direct command patterns
        for pattern in self.DIRECT_PATTERNS:
            if re.search(pattern, text_lower):
                analysis["is_direct_command"] = True
                analysis["score"] += 3
                break

        # Check for vague patterns
        for pattern in self.VAGUE_PATTERNS:
            if re.search(pattern, text_lower):
                analysis["is_vague"] = True
                analysis["score"] -= 2
                break

        # Update patterns
        self.patterns["total_inputs"] += 1

        for word in analysis["action_words_found"]:
            self.patterns["action_words_used"][word] += 1

        for word in analysis["context_words_found"]:
            self.patterns["context_words_used"][word] += 1

        if analysis["is_direct_command"]:
            self.patterns["direct_commands"] += 1

        if analysis["is_vague"]:
            self.patterns["vague_requests"] += 1

        return analysis

    def get_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Get recommendations for improvement"""
        recommendations = []

        if not analysis["has_action_word"]:
            recommendations.append("💡 Add an action word: 'start', 'fix', 'create', etc.")

        if not analysis["has_context_word"]:
            recommendations.append("💡 Add context: 'since', 'because', 'so that', etc.")

        if analysis["is_vague"]:
            recommendations.append("⚠️  Avoid vague phrases like 'can you maybe' - be direct!")

        if not analysis["is_direct_command"]:
            recommendations.append("💡 Try starting with a direct command: 'Start X' or 'Fix Y'")

        if analysis["score"] < 3:
            recommendations.append("📊 Low score - add more action words and context")

        return recommendations

    def print_analysis(self, analysis: Dict[str, Any]):
        """Print analysis results"""
        print("=" * 80)
        print("📊 COMMUNICATION ANALYSIS")
        print("=" * 80)
        print()
        print(f"Input: {analysis['text']}")
        print()
        print(f"Score: {analysis['score']}/10")
        print()
        print("Patterns Detected:")
        if analysis["has_action_word"]:
            print(f"  ✅ Action words: {', '.join(analysis['action_words_found'])}")
        else:
            print("  ❌ No action words found")

        if analysis["has_context_word"]:
            print(f"  ✅ Context words: {', '.join(analysis['context_words_found'])}")
        else:
            print("  ❌ No context words found")

        if analysis["is_direct_command"]:
            print("  ✅ Direct command pattern")
        else:
            print("  ⚠️  Not a direct command")

        if analysis["is_vague"]:
            print("  ⚠️  Contains vague phrasing")
        print()

        recommendations = self.get_recommendations(analysis)
        if recommendations:
            print("Recommendations:")
            for rec in recommendations:
                print(f"  {rec}")
        else:
            print("✅ Great communication pattern!")
        print()

    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics"""
        total = self.patterns["total_inputs"]
        if total == 0:
            return {"message": "No data yet"}

        return {
            "total_inputs": total,
            "direct_command_rate": self.patterns["direct_commands"] / total * 100,
            "vague_request_rate": self.patterns["vague_requests"] / total * 100,
            "top_action_words": dict(self.patterns["action_words_used"].most_common(5)),
            "top_context_words": dict(self.patterns["context_words_used"].most_common(5))
        }


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze communication patterns")
    parser.add_argument("text", nargs="?", help="Text to analyze")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    args = parser.parse_args()

    analyzer = CommunicationAnalyzer()

    if args.stats:
        stats = analyzer.get_statistics()
        print("=" * 80)
        print("📊 COMMUNICATION STATISTICS")
        print("=" * 80)
        print()
        for key, value in stats.items():
            print(f"{key}: {value}")
        print()
    elif args.text:
        analysis = analyzer.analyze_input(args.text)
        analyzer.print_analysis(analysis)
        analyzer.save_patterns()
    else:
        print("Usage: analyze_communication_patterns.py <text>")
        print("   or: analyze_communication_patterns.py --stats")

    return 0


if __name__ == "__main__":


    sys.exit(main())