#!/usr/bin/env python3
"""
JARVIS Auto-Accept All - Eliminate "Accept All Changes" Clicks

One-command solution to automatically handle:
- "Keep All" dialogs
- "Accept All Changes" dialogs
- Any confirmation dialogs in Cursor

Usage:
    python jarvis_auto_accept_all.py
    # Then press Ctrl+Shift+A whenever you see "Accept All Changes"

Or run in background:
    python jarvis_auto_accept_all.py --background
"""

import sys
import time
from pathlib import Path

try:
    import keyboard
    import pyautogui
    AUTOMATION_AVAILABLE = True
except ImportError:
    AUTOMATION_AVAILABLE = False
    print("❌ Missing dependencies. Install:")
    print("   pip install keyboard pyautogui")
    sys.exit(1)

class JARVISAutoAccept:
    """JARVIS Auto-Accept All Changes"""

    def __init__(self):
        self.running = False
        pyautogui.PAUSE = 0.1
        pyautogui.FAILSAFE = True

    def accept_all_changes(self):
        """Accept all changes - tries multiple methods"""
        print("\n🔧 JARVIS: Auto-accepting all changes...")

        # Method 1: Try Enter key (most common)
        print("   Method 1: Pressing Enter...")
        keyboard.press_and_release('enter')
        time.sleep(0.3)

        # Method 2: Try Alt+A (Accept)
        print("   Method 2: Pressing Alt+A...")
        keyboard.press_and_release('alt+a')
        time.sleep(0.3)

        # Method 3: Try Tab then Enter (focus button then accept)
        print("   Method 3: Tab + Enter...")
        keyboard.press_and_release('tab')
        time.sleep(0.1)
        keyboard.press_and_release('enter')
        time.sleep(0.3)

        # Method 4: Try Escape then Enter (close any popup, then accept)
        print("   Method 4: Escape + Enter...")
        keyboard.press_and_release('escape')
        time.sleep(0.1)
        keyboard.press_and_release('enter')

        print("   ✅ Auto-accept sequence completed")
        return True

    def keep_all(self):
        """Keep all - same as accept all"""
        return self.accept_all_changes()

    def start_hotkey_listener(self):
        """Start listening for hotkey"""
        print("="*80)
        print("🤖 JARVIS Auto-Accept All - Active")
        print("="*80)
        print()
        print("✅ Hotkey registered: Ctrl+Shift+A")
        print()
        print("💡 Whenever you see 'Accept All Changes' or 'Keep All':")
        print("   Just press Ctrl+Shift+A")
        print("   JARVIS will automatically click it for you!")
        print()
        print("   No more clicking required! 🎉")
        print()
        print("Press Ctrl+C to stop")
        print("-" * 80)
        print()

        self.running = True

        def on_hotkey():
            self.accept_all_changes()

        # Register hotkey
        keyboard.add_hotkey('ctrl+shift+a', on_hotkey)

        # Also register alternative
        keyboard.add_hotkey('ctrl+shift+k', lambda: self.keep_all())

        print("✅ Hotkeys active:")
        print("   Ctrl+Shift+A = Accept All Changes")
        print("   Ctrl+Shift+K = Keep All")
        print()
        print("👀 Waiting for hotkey...")
        print()

        try:
            keyboard.wait('ctrl+c')
        except KeyboardInterrupt:
            pass

        print("\n👋 JARVIS Auto-Accept stopped")

    def run_once(self):
        """Run auto-accept once (for immediate use)"""
        print("🔧 Running auto-accept once...")
        self.accept_all_changes()
        print("✅ Done!")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="JARVIS Auto-Accept All Changes - No More Clicking!"
    )
    parser.add_argument('--once', action='store_true',
                       help='Run auto-accept once and exit')
    parser.add_argument('--background', action='store_true',
                       help='Run in background (hotkey mode)')

    args = parser.parse_args()

    auto_accept = JARVISAutoAccept()

    if args.once:
        auto_accept.run_once()
    else:
        # Default: hotkey mode
        auto_accept.start_hotkey_listener()


if __name__ == "__main__":


    main()