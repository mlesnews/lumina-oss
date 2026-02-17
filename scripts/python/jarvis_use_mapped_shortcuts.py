#!/usr/bin/env python3
"""
JARVIS - Use Mapped Keyboard Shortcuts

JARVIS now uses the keyboard shortcuts we mapped out in:
- config/cursor_ide_complete_keyboard_shortcuts.json

No more guessing - uses exact shortcuts from our mapping!
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("❌ Install: pip install keyboard")

try:
    from jarvis_fulltime_super_agent import get_jarvis_fulltime
    JARVIS_AVAILABLE = True
except ImportError:
    JARVIS_AVAILABLE = False


class JARVISShortcutExecutor:
    """Execute keyboard shortcuts using mapped configurations"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.shortcuts_config = self.project_root / "config" / "cursor_ide_complete_keyboard_shortcuts.json"

        # Load shortcuts
        self.shortcuts = {}
        self.command_palette = {}
        self._load_shortcuts()

        # Reverse lookup: alias -> shortcut
        self.alias_map = {}
        self._build_alias_map()

    def _load_shortcuts(self):
        """Load keyboard shortcuts from config"""
        if not self.shortcuts_config.exists():
            print(f"⚠️  Shortcuts config not found: {self.shortcuts_config}")
            return

        try:
            with open(self.shortcuts_config, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Load direct shortcuts
            shortcuts_section = config.get("shortcuts", {})
            for category, commands in shortcuts_section.items():
                for cmd_name, cmd_config in commands.items():
                    if "keys" in cmd_config:
                        self.shortcuts[cmd_name] = {
                            "keys": cmd_config["keys"],
                            "description": cmd_config.get("description", ""),
                            "category": cmd_config.get("category", ""),
                            "aliases": cmd_config.get("aliases", [])
                        }

            # Load command palette commands
            self.command_palette = config.get("command_palette_commands", {})

            print(f"✅ Loaded {len(self.shortcuts)} keyboard shortcuts")
            print(f"✅ Loaded {len(self.command_palette)} command palette commands")

        except Exception as e:
            print(f"❌ Failed to load shortcuts: {e}")

    def _build_alias_map(self):
        """Build alias to shortcut mapping"""
        for cmd_name, cmd_config in self.shortcuts.items():
            # Map command name
            self.alias_map[cmd_name] = cmd_name

            # Map aliases
            for alias in cmd_config.get("aliases", []):
                self.alias_map[alias.lower()] = cmd_name

        # Map command palette aliases
        for cmd_name, cmd_config in self.command_palette.items():
            for alias in cmd_config.get("aliases", []):
                self.alias_map[alias.lower()] = f"palette:{cmd_name}"

    def find_shortcut(self, command: str) -> Optional[Dict[str, Any]]:
        """Find shortcut by command name or alias"""
        command_lower = command.lower().strip()

        # Check alias map
        if command_lower in self.alias_map:
            mapped_name = self.alias_map[command_lower]

            # Check if it's a command palette command
            if mapped_name.startswith("palette:"):
                palette_cmd = mapped_name[8:]  # Remove "palette:" prefix
                return {
                    "type": "palette",
                    "command": self.command_palette[palette_cmd]["command"],
                    "name": palette_cmd
                }

            # Regular shortcut
            if mapped_name in self.shortcuts:
                return {
                    "type": "shortcut",
                    "keys": self.shortcuts[mapped_name]["keys"],
                    "name": mapped_name,
                    "description": self.shortcuts[mapped_name]["description"]
                }

        return None

    def execute_shortcut(self, command: str) -> bool:
        """Execute a keyboard shortcut by command name or alias"""
        if not KEYBOARD_AVAILABLE:
            print("❌ Keyboard library not available")
            return False

        shortcut_info = self.find_shortcut(command)

        if not shortcut_info:
            print(f"❌ Shortcut not found: {command}")
            print(f"   Available commands: {', '.join(list(self.shortcuts.keys())[:10])}...")
            return False

        if shortcut_info["type"] == "palette":
            # Execute via command palette
            print(f"📋 Executing command palette: {shortcut_info['command']}")
            return self._execute_command_palette(shortcut_info["command"])
        else:
            # Execute keyboard shortcut
            keys = shortcut_info["keys"]
            print(f"⌨️  Executing: {shortcut_info['description']} ({'+'.join(keys)})")
            return self._press_keys(keys)

    def _press_keys(self, keys: List[str]) -> bool:
        """Press keyboard keys using keyboard library"""
        try:
            # Handle multi-key sequences (like Ctrl+K, S)
            if len(keys) > 3:  # Likely a sequence like ["ctrl", "k", "s"]
                # Press first combination
                first_combo = '+'.join(keys[:2]).lower()
                keyboard.press_and_release(first_combo)
                time.sleep(0.1)
                # Press second key
                keyboard.press_and_release(keys[2].lower())
                time.sleep(0.1)
                return True

            # Single key combination
            key_sequence = '+'.join(keys).lower()

            # Handle special keys
            key_sequence = key_sequence.replace('pageup', 'page up')
            key_sequence = key_sequence.replace('pagedown', 'page down')
            key_sequence = key_sequence.replace('enter', 'enter')
            key_sequence = key_sequence.replace('space', 'space')

            keyboard.press_and_release(key_sequence)
            time.sleep(0.1)  # Small delay
            return True
        except Exception as e:
            print(f"❌ Failed to execute keys {keys}: {e}")
            return False

    def _execute_command_palette(self, command: str) -> bool:
        """Execute command via command palette"""
        try:
            # Open command palette
            keyboard.press_and_release('ctrl+shift+p')
            time.sleep(0.3)

            # Type command
            keyboard.write(command)
            time.sleep(0.2)

            # Press Enter
            keyboard.press_and_release('enter')
            time.sleep(0.1)

            return True
        except Exception as e:
            print(f"❌ Failed to execute command palette: {e}")
            return False

    def list_shortcuts(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all available shortcuts"""
        shortcuts_list = []

        for cmd_name, cmd_config in self.shortcuts.items():
            if category and cmd_config.get("category", "").lower() != category.lower():
                continue

            shortcuts_list.append({
                "name": cmd_name,
                "keys": '+'.join(cmd_config["keys"]),
                "description": cmd_config["description"],
                "category": cmd_config.get("category", ""),
                "aliases": cmd_config.get("aliases", [])
            })

        return shortcuts_list


class JARVISWithShortcuts:
    """JARVIS integrated with mapped keyboard shortcuts"""

    def __init__(self):
        self.shortcut_executor = JARVISShortcutExecutor()

        if JARVIS_AVAILABLE:
            self.jarvis = get_jarvis_fulltime()
        else:
            self.jarvis = None

    def execute_command(self, command: str) -> bool:
        """Execute a command using mapped shortcuts"""
        print(f"🤖 JARVIS: Executing '{command}' using mapped shortcuts...")
        return self.shortcut_executor.execute_shortcut(command)

    def chat_with_shortcuts(self):
        """Interactive chat that can execute shortcuts"""
        print("="*80)
        print("🤖 JARVIS with Mapped Keyboard Shortcuts")
        print("="*80)
        print()
        print("✅ Using shortcuts from: config/cursor_ide_complete_keyboard_shortcuts.json")
        print()
        print("💡 You can say:")
        print("   - 'open chat' → Opens Cursor chat (Ctrl+L)")
        print("   - 'save file' → Saves current file (Ctrl+S)")
        print("   - 'format code' → Formats document (Shift+Alt+F)")
        print("   - 'accept all changes' → Auto-accepts dialogs")
        print("   - Or any command from the mapped shortcuts!")
        print()
        print("Type 'exit' to quit, 'list' to see all shortcuts")
        print("-" * 80)
        print()

        if self.jarvis:
            conv_id = self.jarvis.start_voice_conversation()
            history = self.jarvis.get_conversation_history(conv_id)
            if history:
                for turn in history:
                    if turn.get('speaker') == 'jarvis':
                        print(f"🤖 JARVIS: {turn.get('message')}")
                        print()

        while True:
            try:
                user_input = input("👤 You: ").strip()

                if user_input.lower() in ['exit', 'quit']:
                    break

                if user_input.lower() == 'list':
                    shortcuts = self.shortcut_executor.list_shortcuts()
                    print(f"\n📋 Available shortcuts ({len(shortcuts)}):")
                    for i, sc in enumerate(shortcuts[:20], 1):
                        print(f"   {i}. {sc['name']}: {sc['keys']} - {sc['description']}")
                    if len(shortcuts) > 20:
                        print(f"   ... and {len(shortcuts) - 20} more")
                    print()
                    continue

                # Execute command
                success = self.execute_command(user_input)

                if success:
                    print("   ✅ Command executed!")
                else:
                    print("   ❌ Command failed or not found")
                print()

            except KeyboardInterrupt:
                break

        print("\n👋 Goodbye!")


def main():
    """Main entry point"""
    jarvis_shortcuts = JARVISWithShortcuts()
    jarvis_shortcuts.chat_with_shortcuts()


if __name__ == "__main__":


    main()