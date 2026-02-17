"""
Unified Monitoring System

Plugin-based architecture for all monitoring operations.
Each monitoring type is registered as a plugin.

Tags: #MONITORING #UNIFIED #PLUGIN @JARVIS @LUMINA
"""

from .monitor import UnifiedMonitor, MonitorType, MonitorResult
from .plugins import register_all_plugins

__all__ = ['UnifiedMonitor', 'MonitorType', 'MonitorResult', 'register_all_plugins']
