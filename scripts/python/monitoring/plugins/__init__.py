"""
Monitor Plugins

Individual monitor implementations as plugins.
"""

from .system_health import SystemHealthMonitorPlugin
from .ai_usage import AIUsageMonitorPlugin

__all__ = [
    'SystemHealthMonitorPlugin',
    'AIUsageMonitorPlugin',
    'register_all_plugins'
]


def register_all_plugins(monitor):
    """Register all monitor plugins"""
    # Register plugins
    monitor.register_plugin(SystemHealthMonitorPlugin())
    monitor.register_plugin(AIUsageMonitorPlugin())

    # Add more plugins as they are created
