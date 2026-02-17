#!/usr/bin/env python3
"""
Unified Queue Viewer

Displays all queue items (sources, problems, tasks, etc.) in a unified view,
treating them all the same way - just like VSCode problems panel.

Features:
- Unified display of all queue types
- Real-time updates
- Filtering and sorting
- Status indicators
- Priority highlighting

@UNIFIED @VIEWER @QUEUE
"""

import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import os

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from unified_queue_adapter import UnifiedQueueAdapter, QueueItemType, QueueItemStatus


class UnifiedQueueViewer:
    """Unified viewer for all queue items"""

    def __init__(self, adapter: Optional[UnifiedQueueAdapter] = None):
        """Initialize viewer"""
        self.adapter = adapter or UnifiedQueueAdapter()
        self.running = False
        self.update_interval = 2.0

        # Filter settings
        self.filter_type: Optional[QueueItemType] = None
        self.filter_status: Optional[QueueItemStatus] = None
        self.filter_priority_max: Optional[int] = None
        self.sort_by = "priority"  # priority, created_at, updated_at

    def start(self):
        """Start real-time viewer"""
        self.running = True
        self._display_loop()

    def stop(self):
        """Stop viewer"""
        self.running = False

    def _display_loop(self):
        """Main display loop"""
        while self.running:
            try:
                os.system('cls' if os.name == 'nt' else 'clear')
                self._display_header()
                self._display_summary()
                self._display_items()
                self._display_footer()
                time.sleep(self.update_interval)
            except KeyboardInterrupt:
                self.stop()
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(self.update_interval)

    def _display_header(self):
        """Display header"""
        print("=" * 100)
        print("📋 UNIFIED QUEUE VIEWER")
        print("=" * 100)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

    def _display_summary(self):
        """Display summary"""
        summary = self.adapter.get_queue_summary()

        print("📊 SUMMARY")
        print("-" * 100)
        print(f"Total: {summary['total_items']:>4}  |  "
              f"Pending: {summary['pending_count']:>4}  |  "
              f"Processing: {summary['processing_count']:>4}  |  "
              f"Completed: {summary['completed_count']:>4}  |  "
              f"Failed: {summary['failed_count']:>4}")
        print()

    def _display_items(self):
        """Display queue items"""
        # Get filtered items
        items = self.adapter.get_all_items(
            item_type=self.filter_type,
            status=self.filter_status,
            priority_min=self.filter_priority_max
        )

        # Sort
        if self.sort_by == "priority":
            items.sort(key=lambda x: (x.priority, x.created_at))
        elif self.sort_by == "created_at":
            items.sort(key=lambda x: x.created_at)
        elif self.sort_by == "updated_at":
            items.sort(key=lambda x: x.updated_at, reverse=True)

        if not items:
            print("✅ No items in queue")
            print()
            return

        print(f"📋 QUEUE ITEMS ({len(items)})")
        print("-" * 100)
        print(f"{'Flags':<4} {'Type':<12} {'Status':<12} {'Priority':<8} {'Title':<50} {'Progress':<10}")
        print("-" * 100)
        print("Flags: 📌=pinned, ✓=read, 🔴=unread, 📋=duplicate")
        print("-" * 100)

        for item in items[:50]:  # Show top 50
            # Type icon
            type_icons = {
                QueueItemType.SOURCE: "🔗",
                QueueItemType.PROBLEM: "⚠️",
                QueueItemType.TASK: "📝",
                QueueItemType.NOTIFICATION: "🔔",
                QueueItemType.ALERT: "🚨",
                QueueItemType.CHAT_HISTORY: "💬"
            }
            icon = type_icons.get(item.item_type, "•")

            # Status indicator
            status_icons = {
                QueueItemStatus.PENDING: "⏳",
                QueueItemStatus.QUEUED: "📥",
                QueueItemStatus.PROCESSING: "⚙️",
                QueueItemStatus.COMPLETED: "✅",
                QueueItemStatus.FAILED: "❌",
                QueueItemStatus.CANCELLED: "🚫",
                QueueItemStatus.SKIPPED: "⏭️"
            }
            status_icon = status_icons.get(item.status, "•")

            # Pin indicator
            pinned = "📌" if item.metadata.get("pinned", False) else " "

            # Read indicator
            read = "✓" if item.metadata.get("read", False) else "🔴"

            # Duplicate indicator
            dup = "📋" if item.metadata.get("is_duplicate", False) else " "

            # Priority indicator
            if item.priority <= 3:
                priority_str = f"🔴 {item.priority}"
            elif item.priority <= 6:
                priority_str = f"🟡 {item.priority}"
            else:
                priority_str = f"🟢 {item.priority}"

            # Progress bar
            progress_bar = "█" * int(item.progress / 10) + "░" * (10 - int(item.progress / 10))
            progress_str = f"{progress_bar} {item.progress:5.1f}%"

            # Title (truncate)
            title = item.title[:47] + "..." if len(item.title) > 50 else item.title

            print(f"{pinned}{read}{dup}{icon} {item.item_type.value:<10} {status_icon} {item.status.value:<10} "
                  f"{priority_str:<8} {title:<50} {progress_str}")

            # Show description or error if present
            if item.error:
                print(f"   ❌ Error: {item.error[:70]}")
            elif item.description and item.status == QueueItemStatus.PROCESSING:
                print(f"   ℹ️  {item.description[:70]}")

        if len(items) > 50:
            print(f"\n   ... and {len(items) - 50} more items")
        print()

    def _display_footer(self):
        """Display footer with controls"""
        print("-" * 100)
        print("Controls: Press Ctrl+C to stop | Items update every 2 seconds")
        print("=" * 100)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Unified Queue Viewer")
    parser.add_argument("--filter-type", choices=["source", "problem", "task", "chat_history"],
                       help="Filter by item type")
    parser.add_argument("--filter-status", choices=["pending", "processing", "completed", "failed"],
                       help="Filter by status")
    parser.add_argument("--filter-priority", type=int,
                       help="Filter by maximum priority (1-10)")
    parser.add_argument("--sort", choices=["priority", "created_at", "updated_at"],
                       default="priority", help="Sort by")

    args = parser.parse_args()

    viewer = UnifiedQueueViewer()

    # Apply filters
    if args.filter_type:
        type_map = {
            "source": QueueItemType.SOURCE,
            "problem": QueueItemType.PROBLEM,
            "task": QueueItemType.TASK,
            "chat_history": QueueItemType.CHAT_HISTORY
        }
        viewer.filter_type = type_map.get(args.filter_type)

    if args.filter_status:
        status_map = {
            "pending": QueueItemStatus.PENDING,
            "processing": QueueItemStatus.PROCESSING,
            "completed": QueueItemStatus.COMPLETED,
            "failed": QueueItemStatus.FAILED
        }
        viewer.filter_status = status_map.get(args.filter_status)

    if args.filter_priority:
        viewer.filter_priority_max = args.filter_priority

    if args.sort:
        viewer.sort_by = args.sort

    # Start viewer
    try:
        viewer.start()
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping viewer...")
        viewer.stop()


if __name__ == "__main__":


    main()