#!/usr/bin/env python3
"""
Apply Cursor IDE Keybindings - Keep All / Accept All

Applies keyboard shortcuts for "Keep All" / "Accept All" to Cursor IDE.
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

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

logger = get_logger("ApplyKeybindings")


def find_cursor_keybindings_file() -> Path:
    try:
        """Find Cursor IDE keybindings.json file"""
        # Common locations for Cursor IDE keybindings
        possible_locations = [
            Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "keybindings.json",
            Path.home() / ".cursor" / "User" / "keybindings.json",
            Path.home() / "Library" / "Application Support" / "Cursor" / "User" / "keybindings.json",
        ]

        for location in possible_locations:
            if location.exists():
                logger.info(f"✅ Found keybindings file: {location}")
                return location

        # If not found, use the most common Windows location
        default_location = Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "keybindings.json"
        default_location.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"📝 Will create keybindings file: {default_location}")
        return default_location


    except Exception as e:
        logger.error(f"Error in find_cursor_keybindings_file: {e}", exc_info=True)
        raise
def apply_keybindings():
    """Apply Keep All / Accept All keybindings to Cursor IDE"""

    logger.info("=" * 70)
    logger.info("🔧 Applying Cursor IDE Keybindings - Keep All / Accept All")
    logger.info("=" * 70)

    # Read our keybindings config
    config_file = project_root / "config" / "cursor_keybindings_accept_all.json"
    if not config_file.exists():
        logger.error(f"❌ Keybindings config not found: {config_file}")
        return False

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            new_keybindings = json.load(f)
        logger.info(f"✅ Loaded keybindings from: {config_file}")
    except Exception as e:
        logger.error(f"❌ Failed to read keybindings config: {e}")
        return False

    # Find Cursor keybindings file
    cursor_keybindings_file = find_cursor_keybindings_file()

    # Backup existing keybindings
    if cursor_keybindings_file.exists():
        backup_file = cursor_keybindings_file.parent / f"keybindings_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            shutil.copy2(cursor_keybindings_file, backup_file)
            logger.info(f"✅ Backed up existing keybindings to: {backup_file}")
        except Exception as e:
            logger.warning(f"⚠️  Could not backup keybindings: {e}")

    # Read existing keybindings (if any)
    existing_keybindings = []
    if cursor_keybindings_file.exists():
        try:
            with open(cursor_keybindings_file, 'r', encoding='utf-8') as f:
                existing_keybindings = json.load(f)
                if not isinstance(existing_keybindings, list):
                    existing_keybindings = []
            logger.info(f"✅ Loaded {len(existing_keybindings)} existing keybindings")
        except Exception as e:
            logger.warning(f"⚠️  Could not read existing keybindings: {e}")
            existing_keybindings = []

    # Merge keybindings (avoid duplicates)
    keybindings_to_add = []
    existing_keys = {f"{kb.get('key')}_{kb.get('command')}" for kb in existing_keybindings}

    for new_kb in new_keybindings:
        key_id = f"{new_kb.get('key')}_{new_kb.get('command')}"
        if key_id not in existing_keys:
            keybindings_to_add.append(new_kb)
            logger.info(f"   ➕ Adding: {new_kb.get('key')} → {new_kb.get('command')}")
        else:
            logger.debug(f"   ⏭️  Skipping duplicate: {new_kb.get('key')} → {new_kb.get('command')}")

    # Combine existing and new keybindings
    all_keybindings = existing_keybindings + keybindings_to_add

    # Write keybindings
    try:
        with open(cursor_keybindings_file, 'w', encoding='utf-8') as f:
            json.dump(all_keybindings, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Keybindings applied to: {cursor_keybindings_file}")
        logger.info(f"   Total keybindings: {len(all_keybindings)}")
        logger.info("")
        logger.info("📋 Keyboard Shortcuts:")
        logger.info("   Ctrl+Alt+Enter → Keep All / Accept All Changes")
        logger.info("")
        logger.info("⚠️  IMPORTANT: Restart Cursor IDE for keybindings to take effect")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to write keybindings: {e}")
        return False


def main():
    """Main entry point"""
    success = apply_keybindings()
    return 0 if success else 1


if __name__ == "__main__":


    sys.exit(main())