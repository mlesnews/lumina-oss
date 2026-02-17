#!/usr/bin/env python3
"""
JARVIS Desktop Keyboard Controller
Comprehensive desktop-wide keyboard and mouse control for JARVIS.

Tags: #KEYBOARD #MOUSE #DESKTOP #CONTROL @AUTO @MANUS
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISDesktopControl")

try:
    import pynput
    from pynput.keyboard import Key, Controller as KeyboardController
    from pynput.mouse import Button, Controller as MouseController
    import pyautogui
    import pygetwindow as gw
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    logger.warning("Required libraries not available - install: pip install pynput pyautogui pygetwindow")


class JARVISDesktopController:
    """
    Desktop-wide keyboard and mouse controller for JARVIS.
    """

    def __init__(self):
        if not PYNPUT_AVAILABLE:
            logger.error("❌ Required libraries not available - control disabled")
            self.keyboard = None
            self.mouse = None
            return

        self.keyboard = KeyboardController()
        self.mouse = MouseController()
        self.logger = logger
        self.logger.info("✅ JARVIS Desktop Controller initialized")

    def press_shortcut(self, keys: List[Any]):
        """Press a combination of keys (e.g., [Key.cmd, 'd'])"""
        if not self.keyboard: return

        try:
            # Press all keys
            for key in keys:
                self.keyboard.press(key)
                time.sleep(0.05)

            # Release all keys in reverse order
            for key in reversed(keys):
                self.keyboard.release(key)
                time.sleep(0.05)

            self.logger.info(f"🎹 Executed shortcut: {keys}")
        except Exception as e:
            self.logger.error(f"❌ Keyboard error: {e}")

    def type_text(self, text: str):
        """Type text string"""
        if not self.keyboard: return
        self.keyboard.type(text)
        self.logger.info(f"⌨️ Typed text: {text[:20]}...")

    def move_mouse_to(self, x: int, y: int):
        """Move mouse to coordinates"""
        if not self.mouse: return
        pyautogui.moveTo(x, y, duration=0.2)
        self.logger.info(f"🖱️ Moved mouse to ({x}, {y})")

    def click(self, button=Button.left):
        """Click mouse button"""
        if not self.mouse: return
        self.mouse.click(button)
        self.logger.info(f"🖱️ Clicked {button}")

    def focus_window(self, title_regex: str) -> bool:
        """Focus a window by its title (regex)"""
        try:
            windows = gw.getWindowsWithTitle('')
            for window in windows:
                if title_regex.lower() in window.title.lower():
                    window.activate()
                    self.logger.info(f"🪟 Focused window: {window.title}")
                    return True
            return False
        except Exception as e:
            self.logger.error(f"❌ Window focus error: {e}")
            return False

    def list_windows(self) -> List[str]:
        """List all open window titles"""
        return [w.title for w in gw.getAllTitles() if w.strip()]


def main():
    """CLI interface for testing"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Desktop Controller")
    parser.add_argument("--list-windows", action="store_true", help="List all open windows")
    parser.add_argument("--focus", type=str, help="Focus window by title")
    parser.add_argument("--shortcut", nargs="+", help="Execute shortcut (e.g., cmd d)")

    args = parser.parse_args()
    controller = JARVISDesktopController()

    if args.list_windows:
        for title in controller.list_windows():
            print(f"- {title}")
    elif args.focus:
        controller.focus_window(args.focus)
    elif args.shortcut:
        # Map strings to Key objects if needed
        key_map = {
            "cmd": Key.cmd,
            "ctrl": Key.ctrl,
            "shift": Key.shift,
            "alt": Key.alt,
            "tab": Key.tab,
            "enter": Key.enter,
            "space": Key.space,
            "win": Key.cmd
        }
        keys = [key_map.get(k.lower(), k) for k in args.shortcut]
        controller.press_shortcut(keys)
    else:
        parser.print_help()


if __name__ == "__main__":


    main()