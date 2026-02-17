#!/usr/bin/env python3
"""
JARVIS Switch to KAIJU Script

Temporarily switches Cursor settings to use KAIJU Number Eight (Desktop PC Ollama) 
when local Ollama (ULTRON) is unavailable.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent


def switch_to_kaiju(backup: bool = True) -> Dict[str, Any]:
    """
    Switch Cursor settings to use KAIJU as default model.

    Args:
        backup: Whether to backup current settings before modifying

    Returns:
        Dict with status and details
    """
    settings_path = PROJECT_ROOT / ".cursor" / "settings.json"
    backup_path = PROJECT_ROOT / ".cursor" / f"settings.json.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    result = {
        "status": "UNKNOWN",
        "backup_created": False,
        "backup_path": None,
        "changes_made": [],
        "error": None
    }

    if not settings_path.exists():
        result["status"] = "ERROR"
        result["error"] = f"Settings file not found: {settings_path}"
        return result

    try:
        # Read current settings
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        # Backup if requested
        if backup:
            shutil.copy2(settings_path, backup_path)
            result["backup_created"] = True
            result["backup_path"] = str(backup_path)
            print(f"✅ Backup created: {backup_path}")

        # Track changes
        changes = []

        # Change default models to KAIJU
        if settings.get("cursor.chat.defaultModel") != "KAIJU":
            old_value = settings.get("cursor.chat.defaultModel", "NOT_SET")
            settings["cursor.chat.defaultModel"] = "KAIJU"
            changes.append(f"cursor.chat.defaultModel: {old_value} → KAIJU")

        if settings.get("cursor.composer.defaultModel") != "KAIJU":
            old_value = settings.get("cursor.composer.defaultModel", "NOT_SET")
            settings["cursor.composer.defaultModel"] = "KAIJU"
            changes.append(f"cursor.composer.defaultModel: {old_value} → KAIJU")

        if settings.get("cursor.agent.defaultModel") != "KAIJU":
            old_value = settings.get("cursor.agent.defaultModel", "NOT_SET")
            settings["cursor.agent.defaultModel"] = "KAIJU"
            changes.append(f"cursor.agent.defaultModel: {old_value} → KAIJU")

        if settings.get("cursor.inlineCompletion.defaultModel") != "KAIJU":
            old_value = settings.get("cursor.inlineCompletion.defaultModel", "NOT_SET")
            settings["cursor.inlineCompletion.defaultModel"] = "KAIJU"
            changes.append(f"cursor.inlineCompletion.defaultModel: {old_value} → KAIJU")

        # Write updated settings
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)

        result["status"] = "SUCCESS"
        result["changes_made"] = changes

        print("✅ Successfully switched to KAIJU")
        print()
        print("Changes made:")
        for change in changes:
            print(f"  • {change}")
        print()
        print("⚠️  IMPORTANT: Restart Cursor IDE for changes to take effect!")
        print("   Or manually select 'KAIJU (Iron Legion)' in the model selector.")

    except json.JSONDecodeError as e:
        result["status"] = "ERROR"
        result["error"] = f"Invalid JSON: {e}"
    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)

    return result


def restore_from_backup(backup_path: Path) -> Dict[str, Any]:
    """
    Restore Cursor settings from backup.

    Args:
        backup_path: Path to backup file

    Returns:
        Dict with status and details
    """
    settings_path = PROJECT_ROOT / ".cursor" / "settings.json"

    result = {
        "status": "UNKNOWN",
        "error": None
    }

    if not backup_path.exists():
        result["status"] = "ERROR"
        result["error"] = f"Backup file not found: {backup_path}"
        return result

    try:
        shutil.copy2(backup_path, settings_path)
        result["status"] = "SUCCESS"
        print(f"✅ Restored settings from: {backup_path}")
        print("⚠️  Restart Cursor IDE for changes to take effect!")
    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)

    return result


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Switch Cursor to use KAIJU (NAS Ollama)")
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Don't create backup before modifying settings"
    )
    parser.add_argument(
        "--restore",
        type=Path,
        help="Restore from backup file (provide path)"
    )

    args = parser.parse_args()

    if args.restore:
        result = restore_from_backup(args.restore)
    else:
        result = switch_to_kaiju(backup=not args.no_backup)

    if result["status"] == "ERROR":
        print(f"❌ Error: {result['error']}")
        return 1

    return 0


if __name__ == "__main__":
    import sys


    sys.exit(main())