#!/usr/bin/env python3
"""
Collect Wife's Voice Samples - REQUIRED

Collects voice samples from wife to train the exclusion profile.
This improves voice filtering accuracy.

Tags: #VOICE_FILTER #TRAINING #EXCLUDE_WIFE #REQUIRED @JARVIS @LUMINA
"""

import sys
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CollectWifeVoice")

try:
    import speech_recognition as sr
    import numpy as np
    from voice_filter_system import VoicePrintProfile
    VOICE_FILTER_AVAILABLE = True
except ImportError:
    VOICE_FILTER_AVAILABLE = False
    logger.error("❌ Voice filter system not available")


def collect_wife_voice_samples(num_samples: int = 5):
    """Collect voice samples from wife for training"""
    if not VOICE_FILTER_AVAILABLE:
        logger.error("❌ Voice filter not available")
        return False

    try:
        # Initialize recognizer
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()

        # Load wife profile
        wife_profile = VoicePrintProfile("wife", project_root)

        print("=" * 80)
        print("🎤 COLLECTING WIFE'S VOICE SAMPLES")
        print("=" * 80)
        print()
        print(f"Need {num_samples} voice samples from wife")
        print("Wife should speak clearly into the microphone")
        print()

        # Calibrate microphone
        print("Calibrating microphone for ambient noise...")
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
        print("✅ Microphone calibrated")
        print()

        samples_collected = 0

        while samples_collected < num_samples:
            print(f"Sample {samples_collected + 1}/{num_samples}:")
            print("   Wife, please speak now (say anything)...")

            try:
                with microphone as source:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)

                # Convert to numpy array
                raw_data = audio.get_raw_data(convert_rate=None, convert_width=None)
                audio_data = np.frombuffer(raw_data, dtype=np.int16)
                sample_rate = audio.sample_rate

                # Add to profile
                wife_profile.add_voice_sample(audio_data, sample_rate)
                samples_collected += 1

                print(f"   ✅ Sample {samples_collected} collected")
                print()

                time.sleep(0.5)  # Brief pause between samples

            except sr.WaitTimeoutError:
                print("   ⏱️  Timeout - no speech detected, trying again...")
                continue
            except KeyboardInterrupt:
                print("\n👋 Collection cancelled by user")
                return False

        # Train profile
        print("Training voice profile...")
        if wife_profile.train_profile(min_samples=num_samples):
            print("✅ Voice profile trained successfully!")
            print(f"   Collected {samples_collected} samples")
            print("   Wife's voice will now be filtered out more accurately")
        else:
            print("⚠️  Could not train profile (need more samples)")

        print()
        print("=" * 80)
        print("✅ VOICE SAMPLE COLLECTION COMPLETE")
        print("=" * 80)

        return True

    except Exception as e:
        logger.error(f"❌ Failed to collect voice samples: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Collect Wife's Voice Samples for Training")
    parser.add_argument('--samples', type=int, default=5, help='Number of samples to collect (default: 5)')

    args = parser.parse_args()

    collect_wife_voice_samples(num_samples=args.samples)
