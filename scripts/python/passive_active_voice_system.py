#!/usr/bin/env python3
"""
Passive/Active Voice Listening System with Transcription Editing

PASSIVE MODE: Always listening for trigger word (e.g., "Hey Cursor", "Jarvis")
ACTIVE MODE: After trigger word, actively transcribes and allows voice editing

Voice Editing Commands:
- "Scratch that" → Delete last phrase
- "Change [word] to [word]" → Replace word
- "Delete [word]" → Remove word
- "Add [text]" → Insert text
- "Clear all" → Clear transcription
- "Send it" → Send message

Tags: #VOICE_INPUT #PASSIVE_LISTENING #ACTIVE_LISTENING #TRANSCRIPTION_EDITING #RSI
"""

import sys
import time
import re
import logging
from pathlib import Path
from typing import Optional, Dict, List
from enum import Enum

# Add project root
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import speech_recognition as sr
    HAS_SPEECH_REC = True
except ImportError:
    HAS_SPEECH_REC = False
    print("⚠️  speech_recognition not installed: pip install SpeechRecognition")

try:
    import pyautogui
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False
    print("⚠️  pyautogui not installed: pip install pyautogui")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


class ListeningMode(Enum):
    """Listening mode states"""
    PASSIVE = "passive"  # Listening for trigger word only
    ACTIVE = "active"    # Actively transcribing
    PAUSED = "paused"    # Temporarily paused


class PassiveActiveVoiceSystem:
    """
    Passive/Active Voice Listening System

    PASSIVE: Always listening for trigger word (low CPU, filters everything else)
    ACTIVE: After trigger detected, actively transcribes to Cursor IDE
    """

    def __init__(
        self,
        trigger_words: List[str] = None,
        wake_word: str = "hey jarvis",
        deactivate_word: str = "stop listening"
    ):
        """
        Initialize passive/active voice system

        Args:
            trigger_words: List of trigger phrases (default: ["hey jarvis", "jarvis"])
            wake_word: Primary wake word for passive mode
            deactivate_word: Word to deactivate active mode
        """
        self.trigger_words = trigger_words or ["hey jarvis", "jarvis", "hey cursor"]
        self.wake_word = wake_word.lower()
        self.deactivate_word = deactivate_word.lower()

        # Listening state
        self.mode = ListeningMode.PASSIVE
        self.is_running = False
        self.recognizer = None
        self.microphone = None

        # Transcription buffer (current text being built)
        self.transcription_buffer = ""

        # Voice editing commands
        self.editing_commands = {
            "scratch that": self._handle_scratch_that,
            "undo that": self._handle_scratch_that,
            "delete that": self._handle_scratch_that,
            "clear all": self._handle_clear_all,
            "clear everything": self._handle_clear_all,
            "start over": self._handle_clear_all,
            "delete [word]": self._handle_delete_word,
            "change [word] to [word]": self._handle_change_word,
            "replace [word] with [word]": self._handle_change_word,
            "add [text]": self._handle_add_text,
            "insert [text]": self._handle_add_text,
            "new line": self._handle_new_line,
            "send it": self._handle_send,
            "do it": self._handle_send,
            "execute": self._handle_send,
            "stop listening": self._handle_stop_listening,
            "pause": self._handle_stop_listening,
            "resume": self._handle_resume,
            "wake up": self._handle_resume,
        }

        # Initialize speech recognition with improved settings
        if HAS_SPEECH_REC:
            self.recognizer = sr.Recognizer()
            # Lower energy threshold for better sensitivity
            self.recognizer.energy_threshold = 3000  # Lower = more sensitive
            self.recognizer.pause_threshold = 1.0  # Longer pause for clearer phrases
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.operation_timeout = 5  # Timeout for recognition
            # Adjust for ambient noise more aggressively
            self.recognizer.adjust_for_ambient_noise_duration = 2.0

        logger.info("🎤 Passive/Active Voice System initialized")
        logger.info(f"   Trigger words: {', '.join(self.trigger_words)}")
        logger.info(f"   Primary wake word: '{self.wake_word}'")
        logger.info(f"   Energy threshold: {self.recognizer.energy_threshold if self.recognizer else 'N/A'}")
        logger.info("   Recognition: Google Speech API (with Sphinx fallback)")

    def _handle_scratch_that(self, text: str) -> str:
        """Delete last phrase from transcription"""
        logger.info("↩️  Deleting last phrase...")
        # Remove last sentence or phrase
        # Simple: remove everything after last period/exclamation/question mark
        sentences = re.split(r'[.!?]\s+', self.transcription_buffer)
        if len(sentences) > 1:
            self.transcription_buffer = '. '.join(sentences[:-1]) + '.'
        else:
            # No sentence breaks, remove last word
            words = self.transcription_buffer.split()
            if len(words) > 1:
                self.transcription_buffer = ' '.join(words[:-1])
            else:
                self.transcription_buffer = ""

        # Update Cursor IDE field
        self._update_cursor_field()
        return "Deleted last phrase"

    def _handle_clear_all(self, text: str) -> str:
        """Clear entire transcription"""
        logger.info("🗑️  Clearing all...")
        self.transcription_buffer = ""
        self._update_cursor_field()
        return "Cleared"

    def _handle_delete_word(self, text: str) -> str:
        """Delete specific word from transcription"""
        # Extract word to delete (e.g., "delete hello" → "hello")
        match = re.search(r'delete\s+(\w+)', text.lower())
        if match:
            word_to_delete = match.group(1)
            # Remove word from buffer
            words = self.transcription_buffer.split()
            words = [w for w in words if w.lower() != word_to_delete.lower()]
            self.transcription_buffer = ' '.join(words)
            self._update_cursor_field()
            return f"Deleted '{word_to_delete}'"
        return "Could not find word to delete"

    def _handle_change_word(self, text: str) -> str:
        """Change one word to another"""
        # Extract "change X to Y" or "replace X with Y"
        match = re.search(r'(?:change|replace)\s+(\w+)\s+(?:to|with)\s+(\w+)', text.lower())
        if match:
            old_word = match.group(1)
            new_word = match.group(2)
            # Replace word in buffer
            words = self.transcription_buffer.split()
            words = [new_word if w.lower() == old_word.lower() else w for w in words]
            self.transcription_buffer = ' '.join(words)
            self._update_cursor_field()
            return f"Changed '{old_word}' to '{new_word}'"
        return "Could not parse change command"

    def _handle_add_text(self, text: str) -> str:
        """Add text to transcription"""
        # Extract text to add (e.g., "add hello world" → "hello world")
        match = re.search(r'(?:add|insert)\s+(.+)', text.lower())
        if match:
            text_to_add = match.group(1)
            self.transcription_buffer += " " + text_to_add
            self._update_cursor_field()
            return f"Added '{text_to_add}'"
        return "Could not parse add command"

    def _handle_new_line(self, text: str) -> str:
        """Insert new line"""
        if HAS_PYAUTOGUI:
            pyautogui.hotkey("shift", "enter")
            return "New line inserted"
        return "pyautogui not available"

    def _handle_send(self, text: str) -> str:
        """Send message (Enter key)"""
        logger.info("🚀 Sending message...")
        if HAS_PYAUTOGUI:
            pyautogui.press("enter")
            # Clear buffer after sending
            self.transcription_buffer = ""
            # Return to passive mode
            self.mode = ListeningMode.PASSIVE
            return "Message sent"
        return "pyautogui not available"

    def _handle_stop_listening(self, text: str) -> str:
        """Stop active listening, return to passive"""
        logger.info("⏸️  Stopping active listening...")
        self.mode = ListeningMode.PASSIVE
        return "Returned to passive mode"

    def _handle_resume(self, text: str) -> str:
        """Resume active listening"""
        logger.info("▶️  Resuming active listening...")
        self.mode = ListeningMode.ACTIVE
        return "Active listening resumed"

    def _update_cursor_field(self):
        """Update Cursor IDE input field with current transcription"""
        if not HAS_PYAUTOGUI:
            return

        try:
            # Select all in current field
            pyautogui.hotkey("ctrl", "a")
            time.sleep(0.1)
            # Type the transcription
            pyautogui.write(self.transcription_buffer, interval=0.01)
        except Exception as e:
            logger.warning(f"Could not update Cursor field: {e}")

    def _check_trigger_word(self, text: str) -> bool:
        """Check if text contains trigger word (flexible matching)"""
        if not text:
            return False

        text_lower = text.lower().strip()

        # Exact match
        for trigger in self.trigger_words:
            if trigger == text_lower:
                return True

        # Contains match (e.g., "hey jarvis" in "hey jarvis how are you")
        for trigger in self.trigger_words:
            if trigger in text_lower:
                # Additional check: trigger should be at start or after punctuation
                trigger_pos = text_lower.find(trigger)
                if trigger_pos == 0 or trigger_pos > 0 and text_lower[trigger_pos-1] in [' ', '.', '!', '?', ',']:
                    return True

        # Fuzzy match for common misrecognitions
        fuzzy_triggers = {
            "hey jarvis": ["hey jarvis", "hey jarvus", "hey jarvis", "hey jarvis", "hey jarvis"],
            "jarvis": ["jarvis", "jarvus", "jarvis", "jarvis"],
            "hey cursor": ["hey cursor", "hey cursor", "hey cursor"]
        }

        for trigger, variations in fuzzy_triggers.items():
            if trigger in self.trigger_words:
                for variation in variations:
                    if variation in text_lower:
                        return True

        return False

    def _check_editing_command(self, text: str) -> Optional[str]:
        """Check if text is an editing command"""
        text_lower = text.lower().strip()

        # Check for exact command matches
        for command_phrase, handler in self.editing_commands.items():
            if command_phrase in text_lower:
                return command_phrase

        # Check for pattern-based commands (delete word, change word, etc.)
        if re.search(r'delete\s+\w+', text_lower):
            return "delete [word]"
        if re.search(r'(?:change|replace)\s+\w+\s+(?:to|with)\s+\w+', text_lower):
            return "change [word] to [word]"
        if re.search(r'(?:add|insert)\s+.+', text_lower):
            return "add [text]"

        return None

    def _process_passive_listening(self, audio) -> bool:
        """
        Process audio in passive mode - only respond to trigger words

        Returns:
            True if trigger word detected (should switch to active mode)
        """
        try:
            # Try multiple recognition engines for better reliability
            text = None
            recognition_errors = []

            # Try Google first (most accurate)
            try:
                text = self.recognizer.recognize_google(audio, language="en-US")
                logger.debug(f"Passive mode heard (Google): '{text}'")
            except sr.UnknownValueError as e:
                recognition_errors.append(f"Google: {e}")
            except sr.RequestError as e:
                recognition_errors.append(f"Google API error: {e}")
                # Fallback to sphinx if available
                try:
                    text = self.recognizer.recognize_sphinx(audio)
                    logger.debug(f"Passive mode heard (Sphinx): '{text}'")
                except:
                    pass

            if text:
                text_lower = text.lower().strip()
                logger.debug(f"Recognized text: '{text_lower}'")

                # Check for trigger word (more flexible matching)
                if self._check_trigger_word(text_lower):
                    logger.info(f"🎯 TRIGGER WORD DETECTED: '{text}'")
                    logger.info("   Switching to ACTIVE listening mode...")
                    return True

                # Also check for partial matches (e.g., "jarvis" in "hey jarvis how are you")
                for trigger in self.trigger_words:
                    if trigger in text_lower:
                        logger.info(f"🎯 TRIGGER WORD DETECTED (partial): '{trigger}' in '{text}'")
                        logger.info("   Switching to ACTIVE listening mode...")
                        return True

            # Ignore everything else in passive mode
            if recognition_errors:
                logger.debug(f"Recognition errors: {', '.join(recognition_errors)}")
            return False

        except Exception as e:
            logger.debug(f"Error in passive listening: {e}")
            return False

    def _process_active_listening(self, audio) -> bool:
        """
        Process audio in active mode - transcribe everything

        Returns:
            True if should continue active mode, False if should return to passive
        """
        try:
            text = self.recognizer.recognize_google(audio)
            logger.info(f"Active mode heard: '{text}'")

            # Check for deactivate word
            if self.deactivate_word in text.lower():
                logger.info("🛑 Deactivate word detected - returning to passive mode")
                self.mode = ListeningMode.PASSIVE
                return False

            # Check for editing commands
            command = self._check_editing_command(text)
            if command:
                handler = self.editing_commands.get(command)
                if handler:
                    result = handler(text)
                    logger.info(f"   Command executed: {result}")
                    return True

            # Check for send command
            if any(cmd in text.lower() for cmd in ["send it", "do it", "execute"]):
                self._handle_send(text)
                return False  # Return to passive after sending

            # Regular transcription - add to buffer
            if self.transcription_buffer:
                self.transcription_buffer += " " + text
            else:
                self.transcription_buffer = text

            # Update Cursor IDE field
            self._update_cursor_field()
            logger.info(f"   Transcription: '{self.transcription_buffer}'")

            return True  # Continue active mode

        except sr.UnknownValueError:
            logger.debug("Could not understand audio")
            return True  # Continue trying
        except sr.RequestError as e:
            logger.warning(f"Speech recognition error: {e}")
            return True  # Continue trying

    def _listen_once(self) -> bool:
        """Listen for one phrase and process based on current mode"""
        if not HAS_SPEECH_REC or not self.recognizer:
            return False

        try:
            with sr.Microphone() as source:
                # Adjust for ambient noise (more aggressive in passive mode)
                if self.mode == ListeningMode.PASSIVE:
                    # Longer calibration for passive mode
                    self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                    logger.debug("👂 Passive listening (waiting for trigger word)...")
                else:
                    # Shorter calibration for active mode
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    logger.info("🎤 Active listening (transcribing)...")

                # Listen for phrase (longer timeout in passive mode for trigger word)
                timeout = 3 if self.mode == ListeningMode.PASSIVE else 1
                phrase_limit = 15 if self.mode == ListeningMode.PASSIVE else 10

                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_limit
                )

                # Check audio quality
                if hasattr(audio, 'get_raw_data'):
                    import audioop
                    try:
                        raw_audio = audio.get_raw_data()
                        if raw_audio:
                            rms = audioop.rms(raw_audio, 2)
                            min_energy = self.recognizer.energy_threshold * 0.3
                            if rms < min_energy:
                                logger.debug(f"🔇 Rejected quiet audio (RMS: {rms:.0f} < {min_energy:.0f})")
                                return True  # Continue listening
                    except:
                        pass  # Continue even if audio check fails

                # Process based on mode
                if self.mode == ListeningMode.PASSIVE:
                    trigger_detected = self._process_passive_listening(audio)
                    if trigger_detected:
                        self.mode = ListeningMode.ACTIVE
                        logger.info("✅ ACTIVE MODE ACTIVATED")
                        logger.info("   Speak your message, use voice commands to edit")
                        logger.info("   Say 'stop listening' to return to passive mode")
                        return True
                else:  # ACTIVE mode
                    continue_active = self._process_active_listening(audio)
                    return continue_active

        except sr.WaitTimeoutError:
            # No audio detected - normal in passive mode
            return True
        except Exception as e:
            logger.error(f"Error in listen_once: {e}")
            return True  # Continue running

    def start(self):
        """Start the passive/active voice listening system"""
        if not HAS_SPEECH_REC:
            logger.error("❌ speech_recognition not available - cannot start")
            return

        self.is_running = True
        self.mode = ListeningMode.PASSIVE

        logger.info("=" * 60)
        logger.info("🎤 PASSIVE/ACTIVE VOICE LISTENING SYSTEM")
        logger.info("=" * 60)
        logger.info("")
        logger.info("PASSIVE MODE: Always listening for trigger word")
        logger.info(f"   Trigger words: {', '.join(self.trigger_words)}")
        logger.info("   All other speech is ignored")
        logger.info("")
        logger.info("ACTIVE MODE: Activated after trigger word")
        logger.info("   Transcribes all speech to Cursor IDE")
        logger.info("   Voice editing commands available:")
        logger.info("     - 'Scratch that' → Delete last phrase")
        logger.info("     - 'Change [word] to [word]' → Replace word")
        logger.info("     - 'Delete [word]' → Remove word")
        logger.info("     - 'Add [text]' → Insert text")
        logger.info("     - 'Clear all' → Clear transcription")
        logger.info("     - 'Send it' → Send message")
        logger.info("     - 'Stop listening' → Return to passive mode")
        logger.info("")
        logger.info("Press Ctrl+C to exit")
        logger.info("=" * 60)
        logger.info("")

        try:
            while self.is_running:
                if self.mode == ListeningMode.PAUSED:
                    time.sleep(0.5)
                    continue

                self._listen_once()
                time.sleep(0.1)  # Small delay between listens

        except KeyboardInterrupt:
            logger.info("\n👋 Shutting down voice listening system...")
            self.stop()

    def stop(self):
        """Stop the voice listening system"""
        self.is_running = False
        self.mode = ListeningMode.PASSIVE
        logger.info("🔇 Voice listening system stopped")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Passive/Active Voice Listening System")
    parser.add_argument("--trigger-words", nargs="+", default=["hey jarvis", "jarvis"],
                       help="Trigger words for passive mode (default: 'hey jarvis', 'jarvis')")
    parser.add_argument("--wake-word", default="hey jarvis",
                       help="Primary wake word (default: 'hey jarvis')")

    args = parser.parse_args()

    system = PassiveActiveVoiceSystem(
        trigger_words=args.trigger_words,
        wake_word=args.wake_word
    )

    system.start()


if __name__ == "__main__":


    main()