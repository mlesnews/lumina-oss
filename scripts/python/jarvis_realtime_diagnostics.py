#!/usr/bin/env python3
"""
JARVIS Real-Time Diagnostics

MCU JARVIS Capability: Real-time system analysis, diagnostics, and status reporting.
Continuously monitors system health and provides instant diagnostics.

@JARVIS @REALTIME_DIAGNOSTICS @MCU_FEATURE
"""

import sys
import json
import psutil
import platform
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import threading
import time

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISRealtimeDiagnostics")


class HealthStatus(Enum):
    """System health status"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class SystemMetric:
    """System metric snapshot"""
    metric_name: str
    value: float
    unit: str
    status: HealthStatus
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['status'] = self.status.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class DiagnosticReport:
    """Complete diagnostic report"""
    report_id: str
    timestamp: datetime
    overall_health: HealthStatus
    metrics: List[SystemMetric]
    warnings: List[str]
    recommendations: List[str]
    system_info: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['overall_health'] = self.overall_health.value
        data['metrics'] = [m.to_dict() for m in self.metrics]
        data['timestamp'] = self.timestamp.isoformat()
        return data


class JARVISRealtimeDiagnostics:
    """
    JARVIS Real-Time Diagnostics

    MCU JARVIS Capability: Real-time system analysis and diagnostics
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize real-time diagnostics"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JARVISRealtimeDiagnostics")

        # Monitoring state
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_interval = 30  # seconds

        # Latest diagnostic report
        self.latest_report: Optional[DiagnosticReport] = None

        # Metric history (keep last 100 per metric)
        self.metric_history: Dict[str, List[SystemMetric]] = {}

        # Data storage
        self.data_dir = self.project_root / "data" / "jarvis" / "diagnostics"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.reports_file = self.data_dir / "diagnostic_reports.json"

        # Default thresholds
        self.thresholds = {
            'cpu_percent': {'warning': 70.0, 'critical': 90.0},
            'memory_percent': {'warning': 80.0, 'critical': 95.0},
            'disk_percent': {'warning': 85.0, 'critical': 95.0},
        }

        self.logger.info("📊 JARVIS Real-Time Diagnostics initialized")

    def collect_system_metrics(self) -> List[SystemMetric]:
        """Collect current system metrics"""
        metrics = []

        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_metric = SystemMetric(
                metric_name="CPU Usage",
                value=cpu_percent,
                unit="%",
                status=self._evaluate_health(cpu_percent, 'cpu_percent'),
                threshold_warning=self.thresholds['cpu_percent']['warning'],
                threshold_critical=self.thresholds['cpu_percent']['critical']
            )
            metrics.append(cpu_metric)

            # Memory metrics
            memory = psutil.virtual_memory()
            memory_metric = SystemMetric(
                metric_name="Memory Usage",
                value=memory.percent,
                unit="%",
                status=self._evaluate_health(memory.percent, 'memory_percent'),
                threshold_warning=self.thresholds['memory_percent']['warning'],
                threshold_critical=self.thresholds['memory_percent']['critical']
            )
            metrics.append(memory_metric)

            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_metric = SystemMetric(
                metric_name="Disk Usage",
                value=disk.percent,
                unit="%",
                status=self._evaluate_health(disk.percent, 'disk_percent'),
                threshold_warning=self.thresholds['disk_percent']['warning'],
                threshold_critical=self.thresholds['disk_percent']['critical']
            )
            metrics.append(disk_metric)

            # Network metrics
            try:
                net_io = psutil.net_io_counters()
                net_sent_mb = net_io.bytes_sent / (1024 * 1024)
                net_recv_mb = net_io.bytes_recv / (1024 * 1024)

                metrics.append(SystemMetric(
                    metric_name="Network Sent",
                    value=net_sent_mb,
                    unit="MB",
                    status=HealthStatus.GOOD
                ))
                metrics.append(SystemMetric(
                    metric_name="Network Received",
                    value=net_recv_mb,
                    unit="MB",
                    status=HealthStatus.GOOD
                ))
            except Exception as e:
                self.logger.debug(f"Network metrics error: {e}")

            # Process count
            process_count = len(psutil.pids())
            metrics.append(SystemMetric(
                metric_name="Active Processes",
                value=process_count,
                unit="count",
                status=HealthStatus.GOOD
            ))

        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")

        return metrics

    def _evaluate_health(self, value: float, metric_type: str) -> HealthStatus:
        """Evaluate health status based on value and thresholds"""
        if metric_type not in self.thresholds:
            return HealthStatus.GOOD

        thresholds = self.thresholds[metric_type]

        if value >= thresholds['critical']:
            return HealthStatus.CRITICAL
        elif value >= thresholds['warning']:
            return HealthStatus.POOR
        elif value >= thresholds['warning'] * 0.7:
            return HealthStatus.FAIR
        elif value >= thresholds['warning'] * 0.5:
            return HealthStatus.GOOD
        else:
            return HealthStatus.EXCELLENT

    def generate_diagnostic_report(self) -> DiagnosticReport:
        """Generate complete diagnostic report"""
        metrics = self.collect_system_metrics()

        # Determine overall health (worst status)
        status_values = {
            HealthStatus.EXCELLENT: 5,
            HealthStatus.GOOD: 4,
            HealthStatus.FAIR: 3,
            HealthStatus.POOR: 2,
            HealthStatus.CRITICAL: 1
        }
        worst_status = min(metrics, key=lambda m: status_values[m.status]).status if metrics else HealthStatus.GOOD

        # Generate warnings
        warnings = []
        for metric in metrics:
            if metric.status in [HealthStatus.POOR, HealthStatus.CRITICAL]:
                warnings.append(f"{metric.metric_name} is {metric.status.value}: {metric.value} {metric.unit}")

        # Generate recommendations
        recommendations = []
        for metric in metrics:
            if metric.status == HealthStatus.CRITICAL:
                if "CPU" in metric.metric_name:
                    recommendations.append("Consider closing resource-intensive applications or processes")
                elif "Memory" in metric.metric_name:
                    recommendations.append("Consider freeing up memory or restarting applications")
                elif "Disk" in metric.metric_name:
                    recommendations.append("Consider freeing up disk space or archiving old files")

        # System information
        system_info = {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "processor": platform.processor(),
            "hostname": platform.node(),
            "python_version": platform.python_version(),
        }

        # Store metric history
        for metric in metrics:
            if metric.metric_name not in self.metric_history:
                self.metric_history[metric.metric_name] = []
            self.metric_history[metric.metric_name].append(metric)
            # Keep last 100
            if len(self.metric_history[metric.metric_name]) > 100:
                self.metric_history[metric.metric_name] = self.metric_history[metric.metric_name][-100:]

        report = DiagnosticReport(
            report_id=f"diag_{int(datetime.now().timestamp())}",
            timestamp=datetime.now(),
            overall_health=worst_status,
            metrics=metrics,
            warnings=warnings,
            recommendations=recommendations,
            system_info=system_info
        )

        self.latest_report = report
        return report

    def get_quick_status(self) -> str:
        """Get quick status summary (MCU JARVIS style)"""
        if not self.latest_report:
            self.generate_diagnostic_report()

        report = self.latest_report
        if not report:
            return "Status unavailable"

        status_emoji = {
            HealthStatus.EXCELLENT: "🟢",
            HealthStatus.GOOD: "🟢",
            HealthStatus.FAIR: "🟡",
            HealthStatus.POOR: "🟠",
            HealthStatus.CRITICAL: "🔴"
        }

        emoji = status_emoji.get(report.overall_health, "⚪")

        # Key metrics summary
        cpu = next((m for m in report.metrics if "CPU" in m.metric_name), None)
        memory = next((m for m in report.metrics if "Memory" in m.metric_name), None)
        disk = next((m for m in report.metrics if "Disk" in m.metric_name), None)

        status_parts = [f"{emoji} System: {report.overall_health.value.upper()}"]

        if cpu:
            status_parts.append(f"CPU: {cpu.value:.1f}%")
        if memory:
            status_parts.append(f"Memory: {memory.value:.1f}%")
        if disk:
            status_parts.append(f"Disk: {disk.value:.1f}%")

        if report.warnings:
            status_parts.append(f"⚠️ {len(report.warnings)} warning(s)")

        return " | ".join(status_parts)

    def start_monitoring(self, interval: int = 30):
        """Start continuous monitoring"""
        if self.monitoring_active:
            self.logger.warning("Monitoring already active")
            return

        self.monitoring_active = True
        self.monitoring_interval = interval
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.logger.info(f"📊 Real-time monitoring started (interval: {interval}s)")

    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        self.logger.info("📊 Real-time monitoring stopped")

    def _monitoring_loop(self):
        """Continuous monitoring loop"""
        while self.monitoring_active:
            try:
                report = self.generate_diagnostic_report()

                # Log warnings
                if report.warnings:
                    for warning in report.warnings:
                        self.logger.warning(f"⚠️ {warning}")

                # Save report periodically
                if len(self.metric_history.get("CPU Usage", [])) % 10 == 0:
                    self._save_reports()

                time.sleep(self.monitoring_interval)
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(self.monitoring_interval)

    def _save_reports(self):
        """Save diagnostic reports"""
        try:
            reports = []
            if self.latest_report:
                reports.append(self.latest_report.to_dict())

            # Save to file
            with open(self.reports_file, 'w') as f:
                json.dump(reports, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error saving reports: {e}")

    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report"""
        if not self.latest_report:
            self.generate_diagnostic_report()

        if not self.latest_report:
            return {"error": "Could not generate diagnostic report"}

        return self.latest_report.to_dict()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Real-Time Diagnostics")
    parser.add_argument("--status", action="store_true", help="Get quick status")
    parser.add_argument("--report", action="store_true", help="Generate diagnostic report")
    parser.add_argument("--start", action="store_true", help="Start monitoring")
    parser.add_argument("--stop", action="store_true", help="Stop monitoring")

    args = parser.parse_args()

    diagnostics = JARVISRealtimeDiagnostics()

    if args.status:
        status = diagnostics.get_quick_status()
        print(status)

    elif args.report:
        report = diagnostics.generate_diagnostic_report()
        print(json.dumps(report.to_dict(), indent=2, default=str))

    elif args.start:
        diagnostics.start_monitoring()
        print("✅ Monitoring started")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            diagnostics.stop_monitoring()

    elif args.stop:
        diagnostics.stop_monitoring()
        print("✅ Monitoring stopped")

    else:
        parser.print_help()


if __name__ == "__main__":


    main()