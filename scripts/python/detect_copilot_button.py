#!/usr/bin/env python3
"""
Detect Microsoft Copilot Button Scan Code
Helps identify the exact scan code for your Copilot button
"""

import keyboard
import time

print("=" * 80)
print("COPILOT BUTTON DETECTOR")
print("=" * 80)
print()
print("Press your Copilot button now...")
print("(Press ESC to exit)")
print()
print("=" * 80)
print()

def on_key_event(event):
    """Detect and display key information"""
    print(f"Key Pressed:")
    print(f"  Name: {event.name}")
    print(f"  Scan Code: {hex(event.scan_code)} ({event.scan_code})")
    if hasattr(event, 'vk'):
        print(f"  Virtual Key: {hex(event.vk)} ({event.vk})")
    print()

    # Check if it might be Copilot
    if event.scan_code == 0xFF or event.scan_code == 0x5D or event.name == 'f23':
        print("  ✅ This might be the Copilot button!")
        print()
        print("  Add to AutoHotkey script:")
        if event.scan_code == 0xFF:
            print("    *vkFF::")
        elif event.name == 'f23':
            print("    F23::")
        else:
            print(f"    ; Scan code: {hex(event.scan_code)}")
        print("        Send, @JARVIS{Enter}")
        print("        return")
        print()

# Hook keyboard
keyboard.hook(on_key_event)

print("Listening for key presses...")
print("Press your Copilot button to detect it")
print()

try:
    while True:
        time.sleep(0.1)
        if keyboard.is_pressed('esc'):
            break
except KeyboardInterrupt:
    pass

keyboard.unhook_all()
print("✅ Detection stopped")
