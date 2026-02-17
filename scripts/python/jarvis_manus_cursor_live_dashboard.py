#!/usr/bin/env python3
"""
JARVIS-MANUS-Cursor Live Dashboard
Keeps Live Tabs on Vital Statistics

Persistent dashboard that continuously monitors and displays vital statistics
for JARVIS full control of Cursor IDE via MANUS.

Tags: #JARVIS #MANUS #CURSOR #DASHBOARD #LIVE #STATISTICS #TABS @JARVIS @TEAM
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISManusCursorLiveDashboard")

try:
    from jarvis_manus_cursor_live_stats import JARVISManusCursorLiveStats, StatCategory
    LIVE_STATS_AVAILABLE = True
except ImportError:
    LIVE_STATS_AVAILABLE = False
    logger.warning("Live Statistics Monitor not available")


class LiveDashboard:
    """
    Live Dashboard with Tabs for Vital Statistics

    Keeps live tabs on all vital statistics with real-time updates.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize live dashboard"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "jarvis_manus_cursor" / "live_dashboard"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize live stats monitor
        self.live_stats = None
        if LIVE_STATS_AVAILABLE:
            try:
                self.live_stats = JARVISManusCursorLiveStats(project_root=self.project_root)
                logger.info("✅ Live Statistics Monitor initialized")
            except Exception as e:
                logger.warning(f"⚠️  Live Statistics initialization failed: {e}")

        # Dashboard state
        self.dashboard_file = self.data_dir / "dashboard.json"
        self.update_interval = 1.0

        logger.info("✅ Live Dashboard initialized")
        logger.info("   Live tabs on vital statistics: Active")

    def display_dashboard(self):
        """Display live dashboard with tabs"""
        if not self.live_stats:
            print("❌ Live Statistics Monitor not available")
            return

        # Update stats
        dashboard = self.live_stats.get_live_dashboard()
        vital_stats = self.live_stats.get_vital_statistics()

        # Save to file
        self._save_dashboard(dashboard)

        # Display with tabs
        print("\n" + "="*80)
        print("📊 JARVIS-MANUS-Cursor Live Dashboard")
        print("   Live Tabs on Vital Statistics")
        print("="*80)
        print(f"🕐 Last Updated: {dashboard['timestamp']}\n")

        # Tab 1: Control Statistics
        print("📋 TAB 1: CONTROL STATISTICS")
        print("-" * 80)
        control_stats = dashboard.get("control_stats", {})
        print(f"   MANUS Available: {'✅' if control_stats.get('manus_available') else '❌'}")
        print(f"   Cursor Controller: {'✅' if control_stats.get('cursor_controller_available') else '❌'}")
        print(f"   Complete IDE Control: {'✅' if control_stats.get('complete_ide_control_available') else '❌'}")
        print(f"   Control Active: {'✅' if control_stats.get('control_active') else '❌'}")
        print(f"   Visibility Active: {'✅' if control_stats.get('visibility_active') else '❌'}")
        print(f"   Smart Mappings: {control_stats.get('total_smart_mappings', 0)}")
        print(f"   Total Features: {control_stats.get('total_features', 0)}\n")

        # Tab 2: Features Statistics
        print("📋 TAB 2: FEATURES STATISTICS")
        print("-" * 80)
        features_stats = dashboard.get("features_stats", {})
        print(f"   Total @FF Features: {features_stats.get('total_features', 0)}")
        print(f"   Enabled: {features_stats.get('enabled_features', 0)}")
        print(f"   Disabled: {features_stats.get('disabled_features', 0)}")
        print(f"   With Smart Mapping: {features_stats.get('features_with_smart_mapping', 0)}")
        features_by_category = features_stats.get("features_by_category", {})
        if features_by_category:
            print("   By Category:")
            for category, count in sorted(features_by_category.items()):
                print(f"      - {category}: {count}")
        print()

        # Tab 3: Visibility Statistics
        print("📋 TAB 3: VISIBILITY STATISTICS")
        print("-" * 80)
        visibility_stats = dashboard.get("visibility_stats", {})
        print(f"   Cursor State: {'✅' if visibility_stats.get('cursor_state_available') else '❌'}")
        print(f"   IDE State: {'✅' if visibility_stats.get('ide_state_available') else '❌'}")
        print(f"   Active File: {visibility_stats.get('active_file', 'N/A')}")
        cursor_pos = visibility_stats.get('cursor_position', (0, 0))
        print(f"   Cursor Position: Line {cursor_pos[0]}, Col {cursor_pos[1]}")
        print(f"   Problems: {visibility_stats.get('problems_count', 0)}")
        print(f"   Windows: {visibility_stats.get('windows_count', 0)}")
        print(f"   Tabs: {visibility_stats.get('tabs_count', 0)}")
        print(f"   Editors: {visibility_stats.get('editors_count', 0)}")
        print(f"   Terminals: {visibility_stats.get('terminals_count', 0)}")
        print(f"   Recent Actions: {visibility_stats.get('recent_actions_count', 0)}\n")

        # Tab 4: Performance Statistics
        print("📋 TAB 4: PERFORMANCE STATISTICS")
        print("-" * 80)
        performance_stats = dashboard.get("performance_stats", {})
        print(f"   Total Actions: {performance_stats.get('total_actions', 0)}")
        print(f"   Success Rate: {performance_stats.get('success_rate', 0):.1f}%")
        print(f"   Successful: {performance_stats.get('successful_actions', 0)}")
        print(f"   Failed: {performance_stats.get('failed_actions', 0)}")
        print(f"   Avg Execution Time: {performance_stats.get('average_execution_time', 0):.3f}s")
        print(f"   Min Execution Time: {performance_stats.get('min_execution_time', 0):.3f}s")
        print(f"   Max Execution Time: {performance_stats.get('max_execution_time', 0):.3f}s")
        print(f"   Last Action Time: {performance_stats.get('last_action_time', 0):.3f}s\n")

        # Tab 5: Actions Statistics
        print("📋 TAB 5: ACTIONS STATISTICS")
        print("-" * 80)
        actions_stats = dashboard.get("actions_stats", {})
        print(f"   Total Actions: {actions_stats.get('total_actions', 0)}")
        methods_used = actions_stats.get("methods_used", {})
        if methods_used:
            print("   Methods Used:")
            for method, count in sorted(methods_used.items(), key=lambda x: x[1], reverse=True):
                print(f"      - {method}: {count}")
        most_common = actions_stats.get("most_common_commands", {})
        if most_common:
            print("   Most Common Commands:")
            for cmd, count in sorted(most_common.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"      - {cmd}: {count}")
        print()

        # Tab 6: System Statistics
        print("📋 TAB 6: SYSTEM STATISTICS")
        print("-" * 80)
        system_stats = dashboard.get("system_stats", {})
        print(f"   CPU Usage: {system_stats.get('cpu_percent', 0):.1f}%")
        print(f"   Memory Usage: {system_stats.get('memory_percent', 0):.1f}%")
        print(f"   Memory Available: {system_stats.get('memory_available_gb', 0):.2f} GB")
        print(f"   Monitoring Active: {'✅' if system_stats.get('monitoring_active') else '❌'}")
        print(f"   Update Interval: {system_stats.get('update_interval', 0)}s")
        print(f"   History Size: {system_stats.get('history_size', 0)}\n")

        # Vital Statistics Summary
        print("⭐ VITAL STATISTICS SUMMARY")
        print("-" * 80)
        for stat in vital_stats:
            status_icon = "✅" if stat["alert_status"] == "normal" else "⚠️" if stat["alert_status"] == "warning" else "❌"
            print(f"{status_icon} {stat['name']}: {stat['value']} {stat['unit']}")
        print()

        print("="*80)
        print("💡 Use --monitor to start continuous live monitoring")
        print("="*80 + "\n")

    def _save_dashboard(self, dashboard: Dict[str, Any]):
        """Save dashboard to file"""
        try:
            with open(self.dashboard_file, 'w', encoding='utf-8') as f:
                json.dump(dashboard, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Failed to save dashboard: {e}")

    def start_live_monitoring(self, interval: float = 1.0):
        """Start live monitoring with continuous updates"""
        if not self.live_stats:
            print("❌ Live Statistics Monitor not available")
            return

        print("\n" + "="*80)
        print("📊 JARVIS-MANUS-Cursor Live Dashboard")
        print("   Live Tabs on Vital Statistics - Continuous Monitoring")
        print("="*80)
        print("🔄 Starting live monitoring...")
        print("   (Press Ctrl+C to stop)\n")

        self.live_stats.update_interval = interval
        self.live_stats.start_monitoring()

        try:
            while True:
                # Clear screen (Windows)
                import os
                os.system('cls' if os.name == 'nt' else 'clear')

                # Display dashboard
                self.display_dashboard()

                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n✅ Monitoring stopped")
            self.live_stats.stop_monitoring()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS-MANUS-Cursor Live Dashboard")
    parser.add_argument("--monitor", action="store_true", help="Start continuous live monitoring")
    parser.add_argument("--interval", type=float, default=1.0, help="Update interval (seconds)")
    parser.add_argument("--dashboard", action="store_true", help="Show current dashboard once")

    args = parser.parse_args()

    dashboard = LiveDashboard()

    if args.monitor:
        dashboard.start_live_monitoring(interval=args.interval)
    else:
        dashboard.display_dashboard()
