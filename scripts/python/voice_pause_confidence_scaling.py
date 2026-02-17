#!/usr/bin/env python3
"""
Confidence-Based Dynamic Listening Scaling

Scales pause detection wait time based on transcription confidence.
Higher confidence = shorter wait time, lower confidence = longer wait time.

Tags: #VOICE_PAUSE #CONFIDENCE #DYNAMIC_SCALING #IMPROVEMENT @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import math

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

logger = get_logger("VoicePauseConfidenceScaling")


@dataclass
class ConfidenceScalingResult:
    """Result of confidence-based scaling"""
    wait_time: float
    base_wait_time: float
    confidence: float
    scaling_factor: float
    reasoning: str


class ConfidenceBasedPauseScaling:
    """
    Confidence-Based Dynamic Listening Scaling

    Adjusts pause detection wait time based on:
    - Transcription confidence
    - Historical confidence patterns
    - Context (question vs statement)
    - User patterns
    """

    def __init__(
        self,
        project_root: Optional[Path] = None,
        base_wait_time: float = 1.5,
        min_wait_time: float = 0.5,
        max_wait_time: float = 8.0
    ):
        """Initialize confidence-based scaling"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.base_wait_time = base_wait_time
        self.min_wait_time = min_wait_time
        self.max_wait_time = max_wait_time

        # Confidence thresholds
        self.high_confidence_threshold = 0.8  # 80%+ = high confidence
        self.medium_confidence_threshold = 0.5  # 50-80% = medium
        self.low_confidence_threshold = 0.3  # 30-50% = low
        # Below 30% = very low

        # Scaling factors (how much to adjust wait time)
        self.high_confidence_factor = 0.6  # Reduce wait time by 40%
        self.medium_confidence_factor = 1.0  # No change
        self.low_confidence_factor = 1.5  # Increase wait time by 50%
        self.very_low_confidence_factor = 2.0  # Double wait time

        # History tracking
        self.confidence_history: list[float] = []
        self.wait_time_history: list[float] = []

        logger.info("✅ Confidence-Based Pause Scaling initialized")
        logger.info(f"   Base wait time: {base_wait_time}s")
        logger.info(f"   Range: {min_wait_time}s - {max_wait_time}s")

    def calculate_wait_time(
        self,
        confidence: float,
        transcription_text: Optional[str] = None,
        is_question: bool = False
    ) -> ConfidenceScalingResult:
        """
        Calculate wait time based on confidence

        Args:
            confidence: Transcription confidence (0.0-1.0)
            transcription_text: Transcribed text (for context)
            is_question: Whether this is a question (needs longer wait)

        Returns:
            ConfidenceScalingResult with calculated wait time
        """
        # Clamp confidence to valid range
        confidence = max(0.0, min(1.0, confidence))

        # Determine scaling factor based on confidence
        if confidence >= self.high_confidence_threshold:
            scaling_factor = self.high_confidence_factor
            confidence_level = "high"
        elif confidence >= self.medium_confidence_threshold:
            scaling_factor = self.medium_confidence_factor
            confidence_level = "medium"
        elif confidence >= self.low_confidence_threshold:
            scaling_factor = self.low_confidence_factor
            confidence_level = "low"
        else:
            scaling_factor = self.very_low_confidence_factor
            confidence_level = "very_low"

        # Adjust for questions (questions often need longer wait for response)
        if is_question:
            scaling_factor *= 1.2  # 20% longer for questions

        # Calculate wait time
        wait_time = self.base_wait_time * scaling_factor

        # Apply min/max bounds
        wait_time = max(self.min_wait_time, min(self.max_wait_time, wait_time))

        # Generate reasoning
        reasoning = (
            f"Confidence: {confidence:.1%} ({confidence_level}) → "
            f"scaling factor: {scaling_factor:.2f} → "
            f"wait time: {wait_time:.2f}s"
        )
        if is_question:
            reasoning += " (question - extended wait)"

        result = ConfidenceScalingResult(
            wait_time=wait_time,
            base_wait_time=self.base_wait_time,
            confidence=confidence,
            scaling_factor=scaling_factor,
            reasoning=reasoning
        )

        # Update history
        self.confidence_history.append(confidence)
        self.wait_time_history.append(wait_time)

        # Keep history size manageable
        if len(self.confidence_history) > 100:
            self.confidence_history.pop(0)
            self.wait_time_history.pop(0)

        # Adaptive base wait time (learn from patterns)
        self._adapt_base_wait_time()

        logger.debug(f"   {reasoning}")

        return result

    def _adapt_base_wait_time(self):
        """Adapt base wait time based on historical patterns"""

        # Only adapt if we have enough data
        if len(self.confidence_history) < 20:
            return

        # Calculate average confidence and wait time
        avg_confidence = sum(self.confidence_history[-50:]) / len(self.confidence_history[-50:])
        avg_wait_time = sum(self.wait_time_history[-50:]) / len(self.wait_time_history[-50:])

        # If average confidence is high and average wait time is too long,
        # reduce base wait time
        if avg_confidence > 0.7 and avg_wait_time > self.base_wait_time * 1.2:
            self.base_wait_time *= 0.95  # Reduce by 5%
            self.base_wait_time = max(self.min_wait_time, self.base_wait_time)
            logger.debug(f"   📉 Reduced base wait time to {self.base_wait_time:.2f}s (high confidence pattern)")

        # If average confidence is low and average wait time is too short,
        # increase base wait time
        elif avg_confidence < 0.4 and avg_wait_time < self.base_wait_time * 0.8:
            self.base_wait_time *= 1.05  # Increase by 5%
            self.base_wait_time = min(self.max_wait_time, self.base_wait_time)
            logger.debug(f"   📈 Increased base wait time to {self.base_wait_time:.2f}s (low confidence pattern)")

    def get_statistics(self) -> Dict[str, Any]:
        """Get scaling statistics"""
        if not self.confidence_history:
            return {
                "total_samples": 0,
                "avg_confidence": 0.0,
                "avg_wait_time": 0.0,
                "base_wait_time": self.base_wait_time
            }

        return {
            "total_samples": len(self.confidence_history),
            "avg_confidence": sum(self.confidence_history) / len(self.confidence_history),
            "avg_wait_time": sum(self.wait_time_history) / len(self.wait_time_history),
            "base_wait_time": self.base_wait_time,
            "min_wait_time": self.min_wait_time,
            "max_wait_time": self.max_wait_time
        }


def main():
    """Test confidence-based scaling"""
    scaler = ConfidenceBasedPauseScaling(base_wait_time=1.5)

    print("\n🧪 Testing Confidence-Based Pause Scaling")
    print("=" * 80)

    test_cases = [
        (0.95, False, "High confidence statement"),
        (0.75, False, "Medium-high confidence statement"),
        (0.50, False, "Medium confidence statement"),
        (0.25, False, "Low confidence statement"),
        (0.10, False, "Very low confidence statement"),
        (0.90, True, "High confidence question"),
        (0.30, True, "Low confidence question"),
    ]

    for confidence, is_question, description in test_cases:
        result = scaler.calculate_wait_time(confidence, is_question=is_question)
        print(f"\n{description}:")
        print(f"   Confidence: {confidence:.1%}")
        print(f"   Is Question: {is_question}")
        print(f"   Wait Time: {result.wait_time:.2f}s")
        print(f"   Scaling Factor: {result.scaling_factor:.2f}")
        print(f"   Reasoning: {result.reasoning}")

    print("\n" + "=" * 80)
    stats = scaler.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"   Total Samples: {stats['total_samples']}")
    print(f"   Average Confidence: {stats['avg_confidence']:.1%}")
    print(f"   Average Wait Time: {stats['avg_wait_time']:.2f}s")
    print(f"   Base Wait Time: {stats['base_wait_time']:.2f}s")


if __name__ == "__main__":


    main()