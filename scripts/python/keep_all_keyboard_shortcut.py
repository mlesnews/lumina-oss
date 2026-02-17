#!/usr/bin/env python3
"""
Keep All Keyboard Shortcut - REQUIRED

Maps keyboard shortcut to Keep All button.
User shouldn't have to click - just press shortcut.

Tags: #KEYBOARD_SHORTCUT #KEEP_ALL #REQUIRED @JARVIS @LUMINA
"""

import sys
import time
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("❌ keyboard library not available - install: pip install keyboard")

try:
    from manus_accept_all_button import MANUSAcceptAllButton
    BUTTON_AVAILABLE = True
except ImportError:
    BUTTON_AVAILABLE = False

if KEYBOARD_AVAILABLE and BUTTON_AVAILABLE:
    button = MANUSAcceptAllButton()

    # Map Ctrl+Shift+A to Keep All button
    def click_keep_all():
        print("🔘 Keep All shortcut pressed - clicking button...")
        try:
            button.click_accept_all()
            print("✅ Keep All button clicked")
        except Exception as e:
            print(f"❌ Failed to click: {e}")

    keyboard.add_hotkey('ctrl+shift+a', click_keep_all)
    print("✅ Keep All keyboard shortcut mapped: Ctrl+Shift+A")
    print("   Press Ctrl+Shift+A to auto-click Keep All button")
    print("   (Also works automatically via aggressive button clicker)")
    print()
    print("Press Ctrl+C to stop")

    try:
        keyboard.wait()
    except KeyboardInterrupt:
        print("\n👋 Stopping...")
else:
    print("❌ Required libraries not available")
