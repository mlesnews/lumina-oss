#!/usr/bin/env python3
"""
Tool/App Resource Utilization Historian
Tracks and measures resource utilization percentage scores for major/minor tools/apps

Features:
- Real-time resource monitoring (CPU, Memory, Disk, Network)
- Historical tracking with timestamps
- Percentage score calculation
- Tool/app categorization (major/minor)
- Historical data analysis and reporting

Tags: #measure #historian #resource #utilization #monitoring @JARVIS @TEAM
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import statistics

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

# ALWAYS use the standard logging module: lumina_logger
# This is a critical requirement - all scripts must use lumina_logger.get_logger()
from lumina_logger import get_logger
from standardized_timestamp_logging import get_timestamp_logger, TimestampFormat

logger = get_logger("ToolResourceUtilizationHistorian")

try:
    import psutil
except ImportError:
    logger.error("psutil not installed. Install with: pip install psutil")
    psutil = None


class ResourceType(Enum):
    """Resource type"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"


class ToolCategory(Enum):
    """Tool/app category"""
    MAJOR = "major"  # Primary tools (IDEs, browsers, etc.)
    MINOR = "minor"  # Supporting tools (utilities, background processes)
    SYSTEM = "system"  # System processes
    UNKNOWN = "unknown"


@dataclass
class ResourceMetrics:
    """Resource utilization metrics for a single measurement"""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_mb: float = 0.0
    disk_read_mb: float = 0.0
    disk_write_mb: float = 0.0
    network_sent_mb: float = 0.0
    network_recv_mb: float = 0.0
    num_threads: int = 0
    num_handles: int = 0  # Windows file handles / Linux file descriptors

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class ToolSnapshot:
    """Snapshot of a tool/app's resource utilization at a point in time"""
    tool_name: str
    process_name: str
    pid: int
    category: ToolCategory
    timestamp: datetime
    metrics: ResourceMetrics
    utilization_score: float  # Overall utilization percentage (0-100)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['category'] = self.category.value
        result['timestamp'] = self.timestamp.isoformat()
        result['metrics'] = self.metrics.to_dict()
        return result


@dataclass
class ToolHistory:
    """Historical data for a tool/app"""
    tool_name: str
    process_name: str
    category: ToolCategory
    snapshots: List[ToolSnapshot] = field(default_factory=list)

    def get_average_utilization(self, hours: Optional[int] = None) -> float:
        """Get average utilization score over time period"""
        if not self.snapshots:
            return 0.0

        if hours:
            cutoff = datetime.now() - timedelta(hours=hours)
            recent = [s for s in self.snapshots if s.timestamp >= cutoff]
            if not recent:
                return 0.0
            return statistics.mean([s.utilization_score for s in recent])

        return statistics.mean([s.utilization_score for s in self.snapshots])

    def get_peak_utilization(self, hours: Optional[int] = None) -> float:
        """Get peak utilization score over time period"""
        if not self.snapshots:
            return 0.0

        if hours:
            cutoff = datetime.now() - timedelta(hours=hours)
            recent = [s for s in self.snapshots if s.timestamp >= cutoff]
            if not recent:
                return 0.0
            return max([s.utilization_score for s in recent])

        return max([s.utilization_score for s in self.snapshots])

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "tool_name": self.tool_name,
            "process_name": self.process_name,
            "category": self.category.value,
            "snapshot_count": len(self.snapshots),
            "average_utilization": self.get_average_utilization(),
            "peak_utilization": self.get_peak_utilization(),
            "recent_average_1h": self.get_average_utilization(1),
            "recent_average_24h": self.get_average_utilization(24),
            "snapshots": [s.to_dict() for s in self.snapshots[-100:]]  # Last 100 snapshots
        }


class ToolResourceUtilizationHistorian:
    """
    Tool/App Resource Utilization Historian

    Tracks resource utilization for tools/apps with historical data.
    Provides percentage scores and historical analysis.
    """

    # Major tools/apps (primary applications)
    MAJOR_TOOLS = {
        'cursor.exe', 'code.exe', 'vscode.exe',  # IDEs
        'chrome.exe', 'msedge.exe', 'firefox.exe',  # Browsers
        'notion.exe', 'obsidian.exe',  # Note-taking
        'slack.exe', 'teams.exe', 'discord.exe',  # Communication
        'python.exe', 'node.exe',  # Runtimes (when running scripts)
        'docker.exe', 'docker-desktop.exe',  # Containers
        'git.exe',  # Version control
    }

    # Minor tools/apps (utilities, background)
    MINOR_TOOLS = {
        'explorer.exe', 'dwm.exe',  # Windows shell
        'svchost.exe', 'winlogon.exe',  # System services
        'powershell.exe', 'pwsh.exe',  # Shells
        'conhost.exe', 'cmd.exe',  # Terminals
    }

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize resource utilization historian"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "resource_utilization"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Historical data storage
        self.tool_histories: Dict[str, ToolHistory] = {}

        # Process tracking
        self.tracked_processes: Dict[int, str] = {}  # pid -> tool_name

        # System baseline (for percentage calculation)
        self.system_baseline = {
            'cpu_count': psutil.cpu_count() if psutil else 1,
            'total_memory_mb': psutil.virtual_memory().total / (1024 * 1024) if psutil else 0,
        }

        logger.info("✅ Tool Resource Utilization Historian initialized")
        logger.info(f"   System: {self.system_baseline['cpu_count']} CPUs, "
                   f"{self.system_baseline['total_memory_mb']:.0f} MB RAM")

    def _categorize_tool(self, process_name: str) -> ToolCategory:
        """Categorize tool as major/minor/system"""
        process_lower = process_name.lower()

        if process_lower in self.MAJOR_TOOLS:
            return ToolCategory.MAJOR
        elif process_lower in self.MINOR_TOOLS:
            return ToolCategory.MINOR
        elif any(system in process_lower for system in ['system', 'ntoskrnl', 'csrss', 'smss']):
            return ToolCategory.SYSTEM
        else:
            return ToolCategory.UNKNOWN

    def _calculate_utilization_score(self, metrics: ResourceMetrics) -> float:
        """
        Calculate overall utilization percentage score (0-100)

        Weighted combination of:
        - CPU: 40%
        - Memory: 40%
        - Disk I/O: 10%
        - Network: 10%
        """
        # CPU utilization (already a percentage)
        cpu_score = metrics.cpu_percent

        # Memory utilization (percentage of total system memory)
        memory_score = metrics.memory_percent

        # Disk I/O score (normalized, capped at 100%)
        # Assuming high disk I/O is > 100 MB/s
        disk_score = min(100.0, (metrics.disk_read_mb + metrics.disk_write_mb) / 100.0 * 100)

        # Network score (normalized, capped at 100%)
        # Assuming high network is > 50 MB/s
        network_score = min(100.0, (metrics.network_sent_mb + metrics.network_recv_mb) / 50.0 * 100)

        # Weighted combination
        utilization_score = (
            cpu_score * 0.40 +
            memory_score * 0.40 +
            disk_score * 0.10 +
            network_score * 0.10
        )

        return min(100.0, max(0.0, utilization_score))

    def _get_process_metrics(self, proc: Any) -> Optional[ResourceMetrics]:
        """Get resource metrics for a process"""
        if not psutil:
            return None

        try:
            # CPU
            cpu_percent = proc.cpu_percent(interval=0.1)

            # Memory
            mem_info = proc.memory_info()
            memory_mb = mem_info.rss / (1024 * 1024)
            memory_percent = (mem_info.rss / psutil.virtual_memory().total) * 100

            # Disk I/O
            try:
                io_counters = proc.io_counters()
                disk_read_mb = io_counters.read_bytes / (1024 * 1024)
                disk_write_mb = io_counters.write_bytes / (1024 * 1024)
            except (AttributeError, psutil.AccessDenied):
                disk_read_mb = 0.0
                disk_write_mb = 0.0

            # Network I/O
            try:
                net_io = proc.io_counters()
                network_sent_mb = getattr(net_io, 'bytes_sent', 0) / (1024 * 1024)
                network_recv_mb = getattr(net_io, 'bytes_recv', 0) / (1024 * 1024)
            except (AttributeError, psutil.AccessDenied):
                network_sent_mb = 0.0
                network_recv_mb = 0.0

            # Threads and handles
            num_threads = proc.num_threads()
            try:
                num_handles = proc.num_handles() if hasattr(proc, 'num_handles') else 0
            except (AttributeError, psutil.AccessDenied):
                num_handles = 0

            return ResourceMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_mb=memory_mb,
                disk_read_mb=disk_read_mb,
                disk_write_mb=disk_write_mb,
                network_sent_mb=network_sent_mb,
                network_recv_mb=network_recv_mb,
                num_threads=num_threads,
                num_handles=num_handles
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return None

    def capture_snapshot(self) -> List[ToolSnapshot]:
        """Capture current snapshot of all running tools/apps"""
        if not psutil:
            logger.error("psutil not available")
            return []

        snapshots = []
        timestamp = datetime.now()

        # Get all processes
        processes = {}
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                processes[proc.info['pid']] = proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Capture metrics for each process
        for pid, proc in processes.items():
            try:
                process_name = proc.name()
                tool_name = self._get_tool_name(process_name, pid)
                category = self._categorize_tool(process_name)

                # Skip system processes unless explicitly tracked
                if category == ToolCategory.SYSTEM and tool_name not in self.tracked_processes.values():
                    continue

                # Get metrics
                metrics = self._get_process_metrics(proc)
                if not metrics:
                    continue

                # Calculate utilization score
                utilization_score = self._calculate_utilization_score(metrics)

                # Only track if utilization is significant (> 0.1%) or is a major tool
                if utilization_score < 0.1 and category != ToolCategory.MAJOR:
                    continue

                snapshot = ToolSnapshot(
                    tool_name=tool_name,
                    process_name=process_name,
                    pid=pid,
                    category=category,
                    timestamp=timestamp,
                    metrics=metrics,
                    utilization_score=utilization_score,
                    metadata={
                        "cpu_count": self.system_baseline['cpu_count'],
                        "total_memory_mb": self.system_baseline['total_memory_mb']
                    }
                )

                snapshots.append(snapshot)

                # Update history
                if tool_name not in self.tool_histories:
                    self.tool_histories[tool_name] = ToolHistory(
                        tool_name=tool_name,
                        process_name=process_name,
                        category=category
                    )

                self.tool_histories[tool_name].snapshots.append(snapshot)
                self.tracked_processes[pid] = tool_name

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception as e:
                logger.debug(f"Error capturing snapshot for PID {pid}: {e}")
                continue

        # Clean up dead processes
        active_pids = set(processes.keys())
        dead_pids = set(self.tracked_processes.keys()) - active_pids
        for pid in dead_pids:
            del self.tracked_processes[pid]

        logger.info(f"📊 Captured {len(snapshots)} tool snapshots")
        return snapshots

    def _get_tool_name(self, process_name: str, pid: int) -> str:
        """Get standardized tool name from process name"""
        # Use process name as base, but normalize
        process_lower = process_name.lower()

        # Normalize common variations
        if 'cursor' in process_lower:
            return 'Cursor IDE'
        elif 'code' in process_lower and 'vscode' in process_lower:
            return 'VS Code'
        elif 'chrome' in process_lower:
            return 'Chrome'
        elif 'msedge' in process_lower:
            return 'Edge'
        elif 'firefox' in process_lower:
            return 'Firefox'
        elif 'python' in process_lower:
            return 'Python'
        elif 'node' in process_lower:
            return 'Node.js'
        elif 'docker' in process_lower:
            return 'Docker'
        elif 'git' in process_lower:
            return 'Git'
        elif 'powershell' in process_lower or 'pwsh' in process_lower:
            return 'PowerShell'
        else:
            # Use process name, capitalized
            return process_name.rsplit('.', 1)[0].title()

    def get_tool_utilization_report(self, hours: Optional[int] = None) -> Dict[str, Any]:
        """Get utilization report for all tools"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "period_hours": hours,
            "tools": {},
            "summary": {
                "total_tools": 0,
                "major_tools": 0,
                "minor_tools": 0,
                "average_utilization": 0.0,
                "peak_utilization": 0.0
            }
        }

        major_tools = []
        minor_tools = []
        all_scores = []

        for tool_name, history in self.tool_histories.items():
            if hours:
                # Filter snapshots within time period
                cutoff = datetime.now() - timedelta(hours=hours)
                recent_snapshots = [s for s in history.snapshots if s.timestamp >= cutoff]
                if not recent_snapshots:
                    continue

                avg_util = statistics.mean([s.utilization_score for s in recent_snapshots])
                peak_util = max([s.utilization_score for s in recent_snapshots])
            else:
                avg_util = history.get_average_utilization()
                peak_util = history.get_peak_utilization()

            tool_data = {
                "tool_name": tool_name,
                "process_name": history.process_name,
                "category": history.category.value,
                "average_utilization": round(avg_util, 2),
                "peak_utilization": round(peak_util, 2),
                "snapshot_count": len(history.snapshots),
                "recent_1h_avg": round(history.get_average_utilization(1), 2),
                "recent_24h_avg": round(history.get_average_utilization(24), 2)
            }

            report["tools"][tool_name] = tool_data
            all_scores.append(avg_util)

            if history.category == ToolCategory.MAJOR:
                major_tools.append(tool_data)
            elif history.category == ToolCategory.MINOR:
                minor_tools.append(tool_data)

        # Summary
        report["summary"]["total_tools"] = len(self.tool_histories)
        report["summary"]["major_tools"] = len(major_tools)
        report["summary"]["minor_tools"] = len(minor_tools)
        report["summary"]["average_utilization"] = round(statistics.mean(all_scores) if all_scores else 0.0, 2)
        report["summary"]["peak_utilization"] = round(max(all_scores) if all_scores else 0.0, 2)

        # Sort tools by utilization
        report["tools_sorted"] = sorted(
            report["tools"].items(),
            key=lambda x: x[1]["average_utilization"],
            reverse=True
        )

        return report

    def save_history(self):
        try:
            """Save historical data to disk"""
            history_file = self.data_dir / f"tool_history_{datetime.now().strftime('%Y%m%d')}.json"

            history_data = {
                "timestamp": datetime.now().isoformat(),
                "tools": {name: history.to_dict() for name, history in self.tool_histories.items()}
            }

            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, default=str)

            logger.info(f"💾 Saved history to {history_file}")

        except Exception as e:
            self.logger.error(f"Error in save_history: {e}", exc_info=True)
            raise
    def load_history(self, date: Optional[str] = None):
        try:
            """Load historical data from disk"""
            if date is None:
                date = datetime.now().strftime('%Y%m%d')

            history_file = self.data_dir / f"tool_history_{date}.json"

            if not history_file.exists():
                logger.warning(f"History file not found: {history_file}")
                return

            with open(history_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)

            # Reconstruct tool histories
            for tool_name, tool_data in history_data.get("tools", {}).items():
                category = ToolCategory(tool_data["category"])
                history = ToolHistory(
                    tool_name=tool_name,
                    process_name=tool_data["process_name"],
                    category=category
                )

                # Reconstruct snapshots
                for snap_data in tool_data.get("snapshots", []):
                    snapshot = ToolSnapshot(
                        tool_name=snap_data["tool_name"],
                        process_name=snap_data["process_name"],
                        pid=snap_data["pid"],
                        category=category,
                        timestamp=datetime.fromisoformat(snap_data["timestamp"]),
                        metrics=ResourceMetrics(**snap_data["metrics"]),
                        utilization_score=snap_data["utilization_score"],
                        metadata=snap_data.get("metadata", {})
                    )
                    history.snapshots.append(snapshot)

                self.tool_histories[tool_name] = history

            logger.info(f"📂 Loaded history from {history_file}")


        except Exception as e:
            self.logger.error(f"Error in load_history: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Tool Resource Utilization Historian")
    parser.add_argument('--capture', action='store_true', help='Capture current snapshot')
    parser.add_argument('--report', action='store_true', help='Generate utilization report')
    parser.add_argument('--hours', type=int, help='Time period for report (hours)')
    parser.add_argument('--save', action='store_true', help='Save history to disk')
    parser.add_argument('--load', type=str, help='Load history from date (YYYYMMDD)')
    parser.add_argument('--monitor', type=int, help='Monitor continuously (interval in seconds)')

    args = parser.parse_args()

    historian = ToolResourceUtilizationHistorian()

    if args.load:
        historian.load_history(args.load)

    if args.capture:
        print("\n📊 Capturing tool resource utilization snapshot...")
        snapshots = historian.capture_snapshot()
        print(f"✅ Captured {len(snapshots)} tool snapshots")

        # Show top 10 by utilization
        snapshots.sort(key=lambda x: x.utilization_score, reverse=True)
        print("\n🔝 Top 10 Tools by Utilization:")
        print("=" * 80)
        for i, snap in enumerate(snapshots[:10], 1):
            print(f"{i:2d}. {snap.tool_name:30s} [{snap.category.value:6s}] "
                 f"Util: {snap.utilization_score:6.2f}% | "
                 f"CPU: {snap.metrics.cpu_percent:5.1f}% | "
                 f"Mem: {snap.metrics.memory_percent:5.1f}%")

    if args.report:
        print("\n📊 Generating Utilization Report...")
        report = historian.get_tool_utilization_report(hours=args.hours)

        print("\n" + "=" * 80)
        print("📊 TOOL RESOURCE UTILIZATION REPORT")
        print("=" * 80)
        print(f"Timestamp: {report['timestamp']}")
        if args.hours:
            print(f"Period: Last {args.hours} hours")
        print(f"\nSummary:")
        print(f"  Total Tools: {report['summary']['total_tools']}")
        print(f"  Major Tools: {report['summary']['major_tools']}")
        print(f"  Minor Tools: {report['summary']['minor_tools']}")
        print(f"  Average Utilization: {report['summary']['average_utilization']:.2f}%")
        print(f"  Peak Utilization: {report['summary']['peak_utilization']:.2f}%")

        print(f"\n🔝 Top Tools by Average Utilization:")
        print("-" * 80)
        for tool_name, tool_data in report['tools_sorted'][:20]:
            print(f"  {tool_name:30s} [{tool_data['category']:6s}] "
                 f"Avg: {tool_data['average_utilization']:6.2f}% | "
                 f"Peak: {tool_data['peak_utilization']:6.2f}% | "
                 f"1h: {tool_data['recent_1h_avg']:6.2f}% | "
                 f"24h: {tool_data['recent_24h_avg']:6.2f}%")

        # Save report
        report_file = historian.data_dir / f"utilization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n💾 Report saved to: {report_file}")

    if args.monitor:
        print(f"\n📊 Monitoring tool resource utilization (interval: {args.monitor}s)")
        print("Press Ctrl+C to stop\n")

        try:
            while True:
                historian.capture_snapshot()
                time.sleep(args.monitor)
        except KeyboardInterrupt:
            print("\n✅ Monitoring stopped")
            if args.save:
                historian.save_history()

    if args.save:
        historian.save_history()
        print("✅ History saved to disk")


if __name__ == "__main__":


    main()