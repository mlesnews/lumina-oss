#!/usr/bin/env python3
"""
Network Health Dashboard - Real-Time Action Visibility

Provides real-time visibility into network health monitoring with three-path
resolution and intelligent information filtering (noise/data/information).

Filters input so you can understand what's happening:
- NOISE: Routine checks, can be ignored
- DATA: Raw information, needs analysis
- INFORMATION: Actionable intelligence, requires attention
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import threading
import time

from network_health_monitor import (
    NetworkHealthMonitor, ResolutionPath, InformationType, ResolutionAction
)
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class RealTimeDashboard:
    """
    Real-Time Dashboard for Network Health Monitoring

    Shows actions taken in real-time, filtered by importance.
    Allows you to see what's noise vs data vs information.
    """

    def __init__(self, monitor: NetworkHealthMonitor):
        self.monitor = monitor
        self.running = False
        self.display_mode = "all"  # all, information, data, noise
        self.show_paths = True  # Show all three paths

    def display_action(self, action: ResolutionAction):
        """Display an action based on information type"""
        # Filter based on display mode
        if self.display_mode == "information" and action.information_type != InformationType.INFORMATION:
            return
        if self.display_mode == "data" and action.information_type != InformationType.DATA:
            return
        if self.display_mode == "noise" and action.information_type != InformationType.NOISE:
            return

        # Format display
        timestamp = action.timestamp.strftime("%H:%M:%S")

        # Path indicator
        path_indicator = {
            ResolutionPath.AUTOMATIC_FIX: "🔵 PATH 1",
            ResolutionPath.INTELLIGENT_REVIEW: "🟡 PATH 2",
            ResolutionPath.ESCALATE_HUMAN: "🔴 PATH 3"
        }.get(action.path, "⚪")

        # Status icon
        status_icon = {
            "success": "✅",
            "failed": "❌",
            "in_progress": "⏳",
            "escalated": "🚨"
        }.get(action.status, "⚪")

        # Information type icon
        info_icon = {
            InformationType.INFORMATION: "📊",
            InformationType.DATA: "📈",
            InformationType.NOISE: "⚪"
        }.get(action.information_type, "⚪")

        # Build display line
        if self.show_paths:
            line = f"[{timestamp}] {path_indicator} {info_icon} {status_icon} {action.component}: {action.action}"
        else:
            line = f"[{timestamp}] {info_icon} {status_icon} {action.component}: {action.action}"

        print(line)

        # Show details for information type
        if action.information_type == InformationType.INFORMATION and action.details:
            for key, value in action.details.items():
                if key not in ['timestamp', 'id']:
                    print(f"         → {key}: {value}")

    def show_header(self):
        """Show dashboard header"""
        print("\n" + "=" * 80)
        print("🔌 NETWORK HEALTH DASHBOARD - REAL-TIME ACTION VISIBILITY")
        print("=" * 80)
        print(f"Mode: {self.display_mode.upper()} | Showing: {'All 3 Paths' if self.show_paths else 'Actions Only'}")
        print(f"Path 1 (🔵): Automatic Fix - Self-healing")
        print(f"Path 2 (🟡): Intelligent Review - AI-assisted")
        print(f"Path 3 (🔴): Escalate Human - Manual intervention")
        print("-" * 80)

    def show_statistics(self):
        """Show current statistics"""
        stats = self.monitor.stats
        report = self.monitor.get_status_report()

        print("\n📊 STATISTICS")
        print("-" * 80)
        print(f"Total Checks: {stats['total_checks']}")
        print(f"Healthy Components: {report['components_healthy']}/{report['components_total']}")
        print(f"Unhealthy: {report['components_unhealthy']}")
        print(f"\nThree-Path Resolution:")
        print(f"  Path 1 (Auto-Fix): {stats['path1_actions']} actions | {stats['auto_fixes_successful']}/{stats['auto_fixes_attempted']} successful")
        print(f"  Path 2 (Review): {stats['path2_actions']} actions")
        print(f"  Path 3 (Escalate): {stats['path3_actions']} actions")
        print("-" * 80)

    async def start_dashboard(self, update_interval: int = 5):
        """Start real-time dashboard"""
        self.running = True

        # Register action callback
        self.monitor.register_action_callback(self.display_action)

        # Show initial header
        self.show_header()

        # Start monitoring if not already running
        if not self.monitor.monitoring_active:
            asyncio.create_task(self.monitor.start_monitoring())
            await asyncio.sleep(2)  # Wait for monitoring to start

        # Dashboard loop
        last_stats_time = time.time()

        try:
            while self.running:
                # Show statistics every 30 seconds
                if time.time() - last_stats_time >= 30:
                    self.show_statistics()
                    last_stats_time = time.time()

                await asyncio.sleep(update_interval)

        except KeyboardInterrupt:
            print("\n\n🛑 Dashboard stopped")
            self.running = False

    def set_display_mode(self, mode: str):
        """Set display mode (all, information, data, noise)"""
        if mode in ["all", "information", "data", "noise"]:
            self.display_mode = mode
            print(f"📋 Display mode set to: {mode.upper()}")
        else:
            print(f"❌ Invalid mode. Use: all, information, data, noise")

    def toggle_paths(self):
        """Toggle path indicators"""
        self.show_paths = not self.show_paths
        print(f"📋 Path indicators: {'ON' if self.show_paths else 'OFF'}")


async def interactive_dashboard():
    """Interactive dashboard with controls"""
    monitor = NetworkHealthMonitor()
    dashboard = RealTimeDashboard(monitor)

    print("🔌 Starting Network Health Dashboard...")
    print("Controls:")
    print("  [1] Show all actions")
    print("  [2] Show only INFORMATION (actionable)")
    print("  [3] Show only DATA (needs analysis)")
    print("  [4] Show only NOISE (routine)")
    print("  [s] Show statistics")
    print("  [t] Toggle path indicators")
    print("  [q] Quit")
    print()

    # Start dashboard in background
    dashboard_task = asyncio.create_task(dashboard.start_dashboard())

    # Handle input
    try:
        while dashboard.running:
            # Check for input (non-blocking)
            await asyncio.sleep(1)

            # In a real implementation, you'd use a proper input handler
            # For now, just run and show output
            pass

    except KeyboardInterrupt:
        dashboard.running = False
        monitor.stop_monitoring()
        dashboard_task.cancel()


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Network Health Dashboard")
    parser.add_argument("--mode", choices=["all", "information", "data", "noise"],
                       default="all", help="Display mode")
    parser.add_argument("--no-paths", action="store_true",
                       help="Hide path indicators")

    args = parser.parse_args()

    monitor = NetworkHealthMonitor()
    dashboard = RealTimeDashboard(monitor)
    dashboard.display_mode = args.mode
    dashboard.show_paths = not args.no_paths

    print("🔌 Starting Network Health Dashboard...")
    print(f"Mode: {args.mode.upper()}")
    print("Press Ctrl+C to stop\n")

    try:
        asyncio.run(dashboard.start_dashboard())
    except KeyboardInterrupt:
        print("\n\n🛑 Dashboard stopped")
        monitor.stop_monitoring()


if __name__ == "__main__":



    main()