#!/usr/bin/env python3
"""
Quick Command to Show Migration Progress

Simple command to display the visual progress bar for disk migration.

Usage:
    python show_migration_progress.py           # Show current progress
    python show_migration_progress.py --live     # Live updating progress

Tags: #PROGRESS #QUICK-COMMAND @LUMINA
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from disk_migration_progress_display import MigrationProgressDisplay
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Show Migration Progress")
    parser.add_argument("--live", action="store_true", help="Show live updating progress")
    parser.add_argument("--interval", type=int, default=5, help="Update interval in seconds")

    args = parser.parse_args()

    display = MigrationProgressDisplay()

    if args.live:
        display.display_live_progress(update_interval=args.interval)
    else:
        display.display_progress_bar()
