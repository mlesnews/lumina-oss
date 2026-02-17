#!/usr/bin/env python3
"""
@DOIT: Migrate All Cloud Storage Providers to NAS LOCAL-CLOUD-STORAGE
Root Cause Fix: Move Dropbox, OneDrive, and other cloud storage to NAS

Tags: #NAS_MIGRATION #CLOUD_STORAGE #ROOT_CAUSE #DOIT #V3 @JARVIS @LUMINA
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

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

logger = get_logger("DOITCloudStorageMigration")


class DOITCloudStorageMigration:
    """@DOIT: Migrate all cloud storage providers to NAS LOCAL-CLOUD-STORAGE"""

    def __init__(self):
        self.nas_ip = "<NAS_PRIMARY_IP>"
        self.nas_base = f"\\\\{self.nas_ip}"
        self.local_cloud_storage = Path(f"{self.nas_base}\\backups\\LOCAL-CLOUD-STORAGE")

        # Cloud storage providers to migrate
        self.cloud_providers = [
            {
                "name": "Dropbox",
                "source": Path("C:\\Users\\mlesn\\Dropbox"),
                "target": self.local_cloud_storage / "Dropbox",
                "size_gb": 4605.35,
                "priority": "CRITICAL"
            },
            {
                "name": "OneDrive",
                "source": Path("C:\\Users\\mlesn\\OneDrive"),
                "target": self.local_cloud_storage / "OneDrive",
                "size_gb": 67.97,
                "priority": "HIGH"
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

    def ensure_nas_structure(self) -> bool:
        """Ensure LOCAL-CLOUD-STORAGE structure exists on NAS"""
        logger.info("🔧 Ensuring NAS LOCAL-CLOUD-STORAGE structure...")

        try:
            # Create base directory
            self.local_cloud_storage.mkdir(parents=True, exist_ok=True)

            # Create provider directories
            for provider in self.cloud_providers:
                provider["target"].mkdir(parents=True, exist_ok=True)
                logger.info(f"   ✅ {provider['name']}: {provider['target']}")

            logger.info("   ✅ NAS structure ready")
            return True
        except Exception as e:
            logger.error(f"   ❌ Failed to create NAS structure: {e}")
            return False

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

        # Get source size
        source_size_gb = self.get_directory_size(source)
        logger.info(f"📊 Source size: {source_size_gb:.2f} GB")
        logger.info("")

        # Create target directory
        target.mkdir(parents=True, exist_ok=True)

        # Robocopy with maximum speed settings
        # /MT:64 = 64 threads (maximum)
        # /R:5 = 5 retries
        # /W:3 = 3 second wait
        # /MIR = Mirror (sync)
        # /FFT = Use FAT file times (faster on network)
        # /XJ = Exclude junction points
        # /NP = No progress (faster)
        # /NDL = No directory list (faster)
        # /NFL = No file list (faster)
        # /LOG = Log file for monitoring

        log_file = project_root / "data" / "nas_migration" / f"{name.lower().replace(' ', '_')}_migration.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        robocopy_cmd = [
            "robocopy",
            str(source),
            str(target),
            "/MIR",
            "/MT:64",  # Maximum threads
            "/R:5",    # Retries
            "/W:3",    # Wait time
            "/FFT",    # Fast file times
            "/XJ",     # Exclude junctions
            "/NP",     # No progress
            "/NDL",    # No directory list
            "/NFL",    # No file list
            f"/LOG:{log_file}"  # Log file
        ]

        logger.info("📦 Starting Robocopy migration...")
        logger.info(f"   Command: {' '.join(robocopy_cmd[:5])} ...")
        logger.info(f"   Log: {log_file}")
        logger.info("")
        logger.info("   ⚠️  This may take a long time for large directories (4.6 TB)")
        logger.info("   ⚠️  Migration will continue in background")
        logger.info("")

        try:
            # Run in background - don't wait for completion
            process = subprocess.Popen(
                robocopy_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            logger.info(f"   ✅ Migration started (PID: {process.pid})")
            logger.info(f"   📋 Monitor progress: Get-Content {log_file} -Tail 20 -Wait")

            return {
                "status": "STARTED",
                "pid": process.pid,
                "log_file": str(log_file),
                "source_size_gb": source_size_gb
            }
        except Exception as e:
            logger.error(f"❌ Migration failed to start: {e}")
            return {"status": "FAILED", "error": str(e)}

    def execute_migration(self) -> Dict:
        """@DOIT: Execute cloud storage migration to NAS"""
        logger.info("=" * 80)
        logger.info("@DOIT: CLOUD STORAGE MIGRATION TO NAS")
        logger.info("=" * 80)
        logger.info("")
        logger.info("🎯 ROOT CAUSE FIX: Moving cloud storage providers to NAS")
        logger.info("")

        # Ensure NAS structure
        if not self.ensure_nas_structure():
            logger.error("❌ Failed to create NAS structure")
            return {"status": "FAILED", "reason": "nas_structure_failed"}

        logger.info("")

        results = {
            "timestamp": datetime.now().isoformat(),
            "migrations": {},
            "total_size_gb": 0.0
        }

        # Sort by priority and size
        sorted_providers = sorted(
            self.cloud_providers,
            key=lambda x: (x["priority"] == "CRITICAL", x.get("size_gb", 0)),
            reverse=True
        )

        for provider in sorted_providers:
            name = provider["name"]
            source = provider["source"]
            target = provider["target"]

            # Calculate actual size if not provided
            if provider.get("size_gb", 0) == 0:
                size_gb = self.get_directory_size(source)
                provider["size_gb"] = size_gb

            logger.info("")
            logger.info(f"📋 Processing: {name}")
            logger.info(f"   Size: {provider['size_gb']:.2f} GB")
            logger.info(f"   Priority: {provider['priority']}")
            logger.info("")

            # Execute migration
            result = self.migrate_with_robocopy(source, target, name)
            results["migrations"][name] = result
            results["migrations"][name]["size_gb"] = provider["size_gb"]
            results["total_size_gb"] += provider["size_gb"]

        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 MIGRATION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total size to migrate: {results['total_size_gb']:.2f} GB")
        logger.info("")

        for name, result in results["migrations"].items():
            status = result.get("status", "UNKNOWN")
            size = result.get("size_gb", 0)
            pid = result.get("pid", "N/A")
            logger.info(f"  {name:30s} {status:15s} ({size:.2f} GB) PID: {pid}")

        logger.info("")
        logger.info("=" * 80)
        logger.info("⚠️  IMPORTANT: Migrations are running in background")
        logger.info("   Monitor with: Get-Content <log_file> -Tail 20 -Wait")
        logger.info("   After completion, run @V3 verification")
        logger.info("=" * 80)

        return results


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="@DOIT: Migrate Cloud Storage to NAS")
    parser.add_argument("--execute", action="store_true", help="Actually execute (default: dry run)")

    args = parser.parse_args()

    if not args.execute:
        print("⚠️  DRY RUN MODE")
        print("   Use --execute to actually migrate")
        print("   Example: python scripts/python/doit_migrate_cloud_storage_to_nas.py --execute")
        return

    migrator = DOITCloudStorageMigration()
    results = migrator.execute_migration()

    print("\n" + "=" * 80)
    print("@DOIT: CLOUD STORAGE MIGRATION STARTED")
    print("=" * 80)
    print(f"Total size: {results['total_size_gb']:.2f} GB")
    print("Migrations running in background")
    print()


if __name__ == "__main__":


    main()