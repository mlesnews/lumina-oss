#!/usr/bin/env python3
"""
Voice Activity Detection (VAD) Enhancement for Voice Filtering

Implements advanced VAD to better detect actual speech vs background noise.
Improves voice filtering accuracy by distinguishing real speech from noise.

Tags: #VOICE_FILTER #VAD #IMPROVEMENT #LUMINA_CORE @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import numpy as np

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        get_logger = lambda name: logging.getLogger(name)

logger = get_logger("VoiceFilterVAD")


@dataclass
class VADResult:
    """Voice Activity Detection result"""
    is_speech: bool
    confidence: float
    energy_level: float
    spectral_centroid: float
    zero_crossing_rate: float
    pitch: Optional[float] = None
    formants: Optional[List[float]] = None
    reasoning: str = ""


class VoiceActivityDetection:
    """
    Advanced Voice Activity Detection (VAD)

    Distinguishes actual speech from:
    - Background noise
    - Silence
    - Non-speech sounds
    - TV/radio bleed-through
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize VAD system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # VAD thresholds (tunable)
        self.energy_threshold = 0.01  # Minimum energy for speech
        self.spectral_centroid_min = 1000  # Hz - minimum for speech
        self.spectral_centroid_max = 4000  # Hz - maximum for speech
        self.zcr_min = 0.01  # Minimum zero crossing rate
        self.zcr_max = 0.3  # Maximum zero crossing rate
        self.pitch_min = 80  # Hz - minimum pitch (male voice)
        self.pitch_max = 400  # Hz - maximum pitch (female/child voice)

        # Adaptive thresholds (learn from patterns)
        self.adaptive_energy_threshold = self.energy_threshold
        self.adaptive_spectral_min = self.spectral_centroid_min
        self.adaptive_spectral_max = self.spectral_centroid_max

        # History for pattern learning
        self.speech_history: List[VADResult] = []
        self.noise_history: List[VADResult] = []

        logger.info("✅ Voice Activity Detection (VAD) initialized")
        logger.info("   Advanced speech detection enabled")

    def detect_voice_activity(self, audio_data: Any, sample_rate: int = 16000) -> VADResult:
        """
        Detect if audio contains actual speech

        Args:
            audio_data: Audio data (numpy array or bytes)
            sample_rate: Sample rate in Hz

        Returns:
            VADResult with detection result
        """
        try:
            # Convert audio to numpy array if needed
            if isinstance(audio_data, bytes):
                audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            else:
                audio_array = np.array(audio_data, dtype=np.float32)

            if len(audio_array) == 0:
                return VADResult(
                    is_speech=False,
                    confidence=0.0,
                    energy_level=0.0,
                    spectral_centroid=0.0,
                    zero_crossing_rate=0.0,
                    reasoning="Empty audio data"
                )

            # Extract features
            energy = self._calculate_energy(audio_array)
            spectral_centroid = self._calculate_spectral_centroid(audio_array, sample_rate)
            zcr = self._calculate_zero_crossing_rate(audio_array)
            pitch = self._estimate_pitch(audio_array, sample_rate)

            # Decision logic
            is_speech = self._is_speech(
                energy, spectral_centroid, zcr, pitch
            )

            confidence = self._calculate_confidence(
                energy, spectral_centroid, zcr, pitch, is_speech
            )

            reasoning = self._generate_reasoning(
                energy, spectral_centroid, zcr, pitch, is_speech
            )

            result = VADResult(
                is_speech=is_speech,
                confidence=confidence,
                energy_level=energy,
                spectral_centroid=spectral_centroid,
                zero_crossing_rate=zcr,
                pitch=pitch,
                reasoning=reasoning
            )

            # Update history for learning
            if is_speech:
                self.speech_history.append(result)
                if len(self.speech_history) > 100:
                    self.speech_history.pop(0)
            else:
                self.noise_history.append(result)
                if len(self.noise_history) > 100:
                    self.noise_history.pop(0)

            # Adaptive learning (update thresholds based on patterns)
            self._adapt_thresholds()

            return result

        except Exception as e:
            logger.debug(f"VAD detection error: {e}")
            return VADResult(
                is_speech=False,
                confidence=0.0,
                energy_level=0.0,
                spectral_centroid=0.0,
                zero_crossing_rate=0.0,
                reasoning=f"Error: {e}"
            )

    def _calculate_energy(self, audio: np.ndarray) -> float:
        """Calculate RMS energy"""
        return float(np.sqrt(np.mean(audio ** 2)))

    def _calculate_spectral_centroid(self, audio: np.ndarray, sample_rate: int) -> float:
        """Calculate spectral centroid (brightness)"""
        try:
            # FFT
            fft = np.fft.rfft(audio)
            magnitude = np.abs(fft)
            frequency = np.fft.rfftfreq(len(audio), 1.0 / sample_rate)

            # Spectral centroid
            if np.sum(magnitude) > 0:
                centroid = np.sum(frequency * magnitude) / np.sum(magnitude)
                return float(centroid)
            return 0.0
        except Exception:
            return 0.0

    def _calculate_zero_crossing_rate(self, audio: np.ndarray) -> float:
        """Calculate zero crossing rate"""
        try:
            signs = np.sign(audio)
            zcr = np.sum(np.abs(np.diff(signs))) / (2.0 * len(audio))
            return float(zcr)
        except Exception:
            return 0.0

    def _estimate_pitch(self, audio: np.ndarray, sample_rate: int) -> Optional[float]:
        """Estimate pitch using autocorrelation"""
        try:
            # Autocorrelation
            autocorr = np.correlate(audio, audio, mode='full')
            autocorr = autocorr[len(autocorr)//2:]

            # Find peaks (pitch candidates)
            # Look for period in range 80-400 Hz (human voice range)
            min_period = int(sample_rate / 400)  # 400 Hz
            max_period = int(sample_rate / 80)    # 80 Hz

            if max_period >= len(autocorr):
                return None

            # Find maximum in pitch range
            pitch_range = autocorr[min_period:max_period]
            if len(pitch_range) == 0:
                return None

            max_idx = np.argmax(pitch_range) + min_period
            pitch = sample_rate / max_idx if max_idx > 0 else None

            return float(pitch) if pitch and 80 <= pitch <= 400 else None
        except Exception:
            return None

    def _is_speech(
        self,
        energy: float,
        spectral_centroid: float,
        zcr: float,
        pitch: Optional[float]
    ) -> bool:
        """Determine if audio is speech based on features"""

        # Check energy threshold
        if energy < self.adaptive_energy_threshold:
            return False

        # Check spectral centroid (speech is typically 1-4 kHz)
        if not (self.adaptive_spectral_min <= spectral_centroid <= self.adaptive_spectral_max):
            return False

        # Check zero crossing rate (speech has moderate ZCR)
        if not (self.zcr_min <= zcr <= self.zcr_max):
            return False

        # Check pitch (if available, should be in human voice range)
        if pitch is not None:
            if not (self.pitch_min <= pitch <= self.pitch_max):
                return False

        return True

    def _calculate_confidence(
        self,
        energy: float,
        spectral_centroid: float,
        zcr: float,
        pitch: Optional[float],
        is_speech: bool
    ) -> float:
        """Calculate confidence score for speech detection"""

        if not is_speech:
            return 0.0

        confidence = 0.0

        # Energy contribution (0-0.3)
        energy_score = min(energy / (self.adaptive_energy_threshold * 10), 1.0)
        confidence += energy_score * 0.3

        # Spectral centroid contribution (0-0.3)
        spectral_score = 1.0 - abs(spectral_centroid - 2500) / 1500  # Peak at 2.5 kHz
        spectral_score = max(0.0, min(1.0, spectral_score))
        confidence += spectral_score * 0.3

        # ZCR contribution (0-0.2)
        zcr_score = 1.0 - abs(zcr - 0.15) / 0.15  # Peak at 0.15
        zcr_score = max(0.0, min(1.0, zcr_score))
        confidence += zcr_score * 0.2

        # Pitch contribution (0-0.2, if available)
        if pitch is not None:
            pitch_score = 1.0 - abs(pitch - 200) / 200  # Peak at 200 Hz
            pitch_score = max(0.0, min(1.0, pitch_score))
            confidence += pitch_score * 0.2
        else:
            # No pitch penalty if pitch detection failed
            confidence += 0.1  # Small bonus for other features matching

        return min(1.0, confidence)

    def _generate_reasoning(
        self,
        energy: float,
        spectral_centroid: float,
        zcr: float,
        pitch: Optional[float],
        is_speech: bool
    ) -> str:
        """Generate human-readable reasoning for decision"""

        reasons = []

        if energy < self.adaptive_energy_threshold:
            reasons.append(f"low energy ({energy:.4f} < {self.adaptive_energy_threshold:.4f})")

        if not (self.adaptive_spectral_min <= spectral_centroid <= self.adaptive_spectral_max):
            reasons.append(f"spectral centroid out of range ({spectral_centroid:.1f} Hz)")

        if not (self.zcr_min <= zcr <= self.zcr_max):
            reasons.append(f"ZCR out of range ({zcr:.3f})")

        if pitch is not None and not (self.pitch_min <= pitch <= self.pitch_max):
            reasons.append(f"pitch out of range ({pitch:.1f} Hz)")

        if is_speech:
            return f"Speech detected (energy={energy:.4f}, spectral={spectral_centroid:.1f}Hz, zcr={zcr:.3f}, pitch={pitch or 'N/A'}Hz)"
        else:
            return f"Not speech: {', '.join(reasons) if reasons else 'features do not match speech pattern'}"

    def _adapt_thresholds(self):
        """Adapt thresholds based on learned patterns"""

        # Only adapt if we have enough data
        if len(self.speech_history) < 10 or len(self.noise_history) < 10:
            return

        # Calculate average energy for speech vs noise
        speech_energies = [r.energy_level for r in self.speech_history[-50:]]
        noise_energies = [r.energy_level for r in self.noise_history[-50:]]

        if speech_energies and noise_energies:
            avg_speech_energy = np.mean(speech_energies)
            avg_noise_energy = np.mean(noise_energies)

            # Adaptive threshold: between speech and noise
            if avg_speech_energy > avg_noise_energy:
                self.adaptive_energy_threshold = (avg_speech_energy + avg_noise_energy) / 2.0
                self.adaptive_energy_threshold = max(0.001, min(0.1, self.adaptive_energy_threshold))

        # Adapt spectral centroid range
        speech_spectrals = [r.spectral_centroid for r in self.speech_history[-50:] if r.spectral_centroid > 0]
        if speech_spectrals:
            avg_spectral = np.mean(speech_spectrals)
            std_spectral = np.std(speech_spectrals)

            # Adaptive range: mean ± 2*std
            self.adaptive_spectral_min = max(500, avg_spectral - 2 * std_spectral)
            self.adaptive_spectral_max = min(8000, avg_spectral + 2 * std_spectral)


def main():
    """Test VAD system"""
    vad = VoiceActivityDetection()

    # Simulate audio data (would be real audio in production)
    sample_rate = 16000
    duration = 0.1  # 100ms

    # Simulate speech (sine wave at 200 Hz)
    t = np.linspace(0, duration, int(sample_rate * duration))
    speech_audio = np.sin(2 * np.pi * 200 * t) * 0.5

    # Simulate noise (random)
    noise_audio = np.random.randn(int(sample_rate * duration)) * 0.1

    print("\n🧪 Testing Voice Activity Detection")
    print("=" * 80)

    result_speech = vad.detect_voice_activity(speech_audio, sample_rate)
    print(f"\n✅ Speech Test:")
    print(f"   Is Speech: {result_speech.is_speech}")
    print(f"   Confidence: {result_speech.confidence:.2%}")
    print(f"   Reasoning: {result_speech.reasoning}")

    result_noise = vad.detect_voice_activity(noise_audio, sample_rate)
    print(f"\n❌ Noise Test:")
    print(f"   Is Speech: {result_noise.is_speech}")
    print(f"   Confidence: {result_noise.confidence:.2%}")
    print(f"   Reasoning: {result_noise.reasoning}")

    print("=" * 80)


if __name__ == "__main__":


    main()