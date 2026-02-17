#!/usr/bin/env python3
"""
Real-Time Workflow Monitor

Live visualization of AI SYPHON + IDM Orchestrator workflow processing.

Features:
- Real-time status updates
- Stage-by-stage progress tracking
- Visual workflow representation
- Debug information display
- Performance metrics

@MONITOR @REALTIME @VISUALIZATION @DEBUG
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict
import threading

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from ai_syphon_idm_orchestrator import AIOrchestrator, WorkflowStage
except ImportError:
    AIOrchestrator = None
    WorkflowStage = None


class WorkflowMonitor:
    """Real-time workflow monitor with visualization"""

    def __init__(self, orchestrator: Optional[AIOrchestrator] = None):
        """Initialize monitor"""
        self.logger = get_logger("WorkflowMonitor")
        self.orchestrator = orchestrator
        self.running = False
        self.update_interval = 2.0  # seconds

        # Statistics tracking
        self.stage_times: Dict[str, List[float]] = defaultdict(list)
        self.item_timelines: Dict[str, List[Dict[str, Any]]] = {}

        # Display settings
        self.show_debug = True
        self.show_timeline = True
        self.show_performance = True

    def start(self):
        """Start monitoring"""
        if not self.orchestrator:
            self.logger.error("No orchestrator provided")
            return

        self.running = True

        # Add monitor as status callback
        self.orchestrator.add_status_callback(self._on_status_update)

        # Start display loop
        self._display_loop()

    def stop(self):
        """Stop monitoring"""
        self.running = False

    def _on_status_update(self, status: Dict[str, Any]):
        """Handle status update from orchestrator"""
        if status.get("type") == "stage_update":
            item_id = status.get("item_id")
            new_stage = status.get("new_stage")
            item = status.get("item", {})

            # Track timeline
            if item_id not in self.item_timelines:
                self.item_timelines[item_id] = []

            self.item_timelines[item_id].append({
                "stage": new_stage,
                "timestamp": datetime.now().isoformat(),
                "metadata": item.get("metadata", {})
            })

            # Track stage timing
            if len(self.item_timelines[item_id]) > 1:
                prev_time = datetime.fromisoformat(self.item_timelines[item_id][-2]["timestamp"])
                curr_time = datetime.fromisoformat(self.item_timelines[item_id][-1]["timestamp"])
                duration = (curr_time - prev_time).total_seconds()
                self.stage_times[new_stage].append(duration)

    def _display_loop(self):
        """Main display loop"""
        import os

        while self.running:
            try:
                # Clear screen (works on Windows and Unix)
                os.system('cls' if os.name == 'nt' else 'clear')

                # Get current status
                status = self.orchestrator.get_status()

                # Display header
                self._display_header()

                # Display statistics
                self._display_stats(status)

                # Display active items
                self._display_active_items(status)

                # Display stage queues
                self._display_queues(status)

                # Display performance metrics
                if self.show_performance:
                    self._display_performance()

                # Display debug info
                if self.show_debug:
                    self._display_debug(status)

                # Wait for next update
                time.sleep(self.update_interval)

            except KeyboardInterrupt:
                self.stop()
                break
            except Exception as e:
                self.logger.error(f"Display loop error: {e}")
                time.sleep(self.update_interval)

    def _display_header(self):
        """Display header"""
        print("=" * 100)
        print("🤖 AI SYPHON + IDM ORCHESTRATOR - REAL-TIME MONITOR")
        print("=" * 100)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

    def _display_stats(self, status: Dict[str, Any]):
        """Display statistics with transparency metrics"""
        stats = status.get("stats", {})
        progress = status.get("progress", {})

        # Calculate current position
        total = stats.get('total_items', 0)
        completed = stats.get('completed', 0)
        failed = stats.get('failed', 0)
        in_progress = total - completed - failed
        current_index = completed + in_progress

        # Progress metrics
        percentage = progress.get('completion_percentage', 0.0)
        items_per_sec = progress.get('items_per_second', 0.0)
        items_per_min = progress.get('items_per_minute', 0.0)
        elapsed = progress.get('elapsed_time', 0.0)
        eta_seconds = progress.get('estimated_time_remaining', 0.0)

        # Format time
        def format_time(seconds):
            if seconds < 60:
                return f"{int(seconds)}s"
            elif seconds < 3600:
                return f"{int(seconds // 60)}m {int(seconds % 60)}s"
            else:
                hours = int(seconds // 3600)
                minutes = int((seconds % 3600) // 60)
                return f"{hours}h {minutes}m"

        print("=" * 100)
        print("📊 TRANSPARENCY METRICS")
        print("=" * 100)

        # Progress bar
        bar_width = 60
        filled = int((percentage / 100.0) * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        print(f"\n🎯 PROGRESS: [{bar}] {percentage:5.1f}%")
        print(f"   Current: {current_index}/{total} items")
        print(f"   Completed: {completed} | Failed: {failed} | In Progress: {in_progress}")
        print()

        # Speed metrics
        print("⚡ PROCESSING SPEED")
        print("-" * 100)
        print(f"   Items/Second: {items_per_sec:6.2f} items/s")
        print(f"   Items/Minute: {items_per_min:6.2f} items/min (RPM)")
        print(f"   Elapsed Time: {format_time(elapsed)}")
        if eta_seconds > 0:
            print(f"   ETA: {format_time(eta_seconds)}")
        else:
            print(f"   ETA: Calculating...")
        print()

        # Stage distribution
        print("📋 STAGE DISTRIBUTION")
        print("-" * 100)
        by_stage = stats.get("by_stage", {})
        for stage_name, count in sorted(by_stage.items()):
            if count > 0:
                bar = "█" * min(count, 50)
                print(f"  {stage_name:20s} {count:>6} {bar}")
        print()

    def _display_active_items(self, status: Dict[str, Any]):
        """Display active items"""
        active_items = [
            item for item in status.get("items", [])
            if item.get("stage") not in ["completed", "failed", "skipped"]
        ]

        if not active_items:
            print("✅ No active items")
            print()
            return

        print(f"🔄 ACTIVE ITEMS ({len(active_items)})")
        print("-" * 100)

        for item in active_items[:10]:  # Show top 10
            item_id = item.get("item_id", "unknown")
            stage = item.get("stage", "unknown")
            url = item.get("url", "")[:60]
            progress = item.get("progress", 0.0)

            # Stage indicator
            stage_icons = {
                "discovery": "🔍",
                "queued": "⏳",
                "downloading": "⬇️",
                "downloaded": "✅",
                "extracting": "🔬",
                "extracted": "✅",
                "processing": "⚙️",
                "processed": "✅"
            }
            icon = stage_icons.get(stage, "🔄")

            # Progress bar
            progress_bar = "█" * int(progress * 20) + "░" * (20 - int(progress * 20))

            print(f"{icon} {item_id[:20]:20s} {stage:15s} {progress_bar} {progress:5.1f}%")
            print(f"   {url}")

            if item.get("error"):
                print(f"   ⚠️  Error: {item['error'][:60]}")
            print()

        if len(active_items) > 10:
            print(f"   ... and {len(active_items) - 10} more items")
        print()

    def _display_queues(self, status: Dict[str, Any]):
        """Display stage queues"""
        queues = status.get("stage_queues", {})

        print("📋 STAGE QUEUES")
        print("-" * 100)
        for stage_name, queue_size in sorted(queues.items()):
            if queue_size > 0:
                print(f"  {stage_name:20s} {queue_size:>6} items")
        print()

    def _display_performance(self):
        """Display performance metrics"""
        if not self.stage_times:
            return

        print("⚡ PERFORMANCE METRICS")
        print("-" * 100)

        for stage, times in self.stage_times.items():
            if times:
                avg_time = sum(times) / len(times)
                min_time = min(times)
                max_time = max(times)
                print(f"  {stage:20s} Avg: {avg_time:6.2f}s  Min: {min_time:6.2f}s  Max: {max_time:6.2f}s  Count: {len(times)}")
        print()

    def _display_debug(self, status: Dict[str, Any]):
        """Display debug information"""
        print("🐛 DEBUG INFORMATION")
        print("-" * 100)

        # Show recent timeline entries
        if self.show_timeline and self.item_timelines:
            print("Recent Activity:")
            recent_items = list(self.item_timelines.items())[-5:]
            for item_id, timeline in recent_items:
                if timeline:
                    latest = timeline[-1]
                    print(f"  {item_id[:30]:30s} → {latest['stage']:15s} at {latest['timestamp'][11:19]}")
        print()
        print("=" * 100)
        print("Press Ctrl+C to stop monitoring")
        print()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Real-Time Workflow Monitor")
    parser.add_argument("--orchestrator-status", type=Path, 
                       help="Path to orchestrator status file")
    parser.add_argument("--update-interval", type=float, default=2.0,
                       help="Update interval in seconds")
    parser.add_argument("--no-debug", action="store_true",
                       help="Disable debug information")
    parser.add_argument("--no-performance", action="store_true",
                       help="Disable performance metrics")

    args = parser.parse_args()

    if not AIOrchestrator:
        print("❌ AIOrchestrator not available")
        return

    # Create orchestrator
    orchestrator = AIOrchestrator()

    # Create monitor
    monitor = WorkflowMonitor(orchestrator)
    monitor.update_interval = args.update_interval
    monitor.show_debug = not args.no_debug
    monitor.show_performance = not args.no_performance

    # Start orchestrator monitoring
    orchestrator.start_monitoring()

    # Start visual monitor
    try:
        monitor.start()
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping monitor...")
        monitor.stop()
        orchestrator.stop_monitoring()


if __name__ == "__main__":


    main()