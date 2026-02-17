#!/usr/bin/env python3
"""
JARVIS Phase 3 – integration checklist / validation (#automation)

Verifies .cursor/commands and jarvis/ skeleton exist; prints checklist for routing, tests, author display.
Run from repo root or scripts/python/.

Usage: python scripts/python/jarvis_phase3_check.py
Reference: docs/system/JARVIS_PHASE_3_4_NEXT_STEPS.md
"""

from __future__ import annotations

import sys
from pathlib import Path


def _find_repo_root() -> Path:
    start = Path.cwd()
    for p in [start, *start.parents]:
        if (p / "config" / "auto_update.yaml").exists() or (p / ".git").exists():
            return p
    return start


def main() -> int:
    root = _find_repo_root()
    cursor_commands = root / ".cursor" / "commands"
    jarvis_agents = root / "jarvis" / "agents"
    jarvis_ide = root / "jarvis" / "ide"
    config_yaml = root / "config" / "auto_update.yaml"

    checks = [
        (cursor_commands.exists(), ".cursor/commands/ exists (source of truth for agents)"),
        ((cursor_commands / "@jarvis.md").exists() or (cursor_commands / "jarvis.md").exists(), ".cursor/commands/ has JARVIS entry"),
        (jarvis_agents.exists(), "jarvis/agents/ skeleton exists"),
        (jarvis_ide.exists(), "jarvis/ide/ skeleton exists"),
        (config_yaml.exists(), "config/auto_update.yaml exists"),
    ]
    all_ok = all(c[0] for c in checks)

    print("JARVIS Phase 3 – integration check\n")
    for ok, msg in checks:
        print(f"  {'[OK]' if ok else '[--]'} {msg}")
    print()
    print("Phase 3 checklist (manual):")
    print("  [ ] Configure JARVIS routing (or keep .cursor/commands as source of truth)")
    print("  [ ] Test all agents (orchestrators, droids, specialized, tasks)")
    print("  [ ] Verify author display when invoking agents")
    print()
    print("See docs/system/JARVIS_PHASE_3_4_NEXT_STEPS.md for full Phase 3–4 steps.")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
