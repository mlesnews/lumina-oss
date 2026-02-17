#!/usr/bin/env python3
"""
Apply all Lumina/JARVIS Chat workaround steps in one shot.

1. Fix keybinding: remap lumina.openLuminaAIChat → workbench.action.openChat; add Ctrl+Alt+L.
2. JARVIS master chat: consolidate agents and pin session.
3. Apply JARVIS pinned config to Cursor user settings (pinnedSessions, defaultSession, alwaysOpenPinned).

Run from repo root. Restart Cursor after running.

#automation
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent
    steps = [
        ("Fix Lumina Open Chat keybinding", [sys.executable, str(script_dir / "fix_lumina_open_chat_keybinding.py")]),
        ("JARVIS consolidate + pin", [sys.executable, str(script_dir / "jarvis_master_chat_session.py"), "--consolidate", "--pin"]),
        ("Apply JARVIS pinned to Cursor settings", [sys.executable, str(script_dir / "apply_jarvis_pinned_to_cursor_settings.py")]),
    ]
    for label, cmd in steps:
        print(f"\n--- {label} ---")
        r = subprocess.run(cmd, cwd=str(repo_root))
        if r.returncode != 0:
            print(f"Step failed: {label}", file=sys.stderr)
            return r.returncode
    print("\n✅ All steps done. Restart Cursor to apply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
