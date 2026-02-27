"""
Triple-verification pattern (v3).

Runs a value through three independent verification methods and requires
consensus before accepting. Protects against single-source errors.

Example:
    v = Verifier()
    v.add_method("range_check", lambda x: 0 < x < 100)
    v.add_method("type_check", lambda x: isinstance(x, (int, float)))
    v.add_method("sanity_check", lambda x: x != 42)

    result = v.verify(50)
    print(f"Verified: {result.passed} ({result.pass_count}/{result.total})")
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class VerificationResult:
    """Result of running all verification methods."""
    value: Any
    passed: bool
    pass_count: int
    total: int
    required: int
    details: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def consensus_pct(self) -> float:
        return self.pass_count / self.total if self.total > 0 else 0.0


class Verifier:
    """
    Triple-verification (or N-verification) system.

    Args:
        required: Minimum methods that must pass (default: all registered).
    """

    def __init__(self, required: Optional[int] = None):
        self._methods: List[Dict[str, Any]] = []
        self._required = required

    def add_method(self, name: str, checker: Callable[[Any], bool]) -> None:
        """Register a verification method."""
        self._methods.append({"name": name, "checker": checker})

    def verify(self, value: Any) -> VerificationResult:
        """
        Run all verification methods against a value.

        Args:
            value: The value to verify.

        Returns:
            VerificationResult with consensus details.
        """
        required = self._required or len(self._methods)
        details = []
        pass_count = 0

        for method in self._methods:
            try:
                ok = method["checker"](value)
                details.append({
                    "name": method["name"],
                    "passed": bool(ok),
                    "error": None,
                })
                if ok:
                    pass_count += 1
            except Exception as exc:
                details.append({
                    "name": method["name"],
                    "passed": False,
                    "error": str(exc),
                })

        return VerificationResult(
            value=value,
            passed=pass_count >= required,
            pass_count=pass_count,
            total=len(self._methods),
            required=required,
            details=details,
        )
