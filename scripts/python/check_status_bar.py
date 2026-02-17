#!/usr/bin/env python3
"""Check status bar progress tracking system"""

import json
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts" / "python"))

status_file = project_root / "data" / "progress_tracking" / "cursor_status.json"

print("=" * 80)
print("STATUS BAR PROGRESS TRACKING - POST REBOOT CHECK")
print("=" * 80)
print()

if not status_file.exists():
    print("❌ Status file not found - no active progress tracking")
    sys.exit(0)

with open(status_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("📊 Current Status:")
print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
print(f"   Mode: {data.get('mode', 'N/A')}")
print()

aggregate = data.get('aggregate', {})
print("📈 Aggregate Progress:")
print(f"   Overall: {aggregate.get('overall_percentage', 0):.1f}%")
print(f"   Active Processes: {aggregate.get('active_processes', 0)}")
print(f"   Total Items: {aggregate.get('total_items', 0)}")
print(f"   Completed: {aggregate.get('total_completed', 0)}")
print(f"   ETA: {aggregate.get('eta', 'N/A')}")
print()

progressive = data.get('progressive', {})
per_process = progressive.get('per_process', {})

if per_process:
    print("🔄 Active Processes:")
    for pid, proc in per_process.items():
        status = proc.get('status', 'running')
        pct = proc.get('percentage', 0)
        completed = proc.get('completed', 0)
        total = proc.get('total', 0)
        name = proc.get('name', pid)

        status_icon = "✅" if status == "completed" else "⏳" if status == "running" else "❌"
        print(f"   {status_icon} {name}: {pct:.1f}% ({completed}/{total}) - {status}")
else:
    print("✅ No active processes")

print()
print("📋 Status Bar Text:")
print(f"   Signboard: {data.get('signboard_text', 'N/A')}")
print(f"   Expanded: {data.get('expanded_text', 'N/A')}")
print()

# Check if status updater should be running
print("🔍 Status Updater Check:")
print("   The status updater thread should be running if any process is active")
print("   Check if cursor_status.json is being updated regularly")
print()

# Check for stale migration processes
migration_processes = [pid for pid in per_process.keys() if 'migration' in pid.lower() or 'nas' in pid.lower() or 'ollama' in pid.lower()]
if migration_processes:
    print("⚠️  Migration-related processes detected:")
    for pid in migration_processes:
        proc = per_process[pid]
        if proc.get('status') != 'completed':
            print(f"   - {pid}: {proc.get('percentage', 0):.1f}% - May need cleanup")
    print()
