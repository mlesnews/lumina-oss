#!/usr/bin/env python3
"""
Check Dropbox Space Usage

Identifies large directories and files that may be consuming Dropbox space.
"""

import os
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple
import logging
logger = logging.getLogger("check_dropbox_space")


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

def find_large_directories(dropbox_root: Path, min_size_gb: float = 0.1) -> List[Tuple[str, int]]:
    """Find directories larger than min_size_gb"""
    large_dirs = []
    min_size_bytes = int(min_size_gb * 1024 * 1024 * 1024)

    print(f"Scanning {dropbox_root}...")

    for item in dropbox_root.iterdir():
        if item.is_dir():
            try:
                size = get_dir_size(item)
                if size >= min_size_bytes:
                    large_dirs.append((str(item.name), size))
            except (OSError, PermissionError) as e:
                print(f"  ⚠️  Could not scan {item.name}: {e}")

    return sorted(large_dirs, key=lambda x: x[1], reverse=True)

def find_large_files(directory: Path, min_size_mb: float = 100) -> List[Tuple[str, int]]:
    """Find files larger than min_size_mb"""
    large_files = []
    min_size_bytes = int(min_size_mb * 1024 * 1024)

    try:
        for file_path in directory.rglob('*'):
            try:
                if file_path.is_file():
                    size = file_path.stat().st_size
                    if size >= min_size_bytes:
                        large_files.append((str(file_path.relative_to(directory)), size))
            except (OSError, PermissionError):
                continue
    except (OSError, PermissionError):
        pass

    return sorted(large_files, key=lambda x: x[1], reverse=True)

def check_common_space_hogs(directory: Path) -> Dict[str, int]:
    """Check for common space-consuming patterns"""
    hogs = {
        'node_modules': 0,
        '__pycache__': 0,
        '.git': 0,
        '*.log': 0,
        '*.tmp': 0,
        '*.cache': 0,
        'venv': 0,
        'env': 0,
        '.venv': 0,
        'dist': 0,
        'build': 0,
        '.pytest_cache': 0,
        '.mypy_cache': 0,
    }

    for pattern, size in hogs.items():
        if pattern.startswith('*'):
            # File pattern
            ext = pattern[1:]
            try:
                for file_path in directory.rglob(f'*{ext}'):
                    try:
                        if file_path.is_file():
                            hogs[pattern] += file_path.stat().st_size
                    except (OSError, PermissionError):
                        continue
            except (OSError, PermissionError):
                pass
        else:
            # Directory pattern
            try:
                for dir_path in directory.rglob(pattern):
                    try:
                        if dir_path.is_dir():
                            hogs[pattern] += get_dir_size(dir_path)
                    except (OSError, PermissionError):
                        continue
            except (OSError, PermissionError):
                pass

    return hogs

def main():
    try:
        dropbox_root = Path.home() / "Dropbox"

        if not dropbox_root.exists():
            print(f"❌ Dropbox directory not found: {dropbox_root}")
            return

        print("=" * 60)
        print("DROPBOX SPACE ANALYSIS")
        print("=" * 60)
        print(f"Dropbox root: {dropbox_root}")
        print()

        # Check large directories
        print("📁 LARGE DIRECTORIES (>100MB):")
        print("-" * 60)
        large_dirs = find_large_directories(dropbox_root, min_size_gb=0.1)

        if large_dirs:
            total_size = 0
            for name, size in large_dirs[:20]:  # Top 20
                total_size += size
                print(f"  {format_size(size):>12}  {name}")
            print(f"\n  Total (top 20): {format_size(total_size)}")
        else:
            print("  No large directories found")

        print()

        # Check my_projects specifically
        my_projects = dropbox_root / "my_projects"
        if my_projects.exists():
            print("📂 MY_PROJECTS ANALYSIS:")
            print("-" * 60)

            project_dirs = find_large_directories(my_projects, min_size_gb=0.05)
            if project_dirs:
                for name, size in project_dirs:
                    print(f"  {format_size(size):>12}  {name}")
            else:
                print("  No large project directories found")

            print()

            # Check for common space hogs in my_projects
            print("🔍 COMMON SPACE HOGS IN MY_PROJECTS:")
            print("-" * 60)
            hogs = check_common_space_hogs(my_projects)
            total_hogs = 0
            for pattern, size in sorted(hogs.items(), key=lambda x: x[1], reverse=True):
                if size > 0:
                    total_hogs += size
                    print(f"  {format_size(size):>12}  {pattern}")

            if total_hogs > 0:
                print(f"\n  Total space hogs: {format_size(total_hogs)}")
                print(f"  💡 Consider cleaning these up to free space")
            else:
                print("  No significant space hogs found")

            print()

            # Check for large files in my_projects
            print("📄 LARGE FILES IN MY_PROJECTS (>100MB):")
            print("-" * 60)
            large_files = find_large_files(my_projects, min_size_mb=100)
            if large_files:
                for file_path, size in large_files[:10]:  # Top 10
                    print(f"  {format_size(size):>12}  {file_path}")
            else:
                print("  No large files found")

        print()
        print("=" * 60)
        print("✅ Analysis complete")
        print("=" * 60)

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()