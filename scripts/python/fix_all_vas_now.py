#!/usr/bin/env python3
"""
Fix All VAs Now

Immediately fix and launch all failed Virtual Assistants.

Tags: #VA #FIX #ALL #IMMEDIATE @JARVIS @LUMINA
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from va_health_detector import VAHealthDetector
from lumina_logger import get_logger

logger = get_logger("FixAllVAsNow")

def main():
    """Fix all VAs immediately"""
    logger.info("=" * 80)
    logger.info("🔧 FIXING ALL VAs NOW")
    logger.info("=" * 80)
    logger.info("")

    # Initialize detector
    detector = VAHealthDetector()

    # Check health
    logger.info("📋 Checking VA health...")
    health = detector.check_va_health()

    # Fix failed VAs
    logger.info("")
    logger.info("🔧 Fixing failed VAs...")
    results = detector.fix_failed_vas(health)

    # Report
    logger.info("")
    logger.info("=" * 80)
    logger.info("✅ VA FIX COMPLETE")
    logger.info("=" * 80)
    logger.info(f"   Fixed: {len(results['fixed'])}")
    logger.info(f"   Failed to Fix: {len(results['failed_to_fix'])}")
    logger.info(f"   Skipped: {len(results['skipped'])}")
    logger.info("")

    if results['fixed']:
        logger.info("   ✅ Successfully launched:")
        for fix in results['fixed']:
            logger.info(f"      • {fix.get('va_name', fix.get('va_id'))}")

    if results['failed_to_fix']:
        logger.info("")
        logger.warning("   ⚠️  Failed to launch:")
        for fail in results['failed_to_fix']:
            logger.warning(f"      • {fail.get('va_name', fail.get('va_id'))}: {fail.get('reason')}")

    logger.info("")
    return 0

if __name__ == "__main__":


    sys.exit(main())