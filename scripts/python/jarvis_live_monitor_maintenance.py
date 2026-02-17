#!/usr/bin/env python3
"""
JARVIS Live Monitor & Maintenance System

Provides progressive percentage tracking and ongoing live monitoring/maintenance.
Continuously monitors system health, process progress, and performs maintenance tasks.

@JARVIS @LIVE @MONITORING @MAINTENANCE #PROGRESSIVE #PERCENTAGE #TRACKING
"""

import json
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
import logging

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISLiveMonitor")


@dataclass
class SystemHealth:
    """System health metrics"""
    overall_health_percent: float = 100.0
    processes_running: int = 0
    processes_completed: int = 0
    processes_failed: int = 0
    memory_usage_percent: float = 0.0
    cpu_usage_percent: float = 0.0
    last_update: datetime = field(default_factory=datetime.now)
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class ProgressivePercentage:
    """Progressive percentage tracking"""
    overall: float = 0.0
    active_processes: int = 0
    total_sources: int = 0
    current_sources: int = 0
    eta: str = "Calculating..."
    last_update: datetime = field(default_factory=datetime.now)
    breakdown: Dict[str, float] = field(default_factory=dict)  # Process-specific percentages


class JARVISLiveMonitor:
    """
    Live Monitor & Maintenance System

    Provides:
    - Progressive percentage tracking
    - Ongoing live monitoring
    - Continuous maintenance
    - System health monitoring
    """

    def __init__(self, project_root: Optional[Path] = None, update_interval: float = 0.5):
        """Initialize live monitor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)

        self.update_interval = update_interval  # Update every 0.5 seconds for live monitoring
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None

        # Data storage
        self.data_dir = self.project_root / "data" / "progress_tracking"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.status_file = self.data_dir / "live_monitor_status.json"
        self.cursor_status_file = self.data_dir / "cursor_status.json"  # For Cursor IDE extension

        # State
        self.system_health = SystemHealth()
        self.progressive_percentage = ProgressivePercentage()

        # Maintenance tasks
        self.maintenance_tasks: List[Dict[str, Any]] = []
        self._initialize_maintenance_tasks()

        # Progress tracker integration
        try:
            from jarvis_progress_tracker import get_progress_tracker
            self.progress_tracker = get_progress_tracker(project_root=self.project_root, mode="bau")
        except Exception as e:
            logger.warning(f"⚠️  Progress tracker not available: {e}")
            self.progress_tracker = None

        logger.info("✅ JARVIS Live Monitor initialized")
        logger.info(f"   Update interval: {self.update_interval}s")

    def _initialize_maintenance_tasks(self):
        """Initialize maintenance tasks"""
        self.maintenance_tasks = [
            {
                "id": "health_check",
                "name": "System Health Check",
                "interval": 5.0,  # Every 5 seconds
                "last_run": None,
                "enabled": True
            },
            {
                "id": "progress_update",
                "name": "Progress Update",
                "interval": 0.5,  # Every 0.5 seconds
                "last_run": None,
                "enabled": True
            },
            {
                "id": "status_file_write",
                "name": "Status File Write",
                "interval": 1.0,  # Every 1 second
                "last_run": None,
                "enabled": True
            },
            {
                "id": "cleanup_old_data",
                "name": "Cleanup Old Data",
                "interval": 300.0,  # Every 5 minutes
                "last_run": None,
                "enabled": True
            }
        ]
        logger.info(f"✅ Initialized {len(self.maintenance_tasks)} maintenance tasks")

    def start_monitoring(self):
        """Start live monitoring"""
        if self.monitoring_active:
            logger.warning("⚠️  Monitoring already active")
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("✅ Live monitoring started (update interval: 0.5s) - LIVE MONITORING")
        logger.info("✅ Maintenance tasks started")
        logger.info("✅ Live monitoring active")

    def stop_monitoring(self):
        """Stop live monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        logger.info("⏹️  Live monitoring stopped")

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Run maintenance tasks
                self._run_maintenance_tasks()

                # Update system health
                self._update_system_health()

                # Update progressive percentage
                self._update_progressive_percentage()

                # Write status file
                self._write_status_file()

                # Sleep for update interval
                time.sleep(self.update_interval)

            except Exception as e:
                logger.error(f"Error in monitor loop: {e}", exc_info=True)
                time.sleep(self.update_interval)

    def _run_maintenance_tasks(self):
        """Run scheduled maintenance tasks"""
        now = datetime.now()

        for task in self.maintenance_tasks:
            if not task.get("enabled", True):
                continue

            last_run = task.get("last_run")
            interval = task.get("interval", 1.0)

            # Check if task should run
            if last_run is None or (now - last_run).total_seconds() >= interval:
                try:
                    task_id = task.get("id")

                    if task_id == "health_check":
                        self._maintenance_health_check()
                    elif task_id == "progress_update":
                        self._maintenance_progress_update()
                    elif task_id == "status_file_write":
                        self._maintenance_status_file_write()
                    elif task_id == "cleanup_old_data":
                        self._maintenance_cleanup_old_data()

                    task["last_run"] = now

                except Exception as e:
                    logger.warning(f"Maintenance task {task.get('name')} failed: {e}")

    def _maintenance_health_check(self):
        """Maintenance: System health check"""
        # Check progress tracker health
        if self.progress_tracker:
            try:
                status = self.progress_tracker.get_status()
                processes = status.get("processes", {})

                running = sum(1 for p in processes.values() if p.get("status") == "running")
                completed = sum(1 for p in processes.values() if p.get("status") == "completed")
                failed = sum(1 for p in processes.values() if p.get("status") == "failed")

                self.system_health.processes_running = running
                self.system_health.processes_completed = completed
                self.system_health.processes_failed = failed

            except Exception as e:
                logger.debug(f"Health check error: {e}")

    def _maintenance_progress_update(self):
        """Maintenance: Update progress"""
        if self.progress_tracker:
            try:
                status = self.progress_tracker.get_status()
                self._calculate_progressive_percentage(status)
            except Exception as e:
                logger.debug(f"Progress update error: {e}")

    def _maintenance_status_file_write(self):
        """Maintenance: Write status file"""
        self._write_status_file()

    def _maintenance_cleanup_old_data(self):
        """Maintenance: Cleanup old data"""
        try:
            # Cleanup old status files (older than 24 hours)
            cutoff = datetime.now() - timedelta(hours=24)

            status_dir = self.data_dir
            if status_dir.exists():
                for file in status_dir.glob("*.json"):
                    try:
                        if file.stat().st_mtime < cutoff.timestamp():
                            file.unlink()
                            logger.debug(f"Cleaned up old file: {file.name}")
                    except Exception:
                        pass
        except Exception as e:
            logger.debug(f"Cleanup error: {e}")

    def _update_system_health(self):
        """Update system health metrics"""
        self.system_health.last_update = datetime.now()

        # Calculate overall health
        total = self.system_health.processes_running + self.system_health.processes_completed + self.system_health.processes_failed
        if total > 0:
            success_rate = self.system_health.processes_completed / total
            failure_rate = self.system_health.processes_failed / total
            self.system_health.overall_health_percent = (success_rate * 100.0) - (failure_rate * 50.0)
            self.system_health.overall_health_percent = max(0.0, min(100.0, self.system_health.overall_health_percent))
        else:
            self.system_health.overall_health_percent = 100.0

    def _update_progressive_percentage(self):
        """Update progressive percentage"""
        self.progressive_percentage.last_update = datetime.now()

    def _calculate_progressive_percentage(self, status: Dict[str, Any]):
        """Calculate progressive percentage from status"""
        processes = status.get("processes", {})

        if not processes:
            self.progressive_percentage.overall = 0.0
            self.progressive_percentage.active_processes = 0
            self.progressive_percentage.total_sources = 0
            self.progressive_percentage.current_sources = 0
            return

        # Calculate overall percentage
        total_percentage = 0.0
        active_count = 0
        total_sources = 0
        current_sources = 0

        breakdown = {}

        for process_id, process_data in processes.items():
            if process_data.get("status") == "running":
                active_count += 1
                percentage = process_data.get("progress_percentage", 0.0)
                total_percentage += percentage
                breakdown[process_id] = percentage

                # Get source counts
                total_sources += process_data.get("total_items", 0)
                current_sources += process_data.get("completed_items", 0)

        if active_count > 0:
            self.progressive_percentage.overall = total_percentage / active_count
        else:
            self.progressive_percentage.overall = 0.0

        self.progressive_percentage.active_processes = active_count
        self.progressive_percentage.total_sources = total_sources
        self.progressive_percentage.current_sources = current_sources
        self.progressive_percentage.breakdown = breakdown

        # Calculate ETA
        if self.progress_tracker:
            try:
                aggregate = self.progress_tracker.get_aggregate_status()
                eta = aggregate.get("eta", "Calculating...")
                self.progressive_percentage.eta = eta
            except Exception:
                self.progressive_percentage.eta = "Calculating..."

    def _write_status_file(self):
        """Write status to file for extension to read"""
        try:
            # Internal status file
            status_data = {
                "timestamp": datetime.now().isoformat(),
                "monitoring_active": self.monitoring_active,
                "progressive_percentage": {
                    "overall": self.progressive_percentage.overall,
                    "active_processes": self.progressive_percentage.active_processes,
                    "total_sources": self.progressive_percentage.total_sources,
                    "current_sources": self.progressive_percentage.current_sources,
                    "eta": self.progressive_percentage.eta,
                    "breakdown": self.progressive_percentage.breakdown
                },
                "system_health": {
                    "overall_health_percent": self.system_health.overall_health_percent,
                    "processes_running": self.system_health.processes_running,
                    "processes_completed": self.system_health.processes_completed,
                    "processes_failed": self.system_health.processes_failed,
                    "issues": self.system_health.issues,
                    "warnings": self.system_health.warnings
                }
            }

            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, indent=2, default=str)

            # Cursor IDE extension status file (enhanced with progressive percentage)
            if self.progress_tracker:
                try:
                    # Get progress tracker status
                    tracker_status = self.progress_tracker.get_status()
                    aggregate = tracker_status.get("aggregate", {})
                    processes = tracker_status.get("processes", {})

                    # Build signboard text with progressive percentage
                    pp = self.progressive_percentage
                    signboard_parts = []
                    if pp.overall > 0:
                        signboard_parts.append(f"JARVIS: {pp.overall:.1f}%")
                    if pp.active_processes > 0:
                        signboard_parts.append(f"{pp.active_processes} active")
                    if pp.total_sources > 0:
                        signboard_parts.append(f"{pp.current_sources}/{pp.total_sources} sources")
                    if pp.eta and pp.eta != "Calculating...":
                        signboard_parts.append(f"ETA: {pp.eta}")

                    signboard_text = " | ".join(signboard_parts) if signboard_parts else "JARVIS: Monitoring..."

                    # Enhanced cursor status with progressive percentage
                    cursor_status = {
                        "timestamp": datetime.now().isoformat(),
                        "monitoring_active": self.monitoring_active,
                        "aggregate": {
                            "overall_percentage": pp.overall,
                            "max_sources_processing": pp.current_sources,
                            "total_sources": pp.total_sources,
                            "active_processes": pp.active_processes,
                            "eta": pp.eta,
                            "total_completed": sum(p.get("completed_items", 0) for p in processes.values()),
                            "total_items": sum(p.get("total_items", 0) for p in processes.values()),
                            "progressive_percentage": pp.overall  # Progressive tracking
                        },
                        "progressive": {
                            "overall": pp.overall,
                            "active_processes": pp.active_processes,
                            "total_sources": pp.total_sources,
                            "current_sources": pp.current_sources,
                            "eta": pp.eta,
                            "breakdown": pp.breakdown,
                            "system_health": self.system_health.overall_health_percent
                        },
                        "system_health": {
                            "overall_health_percent": self.system_health.overall_health_percent,
                            "processes_running": self.system_health.processes_running,
                            "processes_completed": self.system_health.processes_completed,
                            "processes_failed": self.system_health.processes_failed
                        },
                        "signboard_text": signboard_text,
                        "expanded_text": f"JARVIS Live Monitor | Progress: {pp.overall:.1f}% | Health: {self.system_health.overall_health_percent:.1f}% | {pp.active_processes} active processes",
                        "compact": True,
                        "mode": "bau",
                        "is_lumina_core": True,
                        "is_bau": True,
                        "processes": [
                            {
                                "id": pid,
                                "name": p.get("process_name", "Unknown"),
                                "source": p.get("source_name", "Unknown"),
                                "progress": p.get("progress_percentage", 0.0),
                                "eta": p.get("eta_string", "Calculating..."),
                                "agent_type": p.get("agent_type", "jarvis")
                            }
                            for pid, p in processes.items()
                            if p.get("status") == "running"
                        ]
                    }

                    with open(self.cursor_status_file, 'w', encoding='utf-8') as f:
                        json.dump(cursor_status, f, indent=2, default=str)

                except Exception as e:
                    logger.debug(f"Cursor status file write error: {e}")

        except Exception as e:
            logger.debug(f"Status file write error: {e}")

    def get_live_status(self) -> Dict[str, Any]:
        """Get current live status"""
        return {
            "monitoring_active": self.monitoring_active,
            "progressive_percentage": asdict(self.progressive_percentage),
            "system_health": asdict(self.system_health),
            "maintenance_tasks": [
                {
                    "id": t["id"],
                    "name": t["name"],
                    "enabled": t.get("enabled", True),
                    "last_run": t.get("last_run").isoformat() if t.get("last_run") else None
                }
                for t in self.maintenance_tasks
            ]
        }


# Global instance
_global_live_monitor: Optional[JARVISLiveMonitor] = None


def get_live_monitor(project_root: Optional[Path] = None, update_interval: float = 0.5) -> JARVISLiveMonitor:
    """Get or create global live monitor instance"""
    global _global_live_monitor

    if _global_live_monitor is None:
        _global_live_monitor = JARVISLiveMonitor(project_root=project_root, update_interval=update_interval)

    return _global_live_monitor


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Live Monitor & Maintenance")
    parser.add_argument("--start", action="store_true", help="Start monitoring")
    parser.add_argument("--stop", action="store_true", help="Stop monitoring")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--interval", type=float, default=0.5, help="Update interval in seconds")

    args = parser.parse_args()

    monitor = get_live_monitor(update_interval=args.interval)

    if args.start:
        monitor.start_monitoring()
        print("✅ Live monitoring started")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            monitor.stop_monitoring()
            print("\n⏹️  Live monitoring stopped")

    elif args.stop:
        monitor.stop_monitoring()
        print("⏹️  Live monitoring stopped")

    elif args.status:
        status = monitor.get_live_status()
        print("\n" + "=" * 80)
        print("📊 JARVIS LIVE MONITOR STATUS")
        print("=" * 80)
        print(f"Monitoring Active: {status['monitoring_active']}")
        print(f"\nProgressive Percentage:")
        pp = status['progressive_percentage']
        print(f"   Overall: {pp['overall']:.1f}%")
        print(f"   Active Processes: {pp['active_processes']}")
        print(f"   Total Sources: {pp['total_sources']}")
        print(f"   Current Sources: {pp['current_sources']}")
        print(f"   ETA: {pp['eta']}")
        print(f"\nSystem Health:")
        sh = status['system_health']
        print(f"   Overall Health: {sh['overall_health_percent']:.1f}%")
        print(f"   Processes Running: {sh['processes_running']}")
        print(f"   Processes Completed: {sh['processes_completed']}")
        print(f"   Processes Failed: {sh['processes_failed']}")
        print("=" * 80)

    else:
        parser.print_help()


if __name__ == "__main__":


    main()