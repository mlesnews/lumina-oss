#!/usr/bin/env python3
"""
Start Migration with Visible Progress Bar

Starts the migration AND shows the progress bar in the FOREGROUND
so the operator can actually see it.

Tags: #PROGRESS #VISIBLE #OPERATOR-VIEW @LUMINA
"""

import sys
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from background_disk_space_migration import BackgroundDiskSpaceMigration
from disk_migration_progress_display import MigrationProgressDisplay

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🚀 STARTING MIGRATION WITH VISIBLE PROGRESS BAR")
    print("=" * 80)
    print()
    print("The progress bar will be visible in this window.")
    print("Migration runs in background, progress updates every 5 seconds.")
    print()
    print("Press Ctrl+C to stop.")
    print("=" * 80)
    print()

    # Start migration
    manager = BackgroundDiskSpaceMigration(project_root)
    manager.start(show_progress=True, foreground_progress=True)

    # Keep this process alive and show progress
    try:
        progress_display = MigrationProgressDisplay(project_root)
        progress_display.display_live_progress(update_interval=5)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping migration...")
        manager.stop()
        print("✅ Migration stopped")
