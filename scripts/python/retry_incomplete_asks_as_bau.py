#!/usr/bin/env python3
"""
Retry Incomplete @ask Directives as @bau

Retries incomplete @ask directives as @bau workflow, focusing on highest priority items.

Tags: #BAU #RETRY #@ASK #INCOMPLETE @JARVIS @LUMINA
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

logger = get_logger("RetryIncompleteAsksAsBau")


def get_high_priority_incomplete_asks(
    project_root: Path,
    max_items: int = 10,
    priority_filter: List[str] = ["critical", "high"]
) -> List[Dict[str, Any]]:
    """
    Get high priority incomplete @ask directives

    Args:
        project_root: Project root directory
        max_items: Maximum number of items to return
        priority_filter: Priority levels to include

    Returns:
        List of high priority incomplete @ask directives
    """
    from find_incomplete_asks import find_incomplete_asks

    incomplete_asks = find_incomplete_asks(
        project_root,
        status_filter=["in_progress", "pending"],
        priority_filter=priority_filter
    )

    # Sort by priority and date
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    incomplete_asks.sort(
        key=lambda x: (
            priority_order.get(x.get("priority", "low").lower(), 99),
            x.get("created_date", "")
        )
    )

    return incomplete_asks[:max_items]


def retry_ask_as_bau(ask: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retry an @ask directive as @bau

    Args:
        ask: @ask directive dictionary

    Returns:
        Retry result dictionary
    """
    ask_id = ask.get("id", "")
    title = ask.get("title", "")
    description = ask.get("description", "")

    logger.info(f"🔄 Retrying as @bau: {title}")
    logger.info(f"   ID: {ask_id}")
    logger.info(f"   Status: {ask.get('status', 'unknown')}")
    logger.info(f"   Priority: {ask.get('priority', 'medium')}")

    # Create @bau ask text
    ask_text = f"@bau {title}"
    if description and len(description) > 0:
        ask_text += f"\n\n{description}"

    result = {
        "ask_id": ask_id,
        "title": title,
        "description": description,
        "status": ask.get("status", ""),
        "priority": ask.get("priority", ""),
        "ask_text": ask_text,
        "retry_timestamp": datetime.now().isoformat(),
        "workflow": "@bau",
        "ready_for_execution": True
    }

    logger.info(f"   ✅ Ready for @bau retry")
    logger.info(f"   Ask text: {ask_text[:100]}...")

    return result


def main():
    try:
        """Main entry point"""
        parser = argparse.ArgumentParser(
            description="Retry incomplete @ask directives as @bau"
        )
        parser.add_argument(
            "--max-items",
            type=int,
            default=10,
            help="Maximum number of items to retry (default: 10)"
        )
        parser.add_argument(
            "--priority",
            nargs="+",
            default=["critical", "high"],
            help="Priority filter (default: critical high)"
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Output results as JSON"
        )
        parser.add_argument(
            "--execute",
            action="store_true",
            help="Actually execute the @bau retries (default: just prepare)"
        )

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent

        # Get high priority incomplete asks
        incomplete_asks = get_high_priority_incomplete_asks(
            project_root,
            max_items=args.max_items,
            priority_filter=args.priority
        )

        if not incomplete_asks:
            print("\n❌ No high priority incomplete @ask directives found")
            return

        # Retry each as @bau
        retry_results = []
        for ask in incomplete_asks:
            result = retry_ask_as_bau(ask)
            retry_results.append(result)

        if args.json:
            print(json.dumps(retry_results, indent=2, default=str))
        else:
            print(f"\n🔄 @bau Retry Preparation")
            print("=" * 80)
            print(f"Total Items: {len(retry_results)}")
            print(f"Priority Filter: {', '.join(args.priority)}")
            print()

            for i, result in enumerate(retry_results, 1):
                priority = result.get("priority", "medium").upper()
                status = result.get("status", "unknown")

                print(f"{i}. [{priority}] {result.get('title', 'No title')}")
                print(f"   Status: {status}")
                print(f"   ID: {result.get('ask_id', 'unknown')}")
                print(f"   @bau Ask Text:")
                print(f"   {result.get('ask_text', '')[:200]}...")
                print()

            if args.execute:
                print("\n✅ Executing @bau retries...")
                # Here you would actually execute the @bau asks
                # For now, just show what would be executed
            else:
                print("\n📋 Ready for @bau retry")
                print("   Use --execute flag to actually retry these @ask directives")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()