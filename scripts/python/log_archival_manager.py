#!/usr/bin/env python3
"""
Log Archival Manager for Homelab

Manages log archival and retention policies:
- Local logs: Normal administration, maintenance, standard rotation (e.g., 30 days)
- NAS archive: Long-term mirror/aggregate copy (6 months to 1 year retention)

This script handles:
- Archiving old logs to NAS
- Cleaning up old logs based on retention policies
- Maintaining separate retention policies for local vs NAS

Tags: #LOGGING #ARCHIVAL #RETENTION #HOMELAB
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from lumina_unified_logger import LuminaUnifiedLogger

logger_module = LuminaUnifiedLogger("System", "LogArchival")
logger = logger_module.get_logger()


class LogArchivalManager:
    """Manage log archival and retention policies"""

    def __init__(
        self,
        local_log_root: Path = None,
        nas_log_root: Path = None,
        local_retention_days: int = 30,
        nas_retention_days: int = 365  # 1 year default
    ):
        """
        Initialize log archival manager.

        Args:
            local_log_root: Local log directory (default: project_root/logs)
            nas_log_root: NAS log directory (default: L:/Logs)
            local_retention_days: Days to keep local logs (default: 30)
            nas_retention_days: Days to keep NAS logs (default: 365)
        """
        self.local_log_root = local_log_root or (project_root / "logs")
        self.nas_log_root = nas_log_root or Path("L:/Logs")
        self.local_retention_days = local_retention_days
        self.nas_retention_days = nas_retention_days

        # Calculate cutoff dates
        self.local_cutoff = datetime.now() - timedelta(days=local_retention_days)
        self.nas_cutoff = datetime.now() - timedelta(days=nas_retention_days)

    def archive_logs_to_nas(self, dry_run: bool = False) -> Dict[str, int]:
        """
        Archive local logs to NAS (mirror/aggregate copy).
        Only copies logs that don't already exist on NAS or are newer.

        Returns:
            Dictionary with archive statistics
        """
        stats = {
            "archived": 0,
            "skipped": 0,
            "errors": 0,
            "bytes_copied": 0
        }

        if not self.local_log_root.exists():
            logger.warning(f"Local log root does not exist: {self.local_log_root}")
            return stats

        if not self.nas_log_root.exists():
            logger.warning(f"NAS log root does not exist: {self.nas_log_root}")
            logger.info("Continuing with local-only operations...")
            return stats

        logger.info(f"Archiving logs from {self.local_log_root} to {self.nas_log_root}")

        # Find all log files in local directory
        for log_file in self.local_log_root.rglob("*.log"):
            try:
                # Calculate relative path from local root
                rel_path = log_file.relative_to(self.local_log_root)
                nas_file = self.nas_log_root / rel_path

                # Create NAS directory if needed
                nas_file.parent.mkdir(parents=True, exist_ok=True)

                # Check if we should copy
                should_copy = False
                if not nas_file.exists():
                    should_copy = True
                    reason = "does not exist on NAS"
                elif log_file.stat().st_mtime > nas_file.stat().st_mtime:
                    should_copy = True
                    reason = "local file is newer"

                if should_copy:
                    if dry_run:
                        logger.info(f"[DRY RUN] Would archive: {rel_path} ({reason})")
                    else:
                        shutil.copy2(log_file, nas_file)
                        stats["archived"] += 1
                        stats["bytes_copied"] += log_file.stat().st_size
                        logger.debug(f"Archived: {rel_path}")
                else:
                    stats["skipped"] += 1

            except Exception as e:
                stats["errors"] += 1
                logger.error(f"Error archiving {log_file}: {e}")

        if not dry_run:
            logger.info(
                f"Archive complete: {stats['archived']} files, "
                f"{stats['skipped']} skipped, {stats['errors']} errors, "
                f"{stats['bytes_copied'] / 1024 / 1024:.2f} MB copied"
            )

        return stats

    def cleanup_local_logs(self, dry_run: bool = False) -> Dict[str, int]:
        """
        Clean up old local logs based on retention policy.
        Normal administration/maintenance - keeps logs for local_retention_days.

        Returns:
            Dictionary with cleanup statistics
        """
        stats = {
            "deleted": 0,
            "kept": 0,
            "errors": 0,
            "bytes_freed": 0
        }

        if not self.local_log_root.exists():
            return stats

        logger.info(f"Cleaning up local logs older than {self.local_retention_days} days")
        logger.info(f"Cutoff date: {self.local_cutoff.strftime('%Y-%m-%d')}")

        for log_file in self.local_log_root.rglob("*.log"):
            try:
                # Get file modification time
                file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                file_size = log_file.stat().st_size

                if file_mtime < self.local_cutoff:
                    if dry_run:
                        logger.info(f"[DRY RUN] Would delete: {log_file} (age: {(datetime.now() - file_mtime).days} days)")
                    else:
                        log_file.unlink()
                        stats["deleted"] += 1
                        stats["bytes_freed"] += file_size
                        logger.debug(f"Deleted: {log_file}")
                else:
                    stats["kept"] += 1

            except Exception as e:
                stats["errors"] += 1
                logger.error(f"Error processing {log_file}: {e}")

        if not dry_run:
            logger.info(
                f"Local cleanup complete: {stats['deleted']} deleted, "
                f"{stats['kept']} kept, {stats['errors']} errors, "
                f"{stats['bytes_freed'] / 1024 / 1024:.2f} MB freed"
            )

        return stats

    def cleanup_nas_logs(self, dry_run: bool = False) -> Dict[str, int]:
        """
        Clean up old NAS logs based on retention policy.
        Long-term archival - keeps logs for nas_retention_days (6 months to 1 year).

        Returns:
            Dictionary with cleanup statistics
        """
        stats = {
            "deleted": 0,
            "kept": 0,
            "errors": 0,
            "bytes_freed": 0
        }

        if not self.nas_log_root.exists():
            logger.warning(f"NAS log root does not exist: {self.nas_log_root}")
            return stats

        logger.info(f"Cleaning up NAS logs older than {self.nas_retention_days} days")
        logger.info(f"Cutoff date: {self.nas_cutoff.strftime('%Y-%m-%d')}")

        for log_file in self.nas_log_root.rglob("*.log"):
            try:
                # Get file modification time
                file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                file_size = log_file.stat().st_size

                if file_mtime < self.nas_cutoff:
                    if dry_run:
                        logger.info(f"[DRY RUN] Would delete: {log_file} (age: {(datetime.now() - file_mtime).days} days)")
                    else:
                        log_file.unlink()
                        stats["deleted"] += 1
                        stats["bytes_freed"] += file_size
                        logger.debug(f"Deleted: {log_file}")
                else:
                    stats["kept"] += 1

            except Exception as e:
                stats["errors"] += 1
                logger.error(f"Error processing {log_file}: {e}")

        if not dry_run:
            logger.info(
                f"NAS cleanup complete: {stats['deleted']} deleted, "
                f"{stats['kept']} kept, {stats['errors']} errors, "
                f"{stats['bytes_freed'] / 1024 / 1024:.2f} MB freed"
            )

        return stats

    def run_full_maintenance(self, dry_run: bool = False) -> Dict[str, Dict[str, int]]:
        """
        Run full maintenance cycle:
        1. Archive local logs to NAS (mirror/aggregate)
        2. Clean up old local logs (normal maintenance)
        3. Clean up old NAS logs (long-term retention)

        Returns:
            Dictionary with all statistics
        """
        logger.info("=" * 70)
        logger.info("LOG ARCHIVAL MAINTENANCE CYCLE")
        logger.info("=" * 70)

        results = {}

        # Step 1: Archive to NAS
        logger.info("")
        logger.info("Step 1: Archiving local logs to NAS (mirror/aggregate)")
        results["archive"] = self.archive_logs_to_nas(dry_run=dry_run)

        # Step 2: Clean up local logs
        logger.info("")
        logger.info("Step 2: Cleaning up old local logs (normal maintenance)")
        results["local_cleanup"] = self.cleanup_local_logs(dry_run=dry_run)

        # Step 3: Clean up NAS logs
        logger.info("")
        logger.info("Step 3: Cleaning up old NAS logs (long-term retention)")
        results["nas_cleanup"] = self.cleanup_nas_logs(dry_run=dry_run)

        # Summary
        logger.info("")
        logger.info("=" * 70)
        logger.info("MAINTENANCE SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Archived to NAS: {results['archive']['archived']} files")
        logger.info(f"Local logs deleted: {results['local_cleanup']['deleted']} files")
        logger.info(f"NAS logs deleted: {results['nas_cleanup']['deleted']} files")
        logger.info("=" * 70)

        return results


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Log archival and retention management")
        parser.add_argument("--local-retention", type=int, default=30, help="Days to keep local logs (default: 30)")
        parser.add_argument("--nas-retention", type=int, default=365, help="Days to keep NAS logs (default: 365)")
        parser.add_argument("--local-path", help="Local log root path")
        parser.add_argument("--nas-path", help="NAS log root path (default: L:/Logs)")
        parser.add_argument("--archive-only", action="store_true", help="Only archive, don't cleanup")
        parser.add_argument("--cleanup-only", action="store_true", help="Only cleanup, don't archive")
        parser.add_argument("--dry-run", action="store_true", help="Show what would be done without doing it")

        args = parser.parse_args()

        manager = LogArchivalManager(
            local_log_root=Path(args.local_path) if args.local_path else None,
            nas_log_root=Path(args.nas_path) if args.nas_path else None,
            local_retention_days=args.local_retention,
            nas_retention_days=args.nas_retention
        )

        if args.archive_only:
            manager.archive_logs_to_nas(dry_run=args.dry_run)
        elif args.cleanup_only:
            manager.cleanup_local_logs(dry_run=args.dry_run)
            manager.cleanup_nas_logs(dry_run=args.dry_run)
        else:
            manager.run_full_maintenance(dry_run=args.dry_run)

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":

    sys.exit(main())