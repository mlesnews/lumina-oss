#!/usr/bin/env python3
"""
Voice Conversational Features - Interrupt & Backchanneling

Features inspired by OpenAI Voice AI UI and Microsoft Copilot:
- Interrupt capability (stop speaking when user speaks)
- Backchanneling (small acknowledgements: "uh-huh", "mm-hmm", "yes", "I see")
- Natural conversation flow
- Real-time voice activity detection

Tags: #VOICE #CONVERSATIONAL #INTERRUPT #BACKCHANNELING #ELEVENLABS @JARVIS @TEAM
"""

import sys
import threading
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("VoiceConversationalFeatures")

# Try speech recognition
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    logger.warning("Speech recognition not available")

# Try ElevenLabs
try:
    from jarvis_elevenlabs_tts import JARVISElevenLabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    try:
        from jarvis_elevenlabs_integration import JARVISElevenLabsTTS
        ELEVENLABS_AVAILABLE = True
        JARVISElevenLabs = JARVISElevenLabsTTS
    except ImportError:
        ELEVENLABS_AVAILABLE = False
        JARVISElevenLabs = None


class BackchannelType(Enum):
    """Types of backchanneling acknowledgements"""
    ACKNOWLEDGE = "acknowledge"  # "uh-huh", "mm-hmm", "yes"
    UNDERSTAND = "understand"  # "I see", "got it", "understood"
    ENCOURAGE = "encourage"  # "go on", "continue", "tell me more"
    AGREE = "agree"  # "exactly", "that's right", "absolutely"


class VoiceConversationalFeatures:
    """
    Voice Conversational Features

    Features inspired by OpenAI Voice AI UI and Microsoft Copilot:
    - Interrupt capability
    - Backchanneling (acknowledgements)
    - Natural conversation flow
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize conversational voice features"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # ElevenLabs for voice output
        self.elevenlabs = None
        if ELEVENLABS_AVAILABLE:
            try:
                self.elevenlabs = JARVISElevenLabs(project_root=project_root)
                logger.info("✅ ElevenLabs initialized for conversational features")
            except Exception as e:
                logger.warning(f"⚠️  ElevenLabs not available: {e}")

        # Speech recognition for interrupt detection
        self.recognizer = None
        if SPEECH_RECOGNITION_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.recognizer.energy_threshold = 300
                self.recognizer.dynamic_energy_threshold = True
                logger.info("✅ Speech recognition initialized for interrupt detection")
            except Exception as e:
                logger.warning(f"⚠️  Speech recognition not available: {e}")

        # Interrupt state
        self.speaking = False
        self.interrupted = False
        self.speak_thread = None
        self.listen_thread = None

        # Backchanneling phrases
        self.backchannel_phrases = {
            BackchannelType.ACKNOWLEDGE: ["uh-huh", "mm-hmm", "yes", "yeah", "okay"],
            BackchannelType.UNDERSTAND: ["I see", "got it", "understood", "I understand"],
            BackchannelType.ENCOURAGE: ["go on", "continue", "tell me more", "I'm listening"],
            BackchannelType.AGREE: ["exactly", "that's right", "absolutely", "precisely"]
        }

        logger.info("✅ Voice Conversational Features initialized")
        logger.info("   Interrupt capability & backchanneling ready")

    def speak_with_interrupt(self, text: str, interrupt_callback: Optional[Callable] = None) -> bool:
        """
        Speak text with interrupt capability

        Can be interrupted if user starts speaking.
        Inspired by OpenAI Voice AI UI and Microsoft Copilot.

        Args:
            text: Text to speak
            interrupt_callback: Callback when interrupted
        """
        if not self.elevenlabs:
            logger.warning("⚠️  ElevenLabs not available - cannot speak")
            return False

        self.speaking = True
        self.interrupted = False

        def speak_thread():
            """Thread for speaking"""
            try:
                # Start listening for interrupts in background
                if self.recognizer and interrupt_callback:
                    listen_thread = threading.Thread(target=self._listen_for_interrupt, args=(interrupt_callback,), daemon=True)
                    listen_thread.start()

                # Speak text
                logger.info(f"🎤 Speaking: {text[:50]}...")
                self.elevenlabs.speak(text, wait=True)

                if self.interrupted:
                    logger.info("   ⚠️  Speech interrupted by user")
                else:
                    logger.info("   ✅ Speech completed")

            except Exception as e:
                logger.error(f"❌ Error speaking: {e}")
            finally:
                self.speaking = False

        self.speak_thread = threading.Thread(target=speak_thread, daemon=True)
        self.speak_thread.start()

        return True

    def _listen_for_interrupt(self, callback: Callable):
        """Listen for user speech to interrupt"""
        if not self.recognizer:
            return

        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)

                while self.speaking and not self.interrupted:
                    try:
                        # Listen for speech (short timeout for responsiveness)
                        audio = self.recognizer.listen(source, timeout=0.5, phrase_time_limit=1.0)

                        # If we got audio, user is speaking - interrupt!
                        if audio:
                            self.interrupted = True
                            logger.info("   🛑 User speech detected - interrupting")
                            if callback:
                                callback()
                            break

                    except sr.WaitTimeoutError:
                        # No speech detected, continue listening
                        continue
                    except Exception as e:
                        logger.debug(f"   Interrupt detection error: {e}")
                        break

        except Exception as e:
            logger.warning(f"⚠️  Interrupt listening error: {e}")

    def backchannel(self, backchannel_type: BackchannelType = BackchannelType.ACKNOWLEDGE) -> bool:
        """
        Provide backchanneling acknowledgement

        Small acknowledgements like "uh-huh", "mm-hmm", "I see"
        Inspired by Microsoft Copilot's natural conversation flow.

        Args:
            backchannel_type: Type of acknowledgement
        """
        if not self.elevenlabs:
            return False

        phrases = self.backchannel_phrases.get(backchannel_type, ["uh-huh"])
        import random
        phrase = random.choice(phrases)

        try:
            # Quick, short acknowledgement
            logger.debug(f"   🎤 Backchannel: {phrase}")
            self.elevenlabs.speak(phrase, wait=False)  # Don't wait - quick acknowledgement
            return True
        except Exception as e:
            logger.debug(f"   Backchannel error: {e}")
            return False

    def acknowledge(self) -> bool:
        """Quick acknowledgement: "uh-huh", "mm-hmm", "yes" """
        return self.backchannel(BackchannelType.ACKNOWLEDGE)

    def understand(self) -> bool:
        """Understanding acknowledgement: "I see", "got it" """
        return self.backchannel(BackchannelType.UNDERSTAND)

    def encourage(self) -> bool:
        """Encouragement: "go on", "continue", "tell me more" """
        return self.backchannel(BackchannelType.ENCOURAGE)

    def agree(self) -> bool:
        """Agreement: "exactly", "that's right", "absolutely" """
        return self.backchannel(BackchannelType.AGREE)

    def stop_speaking(self):
        """Stop current speech (interrupt)"""
        if self.speaking:
            self.interrupted = True
            self.speaking = False
            logger.info("   🛑 Speech stopped")

    def is_speaking(self) -> bool:
        """Check if currently speaking"""
        return self.speaking


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Voice Conversational Features")
    parser.add_argument("--test-interrupt", action="store_true", help="Test interrupt capability")
    parser.add_argument("--test-backchannel", action="store_true", help="Test backchanneling")
    parser.add_argument("--acknowledge", action="store_true", help="Quick acknowledgement")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("🎤 Voice Conversational Features")
    print("   Interrupt & Backchanneling (OpenAI Voice & Copilot Style)")
    print("="*80 + "\n")

    features = VoiceConversationalFeatures()

    if args.test_interrupt:
        print("Testing interrupt capability...")
        print("Start speaking to interrupt JARVIS")
        features.speak_with_interrupt(
            "This is a test of the interrupt capability. You can interrupt me at any time by speaking.",
            interrupt_callback=lambda: print("\n🛑 INTERRUPTED!")
        )
        time.sleep(10)

    elif args.test_backchannel:
        print("Testing backchanneling...")
        features.acknowledge()
        time.sleep(1)
        features.understand()
        time.sleep(1)
        features.encourage()
        time.sleep(1)
        features.agree()
        print("\n✅ Backchanneling test complete")

    elif args.acknowledge:
        features.acknowledge()
        print("✅ Acknowledgement sent")

    else:
        print("Use --test-interrupt, --test-backchannel, or --acknowledge")
        print("="*80 + "\n")
