#!/usr/bin/env python3
"""
JARVIS Proactive Monitoring System

MCU JARVIS Capability: Proactive Monitoring
Continuously monitors systems, predicts failures, automatically remediates.

@JARVIS @MONITORING @PROACTIVE @MCU_FEATURE
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import threading
import time
import tempfile
import shutil
import os

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISProactiveMonitoring")


class SystemStatus(Enum):
    """System status"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    FAILED = "failed"
    UNKNOWN = "unknown"


class MetricType(Enum):
    """Metric types"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    PROCESS = "process"
    SERVICE = "service"
    PERFORMANCE = "performance"
    ERROR_RATE = "error_rate"
    LATENCY = "latency"
    CUSTOM = "custom"


@dataclass
class SystemMetric:
    """System metric"""
    metric_id: str
    metric_type: MetricType
    name: str
    value: float
    unit: str
    timestamp: datetime
    status: SystemStatus
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['metric_type'] = self.metric_type.value
        data['status'] = self.status.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class Alert:
    """Alert"""
    alert_id: str
    metric_id: str
    severity: SystemStatus
    message: str
    timestamp: datetime
    resolved: bool = False
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['severity'] = self.severity.value
        data['timestamp'] = self.timestamp.isoformat()
        if self.resolved_at:
            data['resolved_at'] = self.resolved_at.isoformat()
        return data


class JARVISProactiveMonitoring:
    """
    JARVIS Proactive Monitoring System

    MCU JARVIS Capability: Continuous monitoring, predictive failure detection, automatic remediation.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize proactive monitoring system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JARVISProactiveMonitoring")

        # Metrics storage
        self.metrics: Dict[str, List[SystemMetric]] = {}

        # Alerts
        self.alerts: List[Alert] = []

        # Monitoring state
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_interval = 60  # seconds

        # Remediation handlers
        self.remediation_handlers: Dict[str, Callable] = {}

        # Alert handlers
        self.alert_handlers: List[Callable] = []

        # Data storage
        self.data_dir = self.project_root / "data" / "jarvis_monitoring"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_file = self.data_dir / "metrics.json"
        self.alerts_file = self.data_dir / "alerts.json"

        # Load state
        self._load_state()

        # Register default remediation handlers
        self._register_default_remediations()

        self.logger.info("📊 JARVIS Proactive Monitoring initialized")

    def _load_state(self):
        """Load metrics and alerts"""
        # Load metrics
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    data = json.load(f)
                    for metric_data in data:
                        metric = SystemMetric(
                            metric_id=metric_data['metric_id'],
                            metric_type=MetricType(metric_data['metric_type']),
                            name=metric_data['name'],
                            value=metric_data['value'],
                            unit=metric_data['unit'],
                            timestamp=datetime.fromisoformat(metric_data['timestamp']),
                            status=SystemStatus(metric_data['status']),
                            threshold_warning=metric_data.get('threshold_warning'),
                            threshold_critical=metric_data.get('threshold_critical'),
                            metadata=metric_data.get('metadata', {})
                        )
                        if metric.metric_id not in self.metrics:
                            self.metrics[metric.metric_id] = []
                        self.metrics[metric.metric_id].append(metric)
                        # Keep last 1000 per metric
                        if len(self.metrics[metric.metric_id]) > 1000:
                            self.metrics[metric.metric_id] = self.metrics[metric.metric_id][-1000:]
                self.logger.info(f"   Loaded metrics for {len(self.metrics)} metric IDs")
            except Exception as e:
                self.logger.error(f"Error loading metrics: {e}")

        # Load alerts
        if self.alerts_file.exists():
            try:
                with open(self.alerts_file, 'r') as f:
                    data = json.load(f)
                    for alert_data in data:
                        alert = Alert(
                            alert_id=alert_data['alert_id'],
                            metric_id=alert_data['metric_id'],
                            severity=SystemStatus(alert_data['severity']),
                            message=alert_data['message'],
                            timestamp=datetime.fromisoformat(alert_data['timestamp']),
                            resolved=alert_data.get('resolved', False),
                            resolution=alert_data.get('resolution'),
                            resolved_at=datetime.fromisoformat(alert_data['resolved_at']) if alert_data.get('resolved_at') else None
                        )
                        self.alerts.append(alert)
                self.logger.info(f"   Loaded {len(self.alerts)} alerts")
            except Exception as e:
                self.logger.error(f"Error loading alerts: {e}")

    def _save_state(self):
        """Save metrics and alerts using atomic writes with retry logic"""
        max_retries = 3
        retry_delay = 0.5

        # Save recent metrics (last 100 per metric)
        metrics_to_save = []
        for metric_list in self.metrics.values():
            metrics_to_save.extend(metric_list[-100:])

        # Save alerts (keep last 500)
        alerts_to_save = self.alerts[-500:]

        # Save metrics file with atomic write and retry
        self._atomic_write_file(
            self.metrics_file,
            [m.to_dict() for m in metrics_to_save],
            max_retries=max_retries,
            retry_delay=retry_delay
        )

        # Save alerts file with atomic write and retry
        self._atomic_write_file(
            self.alerts_file,
            [a.to_dict() for a in alerts_to_save],
            max_retries=max_retries,
            retry_delay=retry_delay
        )

    def _atomic_write_file(self, file_path: Path, data: Any, max_retries: int = 3, retry_delay: float = 0.5):
        """
        Atomically write data to a file with retry logic.

        Uses a temporary file and rename to ensure atomic writes and avoid
        permission issues on Windows (especially with Dropbox).

        Args:
            file_path: Target file path
            data: Data to write (will be JSON serialized)
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (exponential backoff)
        """
        # Ensure directory exists and is writable
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            # Test write permissions
            test_file = file_path.parent / ".write_test"
            try:
                test_file.write_text("test")
                test_file.unlink()
            except (PermissionError, OSError) as e:
                self.logger.warning(f"Directory not writable: {file_path.parent} - {e}")
                return
        except Exception as e:
            self.logger.error(f"Error creating directory {file_path.parent}: {e}")
            return

        for attempt in range(max_retries):
            try:
                # Create temporary file in the same directory (ensures same filesystem)
                temp_file = file_path.parent / f".{file_path.name}.tmp"

                # Write to temporary file
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)

                # Atomic rename (works on Windows if files are on same filesystem)
                # On Windows, replace existing file if it exists
                if file_path.exists():
                    # Try to remove existing file first (might be locked)
                    try:
                        file_path.unlink()
                    except PermissionError:
                        # File might be locked by Dropbox or another process
                        # Wait a bit and try again
                        time.sleep(retry_delay * (attempt + 1))
                        if attempt < max_retries - 1:
                            continue
                        else:
                            raise

                # Atomic rename
                temp_file.replace(file_path)
                return  # Success

            except PermissionError as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    self.logger.debug(f"Permission denied, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Error saving state to {file_path}: Permission denied after {max_retries} attempts - {e}")
                    # Clean up temp file if it exists
                    if 'temp_file' in locals() and temp_file.exists():
                        try:
                            temp_file.unlink()
                        except:
                            pass
            except OSError as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    self.logger.debug(f"OS error, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries}): {e}")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Error saving state to {file_path}: {e}")
                    # Clean up temp file if it exists
                    if 'temp_file' in locals() and temp_file.exists():
                        try:
                            temp_file.unlink()
                        except:
                            pass
            except Exception as e:
                self.logger.error(f"Unexpected error saving state to {file_path}: {e}", exc_info=True)
                # Clean up temp file if it exists
                if 'temp_file' in locals() and temp_file.exists():
                    try:
                        temp_file.unlink()
                    except:
                        pass
                return  # Don't retry on unexpected errors

    def _register_default_remediations(self):
        """Register default remediation handlers"""
        # CPU remediation
        self.register_remediation("cpu_high", self._remediate_high_cpu)

        # Memory remediation
        self.register_remediation("memory_high", self._remediate_high_memory)

        # Disk space remediation
        self.register_remediation("disk_full", self._remediate_disk_full)

        # Service remediation
        self.register_remediation("service_down", self._remediate_service_down)

    def _remediate_high_cpu(self, metric: SystemMetric) -> Dict[str, Any]:
        """Remediate high CPU usage"""
        self.logger.info(f"🔧 Proactive: Attempting CPU remediation for {metric.name}")
        # In a real scenario, could use process optimization tools
        return {"action": "cpu_remediation", "status": "monitored", "recommendation": "Check for runaway processes"}

    def _remediate_high_memory(self, metric: SystemMetric) -> Dict[str, Any]:
        """Remediate high memory usage"""
        self.logger.info(f"🔧 Proactive: Attempting Memory remediation for {metric.name}")
        return {"action": "memory_remediation", "status": "monitored", "recommendation": "Close unused applications"}

    def _remediate_disk_full(self, metric: SystemMetric) -> Dict[str, Any]:
        """Remediate disk full using emergency cleanup"""
        self.logger.info(f"🔧 Proactive: Attempting Disk remediation for {metric.name}")
        try:
            from jarvis_emergency_space_cleanup import JARVISEmergencySpaceCleanup
            cleanup = JARVISEmergencySpaceCleanup(self.project_root)
            result = cleanup.perform_emergency_cleanup()
            return {"action": "disk_cleanup", "status": "executed", "result": result}
        except ImportError:
            return {"action": "disk_cleanup", "status": "failed", "error": "Cleanup tool not found"}

    def _remediate_service_down(self, metric: SystemMetric) -> Dict[str, Any]:
        """Remediate service down"""
        self.logger.info(f"🔧 Proactive: Attempting Service remediation for {metric.name}")
        return {"action": "service_restart", "status": "manual_required"}

    def register_remediation(self, remediation_id: str, handler: Callable):
        """Register a remediation handler"""
        self.remediation_handlers[remediation_id] = handler

    def register_alert_handler(self, handler: Callable):
        """Register an alert handler"""
        self.alert_handlers.append(handler)

    def record_metric(self, metric_id: str, metric_type: MetricType, name: str,
                     value: float, unit: str, threshold_warning: Optional[float] = None,
                     threshold_critical: Optional[float] = None,
                     metadata: Dict[str, Any] = None) -> SystemMetric:
        """Record a system metric"""
        # Determine status
        status = SystemStatus.HEALTHY
        if threshold_critical and value >= threshold_critical:
            status = SystemStatus.CRITICAL
        elif threshold_warning and value >= threshold_warning:
            status = SystemStatus.WARNING

        metric = SystemMetric(
            metric_id=metric_id,
            metric_type=metric_type,
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            status=status,
            threshold_warning=threshold_warning,
            threshold_critical=threshold_critical,
            metadata=metadata or {}
        )

        # Store metric
        if metric_id not in self.metrics:
            self.metrics[metric_id] = []
        self.metrics[metric_id].append(metric)

        # Keep last 1000
        if len(self.metrics[metric_id]) > 1000:
            self.metrics[metric_id] = self.metrics[metric_id][-1000:]

        # Check for alerts
        if status in [SystemStatus.WARNING, SystemStatus.CRITICAL]:
            self._check_and_alert(metric)

        # Auto-remediate if critical
        if status == SystemStatus.CRITICAL:
            self._attempt_remediation(metric)

        self._save_state()
        return metric

    def _check_and_alert(self, metric: SystemMetric):
        """Check metric and create alert if needed"""
        # Check if alert already exists for this metric
        recent_alerts = [a for a in self.alerts 
                        if a.metric_id == metric.metric_id and 
                        not a.resolved and
                        a.timestamp > datetime.now() - timedelta(hours=1)]

        if recent_alerts:
            return  # Alert already exists

        # Create alert
        alert = Alert(
            alert_id=f"alert_{int(datetime.now().timestamp())}_{len(self.alerts)}",
            metric_id=metric.metric_id,
            severity=metric.status,
            message=f"{metric.name} is {metric.status.value}: {metric.value} {metric.unit}",
            timestamp=datetime.now()
        )

        self.alerts.append(alert)
        self._save_state()

        # Trigger alert handlers
        for handler in self.alert_handlers:
            try:
                handler(alert, metric)
            except Exception as e:
                self.logger.error(f"Alert handler error: {e}")

        self.logger.warning(f"⚠️ Alert: {alert.message}")

    def _attempt_remediation(self, metric: SystemMetric):
        """
        Attempt automatic remediation with enhanced strategies

        Uses multiple remediation approaches:
        1. Direct remediation handlers
        2. Predictive remediation (before threshold breach)
        3. Escalated remediation for critical issues
        """
        # Find remediation handler
        remediation_id = f"{metric.metric_type.value}_{metric.status.value}"

        remediation_attempted = False
        remediation_results = []

        # Try specific remediation
        if remediation_id in self.remediation_handlers:
            handler = self.remediation_handlers[remediation_id]
            try:
                result = handler(metric)
                remediation_attempted = True
                remediation_results.append({
                    "method": "direct_handler",
                    "remediation_id": remediation_id,
                    "result": result,
                    "success": result.get("status") != "failed"
                })
                self.logger.info(f"🔧 Remediation attempted: {remediation_id} - {result}")
            except Exception as e:
                self.logger.error(f"Remediation failed: {e}")
                remediation_results.append({
                    "method": "direct_handler",
                    "remediation_id": remediation_id,
                    "error": str(e),
                    "success": False
                })

        # Try generic remediation based on metric type
        if not remediation_attempted:
            generic_result = self._generic_remediation(metric)
            if generic_result:
                remediation_results.append(generic_result)

        # If critical and remediation failed, escalate
        if metric.status == SystemStatus.CRITICAL:
            success_count = sum(1 for r in remediation_results if r.get("success", False))
            if success_count == 0:
                self._escalate_remediation(metric, remediation_results)

        # Store remediation history
        self._store_remediation_history(metric, remediation_results)

    def _generic_remediation(self, metric: SystemMetric) -> Optional[Dict[str, Any]]:
        """Attempt generic remediation strategies"""
        try:
            if metric.metric_type == MetricType.MEMORY:
                # Try memory cleanup
                return self._remediate_memory_generic(metric)
            elif metric.metric_type == MetricType.CPU:
                # Try CPU optimization
                return self._remediate_cpu_generic(metric)
            elif metric.metric_type == MetricType.DISK:
                # Try disk cleanup
                return self._remediate_disk_generic(metric)
        except Exception as e:
            self.logger.error(f"Generic remediation error: {e}")

        return None

    def _remediate_memory_generic(self, metric: SystemMetric) -> Dict[str, Any]:
        """Generic memory remediation"""
        self.logger.info(f"🔧 Generic memory remediation for {metric.name}")
        # Could trigger garbage collection, process cleanup, etc.
        return {
            "method": "generic_memory",
            "status": "attempted",
            "recommendation": "Consider closing unused applications or restarting services"
        }

    def _remediate_cpu_generic(self, metric: SystemMetric) -> Dict[str, Any]:
        """Generic CPU remediation"""
        self.logger.info(f"🔧 Generic CPU remediation for {metric.name}")
        # Could trigger process priority adjustment, throttling, etc.
        return {
            "method": "generic_cpu",
            "status": "attempted",
            "recommendation": "Check for runaway processes or high CPU usage"
        }

    def _remediate_disk_generic(self, metric: SystemMetric) -> Dict[str, Any]:
        """Generic disk remediation"""
        self.logger.info(f"🔧 Generic disk remediation for {metric.name}")
        # Already has emergency cleanup integration
        return self._remediate_disk_full(metric)

    def _escalate_remediation(self, metric: SystemMetric, previous_results: List[Dict[str, Any]]):
        """Escalate remediation for critical issues"""
        self.logger.warning(
            f"🚨 ESCALATION: Critical metric {metric.name} requires manual intervention"
        )

        # Create high-priority alert
        escalation_alert = Alert(
            alert_id=f"escalation_{int(datetime.now().timestamp())}",
            metric_id=metric.metric_id,
            severity=SystemStatus.CRITICAL,
            message=f"ESCALATION: {metric.name} remediation failed. Manual intervention required.",
            timestamp=datetime.now()
        )

        self.alerts.append(escalation_alert)
        self._save_state()

        # Could trigger notifications, email alerts, etc.
        self.logger.error(
            f"🚨 CRITICAL ESCALATION: {metric.name} = {metric.value} {metric.unit} "
            f"(Previous remediation attempts: {len(previous_results)})"
        )

    def _store_remediation_history(self, metric: SystemMetric, results: List[Dict[str, Any]]):
        """Store remediation history for analysis"""
        if not hasattr(self, 'remediation_history'):
            self.remediation_history = []

        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "metric_id": metric.metric_id,
            "metric_name": metric.name,
            "metric_value": metric.value,
            "metric_status": metric.status.value,
            "remediation_results": results,
            "success": any(r.get("success", False) for r in results)
        }

        self.remediation_history.append(history_entry)

        # Keep last 200 remediation attempts
        if len(self.remediation_history) > 200:
            self.remediation_history = self.remediation_history[-200:]

    def start_monitoring(self, interval: int = 60):
        """Start proactive monitoring (MCU JARVIS style)"""
        if self.monitoring_active:
            self.logger.warning("Monitoring already active")
            return

        self.monitoring_active = True
        self.monitoring_interval = interval
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.logger.info(f"📊 Proactive monitoring started (interval: {interval}s)")

    def stop_monitoring(self):
        """Stop proactive monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        self.logger.info("📊 Proactive monitoring stopped")

    def _monitoring_loop(self):
        """Continuous monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                self._collect_system_metrics()

                # Predict failures
                self._predict_failures()

                # Check health
                self._check_system_health()

                # Sleep for monitoring interval
                time.sleep(self.monitoring_interval)
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(self.monitoring_interval)

    def _collect_system_metrics(self):
        """Collect system metrics using psutil and other tools"""
        try:
            import psutil

            # CPU
            cpu_usage = psutil.cpu_percent()
            self.record_metric(
                "system_cpu", MetricType.CPU, "CPU Usage", 
                cpu_usage, "%", threshold_warning=80.0, threshold_critical=90.0
            )

            # Memory
            mem = psutil.virtual_memory()
            self.record_metric(
                "system_memory", MetricType.MEMORY, "Memory Usage", 
                mem.percent, "%", threshold_warning=85.0, threshold_critical=95.0
            )

            # Disk (C:)
            disk = psutil.disk_usage('C:')
            self.record_metric(
                "system_disk_c", MetricType.DISK, "Disk Usage (C:)", 
                disk.percent, "%", threshold_warning=90.0, threshold_critical=95.0
            )

            # GPU (if available)
            gpu_usage = self._get_gpu_usage()
            if gpu_usage is not None:
                self.record_metric(
                    "system_gpu", MetricType.CUSTOM, "GPU Usage", 
                    float(gpu_usage), "%", threshold_warning=85.0, threshold_critical=95.0
                )

        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")

    def _get_gpu_usage(self) -> Optional[int]:
        """Try to get real GPU usage via nvidia-smi"""
        import subprocess
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                return int(result.stdout.strip())
        except:
            pass
        return None

    def _predict_failures(self):
        """
        Predict potential failures based on advanced trend analysis

        Uses multiple prediction algorithms:
        - Linear regression for trend detection
        - Rate of change analysis
        - Threshold proximity warnings
        - Anomaly detection
        """
        predictions = []

        for metric_id, metric_list in self.metrics.items():
            if len(metric_list) < 5:
                continue

            recent_metrics = metric_list[-10:]  # Use last 10 for better analysis
            values = [m.value for m in recent_metrics]
            timestamps = [m.timestamp for m in recent_metrics]

            # 1. Linear trend analysis
            trend = self._calculate_trend(values)
            if abs(trend) > 0.5:  # Significant trend
                predicted_value = values[-1] + (trend * 5)  # Predict 5 samples ahead

                # Check if predicted value exceeds thresholds
                latest_metric = recent_metrics[-1]
                if latest_metric.threshold_critical and predicted_value >= latest_metric.threshold_critical:
                    predictions.append({
                        "metric_id": metric_id,
                        "type": "critical_trend",
                        "current": values[-1],
                        "predicted": predicted_value,
                        "timeframe": "5 samples",
                        "confidence": min(abs(trend) * 2, 1.0)
                    })
                    self.logger.warning(
                        f"🔮 PREDICTIVE ALERT: {metric_id} trending toward critical "
                        f"({values[-1]:.1f}% → {predicted_value:.1f}%)"
                    )
                elif latest_metric.threshold_warning and predicted_value >= latest_metric.threshold_warning:
                    predictions.append({
                        "metric_id": metric_id,
                        "type": "warning_trend",
                        "current": values[-1],
                        "predicted": predicted_value,
                        "timeframe": "5 samples",
                        "confidence": min(abs(trend) * 1.5, 0.9)
                    })
                    self.logger.info(
                        f"🔮 Predictive: {metric_id} trending toward warning "
                        f"({values[-1]:.1f}% → {predicted_value:.1f}%)"
                    )

            # 2. Rate of change analysis
            if len(values) >= 3:
                recent_rate = (values[-1] - values[-3]) / 2  # Average rate over last 3 samples
                if abs(recent_rate) > 2.0:  # Significant rate of change
                    if recent_rate > 0 and values[-1] > 70:
                        predictions.append({
                            "metric_id": metric_id,
                            "type": "rapid_increase",
                            "current": values[-1],
                            "rate": recent_rate,
                            "confidence": min(abs(recent_rate) / 10, 0.8)
                        })
                        self.logger.info(
                            f"🔮 Predictive: {metric_id} showing rapid increase "
                            f"({recent_rate:.1f}% per sample, current: {values[-1]:.1f}%)"
                        )

            # 3. Threshold proximity warning
            latest_metric = recent_metrics[-1]
            if latest_metric.threshold_warning:
                proximity = (values[-1] / latest_metric.threshold_warning) * 100
                if 80 <= proximity < 100:  # Within 80-100% of warning threshold
                    predictions.append({
                        "metric_id": metric_id,
                        "type": "threshold_proximity",
                        "current": values[-1],
                        "threshold": latest_metric.threshold_warning,
                        "proximity": proximity,
                        "confidence": 0.7
                    })
                    self.logger.info(
                        f"🔮 Predictive: {metric_id} approaching warning threshold "
                        f"({proximity:.1f}% of {latest_metric.threshold_warning}%)"
                    )

            # 4. Anomaly detection (statistical outlier)
            if len(values) >= 7:
                mean = sum(values) / len(values)
                variance = sum((x - mean) ** 2 for x in values) / len(values)
                std_dev = variance ** 0.5

                if std_dev > 0:
                    z_score = abs((values[-1] - mean) / std_dev)
                    if z_score > 2.0:  # More than 2 standard deviations
                        predictions.append({
                            "metric_id": metric_id,
                            "type": "anomaly",
                            "current": values[-1],
                            "mean": mean,
                            "z_score": z_score,
                            "confidence": min(z_score / 3, 0.9)
                        })
                        self.logger.warning(
                            f"🔮 ANOMALY DETECTED: {metric_id} shows unusual value "
                            f"({values[-1]:.1f}%, z-score: {z_score:.2f})"
                        )

        # Store predictions for reporting
        if predictions:
            self._store_predictions(predictions)

    def _calculate_trend(self, values: List[float]) -> float:
        """
        Calculate linear trend using simple linear regression

        Returns:
            Trend slope (positive = increasing, negative = decreasing)
        """
        if len(values) < 2:
            return 0.0

        n = len(values)
        x = list(range(n))
        y = values

        # Calculate means
        x_mean = sum(x) / n
        y_mean = sum(y) / n

        # Calculate slope (trend)
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        slope = numerator / denominator
        return slope

    def _store_predictions(self, predictions: List[Dict[str, Any]]):
        """Store predictions for analysis"""
        # Store in metadata for later analysis
        if not hasattr(self, 'predictions_history'):
            self.predictions_history = []

        for prediction in predictions:
            prediction['timestamp'] = datetime.now().isoformat()
            self.predictions_history.append(prediction)

        # Keep last 100 predictions
        if len(self.predictions_history) > 100:
            self.predictions_history = self.predictions_history[-100:]

    def _check_system_health(self):
        """Check overall system health"""
        # Calculate health score
        total_metrics = 0
        healthy_metrics = 0

        for metric_list in self.metrics.values():
            if not metric_list: continue
            total_metrics += 1
            if metric_list[-1].status == SystemStatus.HEALTHY:
                healthy_metrics += 1

        health_score = (healthy_metrics / total_metrics * 100) if total_metrics > 0 else 100
        self.record_metric("overall_health", MetricType.CUSTOM, "Overall System Health", health_score, "%")

    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report with predictive analytics (MCU JARVIS style)"""
        recent_metrics = {}
        for metric_id, metrics in self.metrics.items():
            if metrics:
                recent_metrics[metric_id] = metrics[-1].to_dict()

        unresolved_alerts = [a for a in self.alerts if not a.resolved]

        status_counts = {
            status.value: len([m for metrics in self.metrics.values() for m in metrics[-100:] if m.status == status])
            for status in SystemStatus
        }

        # Get recent predictions
        recent_predictions = []
        if hasattr(self, 'predictions_history'):
            recent_predictions = self.predictions_history[-10:]

        # Get remediation statistics
        remediation_stats = {
            "total_attempts": 0,
            "successful": 0,
            "failed": 0
        }
        if hasattr(self, 'remediation_history'):
            remediation_stats["total_attempts"] = len(self.remediation_history)
            remediation_stats["successful"] = sum(
                1 for r in self.remediation_history if r.get("success", False)
            )
            remediation_stats["failed"] = remediation_stats["total_attempts"] - remediation_stats["successful"]

        # Calculate system health score
        total_recent_metrics = sum(len(m) for m in self.metrics.values())
        healthy_count = status_counts.get("healthy", 0)
        health_score = (healthy_count / total_recent_metrics * 100) if total_recent_metrics > 0 else 100

        return {
            "timestamp": datetime.now().isoformat(),
            "monitoring_active": self.monitoring_active,
            "monitoring_interval": self.monitoring_interval,
            "total_metrics": sum(len(m) for m in self.metrics.values()),
            "unique_metric_types": len(self.metrics),
            "status_counts": status_counts,
            "health_score": health_score,
            "total_alerts": len(self.alerts),
            "unresolved_alerts": len(unresolved_alerts),
            "critical_alerts": [a.to_dict() for a in unresolved_alerts if a.severity == SystemStatus.CRITICAL],
            "recent_metrics": recent_metrics,
            "recent_predictions": recent_predictions,
            "remediation_handlers": list(self.remediation_handlers.keys()),
            "remediation_statistics": remediation_stats,
            "predictive_analytics": {
                "enabled": True,
                "prediction_count": len(recent_predictions),
                "trend_analysis": "active"
            }
        }

    def resolve_alert(self, alert_id: str, resolution: str) -> bool:
        """Resolve an alert"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                alert.resolution = resolution
                alert.resolved_at = datetime.now()
                self._save_state()
                self.logger.info(f"✅ Resolved alert: {alert_id}")
                return True
        return False


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Proactive Monitoring")
        parser.add_argument("--status", action="store_true", help="Get status report")
        parser.add_argument("--start", action="store_true", help="Start monitoring")
        parser.add_argument("--stop", action="store_true", help="Stop monitoring")
        parser.add_argument("--record", nargs=6, metavar=("ID", "TYPE", "NAME", "VALUE", "UNIT", "THRESHOLD"), help="Record metric")

        args = parser.parse_args()

        monitoring = JARVISProactiveMonitoring()

        if args.status:
            report = monitoring.get_status_report()
            print(json.dumps(report, indent=2, default=str))

        elif args.start:
            monitoring.start_monitoring()
            print("✅ Monitoring started")

        elif args.stop:
            monitoring.stop_monitoring()
            print("✅ Monitoring stopped")

        elif args.record:
            metric_id, metric_type, name, value, unit, threshold = args.record
            metric = monitoring.record_metric(
                metric_id, MetricType(metric_type), name,
                float(value), unit, threshold_warning=float(threshold) if threshold else None
            )
            print(f"✅ Recorded metric: {metric.name} = {metric.value} {metric.unit} ({metric.status.value})")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()