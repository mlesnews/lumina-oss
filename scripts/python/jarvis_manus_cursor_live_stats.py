#!/usr/bin/env python3
"""
JARVIS-MANUS-Cursor Live Statistics Monitor
Live Tabs on Vital Statistics

Real-time monitoring dashboard for JARVIS full control of Cursor IDE via MANUS.
Tracks all vital statistics with live updates.

Tags: #JARVIS #MANUS #CURSOR #STATISTICS #MONITORING #LIVE #DASHBOARD @JARVIS @TEAM
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import logging
import threading

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISManusCursorLiveStats")

try:
    from jarvis_manus_cursor_full_control import JARVISManusCursorFullControl
    FULL_CONTROL_AVAILABLE = True
except ImportError:
    FULL_CONTROL_AVAILABLE = False
    logger.warning("JARVIS-MANUS-Cursor Full Control not available")


class StatCategory(Enum):
    """Statistics categories (tabs)"""
    CONTROL = "control"
    FEATURES = "features"
    VISIBILITY = "visibility"
    PERFORMANCE = "performance"
    ACTIONS = "actions"
    SYSTEM = "system"


@dataclass
class VitalStatistic:
    """A vital statistic to monitor"""
    stat_id: str
    name: str
    category: StatCategory
    value: Any
    unit: str = ""
    description: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    trend: str = "stable"  # "increasing", "decreasing", "stable"
    alert_threshold: Optional[float] = None
    alert_status: str = "normal"  # "normal", "warning", "critical"


@dataclass
class LiveStatsDashboard:
    """Live statistics dashboard"""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    control_stats: Dict[str, Any] = field(default_factory=dict)
    features_stats: Dict[str, Any] = field(default_factory=dict)
    visibility_stats: Dict[str, Any] = field(default_factory=dict)
    performance_stats: Dict[str, Any] = field(default_factory=dict)
    actions_stats: Dict[str, Any] = field(default_factory=dict)
    system_stats: Dict[str, Any] = field(default_factory=dict)
    vital_statistics: List[VitalStatistic] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["vital_statistics"] = [asdict(stat) for stat in self.vital_statistics]
        return data


class JARVISManusCursorLiveStats:
    """
    JARVIS-MANUS-Cursor Live Statistics Monitor

    Keeps live tabs on all vital statistics with real-time updates.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize live statistics monitor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "jarvis_manus_cursor" / "live_stats"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize full control system
        self.full_control = None
        if FULL_CONTROL_AVAILABLE:
            try:
                self.full_control = JARVISManusCursorFullControl(project_root=self.project_root)
                logger.info("✅ Full Control System initialized")
            except Exception as e:
                logger.warning(f"⚠️  Full Control initialization failed: {e}")

        # Dashboard state
        self.dashboard = LiveStatsDashboard()
        self.monitoring_active = False
        self.monitor_thread = None
        self.update_interval = 1.0  # Update every second

        # Statistics history
        self.stats_history: List[LiveStatsDashboard] = []
        self.max_history = 1000

        logger.info("✅ JARVIS-MANUS-Cursor Live Statistics Monitor initialized")
        logger.info("   Live tabs on vital statistics: Enabled")

    def start_monitoring(self):
        """Start live monitoring"""
        if self.monitoring_active:
            logger.warning("⚠️  Monitoring already active")
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("✅ Live monitoring started")

    def stop_monitoring(self):
        """Stop live monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
        logger.info("✅ Live monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                self.update_all_stats()
                time.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                time.sleep(self.update_interval)

    def update_all_stats(self):
        """Update all vital statistics"""
        self.dashboard.timestamp = datetime.now().isoformat()

        # Update each category
        self._update_control_stats()
        self._update_features_stats()
        self._update_visibility_stats()
        self._update_performance_stats()
        self._update_actions_stats()
        self._update_system_stats()

        # Collect vital statistics
        self._collect_vital_statistics()

        # Save to history
        self._save_to_history()

        # Save current state
        self._save_current_state()

    def _update_control_stats(self):
        """Update control statistics"""
        stats = {
            "manus_available": self.full_control.manus is not None if self.full_control else False,
            "cursor_controller_available": self.full_control.cursor_controller is not None if self.full_control else False,
            "complete_ide_control_available": self.full_control.complete_ide_control is not None if self.full_control else False,
            "control_active": self.full_control.control_active if self.full_control else False,
            "visibility_active": self.full_control.visibility_active if self.full_control else False,
            "total_smart_mappings": len(self.full_control.smart_keymappings) if self.full_control else 0,
            "total_features": len(self.full_control.ff_features) if self.full_control else 0
        }
        self.dashboard.control_stats = stats

    def _update_features_stats(self):
        """Update features statistics"""
        if not self.full_control:
            self.dashboard.features_stats = {}
            return

        features = self.full_control.ff_features
        stats = {
            "total_features": len(features),
            "enabled_features": sum(1 for f in features.values() if f.enabled),
            "disabled_features": sum(1 for f in features.values() if not f.enabled),
            "features_with_smart_mapping": sum(1 for f in features.values() if f.smart_mapping is not None),
            "features_by_category": {}
        }

        # Count by category
        for feature in features.values():
            category = feature.category.value
            stats["features_by_category"][category] = stats["features_by_category"].get(category, 0) + 1

        self.dashboard.features_stats = stats

    def _update_visibility_stats(self):
        """Update visibility statistics"""
        if not self.full_control:
            self.dashboard.visibility_stats = {}
            return

        try:
            visibility = self.full_control.get_visibility()
            stats = {
                "cursor_state_available": visibility.get("cursor_state") is not None,
                "ide_state_available": visibility.get("ide_state") is not None,
                "active_file": visibility.get("cursor_state", {}).get("active_file", ""),
                "cursor_position": visibility.get("cursor_state", {}).get("cursor_position", (0, 0)),
                "problems_count": len(visibility.get("cursor_state", {}).get("problems", [])),
                "windows_count": visibility.get("ide_state", {}).get("windows", 0),
                "tabs_count": visibility.get("ide_state", {}).get("tabs", 0),
                "editors_count": visibility.get("ide_state", {}).get("editors", 0),
                "terminals_count": visibility.get("ide_state", {}).get("terminals", 0),
                "recent_actions_count": len(visibility.get("recent_actions", []))
            }
            self.dashboard.visibility_stats = stats
        except Exception as e:
            logger.warning(f"Error updating visibility stats: {e}")
            self.dashboard.visibility_stats = {"error": str(e)}

    def _update_performance_stats(self):
        """Update performance statistics"""
        if not self.full_control or not self.full_control.last_action:
            self.dashboard.performance_stats = {}
            return

        actions = self.full_control.action_history
        if actions:
            execution_times = [a.get("execution_time", 0) for a in actions if "execution_time" in a]
            stats = {
                "total_actions": len(actions),
                "average_execution_time": sum(execution_times) / len(execution_times) if execution_times else 0,
                "min_execution_time": min(execution_times) if execution_times else 0,
                "max_execution_time": max(execution_times) if execution_times else 0,
                "last_action_time": actions[-1].get("execution_time", 0) if actions else 0,
                "successful_actions": sum(1 for a in actions if a.get("success", False)),
                "failed_actions": sum(1 for a in actions if not a.get("success", False)),
                "success_rate": (sum(1 for a in actions if a.get("success", False)) / len(actions) * 100) if actions else 0
            }
        else:
            stats = {
                "total_actions": 0,
                "average_execution_time": 0,
                "success_rate": 0
            }

        self.dashboard.performance_stats = stats

    def _update_actions_stats(self):
        """Update actions statistics"""
        if not self.full_control:
            self.dashboard.actions_stats = {}
            return

        actions = self.full_control.action_history
        stats = {
            "total_actions": len(actions),
            "recent_actions": actions[-10:] if actions else [],
            "methods_used": {},
            "most_common_commands": {}
        }

        # Count methods
        for action in actions:
            method = action.get("method", "unknown")
            stats["methods_used"][method] = stats["methods_used"].get(method, 0) + 1

        # Count commands
        for action in actions:
            command = action.get("command", "unknown")
            stats["most_common_commands"][command] = stats["most_common_commands"].get(command, 0) + 1

        self.dashboard.actions_stats = stats

    def _update_system_stats(self):
        """Update system statistics"""
        import psutil

        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()

            stats = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "monitoring_active": self.monitoring_active,
                "update_interval": self.update_interval,
                "history_size": len(self.stats_history)
            }
            self.dashboard.system_stats = stats
        except Exception as e:
            logger.warning(f"Error updating system stats: {e}")
            self.dashboard.system_stats = {"error": str(e)}

    def _collect_vital_statistics(self):
        """Collect all vital statistics"""
        vital_stats = []

        # Control vital stats
        vital_stats.append(VitalStatistic(
            stat_id="manus_control_available",
            name="MANUS Control Available",
            category=StatCategory.CONTROL,
            value=self.dashboard.control_stats.get("manus_available", False),
            unit="boolean",
            description="MANUS unified control system availability"
        ))

        vital_stats.append(VitalStatistic(
            stat_id="total_features",
            name="Total @FF Features",
            category=StatCategory.FEATURES,
            value=self.dashboard.features_stats.get("total_features", 0),
            unit="count",
            description="Total features/functionality available"
        ))

        vital_stats.append(VitalStatistic(
            stat_id="enabled_features",
            name="Enabled Features",
            category=StatCategory.FEATURES,
            value=self.dashboard.features_stats.get("enabled_features", 0),
            unit="count",
            description="Number of enabled features"
        ))

        # Visibility vital stats
        vital_stats.append(VitalStatistic(
            stat_id="cursor_state_available",
            name="Cursor State Available",
            category=StatCategory.VISIBILITY,
            value=self.dashboard.visibility_stats.get("cursor_state_available", False),
            unit="boolean",
            description="Real-time Cursor IDE state visibility"
        ))

        vital_stats.append(VitalStatistic(
            stat_id="active_file",
            name="Active File",
            category=StatCategory.VISIBILITY,
            value=self.dashboard.visibility_stats.get("active_file", ""),
            unit="string",
            description="Currently active file in Cursor IDE"
        ))

        # Performance vital stats
        vital_stats.append(VitalStatistic(
            stat_id="success_rate",
            name="Action Success Rate",
            category=StatCategory.PERFORMANCE,
            value=self.dashboard.performance_stats.get("success_rate", 0),
            unit="percent",
            description="Percentage of successful command executions",
            alert_threshold=95.0,
            alert_status="warning" if self.dashboard.performance_stats.get("success_rate", 100) < 95.0 else "normal"
        ))

        vital_stats.append(VitalStatistic(
            stat_id="average_execution_time",
            name="Average Execution Time",
            category=StatCategory.PERFORMANCE,
            value=self.dashboard.performance_stats.get("average_execution_time", 0),
            unit="seconds",
            description="Average time to execute commands",
            alert_threshold=2.0,
            alert_status="warning" if self.dashboard.performance_stats.get("average_execution_time", 0) > 2.0 else "normal"
        ))

        # Actions vital stats
        vital_stats.append(VitalStatistic(
            stat_id="total_actions",
            name="Total Actions",
            category=StatCategory.ACTIONS,
            value=self.dashboard.actions_stats.get("total_actions", 0),
            unit="count",
            description="Total number of commands executed"
        ))

        # System vital stats
        vital_stats.append(VitalStatistic(
            stat_id="cpu_usage",
            name="CPU Usage",
            category=StatCategory.SYSTEM,
            value=self.dashboard.system_stats.get("cpu_percent", 0),
            unit="percent",
            description="System CPU usage",
            alert_threshold=80.0,
            alert_status="warning" if self.dashboard.system_stats.get("cpu_percent", 0) > 80.0 else "normal"
        ))

        vital_stats.append(VitalStatistic(
            stat_id="memory_usage",
            name="Memory Usage",
            category=StatCategory.SYSTEM,
            value=self.dashboard.system_stats.get("memory_percent", 0),
            unit="percent",
            description="System memory usage",
            alert_threshold=85.0,
            alert_status="warning" if self.dashboard.system_stats.get("memory_percent", 0) > 85.0 else "normal"
        ))

        self.dashboard.vital_statistics = vital_stats

    def _save_to_history(self):
        """Save current dashboard to history"""
        self.stats_history.append(self.dashboard)
        if len(self.stats_history) > self.max_history:
            self.stats_history.pop(0)

    def _save_current_state(self):
        """Save current state to file"""
        try:
            state_file = self.data_dir / "current_state.json"
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(self.dashboard.to_dict(), f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Failed to save current state: {e}")

    def get_live_dashboard(self) -> Dict[str, Any]:
        """Get current live dashboard"""
        self.update_all_stats()
        return self.dashboard.to_dict()

    def get_vital_statistics(self) -> List[Dict[str, Any]]:
        """Get all vital statistics"""
        self.update_all_stats()
        return [asdict(stat) for stat in self.dashboard.vital_statistics]

    def get_stats_by_category(self, category: StatCategory) -> Dict[str, Any]:
        """Get statistics for a specific category"""
        self.update_all_stats()

        category_map = {
            StatCategory.CONTROL: self.dashboard.control_stats,
            StatCategory.FEATURES: self.dashboard.features_stats,
            StatCategory.VISIBILITY: self.dashboard.visibility_stats,
            StatCategory.PERFORMANCE: self.dashboard.performance_stats,
            StatCategory.ACTIONS: self.dashboard.actions_stats,
            StatCategory.SYSTEM: self.dashboard.system_stats
        }

        return {
            "category": category.value,
            "timestamp": self.dashboard.timestamp,
            "stats": category_map.get(category, {}),
            "vital_stats": [
                asdict(stat) for stat in self.dashboard.vital_statistics
                if stat.category == category
            ]
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS-MANUS-Cursor Live Statistics Monitor")
    parser.add_argument("--monitor", action="store_true", help="Start live monitoring")
    parser.add_argument("--dashboard", action="store_true", help="Show current dashboard")
    parser.add_argument("--vital", action="store_true", help="Show vital statistics")
    parser.add_argument("--category", type=str, choices=["control", "features", "visibility", "performance", "actions", "system"], help="Show specific category")
    parser.add_argument("--interval", type=float, default=1.0, help="Update interval (seconds)")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("📊 JARVIS-MANUS-Cursor Live Statistics Monitor")
    print("   Live Tabs on Vital Statistics")
    print("="*80 + "\n")

    monitor = JARVISManusCursorLiveStats()
    monitor.update_interval = args.interval

    if args.monitor:
        print("🔄 Starting live monitoring...")
        print("   (Press Ctrl+C to stop)\n")
        monitor.start_monitoring()
        try:
            while True:
                dashboard = monitor.get_live_dashboard()
                print(f"\r📊 Dashboard Updated: {dashboard['timestamp']}", end="", flush=True)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n\n✅ Monitoring stopped")
            monitor.stop_monitoring()

    elif args.vital:
        vital_stats = monitor.get_vital_statistics()
        print("📊 VITAL STATISTICS")
        print("="*80)
        for stat in vital_stats:
            status_icon = "✅" if stat["alert_status"] == "normal" else "⚠️" if stat["alert_status"] == "warning" else "❌"
            print(f"{status_icon} {stat['name']}: {stat['value']} {stat['unit']}")
            if stat.get("description"):
                print(f"   {stat['description']}")
        print("="*80 + "\n")

    elif args.category:
        category = StatCategory(args.category)
        stats = monitor.get_stats_by_category(category)
        print(f"📊 {category.value.upper()} STATISTICS")
        print("="*80)
        print(json.dumps(stats, indent=2, default=str))
        print("="*80 + "\n")

    elif args.dashboard:
        dashboard = monitor.get_live_dashboard()
        print("📊 LIVE DASHBOARD")
        print("="*80)
        print(json.dumps(dashboard, indent=2, default=str))
        print("="*80 + "\n")

    else:
        print("Use --monitor to start live monitoring")
        print("Use --dashboard to show current dashboard")
        print("Use --vital to show vital statistics")
        print("Use --category to show specific category")
        print("="*80 + "\n")
