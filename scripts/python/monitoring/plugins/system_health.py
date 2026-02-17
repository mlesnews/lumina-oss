"""
System Health Monitor Plugin

Monitors system health (CPU, memory, disk, processes).
Consolidates: jarvis_compound_log_health_monitor.py, system_resource_diagnostic.py
"""

import sys
import psutil
from pathlib import Path
from typing import Dict, Any

script_dir = Path(__file__).parent.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from monitoring.monitor import MonitorPlugin, MonitorType, MonitorResult
except ImportError:
    from ..monitor import MonitorPlugin, MonitorType, MonitorResult

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SystemHealthMonitorPlugin")


class SystemHealthMonitorPlugin(MonitorPlugin):
    """Monitor system health"""

    def __init__(self):
        super().__init__(
            monitor_type=MonitorType.SYSTEM_HEALTH,
            name="System Health Monitor",
            description="Monitors CPU, memory, disk, and process health"
        )

    def get_interval(self) -> float:
        """Get monitoring interval"""
        return 30.0  # Check every 30 seconds

    def monitor(self, **kwargs) -> MonitorResult:
        """Monitor system health"""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # Count Python processes
            python_processes = 0
            for proc in psutil.process_iter(['name']):
                try:
                    if 'python' in proc.info['name'].lower():
                        python_processes += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Determine status
            status = "healthy"
            warnings = []

            if cpu_percent > 80:
                status = "warning"
                warnings.append(f"High CPU: {cpu_percent:.1f}%")
            elif cpu_percent > 95:
                status = "critical"
                warnings.append(f"Critical CPU: {cpu_percent:.1f}%")

            if memory.percent > 85:
                status = "warning" if status == "healthy" else status
                warnings.append(f"High memory: {memory.percent:.1f}%")
            elif memory.percent > 95:
                status = "critical"
                warnings.append(f"Critical memory: {memory.percent:.1f}%")

            if disk.percent > 90:
                status = "warning" if status == "healthy" else status
                warnings.append(f"High disk usage: {disk.percent:.1f}%")

            if python_processes > 50:
                status = "warning" if status == "healthy" else status
                warnings.append(f"Many Python processes: {python_processes}")
            elif python_processes > 100:
                status = "critical"
                warnings.append(f"Too many Python processes: {python_processes}")

            message = "System healthy" if status == "healthy" else "; ".join(warnings)

            return MonitorResult(
                monitor_type=self.monitor_type,
                status=status,
                message=message,
                metrics={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_percent": disk.percent,
                    "disk_free_gb": disk.free / (1024**3),
                    "python_processes": python_processes
                }
            )

        except Exception as e:
            return MonitorResult(
                monitor_type=self.monitor_type,
                status="unknown",
                message=f"Error monitoring system: {e}",
                metrics={"error": str(e)}
            )

    def get_status(self) -> MonitorResult:
        """Get current status"""
        return self.monitor()
