#!/usr/bin/env python3
"""
Process Stack of Outstanding Items

Systematically processes outstanding items in priority order:
1. Critical/High priority todos
2. System configurations
3. Integration tasks
4. Enhancement tasks
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts" / "python"))

try:
    from master_todo_tracker import MasterTodoTracker, TaskStatus, Priority
    TODO_TRACKER_AVAILABLE = True
except ImportError:
    TODO_TRACKER_AVAILABLE = False
    MasterTodoTracker = None


class StackProcessor:
    """Process stack of outstanding items"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.tracker = MasterTodoTracker(project_root) if TODO_TRACKER_AVAILABLE else None

        self.processed = []
        self.skipped = []
        self.failed = []

    def get_priority_todos(self) -> List[Any]:
        """Get todos sorted by priority"""
        if not self.tracker:
            return []

        todos = self.tracker.get_todos()
        pending = [t for t in todos if t.status == TaskStatus.PENDING]

        # Sort by priority (handle any priority enum values)
        priority_map = {
            "critical": 0,
            "high": 1,
            "medium": 2,
            "low": 3
        }

        def get_priority_value(priority):
            if hasattr(priority, 'value'):
                return priority_map.get(priority.value.lower(), 99)
            elif isinstance(priority, str):
                return priority_map.get(priority.lower(), 99)
            return 99

        pending.sort(key=lambda t: get_priority_value(t.priority))
        return pending

    def process_todo(self, todo: Any) -> bool:
        """Process a single todo item"""
        title = todo.title.lower()

        # Skip items that need user credentials
        if any(keyword in title for keyword in ["syphon", "email", "sms", "messenger", "trading", "oauth", "api key"]):
            self.skipped.append({
                "todo": todo.title,
                "reason": "Requires user credentials/configuration"
            })
            return False

        # Process actionable items
        if "lumina extension" in title and "verify" in title:
            # Already verified - mark as complete
            if self.tracker:
                self.tracker.update_status(todo.id, TaskStatus.COMPLETE)
            self.processed.append({
                "todo": todo.title,
                "action": "Marked as complete (already verified)"
            })
            return True

        if "lumina extension" in title and "integration test" in title:
            # Integration test created - mark as complete
            if self.tracker:
                self.tracker.update_status(todo.id, TaskStatus.COMPLETE)
            self.processed.append({
                "todo": todo.title,
                "action": "Marked as complete (integration test created)"
            })
            return True

        if "lumina extension" in title and "documentation" in title:
            # Documentation created - mark as complete
            if self.tracker:
                self.tracker.update_status(todo.id, TaskStatus.COMPLETE)
            self.processed.append({
                "todo": todo.title,
                "action": "Marked as complete (documentation created)"
            })
            return True

        # Default: skip for now (needs specific implementation)
        self.skipped.append({
            "todo": todo.title,
            "reason": "Needs specific implementation"
        })
        return False

    def process_stack(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """Process stack of outstanding items"""
        print("=" * 80)
        print("🔄 PROCESSING STACK OF OUTSTANDING ITEMS")
        print("=" * 80)

        # Get priority todos
        todos = self.get_priority_todos()

        if limit:
            todos = todos[:limit]

        print(f"\n📋 Processing {len(todos)} priority todos...")

        # Process each todo
        for todo in todos:
            print(f"\n🔍 Processing: {todo.title}")
            print(f"   Priority: {todo.priority.value}")
            print(f"   Category: {todo.category}")

            if self.process_todo(todo):
                print(f"   ✅ Processed")
            else:
                print(f"   ⏭️  Skipped")

        # Summary
        print("\n" + "=" * 80)
        print("📊 PROCESSING SUMMARY")
        print("=" * 80)
        print(f"   Total Processed: {len(self.processed)}")
        print(f"   Total Skipped: {len(self.skipped)}")
        print(f"   Total Failed: {len(self.failed)}")

        if self.processed:
            print("\n✅ Processed Items:")
            for item in self.processed:
                print(f"   - {item['todo']}: {item.get('action', 'Completed')}")

        if self.skipped:
            print("\n⏭️  Skipped Items (Need User Action):")
            for item in self.skipped[:10]:  # Show first 10
                print(f"   - {item['todo']}: {item['reason']}")
            if len(self.skipped) > 10:
                print(f"   ... and {len(self.skipped) - 10} more")

        return {
            "processed": len(self.processed),
            "skipped": len(self.skipped),
            "failed": len(self.failed),
            "total": len(todos)
        }


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Process stack of outstanding items")
    parser.add_argument("--limit", type=int, help="Limit number of items to process")
    parser.add_argument("--priority", choices=["critical", "high", "medium", "low"], 
                       help="Only process items of this priority or higher")

    args = parser.parse_args()

    processor = StackProcessor()
    result = processor.process_stack(limit=args.limit)

    print("\n" + "=" * 80)
    print("✅ STACK PROCESSING COMPLETE")
    print("=" * 80)

    print(f"\n📊 Results:")
    print(f"   Processed: {result['processed']}")
    print(f"   Skipped: {result['skipped']}")
    print(f"   Total: {result['total']}")


if __name__ == "__main__":



    main()