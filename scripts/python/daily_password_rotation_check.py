#!/usr/bin/env python3
"""
Daily Password Rotation Check

Scheduled task to check for credentials due for rotation.
Run this daily via cron/scheduled task.

Author: LUMINA Security Team
Date: 2025-01-24
Tags: @MARVIN @HK-47 @JARVIS
"""

import sys
from pathlib import Path

try:
    from scripts.python.password_rotation_manager import PasswordRotationManager
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    PasswordRotationManager = None


def main():
    """Daily rotation check"""
    logger = get_logger("DailyRotationCheck")

    if not PasswordRotationManager:
        logger.error("PasswordRotationManager not available")
        return 1

    try:
        manager = PasswordRotationManager()

        # Check for credentials due for rotation
        due_credentials = manager.check_rotations_due()

        if due_credentials:
            logger.warning(f"⚠️ {len(due_credentials)} credentials due for rotation")
            for cred in due_credentials:
                logger.warning(f"  - {cred.name} ({cred.priority.value}) - Due: {cred.next_rotation_due.date()}")

                # Auto-rotate if enabled
                policy = manager.ROTATION_POLICIES[cred.priority]
                if policy.auto_rotate:
                    logger.info(f"🔄 Auto-rotating credential: {cred.name}")
                    success = manager.rotate_credential(cred.name)
                    if success:
                        logger.info(f"✅ Successfully rotated: {cred.name}")
                    else:
                        logger.error(f"❌ Failed to rotate: {cred.name}")
        else:
            logger.info("✅ No credentials due for rotation")

        # Check upcoming rotations (next 7 days)
        upcoming = manager.check_upcoming_rotations(days_ahead=7)
        if upcoming:
            logger.info(f"📅 {len(upcoming)} credentials with upcoming rotations (next 7 days)")
            for cred, days_until in upcoming:
                logger.info(f"  - {cred.name} ({cred.priority.value}) - {days_until} days until rotation")

        # Get status
        status = manager.get_rotation_status()
        logger.info(f"📊 Rotation Status: {status['total_credentials']} total, {status['due_for_rotation']} due, {status['upcoming_rotations']} upcoming")

        return 0

    except Exception as e:
        logger.error(f"❌ Error during rotation check: {e}")
        return 1


if __name__ == "__main__":

    sys.exit(main())