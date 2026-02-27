#!/usr/bin/env python3
"""
PostToolUse Hook: Claude Code Cost Tracker

Logs every tool call with token usage and estimated cost to JSONL.
Reads real token counts from the Claude Code transcript when available,
falls back to character-based estimation.

Output: ~/logs/claude-costs/cost_log.jsonl
Install: Copy to ~/.claude/hooks/ and register as PostToolUse.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path.home() / "logs" / "claude-costs"
LOG_FILE = LOG_DIR / "cost_log.jsonl"

# Pricing per 1M tokens (USD) — update for your model
PRICING = {
    "claude-opus-4-6": {"input": 15.0, "output": 75.0},
    "claude-sonnet-4-6": {"input": 3.0, "output": 15.0},
    "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.0},
    "default": {"input": 3.0, "output": 15.0},
}

# Daily budget threshold ($20/month / 30 days)
DAILY_BUDGET = 0.67


def estimate_cost(model: str, tokens_in: int, tokens_out: int) -> float:
    """Estimate USD cost for a tool call."""
    rates = PRICING.get(model, PRICING["default"])
    cost = (tokens_in / 1_000_000 * rates["input"]) + (tokens_out / 1_000_000 * rates["output"])
    return round(cost, 6)


def get_today_total() -> float:
    """Sum today's costs from the log file."""
    if not LOG_FILE.exists():
        return 0.0
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    total = 0.0
    try:
        with open(LOG_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if entry.get("timestamp", "").startswith(today):
                        total += entry.get("cost_usd", 0.0)
                except json.JSONDecodeError:
                    continue
    except OSError:
        pass
    return total


def main():
    try:
        hook_data = json.loads(sys.stdin.read())
        tool_name = hook_data.get("tool_name", "unknown")
        tool_input = hook_data.get("tool_input", {})
        tool_output = hook_data.get("tool_output", "")
        model = hook_data.get("model", "claude-opus-4-6")

        # Try to get real token counts from transcript
        tokens_in = 0
        tokens_out = 0
        cache_read = 0
        cache_create = 0
        transcript_path = hook_data.get("transcript_path", "")
        if transcript_path and Path(transcript_path).exists():
            try:
                with open(transcript_path, "rb") as f:
                    f.seek(0, 2)
                    size = f.tell()
                    f.seek(max(0, size - 8192))
                    tail = f.read().decode("utf-8", errors="replace")
                for line in reversed(tail.strip().splitlines()):
                    try:
                        entry = json.loads(line)
                        msg = entry.get("message", {})
                        usage = msg.get("usage") if isinstance(msg, dict) else None
                        if usage and usage.get("output_tokens", 0) > 0:
                            tokens_in = usage.get("input_tokens", 0)
                            tokens_out = usage.get("output_tokens", 0)
                            cache_read = usage.get("cache_read_input_tokens", 0)
                            cache_create = usage.get("cache_creation_input_tokens", 0)
                            break
                    except (json.JSONDecodeError, AttributeError):
                        continue
            except OSError:
                pass

        # Fallback: estimate from content size
        if tokens_in == 0 and tokens_out == 0:
            input_text = json.dumps(tool_input)
            output_text = str(tool_output) if tool_output else ""
            tokens_in = max(1, len(input_text) // 4)
            tokens_out = max(1, len(output_text) // 4)

        cost = estimate_cost(model, tokens_in, tokens_out)

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool": tool_name,
            "model": model,
            "tokens_input": tokens_in,
            "tokens_output": tokens_out,
            "cache_read": cache_read,
            "cache_create": cache_create,
            "cost_usd": cost,
            "session_id": hook_data.get("session_id", ""),
        }

        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")

        # Check daily budget
        today_total = get_today_total()
        if today_total > DAILY_BUDGET * 0.8:
            pct = int(today_total / DAILY_BUDGET * 100)
            print(
                f"COST ALERT: ${today_total:.2f} is {pct}% of daily budget ${DAILY_BUDGET:.2f}",
                file=sys.stderr,
            )

    except Exception:
        pass  # Cost tracking should never block tool execution

    sys.exit(0)


if __name__ == "__main__":
    main()
