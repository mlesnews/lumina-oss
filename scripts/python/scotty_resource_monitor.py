#!/usr/bin/env python3
"""
@SCOTTY's Resource Monitoring System
Integrates CPUID Hardware Monitor, Process Lasso, ParkControl, CfosSpeed
Monitors system logs, application logs, disk, and memory

Tags: #SCOTTY #RESOURCE_MONITORING #SYSTEM_HEALTH #ALERTS @SCOTTY @LUMINA
"""

import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("SCOTTYResourceMonitor")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("SCOTTYResourceMonitor")


@dataclass
class ResourceAlert:
    """Resource monitoring alert"""
    timestamp: str
    alert_type: str  # "cpu", "memory", "disk", "temperature", "log_error", etc.
    severity: str  # "critical", "warning", "info"
    message: str
    value: Optional[float] = None
    threshold: Optional[float] = None
    component: Optional[str] = None


class ResourceMonitor:
    """Comprehensive resource monitoring system"""

    def __init__(self, project_root: Path = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "scotty_resource_monitoring"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.alerts_file = self.data_dir / "alerts.jsonl"
        self.metrics_file = self.data_dir / "metrics.jsonl"
        self.config_file = self.data_dir / "config.json"

        # Monitoring tool paths
        self.tool_paths = self._detect_monitoring_tools()

        # Configuration
        self.config = self._load_config()

        logger.info("SCOTTY Resource Monitor initialized")
        logger.info(f"Monitoring tools detected: {len(self.tool_paths)}")

    def _detect_monitoring_tools(self) -> Dict[str, Optional[str]]:
        try:
            """Detect installed monitoring tools"""
            tools = {
                "cpuid_hwmonitor": None,
                "process_lasso": None,
                "parkcontrol": None,
                "cfosspeed": None
            }

            # CPUID Hardware Monitor
            cpuid_paths = [
                r"C:\Program Files\CPUID\HWMonitor\HWMonitor.exe",
                r"C:\Program Files (x86)\CPUID\HWMonitor\HWMonitor.exe",
                r"C:\Program Files\CPUID\HWMonitor Pro\HWMonitorPro.exe"
            ]
            for path in cpuid_paths:
                if Path(path).exists():
                    tools["cpuid_hwmonitor"] = path
                    break

            # Process Lasso
            lasso_paths = [
                r"C:\Program Files\Process Lasso\ProcessLasso.exe",
                r"C:\Program Files (x86)\Process Lasso\ProcessLasso.exe"
            ]
            for path in lasso_paths:
                if Path(path).exists():
                    tools["process_lasso"] = path
                    break

            # ParkControl
            parkcontrol_paths = [
                r"C:\Program Files\ParkControl\ParkControl.exe",
                r"C:\Program Files (x86)\ParkControl\ParkControl.exe"
            ]
            for path in parkcontrol_paths:
                if Path(path).exists():
                    tools["parkcontrol"] = path
                    break

            # CfosSpeed
            cfosspeed_paths = [
                r"C:\Program Files\cfosSpeed\cfosspeed.exe",
                r"C:\Program Files (x86)\cfosSpeed\cfosspeed.exe"
            ]
            for path in cfosspeed_paths:
                if Path(path).exists():
                    tools["cfosspeed"] = path
                    break

            return tools

        except Exception as e:
            self.logger.error(f"Error in _detect_monitoring_tools: {e}", exc_info=True)
            raise
    def _load_config(self) -> Dict:
        """Load monitoring configuration"""
        default_config = {
            "disk_threshold_percent": 80.0,
            "memory_threshold_percent": 90.0,
            "cpu_threshold_percent": 95.0,
            "temperature_threshold_celsius": 85.0,
            "check_interval_seconds": 60,
            "log_tail_lines": 100,
            "monitored_apps": [
                "Cursor.exe",
                "Code.exe",
                "Docker Desktop.exe",
                "neo.exe"
            ],
            "monitored_log_paths": [
                r"C:\ProgramData\Docker\logs",
                r"C:\Users\mlesn\AppData\Roaming\Cursor\logs",
                r"C:\Users\mlesn\AppData\Roaming\Code\logs"
            ],
            "system_log_sources": [
                "System",
                "Application",
                "Security"
            ]
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")

        return default_config

    def check_disk_space(self) -> List[ResourceAlert]:
        """Check disk space usage"""
        alerts = []

        try:
            result = subprocess.run(
                ['powershell', '-Command',
                 'Get-PSDrive -PSProvider FileSystem | Select-Object Name, Used, Free, @{Name="PercentFree";Expression={[math]::Round((($_.Free / ($_.Used + $_.Free)) * 100), 2)}} | ConvertTo-Json'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                import json
                drives = json.loads(result.stdout)
                if not isinstance(drives, list):
                    drives = [drives]

                threshold = self.config.get("disk_threshold_percent", 80.0)

                for drive in drives:
                    percent_used = 100 - drive.get("PercentFree", 0)
                    if percent_used >= threshold:
                        alerts.append(ResourceAlert(
                            timestamp=datetime.now().isoformat(),
                            alert_type="disk",
                            severity="critical" if percent_used >= 90 else "warning",
                            message=f"Disk {drive.get('Name')}: {percent_used:.1f}% used",
                            value=percent_used,
                            threshold=threshold,
                            component=f"Drive {drive.get('Name')}"
                        ))
        except Exception as e:
            logger.error(f"Disk check failed: {e}")

        return alerts

    def check_memory_usage(self) -> List[ResourceAlert]:
        """Check memory usage"""
        alerts = []

        try:
            result = subprocess.run(
                ['powershell', '-Command',
                 '$mem = Get-CimInstance Win32_OperatingSystem; $percent = [math]::Round((($mem.TotalVisibleMemorySize - $mem.FreePhysicalMemory) / $mem.TotalVisibleMemorySize) * 100, 2); Write-Output $percent'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                memory_percent = float(result.stdout.strip())
                threshold = self.config.get("memory_threshold_percent", 90.0)

                if memory_percent >= threshold:
                    alerts.append(ResourceAlert(
                        timestamp=datetime.now().isoformat(),
                        alert_type="memory",
                        severity="critical" if memory_percent >= 95 else "warning",
                        message=f"Memory usage: {memory_percent:.1f}%",
                        value=memory_percent,
                        threshold=threshold,
                        component="System RAM"
                    ))
        except Exception as e:
            logger.error(f"Memory check failed: {e}")

        return alerts

    def check_cpu_usage(self) -> List[ResourceAlert]:
        """Check CPU usage"""
        alerts = []

        try:
            result = subprocess.run(
                ['powershell', '-Command',
                 'Get-Counter "\\Processor(_Total)\\% Processor Time" | Select-Object -ExpandProperty CounterSamples | Select-Object -ExpandProperty CookedValue'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                cpu_percent = float(result.stdout.strip())
                threshold = self.config.get("cpu_threshold_percent", 95.0)

                if cpu_percent >= threshold:
                    alerts.append(ResourceAlert(
                        timestamp=datetime.now().isoformat(),
                        alert_type="cpu",
                        severity="warning",
                        message=f"CPU usage: {cpu_percent:.1f}%",
                        value=cpu_percent,
                        threshold=threshold,
                        component="CPU"
                    ))
        except Exception as e:
            logger.error(f"CPU check failed: {e}")

        return alerts

    def tail_system_logs(self) -> List[ResourceAlert]:
        """Tail Windows Event Logs for critical errors"""
        alerts = []

        log_sources = self.config.get("system_log_sources", ["System", "Application"])
        cutoff_time = datetime.now() - timedelta(minutes=5)

        for log_source in log_sources:
            try:
                result = subprocess.run(
                    ['powershell', '-Command',
                     f'Get-WinEvent -LogName {log_source} -MaxEvents 10 -ErrorAction SilentlyContinue | Where-Object {{$_.LevelDisplayName -eq "Error" -or $_.LevelDisplayName -eq "Critical"}} | Select-Object TimeCreated, LevelDisplayName, Message | ConvertTo-Json'],
                    capture_output=True,
                    text=True,
                    timeout=15
                )

                if result.returncode == 0 and result.stdout.strip():
                    import json
                    events = json.loads(result.stdout)
                    if not isinstance(events, list):
                        events = [events]

                    for event in events:
                        event_time = datetime.fromisoformat(event.get("TimeCreated", "").replace("Z", "+00:00"))
                        if event_time >= cutoff_time:
                            alerts.append(ResourceAlert(
                                timestamp=datetime.now().isoformat(),
                                alert_type="log_error",
                                severity="critical" if event.get("LevelDisplayName") == "Critical" else "warning",
                                message=f"[{log_source}] {event.get('Message', '')[:200]}",
                                component=log_source
                            ))
            except Exception as e:
                logger.debug(f"Log tailing failed for {log_source}: {e}")

        return alerts

    def tail_application_logs(self) -> List[ResourceAlert]:
        """Tail application logs for errors"""
        alerts = []

        log_paths = self.config.get("monitored_log_paths", [])

        for log_path in log_paths:
            log_dir = Path(log_path)
            if not log_dir.exists():
                continue

            # Find recent log files
            log_files = list(log_dir.glob("*.log")) + list(log_dir.glob("*.txt"))
            log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            for log_file in log_files[:5]:  # Check last 5 log files
                try:
                    # Read last N lines
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        recent_lines = lines[-self.config.get("log_tail_lines", 100):]

                        # Look for error patterns
                        for line in recent_lines:
                            line_lower = line.lower()
                            if any(keyword in line_lower for keyword in ["error", "exception", "failed", "critical", "fatal"]):
                                alerts.append(ResourceAlert(
                                    timestamp=datetime.now().isoformat(),
                                    alert_type="app_log_error",
                                    severity="warning",
                                    message=f"[{log_file.name}] {line.strip()[:200]}",
                                    component=str(log_file)
                                ))
                                break  # One alert per log file
                except Exception as e:
                    logger.debug(f"Failed to read log file {log_file}: {e}")

        return alerts

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect all resource metrics"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "disk": {},
            "memory": {},
            "cpu": {},
            "processes": {},
            "tools_status": {}
        }

        # Disk metrics
        try:
            result = subprocess.run(
                ['powershell', '-Command',
                 'Get-PSDrive -PSProvider FileSystem | Select-Object Name, Used, Free | ConvertTo-Json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                import json
                drives = json.loads(result.stdout)
                if not isinstance(drives, list):
                    drives = [drives]
                metrics["disk"] = {d.get("Name"): {"used": d.get("Used"), "free": d.get("Free")} for d in drives}
        except:
            pass

        # Memory metrics
        try:
            result = subprocess.run(
                ['powershell', '-Command',
                 '$mem = Get-CimInstance Win32_OperatingSystem; @{Total=$mem.TotalVisibleMemorySize; Free=$mem.FreePhysicalMemory; Used=($mem.TotalVisibleMemorySize - $mem.FreePhysicalMemory)} | ConvertTo-Json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                import json
                metrics["memory"] = json.loads(result.stdout)
        except:
            pass

        # CPU metrics
        try:
            result = subprocess.run(
                ['powershell', '-Command',
                 'Get-Counter "\\Processor(_Total)\\% Processor Time" | Select-Object -ExpandProperty CounterSamples | Select-Object -ExpandProperty CookedValue'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                metrics["cpu"] = {"usage_percent": float(result.stdout.strip())}
        except:
            pass

        # Tool status
        for tool_name, tool_path in self.tool_paths.items():
            if tool_path:
                # Check if process is running
                try:
                    result = subprocess.run(
                        ['powershell', '-Command',
                         f'Get-Process -Name "{Path(tool_path).stem}" -ErrorAction SilentlyContinue | Select-Object -First 1'],
                        capture_output=True,
                        timeout=5
                    )
                    metrics["tools_status"][tool_name] = {
                        "installed": True,
                        "running": result.returncode == 0,
                        "path": tool_path
                    }
                except:
                    metrics["tools_status"][tool_name] = {
                        "installed": True,
                        "running": False,
                        "path": tool_path
                    }
            else:
                metrics["tools_status"][tool_name] = {
                    "installed": False,
                    "running": False,
                    "path": None
                }

        return metrics

    def monitor_cycle(self) -> List[ResourceAlert]:
        """Run one monitoring cycle"""
        logger.info("Running resource monitoring cycle...")

        all_alerts = []

        # Check resources
        all_alerts.extend(self.check_disk_space())
        all_alerts.extend(self.check_memory_usage())
        all_alerts.extend(self.check_cpu_usage())

        # Check logs
        all_alerts.extend(self.tail_system_logs())
        all_alerts.extend(self.tail_application_logs())

        # Collect metrics
        metrics = self.collect_metrics()

        # Save metrics
        try:
            with open(self.metrics_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(metrics) + '\n')
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")

        # Save alerts
        for alert in all_alerts:
            try:
                with open(self.alerts_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(asdict(alert)) + '\n')
            except Exception as e:
                logger.error(f"Failed to save alert: {e}")

        # Log alerts
        for alert in all_alerts:
            if alert.severity == "critical":
                logger.error(f"🚨 CRITICAL: {alert.message}")
            elif alert.severity == "warning":
                logger.warning(f"⚠️  WARNING: {alert.message}")
            else:
                logger.info(f"ℹ️  INFO: {alert.message}")

        return all_alerts

    def run_continuous(self, interval: int = None):
        """Run continuous monitoring"""
        if interval is None:
            interval = self.config.get("check_interval_seconds", 60)

        logger.info(f"Starting continuous monitoring (interval: {interval}s)")
        logger.info("Press Ctrl+C to stop")

        try:
            while True:
                alerts = self.monitor_cycle()
                if alerts:
                    logger.info(f"Generated {len(alerts)} alerts")
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Monitoring stopped")


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="@SCOTTY's Resource Monitor")
    parser.add_argument("--daemon", action="store_true", help="Run continuous monitoring")
    parser.add_argument("--interval", type=int, help="Check interval in seconds")
    parser.add_argument("--once", action="store_true", help="Run one check cycle")

    args = parser.parse_args()

    monitor = ResourceMonitor()

    if args.daemon:
        monitor.run_continuous(args.interval)
    elif args.once:
        alerts = monitor.monitor_cycle()
        print(f"\n📊 Monitoring cycle complete")
        print(f"   Alerts generated: {len(alerts)}")
        if alerts:
            print("\nAlerts:")
            for alert in alerts:
                print(f"  [{alert.severity.upper()}] {alert.message}")
    else:
        # Show current status
        metrics = monitor.collect_metrics()
        print("\n📊 Current Resource Status:")
        print(f"   CPU Usage: {metrics.get('cpu', {}).get('usage_percent', 'N/A')}%")
        if metrics.get('memory'):
            mem = metrics['memory']
            total_gb = mem.get('Total', 0) / (1024**3)
            used_gb = mem.get('Used', 0) / (1024**3)
            print(f"   Memory: {used_gb:.1f}GB / {total_gb:.1f}GB")
        print(f"\n   Monitoring Tools:")
        for tool, status in metrics.get('tools_status', {}).items():
            status_icon = "✅" if status.get('running') else ("⚠️" if status.get('installed') else "❌")
            print(f"     {status_icon} {tool}: {'Running' if status.get('running') else ('Installed' if status.get('installed') else 'Not Found')}")


if __name__ == "__main__":


    main()