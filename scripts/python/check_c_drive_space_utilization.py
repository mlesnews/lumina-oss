#!/usr/bin/env python3
"""
Check C Drive Space Utilization

The REAL @ASK: C drive is at 90% utilization - migration is URGENT, not "complete"

@DOIT #SPACE-UTILIZATION #C-DRIVE #MIGRATION-URGENT
"""

import sys
import subprocess
from pathlib import Path
from typing import Dict, Any
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CDriveSpaceCheck")


def check_c_drive_space() -> Dict[str, Any]:
    """Check C drive space utilization - THE REAL @ASK"""
    logger.info("=" * 80)
    logger.info("💾 C DRIVE SPACE UTILIZATION CHECK")
    logger.info("=" * 80)
    logger.info("   The REAL @ASK: Space utilization, not migration completion status")
    logger.info("")

    try:
        # Use PowerShell to get accurate disk space
        ps_command = """
        $drive = Get-PSDrive C
        $usedGB = [math]::Round($drive.Used / 1GB, 2)
        $freeGB = [math]::Round($drive.Free / 1GB, 2)
        $totalGB = [math]::Round(($drive.Used + $drive.Free) / 1GB, 2)
        $usedPercent = [math]::Round(($drive.Used / ($drive.Used + $drive.Free)) * 100, 1)
        $freePercent = [math]::Round(($drive.Free / ($drive.Used + $drive.Free)) * 100, 1)

        @{
            used_gb = $usedGB
            free_gb = $freeGB
            total_gb = $totalGB
            used_percent = $usedPercent
            free_percent = $freePercent
            status = if ($usedPercent -ge 90) { 'CRITICAL' } elseif ($usedPercent -ge 80) { 'WARNING' } else { 'OK' }
        } | ConvertTo-Json
        """

        result = subprocess.run(
            ["powershell", "-Command", ps_command],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            import json
            space_data = json.loads(result.stdout)

            logger.info("📊 C DRIVE SPACE STATUS")
            logger.info(f"   Used: {space_data['used_gb']} GB ({space_data['used_percent']}%)")
            logger.info(f"   Free: {space_data['free_gb']} GB ({space_data['free_percent']}%)")
            logger.info(f"   Total: {space_data['total_gb']} GB")
            logger.info(f"   Status: {space_data['status']}")
            logger.info("")

            if space_data['used_percent'] >= 90:
                logger.error("🚨 CRITICAL: C drive is at 90%+ utilization!")
                logger.error("   MIGRATION IS URGENT - NOT 'COMPLETE'")
                logger.error("   The migration tracker is WRONG - files still on C drive")
                logger.error("")
                logger.error("   ACTION REQUIRED:")
                logger.error("   1. Check what's taking up space on C drive")
                logger.error("   2. Migrate my_projects to NAS/D drive IMMEDIATELY")
                logger.error("   3. Free up space to prevent system issues")
            elif space_data['used_percent'] >= 80:
                logger.warning("⚠️  WARNING: C drive is at 80%+ utilization")
                logger.warning("   Migration recommended soon")
            else:
                logger.info("✅ C drive space is OK")

            return {
                "success": True,
                "space_data": space_data,
                "migration_urgent": space_data['used_percent'] >= 90,
                "migration_recommended": space_data['used_percent'] >= 80
            }
        else:
            logger.error(f"❌ Failed to check disk space: {result.stderr}")
            return {"success": False, "error": result.stderr}

    except Exception as e:
        logger.error(f"❌ Error checking disk space: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


def check_my_projects_size() -> Dict[str, Any]:
    """Check size of my_projects directory on C drive"""
    my_projects_path = Path("C:/Users/mlesn/Dropbox/my_projects")

    if not my_projects_path.exists():
        logger.warning(f"⚠️  my_projects path not found: {my_projects_path}")
        return {"exists": False}

    logger.info("📁 Checking my_projects directory size...")

    try:
        # Use PowerShell to get directory size
        ps_command = f"""
        $path = '{my_projects_path}'
        $size = (Get-ChildItem -Path $path -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        $sizeGB = [math]::Round($size / 1GB, 2)
        $fileCount = (Get-ChildItem -Path $path -Recurse -File -ErrorAction SilentlyContinue).Count

        @{{
            size_gb = $sizeGB
            file_count = $fileCount
            path = $path
        }} | ConvertTo-Json
        """

        result = subprocess.run(
            ["powershell", "-Command", ps_command],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            import json
            dir_data = json.loads(result.stdout)

            logger.info(f"   Size: {dir_data['size_gb']} GB")
            logger.info(f"   Files: {dir_data['file_count']:,}")
            logger.info("")

            return {
                "exists": True,
                "size_gb": dir_data['size_gb'],
                "file_count": dir_data['file_count']
            }
        else:
            logger.warning(f"⚠️  Could not calculate directory size: {result.stderr}")
            return {"exists": True, "size_unknown": True}

    except Exception as e:
        logger.warning(f"⚠️  Error checking directory size: {e}")
        return {"exists": True, "error": str(e)}


def main():
    """Main execution"""
    logger.info("")

    # Check C drive space
    space_result = check_c_drive_space()

    # Check my_projects size
    my_projects_info = check_my_projects_size()

    logger.info("=" * 80)
    logger.info("📋 SUMMARY")
    logger.info("=" * 80)

    if space_result.get("success"):
        space_data = space_result["space_data"]
        logger.info(f"C Drive Utilization: {space_data['used_percent']}%")

        if space_result.get("migration_urgent"):
            logger.error("🚨 MIGRATION IS URGENT - C drive at 90%+")
            logger.error("   The migration tracker showing 'complete' is WRONG")
            logger.error("   Files are still on C drive taking up space")

        if my_projects_info.get("exists"):
            size_gb = my_projects_info.get("size_gb", 0)
            if size_gb > 0:
                logger.info(f"my_projects on C drive: {size_gb} GB")
                logger.info(f"   This needs to be migrated to NAS/D drive")

    logger.info("=" * 80)

    return 0 if not space_result.get("migration_urgent") else 1


if __name__ == "__main__":


    sys.exit(main())