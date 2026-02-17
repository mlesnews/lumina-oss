#!/usr/bin/env python3
"""
Monitor Neo Default Browser - Auto-Fix if Changed

Continuously monitors if Neo is the default browser and auto-fixes if it changes.

Tags: #NEO #BROWSER #MONITOR #AUTO_FIX @JARVIS @LUMINA
"""

import sys
import time
from pathlib import Path
from typing import Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MonitorNeoDefault")


def monitor_neo_default(interval_seconds: int = 60, max_checks: Optional[int] = None):
    """
    Monitor Neo default browser status and auto-fix if changed

    Args:
        interval_seconds: How often to check (default: 60 seconds)
        max_checks: Maximum number of checks (None = infinite)
    """
    from set_neo_as_default_browser import NeoDefaultBrowserManager

    manager = NeoDefaultBrowserManager(project_root)

    logger.info("=" * 80)
    logger.info("🔍 Starting Neo Default Browser Monitor")
    logger.info("=" * 80)
    logger.info(f"   Check interval: {interval_seconds} seconds")
    logger.info(f"   Max checks: {'Infinite' if max_checks is None else max_checks}")
    logger.info("")
    logger.info("   Press Ctrl+C to stop")
    logger.info("")

    check_count = 0

    try:
        while max_checks is None or check_count < max_checks:
            check_count += 1

            logger.info(f"   Check #{check_count} - {time.strftime('%H:%M:%S')}")

            result = manager.monitor_and_fix()

            if result["neo_is_default"]:
                logger.info("   ✅ Neo is default - all good")
            else:
                logger.warning("   ⚠️  Neo is NOT default - fix attempted")

            if check_count < (max_checks or float('inf')):
                logger.info(f"   ⏳ Waiting {interval_seconds} seconds until next check...")
                logger.info("")
                time.sleep(interval_seconds)

    except KeyboardInterrupt:
        logger.info("")
        logger.info("   ⏹️  Monitor stopped by user")
        logger.info(f"   Total checks: {check_count}")

    except Exception as e:
        logger.error(f"   ❌ Monitor error: {e}")
        raise

    logger.info("")
    logger.info("✅ Monitor stopped")


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Monitor Neo Default Browser")
    parser.add_argument("--interval", type=int, default=60, help="Check interval in seconds (default: 60)")
    parser.add_argument("--max-checks", type=int, default=None, help="Maximum number of checks (default: infinite)")
    parser.add_argument("--once", action="store_true", help="Check once and exit")

    args = parser.parse_args()

    if args.once:
        from set_neo_as_default_browser import NeoDefaultBrowserManager
        manager = NeoDefaultBrowserManager(project_root)
        result = manager.monitor_and_fix()
        print(f"\nResult: Neo is default = {result['neo_is_default']}")
    else:
        monitor_neo_default(
            interval_seconds=args.interval,
            max_checks=args.max_checks
        )


if __name__ == "__main__":


    main()