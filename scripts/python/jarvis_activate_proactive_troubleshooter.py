#!/usr/bin/env python3
"""
JARVIS Activate Proactive IDE Troubleshooter

Deploys and activates the proactive IDE troubleshooter system.

@CURSOR @IDE #TROUBLESHOOTING #ACTIVATION #DEPLOYMENT
"""

import sys
import signal
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

logger = get_logger("JARVISActivateProactiveTroubleshooter")

try:
    from jarvis_proactive_ide_troubleshooter import JARVISProactiveIDETroubleshooter
    TROUBLESHOOTER_AVAILABLE = True
except ImportError:
    TROUBLESHOOTER_AVAILABLE = False
    JARVISProactiveIDETroubleshooter = None
    logger.error("❌ Proactive IDE Troubleshooter not available")


def main():
    """Activate proactive IDE troubleshooter"""
    if not TROUBLESHOOTER_AVAILABLE:
        logger.error("❌ Proactive IDE Troubleshooter not available")
        return 1

    project_root = Path(__file__).parent.parent.parent
    troubleshooter = JARVISProactiveIDETroubleshooter(project_root)

    # Show status
    status = troubleshooter.get_status()
    print("\n" + "="*80)
    print("JARVIS PROACTIVE IDE TROUBLESHOOTER - DEPLOYMENT & ACTIVATION")
    print("="*80)
    print(f"Patterns Loaded: {status['error_patterns']}")
    print(f"Proven Patterns: {status['proven_patterns']}")
    print(f"Monitoring Active: {status['monitoring_active']}")
    print("="*80)

    # Start monitoring
    if not status['monitoring_active']:
        print("\n🚀 Starting proactive monitoring...")
        troubleshooter.start_monitoring()
        print("✅ Proactive monitoring started")
        print("   Monitoring interval: 5 seconds")
        print("   Auto-fix enabled for proven patterns (>75% success rate)")
        print("\n📊 Monitoring active - errors will be detected and fixed proactively")
        print("   Press Ctrl+C to stop")

        # Keep running
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping monitoring...")
            troubleshooter.stop_monitoring()
            print("✅ Monitoring stopped")
    else:
        print("\n✅ Monitoring already active")

    return 0


if __name__ == "__main__":


    exit(main())