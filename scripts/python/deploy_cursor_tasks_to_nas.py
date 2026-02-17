#!/usr/bin/env python3
"""
Deploy Cursor Tasks to NAS Cron Scheduler
Converts Cursor tasks and deploys them to NAS automatically
#JARVIS #MANUS #NAS #CRON #DEPLOYMENT #AUTOMATION
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from convert_cursor_tasks_to_nas_cron import CursorTasksToNASCron
from nas_kron_daemon_manager import NASKronDaemonManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Convert and deploy Cursor tasks to NAS"""
    print("=" * 70)
    print("   DEPLOY CURSOR TASKS TO NAS CRON")
    print("=" * 70)
    print("")

    # Step 1: Convert tasks
    print("Step 1: Converting Cursor tasks to NAS cron format...")
    print("")

    converter = CursorTasksToNASCron(project_root)
    result = converter.convert_all()

    print(f"✅ Converted: {result['converted']} tasks")
    print(f"⏭️  Skipped: {result['skipped']} tasks (manual only)")
    print("")

    if result['converted'] == 0:
        print("⚠️  No tasks to deploy (all are manual-only)")
        return 0

    # Step 2: Deploy to NAS
    print("Step 2: Deploying cron tasks to NAS...")
    print("")

    cron_file = Path(result['output_files']['crontab'])

    if not cron_file.exists():
        logger.error(f"❌ Cron file not found: {cron_file}")
        return 1

    # Try Synology API first (better method)
    print("🤖 Attempting Synology DSM API deployment...")
    print("")

    try:
        from synology_ai_task_scheduler import SynologyAITaskScheduler
        scheduler = SynologyAITaskScheduler(project_root)
        results = scheduler.deploy_cursor_tasks(cron_file)

        if results["success"]:
            print("✅ Deployment via Synology API successful!")
            print(f"   Deployed: {len(results['deployed'])} tasks")
            if results["failed"]:
                print(f"   Failed: {len(results['failed'])} tasks")
            print("")
            return 0
        else:
            print("⚠️  Synology API deployment failed, trying SSH method...")
            print("")
    except Exception as e:
        print(f"⚠️  Synology API not available: {e}")
        print("   Falling back to SSH method...")
        print("")

    # Fallback to SSH method
    manager = NASKronDaemonManager(project_root)

    print(f"📤 Deploying via SSH: {cron_file}")
    print("")

    success = manager.deploy_cron_to_nas(cron_file, user="root")

    if success:
        print("")
        print("=" * 70)
        print("   ✅ DEPLOYMENT SUCCESSFUL")
        print("=" * 70)
        print("")
        print("Deployed Tasks:")
        for task in result['cron_tasks']:
            print(f"  • {task['name']} ({task['schedule']})")
        print("")
        print("Next Steps:")
        print("  1. Verify tasks are running: ssh to NAS and check crontab -l")
        print("  2. Monitor logs: Check /var/log/cron.log on NAS")
        print("  3. Test manually: Run one task manually to verify it works")
        print("")
        return 0
    else:
        print("")
        print("=" * 70)
        print("   ❌ DEPLOYMENT FAILED")
        print("=" * 70)
        print("")
        print("Troubleshooting:")
        print("  1. Check NAS SSH credentials in Azure Key Vault")
        print("  2. Verify NAS is accessible: ping <NAS_PRIMARY_IP>")
        print("  3. Check SSH connection: ssh admin@<NAS_PRIMARY_IP>")
        print("  4. Review generated cron file: scripts/nas/cron/cursor_tasks_crontab.txt")
        print("")
        return 1


if __name__ == "__main__":


    sys.exit(main())