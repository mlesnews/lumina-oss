#!/usr/bin/env python3
"""
NEO Browser Windows-Level Automation
Uses Windows APIs for direct control (Admin/Engineer access)
#JARVIS #NEO #WINDOWS #AUTOMATION #ADMIN
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
import time
import subprocess
import os
import ctypes
from ctypes import wintypes

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("NEOWindowsAutomation")

# Windows API constants
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_CHAR = 0x0102
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
VK_RETURN = 0x0D
VK_TAB = 0x09
VK_ESCAPE = 0x1B

# Windows API functions
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

class NEOWindowsAutomation:
    """
    Windows-level automation for NEO Browser
    Uses Windows APIs for direct control
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.neo_exe = Path(os.environ.get("LOCALAPPDATA", "")) / "Neo" / "Application" / "neo.exe"
        self.process: Optional[subprocess.Popen] = None
        self.hwnd = None

        if not self.neo_exe.exists():
            raise FileNotFoundError(f"NEO browser not found at: {self.neo_exe}")

        logger.info("✅ NEO Windows Automation initialized (Admin/Engineer access)")

    def _kill_existing_neo_processes(self) -> None:
        """Kill any existing NEO browser processes to prevent multiple instances"""
        try:
            import psutil
            killed = 0
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if 'neo' in proc.info['name'].lower() or 'neo.exe' in proc.info['name'].lower():
                        logger.warning(f"⚠️  Killing existing NEO process: PID {proc.info['pid']}")
                        proc.kill()
                        killed += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            if killed > 0:
                logger.info(f"   ✅ Killed {killed} existing NEO process(es) to prevent duplicates")
                time.sleep(2)  # Wait for processes to terminate
        except ImportError:
            logger.warning("⚠️  psutil not available, cannot kill existing processes")
            # Fallback: Use taskkill command
            try:
                subprocess.run(['taskkill', '/F', '/IM', 'neo.exe'], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
                logger.info("   ✅ Used taskkill to terminate existing NEO processes")
                time.sleep(2)
            except Exception:
                pass
        except Exception as e:
            logger.debug(f"Error killing existing processes: {e}")

    def find_window_by_title(self, title: str, partial: bool = True) -> Optional[int]:
        """Find window by title using Windows API"""
        def enum_windows_callback(hwnd, lParam):
            window_title = ctypes.create_unicode_buffer(512)
            user32.GetWindowTextW(hwnd, window_title, 512)
            title_text = window_title.value

            if partial:
                if title.lower() in title_text.lower():
                    lParam.append(hwnd)
            else:
                if title_text == title:
                    lParam.append(hwnd)
            return True

        windows = []
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        user32.EnumWindows(EnumWindowsProc(enum_windows_callback), windows)

        return windows[0] if windows else None

    def find_neo_window(self) -> Optional[int]:
        """Find NEO browser window"""
        # Try multiple possible window titles
        titles = ["Neo", "NEO", "neo.exe", "Browser"]
        for title in titles:
            hwnd = self.find_window_by_title(title, partial=True)
            if hwnd:
                logger.info(f"✅ Found NEO window: {title}")
                return hwnd
        return None

    def launch(self, url: Optional[str] = None) -> bool:
        """Launch NEO browser - SINGLE INSTANCE ONLY"""
        try:
            # CRITICAL: Kill any existing NEO browser processes FIRST
            self._kill_existing_neo_processes()

            args = [str(self.neo_exe)]
            if url:
                args.append(url)

            logger.info("🚀 Launching NEO browser (SINGLE INSTANCE - killing duplicates first)...")
            self.process = subprocess.Popen(
                args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # Wait for window to appear
            max_wait = 10
            for i in range(max_wait):
                time.sleep(1)
                self.hwnd = self.find_neo_window()
                if self.hwnd:
                    logger.info(f"✅ NEO browser window found (HWND: {self.hwnd})")
                    # Dismiss "Restore All Pages" popup
                    self._dismiss_restore_pages_popup()
                    return True

            logger.warning("⚠️  NEO browser launched but window not found")
            return False
        except Exception as e:
            logger.error(f"Error launching NEO browser: {e}")
            return False

    def _dismiss_restore_pages_popup(self) -> None:
        """Dismiss 'Restore All Pages' popup using Windows API"""
        if not self.hwnd:
            return

        try:
            # Bring window to foreground
            self.bring_to_foreground()
            time.sleep(0.5)

            # Send Escape key to dismiss popup
            VK_ESCAPE = 0x1B
            WM_KEYDOWN = 0x0100
            WM_KEYUP = 0x0101

            user32.PostMessageW(self.hwnd, WM_KEYDOWN, VK_ESCAPE, 0)
            time.sleep(0.1)
            user32.PostMessageW(self.hwnd, WM_KEYUP, VK_ESCAPE, 0)

            logger.info("   ✅ Sent Escape key to dismiss 'Restore All Pages' popup")
            time.sleep(0.5)
        except Exception as e:
            logger.debug(f"   Error dismissing popup: {e}")

        except Exception as e:
            logger.error(f"❌ Failed to launch NEO: {e}")
            return False

    def bring_to_foreground(self) -> bool:
        """Bring window to foreground"""
        if not self.hwnd:
            self.hwnd = self.find_neo_window()

        if not self.hwnd:
            return False

        try:
            # Show window if minimized
            user32.ShowWindow(self.hwnd, 9)  # SW_RESTORE
            # Bring to foreground
            user32.SetForegroundWindow(self.hwnd)
            user32.BringWindowToTop(self.hwnd)
            return True
        except Exception as e:
            logger.debug(f"Error bringing window to foreground: {e}")
            return False

    def send_key(self, key_code: int, modifiers: int = 0) -> bool:
        """Send key press using Windows API"""
        if not self.hwnd:
            if not self.bring_to_foreground():
                return False

        try:
            # Post key messages
            user32.PostMessageW(self.hwnd, WM_KEYDOWN, key_code, 0)
            user32.PostMessageW(self.hwnd, WM_KEYUP, key_code, 0)
            return True
        except Exception as e:
            logger.debug(f"Error sending key: {e}")
            return False

    def send_text(self, text: str) -> bool:
        """Send text using Windows API"""
        if not self.hwnd:
            if not self.bring_to_foreground():
                return False

        try:
            for char in text:
                char_code = ord(char)
                user32.PostMessageW(self.hwnd, WM_CHAR, char_code, 0)
                time.sleep(0.01)  # Small delay between characters
            return True
        except Exception as e:
            logger.debug(f"Error sending text: {e}")
            return False

    def click_at(self, x: int, y: int) -> bool:
        """Click at coordinates using Windows API"""
        if not self.hwnd:
            if not self.bring_to_foreground():
                return False

        try:
            # Convert screen coordinates to window coordinates
            point = wintypes.POINT(x, y)
            user32.ScreenToClient(self.hwnd, ctypes.byref(point))

            # Calculate lParam for PostMessage
            lParam = point.y << 16 | point.x

            # Post click messages
            user32.PostMessageW(self.hwnd, WM_LBUTTONDOWN, 0, lParam)
            user32.PostMessageW(self.hwnd, WM_LBUTTONUP, 0, lParam)
            return True
        except Exception as e:
            logger.debug(f"Error clicking: {e}")
            return False

    def get_window_rect(self) -> Optional[Dict[str, int]]:
        """Get window rectangle"""
        if not self.hwnd:
            return None

        try:
            rect = wintypes.RECT()
            user32.GetWindowRect(self.hwnd, ctypes.byref(rect))
            return {
                "left": rect.left,
                "top": rect.top,
                "right": rect.right,
                "bottom": rect.bottom,
                "width": rect.right - rect.left,
                "height": rect.bottom - rect.top
            }
        except Exception as e:
            logger.debug(f"Error getting window rect: {e}")
            return None

    def close(self):
        """Close browser"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                logger.info("🔒 NEO browser closed")
            except subprocess.TimeoutExpired:
                self.process.kill()
            except Exception as e:
                logger.error(f"Error closing browser: {e}")
            finally:
                self.process = None
                self.hwnd = None

    def is_running(self) -> bool:
        """Check if browser is running"""
        if self.process:
            return self.process.poll() is None
        return False


# Windows API type definitions
def setup_windows_types():
    """Setup Windows API type definitions"""
    try:
        # EnumWindows callback
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

        # Get function signatures
        user32.EnumWindows.argtypes = [EnumWindowsProc, wintypes.LPARAM]
        user32.EnumWindows.restype = ctypes.c_bool

        user32.GetWindowTextW.argtypes = [wintypes.HWND, ctypes.c_wchar_p, ctypes.c_int]
        user32.GetWindowTextW.restype = ctypes.c_int

        user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
        user32.ShowWindow.restype = ctypes.c_bool

        user32.SetForegroundWindow.argtypes = [wintypes.HWND]
        user32.SetForegroundWindow.restype = ctypes.c_bool

        user32.BringWindowToTop.argtypes = [wintypes.HWND]
        user32.BringWindowToTop.restype = ctypes.c_bool

        user32.PostMessageW.argtypes = [wintypes.HWND, ctypes.c_uint, wintypes.WPARAM, wintypes.LPARAM]
        user32.PostMessageW.restype = ctypes.c_bool

        user32.ScreenToClient.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.POINT)]
        user32.ScreenToClient.restype = ctypes.c_bool

        user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
        user32.GetWindowRect.restype = ctypes.c_bool

    except Exception as e:
        logger.warning(f"Could not setup all Windows API types: {e}")


# Setup Windows types on import
setup_windows_types()


def main():
    """Test Windows automation"""
    import argparse

    parser = argparse.ArgumentParser(description="NEO Browser Windows Automation")
    parser.add_argument("--url", help="URL to navigate to")
    parser.add_argument("--test", action="store_true", help="Run test automation")

    args = parser.parse_args()

    try:
        automation = NEOWindowsAutomation(project_root)

        if args.test:
            logger.info("🧪 Running test automation...")
            automation.launch(url="https://www.google.com")
            time.sleep(3)

            window_rect = automation.get_window_rect()
            if window_rect:
                logger.info(f"Window: {window_rect['width']}x{window_rect['height']} at ({window_rect['left']}, {window_rect['top']})")

            automation.close()
        elif args.url:
            automation.launch(url=args.url)
            time.sleep(10)  # Keep open
            automation.close()
        else:
            logger.info("✅ NEO Windows Automation ready")
            logger.info("   Use --url to navigate or --test to run test")

        return 0
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":


    sys.exit(main())