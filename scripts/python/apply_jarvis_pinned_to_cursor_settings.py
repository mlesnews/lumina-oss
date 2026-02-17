#!/usr/bin/env python3
"""
Apply JARVIS pinned session config to Cursor user settings.json

Merges cursor.chat.pinnedSessions, cursor.chat.defaultSession,
cursor.chat.alwaysOpenPinned from config/jarvis_master_chat_cursor_config.json
into Cursor User settings.json. Creates backup before writing.

#automation
"""

from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


def find_cursor_settings() -> Path:
    possible = [
        Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "settings.json",
        Path.home() / ".cursor" / "User" / "settings.json",
        Path.home() / "Library" / "Application Support" / "Cursor" / "User" / "settings.json",
    ]
    for p in possible:
        if p.exists():
            return p
    default = Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "settings.json"
    default.parent.mkdir(parents=True, exist_ok=True)
    return default


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent
    config_path = repo_root / "config" / "jarvis_master_chat_cursor_config.json"
    if not config_path.exists():
        print(f"Config not found: {config_path}", file=sys.stderr)
        return 1

    with config_path.open(encoding="utf-8") as f:
        config = json.load(f)
    jarvis_settings = (config.get("cursor") or {}).get("settings") or {}
    if not jarvis_settings:
        print("No cursor.settings in config", file=sys.stderr)
        return 1

    path = find_cursor_settings()
    print(f"Cursor settings: {path}")

    settings = {}
    if path.exists():
        try:
            with path.open(encoding="utf-8") as f:
                settings = json.load(f)
            if not isinstance(settings, dict):
                settings = {}
        except Exception as e:
            print(f"Error reading settings: {e}", file=sys.stderr)
            return 1

    # Backup
    if path.exists():
        backup = path.parent / f"settings_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        shutil.copy2(path, backup)
        print(f"Backed up to {backup}")

    # Merge JARVIS pinned keys
    for key, value in jarvis_settings.items():
        if key.startswith("cursor.chat."):
            settings[key] = value
            print(f"Set {key}")

    with path.open("w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
    print("Settings saved. Restart Cursor to apply JARVIS pinned session.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
