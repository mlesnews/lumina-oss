#!/usr/bin/env python3
"""
JARVIS Transparency Monitor

Continuously monitors ecosystem transparency and updates dashboard:
- Workflow progress
- Integration status
- IDE/Browser utilization
- Job slot status
- Virtual assistant notifications
"""

import sys
import time
import threading
from pathlib import Path
from typing import Dict, Any
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

logger = get_logger("JARVISTransparencyMonitor")


class JARVISTransparencyMonitor:
    """
    Continuous transparency monitoring
    """

    def __init__(self, project_root: Path, update_interval: int = 300):
        self.project_root = project_root
        self.update_interval = update_interval
        self.logger = logger
        self.running = False
        self.monitor_thread = None

    def start_monitoring(self):
        """Start continuous monitoring"""
        if self.running:
            self.logger.warning("Monitor already running")
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info(f"✅ Transparency monitor started (updates every {self.update_interval}s)")

    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("🛑 Transparency monitor stopped")

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Update transparency report
                from jarvis_ecosystem_transparency import JARVISEcosystemTransparency

                transparency = JARVISEcosystemTransparency(self.project_root)
                report = transparency.generate_transparency_report()

                # Save report
                transparency.save_report(report)

                # Update dashboard
                dashboard_md = transparency.generate_dashboard_markdown(report)
                dashboard_file = self.project_root / "ECOSYSTEM_TRANSPARENCY_DASHBOARD.md"
                dashboard_file.write_text(dashboard_md, encoding='utf-8')

                # Process notifications
                from jarvis_virtual_assistant_notifications import JARVISVirtualAssistantNotifications

                notifications = JARVISVirtualAssistantNotifications(self.project_root)
                notifications.process_ecosystem_notifications()

                self.logger.info(f"📊 Transparency updated: {report['overall_integration_percent']}% integrated")

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}", exc_info=True)

            # Wait for next update
            time.sleep(self.update_interval)

    def update_now(self):
        """Force immediate update"""
        try:
            from jarvis_ecosystem_transparency import JARVISEcosystemTransparency
            from jarvis_virtual_assistant_notifications import JARVISVirtualAssistantNotifications

            transparency = JARVISEcosystemTransparency(self.project_root)
            report = transparency.generate_transparency_report()

            transparency.save_report(report)

            dashboard_md = transparency.generate_dashboard_markdown(report)
            dashboard_file = self.project_root / "ECOSYSTEM_TRANSPARENCY_DASHBOARD.md"
            dashboard_file.write_text(dashboard_md, encoding='utf-8')

            notifications = JARVISVirtualAssistantNotifications(self.project_root)
            notifications.process_ecosystem_notifications()

            self.logger.info("✅ Transparency updated immediately")

            return report

        except Exception as e:
            self.logger.error(f"Error updating transparency: {e}", exc_info=True)
            return None


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Transparency Monitor")
    parser.add_argument("--start", action="store_true", help="Start continuous monitoring")
    parser.add_argument("--stop", action="store_true", help="Stop monitoring")
    parser.add_argument("--update", action="store_true", help="Update now")
    parser.add_argument("--interval", type=int, default=300, help="Update interval in seconds")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    monitor = JARVISTransparencyMonitor(project_root, update_interval=args.interval)

    if args.start:
        monitor.start_monitoring()
        print("✅ Monitoring started")
        print("Press Ctrl+C to stop")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            monitor.stop_monitoring()
            print("\n🛑 Monitoring stopped")
    elif args.stop:
        monitor.stop_monitoring()
        print("✅ Monitoring stopped")
    elif args.update or not args:
        report = monitor.update_now()
        if report:
            print(f"\n✅ Transparency updated")
            print(f"Overall Integration: {report['overall_integration_percent']}%")
            print(f"Major Actors: {report['major_actors']['average_integration']}%")
            print(f"Minor Actors: {report['minor_actors']['average_integration']}%")
            print(f"IDE Utilization: {report['ide_utilization']['utilization_percent']}%")
            print(f"Browser Utilization: {report['browser_utilization']['utilization_percent']}%")


if __name__ == "__main__":


    main()