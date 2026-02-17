#!/usr/bin/env python3
"""
Cleanup Dropbox Before Migration

Dropbox is 15-20 years old with nested/duplicated directories (5+ levels deep).
This script:
1. Finds and removes duplicate files/directories
2. Handles nested Dropbox structures (Dropbox inception)
3. Crushes and recycles duplicates
4. Prepares for clean migration

@DOIT #CLEANUP #DEDUPLICATION #DROPBOX #MIGRATION-PREP
"""

import sys
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import logging
import json
import shutil
import time

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CleanupDropbox")


class DropboxCleanup:
    """
    Cleanup and deduplicate Dropbox before migration

    Handles:
    - Nested Dropbox structures (Dropbox inception)
    - Duplicate files/directories
    - Old/unused files
    """

    def __init__(self, dropbox_path: Path, dry_run: bool = False):
        """Initialize cleanup"""
        self.dropbox_path = Path(dropbox_path)
        self.dry_run = dry_run
        self.recycle_bin = self.dropbox_path.parent / "Dropbox_RecycleBin"
        self.recycle_bin.mkdir(exist_ok=True)

        # Progress tracking
        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent
        self.progress_file = project_root / "data" / "cleanup_progress.json"
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)

        # Statistics
        self.stats = {
            "duplicates_found": 0,
            "duplicates_removed": 0,
            "nested_dropbox_found": 0,
            "nested_dropbox_removed": 0,
            "space_freed_gb": 0.0,
            "files_processed": 0,
            "total_files": 0,
            "current_file": 0,
            "errors": []
        }

        logger.info("✅ Dropbox Cleanup initialized")
        logger.info(f"   Dropbox path: {self.dropbox_path}")
        logger.info(f"   Recycle bin: {self.recycle_bin}")
        logger.info(f"   Dry run: {dry_run}")

    def count_total_files(self) -> int:
        """Count total files in Dropbox for progress tracking"""
        try:
            count = 0
            for item in self.dropbox_path.rglob("*"):
                if item.is_file():
                    count += 1
            return count
        except Exception as e:
            logger.warning(f"   ⚠️  Error counting files: {e}")
            return 0

    def write_progress(self, progress_data: Dict[str, Any]):
        """Write progress to JSON file for real-time monitoring"""
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(progress_data, f, indent=2)
        except Exception as e:
            logger.debug(f"Error writing progress: {e}")

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file for duplicate detection"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                # Read in chunks to handle large files
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.debug(f"Error hashing {file_path}: {e}")
            return ""

    def find_nested_dropbox_structures(self) -> List[Path]:
        """Find nested Dropbox directories (Dropbox inception)"""
        logger.info("🔍 Finding nested Dropbox structures...")

        nested_dropboxes = []

        # Look for directories named "Dropbox" inside Dropbox
        for dropbox_dir in self.dropbox_path.rglob("Dropbox"):
            if dropbox_dir.is_dir():
                # Check if it's actually a nested Dropbox (not the root)
                if dropbox_dir != self.dropbox_path:
                    # Check depth - if it's 5+ levels deep, it's likely inception
                    depth = len(dropbox_dir.relative_to(self.dropbox_path).parts)
                    if depth >= 5:
                        nested_dropboxes.append(dropbox_dir)
                        logger.info(f"   Found nested Dropbox at depth {depth}: {dropbox_dir.relative_to(self.dropbox_path)}")

        self.stats["nested_dropbox_found"] = len(nested_dropboxes)
        logger.info(f"   ✅ Found {len(nested_dropboxes)} nested Dropbox structures")

        return nested_dropboxes

    def find_duplicate_files(self, max_files: int = 10000) -> Dict[str, List[Path]]:
        """
        Find duplicate files by hash

        Limits to max_files to avoid memory issues with 15-20 years of files
        """
        logger.info("🔍 Finding duplicate files...")
        logger.info(f"   Processing up to {max_files:,} files (to avoid memory issues)")

        hash_to_files: Dict[str, List[Path]] = defaultdict(list)
        files_processed = 0

        # Process files in batches
        for file_path in self.dropbox_path.rglob("*"):
            if files_processed >= max_files:
                logger.warning(f"   ⚠️  Reached file limit ({max_files:,}) - stopping scan")
                break

            if file_path.is_file():
                try:
                    # Skip very large files (likely not duplicates)
                    if file_path.stat().st_size > 100 * 1024 * 1024:  # 100 MB
                        continue

                    file_hash = self.calculate_file_hash(file_path)
                    if file_hash:
                        hash_to_files[file_hash].append(file_path)
                        files_processed += 1

                    if files_processed % 1000 == 0:
                        logger.info(f"   Processed {files_processed:,} files...")

                except Exception as e:
                    logger.debug(f"Error processing {file_path}: {e}")
                    continue

        # Find duplicates (files with same hash, count > 1)
        duplicates = {
            file_hash: files
            for file_hash, files in hash_to_files.items()
            if len(files) > 1
        }

        self.stats["duplicates_found"] = sum(len(files) - 1 for files in duplicates.values())
        self.stats["files_processed"] = files_processed

        logger.info(f"   ✅ Found {len(duplicates)} sets of duplicates ({self.stats['duplicates_found']} duplicate files)")

        return duplicates

    def find_duplicate_directories(self) -> List[Tuple[Path, Path]]:
        """Find duplicate directory structures"""
        logger.info("🔍 Finding duplicate directories...")

        # This is a simplified approach - look for directories with same name and similar structure
        # In a full implementation, you'd compare directory contents
        duplicate_dirs = []

        # Group directories by name
        dirs_by_name = defaultdict(list)
        for dir_path in self.dropbox_path.rglob("*"):
            if dir_path.is_dir():
                dirs_by_name[dir_path.name].append(dir_path)

        # Find directories with same name in similar locations
        for dir_name, dir_paths in dirs_by_name.items():
            if len(dir_paths) > 1:
                # Check if they're in similar parent directories (likely duplicates)
                for i, dir1 in enumerate(dir_paths):
                    for dir2 in dir_paths[i+1:]:
                        # Check if they have similar parent paths
                        parent1 = dir1.parent.name
                        parent2 = dir2.parent.name
                        if parent1 == parent2 or abs(len(dir1.parts) - len(dir2.parts)) <= 1:
                            duplicate_dirs.append((dir1, dir2))

        logger.info(f"   ✅ Found {len(duplicate_dirs)} potential duplicate directory pairs")

        return duplicate_dirs

    def recycle_file(self, file_path: Path) -> bool:
        """Move file to recycle bin"""
        try:
            # Create recycle bin path maintaining structure
            relative_path = file_path.relative_to(self.dropbox_path)
            recycle_path = self.recycle_bin / relative_path
            recycle_path.parent.mkdir(parents=True, exist_ok=True)

            if not self.dry_run:
                shutil.move(str(file_path), str(recycle_path))
                logger.debug(f"   Recycled: {file_path.name}")
            else:
                logger.debug(f"   [DRY RUN] Would recycle: {file_path.name}")

            return True
        except Exception as e:
            logger.warning(f"   ⚠️  Error recycling {file_path}: {e}")
            self.stats["errors"].append(f"Error recycling {file_path}: {e}")
            return False

    def remove_duplicate_files(self, duplicates: Dict[str, List[Path]], start_time: datetime) -> int:
        """Remove duplicate files, keeping the oldest or most complete version"""
        logger.info("🗑️  Removing duplicate files...")

        # Calculate total duplicates to remove
        total_duplicates = sum(len(files) - 1 for files in duplicates.values() if len(files) > 1)
        logger.info(f"   📊 Total duplicate files to remove: {total_duplicates:,}")

        removed_count = 0
        processed_count = 0

        for file_hash, files in duplicates.items():
            if len(files) <= 1:
                continue

            # Sort by: 1) Path depth (shallow first), 2) Modification time (oldest first)
            files_sorted = sorted(
                files,
                key=lambda f: (len(f.relative_to(self.dropbox_path).parts), f.stat().st_mtime)
            )

            # Keep the first (shallowest, oldest)
            keep_file = files_sorted[0]

            # Remove duplicates
            for duplicate_file in files_sorted[1:]:
                try:
                    file_size = duplicate_file.stat().st_size

                    if self.recycle_file(duplicate_file):
                        removed_count += 1
                        processed_count += 1
                        self.stats["space_freed_gb"] += file_size / (1024 ** 3)
                        self.stats["duplicates_removed"] += 1
                        self.stats["current_file"] = processed_count

                        # Update progress
                        if total_duplicates > 0:
                            percentage = (processed_count / total_duplicates) * 100
                            elapsed = (datetime.now() - start_time).total_seconds()

                            speed = 0.0
                            eta_str = "Calculating..."

                            if processed_count > 0 and elapsed > 0:
                                speed = processed_count / elapsed
                                remaining = total_duplicates - processed_count
                                eta_seconds = remaining / speed if speed > 0 else 0
                                eta_timedelta = timedelta(seconds=int(eta_seconds))
                                hours = eta_timedelta.seconds // 3600
                                minutes = (eta_timedelta.seconds % 3600) // 60
                                seconds = eta_timedelta.seconds % 60

                                if hours > 0:
                                    eta_str = f"{hours}h {minutes}m {seconds}s"
                                elif minutes > 0:
                                    eta_str = f"{minutes}m {seconds}s"
                                else:
                                    eta_str = f"{seconds}s"

                            progress_data = {
                                "status": "running",
                                "phase": "removing_duplicates",
                                "total_files": total_duplicates,
                                "current_file": processed_count,
                                "removed_files": removed_count,
                                "percentage": round(percentage, 2),
                                "eta_formatted": eta_str,
                                "speed_files_per_second": round(speed, 2),
                                "space_freed_gb": round(self.stats["space_freed_gb"], 2),
                                "elapsed_seconds": round(elapsed, 1)
                            }
                            self.write_progress(progress_data)

                            if processed_count % 100 == 0:
                                logger.info(
                                    f"   📊 Progress: {processed_count:,}/{total_duplicates:,} "
                                    f"({percentage:.1f}%) | Removed: {removed_count:,} | "
                                    f"ETA: {eta_str} | Speed: {speed:.1f} files/sec"
                                )
                except Exception as e:
                    logger.warning(f"   ⚠️  Error removing duplicate {duplicate_file}: {e}")
                    self.stats["errors"].append(f"Error removing {duplicate_file}: {e}")

        logger.info(f"   ✅ Removed {removed_count} duplicate files")
        logger.info(f"   💾 Space freed: {self.stats['space_freed_gb']:.2f} GB")

        return removed_count

    def remove_nested_dropbox(self, nested_dropboxes: List[Path]) -> int:
        """Remove nested Dropbox structures"""
        logger.info("🗑️  Removing nested Dropbox structures...")

        removed_count = 0

        for nested_path in nested_dropboxes:
            try:
                # Calculate size before removal
                size_gb = sum(
                    f.stat().st_size for f in nested_path.rglob("*") if f.is_file()
                ) / (1024 ** 3)

                # Move to recycle bin
                relative_path = nested_path.relative_to(self.dropbox_path)
                recycle_path = self.recycle_bin / "nested_dropbox" / relative_path

                if not self.dry_run:
                    shutil.move(str(nested_path), str(recycle_path))
                    logger.info(f"   Removed nested Dropbox: {relative_path} ({size_gb:.2f} GB)")
                else:
                    logger.info(f"   [DRY RUN] Would remove nested Dropbox: {relative_path} ({size_gb:.2f} GB)")

                removed_count += 1
                self.stats["nested_dropbox_removed"] += 1
                self.stats["space_freed_gb"] += size_gb

            except Exception as e:
                logger.warning(f"   ⚠️  Error removing nested Dropbox {nested_path}: {e}")
                self.stats["errors"].append(f"Error removing {nested_path}: {e}")

        logger.info(f"   ✅ Removed {removed_count} nested Dropbox structures")

        return removed_count

    def cleanup_dropbox(self) -> Dict[str, Any]:
        """Main cleanup process with full progress tracking"""
        start_time = datetime.now()

        logger.info("=" * 80)
        logger.info("🧹 DROPBOX CLEANUP BEFORE MIGRATION")
        logger.info("=" * 80)
        logger.info("   Dropbox is 15-20 years old with nested/duplicated structures")
        logger.info("   Cleaning up before migration to DSM-compounded local cloud package")
        logger.info("")

        if self.dry_run:
            logger.info("🔍 DRY RUN MODE - No files will be removed")
            logger.info("")

        # COUNT TOTAL FILES
        logger.info("📊 Counting total files in Dropbox...")
        total_files = self.count_total_files()
        self.stats["total_files"] = total_files
        logger.info(f"   📁 Total files: {total_files:,}")
        logger.info("")

        # Initialize progress
        progress_data = {
            "status": "running",
            "phase": "scanning",
            "total_files": total_files,
            "current_file": 0,
            "percentage": 0.0,
            "start_time": start_time.isoformat(),
            "elapsed_seconds": 0,
            "eta_formatted": "Calculating...",
            "nested_dropbox_found": 0,
            "nested_dropbox_removed": 0,
            "duplicates_found": 0,
            "duplicates_removed": 0,
            "space_freed_gb": 0.0
        }
        self.write_progress(progress_data)

        # Step 1: Find nested Dropbox structures
        logger.info("🔍 Step 1: Finding nested Dropbox structures...")
        nested_dropboxes = self.find_nested_dropbox_structures()
        self.stats["nested_dropbox_found"] = len(nested_dropboxes)
        progress_data["nested_dropbox_found"] = len(nested_dropboxes)
        progress_data["phase"] = "removing_nested"
        self.write_progress(progress_data)
        logger.info(f"   Found {len(nested_dropboxes)} nested Dropbox structures")
        logger.info("")

        # Step 2: Find duplicate files
        logger.info("🔍 Step 2: Finding duplicate files...")
        logger.info("   This may take a while for 15-20 years of data...")
        duplicates = self.find_duplicate_files(max_files=10000)
        self.stats["duplicates_found"] = sum(len(files) - 1 for files in duplicates.values() if len(files) > 1)
        progress_data["duplicates_found"] = self.stats["duplicates_found"]
        progress_data["phase"] = "removing_duplicates"
        self.write_progress(progress_data)
        logger.info(f"   Found {self.stats['duplicates_found']:,} duplicate files")
        logger.info("")

        # Step 3: Remove nested Dropbox structures
        if nested_dropboxes:
            logger.info("🗑️  Step 3: Removing nested Dropbox structures...")
            self.remove_nested_dropbox(nested_dropboxes)
            progress_data["nested_dropbox_removed"] = self.stats["nested_dropbox_removed"]
            self.write_progress(progress_data)
            logger.info("")

        # Step 4: Remove duplicate files
        if duplicates:
            logger.info("🗑️  Step 4: Removing duplicate files...")
            self.remove_duplicate_files(duplicates, start_time)
            progress_data["duplicates_removed"] = self.stats["duplicates_removed"]
            progress_data["space_freed_gb"] = round(self.stats["space_freed_gb"], 2)
            self.write_progress(progress_data)
            logger.info("")

        # Final summary
        elapsed = (datetime.now() - start_time).total_seconds()
        progress_data.update({
            "status": "completed",
            "phase": "complete",
            "percentage": 100.0,
            "elapsed_seconds": round(elapsed, 1),
            "eta_formatted": "Complete"
        })
        self.write_progress(progress_data)

        logger.info("=" * 80)
        logger.info("📊 CLEANUP SUMMARY")
        logger.info("=" * 80)
        logger.info(f"   Total files scanned: {total_files:,}")
        logger.info(f"   Nested Dropbox found: {self.stats['nested_dropbox_found']}")
        logger.info(f"   Nested Dropbox removed: {self.stats['nested_dropbox_removed']}")
        logger.info(f"   Duplicate files found: {self.stats['duplicates_found']:,}")
        logger.info(f"   Duplicate files removed: {self.stats['duplicates_removed']:,}")
        logger.info(f"   Files processed: {self.stats['files_processed']:,}")
        logger.info(f"   Space freed: {self.stats['space_freed_gb']:.2f} GB")
        logger.info(f"   Time elapsed: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
        logger.info(f"   Errors: {len(self.stats['errors'])}")
        logger.info("=" * 80)

        if self.stats["errors"]:
            logger.warning("⚠️  Errors encountered:")
            for error in self.stats["errors"][:10]:  # Show first 10
                logger.warning(f"   {error}")

        return {
            "success": len(self.stats["errors"]) == 0,
            "stats": self.stats,
            "dry_run": self.dry_run,
            "elapsed_seconds": elapsed
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(
            description="Cleanup Dropbox Before Migration"
        )
        parser.add_argument(
            "--dropbox-path",
            type=str,
            default="C:/Users/mlesn/Dropbox",
            help="Path to Dropbox directory"
        )
        parser.add_argument("--dry-run", action="store_true", help="Dry run (don't actually remove files)")

        args = parser.parse_args()

        dropbox_path = Path(args.dropbox_path)

        if not dropbox_path.exists():
            logger.error(f"❌ Dropbox path does not exist: {dropbox_path}")
            return 1

        cleanup = DropboxCleanup(dropbox_path, dry_run=args.dry_run)
        result = cleanup.cleanup_dropbox()

        return 0 if result["success"] else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())