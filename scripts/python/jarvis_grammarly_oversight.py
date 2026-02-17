"""
JARVIS Grammarly-CLI Oversight System
Provides JARVIS oversight and control over Grammarly-CLI contributions
to AI agent chat sessions for conversational flow.

Author: JARVIS System
Date: 2026-01-09
Tags: #JARVIS @LUMINA #GRAMMARLY #CONVERSATIONAL
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)


class GrammarlyAction(str, Enum):
    """Grammarly action types."""
    CORRECT = "correct"
    SUGGEST = "suggest"
    IGNORE = "ignore"
    OVERRIDE = "override"


@dataclass
class GrammarlyContribution:
    """A Grammarly contribution to chat."""
    original_text: str
    corrected_text: Optional[str] = None
    suggestions: List[str] = None
    action: GrammarlyAction = GrammarlyAction.SUGGEST
    confidence: float = 0.0
    timestamp: Optional[str] = None
    context: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        if isinstance(data.get('action'), GrammarlyAction):
            data['action'] = data['action'].value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GrammarlyContribution':
        """Create from dictionary."""
        if isinstance(data.get('action'), str):
            data['action'] = GrammarlyAction(data['action'])
        return cls(**data)


class JARVISGrammarlyOversight:
    """
    Provides JARVIS oversight and control over Grammarly-CLI contributions.

    Features:
    - Monitor Grammarly corrections in chat
    - Apply conversational flow rules
    - Override when needed for natural conversation
    - Track contribution patterns
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize Grammarly oversight system.

        Args:
            project_root: Project root directory. Defaults to current directory.
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)

        # File paths
        self.contributions_file = self.project_root / "data" / "grammarly" / "contributions.json"
        self.rules_file = self.project_root / "config" / "grammarly_oversight_rules.json"

        # Ensure directories exist
        self.contributions_file.parent.mkdir(parents=True, exist_ok=True)
        self.rules_file.parent.mkdir(parents=True, exist_ok=True)

        # Load state
        self.contributions: List[GrammarlyContribution] = []
        self.rules: Dict[str, Any] = {}

        self._load_all()

    def _load_all(self) -> None:
        """Load contributions and rules."""
        # Load contributions
        if self.contributions_file.exists():
            try:
                with open(self.contributions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.contributions = [
                        GrammarlyContribution.from_dict(item) 
                        for item in data.get('contributions', [])
                    ]
            except Exception as e:
                logger.error(f"Failed to load contributions: {e}", exc_info=True)
                self.contributions = []
        else:
            self.contributions = []

        # Load rules
        if self.rules_file.exists():
            try:
                with open(self.rules_file, 'r', encoding='utf-8') as f:
                    self.rules = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load rules: {e}", exc_info=True)
                self.rules = self._default_rules()
        else:
            self.rules = self._default_rules()
            self._save_rules()

    def _default_rules(self) -> Dict[str, Any]:
        """Get default oversight rules."""
        return {
            'conversational_mode': True,
            'preserve_intent': True,
            'allow_informal': True,
            'override_strict_grammar': True,
            'preserve_voice_tone': True,
            'ignore_casual_errors': True,
            'min_confidence': 0.7,
            'auto_apply': False,
            'patterns_to_ignore': [
                r'^[A-Z\s]+$',  # ALL CAPS (intentional emphasis)
                r'\.{3,}',  # Multiple dots (ellipsis)
                r'!{2,}',  # Multiple exclamation marks
            ],
            'context_aware': True
        }

    def _save_contributions(self) -> None:
        """Save contributions."""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'description': 'Grammarly contributions to AI agent chat',
                'contributions': [c.to_dict() for c in self.contributions]
            }
            with open(self.contributions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save contributions: {e}", exc_info=True)

    def _save_rules(self) -> None:
        """Save rules."""
        try:
            with open(self.rules_file, 'w', encoding='utf-8') as f:
                json.dump(self.rules, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save rules: {e}", exc_info=True)

    def should_apply_correction(self, contribution: GrammarlyContribution) -> bool:
        """
        Determine if Grammarly correction should be applied.

        Args:
            contribution: Grammarly contribution to evaluate

        Returns:
            True if correction should be applied
        """
        # Check confidence threshold
        if contribution.confidence < self.rules.get('min_confidence', 0.7):
            return False

        # Check if auto-apply is enabled
        if not self.rules.get('auto_apply', False):
            return False

        # Check patterns to ignore
        for pattern in self.rules.get('patterns_to_ignore', []):
            if re.match(pattern, contribution.original_text):
                return False

        # Conversational mode: preserve intent and tone
        if self.rules.get('conversational_mode', True):
            # Don't correct if it breaks conversational flow
            if self._breaks_conversational_flow(contribution):
                return False

        return True

    def _breaks_conversational_flow(self, contribution: GrammarlyContribution) -> bool:
        """
        Check if correction would break conversational flow.

        Args:
            contribution: Grammarly contribution

        Returns:
            True if correction would break flow
        """
        original = contribution.original_text.lower()
        corrected = (contribution.corrected_text or "").lower()

        # Preserve informal language in conversational mode
        if self.rules.get('allow_informal', True):
            # Don't correct "gonna" to "going to" in conversation
            if "gonna" in original and "going to" in corrected:
                return True
            # Don't correct "wanna" to "want to"
            if "wanna" in original and "want to" in corrected:
                return True

        # Preserve voice tone
        if self.rules.get('preserve_voice_tone', True):
            # Don't over-formalize casual speech
            if self._is_overly_formal(corrected, original):
                return True

        return False

    def _is_overly_formal(self, corrected: str, original: str) -> bool:
        """Check if correction is overly formal."""
        formal_indicators = [
            "shall", "would like to", "I would", "please be advised"
        ]
        for indicator in formal_indicators:
            if indicator in corrected.lower() and indicator not in original.lower():
                return True
        return False

    def review_contribution(self, original_text: str, corrected_text: str,
                          suggestions: List[str], confidence: float,
                          context: Optional[str] = None) -> GrammarlyContribution:
        """
        Review a Grammarly contribution and decide on action.

        Args:
            original_text: Original text
            corrected_text: Grammarly's corrected text
            suggestions: List of suggestions
            confidence: Confidence score (0.0-1.0)
            context: Optional context

        Returns:
            GrammarlyContribution with action determined
        """
        contribution = GrammarlyContribution(
            original_text=original_text,
            corrected_text=corrected_text,
            suggestions=suggestions,
            confidence=confidence,
            context=context
        )

        # Determine action
        if self.should_apply_correction(contribution):
            contribution.action = GrammarlyAction.CORRECT
        elif self.rules.get('conversational_mode', True):
            # In conversational mode, often ignore for natural flow
            contribution.action = GrammarlyAction.IGNORE
        else:
            contribution.action = GrammarlyAction.SUGGEST

        # Store contribution
        self.contributions.append(contribution)
        self._save_contributions()

        return contribution

    def get_oversight_summary(self) -> Dict[str, Any]:
        """Get summary of Grammarly oversight activity."""
        total = len(self.contributions)
        corrected = len([c for c in self.contributions 
                        if c.action == GrammarlyAction.CORRECT])
        ignored = len([c for c in self.contributions 
                      if c.action == GrammarlyAction.IGNORE])
        suggested = len([c for c in self.contributions 
                        if c.action == GrammarlyAction.SUGGEST])

        return {
            'total_contributions': total,
            'corrected': corrected,
            'ignored': ignored,
            'suggested': suggested,
            'conversational_mode': self.rules.get('conversational_mode', True),
            'auto_apply': self.rules.get('auto_apply', False),
            'rules': self.rules
        }

    def update_rules(self, **kwargs) -> None:
        """Update oversight rules."""
        self.rules.update(kwargs)
        self._save_rules()
        logger.info(f"Updated Grammarly oversight rules: {kwargs}")


def main():
    """CLI interface for Grammarly oversight."""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Grammarly Oversight")
    parser.add_argument('--review', nargs=4, metavar=('ORIGINAL', 'CORRECTED', 'SUGGESTIONS', 'CONFIDENCE'),
                       help='Review a contribution')
    parser.add_argument('--summary', action='store_true', help='Show oversight summary')
    parser.add_argument('--set-rule', nargs=2, metavar=('KEY', 'VALUE'),
                       help='Set a rule (key value)')
    parser.add_argument('--conversational-mode', type=bool, help='Enable/disable conversational mode')

    args = parser.parse_args()

    oversight = JARVISGrammarlyOversight()

    if args.set_rule:
        key, value = args.set_rule
        # Try to parse value as JSON
        try:
            value = json.loads(value)
        except:
            # Keep as string if not JSON
            pass
        oversight.update_rules(**{key: value})
        print(f"✅ Rule updated: {key} = {value}")

    if args.conversational_mode is not None:
        oversight.update_rules(conversational_mode=args.conversational_mode)
        print(f"✅ Conversational mode: {args.conversational_mode}")

    if args.review:
        original, corrected, suggestions_str, confidence = args.review
        suggestions = json.loads(suggestions_str) if suggestions_str else []
        contribution = oversight.review_contribution(
            original, corrected, suggestions, float(confidence)
        )
        print(f"✅ Reviewed: {contribution.action.value}")

    if args.summary or not any([args.review, args.set_rule, args.conversational_mode]):
        summary = oversight.get_oversight_summary()
        print(f"\n📊 Grammarly Oversight Summary")
        print(f"Total Contributions: {summary['total_contributions']}")
        print(f"Corrected: {summary['corrected']}")
        print(f"Ignored: {summary['ignored']}")
        print(f"Suggested: {summary['suggested']}")
        print(f"Conversational Mode: {summary['conversational_mode']}")
        print(f"Auto-Apply: {summary['auto_apply']}")


if __name__ == "__main__":


    main()