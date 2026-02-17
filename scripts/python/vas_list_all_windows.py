#!/usr/bin/env python3
"""
List All Windows - Diagnose VA Visibility Issues

Lists all visible windows to help diagnose why VAs aren't being found.

Tags: #VAS #DIAGNOSTIC #WINDOWS @JARVIS @TEAM
"""

import sys
import ctypes
from ctypes import wintypes
from typing import List, Tuple

if sys.platform != "win32":
    print("This script is for Windows only")
    sys.exit(1)

user32 = ctypes.windll.user32

windows_found = []

def enum_windows_callback(hwnd, lParam):
    """Callback to enumerate windows"""
    if user32.IsWindowVisible(hwnd):
        buffer = ctypes.create_unicode_buffer(512)
        user32.GetWindowTextW(hwnd, buffer, 512)
        title = buffer.value
        if title:  # Only show windows with titles
            windows_found.append((hwnd, title))
    return True

EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
user32.EnumWindows(EnumWindowsProc(enum_windows_callback), 0)

print("="*80)
print("📋 ALL VISIBLE WINDOWS")
print("="*80)
print()

# Filter for potentially relevant windows
relevant = [w for w in windows_found if any(keyword in w[1].lower() for keyword in ['iron', 'man', 'anakin', 'vader', 'acva', 'imva', 'jarvis', 'lumina', 'assistant', 'virtual'])]

if relevant:
    print(f"🔍 Found {len(relevant)} potentially relevant windows:")
    for hwnd, title in relevant:
        print(f"   HWND {hwnd}: {title}")
else:
    print("⚠️  No relevant windows found")
    print()
    print("📋 All visible windows (first 20):")
    for hwnd, title in windows_found[:20]:
        print(f"   HWND {hwnd}: {title}")

print()
print("="*80)
