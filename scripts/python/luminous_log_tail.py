#!/usr/bin/env python3
"""
Luminous System Log Tail

Tails the Luminous system log (aggregated log) for real-time monitoring.
"One ring to find them, and the rest to bind them."

Usage:
    python luminous_log_tail.py [--follow] [--lines N] [--filter SOURCE] [--level LEVEL]

Tags: #LOG_TAILING #LUMINOUS_LOG #MONITORING #ONE_RING @JARVIS @LUMINA
"""

import sys
import argparse
import time
from pathlib import Path
from datetime import datetime
import logging
logger = logging.getLogger("luminous_log_tail")


script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from luminous_system_log_aggregator import get_luminous_log
    LUMINOUS_LOG_AVAILABLE = True
except ImportError:
    LUMINOUS_LOG_AVAILABLE = False
    print("❌ Luminous system log not available")


def tail_luminous_log(follow: bool = True, lines: int = 50, filter_source: Optional[str] = None, filter_level: Optional[str] = None):
    """
    Tail Luminous system log

    Args:
        follow: Continue tailing (like tail -f)
        lines: Number of recent lines to show initially
        filter_source: Filter by source name
        filter_level: Filter by log level
    """
    if not LUMINOUS_LOG_AVAILABLE:
        print("❌ Luminous system log not available")
        return

    try:
        aggregator = get_luminous_log()

        # Get recent logs
        recent_logs = aggregator.get_recent_logs(lines)

        # Apply filters
        if filter_source:
            recent_logs = [log for log in recent_logs if log.source.lower() == filter_source.lower()]

        if filter_level:
            recent_logs = [log for log in recent_logs if log.level.upper() == filter_level.upper()]

        # Display recent logs
        for entry in recent_logs:
            _display_log_entry(entry)

        # Follow new logs
        if follow:
            print("\n" + "=" * 80)
            print("Following Luminous system log (Ctrl+C to stop)...")
            print("=" * 80 + "\n")

            # Monitor for new entries
            last_count = len(aggregator.recent_logs)

            try:
                while True:
                    current_count = len(aggregator.recent_logs)

                    if current_count > last_count:
                        # New entries
                        new_entries = list(aggregator.recent_logs)[last_count:]

                        for entry in new_entries:
                            # Apply filters
                            if filter_source and entry.source.lower() != filter_source.lower():
                                continue
                            if filter_level and entry.level.upper() != filter_level.upper():
                                continue

                            _display_log_entry(entry)

                        last_count = current_count

                    time.sleep(0.5)

            except KeyboardInterrupt:
                print("\n🛑 Stopped tailing")

    except Exception as e:
        print(f"❌ Error tailing log: {e}")


def _display_log_entry(entry):
    try:
        """Display a log entry"""
        # Color coding by level
        colors = {
            "DEBUG": "\033[36m",    # Cyan
            "INFO": "\033[32m",     # Green
            "WARNING": "\033[33m",  # Yellow
            "ERROR": "\033[31m",    # Red
            "CRITICAL": "\033[35m"  # Magenta
        }
        reset = "\033[0m"

        color = colors.get(entry.level, "")
        timestamp = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")

        print(f"{color}{timestamp} [{entry.level:8}] [{entry.source:20}] {entry.message}{reset}")

        if entry.metadata:
            import json
            metadata_str = json.dumps(entry.metadata, indent=2, default=str)
            print(f"   {metadata_str}")


    except Exception as e:
        logger.error(f"Error in _display_log_entry: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tail Luminous system log")
    parser.add_argument(
        "--follow", "-f",
        action="store_true",
        default=True,
        help="Continue tailing (default: True)"
    )
    parser.add_argument(
        "--lines", "-n",
        type=int,
        default=50,
        help="Number of recent lines to show initially (default: 50)"
    )
    parser.add_argument(
        "--filter", "--source",
        dest="filter_source",
        help="Filter by source name"
    )
    parser.add_argument(
        "--level",
        help="Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )

    args = parser.parse_args()

    print("=" * 80)
    print("Luminous System Log Tail")
    print("=" * 80)
    print()
    print("'One ring to find them, and the rest to bind them.'")
    print()

    tail_luminous_log(
        follow=args.follow,
        lines=args.lines,
        filter_source=args.filter_source,
        filter_level=args.level
    )
