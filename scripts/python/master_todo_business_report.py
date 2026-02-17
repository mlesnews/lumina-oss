#!/usr/bin/env python3
"""
Master TODO Business Needs Report

Generates a comprehensive report of master TODO list focusing on business needs.
Shows what's been done, what's in progress, and what's next.

Tags: #TODO #BUSINESS_NEEDS #REPORT @JARVIS @LUMINA  # [ADDRESSED]  # [ADDRESSED]
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    logger = get_logger("MasterTODOBusinessReport")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("MasterTODOBusinessReport")


class MasterTODOBusinessReport:
    """
    Generates business-focused report of master TODO list
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.blueprint_file = self.project_root / "config" / "one_ring_blueprint.json"

    def load_master_todos(self) -> List[Dict[str, Any]]:
        """Load master todos from One Ring Blueprint"""
        todos = []

        if self.blueprint_file.exists():
            try:
                with open(self.blueprint_file, 'r', encoding='utf-8') as f:
                    blueprint = json.load(f)
                    todos = blueprint.get("master_todos", [])
            except Exception as e:
                logger.error(f"Failed to load todos: {e}")

        return todos

    def generate_report(self, priority_filter: Optional[str] = None) -> Dict[str, Any]:
        """Generate comprehensive business report"""
        todos = self.load_master_todos()

        if not todos:
            return {"error": "No todos found"}

        # Filter by priority if specified
        if priority_filter:
            todos = [t for t in todos if t.get("priority", "").lower() == priority_filter.lower()]

        # Categorize todos
        completed_items = []
        in_progress_items = []
        pending_items = []
        completed_subtasks = []

        for item in todos:
            status = item.get("status", "").lower()

            if status in ["completed", "done", "finished"]:
                completed_items.append(item)
            elif status in ["in_progress", "in progress", "working"]:
                in_progress_items.append(item)
            else:
                pending_items.append(item)

            # Check subtasks
            subtasks = item.get("subtasks", [])
            for subtask in subtasks:
                if subtask.get("status", "").lower() in ["completed", "done", "finished"]:
                    completed_subtasks.append({
                        "parent": item,
                        "subtask": subtask
                    })

        # Sort by priority (business needs)
        priority_order = {"high": 1, "medium": 2, "low": 3, "critical": 0}

        def sort_key(item):
            priority = item.get("priority", "low").lower()
            return priority_order.get(priority, 99)

        in_progress_items.sort(key=sort_key)
        pending_items.sort(key=sort_key)

        report = {
            "timestamp": datetime.now().isoformat(),
            "total_todos": len(todos),
            "summary": {
                "completed": len(completed_items),
                "in_progress": len(in_progress_items),
                "pending": len(pending_items),
                "completed_subtasks": len(completed_subtasks)
            },
            "completed_items": completed_items,
            "in_progress_items": in_progress_items,
            "pending_items": pending_items,
            "completed_subtasks": completed_subtasks,
            "high_priority_pending": [t for t in pending_items if t.get("priority", "").lower() == "high"],
            "business_needs": {
                "critical": [t for t in todos if t.get("priority", "").lower() == "critical"],
                "high": [t for t in todos if t.get("priority", "").lower() == "high"],
                "next_actions": self._get_next_actions(in_progress_items, pending_items)
            }
        }

        return report

    def _get_next_actions(self, in_progress: List[Dict], pending: List[Dict]) -> List[Dict]:
        """Get next actions based on business needs"""
        next_actions = []

        # First: Continue in-progress items
        for item in in_progress:
            subtasks = item.get("subtasks", [])
            pending_subtasks = [st for st in subtasks if st.get("status", "").lower() not in ["completed", "done"]]
            if pending_subtasks:
                next_actions.append({
                    "type": "continue",
                    "item": item,
                    "next_subtask": pending_subtasks[0] if pending_subtasks else None
                })

        # Then: Start high-priority pending items
        high_priority = [t for t in pending if t.get("priority", "").lower() == "high"]
        for item in high_priority[:5]:  # Top 5
            next_actions.append({
                "type": "start",
                "item": item,
                "first_subtask": item.get("subtasks", [])[0] if item.get("subtasks") else None
            })

        return next_actions

    def print_report(self, report: Dict[str, Any]):
        """Print formatted report"""
        print("=" * 80)
        print("📋 MASTER TODO LIST - BUSINESS NEEDS REPORT")
        print("=" * 80)
        print(f"   Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Total TODOs: {report['total_todos']}")
        print("")

        # Summary
        summary = report["summary"]
        print("📊 SUMMARY")
        print("=" * 80)
        print(f"   ✅ Completed Items: {summary['completed']}")
        print(f"   🔄 In Progress: {summary['in_progress']}")
        print(f"   ⏳ Pending: {summary['pending']}")
        print(f"   ✅ Completed Subtasks: {summary['completed_subtasks']}")
        print("")

        # Completed Subtasks
        if report["completed_subtasks"]:
            print("✅ COMPLETED SUBTASKS (Validated)")
            print("=" * 80)
            for st_info in report["completed_subtasks"]:
                parent = st_info["parent"]
                subtask = st_info["subtask"]
                print(f"   ✅ {parent.get('id')} → {subtask.get('id')}: {subtask.get('content', '')}")
            print("")

        # In Progress
        if report["in_progress_items"]:
            print("🔄 IN PROGRESS (Business Needs)")
            print("=" * 80)
            for item in report["in_progress_items"]:
                priority = item.get("priority", "unknown").upper()
                print(f"   🔄 [{priority}] {item.get('id')}: {item.get('content', '')}")
                subtasks = item.get("subtasks", [])
                if subtasks:
                    completed = [st for st in subtasks if st.get("status", "").lower() == "completed"]
                    pending = [st for st in subtasks if st.get("status", "").lower() != "completed"]
                    print(f"      Progress: {len(completed)}/{len(subtasks)} subtasks completed")
                    if pending:
                        print(f"      Next: {pending[0].get('content', '')[:60]}...")
                print("")

        # High Priority Pending
        if report["high_priority_pending"]:
            print("🚨 HIGH PRIORITY PENDING (Business Needs)")
            print("=" * 80)
            for item in report["high_priority_pending"]:
                print(f"   ⏳ {item.get('id')}: {item.get('content', '')}")
                category = item.get("category", "unknown")
                print(f"      Category: {category}")
                subtasks = item.get("subtasks", [])
                if subtasks:
                    print(f"      Subtasks: {len(subtasks)}")
                print("")

        # Next Actions
        if report["business_needs"]["next_actions"]:
            print("🎯 NEXT ACTIONS (Business Needs)")
            print("=" * 80)
            for i, action in enumerate(report["business_needs"]["next_actions"], 1):
                item = action["item"]
                action_type = action["type"]
                if action_type == "continue":
                    next_st = action.get("next_subtask")
                    print(f"   {i}. Continue: {item.get('id')} - {item.get('content', '')[:50]}...")
                    if next_st:
                        print(f"      → Next: {next_st.get('content', '')}")
                else:
                    first_st = action.get("first_subtask")
                    print(f"   {i}. Start: {item.get('id')} - {item.get('content', '')[:50]}...")
                    if first_st:
                        print(f"      → First: {first_st.get('content', '')}")
                print("")

        print("=" * 80)


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Generate master TODO business report")
        parser.add_argument("--priority", choices=["high", "medium", "low", "critical"],
                           help="Filter by priority")
        parser.add_argument("--save", action="store_true", help="Save report to file")

        args = parser.parse_args()

        reporter = MasterTODOBusinessReport()
        report = reporter.generate_report(priority_filter=args.priority)

        reporter.print_report(report)

        if args.save:
            reports_dir = reporter.project_root / "data" / "todo_reports"
            reports_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = reports_dir / f"business_report_{timestamp}.json"

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            logger.info(f"📁 Report saved: {report_file}")

        return report


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":

    main()