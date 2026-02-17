#!/usr/bin/env python3
"""
Docker Migration using Volume Shadow Copy Service (VSS)
Creates a VSS snapshot to copy locked files

Tags: #DOIT #NAS_MIGRATION #DOCKER #VSS @JARVIS @LUMINA
"""

import sys
import subprocess
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("DockerVSSMigration")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("DockerVSSMigration")

NAS_IP = "<NAS_PRIMARY_IP>"
DOCKER_SOURCE = Path("C:\\Users\\mlesn\\AppData\\Local\\Docker")
DOCKER_TARGET = Path(f"\\\\{NAS_IP}\\docker\\Docker")


def check_admin():
    """Check if running as administrator"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


def create_vss_snapshot():
    """Create VSS snapshot using vssadmin or PowerShell"""
    logger.info("📸 Creating VSS snapshot...")

    if not check_admin():
        logger.error("   ❌ Administrator privileges required for VSS")
        logger.info("   Please run as Administrator")
        return None

    try:
        # Method 1: Use vssadmin (requires admin)
        result = subprocess.run(
            ["vssadmin", "create", "shadow", f"/For={DOCKER_SOURCE.drive}"],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            # Parse snapshot ID from output
            output = result.stdout
            # Look for "Shadow Copy Volume: \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopyX"
            import re
            match = re.search(r'HarddiskVolumeShadowCopy\d+', output)
            if match:
                snapshot_path = f"\\\\?\\GLOBALROOT\\Device\\{match.group()}"
                logger.info(f"   ✅ VSS snapshot created: {snapshot_path}")
                return snapshot_path
            else:
                logger.warning("   ⚠️  Snapshot created but path not found in output")
                return "UNKNOWN"
        else:
            logger.warning(f"   ⚠️  vssadmin failed: {result.stderr[:200]}")
            return None

    except Exception as e:
        logger.error(f"   ❌ Error creating VSS snapshot: {e}")
        return None


def copy_from_vss_snapshot(snapshot_path, snapshot_docker_path):
    """Copy Docker directory from VSS snapshot"""
    logger.info("📦 Copying from VSS snapshot...")
    logger.info(f"   Source: {snapshot_docker_path}")
    logger.info(f"   Target: {DOCKER_TARGET}")
    logger.info("")

    # Use robocopy from snapshot
    robocopy_cmd = [
        "robocopy",
        snapshot_docker_path,
        str(DOCKER_TARGET),
        "/E",  # Copy subdirectories
        "/R:5",  # Retry 5 times
        "/W:10",  # Wait 10 seconds
        "/MT:8",  # Multi-threaded
        "/LOG:" + str(project_root / "data" / "nas_migration" / "docker_vss_migration.log"),
        "/NP"  # No progress
    ]

    logger.info(f"   Running: {' '.join(robocopy_cmd)}")
    logger.info("   This may take a while...")
    logger.info("")

    try:
        result = subprocess.run(
            robocopy_cmd,
            capture_output=True,
            text=True,
            timeout=7200  # 2 hour timeout
        )

        # Robocopy returns 0-7 for success
        if result.returncode <= 7:
            logger.info("   ✅ Migration complete")
            return True
        else:
            logger.warning(f"   ⚠️  Robocopy returned code: {result.returncode}")
            return False
    except subprocess.TimeoutExpired:
        logger.warning("   ⚠️  Migration timed out")
        return False
    except Exception as e:
        logger.error(f"   ❌ Migration failed: {e}")
        return False


def main():
    """Migrate Docker using VSS snapshot"""
    logger.info("=" * 80)
    logger.info("📸 DOCKER MIGRATION VIA VSS SNAPSHOT")
    logger.info("=" * 80)
    logger.info("")

    # Check admin
    if not check_admin():
        logger.error("❌ This script requires Administrator privileges")
        logger.info("   Please run PowerShell as Administrator")
        return

    # Create VSS snapshot
    snapshot_path = create_vss_snapshot()
    if not snapshot_path:
        logger.error("❌ Failed to create VSS snapshot")
        return

    # Construct Docker path in snapshot
    # VSS path format: \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopyX\...
    # Need to append the Docker directory path
    snapshot_docker_path = f"{snapshot_path}\\Users\\mlesn\\AppData\\Local\\Docker"

    logger.info("")
    logger.info(f"📋 Snapshot Docker path: {snapshot_docker_path}")
    logger.info("")

    # Copy from snapshot
    success = copy_from_vss_snapshot(snapshot_path, snapshot_docker_path)

    logger.info("")
    logger.info("=" * 80)
    if success:
        logger.info("✅ VSS MIGRATION COMPLETE")
    else:
        logger.warning("⚠️  VSS MIGRATION PARTIAL")
    logger.info("=" * 80)
    logger.info("")

    # Note: VSS snapshot will be automatically deleted after a period
    # or can be manually deleted with: vssadmin delete shadows /all


if __name__ == "__main__":


    main()