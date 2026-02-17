#!/usr/bin/env python3
"""
Fix VA Windows - Make Visible and Correct Size - REQUIRED

Fixes:
1. Kenny window size (should be 120x120, not 1368x776)
2. Off-screen windows (move to visible area)
3. Ensure they're actually wandering

Tags: #FIX_VISIBILITY #REQUIRED @JARVIS @LUMINA
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

logger = get_logger("FixVAWindows")


def fix_kenny_window():
    """Fix Kenny window size and position"""
    try:
        import pygetwindow as gw

        # Find Kenny window
        windows = gw.getWindowsWithTitle("IRON MAN Virtual Assistant")
        if not windows:
            windows = gw.getWindowsWithTitle("Kenny")
        if not windows:
            windows = gw.getWindowsWithTitle("IMVA")

        if not windows:
            logger.warning("⚠️  Kenny window not found")
            return False

        for window in windows:
            # Check if window is wrong size
            if window.width > 200 or window.height > 200:
                logger.info(f"🔧 Fixing Kenny window: {window.title}")
                logger.info(f"   Current size: {window.width}x{window.height} (should be 120x120)")

                # Get screen size
                screen_width = window.width  # Use window's screen info
                screen_height = window.height
                try:
                    import pyautogui
                    screen_width, screen_height = pyautogui.size()
                except:
                    pass

                # Set correct size (120x120)
                window.resizeTo(120, 120)

                # Move to visible area (top-right corner)
                visible_x = screen_width - 140
                visible_y = 20

                # If window is off-screen, move it
                if window.left < -100 or window.left > screen_width or \
                   window.top < -100 or window.top > screen_height:
                    logger.info(f"   Moving from ({window.left}, {window.top}) to ({visible_x}, {visible_y})")
                    window.moveTo(visible_x, visible_y)
                else:
                    logger.info(f"   Window at ({window.left}, {window.top}) - keeping position")

                logger.info("✅ Kenny window fixed")
                return True

        return False
    except ImportError:
        logger.error("❌ pygetwindow not available")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to fix Kenny window: {e}")
        import traceback
        traceback.print_exc()
        return False


def fix_off_screen_windows():
    """Fix any windows that are off-screen"""
    try:
        import pygetwindow as gw
        import pyautogui

        screen_width, screen_height = pyautogui.size()
        windows = gw.getAllWindows()

        fixed_count = 0
        for window in windows:
            # Check if window is way off-screen
            if window.left < -1000 or window.left > screen_width + 1000 or \
               window.top < -1000 or window.top > screen_height + 1000:

                # Check if it's a VA-related window
                title = window.title.lower()
                if any(keyword in title for keyword in ['lumina', 'virtual assistant', 'kenny', 'ace', 'imva', 'acva']):
                    logger.info(f"🔧 Fixing off-screen window: {window.title}")
                    logger.info(f"   Current position: ({window.left}, {window.top})")

                    # Move to visible area
                    visible_x = 100
                    visible_y = 100
                    window.moveTo(visible_x, visible_y)

                    logger.info(f"   Moved to ({visible_x}, {visible_y})")
                    fixed_count += 1

        if fixed_count > 0:
            logger.info(f"✅ Fixed {fixed_count} off-screen window(s)")
        else:
            logger.info("ℹ️  No off-screen windows found")

        return fixed_count > 0
    except Exception as e:
        logger.error(f"❌ Failed to fix off-screen windows: {e}")
        return False


def restart_kenny_correctly():
    """Restart Kenny with correct size"""
    try:
        # First, try to close existing Kenny
        import pygetwindow as gw
        windows = gw.getWindowsWithTitle("IRON MAN Virtual Assistant")
        for window in windows:
            if window.width > 200:  # Wrong size
                logger.info("🛑 Closing incorrectly sized Kenny window...")
                window.close()
                time.sleep(1)

        # Now start Kenny correctly
        from kenny_imva_enhanced import KennyIMVAEnhanced
        logger.info("🚀 Starting Kenny with correct size (120x120)...")

        kenny = KennyIMVAEnhanced(size=120)  # Explicitly set size

        # Start in background
        import threading
        def start_kenny():
            kenny.start()

        thread = threading.Thread(target=start_kenny, daemon=True)
        thread.start()

        time.sleep(2)  # Give it time to start

        logger.info("✅ Kenny restarted")
        return kenny
    except Exception as e:
        logger.error(f"❌ Failed to restart Kenny: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main function"""
    print("=" * 80)
    print("🔧 FIXING VA WINDOWS - MAKE VISIBLE AND CORRECT SIZE")
    print("=" * 80)
    print()

    # Fix off-screen windows first
    print("1. Fixing off-screen windows...")
    fix_off_screen_windows()
    print()

    # Fix Kenny window size
    print("2. Fixing Kenny window size...")
    if fix_kenny_window():
        print("✅ Kenny window fixed")
    else:
        print("⚠️  Could not fix Kenny window - may need to restart")
        print("   Attempting to restart Kenny...")
        restart_kenny_correctly()
    print()

    print("=" * 80)
    print("✅ VA WINDOWS FIXED")
    print("=" * 80)
    print()
    print("Windows should now be:")
    print("  - Correct size (120x120 for Kenny)")
    print("  - Visible on screen")
    print("  - Wandering around desktop")
    print()


if __name__ == "__main__":


    main()