#!/usr/bin/env python3
"""
AutoHotkey Dynamic Scaling Helper
Provides dynamic wait times for AutoHotkey scripts based on system state.

AutoHotkey calls this script to get adaptive wait times that scale based on:
- System load (CPU, memory)
- Operation context
- Number of operations

Tags: #AUTOHOTKEY #DYNAMIC_SCALING #TIMING
"""

import sys
import psutil
import json
from typing import Dict, Any
import logging
logger = logging.getLogger("autohotkey_dynamic_scaling")


def calculate_dynamic_wait(
    base_wait: float = 1.0,
    operation_count: int = 0,
    operation_type: str = "default"
) -> float:
    """
    Calculate dynamic wait time based on system state and context.

    Args:
        base_wait: Base wait time in seconds
        operation_count: Number of operations performed
        operation_type: Type of operation (focus, send_text, enter, etc.)

    Returns:
        Calculated wait time in seconds
    """
    wait_time = base_wait

    # Factor 1: Number of operations
    if operation_count > 0:
        wait_time += (operation_count * 0.2)  # +0.2s per operation

    # Factor 2: System load
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_percent = psutil.virtual_memory().percent

        # Higher load = longer wait
        if cpu_percent > 80 or memory_percent > 80:
            wait_time *= 1.5
        elif cpu_percent > 60 or memory_percent > 60:
            wait_time *= 1.2
    except Exception:
        pass  # Use base wait if can't get system stats

    # Factor 3: Operation type
    operation_multipliers = {
        "focus": 1.0,        # Focus operations need minimal wait
        "send_text": 1.2,    # Text sending needs a bit more time
        "enter": 1.5,        # Enter key needs more time for Cursor to process
        "layout_switch": 2.0, # Layout switches need significant time
        "default": 1.0
    }

    multiplier = operation_multipliers.get(operation_type, 1.0)
    wait_time *= multiplier

    return round(wait_time, 2)


def main():
    try:
        """CLI interface for AutoHotkey"""
        import argparse

        parser = argparse.ArgumentParser(description="AutoHotkey Dynamic Scaling")
        parser.add_argument("--base-wait", type=float, default=1.0, help="Base wait time")
        parser.add_argument("--operation-count", type=int, default=0, help="Number of operations")
        parser.add_argument("--operation-type", type=str, default="default", 
                           choices=["focus", "send_text", "enter", "layout_switch", "default"],
                           help="Type of operation")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        wait_time = calculate_dynamic_wait(
            base_wait=args.base_wait,
            operation_count=args.operation_count,
            operation_type=args.operation_type
        )

        if args.json:
            result = {
                "wait_time": wait_time,
                "base_wait": args.base_wait,
                "operation_count": args.operation_count,
                "operation_type": args.operation_type
            }
            print(json.dumps(result))
        else:
            # Output just the wait time (in milliseconds for AutoHotkey)
            print(int(wait_time * 1000))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()