#!/usr/bin/env python3
"""Test migration-style status bar: "3m +5143 -117 Auto" """

import sys
import time
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts" / "python"))

from jarvis_progress_tracker import get_progress_tracker

print("=" * 80)
print("🧪 TEST: Migration-Style Status Bar")
print("=" * 80)
print()
print("Format: '3m +5143 -117 Auto'")
print("  - Elapsed time (3m)")
print("  - Success count in green (+5143)")
print("  - Failure count in red (-117)")
print("  - Auto indicator")
print()

# Get tracker and start status updater
tracker = get_progress_tracker(project_root, auto_start=True)

# Register a test migration process
process_id = "test_migration_demo"
process_name = "Migration Demo"
tracker.register_process(
    process_id=process_id,
    process_name=process_name,
    source_name="Test-Source",
    total_items=1000,
    agent_type="jarvis",
    is_auto=True
)

print("✅ Registered test migration process")
print("   Simulating migration progress...")
print()

# Simulate migration with success/failure counts
success = 0
failure = 0
completed = 0

for i in range(20):
    # Simulate progress
    success += 250  # Files successfully moved
    if i % 5 == 0:
        failure += 10  # Some failures

    completed = success + failure

    # Update progress with success/failure counts
    tracker.update_progress(
        process_id=process_id,
        completed_items=completed,
        success_count=success,
        failure_count=failure
    )

    # Show current status
    proc = tracker.processes[process_id]
    elapsed = proc.elapsed_time_string

    print(f"  [{elapsed}] +{success} -{failure} Auto | {proc.progress_percentage:.1f}%")

    time.sleep(0.5)

print()
print("✅ Test complete")
print()
print("Check cursor_status.json to see the migration-style format:")
print("  Format: '3m +5143 -117 Auto | Migration Demo'")
print()

# Keep running for a bit so you can see it in the status bar
print("Status bar will continue updating for 5 seconds...")
time.sleep(5)

tracker.complete_process(process_id)
print("✅ Test migration process completed")
