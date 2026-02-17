#!/usr/bin/env python3
"""
Deploy HOMELAN Migration as NAS Cron One-Time Daemon

Deploys migration script to NAS and sets up one-time cron job.
Runs on NAS, survives PC reboots, auto-resumes if interrupted.

Tags: #HOMELAN #MIGRATION #NAS #CRON #ONE-TIME #RESUME @JARVIS @DOIT
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
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

logger = get_logger("DeployHOMELANNASCron")


def deploy_script_to_nas() -> bool:
    """Deploy migration script to NAS"""
    local_script = project_root / "scripts" / "nas" / "homelan_migration_one_time.sh"
    nas_script = Path("M:/scripts/homelan_migration_one_time.sh")

    if not local_script.exists():
        logger.error(f"Local script not found: {local_script}")
        return False

    try:
        # Check if NAS is accessible
        nas_root = Path("M:/")
        if not nas_root.exists():
            logger.error("NAS drive (M:\\) not accessible")
            logger.info("Please map network drive M: to \\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups")
            return False

        # Create directory if needed
        nas_script.parent.mkdir(parents=True, exist_ok=True)

        # Read and update script with proper paths
        script_content = local_script.read_text(encoding='utf-8')

        # Write to NAS
        nas_script.write_text(script_content, encoding='utf-8')

        logger.info(f"✅ Deployed script to NAS: {nas_script}")
        return True
    except Exception as e:
        logger.error(f"Failed to deploy script to NAS: {e}")
        return False


def create_cron_entry() -> str:
    """Create cron entry for one-time migration"""
    # Run every minute (cron will check if migration is needed)
    # Script has built-in completion flag to prevent re-running
    cron_entry = """# HOMELAN Storage Migration - One-Time NAS Cron Job
# Runs on NAS, survives PC reboots, auto-resumes if interrupted
# Generated: {timestamp}

# Run every minute (script checks completion flag internally)
* * * * * /volume1/backups/MATT_Backups/scripts/homelan_migration_one_time.sh >> /volume1/backups/MATT_Backups/logs/homelan_migration_$(date +\\%Y\\%m\\%d).log 2>&1

# Note: Script will exit immediately if completion flag exists
# Completion flag: /volume1/backups/MATT_Backups/logs/homelan_migration_complete.flag
""".format(timestamp=datetime.now().isoformat())

    return cron_entry


def deploy_cron_to_nas() -> bool:
    """Deploy cron entry to NAS"""
    cron_entry = create_cron_entry()
    nas_cron_file = Path("M:/cron/homelan_migration_one_time.cron")

    try:
        nas_root = Path("M:/")
        if not nas_root.exists():
            logger.error("NAS drive (M:\\) not accessible")
            return False

        # Create directory
        nas_cron_file.parent.mkdir(parents=True, exist_ok=True)

        # Write cron file
        nas_cron_file.write_text(cron_entry, encoding='utf-8')

        logger.info(f"✅ Created cron file: {nas_cron_file}")
        logger.info("")
        logger.info("To install on NAS, SSH to NAS and run:")
        logger.info(f"  cat {nas_cron_file} | crontab -")
        logger.info("")
        logger.info("Or add manually:")
        logger.info("  crontab -e")
        logger.info("  # Then add the line from the cron file")

        return True
    except Exception as e:
        logger.error(f"Failed to deploy cron to NAS: {e}")
        return False


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Deploy HOMELAN Migration as NAS Cron")
    parser.add_argument("--deploy-script", action="store_true", help="Deploy script to NAS")
    parser.add_argument("--deploy-cron", action="store_true", help="Deploy cron entry to NAS")
    parser.add_argument("--all", action="store_true", help="Deploy everything")

    args = parser.parse_args()

    print("="*80)
    print("🚀 DEPLOY HOMELAN MIGRATION AS NAS CRON ONE-TIME DAEMON")
    print("="*80)
    print()

    success = True

    if args.all or args.deploy_script:
        print("📦 Deploying script to NAS...")
        if not deploy_script_to_nas():
            success = False
        print()

    if args.all or args.deploy_cron:
        print("📅 Creating cron entry...")
        if not deploy_cron_to_nas():
            success = False
        print()

    if success:
        print("✅ Deployment complete!")
        print()
        print("Next steps:")
        print("1. SSH to NAS (<NAS_PRIMARY_IP>)")
        print("2. Make script executable: chmod +x /volume1/backups/MATT_Backups/scripts/homelan_migration_one_time.sh")
        print("3. Install cron: cat /volume1/backups/MATT_Backups/cron/homelan_migration_one_time.cron | crontab -")
        print("4. Verify: crontab -l")
    else:
        print("❌ Deployment had errors - check logs above")
        sys.exit(1)


if __name__ == "__main__":


    main()