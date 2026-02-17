#!/usr/bin/env python3
"""Simple MASTER -> Padawan todolist sync utility.

Usage:
  python abacus_todolist_sync.py --sync
  python abacus_todolist_sync.py --init

Behavior:
  - Ensures `.abacus/master_todolist.json` exists (creates sample when `--init`).
  - Writes `.abacus/padawan_todolist.json` by filtering `master` tasks marked `padawan==true`
    or with priority <= configured threshold.

This is intentionally small and file-based so Abacus desktop or other local tools
can call it as a migration/fallback mechanism for todolist mirroring.
"""

from __future__ import annotations

import argparse
import datetime
import json
from pathlib import Path
from typing import Any, Dict, List
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
import logging
logger = logging.getLogger("abacus_todolist_sync")


try:
    # lightweight telemetry (optional)
    from telemetry.introspection import snapshot_ssot
    from telemetry.tracing import init_collector, trace_event

    telemetry_available = True
except Exception:
    telemetry_available = False

ROOT = Path(__file__).resolve().parents[2]
ABACUS_DIR = ROOT / ".abacus"
MASTER_FILE = ABACUS_DIR / "master_todolist.json"
PADAWAN_FILE = ABACUS_DIR / "padawan_todolist.json"



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def load_json(path: Path) -> Dict[str, Any]:
    try:
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)


    except Exception as e:
        logger.error(f"Error in load_json: {e}", exc_info=True)
        raise
def save_json(path: Path, data: Dict[str, Any]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


    except Exception as e:
        logger.error(f"Error in save_json: {e}", exc_info=True)
        raise
def sync(
    master_path: Path = MASTER_FILE,
    padawan_path: Path = PADAWAN_FILE,
    priority_cutoff: int = 2,
) -> int:
    m = load_json(master_path)
    tasks: List[Dict[str, Any]] = m.get("tasks", []) if m else []

    # Padawan selection rules:
    # - task['padawan'] == True
    # - OR priority <= priority_cutoff and status != 'done'
    padawan: List[Dict[str, Any]] = []
    for t in tasks:
        try:
            if t.get("padawan"):
                pt = dict(t)
                pt.setdefault("enhanced", True)
                padawan.append(pt)
                continue
            pr = int(t.get("priority", 99))
            if pr <= priority_cutoff and t.get("status") != "done":
                pt = dict(t)
                pt.setdefault("enhanced", True)
                padawan.append(pt)
        except Exception:
            continue

    payload = {
        "meta": {
            "synced_at": datetime.datetime.utcnow().isoformat() + "Z",
            "source": "abacus_todolist_sync.py",
            "master_count": len(tasks),
            "padawan_count": len(padawan),
        },
        "tasks": padawan,
    }

    save_json(padawan_path, payload)
    return len(padawan)


def init_sample(master_path: Path = MASTER_FILE) -> None:
    try:
        if master_path.exists():
            print(f"Master todolist already exists: {master_path}")
            return
        sample = {
            "meta": {
                "created_at": datetime.datetime.utcnow().isoformat() + "Z",
                "created_by": "abacus_todolist_sync.py",
            },
            "tasks": [
                {
                    "id": "m-001",
                    "title": "Fix JARVIS SuperAgent error recovery",
                    "priority": 1,
                    "status": "open",
                    "padawan": True,
                },
                {
                    "id": "m-002",
                    "title": "Add Iron Legion node health checks",
                    "priority": 1,
                    "status": "open",
                    "padawan": True,
                },
                {
                    "id": "m-003",
                    "title": "Implement monitoring endpoints",
                    "priority": 2,
                    "status": "open",
                    "padawan": False,
                },
            ],
        }
        save_json(master_path, sample)
        print(f"Created sample master todolist at {master_path}")


    except Exception as e:
        logger.error(f"Error in init_sample: {e}", exc_info=True)
        raise
def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--sync", action="store_true", help="Run MASTER -> Padawan sync")
    p.add_argument(
        "--init", action="store_true", help="Create sample MASTER todolist if missing"
    )
    p.add_argument(
        "--show", choices=["master", "padawan"], help="Show the requested list"
    )
    p.add_argument(
        "--priority-cutoff",
        type=int,
        default=2,
        help="Priority cutoff for padawan selection",
    )
    args = p.parse_args()

    if args.init:
        if telemetry_available:
            init_collector()
        with (
            trace_event("abacus.init", {"action": "init_master"})
            if telemetry_available
            else _noop()
        ):
            init_sample()

    if args.sync:
        if telemetry_available:
            init_collector()
        with (
            trace_event("abacus.sync", {"priority_cutoff": args.priority_cutoff})
            if telemetry_available
            else _noop()
        ):
            count = sync(priority_cutoff=args.priority_cutoff)
        print(f"Synced padawan tasks: {count}")

    # snapshot SSoT for introspection (non-destructive)
    if telemetry_available:
        try:
            snapshot_ssot()
        except Exception:
            pass


class _NoopCtx:
    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc, tb):
        return False


def _noop():
    try:
        return _NoopCtx()

        if args.show == "master":
            print(json.dumps(load_json(MASTER_FILE), indent=2))
        elif args.show == "padawan":
            print(json.dumps(load_json(PADAWAN_FILE), indent=2))


    except Exception as e:
        logger.error(f"Error in _noop: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()