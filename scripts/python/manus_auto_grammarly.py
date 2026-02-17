#!/usr/bin/env python3
"""
MANUS Auto-Grammarly - Automatic Typo Correction

@MANUS automatically uses Grammarly/spell check to fix typos
Works automatically while you work

"WOULD BE NICE IF YOU JUST @MANUS 'D A SOLUTION TO USE IT AUTOMATICALLY"
"""

import sys
import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MANUSAutoGrammarly")

# Try to import spell checking libraries
try:
    from spellchecker import SpellChecker
    SPELL_CHECK_AVAILABLE = True
except ImportError:
    SPELL_CHECK_AVAILABLE = False
    logger.info("pyspellchecker not available - install: pip install pyspellchecker")

try:
    import language_tool_python
    LANGUAGE_TOOL_AVAILABLE = True
except ImportError:
    LANGUAGE_TOOL_AVAILABLE = False
    logger.info("language_tool_python not available - install: pip install language_tool_python")


# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class MANUSAutoGrammarly:
    """
    MANUS Auto-Grammarly - Automatic Typo Correction

    Automatically fixes typos using spell check and grammar tools
    Works automatically while you work
    """

    def __init__(self):
        self.logger = get_logger("MANUSAutoGrammarly")
        self.spell_checker = None
        self.language_tool = None
        self.auto_correct_enabled = True

        # Initialize spell checkers
        if SPELL_CHECK_AVAILABLE:
            try:
                self.spell_checker = SpellChecker()
                self.logger.info("  ✅ Spell checker ready")
            except Exception as e:
                self.logger.debug(f"  Spell checker init error: {e}")

        if LANGUAGE_TOOL_AVAILABLE:
            try:
                self.language_tool = language_tool_python.LanguageTool('en-US')
                self.logger.info("  ✅ Language Tool ready")
            except Exception as e:
                self.logger.debug(f"  Language Tool init error: {e}")

        # Common typos from our conversation
        self.known_typos = {
            "ontandras": "entendres",
            "ONTANDRAS": "ENTENDRES",
            "ontandra": "entendre",
            "ONTANDRA": "ENTENDRE"
        }

        self.logger.info("🔧 MANUS Auto-Grammarly initialized")
        self.logger.info("   Automatic typo correction enabled")

    def correct_text(self, text: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Automatically correct typos in text

        Returns: (corrected_text, corrections_made)
        """
        corrected = text
        corrections = []

        # Check known typos first
        for typo, correct in self.known_typos.items():
            if typo in corrected:
                corrected = corrected.replace(typo, correct)
                corrections.append({
                    "original": typo,
                    "corrected": correct,
                    "type": "known_typo"
                })

        # Use spell checker if available
        if self.spell_checker:
            words = corrected.split()
            for word in words:
                # Remove punctuation for checking
                clean_word = re.sub(r'[^\w]', '', word)
                if clean_word and not self.spell_checker.correction(clean_word) == clean_word:
                    correction = self.spell_checker.correction(clean_word)
                    if correction != clean_word:
                        corrected = corrected.replace(clean_word, correction)
                        corrections.append({
                            "original": clean_word,
                            "corrected": correction,
                            "type": "spell_check"
                        })

        # Use language tool if available
        if self.language_tool:
            try:
                matches = self.language_tool.check(corrected)
                for match in matches:
                    if match.replacements:
                        original = corrected[match.offset:match.offset+match.errorLength]
                        replacement = match.replacements[0]
                        corrected = corrected[:match.offset] + replacement + corrected[match.offset+match.errorLength:]
                        corrections.append({
                            "original": original,
                            "corrected": replacement,
                            "type": "grammar_check",
                            "rule": match.ruleId
                        })
            except Exception as e:
                self.logger.debug(f"Language Tool error: {e}")

        return corrected, corrections

    def auto_correct_input(self, text: str) -> str:
        """Automatically correct input text"""
        if not self.auto_correct_enabled:
            return text

        corrected, corrections = self.correct_text(text)

        if corrections:
            self.logger.info(f"🔧 Auto-corrected {len(corrections)} issues")
            for correction in corrections:
                self.logger.debug(f"  {correction['original']} → {correction['corrected']}")

        return corrected


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="MANUS Auto-Grammarly")
    parser.add_argument("--text", type=str, help="Text to correct")
    parser.add_argument("--test", action="store_true", help="Test with example")

    args = parser.parse_args()

    grammarly = MANUSAutoGrammarly()

    if args.text:
        corrected = grammarly.auto_correct_input(args.text)
        print(f"\nOriginal: {args.text}")
        print(f"Corrected: {corrected}")
    elif args.test:
        test_text = "DOUBLE ONTANDRAS? Would be nice if you just @MANUS 'd a solution"
        corrected = grammarly.auto_correct_input(test_text)
        print(f"\nOriginal: {test_text}")
        print(f"Corrected: {corrected}")
    else:
        parser.print_help()

