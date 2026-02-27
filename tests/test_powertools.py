"""Tests for the powertools module — hook protocol, cost analysis, statusline."""

from lumina.powertools.hook_protocol import HookIO, HookResult
from lumina.powertools.cost_analyzer import CostAnalyzer, CostEntry
from lumina.powertools.statusline import StatusLineBuilder


# ── HookIO ───────────────────────────────────────────────────


def test_hook_io_from_dict():
    """HookIO parses tool_name and tool_input from raw dict."""
    io = HookIO(
        raw={"tool_name": "Bash", "tool_input": {"command": "ls"}},
        tool_name="Bash",
        tool_input={"command": "ls"},
    )
    assert io.tool_name == "Bash"
    assert io.command == "ls"


def test_hook_io_command_empty_for_non_bash():
    """command property returns empty string for non-Bash tools."""
    io = HookIO(tool_name="Read", tool_input={"file_path": "/tmp/test.py"})
    assert io.command == ""
    assert io.file_path == "/tmp/test.py"


def test_hook_io_user_prompt():
    """user_prompt reads from either key format."""
    io1 = HookIO(raw={"user_prompt": "hello"})
    assert io1.user_prompt == "hello"

    io2 = HookIO(raw={"prompt": "world"})
    assert io2.user_prompt == "world"


def test_hook_result():
    """HookResult stores decision and reason."""
    r = HookResult(allowed=False, reason="Blocked by policy")
    assert not r.allowed
    assert r.reason == "Blocked by policy"


# ── CostEntry ────────────────────────────────────────────────


def test_cost_entry_from_dict():
    """CostEntry parses from a log line dict."""
    entry = CostEntry.from_dict({
        "timestamp": "2026-02-27T10:00:00Z",
        "tool": "Bash",
        "model": "claude-sonnet-4-6",
        "tokens_input": 1000,
        "tokens_output": 500,
        "cache_read": 0,
        "cache_create": 0,
        "cost_usd": 0.0105,
        "session_id": "abc123",
    })
    assert entry.tool == "Bash"
    assert entry.tokens_input == 1000
    assert entry.cost_usd == 0.0105


def test_cost_entry_defaults():
    """CostEntry handles missing keys with defaults."""
    entry = CostEntry.from_dict({})
    assert entry.tool == ""
    assert entry.tokens_input == 0
    assert entry.cost_usd == 0.0


# ── CostAnalyzer ─────────────────────────────────────────────


def test_cost_analyzer_missing_file(tmp_path):
    """CostAnalyzer returns empty when log file doesn't exist."""
    analyzer = CostAnalyzer(log_path=tmp_path / "nonexistent.jsonl")
    assert analyzer.read_entries() == []
    assert analyzer.today_total() == 0.0


def test_cost_analyzer_reads_entries(tmp_path):
    """CostAnalyzer reads JSONL entries correctly."""
    import json
    log_file = tmp_path / "cost.jsonl"
    entries = [
        {"timestamp": "2026-02-27T10:00:00Z", "tool": "Bash", "model": "claude-sonnet-4-6",
         "tokens_input": 1000, "tokens_output": 500, "cost_usd": 0.01, "session_id": "s1",
         "cache_read": 0, "cache_create": 0},
        {"timestamp": "2026-02-27T11:00:00Z", "tool": "Read", "model": "claude-sonnet-4-6",
         "tokens_input": 500, "tokens_output": 200, "cost_usd": 0.005, "session_id": "s1",
         "cache_read": 0, "cache_create": 0},
    ]
    log_file.write_text("\n".join(json.dumps(e) for e in entries) + "\n")

    analyzer = CostAnalyzer(log_path=log_file)
    result = analyzer.read_entries()
    assert len(result) == 2
    assert result[0].tool == "Bash"
    assert result[1].tool == "Read"


def test_cost_analyzer_by_model(tmp_path):
    """by_model aggregates cost per model."""
    import json
    log_file = tmp_path / "cost.jsonl"
    entries = [
        {"timestamp": "2026-02-27T10:00:00Z", "tool": "Bash", "model": "opus",
         "tokens_input": 0, "tokens_output": 0, "cost_usd": 0.10, "session_id": "",
         "cache_read": 0, "cache_create": 0},
        {"timestamp": "2026-02-27T11:00:00Z", "tool": "Bash", "model": "sonnet",
         "tokens_input": 0, "tokens_output": 0, "cost_usd": 0.05, "session_id": "",
         "cache_read": 0, "cache_create": 0},
        {"timestamp": "2026-02-27T12:00:00Z", "tool": "Read", "model": "opus",
         "tokens_input": 0, "tokens_output": 0, "cost_usd": 0.20, "session_id": "",
         "cache_read": 0, "cache_create": 0},
    ]
    log_file.write_text("\n".join(json.dumps(e) for e in entries) + "\n")

    analyzer = CostAnalyzer(log_path=log_file)
    by_model = analyzer.by_model()
    assert abs(by_model["opus"] - 0.30) < 1e-9
    assert abs(by_model["sonnet"] - 0.05) < 1e-9


def test_cost_analyzer_estimate():
    """estimate_cost calculates from pricing table."""
    analyzer = CostAnalyzer()
    cost = analyzer.estimate_cost("claude-sonnet-4-6", 1_000_000, 100_000)
    assert cost == 4.5  # $3 input + $1.50 output


# ── StatusLineBuilder ────────────────────────────────────────


def test_statusline_single_line():
    """Single-line statusline with two sections."""
    builder = StatusLineBuilder(lines=1)
    builder.section(0, "GIT", "main")
    builder.section(0, "COST", "$1.23")
    output = builder.render()
    assert "[GIT] main" in output
    assert "[COST] $1.23" in output
    assert " | " in output


def test_statusline_multi_line():
    """Multi-line statusline renders separate lines."""
    builder = StatusLineBuilder(lines=2)
    builder.section(0, "LINE1", "first")
    builder.section(1, "LINE2", "second")
    output = builder.render()
    lines = output.split("\n")
    assert len(lines) == 2
    assert "first" in lines[0]
    assert "second" in lines[1]


def test_statusline_color():
    """Color codes are applied to values."""
    builder = StatusLineBuilder(lines=1)
    builder.section(0, "STATUS", "OK", color="green")
    output = builder.render()
    assert "\033[32m" in output  # green
    assert "\033[0m" in output   # reset


def test_statusline_clear():
    """clear() removes all sections."""
    builder = StatusLineBuilder(lines=1)
    builder.section(0, "X", "Y")
    builder.clear()
    output = builder.render()
    assert output.strip() == ""


def test_statusline_chaining():
    """section() returns self for method chaining."""
    builder = StatusLineBuilder(lines=1)
    result = builder.section(0, "A", "1").section(0, "B", "2")
    assert result is builder


def test_statusline_colon_style():
    """colon label style uses 'LABEL:' format."""
    builder = StatusLineBuilder(lines=1, label_style="colon")
    builder.section(0, "GIT", "main")
    output = builder.render()
    assert "GIT:" in output


def test_statusline_no_label():
    """none label style shows value only."""
    builder = StatusLineBuilder(lines=1, label_style="none")
    builder.section(0, "GIT", "main")
    output = builder.render()
    assert "[GIT]" not in output
    assert "GIT:" not in output
