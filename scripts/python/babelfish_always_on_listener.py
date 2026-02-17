#!/usr/bin/env python3
"""
Babelfish Always-On Listener

Full-time, always-on listening for real-time Japanese translation.
JARVIS speaks summaries and discussions - NO code blocks in output!
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
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

logger = get_logger("BabelfishAlwaysOnListener")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class BabelfishAlwaysOnListener:
    """
    Always-on listening system for real-time translation.
    JARVIS speaks summaries - no code blocks!
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(".").resolve()
        self.logger = get_logger("BabelfishAlwaysOnListener")

        self.data_dir = self.project_root / "data" / "babelfish"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # NAS configuration
        self.nas_ip = "<NAS_PRIMARY_IP>"
        self.nas_path = f"\\\\{self.nas_ip}\\backups\\MATT_Backups"

        # Translation components
        self.translator = None
        self.speech_recognizer = None

        # Always-on state
        self.is_listening = False
        self.listening_thread = None
        self.translation_queue = queue.Queue()

        # Translation history for summaries
        self.translation_history: List[Dict[str, Any]] = []
        self.summary_interval = 60  # Summarize every 60 seconds

        # JARVIS voice/TTS
        self.jarvis_tts = None
        self.jarvis_enabled = True

        self.logger.info("🐟 Babelfish Always-On Listener initialized")
        self.logger.info(f"   NAS Path: {self.nas_path}")

        self._initialize_components()

    def _initialize_components(self):
        """Initialize translation and TTS components"""

        # Initialize translator
        try:
            from deep_translator import GoogleTranslator
            self.translator = GoogleTranslator(source="ja", target="en")
            self.logger.info("✅ Translator initialized")
        except ImportError:
            self.logger.warning("❌ deep-translator not installed")

        # Initialize JARVIS TTS
        try:
            import pyttsx3
            self.jarvis_tts = pyttsx3.init()
            # Configure JARVIS voice (male, clear)
            voices = self.jarvis_tts.getProperty('voices')
            for voice in voices:
                if 'male' in voice.name.lower() or 'david' in voice.name.lower():
                    self.jarvis_tts.setProperty('voice', voice.id)
                    break
            self.jarvis_tts.setProperty('rate', 150)  # Slightly faster
            self.logger.info("✅ JARVIS TTS initialized")
        except ImportError:
            self.logger.warning("❌ pyttsx3 not installed - JARVIS voice disabled")
            self.jarvis_enabled = False
        except Exception as e:
            self.logger.warning(f"❌ TTS initialization error: {e}")
            self.jarvis_enabled = False

    def _jarvis_speak(self, text: str, priority: str = "normal"):
        """JARVIS speaks the text"""
        if not self.jarvis_enabled or not self.jarvis_tts:
            self.logger.info(f"🤖 JARVIS: {text}")
            return

        try:
            # Clean text for speech (remove code blocks, etc.)
            clean_text = text.replace('```', '').replace('`', '')
            clean_text = clean_text.replace('python', '').replace('bash', '')

            # Speak
            self.jarvis_tts.say(clean_text)
            self.jarvis_tts.runAndWait()

            self.logger.info(f"🤖 JARVIS spoke: {text[:100]}...")
        except Exception as e:
            self.logger.error(f"❌ JARVIS TTS error: {e}")
            # Fallback to logging
            self.logger.info(f"🤖 JARVIS: {text}")

    def _find_anime_on_nas(self) -> List[Path]:
        """Find anime files on NAS"""
        nas_path = Path(self.nas_path)
        anime_files = []

        # Try to access NAS (may need authentication)
        try:
            if not nas_path.exists():
                self.logger.warning(f"⚠️  NAS path not directly accessible: {self.nas_path}")
                self.logger.info("   Try mapping the drive first, or check NAS credentials")
                # Try alternative paths
                alt_paths = [
                    Path("Z:\\"),  # Common mapped drive
                    Path("Y:\\"),
                    Path("X:\\"),
                    Path(f"\\\\{self.nas_ip}\\Videos"),
                    Path(f"\\\\{self.nas_ip}\\Media"),
                ]
                for alt_path in alt_paths:
                    if alt_path.exists():
                        self.logger.info(f"   ✅ Found alternative path: {alt_path}")
                        nas_path = alt_path
                        break
                else:
                    return anime_files
        except Exception as e:
            self.logger.warning(f"⚠️  NAS access error: {e}")
            return anime_files

        self.logger.info(f"🔍 Searching for anime on NAS: {self.nas_path}")

        # Common anime locations
        search_paths = [
            nas_path / "Videos",
            nas_path / "Media",
            nas_path / "Anime",
            nas_path / "Entertainment",
            nas_path
        ]

        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.webm']

        for search_path in search_paths:
            if not search_path.exists():
                continue

            try:
                for ext in video_extensions:
                    for video_file in search_path.rglob(f"*{ext}"):
                        # Filter for reasonable size (> 50MB, likely a full episode)
                        if video_file.stat().st_size > 50 * 1024 * 1024:
                            anime_files.append(video_file)
                            self.logger.info(f"   🎬 Found: {video_file.name}")
            except PermissionError:
                self.logger.warning(f"   ⚠️  Permission denied: {search_path}")
            except Exception as e:
                self.logger.warning(f"   ⚠️  Error searching {search_path}: {e}")

        self.logger.info(f"✅ Found {len(anime_files)} anime files on NAS")
        return anime_files

    def _generate_summary(self) -> str:
        """Generate JARVIS summary of recent translations"""
        if not self.translation_history:
            return "No translations yet. Waiting for Japanese audio..."

        recent = self.translation_history[-10:]  # Last 10 translations

        summary_parts = []
        summary_parts.append(f"I've processed {len(recent)} recent translations.")

        # Group by common phrases
        phrases = {}
        for trans in recent:
            orig = trans.get('original', '')
            if orig:
                phrases[orig] = phrases.get(orig, 0) + 1

        if phrases:
            summary_parts.append("Common phrases detected:")
            for phrase, count in sorted(phrases.items(), key=lambda x: x[1], reverse=True)[:3]:
                summary_parts.append(f"  '{phrase}' appeared {count} times")

        # Latest translation
        if recent:
            latest = recent[-1]
            summary_parts.append(f"Latest: '{latest.get('original', '')}' translated to '{latest.get('translated', '')}'")

        return " ".join(summary_parts)

    def _listening_loop(self):
        """Main listening loop"""
        self.logger.info("🐟 Always-on listening started")
        self._jarvis_speak("Babelfish always-on listener activated. Ready to translate Japanese audio in real-time.")

        last_summary_time = time.time()

        while self.is_listening:
            try:
                # Check for audio input (placeholder - needs actual audio capture)
                # For now, simulate with periodic checks
                time.sleep(1)

                # Generate periodic summaries
                current_time = time.time()
                if current_time - last_summary_time >= self.summary_interval:
                    summary = self._generate_summary()
                    self._jarvis_speak(f"Translation summary: {summary}")
                    last_summary_time = current_time

            except Exception as e:
                self.logger.error(f"Listening loop error: {e}")
                time.sleep(1)

    def start(self):
        """Start always-on listening"""
        if self.is_listening:
            self.logger.warning("Already listening")
            return

        self.logger.info("🐟 Starting always-on listener...")
        self.is_listening = True
        self.listening_thread = threading.Thread(target=self._listening_loop, daemon=True)
        self.listening_thread.start()

        self._jarvis_speak("Always-on listening started. I'm ready to translate Japanese audio in real-time.")

        self.logger.info("✅ Always-on listener started")

    def stop(self):
        """Stop always-on listening"""
        if not self.is_listening:
            return

        self.logger.info("🐟 Stopping always-on listener...")
        self.is_listening = False

        if self.listening_thread:
            self.listening_thread.join(timeout=5.0)

        self._jarvis_speak("Always-on listening stopped.")
        self.logger.info("✅ Always-on listener stopped")

    def process_translation(self, japanese_text: str) -> Optional[str]:
        """Process a translation and add to history"""
        if not self.translator:
            return None

        try:
            translated = self.translator.translate(japanese_text)

            translation_data = {
                "original": japanese_text,
                "translated": translated,
                "timestamp": datetime.now().isoformat()
            }

            self.translation_history.append(translation_data)

            # JARVIS speaks the translation
            self._jarvis_speak(f"Translation: {translated}")

            return translated
        except Exception as e:
            self.logger.error(f"Translation error: {e}")
            return None


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Babelfish Always-On Listener")
    parser.add_argument("--test", action="store_true", help="Test with sample phrases")
    parser.add_argument("--find-anime", action="store_true", help="Find anime on NAS")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("🐟 BABELFISH ALWAYS-ON LISTENER")
    print("="*80 + "\n")

    listener = BabelfishAlwaysOnListener()

    if args.find_anime:
        print("🔍 Finding anime on NAS...\n")
        anime_files = listener._find_anime_on_nas()
        print(f"\n✅ Found {len(anime_files)} anime files")
        if anime_files:
            print("\nFirst 5 files:")
            for i, file in enumerate(anime_files[:5], 1):
                print(f"  {i}. {file.name}")

    elif args.test:
        print("🧪 Testing with sample phrases...\n")
        test_phrases = [
            "こんにちは",
            "ありがとうございます",
            "すみません"
        ]

        for phrase in test_phrases:
            print(f"🇯🇵 {phrase}")
            translated = listener.process_translation(phrase)
            if translated:
                print(f"🇺🇸 {translated}\n")

    else:
        print("Starting always-on listener...")
        print("Press Ctrl+C to stop\n")

        try:
            listener.start()

            # Keep running
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\nStopping...")
            listener.stop()
            print("✅ Stopped\n")


if __name__ == "__main__":



    main()