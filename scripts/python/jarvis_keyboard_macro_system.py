#!/usr/bin/env python3
"""
JARVIS Keyboard Macro System

Creates keyboard macros and shortcuts, including right Alt button mapping to send/submit.
Uses AutoHotkey or similar automation tools for keyboard remapping.

Tags: #KEYBOARD #MACRO #SHORTCUT #AUTOHOTKEY #RIGHT_ALT #SEND_BUTTON @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVISKeyboardMacro")
except ImportError:
    try:
        from lumina_logger import get_logger
        logger = get_logger("JARVISKeyboardMacro")
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("JARVISKeyboardMacro")


class KeyboardMacroSystem:
    """Keyboard macro system for creating shortcuts and remappings"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "keyboard_macros"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.macros_file = self.data_dir / "macros.json"
        self.autohotkey_dir = project_root / "scripts" / "autohotkey"
        self.autohotkey_dir.mkdir(parents=True, exist_ok=True)

        self.macros = self._load_macros()

    def _load_macros(self) -> Dict[str, Any]:
        """Load existing macros"""
        if self.macros_file.exists():
            try:
                with open(self.macros_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading macros: {e}")
        return {"macros": {}, "metadata": {"last_updated": None}}

    def _save_macros(self):
        """Save macros to file"""
        self.macros["metadata"]["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.macros_file, 'w', encoding='utf-8') as f:
                json.dump(self.macros, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving macros: {e}")

    def create_macro(
        self,
        macro_id: str,
        name: str,
        trigger_key: str,
        action: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a keyboard macro"""
        macro = {
            "macro_id": macro_id,
            "name": name,
            "trigger_key": trigger_key,
            "action": action,
            "description": description or f"Macro: {name}",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "enabled": True,
            "autohotkey_script": None
        }

        # Generate AutoHotkey script
        autohotkey_script = self._generate_autohotkey_script(macro)
        macro["autohotkey_script"] = autohotkey_script

        # Save AutoHotkey script file
        script_file = self.autohotkey_dir / f"{macro_id}.ahk"
        try:
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(autohotkey_script)
            macro["script_file"] = str(script_file)
        except Exception as e:
            logger.error(f"Error saving AutoHotkey script: {e}")

        self.macros.setdefault("macros", {})[macro_id] = macro
        self._save_macros()

        logger.info(f"✅ Macro created: {name} ({macro_id})")

        return macro

    def _generate_autohotkey_script(self, macro: Dict[str, Any]) -> str:
        """Generate AutoHotkey script for macro"""
        trigger = macro["trigger_key"]
        action = macro["action"]

        # Map common keys to AutoHotkey syntax
        key_map = {
            "right_alt": "RAlt",
            "left_alt": "LAlt",
            "right_ctrl": "RCtrl",
            "left_ctrl": "LCtrl",
            "right_shift": "RShift",
            "left_shift": "LShift",
            "enter": "Enter",
            "return": "Return",
            "send": "Enter",
            "submit": "Enter"
        }

        trigger_key = key_map.get(trigger.lower(), trigger)

        # Map actions to AutoHotkey commands
        if action.lower() in ["send", "submit", "enter"]:
            action_command = "Send, {Enter}"
        elif action.lower().startswith("send "):
            # Custom send command
            action_command = f"Send, {action[5:]}"
        else:
            action_command = f"Send, {action}"

        script = f"""; AutoHotkey Script: {macro['name']}
; Generated: {datetime.now().isoformat()}
; Description: {macro.get('description', '')}

; {trigger_key} hotkey - {action}
{trigger_key}::
{{
    {action_command}
    Return
}}

; End of script
"""

        return script

    def create_right_alt_send_macro(self) -> Dict[str, Any]:
        """Create right Alt button macro to send/submit"""
        macro = self.create_macro(
            macro_id="right_alt_send",
            name="Right Alt Send/Submit",
            trigger_key="right_alt",
            action="send",
            description="Right Alt button triggers send/submit (Enter key)"
        )

        logger.info("✅ Right Alt Send macro created")
        return macro

    def get_macro(self, macro_id: str) -> Optional[Dict[str, Any]]:
        """Get macro by ID"""
        return self.macros.get("macros", {}).get(macro_id)

    def get_all_macros(self) -> List[Dict[str, Any]]:
        """Get all macros"""
        return list(self.macros.get("macros", {}).values())

    def enable_macro(self, macro_id: str) -> bool:
        """Enable a macro"""
        if macro_id in self.macros.get("macros", {}):
            self.macros["macros"][macro_id]["enabled"] = True
            self.macros["macros"][macro_id]["updated_at"] = datetime.now().isoformat()
            self._save_macros()
            logger.info(f"✅ Macro enabled: {macro_id}")
            return True
        return False

    def disable_macro(self, macro_id: str) -> bool:
        """Disable a macro"""
        if macro_id in self.macros.get("macros", {}):
            self.macros["macros"][macro_id]["enabled"] = False
            self.macros["macros"][macro_id]["updated_at"] = datetime.now().isoformat()
            self._save_macros()
            logger.info(f"⏸️  Macro disabled: {macro_id}")
            return True
        return False


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Keyboard Macro System")
        parser.add_argument("--create-right-alt-send", action="store_true",
                           help="Create right Alt button macro to send/submit")
        parser.add_argument("--create", type=str, nargs=4, metavar=("MACRO_ID", "NAME", "TRIGGER", "ACTION"),
                           help="Create custom macro")
        parser.add_argument("--list", action="store_true", help="List all macros")
        parser.add_argument("--get", type=str, metavar="MACRO_ID", help="Get macro by ID")
        parser.add_argument("--enable", type=str, metavar="MACRO_ID", help="Enable macro")
        parser.add_argument("--disable", type=str, metavar="MACRO_ID", help="Disable macro")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        system = KeyboardMacroSystem(project_root)

        if args.create_right_alt_send:
            macro = system.create_right_alt_send_macro()
            print("=" * 80)
            print("RIGHT ALT SEND MACRO CREATED")
            print("=" * 80)
            print(json.dumps(macro, indent=2, default=str))
            print("=" * 80)
            print(f"AutoHotkey script saved to: {macro['script_file']}")
            print("To use: Run the .ahk file with AutoHotkey installed")

        elif args.create:
            macro = system.create_macro(args.create[0], args.create[1], args.create[2], args.create[3])
            print("=" * 80)
            print("MACRO CREATED")
            print("=" * 80)
            print(json.dumps(macro, indent=2, default=str))

        elif args.list:
            macros = system.get_all_macros()
            print("=" * 80)
            print(f"ALL MACROS ({len(macros)})")
            print("=" * 80)
            for macro in macros:
                status = "✅" if macro.get("enabled") else "⏸️"
                print(f"{status} {macro['name']} ({macro['macro_id']}) - {macro['trigger_key']} → {macro['action']}")

        elif args.get:
            macro = system.get_macro(args.get)
            if macro:
                print("=" * 80)
                print("MACRO DETAILS")
                print("=" * 80)
                print(json.dumps(macro, indent=2, default=str))
            else:
                print(f"Macro not found: {args.get}")

        elif args.enable:
            if system.enable_macro(args.enable):
                print(f"✅ Macro enabled: {args.enable}")
            else:
                print(f"❌ Macro not found: {args.enable}")

        elif args.disable:
            if system.disable_macro(args.disable):
                print(f"⏸️  Macro disabled: {args.disable}")
            else:
                print(f"❌ Macro not found: {args.disable}")

        else:
            print("JARVIS Keyboard Macro System")
            print("Use --help for usage information")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()