"""
Weighted dimension health scoring.

A pluggable health aggregator that scores a system across N weighted dimensions
and produces a readiness label. Each dimension is scored 0.0-1.0 independently,
then combined via weighted sum into a single percentage.

Pattern extracted from production: confidence_aggregator.py

Example:
    agg = HealthAggregator(
        dimensions={"uptime": 0.4, "error_rate": 0.3, "latency": 0.3},
        thresholds={"CRITICAL": 40, "DEGRADED": 60, "HEALTHY": 80},
    )

    agg.score("uptime", 0.95, "99.5% uptime last 24h")
    agg.score("error_rate", 0.8, "2% error rate")
    agg.score("latency", 0.6, "p99=450ms")

    report = agg.evaluate()
    print(f"{report.label}: {report.score_pct:.1f}%")
"""

import logging
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Default thresholds (percentage boundaries)
DEFAULT_THRESHOLDS = {
    "CRITICAL": 40.0,
    "DEGRADED": 60.0,
    "HEALTHY": 80.0,
}


@dataclass
class DimensionScore:
    """Score for a single health dimension."""
    name: str
    score: float          # 0.0 - 1.0
    weight: float
    weighted: float       # score * weight
    detail: str           # Human-readable explanation


@dataclass
class HealthReport:
    """Aggregated health report across all dimensions."""
    score_pct: float
    label: str
    dimensions: List[DimensionScore]
    timestamp: float = field(default_factory=time.time)
    recommendation: str = ""

    def to_dict(self) -> dict:
        return {
            "score_pct": round(self.score_pct, 2),
            "label": self.label,
            "dimensions": [asdict(d) for d in self.dimensions],
            "timestamp": self.timestamp,
            "recommendation": self.recommendation,
        }


class HealthAggregator:
    """
    Pluggable weighted-dimension health scorer.

    Args:
        dimensions: Dict mapping dimension name to weight (must sum to 1.0).
        thresholds: Dict mapping label to minimum percentage.
            Labels are applied in ascending order: score < lowest = worst label.
    """

    def __init__(
        self,
        dimensions: Dict[str, float],
        thresholds: Optional[Dict[str, float]] = None,
    ):
        total = sum(dimensions.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(
                f"Dimension weights must sum to 1.0, got {total:.4f}"
            )
        self._weights = dict(dimensions)
        self._thresholds = thresholds or DEFAULT_THRESHOLDS
        self._scores: Dict[str, DimensionScore] = {}
        self._history: List[float] = []

    def score(self, name: str, value: float, detail: str = "") -> DimensionScore:
        """
        Set the score for a dimension.

        Args:
            name: Dimension name (must be registered in weights).
            value: Score from 0.0 to 1.0.
            detail: Human-readable explanation.

        Returns:
            The DimensionScore object.

        Raises:
            KeyError: If dimension name not in registered weights.
        """
        if name not in self._weights:
            raise KeyError(
                f"Unknown dimension '{name}'. "
                f"Registered: {list(self._weights.keys())}"
            )
        value = max(0.0, min(1.0, value))
        weight = self._weights[name]
        dim = DimensionScore(
            name=name,
            score=value,
            weight=weight,
            weighted=value * weight,
            detail=detail,
        )
        self._scores[name] = dim
        return dim

    def evaluate(self) -> HealthReport:
        """
        Compute the aggregate health score and return a report.

        Dimensions without scores are treated as 0.0.
        """
        dimensions = []
        for name, weight in self._weights.items():
            if name in self._scores:
                dimensions.append(self._scores[name])
            else:
                dimensions.append(DimensionScore(
                    name=name, score=0.0, weight=weight,
                    weighted=0.0, detail="No data",
                ))

        score_pct = sum(d.weighted for d in dimensions) * 100.0
        score_pct = max(0.0, min(100.0, score_pct))

        # Determine label from thresholds (ascending order)
        sorted_thresholds = sorted(self._thresholds.items(), key=lambda x: x[1])
        label = sorted_thresholds[0][0]  # Worst label as default
        for lbl, minimum in sorted_thresholds:
            if score_pct >= minimum:
                label = lbl

        self._history.append(score_pct)
        if len(self._history) > 100:
            self._history = self._history[-100:]

        return HealthReport(
            score_pct=score_pct,
            label=label,
            dimensions=dimensions,
            recommendation=self._recommend(label, dimensions),
        )

    def get_trend(self) -> str:
        """Get trend from recent history: improving, declining, or stable."""
        if len(self._history) < 3:
            return "insufficient_data"
        recent = self._history[-5:]
        if all(recent[i] <= recent[i + 1] for i in range(len(recent) - 1)):
            return "improving"
        if all(recent[i] >= recent[i + 1] for i in range(len(recent) - 1)):
            return "declining"
        return "stable"

    def _recommend(self, label: str, dimensions: List[DimensionScore]) -> str:
        """Generate a recommendation based on weakest dimensions."""
        weakest = sorted(dimensions, key=lambda d: d.score)[:3]
        weak_names = [d.name for d in weakest if d.score < 0.5]
        if not weak_names:
            return f"System is {label}. All dimensions above 50%."
        return (
            f"System is {label}. "
            f"Focus on: {', '.join(weak_names)} (below 50%)."
        )


if __name__ == "__main__":
    # Quick demo
    agg = HealthAggregator(
        dimensions={"uptime": 0.3, "errors": 0.3, "latency": 0.2, "throughput": 0.2},
    )
    agg.score("uptime", 0.95, "99.5% uptime")
    agg.score("errors", 0.8, "2% error rate")
    agg.score("latency", 0.6, "p99=450ms")
    agg.score("throughput", 0.9, "950 req/s")

    report = agg.evaluate()
    print(f"Health: {report.score_pct:.1f}% [{report.label}]")
    for d in report.dimensions:
        print(f"  {d.name}: {d.score:.0%} (weight={d.weight:.0%}) — {d.detail}")
    print(f"Recommendation: {report.recommendation}")
