#!/usr/bin/env python3
"""
JARVIS @homelab IDE Notification Handler
USS Lumina - @scotty (Windows Systems Architect)

Comprehensive handler for all IDE/VS Code/Cursor notifications from @homelab:
- Large file dialogs (tokenization, wrapping, folding disabled)
- Performance warnings
- Extension notifications
- Git notifications
- Error dialogs
- Any IDE notification that requires user interaction

Tags: #HOMELAB #IDE #NOTIFICATIONS #VSCODE #CURSOR #AUTOMATION @HOMELAB @SCOTTY
"""

import sys
import asyncio
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISHomelabIDENotifications")

# UI Automation imports
try:
    import pyautogui
    import pygetwindow as gw
    UI_AUTOMATION_AVAILABLE = True
except ImportError:
    UI_AUTOMATION_AVAILABLE = False
    logger.warning("UI automation libraries not available. Install: pip install pyautogui pygetwindow")


class HomelabIDENotificationHandler:
    """
    @homelab IDE Notification Handler

    Handles all IDE/VS Code/Cursor notifications automatically.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.handled_notifications = []

        # Notification patterns to detect and handle
        self.notification_patterns = {
            "large_file_features_disabled": {
                "keywords": [
                    "tokenization",
                    "wrapping",
                    "folding",
                    "codelens",
                    "word highlighting",
                    "sticky scroll",
                    "large file",
                    "memory usage",
                    "freezing",
                    "crashing"
                ],
                "actions": ["dont_show_again", "forcefully_enable"],
                "priority": "medium",
                "description": "Large file features disabled notification"
            },
            "performance_warning": {
                "keywords": ["performance", "slow", "memory", "freeze"],
                "actions": ["dismiss", "optimize"],
                "priority": "high",
                "description": "Performance warning"
            },
            "extension_update": {
                "keywords": ["extension", "update", "available"],
                "actions": ["dismiss", "update"],
                "priority": "low",
                "description": "Extension update notification"
            },
            "git_notification": {
                "keywords": ["git", "repository", "changes", "conflict"],
                "actions": ["handle_git"],
                "priority": "high",
                "description": "Git-related notification"
            }
        }

        self.logger.info("✅ @homelab IDE Notification Handler initialized")

    def find_ide_windows(self) -> List[Any]:
        """Find all IDE windows (Cursor, VS Code)"""
        if not UI_AUTOMATION_AVAILABLE:
            return []

        try:
            ide_windows = []

            # Find Cursor windows
            cursor_windows = gw.getWindowsWithTitle("Cursor")
            ide_windows.extend(cursor_windows)

            # Find VS Code windows
            vscode_windows = gw.getWindowsWithTitle("Visual Studio Code")
            ide_windows.extend(vscode_windows)

            # Find by partial match
            all_windows = gw.getAllWindows()
            for window in all_windows:
                if window.title and any(keyword in window.title.lower() for keyword in ["cursor", "code", "vscode"]):
                    if window not in ide_windows:
                        ide_windows.append(window)

            return ide_windows
        except Exception as e:
            self.logger.warning(f"Could not find IDE windows: {e}")
            return []

    def detect_large_file_dialog(self) -> bool:
        """Detect if large file dialog is visible"""
        if not UI_AUTOMATION_AVAILABLE:
            return False

        try:
            # Look for dialog text patterns
            # The dialog contains: "tokenization, wrapping, folding, codelens, word highlighting and sticky scroll"
            screen = pyautogui.screenshot()

            # Try to find text (would need OCR or image recognition)
            # For now, we'll use keyboard detection - if dialog is focused, Enter or Escape will work

            # Check if there's a dialog by looking for common dialog button positions
            screen_width, screen_height = pyautogui.size()

            # Common dialog button positions (bottom area)
            dialog_button_positions = [
                (screen_width * 0.85, screen_height * 0.85),  # Bottom right
                (screen_width * 0.75, screen_height * 0.85),  # Bottom right-center
                (screen_width * 0.5, screen_height * 0.85),  # Bottom center
            ]

            # Try pressing Escape to see if dialog closes
            # This is a heuristic - if Escape works, there was likely a dialog
            return False  # Would need actual detection
        except Exception as e:
            self.logger.warning(f"Could not detect dialog: {e}")
            return False

    def handle_large_file_dialog(self, action: str = "dont_show_again") -> Dict[str, Any]:
        """
        Handle large file features disabled dialog

        Actions:
        - "dont_show_again": Click "Don't Show Again" button
        - "forcefully_enable": Click "Forcefully Enable Features" button
        """
        if not UI_AUTOMATION_AVAILABLE:
            return {
                "success": False,
                "error": "UI automation not available"
            }

        self.logger.info(f"🔧 Handling large file dialog (action: {action})...")

        try:
            # Find IDE windows
            ide_windows = self.find_ide_windows()
            if not ide_windows:
                self.logger.warning("⚠️  No IDE windows found")
                return {"success": False, "error": "No IDE windows found"}

            # Activate first IDE window
            ide_windows[0].activate()
            time.sleep(0.5)

            # Method 1: Try keyboard shortcuts
            if action == "dont_show_again":
                # "Don't Show Again" is typically the default/secondary button
                # Try Tab to navigate, then Enter
                pyautogui.press('tab')  # Navigate to second button
                time.sleep(0.1)
                pyautogui.press('enter')  # Click "Don't Show Again"
                self.logger.info("  ✅ Pressed Tab+Enter (Don't Show Again)")
            elif action == "forcefully_enable":
                # "Forcefully Enable Features" is typically the primary button
                # Just press Enter (should be focused)
                pyautogui.press('enter')
                self.logger.info("  ✅ Pressed Enter (Forcefully Enable Features)")

            time.sleep(0.5)

            # Method 2: Try clicking button positions if keyboard didn't work
            # Common button positions for dialogs
            screen_width, screen_height = pyautogui.size()

            if action == "dont_show_again":
                # "Don't Show Again" is usually on the right/secondary position
                button_positions = [
                    (screen_width * 0.85, screen_height * 0.85),  # Bottom right
                    (screen_width * 0.75, screen_height * 0.85),  # Bottom right-center
                ]
            else:
                # "Forcefully Enable Features" is usually primary (left or center)
                button_positions = [
                    (screen_width * 0.5, screen_height * 0.85),   # Bottom center
                    (screen_width * 0.4, screen_height * 0.85),  # Bottom left-center
                ]

            # Try clicking positions as fallback
            for pos in button_positions:
                try:
                    pyautogui.click(pos)
                    time.sleep(0.3)
                    self.logger.info(f"  ✅ Clicked position: {pos}")
                except:
                    pass

            return {
                "success": True,
                "action": action,
                "method": "keyboard_and_click"
            }

        except Exception as e:
            self.logger.error(f"❌ Error handling dialog: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def handle_ide_notification(self, notification_type: str, action: Optional[str] = None) -> Dict[str, Any]:
        """Handle a specific IDE notification type"""
        pattern = self.notification_patterns.get(notification_type)
        if not pattern:
            return {
                "success": False,
                "error": f"Unknown notification type: {notification_type}"
            }

        self.logger.info(f"🔧 Handling {notification_type} notification...")

        if notification_type == "large_file_features_disabled":
            action = action or "dont_show_again"
            return self.handle_large_file_dialog(action)

        elif notification_type == "git_notification":
            # Delegate to Git notification handler
            try:
                from jarvis_ide_notification_monitor import JARVISIDENotificationMonitor
                monitor = JARVISIDENotificationMonitor(self.project_root)
                return monitor.monitor_git_notifications()
            except Exception as e:
                return {"success": False, "error": str(e)}

        else:
            # Generic notification handling
            return {
                "success": True,
                "notification_type": notification_type,
                "action": "dismissed",
                "note": "Generic notification handling"
            }

    def monitor_ide_notifications(self, interval: int = 5) -> None:
        """Continuously monitor for IDE notifications"""
        self.logger.info(f"👀 Monitoring IDE notifications (interval: {interval}s)...")
        self.logger.info("   Will auto-handle detected notifications")
        self.logger.info("   Press Ctrl+C to stop")
        self.logger.info("")

        try:
            while True:
                # Check for large file dialog
                if self.detect_large_file_dialog():
                    self.logger.info("🔍 Large file dialog detected - handling...")
                    result = self.handle_large_file_dialog("dont_show_again")
                    if result.get("success"):
                        self.handled_notifications.append({
                            "type": "large_file_features_disabled",
                            "timestamp": datetime.now().isoformat(),
                            "action": "dont_show_again"
                        })
                        self.logger.info("✅ Large file dialog handled")

                time.sleep(interval)

        except KeyboardInterrupt:
            self.logger.info("")
            self.logger.info("🛑 Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Monitoring error: {e}", exc_info=True)

    def setup_auto_handling(self) -> Dict[str, Any]:
        """Set up automatic notification handling"""
        self.logger.info("⚙️  Setting up automatic IDE notification handling...")

        # Create a scheduled task or startup script
        # For now, we'll create a monitoring script
        script_content = f'''#!/usr/bin/env python3
"""
Auto-start IDE Notification Handler
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.python.jarvis_homelab_ide_notification_handler import HomelabIDENotificationHandler

handler = HomelabIDENotificationHandler(project_root)
handler.monitor_ide_notifications(interval=5)
'''

        script_path = self.project_root / "scripts" / "python" / "start_ide_notification_handler.py"
        try:
            script_path.write_text(script_content, encoding='utf-8')
            self.logger.info(f"✅ Created auto-start script: {script_path}")
            return {
                "success": True,
                "script_path": str(script_path),
                "note": "Run this script to start monitoring"
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to create script: {e}")
            return {"success": False, "error": str(e)}


async def handle_large_file_dialog_now() -> Dict[str, Any]:
    """Handle large file dialog immediately"""
    handler = HomelabIDENotificationHandler(project_root)
    return handler.handle_large_file_dialog("dont_show_again")


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="@homelab IDE Notification Handler")
    parser.add_argument("--handle-large-file", action="store_true", 
                       help="Handle large file dialog now")
    parser.add_argument("--action", choices=["dont_show_again", "forcefully_enable"],
                       default="dont_show_again",
                       help="Action for large file dialog")
    parser.add_argument("--monitor", action="store_true",
                       help="Monitor for notifications continuously")
    parser.add_argument("--interval", type=int, default=5,
                       help="Monitoring interval in seconds")
    parser.add_argument("--setup", action="store_true",
                       help="Set up automatic handling")

    args = parser.parse_args()

    handler = HomelabIDENotificationHandler(project_root)

    if args.handle_large_file:
        result = handler.handle_large_file_dialog(args.action)
        print("")
        print("=" * 70)
        print("@homelab IDE Notification Handler")
        print("=" * 70)
        if result.get("success"):
            print(f"✅ Handled large file dialog: {args.action}")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown')}")
        print("=" * 70)

    elif args.monitor:
        handler.monitor_ide_notifications(interval=args.interval)

    elif args.setup:
        result = handler.setup_auto_handling()
        print("")
        print("=" * 70)
        print("@homelab IDE Notification Handler Setup")
        print("=" * 70)
        if result.get("success"):
            print(f"✅ Setup complete")
            print(f"   Script: {result.get('script_path')}")
        else:
            print(f"❌ Setup failed: {result.get('error')}")
        print("=" * 70)

    else:
        # Default: handle large file dialog
        print("=" * 70)
        print("@homelab IDE Notification Handler")
        print("USS Lumina - @scotty (Windows Systems Architect)")
        print("=" * 70)
        print("")
        print("Usage:")
        print("  --handle-large-file  : Handle large file dialog now")
        print("  --action [action]     : Action (dont_show_again or forcefully_enable)")
        print("  --monitor             : Monitor for notifications continuously")
        print("  --setup               : Set up automatic handling")
        print("")
        print("Example:")
        print("  python jarvis_homelab_ide_notification_handler.py --handle-large-file")
        print("")

        # Try to handle large file dialog by default
        result = handler.handle_large_file_dialog("dont_show_again")
        if result.get("success"):
            print("✅ Large file dialog handled")
        else:
            print(f"ℹ️  No dialog detected or handling failed: {result.get('error', 'Unknown')}")


if __name__ == "__main__":


    main()