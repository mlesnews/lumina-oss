#!/usr/bin/env python3
"""
Configure Multi-Function Key for Voice Input
One key with multiple functions: short press, long press, double tap, toggle
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("Multi-Function Key Configuration")
print("Voice Input + Caps Lock Toggle on One Key")
print("=" * 70)
print()

print("KEY RECOMMENDATIONS (Best to Good):")
print("-" * 70)
print()

keys = [
    {
        "key": "Right Alt (RAlt)",
        "pros": ["Rarely used", "Easy to reach", "No conflicts", "Perfect for remapping"],
        "cons": ["None"],
        "rating": "⭐⭐⭐⭐⭐ BEST"
    },
    {
        "key": "Right Ctrl (RCtrl)",
        "pros": ["Rarely used", "Easy to reach", "No conflicts"],
        "cons": ["Some apps use it"],
        "rating": "⭐⭐⭐⭐ EXCELLENT"
    },
    {
        "key": "Menu Key (AppsKey)",
        "pros": ["Almost never used", "Perfect for remapping"],
        "cons": ["Location varies by keyboard"],
        "rating": "⭐⭐⭐⭐ EXCELLENT"
    },
    {
        "key": "Scroll Lock",
        "pros": ["Never used", "Safe to remap"],
        "cons": ["Not on all keyboards", "Location varies"],
        "rating": "⭐⭐⭐ GOOD"
    },
    {
        "key": "Caps Lock",
        "pros": ["Easy to reach", "Always available"],
        "cons": ["Commonly used", "Need to preserve original function"],
        "rating": "⭐⭐⭐ GOOD (with toggle)"
    }
]

for key_info in keys:
    print(f"{key_info['rating']}: {key_info['key']}")
    print(f"  Pros: {', '.join(key_info['pros'])}")
    if key_info['cons']:
        print(f"  Cons: {', '.join(key_info['cons'])}")
    print()

print("=" * 70)
print("MULTI-FUNCTION KEY ACTIONS")
print("=" * 70)
print()

actions = [
    {
        "action": "Short Press (< 500ms)",
        "function": "Voice Input (Windows Key + H)",
        "use_case": "Quick voice command"
    },
    {
        "action": "Long Press (500ms+)",
        "function": "Voice Input (Windows Key + H)",
        "use_case": "Deliberate voice input"
    },
    {
        "action": "Double Tap",
        "function": "Toggle Caps Lock",
        "use_case": "Quick Caps Lock toggle"
    },
    {
        "action": "Very Long Press (1 second+)",
        "function": "Toggle Caps Lock",
        "use_case": "Alternative Caps Lock toggle"
    }
]

for action in actions:
    print(f"• {action['action']}")
    print(f"  → {action['function']}")
    print(f"  Use: {action['use_case']}")
    print()

print("=" * 70)
print("RECOMMENDATION")
print("=" * 70)
print()
print("🎯 BEST CHOICE: Right Alt (RAlt)")
print()
print("Why Right Alt?")
print("  ✅ Rarely used in most applications")
print("  ✅ Easy to reach with thumb")
print("  ✅ No conflicts with existing shortcuts")
print("  ✅ Perfect for remapping")
print("  ✅ Can keep Caps Lock as-is (or use Shift+CapsLock)")
print()

print("=" * 70)
print("SETUP INSTRUCTIONS")
print("=" * 70)
print()

print("1. INSTALL AUTOHOTKEY")
print("   Download: https://www.autohotkey.com/")
print("   Install AutoHotkey v1.1 or v2.0")
print()

print("2. CONFIGURE THE SCRIPT")
print("   Edit: scripts/autohotkey/multifunction_key_voice_input.ahk")
print("   Change: TARGET_KEY := \"RAlt\"  (or your preferred key)")
print("   Options: \"CapsLock\", \"RAlt\", \"RCtrl\", \"AppsKey\", \"ScrollLock\"")
print()

print("3. RUN THE SCRIPT")
print("   Double-click: scripts/autohotkey/multifunction_key_voice_input.ahk")
print("   Or add to Windows Startup folder for auto-start")
print()

print("4. TEST IT")
print("   • Short press Right Alt → Voice Input")
print("   • Double tap Right Alt → Toggle Caps Lock")
print("   • Long hold Right Alt → Toggle Caps Lock")
print()

print("=" * 70)
print("ALTERNATIVE: KEEP CAPS LOCK + ADD VOICE INPUT")
print("=" * 70)
print()

print("If you want to keep Caps Lock AND add voice input:")
print()
print("Option A: Use Right Alt for voice input only")
print("  - Right Alt → Voice Input (simple)")
print("  - Caps Lock → Caps Lock (unchanged)")
print()
print("Option B: Multi-function on Right Alt")
print("  - Right Alt (short) → Voice Input")
print("  - Right Alt (double tap) → Caps Lock toggle")
print("  - Caps Lock → Caps Lock (unchanged)")
print()

print("=" * 70)
print("CUSTOMIZATION")
print("=" * 70)
print()

print("You can customize timing in the script:")
print("  LONG_PRESS_TIME := 500    ; Milliseconds for long press")
print("  DOUBLE_TAP_TIME := 300    ; Milliseconds between taps")
print("  TOGGLE_HOLD_TIME := 1000  ; Milliseconds for toggle mode")
print()

print("=" * 70)
