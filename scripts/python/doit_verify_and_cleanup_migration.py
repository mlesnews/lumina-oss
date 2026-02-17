#!/usr/bin/env python3
"""
@DOIT: Verify NAS Migration and Cleanup Source Files
Verifies files are on NAS, then deletes source to free space

Tags: #NAS_MIGRATION #DOIT #VERIFY #CLEANUP @JARVIS @LUMINA
"""

import sys
import os
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

logger = get_logger("DOITVerifyCleanup")


class DOITVerifyCleanup:
    """@DOIT: Verify and cleanup migration"""

    def __init__(self):
        self.nas_ip = "<NAS_PRIMARY_IP>"
        self.nas_base = f"\\\\{self.nas_ip}"

        self.migration_targets = [
            {
                "name": "Docker Volumes",
                "source": Path("C:\\Users\\mlesn\\AppData\\Local\\Docker"),
                "target": Path(f"{self.nas_base}\\backups\\docker"),
                "min_ratio": 0.90  # Allow 10% difference
            },
            {
                "name": ".cache",
                "source": Path("C:\\Users\\mlesn\\.cache"),
                "target": Path(f"{self.nas_base}\\backups\\cache\\.cache"),
                "min_ratio": 0.90
            },
            {
                "name": "Pip Cache",
                "source": Path("C:\\Users\\mlesn\\AppData\\Local\\pip\\Cache"),
                "target": Path(f"{self.nas_base}\\backups\\cache\\pip"),
                "min_ratio": 0.95
            },
            {
                "name": "Downloads",
                "source": Path("C:\\Users\\mlesn\\Downloads"),
                "target": Path(f"{self.nas_base}\\homes\\mlesn\\Downloads"),
                "min_ratio": 0.95
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

    def verify_migration(self, source: Path, target: Path, min_ratio: float) -> Dict:
        try:
            """Verify migration completed successfully"""
            if not source.exists():
                return {"verified": True, "reason": "source_already_deleted"}

            if not target.exists():
                return {"verified": False, "reason": "target_not_found"}

            source_size = self.get_directory_size(source)
            target_size = self.get_directory_size(target)

            if source_size == 0:
                return {"verified": True, "reason": "source_empty"}

            if target_size == 0:
                return {"verified": False, "reason": "target_empty"}

            ratio = target_size / source_size if source_size > 0 else 0

            verified = ratio >= min_ratio

            return {
                "verified": verified,
                "source_size_gb": source_size,
                "target_size_gb": target_size,
                "ratio": ratio,
                "reason": "verified" if verified else f"ratio_too_low_{ratio:.2f}"
            }

        except Exception as e:
            self.logger.error(f"Error in verify_migration: {e}", exc_info=True)
            raise
    def cleanup_source(self, source: Path, name: str) -> Dict:
        """Delete source files after verification"""
        if not source.exists():
            return {"status": "SKIPPED", "reason": "already_deleted"}

        source_size_gb = self.get_directory_size(source)

        logger.info(f"🗑️  Deleting source: {source}")
        logger.info(f"   Size: {source_size_gb:.2f} GB")

        try:
            if source.is_dir():
                # Delete contents but keep directory structure
                for item in source.iterdir():
                    try:
                        if item.is_dir():
                            shutil.rmtree(item, ignore_errors=True)
                        else:
                            item.unlink()
                    except Exception as e:
                        logger.warning(f"   ⚠️  Could not delete {item}: {e}")

                logger.info("   ✅ Source cleaned")
            else:
                source.unlink()
                logger.info("   ✅ Source file deleted")

            # Verify deletion
            remaining_size = self.get_directory_size(source)
            freed_gb = source_size_gb - remaining_size

            return {
                "status": "SUCCESS",
                "freed_gb": freed_gb,
                "remaining_gb": remaining_size
            }
        except Exception as e:
            logger.error(f"   ❌ Failed to delete source: {e}")
            return {"status": "FAILED", "error": str(e)}

    def execute_verify_and_cleanup(self) -> Dict:
        """@DOIT: Verify and cleanup all migrations"""
        logger.info("=" * 80)
        logger.info("@DOIT: VERIFY AND CLEANUP NAS MIGRATION")
        logger.info("=" * 80)
        logger.info("")

        results = {
            "timestamp": datetime.now().isoformat(),
            "verifications": {},
            "cleanups": {},
            "total_freed_gb": 0.0
        }

        for target in self.migration_targets:
            name = target["name"]
            source = target["source"]
            nas_target = target["target"]
            min_ratio = target["min_ratio"]

            logger.info("")
            logger.info(f"📋 Processing: {name}")
            logger.info(f"   Source: {source}")
            logger.info(f"   Target: {nas_target}")
            logger.info("")

            # Step 1: Verify
            logger.info("🔍 Step 1: Verifying migration...")
            verification = self.verify_migration(source, nas_target, min_ratio)
            results["verifications"][name] = verification

            if verification["verified"]:
                logger.info("   ✅ Migration verified")
                logger.info(f"   Source: {verification.get('source_size_gb', 0):.2f} GB")
                logger.info(f"   Target: {verification.get('target_size_gb', 0):.2f} GB")
                if "ratio" in verification:
                    logger.info(f"   Ratio: {verification['ratio']:.2%}")

                # Step 2: Cleanup
                logger.info("")
                logger.info("🗑️  Step 2: Cleaning up source files...")
                cleanup = self.cleanup_source(source, name)
                results["cleanups"][name] = cleanup

                if cleanup["status"] == "SUCCESS":
                    freed = cleanup.get("freed_gb", 0)
                    results["total_freed_gb"] += freed
                    logger.info(f"   ✅ Freed: {freed:.2f} GB")
                else:
                    logger.warning(f"   ⚠️  Cleanup: {cleanup.get('status', 'UNKNOWN')}")
            else:
                logger.warning(f"   ⚠️  Migration not verified: {verification.get('reason', 'unknown')}")
                logger.info("   ⏸️  Skipping cleanup until verification passes")

        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 VERIFICATION AND CLEANUP SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total space freed: {results['total_freed_gb']:.2f} GB")
        logger.info("")

        for name in results["verifications"]:
            verified = results["verifications"][name].get("verified", False)
            cleanup_status = results["cleanups"].get(name, {}).get("status", "N/A")
            freed = results["cleanups"].get(name, {}).get("freed_gb", 0)
            verified_str = "YES" if verified else "NO"
            logger.info(f"  {name:30s} Verified: {verified_str:5s} | Cleanup: {cleanup_status:10s} | Freed: {freed:6.2f} GB")

        logger.info("")
        logger.info("=" * 80)

        return results


def main():
    """Main entry point"""
    verifier = DOITVerifyCleanup()
    results = verifier.execute_verify_and_cleanup()

    print("\n" + "=" * 80)
    print("@DOIT: VERIFICATION AND CLEANUP COMPLETE")
    print("=" * 80)
    print(f"Total space freed: {results['total_freed_gb']:.2f} GB")
    print()


if __name__ == "__main__":


    main()