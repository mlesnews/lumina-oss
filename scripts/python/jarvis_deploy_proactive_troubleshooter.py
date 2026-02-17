#!/usr/bin/env python3
"""
JARVIS Deploy Proactive IDE Troubleshooter

Deploys and activates the proactive IDE troubleshooter as a background service.

@CURSOR @IDE #TROUBLESHOOTING #DEPLOYMENT #ACTIVATION
"""

import sys
import os
import signal
import time
from pathlib import Path
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISDeployProactiveTroubleshooter")

try:
    from jarvis_proactive_ide_troubleshooter import JARVISProactiveIDETroubleshooter
    TROUBLESHOOTER_AVAILABLE = True
except ImportError:
    TROUBLESHOOTER_AVAILABLE = False
    JARVISProactiveIDETroubleshooter = None
    logger.error("❌ Proactive IDE Troubleshooter not available")


class ProactiveTroubleshooterService:
    """Background service for proactive IDE troubleshooting"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.troubleshooter = None
        self.running = False

        if TROUBLESHOOTER_AVAILABLE:
            try:
                self.troubleshooter = JARVISProactiveIDETroubleshooter(project_root)
                logger.info("✅ Proactive IDE Troubleshooter service initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize troubleshooter: {e}")

    def start(self):
        """Start the service"""
        if not self.troubleshooter:
            logger.error("❌ Troubleshooter not available")
            return False

        if self.running:
            logger.info("ℹ️  Service already running")
            return True

        try:
            self.troubleshooter.start_monitoring()
            self.running = True
            logger.info("✅ Proactive IDE Troubleshooter service started")
            logger.info("   Monitoring interval: 5 seconds")
            logger.info("   Auto-fix enabled for proven patterns (>75% success rate)")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to start service: {e}")
            return False

    def stop(self):
        """Stop the service"""
        if not self.running:
            return

        try:
            if self.troubleshooter:
                self.troubleshooter.stop_monitoring()
            self.running = False
            logger.info("✅ Proactive IDE Troubleshooter service stopped")
        except Exception as e:
            logger.error(f"❌ Failed to stop service: {e}")

    def get_status(self) -> dict:
        """Get service status"""
        if not self.troubleshooter:
            return {"available": False}

        status = self.troubleshooter.get_status()
        status["service_running"] = self.running
        return status


def main():
    """Deploy and activate proactive troubleshooter"""
    import argparse

    parser = argparse.ArgumentParser(description="Deploy JARVIS Proactive IDE Troubleshooter")
    parser.add_argument("--start", action="store_true", help="Start the service")
    parser.add_argument("--stop", action="store_true", help="Stop the service")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon (keep running)")

    args = parser.parse_args()

    if not TROUBLESHOOTER_AVAILABLE:
        print("❌ Proactive IDE Troubleshooter not available")
        return 1

    project_root = Path(__file__).parent.parent.parent
    service = ProactiveTroubleshooterService(project_root)

    # Handle signals for graceful shutdown
    def signal_handler(sig, frame):
        print("\n🛑 Shutting down...")
        service.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if args.start:
        if service.start():
            print("✅ Proactive IDE Troubleshooter service started")
            if args.daemon:
                print("   Running as daemon (press Ctrl+C to stop)")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    service.stop()
        else:
            print("❌ Failed to start service")
            return 1

    if args.stop:
        service.stop()
        print("✅ Service stopped")

    if args.status:
        status = service.get_status()
        print("\n" + "="*80)
        print("PROACTIVE IDE TROUBLESHOOTER SERVICE STATUS")
        print("="*80)
        for key, value in status.items():
            print(f"  {key}: {value}")
        print("="*80)

    if args.daemon and not args.start:
        # Start and run as daemon
        if service.start():
            print("✅ Service started as daemon")
            print("   Press Ctrl+C to stop")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                service.stop()
        else:
            return 1

    if not any([args.start, args.stop, args.status, args.daemon]):
        parser.print_help()

    return 0


if __name__ == "__main__":


    exit(main())