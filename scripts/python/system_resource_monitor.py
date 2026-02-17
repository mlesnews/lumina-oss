#!/usr/bin/env python3
"""
System Resource Monitor
Monitors CPU, memory, disk I/O to detect bottlenecks

Fans spinning up/down = GRAND RED FLAG of overtaxing system resources
Bottlenecking @BAL @LOGIC

Tags: #SYSTEM #RESOURCES #MONITORING #BOTTLENECK #PERFORMANCE
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
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

logger = get_logger("SystemResourceMonitor")


class SystemResourceMonitor:
    """
    System Resource Monitor

    Detects:
    - High CPU usage (fans spinning)
    - High memory usage (bottleneck)
    - Disk I/O bottlenecks
    - System resource warnings
    """

    def __init__(self, project_root: Path):
        """Initialize resource monitor"""
        self.project_root = project_root
        self.logger = logger

        # Data paths
        self.data_path = project_root / "data"
        self.monitoring_path = self.data_path / "system_monitoring"
        self.monitoring_path.mkdir(parents=True, exist_ok=True)

        self.logger.info("⚙️  System Resource Monitor initialized")
        self.logger.warning("⚠️  FANS SPINNING = GRAND RED FLAG - Overtaxing system resources!")

    def check_resources(self) -> Dict[str, Any]:
        """Check system resources"""
        try:
            import psutil

            # Get current metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk_io = psutil.disk_io_counters()

            # Check for warnings
            warnings = []
            critical = []

            if cpu_percent > 80:
                critical.append(f"🔴 CRITICAL: CPU at {cpu_percent:.1f}% - FANS SPINNING!")
            elif cpu_percent > 60:
                warnings.append(f"🟡 WARNING: CPU at {cpu_percent:.1f}% - Approaching bottleneck")

            if memory.percent > 85:
                critical.append(f"🔴 CRITICAL: Memory at {memory.percent:.1f}% - System bottleneck!")
            elif memory.percent > 70:
                warnings.append(f"🟡 WARNING: Memory at {memory.percent:.1f}% - High usage")

            return {
                "timestamp": datetime.now().isoformat(),
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count(),
                    "status": "critical" if cpu_percent > 80 else "warning" if cpu_percent > 60 else "ok"
                },
                "memory": {
                    "percent": memory.percent,
                    "total_gb": memory.total / (1024**3),
                    "available_gb": memory.available / (1024**3),
                    "used_gb": memory.used / (1024**3),
                    "status": "critical" if memory.percent > 85 else "warning" if memory.percent > 70 else "ok"
                },
                "disk_io": {
                    "read_bytes": disk_io.read_bytes if disk_io else 0,
                    "write_bytes": disk_io.write_bytes if disk_io else 0,
                    "read_count": disk_io.read_count if disk_io else 0,
                    "write_count": disk_io.write_count if disk_io else 0
                },
                "warnings": warnings,
                "critical": critical,
                "overall_status": "critical" if critical else "warning" if warnings else "ok"
            }
        except ImportError:
            return {
                "timestamp": datetime.now().isoformat(),
                "error": "psutil not installed",
                "note": "Install with: pip install psutil",
                "overall_status": "unknown"
            }
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "overall_status": "error"
            }

    def get_status_display(self) -> str:
        """Get formatted status display"""
        resources = self.check_resources()

        if "error" in resources:
            return f"⚠️  System monitoring unavailable: {resources.get('error', 'Unknown error')}"

        markdown = []
        markdown.append("## ⚙️ System Resource Monitor")
        markdown.append("")
        markdown.append(f"**Status:** {resources['overall_status'].upper()}")
        markdown.append("")

        # CPU
        cpu = resources.get("cpu", {})
        cpu_status = "🔴" if cpu.get("status") == "critical" else "🟡" if cpu.get("status") == "warning" else "✅"
        markdown.append(f"{cpu_status} **CPU:** {cpu.get('percent', 0):.1f}% ({cpu.get('count', 0)} cores)")
        markdown.append("")

        # Memory
        memory = resources.get("memory", {})
        memory_status = "🔴" if memory.get("status") == "critical" else "🟡" if memory.get("status") == "warning" else "✅"
        markdown.append(f"{memory_status} **Memory:** {memory.get('percent', 0):.1f}% ({memory.get('used_gb', 0):.2f}GB / {memory.get('total_gb', 0):.2f}GB)")
        markdown.append("")

        # Critical warnings
        critical = resources.get("critical", [])
        if critical:
            markdown.append("### 🔴 CRITICAL WARNINGS")
            markdown.append("")
            markdown.append("**FANS SPINNING = GRAND RED FLAG - Overtaxing system resources!**")
            markdown.append("")
            for warning in critical:
                markdown.append(f"- {warning}")
            markdown.append("")
            markdown.append("**Action Required:** Reduce system load immediately!")
            markdown.append("")

        # Warnings
        warnings = resources.get("warnings", [])
        if warnings:
            markdown.append("### 🟡 Warnings")
            markdown.append("")
            for warning in warnings:
                markdown.append(f"- {warning}")
            markdown.append("")

        return "\n".join(markdown)


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="System Resource Monitor")
        parser.add_argument("--check", action="store_true", help="Check system resources")
        parser.add_argument("--status", action="store_true", help="Show status display")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        monitor = SystemResourceMonitor(project_root)

        if args.check or args.status:
            if args.json:
                resources = monitor.check_resources()
                print(json.dumps(resources, indent=2, default=str))
            else:
                display = monitor.get_status_display()
                print(display)
        else:
            display = monitor.get_status_display()
            print(display)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()