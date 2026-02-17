#!/usr/bin/env python3
"""
Migrate Docker Volumes via Export
Uses Docker volume export commands to migrate volumes to NAS

Tags: #DOIT #NAS_MIGRATION #DOCKER #V3_VALIDATION @JARVIS @LUMINA
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
    logger = get_comprehensive_logger("DockerVolumeExport")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("DockerVolumeExport")

NAS_IP = "<NAS_PRIMARY_IP>"
TARGET_BASE = Path(f"\\\\{NAS_IP}\\docker\\volumes")


def list_volumes():
    """List all Docker volumes"""
    logger.info("📋 Listing Docker volumes...")
    try:
        result = subprocess.run(
            ["docker", "volume", "ls", "--format", "{{.Name}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            volumes = [v.strip() for v in result.stdout.strip().split('\n') if v.strip()]
            logger.info(f"   ✅ Found {len(volumes)} volumes")
            return volumes
        return []
    except Exception as e:
        logger.error(f"   ❌ Error: {e}")
        return []


def export_volume(volume_name, target_path):
    """Export a Docker volume using docker run with tar"""
    logger.info(f"   📦 Exporting volume: {volume_name}")

    target_path.mkdir(parents=True, exist_ok=True)
    tar_file = target_path / f"{volume_name}.tar"

    # Use docker run to export volume
    # docker run --rm -v volume_name:/data -v target:/backup alpine tar czf /backup/volume.tar -C /data .
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{volume_name}:/data:ro",
        "-v", f"{target_path}:/backup",
        "alpine:latest",
        "tar", "czf", f"/backup/{volume_name}.tar", "-C", "/data", "."
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour per volume
        )

        if result.returncode == 0 and tar_file.exists():
            size_mb = tar_file.stat().st_size / (1024**2)
            logger.info(f"      ✅ Exported: {size_mb:.2f} MB")
            return True
        else:
            logger.warning(f"      ⚠️  Export failed: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        logger.warning(f"      ⚠️  Export timed out")
        return False
    except Exception as e:
        logger.error(f"      ❌ Error: {e}")
        return False


def main():
    try:
        """Migrate Docker volumes via export"""
        logger.info("=" * 80)
        logger.info("🐳 DOCKER VOLUME MIGRATION VIA EXPORT")
        logger.info("=" * 80)
        logger.info("")

        # Ensure target exists
        if not TARGET_BASE.exists():
            logger.error(f"❌ Target does not exist: {TARGET_BASE}")
            return

        # List volumes
        volumes = list_volumes()
        if not volumes:
            logger.error("❌ No volumes found")
            return

        logger.info("")
        logger.info(f"📦 Exporting {len(volumes)} volumes...")
        logger.info("")

        exported = 0
        failed = 0

        for i, volume in enumerate(volumes, 1):
            logger.info(f"[{i}/{len(volumes)}] {volume}")
            if export_volume(volume, TARGET_BASE):
                exported += 1
            else:
                failed += 1
            logger.info("")

        logger.info("=" * 80)
        logger.info("📊 EXPORT SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total volumes: {len(volumes)}")
        logger.info(f"Exported: {exported}")
        logger.info(f"Failed: {failed}")
        logger.info("")

        if exported == len(volumes):
            logger.info("✅ All volumes exported successfully")
        elif exported > 0:
            logger.warning(f"⚠️  Partial success: {exported}/{len(volumes)} volumes exported")
        else:
            logger.error("❌ No volumes exported")
        logger.info("")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()