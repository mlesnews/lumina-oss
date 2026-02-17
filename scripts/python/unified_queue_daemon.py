#!/usr/bin/env python3
"""
Unified Queue Daemon

Keeps the unified queue adapter running in the background,
ensuring queue state is always up-to-date for the IDE extension.

Usage:
    python scripts/python/unified_queue_daemon.py
    python scripts/python/unified_queue_daemon.py --background
"""

import sys
import time
import signal
from pathlib import Path

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

from unified_queue_adapter import UnifiedQueueAdapter

daemon_running = True

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    global daemon_running
    print("\n⏹️  Shutting down unified queue daemon...")
    daemon_running = False

def main():
    """Main daemon loop"""
    import argparse

    parser = argparse.ArgumentParser(description="Unified Queue Daemon")
    parser.add_argument("--background", action="store_true",
                       help="Run in background (detached)")

    args = parser.parse_args()

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("=" * 80)
    print("🔗 Unified Queue Daemon Starting")
    print("=" * 80)
    print("   This keeps the queue adapter running for IDE extension")
    print("   Press Ctrl+C to stop")
    print("=" * 80)
    print()

    # Initialize adapter (starts auto-save)
    adapter = UnifiedQueueAdapter()

    print("✅ Adapter initialized")
    print("💾 Auto-save active (every 5 seconds)")
    print("📊 Queue state: data/unified_queue/queue_state.json")
    print()

    # Keep running
    try:
        while daemon_running:
            time.sleep(1)

            # Print status every 30 seconds
            if int(time.time()) % 30 == 0:
                summary = adapter.get_queue_summary()
                print(f"📊 Queue: {summary['total_items']} items | "
                      f"Pending: {summary['pending_count']} | "
                      f"Processing: {summary['processing_count']} | "
                      f"Completed: {summary['completed_count']}")
    except KeyboardInterrupt:
        signal_handler(None, None)

    print("\n✅ Daemon stopped")
    adapter.save_queue_state()
    print("💾 Final state saved")

if __name__ == "__main__":


    main()