#!/usr/bin/env python3
"""
MONSTER FILE SLAYER - RAID BOSS CLEANUP SCRIPT
"BY FIRE BE PURGED!" - Ragnaros, probably

This script identifies and cleans up large files that are causing
performance issues in Cursor/VS Code.
"""

import os
import json
import gzip
import shutil
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Tuple, Dict
import argparse
import logging
logger = logging.getLogger("slay_monster_files")


# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
try:
    from json_to_holocron import HolocronConverter
    HOLOCRON_AVAILABLE = True
except ImportError:
    HOLOCRON_AVAILABLE = False

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LARGE_FILE_THRESHOLD_MB = 100  # Files larger than 100MB are considered "monsters"
COMPRESSION_THRESHOLD_MB = 50  # Files larger than 50MB should be compressed
BACKUP_RETENTION_DAYS = 30  # Keep backups for 30 days
MAX_NESTED_BACKUP_DEPTH = 2  # Maximum allowed nesting depth

class MonsterFileSlayer:
    """Slays monster files with the fury of Ragnaros himself!"""

    def __init__(self, dry_run: bool = True, convert_to_holocron: bool = False):
        self.dry_run = dry_run
        self.convert_to_holocron = convert_to_holocron and HOLOCRON_AVAILABLE
        if self.convert_to_holocron and not HOLOCRON_AVAILABLE:
            print("⚠️  Warning: Holocron converter not available")
        self.holocron_converter = HolocronConverter() if self.convert_to_holocron else None
        self.stats = {
            'files_found': 0,
            'files_compressed': 0,
            'files_deleted': 0,
            'files_converted_to_holocron': 0,
            'space_freed_mb': 0,
            'nested_backups_removed': 0
        }

    def find_monster_files(self, threshold_mb: int = LARGE_FILE_THRESHOLD_MB) -> List[Tuple[Path, float]]:
        """Find all files larger than threshold."""
        monsters = []
        for file_path in DATA_DIR.rglob("*"):
            if file_path.is_file():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                if size_mb > threshold_mb:
                    monsters.append((file_path, size_mb))
        return sorted(monsters, key=lambda x: x[1], reverse=True)

    def find_nested_backups(self) -> List[Path]:
        try:
            """Find nested backup directories that are causing issues."""
            nested_backups = []
            local_backup_dir = DATA_DIR / "local_backup"

            if not local_backup_dir.exists():
                return nested_backups

            # Find directories that contain "local_backup" in their path more than MAX_NESTED_BACKUP_DEPTH times
            for item in local_backup_dir.rglob("*"):
                if item.is_dir():
                    path_str = str(item.relative_to(DATA_DIR))
                    # Count occurrences of "local_backup" in path
                    depth = path_str.count("local_backup")
                    if depth > MAX_NESTED_BACKUP_DEPTH:
                        nested_backups.append(item)

            return nested_backups

        except Exception as e:
            self.logger.error(f"Error in find_nested_backups: {e}", exc_info=True)
            raise
    def compress_large_json(self, file_path: Path) -> bool:
        """Compress a large JSON file using gzip."""
        if not file_path.suffix == '.json':
            return False

        compressed_path = file_path.with_suffix('.json.gz')

        if compressed_path.exists():
            return False  # Already compressed

        try:
            if not self.dry_run:
                with open(file_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)

                # Verify compression worked
                if compressed_path.exists() and compressed_path.stat().st_size < file_path.stat().st_size:
                    file_path.unlink()  # Remove original
                    self.stats['space_freed_mb'] += (file_path.stat().st_size - compressed_path.stat().st_size) / (1024 * 1024)
                    self.stats['files_compressed'] += 1
                    return True
                else:
                    compressed_path.unlink()  # Remove failed compression
                    return False
            else:
                self.stats['files_compressed'] += 1
                return True
        except Exception as e:
            print(f"Error compressing {file_path}: {e}")
            return False

    def delete_old_backups(self, days: int = BACKUP_RETENTION_DAYS) -> int:
        """Delete backup files older than specified days."""
        deleted = 0
        cutoff_date = datetime.now() - timedelta(days=days)

        # Find backup files
        backup_patterns = [
            "**/*backup*.json",
            "**/execution_*.json",
            "**/comprehensive_syphon_*.json",
            "**/filesystem_syphon_*.json"
        ]

        for pattern in backup_patterns:
            for file_path in DATA_DIR.glob(pattern):
                if file_path.is_file():
                    try:
                        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if mtime < cutoff_date:
                            if not self.dry_run:
                                size_mb = file_path.stat().st_size / (1024 * 1024)
                                file_path.unlink()
                                self.stats['space_freed_mb'] += size_mb
                                deleted += 1
                            else:
                                deleted += 1
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")

        return deleted

    def remove_nested_backups(self) -> int:
        """Remove deeply nested backup directories."""
        nested = self.find_nested_backups()
        removed = 0

        for backup_dir in nested:
            try:
                if not self.dry_run:
                    size_mb = sum(f.stat().st_size for f in backup_dir.rglob('*') if f.is_file()) / (1024 * 1024)
                    shutil.rmtree(backup_dir)
                    self.stats['space_freed_mb'] += size_mb
                    removed += 1
                else:
                    removed += 1
            except Exception as e:
                print(f"Error removing {backup_dir}: {e}")

        self.stats['nested_backups_removed'] = removed
        return removed

    def generate_report(self) -> Dict:
        """Generate a report of all monster files."""
        monsters = self.find_monster_files()
        self.stats['files_found'] = len(monsters)

        report = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats,
            'monster_files': [
                {
                    'path': str(f.relative_to(PROJECT_ROOT)),
                    'size_mb': round(size_mb, 2),
                    'size_gb': round(size_mb / 1024, 2)
                }
                for f, size_mb in monsters[:50]  # Top 50
            ],
            'nested_backups': len(self.find_nested_backups())
        }

        return report

    def slay_all_monsters(self, compress: bool = True, delete_old: bool = True,
                         remove_nested: bool = True) -> Dict:
        """Execute the full monster slaying operation."""
        print("🔥 BY FIRE BE PURGED! 🔥")
        print("=" * 60)
        print(f"Mode: {'DRY RUN' if self.dry_run else 'EXECUTION'}")
        print("=" * 60)

        # Find monsters
        monsters = self.find_monster_files()
        print(f"\n📊 Found {len(monsters)} monster files (>100MB)")

        if monsters:
            print("\n🏆 Top 10 Monster Files:")
            for i, (file_path, size_mb) in enumerate(monsters[:10], 1):
                rel_path = file_path.relative_to(PROJECT_ROOT)
                print(f"  {i}. {rel_path} ({size_mb:.2f} MB / {size_mb/1024:.2f} GB)")

        # Convert to Holocrons or compress large JSON files
        if self.convert_to_holocron:
            print(f"\n📦 Converting large JSON files to Holocrons (>50MB)...")
            for file_path, size_mb in monsters:
                if size_mb > COMPRESSION_THRESHOLD_MB and file_path.suffix == '.json':
                    if not self.dry_run:
                        holocron_path = self.holocron_converter.convert_json_to_holocron(file_path)
                        if holocron_path:
                            self.stats['files_converted_to_holocron'] += 1
                            # Optionally remove original after successful conversion
                            # file_path.unlink()
                    else:
                        self.stats['files_converted_to_holocron'] += 1
                        print(f"  [DRY RUN] Would convert: {file_path.name}")
        elif compress:
            print(f"\n🗜️  Compressing large JSON files (>50MB)...")
            for file_path, size_mb in monsters:
                if size_mb > COMPRESSION_THRESHOLD_MB:
                    if self.compress_large_json(file_path):
                        print(f"  ✓ Compressed: {file_path.name}")

        # Delete old backups
        if delete_old:
            print(f"\n🗑️  Deleting backups older than {BACKUP_RETENTION_DAYS} days...")
            deleted = self.delete_old_backups()
            print(f"  ✓ Would delete {deleted} old backup files")

        # Remove nested backups
        if remove_nested:
            print(f"\n🧹 Removing nested backup directories...")
            nested = self.find_nested_backups()
            print(f"  Found {len(nested)} deeply nested backup directories")
            removed = self.remove_nested_backups()
            print(f"  ✓ Would remove {removed} nested backup directories")

        # Final report
        print("\n" + "=" * 60)
        print("📈 FINAL STATISTICS:")
        print("=" * 60)
        print(f"  Files found: {self.stats['files_found']}")
        if self.convert_to_holocron:
            print(f"  Files converted to Holocrons: {self.stats['files_converted_to_holocron']}")
        else:
            print(f"  Files compressed: {self.stats['files_compressed']}")
        print(f"  Files deleted: {self.stats['files_deleted']}")
        print(f"  Nested backups removed: {self.stats['nested_backups_removed']}")
        print(f"  Space freed: {self.stats['space_freed_mb']:.2f} MB / {self.stats['space_freed_mb']/1024:.2f} GB")
        print("=" * 60)

        return self.generate_report()


def main():
    try:
        parser = argparse.ArgumentParser(
            description="Slay monster files that are causing performance issues"
        )
        parser.add_argument(
            '--execute',
            action='store_true',
            help='Actually perform the cleanup (default is dry-run)'
        )
        parser.add_argument(
            '--report-only',
            action='store_true',
            help='Only generate a report, no cleanup'
        )
        parser.add_argument(
            '--no-compress',
            action='store_true',
            help='Skip compression step'
        )
        parser.add_argument(
            '--no-delete',
            action='store_true',
            help='Skip deletion of old backups'
        )
        parser.add_argument(
            '--no-nested',
            action='store_true',
            help='Skip removal of nested backups'
        )
        parser.add_argument(
            '--to-holocron',
            action='store_true',
            help='Convert large JSON files to Holocrons instead of compressing'
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Save report to JSON file'
        )

        args = parser.parse_args()

        slayer = MonsterFileSlayer(
            dry_run=not args.execute,
            convert_to_holocron=args.to_holocron
        )

        if args.report_only:
            report = slayer.generate_report()
            print(json.dumps(report, indent=2))
        else:
            report = slayer.slay_all_monsters(
                compress=not args.no_compress,
                delete_old=not args.no_delete,
                remove_nested=not args.no_nested
            )

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n📄 Report saved to: {args.output}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()