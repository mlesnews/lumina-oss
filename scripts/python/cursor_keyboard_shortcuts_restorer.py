#!/usr/bin/env python3
"""
Cursor IDE Keyboard Shortcuts Restorer

Restores and applies comprehensive keyboard shortcuts mapping for Cursor IDE.
Explores and documents full capacities of the IDE application.

Tags: #CURSOR #IDE #KEYBOARD #SHORTCUTS #RESTORATION @JARVIS @DOIT
"""

import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CursorShortcutsRestorer")


class CursorKeyboardShortcutsRestorer:
    """
    Restore and apply Cursor IDE keyboard shortcuts

    Features:
    - Restore from backup/config
    - Apply comprehensive shortcuts mapping
    - Document all available shortcuts
    - Explore IDE capacities
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Cursor IDE paths (Windows)
        self.cursor_user_dir = Path.home() / "AppData" / "Roaming" / "Cursor" / "User"
        self.keybindings_file = self.cursor_user_dir / "keybindings.json"
        self.settings_file = self.cursor_user_dir / "settings.json"

        # Config paths
        self.config_dir = project_root / "config"
        self.shortcuts_config = self.config_dir / "cursor_ide_keyboard_shortcuts.json"
        self.backup_dir = project_root / "data" / "cursor_backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def backup_current_keybindings(self) -> bool:
        """Backup current keybindings before restoration"""
        try:
            if self.keybindings_file.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = self.backup_dir / f"keybindings_backup_{timestamp}.json"
                shutil.copy2(self.keybindings_file, backup_file)
                self.logger.info(f"✅ Backed up current keybindings to: {backup_file}")
                return True
            else:
                self.logger.info("ℹ️  No existing keybindings file to backup")
                return True
        except Exception as e:
            self.logger.error(f"❌ Failed to backup keybindings: {e}")
            return False

    def load_shortcuts_config(self) -> Optional[Dict[str, Any]]:
        """Load shortcuts configuration from config file"""
        try:
            if not self.shortcuts_config.exists():
                self.logger.error(f"❌ Shortcuts config not found: {self.shortcuts_config}")
                return None

            with open(self.shortcuts_config, 'r', encoding='utf-8') as f:
                config = json.load(f)

            self.logger.info(f"✅ Loaded shortcuts config from: {self.shortcuts_config}")
            return config.get("cursor_ide_keyboard_shortcuts", {})
        except Exception as e:
            self.logger.error(f"❌ Failed to load shortcuts config: {e}")
            return None

    def convert_to_vscode_keybindings_format(self, shortcuts_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert shortcuts config to VSCode/Cursor keybindings.json format

        Format:
        [
            {
                "key": "ctrl+k ctrl+s",
                "command": "workbench.action.openGlobalKeybindings",
                "when": "editorTextFocus"
            }
        ]
        """
        keybindings = []

        # Standard shortcuts
        standard_shortcuts = shortcuts_config.get("standard_shortcuts", {})
        for key, info in standard_shortcuts.items():
            keybindings.append({
                "key": key.lower(),
                "command": self._get_command_from_action(info.get("action", "")),
                "when": self._get_when_clause(info.get("context", "global"))
            })

        # Cursor-specific shortcuts
        cursor_shortcuts = shortcuts_config.get("cursor_specific_shortcuts", {})
        for key, info in cursor_shortcuts.items():
            keybindings.append({
                "key": key.lower(),
                "command": self._get_command_from_action(info.get("action", "")),
                "when": self._get_when_clause(info.get("context", "global"))
            })

        # AI-specific shortcuts
        ai_shortcuts = shortcuts_config.get("ai_specific_shortcuts", {})
        for key, info in ai_shortcuts.items():
            keybindings.append({
                "key": key.lower(),
                "command": self._get_command_from_action(info.get("action", "")),
                "when": self._get_when_clause(info.get("context", "global"))
            })

        return keybindings

    def _get_command_from_action(self, action: str) -> str:
        """Map action description to VSCode command ID"""
        action_lower = action.lower()

        # Command palette mappings
        command_mappings = {
            "open keyboard shortcuts": "workbench.action.openGlobalKeybindings",
            "command palette": "workbench.action.showCommands",
            "quick open": "workbench.action.quickOpen",
            "search in files": "workbench.action.findInFiles",
            "toggle terminal": "workbench.action.terminal.toggleTerminal",
            "toggle sidebar": "workbench.action.toggleSidebar",
            "open chat (cursor ai)": "cursor.chat.open",
            "inline edit (cursor ai)": "cursor.inlineEdit",
            "composer (cursor ai)": "cursor.composer.open",
            "chat history": "cursor.chat.history",
            "rename symbol": "editor.action.rename",
            "go to definition": "editor.action.revealDefinition",
            "peek definition": "editor.action.peekDefinition",
            "find next": "editor.action.nextMatchFindAction",
            "start debugging": "workbench.action.debug.start",
            "step over": "workbench.action.debug.stepOver",
            "step into": "workbench.action.debug.stepInto",
            "step out": "workbench.action.debug.stepOut",
            "continue": "workbench.action.debug.continue"
        }

        for key, command in command_mappings.items():
            if key in action_lower:
                return command

        # Default: try to construct from action
        return f"workbench.action.{action.replace(' ', '.').lower()}"

    def _get_when_clause(self, context: str) -> Optional[str]:
        """Get VSCode when clause from context"""
        context_mappings = {
            "global": None,
            "editor": "editorTextFocus",
            "search": "searchViewletFocus",
            "debug": "debugMode",
            "terminal": "terminalFocus",
            "ai": None  # AI commands work globally
        }
        return context_mappings.get(context.lower())

    def restore_keybindings(self, merge: bool = True) -> bool:
        """
        Restore keybindings from config

        Args:
            merge: If True, merge with existing keybindings. If False, replace.
        """
        try:
            # Backup current
            self.backup_current_keybindings()

            # Load config
            shortcuts_config = self.load_shortcuts_config()
            if not shortcuts_config:
                return False

            # Convert to keybindings format
            new_keybindings = self.convert_to_vscode_keybindings_format(shortcuts_config)

            # Load existing keybindings if merging
            existing_keybindings = []
            if merge and self.keybindings_file.exists():
                try:
                    with open(self.keybindings_file, 'r', encoding='utf-8') as f:
                        existing_keybindings = json.load(f)
                        if not isinstance(existing_keybindings, list):
                            existing_keybindings = []
                except Exception as e:
                    self.logger.warning(f"⚠️  Failed to load existing keybindings: {e}")

            # Merge or replace
            if merge:
                # Create a map of existing keybindings by key
                existing_map = {kb.get("key", ""): kb for kb in existing_keybindings}

                # Update or add new keybindings
                for kb in new_keybindings:
                    key = kb.get("key", "")
                    if key in existing_map:
                        # Update existing
                        existing_map[key].update(kb)
                    else:
                        # Add new
                        existing_keybindings.append(kb)

                final_keybindings = existing_keybindings
            else:
                final_keybindings = new_keybindings

            # Ensure directory exists
            self.keybindings_file.parent.mkdir(parents=True, exist_ok=True)

            # Write keybindings
            with open(self.keybindings_file, 'w', encoding='utf-8') as f:
                json.dump(final_keybindings, f, indent=2, ensure_ascii=False)

            self.logger.info(f"✅ Restored {len(final_keybindings)} keybindings to: {self.keybindings_file}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to restore keybindings: {e}", exc_info=True)
            return False

    def generate_shortcuts_documentation(self) -> Optional[Path]:
        """Generate comprehensive shortcuts documentation"""
        try:
            shortcuts_config = self.load_shortcuts_config()
            if not shortcuts_config:
                return None

            docs_dir = self.project_root / "docs" / "system"
            docs_dir.mkdir(parents=True, exist_ok=True)
            doc_file = docs_dir / "CURSOR_IDE_KEYBOARD_SHORTCUTS_COMPLETE.md"

            with open(doc_file, 'w', encoding='utf-8') as f:
                f.write("# Cursor IDE Keyboard Shortcuts - Complete Reference\n\n")
                f.write(f"**Generated**: {datetime.now().isoformat()}\n\n")
                f.write("## Overview\n\n")
                f.write("Complete mapping of all Cursor IDE keyboard shortcuts.\n\n")

                # Standard shortcuts
                f.write("## Standard Shortcuts\n\n")
                standard = shortcuts_config.get("standard_shortcuts", {})
                for key, info in standard.items():
                    f.write(f"### `{key}`\n")
                    f.write(f"- **Action**: {info.get('action', 'N/A')}\n")
                    f.write(f"- **Context**: {info.get('context', 'N/A')}\n")
                    f.write(f"- **Category**: {info.get('category', 'N/A')}\n\n")

                # Cursor-specific
                f.write("## Cursor-Specific Shortcuts\n\n")
                cursor = shortcuts_config.get("cursor_specific_shortcuts", {})
                for key, info in cursor.items():
                    f.write(f"### `{key}`\n")
                    f.write(f"- **Action**: {info.get('action', 'N/A')}\n")
                    f.write(f"- **Context**: {info.get('context', 'N/A')}\n\n")

                # AI-specific
                f.write("## AI-Specific Shortcuts\n\n")
                ai = shortcuts_config.get("ai_specific_shortcuts", {})
                for key, info in ai.items():
                    f.write(f"### `{key}`\n")
                    f.write(f"- **Action**: {info.get('action', 'N/A')}\n")
                    f.write(f"- **Context**: {info.get('context', 'N/A')}\n\n")

                # Hardware conflicts
                f.write("## Hardware Conflicts\n\n")
                conflicts = shortcuts_config.get("hardware_conflicts", {})
                for key, info in conflicts.items():
                    f.write(f"### `{key}`\n")
                    f.write(f"- **Hardware Action**: {info.get('hardware_action', 'N/A')}\n")
                    f.write(f"- **IDE Action**: {info.get('ide_action', 'N/A')}\n")
                    f.write(f"- **Solution**: {info.get('solution', 'N/A')}\n\n")

            self.logger.info(f"✅ Generated documentation: {doc_file}")
            return doc_file

        except Exception as e:
            self.logger.error(f"❌ Failed to generate documentation: {e}")
            return None

    def explore_ide_capacities(self) -> Dict[str, Any]:
        try:
            """Explore and document IDE capacities"""
            capacities = {
                "keybindings_file": str(self.keybindings_file),
                "keybindings_exists": self.keybindings_file.exists(),
                "settings_file": str(self.settings_file),
                "settings_exists": self.settings_file.exists(),
                "config_loaded": self.shortcuts_config.exists(),
                "total_shortcuts": 0,
                "categories": []
            }

            shortcuts_config = self.load_shortcuts_config()
            if shortcuts_config:
                # Count shortcuts
                standard = shortcuts_config.get("standard_shortcuts", {})
                cursor = shortcuts_config.get("cursor_specific_shortcuts", {})
                ai = shortcuts_config.get("ai_specific_shortcuts", {})
                capacities["total_shortcuts"] = len(standard) + len(cursor) + len(ai)

                # Collect categories
                categories = set()
                for info in list(standard.values()) + list(cursor.values()) + list(ai.values()):
                    cat = info.get("category", "")
                    if cat:
                        categories.add(cat)
                capacities["categories"] = sorted(list(categories))

            return capacities


        except Exception as e:
            self.logger.error(f"Error in explore_ide_capacities: {e}", exc_info=True)
            raise
def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(
            description="Restore Cursor IDE keyboard shortcuts"
        )
        parser.add_argument(
            "--restore",
            action="store_true",
            help="Restore keybindings from config"
        )
        parser.add_argument(
            "--merge",
            action="store_true",
            default=True,
            help="Merge with existing keybindings (default: True)"
        )
        parser.add_argument(
            "--replace",
            action="store_true",
            help="Replace existing keybindings (overrides --merge)"
        )
        parser.add_argument(
            "--backup",
            action="store_true",
            help="Backup current keybindings"
        )
        parser.add_argument(
            "--document",
            action="store_true",
            help="Generate shortcuts documentation"
        )
        parser.add_argument(
            "--explore",
            action="store_true",
            help="Explore IDE capacities"
        )

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        restorer = CursorKeyboardShortcutsRestorer(project_root)

        if args.backup:
            restorer.backup_current_keybindings()

        if args.restore:
            merge = not args.replace
            success = restorer.restore_keybindings(merge=merge)
            if success:
                print("✅ Keyboard shortcuts restored successfully")
            else:
                print("❌ Failed to restore keyboard shortcuts")
                return 1

        if args.document:
            doc_file = restorer.generate_shortcuts_documentation()
            if doc_file:
                print(f"✅ Documentation generated: {doc_file}")
            else:
                print("❌ Failed to generate documentation")

        if args.explore:
            capacities = restorer.explore_ide_capacities()
            print("\n" + "="*80)
            print("CURSOR IDE CAPACITIES")
            print("="*80)
            print(f"Keybindings File: {capacities['keybindings_file']}")
            print(f"Keybindings Exists: {capacities['keybindings_exists']}")
            print(f"Total Shortcuts: {capacities['total_shortcuts']}")
            print(f"Categories: {', '.join(capacities['categories'])}")
            print("="*80)

        if not any([args.restore, args.backup, args.document, args.explore]):
            parser.print_help()

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())