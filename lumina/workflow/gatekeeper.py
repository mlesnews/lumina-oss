"""
Quality gate with spectrum-based audit (ZUUL pattern).

A gatekeeper that audits artifacts through a color-coded spectrum:
    RED:    Errors — blocks completion
    ORANGE: Warnings — needs resolution
    CYAN:   Uncommitted — needs commit
    BLUE:   Suggestions — review recommended
    GREY:   Unchanged — no action needed
    GREEN:  Satisfied — safe to proceed

Precedence: RED > ORANGE > CYAN > BLUE > GREY > GREEN

Pattern extracted from production: lumina_core/gatekeeper/zuul.py

Example:
    gk = Gatekeeper()
    gk.add_check("syntax", GateColor.RED, lambda: check_syntax())
    gk.add_check("todos", GateColor.ORANGE, lambda: find_todos())

    result = gk.audit()
    print(f"Status: {result.status.name}")
    if result.can_proceed:
        print("Safe to proceed")
"""

import logging
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class GateColor(IntEnum):
    """Quality spectrum colors (higher = more severe)."""
    GREEN = 0
    GREY = 1
    BLUE = 2
    CYAN = 3
    ORANGE = 4
    RED = 5


@dataclass
class Finding:
    """A single audit finding."""
    check_name: str
    color: GateColor
    message: str


@dataclass
class AuditResult:
    """Result of a gatekeeper audit."""
    status: GateColor
    findings: List[Finding] = field(default_factory=list)
    checks_run: int = 0
    timestamp: str = ""

    @property
    def can_proceed(self) -> bool:
        """True if status is GREEN or GREY (no blockers)."""
        return self.status <= GateColor.GREY

    @property
    def needs_commit(self) -> bool:
        """True if there are uncommitted changes."""
        return any(f.color == GateColor.CYAN for f in self.findings)

    @property
    def has_errors(self) -> bool:
        return any(f.color == GateColor.RED for f in self.findings)

    @property
    def has_warnings(self) -> bool:
        return any(f.color == GateColor.ORANGE for f in self.findings)

    def summary(self) -> str:
        """One-line summary of the audit."""
        counts = {}
        for f in self.findings:
            counts[f.color.name] = counts.get(f.color.name, 0) + 1
        parts = [f"{name}={count}" for name, count in sorted(counts.items())]
        return f"{self.status.name}: {', '.join(parts) or 'clean'}"


class Gatekeeper:
    """
    Quality gate that runs registered checks and produces an audit result.

    Checks are callables that return a list of (message, color) tuples,
    or an empty list if passing.

    Args:
        name: Name of this gatekeeper instance.
    """

    def __init__(self, name: str = "gatekeeper"):
        self.name = name
        self._checks: List[Dict[str, Any]] = []

    def add_check(
        self,
        name: str,
        max_color: GateColor,
        checker: Callable[[], List[str]],
    ) -> None:
        """
        Register a quality check.

        Args:
            name: Check identifier.
            max_color: The color assigned to findings from this check.
            checker: Callable returning list of finding messages (empty = pass).
        """
        self._checks.append({
            "name": name,
            "color": max_color,
            "checker": checker,
        })

    def audit(self) -> AuditResult:
        """
        Run all registered checks and produce an audit result.

        The overall status is the highest (most severe) color found.
        """
        import time
        from datetime import datetime

        findings = []
        highest = GateColor.GREEN

        for check in self._checks:
            try:
                messages = check["checker"]()
                for msg in messages:
                    color = check["color"]
                    findings.append(Finding(
                        check_name=check["name"],
                        color=color,
                        message=msg,
                    ))
                    if color > highest:
                        highest = color
            except Exception as exc:
                findings.append(Finding(
                    check_name=check["name"],
                    color=GateColor.RED,
                    message=f"Check failed: {exc}",
                ))
                highest = GateColor.RED

        return AuditResult(
            status=highest,
            findings=findings,
            checks_run=len(self._checks),
            timestamp=datetime.now().isoformat(),
        )
