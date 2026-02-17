#!/usr/bin/env python3
"""
JARVIS Compound Log Administrator

JARVIS system to monitor, administer, and delegate compound log tailing operations.
Manages tailing processes, monitors health, and delegates tasks.

Tags: #COMPOUND_LOG #ADMINISTRATION #MONITORING #DELEGATION @JARVIS @LUMINA
"""

import sys
import json
import time
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import deque

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger, setup_logging
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    setup_logging = lambda: None

logger = get_logger("JARVISCompoundLogAdmin")

# Import health systems
try:
    from jarvis_compound_log_health_monitor import CompoundLogHealthMonitor
    from jarvis_unified_health_system import UnifiedHealthSystem
    HEALTH_SYSTEMS_AVAILABLE = True
except ImportError:
    HEALTH_SYSTEMS_AVAILABLE = False
    logger.warning("Health systems not available")


class TailProcessManager:
    """Manage tailing processes"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.tail_processes = {}  # {process_id: process_info}
        self.next_process_id = 1

    def start_tail(self, name: str = None) -> Dict[str, Any]:
        try:
            """Start a new tail process in external terminal"""
            process_id = self.next_process_id
            self.next_process_id += 1

            compound_log = self.project_root / "data" / "compound_log_health" / "compound.log"

            if sys.platform == "win32":
                # Windows: Open new PowerShell window
                cmd = f'start powershell.exe -NoExit -Command "cd \'{self.project_root}\'; Write-Host \'📋 JARVIS Compound Log Tail #{process_id}\' -ForegroundColor Cyan; Write-Host \'File: {compound_log}\' -ForegroundColor White; Write-Host \'Press Ctrl+C to stop\' -ForegroundColor Yellow; Write-Host \'\'; Get-Content -Path \'{compound_log}\' -Wait -Tail 50"'
                process = subprocess.Popen(cmd, shell=True)
            else:
                # Linux/Mac
                import shutil
                if shutil.which("gnome-terminal"):
                    process = subprocess.Popen([
                        "gnome-terminal", "--", "bash", "-c",
                        f"cd '{self.project_root}' && tail -f '{compound_log}'"
                    ])
                elif shutil.which("xterm"):
                    process = subprocess.Popen([
                        "xterm", "-e", "bash", "-c",
                        f"cd '{self.project_root}' && tail -f '{compound_log}'"
                    ])
                else:
                    logger.error("No terminal available")
                    return {"error": "No terminal available"}

            process_info = {
                "process_id": process_id,
                "name": name or f"Tail-{process_id}",
                "process": process,
                "started_at": datetime.now().isoformat(),
                "status": "RUNNING",
                "log_file": str(compound_log)
            }

            self.tail_processes[process_id] = process_info
            logger.info(f"✅ Started tail process #{process_id}: {process_info['name']}")

            return process_info

        except Exception as e:
            self.logger.error(f"Error in start_tail: {e}", exc_info=True)
            raise
    def stop_tail(self, process_id: int) -> Dict[str, Any]:
        """Stop a tail process"""
        if process_id not in self.tail_processes:
            return {"error": f"Process {process_id} not found"}

        process_info = self.tail_processes[process_id]
        process = process_info["process"]

        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        except Exception as e:
            logger.error(f"Error stopping process {process_id}: {str(e)}")

        process_info["status"] = "STOPPED"
        process_info["stopped_at"] = datetime.now().isoformat()

        logger.info(f"⏹️  Stopped tail process #{process_id}")

        return process_info

    def list_tails(self) -> List[Dict[str, Any]]:
        """List all tail processes"""
        return [
            {
                "process_id": info["process_id"],
                "name": info["name"],
                "status": info["status"],
                "started_at": info["started_at"],
                "log_file": info["log_file"]
            }
            for info in self.tail_processes.values()
        ]

    def get_tail_status(self, process_id: int) -> Dict[str, Any]:
        """Get status of a tail process"""
        if process_id not in self.tail_processes:
            return {"error": f"Process {process_id} not found"}

        process_info = self.tail_processes[process_id]
        process = process_info["process"]

        # Check if process is still running
        if process.poll() is None:
            process_info["status"] = "RUNNING"
        else:
            process_info["status"] = "STOPPED"
            process_info["stopped_at"] = datetime.now().isoformat()

        return process_info


class HealthCheckRegistry:
    """Registry for all health checks"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.health_checks = {}  # {check_name: check_info}
        self.health_check_history = deque(maxlen=1000)  # Last 1000 health checks

    def register_health_check(self, name: str, check_func, description: str = None):
        """Register a health check"""
        self.health_checks[name] = {
            "name": name,
            "check_func": check_func,
            "description": description or f"Health check: {name}",
            "last_run": None,
            "last_status": None,
            "run_count": 0,
            "error_count": 0
        }
        logger.info(f"✅ Registered health check: {name}")

    def run_health_check(self, name: str) -> Dict[str, Any]:
        """Run a specific health check"""
        if name not in self.health_checks:
            return {"error": f"Health check '{name}' not found"}

        check_info = self.health_checks[name]
        try:
            result = check_info["check_func"]()
            check_info["last_run"] = datetime.now().isoformat()
            check_info["last_status"] = result
            check_info["run_count"] += 1

            # Add to history
            self.health_check_history.append({
                "timestamp": datetime.now().isoformat(),
                "name": name,
                "status": result
            })

            return result
        except Exception as e:
            check_info["error_count"] += 1
            logger.error(f"Error running health check {name}: {str(e)}")
            return {"error": str(e), "status": "ERROR"}

    def run_all_health_checks(self) -> Dict[str, Any]:
        """Run all registered health checks"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "overall_health": "HEALTHY",
            "summary": {
                "total": len(self.health_checks),
                "healthy": 0,
                "warning": 0,
                "degraded": 0,
                "unhealthy": 0,
                "error": 0
            }
        }

        for name in self.health_checks:
            check_result = self.run_health_check(name)
            results["checks"][name] = check_result

            status = check_result.get("status", "UNKNOWN")
            if status == "HEALTHY":
                results["summary"]["healthy"] += 1
            elif status == "WARNING":
                results["summary"]["warning"] += 1
                if results["overall_health"] == "HEALTHY":
                    results["overall_health"] = "WARNING"
            elif status == "DEGRADED":
                results["summary"]["degraded"] += 1
                if results["overall_health"] in ["HEALTHY", "WARNING"]:
                    results["overall_health"] = "DEGRADED"
            elif status == "UNHEALTHY":
                results["summary"]["unhealthy"] += 1
                results["overall_health"] = "UNHEALTHY"
            elif status == "ERROR":
                results["summary"]["error"] += 1
                results["overall_health"] = "UNHEALTHY"

        return results

    def get_health_check_status(self) -> Dict[str, Any]:
        """Get status of all health checks"""
        return {
            "registered_checks": len(self.health_checks),
            "checks": {
                name: {
                    "name": info["name"],
                    "description": info["description"],
                    "last_run": info["last_run"],
                    "last_status": info["last_status"].get("status") if info["last_status"] else None,
                    "run_count": info["run_count"],
                    "error_count": info["error_count"]
                }
                for name, info in self.health_checks.items()
            }
        }


class JARVISCompoundLogAdmin:
    """JARVIS Compound Log Administrator"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "compound_log_admin"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize systems
        if HEALTH_SYSTEMS_AVAILABLE:
            self.compound_monitor = CompoundLogHealthMonitor(project_root)
            self.unified_health = UnifiedHealthSystem(project_root)
        else:
            self.compound_monitor = None
            self.unified_health = None

        # Tail process manager
        self.tail_manager = TailProcessManager(project_root)

        # Health check registry
        self.health_registry = HealthCheckRegistry(project_root)

        # Register default health checks
        self._register_default_health_checks()

        # Administration state
        self.admin_state = {
            "monitoring": False,
            "tailing_active": False,
            "health_monitoring": False,
            "health_checks_active": False,
            "delegated_tasks": []
        }

        # Monitoring thread
        self.monitor_thread = None
        self.health_check_thread = None

    def start_monitoring(self, health_check_interval: int = 60):
        """Start JARVIS monitoring of compound log and all health checks"""
        if self.admin_state["monitoring"]:
            logger.warning("⚠️  Monitoring already active")
            return

        # Start compound log health monitoring
        if self.compound_monitor:
            self.compound_monitor.start_monitoring()
            self.admin_state["health_monitoring"] = True

        # Start unified health system
        if self.unified_health:
            self.unified_health.start_unified_monitoring(interval=60)
            # Integrate unified health system's registered checks
            self._integrate_unified_health_checks()

        # Start health checks
        self.admin_state["health_checks_active"] = True
        self.health_check_thread = threading.Thread(
            target=self._health_check_loop,
            args=(health_check_interval,),
            daemon=True
        )
        self.health_check_thread.start()

        # Start administration monitoring
        self.admin_state["monitoring"] = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()

        logger.info("✅ JARVIS compound log monitoring started")
        logger.info(f"✅ Health checks started (interval: {health_check_interval}s)")

    def _health_check_loop(self, interval: int):
        """Health check monitoring loop"""
        while self.admin_state["health_checks_active"]:
            try:
                # Run all health checks
                health_results = self.health_registry.run_all_health_checks()

                # Save health check results
                health_file = self.data_dir / f"health_checks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(health_file, 'w', encoding='utf-8') as f:
                    json.dump(health_results, f, indent=2, default=str)

                # Log summary
                summary = health_results["summary"]
                logger.info(
                    f"📊 Health checks: {health_results['overall_health']} "
                    f"(Healthy: {summary['healthy']}, Warning: {summary['warning']}, "
                    f"Degraded: {summary['degraded']}, Unhealthy: {summary['unhealthy']}, "
                    f"Error: {summary['error']})"
                )

                time.sleep(interval)
            except Exception as e:
                logger.error(f"Error in health check loop: {str(e)}")
                time.sleep(interval)

    def stop_monitoring(self):
        """Stop JARVIS monitoring"""
        self.admin_state["monitoring"] = False
        self.admin_state["health_checks_active"] = False

        if self.compound_monitor:
            self.compound_monitor.stop_monitoring()
            self.admin_state["health_monitoring"] = False

        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

        if self.health_check_thread:
            self.health_check_thread.join(timeout=5)

        logger.info("⏹️  JARVIS compound log monitoring stopped")

    def _monitoring_loop(self):
        """Administration monitoring loop"""
        while self.admin_state["monitoring"]:
            try:
                # Monitor tail processes
                self._monitor_tail_processes()

                # Monitor health
                self._monitor_health()

                # Process delegated tasks
                self._process_delegated_tasks()

                time.sleep(10)  # Check every 10 seconds
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(10)

    def _monitor_tail_processes(self):
        """Monitor tail processes"""
        for process_id, process_info in list(self.tail_manager.tail_processes.items()):
            status = self.tail_manager.get_tail_status(process_id)
            if status["status"] == "STOPPED" and process_info["status"] == "RUNNING":
                logger.info(f"📊 Tail process #{process_id} stopped")
                process_info["status"] = "STOPPED"

    def _register_default_health_checks(self):
        """Register default health checks"""
        # Compound log health check
        def check_compound_log():
            if self.compound_monitor:
                health = self.compound_monitor.get_health_status()
                return {
                    "status": health.get("health_status", "UNKNOWN"),
                    "metrics": health.get("metrics", {}),
                    "details": "Compound log health status"
                }
            return {"status": "UNKNOWN", "details": "Compound monitor not available"}

        # Tail processes health check
        def check_tail_processes():
            tails = self.tail_manager.list_tails()
            running = [t for t in tails if t["status"] == "RUNNING"]
            stopped = [t for t in tails if t["status"] == "STOPPED"]

            if len(stopped) > len(running):
                status = "WARNING"
            elif len(stopped) > 0:
                status = "DEGRADED"
            else:
                status = "HEALTHY"

            return {
                "status": status,
                "running": len(running),
                "stopped": len(stopped),
                "total": len(tails),
                "details": f"Tail processes: {len(running)} running, {len(stopped)} stopped"
            }

        # System resources health check
        def check_system_resources():
            try:
                import psutil
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()

                if cpu_percent > 90 or memory.percent > 90:
                    status = "DEGRADED"
                elif cpu_percent > 70 or memory.percent > 70:
                    status = "WARNING"
                else:
                    status = "HEALTHY"

                return {
                    "status": status,
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "details": f"CPU: {cpu_percent}%, Memory: {memory.percent}%"
                }
            except ImportError:
                return {"status": "UNKNOWN", "details": "psutil not available"}

        # Unified health check
        def check_unified_health():
            if self.unified_health:
                health = self.unified_health.get_health_status()
                return {
                    "status": health.get("overall_health", "UNKNOWN"),
                    "systems": health.get("systems", {}),
                    "applications": health.get("applications", {}),
                    "details": "Unified health system status"
                }
            return {"status": "UNKNOWN", "details": "Unified health not available"}

        # Disk space health check
        def check_disk_space():
            try:
                import shutil
                disk = shutil.disk_usage(self.project_root)
                total_gb = disk.total / (1024**3)
                used_gb = disk.used / (1024**3)
                free_gb = disk.free / (1024**3)
                used_percent = (disk.used / disk.total) * 100

                if used_percent > 90:
                    status = "DEGRADED"
                elif used_percent > 75:
                    status = "WARNING"
                else:
                    status = "HEALTHY"

                return {
                    "status": status,
                    "total_gb": round(total_gb, 2),
                    "used_gb": round(used_gb, 2),
                    "free_gb": round(free_gb, 2),
                    "used_percent": round(used_percent, 2),
                    "details": f"Disk: {round(used_percent, 1)}% used ({round(free_gb, 1)}GB free)"
                }
            except Exception as e:
                return {"status": "ERROR", "error": str(e), "details": "Disk space check failed"}

        # Process health check
        def check_processes():
            try:
                import psutil
                current_process = psutil.Process()
                children = current_process.children(recursive=True)

                return {
                    "status": "HEALTHY",
                    "process_count": len(children) + 1,
                    "details": f"Running processes: {len(children) + 1}"
                }
            except ImportError:
                return {"status": "UNKNOWN", "details": "psutil not available"}
            except Exception as e:
                return {"status": "ERROR", "error": str(e), "details": "Process check failed"}

        # Register checks
        self.health_registry.register_health_check("compound_log", check_compound_log, "Compound log health status")
        self.health_registry.register_health_check("tail_processes", check_tail_processes, "Tail processes status")
        self.health_registry.register_health_check("system_resources", check_system_resources, "System resources (CPU, Memory)")
        self.health_registry.register_health_check("unified_health", check_unified_health, "Unified health system status")
        self.health_registry.register_health_check("disk_space", check_disk_space, "Disk space availability")
        self.health_registry.register_health_check("processes", check_processes, "Running processes count")

    def _integrate_unified_health_checks(self):
        """Integrate health checks from unified health system"""
        if not self.unified_health:
            return

        # Get registered checks from unified health system
        if hasattr(self.unified_health, 'registered_checks'):
            for check_name, check_func in self.unified_health.registered_checks.items():
                # Register each check with prefix to avoid conflicts
                prefixed_name = f"unified_{check_name}"
                self.health_registry.register_health_check(
                    prefixed_name,
                    check_func,
                    f"Unified health check: {check_name}"
                )
                logger.info(f"✅ Integrated unified health check: {prefixed_name}")

    def _monitor_health(self):
        """Monitor compound log health and all health checks"""
        # Monitor compound log health
        if self.compound_monitor:
            health = self.compound_monitor.get_health_status()
            if health.get("health_status") == "UNHEALTHY":
                logger.error(f"❌ Compound log health: UNHEALTHY")
                # Delegate health recovery task
                self.delegate_task("health_recovery", {
                    "health_status": health,
                    "priority": "HIGH"
                })

        # Run all health checks
        if self.admin_state["health_checks_active"]:
            health_results = self.health_registry.run_all_health_checks()

            # Log overall health
            if health_results["overall_health"] == "UNHEALTHY":
                logger.error(f"❌ Overall health: UNHEALTHY")
                # Delegate health recovery
                self.delegate_task("health_recovery", {
                    "health_results": health_results,
                    "priority": "HIGH"
                })
            elif health_results["overall_health"] == "DEGRADED":
                logger.warning(f"⚠️  Overall health: DEGRADED")

            # Write health check results to compound log
            if self.compound_monitor:
                self.compound_monitor.write_to_compound_log(
                    f"Health checks: {health_results['overall_health']} ({health_results['summary']['healthy']}/{health_results['summary']['total']} healthy)",
                    "HEALTH_CHECKS"
                )

    def _process_delegated_tasks(self):
        """Process delegated tasks"""
        for task in self.admin_state["delegated_tasks"][:]:
            try:
                if task["type"] == "start_tail":
                    self.tail_manager.start_tail(task.get("name"))
                    self.admin_state["delegated_tasks"].remove(task)
                elif task["type"] == "stop_tail":
                    self.tail_manager.stop_tail(task.get("process_id"))
                    self.admin_state["delegated_tasks"].remove(task)
                elif task["type"] == "health_recovery":
                    # Handle health recovery
                    logger.warning(f"⚠️  Health recovery needed: {task.get('health_status', {}).get('health_status')}")
                    self.admin_state["delegated_tasks"].remove(task)
            except Exception as e:
                logger.error(f"Error processing delegated task: {str(e)}")

    def delegate_task(self, task_type: str, task_data: Dict[str, Any]):
        """Delegate a task to JARVIS"""
        task = {
            "type": task_type,
            "data": task_data,
            "created_at": datetime.now().isoformat(),
            "status": "PENDING"
        }
        self.admin_state["delegated_tasks"].append(task)
        logger.info(f"📋 Delegated task: {task_type}")

    def start_tail(self, name: str = None) -> Dict[str, Any]:
        """Start tailing compound log (delegated)"""
        return self.tail_manager.start_tail(name)

    def stop_tail(self, process_id: int) -> Dict[str, Any]:
        """Stop tailing compound log (delegated)"""
        return self.tail_manager.stop_tail(process_id)

    def list_tails(self) -> List[Dict[str, Any]]:
        """List all tail processes (delegated)"""
        return self.tail_manager.list_tails()

    def get_admin_status(self) -> Dict[str, Any]:
        """Get administration status"""
        # Get latest health check results
        health_check_status = self.health_registry.get_health_check_status()

        # Run all health checks for current status
        current_health = self.health_registry.run_all_health_checks()

        return {
            "timestamp": datetime.now().isoformat(),
            "monitoring": self.admin_state["monitoring"],
            "health_monitoring": self.admin_state["health_monitoring"],
            "health_checks_active": self.admin_state["health_checks_active"],
            "tail_processes": self.tail_manager.list_tails(),
            "delegated_tasks": len(self.admin_state["delegated_tasks"]),
            "compound_log_health": self.compound_monitor.get_health_status() if self.compound_monitor else None,
            "health_checks": {
                "registry": health_check_status,
                "current": current_health
            }
        }

    def run_health_check(self, check_name: str) -> Dict[str, Any]:
        """Run a specific health check"""
        return self.health_registry.run_health_check(check_name)

    def run_all_health_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        return self.health_registry.run_all_health_checks()

    def register_health_check(self, name: str, check_func, description: str = None):
        """Register a new health check"""
        self.health_registry.register_health_check(name, check_func, description)

    def write_to_compound_log(self, message: str, source: str = "JARVIS_ADMIN"):
        """Write to compound log"""
        if self.compound_monitor:
            self.compound_monitor.write_to_compound_log(message, source)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Compound Log Administrator")
    parser.add_argument("--start", action="store_true", help="Start JARVIS monitoring")
    parser.add_argument("--stop", action="store_true", help="Stop JARVIS monitoring")
    parser.add_argument("--tail", action="store_true", help="Start tailing in external terminal")
    parser.add_argument("--stop-tail", type=int, help="Stop tail process by ID")
    parser.add_argument("--list-tails", action="store_true", help="List all tail processes")
    parser.add_argument("--status", action="store_true", help="Get administration status")
    parser.add_argument("--delegate", type=str, help="Delegate task (start_tail, stop_tail, health_recovery)")
    parser.add_argument("--name", type=str, help="Name for tail process")
    parser.add_argument("--health-check", type=str, help="Run a specific health check by name")
    parser.add_argument("--health-checks", action="store_true", help="Run all health checks")
    parser.add_argument("--health-status", action="store_true", help="Get health check registry status")
    parser.add_argument("--interval", type=int, default=60, help="Health check interval in seconds (default: 60)")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    admin = JARVISCompoundLogAdmin(project_root)

    if args.start:
        admin.start_monitoring(health_check_interval=args.interval)
        admin.write_to_compound_log("JARVIS compound log administration started", "JARVIS_ADMIN")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            admin.stop_monitoring()
            admin.write_to_compound_log("JARVIS compound log administration stopped", "JARVIS_ADMIN")
    elif args.stop:
        admin.stop_monitoring()
    elif args.tail:
        result = admin.start_tail(args.name)
        print(json.dumps(result, indent=2, default=str))
    elif args.stop_tail:
        result = admin.stop_tail(args.stop_tail)
        print(json.dumps(result, indent=2, default=str))
    elif args.list_tails:
        tails = admin.list_tails()
        print(json.dumps(tails, indent=2, default=str))
    elif args.delegate:
        admin.delegate_task(args.delegate, {"name": args.name} if args.name else {})
        print(f"✅ Delegated task: {args.delegate}")
    elif args.health_check:
        result = admin.run_health_check(args.health_check)
        print(json.dumps(result, indent=2, default=str))
    elif args.health_checks:
        result = admin.run_all_health_checks()
        print(json.dumps(result, indent=2, default=str))
    elif args.health_status:
        status = admin.health_registry.get_health_check_status()
        print(json.dumps(status, indent=2, default=str))
    elif args.status:
        status = admin.get_admin_status()
        print(json.dumps(status, indent=2, default=str))
    else:
        # Default: show status
        status = admin.get_admin_status()
        print(json.dumps(status, indent=2, default=str))


if __name__ == "__main__":


    main()