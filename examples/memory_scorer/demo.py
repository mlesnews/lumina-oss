"""
Demo: programmatic usage of lumina.memory_score.

Generates a sample CLAUDE.md in a temp directory, scores it three ways
(text, markdown, JSON), and demonstrates a custom-weighted scorer.

Run:
    python examples/memory_scorer/demo.py
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from lumina.memory_score import (
    MemoryScorer,
    score_memory_directory,
    score_memory_file,
)


SAMPLE_CLAUDE_MD = """\
---
name: demo-project
description: Sample memory file for scoring demo
---

# Project Memory

## Identity
This project is a demo. The AI assistant must keep responses concise.

## Tools
- pytest for tests
- ruff for lint
- Use the Bash tool for shell commands

## Conventions
- Always run tests before committing
- Never commit secrets or credentials
- Prefer editing files over creating new ones

## Workflows
Build: `pip install -e .`
Test: `pytest tests/ -v`
Deploy: tag a release, CI publishes

## Security
- Do not embed API keys
- Verify secrets are loaded from environment, never hardcoded

## Memory
This file is the index. Topic files live in `memory/` and are referenced
by `#TAGS` and `@AGENT` handles. Last updated: 2026-01-15.

See also: `memory/conventions.md`, `memory/agents.md`.
"""


def demo_single_file() -> None:
    print("=" * 60)
    print("DEMO 1: Score a single memory file")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "CLAUDE.md"
        path.write_text(SAMPLE_CLAUDE_MD, encoding="utf-8")

        report = score_memory_file(str(path))

        print(report.to_text(verbose=True))
        print()
        print(f"Lifecycle stage: {report.lifecycle_stage}")
        print(f"Description:     {report.lifecycle_description}")


def demo_markdown_render() -> None:
    print()
    print("=" * 60)
    print("DEMO 2: Markdown report card")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "CLAUDE.md"
        path.write_text(SAMPLE_CLAUDE_MD, encoding="utf-8")
        report = score_memory_file(str(path))
        print(report.to_markdown())


def demo_json_render() -> None:
    print()
    print("=" * 60)
    print("DEMO 3: JSON output (machine-readable)")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "CLAUDE.md"
        path.write_text(SAMPLE_CLAUDE_MD, encoding="utf-8")
        report = score_memory_file(str(path))
        print(json.dumps(report.to_dict(), indent=2))


def demo_custom_weights() -> None:
    print()
    print("=" * 60)
    print("DEMO 4: Custom weights (heavier actionability emphasis)")
    print("=" * 60)

    weights = {
        "structure": 0.05,
        "completeness": 0.10,
        "conciseness": 0.05,
        "freshness": 0.05,
        "modularity": 0.05,
        "cross_referencing": 0.05,
        "actionability": 0.40,  # the rules matter most
        "coverage": 0.10,
        "platform_compliance": 0.10,
        "meta_awareness": 0.05,
    }
    assert abs(sum(weights.values()) - 1.0) < 1e-9, "weights must sum to 1.0"

    scorer = MemoryScorer(weights=weights)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "CLAUDE.md"
        path.write_text(SAMPLE_CLAUDE_MD, encoding="utf-8")
        report = scorer.score_file(str(path))
        print(f"Grade with custom weights: {report.grade} ({report.score_pct:.1f}/100)")
        for d in sorted(report.dimensions, key=lambda x: -x.score):
            print(f"  {d.name:<22} {d.score:.0%}  weight={d.weight:.0%}  {d.detail}")


def demo_directory_scoring() -> None:
    print()
    print("=" * 60)
    print("DEMO 5: Score a memory directory")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "MEMORY.md").write_text(
            "---\nname: index\n---\n\n# Memory Index\n\n"
            "- [conventions](conventions.md) — coding style and commit rules\n"
            "- [agents](agents.md) — agent personas and routing\n",
            encoding="utf-8",
        )
        (root / "conventions.md").write_text(
            "---\nname: conventions\n---\n\n"
            "# Conventions\n\nAlways run tests. Never commit secrets.\n",
            encoding="utf-8",
        )
        (root / "agents.md").write_text(
            "---\nname: agents\n---\n\n"
            "# Agents\n\n@REVIEWER must verify before merge.\n",
            encoding="utf-8",
        )

        report = score_memory_directory(str(root))
        print(f"Directory grade: {report.grade} ({report.score_pct:.1f}/100)")
        print(f"Primary file:    {report.metrics.filename}")
        print(f"Recommendation:  {report.recommendation}")


if __name__ == "__main__":
    demo_single_file()
    demo_markdown_render()
    demo_json_render()
    demo_custom_weights()
    demo_directory_scoring()
