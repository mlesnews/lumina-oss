#!/usr/bin/env python3
"""
UserPromptSubmit Hook: Fast Mode State Tracker

Detects /fast toggle commands and maintains a state file. Also monitors
recent token throughput from the cost log and recommends enabling fast
mode when sustained heavy load is detected.

State file: ~/.claude/fast_mode_state.json
Reads from: ~/logs/claude-costs/cost_log.jsonl (written by cost_tracker.py)
Install: Register as UserPromptSubmit hook.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

STATE_FILE = Path.home() / ".claude" / "fast_mode_state.json"
COST_LOG = Path.home() / "logs" / "claude-costs" / "cost_log.jsonl"

# Auto-boost recommendation thresholds
HEAVY_LOAD_TPS = 50       # tok/s above this = heavy load
HEAVY_LOAD_ENTRIES = 3    # need N consecutive heavy entries to trigger
RECOMMEND_COOLDOWN = 300  # don't nag more than once per 5 min


def check_auto_boost() -> str | None:
    """Check recent cost log entries. Return recommendation message or None."""
    try:
        if not COST_LOG.exists():
            return None

        fast_mode = False
        last_recommend = ""
        if STATE_FILE.exists():
            state = json.loads(STATE_FILE.read_text())
            fast_mode = state.get("fast_mode", False)
            last_recommend = state.get("last_recommend", "")

        if fast_mode:
            return None

        if last_recommend:
            try:
                lr = datetime.fromisoformat(last_recommend)
                if (datetime.now(timezone.utc) - lr).total_seconds() < RECOMMEND_COOLDOWN:
                    return None
            except ValueError:
                pass

        recent_tps: list[float] = []
        with open(COST_LOG, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - 8192))
            tail = f.read().decode("utf-8", errors="replace")

        for line in reversed(tail.strip().splitlines()):
            try:
                entry = json.loads(line)
                tps = entry.get("tok_per_sec", 0)
                if tps > 0:
                    recent_tps.append(tps)
                if len(recent_tps) >= HEAVY_LOAD_ENTRIES:
                    break
            except (json.JSONDecodeError, KeyError):
                continue

        if len(recent_tps) >= HEAVY_LOAD_ENTRIES and all(t >= HEAVY_LOAD_TPS for t in recent_tps):
            avg_tps = sum(recent_tps) / len(recent_tps)
            state_data = {}
            if STATE_FILE.exists():
                try:
                    state_data = json.loads(STATE_FILE.read_text())
                except (json.JSONDecodeError, OSError):
                    pass
            state_data["last_recommend"] = datetime.now(timezone.utc).isoformat()
            STATE_FILE.write_text(json.dumps(state_data, indent=2) + "\n")
            return f"Heavy tok load detected ({avg_tps:.0f} tok/s avg). Type /fast to engage BOOST mode."

    except Exception:
        pass
    return None


def main():
    try:
        hook_data = json.loads(sys.stdin.read())
        prompt = hook_data.get("user_prompt", hook_data.get("prompt", ""))

        stripped = prompt.strip().lower()
        if stripped in ("/fast", "/fast ", "/fast\n"):
            current = False
            if STATE_FILE.exists():
                try:
                    state = json.loads(STATE_FILE.read_text())
                    current = state.get("fast_mode", False)
                except (json.JSONDecodeError, OSError):
                    pass

            new_state = not current
            STATE_FILE.write_text(json.dumps({
                "fast_mode": new_state,
                "toggled_at": datetime.now(timezone.utc).isoformat(),
                "session_id": hook_data.get("session_id", ""),
            }, indent=2) + "\n")
        else:
            msg = check_auto_boost()
            if msg:
                print(msg, file=sys.stderr)

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
