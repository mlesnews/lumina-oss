#!/usr/bin/env python3
"""
Cleanup Recursive Snapshots

Removes recursive snapshots that contain nested snapshot directories.
This frees up ~1.24 TB of Dropbox space.

CRITICAL: This script identifies and removes ONLY recursive snapshots
(those containing data/time_travel/snapshots within them).
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CleanupRecursiveSnapshots")


def get_dir_size(path: Path) -> int:
    """Get total size of directory in bytes"""
    total = 0
    try:
        for entry in path.rglob('*'):
            try:
                if entry.is_file():
                    total += entry.stat().st_size
            except (OSError, PermissionError):
                continue
    except (OSError, PermissionError):
        pass
    return total


def format_size(size_bytes: int) -> str:
    """Format bytes to human-readable size"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def is_recursive_snapshot(snapshot_path: Path) -> Tuple[bool, int]:
    """
    Check if snapshot contains nested snapshot directories (recursive)

    Returns: (is_recursive, nesting_depth)
    """
    nested_snapshots_path = snapshot_path / "data" / "time_travel" / "snapshots"

    if not nested_snapshots_path.exists():
        return False, 0

    # Count nesting depth by counting how many times 'snapshots' appears
    # in nested paths
    max_depth = 0
    try:
        for nested_path in nested_snapshots_path.rglob("snapshots"):
            # Count how many 'snapshots' directories are in this path
            depth = str(nested_path).count("snapshots")
            max_depth = max(max_depth, depth)
    except (OSError, PermissionError):
        pass

    # If there's a nested snapshots directory, it's recursive
    return max_depth > 1, max_depth


def find_recursive_snapshots(snapshots_dir: Path) -> List[Dict[str, Any]]:
    """Find all recursive snapshots"""
    recursive_snapshots = []

    if not snapshots_dir.exists():
        logger.warning(f"Snapshots directory not found: {snapshots_dir}")
        return recursive_snapshots

    logger.info(f"Scanning snapshots directory: {snapshots_dir}")

    for snapshot_dir in snapshots_dir.iterdir():
        if not snapshot_dir.is_dir():
            continue

        try:
            is_recursive, depth = is_recursive_snapshot(snapshot_dir)
            if is_recursive:
                size = get_dir_size(snapshot_dir)
                recursive_snapshots.append({
                    "path": str(snapshot_dir),
                    "name": snapshot_dir.name,
                    "size_bytes": size,
                    "size_formatted": format_size(size),
                    "nesting_depth": depth
                })
                logger.info(f"  Found recursive snapshot: {snapshot_dir.name} ({format_size(size)}, depth={depth})")
        except Exception as e:
            logger.error(f"Error checking snapshot {snapshot_dir.name}: {e}")

    return recursive_snapshots


def cleanup_recursive_snapshots(
    snapshots_dir: Path,
    dry_run: bool = True,
    confirm: bool = False
) -> Dict[str, Any]:
    """
    Clean up recursive snapshots

    Args:
        snapshots_dir: Path to snapshots directory
        dry_run: If True, only report what would be deleted
        confirm: If True, proceed with deletion (overrides dry_run)

    Returns:
        Report dictionary with cleanup results
    """
    report = {
        "timestamp": datetime.now().isoformat(),
        "dry_run": dry_run and not confirm,
        "snapshots_dir": str(snapshots_dir),
        "recursive_snapshots_found": [],
        "total_size_bytes": 0,
        "total_size_formatted": "0 B",
        "deleted_count": 0,
        "deleted_size_bytes": 0,
        "deleted_size_formatted": "0 B",
        "errors": []
    }

    # Find recursive snapshots
    recursive_snapshots = find_recursive_snapshots(snapshots_dir)
    report["recursive_snapshots_found"] = recursive_snapshots

    if not recursive_snapshots:
        logger.info("No recursive snapshots found")
        return report

    # Calculate total size
    total_size = sum(s["size_bytes"] for s in recursive_snapshots)
    report["total_size_bytes"] = total_size
    report["total_size_formatted"] = format_size(total_size)

    logger.info("=" * 70)
    logger.info(f"RECURSIVE SNAPSHOTS CLEANUP {'(DRY RUN)' if report['dry_run'] else ''}")
    logger.info("=" * 70)
    logger.info(f"Found {len(recursive_snapshots)} recursive snapshots")
    logger.info(f"Total size: {report['total_size_formatted']}")
    logger.info("")

    # Delete recursive snapshots
    if report['dry_run']:
        logger.info("DRY RUN MODE - No files will be deleted")
        logger.info("")
        for snapshot in recursive_snapshots:
            logger.info(f"  Would delete: {snapshot['name']}")
            logger.info(f"    Size: {snapshot['size_formatted']}")
            logger.info(f"    Depth: {snapshot['nesting_depth']}")
            logger.info("")
    else:
        logger.info("DELETING recursive snapshots...")
        logger.info("")

        for snapshot in recursive_snapshots:
            snapshot_path = Path(snapshot["path"])
            try:
                logger.info(f"  Deleting: {snapshot['name']} ({snapshot['size_formatted']})")
                shutil.rmtree(snapshot_path)
                report["deleted_count"] += 1
                report["deleted_size_bytes"] += snapshot["size_bytes"]
                logger.info(f"    ✓ Deleted successfully")
            except Exception as e:
                error_msg = f"Failed to delete {snapshot['name']}: {e}"
                logger.error(f"    ✗ {error_msg}")
                report["errors"].append(error_msg)

    report["deleted_size_formatted"] = format_size(report["deleted_size_bytes"])

    return report


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(
            description="Cleanup recursive snapshots (frees ~1.24 TB of space)"
        )
        parser.add_argument(
            "--snapshots-dir",
            type=str,
            default=str(project_root / "data" / "time_travel" / "snapshots"),
            help="Path to snapshots directory"
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=True,
            help="Dry run mode (default: True, use --confirm to actually delete)"
        )
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Confirm deletion (overrides --dry-run)"
        )
        parser.add_argument(
            "--report",
            type=str,
            help="Save report to JSON file"
        )

        args = parser.parse_args()

        snapshots_dir = Path(args.snapshots_dir)

        logger.info("=" * 70)
        logger.info("RECURSIVE SNAPSHOTS CLEANUP")
        logger.info("=" * 70)
        logger.info(f"Snapshots directory: {snapshots_dir}")
        logger.info(f"Mode: {'DRY RUN' if (args.dry_run and not args.confirm) else 'DELETE'}")
        logger.info("")

        # Run cleanup
        report = cleanup_recursive_snapshots(
            snapshots_dir,
            dry_run=args.dry_run and not args.confirm,
            confirm=args.confirm
        )

        # Save report
        if args.report:
            report_path = Path(args.report)
            report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Report saved to: {report_path}")

        # Summary
        logger.info("")
        logger.info("=" * 70)
        logger.info("SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Recursive snapshots found: {len(report['recursive_snapshots_found'])}")
        logger.info(f"Total size: {report['total_size_formatted']}")

        if not report['dry_run']:
            logger.info(f"Deleted: {report['deleted_count']} snapshots")
            logger.info(f"Freed: {report['deleted_size_formatted']}")
            if report['errors']:
                logger.warning(f"Errors: {len(report['errors'])}")

        logger.info("=" * 70)

        return 0 if report['errors'] == [] else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    sys.exit(main())