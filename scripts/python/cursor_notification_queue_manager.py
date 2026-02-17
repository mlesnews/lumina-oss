#!/usr/bin/env python3
"""
Cursor/VS Code Notification Queue Manager

Monitors and reduces notification queue count in Cursor IDE and VS Code.
Automatically processes notifications to keep queue count low.

Tags: #CURSOR #VSCODE #NOTIFICATIONS #QUEUE #AUTOMATION #REQUIRED @JARVIS @LUMINA
"""

import sys
import time
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CursorNotificationQueue")


class CursorNotificationQueueManager:
    """
    Cursor/VS Code Notification Queue Manager

    Monitors and reduces notification queue count.
    Automatically processes notifications to keep queue low.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize notification queue manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "notification_queue"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.state_file = self.data_dir / "queue_state.json"
        self.history_file = self.data_dir / "queue_history.jsonl"

        # Load state
        self.state = self._load_state()

        logger.info("✅ Cursor Notification Queue Manager initialized")

    def _load_state(self) -> Dict[str, Any]:
        """Load queue state"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.debug(f"Could not load state: {e}")

        return {
            "last_check": None,
            "last_queue_count": 0,
            "notifications_processed": 0,
            "auto_actions_taken": []
        }

    def _save_state(self):
        """Save queue state"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, default=str)
        except Exception as e:
            logger.debug(f"Could not save state: {e}")

    def _log_history(self, entry: Dict[str, Any]):
        """Log to history file"""
        try:
            with open(self.history_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, default=str) + '\n')
        except Exception as e:
            logger.debug(f"Could not log history: {e}")

    def get_notification_count(self) -> Optional[int]:
        """
        Get current notification queue count from Cursor/VS Code

        Returns:
            Notification count or None if unable to determine
        """
        # Method 1: Try to read from Cursor/VS Code state
        # Cursor stores state in various locations
        cursor_state_paths = [
            Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "globalStorage" / "state.vscode" / "notifications.json",
            Path.home() / ".cursor" / "state" / "notifications.json",
            Path.home() / ".vscode" / "state" / "notifications.json",
            Path.home() / "AppData" / "Roaming" / "Code" / "User" / "globalStorage" / "state.vscode" / "notifications.json",
        ]

        for state_path in cursor_state_paths:
            if state_path.exists():
                try:
                    with open(state_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Try to find notification count
                        if isinstance(data, dict):
                            # Look for common notification count fields
                            count = data.get("notificationCount", data.get("count", data.get("queueCount")))
                            if count is not None:
                                logger.info(f"✅ Found notification count: {count} (from {state_path})")
                                return int(count)
                except Exception as e:
                    logger.debug(f"Could not read state from {state_path}: {e}")

        # Method 2: Try to use VLM to detect notification count visually
        try:
            from vlm_integration import VLMIntegration
            vlm = VLMIntegration(project_root=self.project_root)
            # Take screenshot and look for notification count
            screenshot = vlm.capture_screen()
            if screenshot:
                # Ask VLM to count notifications
                prompt = "Count the number of notifications visible in the notification area (usually top-right corner). Return only the number."
                result = vlm.analyze_image(screenshot, prompt)
                # Try to extract number from result
                import re
                numbers = re.findall(r'\d+', str(result))
                if numbers:
                    count = int(numbers[0])
                    logger.info(f"✅ Detected notification count via VLM: {count}")
                    return count
        except Exception as e:
            logger.debug(f"VLM notification detection not available: {e}")

        # Method 3: Use intelligent notification processor
        try:
            from intelligent_notification_processor import IntelligentNotificationProcessor
            processor = IntelligentNotificationProcessor(self.project_root)
            # Get active notification count from processor's state
            if hasattr(processor, 'notification_events'):
                active_count = len([e for e in processor.notification_events.values() if not e.processed])
                if active_count > 0:
                    logger.info(f"✅ Found {active_count} active notifications via processor")
                    return active_count
        except Exception as e:
            logger.debug(f"Notification processor not available: {e}")

        # Method 4: Use notification fix manager
        try:
            from notification_fix_manager import NotificationFixManager
            manager = NotificationFixManager()
            summary = manager.get_notification_summary(hours=1)
            count = summary.get("total_notifications", 0)
            unfixed = summary.get("unfixed_notifications", 0)
            if unfixed > 0:
                logger.info(f"✅ Found {unfixed} unfixed notifications via fix manager")
                return unfixed
        except Exception as e:
            logger.debug(f"Notification fix manager not available: {e}")

        logger.debug("⚠️  Could not determine notification count - using fallback")
        return None

    def process_notifications(self) -> Dict[str, Any]:
        """
        Process notifications to reduce queue count

        Returns:
            Processing result with actions taken
        """
        logger.info("🔔 Processing notification queue...")

        # Get current count
        current_count = self.get_notification_count()

        if current_count is None:
            logger.warning("⚠️  Could not determine notification count")
            return {
                "success": False,
                "error": "Could not determine notification count",
                "actions_taken": []
            }

        logger.info(f"📊 Current notification count: {current_count}")

        actions_taken = []

        # If queue is high, take actions to reduce it
        # CRITICAL: Reduce notification count when it gets too high
        if current_count is not None and current_count > 5:
            logger.warning(f"⚠️  High notification count: {current_count} - taking action to reduce...")

            # Action 1: Auto-dismiss non-critical notifications
            dismissed = self._dismiss_non_critical_notifications()
            if dismissed > 0:
                actions_taken.append({
                    "action": "dismiss_non_critical",
                    "count": dismissed
                })
                logger.info(f"✅ Dismissed {dismissed} non-critical notifications")

            # Action 2: Auto-resolve known issues
            resolved = self._auto_resolve_known_issues()
            if resolved > 0:
                actions_taken.append({
                    "action": "auto_resolve",
                    "count": resolved
                })
                logger.info(f"✅ Auto-resolved {resolved} known issues")

            # Action 3: Process Git notifications
            git_processed = self._process_git_notifications()
            if git_processed > 0:
                actions_taken.append({
                    "action": "process_git",
                    "count": git_processed
                })
                logger.info(f"✅ Processed {git_processed} Git notifications")
        elif current_count is not None:
            logger.info(f"✅ Notification count is low: {current_count} - no action needed")

        # Update state
        self.state["last_check"] = datetime.now().isoformat()
        self.state["last_queue_count"] = current_count
        self.state["notifications_processed"] += len(actions_taken)
        self.state["auto_actions_taken"].extend(actions_taken)

        # Keep only last 100 actions
        if len(self.state["auto_actions_taken"]) > 100:
            self.state["auto_actions_taken"] = self.state["auto_actions_taken"][-100:]

        self._save_state()

        # Log to history
        self._log_history({
            "timestamp": datetime.now().isoformat(),
            "queue_count": current_count,
            "actions_taken": actions_taken
        })

        # Calculate reduction
        reduced_count = sum(action.get("count", 0) for action in actions_taken)

        return {
            "success": True,
            "queue_count": current_count,
            "actions_taken": actions_taken,
            "reduced": len(actions_taken) > 0,
            "reduced_count": reduced_count,
            "message": f"Processed {reduced_count} notifications" if reduced_count > 0 else "No action needed"
        }

    def _dismiss_non_critical_notifications(self) -> int:
        """Dismiss non-critical notifications"""
        dismissed = 0

        # Try to use IDE notification service
        try:
            from jarvis_ide_notification_service import JARVISIDENotificationService
            service = JARVISIDENotificationService(self.project_root)
            result = service.check_and_handle_notifications()

            if result.get("handled"):
                dismissed = 1
                logger.info("✅ Dismissed notification via IDE service")
        except Exception as e:
            logger.debug(f"Could not use notification service: {e}")

        # Try intelligent notification processor
        try:
            from intelligent_notification_processor import IntelligentNotificationProcessor, NotificationPriority
            processor = IntelligentNotificationProcessor(self.project_root)
            # Process low-priority notifications
            if hasattr(processor, 'notification_events'):
                low_priority = [
                    e for e in processor.notification_events.values()
                    if e.priority == NotificationPriority.LOW and not e.processed
                ]
                for event in low_priority[:5]:  # Process up to 5 at a time
                    try:
                        processor.process_notification(event.title, event.message, event.source, event.metadata)
                        dismissed += 1
                    except:
                        pass
        except Exception as e:
            logger.debug(f"Could not use notification processor: {e}")

        # Try notification fix manager
        try:
            from notification_fix_manager import NotificationFixManager
            manager = NotificationFixManager()
            # Get recent notifications and suppress non-critical ones
            summary = manager.get_notification_summary(hours=1)
            # Suppress low-severity notifications
            for notification in manager.notifications:
                if notification.get("severity") == "low" and not notification.get("fixed"):
                    manager.suppress_notification(notification["id"])
                    dismissed += 1
                    if dismissed >= 5:  # Limit to 5 per cycle
                        break
        except Exception as e:
            logger.debug(f"Could not use notification fix manager: {e}")

        return dismissed

    def _auto_resolve_known_issues(self) -> int:
        """Auto-resolve known issues that cause notifications"""
        resolved = 0

        # Common issues that can be auto-resolved:
        # 1. Git "too many changes" - auto-commit
        # 2. Import errors - try to fix imports
        # 3. Linter warnings - auto-fix where possible
        # 4. Task errors - reset task manager
        # 5. Extension warnings - update extensions

        # 1. Git issues
        try:
            from jarvis_ide_notification_monitor import JARVISIDENotificationMonitor
            monitor = JARVISIDENotificationMonitor(self.project_root)
            result = monitor.monitor_git_notifications()

            if result.get("action") == "auto_committed":
                resolved += 1
                logger.info("✅ Auto-resolved Git 'too many changes' issue")
        except Exception as e:
            logger.debug(f"Could not auto-resolve Git issues: {e}")

        # 2. Notification fix manager
        try:
            from notification_fix_manager import NotificationFixManager
            manager = NotificationFixManager()
            # Try to fix recent unfixed notifications
            recent_unfixed = [
                n for n in manager.notifications
                if not n.get("fixed") and not n.get("suppressed", False)
            ]
            for notification in recent_unfixed[:3]:  # Try up to 3
                if manager.report_notification(
                    notification["type"],
                    notification["message"],
                    notification["source"],
                    notification["severity"],
                    notification.get("metadata")
                ):
                    resolved += 1
        except Exception as e:
            logger.debug(f"Could not use notification fix manager: {e}")

        return resolved

    def _process_git_notifications(self) -> int:
        """Process Git-related notifications"""
        processed = 0

        try:
            from jarvis_ide_notification_monitor import JARVISIDENotificationMonitor
            monitor = JARVISIDENotificationMonitor(self.project_root)
            result = monitor.monitor_git_notifications()

            if result.get("action"):
                processed += 1
        except Exception as e:
            logger.debug(f"Could not process Git notifications: {e}")

        return processed

    def monitor_continuously(self, interval: int = 60):
        """Monitor and process notifications continuously"""
        logger.info(f"🔄 Starting continuous notification queue monitoring (interval: {interval}s)...")
        logger.info(f"   Will check notification count every {interval} seconds")
        logger.info(f"   Will auto-reduce queue when count > 5")

        try:
            while True:
                result = self.process_notifications()

                if result.get("reduced"):
                    reduced_count = result.get("reduced_count", 0)
                    queue_count = result.get("queue_count", "unknown")
                    logger.info(f"✅ Reduced notification queue: {reduced_count} processed (queue: {queue_count})")
                elif result.get("queue_count") is not None:
                    queue_count = result.get("queue_count")
                    logger.debug(f"📊 Notification queue: {queue_count} (no action needed)")

                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("🛑 Monitoring stopped")
        except Exception as e:
            logger.error(f"❌ Monitoring error: {e}", exc_info=True)


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Cursor Notification Queue Manager")
        parser.add_argument('--monitor', action='store_true', help='Monitor continuously')
        parser.add_argument('--interval', type=int, default=60, help='Check interval in seconds')
        parser.add_argument('--process', action='store_true', help='Process once and exit')

        args = parser.parse_args()

        manager = CursorNotificationQueueManager()

        if args.monitor:
            manager.monitor_continuously(interval=args.interval)
        elif args.process:
            result = manager.process_notifications()
            print(json.dumps(result, indent=2, default=str))
        else:
            # Default: process once
            result = manager.process_notifications()
            print(json.dumps(result, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()