#!/usr/bin/env python3
"""
Update Disk Migration to TOP PRIORITY

Quick script to update the disk migration task to top priority and in progress.
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_master_roadmap_display import get_master_roadmap

if __name__ == "__main__":
    roadmap = get_master_roadmap()

    # Find and update disk migration items
    for item in roadmap.roadmap.get("current_sprint", []):
        title = item.get("title", "")
        if "disk" in title.lower() or "migration" in title.lower():
            # Update to top priority
            roadmap.update_focus_item(
                item.get("id"),
                {
                    "priority": "critical",
                    "status": "in_progress"
                }
            )
            print(f"✅ Updated: {title} -> CRITICAL, IN_PROGRESS")

    print("\n✅ Disk migration updated to TOP PRIORITY")
