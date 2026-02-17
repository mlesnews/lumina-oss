#!/usr/bin/env python3
"""
LUMINA Babelfish - Real-Time Japanese Translation System

Inspired by Hitchhiker's Guide to the Galaxy's Babelfish.
Translates Japanese audio to English in real-time.

"Nothing travels faster than the speed of light with the possible exception
of bad news, which obeys its own special laws." - Douglas Adams

But translations? We can try.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
import json
import threading
import queue
import time
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LuminaBabelfish")

try:
    from lumina_always_marvin_jarvis import always_assess
except ImportError:
    logger.warning("Could not import lumina_always_marvin_jarvis")
    always_assess = None


@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class TranslationResult:
    """Result of a translation"""
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    processing_time_ms: float = 0.0


@dataclass
class BabelfishConfig:
    """Configuration for Babelfish"""
    source_language: str = "ja"  # Japanese
    target_language: str = "en"  # English
    audio_source: str = "system"  # "system" or "microphone"
    chunk_duration_seconds: float = 3.0  # Process audio in chunks
    min_confidence: float = 0.5  # Minimum confidence for translation
    real_time_display: bool = True
    save_translations: bool = True
    display_format: str = "overlay"  # "overlay", "console", "file"


class LuminaBabelfish:
    """
    LUMINA Babelfish - Real-Time Japanese Translation

    Like the Babelfish from Hitchhiker's Guide, but for anime.
    """

    def __init__(self, project_root: Optional[Path] = None, config: Optional[BabelfishConfig] = None):
        self.project_root = project_root or Path(".").resolve()
        self.config = config or BabelfishConfig()
        self.logger = get_logger("LuminaBabelfish")

        self.data_dir = self.project_root / "data" / "babelfish"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Translation queue
        self.translation_queue = queue.Queue()
        self.is_running = False
        self.translation_thread = None

        # Translation history
        self.translation_history: List[TranslationResult] = []

        # Initialize components
        self.speech_recognizer = None
        self.translator = None

        self.logger.info("🐟 LUMINA Babelfish initialized")
        self.logger.info(f"   Source: {self.config.source_language} → Target: {self.config.target_language}")
        self.logger.info(f"   Audio Source: {self.config.audio_source}")

        # Get @MARVIN and JARVIS assessment
        self._get_initial_assessment()

    def _get_initial_assessment(self):
        """Get @MARVIN and JARVIS assessment of this system"""
        if always_assess:
            assessment = always_assess(
                "Can we build a real-time Japanese-to-English translation system "
                "that works like the Babelfish from Hitchhiker's Guide?"
            )
            self.logger.info("🤖 @MARVIN & JARVIS Assessment:")
            if hasattr(assessment, 'marvin_perspective'):
                self.logger.info(f"   @MARVIN: {assessment.marvin_perspective[:200]}...")
            if hasattr(assessment, 'jarvis_perspective'):
                self.logger.info(f"   JARVIS: {assessment.jarvis_perspective[:200]}...")

    def _initialize_speech_recognition(self) -> bool:
        """Initialize speech recognition"""
        try:
            import speech_recognition as sr
            self.speech_recognizer = sr.Recognizer()
            self.logger.info("✅ Speech recognition initialized")
            return True
        except ImportError:
            self.logger.warning("❌ speech_recognition not installed. Install: pip install SpeechRecognition")
            return False
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize speech recognition: {e}")
            return False

    def _initialize_translator(self) -> bool:
        """Initialize translation service"""
        try:
            # Try deep-translator first (better, free)
            from deep_translator import GoogleTranslator
            self.translator = GoogleTranslator(source=self.config.source_language, target=self.config.target_language)
            self.logger.info("✅ Translation service initialized (deep-translator)")
            return True
        except ImportError:
            try:
                # Fallback to googletrans
                from googletrans import Translator
                self.translator = Translator()
                self.logger.info("✅ Translation service initialized (googletrans)")
                return True
            except ImportError:
                self.logger.warning("❌ No translation library found. Install: pip install deep-translator OR pip install googletrans==4.0.0rc1")
                return False
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize translator: {e}")
            return False

    def _translate_text(self, text: str) -> Optional[str]:
        """Translate text from source to target language"""
        if not self.translator:
            if not self._initialize_translator():
                return None

        try:
            start_time = time.time()

            # Use deep-translator if available
            if hasattr(self.translator, 'translate'):
                translated = self.translator.translate(text)
            else:
                # Use googletrans
                result = self.translator.translate(text, src=self.config.source_language, dest=self.config.target_language)
                translated = result.text

            processing_time = (time.time() - start_time) * 1000  # ms

            self.logger.debug(f"Translated: '{text[:50]}...' → '{translated[:50]}...' ({processing_time:.1f}ms)")
            return translated

        except Exception as e:
            self.logger.error(f"Translation error: {e}")
            return None

    def _recognize_speech(self, audio_data) -> Optional[str]:
        """Recognize speech from audio data"""
        if not self.speech_recognizer:
            if not self._initialize_speech_recognition():
                return None

        try:
            import speech_recognition as sr

            # Recognize Japanese
            text = self.speech_recognizer.recognize_google(audio_data, language="ja-JP")
            return text
        except sr.UnknownValueError:
            self.logger.debug("Could not understand audio")
            return None
        except sr.RequestError as e:
            self.logger.error(f"Speech recognition error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Speech recognition error: {e}")
            return None

    def _capture_audio_chunk(self) -> Optional[Any]:
        """Capture a chunk of audio"""
        try:
            import speech_recognition as sr
            import pyaudio

            # Initialize audio
            audio = pyaudio.PyAudio()

            # Open stream
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=1024
            )

            # Read chunk
            frames = []
            chunk_duration = self.config.chunk_duration_seconds
            chunk_size = int(44100 * chunk_duration)

            for _ in range(0, chunk_size, 1024):
                data = stream.read(1024)
                frames.append(data)

            # Convert to AudioData
            audio_data = sr.AudioData(b''.join(frames), 44100, 2)

            stream.stop_stream()
            stream.close()
            audio.terminate()

            return audio_data

        except ImportError:
            self.logger.warning("❌ pyaudio not installed. Install: pip install pyaudio")
            return None
        except Exception as e:
            self.logger.error(f"Audio capture error: {e}")
            return None

    def _process_translation_loop(self):
        """Main translation processing loop"""
        self.logger.info("🐟 Babelfish translation loop started")

        while self.is_running:
            try:
                # Capture audio chunk
                audio_data = self._capture_audio_chunk()
                if not audio_data:
                    time.sleep(0.1)
                    continue

                # Recognize speech
                original_text = self._recognize_speech(audio_data)
                if not original_text:
                    continue

                # Translate
                translated_text = self._translate_text(original_text)
                if not translated_text:
                    continue

                # Create result
                result = TranslationResult(
                    original_text=original_text,
                    translated_text=translated_text,
                    source_language=self.config.source_language,
                    target_language=self.config.target_language,
                    confidence=0.8,  # TODO: Get actual confidence  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
                    processing_time_ms=0.0  # TODO: Calculate actual time  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
                )

                # Add to history
                self.translation_history.append(result)

                # Display
                if self.config.real_time_display:
                    self._display_translation(result)

                # Save if configured
                if self.config.save_translations:
                    self._save_translation(result)

            except Exception as e:
                self.logger.error(f"Translation loop error: {e}")
                time.sleep(0.1)

    def _display_translation(self, result: TranslationResult):
        """Display translation in real-time"""
        if self.config.display_format == "console":
            print(f"\n[{result.timestamp}]")
            print(f"🇯🇵 {result.original_text}")
            print(f"🇺🇸 {result.translated_text}")
            print("-" * 80)
        elif self.config.display_format == "overlay":
            # TODO: Implement overlay display (requires GUI library)  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
            print(f"🇯🇵 → 🇺🇸: {result.translated_text}")
        else:
            print(f"{result.translated_text}")

    def _save_translation(self, result: TranslationResult):
        """Save translation to file"""
        try:
            translation_file = self.data_dir / f"translations_{datetime.now().strftime('%Y%m%d')}.jsonl"

            with open(translation_file, 'a', encoding='utf-8') as f:
                json.dump({
                    "original": result.original_text,
                    "translated": result.translated_text,
                    "timestamp": result.timestamp,
                    "confidence": result.confidence,
                    "processing_time_ms": result.processing_time_ms
                }, f, ensure_ascii=False)
                f.write('\n')

        except Exception as e:
            self.logger.error(f"Failed to save translation: {e}")

    def start(self):
        """Start real-time translation"""
        if self.is_running:
            self.logger.warning("🐟 Babelfish is already running")
            return

        self.logger.info("🐟 Starting LUMINA Babelfish...")

        # Initialize components
        if not self._initialize_speech_recognition():
            self.logger.error("❌ Cannot start: Speech recognition not available")
            return False

        if not self._initialize_translator():
            self.logger.error("❌ Cannot start: Translation service not available")
            return False

        # Start translation thread
        self.is_running = True
        self.translation_thread = threading.Thread(target=self._process_translation_loop, daemon=True)
        self.translation_thread.start()

        self.logger.info("✅ LUMINA Babelfish is now listening and translating...")
        self.logger.info("   Press Ctrl+C to stop")

        return True

    def stop(self):
        """Stop real-time translation"""
        if not self.is_running:
            return

        self.logger.info("🐟 Stopping LUMINA Babelfish...")
        self.is_running = False

        if self.translation_thread:
            self.translation_thread.join(timeout=5.0)

        self.logger.info("✅ LUMINA Babelfish stopped")

    def translate_text(self, text: str) -> Optional[TranslationResult]:
        """Translate a single text string"""
        translated = self._translate_text(text)
        if not translated:
            return None

        return TranslationResult(
            original_text=text,
            translated_text=translated,
            source_language=self.config.source_language,
            target_language=self.config.target_language,
            confidence=1.0
        )

    def get_translation_history(self) -> List[TranslationResult]:
        """Get translation history"""
        return self.translation_history.copy()

    def save_session(self, session_name: Optional[str] = None):
        try:
            """Save current translation session"""
            if not session_name:
                session_name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            session_file = self.data_dir / f"{session_name}.json"

            session_data = {
                "session_name": session_name,
                "timestamp": datetime.now().isoformat(),
                "config": {
                    "source_language": self.config.source_language,
                    "target_language": self.config.target_language,
                    "audio_source": self.config.audio_source
                },
                "translations": [
                    {
                        "original": t.original_text,
                        "translated": t.translated_text,
                        "timestamp": t.timestamp,
                        "confidence": t.confidence
                    }
                    for t in self.translation_history
                ]
            }

            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"📁 Session saved: {session_file}")
            return session_file


        except Exception as e:
            self.logger.error(f"Error in save_session: {e}", exc_info=True)
            raise
def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="LUMINA Babelfish - Real-Time Japanese Translation")
    parser.add_argument("--source", default="ja", help="Source language code (default: ja)")
    parser.add_argument("--target", default="en", help="Target language code (default: en)")
    parser.add_argument("--audio", choices=["system", "microphone"], default="microphone", help="Audio source")
    parser.add_argument("--text", help="Translate a single text string instead of real-time")
    parser.add_argument("--display", choices=["console", "overlay", "file"], default="console", help="Display format")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("🐟 LUMINA BABELFISH - Real-Time Translation System")
    print("="*80 + "\n")
    print("Inspired by Hitchhiker's Guide to the Galaxy")
    print("'The Babelfish is small, yellow, leech-like, and probably the oddest")
    print("thing in the Universe.' - Douglas Adams\n")

    config = BabelfishConfig(
        source_language=args.source,
        target_language=args.target,
        audio_source=args.audio,
        display_format=args.display
    )

    babelfish = LuminaBabelfish(config=config)

    if args.text:
        # Translate single text
        print(f"\n🇯🇵 Original: {args.text}")
        result = babelfish.translate_text(args.text)
        if result:
            print(f"🇺🇸 Translated: {result.translated_text}\n")
        else:
            print("❌ Translation failed\n")
    else:
        # Real-time translation
        try:
            if babelfish.start():
                # Keep running until interrupted
                while True:
                    time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🐟 Stopping Babelfish...")
            babelfish.stop()
            babelfish.save_session()
            print("✅ Done\n")


if __name__ == "__main__":



    main()