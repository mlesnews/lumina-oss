"""
Cost Analyzer — Read and analyze Claude Code cost logs.

Reads JSONL cost logs written by the cost_tracker hook and provides
aggregation by day, model, tool, and session.

Pattern extracted from production cost tracking system.

Example:
    from lumina.powertools import CostAnalyzer

    analyzer = CostAnalyzer()
    print(f"Today: ${analyzer.today_total():.2f}")
    print(f"This week: ${analyzer.week_total():.2f}")

    for day, cost in analyzer.daily_breakdown(days=7):
        print(f"  {day}: ${cost:.4f}")
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator

logger = logging.getLogger(__name__)

DEFAULT_LOG_PATH = Path.home() / "logs" / "claude-costs" / "cost_log.jsonl"

# Pricing per 1M tokens (USD)
DEFAULT_PRICING = {
    "claude-opus-4-6": {"input": 15.0, "output": 75.0},
    "claude-sonnet-4-6": {"input": 3.0, "output": 15.0},
    "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.0},
}


@dataclass
class CostEntry:
    """A single cost log entry."""
    timestamp: str
    tool: str
    model: str
    tokens_input: int
    tokens_output: int
    cache_read: int
    cache_create: int
    cost_usd: float
    session_id: str

    @classmethod
    def from_dict(cls, d: dict) -> "CostEntry":
        return cls(
            timestamp=d.get("timestamp", ""),
            tool=d.get("tool", ""),
            model=d.get("model", ""),
            tokens_input=d.get("tokens_input", 0),
            tokens_output=d.get("tokens_output", 0),
            cache_read=d.get("cache_read", 0),
            cache_create=d.get("cache_create", 0),
            cost_usd=d.get("cost_usd", 0.0),
            session_id=d.get("session_id", ""),
        )


class CostAnalyzer:
    """Analyze Claude Code cost logs.

    Args:
        log_path: Path to the JSONL cost log file.
        pricing: Model pricing dict (per 1M tokens).
    """

    def __init__(
        self,
        log_path: Path | None = None,
        pricing: dict | None = None,
    ):
        self.log_path = log_path or DEFAULT_LOG_PATH
        self.pricing = pricing or DEFAULT_PRICING

    def read_entries(self, since: datetime | None = None) -> list[CostEntry]:
        """Read all cost entries, optionally filtered by timestamp."""
        if not self.log_path.exists():
            return []

        entries: list[CostEntry] = []
        since_str = since.isoformat() if since else ""

        try:
            with open(self.log_path) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        d = json.loads(line)
                        if since_str and d.get("timestamp", "") < since_str:
                            continue
                        entries.append(CostEntry.from_dict(d))
                    except json.JSONDecodeError:
                        continue
        except OSError as e:
            logger.warning("Failed to read cost log: %s", e)

        return entries

    def today_total(self) -> float:
        """Total cost for today (UTC)."""
        today = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0,
        )
        return sum(e.cost_usd for e in self.read_entries(since=today))

    def week_total(self) -> float:
        """Total cost for the current week (Mon-Sun, UTC)."""
        now = datetime.now(timezone.utc)
        monday = now - timedelta(days=now.weekday())
        start = monday.replace(hour=0, minute=0, second=0, microsecond=0)
        return sum(e.cost_usd for e in self.read_entries(since=start))

    def month_total(self) -> float:
        """Total cost for the current month (UTC)."""
        now = datetime.now(timezone.utc)
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return sum(e.cost_usd for e in self.read_entries(since=start))

    def daily_breakdown(self, days: int = 7) -> list[tuple[str, float]]:
        """Cost per day for the last N days."""
        now = datetime.now(timezone.utc)
        start = (now - timedelta(days=days)).replace(
            hour=0, minute=0, second=0, microsecond=0,
        )
        entries = self.read_entries(since=start)

        by_day: dict[str, float] = {}
        for e in entries:
            day = e.timestamp[:10]
            by_day[day] = by_day.get(day, 0.0) + e.cost_usd

        result = []
        for i in range(days):
            day = (now - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
            result.append((day, by_day.get(day, 0.0)))
        return result

    def by_model(self, since: datetime | None = None) -> dict[str, float]:
        """Cost breakdown by model."""
        entries = self.read_entries(since=since)
        by_model: dict[str, float] = {}
        for e in entries:
            by_model[e.model] = by_model.get(e.model, 0.0) + e.cost_usd
        return by_model

    def by_tool(self, since: datetime | None = None) -> dict[str, float]:
        """Cost breakdown by tool."""
        entries = self.read_entries(since=since)
        by_tool: dict[str, float] = {}
        for e in entries:
            by_tool[e.tool] = by_tool.get(e.tool, 0.0) + e.cost_usd
        return by_tool

    def total_tokens(self, since: datetime | None = None) -> dict[str, int]:
        """Total token counts."""
        entries = self.read_entries(since=since)
        return {
            "input": sum(e.tokens_input for e in entries),
            "output": sum(e.tokens_output for e in entries),
            "cache_read": sum(e.cache_read for e in entries),
            "cache_create": sum(e.cache_create for e in entries),
        }

    def estimate_cost(self, model: str, tokens_in: int, tokens_out: int) -> float:
        """Estimate USD cost for given token counts."""
        rates = self.pricing.get(model, self.pricing.get("default", {"input": 3.0, "output": 15.0}))
        return round(
            (tokens_in / 1_000_000 * rates["input"]) +
            (tokens_out / 1_000_000 * rates["output"]),
            6,
        )
