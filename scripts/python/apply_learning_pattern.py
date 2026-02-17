#!/usr/bin/env python3
"""
Apply Learning Pattern - Learn From Mistakes

"What have we learned? What's the pattern? What's the logic? 
Where they actually learn from their own mistakes. 
No one has figured out how to do that."

This system applies the systematic learning pattern:
1. Recognize the mistake
2. Identify the pattern
3. Extract the logic
4. Apply the correction
5. Document for future
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
import json
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ApplyLearningPattern")


@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class Mistake:
    """A mistake that was made"""
    mistake_id: str
    description: str
    what_went_wrong: str
    pattern_identified: str
    logic_extracted: str
    correction_applied: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LearningPattern:
    """A learning pattern extracted from mistakes"""
    pattern_id: str
    pattern_name: str
    description: str
    correct_approach: str
    application_domain: str
    mistake_examples: List[str] = field(default_factory=list)
    documented: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ApplyLearningPattern:
    """
    Apply Learning Pattern - Learn From Mistakes

    Systematic learning from mistakes:
    1. Recognize the mistake
    2. Identify the pattern
    3. Extract the logic
    4. Apply the correction
    5. Document for future
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Learning Pattern System"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("ApplyLearningPattern")

        # Data storage
        self.data_dir = self.project_root / "data" / "learning_patterns"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load existing learnings
        self.mistakes: List[Mistake] = []
        self.patterns: List[LearningPattern] = []
        self._load_learnings()

        # Add the YouTube API Key pattern we just learned
        self._add_youtube_api_key_pattern()

        self.logger.info("🧠 Learning Pattern System initialized")
        self.logger.info("   Learning from mistakes, systematically")

    def _load_learnings(self) -> None:
        """Load existing learnings"""
        mistakes_file = self.data_dir / "mistakes.json"
        patterns_file = self.data_dir / "patterns.json"

        if mistakes_file.exists():
            try:
                with open(mistakes_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.mistakes = [Mistake(**m) for m in data]
            except Exception as e:
                self.logger.warning(f"  Could not load mistakes: {e}")

        if patterns_file.exists():
            try:
                with open(patterns_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.patterns = [LearningPattern(**p) for p in data]
            except Exception as e:
                self.logger.warning(f"  Could not load patterns: {e}")

    def _save_learnings(self) -> None:
        try:
            """Save learnings"""
            mistakes_file = self.data_dir / "mistakes.json"
            patterns_file = self.data_dir / "patterns.json"

            with open(mistakes_file, 'w', encoding='utf-8') as f:
                json.dump([m.to_dict() for m in self.mistakes], f, indent=2)

            with open(patterns_file, 'w', encoding='utf-8') as f:
                json.dump([p.to_dict() for p in self.patterns], f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_learnings: {e}", exc_info=True)
            raise
    def _add_youtube_api_key_pattern(self) -> None:
        """Add the YouTube API Key learning pattern"""
        # Check if already added
        if any(p.pattern_id == "youtube-api-key-lookup" for p in self.patterns):
            return

        mistake = Mistake(
            mistake_id="youtube-api-key-001",
            description="Assumed YouTube API key wasn't in Azure Key Vault",
            what_went_wrong="Guessed secret names instead of listing actual secrets. Gave up after first attempts failed.",
            pattern_identified="Assumed failure instead of verifying. Guessed instead of enumerating.",
            logic_extracted="LIST FIRST, then use real names. Check what exists before assuming what's missing.",
            correction_applied="List all secrets, filter by keywords, use actual secret names found"
        )

        pattern = LearningPattern(
            pattern_id="youtube-api-key-lookup",
            pattern_name="List Before Lookup Pattern",
            description="When looking for something that 'might not exist', LIST/ENUMERATE first, then use real data.",
            mistake_examples=[
                "Guessing secret names instead of listing them",
                "Assuming failure without verification",
                "Giving up after first attempt"
            ],
            correct_approach="1. LIST/ENUMERATE what exists 2. Use REAL data 3. Check SYSTEMATICALLY",
            application_domain="Secret/API key lookup, Resource discovery, Data verification",
            documented=True
        )

        self.mistakes.append(mistake)
        self.patterns.append(pattern)
        self._save_learnings()

        self.logger.info(f"  ✅ Added YouTube API Key learning pattern")

    def apply_pattern(self, problem_description: str, pattern_id: str) -> Dict[str, Any]:
        """Apply a learning pattern to a problem"""
        pattern = next((p for p in self.patterns if p.pattern_id == pattern_id), None)

        if not pattern:
            return {
                "success": False,
                "error": f"Pattern {pattern_id} not found"
            }

        return {
            "success": True,
            "pattern": pattern.pattern_name,
            "approach": pattern.correct_approach,
            "application": f"Applying {pattern.pattern_name} to: {problem_description}"
        }

    def get_all_patterns(self) -> List[Dict[str, Any]]:
        """Get all learning patterns"""
        return [p.to_dict() for p in self.patterns]

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of learnings"""
        return {
            "total_mistakes": len(self.mistakes),
            "total_patterns": len(self.patterns),
            "patterns": [p.to_dict() for p in self.patterns],
            "philosophy": "Learn from mistakes systematically. List first, verify, use real data. Document for future."
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Apply Learning Pattern - Learn From Mistakes")
    parser.add_argument("--summary", action="store_true", help="Get learning summary")
    parser.add_argument("--patterns", action="store_true", help="List all patterns")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    learning = ApplyLearningPattern()

    if args.summary:
        summary = learning.get_summary()
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print(f"\n🧠 Learning Pattern Summary")
            print(f"   Total Mistakes: {summary['total_mistakes']}")
            print(f"   Total Patterns: {summary['total_patterns']}")
            print(f"\n   Philosophy: {summary['philosophy']}")
            print(f"\n   Patterns:")
            for pattern in summary['patterns']:
                print(f"\n     - {pattern['pattern_name']}")
                print(f"       {pattern['description']}")

    elif args.patterns:
        patterns = learning.get_all_patterns()
        if args.json:
            print(json.dumps(patterns, indent=2))
        else:
            print(f"\n📚 Learning Patterns")
            for pattern in patterns:
                print(f"\n   {pattern['pattern_name']}")
                print(f"     ID: {pattern['pattern_id']}")
                print(f"     Description: {pattern['description']}")
                print(f"     Approach: {pattern['correct_approach']}")

    else:
        parser.print_help()
        print("\n🧠 Learning Pattern System")
        print("   Learn from mistakes systematically")

