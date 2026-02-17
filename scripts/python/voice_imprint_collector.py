#!/usr/bin/env python3
"""
Voice Imprint Collector - Capture and Improve Voice Profiles

Records voice samples, extracts features, and trains voice profiles for better recognition.
Specifically designed to help capture and improve wife's (Glenda's) voiceprint.

Usage:
    python scripts/python/voice_imprint_collector.py --profile wife --record
    python scripts/python/voice_imprint_collector.py --profile wife --analyze
    python scripts/python/voice_imprint_collector.py --profile wife --improve

Tags: #VOICE_IMPRINT #VOICE_PROFILE #TRAINING #CAPTURE @JARVIS @LUMINA
"""

import sys
import json
import argparse
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add project root to path
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

logger = get_logger("VoiceImprintCollector")

try:
    from voice_profile_library_system import VoiceProfileLibrarySystem, VoiceProfile, SoundType
    VOICE_PROFILE_AVAILABLE = True
except ImportError as e:
    VOICE_PROFILE_AVAILABLE = False
    logger.error(f"❌ Voice Profile Library not available: {e}")

try:
    import pyaudio
    import wave
    import numpy as np
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False
    logger.warning("⚠️  Audio libraries not available. Install: pip install pyaudio numpy")


class VoiceImprintCollector:
    """
    Voice Imprint Collector

    Records voice samples, extracts features, and improves voice profiles.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize voice imprint collector"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "voice_imprints"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize voice profile library
        if VOICE_PROFILE_AVAILABLE:
            self.profile_library = VoiceProfileLibrarySystem(project_root)
        else:
            self.profile_library = None

        # Audio settings
        self.chunk = 1024
        self.format = pyaudio.paInt16 if AUDIO_LIBS_AVAILABLE else None
        self.channels = 1
        self.rate = 44100
        self.record_seconds = 5  # Default 5 seconds per sample

        logger.info("="*80)
        logger.info("🎤 VOICE IMPRINT COLLECTOR")
        logger.info("="*80)
        logger.info(f"   Data directory: {self.data_dir}")
        logger.info(f"   Voice Profile Library: {'✅ Available' if VOICE_PROFILE_AVAILABLE else '❌ Not available'}")
        logger.info(f"   Audio Libraries: {'✅ Available' if AUDIO_LIBS_AVAILABLE else '❌ Not available'}")
        logger.info("="*80)

    def record_sample(
        self,
        profile_id: str,
        duration: Optional[float] = None,
        sample_name: Optional[str] = None
    ) -> Optional[Path]:
        """
        Record a voice sample

        Args:
            profile_id: Profile ID (e.g., "wife", "glenda")
            duration: Recording duration in seconds (default: 5)
            sample_name: Optional name for this sample

        Returns:
            Path to saved audio file
        """
        if not AUDIO_LIBS_AVAILABLE:
            logger.error("❌ Audio libraries not available. Install: pip install pyaudio numpy")
            return None

        duration = duration or self.record_seconds

        logger.info("")
        logger.info("="*80)
        logger.info(f"🎤 RECORDING VOICE SAMPLE: {profile_id}")
        logger.info("="*80)
        logger.info(f"   Duration: {duration} seconds")
        logger.info(f"   Profile: {profile_id}")
        logger.info("")
        logger.info("   🎙️  Start speaking now...")
        logger.info("")

        # Create audio file path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sample_name = sample_name or f"{profile_id}_{timestamp}"
        audio_file = self.data_dir / f"{sample_name}.wav"

        try:
            # Initialize PyAudio
            audio = pyaudio.PyAudio()

            # Open stream
            stream = audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )

            logger.info("   ⏺️  Recording...")
            frames = []

            # Record audio
            for i in range(0, int(self.rate / self.chunk * duration)):
                data = stream.read(self.chunk)
                frames.append(data)
                # Show progress
                if i % 10 == 0:
                    progress = int((i / (self.rate / self.chunk * duration)) * 100)
                    print(f"\r   Progress: {progress}%", end="", flush=True)

            print()  # New line after progress

            # Stop recording
            stream.stop_stream()
            stream.close()
            audio.terminate()

            # Save audio file
            wf = wave.open(str(audio_file), 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))
            wf.close()

            logger.info(f"   ✅ Sample saved: {audio_file}")
            logger.info(f"   📊 File size: {audio_file.stat().st_size / 1024:.2f} KB")
            logger.info("")

            return audio_file

        except Exception as e:
            logger.error(f"   ❌ Error recording: {e}")
            return None

    def extract_features(self, audio_file: Path) -> Dict[str, Any]:
        """
        Extract voice features from audio file

        Args:
            audio_file: Path to audio file

        Returns:
            Dictionary of voice features
        """
        if not AUDIO_LIBS_AVAILABLE:
            logger.error("❌ Audio libraries not available")
            return {}

        logger.info(f"   🔍 Extracting features from: {audio_file.name}")

        try:
            # Read audio file
            wf = wave.open(str(audio_file), 'rb')
            frames = wf.readframes(-1)
            sound_info = np.frombuffer(frames, dtype=np.int16)
            sample_rate = wf.getframerate()
            wf.close()

            # Basic features
            duration = len(sound_info) / sample_rate
            amplitude = np.abs(sound_info)
            amplitude_mean = np.mean(amplitude)
            amplitude_std = np.std(amplitude)
            amplitude_max = np.max(amplitude)

            # Spectral features (simplified)
            fft = np.fft.fft(sound_info)
            magnitude = np.abs(fft)
            frequency = np.fft.fftfreq(len(fft), 1/sample_rate)

            # Find dominant frequency
            dominant_freq_idx = np.argmax(magnitude[:len(magnitude)//2])
            dominant_frequency = abs(frequency[dominant_freq_idx])

            # Energy features
            energy = np.sum(amplitude ** 2) / len(amplitude)

            features = {
                "duration": float(duration),
                "sample_rate": int(sample_rate),
                "amplitude_mean": float(amplitude_mean),
                "amplitude_std": float(amplitude_std),
                "amplitude_max": int(amplitude_max),
                "dominant_frequency": float(dominant_frequency),
                "energy": float(energy),
                "sample_count": len(sound_info),
                "timestamp": datetime.now().isoformat()
            }

            logger.info(f"   ✅ Features extracted:")
            logger.info(f"      Duration: {duration:.2f}s")
            logger.info(f"      Dominant Frequency: {dominant_frequency:.2f} Hz")
            logger.info(f"      Energy: {energy:.2e}")

            return features

        except Exception as e:
            logger.error(f"   ❌ Error extracting features: {e}")
            return {}

    def train_profile(
        self,
        profile_id: str,
        name: str,
        audio_files: Optional[List[Path]] = None,
        num_samples: int = 5
    ) -> Dict[str, Any]:
        """
        Train a voice profile with recorded samples

        Args:
            profile_id: Profile ID (e.g., "wife", "glenda")
            name: Display name
            audio_files: Optional list of audio files to use
            num_samples: Number of samples to record if audio_files not provided

        Returns:
            Training results
        """
        if not VOICE_PROFILE_AVAILABLE:
            logger.error("❌ Voice Profile Library not available")
            return {"success": False, "error": "Voice Profile Library not available"}

        logger.info("")
        logger.info("="*80)
        logger.info(f"🎓 TRAINING VOICE PROFILE: {profile_id}")
        logger.info("="*80)
        logger.info(f"   Profile: {profile_id} ({name})")
        logger.info("")

        # Collect samples
        if audio_files is None:
            logger.info(f"   📝 Recording {num_samples} samples...")
            audio_files = []
            for i in range(num_samples):
                logger.info(f"   Sample {i+1}/{num_samples}:")
                audio_file = self.record_sample(profile_id, sample_name=f"{profile_id}_training_{i+1}")
                if audio_file:
                    audio_files.append(audio_file)
                time.sleep(1)  # Brief pause between samples

        if not audio_files:
            logger.error("   ❌ No audio samples collected")
            return {"success": False, "error": "No audio samples"}

        # Extract features from all samples
        logger.info("")
        logger.info("   🔍 Extracting features from all samples...")
        all_features = []
        for audio_file in audio_files:
            features = self.extract_features(audio_file)
            if features:
                all_features.append(features)

        if not all_features:
            logger.error("   ❌ No features extracted")
            return {"success": False, "error": "No features extracted"}

        # Aggregate features
        logger.info("")
        logger.info("   📊 Aggregating features...")
        aggregated_features = self._aggregate_features(all_features)

        # Add/update profile in library
        logger.info("")
        logger.info("   💾 Saving profile to library...")
        profile = self.profile_library.add_voice_profile(
            profile_id=profile_id,
            name=name,
            voice_features=aggregated_features
        )

        # Save sample metadata
        sample_metadata = {
            "profile_id": profile_id,
            "name": name,
            "samples": [str(f) for f in audio_files],
            "features": all_features,
            "aggregated_features": aggregated_features,
            "sample_count": len(audio_files),
            "timestamp": datetime.now().isoformat()
        }

        metadata_file = self.data_dir / f"{profile_id}_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(sample_metadata, f, indent=2, default=str)

        logger.info("")
        logger.info("="*80)
        logger.info("✅ PROFILE TRAINING COMPLETE")
        logger.info("="*80)
        logger.info(f"   Profile: {profile_id} ({name})")
        logger.info(f"   Samples: {len(audio_files)}")
        logger.info(f"   Features: {len(aggregated_features)}")
        logger.info(f"   Metadata: {metadata_file}")
        logger.info("="*80)

        return {
            "success": True,
            "profile_id": profile_id,
            "name": name,
            "samples": len(audio_files),
            "features": len(aggregated_features),
            "metadata_file": str(metadata_file),
            "profile": {
                "profile_id": profile.profile_id,
                "name": profile.name,
                "sample_count": profile.sample_count,
                "confidence_threshold": profile.confidence_threshold
            }
        }

    def _aggregate_features(self, features_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate features from multiple samples"""
        if not features_list:
            return {}

        aggregated = {
            "sample_count": len(features_list),
            "duration_mean": np.mean([f.get("duration", 0) for f in features_list]),
            "duration_std": np.std([f.get("duration", 0) for f in features_list]),
            "amplitude_mean": np.mean([f.get("amplitude_mean", 0) for f in features_list]),
            "amplitude_std": np.mean([f.get("amplitude_std", 0) for f in features_list]),
            "dominant_frequency_mean": np.mean([f.get("dominant_frequency", 0) for f in features_list]),
            "dominant_frequency_std": np.std([f.get("dominant_frequency", 0) for f in features_list]),
            "energy_mean": np.mean([f.get("energy", 0) for f in features_list]),
            "energy_std": np.std([f.get("energy", 0) for f in features_list]),
            "timestamp": datetime.now().isoformat()
        }

        return aggregated

    def improve_profile(
        self,
        profile_id: str,
        additional_samples: int = 3
    ) -> Dict[str, Any]:
        """
        Improve existing profile with additional samples

        Args:
            profile_id: Profile ID to improve
            additional_samples: Number of additional samples to record

        Returns:
            Improvement results
        """
        if not VOICE_PROFILE_AVAILABLE:
            logger.error("❌ Voice Profile Library not available")
            return {"success": False, "error": "Voice Profile Library not available"}

        # Get existing profile
        if profile_id not in self.profile_library.voice_profiles:
            logger.error(f"   ❌ Profile not found: {profile_id}")
            return {"success": False, "error": f"Profile not found: {profile_id}"}

        existing_profile = self.profile_library.voice_profiles[profile_id]
        logger.info("")
        logger.info("="*80)
        logger.info(f"🔧 IMPROVING VOICE PROFILE: {profile_id}")
        logger.info("="*80)
        logger.info(f"   Current samples: {existing_profile.sample_count}")
        logger.info(f"   Current confidence: {existing_profile.confidence_threshold:.2f}")
        logger.info("")

        # Record additional samples
        audio_files = []
        for i in range(additional_samples):
            logger.info(f"   Additional sample {i+1}/{additional_samples}:")
            audio_file = self.record_sample(
                profile_id,
                sample_name=f"{profile_id}_improvement_{existing_profile.sample_count + i + 1}"
            )
            if audio_file:
                audio_files.append(audio_file)
            time.sleep(1)

        if not audio_files:
            logger.error("   ❌ No additional samples recorded")
            return {"success": False, "error": "No additional samples"}

        # Extract features
        logger.info("")
        logger.info("   🔍 Extracting features from new samples...")
        new_features = []
        for audio_file in audio_files:
            features = self.extract_features(audio_file)
            if features:
                new_features.append(features)

        # Merge with existing features
        existing_features = existing_profile.voice_features or {}
        if new_features:
            aggregated_new = self._aggregate_features(new_features)
            # Merge features (weighted average: 70% existing, 30% new)
            merged_features = {}
            for key in set(list(existing_features.keys()) + list(aggregated_new.keys())):
                if key.endswith("_mean"):
                    base_key = key.replace("_mean", "")
                    old_val = existing_features.get(key, 0)
                    new_val = aggregated_new.get(key, old_val)
                    merged_features[key] = 0.7 * old_val + 0.3 * new_val
                else:
                    merged_features[key] = aggregated_new.get(key, existing_features.get(key))

            # Update profile
            existing_profile.voice_features = merged_features
            existing_profile.sample_count += len(audio_files)
            existing_profile.last_seen = datetime.now().isoformat()

            # Save
            self.profile_library._save_profiles()

        logger.info("")
        logger.info("="*80)
        logger.info("✅ PROFILE IMPROVEMENT COMPLETE")
        logger.info("="*80)
        logger.info(f"   Profile: {profile_id}")
        logger.info(f"   New samples: {len(audio_files)}")
        logger.info(f"   Total samples: {existing_profile.sample_count}")
        logger.info("="*80)

        return {
            "success": True,
            "profile_id": profile_id,
            "new_samples": len(audio_files),
            "total_samples": existing_profile.sample_count
        }

    def analyze_profile(self, profile_id: str) -> Dict[str, Any]:
        """Analyze existing profile"""
        if not VOICE_PROFILE_AVAILABLE:
            logger.error("❌ Voice Profile Library not available")
            return {"success": False, "error": "Voice Profile Library not available"}

        if profile_id not in self.profile_library.voice_profiles:
            logger.error(f"   ❌ Profile not found: {profile_id}")
            return {"success": False, "error": f"Profile not found: {profile_id}"}

        profile = self.profile_library.voice_profiles[profile_id]

        logger.info("")
        logger.info("="*80)
        logger.info(f"📊 PROFILE ANALYSIS: {profile_id}")
        logger.info("="*80)
        logger.info(f"   Name: {profile.name}")
        logger.info(f"   Profile ID: {profile.profile_id}")
        logger.info(f"   Sample Count: {profile.sample_count}")
        logger.info(f"   Confidence Threshold: {profile.confidence_threshold:.2f}")
        logger.info(f"   Success Rate: {profile.success_rate:.2%}")
        logger.info(f"   Last Seen: {profile.last_seen}")
        logger.info(f"   Is Active: {profile.is_active}")
        logger.info("")
        logger.info("   Features:")
        if profile.voice_features:
            for key, value in profile.voice_features.items():
                if isinstance(value, (int, float)):
                    logger.info(f"      {key}: {value:.2f}")
                else:
                    logger.info(f"      {key}: {value}")
        else:
            logger.info("      No features available")
        logger.info("="*80)

        return {
            "success": True,
            "profile": {
                "profile_id": profile.profile_id,
                "name": profile.name,
                "sample_count": profile.sample_count,
                "confidence_threshold": profile.confidence_threshold,
                "success_rate": profile.success_rate,
                "voice_features": profile.voice_features
            }
        }


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(
        description="Voice Imprint Collector - Capture and improve voice profiles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Record and train wife's voice profile
  python scripts/python/voice_imprint_collector.py --profile wife --name "Glenda" --train --samples 5

  # Improve existing profile
  python scripts/python/voice_imprint_collector.py --profile wife --improve --samples 3

  # Analyze existing profile
  python scripts/python/voice_imprint_collector.py --profile wife --analyze

  # Record single sample
  python scripts/python/voice_imprint_collector.py --profile wife --record --duration 10
        """
    )

    parser.add_argument(
        "--profile", "-p",
        type=str,
        required=True,
        help="Profile ID (e.g., 'wife', 'glenda')"
    )
    parser.add_argument(
        "--name", "-n",
        type=str,
        help="Display name for profile (default: same as profile ID)"
    )
    parser.add_argument(
        "--train",
        action="store_true",
        help="Train a new profile"
    )
    parser.add_argument(
        "--improve",
        action="store_true",
        help="Improve existing profile"
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze existing profile"
    )
    parser.add_argument(
        "--record",
        action="store_true",
        help="Record a single sample"
    )
    parser.add_argument(
        "--samples", "-s",
        type=int,
        default=5,
        help="Number of samples to record (default: 5)"
    )
    parser.add_argument(
        "--duration", "-d",
        type=float,
        default=5.0,
        help="Recording duration in seconds (default: 5.0)"
    )

    args = parser.parse_args()

    collector = VoiceImprintCollector()

    profile_id = args.profile
    name = args.name or profile_id

    if args.train:
        result = collector.train_profile(profile_id, name, num_samples=args.samples)
    elif args.improve:
        result = collector.improve_profile(profile_id, additional_samples=args.samples)
    elif args.analyze:
        result = collector.analyze_profile(profile_id)
    elif args.record:
        audio_file = collector.record_sample(profile_id, duration=args.duration)
        result = {"success": audio_file is not None, "audio_file": str(audio_file) if audio_file else None}
    else:
        parser.print_help()
        return 1

    if not result.get("success"):
        logger.error("❌ Operation failed")
        return 1

    return 0


if __name__ == "__main__":


    sys.exit(main())