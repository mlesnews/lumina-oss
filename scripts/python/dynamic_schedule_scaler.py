#!/usr/bin/env python3
"""
Dynamic Schedule Scaler - Smart Load Balancing with @AIQ Fallback

Calculates optimal schedule interval (1-3 hours) based on:
- System load
- Pending TODOs
- Roadblocks
- VA health
- Resource utilization

Uses @AIQ fallback for decisioning and troubleshooting.

Tags: #DYNAMIC_SCALING #LOAD_BALANCING #DECISIONING #TROUBLESHOOTING @AIQ @JARVIS @LUMINA
"""

import sys
import json
import psutil
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DynamicScheduleScaler")


class DynamicScheduleScaler:
    """
    Dynamic Schedule Scaler

    Calculates optimal schedule interval (1-3 hours) based on system state.
    Uses @AIQ fallback for decisioning and troubleshooting.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize dynamic schedule scaler"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "dynamic_schedule"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Import components
        try:
            from autonomous_ai_agent import AutonomousAIAgent
            self.autonomous_agent = AutonomousAIAgent(project_root)
        except ImportError:
            self.autonomous_agent = None

        try:
            from va_health_detector import VAHealthDetector
            self.va_detector = VAHealthDetector(project_root)
        except ImportError:
            self.va_detector = None

        logger.info("✅ Dynamic Schedule Scaler initialized")
        logger.info("   Smart load balancing with @AIQ fallback")

    def calculate_optimal_interval(self) -> Dict[str, Any]:
        try:
            """
            Calculate optimal schedule interval (1-3 hours)

            Returns:
                Schedule calculation result
            """
            logger.info("=" * 80)
            logger.info("📊 CALCULATING OPTIMAL SCHEDULE INTERVAL")
            logger.info("=" * 80)
            logger.info("")

            result = {
                "timestamp": datetime.now().isoformat(),
                "interval_hours": 1.0,
                "factors": {},
                "recommendation": "1 hour",
                "reason": "Default"
            }

            # Factor 1: System Load
            system_load = self._assess_system_load()
            result["factors"]["system_load"] = system_load
            logger.info(f"   📊 System Load: {system_load['level']} ({system_load['cpu_percent']:.1f}% CPU, {system_load['memory_percent']:.1f}% Memory)")

            # Factor 2: Pending TODOs
            pending_todos = self._assess_pending_todos()
            result["factors"]["pending_todos"] = pending_todos
            logger.info(f"   📋 Pending TODOs: {pending_todos['count']} ({pending_todos['level']})")

            # Factor 3: Roadblocks
            roadblocks = self._assess_roadblocks()
            result["factors"]["roadblocks"] = roadblocks
            logger.info(f"   ⚠️  Roadblocks: {roadblocks['count']} ({roadblocks['level']})")

            # Factor 4: VA Health
            va_health = self._assess_va_health()
            result["factors"]["va_health"] = va_health
            logger.info(f"   🤖 VA Health: {va_health['level']} ({va_health['failed']} failed)")

            # Calculate interval using @AIQ decisioning
            interval = self._calculate_interval_with_aiq(
                system_load,
                pending_todos,
                roadblocks,
                va_health
            )

            result["interval_hours"] = interval
            result["recommendation"] = f"{interval} hour(s)"
            result["reason"] = self._generate_reason(system_load, pending_todos, roadblocks, va_health, interval)

            # Save calculation
            calc_file = self.data_dir / f"schedule_calc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(calc_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ SCHEDULE CALCULATION COMPLETE")
            logger.info("=" * 80)
            logger.info(f"   Recommended Interval: {result['recommendation']}")
            logger.info(f"   Reason: {result['reason']}")
            logger.info(f"   Calculation saved: {calc_file.name}")
            logger.info("")

            return result

        except Exception as e:
            self.logger.error(f"Error in calculate_optimal_interval: {e}", exc_info=True)
            raise
    def _assess_system_load(self) -> Dict[str, Any]:
        """Assess system load"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk_io = psutil.disk_io_counters()
            network_io = psutil.net_io_counters()

            # Determine load level
            if cpu_percent < 50 and memory.percent < 50:
                level = "low"
            elif cpu_percent < 80 and memory.percent < 80:
                level = "medium"
            else:
                level = "high"

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_io_active": disk_io is not None,
                "network_io_active": network_io is not None,
                "level": level
            }
        except Exception as e:
            logger.warning(f"   ⚠️  System load assessment failed: {e}")
            return {"level": "unknown", "cpu_percent": 0, "memory_percent": 0}

    def _assess_pending_todos(self) -> Dict[str, Any]:
        """Assess pending TODOs"""
        if not self.autonomous_agent or not self.autonomous_agent.master_todo_tracker:
            return {"count": 0, "level": "unknown"}

        pending = self.autonomous_agent.get_pending_todos()
        count = len(pending)

        if count < 20:
            level = "low"
        elif count < 50:
            level = "medium"
        else:
            level = "high"

        return {"count": count, "level": level}

    def _assess_roadblocks(self) -> Dict[str, Any]:
        """Assess roadblocks"""
        # Check for roadblock reports
        roadblock_dir = self.project_root / "data" / "autonomous_ai"
        if roadblock_dir.exists():
            reports = list(roadblock_dir.glob("roadblocks_report_*.json"))
            if reports:
                latest = max(reports, key=lambda p: p.stat().st_mtime)
                try:
                    with open(latest, 'r', encoding='utf-8') as f:
                        report = json.load(f)
                        count = report.get("total_roadblocks", 0)

                        if count == 0:
                            level = "none"
                        elif count < 10:
                            level = "some"
                        else:
                            level = "many"

                        return {"count": count, "level": level}
                except Exception:
                    pass

        return {"count": 0, "level": "unknown"}

    def _assess_va_health(self) -> Dict[str, Any]:
        """Assess VA health"""
        if not self.va_detector:
            return {"level": "unknown", "failed": 0}

        try:
            health = self.va_detector.check_va_health()
            failed = health["summary"].get("failed", 0)
            required_not_running = health["summary"].get("required_not_running", 0)

            if failed == 0 and required_not_running == 0:
                level = "all_healthy"
            elif failed < 2:
                level = "some_issues"
            else:
                level = "critical"

            return {"level": level, "failed": failed, "required_not_running": required_not_running}
        except Exception as e:
            logger.warning(f"   ⚠️  VA health assessment failed: {e}")
            return {"level": "unknown", "failed": 0}

    def _calculate_interval_with_aiq(
        self,
        system_load: Dict[str, Any],
        pending_todos: Dict[str, Any],
        roadblocks: Dict[str, Any],
        va_health: Dict[str, Any]
    ) -> float:
        """
        Calculate interval using @AIQ decisioning

        Returns:
            Interval in hours (1.0 to 3.0)
        """
        # Base interval: 1 hour
        interval = 1.0

        # Adjust based on factors
        # Higher load = longer interval (less frequent)
        # More TODOs = shorter interval (more frequent)
        # More roadblocks = shorter interval (more frequent)
        # VA issues = shorter interval (more frequent)

        load_factor = {"low": 0.0, "medium": 0.5, "high": 1.0}.get(system_load.get("level", "medium"), 0.5)
        todos_factor = {"low": 0.0, "medium": -0.5, "high": -1.0}.get(pending_todos.get("level", "medium"), 0.0)
        roadblocks_factor = {"none": 0.0, "some": -0.5, "many": -1.0}.get(roadblocks.get("level", "some"), -0.5)
        va_factor = {"all_healthy": 0.0, "some_issues": -0.5, "critical": -1.0}.get(va_health.get("level", "all_healthy"), 0.0)

        # Calculate adjustment
        adjustment = load_factor + todos_factor + roadblocks_factor + va_factor

        # Apply adjustment (clamp between 1 and 3 hours)
        interval = max(1.0, min(3.0, 1.0 + adjustment))

        return round(interval, 1)

    def _generate_reason(
        self,
        system_load: Dict[str, Any],
        pending_todos: Dict[str, Any],
        roadblocks: Dict[str, Any],
        va_health: Dict[str, Any],
        interval: float
    ) -> str:
        """Generate reason for interval"""
        reasons = []

        if system_load.get("level") == "high":
            reasons.append("High system load")
        if pending_todos.get("level") == "high":
            reasons.append("Many pending TODOs")
        if roadblocks.get("level") == "many":
            reasons.append("Many roadblocks")
        if va_health.get("level") == "critical":
            reasons.append("Critical VA health issues")

        if not reasons:
            reasons.append("Optimal system state")

        return f"{interval}h interval: " + ", ".join(reasons)


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Dynamic Schedule Scaler")
    parser.add_argument("--calculate", action="store_true", help="Calculate optimal interval")

    args = parser.parse_args()

    scaler = DynamicScheduleScaler()

    if args.calculate:
        result = scaler.calculate_optimal_interval()
        print(f"\n📊 Optimal Interval: {result['recommendation']}")
        print(f"   Reason: {result['reason']}")
    else:
        # Default: calculate
        result = scaler.calculate_optimal_interval()
        print(f"\n📊 Optimal Interval: {result['recommendation']}")

    return 0


if __name__ == "__main__":


    sys.exit(main())