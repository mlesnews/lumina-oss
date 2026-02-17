#!/usr/bin/env python3
"""
JARVIS Startup/Shutdown Performance Tracker

Comprehensive tracing, capture, and tracking for performance tuning of optimal startup and shutdown procedures.
Tracks all items in a staggered parallel manner for fastest startup without severely taxing system resources.

Tags: #PERFORMANCE #TRACKING #STARTUP #SHUTDOWN #OPTIMIZATION #STAGGERED #PARALLEL @JARVIS @LUMINA
"""

import sys
import json
import time
import psutil
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVISStartupPerf")
except ImportError:
    try:
        from lumina_logger import get_logger
        logger = get_logger("JARVISStartupPerf")
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("JARVISStartupPerf")


class PhaseType(Enum):
    """Performance tracking phases"""
    STARTUP = "startup"
    SHUTDOWN = "shutdown"
    SYSTEM_REBOOT = "system_reboot"


class ResourceMetric(Enum):
    """Resource metrics to track"""
    CPU_PERCENT = "cpu_percent"
    MEMORY_PERCENT = "memory_percent"
    MEMORY_AVAILABLE = "memory_available"
    DISK_IO_READ = "disk_io_read"
    DISK_IO_WRITE = "disk_io_write"
    NETWORK_BYTES_SENT = "network_bytes_sent"
    NETWORK_BYTES_RECV = "network_bytes_recv"
    PROCESS_COUNT = "process_count"
    THREAD_COUNT = "thread_count"


@dataclass
class PerformanceSnapshot:
    """Single performance snapshot"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_bytes_sent_mb: float
    network_bytes_recv_mb: float
    process_count: int
    thread_count: int


@dataclass
class ItemPerformance:
    """Performance metrics for a single startup item"""
    item_id: str
    item_name: str
    start_time: float
    end_time: Optional[float]
    duration_seconds: Optional[float]
    cpu_peak_percent: float
    cpu_avg_percent: float
    memory_peak_percent: float
    memory_avg_percent: float
    memory_delta_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_bytes_sent_mb: float
    network_bytes_recv_mb: float
    success: bool
    error: Optional[str]
    snapshots: List[Dict[str, Any]]


@dataclass
class StartupPerformanceReport:
    """Complete startup performance report"""
    phase: str
    start_time: float
    end_time: Optional[float]
    total_duration_seconds: Optional[float]
    items: List[Dict[str, Any]]
    system_resources: Dict[str, Any]
    parallel_groups: List[Dict[str, Any]]
    optimization_recommendations: List[str]


class StartupPerformanceTracker:
    """Comprehensive startup/shutdown performance tracker"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "startup_performance"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.tracking_file = self.data_dir / "performance_tracking.jsonl"
        self.reports_dir = self.data_dir / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        self.current_phase: Optional[PhaseType] = None
        self.phase_start_time: Optional[float] = None
        self.items_tracking: Dict[str, ItemPerformance] = {}
        self.snapshots: List[PerformanceSnapshot] = []
        self.snapshot_interval = 0.5  # Take snapshot every 0.5 seconds
        self.snapshot_thread: Optional[threading.Thread] = None
        self.snapshot_active = False

        # Resource thresholds for optimization
        self.max_cpu_percent = 80.0
        self.max_memory_percent = 85.0
        self.optimal_parallel_items = 4  # Start with 4 parallel items

    def start_phase(self, phase: PhaseType) -> str:
        """Start tracking a phase (startup/shutdown/reboot)"""
        self.current_phase = phase
        self.phase_start_time = time.time()
        self.items_tracking = {}
        self.snapshots = []

        # Start snapshot thread
        self.snapshot_active = True
        self.snapshot_thread = threading.Thread(target=self._snapshot_loop, daemon=True)
        self.snapshot_thread.start()

        phase_id = f"{phase.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        logger.info("=" * 80)
        logger.info(f"📊 STARTING PERFORMANCE TRACKING: {phase.value.upper()}")
        logger.info("=" * 80)
        logger.info(f"Phase ID: {phase_id}")
        logger.info(f"Start Time: {datetime.now().isoformat()}")
        logger.info("=" * 80)

        return phase_id

    def stop_phase(self) -> Dict[str, Any]:
        try:
            """Stop tracking current phase and generate report"""
            if not self.current_phase:
                return {}

            phase_end_time = time.time()
            total_duration = phase_end_time - self.phase_start_time if self.phase_start_time else None

            # Stop snapshot thread
            self.snapshot_active = False
            if self.snapshot_thread:
                self.snapshot_thread.join(timeout=2)

            # Generate report
            report = self._generate_report(phase_end_time, total_duration)

            # Save report
            report_file = self.reports_dir / f"{self.current_phase.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)

            # Log to tracking file
            tracking_entry = {
                "timestamp": datetime.now().isoformat(),
                "phase": self.current_phase.value,
                "duration_seconds": total_duration,
                "items_count": len(self.items_tracking),
                "report_file": str(report_file)
            }
            with open(self.tracking_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(tracking_entry) + '\n')

            logger.info("=" * 80)
            logger.info(f"📊 PERFORMANCE TRACKING COMPLETE: {self.current_phase.value.upper()}")
            logger.info("=" * 80)
            logger.info(f"Total Duration: {total_duration:.2f} seconds" if total_duration else "N/A")
            logger.info(f"Items Tracked: {len(self.items_tracking)}")
            logger.info(f"Report Saved: {report_file}")
            logger.info("=" * 80)

            # Reset
            phase = self.current_phase
            self.current_phase = None
            self.phase_start_time = None

            return report

        except Exception as e:
            self.logger.error(f"Error in stop_phase: {e}", exc_info=True)
            raise
    def start_item(self, item_id: str, item_name: str) -> None:
        """Start tracking a startup item"""
        start_time = time.time()
        initial_snapshot = self._take_snapshot()

        item_perf = ItemPerformance(
            item_id=item_id,
            item_name=item_name,
            start_time=start_time,
            end_time=None,
            duration_seconds=None,
            cpu_peak_percent=initial_snapshot.cpu_percent,
            cpu_avg_percent=initial_snapshot.cpu_percent,
            memory_peak_percent=initial_snapshot.memory_percent,
            memory_avg_percent=initial_snapshot.memory_percent,
            memory_delta_mb=0.0,
            disk_io_read_mb=initial_snapshot.disk_io_read_mb,
            disk_io_write_mb=initial_snapshot.disk_io_write_mb,
            network_bytes_sent_mb=initial_snapshot.network_bytes_sent_mb,
            network_bytes_recv_mb=initial_snapshot.network_bytes_recv_mb,
            success=False,
            error=None,
            snapshots=[asdict(initial_snapshot)]
        )

        self.items_tracking[item_id] = item_perf

        logger.info(f"📈 Started tracking: {item_name} ({item_id})")

    def update_item(self, item_id: str, snapshot: Optional[PerformanceSnapshot] = None) -> None:
        """Update item tracking with current snapshot"""
        if item_id not in self.items_tracking:
            return

        if snapshot is None:
            snapshot = self._take_snapshot()

        item = self.items_tracking[item_id]
        item.snapshots.append(asdict(snapshot))

        # Update metrics
        item.cpu_peak_percent = max(item.cpu_peak_percent, snapshot.cpu_percent)
        item.memory_peak_percent = max(item.memory_peak_percent, snapshot.memory_percent)

        # Calculate averages
        cpu_values = [s['cpu_percent'] for s in item.snapshots]
        memory_values = [s['memory_percent'] for s in item.snapshots]
        item.cpu_avg_percent = sum(cpu_values) / len(cpu_values) if cpu_values else 0
        item.memory_avg_percent = sum(memory_values) / len(memory_values) if memory_values else 0

    def end_item(self, item_id: str, success: bool = True, error: Optional[str] = None) -> None:
        """End tracking a startup item"""
        if item_id not in self.items_tracking:
            return

        end_time = time.time()
        final_snapshot = self._take_snapshot()
        item = self.items_tracking[item_id]

        item.end_time = end_time
        item.duration_seconds = end_time - item.start_time
        item.success = success
        item.error = error

        # Update with final snapshot
        self.update_item(item_id, final_snapshot)

        # Calculate memory delta
        if item.snapshots:
            initial_memory = item.snapshots[0].get('memory_available_mb', 0)
            final_memory = item.snapshots[-1].get('memory_available_mb', 0)
            item.memory_delta_mb = initial_memory - final_memory

        # Calculate I/O deltas
        if len(item.snapshots) > 1:
            initial_io = item.snapshots[0]
            final_io = item.snapshots[-1]
            item.disk_io_read_mb = final_io.get('disk_io_read_mb', 0) - initial_io.get('disk_io_read_mb', 0)
            item.disk_io_write_mb = final_io.get('disk_io_write_mb', 0) - initial_io.get('disk_io_write_mb', 0)
            item.network_bytes_sent_mb = final_io.get('network_bytes_sent_mb', 0) - initial_io.get('network_bytes_sent_mb', 0)
            item.network_bytes_recv_mb = final_io.get('network_bytes_recv_mb', 0) - initial_io.get('network_bytes_recv_mb', 0)

        status = "✅" if success else "❌"
        logger.info(f"{status} Completed tracking: {item['item_name']} ({item_id}) - {item.duration_seconds:.2f}s")

    def _snapshot_loop(self):
        """Continuous snapshot loop"""
        while self.snapshot_active:
            snapshot = self._take_snapshot()
            self.snapshots.append(snapshot)
            time.sleep(self.snapshot_interval)

    def _take_snapshot(self) -> PerformanceSnapshot:
        """Take a performance snapshot"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk_io = psutil.disk_io_counters()
            network_io = psutil.net_io_counters()

            return PerformanceSnapshot(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_available_mb=memory.available / (1024 * 1024),
                disk_io_read_mb=(disk_io.read_bytes / (1024 * 1024)) if disk_io else 0,
                disk_io_write_mb=(disk_io.write_bytes / (1024 * 1024)) if disk_io else 0,
                network_bytes_sent_mb=network_io.bytes_sent / (1024 * 1024),
                network_bytes_recv_mb=network_io.bytes_recv / (1024 * 1024),
                process_count=len(psutil.pids()),
                thread_count=psutil.Process().num_threads()
            )
        except Exception as e:
            logger.warning(f"Error taking snapshot: {e}")
            return PerformanceSnapshot(
                timestamp=time.time(),
                cpu_percent=0,
                memory_percent=0,
                memory_available_mb=0,
                disk_io_read_mb=0,
                disk_io_write_mb=0,
                network_bytes_sent_mb=0,
                network_bytes_recv_mb=0,
                process_count=0,
                thread_count=0
            )

    def _generate_report(self, end_time: float, total_duration: Optional[float]) -> Dict[str, Any]:
        """Generate performance report"""
        # System resources summary
        if self.snapshots:
            avg_cpu = sum(s.cpu_percent for s in self.snapshots) / len(self.snapshots)
            peak_cpu = max(s.cpu_percent for s in self.snapshots)
            avg_memory = sum(s.memory_percent for s in self.snapshots) / len(self.snapshots)
            peak_memory = max(s.memory_percent for s in self.snapshots)
        else:
            avg_cpu = peak_cpu = avg_memory = peak_memory = 0

        # Items summary
        items_data = [asdict(item) for item in self.items_tracking.values()]

        # Identify parallel groups (items that ran concurrently)
        parallel_groups = self._identify_parallel_groups()

        # Generate optimization recommendations
        recommendations = self._generate_recommendations(items_data, parallel_groups)

        report = {
            "phase": self.current_phase.value if self.current_phase else "unknown",
            "start_time": datetime.fromtimestamp(self.phase_start_time).isoformat() if self.phase_start_time else None,
            "end_time": datetime.fromtimestamp(end_time).isoformat(),
            "total_duration_seconds": total_duration,
            "items": items_data,
            "system_resources": {
                "avg_cpu_percent": avg_cpu,
                "peak_cpu_percent": peak_cpu,
                "avg_memory_percent": avg_memory,
                "peak_memory_percent": peak_memory,
                "snapshots_count": len(self.snapshots)
            },
            "parallel_groups": parallel_groups,
            "optimization_recommendations": recommendations
        }

        return report

    def _identify_parallel_groups(self) -> List[Dict[str, Any]]:
        """Identify which items ran in parallel"""
        groups = []
        items = list(self.items_tracking.values())

        for i, item1 in enumerate(items):
            if item1.end_time is None:
                continue

            group = {
                "items": [item1.item_id],
                "start_time": item1.start_time,
                "end_time": item1.end_time,
                "overlap_count": 1
            }

            for item2 in items[i+1:]:
                if item2.end_time is None:
                    continue

                # Check if items overlapped
                if (item1.start_time <= item2.end_time and item2.start_time <= item1.end_time):
                    group["items"].append(item2.item_id)
                    group["start_time"] = min(group["start_time"], item2.start_time)
                    group["end_time"] = max(group["end_time"], item2.end_time)
                    group["overlap_count"] += 1

            if group["overlap_count"] > 1:
                groups.append(group)

        return groups

    def _generate_recommendations(self, items: List[Dict], parallel_groups: List[Dict]) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []

        # Check for high resource usage
        high_cpu_items = [item for item in items if item.get('cpu_peak_percent', 0) > self.max_cpu_percent]
        high_memory_items = [item for item in items if item.get('memory_peak_percent', 0) > self.max_memory_percent]

        if high_cpu_items:
            recommendations.append(f"Consider staggering {len(high_cpu_items)} items with high CPU usage (>80%)")

        if high_memory_items:
            recommendations.append(f"Consider staggering {len(high_memory_items)} items with high memory usage (>85%)")

        # Check parallel execution efficiency
        if parallel_groups:
            max_parallel = max(g.get('overlap_count', 0) for g in parallel_groups)
            if max_parallel > self.optimal_parallel_items:
                recommendations.append(f"Reduce parallel execution from {max_parallel} to {self.optimal_parallel_items} items for better resource balance")

        # Check for long-running items
        long_items = [item for item in items if item.get('duration_seconds', 0) > 60]
        if long_items:
            recommendations.append(f"Optimize {len(long_items)} long-running items (>60s) - consider breaking into smaller tasks")

        # Check for sequential bottlenecks
        sequential_items = [item for item in items if item.get('duration_seconds', 0) > 30 and not any(
            g for g in parallel_groups if item['item_id'] in g.get('items', [])
        )]
        if sequential_items:
            recommendations.append(f"Consider parallelizing {len(sequential_items)} sequential items that could run concurrently")

        return recommendations


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Startup/Shutdown Performance Tracker")
        parser.add_argument("--start-phase", type=str, choices=["startup", "shutdown", "system_reboot"],
                           help="Start tracking a phase")
        parser.add_argument("--stop-phase", action="store_true", help="Stop tracking current phase")
        parser.add_argument("--start-item", type=str, nargs=2, metavar=("ITEM_ID", "ITEM_NAME"),
                           help="Start tracking an item")
        parser.add_argument("--end-item", type=str, nargs=3, metavar=("ITEM_ID", "SUCCESS", "ERROR"),
                           help="End tracking an item")
        parser.add_argument("--report", action="store_true", help="Show latest report")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        tracker = StartupPerformanceTracker(project_root)

        if args.start_phase:
            phase = PhaseType(args.start_phase)
            phase_id = tracker.start_phase(phase)
            print(f"Phase tracking started: {phase_id}")

        elif args.stop_phase:
            report = tracker.stop_phase()
            print("=" * 80)
            print("PERFORMANCE REPORT")
            print("=" * 80)
            print(json.dumps(report, indent=2, default=str))

        elif args.start_item:
            tracker.start_item(args.start_item[0], args.start_item[1])
            print(f"Started tracking: {args.start_item[1]}")

        elif args.end_item:
            success = args.end_item[1].lower() == "true"
            error = args.end_item[2] if args.end_item[2] != "None" else None
            tracker.end_item(args.end_item[0], success, error)
            print(f"Ended tracking: {args.end_item[0]}")

        elif args.report:
            # Show latest report
            reports = sorted(tracker.reports_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
            if reports:
                with open(reports[0], 'r', encoding='utf-8') as f:
                    report = json.load(f)
                print("=" * 80)
                print("LATEST PERFORMANCE REPORT")
                print("=" * 80)
                print(json.dumps(report, indent=2, default=str))
            else:
                print("No reports found")

        else:
            print("JARVIS Startup/Shutdown Performance Tracker")
            print("Use --help for usage information")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()