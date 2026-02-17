#!/usr/bin/env python3
"""
Deploy and Start NAS Migration on NAS KronScheduler
Deploys the cron job and optionally starts it immediately
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts" / "python"))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("DeployAndStartNASMigration")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("DeployAndStartNASMigration")

NAS_HOST = "<NAS_PRIMARY_IP>"
NAS_USER = "mlesn"
NAS_SCRIPT_PATH = "/volume1/docker/lumina/scripts/python/real_deal_migration_v3.py"
LOCAL_SCRIPT = project_root / "scripts" / "python" / "real_deal_migration_v3.py"

def run_ssh_command(cmd, timeout=10):
    """Run SSH command with timeout"""
    full_cmd = f'ssh {NAS_USER}@{NAS_HOST} "{cmd}"'
    try:
        result = subprocess.run(
            full_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "SSH command timed out"
    except Exception as e:
        return False, "", str(e)

def run_scp_command(local_path, remote_path, timeout=30):
    """Copy file to NAS via SCP"""
    full_cmd = f'scp "{local_path}" {NAS_USER}@{NAS_HOST}:"{remote_path}"'
    try:
        result = subprocess.run(
            full_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "SCP command timed out"
    except Exception as e:
        return False, "", str(e)

def deploy_migration():
    try:
        """Deploy NAS migration cron job"""
        logger.info("=" * 80)
        logger.info("🚀 DEPLOYING NAS MIGRATION TO NAS KRONSCHEDULER")
        logger.info("=" * 80)
        logger.info("")

        # Check local script
        if not LOCAL_SCRIPT.exists():
            logger.error(f"❌ Migration script not found: {LOCAL_SCRIPT}")
            return False

        logger.info(f"✅ Local script found: {LOCAL_SCRIPT}")
        logger.info("")

        # Check if script exists on NAS
        logger.info("🔍 Checking if script exists on NAS...")
        success, stdout, stderr = run_ssh_command(f"test -f {NAS_SCRIPT_PATH} && echo 'EXISTS' || echo 'NOT_FOUND'")

        if not success:
            logger.warning(f"   ⚠️  Could not check NAS (SSH may need setup): {stderr}")
            logger.info("   📤 Attempting to copy script to NAS...")

            # Ensure directory exists
            script_dir = str(Path(NAS_SCRIPT_PATH).parent)
            run_ssh_command(f"mkdir -p {script_dir}", timeout=5)

            # Copy script
            success, stdout, stderr = run_scp_command(str(LOCAL_SCRIPT), NAS_SCRIPT_PATH)
            if success:
                logger.info("   ✅ Script copied to NAS")
            else:
                logger.error(f"   ❌ Failed to copy script: {stderr}")
                logger.info("   ℹ️  You may need to copy manually or set up SSH keys")
                return False
        elif "NOT_FOUND" in stdout:
            logger.info("   ⚠️  Script not found on NAS")
            logger.info("   📤 Copying script to NAS...")

            script_dir = str(Path(NAS_SCRIPT_PATH).parent)
            run_ssh_command(f"mkdir -p {script_dir}", timeout=5)

            success, stdout, stderr = run_scp_command(str(LOCAL_SCRIPT), NAS_SCRIPT_PATH)
            if success:
                logger.info("   ✅ Script copied to NAS")
            else:
                logger.error(f"   ❌ Failed to copy script: {stderr}")
                return False
        else:
            logger.info("   ✅ Script already exists on NAS")

        logger.info("")

        # Get existing crontab
        logger.info("📋 Getting existing crontab...")
        success, stdout, stderr = run_ssh_command("crontab -l 2>/dev/null || echo ''")

        existing_cron = stdout.strip() if success else ""
        cron_lines = []

        if existing_cron:
            # Filter out existing NAS Migration entries
            for line in existing_cron.split('\n'):
                if line.strip() and '# NAS Migration' not in line:
                    cron_lines.append(line)
            logger.info(f"   ✅ Found {len(cron_lines)} existing cron jobs")
        else:
            logger.info("   ℹ️  No existing cron jobs")

        logger.info("")

        # Add NAS Migration cron job
        logger.info("📤 Adding NAS Migration cron job...")
        migration_cron = f"0 2 * * * cd /volume1/docker/lumina && python {NAS_SCRIPT_PATH} >> /volume1/docker/lumina/logs/nas_migration_$(date +%Y%m%d).log 2>&1 # NAS Migration - Ollama Models"
        cron_lines.append(migration_cron)

        # Write crontab
        all_cron = '\n'.join(cron_lines) + '\n'
        success, stdout, stderr = run_ssh_command(f"echo '{all_cron}' | crontab -")

        if success:
            logger.info("   ✅ NAS Migration cron job deployed")
        else:
            logger.error(f"   ❌ Failed to deploy cron job: {stderr}")
            return False

        logger.info("")

        # Verify
        logger.info("🔍 Verifying deployment...")
        success, stdout, stderr = run_ssh_command("crontab -l | grep 'NAS Migration'")

        if success and "NAS Migration" in stdout:
            logger.info("   ✅ Migration cron job verified:")
            for line in stdout.strip().split('\n'):
                if 'NAS Migration' in line:
                    logger.info(f"      {line.strip()}")
        else:
            logger.warning("   ⚠️  Could not verify cron job (may need manual check)")

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ DEPLOYMENT COMPLETE")
        logger.info("=" * 80)
        logger.info("")
        logger.info("NAS Migration scheduled:")
        logger.info("  Schedule: Daily at 2:00 AM")
        logger.info(f"  Script: {NAS_SCRIPT_PATH}")
        logger.info("  Logs: /volume1/docker/lumina/logs/nas_migration_YYYYMMDD.log")
        logger.info("")

        return True

    except Exception as e:
        logger.error(f"Error in deploy_migration: {e}", exc_info=True)
        raise
def start_migration_now():
    """Start migration immediately (for testing)"""
    logger.info("=" * 80)
    logger.info("🚀 STARTING NAS MIGRATION NOW")
    logger.info("=" * 80)
    logger.info("")

    logger.info("📤 Executing migration script on NAS...")
    success, stdout, stderr = run_ssh_command(
        f"cd /volume1/docker/lumina && python {NAS_SCRIPT_PATH}",
        timeout=300  # 5 minute timeout for migration
    )

    if success:
        logger.info("   ✅ Migration started")
        if stdout:
            logger.info(f"   Output: {stdout[:500]}")  # First 500 chars
    else:
        logger.error(f"   ❌ Failed to start migration: {stderr}")
        if stdout:
            logger.info(f"   Output: {stdout[:500]}")
        return False

    logger.info("")
    logger.info("=" * 80)
    logger.info("✅ MIGRATION STARTED")
    logger.info("=" * 80)
    logger.info("")

    return True

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Deploy and/or start NAS migration")
    parser.add_argument("--deploy", action="store_true", help="Deploy cron job to NAS")
    parser.add_argument("--start", action="store_true", help="Start migration immediately")
    parser.add_argument("--both", action="store_true", help="Deploy and start")

    args = parser.parse_args()

    if args.both or (not args.deploy and not args.start):
        # Default: do both
        if deploy_migration():
            logger.info("")
            start_migration_now()
    elif args.deploy:
        deploy_migration()
    elif args.start:
        start_migration_now()

    sys.exit(0)
