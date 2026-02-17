#!/usr/bin/env python3
"""
Find and Show Kenny Window
Finds Kenny's tkinter window and forces it to be visible on screen.

Tags: #KENNY #WINDOW #VISIBILITY #FIX @JARVIS @LUMINA
"""

import sys
import ctypes
from ctypes import wintypes
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Windows API
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Constants
SW_SHOWNORMAL = 1
SW_RESTORE = 9
SW_SHOW = 5
HWND_TOP = 0
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_SHOWWINDOW = 0x0040

def find_kenny_window():
    """Find Kenny's tkinter window"""
    windows = []

    def enum_windows_callback(hwnd, lParam):
        try:
            # Get window title
            length = user32.GetWindowTextLengthW(hwnd)
            if length == 0:
                return True

            buffer = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buffer, length + 1)
            title = buffer.value

            # Get class name
            class_buffer = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, class_buffer, 256)
            class_name = class_buffer.value

            # Check if it's a tkinter window (TkTopLevel or Tk)
            if 'Tk' in class_name or 'tk' in class_name.lower():
                # Get window position
                rect = wintypes.RECT()
                user32.GetWindowRect(hwnd, ctypes.byref(rect))

                width = rect.right - rect.left
                height = rect.bottom - rect.top

                # Check if this might be Kenny (120x120 window or title contains "Kenny")
                is_kenny = (
                    'kenny' in title.lower() or 
                    'imva' in title.lower() or
                    (width >= 115 and width <= 125 and height >= 115 and height <= 125)  # ~120x120
                )

                windows.append({
                    'hwnd': hwnd,
                    'title': title,
                    'class': class_name,
                    'x': rect.left,
                    'y': rect.top,
                    'width': width,
                    'height': height,
                    'visible': user32.IsWindowVisible(hwnd),
                    'is_kenny': is_kenny
                })
        except:
            pass
        return True

    # EnumWindows callback type
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    callback = EnumWindowsProc(enum_windows_callback)

    # Enumerate all windows
    user32.EnumWindows(callback, 0)

    return windows

def show_window(hwnd, x=100, y=100):
    """Force window to be visible at specific position"""
    try:
        # Show window
        user32.ShowWindow(hwnd, SW_SHOWNORMAL)
        user32.ShowWindow(hwnd, SW_RESTORE)

        # Move to visible position
        user32.SetWindowPos(
            hwnd,
            HWND_TOP,
            x, y,
            0, 0,
            SWP_NOSIZE | SWP_SHOWWINDOW
        )

        # Bring to front
        user32.SetForegroundWindow(hwnd)
        user32.BringWindowToTop(hwnd)

        # Get screen dimensions
        screen_width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
        screen_height = user32.GetSystemMetrics(1)  # SM_CYSCREEN

        # Ensure window is on screen
        rect = wintypes.RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))

        # If off-screen, move to top-right
        if rect.left < -100 or rect.left > screen_width or \
           rect.top < -100 or rect.top > screen_height:
            safe_x = screen_width - 140  # 120px window + 20px margin
            safe_y = 20
            user32.SetWindowPos(
                hwnd,
                HWND_TOP,
                safe_x, safe_y,
                0, 0,
                SWP_NOSIZE | SWP_SHOWWINDOW
            )

        return True
    except Exception as e:
        print(f"   ❌ Error showing window: {e}")
        return False

def process_window(win, screen_w, screen_h):
    """Process a single window"""
    is_off_screen = (
        win['x'] < -100 or win['x'] > screen_w or
        win['y'] < -100 or win['y'] > screen_h
    )

    if is_off_screen:
        print(f"   ⚠️  Window is OFF-SCREEN!")
        print(f"   → Moving to visible position...")
        if show_window(win['hwnd'], screen_w - 140, 20):
            print(f"   ✅ Window moved to visible position")
    elif not win['visible']:
        print(f"   ⚠️  Window is not visible")
        print(f"   → Making visible...")
        if show_window(win['hwnd'], win['x'], win['y']):
            print(f"   ✅ Window made visible")
    else:
        print(f"   ✅ Window is visible")
        # Still bring to front
        show_window(win['hwnd'], win['x'], win['y'])
        print(f"   ✅ Window brought to front")

    print()

def main():
    """Main function"""
    print("=" * 80)
    print("🔍 FINDING AND SHOWING KENNY WINDOW")
    print("=" * 80)
    print()

    # Find all tkinter windows
    print("🔍 Searching for tkinter windows...")
    windows = find_kenny_window()

    if not windows:
        print("   ❌ No tkinter windows found")
        print("   → Kenny might not be running")
        print("   → Run: python scripts/python/start_kenny_visible.py")
        return

    print(f"   ✅ Found {len(windows)} tkinter window(s)")
    print()

    # Get screen dimensions
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)

    # Prioritize Kenny windows
    kenny_windows = [w for w in windows if w.get('is_kenny', False)]
    other_windows = [w for w in windows if not w.get('is_kenny', False)]

    # Show Kenny windows first
    if kenny_windows:
        print("🤖 KENNY WINDOWS FOUND:")
        print()
        for i, win in enumerate(kenny_windows, 1):
            print(f"📊 Kenny Window {i}:")
            print(f"   HWND: {win['hwnd']}")
            print(f"   Title: {win['title']}")
            print(f"   Class: {win['class']}")
            print(f"   Position: ({win['x']}, {win['y']})")
            print(f"   Size: {win['width']}x{win['height']}")
            print(f"   Visible: {win['visible']}")
            process_window(win, screen_width, screen_height)
    else:
        print("❌ No Kenny windows found!")
        print("   → Kenny might not be running")
        print("   → Or window hasn't been created yet")
        print()

    # Show other tkinter windows (for reference, first 3 only)
    if other_windows:
        print("📋 Other Tkinter Windows (for reference):")
        print()
        for i, win in enumerate(other_windows[:3], 1):
            print(f"📊 Window {i}:")
            print(f"   HWND: {win['hwnd']}")
            print(f"   Title: {win['title']}")
            print(f"   Size: {win['width']}x{win['height']}")
            print()

    print("=" * 80)
    print("✅ Done! Kenny window(s) should now be visible")
    print("=" * 80)
    print()
    print("Look for:")
    print("  - 120x120px window")
    print("  - Hot Rod Red circle")
    print("  - Hexagonal helmet")
    print("  - Top-right corner of screen (or visible position)")
    print()

if __name__ == "__main__":


    main()