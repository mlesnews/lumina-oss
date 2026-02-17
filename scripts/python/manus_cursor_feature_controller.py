#!/usr/bin/env python3
"""
MANUS Cursor Feature Controller - Execute Cursor IDE Features

Provides execution methods for all Cursor IDE features via MANUS control.

Tags: #MANUS #CURSOR_IDE #FEATURE_CONTROL #EXECUTION @JARVIS @LUMINA #PEAK
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
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

logger = get_logger("MANUSCursorFeatureController")

try:
    from manus_cursor_controller import ManusCursorController
    CURSOR_CONTROLLER_AVAILABLE = True
except ImportError:
    CURSOR_CONTROLLER_AVAILABLE = False
    logger.warning("MANUS Cursor Controller not available")

try:
    import pyautogui
    import keyboard
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    logger.warning("pyautogui/keyboard not available")


class MANUSCursorFeatureController:
    """
    MANUS Cursor Feature Controller

    Executes Cursor IDE features via keyboard shortcuts, command palette, or direct control.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize feature controller"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.cursor_controller = None

        if CURSOR_CONTROLLER_AVAILABLE:
            try:
                self.cursor_controller = ManusCursorController()
                if not self.cursor_controller.connect_to_cursor():
                    logger.warning("⚠️  Failed to connect to Cursor IDE")
                else:
                    logger.info("✅ Connected to Cursor IDE")
            except Exception as e:
                logger.warning(f"⚠️  Cursor Controller initialization failed: {e}")

    def execute_keyboard_shortcut(self, shortcut: str) -> Dict[str, Any]:
        """
        Execute feature via keyboard shortcut

        Args:
            shortcut: Keyboard shortcut (e.g., "Ctrl+P", "F12")

        Returns:
            Execution result
        """
        start_time = time.time()

        try:
            if not self.cursor_controller:
                return {
                    "success": False,
                    "error": "Cursor Controller not available",
                    "method": "keyboard_shortcut"
                }

            # Parse shortcut
            keys = self._parse_shortcut(shortcut)

            # Send keyboard shortcut
            if self.cursor_controller.keyboard:
                for key in keys:
                    if hasattr(self.cursor_controller.keyboard, 'press'):
                        # Use pynput keyboard
                        key_obj = self._get_key_object(key)
                        if key_obj:
                            self.cursor_controller.keyboard.press(key_obj)
                        else:
                            self.cursor_controller.keyboard.press(key)

                time.sleep(0.1)

                # Release in reverse order
                for key in reversed(keys):
                    key_obj = self._get_key_object(key)
                    if key_obj:
                        self.cursor_controller.keyboard.release(key_obj)
                    else:
                        self.cursor_controller.keyboard.release(key)
            elif PYAUTOGUI_AVAILABLE:
                # Use pyautogui as fallback
                pyautogui.hotkey(*keys)
            else:
                return {
                    "success": False,
                    "error": "No keyboard control available",
                    "method": "keyboard_shortcut"
                }

            execution_time = time.time() - start_time

            return {
                "success": True,
                "method": "keyboard_shortcut",
                "shortcut": shortcut,
                "execution_time": execution_time
            }

        except Exception as e:
            logger.error(f"Error executing keyboard shortcut '{shortcut}': {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "method": "keyboard_shortcut",
                "execution_time": time.time() - start_time
            }

    def execute_command_palette(self, command_name: str) -> Dict[str, Any]:
        """
        Execute feature via Command Palette

        Args:
            command_name: Command name to search for (e.g., "Git: Stage All Changes")

        Returns:
            Execution result
        """
        start_time = time.time()

        try:
            if not self.cursor_controller:
                return {
                    "success": False,
                    "error": "Cursor Controller not available",
                    "method": "command_palette"
                }

            # Open command palette
            palette_result = self.execute_keyboard_shortcut("Ctrl+Shift+P")
            if not palette_result.get("success"):
                return palette_result

            time.sleep(0.5)  # Wait for palette to open

            # Type command name
            if self.cursor_controller.keyboard:
                self.cursor_controller.keyboard.type(command_name)
                time.sleep(0.3)

                # Press Enter to execute
                from pynput.keyboard import Key
                self.cursor_controller.keyboard.press(Key.enter)
                time.sleep(0.1)
                self.cursor_controller.keyboard.release(Key.enter)
            elif PYAUTOGUI_AVAILABLE:
                keyboard.write(command_name)
                time.sleep(0.3)
                keyboard.press_and_release('enter')
            else:
                return {
                    "success": False,
                    "error": "No keyboard control available",
                    "method": "command_palette"
                }

            execution_time = time.time() - start_time

            return {
                "success": True,
                "method": "command_palette",
                "command": command_name,
                "execution_time": execution_time
            }

        except Exception as e:
            logger.error(f"Error executing command palette '{command_name}': {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "method": "command_palette",
                "execution_time": time.time() - start_time
            }

    def _parse_shortcut(self, shortcut: str) -> List[str]:
        """Parse keyboard shortcut string into key list"""
        # Normalize shortcut
        shortcut = shortcut.replace("+", " ").strip()
        keys = shortcut.split()

        # Normalize key names
        normalized = []
        for key in keys:
            key_lower = key.lower()
            if key_lower == "ctrl":
                normalized.append("ctrl")
            elif key_lower == "shift":
                normalized.append("shift")
            elif key_lower == "alt":
                normalized.append("alt")
            elif key_lower.startswith("f") and key_lower[1:].isdigit():
                normalized.append(key.upper())  # F1, F2, etc.
            else:
                normalized.append(key.lower())

        return normalized

    def _get_key_object(self, key_name: str):
        """Get pynput Key object from key name"""
        try:
            from pynput.keyboard import Key

            key_map = {
                "ctrl": Key.ctrl,
                "shift": Key.shift,
                "alt": Key.alt,
                "enter": Key.enter,
                "escape": Key.esc,
                "tab": Key.tab,
                "space": Key.space,
                "backspace": Key.backspace,
                "delete": Key.delete,
                "up": Key.up,
                "down": Key.down,
                "left": Key.left,
                "right": Key.right,
                "home": Key.home,
                "end": Key.end,
                "pageup": Key.page_up,
                "pagedown": Key.page_down,
            }

            # Add function keys
            if key_name.upper().startswith("F") and key_name[1:].isdigit():
                return getattr(Key, f"f{key_name[1:]}", None)

            return key_map.get(key_name.lower())
        except ImportError:
            return None


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="MANUS Cursor Feature Controller")
    parser.add_argument("--shortcut", type=str, help="Keyboard shortcut to execute (e.g., Ctrl+P)")
    parser.add_argument("--command", type=str, help="Command palette command to execute")

    args = parser.parse_args()

    controller = MANUSCursorFeatureController()

    if args.shortcut:
        result = controller.execute_keyboard_shortcut(args.shortcut)
        print(f"Result: {result}")

    elif args.command:
        result = controller.execute_command_palette(args.command)
        print(f"Result: {result}")

    else:
        print("Use --shortcut to execute keyboard shortcut or --command for command palette")


if __name__ == "__main__":


    main()