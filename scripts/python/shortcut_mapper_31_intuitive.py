#!/usr/bin/env python3
"""
SHORTCUT MAPPER 31 - Human-Intuitive Keyboard Shortcut Mapping

Map all keyboard shortcuts for each and every application and Windows OS.
Default mappings exist but don't include everything.
Complete list that can be manually updated and propagated.

Human-intuitive fashion - easy to understand and use.

Prime number: 31 (Mapping number - comprehensive coverage)

Tags: #SHORTCUT-MAPPER #KEYBOARD-SHORTCUTS #WINDOWS-OS #APPLICATIONS #HUMAN-INTUITIVE @JARVIS @TEAM
"""

import sys
import json
import winreg
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from standardized_timestamp_logging import get_timestamp_logger
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

logger = get_logger("ShortcutMapper31")
ts_logger = get_timestamp_logger()


class ShortcutCategory(Enum):
    """Shortcut category"""
    WINDOWS_OS = "windows_os"
    APPLICATION = "application"
    CURSOR_IDE = "cursor_ide"
    VSCODE = "vscode"
    BROWSER = "browser"
    SYSTEM = "system"


class ShortcutType(Enum):
    """Shortcut type"""
    DEFAULT = "default"  # Default system mapping
    CUSTOM = "custom"  # Custom/user mapping
    MISSING = "missing"  # Not in default mappings
    PROPAGATED = "propagated"  # Propagated to other systems


@dataclass
class KeyboardShortcut:
    """A keyboard shortcut"""
    shortcut_id: str
    application: str
    category: ShortcutCategory
    action: str
    key_combination: str
    description: str
    shortcut_type: ShortcutType = ShortcutType.DEFAULT
    human_intuitive_name: Optional[str] = None
    manually_updated: bool = False
    propagated: bool = False
    notes: str = ""


@dataclass
class ApplicationMapping:
    """Application shortcut mapping"""
    application_name: str
    shortcuts: List[KeyboardShortcut]
    default_count: int = 0
    custom_count: int = 0
    missing_count: int = 0
    manually_updated_count: int = 0


class SHORTCUTMAPPER31:
    """
    SHORTCUT MAPPER 31 - Human-Intuitive Keyboard Shortcut Mapping

    Map all keyboard shortcuts for each and every application and Windows OS.
    Default mappings exist but don't include everything.
    Complete list that can be manually updated and propagated.

    Human-intuitive fashion - easy to understand and use.

    Prime number: 31 (Mapping number - comprehensive coverage)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize SHORTCUT MAPPER 31"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "shortcut_mapper_31"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.mappings_dir = self.data_dir / "mappings"
        self.mappings_dir.mkdir(parents=True, exist_ok=True)

        self.shortcuts: Dict[str, KeyboardShortcut] = {}
        self.applications: Dict[str, ApplicationMapping] = {}

        logger.info("⌨️  SHORTCUT MAPPER 31 initialized")
        logger.info("   Human-intuitive keyboard shortcut mapping")
        logger.info("   All applications and Windows OS")
        logger.info("   Manual updates and propagation")
        logger.info("   Prime number: 31 (Mapping number)")

    def discover_windows_shortcuts(self) -> List[KeyboardShortcut]:
        """Discover Windows OS keyboard shortcuts"""
        shortcuts = []

        # Common Windows shortcuts
        windows_shortcuts = [
            ("Win", "Open Start menu"),
            ("Win+D", "Show desktop"),
            ("Win+E", "Open File Explorer"),
            ("Win+R", "Open Run dialog"),
            ("Win+L", "Lock computer"),
            ("Win+X", "Open Quick Link menu"),
            ("Win+I", "Open Settings"),
            ("Win+A", "Open Action Center"),
            ("Win+S", "Open Search"),
            ("Win+Tab", "Open Task View"),
            ("Alt+Tab", "Switch between apps"),
            ("Alt+F4", "Close active window"),
            ("Ctrl+Shift+Esc", "Open Task Manager"),
            ("Win+PrtScn", "Take screenshot"),
            ("Win+Shift+S", "Take screenshot (Snipping Tool)"),
            ("Ctrl+C", "Copy"),
            ("Ctrl+V", "Paste"),
            ("Ctrl+X", "Cut"),
            ("Ctrl+Z", "Undo"),
            ("Ctrl+Y", "Redo"),
            ("Ctrl+A", "Select all"),
            ("Ctrl+F", "Find"),
            ("Ctrl+S", "Save"),
            ("Ctrl+O", "Open"),
            ("Ctrl+N", "New"),
            ("Ctrl+P", "Print"),
            ("Ctrl+W", "Close window/tab"),
            ("Ctrl+T", "New tab"),
            ("F5", "Refresh"),
            ("F11", "Fullscreen"),
        ]

        for key_combo, description in windows_shortcuts:
            shortcut_id = f"win_{key_combo.replace('+', '_').replace(' ', '_').lower()}"
            shortcut = KeyboardShortcut(
                shortcut_id=shortcut_id,
                application="Windows OS",
                category=ShortcutCategory.WINDOWS_OS,
                action=description,
                key_combination=key_combo,
                description=description,
                shortcut_type=ShortcutType.DEFAULT,
                human_intuitive_name=description,
            )
            shortcuts.append(shortcut)
            self.shortcuts[shortcut_id] = shortcut

        logger.info(f"⌨️  Discovered {len(shortcuts)} Windows OS shortcuts")
        return shortcuts

    def discover_cursor_shortcuts(self) -> List[KeyboardShortcut]:
        """Discover Cursor IDE keyboard shortcuts"""
        shortcuts = []

        # Load from config if exists
        config_file = self.project_root / "config" / "cursor_ide_keyboard_shortcuts.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Parse Cursor IDE shortcuts from config
                    if isinstance(config, dict):
                        for key, value in config.items():
                            if isinstance(value, dict) and "key" in value:
                                shortcut_id = f"cursor_{key}"
                                shortcut = KeyboardShortcut(
                                    shortcut_id=shortcut_id,
                                    application="Cursor IDE",
                                    category=ShortcutCategory.CURSOR_IDE,
                                    action=key,
                                    key_combination=value.get("key", ""),
                                    description=value.get("description", key),
                                    shortcut_type=ShortcutType.DEFAULT,
                                    human_intuitive_name=value.get("description", key),
                                )
                                shortcuts.append(shortcut)
                                self.shortcuts[shortcut_id] = shortcut
            except Exception as e:
                logger.warning(f"Error loading Cursor IDE shortcuts: {e}")

        # Common Cursor IDE shortcuts (if config doesn't exist)
        if not shortcuts:
            cursor_shortcuts = [
                ("Ctrl+K", "Command palette"),
                ("Ctrl+Shift+P", "Command palette"),
                ("Ctrl+`", "Toggle terminal"),
                ("Ctrl+B", "Toggle sidebar"),
                ("Ctrl+Shift+E", "Focus explorer"),
                ("Ctrl+Shift+F", "Focus search"),
                ("Ctrl+Shift+G", "Focus source control"),
                ("F12", "Go to definition"),
                ("Shift+F12", "Find references"),
                ("Alt+F12", "Peek definition"),
            ]

            for key_combo, description in cursor_shortcuts:
                shortcut_id = f"cursor_{key_combo.replace('+', '_').replace(' ', '_').lower()}"
                shortcut = KeyboardShortcut(
                    shortcut_id=shortcut_id,
                    application="Cursor IDE",
                    category=ShortcutCategory.CURSOR_IDE,
                    action=description,
                    key_combination=key_combo,
                    description=description,
                    shortcut_type=ShortcutType.DEFAULT,
                    human_intuitive_name=description,
                )
                shortcuts.append(shortcut)
                self.shortcuts[shortcut_id] = shortcut

        logger.info(f"⌨️  Discovered {len(shortcuts)} Cursor IDE shortcuts")
        return shortcuts

    def add_shortcut(self, application: str, action: str, key_combination: str,
                    description: str, category: ShortcutCategory = ShortcutCategory.APPLICATION,
                    human_intuitive_name: Optional[str] = None) -> KeyboardShortcut:
        """Add a keyboard shortcut (manual update)"""
        shortcut_id = f"{application.lower().replace(' ', '_')}_{action.lower().replace(' ', '_')}"

        shortcut = KeyboardShortcut(
            shortcut_id=shortcut_id,
            application=application,
            category=category,
            action=action,
            key_combination=key_combination,
            description=description,
            shortcut_type=ShortcutType.CUSTOM,
            human_intuitive_name=human_intuitive_name or description,
            manually_updated=True,
        )

        self.shortcuts[shortcut_id] = shortcut

        # Update application mapping
        if application not in self.applications:
            self.applications[application] = ApplicationMapping(
                application_name=application,
                shortcuts=[],
            )
        self.applications[application].shortcuts.append(shortcut)
        self.applications[application].custom_count += 1
        self.applications[application].manually_updated_count += 1

        logger.info(f"⌨️  Shortcut added (manual): {shortcut_id}")
        logger.info(f"   Application: {application}")
        logger.info(f"   Key: {key_combination}")
        logger.info(f"   Action: {action}")

        # Save shortcut
        self._save_shortcut(shortcut)

        return shortcut

    def update_shortcut(self, shortcut_id: str, key_combination: Optional[str] = None,
                       description: Optional[str] = None,
                       human_intuitive_name: Optional[str] = None) -> KeyboardShortcut:
        """Update a keyboard shortcut (manual update)"""
        shortcut = self.shortcuts.get(shortcut_id)
        if shortcut is None:
            raise ValueError(f"Shortcut not found: {shortcut_id}")

        if key_combination:
            shortcut.key_combination = key_combination
        if description:
            shortcut.description = description
        if human_intuitive_name:
            shortcut.human_intuitive_name = human_intuitive_name

        shortcut.manually_updated = True
        shortcut.shortcut_type = ShortcutType.CUSTOM

        logger.info(f"⌨️  Shortcut updated: {shortcut_id}")

        # Save updated shortcut
        self._save_shortcut(shortcut)

        return shortcut

    def mark_missing(self, application: str, action: str, description: str) -> KeyboardShortcut:
        """Mark a shortcut as missing (not in default mappings)"""
        shortcut_id = f"{application.lower().replace(' ', '_')}_{action.lower().replace(' ', '_')}"

        shortcut = KeyboardShortcut(
            shortcut_id=shortcut_id,
            application=application,
            category=ShortcutCategory.APPLICATION,
            action=action,
            key_combination="",  # Unknown
            description=description,
            shortcut_type=ShortcutType.MISSING,
            human_intuitive_name=description,
        )

        self.shortcuts[shortcut_id] = shortcut

        # Update application mapping
        if application not in self.applications:
            self.applications[application] = ApplicationMapping(
                application_name=application,
                shortcuts=[],
            )
        self.applications[application].shortcuts.append(shortcut)
        self.applications[application].missing_count += 1

        logger.info(f"⌨️  Shortcut marked as missing: {shortcut_id}")
        logger.info(f"   Application: {application}")
        logger.info(f"   Action: {action}")

        # Save shortcut
        self._save_shortcut(shortcut)

        return shortcut

    def propagate_shortcuts(self, target_system: str) -> Dict[str, Any]:
        """Propagate shortcuts to target system"""
        propagated = []

        for shortcut in self.shortcuts.values():
            if shortcut.shortcut_type == ShortcutType.CUSTOM or shortcut.manually_updated:
                shortcut.propagated = True
                propagated.append(shortcut.shortcut_id)

        result = {
            "target_system": target_system,
            "propagated_count": len(propagated),
            "propagated_shortcuts": propagated,
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(f"📤 Propagated {len(propagated)} shortcuts to {target_system}")

        # Save propagation record
        self._save_propagation(result)

        return result

    def get_application_mapping(self, application: str) -> ApplicationMapping:
        """Get mapping for an application"""
        if application not in self.applications:
            return ApplicationMapping(
                application_name=application,
                shortcuts=[],
            )
        return self.applications[application]

    def get_all_mappings(self) -> Dict[str, ApplicationMapping]:
        """Get all application mappings"""
        return self.applications

    def get_missing_shortcuts(self) -> List[KeyboardShortcut]:
        """Get all missing shortcuts (not in default mappings)"""
        return [s for s in self.shortcuts.values() if s.shortcut_type == ShortcutType.MISSING]

    def get_manually_updated_shortcuts(self) -> List[KeyboardShortcut]:
        """Get all manually updated shortcuts"""
        return [s for s in self.shortcuts.values() if s.manually_updated]

    def discover_all(self) -> Dict[str, Any]:
        """Discover all shortcuts for all applications and Windows OS"""
        logger.info("🔍 Discovering all keyboard shortcuts...")

        # Discover Windows OS
        windows_shortcuts = self.discover_windows_shortcuts()

        # Discover Cursor IDE
        cursor_shortcuts = self.discover_cursor_shortcuts()

        # Create application mappings
        self.applications["Windows OS"] = ApplicationMapping(
            application_name="Windows OS",
            shortcuts=windows_shortcuts,
            default_count=len(windows_shortcuts),
        )

        self.applications["Cursor IDE"] = ApplicationMapping(
            application_name="Cursor IDE",
            shortcuts=cursor_shortcuts,
            default_count=len(cursor_shortcuts),
        )

        result = {
            "windows_os": len(windows_shortcuts),
            "cursor_ide": len(cursor_shortcuts),
            "total_shortcuts": len(self.shortcuts),
            "total_applications": len(self.applications),
        }

        logger.info(f"✅ Discovery complete:")
        logger.info(f"   Windows OS: {result['windows_os']} shortcuts")
        logger.info(f"   Cursor IDE: {result['cursor_ide']} shortcuts")
        logger.info(f"   Total: {result['total_shortcuts']} shortcuts")

        return result

    def _save_shortcut(self, shortcut: KeyboardShortcut):
        try:
            """Save shortcut"""
            file_path = self.mappings_dir / f"{shortcut.shortcut_id}.json"
            data = {
                "shortcut_id": shortcut.shortcut_id,
                "application": shortcut.application,
                "category": shortcut.category.value,
                "action": shortcut.action,
                "key_combination": shortcut.key_combination,
                "description": shortcut.description,
                "shortcut_type": shortcut.shortcut_type.value,
                "human_intuitive_name": shortcut.human_intuitive_name,
                "manually_updated": shortcut.manually_updated,
                "propagated": shortcut.propagated,
                "notes": shortcut.notes,
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _save_shortcut: {e}", exc_info=True)
            raise
    def _save_propagation(self, propagation: Dict[str, Any]):
        try:
            """Save propagation record"""
            file_path = self.data_dir / "propagations.jsonl"
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(propagation, ensure_ascii=False) + '\n')


        except Exception as e:
            self.logger.error(f"Error in _save_propagation: {e}", exc_info=True)
            raise
def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="SHORTCUT MAPPER 31 - Human-Intuitive Keyboard Shortcut Mapping")
    parser.add_argument("--discover", action="store_true", help="Discover all shortcuts")
    parser.add_argument("--add", nargs=4, metavar=("APP", "ACTION", "KEY", "DESCRIPTION"), help="Add shortcut (manual)")
    parser.add_argument("--update", nargs=2, metavar=("SHORTCUT_ID", "KEY"), help="Update shortcut")
    parser.add_argument("--missing", nargs=3, metavar=("APP", "ACTION", "DESCRIPTION"), help="Mark shortcut as missing")
    parser.add_argument("--propagate", type=str, metavar="TARGET", help="Propagate shortcuts")
    parser.add_argument("--app", type=str, metavar="APPLICATION", help="Show mapping for application")
    parser.add_argument("--missing-list", action="store_true", help="List missing shortcuts")
    parser.add_argument("--status", action="store_true", help="Show status")

    args = parser.parse_args()

    print("="*80)
    print("⌨️  SHORTCUT MAPPER 31 - HUMAN-INTUITIVE KEYBOARD SHORTCUT MAPPING")
    print("="*80)
    print()
    print("Map all keyboard shortcuts for each and every application and Windows OS")
    print("Default mappings exist but don't include everything")
    print("Complete list that can be manually updated and propagated")
    print("Human-intuitive fashion - easy to understand and use")
    print("Prime number: 31 (Mapping number)")
    print()

    mapper = SHORTCUTMAPPER31()

    if args.discover:
        result = mapper.discover_all()
        print("🔍 DISCOVERY RESULTS:")
        print(f"   Windows OS: {result['windows_os']} shortcuts")
        print(f"   Cursor IDE: {result['cursor_ide']} shortcuts")
        print(f"   Total: {result['total_shortcuts']} shortcuts")
        print(f"   Applications: {result['total_applications']}")
        print()

    if args.add:
        app, action, key, description = args.add
        shortcut = mapper.add_shortcut(app, action, key, description)
        print(f"⌨️  Shortcut added: {shortcut.shortcut_id}")
        print(f"   Application: {app}")
        print(f"   Key: {key}")
        print(f"   Action: {action}")
        print()

    if args.update:
        shortcut_id, key = args.update
        shortcut = mapper.update_shortcut(shortcut_id, key_combination=key)
        print(f"⌨️  Shortcut updated: {shortcut_id}")
        print(f"   New key: {key}")
        print()

    if args.missing:
        app, action, description = args.missing
        shortcut = mapper.mark_missing(app, action, description)
        print(f"⌨️  Shortcut marked as missing: {shortcut.shortcut_id}")
        print(f"   Application: {app}")
        print(f"   Action: {action}")
        print()

    if args.propagate:
        result = mapper.propagate_shortcuts(args.propagate)
        print(f"📤 Propagated to {args.propagate}:")
        print(f"   Shortcuts: {result['propagated_count']}")
        print()

    if args.app:
        mapping = mapper.get_application_mapping(args.app)
        print(f"⌨️  MAPPING FOR '{args.app}':")
        print(f"   Total shortcuts: {len(mapping.shortcuts)}")
        print(f"   Default: {mapping.default_count}")
        print(f"   Custom: {mapping.custom_count}")
        print(f"   Missing: {mapping.missing_count}")
        print(f"   Manually updated: {mapping.manually_updated_count}")
        print()

    if args.missing_list:
        missing = mapper.get_missing_shortcuts()
        print(f"⌨️  MISSING SHORTCUTS ({len(missing)}):")
        for shortcut in missing:
            print(f"   {shortcut.application}: {shortcut.action} - {shortcut.description}")
        print()

    if args.status:
        mappings = mapper.get_all_mappings()
        print("📊 STATUS:")
        print(f"   Total shortcuts: {len(mapper.shortcuts)}")
        print(f"   Applications: {len(mappings)}")
        print(f"   Missing shortcuts: {len(mapper.get_missing_shortcuts())}")
        print(f"   Manually updated: {len(mapper.get_manually_updated_shortcuts())}")
        print()

    if not any([args.discover, args.add, args.update, args.missing, args.propagate, args.app, args.missing_list, args.status]):
        # Default: discover all
        result = mapper.discover_all()
        print("📊 DISCOVERY COMPLETE:")
        print(f"   Windows OS: {result['windows_os']} shortcuts")
        print(f"   Cursor IDE: {result['cursor_ide']} shortcuts")
        print(f"   Total: {result['total_shortcuts']} shortcuts")
        print()
        print("Use --discover to discover all shortcuts")
        print("Use --add APP ACTION KEY DESCRIPTION to add shortcut")
        print("Use --update SHORTCUT_ID KEY to update shortcut")
        print("Use --missing APP ACTION DESCRIPTION to mark as missing")
        print("Use --propagate TARGET to propagate shortcuts")
        print("Use --app APPLICATION to show mapping")
        print("Use --missing-list to list missing shortcuts")
        print("Use --status to show status")
        print()


if __name__ == "__main__":


    main()