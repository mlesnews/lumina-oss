#!/usr/bin/env python3
"""
Deploy SYPHON Scheduled Daemon to NAS KronScheduler

Deploys the SYPHON scheduled daemon to NAS KronScheduler (<SCHEDULER_HOSTNAME>)
for regularly scheduled task execution.

#JARVIS #LUMINA #SYPHON #DAEMON #NAS #KRONSCHEDULER #DEPLOYMENT
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("DeploySyphonDaemon")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("DeploySyphonDaemon")

try:
    from scripts.python.syphon_scheduled_daemon_nas_kron import SyphonScheduledDaemon
    from scripts.python.nas_kron_daemon_manager import NASKronDaemonManager
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    logger.error(f"❌ Missing dependencies: {e}")
    sys.exit(1)


def deploy_syphon_daemon_to_nas_kron(
    nas_kron_host: str = "<SCHEDULER_HOSTNAME>",
    schedule_hours: int = 6
) -> bool:
    """
    Deploy SYPHON Scheduled Daemon to NAS KronScheduler.

    Args:
        nas_kron_host: NAS KronScheduler hostname
        schedule_hours: Schedule interval in hours (default: 6)

    Returns:
        True if deployment successful, False otherwise
    """
    logger.info("="*80)
    logger.info("🚀 DEPLOYING SYPHON SCHEDULED DAEMON TO NAS KRONSCHEDULER")
    logger.info("="*80)
    logger.info(f"   NAS KronScheduler: {nas_kron_host}")
    logger.info(f"   Schedule: Every {schedule_hours} hours")
    logger.info("")

    try:
        # Initialize daemon
        daemon = SyphonScheduledDaemon(
            nas_kron_host=nas_kron_host,
            interval_hours=schedule_hours
        )

        # Initialize NAS Kron manager
        nas_kron = NASKronDaemonManager(project_root=project_root)

        # Create cron file
        logger.info("📅 Creating cron file...")
        cron_file = daemon.create_nas_kron_cron_file()

        if not cron_file.exists():
            logger.error("❌ Failed to create cron file")
            return False

        logger.info(f"✅ Cron file created: {cron_file}")

        # Deploy to NAS
        logger.info("📤 Deploying to NAS KronScheduler...")
        success = nas_kron.deploy_cron_to_nas(cron_file)

        if success:
            logger.info("="*80)
            logger.info("✅ SYPHON SCHEDULED DAEMON DEPLOYED SUCCESSFULLY")
            logger.info("="*80)
            logger.info(f"   NAS KronScheduler: {nas_kron_host}")
            logger.info(f"   Schedule: Every {schedule_hours} hours (0 */{schedule_hours} * * *)")
            logger.info(f"   Cron File: {cron_file}")
            logger.info("")
            logger.info("   Sources:")
            logger.info("     #internal: Filesystems (Priority 1, 24h interval)")
            logger.info("     #external: Email, Financial (Priority 2-3, 5-6h intervals)")
            logger.info("")
            logger.info("   Next Steps:")
            logger.info("     1. Verify cron job on NAS KronScheduler")
            logger.info("     2. Check logs: data/syphon_scheduled/logs/syphon_scheduled.log")
            logger.info("     3. Monitor results: data/syphon_scheduled/results/")
            logger.info("="*80)
            return True
        else:
            logger.error("❌ Failed to deploy to NAS KronScheduler")
            return False

    except Exception as e:
        logger.error(f"❌ Error deploying SYPHON daemon: {e}", exc_info=True)
        return False


def verify_deployment(nas_kron_host: str = "<SCHEDULER_HOSTNAME>") -> Dict[str, Any]:
    """
    Verify deployment status.

    Args:
        nas_kron_host: NAS KronScheduler hostname

    Returns:
        Dict with verification status
    """
    logger.info("🔍 Verifying deployment...")

    result = {
        "deployed": False,
        "cron_file_exists": False,
        "nas_accessible": False,
        "credentials_available": False,
        "details": {}
    }

    try:
        # Check cron file
        daemon = SyphonScheduledDaemon(nas_kron_host=nas_kron_host)
        cron_file = daemon.data_dir / "syphon_scheduled.cron"
        result["cron_file_exists"] = cron_file.exists()
        result["details"]["cron_file"] = str(cron_file)

        # Check NAS accessibility (test credentials)
        nas_kron = NASKronDaemonManager(project_root=project_root)
        credentials = nas_kron._get_credentials()
        result["credentials_available"] = credentials is not None
        result["nas_accessible"] = result["credentials_available"]

        if credentials:
            result["details"]["nas_host"] = credentials.get("host", "unknown")
            result["details"]["nas_port"] = credentials.get("port", "unknown")
            result["details"]["nas_username"] = credentials.get("username", "unknown")

        # Check if deployed (cron file exists and credentials available)
        result["deployed"] = result["cron_file_exists"] and result["nas_accessible"]

        logger.info(f"   Cron File: {'✅' if result['cron_file_exists'] else '❌'}")
        logger.info(f"   NAS Credentials: {'✅' if result['credentials_available'] else '❌'}")
        logger.info(f"   Deployment Status: {'✅ READY' if result['deployed'] else '⚠️  NOT READY'}")

        if result["deployed"]:
            logger.info("   ✅ All components ready for deployment")
        else:
            if not result["cron_file_exists"]:
                logger.info("   ⚠️  Cron file not created yet - run deployment first")
            if not result["credentials_available"]:
                logger.info("   ⚠️  NAS credentials not available - check Azure Key Vault")

    except Exception as e:
        logger.error(f"❌ Error verifying deployment: {e}")
        result["error"] = str(e)

    return result


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Deploy SYPHON Scheduled Daemon to NAS KronScheduler"
    )
    parser.add_argument(
        "--nas-kron-host",
        default="<SCHEDULER_HOSTNAME>",
        help="NAS KronScheduler hostname (default: <SCHEDULER_HOSTNAME>)"
    )
    parser.add_argument(
        "--schedule-hours",
        type=int,
        default=6,
        help="Schedule interval in hours (default: 6)"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify deployment status"
    )

    args = parser.parse_args()

    if args.verify:
        result = verify_deployment(nas_kron_host=args.nas_kron_host)
        sys.exit(0 if result.get("deployed", False) else 1)
    else:
        success = deploy_syphon_daemon_to_nas_kron(
            nas_kron_host=args.nas_kron_host,
            schedule_hours=args.schedule_hours
        )
        sys.exit(0 if success else 1)


if __name__ == "__main__":


    main()