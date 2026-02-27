#!/usr/bin/env python3
"""
Stop Hook: API Watchdog — Session Crash Detection

Detects Anthropic API 500 errors, timeouts, and rate limits that crash
Claude Code sessions. Logs every session stop with classification and
alerts via Telegram when repeated failures exceed threshold.

Install: Copy to ~/.claude/hooks/ and register as Stop hook.

Log: ~/logs/claude-api-watchdog/api_errors.jsonl
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path.home() / "logs" / "claude-api-watchdog"
LOG_FILE = LOG_DIR / "api_errors.jsonl"

# Alert if N failures in M minutes
ALERT_THRESHOLD = 3
ALERT_WINDOW_MINUTES = 30


def classify_stop(stdin_data: str) -> dict:
    """Classify why the session stopped."""
    event = {}
    try:
        event = json.loads(stdin_data) if stdin_data.strip() else {}
    except (json.JSONDecodeError, TypeError):
        pass

    stop_reason = event.get("stop_reason", "")
    error_msg = event.get("error", "")
    combined = f"{stop_reason} {error_msg} {stdin_data}"

    classification = "clean_exit"
    if "500" in combined or "Internal server error" in combined:
        classification = "api_500"
    elif "timeout" in combined.lower() or "timed out" in combined.lower():
        classification = "timeout"
    elif "rate_limit" in combined.lower() or "429" in combined:
        classification = "rate_limit"
    elif "overloaded" in combined.lower() or "529" in combined:
        classification = "overloaded"
    elif "error" in combined.lower() and combined.strip():
        classification = "unknown_error"

    request_ids = list(dict.fromkeys(re.findall(r'req_[A-Za-z0-9]+', combined)))
    error_codes = list(set(re.findall(r'\b[45]\d{2}\b', combined)))

    return {
        "classification": classification,
        "request_ids": request_ids,
        "error_codes": error_codes,
        "raw_snippet": combined[:500] if classification != "clean_exit" else "",
    }


def log_event(data: dict) -> dict:
    """Append event to JSONL log."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "epoch": time.time(),
        **data,
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def check_alert_threshold() -> int:
    """Count recent failures within alert window."""
    if not LOG_FILE.exists():
        return 0
    cutoff = time.time() - (ALERT_WINDOW_MINUTES * 60)
    count = 0
    with open(LOG_FILE, "r") as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry.get("epoch", 0) > cutoff and entry["classification"] != "clean_exit":
                    count += 1
            except (json.JSONDecodeError, KeyError):
                continue
    return count


def send_alert(entry: dict, failure_count: int):
    """Send alert via Telegram (requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID env vars)."""
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not bot_token or not chat_id:
        return

    text = (
        f"[API WATCHDOG] Claude Code Session Crashed\n\n"
        f"Type: {entry['classification']}\n"
        f"Failures in last {ALERT_WINDOW_MINUTES}min: {failure_count}\n"
        f"Request IDs: {', '.join(entry.get('request_ids', [])[:3]) or 'none'}\n"
        f"Time: {entry['timestamp'][:19]}Z"
    )

    try:
        import urllib.request
        data = json.dumps({"chat_id": chat_id, "text": text}).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass


def main():
    stdin_data = ""
    try:
        if not sys.stdin.isatty():
            stdin_data = sys.stdin.read()
    except Exception:
        pass

    data = classify_stop(stdin_data)
    entry = log_event(data)

    if data["classification"] != "clean_exit":
        failure_count = check_alert_threshold()
        if failure_count >= ALERT_THRESHOLD:
            send_alert(entry, failure_count)
        print(
            f"API WATCHDOG: {data['classification']} ({failure_count} in {ALERT_WINDOW_MINUTES}min)",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
