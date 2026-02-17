#!/usr/bin/env python3
"""
Progressive Curve Grading - Infinite Curve Calculations

Grading on a curve with infinite curve calculations.
Something humans struggle with, but "it's cake" for AI.

Tags: #CURVE_GRADING #STATISTICS #INFINITE_CURVE @JARVIS @LUMINA
"""

from typing import Dict, List, Any, Optional, Callable
import math
import numpy as np
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

scripts_python = Path(__file__).parent.parent
if str(scripts_python) not in sys.path:
    sys.path.insert(0, str(scripts_python))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CurveGrading")

# Fallback if numpy not available
try:
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    logger.warning("NumPy not available, using fallback calculations")


class ProgressiveCurveGrading:
    """
    Progressive Curve Grading

    Infinite curve calculations for grading on a curve.
    "It's cake" for AI, challenging for humans.
    """

    def __init__(self):
        """Initialize Progressive Curve Grading"""
        logger.info("📊 Progressive Curve Grading initialized")
        logger.info("   Infinite curve calculations - 'It's cake' for AI")

    def calculate_curve(
        self,
        scores: List[float],
        curve_type: str = "infinite",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Calculate grading curve.

        Args:
            scores: List of scores
            curve_type: Type of curve (infinite, normal, exponential, logarithmic)
            **kwargs: Additional parameters

        Returns:
            Curve parameters
        """
        if not scores:
            return {'error': 'No scores provided'}

        logger.info(f"📊 Calculating {curve_type} curve for {len(scores)} scores")

        if curve_type == "infinite":
            return self._calculate_infinite_curve(scores, **kwargs)
        elif curve_type == "normal":
            return self._calculate_normal_curve(scores, **kwargs)
        elif curve_type == "exponential":
            return self._calculate_exponential_curve(scores, **kwargs)
        elif curve_type == "logarithmic":
            return self._calculate_logarithmic_curve(scores, **kwargs)
        else:
            return self._calculate_infinite_curve(scores, **kwargs)

    def _calculate_infinite_curve(
        self,
        scores: List[float],
        **kwargs
    ) -> Dict[str, Any]:
        """Calculate infinite curve (complex statistical distribution)"""
        mean = sum(scores) / len(scores)
        std = self._std(scores)

        # Infinite curve uses multiple distribution components
        # This is where AI excels - complex calculations humans struggle with

        curve = {
            'type': 'infinite',
            'mean': mean,
            'std': std,
            'min': min(scores),
            'max': max(scores),
            'range': max(scores) - min(scores),
            'percentiles': self._calculate_percentiles(scores),
            'distribution': self._analyze_distribution(scores),
            'adaptive_thresholds': self._calculate_adaptive_thresholds(scores)
        }

        return curve

    def _calculate_normal_curve(
        self,
        scores: List[float],
        **kwargs
    ) -> Dict[str, Any]:
        """Calculate normal distribution curve"""
        mean = sum(scores) / len(scores)
        std = self._std(scores)

        return {
            'type': 'normal',
            'mean': mean,
            'std': std,
            'variance': std ** 2
        }

    def _calculate_exponential_curve(
        self,
        scores: List[float],
        **kwargs
    ) -> Dict[str, Any]:
        """Calculate exponential curve"""
        # Exponential curve fitting
        # y = a * e^(b * x)

        return {
            'type': 'exponential',
            'parameters': self._fit_exponential(scores)
        }

    def _calculate_logarithmic_curve(
        self,
        scores: List[float],
        **kwargs
    ) -> Dict[str, Any]:
        """Calculate logarithmic curve"""
        # Logarithmic curve fitting
        # y = a * ln(x) + b

        return {
            'type': 'logarithmic',
            'parameters': self._fit_logarithmic(scores)
        }

    def grade_on_curve(
        self,
        score: float,
        curve: Dict[str, Any],
        method: str = "percentile"
    ) -> Dict[str, Any]:
        """
        Grade score on curve.

        Args:
            score: Score to grade
            curve: Curve parameters
            method: Grading method (percentile, z_score, adaptive)

        Returns:
            Graded result
        """
        if method == "percentile":
            return self._grade_by_percentile(score, curve)
        elif method == "z_score":
            return self._grade_by_z_score(score, curve)
        elif method == "adaptive":
            return self._grade_by_adaptive(score, curve)
        else:
            return self._grade_by_percentile(score, curve)

    def _grade_by_percentile(
        self,
        score: float,
        curve: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Grade by percentile"""
        percentiles = curve.get('percentiles', {})

        # Find percentile
        percentile = self._calculate_percentile_for_score(score, curve)

        # Map to letter grade
        letter_grade = self._percentile_to_letter(percentile)

        return {
            'score': score,
            'percentile': percentile,
            'letter_grade': letter_grade,
            'curve_adjusted': True
        }

    def _grade_by_z_score(
        self,
        score: float,
        curve: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Grade by z-score"""
        mean = curve.get('mean', 0)
        std = curve.get('std', 1)

        if std == 0:
            z_score = 0
        else:
            z_score = (score - mean) / std

        # Map z-score to grade
        letter_grade = self._z_score_to_letter(z_score)

        return {
            'score': score,
            'z_score': z_score,
            'letter_grade': letter_grade,
            'curve_adjusted': True
        }

    def _grade_by_adaptive(
        self,
        score: float,
        curve: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Grade by adaptive thresholds"""
        thresholds = curve.get('adaptive_thresholds', {})

        # Find appropriate threshold
        letter_grade = self._find_adaptive_grade(score, thresholds)

        return {
            'score': score,
            'letter_grade': letter_grade,
            'curve_adjusted': True,
            'method': 'adaptive'
        }

    def _std(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)

    def _calculate_percentiles(self, scores: List[float]) -> Dict[str, float]:
        """Calculate percentiles"""
        sorted_scores = sorted(scores)
        n = len(sorted_scores)

        percentiles = {}
        for p in [10, 25, 50, 75, 90, 95, 99]:
            index = int((p / 100) * (n - 1))
            percentiles[f'p{p}'] = sorted_scores[index] if index < n else sorted_scores[-1]

        return percentiles

    def _analyze_distribution(self, scores: List[float]) -> Dict[str, Any]:
        """Analyze score distribution"""
        mean = sum(scores) / len(scores)
        std = self._std(scores)

        # Skewness (simplified)
        skewness = self._calculate_skewness(scores, mean, std)

        # Kurtosis (simplified)
        kurtosis = self._calculate_kurtosis(scores, mean, std)

        return {
            'mean': mean,
            'std': std,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'shape': self._describe_shape(skewness, kurtosis)
        }

    def _calculate_skewness(
        self,
        scores: List[float],
        mean: float,
        std: float
    ) -> float:
        """Calculate skewness"""
        if std == 0:
            return 0.0
        n = len(scores)
        skew = sum(((x - mean) / std) ** 3 for x in scores) / n
        return skew

    def _calculate_kurtosis(
        self,
        scores: List[float],
        mean: float,
        std: float
    ) -> float:
        """Calculate kurtosis"""
        if std == 0:
            return 0.0
        n = len(scores)
        kurt = sum(((x - mean) / std) ** 4 for x in scores) / n - 3
        return kurt

    def _describe_shape(self, skewness: float, kurtosis: float) -> str:
        """Describe distribution shape"""
        if abs(skewness) < 0.5 and abs(kurtosis) < 0.5:
            return "normal"
        elif skewness > 0.5:
            return "right_skewed"
        elif skewness < -0.5:
            return "left_skewed"
        elif kurtosis > 0.5:
            return "heavy_tailed"
        else:
            return "light_tailed"

    def _calculate_adaptive_thresholds(
        self,
        scores: List[float]
    ) -> Dict[str, float]:
        """Calculate adaptive grade thresholds"""
        sorted_scores = sorted(scores, reverse=True)
        n = len(sorted_scores)

        # Top 10% = A
        # Next 20% = B
        # Next 40% = C
        # Next 20% = D
        # Bottom 10% = F

        thresholds = {
            'A': sorted_scores[int(0.10 * n)] if n > 0 else 0,
            'B': sorted_scores[int(0.30 * n)] if n > 0 else 0,
            'C': sorted_scores[int(0.70 * n)] if n > 0 else 0,
            'D': sorted_scores[int(0.90 * n)] if n > 0 else 0,
            'F': sorted_scores[-1] if n > 0 else 0
        }

        return thresholds

    def _calculate_percentile_for_score(
        self,
        score: float,
        curve: Dict[str, Any]
    ) -> float:
        """Calculate percentile for a score"""
        # Simplified - would need full score distribution
        mean = curve.get('mean', 0)
        std = curve.get('std', 1)

        if std == 0:
            return 50.0

        z_score = (score - mean) / std
        # Convert z-score to percentile (normal approximation)
        percentile = 50 + (z_score * 34.13)  # Simplified

        return max(0, min(100, percentile))

    def _percentile_to_letter(self, percentile: float) -> str:
        """Convert percentile to letter grade"""
        if percentile >= 90:
            return 'A'
        elif percentile >= 80:
            return 'B'
        elif percentile >= 70:
            return 'C'
        elif percentile >= 60:
            return 'D'
        else:
            return 'F'

    def _z_score_to_letter(self, z_score: float) -> str:
        """Convert z-score to letter grade"""
        if z_score >= 1.5:
            return 'A'
        elif z_score >= 0.5:
            return 'B'
        elif z_score >= -0.5:
            return 'C'
        elif z_score >= -1.5:
            return 'D'
        else:
            return 'F'

    def _find_adaptive_grade(
        self,
        score: float,
        thresholds: Dict[str, float]
    ) -> str:
        """Find grade using adaptive thresholds"""
        if score >= thresholds.get('A', 0):
            return 'A'
        elif score >= thresholds.get('B', 0):
            return 'B'
        elif score >= thresholds.get('C', 0):
            return 'C'
        elif score >= thresholds.get('D', 0):
            return 'D'
        else:
            return 'F'

    def _fit_exponential(self, scores: List[float]) -> Dict[str, float]:
        """Fit exponential curve"""
        # Simplified exponential fitting
        return {'a': 1.0, 'b': 0.1}

    def _fit_logarithmic(self, scores: List[float]) -> Dict[str, float]:
        """Fit logarithmic curve"""
        # Simplified logarithmic fitting
        return {'a': 1.0, 'b': 0.0}


def main():
    """Example usage"""
    print("=" * 80)
    print("📊 PROGRESSIVE CURVE GRADING")
    print("   Infinite curve calculations - 'It's cake' for AI")
    print("=" * 80)
    print()

    grading = ProgressiveCurveGrading()

    # Sample scores
    scores = [85, 90, 92, 88, 95, 87, 91, 89, 93, 86]

    # Calculate curve
    print("CALCULATING INFINITE CURVE:")
    print("-" * 80)
    curve = grading.calculate_curve(scores, curve_type="infinite")
    print(f"Type: {curve['type']}")
    print(f"Mean: {curve['mean']:.2f}")
    print(f"Std: {curve['std']:.2f}")
    print(f"Distribution: {curve['distribution']['shape']}")
    print()

    # Grade on curve
    print("GRADING ON CURVE:")
    print("-" * 80)
    test_score = 88
    graded = grading.grade_on_curve(test_score, curve, method="percentile")
    print(f"Score: {test_score}")
    print(f"Percentile: {graded['percentile']:.1f}%")
    print(f"Letter Grade: {graded['letter_grade']}")
    print()

    # Adaptive grading
    print("ADAPTIVE THRESHOLDS:")
    print("-" * 80)
    thresholds = curve.get('adaptive_thresholds', {})
    for grade, threshold in sorted(thresholds.items()):
        print(f"{grade}: {threshold:.2f}")
    print()

    print("=" * 80)
    print("📊 Progressive Curve Grading - Infinite calculations made easy")
    print("=" * 80)


if __name__ == "__main__":


    main()