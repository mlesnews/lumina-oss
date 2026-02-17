#!/usr/bin/env python3
"""
Iron Legion Activation Detector

Detects the magic words "Jarvis Iron Legion" from voice input or text
and enables Iron Man assistant activation.

Tags: #IRON_LEGION #MAGIC_WORDS #ACTIVATION @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Optional

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

logger = get_logger("IronLegionActivation")


class IronLegionActivationDetector:
    """
    Detects "Jarvis Iron Legion" magic words

    When detected, enables Iron Man assistant activation.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.activation_phrase_file = self.project_root / "data" / "iron_man_activation_phrase.txt"
        self.activation_phrase_file.parent.mkdir(parents=True, exist_ok=True)

        self.magic_words = "jarvis iron legion"

        logger.info("=" * 80)
        logger.info("⚔️  IRON LEGION ACTIVATION DETECTOR")
        logger.info("=" * 80)
        logger.info(f"   Magic Words: '{self.magic_words}'")
        logger.info("   Status: Listening for activation phrase")
        logger.info("=" * 80)

    def detect_in_text(self, text: str) -> bool:
        """
        Detect magic words in text

        Args:
            text: Text to check

        Returns:
            True if magic words detected
        """
        text_lower = text.lower().strip()
        magic_lower = self.magic_words.lower()

        if magic_lower in text_lower:
            logger.info(f"✅ MAGIC WORDS DETECTED: '{self.magic_words}'")
            self._enable_activation()
            return True

        return False

    def _enable_activation(self):
        """Enable Iron Man assistant activation"""
        try:
            # Write activation phrase to file (manager will detect it)
            with open(self.activation_phrase_file, 'w', encoding='utf-8') as f:
                f.write(self.magic_words)

            logger.info("✅ Iron Man assistant activation ENABLED")
            logger.info("   Assistants can now be launched")
        except Exception as e:
            logger.error(f"❌ Error enabling activation: {e}")

    def check_voice_input(self, voice_text: str) -> bool:
        """Check voice input for magic words"""
        return self.detect_in_text(voice_text)

    def check_command(self, command: str) -> bool:
        """Check command for magic words"""
        return self.detect_in_text(command)


def main():
    """Main entry point for testing"""
    detector = IronLegionActivationDetector()

    # Test detection
    test_phrases = [
        "Jarvis Iron Legion",
        "jarvis iron legion",
        "Hey, Jarvis Iron Legion activate",
        "I want to activate Jarvis Iron Legion",
        "Just some normal text"
    ]

    print("\n" + "=" * 80)
    print("🧪 TESTING MAGIC WORDS DETECTION")
    print("=" * 80)

    for phrase in test_phrases:
        detected = detector.detect_in_text(phrase)
        status = "✅ DETECTED" if detected else "❌ NOT DETECTED"
        print(f"{status}: '{phrase}'")

    print("=" * 80)


if __name__ == "__main__":


    main()