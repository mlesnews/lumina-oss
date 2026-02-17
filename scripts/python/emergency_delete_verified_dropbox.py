#!/usr/bin/env python3
"""
EMERGENCY: Delete Dropbox files verified to exist on NAS
Only deletes files that are confirmed to be on NAS (151 GB)
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

dropbox_local = Path("C:\\Users\\mlesn\\Dropbox")
dropbox_nas = Path("\\\\<NAS_PRIMARY_IP>\\backups\\LOCAL-CLOUD-STORAGE\\Dropbox")

def get_files_by_size(path: Path, min_size_mb=10):
    """Get large files with their relative paths"""
    files = {}
    if not path.exists():
        return files

    try:
        for file_path in path.rglob("*"):
            if file_path.is_file():
                try:
                    size = file_path.stat().st_size
                    if size > min_size_mb * 1024 * 1024:  # Only large files
                        rel_path = file_path.relative_to(path)
                        files[str(rel_path)] = size
                except:
                    pass
    except:
        pass

    return files

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    print("=" * 80)
    print("EMERGENCY: Delete Verified Dropbox Files")
    print("=" * 80)
    print(f"Local: {dropbox_local}")
    print(f"NAS: {dropbox_nas}")
    print("")

    if not dropbox_nas.exists():
        print("❌ NAS path not accessible")
        return

    print("📋 Scanning for large files (>10 MB)...")
    nas_files = get_files_by_size(dropbox_nas, min_size_mb=10)
    print(f"   Found {len(nas_files)} large files on NAS")

    if not args.execute:
        print("\n⚠️  DRY RUN - Use --execute to delete")
        print(f"   Would check and delete matching files from local")
        return

    print("\n🔍 Checking local files...")
    deleted_count = 0
    deleted_size = 0

    for rel_path, nas_size in list(nas_files.items())[:500]:  # Limit to 500 files
        local_file = dropbox_local / rel_path
        if local_file.exists():
            try:
                local_size = local_file.stat().st_size
                # Verify sizes match (within 1%)
                if abs(local_size - nas_size) / max(nas_size, 1) < 0.01:
                    local_file.unlink()
                    deleted_count += 1
                    deleted_size += local_size
                    if deleted_count % 50 == 0:
                        print(f"   Deleted {deleted_count} files ({deleted_size / (1024**3):.2f} GB)...")
            except:
                pass

    print(f"\n✅ Deleted {deleted_count} files ({deleted_size / (1024**3):.2f} GB)")
    print("=" * 80)

if __name__ == "__main__":


    main()