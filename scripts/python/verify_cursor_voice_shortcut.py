#!/usr/bin/env python3
"""
Verify Cursor IDE Voice Input Shortcut
Helps identify the correct keyboard shortcut for Cursor IDE voice input
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("Cursor IDE Voice Input Shortcut Verification")
print("=" * 70)
print()

print("HOW TO FIND YOUR CURSOR IDE VOICE INPUT SHORTCUT:")
print("-" * 70)
print()
print("METHOD 1: Keyboard Shortcuts Menu")
print("  1. Open Cursor IDE")
print("  2. Press: Ctrl+K Ctrl+S  (or File > Preferences > Keyboard Shortcuts)")
print("  3. In the search box, type: voice")
print("  4. Look for commands like:")
print("     - cursor.voice.start")
print("     - cursor.speech.start")
print("     - cursor.microphone.start")
print("     - cursor.transcription.start")
print("     - workbench.action.voice.start")
print("  5. Note the keyboard shortcut shown")
print()

print("METHOD 2: Command Palette")
print("  1. Open Cursor IDE")
print("  2. Press: Ctrl+Shift+P  (Command Palette)")
print("  3. Type: voice")
print("  4. Look for voice-related commands")
print("  5. Check if a keyboard shortcut is shown")
print()

print("METHOD 3: UI Button")
print("  1. Open Cursor IDE")
print("  2. Look for microphone/voice button in the chat panel")
print("  3. Right-click the button")
print("  4. Check for 'Keyboard Shortcut' option")
print()

print("=" * 70)
print("COMMON CURSOR IDE VOICE INPUT SHORTCUTS")
print("=" * 70)
print()

common_shortcuts = [
    {
        "shortcut": "Ctrl+Shift+V",
        "autohotkey": "^+V",
        "likelihood": "⭐⭐⭐⭐⭐ Most Common",
        "notes": "Standard VS Code/Cursor pattern"
    },
    {
        "shortcut": "Ctrl+Alt+V",
        "autohotkey": "^!V",
        "likelihood": "⭐⭐⭐ Possible",
        "notes": "Alternative voice input"
    },
    {
        "shortcut": "Alt+V",
        "autohotkey": "!V",
        "likelihood": "⭐⭐ Possible",
        "notes": "Simple Alt combination"
    },
    {
        "shortcut": "F2",
        "autohotkey": "{F2}",
        "likelihood": "⭐ Unlikely",
        "notes": "If custom configured"
    },
    {
        "shortcut": "Ctrl+Shift+S",
        "autohotkey": "^+S",
        "likelihood": "⭐ Unlikely",
        "notes": "Speech input variant"
    }
]

for shortcut_info in common_shortcuts:
    print(f"{shortcut_info['likelihood']}: {shortcut_info['shortcut']}")
    print(f"  AutoHotkey format: {shortcut_info['autohotkey']}")
    print(f"  Notes: {shortcut_info['notes']}")
    print()

print("=" * 70)
print("AUTOHOTKEY SCRIPT CONFIGURATION")
print("=" * 70)
print()

print("Current script uses: Ctrl+Shift+V (^+V)")
print()
print("To change it, edit: scripts/autohotkey/cursor_ide_voice_input_right_alt.ahk")
print("Change this line:")
print("  Send, ^+v")
print()
print("To one of these:")
print("  Send, ^!v      ; Ctrl+Alt+V")
print("  Send, !v       ; Alt+V")
print("  Send, {F2}     ; F2")
print()

print("=" * 70)
print("TESTING INSTRUCTIONS")
print("=" * 70)
print()

print("1. Install AutoHotkey: https://www.autohotkey.com/")
print("2. Run the script: cursor_ide_voice_input_right_alt.ahk")
print("3. Open Cursor IDE")
print("4. Press Right Alt")
print("5. If voice input doesn't activate:")
print("   a. Check Cursor IDE keyboard shortcuts (Ctrl+K Ctrl+S)")
print("   b. Find the actual voice input shortcut")
print("   c. Update the AutoHotkey script")
print()

print("=" * 70)
print("QUICK VERIFICATION COMMAND")
print("=" * 70)
print()
print("Run this in Cursor IDE Command Palette (Ctrl+Shift+P):")
print("  > Preferences: Open Keyboard Shortcuts (JSON)")
print()
print("Then search for 'voice' in the JSON file")
print()

print("=" * 70)
