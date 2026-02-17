#!/usr/bin/env python3
"""
JARVIS Voice Filter System

Filters out wife's voice/speech from voice transcriptions.
Uses voice recognition and filtering to exclude specific speaker.

Tags: #JARVIS #VOICE_FILTER #SPEECH_RECOGNITION @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import List, Optional, Dict, Any

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

logger = get_logger("JARVISVoiceFilter")


class JARVISVoiceFilter:
    """Voice filter to exclude wife's speech"""

    def __init__(self):
        # Keywords/phrases to filter out (wife's speech patterns)
        self.filter_patterns = [
            "do they have class",
            "facilities",
            # Add more patterns as needed
        ]

        # Voice characteristics to identify (if voice recognition available)
        self.filtered_speaker_id = "wife"  # Speaker ID to filter

        # Filter mode
        self.filter_enabled = True

    def should_filter(self, text: str, speaker_id: Optional[str] = None) -> bool:
        """Check if text should be filtered out"""
        if not self.filter_enabled:
            return False

        text_lower = text.lower()

        # Check against filter patterns
        for pattern in self.filter_patterns:
            if pattern in text_lower:
                logger.debug(f"🔇 Filtered out text matching pattern: {pattern}")
                return True

        # Check speaker ID if available
        if speaker_id and speaker_id == self.filtered_speaker_id:
            logger.debug(f"🔇 Filtered out text from speaker: {speaker_id}")
            return True

        return False

    def filter_text(self, text: str, speaker_id: Optional[str] = None) -> Optional[str]:
        """Filter text - returns None if filtered, text if not"""
        if self.should_filter(text, speaker_id):
            return None
        return text

    def add_filter_pattern(self, pattern: str):
        """Add a new filter pattern"""
        if pattern not in self.filter_patterns:
            self.filter_patterns.append(pattern.lower())
            logger.info(f"✅ Added filter pattern: {pattern}")

    def remove_filter_pattern(self, pattern: str):
        """Remove a filter pattern"""
        if pattern.lower() in self.filter_patterns:
            self.filter_patterns.remove(pattern.lower())
            logger.info(f"✅ Removed filter pattern: {pattern}")


# Singleton instance
_voice_filter_instance = None

def get_jarvis_voice_filter():
    """Get singleton instance of voice filter"""
    global _voice_filter_instance
    if _voice_filter_instance is None:
        _voice_filter_instance = JARVISVoiceFilter()
    return _voice_filter_instance
