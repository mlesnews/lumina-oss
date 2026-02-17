#!/usr/bin/env python3
"""
JARVIS Integrated Live Monitor

Integrates live monitoring with ask processing for real-time updates.

Tags: #INTEGRATED_MONITORING #LIVE_UPDATES #REAL_TIME @JARVIS @LUMINA
"""

import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger, setup_logging
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    setup_logging = lambda: None

logger = get_logger("JARVISIntegratedLiveMonitor")

# Import live monitor
try:
    from jarvis_ask_live_monitor import LiveMonitor
    LIVE_MONITOR_AVAILABLE = True
except ImportError:
    LIVE_MONITOR_AVAILABLE = False
    logger.warning("Live monitor not available")


def main():
    """Main entry point - Start integrated monitoring"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Integrated Live Monitor")
    parser.add_argument("--start", action="store_true", help="Start processing with live monitoring")
    parser.add_argument("--monitor-only", action="store_true", help="Monitor only (no processing)")
    parser.add_argument("--total", type=int, default=1190, help="Total asks to process")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent

    if not LIVE_MONITOR_AVAILABLE:
        logger.error("Live monitor not available")
        return

    monitor = LiveMonitor(project_root)

    if args.start:
        # Start processing in background
        logger.info("Starting ask processing with live monitoring...")
        process = subprocess.Popen(
            ["python", "scripts/python/jarvis_ask_processor.py", "--all-incomplete"],
            cwd=str(project_root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Start monitoring
        monitor.start_monitoring(args.total)

        try:
            # Monitor while processing
            while process.poll() is None:
                status = monitor.get_current_status()
                monitor.display_status(status)
                monitor.save_status(status)
                time.sleep(10)  # Update every 10 seconds

            # Processing complete
            monitor.stop_monitoring()
            logger.info("✅ Processing complete")

        except KeyboardInterrupt:
            logger.info("Stopping...")
            process.terminate()
            monitor.stop_monitoring()

    elif args.monitor_only:
        # Monitor only
        monitor.start_monitoring(args.total)
        try:
            while True:
                status = monitor.get_current_status()
                monitor.display_status(status)
                monitor.save_status(status)
                time.sleep(10)
        except KeyboardInterrupt:
            monitor.stop_monitoring()
    else:
        # Default: show status
        status = monitor.get_current_status()
        monitor.display_status(status)


if __name__ == "__main__":


    main()