"""
JARVIS Voice Trigger System
============================

Listens for voice commands and triggers actions:
- "Jarvis, do it" → Sends the message (Enter key)
- "Scratch that" → Deletes last utterance (Ctrl+Z or backspace)
- "Clear all" → Clears the input (Ctrl+A, Delete)
- "New line" → Inserts newline
- "Go back" → Backspace

Inspired by Dragon NaturallySpeaking command set.

INTEGRATION:
    This integrates with cursor_auto_send_monitor.py to:
    - CANCEL pending auto-sends when correction commands are spoken
    - OVERRIDE the timer with "Jarvis, do it" for immediate send

Requirements:
    pip install SpeechRecognition pyaudio pyautogui

Usage:
    python jarvis_voice_trigger.py
"""

import speech_recognition as sr
import pyautogui
import re
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable, Dict

# Integration with auto-send monitor
try:
    from cursor_auto_send_monitor import (
        stop_auto_send,
        resume_listening,
        mark_activity
    )
    HAS_AUTO_SEND = True
except ImportError:
    HAS_AUTO_SEND = False
    def stop_auto_send(): pass
    def resume_listening(): pass
    def mark_activity(): pass

# Configuration
CONFIG = {
    "trigger_phrases": {
        # Send/Execute commands
        "jarvis do it": "send",
        "jarvis send": "send",
        "do it": "send",
        "send it": "send",
        "execute": "send",

        # Correction commands (Dragon-style)
        "scratch that": "undo",
        "undo that": "undo",
        "delete that": "undo",

        "clear all": "clear",
        "clear everything": "clear",
        "start over": "clear",

        "new line": "newline",
        "next line": "newline",

        "go back": "backspace",
        "back space": "backspace",
        "delete": "backspace",

        # Voice control
        "stop listening": "pause",
        "pause": "pause",
        "resume": "resume",
        "wake up": "resume",
    },

    "microphone_index": None,  # None = default mic
    "energy_threshold": 4000,  # HIGHER = Only capture loud/close speech (prevents background bleed)
    "dynamic_energy_threshold": True,  # Adjust based on ambient noise
    "pause_threshold": 0.8,    # Seconds of silence before phrase end
    "phrase_time_limit": 10,   # Max seconds per phrase
    "adjust_for_ambient_noise": True,  # Calibrate to room noise
    "ambient_noise_duration": 1.0,  # Seconds to sample ambient noise
}


class JarvisVoiceTrigger:
    """Voice command system for JARVIS."""

    def __init__(self, config: dict = None):
        self.config = config or CONFIG
        self.recognizer = sr.Recognizer()
        self.is_listening = True
        self.is_paused = False

        # Configure recognizer with better filtering
        self.recognizer.energy_threshold = self.config["energy_threshold"]
        self.recognizer.pause_threshold = self.config["pause_threshold"]
        self.recognizer.dynamic_energy_threshold = self.config.get("dynamic_energy_threshold", True)

        # Calibrate to ambient noise (reduces background voice pickup)
        if self.config.get("adjust_for_ambient_noise", True):
            print("🎤 Calibrating microphone to ambient noise...")
            try:
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(
                        source,
                        duration=self.config.get("ambient_noise_duration", 1.0)
                    )
                print(f"✅ Calibrated. Energy threshold: {self.recognizer.energy_threshold:.0f}")
            except Exception as e:
                print(f"⚠️  Could not calibrate: {e}")

        # Command handlers
        self.handlers: Dict[str, Callable] = {
            "send": self._handle_send,
            "undo": self._handle_undo,
            "clear": self._handle_clear,
            "newline": self._handle_newline,
            "backspace": self._handle_backspace,
            "pause": self._handle_pause,
            "resume": self._handle_resume,
        }

        # Log file
        self.log_path = Path(__file__).parent.parent.parent / "data" / "voice_commands" / "command_log.jsonl"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def _log_command(self, text: str, command: Optional[str], action_taken: str):
        try:
            """Log voice command to file."""
            entry = {
                "timestamp": datetime.now().isoformat(),
                "recognized_text": text,
                "matched_command": command,
                "action": action_taken
            }
            with open(self.log_path, "a") as f:
                f.write(json.dumps(entry) + "\n")

        except Exception as e:
            self.logger.error(f"Error in _log_command: {e}", exc_info=True)
            raise
    def _handle_send(self):
        """Send the message (press Enter)."""
        print("🚀 JARVIS: Sending message...")
        # Stop any pending auto-send timers - we're sending NOW
        stop_auto_send()
        pyautogui.press("enter")
        # Resume listening after send
        time.sleep(0.1)
        resume_listening()
        return "Message sent"

    def _handle_undo(self):
        """Undo last action (Ctrl+Z)."""
        print("↩️ JARVIS: Undoing... (canceling auto-send)")
        # CRITICAL: Cancel pending auto-send when making corrections
        stop_auto_send()
        pyautogui.hotkey("ctrl", "z")
        # Resume listening - user is still editing
        resume_listening()
        mark_activity()
        return "Undo executed"

    def _handle_clear(self):
        """Clear all text (Ctrl+A, Delete)."""
        print("🗑️ JARVIS: Clearing all... (canceling auto-send)")
        # Cancel pending auto-send
        stop_auto_send()
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.05)
        pyautogui.press("delete")
        # Resume listening
        resume_listening()
        return "Cleared"

    def _handle_newline(self):
        """Insert new line (Shift+Enter for soft break)."""
        print("↵ JARVIS: New line...")
        # Mark activity - user is still editing
        mark_activity()
        pyautogui.hotkey("shift", "enter")
        return "New line inserted"

    def _handle_backspace(self):
        """Delete last character."""
        print("⌫ JARVIS: Backspace... (canceling auto-send)")
        # Cancel pending auto-send when making corrections
        stop_auto_send()
        pyautogui.press("backspace")
        # Resume listening
        resume_listening()
        mark_activity()
        return "Backspace"

    def _handle_pause(self):
        """Pause listening."""
        print("⏸️ JARVIS: Pausing voice recognition...")
        self.is_paused = True
        return "Paused"

    def _handle_resume(self):
        """Resume listening."""
        print("▶️ JARVIS: Resuming voice recognition...")
        self.is_paused = False
        return "Resumed"

    def _find_command(self, text: str) -> Optional[str]:
        """Find if text contains a trigger phrase."""
        text_lower = text.lower().strip()

        # Check for exact or partial matches
        for phrase, command in self.config["trigger_phrases"].items():
            if phrase in text_lower:
                return command

        return None

    def _process_text(self, text: str) -> str:
        """Process recognized text, stripping command phrases."""
        text_lower = text.lower()

        # Remove trigger phrases from text
        for phrase in self.config["trigger_phrases"].keys():
            text_lower = text_lower.replace(phrase, "")

        # Clean up
        text_clean = re.sub(r'\s+', ' ', text_lower).strip()
        return text_clean

    def listen_once(self) -> Optional[str]:
        """Listen for a single phrase and process it."""
        try:
            with sr.Microphone(device_index=self.config["microphone_index"]) as source:
                # Re-calibrate if dynamic threshold is enabled (adapts to changing noise)
                if self.config.get("dynamic_energy_threshold", True):
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                print("🎤 Listening... (filtering background voices)")
                audio = self.recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=self.config["phrase_time_limit"]
                )

                # Check audio energy level - reject if too quiet (likely background)
                if hasattr(audio, 'get_raw_data'):
                    import audioop
                    raw_audio = audio.get_raw_data()
                    if raw_audio:
                        rms = audioop.rms(raw_audio, 2)  # Root mean square (volume)
                        min_energy = self.config["energy_threshold"] * 0.5
                        if rms < min_energy:
                            print(f"🔇 Rejected quiet audio (RMS: {rms:.0f} < {min_energy:.0f})")
                            return None

            # Recognize speech
            text = self.recognizer.recognize_google(audio)
            print(f"📝 Heard: '{text}'")

            # Find command
            command = self._find_command(text)

            if command:
                # Execute command
                handler = self.handlers.get(command)
                if handler:
                    result = handler()
                    self._log_command(text, command, result)
                    return result
            else:
                # No command - this was just dictation
                # The text should already be in the input field via Windows speech
                self._log_command(text, None, "dictation")
                return None

        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            print("❓ Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            return None

    def run(self):
        """Main listening loop."""
        print("=" * 60)
        print("🤖 JARVIS Voice Trigger System")
        print("=" * 60)
        print()
        print("Commands:")
        print("  'Jarvis, do it' or 'Send it'  → Send message")
        print("  'Scratch that' or 'Undo'      → Undo last")
        print("  'Clear all'                   → Clear input")
        print("  'New line'                    → Insert line break")
        print("  'Stop listening'              → Pause")
        print("  'Wake up'                     → Resume")
        print()
        print("Press Ctrl+C to exit")
        print("=" * 60)
        print()

        try:
            while self.is_listening:
                if self.is_paused:
                    time.sleep(0.5)
                    continue

                self.listen_once()

        except KeyboardInterrupt:
            print("\n👋 JARVIS signing off...")


def check_dependencies():
    """Check if required packages are installed."""
    missing = []

    try:
        import speech_recognition
    except ImportError:
        missing.append("SpeechRecognition")

    try:
        import pyaudio
    except ImportError:
        missing.append("pyaudio")

    try:
        import pyautogui
    except ImportError:
        missing.append("pyautogui")

    if missing:
        print("❌ Missing dependencies:")
        print(f"   pip install {' '.join(missing)}")
        return False

    return True


def main():
    """Entry point."""
    if not check_dependencies():
        return

    jarvis = JarvisVoiceTrigger()
    jarvis.run()


if __name__ == "__main__":


    main()