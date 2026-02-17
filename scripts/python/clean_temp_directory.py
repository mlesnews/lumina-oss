#!/usr/bin/env python3
"""
Clean Temp Directory
Safely cleans temporary files from AppData/Local/Temp to free up space.

Tags: #CLEANUP #DISK_SPACE #TEMP
"""

import sys
import shutil
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timedelta

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CleanTempDirectory")


def get_directory_size(path: Path) -> int:
    """Get total size of directory in bytes"""
    total = 0
    try:
        for item in path.rglob('*'):
            if item.is_file():
                try:
                    total += item.stat().st_size
                except (OSError, PermissionError):
                    pass
    except (OSError, PermissionError):
        pass
    return total


def format_size(bytes_size: int) -> str:
    """Format bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"


def clean_temp_directory(temp_path: Path, dry_run: bool = False, days_old: int = 7) -> Dict[str, Any]:
    """Clean temporary directory"""
    logger.info("=" * 80)
    logger.info("🧹 CLEANING TEMP DIRECTORY")
    logger.info("=" * 80)
    logger.info(f"Path: {temp_path}")
    logger.info(f"Dry Run: {dry_run}")
    logger.info(f"Delete files older than: {days_old} days")
    logger.info("")

    if not temp_path.exists():
        logger.error(f"❌ Temp directory does not exist: {temp_path}")
        return {"error": "Directory does not exist"}

    # Calculate initial size
    initial_size = get_directory_size(temp_path)
    logger.info(f"📊 Initial size: {format_size(initial_size)}")
    logger.info("")

    if dry_run:
        logger.info("🔍 DRY RUN MODE - No files will be deleted")
        logger.info("")

    cutoff_date = datetime.now() - timedelta(days=days_old)
    deleted_count = 0
    deleted_size = 0
    errors = []

    try:
        for item in temp_path.iterdir():
            try:
                if item.is_file():
                    # Check file age
                    file_age = datetime.fromtimestamp(item.stat().st_mtime)
                    if file_age < cutoff_date:
                        file_size = item.stat().st_size
                        if dry_run:
                            logger.info(f"   [DRY RUN] Would delete: {item.name} ({format_size(file_size)})")
                        else:
                            item.unlink()
                            deleted_count += 1
                            deleted_size += file_size
                            logger.debug(f"   ✅ Deleted: {item.name}")

                elif item.is_dir():
                    # Check directory age (use oldest file or dir mtime)
                    try:
                        dir_age = datetime.fromtimestamp(item.stat().st_mtime)
                        if dir_age < cutoff_date:
                            dir_size = get_directory_size(item)
                            if dry_run:
                                logger.info(f"   [DRY RUN] Would delete directory: {item.name} ({format_size(dir_size)})")
                            else:
                                shutil.rmtree(item)
                                deleted_count += 1
                                deleted_size += dir_size
                                logger.info(f"   ✅ Deleted directory: {item.name} ({format_size(dir_size)})")
                    except Exception as e:
                        errors.append(f"Error deleting {item.name}: {e}")
                        logger.warning(f"   ⚠️  Could not delete {item.name}: {e}")

            except (PermissionError, OSError) as e:
                errors.append(f"Error accessing {item.name}: {e}")
                logger.debug(f"   ⚠️  Skipping {item.name}: {e}")
                continue

    except Exception as e:
        logger.error(f"❌ Error during cleanup: {e}", exc_info=True)
        errors.append(str(e))

    # Calculate final size
    final_size = get_directory_size(temp_path)
    space_freed = initial_size - final_size

    result = {
        "timestamp": datetime.now().isoformat(),
        "dry_run": dry_run,
        "temp_path": str(temp_path),
        "initial_size_bytes": initial_size,
        "initial_size_gb": round(initial_size / (1024 ** 3), 2),
        "final_size_bytes": final_size,
        "final_size_gb": round(final_size / (1024 ** 3), 2),
        "space_freed_bytes": space_freed,
        "space_freed_gb": round(space_freed / (1024 ** 3), 2),
        "deleted_count": deleted_count,
        "errors": errors
    }

    logger.info("")
    logger.info("=" * 80)
    logger.info("📊 CLEANUP SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Initial size: {format_size(initial_size)}")
    logger.info(f"Final size: {format_size(final_size)}")
    logger.info(f"Space freed: {format_size(space_freed)} ({result['space_freed_gb']:.2f} GB)")
    logger.info(f"Items deleted: {deleted_count}")
    if errors:
        logger.warning(f"Errors: {len(errors)}")
    logger.info("=" * 80)

    return result


def main():
    try:
        """Main function"""
        import argparse

        parser = argparse.ArgumentParser(description="Clean Temp Directory")
        parser.add_argument("--dry-run", action="store_true", help="Dry run (don't delete)")
        parser.add_argument("--days", type=int, default=7, help="Delete files older than N days (default: 7)")
        parser.add_argument("--path", type=str, help="Temp directory path (default: AppData/Local/Temp)")

        args = parser.parse_args()

        if args.path:
            temp_path = Path(args.path)
        else:
            temp_path = Path.home() / "AppData" / "Local" / "Temp"

        result = clean_temp_directory(temp_path, dry_run=args.dry_run, days_old=args.days)

        # Save results
        results_file = project_root / "data" / "system" / f"temp_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)

        import json
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        logger.info(f"💾 Results saved to: {results_file}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()