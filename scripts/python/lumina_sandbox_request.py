#!/usr/bin/env python3
"""
LUMINA A-Side Sandbox Request (run inside Cursor / Agent sandbox)
=================================================================
Writes a job file for the B-Side daemon to execute. No network required — only
file I/O in the workspace. Use this when the Agent needs to run a script that
requires network (drive mapping, backups, NAS deploy, etc.). The B-Side daemon
must be running (started by user or Task Scheduler).

#automation #workaround #cursor-sandbox
"""

import json
import sys
import time
import uuid
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "lumina_sandbox.json"
REQUEST_DIR_DEFAULT = PROJECT_ROOT / "data" / "lumina_sandbox" / "requests"
RESPONSE_DIR_DEFAULT = PROJECT_ROOT / "data" / "lumina_sandbox" / "responses"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config not found: {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def submit_request(action_id: str, wait_seconds: int = 60, poll_interval: float = 2.0) -> dict:
    """
    Submit a request to the B-Side daemon and optionally wait for the response.

    Args:
        action_id: One of the allowlisted ids in config/lumina_sandbox.json
                   (e.g. map_network_drives, setup_nas_git_repos, execute_all_backups).
        wait_seconds: If > 0, poll for response file up to this many seconds.
        poll_interval: Seconds between polls when waiting.

    Returns:
        If wait_seconds > 0 and response found: the response dict (ok, stdout, stderr, exit_code).
        If wait_seconds == 0: {"submitted": True, "request_id": "...", "response_path": "..."}.
        On error: {"ok": False, "error": "..."}.
    """
    config = load_config()
    request_dir = PROJECT_ROOT / config.get("request_dir", "data/lumina_sandbox/requests")
    response_dir = PROJECT_ROOT / config.get("response_dir", "data/lumina_sandbox/responses")
    request_dir.mkdir(parents=True, exist_ok=True)
    response_dir.mkdir(parents=True, exist_ok=True)

    allowed_ids = [a["id"] for a in config.get("allowed_actions", [])]
    if action_id not in allowed_ids:
        return {"ok": False, "error": f"Action not allowlisted: {action_id}. Allowed: {allowed_ids}"}

    request_id = f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    request_data = {
        "request_id": request_id,
        "action_id": action_id,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    }
    request_path = request_dir / f"{request_id}.json"
    with open(request_path, "w", encoding="utf-8") as f:
        json.dump(request_data, f, indent=2)

    if wait_seconds <= 0:
        return {
            "submitted": True,
            "request_id": request_id,
            "request_path": str(request_path),
            "response_path": str(response_dir / f"{request_id}.json"),
            "message": "Request submitted. Ensure B-Side daemon is running; then read the response file.",
        }

    response_path = response_dir / f"{request_id}.json"
    deadline = time.monotonic() + wait_seconds
    while time.monotonic() < deadline:
        if response_path.exists():
            try:
                with open(response_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        time.sleep(poll_interval)

    return {
        "ok": False,
        "error": f"No response within {wait_seconds}s. Is the B-Side daemon running?",
        "request_id": request_id,
        "response_path": str(response_path),
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Submit a B-Side sandbox request (A-Side: run from Cursor/Agent; no network needed)."
    )
    parser.add_argument("action_id", help="Allowlisted action id (e.g. map_network_drives, execute_all_backups)")
    parser.add_argument("--wait", type=int, default=120, metavar="SEC",
                        help="Seconds to wait for response (default 120). Use 0 to submit only.")
    parser.add_argument("--poll", type=float, default=2.0, help="Poll interval when waiting (default 2.0)")
    args = parser.parse_args()

    result = submit_request(args.action_id, wait_seconds=args.wait, poll_interval=args.poll)
    print(json.dumps(result, indent=2))
    if result.get("ok") is False and "error" in result:
        sys.exit(1)
    sys.exit(0 if result.get("ok", result.get("submitted", False)) else 1)


if __name__ == "__main__":
    main()
