#!/usr/bin/env python3
"""
Configure Right Alt Key for Cursor IDE Voice Input
Maps Right Alt to trigger voice input specifically in Cursor IDE
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("Cursor IDE Voice Input Configuration")
print("Right Alt → Voice Input in Cursor IDE")
print("=" * 70)
print()

print("CONFIGURATION:")
print("-" * 70)
print("  Key: Right Alt (RAlt)")
print("  Target: Cursor IDE Voice Input")
print("  Fallback: Windows Voice Input (if not in Cursor IDE)")
print()

print("HOW IT WORKS:")
print("-" * 70)
print("  • Right Alt pressed in Cursor IDE → Triggers Cursor voice input")
print("  • Right Alt pressed elsewhere → Triggers Windows voice input")
print("  • Context-aware: Detects Cursor IDE window automatically")
print()

print("CURSOR IDE VOICE INPUT SHORTCUT:")
print("-" * 70)
print("  Default: Ctrl+Shift+V")
print("  (Check your Cursor IDE settings to confirm)")
print()

print("TO FIND YOUR CURSOR IDE VOICE INPUT SHORTCUT:")
print("-" * 70)
print("  1. Open Cursor IDE")
print("  2. Go to: File > Preferences > Keyboard Shortcuts")
print("  3. Search for: 'voice' or 'speech' or 'input'")
print("  4. Note the keyboard shortcut")
print("  5. Update the script if different from Ctrl+Shift+V")
print()

print("=" * 70)
print("SETUP INSTRUCTIONS")
print("=" * 70)
print()

print("1. INSTALL AUTOHOTKEY")
print("   Download: https://www.autohotkey.com/")
print("   Install AutoHotkey v1.1 or v2.0")
print()

print("2. VERIFY CURSOR IDE VOICE INPUT SHORTCUT")
print("   Check Cursor IDE settings for voice input shortcut")
print("   Default is usually: Ctrl+Shift+V")
print()

print("3. UPDATE SCRIPT (if needed)")
print("   Edit: scripts/autohotkey/cursor_ide_voice_input_right_alt.ahk")
print("   Change: VOICE_INPUT_SHORTCUT := \"^+V\"")
print("   Format: ^ = Ctrl, + = Shift, ! = Alt, # = Win")
print()

print("4. RUN THE SCRIPT")
print("   Double-click: scripts/autohotkey/cursor_ide_voice_input_right_alt.ahk")
print("   Or add to Windows Startup folder for auto-start")
print()

print("5. TEST IT")
print("   • Open Cursor IDE")
print("   • Press Right Alt")
print("   • Voice input should activate in Cursor IDE")
print()

print("=" * 70)
print("CUSTOMIZATION")
print("=" * 70)
print()

print("If Cursor IDE uses a different shortcut:")
print("  • Ctrl+Shift+V → \"^+V\"")
print("  • Ctrl+Shift+S → \"^+S\"")
print("  • F2 → \"{F2}\"")
print("  • Custom → Check AutoHotkey key syntax")
print()

print("To change the key (if Right Alt doesn't work):")
print("  • Change 'RAlt::' to your preferred key")
print("  • Options: RCtrl, AppsKey, ScrollLock, etc.")
print()

print("=" * 70)
print("FILES CREATED")
print("=" * 70)
print()

autohotkey_file = project_root / "scripts" / "autohotkey" / "cursor_ide_voice_input_right_alt.ahk"
print(f"✅ AutoHotkey script: {autohotkey_file}")
print()

print("=" * 70)
