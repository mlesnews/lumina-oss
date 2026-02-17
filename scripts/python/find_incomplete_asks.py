#!/usr/bin/env python3
"""
Find Incomplete @ask Directives with Partial Status

Searches for @ask directives that were given by the O.P. but were never completed.
Shows items with partial/in_progress status.

Tags: #BAU #@ASK #INCOMPLETE #PARTIAL @JARVIS @LUMINA
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        get_logger = lambda name: logging.getLogger(name)

logger = get_logger("FindIncompleteAsks")


def find_incomplete_asks(
    project_root: Path,
    status_filter: List[str] = ["in_progress", "pending"],
    priority_filter: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Find incomplete @ask directives

    Args:
        project_root: Project root directory
        status_filter: List of statuses to include (default: in_progress, pending)
        priority_filter: Optional list of priorities to filter by

    Returns:
        List of incomplete @ask directives
    """
    logger.info("🔍 Searching for incomplete @ask directives...")

    # Load master todos
    master_todos_file = project_root / "data" / "todo" / "master_todos.json"

    if not master_todos_file.exists():
        logger.error(f"   ❌ Master todos file not found: {master_todos_file}")
        return []

    with open(master_todos_file, 'r', encoding='utf-8') as f:
        todos_data = json.load(f)

    incomplete_asks = []

    # Filter todos by status
    for todo_id, todo in todos_data.items():
        status = todo.get("status", "").lower()
        priority = todo.get("priority", "").lower()

        # Check status filter
        if status not in status_filter:
            continue

        # Check priority filter if provided
        if priority_filter and priority not in priority_filter:
            continue

        # Check if it's an @ask (has @ask in title/description or tags)
        title = todo.get("title", "").lower()
        description = todo.get("description", "").lower()
        tags = [tag.lower() for tag in todo.get("tags", [])]

        is_ask = (
            "@ask" in title or
            "@ask" in description or
            any("@ask" in tag for tag in tags) or
            "sub-ask" in title or
            "sub-ask" in description
        )

        if is_ask or True:  # Include all incomplete items for now
            incomplete_asks.append({
                "id": todo_id,
                "title": todo.get("title", ""),
                "description": todo.get("description", ""),
                "status": todo.get("status", ""),
                "priority": todo.get("priority", ""),
                "category": todo.get("category", ""),
                "created_date": todo.get("created_date", ""),
                "updated_date": todo.get("updated_date", ""),
                "tags": todo.get("tags", []),
                "notes": todo.get("notes", []),
                "percentage": todo.get("percentage", None)
            })

    logger.info(f"   ✅ Found {len(incomplete_asks)} incomplete @ask directives")

    return incomplete_asks


def format_incomplete_asks_report(incomplete_asks: List[Dict[str, Any]]) -> str:
    """
    Format incomplete asks as a report

    Args:
        incomplete_asks: List of incomplete @ask directives

    Returns:
        Formatted report string
    """
    if not incomplete_asks:
        return "No incomplete @ask directives found."

    report = []
    report.append(f"\n📋 Incomplete @ask Directives Report")
    report.append("=" * 80)
    report.append(f"Total Found: {len(incomplete_asks)}\n")

    # Group by status
    by_status = {}
    for ask in incomplete_asks:
        status = ask.get("status", "unknown")
        if status not in by_status:
            by_status[status] = []
        by_status[status].append(ask)

    # Sort by priority
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}

    for status in sorted(by_status.keys()):
        asks = by_status[status]
        asks.sort(key=lambda x: priority_order.get(x.get("priority", "low").lower(), 99))

        report.append(f"\n{'=' * 80}")
        report.append(f"Status: {status.upper()} ({len(asks)} items)")
        report.append(f"{'=' * 80}\n")

        for i, ask in enumerate(asks, 1):
            priority = ask.get("priority", "medium").upper()
            percentage = ask.get("percentage")
            percentage_str = f" ({percentage}% complete)" if percentage else ""

            report.append(f"{i}. [{priority}] {ask.get('title', 'No title')}{percentage_str}")
            report.append(f"   ID: {ask.get('id', 'unknown')}")
            report.append(f"   Category: {ask.get('category', 'uncategorized')}")

            description = ask.get('description', '')
            if description:
                desc_lines = description.split('\n')
                if len(desc_lines) > 3:
                    report.append(f"   Description: {desc_lines[0][:100]}...")
                else:
                    report.append(f"   Description: {description[:200]}")

            tags = ask.get('tags', [])
            if tags:
                report.append(f"   Tags: {', '.join(tags[:5])}")

            created = ask.get('created_date', '')
            updated = ask.get('updated_date', '')
            if created:
                report.append(f"   Created: {created}")
            if updated and updated != created:
                report.append(f"   Updated: {updated}")

            notes = ask.get('notes', [])
            if notes:
                report.append(f"   Notes: {len(notes)} note(s)")

            report.append("")

    return "\n".join(report)


def main():
    try:
        """Main entry point"""
        parser = argparse.ArgumentParser(
            description="Find incomplete @ask directives with partial status"
        )
        parser.add_argument(
            "--status",
            nargs="+",
            default=["in_progress", "pending"],
            help="Status filter (default: in_progress pending)"
        )
        parser.add_argument(
            "--priority",
            nargs="+",
            help="Priority filter (e.g., high critical)"
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Output results as JSON"
        )

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        incomplete_asks = find_incomplete_asks(
            project_root,
            status_filter=args.status,
            priority_filter=args.priority
        )

        if args.json:
            print(json.dumps(incomplete_asks, indent=2, default=str))
        else:
            report = format_incomplete_asks_report(incomplete_asks)
            print(report)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()