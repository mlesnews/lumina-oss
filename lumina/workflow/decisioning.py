"""
Context scoring and threshold-based decisioning.

Tracks questions and context, computes a score, and decides whether to
proceed autonomously or ask for human input based on a threshold.

Pattern extracted from production: decisioning_troubleshooting_system.py

Example:
    engine = DecisionEngine(threshold=0.7)
    engine.add_context("error", "API returning 500s")
    engine.add_context("logs", "Connection timeout in worker pool")

    result = engine.decide("Should we restart the service?")
    if result.needs_human:
        print(f"ASK: confidence {result.score:.2f} < {engine.threshold}")
    else:
        print(f"PROCEED: {result.decision}")
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ContextEntry:
    """A piece of context relevant to a decision."""
    category: str
    content: str
    weight: float = 1.0
    timestamp: float = field(default_factory=time.time)


@dataclass
class DecisionResult:
    """Outcome of a decisioning evaluation."""
    question: str
    score: float
    threshold: float
    needs_human: bool
    decision: str
    rationale: str
    context_entries: int
    timestamp: float = field(default_factory=time.time)


class DecisionEngine:
    """
    Context-score threshold decisioning engine.

    Accumulates context entries, scores them, and determines whether the
    system has enough information to proceed autonomously or needs to ask.

    Args:
        threshold: Minimum score to proceed without asking (0.0-1.0).
        weights: Optional dict mapping category names to weight multipliers.
    """

    def __init__(
        self,
        threshold: float = 0.7,
        weights: Optional[Dict[str, float]] = None,
    ):
        self.threshold = threshold
        self._weights = weights or {}
        self._context: List[ContextEntry] = []
        self._history: List[DecisionResult] = []

    def add_context(
        self,
        category: str,
        content: str,
        weight: Optional[float] = None,
    ) -> None:
        """
        Add a context entry for future decisions.

        Args:
            category: Type of context (e.g., "error", "logs", "user_input").
            content: The context text.
            weight: Override weight (default: use category weight or 1.0).
        """
        w = weight or self._weights.get(category, 1.0)
        self._context.append(ContextEntry(
            category=category, content=content, weight=w,
        ))

    def decide(self, question: str) -> DecisionResult:
        """
        Evaluate accumulated context and decide whether to proceed or ask.

        Args:
            question: The question or action being considered.

        Returns:
            DecisionResult with score, threshold comparison, and decision.
        """
        score = self._compute_score(question)
        needs_human = score < self.threshold

        if needs_human:
            decision = "ASK"
            rationale = (
                f"Context score {score:.2f} below threshold {self.threshold}. "
                f"Need more information or human confirmation."
            )
        else:
            decision = "PROCEED"
            rationale = (
                f"Context score {score:.2f} meets threshold {self.threshold}. "
                f"Sufficient context to proceed autonomously."
            )

        result = DecisionResult(
            question=question,
            score=score,
            threshold=self.threshold,
            needs_human=needs_human,
            decision=decision,
            rationale=rationale,
            context_entries=len(self._context),
        )
        self._history.append(result)
        return result

    def clear_context(self) -> None:
        """Clear all accumulated context."""
        self._context.clear()

    def _compute_score(self, question: str) -> float:
        """
        Compute a context score based on accumulated entries.

        Scoring factors:
        - Base: 0.3 if any context exists
        - Quantity: more context entries = higher score (diminishing returns)
        - Relevance: keyword overlap between question and context
        - Weight: weighted average of entry weights
        """
        if not self._context:
            return 0.0

        # Base score for having context
        score = 0.3

        # Quantity factor (logarithmic diminishing returns)
        import math
        quantity_bonus = min(0.2, 0.1 * math.log1p(len(self._context)))
        score += quantity_bonus

        # Relevance: keyword overlap
        q_words = set(question.lower().split())
        total_overlap = 0
        for entry in self._context:
            c_words = set(entry.content.lower().split())
            overlap = len(q_words & c_words)
            total_overlap += overlap * entry.weight

        relevance_bonus = min(0.3, total_overlap * 0.05)
        score += relevance_bonus

        # Weight average
        avg_weight = sum(e.weight for e in self._context) / len(self._context)
        weight_bonus = min(0.2, (avg_weight - 1.0) * 0.1) if avg_weight > 1.0 else 0
        score += weight_bonus

        return min(1.0, score)

    @property
    def history(self) -> List[DecisionResult]:
        return list(self._history)
