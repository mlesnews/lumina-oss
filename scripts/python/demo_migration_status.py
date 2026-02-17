#!/usr/bin/env python3
"""Quick demo of migration status bar format"""

import sys
import time
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts" / "python"))

from jarvis_progress_tracker import get_progress_tracker

tracker = get_progress_tracker(project_root, auto_start=True)

# Register migration process
process_id = "demo_migration"
tracker.register_process(
    process_id=process_id,
    process_name="NAS Migration",
    source_name="Migration-Source",
    total_items=5000,
    is_auto=True
)

# Update with migration metrics
tracker.update_progress(
    process_id=process_id,
    completed_items=5143,
    success_count=5143,
    failure_count=117
)

print("✅ Migration status bar active!")
print()
print("Status bar should show: '3m +5143 -117 Auto | NAS Migration'")
print()
print("Check cursor_status.json - the signboard_text should show the migration format")
print()

# Wait a moment for status to update
time.sleep(2)

# Check status file
import json
status_file = project_root / "data" / "progress_tracking" / "cursor_status.json"
if status_file.exists():
    with open(status_file, 'r') as f:
        data = json.load(f)
    print("Current status bar text:")
    print(f"  {data.get('signboard_text', 'N/A')}")
    print()

print("Keeping process active for 10 seconds so you can see it...")
time.sleep(10)

tracker.complete_process(process_id)
print("✅ Demo complete")
