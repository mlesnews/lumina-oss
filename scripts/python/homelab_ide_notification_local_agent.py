#!/usr/bin/env python3
"""
@homelab IDE Notification Local Agent
USS Lumina - @scotty (Windows Systems Architect)

Local agent that runs on the IDE machine and communicates with NAS service.
Handles actual UI interaction with IDE notifications.

Tags: #HOMELAB #IDE #NOTIFICATIONS #LOCAL_AGENT @HOMELAB @SCOTTY
"""

import sys
import asyncio
import requests
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("HomelabIDENotificationLocalAgent")

# Import the handler
try:
    from jarvis_homelab_ide_notification_handler import HomelabIDENotificationHandler
except ImportError:
    logger.error("Could not import IDE notification handler")
    sys.exit(1)


class HomelabIDENotificationLocalAgent:
    """
    Local Agent for @homelab IDE Notification Handler

    Runs on the local machine where IDE is running.
    Communicates with NAS service for coordination.
    """

    def __init__(self, project_root: Path, nas_service_url: Optional[str] = None):
        self.project_root = project_root
        self.nas_service_url = nas_service_url or "http://<NAS_PRIMARY_IP>:8080"  # Default NAS service URL
        self.handler = HomelabIDENotificationHandler(project_root)
        self.logger = logger
        self.running = False

        self.logger.info("✅ @homelab IDE Notification Local Agent initialized")
        self.logger.info(f"   NAS Service URL: {self.nas_service_url}")

    def report_to_nas(self, notification_type: str, action: str, result: Dict[str, Any]) -> bool:
        """Report notification handling to NAS service"""
        if not self.nas_service_url:
            return False

        try:
            payload = {
                "timestamp": datetime.now().isoformat(),
                "notification_type": notification_type,
                "action": action,
                "result": result,
                "agent": "local_ide_machine"
            }

            response = requests.post(
                f"{self.nas_service_url}/api/notifications/report",
                json=payload,
                timeout=5
            )

            return response.status_code == 200
        except Exception as e:
            self.logger.debug(f"Could not report to NAS service: {e}")
            return False

    async def monitor_and_handle(self, interval: int = 5):
        """Monitor for IDE notifications and handle them"""
        self.running = True
        self.logger.info(f"👀 Starting local agent monitoring (interval: {interval}s)...")
        self.logger.info("   Will handle IDE notifications and report to NAS service")
        self.logger.info("   Press Ctrl+C to stop")
        self.logger.info("")

        try:
            while self.running:
                # Check for large file dialog
                if self.handler.detect_large_file_dialog():
                    self.logger.info("🔍 Large file dialog detected - handling...")
                    result = self.handler.handle_large_file_dialog("dont_show_again")

                    if result.get("success"):
                        # Report to NAS service
                        self.report_to_nas("large_file_features_disabled", "dont_show_again", result)
                        self.logger.info("✅ Large file dialog handled and reported to NAS")

                await asyncio.sleep(interval)

        except KeyboardInterrupt:
            self.logger.info("")
            self.logger.info("🛑 Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Monitoring error: {e}", exc_info=True)
        finally:
            self.running = False


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="@homelab IDE Notification Local Agent")
    parser.add_argument("--nas-url", default="http://<NAS_PRIMARY_IP>:8080",
                       help="NAS service URL")
    parser.add_argument("--interval", type=int, default=5,
                       help="Monitoring interval in seconds")
    parser.add_argument("--handle-now", action="store_true",
                       help="Handle large file dialog now and exit")

    args = parser.parse_args()

    agent = HomelabIDENotificationLocalAgent(project_root, nas_service_url=args.nas_url)

    if args.handle_now:
        result = agent.handler.handle_large_file_dialog("dont_show_again")
        if result.get("success"):
            agent.report_to_nas("large_file_features_disabled", "dont_show_again", result)
            print("✅ Handled and reported to NAS")
        else:
            print(f"❌ Failed: {result.get('error')}")
    else:
        asyncio.run(agent.monitor_and_handle(interval=args.interval))


if __name__ == "__main__":


    main()