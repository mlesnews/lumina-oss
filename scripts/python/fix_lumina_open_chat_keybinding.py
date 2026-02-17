#!/usr/bin/env python3
"""
Fix Lumina Open Chat keybinding – remap lumina.openLuminaAIChat to workbench.action.openChat

When the Lumina/JARVIS Chat extension is not installed, the command
lumina.openLuminaAIChat is missing and triggers "command not found". This script
updates the user Cursor keybindings so any binding to that command instead
opens Cursor Chat (workbench.action.openChat).

#automation
"""

from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

MISSING_COMMAND = "lumina.openLuminaAIChat"
OPEN_CHAT_COMMAND = "workbench.action.openChat"


def find_cursor_keybindings_file() -> Path:
    possible = [
        Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "keybindings.json",
        Path.home() / ".cursor" / "User" / "keybindings.json",
        Path.home() / "Library" / "Application Support" / "Cursor" / "User" / "keybindings.json",
    ]
    for p in possible:
        if p.exists():
            return p
    default = Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "keybindings.json"
    default.parent.mkdir(parents=True, exist_ok=True)
    return default


def main() -> int:
    path = find_cursor_keybindings_file()
    print(f"Keybindings file: {path}")

    # Load
    bindings = []
    if path.exists():
        try:
            with path.open(encoding="utf-8") as f:
                raw = json.load(f)
                bindings = raw if isinstance(raw, list) else []
        except Exception as e:
            print(f"Error reading keybindings: {e}", file=sys.stderr)
            return 1

    # Backup
    if path.exists():
        backup = path.parent / f"keybindings_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        shutil.copy2(path, backup)
        print(f"Backed up to {backup}")

    # Remap any binding from lumina.openLuminaAIChat to workbench.action.openChat
    changed = 0
    for item in bindings:
        if not isinstance(item, dict):
            continue
        if item.get("command") == MISSING_COMMAND:
            item["command"] = OPEN_CHAT_COMMAND
            key = item.get("key", "?")
            print(f"Remapped: {key} → {OPEN_CHAT_COMMAND} (was {MISSING_COMMAND})")
            changed += 1

    if not changed:
        # Ensure Open Chat is bound: add a common fallback if not already present
        has_open_chat = any(
            isinstance(b, dict) and b.get("command") == OPEN_CHAT_COMMAND
            for b in bindings
        )
        if not has_open_chat:
            bindings.append({
                "key": "ctrl+alt+l",
                "command": OPEN_CHAT_COMMAND,
            })
            print(f"Added: ctrl+alt+l → {OPEN_CHAT_COMMAND}")
            changed += 1

    if not changed:
        print("No binding to remap; Open Chat already configured.")
        return 0

    # Write
    with path.open("w", encoding="utf-8") as f:
        json.dump(bindings, f, indent=2)
    print("Keybindings saved. Restart Cursor if the change doesn’t apply immediately.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
