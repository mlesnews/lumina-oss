"""
Fix Plugins

Individual fix implementations as plugins.
"""

from .cursor_config import CursorConfigFixPlugin
from .local_models import LocalModelsFixPlugin
from .code_problems import CodeProblemsFixPlugin
from .ask_retries import AskRetriesFixPlugin
from .iron_legion import IronLegionFixPlugin
from .connection_errors import ConnectionErrorsFixPlugin
from .cursor_stability import CursorStabilityFixPlugin

__all__ = [
    'CursorConfigFixPlugin',
    'LocalModelsFixPlugin',
    'CodeProblemsFixPlugin',
    'AskRetriesFixPlugin',
    'IronLegionFixPlugin',
    'ConnectionErrorsFixPlugin',
    'CursorStabilityFixPlugin',
    'register_all_plugins'
]


def register_all_plugins(fixer):
    """Register all fix plugins"""
    # Register plugins
    fixer.register_plugin(CursorConfigFixPlugin())
    fixer.register_plugin(LocalModelsFixPlugin())
    fixer.register_plugin(CodeProblemsFixPlugin())
    fixer.register_plugin(AskRetriesFixPlugin())
    fixer.register_plugin(IronLegionFixPlugin())
    fixer.register_plugin(ConnectionErrorsFixPlugin())
    fixer.register_plugin(CursorStabilityFixPlugin())

    # Add more plugins as they are created
