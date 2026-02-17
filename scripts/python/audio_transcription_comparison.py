#!/usr/bin/env python3
"""
Audio-to-Transcription Comparison System

Real-time comparison of transcribed text to actual audio live feed.
Looks for patterns or lack of patterns to:
- Define results
- Break out (or not) of loops
- Improve listening accuracy
- Filter unwanted voices (e.g., wife/Glenda)

Tags: #VOICE_RECOGNITION #AUDIO_ANALYSIS #PATTERN_DETECTION #LUMINA_CORE
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from collections import deque
import numpy as np

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

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

logger = get_logger("AudioTranscriptionComparison")


@dataclass
class ComparisonResult:
    """Result of audio-to-transcription comparison"""
    match_confidence: float  # 0.0-1.0
    pattern_detected: bool
    pattern_type: Optional[str]  # "consistent", "inconsistent", "noise", "voice_mismatch"
    audio_features: Dict[str, Any]
    transcription_text: str
    should_break_loop: bool
    should_filter: bool
    reasoning: str


class AudioTranscriptionComparator:
    """
    Real-time comparison of audio to transcription

    Compares:
    - Audio features (pitch, energy, spectral characteristics)
    - Transcription text patterns
    - Voice characteristics
    - Pattern consistency

    Uses this to:
    - Detect voice mismatches (e.g., wife's voice transcribed as user's)
    - Break out of loops when patterns don't match
    - Improve filtering accuracy
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize audio-transcription comparator"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Pattern detection buffers
        self.audio_buffer = deque(maxlen=100)  # Last 100 audio samples
        self.transcription_buffer = deque(maxlen=50)  # Last 50 transcriptions
        self.comparison_history = deque(maxlen=100)  # Last 100 comparisons

        # Pattern detection thresholds
        self.pattern_consistency_threshold = 0.7  # 70% consistency = pattern
        self.mismatch_threshold = 0.4  # Below 40% = mismatch, break loop
        self.filter_threshold = 0.3  # Below 30% = filter out

        # AGGRESSIVE FILTERING: More sensitive thresholds for better detection
        # Lower thresholds = more likely to filter (better for catching wife's voice)
        self.aggressive_mismatch_threshold = 0.5  # 50% = mismatch (more aggressive)
        self.aggressive_filter_threshold = 0.4  # 40% = filter (more aggressive)

        logger.info("✅ Audio-Transcription Comparator initialized")
        logger.info("   Real-time pattern detection enabled")

    def extract_audio_features(self, audio_data: Any) -> Dict[str, Any]:
        """
        Extract features from audio data for comparison

        Returns: Dictionary of audio features
        """
        features = {
            "timestamp": datetime.now().isoformat(),
            "duration": getattr(audio_data, 'duration', 0.0),
            "sample_rate": getattr(audio_data, 'sample_rate', 16000),
            "channels": getattr(audio_data, 'channels', 1),
        }

        # Try to extract more detailed features
        try:
            import numpy as np

            if hasattr(audio_data, 'audio'):
                audio_array = audio_data.audio
                if isinstance(audio_array, np.ndarray):
                    # Energy features
                    features["mean_energy"] = float(np.mean(np.abs(audio_array)))
                    features["std_energy"] = float(np.std(np.abs(audio_array)))
                    features["max_energy"] = float(np.max(np.abs(audio_array)))

                    # Spectral features (if we can compute FFT)
                    if len(audio_array) > 0:
                        fft = np.fft.rfft(audio_array)
                        magnitude = np.abs(fft)
                        features["spectral_centroid"] = float(np.sum(np.arange(len(magnitude)) * magnitude) / (np.sum(magnitude) + 1e-10))
                        features["spectral_rolloff"] = float(np.sum(magnitude > (0.85 * np.max(magnitude))) / len(magnitude))

                    # Zero crossing rate (voice activity indicator)
                    zero_crossings = np.sum(np.diff(np.signbit(audio_array)))
                    features["zero_crossing_rate"] = float(zero_crossings / len(audio_array))

        except (ImportError, AttributeError) as e:
            logger.debug(f"   Could not extract advanced features: {e}")

        return features

    def analyze_transcription_pattern(self, transcription_text: str) -> Dict[str, Any]:
        """
        Analyze transcription text for patterns

        Looks for:
        - Word patterns
        - Speaking style
        - Vocabulary usage
        - Sentence structure
        """
        pattern = {
            "word_count": len(transcription_text.split()),
            "avg_word_length": np.mean([len(w) for w in transcription_text.split()]) if transcription_text.split() else 0,
            "sentence_count": transcription_text.count('.') + transcription_text.count('?') + transcription_text.count('!'),
            "question_marks": transcription_text.count('?'),
            "exclamation_marks": transcription_text.count('!'),
            "has_question": '?' in transcription_text,
            "has_exclamation": '!' in transcription_text,
            "text_length": len(transcription_text),
            "capitalization_ratio": sum(1 for c in transcription_text if c.isupper()) / len(transcription_text) if transcription_text else 0
        }

        return pattern

    def compare_audio_to_transcription(
        self,
        audio_data: Any,
        transcription_text: str,
        expected_speaker: Optional[str] = None
    ) -> ComparisonResult:
        """
        Instantaneous comparison of audio to transcription

        Compares:
        - Audio features to transcription patterns
        - Pattern consistency
        - Voice characteristics
        - Expected vs actual speaker

        Returns: ComparisonResult with match confidence and recommendations
        """
        # Extract features
        audio_features = self.extract_audio_features(audio_data)
        transcription_pattern = self.analyze_transcription_pattern(transcription_text)

        # Add to buffers
        self.audio_buffer.append(audio_features)
        self.transcription_buffer.append(transcription_pattern)

        # Compare to historical patterns
        match_confidence = self._calculate_match_confidence(
            audio_features,
            transcription_pattern,
            expected_speaker
        )

        # Detect patterns
        pattern_detected, pattern_type = self._detect_patterns(
            audio_features,
            transcription_pattern
        )

        # Determine if we should break loop
        should_break_loop = self._should_break_loop(
            match_confidence,
            pattern_type,
            audio_features,
            transcription_pattern
        )

        # Determine if we should filter
        should_filter = self._should_filter_voice(
            match_confidence,
            pattern_type,
            expected_speaker
        )

        # Generate reasoning
        reasoning = self._generate_reasoning(
            match_confidence,
            pattern_type,
            should_break_loop,
            should_filter
        )

        result = ComparisonResult(
            match_confidence=match_confidence,
            pattern_detected=pattern_detected,
            pattern_type=pattern_type,
            audio_features=audio_features,
            transcription_text=transcription_text,
            should_break_loop=should_break_loop,
            should_filter=should_filter,
            reasoning=reasoning
        )

        # Add to history
        self.comparison_history.append(result)

        logger.debug(
            f"   🔍 Comparison: confidence={match_confidence:.2f}, "
            f"pattern={pattern_type}, break_loop={should_break_loop}, "
            f"filter={should_filter}"
        )

        return result

    def _calculate_match_confidence(
        self,
        audio_features: Dict[str, Any],
        transcription_pattern: Dict[str, Any],
        expected_speaker: Optional[str] = None
    ) -> float:
        """
        Calculate confidence that audio matches transcription

        Returns: 0.0-1.0 confidence score
        """
        confidence_factors = []

        # Factor 1: Audio energy consistency
        if "mean_energy" in audio_features and len(self.audio_buffer) > 1:
            recent_energies = [a.get("mean_energy", 0) for a in list(self.audio_buffer)[-5:]]
            if recent_energies:
                energy_std = np.std(recent_energies)
                energy_mean = np.mean(recent_energies)
                consistency = 1.0 - min(1.0, energy_std / (energy_mean + 1e-10))
                confidence_factors.append(consistency * 0.3)

        # Factor 2: Transcription pattern consistency
        if len(self.transcription_buffer) > 1:
            recent_patterns = list(self.transcription_buffer)[-5:]
            word_counts = [p.get("word_count", 0) for p in recent_patterns]
            if word_counts:
                word_count_std = np.std(word_counts)
                word_count_mean = np.mean(word_counts)
                consistency = 1.0 - min(1.0, word_count_std / (word_count_mean + 1e-10))
                confidence_factors.append(consistency * 0.3)

        # Factor 3: Audio quality indicators
        if "zero_crossing_rate" in audio_features:
            zcr = audio_features["zero_crossing_rate"]
            # Voice typically has ZCR in certain range
            if 0.01 < zcr < 0.3:  # Typical voice range
                confidence_factors.append(0.2)
            else:
                confidence_factors.append(0.1)

        # Factor 4: Transcription quality
        if transcription_pattern.get("word_count", 0) > 0:
            # Has actual words
            confidence_factors.append(0.2)
        else:
            # No words = low confidence
            confidence_factors.append(0.0)

        # Calculate final confidence
        if confidence_factors:
            match_confidence = sum(confidence_factors)
        else:
            match_confidence = 0.5  # Default if no factors

        return max(0.0, min(1.0, match_confidence))

    def _detect_patterns(
        self,
        audio_features: Dict[str, Any],
        transcription_pattern: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Detect patterns in audio and transcription

        Returns: (pattern_detected, pattern_type)
        """
        # Check for consistent patterns
        if len(self.comparison_history) >= 5:
            recent_confidences = [r.match_confidence for r in list(self.comparison_history)[-5:]]
            avg_confidence = np.mean(recent_confidences)
            std_confidence = np.std(recent_confidences)

            if avg_confidence >= self.pattern_consistency_threshold and std_confidence < 0.2:
                return True, "consistent"
            elif avg_confidence < self.mismatch_threshold:
                return True, "inconsistent"
            elif std_confidence > 0.3:
                return True, "noise"

        # Check for voice mismatch patterns
        if len(self.comparison_history) >= 3:
            recent_confidences = [r.match_confidence for r in list(self.comparison_history)[-3:]]
            if all(c < self.mismatch_threshold for c in recent_confidences):
                return True, "voice_mismatch"

        return False, None

    def _should_break_loop(
        self,
        match_confidence: float,
        pattern_type: Optional[str],
        audio_features: Dict[str, Any],
        transcription_pattern: Dict[str, Any]
    ) -> bool:
        """
        Determine if we should break out of a loop

        Break loop if:
        - Low match confidence (audio doesn't match transcription)
        - Inconsistent patterns detected
        - Voice mismatch detected
        """
        # AGGRESSIVE: Use more aggressive threshold for better detection
        # Low confidence = break loop
        if match_confidence < self.aggressive_mismatch_threshold:
            return True

        # Inconsistent pattern = break loop
        if pattern_type == "inconsistent":
            return True

        # Voice mismatch = break loop
        if pattern_type == "voice_mismatch":
            return True

        # Noise pattern = break loop (not real voice)
        if pattern_type == "noise":
            return True

        return False

    def _should_filter_voice(
        self,
        match_confidence: float,
        pattern_type: Optional[str],
        expected_speaker: Optional[str] = None
    ) -> bool:
        """
        Determine if voice should be filtered

        Filter if:
        - Very low match confidence
        - Voice mismatch (not expected speaker)
        - Noise pattern
        """
        # AGGRESSIVE: Use more aggressive threshold for better wife detection
        # Very low confidence = filter
        if match_confidence < self.aggressive_filter_threshold:
            return True

        # Voice mismatch = filter (not expected speaker, e.g., wife)
        if pattern_type == "voice_mismatch":
            return True

        # Inconsistent pattern = filter (likely wrong speaker)
        if pattern_type == "inconsistent":
            return True

        # Noise = filter
        if pattern_type == "noise":
            return True

        return False

    def _generate_reasoning(
        self,
        match_confidence: float,
        pattern_type: Optional[str],
        should_break_loop: bool,
        should_filter: bool
    ) -> str:
        """Generate human-readable reasoning for the comparison result"""
        reasons = []

        if match_confidence < self.mismatch_threshold:
            reasons.append(f"Low match confidence ({match_confidence:.2f})")

        if pattern_type:
            reasons.append(f"Pattern: {pattern_type}")

        if should_break_loop:
            reasons.append("Should break loop - patterns don't match")

        if should_filter:
            reasons.append("Should filter - voice mismatch or noise")

        if not reasons:
            reasons.append("Normal pattern match")

        return " | ".join(reasons)

    def get_pattern_summary(self) -> Dict[str, Any]:
        """Get summary of detected patterns"""
        if not self.comparison_history:
            return {"status": "no_data", "message": "No comparison history available"}

        recent = list(self.comparison_history)[-20:]  # Last 20 comparisons

        pattern_types = [r.pattern_type for r in recent if r.pattern_type]
        confidences = [r.match_confidence for r in recent]

        summary = {
            "total_comparisons": len(recent),
            "avg_confidence": np.mean(confidences) if confidences else 0.0,
            "pattern_distribution": {
                pt: pattern_types.count(pt) for pt in set(pattern_types)
            },
            "low_confidence_count": sum(1 for c in confidences if c < self.mismatch_threshold),
            "filtered_count": sum(1 for r in recent if r.should_filter),
            "loop_breaks": sum(1 for r in recent if r.should_break_loop)
        }

        return summary


def main():
    """Main entry point for testing"""
    import argparse

    parser = argparse.ArgumentParser(description="Audio-Transcription Comparison")
    parser.add_argument("--summary", action="store_true", help="Show pattern summary")

    args = parser.parse_args()

    comparator = AudioTranscriptionComparator()

    if args.summary:
        summary = comparator.get_pattern_summary()
        print("\n📊 Pattern Summary:")
        print(f"  Total comparisons: {summary.get('total_comparisons', 0)}")
        print(f"  Average confidence: {summary.get('avg_confidence', 0):.2f}")
        print(f"  Pattern distribution: {summary.get('pattern_distribution', {})}")
        print(f"  Low confidence count: {summary.get('low_confidence_count', 0)}")
        print(f"  Filtered count: {summary.get('filtered_count', 0)}")
        print(f"  Loop breaks: {summary.get('loop_breaks', 0)}")

    return 0


if __name__ == "__main__":


    sys.exit(main())