#!/usr/bin/env python3
"""
Active Team Supervision Monitor

Continuously monitors team management and ensures:
A) Managers are supervised by higher-level AI/agents
B) Subordinates report completion status to managers/leads

Runs continuously to maintain @PEAK supervision.

Tags: #MANAGEMENT #SUPERVISION #MONITOR #ACTIVE #REQUIRED @PEAK @JARVIS @LUMINA
"""

import sys
import time
from pathlib import Path
from datetime import datetime

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

logger = get_logger("ActiveTeamSupervisionMonitor")

from team_management_supervision import TeamManagementSupervision


def run_active_supervision(check_interval=300):
    """
    Run active supervision monitoring

    Args:
        check_interval: Seconds between supervision checks (default: 5 minutes)
    """
    supervision = TeamManagementSupervision()

    logger.info("=" * 80)
    logger.info("🔄 ACTIVE TEAM SUPERVISION MONITOR")
    logger.info("=" * 80)
    logger.info("   @PEAK: Continuous supervision and reporting")
    logger.info(f"   Check interval: {check_interval}s ({check_interval/60:.1f} minutes)")
    logger.info("=" * 80)
    logger.info("")
    logger.info("📋 Supervision Hierarchy:")
    logger.info("   @jarvis (Top Level)")
    logger.info("   └─ @c3po (Reports to JARVIS)")
    logger.info("      └─ @r2d2 (Reports to C-3PO)")
    logger.info("         └─ Team Members (Report to R2-D2/C-3PO)")
    logger.info("")
    logger.info("🔄 Starting continuous monitoring...")
    logger.info("=" * 80)

    cycle = 0
    while True:
        cycle += 1
        logger.info("")
        logger.info(f"🔄 Supervision Cycle {cycle} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("-" * 80)

        try:
            # Process all managers
            results = supervision.process_all_managers()

            logger.info("")
            logger.info("📊 Cycle Summary:")
            logger.info(f"   Managers: {results['managers_processed']}")
            logger.info(f"   Reports: {results['reports_generated']}")
            logger.info(f"   Sent to Supervisors: {results['reports_sent']}")

            # Check for critical issues
            for manager_id, stats in results.get("managers", {}).items():
                if stats.get("health") == "critical":
                    logger.warning(f"⚠️  CRITICAL: {manager_id} team health is CRITICAL")
                    logger.warning(f"   Blocked tasks: {stats.get('blocked', 0)}")
                elif stats.get("health") == "at_risk":
                    logger.warning(f"⚠️  AT RISK: {manager_id} team health is AT RISK")

        except Exception as e:
            logger.error(f"❌ Error in supervision cycle: {e}")

        logger.info("")
        logger.info(f"⏳ Waiting {check_interval}s until next cycle...")
        time.sleep(check_interval)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Active Team Supervision Monitor")
    parser.add_argument("--interval", type=int, default=300, help="Check interval in seconds (default: 300 = 5 minutes)")
    parser.add_argument("--once", action="store_true", help="Run once and exit (no continuous monitoring)")
    args = parser.parse_args()

    if args.once:
        supervision = TeamManagementSupervision()
        supervision.process_all_managers()
    else:
        run_active_supervision(check_interval=args.interval)
