#!/usr/bin/env python3
"""
Complete Docker Volume Migration via Export
Exports all Docker volumes individually to NAS

Tags: #DOIT #NAS_MIGRATION #DOCKER #V3_VALIDATION @JARVIS @LUMINA
"""

import sys
import subprocess
import time
import json
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("DockerVolumeExportComplete")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("DockerVolumeExportComplete")

NAS_IP = "<NAS_PRIMARY_IP>"
TARGET_BASE = Path(f"\\\\{NAS_IP}\\docker\\volumes")
# Docker on Windows doesn't support UNC paths directly, so use local temp first
TEMP_EXPORT_DIR = Path("C:\\temp\\docker_volume_exports")


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


def get_volume_size(volume_name):
    """Get approximate size of a volume"""
    try:
        result = subprocess.run(
            ["docker", "run", "--rm", "-v", f"{volume_name}:/data:ro", "alpine:latest", "du", "-sh", "/data"],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            # Parse output like "1.2G    /data"
            size_str = result.stdout.strip().split()[0]
            return size_str
        return "unknown"
    except:
        return "unknown"


def export_volume(volume_name, temp_path, nas_path):
    """Export a Docker volume using docker run with tar"""
    logger.info(f"   📦 Exporting: {volume_name}")

    # Use local temp directory (Docker on Windows doesn't support UNC paths)
    temp_path.mkdir(parents=True, exist_ok=True)
    temp_tar_file = temp_path / f"{volume_name}.tar.gz"

    # Get volume size estimate
    size_estimate = get_volume_size(volume_name)
    logger.info(f"      Size estimate: {size_estimate}")

    # Use docker run to export volume to local temp
    # docker run --rm -v volume_name:/data:ro -v temp_path:/backup alpine tar czf /backup/volume.tar.gz -C /data .
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{volume_name}:/data:ro",
        "-v", f"{temp_path}:/backup",
        "alpine:latest",
        "tar", "czf", f"/backup/{volume_name}.tar.gz", "-C", "/data", "."
    ]

    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=7200  # 2 hours per volume
        )

        elapsed = time.time() - start_time

        if result.returncode == 0 and temp_tar_file.exists():
            size_mb = temp_tar_file.stat().st_size / (1024**2)
            logger.info(f"      ✅ Exported to temp: {size_mb:.2f} MB in {elapsed:.1f}s")

            # Copy to NAS
            nas_path.mkdir(parents=True, exist_ok=True)
            nas_tar_file = nas_path / f"{volume_name}.tar.gz"
            logger.info(f"      📤 Copying to NAS...")

            import shutil
            shutil.copy2(temp_tar_file, nas_tar_file)

            if nas_tar_file.exists():
                logger.info(f"      ✅ Copied to NAS: {nas_tar_file}")
                # Clean up temp file
                temp_tar_file.unlink()
                return True, size_mb
            else:
                logger.warning(f"      ⚠️  NAS copy failed")
                return False, 0
        else:
            logger.warning(f"      ⚠️  Export failed: {result.stderr[:200]}")
            return False, 0
    except subprocess.TimeoutExpired:
        logger.warning(f"      ⚠️  Export timed out after 2 hours")
        return False, 0
    except Exception as e:
        logger.error(f"      ❌ Error: {e}")
        return False, 0


def main():
    try:
        """Migrate all Docker volumes via export"""
        logger.info("=" * 80)
        logger.info("🐳 COMPLETE DOCKER VOLUME MIGRATION VIA EXPORT")
        logger.info("=" * 80)
        logger.info("")

        # Ensure temp directory exists
        TEMP_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Using temp directory: {TEMP_EXPORT_DIR}")

        # Ensure NAS target exists
        if not TARGET_BASE.exists():
            logger.warning(f"⚠️  NAS target does not exist: {TARGET_BASE}")
            logger.info("   Will create during copy, or check NAS share access")

        # List volumes
        volumes = list_volumes()
        if not volumes:
            logger.error("❌ No volumes found")
            return

        logger.info("")
        logger.info(f"📦 Exporting {len(volumes)} volumes to: {TARGET_BASE}")
        logger.info("   This will export each volume as a .tar.gz file")
        logger.info("")

        results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "volumes_total": len(volumes),
            "volumes_exported": 0,
            "volumes_failed": 0,
            "total_size_mb": 0,
            "volumes": []
        }

        exported = 0
        failed = 0
        total_size = 0

        for i, volume in enumerate(volumes, 1):
            logger.info(f"[{i}/{len(volumes)}] {volume}")
            success, size_mb = export_volume(volume, TEMP_EXPORT_DIR, TARGET_BASE)

            volume_result = {
                "name": volume,
                "success": success,
                "size_mb": round(size_mb, 2) if success else 0
            }
            results["volumes"].append(volume_result)

            if success:
                exported += 1
                total_size += size_mb
            else:
                failed += 1
            logger.info("")

        results["volumes_exported"] = exported
        results["volumes_failed"] = failed
        results["total_size_mb"] = round(total_size, 2)

        # Save results
        results_file = project_root / "data" / "nas_migration" / "docker_volumes_export_results.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

        logger.info("=" * 80)
        logger.info("📊 EXPORT SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total volumes: {len(volumes)}")
        logger.info(f"Exported: {exported}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Total size: {total_size / 1024:.2f} GB")
        logger.info("")
        logger.info(f"📄 Results saved: {results_file}")
        logger.info("")

        if exported == len(volumes):
            logger.info("✅ All volumes exported successfully")
            logger.info("   Volumes are now on NAS as .tar.gz files")
            logger.info("   To restore: Extract .tar.gz files to Docker volume mount points")
        elif exported > 0:
            logger.warning(f"⚠️  Partial success: {exported}/{len(volumes)} volumes exported")
            logger.info("   Check logs for failed volumes")
        else:
            logger.error("❌ No volumes exported")
        logger.info("")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()