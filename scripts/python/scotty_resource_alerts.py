#!/usr/bin/env python3
"""
@SCOTTY's Resource Alert System
Audio/Visual notifications for resource monitoring alerts

Tags: #SCOTTY #ALERTS #NOTIFICATIONS #AUDIO #VISUAL @SCOTTY @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("SCOTTYResourceAlerts")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("SCOTTYResourceAlerts")


class ResourceAlertNotifier:
    """Audio/Visual alert system for resource monitoring"""

    def __init__(self, project_root: Path = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "scotty_resource_monitoring"
        self.last_beep_time = {}
        self.beep_cooldown = 600  # 10 minute cooldown for resource beeps
        self.tactical_silence = True  # Enable silence during disk crisis

    def send_alert(self, alert: Dict):
        """Send audio/visual alert"""
        severity = alert.get("severity", "info")
        alert_type = alert.get("alert_type", "unknown")
        message = alert.get("message", "")

        # Visual notification (Windows Toast)
        self._send_toast_notification(alert)

        # Audio notification
        if severity in ["critical", "warning"]:
            self._play_alert_sound(severity, alert_type)

        # Log notification
        logger.info(f"Alert sent: {message}")

    def _send_toast_notification(self, alert: Dict):
        """Send Windows Toast notification"""
        try:
            import subprocess

            severity = alert.get("severity", "info")
            message = alert.get("message", "")
            component = alert.get("component", "System")

            # Create toast notification via PowerShell
            ps_script = f'''
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
            $textNodes = $template.GetElementsByTagName("text")
            $textNodes.Item(0).AppendChild($template.CreateTextNode("SCOTTY Resource Alert"))
            $textNodes.Item(1).AppendChild($template.CreateTextNode("{message[:100]}"))
            $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("SCOTTY").Show($toast)
            '''

            subprocess.run(
                ['powershell', '-Command', ps_script],
                capture_output=True,
                timeout=5
            )
        except Exception as e:
            logger.debug(f"Toast notification failed: {e}")

    def _play_alert_sound(self, severity: str, alert_type: str):
        """Play alert sound - with Throttling and Tactical Silence"""
        if self.tactical_silence:
            return

        import time
        current_time = time.time()
        alert_key = f"{severity}_{alert_type}"
        last_time = self.last_beep_time.get(alert_key, 0)

        if (current_time - last_time < self.beep_cooldown) and severity != "critical":
            return

        self.last_beep_time[alert_key] = current_time

        try:
            import subprocess

            # Use Windows system sounds
            if severity == "critical":
                sound = "SystemHand"  # Critical stop sound
            elif severity == "warning":
                sound = "SystemExclamation"  # Warning sound
            else:
                sound = "SystemDefault"  # Default beep

            subprocess.run(
                ['powershell', '-Command', f'[console]::beep(800, 300)'],
                timeout=2
            )

            # Optional: Play Windows sound
            # subprocess.run(['powershell', '-Command', f'(New-Object Media.SoundPlayer "C:\\Windows\\Media\\{sound}.wav").PlaySync()'])
        except Exception as e:
            logger.debug(f"Sound alert failed: {e}")


def main():
    try:
        """Monitor alerts and send notifications"""
        import argparse

        parser = argparse.ArgumentParser(description="@SCOTTY's Resource Alert System")
        parser.add_argument("--monitor", action="store_true", help="Monitor for new alerts")
        parser.add_argument("--test", action="store_true", help="Send test alert")

        args = parser.parse_args()

        notifier = ResourceAlertNotifier()

        if args.test:
            test_alert = {
                "timestamp": datetime.now().isoformat(),
                "alert_type": "test",
                "severity": "warning",
                "message": "Test alert from SCOTTY Resource Monitor",
                "component": "Test System"
            }
            notifier.send_alert(test_alert)
            print("✅ Test alert sent")
        elif args.monitor:
            alerts_file = notifier.data_dir / "alerts.jsonl"
            if not alerts_file.exists():
                print("No alerts file found. Run resource monitor first.")
                return

            print("Monitoring for new alerts...")
            last_position = alerts_file.stat().st_size if alerts_file.exists() else 0

            import time
            while True:
                if alerts_file.exists():
                    current_size = alerts_file.stat().st_size
                    if current_size > last_position:
                        # Read new alerts
                        with open(alerts_file, 'r', encoding='utf-8') as f:
                            f.seek(last_position)
                            for line in f:
                                if line.strip():
                                    alert = json.loads(line)
                                    notifier.send_alert(alert)
                        last_position = current_size

                time.sleep(5)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()