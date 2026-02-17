#!/usr/bin/env python3
"""
Demo: AI SYPHON + IDM Orchestrator

Demonstrates the integrated system with real-time monitoring.

Usage:
    python demo_ai_syphon_idm.py --urls "https://example.com" "https://youtube.com/watch?v=..."
    python demo_ai_syphon_idm.py --file urls.txt --monitor
"""

import sys
import time
from pathlib import Path

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from ai_syphon_idm_orchestrator import AIOrchestrator
from workflow_realtime_monitor import WorkflowMonitor


def demo_basic():
    """Basic demo without real-time monitor"""
    print("=" * 80)
    print("🤖 AI SYPHON + IDM Orchestrator - Basic Demo")
    print("=" * 80)

    # Initialize orchestrator
    orchestrator = AIOrchestrator(enable_ai_routing=True)
    orchestrator.start_monitoring()

    # Add some demo URLs
    demo_urls = [
        "https://www.youtube.com/@EWTN",
        "https://www.ewtn.com",
    ]

    print(f"\n➕ Adding {len(demo_urls)} items...")
    for url in demo_urls:
        item_id = orchestrator.add_item(url, source_type="web")
        print(f"   ✅ Added: {item_id}")

    # Monitor for a bit
    print("\n⏳ Processing items (30 seconds)...")
    try:
        for i in range(6):
            time.sleep(5)
            orchestrator.print_status()
    except KeyboardInterrupt:
        pass

    # Stop
    orchestrator.stop_monitoring()
    orchestrator.print_status()

    print("\n✅ Demo complete!")


def demo_with_monitor():
    """Demo with real-time visual monitor"""
    print("=" * 80)
    print("🤖 AI SYPHON + IDM Orchestrator - Real-Time Monitor Demo")
    print("=" * 80)

    # Initialize orchestrator
    orchestrator = AIOrchestrator(enable_ai_routing=True)
    orchestrator.start_monitoring()

    # Add demo URLs
    demo_urls = [
        "https://www.youtube.com/@EWTN",
        "https://www.ewtn.com",
    ]

    print(f"\n➕ Adding {len(demo_urls)} items...")
    for url in demo_urls:
        orchestrator.add_item(url, source_type="web")

    # Start monitor in separate thread
    monitor = WorkflowMonitor(orchestrator)
    monitor.update_interval = 2.0

    print("\n🚀 Starting real-time monitor...")
    print("   Press Ctrl+C to stop\n")

    try:
        # Run monitor (blocks)
        monitor.start()
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping...")
        monitor.stop()
        orchestrator.stop_monitoring()

    print("\n✅ Demo complete!")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="AI SYPHON + IDM Demo")
    parser.add_argument("--monitor", action="store_true",
                       help="Use real-time visual monitor")
    parser.add_argument("--urls", nargs="+",
                       help="URLs to process")

    args = parser.parse_args()

    if args.monitor:
        demo_with_monitor()
    else:
        demo_basic()


if __name__ == "__main__":


    main()