#!/usr/bin/env python3
"""
Bring VAs to Front - Make Windows Visible

Brings VA windows to the front and ensures they're visible on desktop.
Uses Windows API to find and activate VA windows.

Tags: #VAS #WINDOWS #VISIBILITY #DESKTOP @JARVIS @TEAM
"""

import sys
import ctypes
from ctypes import wintypes
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("VAsBringToFront")

# Windows API constants
HWND_TOP = 0
SW_RESTORE = 9
SW_SHOW = 5
SW_SHOWMAXIMIZED = 3


class VAsBringToFront:
    """
    Bring VA windows to front and make them visible
    """

    def __init__(self):
        """Initialize window finder"""
        if sys.platform != "win32":
            logger.warning("This script is designed for Windows")
            return

        # Windows API functions
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32

        logger.info("✅ VAs Bring To Front initialized")

    def find_window_by_title(self, title_substring: str) -> Optional[int]:
        """Find window handle by title substring"""
        def enum_windows_callback(hwnd, windows):
            if self.user32.IsWindowVisible(hwnd):
                window_title = ctypes.create_unicode_buffer(512)
                self.user32.GetWindowTextW(hwnd, window_title, 512)
                if title_substring.lower() in window_title.value.lower():
                    windows.append((hwnd, window_title.value))
            return True

        windows = []
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, ctypes.POINTER(ctypes.c_int))
        self.user32.EnumWindows(EnumWindowsProc(enum_windows_callback), ctypes.byref(ctypes.c_int()))

        # Use the callback properly
        windows_found = []
        def callback(hwnd, lParam):
            if self.user32.IsWindowVisible(hwnd):
                buffer = ctypes.create_unicode_buffer(512)
                self.user32.GetWindowTextW(hwnd, buffer, 512)
                if title_substring.lower() in buffer.value.lower():
                    windows_found.append((hwnd, buffer.value))
            return True

        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        self.user32.EnumWindows(EnumWindowsProc(callback), 0)

        if windows_found:
            return windows_found[0][0]
        return None

    def bring_window_to_front(self, hwnd: int) -> bool:
        """Bring window to front"""
        try:
            # Restore if minimized
            self.user32.ShowWindow(hwnd, SW_RESTORE)

            # Bring to front
            self.user32.SetForegroundWindow(hwnd)
            self.user32.BringWindowToTop(hwnd)
            self.user32.SetActiveWindow(hwnd)

            # Set window position to top
            self.user32.SetWindowPos(hwnd, HWND_TOP, 0, 0, 0, 0, 0x0001 | 0x0002)  # SWP_NOMOVE | SWP_NOSIZE

            return True
        except Exception as e:
            logger.error(f"Error bringing window to front: {e}")
            return False

    def bring_all_vas_to_front(self) -> Dict[str, Any]:
        """Bring all VA windows to front"""
        logger.info("="*80)
        logger.info("👁️  Bringing All VA Windows to Front")
        logger.info("="*80)

        result = {
            "vas_found": [],
            "vas_brought_to_front": [],
            "vas_not_found": [],
            "success": True
        }

        # VA window titles to search for
        va_titles = [
            ("IMVA", "IRON MAN Virtual Assistant"),
            ("IMVA", "IRON MAN Virtual Assistant - LUMINA"),
            ("ACVA_REAL", "ASUSMascot"),  # Real ASUS Armoury Crate VA
            ("ACVA_REAL", "Virtual Pet"),  # Real ASUS ACVA process name
            ("ACVA", "Anakin/Vader Combat VA"),
            ("ACVA", "Anakin/Vader Combat VA - LUMINA"),
            ("ACVA", "ACVA"),
            ("JARVIS_VA", "JARVIS")
        ]

        logger.info("\n🔍 Searching for VA windows...")
        for va_id, title_substring in va_titles:
            logger.info(f"   Searching for {va_id} ({title_substring})...")

            hwnd = self.find_window_by_title(title_substring)
            if hwnd:
                result["vas_found"].append(va_id)
                logger.info(f"   ✅ Found {va_id} window (HWND: {hwnd})")

                if self.bring_window_to_front(hwnd):
                    result["vas_brought_to_front"].append(va_id)
                    logger.info(f"   ✅ Brought {va_id} to front")
                else:
                    logger.warning(f"   ⚠️  Failed to bring {va_id} to front")
            else:
                result["vas_not_found"].append(va_id)
                logger.warning(f"   ⚠️  {va_id} window not found")

        logger.info("="*80)
        logger.info("✅ Window Management Complete")
        logger.info(f"   VAs Found: {len(result['vas_found'])}")
        logger.info(f"   VAs Brought to Front: {len(result['vas_brought_to_front'])}")
        logger.info(f"   VAs Not Found: {len(result['vas_not_found'])}")
        logger.info("="*80)

        return result


if __name__ == "__main__":
    if sys.platform != "win32":
        print("❌ This script requires Windows")
        sys.exit(1)

    print("\n" + "="*80)
    print("👁️  Bringing All VA Windows to Front")
    print("="*80 + "\n")

    bringer = VAsBringToFront()
    result = bringer.bring_all_vas_to_front()

    print("\n" + "="*80)
    print("📊 RESULTS")
    print("="*80)
    print(f"VAs Found: {len(result['vas_found'])}")
    for va_id in result['vas_found']:
        print(f"   ✅ {va_id}")

    print(f"\nVAs Brought to Front: {len(result['vas_brought_to_front'])}")
    for va_id in result['vas_brought_to_front']:
        print(f"   👁️  {va_id}")

    if result.get('vas_not_found'):
        print(f"\nVAs Not Found: {len(result['vas_not_found'])}")
        for va_id in result['vas_not_found']:
            print(f"   ⚠️  {va_id}")

    print("\n✅ Complete")
    print("="*80 + "\n")
