#!/usr/bin/env python3
"""
Cursor IDE Complete Keyboard Controller
MANUS Framework - Complete IDE Control via Keyboard Shortcuts

Comprehensive keyboard shortcut system for ALL Cursor IDE commands.
No mouse clicking required - full control via keyboard shortcuts.

Features:
- Complete keyboard shortcut mapping for all Cursor IDE commands
- Natural language command parsing
- Intelligent command mapping
- JARVIS integration for voice/text control
- Intuitive command aliases

@MANUS @JARVIS @SYPHON
"""

import sys
import json
import time
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CursorIDEKeyboardController")

try:
    import pynput
    from pynput.keyboard import Key, Controller as KeyboardController
    from pynput.mouse import Button, Controller as MouseController
    import pygetwindow as gw
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    logger.warning("pynput not available - install: pip install pynput pygetwindow")


@dataclass
class ShortcutResult:
    """Result of executing a keyboard shortcut"""
    success: bool
    method: str  # "keyboard" or "command_palette"
    shortcut_name: str
    command: Optional[str] = None
    error: Optional[str] = None
    execution_time: float = 0.0


class CursorIDEKeyboardController:
    """
    Complete Cursor IDE Keyboard Controller

    Provides comprehensive keyboard control for ALL Cursor IDE commands.
    Supports natural language commands mapped to keyboard shortcuts.
    """

    def __init__(self, shortcuts_config_path: Optional[Path] = None):
        """Initialize keyboard controller"""
        if not PYNPUT_AVAILABLE:
            logger.error("❌ pynput not available - keyboard control disabled")
            self.keyboard = None
            self.mouse = None
            return

        self.keyboard = KeyboardController()
        self.mouse = MouseController()
        self.cursor_window = None

        # Load keyboard shortcuts configuration
        if shortcuts_config_path is None:
            shortcuts_config_path = project_root / "config" / "cursor_ide_complete_keyboard_shortcuts.json"

        self.shortcuts_config = self._load_shortcuts_config(shortcuts_config_path)
        self.shortcuts_map = self._build_shortcuts_map()
        self.command_palette_map = self._build_command_palette_map()
        self.alias_map = self._build_alias_map()

        logger.info("✅ Cursor IDE Keyboard Controller initialized")
        logger.info(f"   Loaded {len(self.shortcuts_map)} keyboard shortcuts")
        logger.info(f"   Loaded {len(self.alias_map)} command aliases")

    def _load_shortcuts_config(self, config_path: Path) -> Dict[str, Any]:
        """Load keyboard shortcuts configuration"""
        try:
            if not config_path.exists():
                logger.error(f"❌ Shortcuts config not found: {config_path}")
                return {}

            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            logger.info(f"✅ Loaded shortcuts config from: {config_path}")
            return config
        except Exception as e:
            logger.error(f"❌ Failed to load shortcuts config: {e}")
            return {}

    def _build_shortcuts_map(self) -> Dict[str, Dict[str, Any]]:
        """Build map of shortcut names to key combinations"""
        shortcuts_map = {}

        if "shortcuts" not in self.shortcuts_config:
            return shortcuts_map

        for category, shortcuts in self.shortcuts_config["shortcuts"].items():
            for shortcut_name, shortcut_info in shortcuts.items():
                shortcuts_map[shortcut_name] = shortcut_info

        return shortcuts_map

    def _build_command_palette_map(self) -> Dict[str, str]:
        """Build map of aliases to command palette commands"""
        command_map = {}

        if "command_palette_commands" not in self.shortcuts_config:
            return command_map

        for cmd_name, cmd_info in self.shortcuts_config["command_palette_commands"].items():
            command_map[cmd_name] = cmd_info["command"]
            for alias in cmd_info.get("aliases", []):
                command_map[alias.lower()] = cmd_info["command"]

        return command_map

    def _build_alias_map(self) -> Dict[str, str]:
        """Build map of natural language aliases to shortcut names"""
        alias_map = {}

        for shortcut_name, shortcut_info in self.shortcuts_map.items():
            # Add the shortcut name itself
            alias_map[shortcut_name.lower()] = shortcut_name

            # Add all aliases
            for alias in shortcut_info.get("aliases", []):
                alias_map[alias.lower()] = shortcut_name

        return alias_map

    def find_cursor_window(self) -> bool:
        """Find and activate Cursor window"""
        if not PYNPUT_AVAILABLE:
            return False

        try:
            windows = gw.getWindowsWithTitle('Cursor')
            if not windows:
                windows = gw.getWindowsWithTitle('cursor')
            if not windows:
                # Try partial match
                all_windows = gw.getAllWindows()
                windows = [w for w in all_windows if 'cursor' in w.title.lower()]

            if windows:
                self.cursor_window = windows[0]
                self.cursor_window.activate()
                time.sleep(0.2)  # Wait for window to activate
                logger.debug(f"✅ Found Cursor window: {self.cursor_window.title}")
                return True
            else:
                logger.warning("⚠️  Cursor window not found")
                return False
        except Exception as e:
            logger.error(f"❌ Error finding Cursor window: {e}")
            return False

    def parse_natural_language_command(self, command: str) -> Optional[str]:
        """
        Parse natural language command to shortcut name

        Args:
            command: Natural language command (e.g., "open file", "save", "format code")

        Returns:
            Shortcut name if found, None otherwise
        """
        command_lower = command.lower().strip()

        # Direct alias lookup
        if command_lower in self.alias_map:
            return self.alias_map[command_lower]

        # Fuzzy matching - try partial matches
        for alias, shortcut_name in self.alias_map.items():
            if alias in command_lower or command_lower in alias:
                return shortcut_name

        # Try removing common prefixes/suffixes
        command_clean = re.sub(r'^(please|can you|could you|let me|i want to|i need to)\s+', '', command_lower)
        command_clean = re.sub(r'\s+(please|now|right now)$', '', command_clean)

        if command_clean in self.alias_map:
            return self.alias_map[command_clean]

        # Try command palette commands
        if command_lower in self.command_palette_map:
            return None  # Return None to indicate command palette command

        logger.warning(f"⚠️  Could not parse command: {command}")
        return None

    def execute_shortcut(self, shortcut_name: str, wait_after: float = 0.3) -> ShortcutResult:
        """
        Execute keyboard shortcut by name

        Args:
            shortcut_name: Name of shortcut (e.g., "open_file", "save_file")
            wait_after: Time to wait after execution (seconds)

        Returns:
            ShortcutResult with execution details
        """
        start_time = time.time()

        if not self.keyboard:
            return ShortcutResult(
                success=False,
                method="keyboard",
                shortcut_name=shortcut_name,
                error="Keyboard controller not available"
            )

        if shortcut_name not in self.shortcuts_map:
            return ShortcutResult(
                success=False,
                method="keyboard",
                shortcut_name=shortcut_name,
                error=f"Unknown shortcut: {shortcut_name}"
            )

        # Ensure Cursor window is active
        if not self.cursor_window:
            if not self.find_cursor_window():
                return ShortcutResult(
                    success=False,
                    method="keyboard",
                    shortcut_name=shortcut_name,
                    error="Cursor window not found"
                )

        try:
            shortcut_info = self.shortcuts_map[shortcut_name]
            keys = shortcut_info.get("keys", [])

            logger.info(f"⌨️  Executing shortcut: {shortcut_name} ({shortcut_info.get('description', 'N/A')})")

            # Execute key combination
            success = self._press_key_combination(keys)

            if success:
                time.sleep(wait_after)
                execution_time = time.time() - start_time
                logger.info(f"   ✅ Shortcut executed successfully ({execution_time:.2f}s)")
                return ShortcutResult(
                    success=True,
                    method="keyboard",
                    shortcut_name=shortcut_name,
                    execution_time=execution_time
                )
            else:
                return ShortcutResult(
                    success=False,
                    method="keyboard",
                    shortcut_name=shortcut_name,
                    error="Key combination execution failed"
                )

        except Exception as e:
            logger.error(f"   ❌ Shortcut execution failed: {e}")
            return ShortcutResult(
                success=False,
                method="keyboard",
                shortcut_name=shortcut_name,
                error=str(e)
            )

    def execute_command_palette_command(self, command: str, wait_after: float = 0.5) -> ShortcutResult:
        """
        Execute command via command palette

        Args:
            command: Command palette command name or alias
            wait_after: Time to wait after execution (seconds)

        Returns:
            ShortcutResult with execution details
        """
        start_time = time.time()

        if not self.keyboard:
            return ShortcutResult(
                success=False,
                method="command_palette",
                shortcut_name=command,
                error="Keyboard controller not available"
            )

        # Get actual command if alias provided
        actual_command = self.command_palette_map.get(command.lower(), command)

        # Ensure Cursor window is active
        if not self.cursor_window:
            if not self.find_cursor_window():
                return ShortcutResult(
                    success=False,
                    method="command_palette",
                    shortcut_name=command,
                    error="Cursor window not found"
                )

        try:
            logger.info(f"📋 Executing command palette command: {actual_command}")

            # Open command palette (Ctrl+Shift+P)
            self._press_key_combination(["ctrl", "shift", "p"])
            time.sleep(0.3)

            # Type command
            self.keyboard.type(actual_command)
            time.sleep(0.2)

            # Press Enter to execute
            self.keyboard.press(Key.enter)
            self.keyboard.release(Key.enter)

            time.sleep(wait_after)
            execution_time = time.time() - start_time

            logger.info(f"   ✅ Command palette command executed ({execution_time:.2f}s)")
            return ShortcutResult(
                success=True,
                method="command_palette",
                shortcut_name=command,
                command=actual_command,
                execution_time=execution_time
            )

        except Exception as e:
            logger.error(f"   ❌ Command palette execution failed: {e}")
            return ShortcutResult(
                success=False,
                method="command_palette",
                shortcut_name=command,
                error=str(e)
            )

    def execute_natural_language_command(self, command: str) -> ShortcutResult:
        """
        Execute command from natural language input

        Args:
            command: Natural language command (e.g., "open file", "save", "format code")

        Returns:
            ShortcutResult with execution details
        """
        # Parse command
        shortcut_name = self.parse_natural_language_command(command)

        if shortcut_name:
            # Execute keyboard shortcut
            return self.execute_shortcut(shortcut_name)
        elif command.lower() in self.command_palette_map:
            # Execute via command palette
            return self.execute_command_palette_command(command.lower())
        else:
            # Try command palette as fallback
            return self.execute_command_palette_command(command)

    def _press_key_combination(self, keys: List[str]) -> bool:
        """
        Press a key combination

        Args:
            keys: List of keys (e.g., ["ctrl", "shift", "p"])

        Returns:
            True if successful
        """
        try:
            # Key mapping
            key_map = {
                "ctrl": Key.ctrl,
                "shift": Key.shift,
                "alt": Key.alt,
                "cmd": Key.cmd,
                "tab": Key.tab,
                "enter": Key.enter,
                "space": Key.space,
                "escape": Key.esc,
                "backspace": Key.backspace,
                "up": Key.up,
                "down": Key.down,
                "left": Key.left,
                "right": Key.right,
                "pageup": Key.page_up,
                "pagedown": Key.page_down,
                "home": Key.home,
                "end": Key.end,
                "insert": Key.insert,
                "delete": Key.delete,
                "f1": Key.f1, "f2": Key.f2, "f3": Key.f3, "f4": Key.f4,
                "f5": Key.f5, "f6": Key.f6, "f7": Key.f7, "f8": Key.f8,
                "f9": Key.f9, "f10": Key.f10, "f11": Key.f11, "f12": Key.f12,
            }

            # Separate modifiers and regular keys
            modifiers = []
            regular_keys = []

            for key in keys:
                key_lower = key.lower()
                if key_lower in key_map:
                    if key_lower in ["ctrl", "shift", "alt", "cmd"]:
                        modifiers.append(key_map[key_lower])
                    else:
                        regular_keys.append(key_map[key_lower])
                elif key == "`":
                    regular_keys.append("`")
                elif len(key) == 1:
                    regular_keys.append(key)
                else:
                    logger.warning(f"Unknown key: {key}")

            # Release all keys first (safety)
            for mod in [Key.ctrl, Key.shift, Key.alt, Key.cmd]:
                try:
                    self.keyboard.release(mod)
                except:
                    pass

            time.sleep(0.05)

            # Press all modifiers first
            for mod in modifiers:
                self.keyboard.press(mod)

            time.sleep(0.05)

            # Press regular keys
            for key in regular_keys:
                if isinstance(key, Key):
                    self.keyboard.press(key)
                    time.sleep(0.02)
                    self.keyboard.release(key)
                else:
                    self.keyboard.press(key)
                    time.sleep(0.02)
                    self.keyboard.release(key)
                time.sleep(0.02)

            # Release modifiers (in reverse order)
            for mod in reversed(modifiers):
                self.keyboard.release(mod)

            return True

        except Exception as e:
            logger.error(f"Error pressing key combination: {e}")
            return False

    def type_text(self, text: str, delay: float = 0.03) -> bool:
        """
        Type text into active Cursor window

        Args:
            text: Text to type
            delay: Delay between characters (seconds)

        Returns:
            True if successful
        """
        if not self.keyboard:
            return False

        try:
            if not self.cursor_window:
                if not self.find_cursor_window():
                    return False

            logger.info(f"⌨️  Typing text: {text[:50]}...")
            self.keyboard.type(text)
            time.sleep(0.2)
            return True

        except Exception as e:
            logger.error(f"Typing failed: {e}")
            return False

    def get_available_shortcuts(self, category: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Get available shortcuts, optionally filtered by category

        Args:
            category: Optional category filter (e.g., "file_operations", "editing")

        Returns:
            Dictionary of shortcuts
        """
        if category:
            return {
                name: info
                for name, info in self.shortcuts_map.items()
                if info.get("category", "").lower() == category.lower()
            }
        return self.shortcuts_map

    def search_shortcuts(self, query: str) -> List[Dict[str, Any]]:
        """
        Search shortcuts by description or alias

        Args:
            query: Search query

        Returns:
            List of matching shortcuts
        """
        query_lower = query.lower()
        results = []

        for shortcut_name, shortcut_info in self.shortcuts_map.items():
            # Check description
            if query_lower in shortcut_info.get("description", "").lower():
                results.append({
                    "name": shortcut_name,
                    "description": shortcut_info.get("description"),
                    "keys": shortcut_info.get("keys", []),
                    "category": shortcut_info.get("category")
                })
                continue

            # Check aliases
            if any(query_lower in alias.lower() for alias in shortcut_info.get("aliases", [])):
                results.append({
                    "name": shortcut_name,
                    "description": shortcut_info.get("description"),
                    "keys": shortcut_info.get("keys", []),
                    "category": shortcut_info.get("category")
                })

        return results


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Cursor IDE Complete Keyboard Controller")
    parser.add_argument("--command", type=str, help="Execute natural language command")
    parser.add_argument("--shortcut", type=str, help="Execute shortcut by name")
    parser.add_argument("--palette", type=str, help="Execute command palette command")
    parser.add_argument("--search", type=str, help="Search shortcuts")
    parser.add_argument("--list", action="store_true", help="List all shortcuts")
    parser.add_argument("--category", type=str, help="Filter by category")
    parser.add_argument("--type", type=str, help="Type text")

    args = parser.parse_args()

    controller = CursorIDEKeyboardController()

    if args.command:
        result = controller.execute_natural_language_command(args.command)
        print(f"Success: {result.success}")
        if result.error:
            print(f"Error: {result.error}")

    elif args.shortcut:
        result = controller.execute_shortcut(args.shortcut)
        print(f"Success: {result.success}")
        if result.error:
            print(f"Error: {result.error}")

    elif args.palette:
        result = controller.execute_command_palette_command(args.palette)
        print(f"Success: {result.success}")
        if result.error:
            print(f"Error: {result.error}")

    elif args.search:
        results = controller.search_shortcuts(args.search)
        print(f"Found {len(results)} matches:")
        for result in results:
            print(f"  {result['name']}: {result['description']} ({result['keys']})")

    elif args.list:
        shortcuts = controller.get_available_shortcuts(category=args.category)
        print(f"Available shortcuts ({len(shortcuts)}):")
        for name, info in shortcuts.items():
            print(f"  {name}: {info.get('description')} - {info.get('keys')}")

    elif args.type:
        success = controller.type_text(args.type)
        print(f"Typing: {'Success' if success else 'Failed'}")

    else:
        parser.print_help()
        print("\n✅ Cursor IDE Complete Keyboard Controller")
        print("   Full keyboard control - no mouse required")


if __name__ == "__main__":

    main()