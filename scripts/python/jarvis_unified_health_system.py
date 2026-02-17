#!/usr/bin/env python3
"""
JARVIS Unified Health System

Unified health monitoring system integrating:
- Compound log tailing and parsing
- System health checks
- Application health checks
- BAU policy compliance

Tags: #UNIFIED_HEALTH #COMPOUND_LOG #BAU #SYSTEM_HEALTH @JARVIS @LUMINA
"""

import json
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict

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

logger = get_logger("JARVISUnifiedHealthSystem")

# Import health systems
try:
    from jarvis_compound_log_health_monitor import (CompoundLogHealthMonitor,
                                                    SystemHealthChecker)
    HEALTH_SYSTEMS_AVAILABLE = True
except ImportError:
    HEALTH_SYSTEMS_AVAILABLE = False
    logger.warning("Health systems not available")


class UnifiedHealthSystem:
    """Unified health monitoring system"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "unified_health"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        if not HEALTH_SYSTEMS_AVAILABLE:
            logger.error("Health systems not available")
            return

        # Initialize health systems
        self.compound_monitor = CompoundLogHealthMonitor(project_root)
        self.health_checker = SystemHealthChecker(project_root)

        # Health check registry
        self.registered_checks = {}
        self.health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_health": "UNKNOWN",
            "systems": {},
            "applications": {},
            "compound_log": {}
        }

        self.monitoring = False
        self.monitor_thread = None

    def register_system_health_check(self, system_name: str, check_func: Callable):
        """Register a system health check"""
        self.registered_checks[system_name] = check_func
        self.health_checker.register_health_check(system_name, check_func)
        logger.info(f"✅ Registered health check: {system_name}")

    def register_application_health_check(self, app_name: str, check_func: Callable):
        """Register an application health check"""
        self.registered_checks[f"APP_{app_name}"] = check_func
        self.health_checker.register_health_check(f"APP_{app_name}", check_func)
        logger.info(f"✅ Registered application health check: {app_name}")

    def start_unified_monitoring(self, interval: int = 60):
        """Start unified health monitoring"""
        # Start compound log monitoring
        self.compound_monitor.start_monitoring()

        # Start continuous health checks
        self.health_checker.start_continuous_health_checks(interval)

        # Start unified monitoring loop
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()

        logger.info("✅ Unified health monitoring started")

    def stop_unified_monitoring(self):
        """Stop unified health monitoring"""
        self.monitoring = False
        self.compound_monitor.stop_monitoring()
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("⏹️  Unified health monitoring stopped")

    def _monitoring_loop(self):
        """Unified monitoring loop"""
        while self.monitoring:
            try:
                # Get compound log health
                compound_health = self.compound_monitor.get_health_status()

                # Get system health checks
                system_health = self.health_checker.run_health_checks()

                # Combine health status
                self.health_status = {
                    "timestamp": datetime.now().isoformat(),
                    "overall_health": self._determine_overall_health(compound_health, system_health),
                    "compound_log": compound_health,
                    "systems": system_health,
                    "applications": self._get_application_health()
                }

                # Save health status
                self._save_health_status()

                # Display status
                self._display_health_status()

                time.sleep(60)  # Update every minute
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(60)

    def _determine_overall_health(self, compound_health: Dict[str, Any],
                                 system_health: Dict[str, Any]) -> str:
        """Determine overall health status"""
        # Check compound log health
        compound_status = compound_health.get("health_status", "UNKNOWN")

        # Check system health
        system_status = system_health.get("overall_health", "UNKNOWN")

        # Determine overall
        if compound_status == "UNHEALTHY" or system_status == "UNHEALTHY":
            return "UNHEALTHY"
        elif compound_status == "DEGRADED" or system_status == "DEGRADED":
            return "DEGRADED"
        elif compound_status == "WARNING" or system_status == "WARNING":
            return "WARNING"
        else:
            return "HEALTHY"

    def _get_application_health(self) -> Dict[str, Any]:
        """Get application health status"""
        app_health = {}

        # Run registered application health checks
        for app_name, check_func in self.registered_checks.items():
            if app_name.startswith("APP_"):
                try:
                    result = check_func()
                    app_health[app_name.replace("APP_", "")] = result
                except Exception as e:
                    logger.error(f"Error checking {app_name}: {e}")
                    app_health[app_name.replace("APP_", "")] = {"status": "UNKNOWN", "error": str(e)}

        return app_health

    def _save_health_status(self):
        try:
            """Save health status"""
            health_file = self.data_dir / f"health_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(health_file, 'w', encoding='utf-8') as f:
                json.dump(self.health_status, f, indent=2, default=str)

        except Exception as e:
            self.logger.error(f"Error in _save_health_status: {e}", exc_info=True)
            raise
    def _display_health_status(self):
        """Display health status"""
        print("\n" + "=" * 80)
        print("🏥 UNIFIED HEALTH SYSTEM - BAU MONITORING")
        print("=" * 80)
        print(f"📊 Overall Health: {self.health_status['overall_health']}")
        print(f"📝 Compound Log: {self.health_status.get('compound_log', {}).get('health_status', 'UNKNOWN')}")
        print(f"⚙️  Systems: {self.health_status.get('systems', {}).get('overall_health', 'UNKNOWN')}")
        print(f"📱 Applications: {len(self.health_status.get('applications', {}))} checked")
        print("=" * 80 + "\n")

    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        return self.health_status

    def write_to_compound_log(self, message: str, source: str = "UNIFIED_HEALTH"):
        """Write to compound log"""
        self.compound_monitor.write_to_compound_log(message, source)


def create_default_health_checks(unified_system: UnifiedHealthSystem):
    """Create default health checks"""

    def check_ask_processor():
        try:
            """Check ask processor health"""
            processing_dir = unified_system.project_root / "data" / "ask_processing"
            if processing_dir.exists():
                result_files = list(processing_dir.glob("processing_results_*.json"))
                if result_files:
                    latest = max(result_files, key=lambda p: p.stat().st_mtime)
                    with open(latest, encoding='utf-8') as f:
                        results = json.load(f)

                    failed = results.get("failed", 0)
                    if failed > 0:
                        return {"status": "DEGRADED", "failed": failed}
                    else:
                        return {"status": "HEALTHY", "processed": results.get("processed", 0)}
            return {"status": "UNKNOWN"}

        except Exception as e:
            logger.error(f"Error in check_ask_processor: {e}", exc_info=True)
            raise
    def check_compound_log():
        try:
            """Check compound log health"""
            compound_log = unified_system.compound_monitor.compound_log
            if compound_log.exists():
                size = compound_log.stat().st_size
                if size > 0:
                    return {"status": "HEALTHY", "size": size}
                else:
                    return {"status": "WARNING", "size": 0}
            return {"status": "UNHEALTHY", "reason": "Log file not found"}

        except Exception as e:
            logger.error(f"Error in check_compound_log: {e}", exc_info=True)
            raise
    def check_system_resources():
        """Check system resources"""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()

            if cpu_percent > 90 or memory.percent > 90:
                return {"status": "DEGRADED", "cpu": cpu_percent, "memory": memory.percent}
            elif cpu_percent > 70 or memory.percent > 70:
                return {"status": "WARNING", "cpu": cpu_percent, "memory": memory.percent}
            else:
                return {"status": "HEALTHY", "cpu": cpu_percent, "memory": memory.percent}
        except ImportError:
            return {"status": "UNKNOWN", "reason": "psutil not available"}

    # Register Cursor IDE models health check
    try:
        from jarvis_cursor_models_health_check import \
            create_models_health_check_function
        check_cursor_models = create_models_health_check_function(unified_system.project_root)
        unified_system.register_application_health_check("cursor_models", check_cursor_models)
        logger.info("✅ Registered Cursor IDE models health check")
    except ImportError as e:
        logger.warning(f"⚠️  Could not register Cursor models health check: {e}")

    # Register health checks
    unified_system.register_system_health_check("ask_processor", check_ask_processor)
    unified_system.register_system_health_check("compound_log", check_compound_log)
    unified_system.register_system_health_check("system_resources", check_system_resources)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Unified Health System")
    parser.add_argument("--start", action="store_true", help="Start unified monitoring")
    parser.add_argument("--status", action="store_true", help="Get health status")
    parser.add_argument("--interval", type=int, default=60, help="Health check interval (seconds)")

    args = parser.parse_args()

    if not HEALTH_SYSTEMS_AVAILABLE:
        logger.error("Health systems not available")
        return

    project_root = Path(__file__).parent.parent.parent
    unified_system = UnifiedHealthSystem(project_root)

    # Create default health checks
    create_default_health_checks(unified_system)

    if args.start:
        unified_system.start_unified_monitoring(args.interval)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            unified_system.stop_unified_monitoring()
    elif args.status:
        unified_system.compound_monitor.start_monitoring()
        time.sleep(2)
        status = unified_system.get_health_status()
        print(json.dumps(status, indent=2, default=str))
        unified_system.compound_monitor.stop_monitoring()
    else:
        # Default: show status
        unified_system.compound_monitor.start_monitoring()
        time.sleep(2)
        status = unified_system.get_health_status()
        unified_system._display_health_status()
        unified_system.compound_monitor.stop_monitoring()


if __name__ == "__main__":
    main()
if __name__ == "__main__":
    main()
if __name__ == "__main__":
    main()
if __name__ == "__main__":
    main()
if __name__ == "__main__":


    main()