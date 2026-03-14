"""Tests for the Memory Quality Scorer."""
import json
import os
import tempfile
from pathlib import Path

import pytest

from lumina.memory_score import (
    MemoryFileMetrics,
    MemoryScoreReport,
    MemoryScorer,
    parse_file,
    parse_directory,
    score_memory_file,
    score_memory_directory,
)
from lumina.memory_score.constants import DEFAULT_WEIGHTS, GRADE_THRESHOLDS
from lumina.memory_score.dimensions import (
    score_structure,
    score_completeness,
    score_conciseness,
    score_freshness,
    score_cross_referencing,
    score_actionability,
    score_platform_compliance,
    score_meta_awareness,
)
from lumina.memory_score.parser import detect_format


# --- Fixtures ---


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture
def minimal_memory(tmp_dir):
    """A minimal MEMORY.md file."""
    f = tmp_dir / "MEMORY.md"
    f.write_text("# Memory\n\nSome notes.\n")
    return f


@pytest.fixture
def rich_memory(tmp_dir):
    """A well-structured MEMORY.md with frontmatter, headings, tables, code blocks."""
    content = """---
name: test_memory
description: Test memory system
type: reference
---

# Memory System

## Topic Triggers
| When working on... | Read this file |
|---|---|
| trading, signals | `trading.md` |
| agents, personas | `AGENTS.md` |
| security, vault, COMPUSEC | `compusec.md` |
| testing, QA, verification | `testing.md` |
| deployment, CI/CD | `deploy.md` |
| monitoring, health | `health.md` |

## Rules

- **NEVER** hardcode secrets. Use vault only. #VAULT_ONLY
- **ALWAYS** verify outcomes before closing tickets. #VERIFY_OUTCOMES
- **MUST** read roadmap first every session. #ROADMAP
- Use @MARVIN for security audits.
- Delegate to @JARVIS for execution.

## Environment

Platform: Linux WSL2. Docker networking via bridge.

```bash
# Deploy command
docker compose up -d
```

## File Index
| File | Summary |
|---|---|
| [trading.md](trading.md) | Trading system reference |
| [AGENTS.md](AGENTS.md) | Agent registry |

## Architecture

The system uses a 3-layer brain model with id/ego/superego routing.

## Monitoring

Health checks run via systemd timer every 15 minutes.
Last updated: 2026-03-14. Version 2.0.

**Connects to:** rules.md, trading.md
"""
    f = tmp_dir / "MEMORY.md"
    f.write_text(content)
    return f


@pytest.fixture
def memory_directory(tmp_dir):
    """A directory with multiple memory files."""
    (tmp_dir / "MEMORY.md").write_text(
        "# Memory\n\n## Topic Triggers\n"
        "| When working on... | Read this file |\n|---|---|\n"
        "| trading | `trading.md` |\n"
        "| agents | `AGENTS.md` |\n\n"
        "## File Index\n"
        "| File | Summary |\n|---|---|\n"
        "| [trading.md](trading.md) | Trading |\n"
        "NEVER guess. ALWAYS verify. MUST check.\n"
    )
    (tmp_dir / "trading.md").write_text(
        "---\nname: trading\ntype: reference\n---\n"
        "# Trading\nBinance.US API. Deploy with vault.\n"
        "Test all orders. Monitor health dashboard.\n"
        "Last updated: 2026-03-14\n"
    )
    (tmp_dir / "AGENTS.md").write_text(
        "---\nname: agents\ntype: reference\n---\n"
        "# Agents\n@JARVIS CTO. @MARVIN security.\n"
        "Convention: snake_case. Environment: WSL2.\n"
    )
    return tmp_dir


# --- Parser Tests ---


class TestParser:
    def test_detect_format_claude(self):
        assert detect_format("CLAUDE.md") == "claude"
        assert detect_format("MEMORY.md") == "claude"
        assert detect_format("rules.md") == "claude"

    def test_detect_format_cursor(self):
        assert detect_format(".cursorrules") == "cursor"

    def test_detect_format_copilot(self):
        assert detect_format("copilot-instructions.md") == "copilot"

    def test_detect_format_unknown(self):
        assert detect_format("random.txt") == "unknown"

    def test_parse_minimal(self, minimal_memory):
        m = parse_file(str(minimal_memory))
        assert m.filename == "MEMORY.md"
        assert m.format_type == "claude"
        assert m.line_count == 3
        assert not m.has_frontmatter

    def test_parse_rich(self, rich_memory):
        m = parse_file(str(rich_memory))
        assert m.has_frontmatter
        assert m.heading_counts.get(1, 0) >= 1
        assert m.heading_counts.get(2, 0) >= 1
        assert m.table_count > 0
        assert m.code_block_count >= 1
        assert len(m.hashtags) >= 2
        assert len(m.agent_refs) >= 1
        assert m.has_trigger_table
        assert m.has_index_section
        assert m.most_recent_date == "2026-03-14"

    def test_parse_frontmatter_extraction(self, rich_memory):
        m = parse_file(str(rich_memory))
        assert m.has_frontmatter is True

    def test_parse_directory(self, memory_directory):
        files = parse_directory(str(memory_directory))
        assert len(files) == 3
        names = {f.filename for f in files}
        assert "MEMORY.md" in names
        assert "trading.md" in names

    def test_parse_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            parse_file("/nonexistent/file.md")

    def test_parse_empty_file(self, tmp_dir):
        f = tmp_dir / "empty.md"
        f.write_text("")
        m = parse_file(str(f))
        assert m.line_count == 0

    def test_never_always_count(self, rich_memory):
        m = parse_file(str(rich_memory))
        assert m.never_always_count >= 3  # NEVER, ALWAYS, MUST

    def test_crossref_lines(self, rich_memory):
        m = parse_file(str(rich_memory))
        assert len(m.crossref_lines) >= 1  # "Connects to:" line


# --- Dimension Tests ---


class TestDimensions:
    def test_structure_minimal(self, minimal_memory):
        m = parse_file(str(minimal_memory))
        score, detail = score_structure(m)
        assert 0.0 <= score <= 1.0
        assert "no frontmatter" in detail

    def test_structure_rich(self, rich_memory):
        m = parse_file(str(rich_memory))
        score, detail = score_structure(m)
        assert score >= 0.5
        assert "frontmatter present" in detail

    def test_conciseness_normal(self, rich_memory):
        m = parse_file(str(rich_memory))
        score, detail = score_conciseness(m)
        assert 0.0 <= score <= 1.0
        assert "words/line" in detail

    def test_freshness_current(self, rich_memory):
        m = parse_file(str(rich_memory))
        score, detail = score_freshness(m)
        # 2026-03-14 should be very recent
        assert score >= 0.8

    def test_freshness_no_dates(self, minimal_memory):
        m = parse_file(str(minimal_memory))
        score, detail = score_freshness(m)
        assert score == 0.3
        assert "no dates" in detail

    def test_actionability_rules_heavy(self, rich_memory):
        m = parse_file(str(rich_memory))
        score, detail = score_actionability(m)
        assert score > 0.0
        assert "imperatives" in detail

    def test_platform_compliance_under_limit(self, rich_memory):
        m = parse_file(str(rich_memory))
        score, detail = score_platform_compliance(m)
        assert score >= 0.6  # Under limit, no secrets, clean UTF-8

    def test_cross_referencing(self, rich_memory):
        m = parse_file(str(rich_memory))
        score, detail = score_cross_referencing(m)
        assert score > 0.0
        assert "tags" in detail

    def test_meta_awareness(self, rich_memory):
        m = parse_file(str(rich_memory))
        score, detail = score_meta_awareness(m)
        assert score > 0.0


# --- Scorer Tests ---


class TestScorer:
    def test_weights_sum_to_one(self):
        total = sum(DEFAULT_WEIGHTS.values())
        assert abs(total - 1.0) < 0.01

    def test_score_file(self, rich_memory):
        report = score_memory_file(str(rich_memory))
        assert isinstance(report, MemoryScoreReport)
        assert 0 <= report.score_pct <= 100
        assert report.grade in ("A", "B", "C", "D", "F", "?")
        assert len(report.dimensions) == 10

    def test_score_directory(self, memory_directory):
        report = score_memory_directory(str(memory_directory))
        assert isinstance(report, MemoryScoreReport)
        assert report.metrics.filename == "MEMORY.md"
        assert report.score_pct > 0

    def test_to_dict(self, rich_memory):
        report = score_memory_file(str(rich_memory))
        d = report.to_dict()
        assert "grade" in d
        assert "score_pct" in d
        assert "dimensions" in d
        assert "file" in d
        assert d["file"] == "MEMORY.md"

    def test_to_text(self, rich_memory):
        report = score_memory_file(str(rich_memory))
        text = report.to_text()
        assert "Memory Quality Report" in text
        assert "Grade:" in text
        assert "Dimensions:" in text

    def test_to_markdown(self, rich_memory):
        report = score_memory_file(str(rich_memory))
        md = report.to_markdown()
        assert "## Memory Quality" in md
        assert "| Dimension |" in md

    def test_to_dict_is_json_serializable(self, rich_memory):
        report = score_memory_file(str(rich_memory))
        serialized = json.dumps(report.to_dict())
        assert isinstance(serialized, str)

    def test_custom_weights(self, rich_memory):
        weights = {k: 1.0 / 10 for k in DEFAULT_WEIGHTS}
        scorer = MemoryScorer(weights=weights)
        report = scorer.score_file(str(rich_memory))
        assert report.score_pct > 0

    def test_grade_letters(self, rich_memory):
        report = score_memory_file(str(rich_memory))
        # Grade should be one of the defined letters
        assert report.grade in ("A", "B", "C", "D", "F", "?")


# --- CLI Tests ---


class TestCLI:
    def test_module_runnable(self, rich_memory):
        """python -m lumina.memory_score should work."""
        exit_code = os.system(
            f"cd /home/mlesn/lumina-oss && "
            f"python -m lumina.memory_score {rich_memory} > /dev/null 2>&1"
        )
        assert exit_code == 0

    def test_json_output(self, rich_memory):
        """--format json should produce valid JSON."""
        import subprocess
        result = subprocess.run(
            ["python", "-m", "lumina.memory_score", str(rich_memory), "--format", "json"],
            capture_output=True, text=True, cwd="/home/mlesn/lumina-oss"
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "grade" in data

    def test_directory_scoring(self, memory_directory):
        exit_code = os.system(
            f"cd /home/mlesn/lumina-oss && "
            f"python -m lumina.memory_score {memory_directory} > /dev/null 2>&1"
        )
        assert exit_code == 0
