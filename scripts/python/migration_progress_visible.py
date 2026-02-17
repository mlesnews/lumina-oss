#!/usr/bin/env python3
"""
Migration Progress - VISIBLE to Operator

Shows the progress bar in the FOREGROUND so the operator can actually see it.
This is the command to run to see the progress bar while migration runs.

Tags: #PROGRESS #VISIBLE #OPERATOR @LUMINA
"""

import sys
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from disk_migration_progress_display import MigrationProgressDisplay

if __name__ == "__main__":
    import signal
    import sys

    def signal_handler(sig, frame):
        print("\n\n👋 Progress display stopped (Ctrl+C).")
        print("💡 Migration continues in background if it was running.")
        print("   Use 'check_migration_activity.py' to see current status.")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    print("\n" + "=" * 80)
    print("📊 MIGRATION PROGRESS BAR - VISIBLE TO OPERATOR")
    print("=" * 80)
    print()
    print("This window shows the LIVE progress bar.")
    print("Updates every 5 seconds automatically.")
    print()
    print("Press Ctrl+C to exit cleanly.")
    print("=" * 80)
    print()

    try:
        # Show live progress - THIS IS VISIBLE TO OPERATOR
        display = MigrationProgressDisplay(project_root)
        display.display_live_progress(update_interval=5)
    except KeyboardInterrupt:
        print("\n\n👋 Progress display stopped.")
        sys.exit(0)
