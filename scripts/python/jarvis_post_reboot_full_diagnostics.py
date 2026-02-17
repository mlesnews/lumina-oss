#!/usr/bin/env python3
"""
JARVIS Post-Reboot Full Diagnostics
Comprehensive system diagnostics after reboot, specifically for Cursor IDE serialization errors.

This script runs after PC reboot to:
1. Verify system health
2. Check Cursor IDE status
3. Run full diagnostics
4. Check for serialization error patterns
5. Generate comprehensive diagnostic report

Tags: #JARVIS #REBOOT #DIAGNOSTICS #CURSOR_IDE #SERIALIZATION_ERROR @AIMLSEA
"""

import sys
import json
import subprocess
import psutil
import platform
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

# Import JARVIS diagnostic modules
try:
    from jarvis_realtime_diagnostics import JARVISRealtimeDiagnostics
except ImportError:
    JARVISRealtimeDiagnostics = None

logger = get_logger("JARVISPostRebootDiagnostics")

PROJECT_ROOT = script_dir.parent.parent


class JARVISPostRebootDiagnostics:
    """Comprehensive post-reboot diagnostics for Cursor IDE serialization errors"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = PROJECT_ROOT
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "diagnostics"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize real-time diagnostics if available
        self.realtime_diag = None
        if JARVISRealtimeDiagnostics:
            try:
                self.realtime_diag = JARVISRealtimeDiagnostics(self.project_root)
            except Exception as e:
                logger.warning(f"Could not initialize real-time diagnostics: {e}")

    def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health"""
        logger.info("="*80)
        logger.info("📊 SYSTEM HEALTH CHECK")
        logger.info("="*80)

        health = {
            "timestamp": datetime.now().isoformat(),
            "platform": platform.system(),
            "platform_version": platform.version(),
            "hostname": platform.node(),
            "uptime_seconds": None,
            "cpu": {},
            "memory": {},
            "disk": {},
            "processes": {},
            "network": {},
            "status": "unknown"
        }

        try:
            # Uptime
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            health["uptime_seconds"] = uptime.total_seconds()
            health["uptime_human"] = str(uptime)

            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            health["cpu"] = {
                "usage_percent": cpu_percent,
                "count": cpu_count,
                "status": "good" if cpu_percent < 80 else "warning" if cpu_percent < 90 else "critical"
            }

            # Memory
            memory = psutil.virtual_memory()
            health["memory"] = {
                "total_gb": memory.total / (1024**3),
                "available_gb": memory.available / (1024**3),
                "used_percent": memory.percent,
                "status": "good" if memory.percent < 80 else "warning" if memory.percent < 95 else "critical"
            }

            # Disk
            disk = psutil.disk_usage('/')
            health["disk"] = {
                "total_gb": disk.total / (1024**3),
                "free_gb": disk.free / (1024**3),
                "used_percent": disk.percent,
                "status": "good" if disk.percent < 85 else "warning" if disk.percent < 95 else "critical"
            }

            # Processes
            process_count = len(psutil.pids())
            health["processes"] = {
                "total": process_count,
                "status": "good"
            }

            # Network
            try:
                net_io = psutil.net_io_counters()
                health["network"] = {
                    "bytes_sent_mb": net_io.bytes_sent / (1024 * 1024),
                    "bytes_recv_mb": net_io.bytes_recv / (1024 * 1024),
                    "status": "good"
                }
            except Exception as e:
                health["network"] = {"error": str(e), "status": "unknown"}

            # Overall status
            statuses = [
                health["cpu"]["status"],
                health["memory"]["status"],
                health["disk"]["status"]
            ]
            if "critical" in statuses:
                health["status"] = "critical"
            elif "warning" in statuses:
                health["status"] = "warning"
            else:
                health["status"] = "good"

            logger.info(f"✅ System Health: {health['status'].upper()}")
            logger.info(f"   Uptime: {health['uptime_human']}")
            logger.info(f"   CPU: {cpu_percent:.1f}% ({cpu_count} cores)")
            logger.info(f"   Memory: {memory.percent:.1f}% ({health['memory']['available_gb']:.1f} GB available)")
            logger.info(f"   Disk: {disk.percent:.1f}% ({health['disk']['free_gb']:.1f} GB free)")
            logger.info(f"   Processes: {process_count}")

        except Exception as e:
            logger.error(f"❌ Error checking system health: {e}")
            health["error"] = str(e)
            health["status"] = "error"

        return health

    def check_cursor_ide_status(self) -> Dict[str, Any]:
        """Check Cursor IDE status and processes"""
        logger.info("")
        logger.info("="*80)
        logger.info("🔍 CURSOR IDE STATUS CHECK")
        logger.info("="*80)

        cursor_status = {
            "timestamp": datetime.now().isoformat(),
            "cursor_processes": [],
            "cursor_running": False,
            "cursor_version": None,
            "cursor_cache_path": None,
            "cursor_cache_size_mb": None,
            "status": "unknown"
        }

        try:
            # Find Cursor processes
            cursor_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'memory_info', 'create_time']):
                try:
                    proc_info = proc.info
                    name = proc_info['name'].lower()
                    if 'cursor' in name:
                        cursor_processes.append({
                            "name": proc_info['name'],
                            "pid": proc_info['pid'],
                            "exe": proc_info.get('exe', 'unknown'),
                            "memory_mb": proc_info['memory_info'].rss / (1024 * 1024),
                            "uptime_seconds": datetime.now().timestamp() - proc_info['create_time']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            cursor_status["cursor_processes"] = cursor_processes
            cursor_status["cursor_running"] = len(cursor_processes) > 0

            if cursor_status["cursor_running"]:
                logger.info(f"✅ Cursor IDE is running ({len(cursor_processes)} process(es))")
                for proc in cursor_processes:
                    logger.info(f"   - {proc['name']} (PID: {proc['pid']}, Memory: {proc['memory_mb']:.1f} MB)")
            else:
                logger.info("ℹ️  Cursor IDE is not currently running")

            # Check Cursor cache
            import os
            cache_paths = [
                Path(os.path.expanduser("~")) / "AppData" / "Roaming" / "Cursor" / "Cache",
                Path(os.path.expanduser("~")) / ".cursor" / "cache",
            ]

            for cache_path in cache_paths:
                if cache_path.exists():
                    cursor_status["cursor_cache_path"] = str(cache_path)
                    # Calculate cache size
                    total_size = sum(f.stat().st_size for f in cache_path.rglob('*') if f.is_file())
                    cursor_status["cursor_cache_size_mb"] = total_size / (1024 * 1024)
                    logger.info(f"📁 Cursor cache: {cache_path} ({cursor_status['cursor_cache_size_mb']:.1f} MB)")
                    break

            cursor_status["status"] = "running" if cursor_status["cursor_running"] else "not_running"

        except Exception as e:
            logger.error(f"❌ Error checking Cursor IDE status: {e}")
            cursor_status["error"] = str(e)
            cursor_status["status"] = "error"

        return cursor_status

    def check_serialization_error_patterns(self) -> Dict[str, Any]:
        """Check for serialization error patterns in diagnostics"""
        logger.info("")
        logger.info("="*80)
        logger.info("🔍 SERIALIZATION ERROR PATTERN CHECK")
        logger.info("="*80)

        pattern_check = {
            "timestamp": datetime.now().isoformat(),
            "diagnostic_files": [],
            "recent_errors": [],
            "error_count": 0,
            "pattern_detected": False,
            "status": "unknown"
        }

        try:
            # Check diagnostic files for serialization errors
            diagnostic_files = list(self.data_dir.glob("cursor_ide_serialization_error*.md"))
            diagnostic_files.extend(list(self.data_dir.glob("request_id_tracking_*.json")))

            pattern_check["diagnostic_files"] = [str(f.name) for f in diagnostic_files]

            # Check recent errors (last 7 days)
            cutoff_date = datetime.now() - timedelta(days=7)
            recent_errors = []

            for diag_file in diagnostic_files:
                try:
                    file_time = datetime.fromtimestamp(diag_file.stat().st_mtime)
                    if file_time >= cutoff_date:
                        if diag_file.suffix == '.json':
                            with open(diag_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                if 'error_details' in data or 'error_type' in data:
                                    recent_errors.append({
                                        "file": diag_file.name,
                                        "date": file_time.isoformat(),
                                        "type": data.get('error_type', 'unknown')
                                    })
                        else:
                            recent_errors.append({
                                "file": diag_file.name,
                                "date": file_time.isoformat(),
                                "type": "serialization_error"
                            })
                except Exception as e:
                    logger.debug(f"Error reading {diag_file}: {e}")

            pattern_check["recent_errors"] = recent_errors
            pattern_check["error_count"] = len(recent_errors)
            pattern_check["pattern_detected"] = len(recent_errors) > 0

            if pattern_check["pattern_detected"]:
                logger.warning(f"⚠️  Found {len(recent_errors)} recent serialization error(s) in last 7 days")
                for error in recent_errors:
                    logger.warning(f"   - {error['file']} ({error['date']})")
            else:
                logger.info("✅ No recent serialization errors detected")

            pattern_check["status"] = "pattern_detected" if pattern_check["pattern_detected"] else "no_pattern"

        except Exception as e:
            logger.error(f"❌ Error checking serialization error patterns: {e}")
            pattern_check["error"] = str(e)
            pattern_check["status"] = "error"

        return pattern_check

    def run_full_diagnostics(self) -> Dict[str, Any]:
        """Run full diagnostic report"""
        logger.info("")
        logger.info("="*80)
        logger.info("📊 RUNNING FULL DIAGNOSTICS")
        logger.info("="*80)

        # Run real-time diagnostics if available
        realtime_report = None
        if self.realtime_diag:
            try:
                logger.info("Running real-time diagnostics...")
                realtime_report = self.realtime_diag.generate_diagnostic_report()
                logger.info(f"✅ Real-time diagnostics: {realtime_report.overall_health.value}")
            except Exception as e:
                logger.warning(f"Real-time diagnostics error: {e}")

        # Collect all diagnostic data
        diagnostics = {
            "timestamp": datetime.now().isoformat(),
            "system_health": self.check_system_health(),
            "cursor_ide_status": self.check_cursor_ide_status(),
            "serialization_error_patterns": self.check_serialization_error_patterns(),
            "realtime_diagnostics": realtime_report.to_dict() if realtime_report else None,
            "recommendations": []
        }

        # Generate recommendations
        recommendations = []

        if diagnostics["system_health"]["status"] == "critical":
            recommendations.append("System health is critical - investigate resource issues")

        if not diagnostics["cursor_ide_status"]["cursor_running"]:
            recommendations.append("Cursor IDE is not running - start it to test serialization fix")

        if diagnostics["serialization_error_patterns"]["pattern_detected"]:
            recommendations.append("Serialization error pattern detected - monitor after restarting Cursor IDE")
            recommendations.append("If errors persist, clear Cursor cache and update Cursor IDE")

        if diagnostics["cursor_ide_status"].get("cursor_cache_size_mb", 0) > 1000:
            recommendations.append("Cursor cache is large (>1GB) - consider clearing cache")

        diagnostics["recommendations"] = recommendations

        return diagnostics

    def generate_report(self) -> Path:
        try:
            """Generate comprehensive diagnostic report file"""
            logger.info("")
            logger.info("="*80)
            logger.info("📝 GENERATING DIAGNOSTIC REPORT")
            logger.info("="*80)

            diagnostics = self.run_full_diagnostics()

            # Save JSON report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.data_dir / f"post_reboot_full_diagnostics_{timestamp}.json"

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(diagnostics, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"✅ Diagnostic report saved: {report_file}")

            # Generate summary
            logger.info("")
            logger.info("="*80)
            logger.info("📋 DIAGNOSTIC SUMMARY")
            logger.info("="*80)
            logger.info(f"System Health: {diagnostics['system_health']['status'].upper()}")
            logger.info(f"Cursor IDE: {'RUNNING' if diagnostics['cursor_ide_status']['cursor_running'] else 'NOT RUNNING'}")
            logger.info(f"Serialization Errors (7 days): {diagnostics['serialization_error_patterns']['error_count']}")

            if diagnostics['recommendations']:
                logger.info("")
                logger.info("💡 Recommendations:")
                for i, rec in enumerate(diagnostics['recommendations'], 1):
                    logger.info(f"   {i}. {rec}")

            logger.info("")
            logger.info("="*80)
            logger.info("✅ FULL DIAGNOSTICS COMPLETE")
            logger.info("="*80)

            return report_file


        except Exception as e:
            self.logger.error(f"Error in generate_report: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Post-Reboot Full Diagnostics")
    parser.add_argument('--quick', action='store_true', help='Quick status check only')
    parser.add_argument('--full', action='store_true', help='Run full diagnostics (default)')

    args = parser.parse_args()

    diag = JARVISPostRebootDiagnostics()

    if args.quick:
        # Quick status
        health = diag.check_system_health()
        cursor = diag.check_cursor_ide_status()
        print(f"System: {health['status']} | Cursor: {'RUNNING' if cursor['cursor_running'] else 'NOT RUNNING'}")
    else:
        # Full diagnostics
        report_file = diag.generate_report()
        print(f"\n✅ Full diagnostics complete. Report: {report_file}")


if __name__ == "__main__":


    main()