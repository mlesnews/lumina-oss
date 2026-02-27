"""
Troubleshooting decorator and context tracker.

Provides a @troubleshoot decorator that wraps functions with automatic
symptom collection, step tracking, and resolution logging.

Example:
    tracker = TroubleshootTracker()

    @troubleshoot(tracker, issue="API latency spike")
    def investigate_latency(ctx):
        ctx.add_symptom("p99 > 500ms")
        ctx.add_step("Checked connection pool: saturated")
        ctx.add_step("Increased pool size from 10 to 50")
        return "Pool size increased, monitoring"

    result = investigate_latency()
    print(tracker.get_report())
"""

import functools
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class TroubleshootContext:
    """Context passed to troubleshooting functions."""
    issue: str
    symptoms: List[str] = field(default_factory=list)
    steps: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_symptom(self, symptom: str) -> None:
        self.symptoms.append(symptom)

    def add_step(self, step: str) -> None:
        self.steps.append(step)


@dataclass
class TroubleshootResult:
    """Result of a troubleshooting session."""
    issue: str
    resolution: Optional[str]
    symptoms: List[str]
    steps_taken: List[str]
    success: bool
    duration: float
    error: Optional[str] = None


class TroubleshootTracker:
    """Tracks troubleshooting sessions and their outcomes."""

    def __init__(self):
        self._sessions: List[TroubleshootResult] = []

    def record(self, result: TroubleshootResult) -> None:
        self._sessions.append(result)

    def get_report(self) -> Dict[str, Any]:
        total = len(self._sessions)
        successes = sum(1 for s in self._sessions if s.success)
        return {
            "total_sessions": total,
            "success_rate": successes / total if total > 0 else 0,
            "sessions": [
                {
                    "issue": s.issue,
                    "success": s.success,
                    "steps": len(s.steps_taken),
                    "duration": round(s.duration, 2),
                }
                for s in self._sessions[-10:]
            ],
        }

    @property
    def sessions(self) -> List[TroubleshootResult]:
        return list(self._sessions)


def troubleshoot(
    tracker: TroubleshootTracker,
    issue: str = "unspecified",
) -> Callable:
    """
    Decorator that wraps a function with troubleshooting context.

    The decorated function receives a TroubleshootContext as its first arg.

    Args:
        tracker: TroubleshootTracker instance to record results.
        issue: Description of the issue being troubleshot.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            ctx = TroubleshootContext(issue=issue)
            start = time.monotonic()

            try:
                resolution = func(ctx, *args, **kwargs)
                result = TroubleshootResult(
                    issue=issue,
                    resolution=str(resolution) if resolution else None,
                    symptoms=ctx.symptoms,
                    steps_taken=ctx.steps,
                    success=True,
                    duration=time.monotonic() - start,
                )
            except Exception as exc:
                result = TroubleshootResult(
                    issue=issue,
                    resolution=None,
                    symptoms=ctx.symptoms,
                    steps_taken=ctx.steps,
                    success=False,
                    duration=time.monotonic() - start,
                    error=str(exc),
                )
                raise
            finally:
                tracker.record(result)

            return resolution
        return wrapper
    return decorator
