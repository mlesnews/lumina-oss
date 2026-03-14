"""
Memory Quality Scorer — grade AI memory files across 10 weighted dimensions.

Score any memory file format: CLAUDE.md, .cursorrules, .aider, copilot-instructions.md.
Built on HealthAggregator. Zero external dependencies.

Usage:
    from lumina.memory_score import score_memory_file, score_memory_directory

    report = score_memory_file("CLAUDE.md")
    print(report.to_text())

    report = score_memory_directory("~/.claude/projects/myproject/memory/")
    print(f"Grade: {report.grade} ({report.score_pct:.1f}%)")
"""

from .parser import MemoryFileMetrics, parse_file, parse_directory
from .scorer import (
    MemoryScorer,
    MemoryScoreReport,
    score_memory_file,
    score_memory_directory,
)

__all__ = [
    "MemoryScorer",
    "MemoryScoreReport",
    "MemoryFileMetrics",
    "parse_file",
    "parse_directory",
    "score_memory_file",
    "score_memory_directory",
]
