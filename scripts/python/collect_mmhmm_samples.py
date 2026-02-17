#!/usr/bin/env python3
"""
Collect MM-HMM Samples for Learning - REQUIRED

Collects "mm-hmm" samples from both user and wife to train the MM-HMM detector.
Uses speech pathologist analysis to distinguish between speakers.

Tags: #MMHMM #VOICE_TRAINING #SPEECH_PATHOLOGY #REQUIRED @JARVIS @LUMINA
"""

import sys
import time
import numpy as np
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

logger = get_logger("CollectMMHMMSamples")

try:
    import speech_recognition as sr
    import pyaudio
    SPEECH_REC_AVAILABLE = True
except ImportError:
    SPEECH_REC_AVAILABLE = False
    logger.error("❌ speech_recognition/pyaudio not available")

try:
    from mmhmm_voice_detection import MMHMMVoiceDetector
    MMHMM_AVAILABLE = True
except ImportError:
    MMHMM_AVAILABLE = False
    logger.error("❌ MM-HMM detector not available")


def collect_mmhmm_samples(speaker: str, num_samples: int = 5):
    """
    Collect MM-HMM samples from a speaker

    Args:
        speaker: "user" or "wife"
        num_samples: Number of samples to collect
    """
    if not SPEECH_REC_AVAILABLE or not MMHMM_AVAILABLE:
        logger.error("❌ Required libraries not available")
        return False

    print("=" * 80)
    print(f"🎤 COLLECTING {speaker.upper()}'S MM-HMM SAMPLES")
    print("=" * 80)
    print()
    print(f"Please say 'mm-hmm' {num_samples} times")
    print("   (Natural acknowledgment sounds)")
    print()
    print("Press Enter when ready to start...")
    input()
    print()

    detector = MMHMMVoiceDetector(project_root)
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    samples_collected = 0

    with microphone as source:
        # Adjust for ambient noise
        print("🔧 Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1.0)
        print("✅ Ready")
        print()

        while samples_collected < num_samples:
            print(f"📝 Sample {samples_collected + 1}/{num_samples}: Say 'mm-hmm'...")

            try:
                # Listen for audio
                audio = recognizer.listen(source, timeout=5.0, phrase_time_limit=2.0)

                # Convert to numpy array
                raw_data = audio.get_raw_data(convert_rate=None, convert_width=None)
                audio_data = np.frombuffer(raw_data, dtype=np.int16)
                sample_rate = audio.sample_rate

                # Detect MM-HMM
                is_mmhmm, pattern = detector.detect_mmhmm(audio_data, sample_rate)

                if is_mmhmm:
                    # Learn pattern
                    if speaker == "user":
                        detector.learn_user_mmhmm(pattern)
                    elif speaker == "wife":
                        detector.learn_wife_mmhmm(pattern)

                    samples_collected += 1
                    print(f"   ✅ MM-HMM detected and learned!")
                    print(f"      Pitch: {pattern.pitch:.1f}Hz")
                    print(f"      Nasal quality: {pattern.nasal_quality:.2f}")
                    print(f"      Duration: {pattern.duration:.2f}s")
                    print()
                else:
                    print("   ⚠️  Not detected as MM-HMM - please try again")
                    print()

            except sr.WaitTimeoutError:
                print("   ⏱️  Timeout - please try again")
                print()
            except Exception as e:
                logger.error(f"❌ Error collecting sample: {e}")
                print()

    print("=" * 80)
    print(f"✅ COLLECTED {samples_collected} MM-HMM SAMPLES FROM {speaker.upper()}")
    print("=" * 80)
    print()
    print("The system can now distinguish between your 'mm-hmm' and wife's 'mm-hmm'")
    print("   using speech pathologist analysis")
    print()

    return True


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Collect MM-HMM Samples for Learning")
    parser.add_argument('--speaker', type=str, choices=['user', 'wife'], required=True,
                       help='Speaker to collect samples from (user or wife)')
    parser.add_argument('--samples', type=int, default=5,
                       help='Number of samples to collect (default: 5)')

    args = parser.parse_args()

    print("=" * 80)
    print("🎤 MM-HMM SAMPLE COLLECTION - SPEECH PATHOLOGIST TRAINING")
    print("=" * 80)
    print()
    print("This will collect 'mm-hmm' samples to train the voice detector")
    print("The system will learn to distinguish between your 'mm-hmm' and wife's 'mm-hmm'")
    print()
    print("=" * 80)
    print()

    if not SPEECH_REC_AVAILABLE:
        print("❌ speech_recognition not available")
        print("   Install: pip install SpeechRecognition pyaudio")
        return 1

    if not MMHMM_AVAILABLE:
        print("❌ MM-HMM detector not available")
        return 1

    success = collect_mmhmm_samples(args.speaker, args.samples)

    if success:
        print("✅ Sample collection complete!")
        return 0
    else:
        print("❌ Sample collection failed")
        return 1


if __name__ == "__main__":


    sys.exit(main() or 0)