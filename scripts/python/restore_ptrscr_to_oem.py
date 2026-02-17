#!/usr/bin/env python3
"""
Restore PTRSCR (Print Screen) to OEM behavior.

Removes any Cursor/VS Code keybinding that uses Print Screen so the key
behaves as OEM (normal Windows screen capture). #automation
"""

import json
import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_adaptive_logger import get_adaptive_logger

    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging

        logging.basicConfig(level=logging.INFO)
        get_logger = lambda name: logging.getLogger(name)

logger = get_logger("RestorePTRSCR")


def find_cursor_keybindings_file() -> Path:
    """Find Cursor IDE keybindings.json file."""
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


def is_print_screen_key(key: str) -> bool:
    """True if key is Print Screen (any variant)."""
    if not key:
        return False
    k = key.lower()
    return "printscreen" in k or "print screen" in k or "prtsc" in k or k == "snapshot"


def restore_ptrscr_to_oem() -> bool:
    """Remove any Print Screen keybindings from Cursor keybindings so PTRSCR returns to OEM."""
    path = find_cursor_keybindings_file()
    logger.info("Restore PTRSCR to OEM: removing Print Screen keybindings from Cursor")
    logger.info("Keybindings file: %s", path)

    if not path.exists():
        logger.info("No keybindings file found; PTRSCR is already OEM.")
        return True

    try:
        with open(path, encoding="utf-8") as f:
            data = f.read()
    except Exception as e:
        logger.error("Failed to read keybindings: %s", e)
        return False

    try:
        keybindings = json.loads(data)
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in keybindings: %s", e)
        return False

    if not isinstance(keybindings, list):
        logger.warning("Keybindings is not a list; leaving file unchanged.")
        return True

    original_count = len(keybindings)
    kept = [kb for kb in keybindings if not is_print_screen_key(kb.get("key") or "")]
    removed_count = original_count - len(kept)

    if removed_count == 0:
        logger.info("No Print Screen keybindings found; PTRSCR is already OEM.")
        return True

    for kb in keybindings:
        if is_print_screen_key(kb.get("key") or ""):
            logger.info("Removing: key=%s command=%s", kb.get("key"), kb.get("command"))

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(kept, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error("Failed to write keybindings: %s", e)
        return False

    logger.info("Removed %d Print Screen keybinding(s). PTRSCR restored to OEM.", removed_count)
    return True


def main() -> int:
    ok = restore_ptrscr_to_oem()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
