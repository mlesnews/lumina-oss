#!/usr/bin/env python3
"""
MM-HMM Voice Detection - Speech Pathologist Analysis

Detects and distinguishes between user's "mm-hmm" and wife's "mm-hmm" sounds.
Uses speech pathologist principles to analyze vocal patterns.

Tags: #VOICE_DETECTION #MMHMM #SPEECH_PATHOLOGY #VOICE_FILTER #REQUIRED @JARVIS @LUMINA
"""

import sys
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime

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

logger = get_logger("MMHMMDetection")

try:
    from scipy import signal
    from scipy.fft import fft
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logger.warning("⚠️  scipy not available - some features may not work")


@dataclass
class MMHMMPattern:
    """MM-HMM vocal pattern characteristics"""
    duration: float  # Duration in seconds
    pitch: float  # Dominant frequency (Hz)
    energy: float  # Audio energy
    formant_f1: float  # First formant (vowel quality)
    formant_f2: float  # Second formant (vowel quality)
    nasal_quality: float  # Nasal resonance (0.0-1.0)
    voice_quality: str  # "clear", "nasal", "muffled"
    speaker_id: Optional[str] = None  # "user" or "wife" if identified
    confidence: float = 0.0  # Confidence in identification


class MMHMMVoiceDetector:
    """
    MM-HMM Voice Detector - Speech Pathologist Approach

    Analyzes "mm-hmm" sounds using speech pathologist principles:
    - Vocal tract resonance (formants)
    - Nasal quality
    - Pitch characteristics
    - Duration patterns
    - Voice quality markers
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize MM-HMM detector"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "mmhmm_patterns"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # User's MM-HMM patterns (learned)
        self.user_mmhmm_patterns = []
        self.wife_mmhmm_patterns = []

        # Speech pathologist analysis parameters
        self.nasal_freq_range = (200, 400)  # Nasal resonance frequency range
        self.mmhmm_duration_range = (0.1, 0.8)  # Typical "mm-hmm" duration (seconds)

        logger.info("✅ MM-HMM Voice Detector initialized (Speech Pathologist approach)")

    def detect_mmhmm(self, audio_data: np.ndarray, sample_rate: int) -> Tuple[bool, Optional[MMHMMPattern]]:
        """
        Detect if audio contains "mm-hmm" sound

        Returns:
            (is_mmhmm, pattern) - True if detected, with pattern characteristics
        """
        if not SCIPY_AVAILABLE:
            return False, None

        try:
            # Extract features
            duration = len(audio_data) / sample_rate

            # Check duration (mm-hmm is typically short, 0.1-0.8 seconds)
            if duration < self.mmhmm_duration_range[0] or duration > self.mmhmm_duration_range[1]:
                return False, None

            # Frequency analysis
            fft_data = np.abs(fft(audio_data))
            freqs = np.fft.fftfreq(len(fft_data), 1/sample_rate)

            # Find dominant frequency (pitch)
            dominant_freq_idx = np.argmax(fft_data[:len(fft_data)//2])
            dominant_freq = abs(freqs[dominant_freq_idx])

            # Check for nasal quality (mm-hmm has nasal resonance)
            nasal_energy = np.sum(fft_data[(freqs >= self.nasal_freq_range[0]) & (freqs <= self.nasal_freq_range[1])])
            total_energy = np.sum(fft_data[:len(fft_data)//2])
            nasal_quality = nasal_energy / total_energy if total_energy > 0 else 0.0

            # Formant analysis (vowel quality)
            formant_f1, formant_f2 = self._extract_formants(audio_data, sample_rate)

            # Energy
            energy = np.sum(audio_data ** 2)

            # Determine voice quality
            if nasal_quality > 0.3:
                voice_quality = "nasal"
            elif dominant_freq > 200:  # Higher pitch
                voice_quality = "clear"
            else:
                voice_quality = "muffled"

            # Check if this matches "mm-hmm" characteristics
            # MM-HMM typically has:
            # - Nasal quality (nasal_quality > 0.2)
            # - Short duration (0.1-0.8s)
            # - Moderate energy
            is_mmhmm = (
                nasal_quality > 0.2 and
                duration >= 0.1 and
                duration <= 0.8 and
                energy > 0.01  # Minimum energy threshold
            )

            if is_mmhmm:
                pattern = MMHMMPattern(
                    duration=duration,
                    pitch=dominant_freq,
                    energy=energy,
                    formant_f1=formant_f1,
                    formant_f2=formant_f2,
                    nasal_quality=nasal_quality,
                    voice_quality=voice_quality
                )
                return True, pattern

            return False, None
        except Exception as e:
            logger.debug(f"MM-HMM detection error: {e}")
            return False, None

    def _extract_formants(self, audio_data: np.ndarray, sample_rate: int) -> Tuple[float, float]:
        """Extract formant frequencies (F1, F2) - speech pathologist analysis"""
        try:
            if not SCIPY_AVAILABLE:
                return 0.0, 0.0

            # Use LPC (Linear Predictive Coding) for formant extraction
            # Simplified: find peaks in frequency spectrum
            fft_data = np.abs(fft(audio_data))
            freqs = np.fft.fftfreq(len(fft_data), 1/sample_rate)

            # Find peaks in frequency spectrum (formants)
            positive_freqs = freqs[:len(freqs)//2]
            positive_fft = fft_data[:len(fft_data)//2]

            # Find first two major peaks (F1 and F2)
            peaks, _ = signal.find_peaks(positive_fft, height=np.max(positive_fft) * 0.1)

            if len(peaks) >= 2:
                # Sort by amplitude
                peak_amplitudes = positive_fft[peaks]
                sorted_indices = np.argsort(peak_amplitudes)[::-1]
                f1_idx = peaks[sorted_indices[0]]
                f2_idx = peaks[sorted_indices[1]] if len(sorted_indices) > 1 else peaks[sorted_indices[0]]
                return float(positive_freqs[f1_idx]), float(positive_freqs[f2_idx])
            elif len(peaks) >= 1:
                f1_idx = peaks[0]
                return float(positive_freqs[f1_idx]), 0.0

            return 0.0, 0.0
        except Exception as e:
            logger.debug(f"Formant extraction error: {e}")
            return 0.0, 0.0

    def identify_speaker(self, pattern: MMHMMPattern) -> Tuple[Optional[str], float]:
        """
        Identify speaker (user vs wife) based on MM-HMM pattern

        Uses speech pathologist analysis:
        - Pitch differences (male vs female)
        - Formant patterns (vocal tract differences)
        - Nasal quality differences
        - Duration patterns

        Returns:
            (speaker_id, confidence) - "user", "wife", or None with confidence (0.0-1.0)
        """
        if not self.user_mmhmm_patterns and not self.wife_mmhmm_patterns:
            # No training data - use basic heuristics
            # Male voices typically: 85-180 Hz, Female: 165-255 Hz
            if pattern.pitch > 180:
                return "wife", 0.6  # Higher pitch suggests female
            elif pattern.pitch < 150:
                return "user", 0.6  # Lower pitch suggests male
            else:
                return None, 0.3  # Ambiguous

        # Compare with learned patterns
        user_similarities = []
        wife_similarities = []

        for user_pattern in self.user_mmhmm_patterns:
            similarity = self._compare_patterns(pattern, user_pattern)
            user_similarities.append(similarity)

        for wife_pattern in self.wife_mmhmm_patterns:
            similarity = self._compare_patterns(pattern, wife_pattern)
            wife_similarities.append(similarity)

        # Determine best match
        avg_user_sim = np.mean(user_similarities) if user_similarities else 0.0
        avg_wife_sim = np.mean(wife_similarities) if wife_similarities else 0.0

        threshold = 0.5  # Minimum similarity to identify

        if avg_user_sim > threshold and avg_user_sim > avg_wife_sim:
            return "user", min(1.0, avg_user_sim)
        elif avg_wife_sim > threshold and avg_wife_sim > avg_user_sim:
            return "wife", min(1.0, avg_wife_sim)
        else:
            return None, max(avg_user_sim, avg_wife_sim)

    def _compare_patterns(self, pattern1: MMHMMPattern, pattern2: MMHMMPattern) -> float:
        """Compare two MM-HMM patterns - speech pathologist similarity"""
        similarities = []

        # Pitch similarity (weighted heavily)
        pitch_diff = abs(pattern1.pitch - pattern2.pitch)
        pitch_sim = 1.0 - min(1.0, pitch_diff / 100.0)  # Normalize to 0-1
        similarities.append(pitch_sim * 0.4)  # 40% weight

        # Formant similarity (vocal tract characteristics)
        f1_diff = abs(pattern1.formant_f1 - pattern2.formant_f1)
        f1_sim = 1.0 - min(1.0, f1_diff / 200.0)
        similarities.append(f1_sim * 0.2)  # 20% weight

        f2_diff = abs(pattern1.formant_f2 - pattern2.formant_f2)
        f2_sim = 1.0 - min(1.0, f2_diff / 500.0)
        similarities.append(f2_sim * 0.2)  # 20% weight

        # Nasal quality similarity
        nasal_diff = abs(pattern1.nasal_quality - pattern2.nasal_quality)
        nasal_sim = 1.0 - min(1.0, nasal_diff / 0.5)
        similarities.append(nasal_sim * 0.1)  # 10% weight

        # Duration similarity
        duration_diff = abs(pattern1.duration - pattern2.duration)
        duration_sim = 1.0 - min(1.0, duration_diff / 0.5)
        similarities.append(duration_sim * 0.1)  # 10% weight

        return sum(similarities)

    def learn_user_mmhmm(self, pattern: MMHMMPattern):
        """Learn user's MM-HMM pattern"""
        pattern.speaker_id = "user"
        self.user_mmhmm_patterns.append(pattern)
        logger.info(f"✅ Learned user's MM-HMM pattern (pitch: {pattern.pitch:.1f}Hz, nasal: {pattern.nasal_quality:.2f})")

    def learn_wife_mmhmm(self, pattern: MMHMMPattern):
        """Learn wife's MM-HMM pattern"""
        pattern.speaker_id = "wife"
        self.wife_mmhmm_patterns.append(pattern)
        logger.info(f"✅ Learned wife's MM-HMM pattern (pitch: {pattern.pitch:.1f}Hz, nasal: {pattern.nasal_quality:.2f})")

    def analyze_mmhmm(self, audio_data: np.ndarray, sample_rate: int) -> Optional[Dict]:
        """
        Complete speech pathologist analysis of MM-HMM sound

        Returns:
            Analysis dict with detection, identification, and recommendations
        """
        is_mmhmm, pattern = self.detect_mmhmm(audio_data, sample_rate)

        if not is_mmhmm:
            return None

        # Identify speaker
        speaker_id, confidence = self.identify_speaker(pattern)
        pattern.speaker_id = speaker_id
        pattern.confidence = confidence

        # Speech pathologist insights
        insights = []

        if pattern.nasal_quality > 0.3:
            insights.append("High nasal resonance - typical of 'mm-hmm'")

        if pattern.pitch > 180:
            insights.append("Higher pitch suggests female speaker")
        elif pattern.pitch < 150:
            insights.append("Lower pitch suggests male speaker")

        if pattern.duration < 0.3:
            insights.append("Short duration - quick acknowledgment")
        elif pattern.duration > 0.5:
            insights.append("Longer duration - more emphatic acknowledgment")

        return {
            "is_mmhmm": True,
            "pattern": pattern,
            "speaker_id": speaker_id,
            "confidence": confidence,
            "insights": insights,
            "recommendation": "filter" if speaker_id == "wife" else "accept"
        }


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="MM-HMM Voice Detection - Speech Pathologist Analysis")
    parser.add_argument('--test', action='store_true', help='Test mode')

    args = parser.parse_args()

    print("=" * 80)
    print("🎤 MM-HMM VOICE DETECTION - SPEECH PATHOLOGIST ANALYSIS")
    print("=" * 80)
    print()
    print("Detects and distinguishes between user's and wife's 'mm-hmm' sounds")
    print("Uses speech pathologist principles for analysis")
    print()
    print("=" * 80)

    detector = MMHMMVoiceDetector()

    if args.test:
        print("🧪 Test mode - detector ready")
        print("   Use in voice filtering system")
    else:
        print("✅ MM-HMM detector initialized")
        print("   Integrated with voice filtering system")

    print("=" * 80)


if __name__ == "__main__":


    main()