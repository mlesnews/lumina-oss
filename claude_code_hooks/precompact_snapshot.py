#!/usr/bin/env python3
"""
PreCompact Hook: Emergency Context Snapshot

Fires before Claude Code context compaction. Saves a JSON snapshot of the
current session state (working directory, git status, open files from recent
tool calls) so the post-compaction context can recover awareness.

Snapshot location: ~/.claude/snapshots/
Install: Register as PreCompact hook.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SNAPSHOT_DIR = Path.home() / ".claude" / "snapshots"
MAX_SNAPSHOTS = 10  # Keep last N snapshots


def capture_git_state() -> dict:
    """Capture current git branch, status, and recent commits."""
    state = {}
    try:
        state["branch"] = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5,
        ).stdout.strip()

        state["status"] = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=5,
        ).stdout.strip()

        state["recent_commits"] = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            capture_output=True, text=True, timeout=5,
        ).stdout.strip()
    except Exception:
        pass
    return state


def main():
    try:
        SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc)

        snapshot = {
            "timestamp": now.isoformat(),
            "reason": "precompact",
            "cwd": os.getcwd(),
            "git": capture_git_state(),
        }

        # Read session_id from stdin if available
        try:
            hook_data = json.loads(sys.stdin.read())
            snapshot["session_id"] = hook_data.get("session_id", "")
        except Exception:
            pass

        # Save snapshot
        filename = f"snapshot_{now.strftime('%Y%m%d_%H%M%S')}.json"
        snapshot_path = SNAPSHOT_DIR / filename
        with open(snapshot_path, "w") as f:
            json.dump(snapshot, f, indent=2)

        # Prune old snapshots
        snapshots = sorted(SNAPSHOT_DIR.glob("snapshot_*.json"), reverse=True)
        for old in snapshots[MAX_SNAPSHOTS:]:
            old.unlink(missing_ok=True)

        print(json.dumps({"status": "ok", "message": f"Pre-compaction snapshot saved: {filename}"}))

    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)[:200]}))

    sys.exit(0)


if __name__ == "__main__":
    main()
