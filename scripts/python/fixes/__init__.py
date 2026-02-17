"""
Unified Fix System

Plugin-based architecture for all fix operations.
Each fix type is registered as a plugin.

Tags: #FIX #UNIFIED #PLUGIN @JARVIS @LUMINA
"""

from .fixer import UnifiedFixer, FixType, FixResult
from .plugins import register_all_plugins

__all__ = ['UnifiedFixer', 'FixType', 'FixResult', 'register_all_plugins']
