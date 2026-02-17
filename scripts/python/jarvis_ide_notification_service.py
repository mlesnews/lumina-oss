#!/usr/bin/env python3
"""
JARVIS IDE Notification Service

Background service that continuously monitors and responds to IDE notifications.
Runs automatically and handles Git warnings, errors, and other notifications.

Tags: #CURSOR-IDE #AUTOMATION #SERVICE @CURSOR-ENGINEER
"""

import sys
import subprocess
import json
import time
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

logger = get_logger("JARVISIDEService")


class JARVISIDENotificationService:
    """
    JARVIS IDE Notification Service

    Background service for automatic IDE notification monitoring and response.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.running = False
        self.check_interval = 30  # Check every 30 seconds
        self.last_check = None

        self.logger.info("✅ JARVIS IDE Notification Service initialized")

    def check_and_handle_notifications(self) -> Dict[str, Any]:
        """Check for notifications and handle them"""
        try:
            # Import notification monitor
            from jarvis_ide_notification_monitor import JARVISIDENotificationMonitor

            monitor = JARVISIDENotificationMonitor(self.project_root)
            result = monitor.monitor_git_notifications()

            if result.get("action") == "auto_committed":
                self.logger.info(f"✅ Handled notification: {result.get('changes_committed', 0)} changes committed")
                return {
                    "handled": True,
                    "action": result.get("action"),
                    "details": result
                }

            return {
                "handled": False,
                "status": result.get("status", "ok")
            }

        except Exception as e:
            self.logger.error(f"❌ Error checking notifications: {e}", exc_info=True)
            return {"handled": False, "error": str(e)}

    def run_continuous(self) -> None:
        """Run continuous monitoring"""
        self.logger.info(f"🔄 Starting continuous IDE notification monitoring (interval: {self.check_interval}s)...")
        self.running = True

        try:
            while self.running:
                self.last_check = datetime.now()
                result = self.check_and_handle_notifications()

                if result.get("handled"):
                    self.logger.info(f"✅ Notification handled at {self.last_check.isoformat()}")

                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            self.logger.info("🛑 Service stopped by user")
            self.running = False
        except Exception as e:
            self.logger.error(f"❌ Service error: {e}", exc_info=True)
            self.running = False

    def stop(self) -> None:
        """Stop the service"""
        self.logger.info("🛑 Stopping IDE notification service...")
        self.running = False


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS IDE Notification Service")
        parser.add_argument("--start", action="store_true", help="Start continuous monitoring")
        parser.add_argument("--check", action="store_true", help="Check once and exit")
        parser.add_argument("--interval", type=int, default=30, help="Check interval in seconds")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        service = JARVISIDENotificationService(project_root)

        if args.interval:
            service.check_interval = args.interval

        if args.check:
            result = service.check_and_handle_notifications()
            print(json.dumps(result, indent=2, default=str))

        elif args.start:
            service.run_continuous()

        else:
            # Default: check once
            result = service.check_and_handle_notifications()
            print(json.dumps(result, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()