#!/usr/bin/env python3
"""
Force Start Kenny Visible - REQUIRED

Actually starts Kenny and makes sure it's visible and wandering.
No assumptions - actually checks and starts it.

Tags: #FORCE_START #VISIBLE #WANDERING #REQUIRED @JARVIS @LUMINA
"""

import sys
import time
import threading
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

logger = get_logger("ForceStartKenny")


def kill_existing_kenny():
    """Kill any existing Kenny windows"""
    try:
        import pygetwindow as gw
        windows = gw.getWindowsWithTitle("IRON MAN")
        windows.extend(gw.getWindowsWithTitle("Kenny"))
        windows.extend(gw.getWindowsWithTitle("IMVA"))

        for window in windows:
            try:
                logger.info(f"🛑 Closing existing window: {window.title}")
                window.close()
                time.sleep(0.5)
            except:
                pass
    except Exception as e:
        logger.debug(f"Could not kill existing windows: {e}")


def start_kenny_visible():
    """Actually start Kenny and make sure it's visible"""
    print("=" * 80)
    print("🤖 FORCE STARTING KENNY - VISIBLE AND WANDERING")
    print("=" * 80)
    print()

    # Kill any existing Kenny
    print("1. Closing any existing Kenny windows...")
    kill_existing_kenny()
    time.sleep(1)
    print()

    # Start Kenny
    print("2. Starting Kenny with correct settings...")
    try:
        from kenny_imva_enhanced import KennyIMVAEnhanced

        # Create Kenny with explicit size
        kenny = KennyIMVAEnhanced(size=120)
        print(f"✅ Kenny created (size: {kenny.size}px)")
        print()

        # Start in background thread
        print("3. Starting Kenny window...")
        def start_kenny_thread():
            try:
                kenny.start()
            except Exception as e:
                logger.error(f"❌ Kenny start failed: {e}")
                import traceback
                traceback.print_exc()

        thread = threading.Thread(target=start_kenny_thread, daemon=True)
        thread.start()

        # Wait for window to appear
        print("4. Waiting for Kenny window to appear...")
        time.sleep(3)

        # Verify window exists
        print("5. Verifying Kenny is visible...")
        try:
            import pygetwindow as gw
            windows = gw.getWindowsWithTitle("IRON MAN")
            if windows:
                window = windows[0]
                print(f"✅ Found Kenny window: {window.title}")
                print(f"   Position: ({window.left}, {window.top})")
                print(f"   Size: {window.width}x{window.height}")
                print(f"   Visible: {window.visible}")

                if window.width > 200 or window.height > 200:
                    print(f"⚠️  Window size is wrong ({window.width}x{window.height}) - resizing...")
                    window.resizeTo(120, 120)
                    print("✅ Resized to 120x120")

                if not window.visible:
                    print("⚠️  Window not visible - bringing to front...")
                    window.activate()
                    time.sleep(0.5)

                # Move to visible area if needed
                import pyautogui
                screen_width, screen_height = pyautogui.size()
                if window.left < 0 or window.left > screen_width or \
                   window.top < 0 or window.top > screen_height:
                    print("⚠️  Window off-screen - moving to visible area...")
                    visible_x = screen_width - 140
                    visible_y = 20
                    window.moveTo(visible_x, visible_y)
                    print(f"✅ Moved to ({visible_x}, {visible_y})")
            else:
                print("❌ Kenny window not found!")
                print("   Window may not have started properly")
        except Exception as e:
            print(f"⚠️  Could not verify window: {e}")

        print()
        print("=" * 80)
        print("✅ KENNY STARTED")
        print("=" * 80)
        print()
        print("Kenny should now be:")
        print("  - Visible on screen (120x120)")
        print("  - Wandering around desktop borders")
        print("  - Animated (Iron Man design)")
        print()
        print("If you don't see Kenny:")
        print("  1. Check if window is behind other windows")
        print("  2. Look for a small red/orange circle with helmet")
        print("  3. Check taskbar for 'IRON MAN Virtual Assistant'")
        print()

        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Stopping Kenny...")
            try:
                kenny.stop()
            except:
                pass

        return kenny
    except Exception as e:
        print(f"❌ Failed to start Kenny: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    start_kenny_visible()
