#!/usr/bin/env python3
"""
PowerToys Macro Integration

Integrates with Microsoft PowerToys Keyboard Manager for @MACROS.
PowerToys is the recommended tool for Windows keyboard remapping.

Tags: #MACROS #POWERTOYS #KEYBOARD_MANAGER #WINDOWS @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("PowerToysMacroIntegration")


class PowerToysMacroIntegration:
    """
    PowerToys Macro Integration

    Creates @MACROS using Microsoft PowerToys Keyboard Manager.
    PowerToys is the recommended tool for Windows keyboard automation.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize PowerToys integration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "macros"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # PowerToys config location (default)
        self.powertoys_config_path = Path.home() / "AppData" / "Local" / "Microsoft" / "PowerToys" / "Keyboard Manager" / "default.json"

        logger.info("✅ PowerToys Macro Integration initialized")
        logger.info("   🎹 PowerToys Keyboard Manager: READY")

    def create_macro_config(self, macros: List[Dict[str, Any]]) -> Path:
        try:
            """
            Create PowerToys Keyboard Manager configuration

            PowerToys format:
            {
                "remapKeys": [...],
                "remapShortcuts": [...],
                "remapShortcutsToText": [...]
            }
            """
            config_file = self.data_dir / "powertoys_keyboard_manager.json"

            remap_keys = []
            remap_shortcuts = []
            remap_shortcuts_to_text = []

            for macro in macros:
                if not macro.get("enabled", True):
                    continue

                trigger = macro.get("trigger", "")
                actions = macro.get("actions", [])
                macro_type = macro.get("type", "keyboard_shortcut")

                if macro_type == "text_expansion":
                    # Remap shortcut to text
                    remap_shortcuts_to_text.append({
                        "originalKeys": self._parse_shortcut(trigger),
                        "newText": self._actions_to_text(actions)
                    })
                elif len(trigger.split()) > 1:
                    # Multi-key shortcut
                    remap_shortcuts.append({
                        "originalKeys": self._parse_shortcut(trigger),
                        "newRemapKeys": self._actions_to_keys(actions)
                    })
                else:
                    # Single key remap
                    remap_keys.append({
                        "originalKeys": self._parse_shortcut(trigger),
                        "newRemapKeys": self._actions_to_keys(actions)
                    })

            config = {
                "remapKeys": remap_keys,
                "remapShortcuts": remap_shortcuts,
                "remapShortcutsToText": remap_shortcuts_to_text
            }

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ PowerToys config created: {config_file.name}")
            logger.info(f"   📋 Remap Keys: {len(remap_keys)}")
            logger.info(f"   📋 Remap Shortcuts: {len(remap_shortcuts)}")
            logger.info(f"   📋 Text Expansions: {len(remap_shortcuts_to_text)}")

            return config_file

        except Exception as e:
            self.logger.error(f"Error in create_macro_config: {e}", exc_info=True)
            raise
    def _parse_shortcut(self, shortcut: str) -> str:
        """Parse shortcut to PowerToys format"""
        # Convert "Ctrl+Alt+U" to PowerToys format
        parts = shortcut.upper().split("+")
        return " ".join(parts)

    def _actions_to_keys(self, actions: List[Dict[str, Any]]) -> str:
        """Convert actions to key sequence"""
        if not actions:
            return ""

        # Get first key action
        for action in actions:
            if action.get("type") == "key":
                return action.get("key", "").upper()

        return ""

    def _actions_to_text(self, actions: List[Dict[str, Any]]) -> str:
        """Convert actions to text"""
        text_parts = []
        for action in actions:
            if action.get("type") == "text":
                text_parts.append(action.get("text", ""))
        return "".join(text_parts)

    def install_config(self) -> bool:
        """Install PowerToys configuration"""
        config_file = self.data_dir / "powertoys_keyboard_manager.json"

        if not config_file.exists():
            logger.error("   ❌ PowerToys config not found")
            return False

        if not self.powertoys_config_path.parent.exists():
            logger.warning("   ⚠️  PowerToys not installed or config path not found")
            logger.info("   📋 Manual installation required:")
            logger.info(f"      1. Copy: {config_file}")
            logger.info(f"      2. To: {self.powertoys_config_path}")
            logger.info("      3. Restart PowerToys")
            return False

        try:
            import shutil
            shutil.copy2(config_file, self.powertoys_config_path)
            logger.info("✅ PowerToys config installed")
            logger.info("   🔄 Restart PowerToys to apply changes")
            return True
        except Exception as e:
            logger.error(f"   ❌ Installation failed: {e}")
            return False


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="PowerToys Macro Integration")
    parser.add_argument("--create-config", action="store_true", help="Create PowerToys config")
    parser.add_argument("--install", action="store_true", help="Install PowerToys config")

    args = parser.parse_args()

    integration = PowerToysMacroIntegration()

    if args.install:
        integration.install_config()
    elif args.create_config:
        # Load macros from macro_plugin_manager
        from macro_plugin_manager import MacroPluginManager
        manager = MacroPluginManager()
        manager.create_cursor_ide_macros()

        macros = [macro.to_dict() for macro in manager.macros.values()]
        integration.create_macro_config(macros)
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":


    sys.exit(main())