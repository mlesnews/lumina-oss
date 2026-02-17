#!/usr/bin/env python3
"""
Auto-Activate Voice Input - Automatically clicks voice input button

Automatically activates voice input in Cursor IDE so Jarvis can listen
without requiring manual button click.

Tags: #VOICE_INPUT #AUTOMATION #CURSOR_IDE @JARVIS @LUMINA
"""

import sys
import time
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

try:
    from manus_voice_input_button import MANUSVoiceInputButton
    VOICE_INPUT_AVAILABLE = True
except ImportError:
    VOICE_INPUT_AVAILABLE = False

logger = get_logger("AutoActivateVoice")


def auto_activate_voice_input():
    """Automatically activate voice input using MANUS"""

    logger.info("="*80)
    logger.info("🎤 AUTO-ACTIVATING VOICE INPUT")
    logger.info("="*80)
    logger.info("")

    if not VOICE_INPUT_AVAILABLE:
        logger.error("❌ MANUS Voice Input not available")
        return False

    try:
        automator = MANUSVoiceInputButton()
        success = automator.activate_voice_input()

        if success:
            logger.info("")
            logger.info("✅ Voice input activated successfully")
            logger.info("   Jarvis can now listen without manual button click")
            return True
        else:
            logger.warning("⚠️  Failed to activate voice input")
            return False

    except Exception as e:
        logger.error(f"❌ Error activating voice input: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = auto_activate_voice_input()
    sys.exit(0 if success else 1)
