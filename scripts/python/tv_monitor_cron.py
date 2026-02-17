#!/usr/bin/env python3
"""
TV Channel Monitor Cron Job
Scheduled monitoring of TV channels for automated content extraction

Usage:
    python tv_monitor_cron.py
    # Add to cron: */60 * * * * python /path/to/tv_monitor_cron.py
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

from tv_channel_monitor import TVChannelMonitor
from universal_decision_tree import decide, DecisionContext, DecisionOutcome


# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def main():
    """Run TV channel monitoring"""
    monitor = TVChannelMonitor()

    print("Starting TV Channel Monitor...")
    results = monitor.monitor_all()

    total_new = sum(len(contents) for contents in results.values())

    print(f"\n{'='*80}")
    print(f"TV Channel Monitor Complete")
    print(f"{'='*80}")
    print(f"Channels monitored: {len(results)}")
    print(f"Total new items: {total_new}\n")

    for channel, contents in results.items():
        if contents:
            print(f"{channel}: {len(contents)} new items")
            for content in contents:
                print(f"  [{content.relevance.value.upper()}] {content.title}")

    return 0 if total_new > 0 else 1

if __name__ == "__main__":



    sys.exit(main())