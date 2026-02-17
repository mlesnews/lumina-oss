"""
AI Usage Monitor Plugin

Monitors AI usage and enforces local-first routing.
Consolidates: monitor_ai_usage_and_enforce_local_first.py
"""

import sys
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

logger = get_logger("AIUsageMonitorPlugin")


class AIUsageMonitorPlugin(MonitorPlugin):
    """Monitor AI usage and enforce local-first routing"""

    def __init__(self):
        super().__init__(
            monitor_type=MonitorType.AI_USAGE,
            name="AI Usage Monitor",
            description="Monitors AI usage and enforces local-first routing"
        )

    def get_interval(self) -> float:
        """Get monitoring interval"""
        return 60.0  # Check every minute

    def monitor(self, **kwargs) -> MonitorResult:
        """Monitor AI usage"""
        try:
            # Check Cursor settings for AI routing
            project_root = kwargs.get('project_root', Path(__file__).parent.parent.parent.parent)

            # Import and use existing monitor if available
            try:
                from monitor_ai_usage_and_enforce_local_first import AIUsageMonitor
                monitor = AIUsageMonitor(project_root)
                result = monitor.check_and_enforce()

                status = "healthy" if result.get("local_first", True) else "warning"
                message = result.get("message", "AI usage monitoring active")

                return MonitorResult(
                    monitor_type=self.monitor_type,
                    status=status,
                    message=message,
                    metrics=result
                )
            except ImportError:
                # Fallback: basic check
                logger.warning("monitor_ai_usage_and_enforce_local_first not available")
                return MonitorResult(
                    monitor_type=self.monitor_type,
                    status="unknown",
                    message="AI usage monitor module not available",
                    metrics={"error": "Module not found"}
                )

        except Exception as e:
            return MonitorResult(
                monitor_type=self.monitor_type,
                status="unknown",
                message=f"Error monitoring AI usage: {e}",
                metrics={"error": str(e)}
            )

    def get_status(self) -> MonitorResult:
        """Get current status"""
        return self.monitor()
