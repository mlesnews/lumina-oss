#!/usr/bin/env python3
"""
URGENT NAS Migration Accelerator

Accelerates NAS migration to free up hard drive space immediately.
Prioritizes largest directories and uses maximum speed settings.

Tags: #NAS_MIGRATION #URGENT #ACCELERATOR #DISK_SPACE @JARVIS @LUMINA
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

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

logger = get_logger("UrgentNASMigration")


class UrgentMigrationAccelerator:
    """Accelerate NAS migration to free up disk space"""

    def __init__(self):
        self.nas_ip = "<NAS_PRIMARY_IP>"
        self.nas_base = f"\\\\{self.nas_ip}"

        # Priority targets (largest first)
        self.priority_targets = [
            {
                "name": "Docker Volumes",
                "source": Path("C:\\Users\\mlesn\\AppData\\Local\\Docker"),
                "target": f"{self.nas_base}\\backups\\docker",
                "size_gb": 82.22,
                "priority": "CRITICAL"
            },
            {
                "name": "Downloads Folder",
                "source": Path("C:\\Users\\mlesn\\Downloads"),
                "target": f"{self.nas_base}\\homes\\mlesn\\Downloads",
                "size_gb": 0.76,
                "priority": "HIGH"
            },
            {
                "name": "Pip Cache",
                "source": Path("C:\\Users\\mlesn\\AppData\\Local\\pip\\Cache"),
                "target": f"{self.nas_base}\\backups\\cache\\pip",
                "size_gb": 3.42,
                "priority": "HIGH"
            },
            {
                "name": "npm Cache",
                "source": Path("C:\\Users\\mlesn\\AppData\\Local\\npm-cache"),
                "target": f"{self.nas_base}\\backups\\cache\\npm",
                "size_gb": 0.5,
                "priority": "MEDIUM"
            },
            {
                "name": "Temp Files",
                "source": Path("C:\\Users\\mlesn\\AppData\\Local\\Temp"),
                "target": f"{self.nas_base}\\backups\\temp",
                "size_gb": 0.0,  # Will calculate
                "priority": "MEDIUM"
            }
        ]

    def get_directory_size(self, path: Path) -> float:
        """Get directory size in GB"""
        if not path.exists():
            return 0.0

        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = Path(dirpath) / filename
                    try:
                        total_size += filepath.stat().st_size
                    except (OSError, PermissionError):
                        pass
        except (OSError, PermissionError):
            pass

        return total_size / (1024**3)

    def migrate_with_robocopy(self, source: Path, target: Path, name: str) -> Dict:
        """Migrate using Robocopy with maximum speed settings"""
        logger.info("=" * 80)
        logger.info(f"🚀 MIGRATING: {name}")
        logger.info("=" * 80)
        logger.info(f"Source: {source}")
        logger.info(f"Target: {target}")
        logger.info("")

        if not source.exists():
            logger.warning(f"❌ Source does not exist: {source}")
            return {"status": "SKIPPED", "reason": "source_not_found"}

        # Create target directory
        target.mkdir(parents=True, exist_ok=True)

        # Robocopy with maximum speed settings
        # /MT:32 = 32 threads (maximum)
        # /R:1 = 1 retry (fast)
        # /W:1 = 1 second wait (fast)
        # /MIR = Mirror (delete files on target that don't exist in source)
        # /FFT = Use FAT file times (faster on network)
        # /XJ = Exclude junction points
        # /NP = No progress (faster)
        # /NDL = No directory list (faster)
        # /NFL = No file list (faster)

        robocopy_cmd = [
            "robocopy",
            str(source),
            str(target),
            "/MIR",
            "/MT:32",  # Maximum threads
            "/R:1",    # Minimal retries
            "/W:1",    # Minimal wait
            "/FFT",    # Fast file times
            "/XJ",     # Exclude junctions
            "/NP",     # No progress
            "/NDL",    # No directory list
            "/NFL"     # No file list
        ]

        logger.info("📦 Starting Robocopy migration...")
        logger.info(f"   Command: {' '.join(robocopy_cmd)}")
        logger.info("")

        try:
            result = subprocess.run(
                robocopy_cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            , check=False)

            # Robocopy exit codes: 0-7 = success, 8+ = error
            if result.returncode <= 7:
                logger.info("✅ Migration successful!")
                logger.info(f"   Exit code: {result.returncode}")
                return {
                    "status": "SUCCESS",
                    "exit_code": result.returncode,
                    "output": result.stdout
                }
            else:
                logger.warning(f"⚠️  Migration completed with warnings (exit code: {result.returncode})")
                return {
                    "status": "WARNING",
                    "exit_code": result.returncode,
                    "output": result.stdout,
                    "error": result.stderr
                }
        except subprocess.TimeoutExpired:
            logger.error("❌ Migration timed out (took longer than 1 hour)")
            return {"status": "TIMEOUT"}
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return {"status": "FAILED", "error": str(e)}

    def execute_urgent_migration(self, dry_run: bool = False) -> Dict:
        try:
            """Execute urgent migration of priority targets"""
            logger.info("=" * 80)
            logger.info("🚨 URGENT NAS MIGRATION - ACCELERATED MODE")
            logger.info("=" * 80)
            logger.info("")
            logger.info("⚠️  CRITICAL: Freeing up hard drive space immediately")
            logger.info("")

            if dry_run:
                logger.info("🔍 DRY RUN MODE - No files will be moved")
                logger.info("")

            results = {
                "timestamp": datetime.now().isoformat(),
                "dry_run": dry_run,
                "migrations": {},
                "total_space_freed_gb": 0.0
            }

            # Sort by priority and size
            sorted_targets = sorted(
                self.priority_targets,
                key=lambda x: (x["priority"] == "CRITICAL", x.get("size_gb", 0)),
                reverse=True
            )

            for target in sorted_targets:
                name = target["name"]
                source = target["source"]
                target_path = Path(target["target"])

                # Calculate actual size if not provided
                if target.get("size_gb", 0) == 0:
                    size_gb = self.get_directory_size(source)
                    target["size_gb"] = size_gb

                logger.info("")
                logger.info(f"📋 Processing: {name}")
                logger.info(f"   Size: {target['size_gb']:.2f} GB")
                logger.info(f"   Priority: {target['priority']}")
                logger.info("")

                if dry_run:
                    logger.info("   [DRY RUN] Would migrate to: " + str(target_path))
                    results["migrations"][name] = {
                        "status": "DRY_RUN",
                        "size_gb": target["size_gb"]
                    }
                else:
                    # Execute migration
                    result = self.migrate_with_robocopy(source, target_path, name)
                    results["migrations"][name] = result
                    results["migrations"][name]["size_gb"] = target["size_gb"]

                    if result.get("status") == "SUCCESS":
                        results["total_space_freed_gb"] += target["size_gb"]

            logger.info("")
            logger.info("=" * 80)
            logger.info("📊 MIGRATION SUMMARY")
            logger.info("=" * 80)
            logger.info(f"Total space to be freed: {results['total_space_freed_gb']:.2f} GB")
            logger.info("")

            for name, result in results["migrations"].items():
                status = result.get("status", "UNKNOWN")
                size = result.get("size_gb", 0)
                logger.info(f"  {name:30s} {status:15s} ({size:.2f} GB)")

            logger.info("")
            logger.info("=" * 80)

            return results


        except Exception as e:
            self.logger.error(f"Error in execute_urgent_migration: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Urgent NAS Migration Accelerator")
        parser.add_argument("--execute", action="store_true", help="Actually execute migration (default: dry run)")
        parser.add_argument("--docker-only", action="store_true", help="Migrate Docker volumes only (82GB)")

        args = parser.parse_args()

        accelerator = UrgentMigrationAccelerator()

        if args.docker_only:
            # Migrate Docker only (biggest win)
            docker_target = next(t for t in accelerator.priority_targets if t["name"] == "Docker Volumes")
            result = accelerator.migrate_with_robocopy(
                docker_target["source"],
                Path(docker_target["target"]),
                docker_target["name"]
            )
            print(f"\n✅ Docker migration: {result.get('status')}")
        else:
            # Execute all migrations
            results = accelerator.execute_urgent_migration(dry_run=not args.execute)

            if not args.execute:
                print("\n💡 To actually execute, run with --execute flag")
                print("   Example: python scripts/python/urgent_nas_migration_accelerator.py --execute")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()