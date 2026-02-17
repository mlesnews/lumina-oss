#!/usr/bin/env python3
"""
Cleanup Dropbox Nested Inception & Duplicates

Dropbox is 15-20 years old with:
- Nested Dropbox inception (5+ levels deep)
- Duplicated directories/subdirectories/files
- Need to crush and recycle duplicates before migration

@DOIT #DROPBOX #CLEANUP #DEDUPLICATION #MIGRATION-PREP
"""

import sys
import hashlib
import shutil
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from datetime import datetime
from collections import defaultdict
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DropboxCleanup")


class DropboxNestedCleanup:
    """
    Cleanup Dropbox nested inception and duplicates

    Handles:
    - Nested Dropbox folders (5+ levels deep)
    - Duplicate directories and files
    - Crush and recycle duplicates
    """

    def __init__(self, dropbox_path: Optional[Path] = None):
        """Initialize cleanup"""
        if dropbox_path is None:
            dropbox_path = Path("C:/Users/mlesn/Dropbox")
        self.dropbox_path = Path(dropbox_path)

        self.recycle_dir = self.dropbox_path.parent / "Dropbox_Recycled"
        self.recycle_dir.mkdir(exist_ok=True)

        # Statistics
        self.stats = {
            "nested_dropbox_found": 0,
            "duplicates_found": 0,
            "files_recycled": 0,
            "space_freed_gb": 0.0,
            "nested_paths": [],
            "duplicate_groups": []
        }

        logger.info("✅ Dropbox Nested Cleanup initialized")
        logger.info(f"   Dropbox path: {self.dropbox_path}")
        logger.info(f"   Recycle dir: {self.recycle_dir}")

    def find_nested_dropbox_folders(self, max_depth: int = 10) -> List[Path]:
        """
        Find nested Dropbox folders (Dropbox inception)

        Looks for folders named "Dropbox" inside the Dropbox folder
        """
        logger.info("🔍 Searching for nested Dropbox folders...")

        nested_folders = []
        search_patterns = ["Dropbox", "dropbox", "DROPBOX"]

        def search_recursive(path: Path, depth: int = 0):
            if depth > max_depth:
                return

            try:
                for item in path.iterdir():
                    if item.is_dir():
                        # Check if this is a nested Dropbox folder
                        if any(item.name == pattern for pattern in search_patterns):
                            nested_folders.append(item)
                            logger.info(f"   ⚠️  Found nested Dropbox at depth {depth}: {item}")

                        # Recurse (but skip if we found a nested Dropbox to avoid infinite loops)
                        if item not in nested_folders:
                            search_recursive(item, depth + 1)
            except PermissionError:
                pass
            except Exception as e:
                logger.debug(f"Error searching {path}: {e}")

        search_recursive(self.dropbox_path, depth=0)

        self.stats["nested_dropbox_found"] = len(nested_folders)
        self.stats["nested_paths"] = [str(p) for p in nested_folders]

        logger.info(f"   ✅ Found {len(nested_folders)} nested Dropbox folder(s)")
        return nested_folders

    def calculate_file_hash(self, file_path: Path, chunk_size: int = 8192) -> Optional[str]:
        """Calculate MD5 hash of file for duplicate detection"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.debug(f"Error hashing {file_path}: {e}")
            return None

    def find_duplicate_files(self, max_files: int = 100000) -> Dict[str, List[Path]]:
        """
        Find duplicate files by content hash

        Returns dict mapping hash -> list of file paths with that hash
        """
        logger.info("🔍 Searching for duplicate files...")
        logger.info("   This may take a while for large Dropbox...")

        file_hashes: Dict[str, List[Path]] = defaultdict(list)
        files_processed = 0

        def scan_recursive(path: Path, depth: int = 0):
            nonlocal files_processed

            if files_processed >= max_files:
                return

            try:
                for item in path.iterdir():
                    if files_processed >= max_files:
                        break

                    if item.is_file():
                        files_processed += 1
                        if files_processed % 1000 == 0:
                            logger.info(f"   Processed {files_processed:,} files...")

                        file_hash = self.calculate_file_hash(item)
                        if file_hash:
                            file_hashes[file_hash].append(item)

                    elif item.is_dir():
                        # Skip nested Dropbox folders (will handle separately)
                        if item.name.lower() == "dropbox":
                            continue
                        scan_recursive(item, depth + 1)
            except PermissionError:
                pass
            except Exception as e:
                logger.debug(f"Error scanning {path}: {e}")

        scan_recursive(self.dropbox_path)

        # Filter to only duplicates (hash appears more than once)
        duplicates = {h: paths for h, paths in file_hashes.items() if len(paths) > 1}

        self.stats["duplicates_found"] = sum(len(paths) - 1 for paths in duplicates.values())
        self.stats["duplicate_groups"] = [
            {"hash": h, "count": len(paths), "files": [str(p) for p in paths]}
            for h, paths in duplicates.items()
        ]

        logger.info(f"   ✅ Found {len(duplicates)} duplicate groups ({self.stats['duplicates_found']} duplicate files)")
        return duplicates

    def recycle_duplicate_files(
        self,
        duplicates: Dict[str, List[Path]],
        keep_strategy: str = "oldest"
    ) -> Dict[str, Any]:
        """
        Recycle duplicate files, keeping one copy based on strategy

        Strategies:
        - "oldest": Keep the oldest file (by modification time)
        - "newest": Keep the newest file
        - "shortest_path": Keep the file with shortest path
        - "longest_path": Keep the file with longest path
        """
        logger.info("♻️  Recycling duplicate files...")
        logger.info(f"   Strategy: {keep_strategy}")

        recycled = 0
        space_freed = 0

        for file_hash, file_paths in duplicates.items():
            if len(file_paths) <= 1:
                continue

            # Determine which file to keep
            if keep_strategy == "oldest":
                keep_file = min(file_paths, key=lambda p: p.stat().st_mtime)
            elif keep_strategy == "newest":
                keep_file = max(file_paths, key=lambda p: p.stat().st_mtime)
            elif keep_strategy == "shortest_path":
                keep_file = min(file_paths, key=lambda p: len(str(p)))
            elif keep_strategy == "longest_path":
                keep_file = max(file_paths, key=lambda p: len(str(p)))
            else:
                keep_file = file_paths[0]  # Default: first one

            # Recycle the rest
            for file_path in file_paths:
                if file_path == keep_file:
                    continue

                try:
                    # Calculate size before moving
                    file_size = file_path.stat().st_size

                    # Move to recycle directory, preserving relative path
                    relative_path = file_path.relative_to(self.dropbox_path)
                    recycle_target = self.recycle_dir / relative_path
                    recycle_target.parent.mkdir(parents=True, exist_ok=True)

                    # Handle name conflicts
                    counter = 1
                    original_target = recycle_target
                    while recycle_target.exists():
                        stem = original_target.stem
                        suffix = original_target.suffix
                        recycle_target = original_target.parent / f"{stem}_dup{counter}{suffix}"
                        counter += 1

                    shutil.move(str(file_path), str(recycle_target))

                    recycled += 1
                    space_freed += file_size

                    if recycled % 100 == 0:
                        logger.info(f"   Recycled {recycled:,} duplicate files...")

                except Exception as e:
                    logger.warning(f"   ⚠️  Error recycling {file_path}: {e}")

        space_freed_gb = space_freed / (1024 ** 3)
        self.stats["files_recycled"] = recycled
        self.stats["space_freed_gb"] = space_freed_gb

        logger.info(f"   ✅ Recycled {recycled:,} duplicate files")
        logger.info(f"   💾 Space freed: {space_freed_gb:.2f} GB")

        return {
            "recycled": recycled,
            "space_freed_gb": space_freed_gb
        }

    def crush_nested_dropbox_folders(
        self,
        nested_folders: List[Path],
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Crush nested Dropbox folders by flattening them

        Moves contents of nested Dropbox folders up to parent level
        """
        logger.info("💥 Crushing nested Dropbox folders...")

        if dry_run:
            logger.info("   🔍 DRY RUN - No folders will be crushed")

        crushed = 0
        space_freed = 0

        for nested_folder in nested_folders:
            try:
                # Calculate size
                folder_size = sum(
                    f.stat().st_size for f in nested_folder.rglob('*') if f.is_file()
                )

                if dry_run:
                    logger.info(f"   Would crush: {nested_folder} ({folder_size / (1024**3):.2f} GB)")
                    crushed += 1
                    space_freed += folder_size
                    continue

                # Move contents to parent, then remove nested folder
                parent = nested_folder.parent

                # Move all contents
                for item in nested_folder.iterdir():
                    target = parent / item.name

                    # Handle name conflicts
                    counter = 1
                    original_target = target
                    while target.exists():
                        if item.is_file():
                            stem = original_target.stem
                            suffix = original_target.suffix
                            target = original_target.parent / f"{stem}_nested{counter}{suffix}"
                        else:
                            target = original_target.parent / f"{original_target.name}_nested{counter}"
                        counter += 1

                    shutil.move(str(item), str(target))

                # Remove empty nested folder
                nested_folder.rmdir()

                crushed += 1
                space_freed += folder_size

                logger.info(f"   ✅ Crushed: {nested_folder}")

            except Exception as e:
                logger.error(f"   ❌ Error crushing {nested_folder}: {e}")

        space_freed_gb = space_freed / (1024 ** 3)

        logger.info(f"   ✅ Crushed {crushed} nested Dropbox folder(s)")
        logger.info(f"   💾 Space freed: {space_freed_gb:.2f} GB")

        return {
            "crushed": crushed,
            "space_freed_gb": space_freed_gb
        }

    def cleanup_all(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Complete cleanup process:
        1. Find nested Dropbox folders
        2. Find duplicate files
        3. Recycle duplicates
        4. Crush nested folders
        """
        logger.info("=" * 80)
        logger.info("🧹 DROPBOX NESTED CLEANUP & DEDUPLICATION")
        logger.info("=" * 80)
        logger.info("   Handling 15-20 year old Dropbox with nested inception")
        logger.info("")

        if dry_run:
            logger.info("🔍 DRY RUN MODE - No files will be modified")
            logger.info("")

        results = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "nested_cleanup": {},
            "duplicate_cleanup": {},
            "total_space_freed_gb": 0.0
        }

        # Step 1: Find nested Dropbox folders
        nested_folders = self.find_nested_dropbox_folders()
        logger.info("")

        # Step 2: Find duplicate files
        duplicates = self.find_duplicate_files()
        logger.info("")

        # Step 3: Recycle duplicates
        if duplicates:
            duplicate_result = self.recycle_duplicate_files(duplicates, keep_strategy="oldest")
            results["duplicate_cleanup"] = duplicate_result
            results["total_space_freed_gb"] += duplicate_result.get("space_freed_gb", 0)
        logger.info("")

        # Step 4: Crush nested folders
        if nested_folders:
            nested_result = self.crush_nested_dropbox_folders(nested_folders, dry_run=dry_run)
            results["nested_cleanup"] = nested_result
            results["total_space_freed_gb"] += nested_result.get("space_freed_gb", 0)
        logger.info("")

        # Summary
        logger.info("=" * 80)
        logger.info("📊 CLEANUP SUMMARY")
        logger.info("=" * 80)
        logger.info(f"   Nested Dropbox folders found: {len(nested_folders)}")
        logger.info(f"   Duplicate groups found: {len(duplicates)}")
        logger.info(f"   Total space freed: {results['total_space_freed_gb']:.2f} GB")
        logger.info("=" * 80)

        return results


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(
            description="Cleanup Dropbox Nested Inception & Duplicates"
        )
        parser.add_argument("--dropbox-path", type=str, help="Dropbox path (default: C:/Users/mlesn/Dropbox)")
        parser.add_argument("--dry-run", action="store_true", help="Dry run (don't modify files)")
        parser.add_argument("--find-nested-only", action="store_true", help="Only find nested Dropbox folders")
        parser.add_argument("--find-duplicates-only", action="store_true", help="Only find duplicate files")

        args = parser.parse_args()

        dropbox_path = Path(args.dropbox_path) if args.dropbox_path else None
        cleanup = DropboxNestedCleanup(dropbox_path=dropbox_path)

        if args.find_nested_only:
            nested = cleanup.find_nested_dropbox_folders()
            print(f"\nFound {len(nested)} nested Dropbox folders:")
            for folder in nested:
                print(f"  - {folder}")
        elif args.find_duplicates_only:
            duplicates = cleanup.find_duplicate_files()
            print(f"\nFound {len(duplicates)} duplicate groups")
            for hash_val, paths in list(duplicates.items())[:10]:  # Show first 10
                print(f"\nHash: {hash_val[:16]}... ({len(paths)} copies)")
                for path in paths[:5]:  # Show first 5 paths
                    print(f"  - {path}")
        else:
            results = cleanup.cleanup_all(dry_run=args.dry_run)

            if not results.get("dry_run") and results.get("total_space_freed_gb", 0) > 0:
                print(f"\n✅ Cleanup complete! Freed {results['total_space_freed_gb']:.2f} GB")
                print("   Ready for migration")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())