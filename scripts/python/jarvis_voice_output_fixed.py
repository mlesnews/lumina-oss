#!/usr/bin/env python3
"""
JARVIS Voice Output - FIXED with Fallbacks

Real-world smoke test - fixes voice output issues with multiple fallbacks.
Works NOW, not later.

Fallback chain:
1. ElevenLabs TTS (if configured)
2. Windows SAPI TTS (built-in, always works)
3. Text output (last resort)

Tags: #VOICE #TTS #FIX #SMOKE-TEST #REAL-WORLD @JARVIS @TEAM
"""

import sys
from pathlib import Path
from typing import Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISVoiceOutputFixed")

# Try ElevenLabs first
ELEVENLABS_AVAILABLE = False
JARVISElevenLabs = None
try:
    from jarvis_elevenlabs_integration import JARVISElevenLabsTTS
    JARVISElevenLabs = JARVISElevenLabsTTS
    ELEVENLABS_AVAILABLE = True
except ImportError:
    try:
        from jarvis_elevenlabs_tts import JARVISElevenLabs
        ELEVENLABS_AVAILABLE = True
    except ImportError:
        pass

# Windows SAPI TTS fallback (always works on Windows)
WINDOWS_TTS_AVAILABLE = False
WINDOWS_TTS_TYPE = None
try:
    import win32com.client
    WINDOWS_TTS_AVAILABLE = True
    WINDOWS_TTS_TYPE = "win32com"
except ImportError:
    try:
        import pyttsx3
        WINDOWS_TTS_AVAILABLE = True
        WINDOWS_TTS_TYPE = "pyttsx3"
    except ImportError:
        pass


class JARVISVoiceOutputFixed:
    """
    JARVIS Voice Output - FIXED

    Real-world smoke test - works NOW with fallbacks
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize voice output with fallbacks"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Try ElevenLabs
        self.elevenlabs = None
        if ELEVENLABS_AVAILABLE:
            try:
                self.elevenlabs = JARVISElevenLabs(project_root=project_root)
                if self.elevenlabs and hasattr(self.elevenlabs, 'api_key') and self.elevenlabs.api_key:
                    logger.info("✅ ElevenLabs TTS available")
                else:
                    logger.info("⚠️  ElevenLabs available but API key not configured")
                    self.elevenlabs = None
            except Exception as e:
                logger.warning(f"⚠️  ElevenLabs initialization failed: {e}")
                self.elevenlabs = None

        # Windows SAPI TTS (fallback)
        self.windows_tts = None
        if WINDOWS_TTS_AVAILABLE:
            try:
                if WINDOWS_TTS_TYPE == "win32com":
                    import win32com.client
                    self.windows_tts = win32com.client.Dispatch("SAPI.SpVoice")
                    logger.info("✅ Windows SAPI TTS available")
                elif WINDOWS_TTS_TYPE == "pyttsx3":
                    import pyttsx3
                    self.windows_tts = pyttsx3.init()
                    logger.info("✅ Windows TTS (pyttsx3) available")
            except Exception as e:
                logger.warning(f"⚠️  Windows TTS initialization failed: {e}")
                self.windows_tts = None

        # Determine active voice method
        if self.elevenlabs:
            self.active_method = "elevenlabs"
            logger.info("🎤 Voice: ElevenLabs TTS")
        elif self.windows_tts:
            self.active_method = "windows_tts"
            logger.info("🎤 Voice: Windows SAPI TTS (fallback)")
        else:
            self.active_method = "text_only"
            logger.warning("⚠️  Voice: Text-only mode (no TTS available)")

    def speak(self, text: str, interrupt: bool = False) -> bool:
        """
        Speak text aloud - REAL WORLD FIX

        Returns True if spoken, False if text-only
        """
        if not text or not text.strip():
            return False

        try:
            # Try ElevenLabs first
            if self.elevenlabs and self.active_method == "elevenlabs":
                try:
                    if hasattr(self.elevenlabs, 'speak'):
                        self.elevenlabs.speak(text)
                        return True
                    elif hasattr(self.elevenlabs, 'generate_and_play'):
                        self.elevenlabs.generate_and_play(text)
                        return True
                except Exception as e:
                    logger.warning(f"⚠️  ElevenLabs speak failed: {e}, falling back to Windows TTS")
                    self.active_method = "windows_tts"

            # Fallback to Windows SAPI TTS
            if self.windows_tts and self.active_method == "windows_tts":
                try:
                    if hasattr(self.windows_tts, 'Speak'):
                        # Windows SAPI
                        if interrupt:
                            self.windows_tts.Speak("", 2)  # Stop current speech
                        self.windows_tts.Speak(text, 0)  # Async
                        return True
                    elif hasattr(self.windows_tts, 'say'):
                        # pyttsx3
                        if interrupt:
                            self.windows_tts.stop()
                        self.windows_tts.say(text)
                        self.windows_tts.runAndWait()
                        return True
                except Exception as e:
                    logger.warning(f"⚠️  Windows TTS speak failed: {e}")

            # Last resort: print for manual reading
            print(f"\n[JARVIS SPEAKS - READ ALOUD]: {text}\n")
            return False

        except Exception as e:
            logger.error(f"❌ Error speaking: {e}")
            print(f"\n[JARVIS SPEAKS - READ ALOUD]: {text}\n")
            return False

    def speak_with_pause(self, text: str, pause_seconds: float = 0.5):
        """Speak text with pause after"""
        self.speak(text)
        if pause_seconds > 0:
            import time
            time.sleep(pause_seconds)


def speak_text_fixed(text: str, project_root: Optional[Path] = None) -> bool:
    """
    Quick function to speak text - FIXED version

    Returns True if spoken, False if text-only
    """
    voice = JARVISVoiceOutputFixed(project_root=project_root)
    return voice.speak(text)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Voice Output - FIXED")
    parser.add_argument("--text", type=str, help="Text to speak")
    parser.add_argument("--test", action="store_true", help="Test all voice methods")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("🎤 JARVIS Voice Output - FIXED")
    print("   Real-world smoke test")
    print("="*80 + "\n")

    voice = JARVISVoiceOutputFixed()

    if args.test:
        test_text = "Hello, this is a test of JARVIS voice output. Can you hear me?"
        print(f"Testing voice output: {voice.active_method}\n")
        success = voice.speak(test_text)
        print(f"\nResult: {'✅ Spoken' if success else '⚠️  Text-only (read aloud)'}\n")

    elif args.text:
        success = voice.speak(args.text)
        print(f"\nResult: {'✅ Spoken' if success else '⚠️  Text-only (read aloud)'}\n")

    else:
        print(f"Active voice method: {voice.active_method}\n")
        print("Use --text 'your text' to speak, or --test to test\n")
