#!/usr/bin/env python3
"""
JARVIS Voice Interface - Hands-Free, Fully Accessible

Voice interface for JARVIS - works when Lumina/JARVIS are active 100%
Designed for blind users - full voice control, no visual requirements

"Speak directly to JARVIS by voice, as if I was blind"
"""

import sys
import json
import threading
import queue
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Callable
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

logger = get_logger("JARVISVoiceInterface")

# Voice recognition
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    logger.warning("speech_recognition not available - install: pip install SpeechRecognition")

# Text-to-speech
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    try:
        from gtts import gTTS
        import playsound
        TTS_AVAILABLE = True
        TTS_METHOD = "gtts"
    except ImportError:
        TTS_AVAILABLE = False
        logger.warning("TTS not available - install: pip install pyttsx3 or gtts playsound")

# Wake word detection
try:
    import pvporcupine
    WAKE_WORD_AVAILABLE = True
except ImportError:
    WAKE_WORD_AVAILABLE = False
    logger.info("Wake word detection not available (optional)")


# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class JARVISVoiceInterface:
    """
    JARVIS Voice Interface - Hands-Free, Fully Accessible

    Works when Lumina/JARVIS are active 100%
    Designed for blind users - full voice control
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize voice interface"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JARVISVoiceInterface")

        # Voice components
        self.recognizer = None
        self.tts_engine = None
        self.is_listening = False
        self.is_speaking = False

        # Command queue
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()

        # JARVIS integration
        self.jarvis_interface = None
        self.lumina_active = False

        # Initialize voice components
        self._initialize_voice()

        # Check Lumina/JARVIS status
        self._check_lumina_jarvis_status()

        self.logger.info("🎤 JARVIS Voice Interface initialized")
        self.logger.info("   Hands-free operation enabled")
        self.logger.info("   Fully accessible for blind users")

    def _initialize_voice(self):
        """Initialize voice recognition and TTS"""
        # Speech recognition
        if SPEECH_RECOGNITION_AVAILABLE:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.logger.info("  ✅ Speech recognition ready")
        else:
            self.logger.warning("  ⚠️  Speech recognition not available")

        # Text-to-speech
        if TTS_AVAILABLE:
            if 'TTS_METHOD' in globals() and TTS_METHOD == "gtts":
                self.tts_method = "gtts"
            else:
                try:
                    self.tts_engine = pyttsx3.init()
                    # Configure TTS for accessibility
                    self.tts_engine.setProperty('rate', 150)  # Speaking rate
                    self.tts_engine.setProperty('volume', 1.0)  # Volume
                    # Try to set a clear voice
                    voices = self.tts_engine.getProperty('voices')
                    if voices:
                        self.tts_engine.setProperty('voice', voices[0].id)
                    self.tts_method = "pyttsx3"
                except:
                    self.tts_method = "gtts"
            self.logger.info(f"  ✅ Text-to-speech ready ({self.tts_method})")
        else:
            self.logger.warning("  ⚠️  Text-to-speech not available")

    def _check_lumina_jarvis_status(self):
        """Check if Lumina/JARVIS are active"""
        try:
            from jarvis_unified_interface import JARVISUnifiedInterface
            self.jarvis_interface = JARVISUnifiedInterface()
            self.lumina_active = True
            self.logger.info("  ✅ Lumina/JARVIS active - voice interface ready")
        except Exception as e:
            self.logger.debug(f"  ⚠️  Lumina/JARVIS check: {e}")
            self.lumina_active = False

    def speak(self, text: str, interrupt: bool = False):
        """Speak text (accessible TTS)"""
        if not TTS_AVAILABLE:
            print(f"JARVIS: {text}")  # Fallback to text
            return

        if interrupt and self.is_speaking:
            # Stop current speech
            if self.tts_method == "pyttsx3" and self.tts_engine:
                self.tts_engine.stop()

        self.is_speaking = True

        try:
            if self.tts_method == "pyttsx3" and self.tts_engine:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            elif self.tts_method == "gtts":
                from gtts import gTTS
                import playsound
                import tempfile
                tts = gTTS(text=text, lang='en')
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                    tts.save(tmp.name)
                    playsound.playsound(tmp.name)
                    Path(tmp.name).unlink()
        except Exception as e:
            self.logger.error(f"TTS error: {e}")
            print(f"JARVIS: {text}")  # Fallback

        self.is_speaking = False

    def listen(self, timeout: Optional[float] = None) -> Optional[str]:
        """Listen for voice input"""
        if not SPEECH_RECOGNITION_AVAILABLE or not self.recognizer:
            return None

        try:
            with sr.Microphone() as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                # Listen for audio
                self.logger.info("🎤 Listening...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)

            # Recognize speech
            try:
                text = self.recognizer.recognize_google(audio)
                self.logger.info(f"  Heard: {text}")
                return text
            except sr.UnknownValueError:
                self.logger.debug("  Could not understand audio")
                return None
            except sr.RequestError as e:
                self.logger.error(f"  Speech recognition error: {e}")
                return None
        except Exception as e:
            self.logger.error(f"  Listening error: {e}")
            return None

    def process_voice_command(self, command: str) -> str:
        """Process voice command and get response"""
        if not self.lumina_active or not self.jarvis_interface:
            return "Lumina and JARVIS are not active. Please activate them first."

        # Delegate to JARVIS
        result = self.jarvis_interface.delegate(command)

        if result.get('success'):
            response = f"Done. {result.get('agent_name', 'JARVIS')} handled that."
            if 'result' in result:
                # Include result details if available
                response += f" {str(result['result'])}"
        else:
            response = f"Sorry, I couldn't do that. {result.get('error', 'Unknown error')}"

        return response

    def voice_loop(self):
        """Main voice interaction loop - hands-free"""
        self.logger.info("🎤 Starting voice interface loop")
        self.speak("JARVIS voice interface activated. I'm listening.")

        while self.is_listening:
            try:
                # Listen for command
                command = self.listen(timeout=5)

                if command:
                    # Process command
                    self.speak("Processing...")
                    response = self.process_voice_command(command)
                    self.speak(response)
                else:
                    # No command heard, continue listening
                    pass
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"Voice loop error: {e}")
                self.speak("I encountered an error. Please try again.")

    def start(self):
        """Start voice interface"""
        if not self.lumina_active:
            self.speak("Lumina and JARVIS are not active. Please activate them first.")
            return False

        self.is_listening = True

        # Start voice loop in thread
        voice_thread = threading.Thread(target=self.voice_loop, daemon=True)
        voice_thread.start()

        self.logger.info("✅ Voice interface started - hands-free operation active")
        self.speak("JARVIS voice interface started. I'm ready for your commands.")

        return True

    def stop(self):
        """Stop voice interface"""
        self.is_listening = False
        self.speak("Voice interface stopped.")
        self.logger.info("Voice interface stopped")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Voice Interface")
    parser.add_argument("--start", action="store_true", help="Start voice interface")
    parser.add_argument("--test", action="store_true", help="Test voice recognition")
    parser.add_argument("--speak", type=str, help="Test TTS with text")

    args = parser.parse_args()

    interface = JARVISVoiceInterface()

    if args.speak:
        interface.speak(args.speak)
    elif args.test:
        print("🎤 Testing voice recognition...")
        print("Say something...")
        text = interface.listen()
        if text:
            print(f"  Heard: {text}")
        else:
            print("  Could not understand")
    elif args.start:
        print("🎤 Starting JARVIS Voice Interface...")
        print("   Hands-free operation")
        print("   Fully accessible for blind users")
        print("\nPress Ctrl+C to stop\n")
        interface.start()
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            interface.stop()
    else:
        parser.print_help()

