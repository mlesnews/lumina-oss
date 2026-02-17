#!/usr/bin/env python3
"""
Debug Kenny Window - Check Why It's Not Visible

Actually checks if Kenny window is rendering and visible.

Tags: #DEBUG #VISIBILITY #REQUIRED @JARVIS @LUMINA
"""

import sys
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    import pygetwindow as gw
    import pyautogui
except ImportError:
    print("❌ pygetwindow/pyautogui not available")
    sys.exit(1)

print("=" * 80)
print("🔍 DEBUGGING KENNY WINDOW")
print("=" * 80)
print()

# Find Kenny window
windows = gw.getWindowsWithTitle("IRON MAN")
if not windows:
    windows = gw.getWindowsWithTitle("Kenny")
if not windows:
    windows = gw.getWindowsWithTitle("IMVA")

if not windows:
    print("❌ No Kenny window found!")
    print("   Kenny may not be running")
    sys.exit(1)

window = windows[0]
print(f"✅ Found window: {window.title}")
print(f"   Position: ({window.left}, {window.top})")
print(f"   Size: {window.width}x{window.height}")
print(f"   Visible: {window.visible}")
print()

# Check if window is on screen
screen_width, screen_height = pyautogui.size()
print(f"📺 Screen size: {screen_width}x{screen_height}")
print()

on_screen = (0 <= window.left <= screen_width and 0 <= window.top <= screen_height)
print(f"   On screen: {on_screen}")

if not on_screen:
    print("⚠️  Window is off-screen!")
    print(f"   Moving to visible area...")
    window.moveTo(screen_width - 140, 20)
    window.resizeTo(120, 120)
    print("✅ Moved and resized")

# Bring to front
print()
print("🔝 Bringing window to front...")
try:
    window.activate()
    window.restore()  # Un-minimize if minimized
    time.sleep(0.5)
    print("✅ Window brought to front")
except Exception as e:
    print(f"⚠️  Could not bring to front: {e}")

# Check if window is actually rendering
print()
print("🎨 Checking if window is rendering...")
print("   Taking screenshot of window area...")

try:
    # Take screenshot of window area
    screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
    screenshot_path = project_root / "data" / "kenny_window_screenshot.png"
    screenshot.save(screenshot_path)
    print(f"✅ Screenshot saved: {screenshot_path}")

    # Check if screenshot has content (not just transparent/black)
    from PIL import Image
    import numpy as np

    pixels = np.array(screenshot)
    # Check for non-transparent/non-black pixels
    non_black = np.sum(pixels > 10)  # Pixels brighter than very dark
    total_pixels = pixels.size

    print(f"   Non-black pixels: {non_black}/{total_pixels} ({100*non_black/total_pixels:.1f}%)")

    if non_black < total_pixels * 0.01:  # Less than 1% non-black
        print("⚠️  Window appears to be empty/transparent!")
        print("   Kenny may not be drawing/rendering")
    else:
        print("✅ Window has content (should be visible)")
except Exception as e:
    print(f"⚠️  Could not check rendering: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("✅ DEBUG COMPLETE")
print("=" * 80)
print()
print("If Kenny is still not visible:")
print("  1. Window may not be rendering (check screenshot)")
print("  2. Window may be behind other windows")
print("  3. Animation loop may not be running")
print("  4. Drawing code may have errors")
print()
