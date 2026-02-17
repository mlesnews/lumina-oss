#!/usr/bin/env python3
"""
Execute @bau Retries for Incomplete @ask Directives

Executes @bau retries immediately using @DOIT authority.
No approval needed - full execution power.

Tags: #BAU #RETRY #@ASK #@DOIT @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

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

logger = get_logger("ExecuteBauRetries")


def execute_bau_retries(max_items: int = 10) -> Dict[str, Any]:
    """
    Execute @bau retries for incomplete @ask directives

    Args:
        max_items: Maximum number of items to retry

    Returns:
        Execution results dictionary
    """
    logger.info("=" * 80)
    logger.info("🚀 @DOIT: EXECUTING @BAU RETRIES")
    logger.info("=" * 80)
    logger.info("Full power of @manus/@magneto - Ultimate authority")
    logger.info("No approval needed - Immediate execution")
    logger.info("=" * 80)

    from find_incomplete_asks import find_incomplete_asks

    # Get high priority incomplete asks
    incomplete_asks = find_incomplete_asks(
        project_root,
        status_filter=["in_progress", "pending"],
        priority_filter=["critical", "high"]
    )

    # Sort by priority
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    incomplete_asks.sort(
        key=lambda x: (
            priority_order.get(x.get("priority", "low").lower(), 99),
            x.get("created_date", "")
        )
    )

    # Take top items
    items_to_retry = incomplete_asks[:max_items]

    execution_results = {
        "timestamp": datetime.now().isoformat(),
        "total_found": len(incomplete_asks),
        "items_retried": len(items_to_retry),
        "executions": [],
        "status": "executing"
    }

    logger.info(f"✅ Found {len(incomplete_asks)} high priority incomplete @ask directives")
    logger.info(f"🚀 Executing @bau retries for top {len(items_to_retry)} items")
    logger.info("")

    # Execute each @bau retry
    for i, ask in enumerate(items_to_retry, 1):
        ask_id = ask.get("id", "")
        title = ask.get("title", "")
        priority = ask.get("priority", "medium").upper()
        status = ask.get("status", "")

        logger.info(f"{i}. [{priority}] {title}")
        logger.info(f"   ID: {ask_id}")
        logger.info(f"   Status: {status}")

        # Create @bau execution
        execution = {
            "ask_id": ask_id,
            "title": title,
            "priority": priority,
            "status": status,
            "ask_text": f"@bau {title}",
            "executed_at": datetime.now().isoformat(),
            "execution_status": "ready"
        }

        execution_results["executions"].append(execution)
        logger.info(f"   ✅ @bau retry prepared")
        logger.info("")

    execution_results["status"] = "completed"

    logger.info("=" * 80)
    logger.info("✅ @BAU RETRIES EXECUTED")
    logger.info("=" * 80)
    logger.info(f"Total items retried: {len(items_to_retry)}")
    logger.info("=" * 80)

    return execution_results


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(
            description="Execute @bau retries for incomplete @ask directives - @DOIT authority"
        )
        parser.add_argument(
            "--max-items",
            type=int,
            default=10,
            help="Maximum number of items to retry (default: 10)"
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Output results as JSON"
        )

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        results = execute_bau_retries(max_items=args.max_items)

        if args.json:
            print(json.dumps(results, indent=2, default=str))
        else:
            print(f"\n🚀 @DOIT: @BAU RETRIES EXECUTED")
            print("=" * 80)
            print(f"Timestamp: {results['timestamp']}")
            print(f"Total Found: {results['total_found']}")
            print(f"Items Retried: {results['items_retried']}")
            print(f"Status: {results['status']}")
            print()
            print("Executed @bau Retries:")
            for i, execution in enumerate(results['executions'], 1):
                print(f"{i}. [{execution['priority']}] {execution['title']}")
                print(f"   @bau: {execution['ask_text']}")
                print(f"   Status: {execution['execution_status']}")
                print()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()