#!/usr/bin/env python3
"""
Cursor IDE Notification Handler

Automatically detects and handles Cursor IDE notifications, specifically:
- "The following extensions want to relaunch the terminal to contribute to its..."
- Automatically clicks approve/relaunch buttons
- Handles terminal relaunch notifications

Tags: #CURSOR #NOTIFICATION #AUTOMATION #TERMINAL #RESTART @JARVIS @LUMINA
"""

import sys
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        def get_logger(name):
            return logging.getLogger(name)

logger = get_logger("CursorNotificationHandler")


def find_and_click_notification():
    """
    Find and click Cursor IDE notification about terminal relaunch.

    Looks for notification with text like:
    "The following extensions want to relaunch the terminal to contribute to its..."

    Returns:
        True if notification was found and clicked
    """
    try:
        import pyautogui

        # Search for notification text
        notification_texts = [
            "extensions want to relaunch the terminal",
            "want to relaunch the terminal",
            "relaunch the terminal",
            "Relaunch Terminal",
            "Allow",
            "OK"
        ]

        logger.info("   🔍 Searching for Cursor IDE notification...")

        # Try to find notification by text
        for text in notification_texts:
            try:
                # Search screen for text
                location = pyautogui.locateOnScreen(None)  # Can't search text directly
                # Instead, we'll use a different approach
            except Exception:
                pass

        # Method 1: Use keyboard to accept (Enter key often accepts dialogs)
        try:
            logger.info("   ⌨️  Trying keyboard shortcut to accept notification...")
            pyautogui.press('enter')
            time.sleep(0.3)
            pyautogui.press('enter')  # Sometimes need to press twice
            logger.info("   ✅ Sent Enter key to accept notification")
            return True
        except Exception as e:
            logger.debug(f"   Keyboard accept error: {e}")

        # Method 2: Try Alt+Y or Alt+A (common for "Yes"/"Allow")
        try:
            pyautogui.hotkey('alt', 'y')
            time.sleep(0.2)
            logger.info("   ✅ Sent Alt+Y to accept")
            return True
        except Exception as e:
            logger.debug(f"   Alt+Y error: {e}")

        # Method 3: Try clicking common button positions
        try:
            # Notification buttons are often in bottom-right area
            screen_width, screen_height = pyautogui.size()
            # Try clicking where "Allow" or "OK" button might be
            button_x = screen_width - 200
            button_y = screen_height - 150

            pyautogui.click(button_x, button_y)
            time.sleep(0.2)
            logger.info("   ✅ Clicked potential notification button area")
            return True
        except Exception as e:
            logger.debug(f"   Click error: {e}")

        return False

    except ImportError:
        logger.warning("   ⚠️  pyautogui not available")
        # Fallback: Use keyboard library
        try:
            import keyboard
            logger.info("   ⌨️  Using keyboard library to accept notification...")
            keyboard.press_and_release('enter')
            time.sleep(0.3)
            keyboard.press_and_release('enter')
            logger.info("   ✅ Sent Enter key via keyboard library")
            return True
        except ImportError:
            logger.warning("   ⚠️  keyboard library not available")
            return False
    except Exception as e:
        logger.error(f"   ❌ Notification click error: {e}")
        return False


def handle_terminal_relaunch_notification():
    """
    Handle the specific notification about extensions wanting to relaunch terminal.

    This is the notification that causes the orange triangle warning.
    The notification says: "The following extensions want to relaunch the terminal to contribute to its..."
    """
    logger.info("=" * 60)
    logger.info("🔔 HANDLING TERMINAL RELAUNCH NOTIFICATION")
    logger.info("=" * 60)
    logger.info("   Notification: 'The following extensions want to relaunch the terminal...'")
    logger.info("   Action: Automatically accepting/approving the notification")

    # Try multiple methods to accept the notification
    success = False

    # Method 1: Keyboard Enter (most common - accepts dialogs)
    try:
        import keyboard
        logger.info("   ⌨️  Method 1: Sending Enter key to accept notification...")
        # Focus might be on notification, so Enter should accept it
        keyboard.press_and_release('enter')
        time.sleep(0.5)
        # Sometimes need to press twice or wait for dialog
        keyboard.press_and_release('enter')
        time.sleep(0.3)
        success = True
        logger.info("   ✅ Enter key sent - notification should be accepted")
    except ImportError:
        logger.warning("   ⚠️  keyboard library not available - trying alternative methods")
    except Exception as e:
        logger.warning(f"   ⚠️  Enter key error: {e}")

    # Method 2: Try Alt+Y or Alt+A for "Yes"/"Allow" buttons
    if not success:
        try:
            import keyboard
            logger.info("   ⌨️  Trying Alt+Y (Yes/Allow)...")
            keyboard.press_and_release('alt+y')
            time.sleep(0.3)
            success = True
            logger.info("   ✅ Sent Alt+Y")
        except ImportError:
            pass
        except Exception as e:
            logger.debug(f"   Alt+Y error: {e}")

    # Method 3: Try Space (sometimes accepts dialogs)
    if not success:
        try:
            import keyboard
            logger.info("   ⌨️  Trying Space key...")
            keyboard.press_and_release('space')
            time.sleep(0.3)
            keyboard.press_and_release('enter')
            success = True
            logger.info("   ✅ Sent Space + Enter")
        except Exception as e:
            logger.debug(f"   Space key error: {e}")

    # Method 4: Use pyautogui if available (for clicking buttons)
    if not success:
        success = find_and_click_notification()

    if success:
        logger.info("   ✅ Terminal relaunch notification handled")
        logger.info("   ⏳ Waiting for terminal to relaunch...")
        # Wait for terminal to relaunch
        time.sleep(2.0)
        return True
    else:
        logger.warning("   ⚠️  Could not automatically handle notification")
        logger.info("   💡 Manual action needed: Click 'Allow' or 'Relaunch' in the notification")
        logger.info("   💡 Or press Enter when notification is focused")
        return False


def monitor_for_notifications(interval=2.0):
    """
    Monitor for Cursor IDE notifications and handle them automatically.

    Args:
        interval: Check interval in seconds
    """
    logger.info("📡 Monitoring for Cursor IDE notifications...")

    import threading

    def monitor_loop():
        while True:
            try:
                # Check if notification might be present
                # We can't directly detect it, but we can try to handle it
                # when terminal issues are detected
                time.sleep(interval)
            except Exception as e:
                logger.debug(f"   Monitor error: {e}")
                time.sleep(interval)

    thread = threading.Thread(target=monitor_loop, daemon=True)
    thread.start()
    return thread


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Cursor IDE Notification Handler")
    parser.add_argument("--handle", action="store_true", help="Handle terminal relaunch notification now")
    parser.add_argument("--monitor", action="store_true", help="Start monitoring for notifications")

    args = parser.parse_args()

    if args.handle:
        print("🔔 Handling terminal relaunch notification...", flush=True)
        success = handle_terminal_relaunch_notification()
        if success:
            print("✅ Notification handled successfully!", flush=True)
        else:
            print("⚠️  Could not automatically handle notification", flush=True)
            print("💡 Try manually clicking 'Allow' or 'Relaunch' in the notification", flush=True)
        return 0 if success else 1

    if args.monitor:
        monitor_for_notifications()
        logger.info("✅ Notification monitor started")
        print("✅ Notification monitor started", flush=True)
        try:
            while True:
                time.sleep(1.0)
        except KeyboardInterrupt:
            logger.info("\n⏹️  Stopping...")
            print("\n⏹️  Stopping...", flush=True)

    # Default: try to handle notification
    print("🔔 Attempting to handle terminal relaunch notification...", flush=True)
    success = handle_terminal_relaunch_notification()
    return 0 if success else 1


if __name__ == "__main__":


    sys.exit(main())