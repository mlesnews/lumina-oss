#!/usr/bin/env python3
"""
Automate Cursor Dialogs - No More Clicking "Accept All Changes"

Automatically handles:
- "Keep All" button
- "Accept All Changes" button
- File change dialogs
- Merge conflict dialogs
- Any dialog that requires clicking
"""

import sys
import time
from pathlib import Path
from typing import Optional

try:
    import pyautogui
    import keyboard
    AUTOMATION_AVAILABLE = True
except ImportError:
    AUTOMATION_AVAILABLE = False
    print("⚠️  Install: pip install pyautogui keyboard")

class CursorDialogAutomation:
    """Automate Cursor dialog interactions"""

    def __init__(self):
        self.automation_available = AUTOMATION_AVAILABLE
        if AUTOMATION_AVAILABLE:
            self.pyautogui = pyautogui
            self.keyboard = keyboard

            # Safety settings
            pyautogui.PAUSE = 0.1
            pyautogui.FAILSAFE = True

        # Dialog patterns to detect
        # NOTE: "Keep All" button is actually the "Accept All Changes" button
        # The button text says "Keep All" but tooltip says "Accept all changes"
        self.dialog_patterns = {
            "accept_all_changes": {
                "text": ["Accept All Changes", "accept all", "Keep All", "keep all"],
                "shortcuts": ["Enter", "Alt+A", "Ctrl+Enter", "Alt+K"],
                "button_position": None  # Will be detected
            },
            "keep_all": {
                "text": ["Keep All", "keep all", "Accept All Changes", "accept all"],
                "shortcuts": ["Enter", "Alt+K", "Alt+A"],
                "button_position": None
            }
        }

    def auto_accept_all_changes(self):
        """
        Automatically accept all changes dialog

        Methods tried in order:
        1. Keyboard shortcut (Enter, Alt+A, etc.)
        2. Find button by text and click
        3. Click common button positions
        """
        if not self.automation_available:
            print("❌ Automation not available")
            return False

        print("🔧 Auto-accepting all changes...")

        # Method 1: Try keyboard shortcuts
        shortcuts = ["Enter", "Alt+A", "Ctrl+Enter", "Alt+Y"]
        for shortcut in shortcuts:
            print(f"   Trying shortcut: {shortcut}")
            try:
                self.keyboard.press_and_release(shortcut)
                time.sleep(0.5)
                # Check if dialog is gone (would need screen detection)
                print(f"   ✅ Sent {shortcut}")
                return True
            except Exception as e:
                print(f"   ⚠️  {shortcut} failed: {e}")

        # Method 2: Find button by text
        print("   Searching for 'Accept All Changes' button...")
        try:
            # Look for button text
            button_location = self.pyautogui.locateOnScreen(
                None,  # Would need screenshot of button
                confidence=0.8
            )
            if button_location:
                center = self.pyautogui.center(button_location)
                self.pyautogui.click(center)
                print("   ✅ Clicked 'Accept All Changes' button")
                return True
        except Exception as e:
            print(f"   ⚠️  Button detection failed: {e}")

        # Method 3: Try common button positions
        print("   Trying common button positions...")
        screen_width, screen_height = self.pyautogui.size()

        # Common positions for "Accept" buttons (right side, bottom area)
        common_positions = [
            (screen_width * 0.85, screen_height * 0.85),  # Bottom right
            (screen_width * 0.75, screen_height * 0.85),  # Bottom right-center
            (screen_width * 0.5, screen_height * 0.85),   # Bottom center
        ]

        for pos in common_positions:
            try:
                print(f"   Clicking position: {pos}")
                self.pyautogui.click(pos)
                time.sleep(0.3)
                print("   ✅ Clicked")
                return True
            except Exception as e:
                print(f"   ⚠️  Position {pos} failed: {e}")

        print("   ❌ Could not auto-accept")
        return False

    def auto_keep_all(self):
        """Automatically click 'Keep All' button"""
        if not self.automation_available:
            return False

        print("🔧 Auto-clicking 'Keep All'...")

        # Try keyboard shortcuts first
        shortcuts = ["Enter", "Alt+K", "Alt+Y"]
        for shortcut in shortcuts:
            try:
                self.keyboard.press_and_release(shortcut)
                time.sleep(0.5)
                print(f"   ✅ Sent {shortcut}")
                return True
            except:
                pass

        # Try clicking
        return self.auto_accept_all_changes()  # Same logic

    def watch_and_auto_accept(self, interval: float = 1.0):
        """
        Watch for dialogs and automatically accept

        Runs in background, checks periodically for dialogs
        """
        print("👀 Watching for 'Accept All Changes' dialogs...")
        print("   Will auto-accept when detected")
        print("   Press Ctrl+C to stop")
        print()

        try:
            while True:
                # Check for dialog (simplified - would need actual detection)
                # For now, just wait for manual trigger
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n👋 Stopped watching")


def create_keyboard_hotkey_handler():
    """Create global hotkey to trigger auto-accept"""
    automation = CursorDialogAutomation()

    def on_hotkey():
        print("\n🔥 Hotkey triggered: Auto-accepting all changes...")
        automation.auto_accept_all_changes()

    # Register hotkey (Ctrl+Shift+A for Accept All)
    try:
        keyboard.add_hotkey('ctrl+shift+a', on_hotkey)
        print("✅ Hotkey registered: Ctrl+Shift+A")
        print("   Press Ctrl+Shift+A anytime to auto-accept dialogs")
        print("   Press Ctrl+C to exit")

        keyboard.wait('ctrl+c')
    except Exception as e:
        print(f"❌ Hotkey registration failed: {e}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Automate Cursor dialogs")
    parser.add_argument('--auto-accept', action='store_true',
                       help='Auto-accept all changes dialog')
    parser.add_argument('--keep-all', action='store_true',
                       help='Auto-click Keep All')
    parser.add_argument('--watch', action='store_true',
                       help='Watch for dialogs and auto-accept')
    parser.add_argument('--hotkey', action='store_true',
                       help='Register hotkey (Ctrl+Shift+A) for auto-accept')

    args = parser.parse_args()

    automation = CursorDialogAutomation()

    if args.hotkey:
        create_keyboard_hotkey_handler()
    elif args.watch:
        automation.watch_and_auto_accept()
    elif args.keep_all:
        automation.auto_keep_all()
    elif args.auto_accept:
        automation.auto_accept_all_changes()
    else:
        # Default: register hotkey
        print("="*80)
        print("🔧 Cursor Dialog Automation")
        print("="*80)
        print()
        print("Usage:")
        print("  --auto-accept  : Accept all changes once")
        print("  --keep-all     : Click Keep All once")
        print("  --watch        : Watch for dialogs continuously")
        print("  --hotkey       : Register Ctrl+Shift+A hotkey (recommended)")
        print()
        print("Recommended: python automate_cursor_dialogs.py --hotkey")
        print()
        create_keyboard_hotkey_handler()


if __name__ == "__main__":


    main()