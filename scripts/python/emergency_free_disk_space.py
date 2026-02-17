#!/usr/bin/env python3
"""
EMERGENCY: Free Disk Space Immediately
Deletes local files that have been successfully migrated to NAS

CRITICAL: Only deletes files that are verified to exist on NAS
"""

import sys
import os
import shutil
from pathlib import Path
from datetime import datetime
import logging
logger = logging.getLogger("emergency_free_disk_space")


script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

nas_base = Path("\\\\<NAS_PRIMARY_IP>\\backups\\LOCAL-CLOUD-STORAGE")

def get_file_list(path: Path):
    """Get list of all files with relative paths"""
    files = {}
    if not path.exists():
        return files

    try:
        for file_path in path.rglob("*"):
            if file_path.is_file():
                try:
                    rel_path = file_path.relative_to(path)
                    files[str(rel_path)] = file_path.stat().st_size
                except:
                    pass
    except:
        pass

    return files

def delete_verified_files(local_path: Path, nas_path: Path, dry_run: bool = False):
    """Delete local files that exist on NAS"""
    print(f"\nProcessing: {local_path.name}")
    print(f"  Local: {local_path}")
    print(f"  NAS: {nas_path}")

    if not nas_path.exists():
        print(f"  ⚠️  NAS path doesn't exist - skipping")
        return 0

    # Get file lists
    print("  📋 Scanning files...")
    local_files = get_file_list(local_path)
    nas_files = get_file_list(nas_path)

    print(f"  Local files: {len(local_files)}")
    print(f"  NAS files: {len(nas_files)}")

    # Find files that exist in both
    verified_files = []
    total_size = 0

    for rel_path, size in local_files.items():
        if rel_path in nas_files:
            # Verify sizes match (allow 1% difference)
            nas_size = nas_files[rel_path]
            if abs(size - nas_size) / max(size, 1) < 0.01:
                verified_files.append((rel_path, size))
                total_size += size

    print(f"  ✅ Verified files on NAS: {len(verified_files)} ({total_size / (1024**3):.2f} GB)")

    if dry_run:
        print(f"  [DRY RUN] Would delete {len(verified_files)} files")
        return total_size

    # Delete verified files
    deleted_count = 0
    deleted_size = 0

    for rel_path, size in verified_files[:1000]:  # Limit to 1000 files at a time
        local_file = local_path / rel_path
        try:
            if local_file.exists():
                local_file.unlink()
                deleted_count += 1
                deleted_size += size
                if deleted_count % 100 == 0:
                    print(f"  Deleted {deleted_count} files ({deleted_size / (1024**3):.2f} GB)...")
        except Exception as e:
            pass

    print(f"  ✅ Deleted {deleted_count} files ({deleted_size / (1024**3):.2f} GB)")
    return deleted_size

def main():
    try:
        import argparse

        parser = argparse.ArgumentParser(description="Emergency: Free disk space")
        parser.add_argument("--execute", action="store_true", help="Actually delete files")
        parser.add_argument("--limit", type=int, default=1000, help="Max files to delete per run")

        args = parser.parse_args()

        if not args.execute:
            print("⚠️  DRY RUN MODE")
            print("   Use --execute to actually delete files")
            return

        print("=" * 80)
        print("EMERGENCY: FREEING DISK SPACE")
        print("=" * 80)
        print("Deleting local files verified to exist on NAS")
        print("")

        # Process OneDrive first (smaller, faster)
        onedrive_local = Path("C:\\Users\\mlesn\\OneDrive")
        onedrive_nas = nas_base / "OneDrive"

        if onedrive_local.exists() and onedrive_nas.exists():
            deleted = delete_verified_files(onedrive_local, onedrive_nas, args.execute)
            print(f"  Freed: {deleted / (1024**3):.2f} GB")

        print("\n" + "=" * 80)
        print("⚠️  For Dropbox (4.6 TB), use robocopy /MOVE after verification")
        print("   This script handles smaller batches safely")
        print("=" * 80)

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()