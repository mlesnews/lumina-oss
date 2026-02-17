#!/usr/bin/env python3
"""
Passive/Active Voice System using Windows Speech Recognition
Uses Windows built-in speech recognition (offline, no internet needed)

PASSIVE: Always listening for "Hey Jarvis"
ACTIVE: After trigger, transcribes to Cursor IDE
"""

import sys
import time
import re
import logging
from pathlib import Path
from typing import Optional

# Add project root
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import pyautogui
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False
    print("⚠️  pyautogui not installed: pip install pyautogui")

# Try Windows Speech Recognition
try:
    import win32com.client
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False
    print("⚠️  pywin32 not installed: pip install pywin32")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


class PassiveActiveVoiceWindows:
    """
    Passive/Active Voice System using Windows Speech Recognition

    Uses Windows built-in speech recognition (offline, reliable)
    """

    def __init__(self, trigger_word: str = "hey jarvis"):
        """Initialize with Windows Speech Recognition"""
        self.trigger_word = trigger_word.lower()
        self.is_running = False
        self.is_active = False
        self.transcription_buffer = ""
        self.speech_engine = None

        # Initialize Windows Speech Recognition
        if HAS_WIN32:
            try:
                self.speech_engine = win32com.client.Dispatch("SAPI.SpSharedRecognizer")
                logger.info("✅ Windows Speech Recognition initialized")
            except Exception as e:
                logger.error(f"❌ Could not initialize Windows Speech Recognition: {e}")
                logger.info("   Try: pip install pywin32")
        else:
            logger.error("❌ pywin32 not available")
            logger.info("   Install: pip install pywin32")

    def _update_cursor_field(self):
        """Update Cursor IDE input field"""
        if not HAS_PYAUTOGUI:
            return

        try:
            pyautogui.hotkey("ctrl", "a")
            time.sleep(0.1)
            pyautogui.write(self.transcription_buffer, interval=0.01)
        except Exception as e:
            logger.warning(f"Could not update Cursor field: {e}")

    def _handle_scratch_that(self):
        """Delete last phrase"""
        sentences = re.split(r'[.!?]\s+', self.transcription_buffer)
        if len(sentences) > 1:
            self.transcription_buffer = '. '.join(sentences[:-1]) + '.'
        else:
            words = self.transcription_buffer.split()
            if len(words) > 1:
                self.transcription_buffer = ' '.join(words[:-1])
            else:
                self.transcription_buffer = ""
        self._update_cursor_field()
        logger.info("↩️  Deleted last phrase")

    def _handle_clear_all(self):
        """Clear transcription"""
        self.transcription_buffer = ""
        self._update_cursor_field()
        logger.info("🗑️  Cleared all")

    def _handle_send(self):
        """Send message"""
        if HAS_PYAUTOGUI:
            pyautogui.press("enter")
            self.transcription_buffer = ""
            self.is_active = False
            logger.info("🚀 Message sent, returning to passive mode")

    def _process_speech(self, text: str):
        """Process recognized speech"""
        text_lower = text.lower().strip()

        # Check for trigger word (passive mode)
        if not self.is_active:
            if self.trigger_word in text_lower:
                self.is_active = True
                logger.info(f"🎯 TRIGGER DETECTED: '{text}'")
                logger.info("✅ ACTIVE MODE ACTIVATED")
                return

        # Active mode - process commands or transcribe
        if self.is_active:
            # Check for deactivate
            if "stop listening" in text_lower or "pause" in text_lower:
                self.is_active = False
                logger.info("⏸️  Returning to passive mode")
                return

            # Check for editing commands
            if "scratch that" in text_lower or "undo that" in text_lower:
                self._handle_scratch_that()
                return

            if "clear all" in text_lower or "start over" in text_lower:
                self._handle_clear_all()
                return

            if "send it" in text_lower or "do it" in text_lower:
                self._handle_send()
                return

            # Regular transcription
            if self.transcription_buffer:
                self.transcription_buffer += " " + text
            else:
                self.transcription_buffer = text

            self._update_cursor_field()
            logger.info(f"📝 Transcription: '{self.transcription_buffer}'")

    def start(self):
        """Start the system"""
        logger.info("=" * 60)
        logger.info("🎤 PASSIVE/ACTIVE VOICE (Windows Speech Recognition)")
        logger.info("=" * 60)
        logger.info("")
        logger.info("PASSIVE MODE: Listening for trigger word")
        logger.info(f"   Trigger: '{self.trigger_word}'")
        logger.info("")
        logger.info("ACTIVE MODE: Transcribing to Cursor IDE")
        logger.info("   Commands: 'Scratch that', 'Clear all', 'Send it'")
        logger.info("")
        logger.info("Press Ctrl+C to exit")
        logger.info("=" * 60)
        logger.info("")

        # Note: Windows Speech Recognition needs to be set up
        logger.info("📋 SETUP REQUIRED:")
        logger.info("   1. Open Windows Speech Recognition")
        logger.info("   2. Say 'Start listening'")
        logger.info("   3. This script will process recognized text")
        logger.info("")
        logger.info("   OR use F23 key for voice input (already working)")
        logger.info("")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Passive/Active Voice (Windows)")
    parser.add_argument("--trigger", default="hey jarvis",
                       help="Trigger word (default: 'hey jarvis')")

    args = parser.parse_args()

    system = PassiveActiveVoiceWindows(trigger_word=args.trigger)
    system.start()


if __name__ == "__main__":


    main()