#!/usr/bin/env python3
"""Clean up completed migration processes from status tracking"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts" / "python"))

from jarvis_progress_tracker import get_progress_tracker

print("=" * 80)
print("CLEANUP: Migration Process Status")
print("=" * 80)
print()

# Get tracker
tracker = get_progress_tracker(project_root)

# Migration process IDs that should be completed
migration_processes = [
    "ollama_nas_move_v3",
    "ollama_nas_move",
    "nas_migration_move"
]

print("🔍 Checking migration processes...")
print()

for pid in migration_processes:
    if pid in tracker.processes:
        proc = tracker.processes[pid]
        print(f"   Found: {pid} ({proc.process_name})")
        print(f"      Status: {proc.status}")
        print(f"      Progress: {proc.progress_percentage:.1f}% ({proc.completed_items}/{proc.total_items})")

        # Mark as completed if still running
        if proc.status == "running":
            print(f"      → Marking as completed (migration is done)")
            tracker.complete_process(pid)
        else:
            print(f"      → Already {proc.status}")
        print()
    else:
        print(f"   Not found: {pid}")
        print()

# Update status
tracker._update_cursor_status()

print("✅ Cleanup complete")
print("   Status bar should now reflect current state")
