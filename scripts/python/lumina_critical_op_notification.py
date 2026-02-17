#!/usr/bin/env python3
"""
LUMINA Critical Command Center Issues - @OP Notification System

EASIEST WAY TO NOTIFY @OP OF CRITICAL COMMAND CENTER ISSUES

Multi-channel notification system for critical issues:
1. Windows Desktop Notification (Primary - Easiest)
2. Cursor IDE Notification (If available)
3. Console Alert (Fallback)
4. Log File (Persistence)

Tags: #LUMINA #@OP #CRITICAL #NOTIFICATION #COMMAND_CENTER #ALERT @JARVIS @TEAM
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LUMINACriticalOPNotification")


class CriticalSeverity(Enum):
    """Critical issue severity levels"""
    CRITICAL = "critical"  # System-breaking, immediate action required
    HIGH = "high"  # Important, address soon
    WARNING = "warning"  # Attention needed
    INFO = "info"  # Informational


class LUMINACriticalOPNotification:
    """
    EASIEST WAY TO NOTIFY @OP OF CRITICAL COMMAND CENTER ISSUES

    Primary Method: Windows Desktop Notification (win10toast)
    Fallback Methods: Console alerts, log files
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize notification system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "critical_notifications"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Windows notification (easiest method)
        self.windows_notification_available = False
        try:
            import win10toast
            self.windows_notification_available = True
            self.toaster = win10toast.ToastNotifier()
            logger.info("✅ Windows Desktop Notification available (PRIMARY METHOD)")
        except ImportError:
            logger.warning("⚠️  win10toast not available - install with: pip install win10toast")
            logger.info("   Using console alerts as fallback")

        # Notification history
        self.notification_history_file = self.data_dir / "notification_history.jsonl"

        logger.info("✅ LUMINA Critical @OP Notification System initialized")
        logger.info("   EASIEST METHOD: Windows Desktop Notification")

    def notify_critical_issue(
        self,
        title: str,
        message: str,
        severity: CriticalSeverity = CriticalSeverity.CRITICAL,
        source: str = "LUMINA Command Center",
        details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Notify @OP of critical command center issue

        PRIMARY METHOD: Windows Desktop Notification (easiest)
        FALLBACK: Console alert + log file
        """
        notification_id = f"lumina_critical_{int(time.time())}"

        # Format notification
        severity_icon = {
            CriticalSeverity.CRITICAL: "🔴",
            CriticalSeverity.HIGH: "🟠",
            CriticalSeverity.WARNING: "🟡",
            CriticalSeverity.INFO: "🔵"
        }.get(severity, "⚪")

        formatted_title = f"{severity_icon} {title}"
        formatted_message = f"{message}\n\nSource: {source}\nSeverity: {severity.value.upper()}"

        # Method 1: Windows Desktop Notification (EASIEST)
        success = False
        if self.windows_notification_available:
            try:
                # Windows notification duration: 10 seconds for critical, 5 for others
                duration = 10 if severity == CriticalSeverity.CRITICAL else 5

                self.toaster.show_toast(
                    title=formatted_title,
                    msg=formatted_message,
                    duration=duration,
                    threaded=True,
                    icon_path=None  # Can add custom icon later
                )
                success = True
                logger.info(f"✅ Windows Desktop Notification sent: {title}")
            except Exception as e:
                logger.warning(f"⚠️  Windows notification failed: {e}")

        # Method 2: Console Alert (Fallback)
        if not success:
            print("\n" + "="*80)
            print(f"🚨 CRITICAL COMMAND CENTER ISSUE - @OP NOTIFICATION")
            print("="*80)
            print(f"Title: {formatted_title}")
            print(f"Message: {formatted_message}")
            if details:
                print(f"Details: {json.dumps(details, indent=2)}")
            print("="*80 + "\n")
            success = True

        # Method 3: Log to file (Persistence)
        self._log_notification({
            "notification_id": notification_id,
            "timestamp": datetime.now().isoformat(),
            "title": title,
            "message": message,
            "severity": severity.value,
            "source": source,
            "details": details or {},
            "delivery_method": "windows_desktop" if self.windows_notification_available else "console"
        })

        return success

    def notify_system_down(self, system_name: str, reason: str = "Unknown"):
        """Notify @OP that a system is down"""
        return self.notify_critical_issue(
            title=f"System Down: {system_name}",
            message=f"Critical system '{system_name}' is down.\nReason: {reason}\nImmediate attention required.",
            severity=CriticalSeverity.CRITICAL,
            source="LUMINA Command Center - System Monitor"
        )

    def notify_threshold_exceeded(self, metric: str, value: float, threshold: float):
        """Notify @OP that a threshold has been exceeded"""
        return self.notify_critical_issue(
            title=f"Threshold Exceeded: {metric}",
            message=f"{metric} has exceeded threshold.\nCurrent: {value}\nThreshold: {threshold}",
            severity=CriticalSeverity.HIGH,
            source="LUMINA Command Center - Metrics Monitor",
            details={"metric": metric, "value": value, "threshold": threshold}
        )

    def notify_error(self, error_type: str, error_message: str, context: Optional[str] = None):
        """Notify @OP of an error"""
        return self.notify_critical_issue(
            title=f"Error: {error_type}",
            message=f"{error_message}\n\nContext: {context or 'No additional context'}",
            severity=CriticalSeverity.CRITICAL,
            source="LUMINA Command Center - Error Handler",
            details={"error_type": error_type, "error_message": error_message, "context": context}
        )

    def notify_security_alert(self, alert_type: str, description: str):
        """Notify @OP of a security alert"""
        return self.notify_critical_issue(
            title=f"Security Alert: {alert_type}",
            message=f"{description}\n\nSecurity issue detected. Immediate review required.",
            severity=CriticalSeverity.CRITICAL,
            source="LUMINA Command Center - Security Monitor",
            details={"alert_type": alert_type, "description": description}
        )

    def _log_notification(self, notification: Dict[str, Any]):
        """Log notification to file for persistence"""
        try:
            with open(self.notification_history_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(notification) + '\n')
        except Exception as e:
            logger.warning(f"Failed to log notification: {e}")

    def get_recent_notifications(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent notifications"""
        notifications = []
        if self.notification_history_file.exists():
            try:
                with open(self.notification_history_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines[-limit:]:
                        if line.strip():
                            notifications.append(json.loads(line))
            except Exception as e:
                logger.warning(f"Failed to read notification history: {e}")
        return notifications


# Convenience function for easiest notification
def notify_op_critical(title: str, message: str, severity: str = "critical"):
    """
    EASIEST WAY TO NOTIFY @OP OF CRITICAL ISSUES

    Usage:
        from lumina_critical_op_notification import notify_op_critical
        notify_op_critical("System Down", "JARVIS command center is offline")
    """
    notifier = LUMINACriticalOPNotification()
    severity_enum = CriticalSeverity[severity.upper()] if severity.upper() in [s.name for s in CriticalSeverity] else CriticalSeverity.CRITICAL
    return notifier.notify_critical_issue(title, message, severity_enum)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="LUMINA Critical @OP Notification System")
    parser.add_argument("--test", action="store_true", help="Send test notification")
    parser.add_argument("--title", type=str, help="Notification title")
    parser.add_argument("--message", type=str, help="Notification message")
    parser.add_argument("--severity", type=str, default="critical", choices=["critical", "high", "warning", "info"], help="Severity level")
    parser.add_argument("--system-down", type=str, help="Notify system down (provide system name)")
    parser.add_argument("--threshold", action="store_true", help="Notify threshold exceeded (requires --metric, --value, --limit)")
    parser.add_argument("--metric", type=str, help="Metric name")
    parser.add_argument("--value", type=float, help="Current value")
    parser.add_argument("--limit", type=float, help="Threshold limit")
    parser.add_argument("--recent", type=int, help="Show recent notifications (number)")

    args = parser.parse_args()

    notifier = LUMINACriticalOPNotification()

    if args.test:
        notifier.notify_critical_issue(
            title="Test Notification",
            message="This is a test notification from LUMINA Command Center.",
            severity=CriticalSeverity.INFO
        )
        print("✅ Test notification sent")

    elif args.system_down:
        notifier.notify_system_down(args.system_down)
        print(f"✅ System down notification sent: {args.system_down}")

    elif args.threshold:
        if args.metric and args.value is not None and args.limit is not None:
            notifier.notify_threshold_exceeded(args.metric, args.value, args.limit)
            print(f"✅ Threshold exceeded notification sent: {args.metric}")
        else:
            print("❌ --threshold requires --metric, --value, and --limit")

    elif args.title and args.message:
        severity_enum = CriticalSeverity[args.severity.upper()]
        notifier.notify_critical_issue(args.title, args.message, severity_enum)
        print(f"✅ Notification sent: {args.title}")

    elif args.recent:
        notifications = notifier.get_recent_notifications(args.recent)
        print(f"\n📋 Recent Notifications (last {args.recent}):")
        print("="*80)
        for notif in notifications:
            print(f"  [{notif['timestamp']}] {notif['severity'].upper()}: {notif['title']}")
            print(f"    {notif['message'][:100]}...")
        print("="*80)

    else:
        print("\n" + "="*80)
        print("🚨 LUMINA Critical @OP Notification System")
        print("   EASIEST WAY TO NOTIFY @OP OF CRITICAL COMMAND CENTER ISSUES")
        print("="*80)
        print("\nUsage:")
        print("  --test                    Send test notification")
        print("  --title TITLE --message MSG  Send custom notification")
        print("  --system-down SYSTEM     Notify system is down")
        print("  --threshold --metric METRIC --value VALUE --limit LIMIT  Notify threshold exceeded")
        print("  --recent N                Show recent notifications")
        print("\nExample:")
        print('  python lumina_critical_op_notification.py --test')
        print('  python lumina_critical_op_notification.py --title "JARVIS Down" --message "Command center offline"')
        print('  python lumina_critical_op_notification.py --system-down "JARVIS"')
        print("="*80 + "\n")
