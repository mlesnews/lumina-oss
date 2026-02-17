#!/usr/bin/env python3
"""
Cursor IDE Footer Customization

Customizes Cursor IDE footer (VS Code based) to add:
- Prefix: (#/#) #ask-heap-stack (current/total numbers)
- Suffix: (N) #notifications [IDE-QUEUE]

Original footer: (X) #problems, /_\\ #warnings, (( i )) #information

Tags: #CURSOR_IDE #FOOTER #STATUSBAR #CUSTOMIZATION #ASK_HEAP_STACK #NOTIFICATIONS @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

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

logger = get_logger("CursorIDEFooter")


class AskHeapStackTracker:
    """Track ask-heap-stack current/total numbers"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "ask_heap_stack"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.data_file = self.data_dir / "ask_heap_stack.json"

        self.current = 0
        self.total = 0
        self._load_data()

    def _load_data(self):
        """Load ask-heap-stack data"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.current = data.get("current", 0)
                    self.total = data.get("total", 0)
            except Exception as e:
                logger.debug(f"Could not load ask-heap-stack data: {e}")

    def _save_data(self):
        """Save ask-heap-stack data"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump({
                    "current": self.current,
                    "total": self.total,
                    "updated_at": datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving ask-heap-stack data: {e}")

    def add_ask(self):
        """Add new ask to heap-stack"""
        self.current += 1
        self.total += 1
        self._save_data()

    def remove_ask(self):
        """Remove ask from heap-stack"""
        if self.current > 0:
            self.current -= 1
            self._save_data()

    def get_display(self) -> str:
        """Get display format: (#/#)"""
        return f"({self.current}/{self.total})"

    def reset_current(self):
        """Reset current count"""
        self.current = 0
        self._save_data()


class IDENotificationTracker:
    """Track IDE notifications for IDE-QUEUE"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "ide_notifications"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.data_file = self.data_dir / "notifications.json"

        self.notifications: list = []
        self._load_data()

    def _load_data(self):
        """Load notifications data"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.notifications = data.get("notifications", [])
            except Exception as e:
                logger.debug(f"Could not load notifications data: {e}")

    def _save_data(self):
        """Save notifications data"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump({
                    "notifications": self.notifications,
                    "count": len(self.notifications),
                    "updated_at": datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving notifications data: {e}")

    def add_notification(self, notification: Dict[str, Any]):
        """Add notification to IDE-QUEUE"""
        notification["id"] = f"notif_{int(datetime.now().timestamp())}"
        notification["timestamp"] = datetime.now().isoformat()
        self.notifications.append(notification)
        self._save_data()

    def remove_notification(self, notification_id: str):
        """Remove notification from IDE-QUEUE"""
        self.notifications = [n for n in self.notifications if n.get("id") != notification_id]
        self._save_data()

    def get_count(self) -> int:
        """Get notification count"""
        return len(self.notifications)

    def get_display(self) -> str:
        """Get display format: (N)"""
        count = self.get_count()
        return f"({count})" if count > 0 else "(0)"


class CursorIDEFooterCustomization:
    """
    Cursor IDE Footer Customization

    Customizes footer to add:
    - Prefix: (#/#) #ask-heap-stack
    - Suffix: (N) #notifications [IDE-QUEUE]
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize footer customization"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.cursor_dir = self.project_root / ".cursor"
        self.settings_file = self.cursor_dir / "settings.json"

        self.ask_tracker = AskHeapStackTracker(self.project_root)
        self.notification_tracker = IDENotificationTracker(self.project_root)

        logger.info("=" * 80)
        logger.info("🎨 CURSOR IDE FOOTER CUSTOMIZATION")
        logger.info("=" * 80)
        logger.info("   Prefix: (#/#) #ask-heap-stack")
        logger.info("   Suffix: (N) #notifications [IDE-QUEUE]")
        logger.info("=" * 80)

    def get_footer_config(self) -> Dict[str, Any]:
        """Get footer configuration for Cursor IDE settings"""
        ask_display = self.ask_tracker.get_display()
        notification_display = self.notification_tracker.get_display()

        return {
            "footer_prefix": f"{ask_display} #ask-heap-stack",
            "footer_suffix": f"{notification_display} #notifications [IDE-QUEUE]",
            "ask_heap_stack": {
                "current": self.ask_tracker.current,
                "total": self.ask_tracker.total,
                "display": ask_display
            },
            "notifications": {
                "count": self.notification_tracker.get_count(),
                "display": notification_display
            }
        }

    def update_settings(self):
        """Update Cursor IDE settings.json with footer customization"""
        try:
            # Load existing settings
            settings = {}
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)

            # Add footer customization
            footer_config = self.get_footer_config()

            # VS Code/Cursor status bar customization
            # Note: VS Code doesn't directly support custom footer text,
            # but we can use status bar contributions via extension or API

            # Store footer config in settings for reference
            settings["lumina.footer"] = footer_config

            # Save settings
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)

            logger.info("✅ Cursor IDE settings updated with footer customization")
            logger.info(f"   Prefix: {footer_config['footer_prefix']}")
            logger.info(f"   Suffix: {footer_config['footer_suffix']}")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to update settings: {e}")
            return False

    def get_footer_display(self) -> str:
        """Get complete footer display string"""
        ask_display = self.ask_tracker.get_display()
        notification_display = self.notification_tracker.get_display()

        # Original VS Code footer: (X) #problems, /_\ #warnings, (( i )) #information
        # Custom footer with prefix and suffix:
        footer = (
            f"{ask_display} #ask-heap-stack | "
            f"(X) #problems | "
            f"/_\\ #warnings | "
            f"(( i )) #information | "
            f"{notification_display} #notifications [IDE-QUEUE]"
        )

        return footer

    def add_ask(self):
        """Add ask to heap-stack"""
        self.ask_tracker.add_ask()
        logger.info(f"📝 Ask added to heap-stack: {self.ask_tracker.get_display()}")
        self.update_settings()  # Auto-update settings

    def remove_ask(self):
        """Remove ask from heap-stack"""
        self.ask_tracker.remove_ask()
        logger.info(f"📝 Ask removed from heap-stack: {self.ask_tracker.get_display()}")
        self.update_settings()  # Auto-update settings

    def sync_with_unified_queue(self):
        """Sync ask-heap-stack and notifications with unified queue"""
        try:
            from unified_queue_adapter import UnifiedQueueAdapter, QueueItemType

            queue_adapter = UnifiedQueueAdapter(self.project_root)

            # Get all queue items
            all_items = queue_adapter.get_all_items()

            # Count asks (chat history items)
            ask_count = len([item for item in all_items if item.item_type == QueueItemType.CHAT_HISTORY])
            total_asks = len([item for item in all_items if item.item_type == QueueItemType.CHAT_HISTORY])

            # Update ask tracker
            self.ask_tracker.current = ask_count
            self.ask_tracker.total = total_asks
            self.ask_tracker._save_data()

            # Count notifications
            notification_count = len([item for item in all_items if item.item_type == QueueItemType.NOTIFICATION])

            # Update notification tracker
            for _ in range(notification_count - self.notification_tracker.get_count()):
                self.notification_tracker.add_notification({
                    "source": "unified_queue",
                    "type": "queue_sync"
                })

            logger.info(f"✅ Synced with unified queue: {ask_count} asks, {notification_count} notifications")

        except ImportError:
            logger.debug("Unified queue adapter not available")
        except Exception as e:
            logger.debug(f"Sync error: {e}")

    def add_notification(self, notification: Dict[str, Any]):
        """Add notification to IDE-QUEUE"""
        self.notification_tracker.add_notification(notification)
        logger.info(f"🔔 Notification added: {self.notification_tracker.get_display()}")

    def remove_notification(self, notification_id: str):
        """Remove notification from IDE-QUEUE"""
        self.notification_tracker.remove_notification(notification_id)
        logger.info(f"🔔 Notification removed: {self.notification_tracker.get_display()}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Cursor IDE Footer Customization")
    parser.add_argument("--update", action="store_true", help="Update Cursor IDE settings")
    parser.add_argument("--display", action="store_true", help="Show footer display")
    parser.add_argument("--add-ask", action="store_true", help="Add ask to heap-stack")
    parser.add_argument("--remove-ask", action="store_true", help="Remove ask from heap-stack")
    parser.add_argument("--add-notification", type=str, help="Add notification (JSON)")
    parser.add_argument("--status", action="store_true", help="Show status")

    args = parser.parse_args()

    customization = CursorIDEFooterCustomization()

    if args.update:
        customization.update_settings()

    if args.display:
        footer = customization.get_footer_display()
        print(f"\nFooter Display:\n{footer}\n")

    if args.add_ask:
        customization.add_ask()

    if args.remove_ask:
        customization.remove_ask()

    if args.add_notification:
        try:
            notification = json.loads(args.add_notification)
            customization.add_notification(notification)
        except Exception as e:
            print(f"❌ Error adding notification: {e}")

    if args.status:
        config = customization.get_footer_config()
        print(json.dumps(config, indent=2))


if __name__ == "__main__":


    main()