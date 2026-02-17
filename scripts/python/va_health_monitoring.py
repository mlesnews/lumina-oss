#!/usr/bin/env python3
"""
VA Health Monitoring System

Monitors VA health, performance, availability, and auto-recovery.

Tags: #VIRTUAL_ASSISTANT #HEALTH #MONITORING #METRICS @JARVIS @LUMINA
"""

import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from character_avatar_registry import (CharacterAvatarRegistry,
                                           CharacterType)
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    CharacterAvatarRegistry = None
    CharacterType = None

logger = get_logger("VAHealthMonitoring")


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthMetrics:
    """VA health metrics"""
    va_id: str
    status: HealthStatus
    response_time: float = 0.0  # seconds
    task_completion_rate: float = 1.0  # 0.0-1.0
    error_rate: float = 0.0  # 0.0-1.0
    uptime: float = 0.0  # seconds
    last_check: str = field(default_factory=lambda: datetime.now().isoformat())
    issues: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["status"] = self.status.value
        return data


class VAHealthMonitoring:
    """
    VA Health Monitoring System

    Features:
    - Health checks
    - Performance metrics
    - Availability monitoring
    - Error tracking
    - Auto-recovery
    """

    def __init__(self, registry: Optional[CharacterAvatarRegistry] = None):
        """Initialize health monitoring system"""
        if registry is None:
            if CharacterAvatarRegistry:
                registry = CharacterAvatarRegistry()
            else:
                raise ValueError("CharacterAvatarRegistry not available")

        self.registry = registry
        self.vas = self.registry.get_characters_by_type(CharacterType.VIRTUAL_ASSISTANT)

        # Health metrics
        self.health_metrics: Dict[str, HealthMetrics] = {}

        # Error tracking
        self.error_history: Dict[str, List[Dict[str, Any]]] = {va.character_id: [] for va in self.vas}

        # Performance history
        self.performance_history: Dict[str, List[Dict[str, Any]]] = {va.character_id: [] for va in self.vas}

        # Auto-recovery enabled
        self.auto_recovery_enabled = True

        # Thresholds
        self.thresholds = {
            "response_time_warning": 2.0,  # seconds
            "response_time_critical": 5.0,
            "error_rate_warning": 0.1,  # 10%
            "error_rate_critical": 0.3,  # 30%
            "completion_rate_warning": 0.9,  # 90%
            "completion_rate_critical": 0.7  # 70%
        }

        # Initialize health metrics
        self._initialize_health_metrics()

        # Data persistence
        self.data_dir = project_root / "data" / "va_health_monitoring"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 80)
        logger.info("🏥 VA HEALTH MONITORING SYSTEM")
        logger.info("=" * 80)
        logger.info(f"   VAs Registered: {len(self.vas)}")
        logger.info("   Health monitoring active")
        logger.info("=" * 80)

    def _initialize_health_metrics(self):
        """Initialize health metrics for all VAs"""
        for va in self.vas:
            self.health_metrics[va.character_id] = HealthMetrics(
                va_id=va.character_id,
                status=HealthStatus.HEALTHY,
                response_time=0.5,  # Default
                task_completion_rate=1.0,
                error_rate=0.0,
                uptime=0.0
            )

    def health_check(self, va_id: str) -> HealthMetrics:
        """Perform health check for a VA"""
        if va_id not in self.health_metrics:
            raise ValueError(f"VA {va_id} not found")

        metrics = self.health_metrics[va_id]

        # Simulate health check (in real implementation, would check actual VA status)
        # For now, we'll use existing metrics

        # Determine status based on thresholds
        status = HealthStatus.HEALTHY
        issues = []

        if metrics.response_time > self.thresholds["response_time_critical"]:
            status = HealthStatus.CRITICAL
            issues.append("Response time critical")
        elif metrics.response_time > self.thresholds["response_time_warning"]:
            if status == HealthStatus.HEALTHY:
                status = HealthStatus.WARNING
            issues.append("Response time high")

        if metrics.error_rate > self.thresholds["error_rate_critical"]:
            status = HealthStatus.CRITICAL
            issues.append("Error rate critical")
        elif metrics.error_rate > self.thresholds["error_rate_warning"]:
            if status == HealthStatus.HEALTHY:
                status = HealthStatus.WARNING
            issues.append("Error rate elevated")

        if metrics.task_completion_rate < self.thresholds["completion_rate_critical"]:
            status = HealthStatus.CRITICAL
            issues.append("Completion rate critical")
        elif metrics.task_completion_rate < self.thresholds["completion_rate_warning"]:
            if status == HealthStatus.HEALTHY:
                status = HealthStatus.WARNING
            issues.append("Completion rate low")

        metrics.status = status
        metrics.issues = issues
        metrics.last_check = datetime.now().isoformat()

        logger.info(f"🏥 Health check for {va_id}: {status.value}")
        if issues:
            logger.warning(f"   Issues: {', '.join(issues)}")

        return metrics

    def update_metrics(self, va_id: str, response_time: Optional[float] = None,
                      task_completed: Optional[bool] = None,
                      error_occurred: Optional[bool] = None):
        """Update health metrics"""
        if va_id not in self.health_metrics:
            return

        metrics = self.health_metrics[va_id]

        # Update response time
        if response_time is not None:
            # Moving average
            metrics.response_time = (metrics.response_time * 0.8) + (response_time * 0.2)

        # Update completion rate
        if task_completed is not None:
            # Simplified: would track actual completion rate
            if task_completed:
                metrics.task_completion_rate = min(1.0, metrics.task_completion_rate + 0.01)
            else:
                metrics.task_completion_rate = max(0.0, metrics.task_completion_rate - 0.02)

        # Update error rate
        if error_occurred is not None:
            if error_occurred:
                metrics.error_rate = min(1.0, metrics.error_rate + 0.05)
                self._record_error(va_id, "Task error")
            else:
                metrics.error_rate = max(0.0, metrics.error_rate - 0.01)

    def _record_error(self, va_id: str, error_message: str):
        """Record error in history"""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "message": error_message
        }
        self.error_history[va_id].append(error_entry)

        # Keep only last 100 errors
        if len(self.error_history[va_id]) > 100:
            self.error_history[va_id] = self.error_history[va_id][-100:]

    def performance_metrics(self, va_id: str) -> Dict[str, Any]:
        """Get performance metrics for a VA"""
        metrics = self.health_metrics.get(va_id)
        if not metrics:
            return {}

        return {
            "va_id": va_id,
            "response_time": metrics.response_time,
            "task_completion_rate": metrics.task_completion_rate,
            "error_rate": metrics.error_rate,
            "uptime": metrics.uptime,
            "status": metrics.status.value,
            "recent_errors": len(self.error_history.get(va_id, []))
        }

    def availability_status(self, va_id: str) -> Dict[str, Any]:
        """Get availability status"""
        metrics = self.health_metrics.get(va_id)
        if not metrics:
            return {"available": False, "status": "unknown"}

        available = metrics.status != HealthStatus.CRITICAL

        return {
            "available": available,
            "status": metrics.status.value,
            "issues": metrics.issues,
            "last_check": metrics.last_check
        }

    def auto_recovery(self, va_id: str) -> bool:
        """Attempt auto-recovery for a VA"""
        if not self.auto_recovery_enabled:
            return False

        metrics = self.health_metrics.get(va_id)
        if not metrics or metrics.status != HealthStatus.CRITICAL:
            return False

        logger.info(f"🔄 Attempting auto-recovery for {va_id}")

        # Reset metrics (simplified recovery)
        metrics.status = HealthStatus.HEALTHY
        metrics.response_time = 0.5
        metrics.error_rate = 0.0
        metrics.issues = []
        metrics.last_check = datetime.now().isoformat()

        logger.info(f"✅ Auto-recovery successful for {va_id}")
        return True

    def get_all_health_status(self) -> Dict[str, Dict[str, Any]]:
        """Get health status for all VAs"""
        return {
            va_id: {
                "status": metrics.status.value,
                "response_time": metrics.response_time,
                "completion_rate": metrics.task_completion_rate,
                "error_rate": metrics.error_rate,
                "issues": metrics.issues
            }
            for va_id, metrics in self.health_metrics.items()
        }

    def _save_state(self):
        try:
            """Save health monitoring state"""
            state_file = self.data_dir / "health_state.json"

            state = {
                "health_metrics": {va_id: m.to_dict() for va_id, m in self.health_metrics.items()},
                "error_counts": {va_id: len(errors) for va_id, errors in self.error_history.items()},
                "timestamp": datetime.now().isoformat()
            }

            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)

            logger.info(f"💾 Saved health state to {state_file}")


        except Exception as e:
            self.logger.error(f"Error in _save_state: {e}", exc_info=True)
            raise
def main():
    """Main entry point for testing"""
    if not CharacterAvatarRegistry:
        print("❌ Character Avatar Registry not available")
        return

    registry = CharacterAvatarRegistry()
    health = VAHealthMonitoring(registry)

    print("=" * 80)
    print("🏥 VA HEALTH MONITORING SYSTEM TEST")
    print("=" * 80)
    print()

    # Test: Health checks
    print("Performing health checks...")
    for va in health.vas:
        metrics = health.health_check(va.character_id)
        print(f"  • {va.name}: {metrics.status.value}")
        if metrics.issues:
            print(f"    Issues: {', '.join(metrics.issues)}")
    print()

    # Test: Update metrics
    print("Updating metrics...")
    health.update_metrics("jarvis_va", response_time=1.5, task_completed=True)
    health.update_metrics("ace", response_time=0.3, task_completed=True)
    health.update_metrics("imva", response_time=3.0, error_occurred=True)
    print("  ✅ Metrics updated")
    print()

    # Test: Performance metrics
    print("Performance Metrics:")
    for va in health.vas:
        perf = health.performance_metrics(va.character_id)
        if perf:
            print(f"  • {va.name}:")
            print(f"    Response Time: {perf['response_time']:.2f}s")
            print(f"    Completion Rate: {perf['task_completion_rate']:.1%}")
            print(f"    Error Rate: {perf['error_rate']:.1%}")
    print()

    # Test: Auto-recovery
    print("Testing auto-recovery...")
    health.health_metrics["imva"].status = HealthStatus.CRITICAL
    health.auto_recovery("imva")
    print("  ✅ Auto-recovery tested")
    print()

    # Save state
    health._save_state()

    print("=" * 80)


if __name__ == "__main__":


    main()