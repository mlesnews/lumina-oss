#!/usr/bin/env python3
"""
JARVIS Monitor: Docker Volume Export Progress
Monitors and reports on Docker volume export status

Tags: #JARVIS #MONITORING #DOCKER #NAS_MIGRATION @JARVIS @LUMINA
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVISDockerExportMonitor")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("JARVISDockerExportMonitor")

TEMP_EXPORT_DIR = Path("C:\\temp\\docker_volume_exports")
NAS_VOLUMES_DIR = Path("\\\\<NAS_PRIMARY_IP>\\docker\\volumes")
RESULTS_FILE = project_root / "data" / "nas_migration" / "docker_volumes_export_results.json"


def get_docker_volumes():
    """Get list of all Docker volumes"""
    try:
        import subprocess
        result = subprocess.run(
            ["docker", "volume", "ls", "--format", "{{.Name}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return [v.strip() for v in result.stdout.strip().split('\n') if v.strip()]
        return []
    except:
        return []


def check_export_status():
    """Check current export status"""
    volumes = get_docker_volumes()
    total_volumes = len(volumes)

    # Check local temp exports
    temp_files = {}
    if TEMP_EXPORT_DIR.exists():
        for file in TEMP_EXPORT_DIR.glob("*.tar.gz"):
            volume_name = file.stem
            temp_files[volume_name] = {
                "path": str(file),
                "size_mb": round(file.stat().st_size / (1024**2), 2),
                "last_modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
            }

    # Check NAS exports
    nas_files = {}
    if NAS_VOLUMES_DIR.exists():
        for file in NAS_VOLUMES_DIR.glob("*.tar.gz"):
            volume_name = file.stem
            size = file.stat().st_size
            nas_files[volume_name] = {
                "path": str(file),
                "size_mb": round(size / (1024**2), 2),
                "last_modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat(),
                "complete": size > 1000  # More than 1KB means file copied
            }

    # Check results file for script status
    script_status = "unknown"
    if RESULTS_FILE.exists():
        try:
            with open(RESULTS_FILE, 'r') as f:
                results = json.load(f)
                script_status = results.get("status", "unknown")
        except:
            pass

    # Calculate progress
    exported_to_temp = len(temp_files)
    copied_to_nas = len([v for v in nas_files.values() if v.get("complete", False)])
    in_progress = exported_to_temp - copied_to_nas

    return {
        "timestamp": datetime.now().isoformat(),
        "total_volumes": total_volumes,
        "exported_to_temp": exported_to_temp,
        "copied_to_nas": copied_to_nas,
        "in_progress": in_progress,
        "remaining": total_volumes - exported_to_temp,
        "temp_files": temp_files,
        "nas_files": nas_files,
        "script_status": script_status,
        "progress_percent": round((exported_to_temp / total_volumes * 100), 1) if total_volumes > 0 else 0
    }


def generate_report(status):
    """Generate human-readable report"""
    logger.info("")
    logger.info("=" * 80)
    logger.info("🔍 JARVIS MONITOR: DOCKER VOLUME EXPORT STATUS")
    logger.info("=" * 80)
    logger.info("")

    logger.info(f"📊 Overall Progress: {status['progress_percent']}%")
    logger.info(f"   Total volumes: {status['total_volumes']}")
    logger.info(f"   Exported to temp: {status['exported_to_temp']}")
    logger.info(f"   Copied to NAS: {status['copied_to_nas']}")
    logger.info(f"   In progress: {status['in_progress']}")
    logger.info(f"   Remaining: {status['remaining']}")
    logger.info("")

    if status['temp_files']:
        logger.info("📦 Local Temp Exports:")
        total_temp_size = sum(v['size_mb'] for v in status['temp_files'].values())
        logger.info(f"   Files: {len(status['temp_files'])}")
        logger.info(f"   Total size: {total_temp_size:.2f} MB")
        logger.info("")

    if status['nas_files']:
        logger.info("📤 NAS Exports:")
        complete_nas = [v for v in status['nas_files'].values() if v.get('complete', False)]
        total_nas_size = sum(v['size_mb'] for v in complete_nas)
        logger.info(f"   Complete files: {len(complete_nas)}")
        logger.info(f"   Total size: {total_nas_size:.2f} MB")

        incomplete = [k for k, v in status['nas_files'].items() if not v.get('complete', False)]
        if incomplete:
            logger.info(f"   Incomplete files: {len(incomplete)}")
        logger.info("")

    # Recent activity
    if status['temp_files']:
        logger.info("🕐 Recent Activity:")
        recent = sorted(status['temp_files'].items(), 
                       key=lambda x: x[1]['last_modified'], 
                       reverse=True)[:3]
        for vol, info in recent:
            logger.info(f"   {vol[:20]}... - {info['size_mb']:.2f} MB - {info['last_modified'][:19]}")
        logger.info("")

    logger.info("=" * 80)
    logger.info("")


def monitor_loop(interval=30, max_iterations=None):
    try:
        """Monitor export progress in a loop"""
        logger.info("🔍 JARVIS Monitor: Starting Docker Volume Export monitoring...")
        logger.info(f"   Check interval: {interval} seconds")
        logger.info("")

        iteration = 0
        last_status = None

        while True:
            iteration += 1
            if max_iterations and iteration > max_iterations:
                break

            status = check_export_status()

            # Only log if status changed
            if status != last_status:
                generate_report(status)
                last_status = status

                # Save status
                status_file = project_root / "data" / "nas_migration" / "jarvis_export_monitor_status.json"
                status_file.parent.mkdir(parents=True, exist_ok=True)
                with open(status_file, 'w') as f:
                    json.dump(status, f, indent=2)

            # Check if complete
            if status['exported_to_temp'] >= status['total_volumes'] and status['in_progress'] == 0:
                logger.info("✅ All volumes exported and copied to NAS!")
                logger.info("   Export process appears complete")
                break

            time.sleep(interval)


    except Exception as e:
        logger.error(f"Error in monitor_loop: {e}", exc_info=True)
        raise
def main():
    try:
        """JARVIS Monitor main"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Monitor: Docker Volume Export")
        parser.add_argument("--interval", type=int, default=30, help="Check interval in seconds")
        parser.add_argument("--once", action="store_true", help="Check once and exit")
        parser.add_argument("--iterations", type=int, help="Maximum iterations")

        args = parser.parse_args()

        if args.once:
            status = check_export_status()
            generate_report(status)

            # Save status
            status_file = project_root / "data" / "nas_migration" / "jarvis_export_monitor_status.json"
            status_file.parent.mkdir(parents=True, exist_ok=True)
            with open(status_file, 'w') as f:
                json.dump(status, f, indent=2)
        else:
            monitor_loop(interval=args.interval, max_iterations=args.iterations)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()