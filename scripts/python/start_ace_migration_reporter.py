#!/usr/bin/env python3
"""
Start ACE Migration Status Reporter

Starts ACE (Anakin Combat Virtual Assistant) migration status reporter in background.

Tags: #ACE #NAS #MIGRATION #STATUS @JARVIS @LUMINA
"""

import signal
import sys
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from ace_migration_status_reporter import ACEMigrationStatusReporter
from lumina_logger import get_logger

logger = get_logger("StartACEMigrationReporter")


def main():
    """Start ACE Migration Status Reporter."""
    project_root = Path(__file__).parent.parent.parent

    # Create reporter with 60-second update interval
    reporter = ACEMigrationStatusReporter(project_root, update_interval=60)

    # Report once immediately
    logger.info("🔄 Reporting migration status...")
    reporter.report_status()

    # Start continuous reporting
    logger.info("🚀 Starting ACE Migration Status Reporter...")
    logger.info("   Update interval: 60 seconds")
    logger.info(f"   Status file: {reporter.ace_status_file}")
    logger.info(f"   Voice file: {reporter.ace_voice_file}")
    logger.info("   Press Ctrl+C to stop")

    reporter.start_reporting()

    # Handle graceful shutdown
    def signal_handler(sig, frame):
        logger.info("\n⏸️ Stopping reporter...")
        reporter.stop_reporting()
        logger.info("✅ Reporter stopped")
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