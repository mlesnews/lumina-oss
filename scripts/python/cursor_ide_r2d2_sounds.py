#!/usr/bin/env python3
"""
Cursor IDE R2-D2 Sound Integration
Replace Cursor IDE sounds with R2-D2 Star Wars themed sounds

This can be used to intercept Cursor IDE notifications and play R2-D2 sounds instead.

Tags: #CURSOR #R2D2 #STAR_WARS #SOUND #NOTIFICATION @JARVIS @LUMINA
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from r2d2_sound_system import get_r2d2_sound_system, R2D2SoundType
    from lumina_logger import get_logger
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    print(f"❌ Import error: {e}")

logger = get_logger("CursorR2D2Sounds")


def play_cursor_notification(sound_context: str = "notification"):
    """
    Play R2-D2 sound for Cursor IDE notification

    Args:
        sound_context: Context of the notification
            - "success" / "happy" → R2-D2 happy sound
            - "error" / "bad" → R2-D2 error sound
            - "alert" / "warning" → R2-D2 alert sound
            - "prompt" / "waiting" → R2-D2 prompt sound
            - "notification" / "info" → R2-D2 notification sound
            - "working" / "processing" → R2-D2 working sound
    """
    try:
        r2d2 = get_r2d2_sound_system()

        context_lower = sound_context.lower()

        if context_lower in ["success", "happy", "completed", "done"]:
            r2d2.play_happy()
        elif context_lower in ["error", "bad", "failed", "failure"]:
            r2d2.play_error()
        elif context_lower in ["alert", "warning", "caution"]:
            r2d2.play_alert()
        elif context_lower in ["prompt", "waiting", "input"]:
            r2d2.play_prompt()
        elif context_lower in ["working", "processing", "loading"]:
            r2d2.play_working()
        elif context_lower in ["excited", "great", "excellent"]:
            r2d2.play_excited()
        else:
            # Default to notification
            r2d2.play_notification()

        logger.debug(f"🔊 Played R2-D2 sound for Cursor IDE: {sound_context}")
    except Exception as e:
        logger.debug(f"Error playing R2-D2 sound for Cursor: {e}")


# Example usage for different Cursor IDE events
if __name__ == "__main__":
    print("=" * 80)
    print("🔊 CURSOR IDE R2-D2 SOUNDS")
    print("=" * 80)
    print()
    print("This module provides R2-D2 sounds for Cursor IDE notifications.")
    print("Import and use play_cursor_notification() in your Cursor workflows.")
    print()
    print("Example contexts:")
    print("  - 'success' / 'happy' → Happy R2-D2 beeps")
    print("  - 'error' / 'bad' → Error R2-D2 beeps")
    print("  - 'alert' / 'warning' → Alert R2-D2 beeps")
    print("  - 'prompt' / 'waiting' → Prompt R2-D2 beeps")
    print("  - 'notification' / 'info' → Notification R2-D2 beep")
    print("  - 'working' / 'processing' → Working R2-D2 beeps")
    print()
    print("=" * 80)
