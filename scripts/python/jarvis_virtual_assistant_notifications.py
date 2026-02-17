#!/usr/bin/env python3
"""
JARVIS Virtual Assistant Notifications

Enables the virtual assistant to show notifications for:
- Workflow progress
- Integration status
- System health
- Important events
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISVirtualAssistantNotifications")


class JARVISVirtualAssistantNotifications:
    """
    Notification system for virtual assistant
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.notification_queue = []

    def notify_workflow_progress(self, workflow_name: str, progress: float, status: str):
        """Notify about workflow progress"""
        notification = {
            "type": "workflow",
            "title": f"Workflow: {workflow_name}",
            "message": f"{progress:.1f}% complete - {status}",
            "priority": "high" if progress == 100 else "medium",
            "timestamp": datetime.now().isoformat()
        }
        self._add_notification(notification)
        return notification

    def notify_integration_status(self, actor_name: str, integration_percent: float):
        """Notify about integration status"""
        if integration_percent < 50:
            notification = {
                "type": "integration",
                "title": f"Low Integration: {actor_name}",
                "message": f"Only {integration_percent:.1f}% integrated - needs attention",
                "priority": "high",
                "timestamp": datetime.now().isoformat()
            }
            self._add_notification(notification)
            return notification
        return None

    def notify_system_health(self, health_score: float, issues: List[str]):
        """Notify about system health"""
        if health_score < 70:
            notification = {
                "type": "health",
                "title": "System Health Alert",
                "message": f"Health score: {health_score:.1f}% - {len(issues)} issues found",
                "priority": "critical" if health_score < 50 else "high",
                "details": issues,
                "timestamp": datetime.now().isoformat()
            }
            self._add_notification(notification)
            return notification
        return None

    def notify_ide_utilization(self, utilization_percent: float):
        """Notify about IDE utilization"""
        if utilization_percent < 50:
            notification = {
                "type": "utilization",
                "title": "IDE Underutilized",
                "message": f"IDE utilization only {utilization_percent:.1f}% - potential for automation",
                "priority": "medium",
                "timestamp": datetime.now().isoformat()
            }
            self._add_notification(notification)
            return notification
        return None

    def notify_browser_utilization(self, utilization_percent: float):
        """Notify about browser utilization"""
        if utilization_percent < 50:
            notification = {
                "type": "utilization",
                "title": "Browser Underutilized",
                "message": f"Browser utilization only {utilization_percent:.1f}% - potential for automation",
                "priority": "medium",
                "timestamp": datetime.now().isoformat()
            }
            self._add_notification(notification)
            return notification
        return None

    def _add_notification(self, notification: Dict[str, Any]):
        """Add notification to queue"""
        self.notification_queue.append(notification)

        # Limit queue size
        if len(self.notification_queue) > 100:
            self.notification_queue = self.notification_queue[-100:]

    def get_notifications(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent notifications"""
        return sorted(self.notification_queue, key=lambda x: x['timestamp'], reverse=True)[:limit]

    def send_to_virtual_assistant(self, notification: Dict[str, Any]) -> bool:
        """Send notification to virtual assistant"""
        try:
            # Try to import and use virtual assistant
            from jarvis_virtual_assistant import JARVISVirtualAssistant

            va = JARVISVirtualAssistant(self.project_root)

            # Show notification
            title = notification.get('title', 'Notification')
            message = notification.get('message', '')
            priority = notification.get('priority', 'medium')

            # Use virtual assistant's notification system
            if hasattr(va, 'show_notification'):
                va.show_notification(title, message, priority)
                return True
            else:
                # Fallback: log it
                self.logger.info(f"📢 {title}: {message}")
                return True

        except ImportError:
            # Virtual assistant not available, just log
            self.logger.info(f"📢 {notification.get('title', 'Notification')}: {notification.get('message', '')}")
            return False
        except Exception as e:
            self.logger.error(f"Error sending notification: {e}")
            return False

    def process_ecosystem_notifications(self):
        """Process ecosystem-wide notifications"""
        try:
            from jarvis_ecosystem_transparency import JARVISEcosystemTransparency

            transparency = JARVISEcosystemTransparency(self.project_root)
            report = transparency.generate_transparency_report()

            # Notify about overall integration
            if report['overall_integration_percent'] < 70:
                self.notify_integration_status("Overall Ecosystem", report['overall_integration_percent'])

            # Notify about low integration actors
            for actor in report['major_actors']['actors']:
                if actor['integration_percent'] < 50:
                    self.notify_integration_status(actor['name'], actor['integration_percent'])

            # Notify about IDE utilization
            if report['ide_utilization']['utilization_percent'] < 50:
                self.notify_ide_utilization(report['ide_utilization']['utilization_percent'])

            # Notify about browser utilization
            if report['browser_utilization']['utilization_percent'] < 50:
                self.notify_browser_utilization(report['browser_utilization']['utilization_percent'])

            # Send notifications to virtual assistant
            for notification in self.get_notifications(limit=5):
                self.send_to_virtual_assistant(notification)

        except Exception as e:
            self.logger.error(f"Error processing ecosystem notifications: {e}")


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Virtual Assistant Notifications")
        parser.add_argument("--process", action="store_true", help="Process ecosystem notifications")
        parser.add_argument("--notify", type=str, help="Send a custom notification")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        notifications = JARVISVirtualAssistantNotifications(project_root)

        if args.process or not args:
            notifications.process_ecosystem_notifications()
            print("✅ Notifications processed")

        if args.notify:
            notification = {
                "type": "custom",
                "title": "Custom Notification",
                "message": args.notify,
                "priority": "medium",
                "timestamp": datetime.now().isoformat()
            }
            notifications.send_to_virtual_assistant(notification)
            print(f"✅ Notification sent: {args.notify}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()