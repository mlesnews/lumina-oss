#!/usr/bin/env python3
"""
Unified Monitoring System - Main Monitor

Plugin-based architecture for all monitoring operations.
Consolidates all monitoring scripts into a single unified system.

Tags: #MONITORING #UNIFIED #PLUGIN @JARVIS @LUMINA
"""

import sys
import threading
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("UnifiedMonitor")


class MonitorType(Enum):
    """Types of monitoring available"""
    SYSTEM_HEALTH = "system_health"
    AI_USAGE = "ai_usage"
    LOGS = "logs"
    HVAC = "hvac"
    NETWORK = "network"
    PERFORMANCE = "performance"
    FILE_CHANGES = "file_changes"
    THREAT = "threat"
    MIGRATION = "migration"
    FLOW_RATE = "flow_rate"
    HEARTBEAT = "heartbeat"
    OTHER = "other"


@dataclass
class MonitorResult:
    """Result of a monitoring operation"""
    monitor_type: MonitorType
    status: str  # "healthy", "warning", "critical", "unknown"
    message: str
    metrics: Dict[str, Any] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.metrics is None:
            self.metrics = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()


class MonitorPlugin:
    """Base class for monitor plugins"""

    def __init__(self, monitor_type: MonitorType, name: str, description: str):
        self.monitor_type = monitor_type
        self.name = name
        self.description = description
        self.running = False
        self.thread = None

    def start(self, **kwargs) -> bool:
        """Start monitoring"""
        if self.running:
            return False

        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, kwargs=kwargs, daemon=True)
        self.thread.start()
        return True

    def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)

    def _monitor_loop(self, **kwargs):
        """Internal monitoring loop"""
        while self.running:
            try:
                self.monitor(**kwargs)
            except Exception as e:
                logger.error(f"Monitor {self.name} error: {e}")
            time.sleep(self.get_interval())

    def monitor(self, **kwargs) -> MonitorResult:
        """Execute monitoring check"""
        raise NotImplementedError("Subclasses must implement monitor()")

    def get_interval(self) -> float:
        """Get monitoring interval in seconds"""
        return 60.0  # Default 1 minute

    def get_status(self) -> MonitorResult:
        """Get current status"""
        raise NotImplementedError("Subclasses must implement get_status()")


class UnifiedMonitor:
    """
    Unified Monitoring System

    Consolidates all monitoring scripts into a single plugin-based system.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize unified monitor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.plugins: Dict[MonitorType, List[MonitorPlugin]] = {}
        self.active_monitors: Dict[str, MonitorPlugin] = {}
        self.monitor_history: List[MonitorResult] = []

        logger.info("📊 Unified Monitoring System initialized")

    def register_plugin(self, plugin: MonitorPlugin):
        """Register a monitor plugin"""
        if plugin.monitor_type not in self.plugins:
            self.plugins[plugin.monitor_type] = []

        self.plugins[plugin.monitor_type].append(plugin)
        logger.debug(f"   Registered plugin: {plugin.name} ({plugin.monitor_type.value})")

    def list_monitors(self) -> Dict[str, List[str]]:
        """List all available monitors"""
        monitors = {}
        for monitor_type, plugins in self.plugins.items():
            monitors[monitor_type.value] = [p.name for p in plugins]
        return monitors

    def start_monitor(self, monitor_type: MonitorType, **kwargs) -> bool:
        """Start a monitor by type"""
        if monitor_type not in self.plugins:
            logger.error(f"No plugins registered for {monitor_type.value}")
            return False

        # Start first available plugin for this type
        for plugin in self.plugins[monitor_type]:
            if plugin.start(**kwargs):
                self.active_monitors[f"{monitor_type.value}_{plugin.name}"] = plugin
                logger.info(f"📊 Started monitor: {plugin.name}")
                return True

        return False

    def stop_monitor(self, monitor_type: MonitorType):
        """Stop a monitor by type"""
        keys_to_remove = []
        for key, plugin in self.active_monitors.items():
            if plugin.monitor_type == monitor_type:
                plugin.stop()
                keys_to_remove.append(key)
                logger.info(f"🛑 Stopped monitor: {plugin.name}")

        for key in keys_to_remove:
            del self.active_monitors[key]

    def stop_all(self):
        """Stop all active monitors"""
        for plugin in self.active_monitors.values():
            plugin.stop()
        self.active_monitors.clear()
        logger.info("🛑 Stopped all monitors")

    def get_status(self, monitor_type: Optional[MonitorType] = None) -> Dict[str, MonitorResult]:
        """Get status of monitors"""
        results = {}

        if monitor_type:
            # Get status for specific type
            if monitor_type in self.plugins:
                for plugin in self.plugins[monitor_type]:
                    try:
                        result = plugin.get_status()
                        results[f"{monitor_type.value}_{plugin.name}"] = result
                    except Exception as e:
                        logger.error(f"Error getting status for {plugin.name}: {e}")
        else:
            # Get status for all active monitors
            for key, plugin in self.active_monitors.items():
                try:
                    result = plugin.get_status()
                    results[key] = result
                except Exception as e:
                    logger.error(f"Error getting status for {key}: {e}")

        return results

    def check_all(self) -> Dict[str, MonitorResult]:
        """Check all registered monitors (one-time check)"""
        results = {}

        for monitor_type, plugins in self.plugins.items():
            for plugin in plugins:
                try:
                    result = plugin.monitor()
                    results[f"{monitor_type.value}_{plugin.name}"] = result
                    self.monitor_history.append(result)
                except Exception as e:
                    logger.error(f"Error checking {plugin.name}: {e}")

        return results


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Unified Monitoring System")
    parser.add_argument("--type", type=str, help="Monitor type to start")
    parser.add_argument("--list", action="store_true", help="List all available monitors")
    parser.add_argument("--start", type=str, help="Start a monitor by type")
    parser.add_argument("--stop", type=str, help="Stop a monitor by type")
    parser.add_argument("--stop-all", action="store_true", help="Stop all monitors")
    parser.add_argument("--status", type=str, nargs="?", const="all", help="Get monitor status")
    parser.add_argument("--check", action="store_true", help="Check all monitors (one-time)")

    args = parser.parse_args()

    # Initialize monitor
    monitor = UnifiedMonitor()

    # Register all plugins
    try:
        from .plugins import register_all_plugins
    except ImportError:
        from monitoring.plugins import register_all_plugins
    register_all_plugins(monitor)

    if args.list:
        print("=" * 80)
        print("📊 AVAILABLE MONITORS")
        print("=" * 80)
        monitors = monitor.list_monitors()
        for monitor_type, plugins in monitors.items():
            print(f"\n{monitor_type}:")
            for plugin in plugins:
                print(f"   - {plugin}")

    elif args.start:
        try:
            monitor_type = MonitorType(args.start)
            if monitor.start_monitor(monitor_type):
                print(f"✅ Started monitor: {monitor_type.value}")
            else:
                print(f"❌ Failed to start monitor: {monitor_type.value}")
        except ValueError:
            print(f"❌ Unknown monitor type: {args.start}")
            print(f"Available types: {[t.value for t in MonitorType]}")

    elif args.stop:
        try:
            monitor_type = MonitorType(args.stop)
            monitor.stop_monitor(monitor_type)
            print(f"✅ Stopped monitor: {monitor_type.value}")
        except ValueError:
            print(f"❌ Unknown monitor type: {args.stop}")

    elif args.stop_all:
        monitor.stop_all()
        print("✅ Stopped all monitors")

    elif args.status:
        if args.status == "all":
            results = monitor.get_status()
        else:
            try:
                monitor_type = MonitorType(args.status)
                results = monitor.get_status(monitor_type)
            except ValueError:
                print(f"❌ Unknown monitor type: {args.status}")
                return

        print("=" * 80)
        print("📊 MONITOR STATUS")
        print("=" * 80)
        for key, result in results.items():
            status_icon = {
                "healthy": "✅",
                "warning": "⚠️",
                "critical": "❌",
                "unknown": "❓"
            }.get(result.status, "❓")
            print(f"{status_icon} {key}: {result.message}")
            if result.metrics:
                for metric, value in result.metrics.items():
                    print(f"   {metric}: {value}")

    elif args.check:
        print("=" * 80)
        print("🔍 CHECKING ALL MONITORS")
        print("=" * 80)
        results = monitor.check_all()
        for key, result in results.items():
            status_icon = {
                "healthy": "✅",
                "warning": "⚠️",
                "critical": "❌",
                "unknown": "❓"
            }.get(result.status, "❓")
            print(f"{status_icon} {key}: {result.message}")

    else:
        parser.print_help()


if __name__ == "__main__":


    main()