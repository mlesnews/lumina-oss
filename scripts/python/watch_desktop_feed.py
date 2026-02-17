#!/usr/bin/env python3
"""
Watch Desktop Feed - Monitor what's actually on screen

Uses Manus desktop video feed to continuously watch and report
what's visible on the desktop, especially VA windows.

Tags: #MONITORING #DESKTOP #VIDEO_FEED #MANUS @JARVIS @LUMINA
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
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("WatchDesktopFeed")


def watch_desktop():
    """Continuously watch desktop and report what's visible"""
    try:
        from screen_capture_system import ScreenCaptureSystem
        from manus_rdp_screenshot_capture import MANUSRDPScreenshotCapture
    except ImportError as e:
        logger.error(f"❌ Required modules not available: {e}")
        return

    screen_cap = ScreenCaptureSystem()
    rdp_cap = MANUSRDPScreenshotCapture()

    print("=" * 80)
    print("👁️  WATCHING DESKTOP FEED")
    print("=" * 80)
    print()
    print("Monitoring desktop for VA windows...")
    print("Press Ctrl+C to stop")
    print()

    try:
        while True:
            # Capture screenshot
            screenshot = screen_cap.capture_screenshot()
            rdp_metadata = rdp_cap.capture_with_context("Monitoring desktop for VA windows", auto_capture=True)

            print(f"📸 Screenshot captured: {screenshot}")
            print(f"   RDP capture: {rdp_metadata.get('screenshot_path')}")
            print()

            # Check for running VA processes
            try:
                import psutil
                import os
                current_pid = os.getpid()

                va_processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['pid'] == current_pid:
                            continue
                        if not proc.info['name'] or 'python' not in proc.info['name'].lower():
                            continue
                        cmdline = proc.info.get('cmdline', [])
                        if not cmdline:
                            continue
                        cmdline_str = ' '.join(str(arg) for arg in cmdline).lower()

                        va_patterns = ['jarvis', 'kenny', 'imva', 'ultron', 'virtual_assistant', 'desktop_assistant']
                        if any(pattern in cmdline_str for pattern in va_patterns):
                            va_processes.append({
                                'pid': proc.info['pid'],
                                'cmdline': cmdline_str[:60]
                            })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

                if va_processes:
                    print(f"🔍 Found {len(va_processes)} VA process(es):")
                    for proc in va_processes:
                        print(f"   PID {proc['pid']}: {proc['cmdline']}")
                else:
                    print("   No VA processes found")
                print()

            except ImportError:
                print("   ⚠️  psutil not available - cannot check processes")
                print()

            time.sleep(5)  # Check every 5 seconds

    except KeyboardInterrupt:
        print("\n👋 Stopping desktop monitor...")
        print("✅ Stopped")


if __name__ == "__main__":
    try:
        watch_desktop()
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
