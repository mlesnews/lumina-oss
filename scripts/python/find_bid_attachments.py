"""
Find HVAC Bid Attachments
Helps locate bid attachment files from contractors.

#JARVIS #LUMINA
"""

import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional
import logging
logger = logging.getLogger("find_bid_attachments")



def find_recent_files(directories: List[Path], 
                     extensions: List[str],
                     days: int = 7,
                     max_results: int = 20) -> List[Path]:
    """
    Find recent files with specified extensions in given directories.

    Args:
        directories: List of directories to search
        extensions: List of file extensions to look for (e.g., ['.pdf', '.docx'])
        days: Number of recent days to search
        max_results: Maximum number of results to return

    Returns:
        List of file paths, sorted by modification time (newest first)
    """
    found_files = []
    cutoff_time = datetime.now() - timedelta(days=days)

    for directory in directories:
        if not directory.exists():
            continue

        for ext in extensions:
            pattern = f"*{ext}"
            for file_path in directory.glob(pattern):
                try:
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime >= cutoff_time:
                        found_files.append((mtime, file_path))
                except (OSError, PermissionError):
                    continue

    # Sort by modification time (newest first)
    found_files.sort(key=lambda x: x[0], reverse=True)

    return [file_path for _, file_path in found_files[:max_results]]


def search_common_locations() -> List[Path]:
    try:
        """
        Search common locations for bid attachments.

        Returns:
            List of potential bid files
        """
        # Common file extensions for bids
        extensions = ['.pdf', '.docx', '.doc', '.txt']

        # Common locations
        search_dirs = []

        # User directories
        user_home = Path.home()
        search_dirs.extend([
            user_home / "Downloads",
            user_home / "Desktop",
            user_home / "Documents",
            user_home / "Dropbox" / "Downloads",
            user_home / "Dropbox" / "Desktop",
        ])

        # Email attachment locations (common)
        if os.name == 'nt':  # Windows
            search_dirs.extend([
                Path(os.environ.get('APPDATA', '')) / "Microsoft" / "Outlook",
                Path(os.environ.get('LOCALAPPDATA', '')) / "Microsoft" / "Outlook",
            ])

        # Filter to existing directories
        search_dirs = [d for d in search_dirs if d.exists()]

        print(f"Searching {len(search_dirs)} directories for recent bid files...")
        print(f"Looking for: {', '.join(extensions)}")
        print(f"Last 7 days...\n")

        return find_recent_files(search_dirs, extensions, days=7, max_results=30)


    except Exception as e:
        logger.error(f"Error in search_common_locations: {e}", exc_info=True)
        raise
def main():
    """Main function."""
    print("="*80)
    print("HVAC BID ATTACHMENT FINDER")
    print("="*80)
    print()

    # Search for files
    files = search_common_locations()

    if not files:
        print("No recent bid files found in common locations.")
        print("\nYou can manually specify file paths when running the extractor:")
        print("  python scripts/python/hvac_bid_extractor.py <file1> <file2> <file3>")
        return

    print(f"Found {len(files)} potential bid file(s):\n")

    for i, file_path in enumerate(files, 1):
        try:
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            size_kb = file_path.stat().st_size / 1024
            print(f"{i}. {file_path.name}")
            print(f"   Path: {file_path}")
            print(f"   Modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Size: {size_kb:.1f} KB")
            print()
        except (OSError, PermissionError):
            continue

    print("="*80)
    print("\nTo extract bids from these files, run:")
    print("\n  python scripts/python/hvac_bid_extractor.py \\")
    for i, file_path in enumerate(files[:3], 1):
        print(f"    \"{file_path}\"", end="")
        if i < min(3, len(files)):
            print(" \\")
        else:
            print()

    if len(files) > 3:
        print(f"\n  (Showing first 3 of {len(files)} files)")

    print("\nOr specify contractor names:")
    print("\n  python scripts/python/hvac_bid_extractor.py \\")
    print("    --contractor-names \"Contractor 1\" \"Contractor 2\" \"Contractor 3\" \\")
    for i, file_path in enumerate(files[:3], 1):
        print(f"    \"{file_path}\"", end="")
        if i < min(3, len(files)):
            print(" \\")
        else:
            print()

    print("\nTo auto-import after extraction:")
    print("  python scripts/python/hvac_bid_extractor.py --auto-import <files...>")


if __name__ == "__main__":


    main()