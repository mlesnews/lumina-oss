"""
PUBLIC: Spring Cleaning Executor
Location: scripts/python/spring_cleaning_executor.py
License: MIT

Executes spring cleaning operations with safety checks.
Supports dry-run mode for preview.
"""

import json
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import argparse


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SpringCleaningExecutor:
    """Execute spring cleaning operations safely."""

    def __init__(self, project_root: Path, dry_run: bool = True, archive: bool = True):
        """
        Initialize executor.

        Args:
            project_root: Path to project root
            dry_run: If True, only preview (don't actually delete)
            archive: If True, move to archive instead of delete
        """
        self.project_root = project_root
        self.dry_run = dry_run
        self.archive = archive
        self.archive_path = project_root / "archive" / "spring_cleaning"
        self.config_path = project_root / "config"
        self.data_path = project_root / "data"

        self.results = {
            "executed_at": datetime.now().isoformat(),
            "dry_run": dry_run,
            "archive_mode": archive,
            "operations": [],
            "summary": {}
        }

        if archive and not dry_run:
            self.archive_path.mkdir(parents=True, exist_ok=True)

    def cleanup_config_backups(self, keep_latest: int = 3) -> Dict[str, Any]:
        """
        Clean up config backup files, keeping only latest N per file.

        Args:
            keep_latest: Number of latest backups to keep per file

        Returns:
            Cleanup results
        """
        logger.info(f"Cleaning config backups (keeping latest {keep_latest} per file)...")

        backup_files = list(self.config_path.glob("*backup*.json"))
        backup_files.extend(self.config_path.glob("*backup*.encrypted"))

        # Group by base name
        backups_by_base = {}
        for backup in backup_files:
            name = backup.stem
            if ".encrypted" in name:
                name = name.replace(".encrypted", "")

            if "backup_" in name:
                base = name.split("backup_")[0]
                if base not in backups_by_base:
                    backups_by_base[base] = []
                backups_by_base[base].append(backup)

        # Sort by modification time and keep only latest
        files_to_remove = []
        files_kept = []

        for base, files in backups_by_base.items():
            # Sort by modification time (newest first)
            files_sorted = sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)

            # Keep latest N
            files_kept.extend(files_sorted[:keep_latest])
            # Remove rest
            files_to_remove.extend(files_sorted[keep_latest:])

        # Execute cleanup
        removed_count = 0
        archived_count = 0

        for file in files_to_remove:
            try:
                if self.dry_run:
                    logger.info(f"[DRY RUN] Would {'archive' if self.archive else 'delete'}: {file}")
                    removed_count += 1
                elif self.archive:
                    # Move to archive
                    archive_file = self.archive_path / "config_backups" / file.name
                    archive_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(file), str(archive_file))
                    archived_count += 1
                    removed_count += 1
                    logger.info(f"Archived: {file} -> {archive_file}")
                else:
                    # Delete
                    file.unlink()
                    removed_count += 1
                    logger.info(f"Deleted: {file}")
            except Exception as e:
                logger.error(f"Error processing {file}: {e}")

        return {
            "category": "config_backups",
            "files_removed": removed_count,
            "files_archived": archived_count if self.archive else 0,
            "files_kept": len(files_kept),
            "operation": "archive" if self.archive else "delete"
        }

    def cleanup_temporary_files(self) -> Dict[str, Any]:
        """
        Clean up temporary files.

        Returns:
            Cleanup results
        """
        logger.info("Cleaning temporary files...")

        temp_patterns = [
            "**/*.tmp",
            "**/*.cache",
            "**/*.swp",
            "**/*.bak",
            "**/*~",
            "**/.DS_Store",
            "**/Thumbs.db"
        ]

        temp_files = []
        for pattern in temp_patterns:
            try:
                temp_files.extend(self.project_root.glob(pattern))
            except Exception as e:
                logger.warning(f"Error finding {pattern}: {e}")

        removed_count = 0

        for file in temp_files:
            if not file.is_file():
                continue

            try:
                if self.dry_run:
                    logger.info(f"[DRY RUN] Would delete: {file}")
                    removed_count += 1
                else:
                    file.unlink()
                    removed_count += 1
                    logger.info(f"Deleted: {file}")
            except Exception as e:
                logger.error(f"Error deleting {file}: {e}")

        return {
            "category": "temporary_files",
            "files_removed": removed_count,
            "operation": "delete"
        }

    def execute_safe_cleanup(self) -> Dict[str, Any]:
        """
        Execute safe cleanup operations (low risk).

        Returns:
            Cleanup results
        """
        logger.info("Executing safe cleanup operations...")

        # Clean config backups
        try:
            backup_results = self.cleanup_config_backups(keep_latest=3)
            self.results["operations"].append(backup_results)
        except Exception as e:
            logger.error(f"Error cleaning config backups: {e}")
            self.results["operations"].append({
                "category": "config_backups",
                "error": str(e)
            })

        # Clean temporary files
        try:
            temp_results = self.cleanup_temporary_files()
            self.results["operations"].append(temp_results)
        except Exception as e:
            logger.error(f"Error cleaning temporary files: {e}")
            self.results["operations"].append({
                "category": "temporary_files",
                "error": str(e)
            })

        # Generate summary
        total_removed = sum(
            op.get("files_removed", 0)
            for op in self.results["operations"]
        )

        total_archived = sum(
            op.get("files_archived", 0)
            for op in self.results["operations"]
        )

        self.results["summary"] = {
            "total_files_removed": total_removed,
            "total_files_archived": total_archived,
            "operations_completed": len(self.results["operations"]),
            "mode": "dry_run" if self.dry_run else ("archive" if self.archive else "delete")
        }

        return self.results

    def print_results(self):
        """Print formatted results."""
        mode = "DRY RUN" if self.dry_run else ("ARCHIVE" if self.archive else "DELETE")

        print("\n" + "=" * 80)
        print(f"SPRING CLEANING EXECUTION - {mode}")
        print("=" * 80)
        print(f"Executed: {self.results['executed_at']}")
        print()

        summary = self.results["summary"]
        print("SUMMARY")
        print("-" * 80)
        print(f"Mode: {summary.get('mode', 'unknown').upper()}")
        print(f"Files Removed: {summary.get('total_files_removed', 0):,}")
        if summary.get('total_files_archived', 0) > 0:
            print(f"Files Archived: {summary.get('total_files_archived', 0):,}")
        print(f"Operations: {summary.get('operations_completed', 0)}")
        print()

        print("DETAILED RESULTS")
        print("-" * 80)
        for op in self.results["operations"]:
            if "error" not in op:
                print(f"\n{op.get('category', 'unknown').upper().replace('_', ' ')}")
                print(f"  Files Removed: {op.get('files_removed', 0):,}")
                if op.get('files_archived', 0) > 0:
                    print(f"  Files Archived: {op.get('files_archived', 0):,}")
                if op.get('files_kept', 0) > 0:
                    print(f"  Files Kept: {op.get('files_kept', 0):,}")
                print(f"  Operation: {op.get('operation', 'unknown')}")
            else:
                print(f"\n{op.get('category', 'unknown').upper().replace('_', ' ')}")
                print(f"  Error: {op.get('error', 'Unknown error')}")

        print()
        print("=" * 80)
        print()


def main():
    try:
        """Main function to execute cleanup."""
        parser = argparse.ArgumentParser(description="Spring Cleaning Executor")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=True,
            help="Dry run mode (preview only, default: True)"
        )
        parser.add_argument(
            "--execute",
            action="store_true",
            help="Actually execute (overrides dry-run)"
        )
        parser.add_argument(
            "--archive",
            action="store_true",
            default=True,
            help="Archive instead of delete (default: True)"
        )
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete instead of archive (use with caution)"
        )

        args = parser.parse_args()

        # Determine mode
        dry_run = not args.execute
        archive = not args.delete if args.execute else True

        script_path = Path(__file__).resolve()
        project_root = script_path.parent.parent.parent

        mode_str = "DRY RUN (preview only)" if dry_run else ("ARCHIVE" if archive else "DELETE")

        print("🧹 Spring Cleaning Executor")
        print(f"   Mode: {mode_str}")
        if dry_run:
            print("   ⚠️  This is a preview - no files will be modified")
        elif archive:
            print("   📦 Files will be archived (not deleted)")
        else:
            print("   ⚠️  WARNING: Files will be DELETED permanently!")
            response = input("   Continue? (yes/no): ")
            if response.lower() != "yes":
                print("   Cancelled.")
                return

        print()

        executor = SpringCleaningExecutor(project_root, dry_run=dry_run, archive=archive)
        results = executor.execute_safe_cleanup()

        executor.print_results()

        # Save results
        output_path = project_root / "data" / "time_tracking" / f"spring_cleaning_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"💾 Results saved to: {output_path}")
        print()

        if dry_run:
            print("NEXT STEPS:")
            print("1. Review the results above")
            print("2. Run with --execute to actually perform cleanup")
            print("3. Use --archive (default) to archive files safely")
            print("4. Use --delete only if you're sure (dangerous!)")
        print()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()