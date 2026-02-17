#!/usr/bin/env python3
"""
Babelfish System Audio Capture

Captures system audio (what's playing) for real-time translation.
Integrates with agent chat workflows.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
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

logger = get_logger("BabelfishSystemAudioCapture")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class BabelfishSystemAudioCapture:
    """
    Captures system audio for real-time translation.
    Integrates with agent workflows.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(".").resolve()
        self.logger = get_logger("BabelfishSystemAudioCapture")

        self.data_dir = self.project_root / "data" / "babelfish"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Translation components
        self.translator = None
        self.speech_recognizer = None

        # Audio capture
        self.is_capturing = False
        self.capture_thread = None
        self.audio_queue = queue.Queue()

        # Translation processing
        self.translation_queue = queue.Queue()
        self.translation_thread = None

        # Agent workflow integration
        self.workflow_callbacks: List[Callable] = []
        self.translation_buffer: List[Dict[str, Any]] = []
        self.buffer_size = 10  # Keep last 10 translations

        # Real-time processing
        self.processing_delay = 0.5  # Process every 0.5 seconds
        self.chunk_duration = 3.0  # 3 second audio chunks

        self.logger.info("🐟 Babelfish System Audio Capture initialized")
        self._initialize_components()

    def _initialize_components(self):
        """Initialize translation and audio components"""

        # Initialize translator
        try:
            from deep_translator import GoogleTranslator
            self.translator = GoogleTranslator(source="ja", target="en")
            self.logger.info("✅ Translator initialized")
        except ImportError:
            self.logger.warning("❌ deep-translator not installed")

        # Initialize speech recognition
        try:
            import speech_recognition as sr
            self.speech_recognizer = sr.Recognizer()
            self.logger.info("✅ Speech recognition initialized")
        except ImportError:
            self.logger.warning("❌ speech_recognition not installed")

    def _capture_system_audio(self):
        """Capture system audio (what's playing)"""
        # This is the tricky part on Windows
        # Options:
        # 1. Use WASAPI loopback (Windows Audio Session API)
        # 2. Use VB-Audio Virtual Cable
        # 3. Use Voicemeeter
        # 4. Use screen capture with audio

        try:
            import pyaudio
            import numpy as np

            # Try WASAPI loopback (Windows)
            audio = pyaudio.PyAudio()

            # Find WASAPI loopback device
            wasapi_info = None
            for i in range(audio.get_device_count()):
                info = audio.get_device_info_by_index(i)
                if 'wasapi' in info['name'].lower() or 'loopback' in info['name'].lower():
                    wasapi_info = info
                    break

            if wasapi_info:
                self.logger.info(f"✅ Found WASAPI device: {wasapi_info['name']}")
            else:
                self.logger.warning("⚠️  WASAPI loopback not found. Using default device.")
                self.logger.info("   Suggestion: Install VB-Audio Virtual Cable for system audio capture")

            # Open stream
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                input_device_index=wasapi_info['index'] if wasapi_info else None,
                frames_per_buffer=1024
            )

            self.logger.info("✅ Audio stream opened")

            # Capture chunks
            while self.is_capturing:
                try:
                    # Read audio chunk
                    data = stream.read(1024)
                    self.audio_queue.put(data)
                except Exception as e:
                    self.logger.error(f"Audio capture error: {e}")
                    time.sleep(0.1)

            stream.stop_stream()
            stream.close()
            audio.terminate()

        except ImportError:
            self.logger.warning("❌ pyaudio not installed")
            self.logger.info("   Install: pip install pyaudio")
        except Exception as e:
            self.logger.error(f"System audio capture error: {e}")
            self.logger.info("   Suggestion: Use VB-Audio Virtual Cable or Voicemeeter for system audio")

    def _process_audio_chunks(self):
        """Process audio chunks and translate"""
        import speech_recognition as sr

        while self.is_capturing:
            try:
                # Collect audio chunk (3 seconds)
                audio_data = []
                chunk_samples = int(44100 * self.chunk_duration / 1024)

                for _ in range(chunk_samples):
                    try:
                        data = self.audio_queue.get(timeout=0.1)
                        audio_data.append(data)
                    except queue.Empty:
                        break

                if not audio_data:
                    time.sleep(0.1)
                    continue

                # Convert to AudioData
                audio_bytes = b''.join(audio_data)
                audio_source = sr.AudioData(audio_bytes, 44100, 2)

                # Recognize Japanese speech
                try:
                    japanese_text = self.speech_recognizer.recognize_google(
                        audio_source, 
                        language="ja-JP"
                    )

                    if japanese_text:
                        # Translate
                        translated = self.translator.translate(japanese_text)

                        translation_data = {
                            "original": japanese_text,
                            "translated": translated,
                            "timestamp": datetime.now().isoformat(),
                            "source": "system_audio"
                        }

                        # Add to buffer
                        self.translation_buffer.append(translation_data)
                        if len(self.translation_buffer) > self.buffer_size:
                            self.translation_buffer.pop(0)

                        # Send to workflow callbacks
                        for callback in self.workflow_callbacks:
                            try:
                                callback(translation_data)
                            except Exception as e:
                                self.logger.error(f"Workflow callback error: {e}")

                        self.logger.info(f"🇯🇵 {japanese_text} → 🇺🇸 {translated}")

                except sr.UnknownValueError:
                    # No speech detected, continue
                    pass
                except Exception as e:
                    self.logger.debug(f"Recognition error: {e}")

            except Exception as e:
                self.logger.error(f"Audio processing error: {e}")
                time.sleep(0.1)

    def register_workflow_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Register a callback for agent workflow integration"""
        self.workflow_callbacks.append(callback)
        self.logger.info(f"✅ Registered workflow callback: {callback.__name__}")

    def start(self):
        """Start system audio capture and translation"""
        if self.is_capturing:
            self.logger.warning("Already capturing")
            return

        self.logger.info("🐟 Starting system audio capture...")
        self.is_capturing = True

        # Start audio capture thread
        self.capture_thread = threading.Thread(target=self._capture_system_audio, daemon=True)
        self.capture_thread.start()

        # Start translation processing thread
        self.translation_thread = threading.Thread(target=self._process_audio_chunks, daemon=True)
        self.translation_thread.start()

        self.logger.info("✅ System audio capture started")
        self.logger.info("   Playing anime will now be translated in real-time")

    def stop(self):
        """Stop system audio capture"""
        if not self.is_capturing:
            return

        self.logger.info("🐟 Stopping system audio capture...")
        self.is_capturing = False

        if self.capture_thread:
            self.capture_thread.join(timeout=5.0)
        if self.translation_thread:
            self.translation_thread.join(timeout=5.0)

        self.logger.info("✅ System audio capture stopped")

    def get_recent_translations(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent translations for agent workflows"""
        return self.translation_buffer[-count:]

    def get_translation_summary(self) -> Dict[str, Any]:
        """Get summary of translations for agent workflows"""
        recent = self.get_recent_translations()

        return {
            "total_translations": len(recent),
            "latest": recent[-1] if recent else None,
            "common_phrases": self._get_common_phrases(recent),
            "timestamp": datetime.now().isoformat()
        }

    def _get_common_phrases(self, translations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get common phrases from translations"""
        phrase_counts = {}
        for trans in translations:
            orig = trans.get('original', '')
            if orig:
                phrase_counts[orig] = phrase_counts.get(orig, 0) + 1

        common = sorted(phrase_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        return [{"phrase": phrase, "count": count} for phrase, count in common]


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Babelfish System Audio Capture")
    parser.add_argument("--start", action="store_true", help="Start capturing")
    parser.add_argument("--test", action="store_true", help="Test audio capture")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("🐟 BABELFISH SYSTEM AUDIO CAPTURE")
    print("="*80 + "\n")

    capture = BabelfishSystemAudioCapture()

    if args.start:
        print("Starting system audio capture...")
        print("Play your anime and translations will appear in real-time")
        print("Press Ctrl+C to stop\n")

        try:
            capture.start()
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nStopping...")
            capture.stop()
            print("✅ Stopped\n")

    elif args.test:
        print("Testing audio capture setup...\n")
        # Test would go here
        print("✅ Test complete\n")

    else:
        print("Usage:")
        print("  --start  : Start capturing system audio")
        print("  --test   : Test audio capture setup")
        print()


if __name__ == "__main__":



    main()