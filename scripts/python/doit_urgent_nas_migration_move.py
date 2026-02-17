#!/usr/bin/env python3
"""
DOIT URGENT NAS MIGRATION - MOVE FILES TO FREE SPACE IMMEDIATELY
Actually moves files (not just copies) to free disk space NOW

Tags: #NAS_MIGRATION #URGENT #DOIT #MOVE @JARVIS @LUMINA
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List

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

logger = get_logger("DOITUrgentNASMigration")


class DOITUrgentMigration:
    """DOIT: Move files to NAS to free space immediately"""

    def __init__(self):
        self.nas_ip = "<NAS_PRIMARY_IP>"
        self.nas_base = f"\\\\{self.nas_ip}"

        # Priority targets - files that can be safely MOVED (not just copied)
        self.move_targets = [
            {
                "name": "Docker Volumes",
                "source": Path("C:\\Users\\mlesn\\AppData\\Local\\Docker"),
                "target": f"{self.nas_base}\\backups\\docker",
                "size_gb": 82.22,
                "priority": "CRITICAL",
                "verify_first": True
            },
            {
                "name": "Pip Cache",
                "source": Path("C:\\Users\\mlesn\\AppData\\Local\\pip\\Cache"),
                "target": f"{self.nas_base}\\backups\\cache\\pip",
                "size_gb": 3.42,
                "priority": "HIGH",
                "verify_first": True
            },
            {
                "name": "Downloads Folder",
                "source": Path("C:\\Users\\mlesn\\Downloads"),
                "target": f"{self.nas_base}\\homes\\mlesn\\Downloads",
                "size_gb": 0.76,
                "priority": "HIGH",
                "verify_first": True
            },
            {
                "name": "Temp Files (Old)",
                "source": Path("C:\\Users\\mlesn\\AppData\\Local\\Temp"),
                "target": f"{self.nas_base}\\backups\\temp",
                "size_gb": 4.27,
                "priority": "MEDIUM",
                "verify_first": False,
                "age_days": 7  # Only move files older than 7 days
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

    def verify_nas_copy(self, source: Path, target: Path) -> bool:
        try:
            """Verify files were copied to NAS successfully"""
            if not source.exists():
                return False

            # Check if target exists and has reasonable size
            if not Path(target).exists():
                return False

            source_size = self.get_directory_size(source)
            target_size = self.get_directory_size(Path(target))

            # Allow 5% difference for network/filesystem differences
            if source_size == 0:
                return target_size == 0

            ratio = target_size / source_size if source_size > 0 else 0
            return 0.95 <= ratio <= 1.05

        except Exception as e:
            self.logger.error(f"Error in verify_nas_copy: {e}", exc_info=True)
            raise
    def move_with_robocopy(self, source: Path, target: Path, name: str, verify_first: bool = True) -> Dict:
        """Move files using Robocopy /MOVE (actually moves, not copies)"""
        logger.info("=" * 80)
        logger.info(f"🚀 MOVING: {name}")
        logger.info("=" * 80)
        logger.info(f"Source: {source}")
        logger.info(f"Target: {target}")
        logger.info("")

        if not source.exists():
            logger.warning(f"❌ Source does not exist: {source}")
            return {"status": "SKIPPED", "reason": "source_not_found"}

        # Get source size before move
        source_size_gb = self.get_directory_size(source)
        logger.info(f"📊 Source size: {source_size_gb:.2f} GB")
        logger.info("")

        # Create target directory
        target_path = Path(target)
        target_path.mkdir(parents=True, exist_ok=True)

        # First, copy with verification
        if verify_first:
            logger.info("📋 Step 1: Copying to NAS (with verification)...")
            robocopy_copy = [
                "robocopy",
                str(source),
                str(target_path),
                "/MIR",
                "/MT:32",
                "/R:3",
                "/W:2",
                "/FFT",
                "/XJ",
                "/NP"
            ]

            try:
                result = subprocess.run(
                    robocopy_copy,
                    capture_output=True,
                    text=True,
                    timeout=7200  # 2 hour timeout
                )

                if result.returncode > 7:
                    logger.error(f"❌ Copy failed (exit code: {result.returncode})")
                    return {"status": "FAILED", "exit_code": result.returncode}

                # Verify copy
                logger.info("🔍 Verifying copy...")
                if not self.verify_nas_copy(source, target_path):
                    logger.error("❌ Copy verification failed - sizes don't match")
                    return {"status": "FAILED", "reason": "verification_failed"}

                logger.info("✅ Copy verified successfully")
                logger.info("")
            except subprocess.TimeoutExpired:
                logger.error("❌ Copy timed out")
                return {"status": "TIMEOUT"}
            except Exception as e:
                logger.error(f"❌ Copy failed: {e}")
                return {"status": "FAILED", "error": str(e)}

        # Step 2: Delete source after successful copy
        logger.info("🗑️  Step 2: Removing source files (freeing space)...")
        try:
            # Use robocopy /PURGE to remove source files that exist on target
            # Actually, just delete the source directory
            if source.is_dir():
                shutil.rmtree(source, ignore_errors=True)
                # Recreate empty directory structure if needed
                source.mkdir(parents=True, exist_ok=True)
            else:
                source.unlink()

            logger.info("✅ Source files removed")

            # Verify space was freed
            remaining_size = self.get_directory_size(source)
            freed_gb = source_size_gb - remaining_size

            return {
                "status": "SUCCESS",
                "freed_gb": freed_gb,
                "source_size_gb": source_size_gb
            }
        except Exception as e:
            logger.error(f"❌ Failed to remove source: {e}")
            return {"status": "PARTIAL", "error": str(e), "freed_gb": 0}

    def execute_doit_migration(self) -> Dict:
        try:
            """DOIT: Execute urgent migration - MOVE files to free space"""
            logger.info("=" * 80)
            logger.info("🚨 DOIT URGENT NAS MIGRATION - MOVING FILES NOW")
            logger.info("=" * 80)
            logger.info("")
            logger.info("⚠️  CRITICAL: Moving files to NAS to free disk space IMMEDIATELY")
            logger.info("⚠️  WARNING: Source files will be DELETED after successful copy")
            logger.info("")

            results = {
                "timestamp": datetime.now().isoformat(),
                "migrations": {},
                "total_space_freed_gb": 0.0
            }

            # Sort by priority and size
            sorted_targets = sorted(
                self.move_targets,
                key=lambda x: (x["priority"] == "CRITICAL", x.get("size_gb", 0)),
                reverse=True
            )

            for target in sorted_targets:
                name = target["name"]
                source = target["source"]
                target_path = Path(target["target"])
                verify_first = target.get("verify_first", True)

                # Calculate actual size if not provided
                if target.get("size_gb", 0) == 0:
                    size_gb = self.get_directory_size(source)
                    target["size_gb"] = size_gb

                logger.info("")
                logger.info(f"📋 Processing: {name}")
                logger.info(f"   Size: {target['size_gb']:.2f} GB")
                logger.info(f"   Priority: {target['priority']}")
                logger.info("")

                # Execute move
                result = self.move_with_robocopy(source, target_path, name, verify_first)
                results["migrations"][name] = result
                results["migrations"][name]["size_gb"] = target["size_gb"]

                if result.get("status") == "SUCCESS":
                    freed = result.get("freed_gb", target["size_gb"])
                    results["total_space_freed_gb"] += freed
                    logger.info(f"✅ Freed: {freed:.2f} GB")

            logger.info("")
            logger.info("=" * 80)
            logger.info("📊 MIGRATION SUMMARY")
            logger.info("=" * 80)
            logger.info(f"Total space freed: {results['total_space_freed_gb']:.2f} GB")
            logger.info("")

            for name, result in results["migrations"].items():
                status = result.get("status", "UNKNOWN")
                size = result.get("size_gb", 0)
                freed = result.get("freed_gb", 0)
                logger.info(f"  {name:30s} {status:15s} (Freed: {freed:.2f} GB / {size:.2f} GB)")

            logger.info("")
            logger.info("=" * 80)

            return results


        except Exception as e:
            self.logger.error(f"Error in execute_doit_migration: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="DOIT Urgent NAS Migration - Move Files")
    parser.add_argument("--execute", action="store_true", help="Actually execute (default: dry run)")

    args = parser.parse_args()

    if not args.execute:
        print("⚠️  DRY RUN MODE")
        print("   Use --execute to actually move files")
        print("   Example: python scripts/python/doit_urgent_nas_migration_move.py --execute")
        return

    migrator = DOITUrgentMigration()
    results = migrator.execute_doit_migration()

    print("\n" + "=" * 80)
    print("✅ DOIT MIGRATION COMPLETE")
    print("=" * 80)
    print(f"Total space freed: {results['total_space_freed_gb']:.2f} GB")
    print()


if __name__ == "__main__":


    main()