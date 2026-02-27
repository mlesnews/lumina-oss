"""
Multi-level circuit breaker with threshold-based state transitions.

A fail-closed state machine that monitors system metrics and automatically
transitions between safety levels. Defaults to YELLOW (caution) on startup,
not GREEN — because an untested system should not be trusted.

Levels:
    GREEN:  All clear — normal operations
    YELLOW: Caution — reduce exposure
    ORANGE: Restricted — close-only, no new positions
    RED:    Halted — all operations stopped
    BLACK:  Emergency — system shutdown, manual restart required

Pattern extracted from production: agents/safety/circuit_breaker.py

Example:
    cb = CircuitBreaker(
        thresholds={
            Level.YELLOW: {"error_rate": 0.05},
            Level.RED: {"error_rate": 0.20},
        }
    )
    level, reason = cb.check({"error_rate": 0.15})
    print(f"{level.name}: {reason}")
    print(f"Can proceed: {cb.can_proceed()}")
"""

import json
import logging
import time
from enum import IntEnum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class Level(IntEnum):
    """Circuit breaker levels (higher = more severe)."""
    GREEN = 0
    YELLOW = 1
    ORANGE = 2
    RED = 3
    BLACK = 4


# Default threshold config
DEFAULT_THRESHOLDS: Dict[Level, Dict[str, float]] = {
    Level.YELLOW: {"error_rate": 0.05, "loss_pct": 2.0},
    Level.ORANGE: {"error_rate": 0.10, "loss_pct": 5.0},
    Level.RED: {"error_rate": 0.20, "loss_pct": 10.0},
    Level.BLACK: {"error_rate": 0.50, "loss_pct": 20.0},
}


class CircuitBreaker:
    """
    Threshold-based circuit breaker state machine.

    Args:
        thresholds: Dict mapping Level to metric thresholds.
            Each threshold dict maps metric name to maximum allowed value.
        state_file: Optional path to persist state across restarts.
        default_level: Starting level (YELLOW = fail-closed default).
    """

    def __init__(
        self,
        thresholds: Optional[Dict[Level, Dict[str, float]]] = None,
        state_file: Optional[Path] = None,
        default_level: Level = Level.YELLOW,
    ):
        self._thresholds = thresholds or DEFAULT_THRESHOLDS
        self._state_file = state_file
        self._level = default_level
        self._last_transition = time.time()
        self._history: List[Dict[str, Any]] = []

        if state_file:
            self._load_state()

    @property
    def level(self) -> Level:
        """Current circuit breaker level."""
        return self._level

    def check(self, metrics: Dict[str, float]) -> Tuple[Level, str]:
        """
        Evaluate metrics against thresholds.

        Checks from BLACK (most severe) down to YELLOW. Returns the highest
        triggered level, or GREEN if no thresholds are breached.

        Args:
            metrics: Dict of metric_name -> current_value.

        Returns:
            Tuple of (level, reason_string).
        """
        for severity in [Level.BLACK, Level.RED, Level.ORANGE, Level.YELLOW]:
            threshold = self._thresholds.get(severity, {})
            for metric_name, max_value in threshold.items():
                current = metrics.get(metric_name, 0.0)
                if current >= max_value:
                    reason = (
                        f"{metric_name}={current:.4f} >= {max_value:.4f}"
                    )
                    self._transition(severity, reason)
                    return severity, reason

        self._transition(Level.GREEN, "All checks passed")
        return Level.GREEN, "All checks passed"

    def can_proceed(self) -> bool:
        """True if operations are allowed (GREEN or YELLOW)."""
        return self._level <= Level.YELLOW

    def is_restricted(self) -> bool:
        """True if in close-only mode (ORANGE)."""
        return self._level == Level.ORANGE

    def is_halted(self) -> bool:
        """True if all operations should stop (RED or BLACK)."""
        return self._level >= Level.RED

    def reset(self, level: Level = Level.GREEN) -> None:
        """Manually reset the circuit breaker level."""
        self._transition(level, "Manual reset")

    def _transition(self, new_level: Level, reason: str) -> None:
        """Record a state transition."""
        if new_level != self._level:
            logger.info(
                "Circuit breaker: %s -> %s (%s)",
                self._level.name, new_level.name, reason,
            )
            self._history.append({
                "from": self._level.name,
                "to": new_level.name,
                "reason": reason,
                "timestamp": time.time(),
            })
            self._level = new_level
            self._last_transition = time.time()
            if self._state_file:
                self._save_state()

    def _save_state(self) -> None:
        """Persist state to file."""
        if not self._state_file:
            return
        try:
            self._state_file.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "level": self._level.name,
                "last_transition": self._last_transition,
                "history": self._history[-50:],
            }
            self._state_file.write_text(json.dumps(data, indent=2))
        except OSError as exc:
            logger.warning("Failed to save CB state: %s", exc)

    def _load_state(self) -> None:
        """Load state from file."""
        if not self._state_file or not self._state_file.exists():
            return
        try:
            data = json.loads(self._state_file.read_text())
            level_name = data.get("level", "YELLOW")
            self._level = Level[level_name]
            self._last_transition = data.get("last_transition", time.time())
            self._history = data.get("history", [])
        except (json.JSONDecodeError, KeyError, OSError) as exc:
            logger.warning(
                "CB state file unreadable (%s) — defaulting to YELLOW", exc
            )
            self._level = Level.YELLOW
