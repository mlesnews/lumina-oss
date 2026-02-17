#!/usr/bin/env python3
"""
Fix Dropbox Nested Folders

Identifies and fixes nested "Dropbox" folders inside Dropbox directory structure.
Renames nested folders to prevent confusion and sync issues.

Author: <COMPANY_NAME> LLC
Date: 2025-01-24
Issue: Nested Dropbox folders create confusing directory structure
"""

from __future__ import annotations

import shutil
import sys
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import json

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)


class DropboxNestingFixer:
    """Fix nested Dropbox folders"""

    def __init__(self, dropbox_path: Path, dry_run: bool = False, backup: bool = True):
        """
        Initialize fixer.

        Args:
            dropbox_path: Path to Dropbox root directory
            dry_run: If True, show what would be done without making changes
            backup: If True, create backups before renaming
        """
        self.dropbox_path = Path(dropbox_path).resolve()
        self.dry_run = dry_run
        self.backup = backup
        self.logger = get_logger("DropboxNestingFixer")
        self.found_nested: List[Dict[str, any]] = []
        self.fixed_nested: List[Dict[str, any]] = []
        self.backup_root: Optional[Path] = None

        if backup and not dry_run:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.backup_root = self.dropbox_path.parent / f"Dropbox_Reorganization_Backup_{timestamp}"
            self.backup_root.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Backup location: {self.backup_root}")

    def find_nested_dropbox(self, search_path: Path, depth: int = 0, max_depth: int = 15) -> List[Dict[str, any]]:
        """
        Recursively find nested "Dropbox" folders.

        Args:
            search_path: Directory to search
            depth: Current depth in recursion
            max_depth: Maximum depth to search

        Returns:
            List of nested Dropbox folder information
        """
        nested = []

        if depth > max_depth:
            return nested

        if not search_path.exists() or not search_path.is_dir():
            return nested

        try:
            # Look for folders named "Dropbox" or "dropbox"
            for item in search_path.iterdir():
                if item.is_dir() and item.name.lower() == "dropbox":
                    # Calculate size (approximate)
                    try:
                        size_gb = sum(
                            f.stat().st_size for f in item.rglob('*') if f.is_file()
                        ) / (1024 ** 3)
                    except (PermissionError, OSError):
                        size_gb = 0.0

                    nested_info = {
                        "path": str(item),
                        "depth": depth,
                        "parent": str(search_path),
                        "size_gb": round(size_gb, 2),
                        "name": item.name
                    }
                    nested.append(nested_info)

                    # Recurse into nested folder to find deeper nesting
                    nested.extend(self.find_nested_dropbox(item, depth + 1, max_depth))

        except (PermissionError, OSError) as e:
            self.logger.debug(f"Access denied to {search_path}: {e}")

        return nested

    def fix_nested_folder(self, nested_info: Dict[str, any]) -> bool:
        """
        Fix a single nested Dropbox folder by renaming it.

        Args:
            nested_info: Information about the nested folder

        Returns:
            True if fix succeeded, False otherwise
        """
        nested_path = Path(nested_info["path"])
        parent_path = Path(nested_info["parent"])

        # Generate new name
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_name = f"Dropbox_Flattened_{timestamp}"
        new_path = parent_path / new_name

        self.logger.info(f"\nFixing nested folder:")
        self.logger.info(f"  Path: {nested_path}")
        self.logger.info(f"  Depth: {nested_info['depth']}")
        self.logger.info(f"  Size: {nested_info['size_gb']} GB")
        self.logger.info(f"  New name: {new_name}")

        if self.dry_run:
            self.logger.info(f"  [DRY RUN] Would rename to: {new_path}")
            return True

        try:
            # Backup if requested
            if self.backup and self.backup_root:
                # Create unique backup path using hash of full path to prevent collisions
                # when multiple nested folders share the same name
                path_hash = hashlib.md5(str(nested_path).encode('utf-8')).hexdigest()[:8]
                backup_path = self.backup_root / f"nested_{nested_path.name}_{path_hash}_backup"
                self.logger.info(f"  Creating backup: {backup_path}")
                shutil.copytree(nested_path, backup_path, dirs_exist_ok=True)

            # Rename folder
            nested_path.rename(new_path)
            self.logger.info(f"  ✓ Renamed successfully")

            self.fixed_nested.append({
                **nested_info,
                "new_path": str(new_path),
                "fixed_at": datetime.now().isoformat()
            })

            return True

        except Exception as e:
            self.logger.error(f"  ✗ Failed to fix: {e}", exc_info=True)
            return False

    def fix_all_nested(self) -> Dict[str, any]:
        """
        Find and fix all nested Dropbox folders.

        Returns:
            Summary of fixes
        """
        self.logger.info("=" * 60)
        self.logger.info("Dropbox Nested Folders Fix")
        self.logger.info("=" * 60)
        self.logger.info(f"Searching in: {self.dropbox_path}")
        self.logger.info(f"Mode: {'DRY RUN (no changes)' if self.dry_run else 'LIVE (will make changes)'}")
        self.logger.info("")

        # Find all nested folders
        self.logger.info("Scanning for nested Dropbox folders...")
        self.found_nested = self.find_nested_dropbox(self.dropbox_path)

        if not self.found_nested:
            self.logger.info("✓ No nested Dropbox folders found!")
            return {
                "success": True,
                "found": 0,
                "fixed": 0,
                "nested_folders": []
            }

        self.logger.info(f"\nFound {len(self.found_nested)} nested Dropbox folder(s):")

        # Group by depth
        by_depth = {}
        for nested in self.found_nested:
            depth = nested["depth"]
            if depth not in by_depth:
                by_depth[depth] = []
            by_depth[depth].append(nested)

        for depth in sorted(by_depth.keys()):
            folders = by_depth[depth]
            self.logger.info(f"\n  Depth {depth} ({len(folders)} folders):")
            for nested in folders[:10]:  # Show first 10
                self.logger.info(f"    - {nested['path']} ({nested['size_gb']} GB)")
            if len(folders) > 10:
                self.logger.info(f"    ... and {len(folders) - 10} more")

        # Fix all nested folders
        self.logger.info("\n" + "=" * 60)
        self.logger.info("Fixing nested folders...")
        self.logger.info("=" * 60)

        fixed = 0
        failed = 0

        for nested in self.found_nested:
            if self.fix_nested_folder(nested):
                fixed += 1
            else:
                failed += 1

        summary = {
            "success": failed == 0,
            "found": len(self.found_nested),
            "fixed": fixed,
            "failed": failed,
            "nested_folders": self.found_nested,
            "fixed_folders": self.fixed_nested,
            "backup_location": str(self.backup_root) if self.backup_root else None
        }

        return summary

    def save_report(self, report_path: Optional[Path] = None):
        try:
            """Save fix report to JSON file"""
            if report_path is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                report_path = Path(f"dropbox_nesting_fix_report_{timestamp}.json")

            report = {
                "fix_date": datetime.now().isoformat(),
                "dropbox_path": str(self.dropbox_path),
                "dry_run": self.dry_run,
                "backup": self.backup,
                "found_nested": self.found_nested,
                "fixed_nested": self.fixed_nested,
                "backup_location": str(self.backup_root) if self.backup_root else None
            }

            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)

            self.logger.info(f"\nReport saved: {report_path}")


        except Exception as e:
            self.logger.error(f"Error in save_report: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Fix nested Dropbox folders",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run to see what would be fixed
  python fix_dropbox_nesting.py --dry-run

  # Fix nested folders with backup
  python fix_dropbox_nesting.py --path "C:\\Users\\mlesn\\Dropbox" --backup

  # Fix without backup (not recommended)
  python fix_dropbox_nesting.py --path "C:\\Users\\mlesn\\Dropbox" --no-backup
        """
    )
    parser.add_argument(
        "--path",
        type=str,
        default="C:\\Users\\mlesn\\Dropbox",
        help="Path to Dropbox root directory"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        default=True,
        help="Create backup before renaming (default: True)"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Don't create backup (not recommended)"
    )
    parser.add_argument(
        "--report",
        type=str,
        help="Path to save report JSON (default: auto-generated)"
    )

    args = parser.parse_args()

    backup = args.backup and not args.no_backup

    if args.dry_run:
        print("\n" + "="*60)
        print("DRY RUN MODE - No changes will be made")
        print("="*60 + "\n")

    fixer = DropboxNestingFixer(
        dropbox_path=Path(args.path),
        dry_run=args.dry_run,
        backup=backup
    )

    summary = fixer.fix_all_nested()

    # Save report
    report_path = Path(args.report) if args.report else None
    fixer.save_report(report_path)

    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Nested folders found: {summary['found']}")
    print(f"Successfully fixed: {summary['fixed']}")
    print(f"Failed: {summary['failed']}")
    if summary.get('backup_location'):
        print(f"Backup location: {summary['backup_location']}")
    print("="*60)

    if summary['found'] == 0:
        print("\n✓ No nested folders found - structure is clean!")
    elif summary['failed'] > 0:
        return 1

    return 0


if __name__ == "__main__":



    sys.exit(main())