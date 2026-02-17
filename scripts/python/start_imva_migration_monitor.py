#!/usr/bin/env python3
"""
Start IMVA NAS Migration Monitor

Starts the IMVA NAS Migration Monitor in background to provide periodic status updates.
Can be run as a daemon or integrated with IMVA GUI.

Tags: #IMVA #NAS #MIGRATION #MONITORING @JARVIS @LUMINA
"""

import sys
import signal
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from imva_nas_migration_monitor import IMVANASMigrationMonitor
from lumina_logger import get_logger

logger = get_logger("StartIMVAMigrationMonitor")


def main():
    """Start IMVA NAS Migration Monitor."""
    project_root = Path(__file__).parent.parent.parent

    # Create monitor with 30-second update interval
    monitor = IMVANASMigrationMonitor(project_root, update_interval=30)

    # Update once immediately
    logger.info("🔄 Updating migration status...")
    monitor.update_imva_status()

    # Start continuous monitoring
    logger.info("🚀 Starting IMVA NAS Migration Monitor...")
    logger.info(f"   Update interval: 30 seconds")
    logger.info(f"   Status file: {monitor.imva_status_file}")
    logger.info("   Press Ctrl+C to stop")

    monitor.start_monitoring()

    # Handle graceful shutdown
    def signal_handler(sig, frame):
        logger.info("\n⏸️ Stopping monitor...")
        monitor.stop_monitoring()
        logger.info("✅ Monitor stopped")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Keep running
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":


    main()