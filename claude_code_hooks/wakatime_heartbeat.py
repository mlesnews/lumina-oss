#!/usr/bin/env python3
"""
PostToolUse Hook: WakaTime Heartbeat

Sends coding activity heartbeats to WakaTime for tracking AI-assisted
development time. Fires on file-touching tools (Read, Edit, Write, Bash).

Requires: WakaTime CLI installed and configured (~/.wakatime.cfg)
Install: Register as PostToolUse for Read, Edit, Write, Bash, Grep, Glob.
"""

import json
import subprocess
import sys
from pathlib import Path

WAKATIME_CLI = Path.home() / ".wakatime" / "wakatime-cli"
# Fallback locations
WAKATIME_FALLBACK = [
    Path("/usr/local/bin/wakatime-cli"),
    Path("/usr/bin/wakatime-cli"),
]


def find_wakatime() -> Path | None:
    """Find wakatime-cli binary."""
    if WAKATIME_CLI.exists():
        return WAKATIME_CLI
    for path in WAKATIME_FALLBACK:
        if path.exists():
            return path
    return None


def extract_file_path(hook_data: dict) -> str | None:
    """Extract the file path from tool input."""
    tool_name = hook_data.get("tool_name", "")
    tool_input = hook_data.get("tool_input", {})

    if tool_name in ("Read", "Edit", "Write"):
        return tool_input.get("file_path")
    elif tool_name == "Bash":
        # Try to extract file path from command
        cmd = tool_input.get("command", "")
        # Common patterns: editing/reading a file
        for token in cmd.split():
            if "/" in token and not token.startswith("-"):
                p = Path(token)
                if p.suffix and len(p.suffix) < 10:
                    return str(p)
    elif tool_name in ("Grep", "Glob"):
        return tool_input.get("path", ".")

    return None


def main():
    try:
        cli = find_wakatime()
        if not cli:
            sys.exit(0)

        hook_data = json.loads(sys.stdin.read())
        file_path = extract_file_path(hook_data)
        if not file_path:
            sys.exit(0)

        # Send heartbeat
        cmd = [
            str(cli),
            "--entity", file_path,
            "--plugin", "claude-code-hook",
            "--category", "coding",
            "--write",
        ]
        subprocess.run(cmd, capture_output=True, timeout=5)

    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
