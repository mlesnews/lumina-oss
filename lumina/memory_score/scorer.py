"""
Memory Quality Scorer — orchestrates 10 dimension analyzers via HealthAggregator.

Usage:
    scorer = MemoryScorer()
    report = scorer.score_file("MEMORY.md")
    print(f"{report.grade}: {report.score_pct:.1f}%")

    # Or score an entire directory:
    report = scorer.score_directory("~/.claude/projects/myproject/memory/")

Zero external dependencies.
"""

from typing import Dict, List, Optional

from ..aios.health import HealthAggregator, HealthReport
from .constants import DEFAULT_WEIGHTS, GRADE_LETTERS, GRADE_THRESHOLDS, ILLITHID_DESCRIPTIONS, ILLITHID_STAGES
from .dimensions import (
    score_actionability,
    score_completeness,
    score_conciseness,
    score_coverage,
    score_cross_referencing,
    score_freshness,
    score_meta_awareness,
    score_modularity,
    score_platform_compliance,
    score_structure,
)
from .parser import MemoryFileMetrics, parse_directory, parse_file


class MemoryScoreReport:
    """Extended report with grade letter and per-dimension breakdown."""

    def __init__(self, health_report: HealthReport, metrics: MemoryFileMetrics):
        self.health_report = health_report
        self.metrics = metrics
        self.score_pct = health_report.score_pct
        self.label = health_report.label
        self.grade = GRADE_LETTERS.get(health_report.label, "?")
        self.dimensions = health_report.dimensions
        self.recommendation = health_report.recommendation

    @property
    def lifecycle_stage(self) -> str:
        """D&D Mind Flayer lifecycle stage mapped from grade label."""
        return ILLITHID_STAGES.get(self.label, "Tadpole")

    @property
    def lifecycle_description(self) -> str:
        """Human-readable description of the lifecycle stage."""
        return ILLITHID_DESCRIPTIONS.get(self.lifecycle_stage, "")

    def to_dict(self) -> dict:
        base = self.health_report.to_dict()
        base["grade"] = self.grade
        base["file"] = self.metrics.filename
        base["line_count"] = self.metrics.line_count
        base["format_type"] = self.metrics.format_type
        base["lifecycle_stage"] = self.lifecycle_stage
        base["lifecycle_description"] = self.lifecycle_description
        return base

    def to_text(self, verbose: bool = False) -> str:
        """Render a human-readable report card."""
        lines = [
            f"Memory Quality Report: {self.metrics.filename}",
            "=" * 50,
            f"Grade: {self.grade} ({self.score_pct:.1f}/100) [{self.label}]",
            f"Format: {self.metrics.format_type} | Lines: {self.metrics.line_count}",
        ]

        if verbose:
            lines.append(
                f"Lifecycle: {self.lifecycle_stage} — {self.lifecycle_description}"
            )

        lines.extend(["", "Dimensions:"])

        for d in sorted(self.dimensions, key=lambda x: -x.score):
            bar_filled = int(d.score * 10)
            bar = "\u2588" * bar_filled + "\u2591" * (10 - bar_filled)
            pct = f"{d.score:.0%}"
            weight = f"({d.weight:.0%}w)"
            lines.append(f"  {d.name:<22} {bar}  {pct:>4}  {weight}  {d.detail}")

        lines.append("")
        lines.append(f"Recommendation: {self.recommendation}")
        return "\n".join(lines)

    def to_markdown(self) -> str:
        """Render a markdown report."""
        lines = [
            f"## Memory Quality: {self.grade} ({self.score_pct:.1f}/100)",
            "",
            f"**File:** `{self.metrics.filename}` | "
            f"**Format:** {self.metrics.format_type} | "
            f"**Lines:** {self.metrics.line_count}",
            "",
            "| Dimension | Score | Weight | Detail |",
            "|-----------|-------|--------|--------|",
        ]

        for d in sorted(self.dimensions, key=lambda x: -x.score):
            lines.append(
                f"| {d.name} | {d.score:.0%} | {d.weight:.0%} | {d.detail} |"
            )

        lines.extend(["", f"**Recommendation:** {self.recommendation}"])
        return "\n".join(lines)


class MemoryScorer:
    """
    Orchestrates 10 dimension analyzers and produces a quality score.

    Uses HealthAggregator internally for weighted scoring and trend detection.
    """

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self._weights = weights or DEFAULT_WEIGHTS

    def score_file(
        self,
        filepath: str,
        all_files: Optional[List[MemoryFileMetrics]] = None,
    ) -> MemoryScoreReport:
        """Score a single memory file."""
        metrics = parse_file(filepath)
        return self._score_metrics(metrics, all_files)

    def score_directory(self, dirpath: str) -> MemoryScoreReport:
        """Score an entire memory directory (uses MEMORY.md as primary)."""
        all_files = parse_directory(dirpath)

        # Find the primary index file (MEMORY.md or CLAUDE.md)
        primary = None
        for f in all_files:
            if f.filename in ("MEMORY.md", "CLAUDE.md"):
                primary = f
                break

        if primary is None and all_files:
            # Use the largest file as primary
            primary = max(all_files, key=lambda f: f.line_count)

        if primary is None:
            raise FileNotFoundError(f"No memory files found in {dirpath}")

        return self._score_metrics(primary, all_files)

    def _score_metrics(
        self,
        primary: MemoryFileMetrics,
        all_files: Optional[List[MemoryFileMetrics]] = None,
    ) -> MemoryScoreReport:
        """Run all 10 dimension analyzers and produce a report."""
        agg = HealthAggregator(
            dimensions=self._weights,
            thresholds=GRADE_THRESHOLDS,
        )

        # Score each dimension
        analyzers = {
            "structure": lambda: score_structure(primary),
            "completeness": lambda: score_completeness(primary, all_files),
            "conciseness": lambda: score_conciseness(primary),
            "freshness": lambda: score_freshness(primary),
            "modularity": lambda: score_modularity(primary, all_files),
            "cross_referencing": lambda: score_cross_referencing(primary),
            "actionability": lambda: score_actionability(primary),
            "coverage": lambda: score_coverage(primary, all_files),
            "platform_compliance": lambda: score_platform_compliance(primary),
            "meta_awareness": lambda: score_meta_awareness(primary),
        }

        for name, analyzer_fn in analyzers.items():
            score_val, detail = analyzer_fn()
            agg.score(name, score_val, detail)

        report = agg.evaluate()
        return MemoryScoreReport(report, primary)


def score_memory_file(filepath: str) -> MemoryScoreReport:
    """Convenience function: score a single file with default weights."""
    return MemoryScorer().score_file(filepath)


def score_memory_directory(dirpath: str) -> MemoryScoreReport:
    """Convenience function: score a directory with default weights."""
    return MemoryScorer().score_directory(dirpath)
