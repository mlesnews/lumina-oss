#!/usr/bin/env python3
"""
JARVIS Cursor IDE Keyboard Shortcuts Mapper
Complete mapping of all Cursor IDE keyboard shortcuts for all @FF (function keys)

@JARVIS @CURSOR @IDE @FF @KEYBOARD @SHORTCUTS
"""

import sys
import json
from pathlib import Path
import logging
logger = logging.getLogger("jarvis_cursor_shortcuts_mapper")


project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def main():
    try:
        """Display Cursor IDE keyboard shortcuts mapping"""
        print("=" * 70)
        print("⌨️  CURSOR IDE KEYBOARD SHORTCUTS MAPPING")
        print("   Complete mapping for all @FF (Function Keys)")
        print("=" * 70)
        print()

        # Load shortcuts config
        shortcuts_file = project_root / "config" / "cursor_ide_keyboard_shortcuts.json"

        if not shortcuts_file.exists():
            print("⚠️  Shortcuts config not found. Creating default...")
            # Config should have been created by previous tool call
            return

        with open(shortcuts_file, "r", encoding="utf-8") as f:
            shortcuts = json.load(f)

        config = shortcuts.get("cursor_ide_keyboard_shortcuts", {})

        # Display Function Keys
        print("🔢 FUNCTION KEYS (@FF):")
        print("-" * 70)
        function_keys = config.get("function_keys", {})
        for key, info in sorted(function_keys.items()):
            default = info.get("default", "Unknown")
            alternate = info.get("alternate", "")
            category = info.get("category", "")
            note = info.get("note", "")

            print(f"  {key:4} → {default}")
            if alternate:
                print(f"       Alt: {alternate}")
            print(f"       Category: {category}")
            if note:
                print(f"       ⚠️  Note: {note}")
            print()

        # Display Function Key Combinations
        print("🔀 FUNCTION KEY COMBINATIONS:")
        print("-" * 70)
        combinations = config.get("function_key_combinations", {})
        for combo, info in sorted(combinations.items()):
            action = info.get("action", "Unknown")
            category = info.get("category", "")
            note = info.get("note", "")

            print(f"  {combo:12} → {action}")
            print(f"              Category: {category}")
            if note:
                print(f"              ⚠️  Note: {note}")
            print()

        # Display Cursor-Specific Shortcuts
        print("🎯 CURSOR-SPECIFIC SHORTCUTS:")
        print("-" * 70)
        cursor_shortcuts = config.get("cursor_specific_shortcuts", {})
        for combo, info in sorted(cursor_shortcuts.items()):
            if isinstance(info, dict):
                action = info.get("action", "Unknown")
                category = info.get("category", "")
            else:
                action = info
                category = "general"

            print(f"  {combo:20} → {action}")
            if category:
                print(f"                      Category: {category}")
            print()

        # Display AI-Specific Shortcuts
        print("🤖 AI-SPECIFIC SHORTCUTS (Cursor AI):")
        print("-" * 70)
        ai_shortcuts = config.get("ai_specific_shortcuts", {})
        for combo, info in sorted(ai_shortcuts.items()):
            if isinstance(info, dict):
                action = info.get("action", "Unknown")
                category = info.get("category", "")
            else:
                action = info
                category = "ai"

            print(f"  {combo:20} → {action}")
            if category:
                print(f"                      Category: {category}")
            print()

        # Display Hardware Conflicts
        print("⚠️  HARDWARE CONFLICTS:")
        print("-" * 70)
        conflicts = config.get("hardware_conflicts", {})
        for combo, info in sorted(conflicts.items()):
            hardware = info.get("hardware_action", "Unknown")
            ide = info.get("ide_action", "Unknown")
            conflict = info.get("conflict", "")
            solution = info.get("solution", "")
            note = info.get("note", "")

            print(f"  {combo:12}")
            print(f"    Hardware: {hardware}")
            print(f"    IDE:      {ide}")
            print(f"    Conflict: {conflict}")
            print(f"    Solution: {solution}")
            if note:
                print(f"    ⚠️  {note}")
            print()

        # Display Customization Info
        print("⚙️  CUSTOMIZATION:")
        print("-" * 70)
        customization = config.get("customization", {})
        for key, value in customization.items():
            if key != "tags":
                print(f"  {key}: {value}")
        print()

        print("=" * 70)
        print("✅ Cursor IDE Keyboard Shortcuts Mapping Complete!")
        print("=" * 70)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()