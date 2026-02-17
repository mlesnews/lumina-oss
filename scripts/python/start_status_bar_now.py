#!/usr/bin/env python3
"""Immediate deployment: Start status bar system NOW"""

import sys
import time
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts" / "python"))

from jarvis_progress_tracker import get_progress_tracker

print("=" * 80)
print("🚀 IMMEDIATE DEPLOYMENT: STATUS BAR SYSTEM")
print("=" * 80)
print()

# Get tracker and start status updater immediately
tracker = get_progress_tracker(project_root, auto_start=True)

print("✅ Status tracker initialized")
print("✅ Status updater thread started")
print()

# Verify it's running
if hasattr(tracker, '_running') and tracker._running:
    print("✅ Status updater is RUNNING")
else:
    print("⚠️  Status updater not running - starting now...")
    tracker.start_status_updater()

print()

# Show current status
aggregate = tracker.get_aggregate_progress()
print("📊 Current Status:")
print(f"   Overall Progress: {aggregate.overall_percentage:.1f}%")
print(f"   Active Processes: {aggregate.active_processes}")
print(f"   Total Items: {aggregate.total_items}")
print(f"   Completed: {aggregate.total_completed}")
if aggregate.eta_string:
    print(f"   ETA: {aggregate.eta_string}")
print()

# Force immediate update
print("🔄 Forcing immediate status update...")
tracker._update_cursor_status()
print("✅ Status file updated")
print()

# Check status file
status_file = project_root / "data" / "progress_tracking" / "cursor_status.json"
if status_file.exists():
    import json
    with open(status_file, 'r') as f:
        data = json.load(f)
    print("📋 Status Bar Text (visible in Cursor IDE):")
    print(f"   Signboard: {data.get('signboard_text', 'N/A')}")
    print(f"   Expanded: {data.get('expanded_text', 'N/A')}")
    print()
    print(f"   Last Updated: {data.get('timestamp', 'N/A')}")
else:
    print("⚠️  Status file not found")

print()
print("=" * 80)
print("✅ STATUS BAR SYSTEM DEPLOYED AND RUNNING")
print("=" * 80)
print()
print("The status bar should now be visible in Cursor IDE footer/status bar.")
print("It updates every 0.5 seconds while processes are active.")
