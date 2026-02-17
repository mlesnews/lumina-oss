#!/usr/bin/env python3
"""
JARVIS All Systems Check - "Rock, Paper, Lizard, Spock" Game
Comprehensive check of ALL queues, localhost, homelab, devices, OS, apps, logs, notifications, alerts

Tags: #JARVIS #ALL_SYSTEMS #COMPREHENSIVE #ROCK_PAPER_LIZARD_SPOCK @DOIT
"""

import sys
import json
import platform
import psutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISAllSystemsCheck")

PROJECT_ROOT = script_dir.parent.parent


@dataclass
class SystemStatus:
    """System status result"""
    category: str
    status: str  # "ok", "warning", "error", "critical"
    message: str
    details: Dict[str, Any]
    timestamp: str


class JARVISAllSystemsChecker:
    """Comprehensive system checker for all domains"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = PROJECT_ROOT
        self.project_root = Path(project_root)
        self.results: List[SystemStatus] = []

    def check_all_ide_queues(self) -> List[SystemStatus]:
        """Check all IDE queues"""
        statuses = []

        try:
            from jarvis_ide_queue_monitor import JARVISIDEQueueMonitor
            monitor = JARVISIDEQueueMonitor(self.project_root)
            summary = monitor.get_queue_summary()

            total_items = summary.get('total_items', 0)
            queue_counts = summary.get('queue_counts', {})

            problems_count = queue_counts.get('problems', 0)
            tasks_count = queue_counts.get('tasks', 0)
            output_count = queue_counts.get('output', 0)

            if problems_count > 2000:
                status = "critical"
                message = f"🚨 CRITICAL: {problems_count} problems in queue"
            elif problems_count > 100:
                status = "warning"
                message = f"⚠️  {problems_count} problems in queue"
            else:
                status = "ok"
                message = f"✅ {problems_count} problems in queue"

            statuses.append(SystemStatus(
                category="IDE_QUEUES",
                status=status,
                message=message,
                details={
                    "total_items": total_items,
                    "problems": problems_count,
                    "tasks": tasks_count,
                    "output": output_count,
                    "all_queues": queue_counts
                },
                timestamp=datetime.now().isoformat()
            ))
        except Exception as e:
            statuses.append(SystemStatus(
                category="IDE_QUEUES",
                status="error",
                message=f"❌ Error checking IDE queues: {e}",
                details={"error": str(e)},
                timestamp=datetime.now().isoformat()
            ))

        return statuses

    def check_localhost(self) -> List[SystemStatus]:
        """Check localhost system status"""
        statuses = []

        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_status = "ok" if cpu_percent < 80 else "warning" if cpu_percent < 95 else "critical"

            # Memory
            memory = psutil.virtual_memory()
            memory_status = "ok" if memory.percent < 80 else "warning" if memory.percent < 95 else "critical"

            # Disk
            disk = psutil.disk_usage('/')
            disk_status = "ok" if disk.percent < 80 else "warning" if disk.percent < 95 else "critical"

            statuses.append(SystemStatus(
                category="LOCALHOST",
                status="ok" if all(s == "ok" for s in [cpu_status, memory_status, disk_status]) else "warning",
                message=f"🖥️  Localhost: CPU {cpu_percent:.1f}%, RAM {memory.percent:.1f}%, Disk {disk.percent:.1f}%",
                details={
                    "cpu_percent": cpu_percent,
                    "cpu_status": cpu_status,
                    "memory_percent": memory.percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "memory_status": memory_status,
                    "disk_percent": disk.percent,
                    "disk_free_gb": disk.free / (1024**3),
                    "disk_status": disk_status
                },
                timestamp=datetime.now().isoformat()
            ))
        except Exception as e:
            statuses.append(SystemStatus(
                category="LOCALHOST",
                status="error",
                message=f"❌ Error checking localhost: {e}",
                details={"error": str(e)},
                timestamp=datetime.now().isoformat()
            ))

        return statuses

    def check_os(self) -> List[SystemStatus]:
        """Check OS status"""
        statuses = []

        try:
            os_name = platform.system()
            os_version = platform.version()
            os_release = platform.release()
            arch = platform.machine()

            # Check for critical Windows updates (if Windows)
            update_status = "unknown"
            if os_name == "Windows":
                try:
                    import subprocess
                    result = subprocess.run(
                        ["powershell", "-Command", "Get-WindowsUpdate"],
                        capture_output=True,
                        timeout=5
                    )
                    update_status = "checked" if result.returncode == 0 else "unknown"
                except:
                    update_status = "unknown"

            statuses.append(SystemStatus(
                category="OS",
                status="ok",
                message=f"💻 OS: {os_name} {os_release} ({arch})",
                details={
                    "os_name": os_name,
                    "os_version": os_version,
                    "os_release": os_release,
                    "architecture": arch,
                    "update_status": update_status
                },
                timestamp=datetime.now().isoformat()
            ))
        except Exception as e:
            statuses.append(SystemStatus(
                category="OS",
                status="error",
                message=f"❌ Error checking OS: {e}",
                details={"error": str(e)},
                timestamp=datetime.now().isoformat()
            ))

        return statuses

    def check_applications(self) -> List[SystemStatus]:
        """Check applications and services"""
        statuses = []

        try:
            # Check running processes
            processes = []
            critical_processes = ["Cursor.exe", "python.exe", "code.exe"]

            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    if any(cp.lower() in proc_info['name'].lower() for cp in critical_processes):
                        processes.append({
                            "name": proc_info['name'],
                            "pid": proc_info['pid'],
                            "cpu": proc_info.get('cpu_percent', 0),
                            "memory": proc_info.get('memory_percent', 0)
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            cursor_running = any("cursor" in p['name'].lower() for p in processes)
            python_running = any("python" in p['name'].lower() for p in processes)

            statuses.append(SystemStatus(
                category="APPLICATIONS",
                status="ok" if cursor_running and python_running else "warning",
                message=f"📱 Apps: Cursor {'✅' if cursor_running else '❌'}, Python {'✅' if python_running else '❌'}",
                details={
                    "cursor_running": cursor_running,
                    "python_running": python_running,
                    "critical_processes": processes,
                    "total_processes": len(processes)
                },
                timestamp=datetime.now().isoformat()
            ))
        except Exception as e:
            statuses.append(SystemStatus(
                category="APPLICATIONS",
                status="error",
                message=f"❌ Error checking applications: {e}",
                details={"error": str(e)},
                timestamp=datetime.now().isoformat()
            ))

        return statuses

    def check_logs(self) -> List[SystemStatus]:
        """Check logs for errors and warnings"""
        statuses = []

        try:
            log_dirs = [
                self.project_root / "data" / "logs",
                self.project_root / "data" / "ide_problems",
                self.project_root / "data" / "health_checks"
            ]

            error_count = 0
            warning_count = 0
            recent_errors = []

            for log_dir in log_dirs:
                if log_dir.exists():
                    for log_file in log_dir.glob("*.log"):
                        try:
                            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                                lines = f.readlines()
                                for line in lines[-100:]:  # Last 100 lines
                                    line_lower = line.lower()
                                    if "error" in line_lower or "exception" in line_lower:
                                        error_count += 1
                                        if len(recent_errors) < 10:
                                            recent_errors.append(line.strip()[:100])
                                    elif "warning" in line_lower:
                                        warning_count += 1
                        except Exception:
                            pass

            if error_count > 100:
                status = "critical"
                message = f"🚨 CRITICAL: {error_count} errors in logs"
            elif error_count > 10:
                status = "warning"
                message = f"⚠️  {error_count} errors, {warning_count} warnings in logs"
            else:
                status = "ok"
                message = f"✅ Logs: {error_count} errors, {warning_count} warnings"

            statuses.append(SystemStatus(
                category="LOGS",
                status=status,
                message=message,
                details={
                    "error_count": error_count,
                    "warning_count": warning_count,
                    "recent_errors": recent_errors[:5]
                },
                timestamp=datetime.now().isoformat()
            ))
        except Exception as e:
            statuses.append(SystemStatus(
                category="LOGS",
                status="error",
                message=f"❌ Error checking logs: {e}",
                details={"error": str(e)},
                timestamp=datetime.now().isoformat()
            ))

        return statuses

    def check_notifications_alerts(self) -> List[SystemStatus]:
        """Check notifications and alerts"""
        statuses = []

        try:
            # Check IDE problems alerts
            alerts_file = self.project_root / "data" / "ide_problems" / "alerts.json"
            alert_count = 0
            alerts = []

            if alerts_file.exists():
                try:
                    with open(alerts_file, 'r', encoding='utf-8') as f:
                        alerts_data = json.load(f)
                        if isinstance(alerts_data, dict) and 'alerts' in alerts_data:
                            alerts = alerts_data['alerts']
                            alert_count = len(alerts)
                except Exception:
                    pass

            # Check health check results
            health_checks_dir = self.project_root / "data" / "health_checks"
            health_issues = 0
            if health_checks_dir.exists():
                for health_file in health_checks_dir.glob("*.json"):
                    try:
                        with open(health_file, 'r', encoding='utf-8') as f:
                            health_data = json.load(f)
                            if isinstance(health_data, dict):
                                if health_data.get('status') in ['error', 'critical', 'warning']:
                                    health_issues += 1
                    except Exception:
                        pass

            total_alerts = alert_count + health_issues

            if total_alerts > 10:
                status = "critical"
                message = f"🚨 CRITICAL: {total_alerts} alerts active"
            elif total_alerts > 0:
                status = "warning"
                message = f"⚠️  {total_alerts} alerts active"
            else:
                status = "ok"
                message = f"✅ No active alerts"

            statuses.append(SystemStatus(
                category="NOTIFICATIONS_ALERTS",
                status=status,
                message=message,
                details={
                    "alert_count": alert_count,
                    "health_issues": health_issues,
                    "total_alerts": total_alerts,
                    "recent_alerts": alerts[:5] if alerts else []
                },
                timestamp=datetime.now().isoformat()
            ))
        except Exception as e:
            statuses.append(SystemStatus(
                category="NOTIFICATIONS_ALERTS",
                status="error",
                message=f"❌ Error checking alerts: {e}",
                details={"error": str(e)},
                timestamp=datetime.now().isoformat()
            ))

        return statuses

    def check_homelab_devices(self) -> List[SystemStatus]:
        """Check homelab devices (placeholder - would need actual device access)"""
        statuses = []

        try:
            # Check for NAS connectivity
            nas_config = self.project_root / "config" / "nas_config.json"
            nas_available = False

            if nas_config.exists():
                try:
                    with open(nas_config, 'r', encoding='utf-8') as f:
                        nas_data = json.load(f)
                        # Check if NAS is configured
                        nas_available = bool(nas_data.get('host') or nas_data.get('ip'))
                except Exception:
                    pass

            # Check MCP servers (homelab services)
            mcp_configs = list((self.project_root / "config").glob("mcp_config*.json"))
            mcp_count = len(mcp_configs)

            statuses.append(SystemStatus(
                category="HOMELAB_DEVICES",
                status="ok" if nas_available or mcp_count > 0 else "warning",
                message=f"🏠 Homelab: NAS {'✅' if nas_available else '❌'}, {mcp_count} MCP configs",
                details={
                    "nas_available": nas_available,
                    "mcp_configs": mcp_count,
                    "mcp_files": [str(f.name) for f in mcp_configs[:5]]
                },
                timestamp=datetime.now().isoformat()
            ))
        except Exception as e:
            statuses.append(SystemStatus(
                category="HOMELAB_DEVICES",
                status="error",
                message=f"❌ Error checking homelab: {e}",
                details={"error": str(e)},
                timestamp=datetime.now().isoformat()
            ))

        return statuses

    def check_all_systems(self) -> Dict[str, Any]:
        """Check ALL systems"""
        logger.info("="*80)
        logger.info("🎮 ROCK, PAPER, LIZARD, SPOCK - ALL SYSTEMS CHECK")
        logger.info("="*80)
        logger.info("")

        all_statuses = []

        # Check all categories
        logger.info("📊 Checking IDE Queues...")
        all_statuses.extend(self.check_all_ide_queues())

        logger.info("🖥️  Checking Localhost...")
        all_statuses.extend(self.check_localhost())

        logger.info("💻 Checking OS...")
        all_statuses.extend(self.check_os())

        logger.info("📱 Checking Applications...")
        all_statuses.extend(self.check_applications())

        logger.info("📝 Checking Logs...")
        all_statuses.extend(self.check_logs())

        logger.info("🔔 Checking Notifications & Alerts...")
        all_statuses.extend(self.check_notifications_alerts())

        logger.info("🏠 Checking Homelab & Devices...")
        all_statuses.extend(self.check_homelab_devices())

        self.results = all_statuses

        # Generate summary
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_checks": len(all_statuses),
            "status_counts": {
                "ok": len([s for s in all_statuses if s.status == "ok"]),
                "warning": len([s for s in all_statuses if s.status == "warning"]),
                "error": len([s for s in all_statuses if s.status == "error"]),
                "critical": len([s for s in all_statuses if s.status == "critical"])
            },
            "categories": {}
        }

        for status in all_statuses:
            if status.category not in summary["categories"]:
                summary["categories"][status.category] = []
            summary["categories"][status.category].append({
                "status": status.status,
                "message": status.message,
                "details": status.details
            })

        return summary

    def get_status_report(self) -> str:
        """Get human-readable status report"""
        if not self.results:
            self.check_all_systems()

        lines = []
        lines.append("="*80)
        lines.append("🎮 ROCK, PAPER, LIZARD, SPOCK - ALL SYSTEMS STATUS")
        lines.append("="*80)
        lines.append("")
        lines.append(f"**Timestamp:** {datetime.now().isoformat()}")
        lines.append("")

        # Group by category
        categories = {}
        for status in self.results:
            if status.category not in categories:
                categories[status.category] = []
            categories[status.category].append(status)

        # Status icons
        status_icons = {
            "ok": "✅",
            "warning": "⚠️",
            "error": "❌",
            "critical": "🚨"
        }

        for category, statuses in categories.items():
            lines.append(f"## {category.replace('_', ' ').title()}")
            lines.append("")
            for status in statuses:
                icon = status_icons.get(status.status, "❓")
                lines.append(f"{icon} **{status.status.upper()}:** {status.message}")
            lines.append("")

        # Summary
        ok_count = len([s for s in self.results if s.status == "ok"])
        warning_count = len([s for s in self.results if s.status == "warning"])
        error_count = len([s for s in self.results if s.status == "error"])
        critical_count = len([s for s in self.results if s.status == "critical"])

        lines.append("="*80)
        lines.append("📊 **SUMMARY**")
        lines.append("="*80)
        lines.append(f"✅ OK: {ok_count}")
        lines.append(f"⚠️  Warnings: {warning_count}")
        lines.append(f"❌ Errors: {error_count}")
        lines.append(f"🚨 Critical: {critical_count}")
        lines.append("")

        if critical_count > 0:
            lines.append("🚨 **CRITICAL ISSUES DETECTED - IMMEDIATE ACTION REQUIRED**")
        elif error_count > 0:
            lines.append("⚠️  **Errors detected - Review required**")
        elif warning_count > 0:
            lines.append("⚠️  **Warnings detected - Monitor closely**")
        else:
            lines.append("✅ **All systems operational**")

        return "\n".join(lines)

    def save_report(self) -> Path:
        try:
            """Save comprehensive report to file"""
            report_file = self.project_root / "data" / "health_checks" / f"all_systems_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_file.parent.mkdir(parents=True, exist_ok=True)

            report = {
                "timestamp": datetime.now().isoformat(),
                "results": [asdict(status) for status in self.results],
                "summary": {
                    "total": len(self.results),
                    "ok": len([s for s in self.results if s.status == "ok"]),
                    "warning": len([s for s in self.results if s.status == "warning"]),
                    "error": len([s for s in self.results if s.status == "error"]),
                    "critical": len([s for s in self.results if s.status == "critical"])
                }
            }

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Report saved to {report_file}")
            return report_file


        except Exception as e:
            self.logger.error(f"Error in save_report: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS All Systems Check")
    parser.add_argument('--check', action='store_true', help='Run all system checks')
    parser.add_argument('--report', action='store_true', help='Show status report')
    parser.add_argument('--save', action='store_true', help='Save report to file')

    args = parser.parse_args()

    checker = JARVISAllSystemsChecker()

    if args.check or args.report or args.save or not any([args.check, args.report, args.save]):
        checker.check_all_systems()

        if args.report or args.save or not any([args.check, args.report, args.save]):
            print(checker.get_status_report())

        if args.save:
            report_file = checker.save_report()
            print(f"\n✅ Report saved to {report_file}")


if __name__ == "__main__":


    main()