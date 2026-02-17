#!/usr/bin/env python3
"""
JARVIS Problem Management SLA Notifier
Problem Management Team notifies JARVIS of:
- SLAs due to expire
- Unserviced SLAs

Tags: #PROBLEM_MANAGEMENT #SLA #NOTIFICATIONS @JARVIS @C3PO @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, Any

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from jarvis_sla_management_system import JARVISSLAManagementSystem
    from jarvis_management_supervision import JARVISManagementSupervision
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

logger = get_logger("JARVISProblemManagementSLANotifier")


def notify_jarvis_sla_issues():
    try:
        """Problem Management Team notifies JARVIS of SLA issues"""
        logger.info("=" * 80)
        logger.info("📢 PROBLEM MANAGEMENT: Notifying JARVIS of SLA Issues")
        logger.info("=" * 80)
        logger.info("   Team: Problem Management")
        logger.info("   Responsibility: Handle all SLAs and notify JARVIS")

        project_root = Path(__file__).parent.parent.parent

        # Initialize systems
        sla_system = JARVISSLAManagementSystem(project_root)
        supervision_system = JARVISManagementSupervision(project_root)

        # Check for expiring SLAs
        expiring = sla_system.check_expiring_slas()
        if expiring:
            logger.warning(f"⚠️  Found {len(expiring)} expiring SLAs - Notifying JARVIS")
            sla_system.notify_jarvis(expiring, "expiring")

        # Check for expired SLAs
        expired = sla_system.check_expired_slas()
        if expired:
            logger.error(f"❌ Found {len(expired)} expired SLAs - Notifying JARVIS")
            sla_system.notify_jarvis(expired, "expired")

        # Check for unserviced SLAs
        unserviced = sla_system.check_unserviced_slas()
        if unserviced:
            logger.error(f"❌ Found {len(unserviced)} unserviced SLAs - Notifying JARVIS")
            sla_system.notify_jarvis(unserviced, "unserviced")

        # Notify JARVIS of all management issues
        notifications = supervision_system.notify_jarvis_management_issues()

        logger.info(f"\n📊 Problem Management Notification Summary:")
        logger.info(f"   Expiring SLAs: {len(expiring)}")
        logger.info(f"   Expired SLAs: {len(expired)}")
        logger.info(f"   Unserviced SLAs: {len(unserviced)}")
        logger.info(f"   Total Management Issues: {notifications.get('total_issues', 0)}")

        return {
            "expiring": len(expiring),
            "expired": len(expired),
            "unserviced": len(unserviced),
            "total_issues": notifications.get('total_issues', 0)
        }


    except Exception as e:
        logger.error(f"Error in notify_jarvis_sla_issues: {e}", exc_info=True)
        raise
def main():
    """CLI interface"""
    print("="*80)
    print("📢 PROBLEM MANAGEMENT SLA NOTIFIER")
    print("="*80)
    print()
    print("Team: Problem Management")
    print("Responsibility: Notify JARVIS of SLA issues")
    print()

    result = notify_jarvis_sla_issues()

    print()
    print("="*80)
    print("✅ NOTIFICATIONS COMPLETE")
    print("="*80)
    print(f"Expiring: {result['expiring']}")
    print(f"Expired: {result['expired']}")
    print(f"Unserviced: {result['unserviced']}")
    print(f"Total Issues: {result['total_issues']}")
    print()


if __name__ == "__main__":


    main()