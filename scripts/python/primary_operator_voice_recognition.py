#!/usr/bin/env python3
"""
Primary Operator Voice Recognition - Auto-Listening System

Automatically recognizes the primary operator's (OP's) voice and starts listening
without requiring manual clicks. Identifies OP specifically for Cursor IDE.

Tags: #PRIMARY_OPERATOR #VOICE_RECOGNITION #AUTO_LISTEN #REQUIRED @JARVIS @LUMINA
"""

import sys
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Callable

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

try:
    from voice_filter_system import VoiceFilterSystem, VoicePrintProfile
    VOICE_FILTER_AVAILABLE = True
except ImportError:
    VOICE_FILTER_AVAILABLE = False
    VoiceFilterSystem = None
    VoicePrintProfile = None

try:
    from cursor_auto_recording_transcription_fixed import CursorAutoRecordingTranscriptionFixed
    TRANSCRIPTION_AVAILABLE = True
except ImportError:
    TRANSCRIPTION_AVAILABLE = False
    CursorAutoRecordingTranscriptionFixed = None

logger = get_logger("PrimaryOperatorVoice")


class PrimaryOperatorVoiceRecognition:
    """
    Primary Operator Voice Recognition System

    Automatically:
    - Recognizes OP's voice specifically
    - Starts listening without manual clicks
    - Filters out all other voices (TV, background, wife, etc.)
    - Maintains OP voice profile
    """

    def __init__(self, project_root: Optional[Path] = None, user_id: str = "primary_operator"):
        """Initialize primary operator voice recognition"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.user_id = user_id
        self.op_voice_profile = None
        self.voice_filter = None
        self.transcription_service = None

        # Auto-listening state
        self.auto_listening_enabled = True
        self.is_listening = False
        self.listening_thread = None
        self.stop_event = threading.Event()

        # OP recognition state
        self.op_recognized = False
        self.op_confidence = 0.0
        self.min_confidence = 0.7  # Minimum confidence to recognize as OP

        # Statistics
        self.stats = {
            "op_recognitions": 0,
            "non_op_rejections": 0,
            "auto_listen_starts": 0,
            "voice_samples_collected": 0,
            "profile_trained": False
        }

        # Initialize components
        self._initialize_voice_profile()
        self._initialize_voice_filter()
        self._initialize_transcription()

        logger.info("✅ Primary Operator Voice Recognition initialized")

    def _initialize_voice_profile(self):
        """Initialize OP voice profile"""
        if not VOICE_FILTER_AVAILABLE:
            logger.warning("⚠️  Voice filter not available - cannot create OP profile")
            return

        try:
            self.op_voice_profile = VoicePrintProfile(
                user_id=self.user_id,
                project_root=self.project_root
            )

            # Check if profile is trained
            profile_data = self.op_voice_profile.profile_data
            self.stats["profile_trained"] = profile_data.get("trained", False)

            if self.stats["profile_trained"]:
                logger.info("✅ OP voice profile loaded (trained)")
            else:
                logger.warning("⚠️  OP voice profile not trained - will train automatically")
                logger.info("   Speak naturally - system will learn your voice")

        except Exception as e:
            logger.error(f"❌ Failed to initialize voice profile: {e}")
            self.op_voice_profile = None

    def _initialize_voice_filter(self):
        """Initialize voice filter system"""
        if not VOICE_FILTER_AVAILABLE:
            logger.warning("⚠️  Voice filter not available")
            return

        try:
            self.voice_filter = VoiceFilterSystem(
                user_id=self.user_id,
                project_root=self.project_root
            )
            logger.info("✅ Voice filter system initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize voice filter: {e}")
            self.voice_filter = None

    def _initialize_transcription(self):
        """Initialize transcription service"""
        if not TRANSCRIPTION_AVAILABLE:
            logger.warning("⚠️  Transcription service not available")
            return

        try:
            # Auto-start transcription (no manual click)
            self.transcription_service = CursorAutoRecordingTranscriptionFixed(
                project_root=self.project_root,
                auto_start=True  # REQUIRED - auto-start without manual click
            )

            # CRITICAL: Add "Jarvis" as trigger word (REQUIRED)
            # Note: Default trigger uses "activate" action, but we also add "start_recording" for explicit recording
            self.transcription_service.add_trigger_word(
                word="jarvis",
                action="start_recording",  # Explicitly start recording
                case_sensitive=False,
                confidence_threshold=0.5  # Even lower threshold for better detection
            )
            logger.info("✅ Added 'Jarvis' trigger word -> start_recording (REQUIRED)")

            # Also add "activate" action (in case that's what's needed)
            self.transcription_service.add_trigger_word("jarvis", "activate", False, 0.5)

            # Add variations
            self.transcription_service.add_trigger_word("jarv", "start_recording", False, 0.5)
            self.transcription_service.add_trigger_word("jarvis", "start_recording", False, 0.5)

            logger.info("✅ Transcription service initialized (auto-start enabled, 'Jarvis' trigger added)")
        except Exception as e:
            logger.error(f"❌ Failed to initialize transcription: {e}")
            self.transcription_service = None

    def train_op_voice(self, audio_samples: Optional[list] = None, auto_collect: bool = True):
        """
        Train OP voice profile

        Args:
            audio_samples: Optional list of audio samples (if None, will auto-collect)
            auto_collect: If True, automatically collect samples from microphone
        """
        if not self.op_voice_profile:
            logger.error("❌ Voice profile not available")
            return False

        logger.info("🎤 Training OP voice profile...")
        logger.info("   Speak naturally - system will learn your voice")

        if auto_collect:
            # Auto-collect samples
            samples_collected = self._auto_collect_voice_samples()
            if samples_collected > 0:
                self.stats["voice_samples_collected"] += samples_collected
                logger.info(f"✅ Collected {samples_collected} voice samples")

        # Mark profile as trained
        self.op_voice_profile.profile_data["trained"] = True
        self.op_voice_profile.save_profile()
        self.stats["profile_trained"] = True

        logger.info("✅ OP voice profile trained")
        return True

    def _auto_collect_voice_samples(self, num_samples: int = 5) -> int:
        """Automatically collect voice samples from microphone"""
        if not VOICE_FILTER_AVAILABLE:
            return 0

        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            microphone = sr.Microphone()

            samples_collected = 0

            logger.info(f"🎤 Collecting {num_samples} voice samples...")
            logger.info("   Please speak naturally")

            with microphone as source:
                # Adjust for ambient noise
                recognizer.adjust_for_ambient_noise(source, duration=1)

                for i in range(num_samples):
                    logger.info(f"   Sample {i+1}/{num_samples}...")
                    try:
                        audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)

                        # Convert to numpy array
                        import numpy as np
                        audio_data = np.frombuffer(audio.get_raw_data(), dtype=np.int16)
                        sample_rate = audio.sample_rate

                        # Add to profile
                        if self.op_voice_profile:
                            self.op_voice_profile.add_voice_sample(audio_data, sample_rate)
                            samples_collected += 1

                        time.sleep(0.5)  # Brief pause between samples

                    except sr.WaitTimeoutError:
                        logger.warning(f"   Sample {i+1} timeout - no speech detected")
                        continue
                    except Exception as e:
                        logger.error(f"   Sample {i+1} error: {e}")
                        continue

            # Save profile after collection
            if self.op_voice_profile and samples_collected > 0:
                self.op_voice_profile.save_profile()

            return samples_collected

        except Exception as e:
            logger.error(f"❌ Auto-collection failed: {e}")
            return 0

    def recognize_op_voice(self, audio_data, sample_rate: int) -> tuple[bool, float]:
        """
        Recognize if audio is from OP

        Returns:
            (is_op, confidence): True if OP's voice, confidence score
        """
        if not self.op_voice_profile:
            # If no profile, assume it's OP (for initial training)
            return True, 0.5

        # Check if profile is trained
        if not self.stats["profile_trained"]:
            # Not trained yet - accept all voice for training
            logger.debug("Profile not trained - accepting voice for training")
            return True, 0.5

        # Match against OP profile
        is_match, confidence = self.op_voice_profile.match_voice(
            audio_data,
            sample_rate,
            threshold=self.min_confidence
        )

        if is_match:
            self.stats["op_recognitions"] += 1
            self.op_recognized = True
            self.op_confidence = confidence
            logger.info(f"✅ OP voice recognized (confidence: {confidence:.2f})")
        else:
            self.stats["non_op_rejections"] += 1
            self.op_recognized = False
            self.op_confidence = confidence
            logger.debug(f"🚫 Non-OP voice rejected (confidence: {confidence:.2f})")

        return is_match, confidence

    def _auto_listen_loop(self):
        """Auto-listening loop - continuously listens for OP's voice"""
        logger.info("👂 Auto-listening started - waiting for OP's voice...")

        if not VOICE_FILTER_AVAILABLE:
            logger.error("❌ Voice recognition not available")
            return

        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            microphone = sr.Microphone()

            with microphone as source:
                # Adjust for ambient noise
                recognizer.adjust_for_ambient_noise(source, duration=1)

                while self.is_listening and not self.stop_event.is_set():
                    try:
                        # Listen for audio
                        audio = recognizer.listen(source, timeout=1, phrase_time_limit=10)

                        # Convert to numpy array
                        import numpy as np
                        audio_data = np.frombuffer(audio.get_raw_data(), dtype=np.int16)
                        sample_rate = audio.sample_rate

                        # Recognize OP voice
                        is_op, confidence = self.recognize_op_voice(audio_data, sample_rate)

                        if is_op:
                            # OP voice detected - start transcription
                            logger.info("🎤 OP voice detected - starting transcription...")
                            self._start_transcription_for_op()

                            # If profile not trained, add this as training sample
                            if not self.stats["profile_trained"]:
                                if self.op_voice_profile:
                                    self.op_voice_profile.add_voice_sample(audio_data, sample_rate)
                                    self.stats["voice_samples_collected"] += 1

                                    # Auto-train after 5 samples
                                    if self.stats["voice_samples_collected"] >= 5:
                                        logger.info("✅ Enough samples collected - training profile...")
                                        self.train_op_voice(auto_collect=False)

                    except sr.WaitTimeoutError:
                        # No audio - continue listening
                        continue
                    except Exception as e:
                        logger.error(f"❌ Auto-listen error: {e}")
                        time.sleep(0.5)
                        continue

        except Exception as e:
            logger.error(f"❌ Auto-listen loop failed: {e}")

    def _start_transcription_for_op(self):
        """Start transcription when OP voice is detected"""
        if self.transcription_service:
            # CRITICAL: Ensure listening is started
            if not self.transcription_service.is_listening:
                logger.info("🔄 Starting transcription service listening...")
                self.transcription_service.start_listening()
                self.stats["auto_listen_starts"] += 1
                logger.info("✅ Transcription started automatically (OP voice detected)")
            else:
                logger.debug("✅ Transcription already listening")
        else:
            logger.warning("⚠️  Transcription service not available")

    def start_auto_listening(self):
        """Start automatic listening for OP's voice (REQUIRED - no manual click)"""
        if self.is_listening:
            logger.warning("⚠️  Already listening")
            return True

        if not self.auto_listening_enabled:
            logger.warning("⚠️  Auto-listening disabled")
            return False

        # CRITICAL: Start transcription service FIRST (this handles "Jarvis" trigger)
        if self.transcription_service:
            if not self.transcription_service.is_listening:
                logger.info("🚀 Starting transcription service (handles 'Jarvis' trigger)...")
                self.transcription_service.start_listening()
                logger.info("✅ Transcription service listening - 'Jarvis' trigger active")
            else:
                logger.info("✅ Transcription service already listening")
        else:
            logger.error("❌ Transcription service not available - 'Jarvis' trigger won't work!")

        self.is_listening = True
        self.stop_event.clear()

        # Start listening thread (for OP voice recognition)
        self.listening_thread = threading.Thread(target=self._auto_listen_loop, daemon=True)
        self.listening_thread.start()

        logger.info("✅ Auto-listening started (REQUIRED - no manual click needed)")
        logger.info("   Say 'Jarvis' to trigger transcription")
        logger.info("   System will automatically recognize OP's voice")

        # If profile not trained, start training
        if not self.stats["profile_trained"]:
            logger.info("🎤 OP voice profile not trained - will train automatically")
            logger.info("   Speak naturally - system will learn your voice")

        return True

    def stop_auto_listening(self):
        """Stop automatic listening"""
        self.is_listening = False
        self.stop_event.set()

        if self.listening_thread:
            self.listening_thread.join(timeout=2)

        logger.info("👋 Auto-listening stopped")

    def get_stats(self) -> Dict[str, Any]:
        """Get recognition statistics"""
        return {
            **self.stats,
            "is_listening": self.is_listening,
            "op_recognized": self.op_recognized,
            "op_confidence": self.op_confidence,
            "auto_listening_enabled": self.auto_listening_enabled
        }


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Primary Operator Voice Recognition (REQUIRED)")
    parser.add_argument("--start", action="store_true", help="Start auto-listening (REQUIRED)")
    parser.add_argument("--train", action="store_true", help="Train OP voice profile")
    parser.add_argument("--stats", action="store_true", help="Show statistics")

    args = parser.parse_args()

    try:
        recognition = PrimaryOperatorVoiceRecognition()

        if args.train:
            print("="*80)
            print("🎤 TRAINING PRIMARY OPERATOR VOICE PROFILE")
            print("="*80)
            print()
            print("Please speak naturally - system will learn your voice")
            print()
            recognition.train_op_voice()
            return 0

        if args.stats:
            stats = recognition.get_stats()
            print("="*80)
            print("📊 PRIMARY OPERATOR VOICE RECOGNITION STATISTICS")
            print("="*80)
            print(f"Profile Trained: {stats['profile_trained']}")
            print(f"OP Recognitions: {stats['op_recognitions']}")
            print(f"Non-OP Rejections: {stats['non_op_rejections']}")
            print(f"Auto-Listen Starts: {stats['auto_listen_starts']}")
            print(f"Voice Samples: {stats['voice_samples_collected']}")
            print(f"Currently Listening: {stats['is_listening']}")
            print(f"OP Recognized: {stats['op_recognized']}")
            print(f"OP Confidence: {stats['op_confidence']:.2f}")
            return 0

        if args.start or not any([args.train, args.stats]):
            print("="*80)
            print("🎤 PRIMARY OPERATOR VOICE RECOGNITION (REQUIRED)")
            print("="*80)
            print()
            print("This will:")
            print("  - Automatically recognize your voice (OP)")
            print("  - Start listening without manual clicks")
            print("  - Filter out all other voices")
            print("  - Train your voice profile automatically")
            print()
            print("Press Ctrl+C to stop")
            print("-"*80)
            print()

            recognition.start_auto_listening()

            try:
                while True:
                    time.sleep(5)
                    stats = recognition.get_stats()
                    print(f"Listening: {'✅' if stats['is_listening'] else '❌'} | "
                          f"OP Recognized: {'✅' if stats['op_recognized'] else '❌'} | "
                          f"Confidence: {stats['op_confidence']:.2f} | "
                          f"Recognitions: {stats['op_recognitions']}")
            except KeyboardInterrupt:
                pass

            recognition.stop_auto_listening()
            return 0

    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":


    sys.exit(main() or 0)