#!/usr/bin/env python3
"""
Macro/Plugin Manager - PowerToys, AutoHotkey, Armoury Crate

Creates @MACROS (keyboard automation sequences) using:
- PowerToys Keyboard Manager
- AutoHotkey
- Armoury Crate

Terminology: @MACROS = Recorded sequences of keyboard/mouse actions

Tags: #MACROS #PLUGINS #POWERTOYS #AUTOHOTKEY #ARMOURY_CRATE #KEYBOARD_AUTOMATION @JARVIS @LUMINA @MANUS
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
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

logger = get_logger("MacroPluginManager")


class MacroType(Enum):
    """Macro types"""
    KEYBOARD_SHORTCUT = "keyboard_shortcut"
    KEY_SEQUENCE = "key_sequence"
    APPLICATION_LAUNCH = "application_launch"
    TEXT_EXPANSION = "text_expansion"
    AUTOMATION_SCRIPT = "automation_script"


@dataclass
class Macro:
    """
    @MACRO - Keyboard automation sequence

    A macro is a recorded sequence of keyboard/mouse actions that can be replayed.
    """
    macro_id: str
    name: str
    macro_type: MacroType
    trigger: str  # Keyboard shortcut that triggers the macro
    actions: List[Dict[str, Any]]  # Sequence of actions
    description: str = ""
    enabled: bool = True
    application: Optional[str] = None  # Specific application or "global"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['macro_type'] = self.macro_type.value
        return data


class MacroPluginManager:
    """
    Macro/Plugin Manager

    Creates @MACROS using PowerToys, AutoHotkey, and Armoury Crate.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize macro plugin manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "macros"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.macros: Dict[str, Macro] = {}
        self.macro_by_name: Dict[str, Macro] = {}  # Track by name to avoid duplicates
        self.prefer_powertoys = True
        self.prefer_autohotkey = False
        self.prefer_armoury_crate = False

        logger.info("✅ Macro/Plugin Manager initialized")
        logger.info("   🎹 PowerToys: READY")
        logger.info("   ⌨️  AutoHotkey: READY")
        logger.info("   🎨 Armoury Crate: READY")

    def create_macro(self, name: str, trigger: str, actions: List[Dict[str, Any]],
                    macro_type: MacroType = MacroType.KEYBOARD_SHORTCUT,
                    description: str = "", application: Optional[str] = None) -> Macro:
        """
        Create @MACRO

        Args:
            name: Macro name
            trigger: Keyboard shortcut (e.g., "Ctrl+Alt+M")
            actions: Sequence of actions
            macro_type: Type of macro
            description: Description
            application: Application scope (None = global)
        """
        import time
        import random
        # Generate unique macro ID with microsecond precision + random
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        microsecond = int(time.time() * 1000000) % 1000000
        random_suffix = random.randint(1000, 9999)
        unique_id = f"macro_{timestamp}_{microsecond}_{random_suffix}"

        macro = Macro(
            macro_id=unique_id,
            name=name,
            macro_type=macro_type,
            trigger=trigger,
            actions=actions,
            description=description,
            application=application
        )

        # Check if macro with same name already exists
        if name in self.macro_by_name:
            logger.warning(f"   ⚠️  Macro '{name}' already exists, updating...")
            old_macro = self.macro_by_name[name]
            del self.macros[old_macro.macro_id]

        self.macros[macro.macro_id] = macro
        self.macro_by_name[name] = macro

        logger.info(f"✅ @MACRO created: {macro.macro_id}")
        logger.info(f"   Name: {name}")
        logger.info(f"   Trigger: {trigger}")
        logger.info(f"   Type: {macro_type.value}")

        return macro

    def generate_powertoys_config(self) -> Path:
        try:
            """Generate PowerToys Keyboard Manager configuration"""
            config_file = self.data_dir / "powertoys_keyboard_manager.json"

            remap_keys = []
            remap_shortcuts = []
            remap_shortcuts_to_text = []

            for macro in self.macros.values():
                if not macro.enabled:
                    continue

                trigger = macro.trigger
                actions = macro.actions

                # Check if multi-key shortcut
                if len(trigger.split()) > 1 or "+" in trigger and trigger.count("+") > 1:
                    # Multi-key shortcut
                    remap_shortcuts.append({
                        "originalKeys": self._parse_shortcut(trigger),
                        "newRemapKeys": self._actions_to_keys(actions)
                    })
                else:
                    # Single key
                    remap_keys.append({
                        "originalKeys": self._parse_shortcut(trigger),
                        "newRemapKeys": self._actions_to_keys(actions)
                    })

            config = {
                "version": "1.0",
                "remapKeys": remap_keys,
                "remapShortcuts": remap_shortcuts,
                "remapShortcutsToText": remap_shortcuts_to_text
            }

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ PowerToys config generated: {config_file.name}")
            logger.info(f"   📋 Remap Keys: {len(remap_keys)}")
            logger.info(f"   📋 Remap Shortcuts: {len(remap_shortcuts)}")
            return config_file

        except Exception as e:
            self.logger.error(f"Error in generate_powertoys_config: {e}", exc_info=True)
            raise
    def generate_autohotkey_script(self) -> Path:
        try:
            """Generate AutoHotkey script"""
            script_file = self.data_dir / "lumina_macros.ahk"

            script_content = [
                "; LUMINA Macros - AutoHotkey Script",
                "; @MACROS for LUMINA JARVIS System",
                "; Auto-generated",
                "",
                "#NoEnv",
                "#SingleInstance Force",
                "",
                "; Macros"
            ]

            # Use macro_by_name to avoid duplicates
            seen_names = set()
            for macro in sorted(self.macros.values(), key=lambda m: m.name):
                if macro.enabled and macro.name not in seen_names:
                    seen_names.add(macro.name)
                    ahk_trigger = self._convert_to_ahk_shortcut(macro.trigger)
                    ahk_actions = self._actions_to_ahk(macro.actions)

                    script_content.append(f"")
                    script_content.append(f"; {macro.name}")
                    if macro.description:
                        script_content.append(f"; {macro.description}")
                    script_content.append(f"{ahk_trigger}::")
                    for action in ahk_actions:
                        script_content.append(f"    {action}")
                    script_content.append("return")

            with open(script_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(script_content))

            logger.info(f"✅ AutoHotkey script generated: {script_file.name}")
            return script_file

        except Exception as e:
            self.logger.error(f"Error in generate_autohotkey_script: {e}", exc_info=True)
            raise
    def generate_armoury_crate_macros(self) -> Dict[str, Any]:
        """Generate Armoury Crate macro configuration"""
        try:
            from armoury_crate_manager import ArmouryCrateManager
            ac_manager = ArmouryCrateManager()

            macros_config = {
                "version": "1.0",
                "macros": []
            }

            seen_names = set()
            for macro in self.macros.values():
                if macro.enabled and macro.name not in seen_names:
                    seen_names.add(macro.name)
                    ac_macro = {
                        "name": macro.name,
                        "trigger": macro.trigger,
                        "actions": macro.actions,
                        "type": macro.macro_type.value
                    }
                    macros_config["macros"].append(ac_macro)

            # Save to Armoury Crate if available
            config_file = self.data_dir / "armoury_crate_macros.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(macros_config, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Armoury Crate macros generated: {config_file.name}")
            return macros_config
        except ImportError:
            logger.warning("   ⚠️  Armoury Crate manager not available")
            return {}

    def _parse_shortcut(self, shortcut: str) -> str:
        """Parse shortcut to PowerToys format"""
        # Convert "Ctrl+Alt+M" to PowerToys format "Ctrl Alt M"
        parts = shortcut.split("+")
        formatted = []
        for part in parts:
            part = part.strip()
            if part.lower() == "ctrl":
                formatted.append("Ctrl")
            elif part.lower() == "alt":
                formatted.append("Alt")
            elif part.lower() == "shift":
                formatted.append("Shift")
            elif part.lower() == "win":
                formatted.append("Win")
            else:
                formatted.append(part.upper())
        return " ".join(formatted)

    def _convert_to_ahk_shortcut(self, shortcut: str) -> str:
        """Convert shortcut to AutoHotkey format"""
        key_map = {
            "ctrl": "^",
            "alt": "!",
            "shift": "+",
            "win": "#"
        }

        # Handle multi-key sequences like "Ctrl+K Ctrl+J"
        # For AutoHotkey, we use the first key as trigger and execute sequence in actions
        if " " in shortcut and any("+" in part for part in shortcut.split()):
            # Multi-key sequence - use first key as trigger
            first_key = shortcut.split()[0]
            parts = first_key.lower().split("+")
            ahk_parts = []
            for part in parts:
                part = part.strip()
                if part in key_map:
                    ahk_parts.append(key_map[part])
                else:
                    ahk_parts.append(part.upper())
            return "".join(ahk_parts)
        else:
            # Single shortcut
            parts = shortcut.lower().split("+")
            ahk_parts = []
            for part in parts:
                part = part.strip()
                if part in key_map:
                    ahk_parts.append(key_map[part])
                else:
                    ahk_parts.append(part.upper())
            return "".join(ahk_parts)

    def _actions_to_keys(self, actions: List[Dict[str, Any]]) -> str:
        """Convert actions to key sequence for PowerToys"""
        if not actions:
            return ""

        # Get first key action and format for PowerToys
        for action in actions:
            if action.get("type") == "key":
                key = action.get("key", "")
                return self._parse_shortcut(key)

        return ""

    def _actions_to_ahk(self, actions: List[Dict[str, Any]]) -> List[str]:
        """Convert actions to AutoHotkey commands"""
        ahk_actions = []
        for action in actions:
            action_type = action.get("type", "key")
            if action_type == "key":
                key = action.get("key", "")
                # Format key for AutoHotkey Send command
                if "+" in key:
                    # Multi-key combination
                    parts = key.split("+")
                    formatted = []
                    for part in parts:
                        part = part.strip()
                        if part.lower() == "ctrl":
                            formatted.append("^")
                        elif part.lower() == "alt":
                            formatted.append("!")
                        elif part.lower() == "shift":
                            formatted.append("+")
                        elif part.lower() == "win":
                            formatted.append("#")
                        else:
                            formatted.append(part.upper())
                    ahk_actions.append(f"Send, {{{''.join(formatted)}}}")
                else:
                    ahk_actions.append(f"Send, {{{key.upper()}}}")
            elif action_type == "text":
                text = action.get("text", "")
                ahk_actions.append(f'Send, "{text}"')
            elif action_type == "delay":
                delay = action.get("delay", 100)
                ahk_actions.append(f"Sleep, {delay}")
            elif action_type == "application":
                app = action.get("application", "")
                ahk_actions.append(f'Run, "{app}"')

        return ahk_actions

    def create_cursor_ide_macros(self):
        """Create macros for Cursor IDE shortcuts"""
        logger.info("=" * 80)
        logger.info("🎹 CREATING CURSOR IDE MACROS")
        logger.info("=" * 80)
        logger.info("")

        cursor_macros_count = len([m for m in self.macros.values() if m.application == "Cursor"])

        # Macro 1: Undo All
        self.create_macro(
            name="Cursor IDE: Undo All",
            trigger="Ctrl+Alt+U",
            actions=[
                {"type": "key", "key": "Ctrl+Z"},
                {"type": "delay", "delay": 50},
                {"type": "key", "key": "Ctrl+Z"}
            ],
            description="Undo all changes in Cursor IDE",
            application="Cursor"
        )

        # Macro 2: Keep All
        self.create_macro(
            name="Cursor IDE: Keep All",
            trigger="Ctrl+Alt+K",
            actions=[
                {"type": "key", "key": "Ctrl+A"},
                {"type": "delay", "delay": 50},
                {"type": "key", "key": "Ctrl+S"}
            ],
            description="Keep all changes in Cursor IDE",
            application="Cursor"
        )

        # Macro 3: Focus Chat
        self.create_macro(
            name="Cursor IDE: Focus Chat",
            trigger="Ctrl+K Ctrl+J",
            actions=[
                {"type": "key", "key": "Ctrl+K"},
                {"type": "delay", "delay": 100},
                {"type": "key", "key": "Ctrl+J"}
            ],
            description="Focus Cursor IDE chat",
            application="Cursor"
        )

        new_cursor_macros = len([m for m in self.macros.values() if m.application == "Cursor"]) - cursor_macros_count
        logger.info(f"   ✅ Created {new_cursor_macros} Cursor IDE macros")
        logger.info("")

    def generate_all_configs(self):
        """Generate all macro configurations"""
        logger.info("=" * 80)
        logger.info("🎹 GENERATING ALL MACRO CONFIGS")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"   📋 Total Macros: {len(self.macros)}")
        logger.info("")

        # PowerToys
        powertoys_config = self.generate_powertoys_config()
        logger.info(f"   ✅ PowerToys: {powertoys_config.name}")

        # AutoHotkey
        ahk_script = self.generate_autohotkey_script()
        logger.info(f"   ✅ AutoHotkey: {ahk_script.name}")

        # Armoury Crate
        ac_config = self.generate_armoury_crate_macros()
        if ac_config:
            logger.info(f"   ✅ Armoury Crate: Generated")

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ ALL MACRO CONFIGS GENERATED")
        logger.info("=" * 80)
        logger.info("")


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Macro/Plugin Manager")
    parser.add_argument("--create-cursor", action="store_true", help="Create Cursor IDE macros")
    parser.add_argument("--generate-all", action="store_true", help="Generate all configs")
    parser.add_argument("--powertoys", action="store_true", help="Generate PowerToys config")
    parser.add_argument("--autohotkey", action="store_true", help="Generate AutoHotkey script")
    parser.add_argument("--armoury", action="store_true", help="Generate Armoury Crate macros")

    args = parser.parse_args()

    manager = MacroPluginManager()

    if args.generate_all:
        manager.create_cursor_ide_macros()
        manager.generate_all_configs()
    elif args.create_cursor:
        manager.create_cursor_ide_macros()
    elif args.powertoys:
        manager.create_cursor_ide_macros()
        manager.generate_powertoys_config()
    elif args.autohotkey:
        manager.create_cursor_ide_macros()
        manager.generate_autohotkey_script()
    elif args.armoury:
        manager.create_cursor_ide_macros()
        manager.generate_armoury_crate_macros()
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":


    sys.exit(main())