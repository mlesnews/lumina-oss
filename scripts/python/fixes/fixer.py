#!/usr/bin/env python3
"""
Unified Fix System - Main Fixer

Plugin-based architecture for all fix operations.
Consolidates all fix scripts into a single unified system.

Tags: #FIX #UNIFIED #PLUGIN @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("UnifiedFixer")


class FixType(Enum):
    """Types of fixes available"""
    CURSOR_CONFIG = "cursor_config"
    LOCAL_MODELS = "local_models"
    CODE_PROBLEMS = "code_problems"
    BEDROCK_ROUTING = "bedrock_routing"
    ASK_RETRIES = "ask_retries"
    BAD_REQUEST = "bad_request"
    IRON_LEGION = "iron_legion"
    KEYBOARD = "keyboard"
    LIGHTING = "lighting"
    SECURITY = "security"
    INDEXING = "indexing"
    CONNECTION_ERRORS = "connection_errors"
    CURSOR_STABILITY = "cursor_stability"
    OTHER = "other"


@dataclass
class FixResult:
    """Result of a fix operation"""
    fix_type: FixType
    success: bool
    message: str
    details: Dict[str, Any] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()


class FixPlugin:
    """Base class for fix plugins"""

    def __init__(self, fix_type: FixType, name: str, description: str):
        self.fix_type = fix_type
        self.name = name
        self.description = description

    def can_fix(self, issue: str) -> bool:
        """Check if this plugin can fix the given issue"""
        return False

    def fix(self, **kwargs) -> FixResult:
        """Execute the fix"""
        raise NotImplementedError("Subclasses must implement fix()")

    def detect(self, **kwargs) -> List[str]:
        """Detect issues that this plugin can fix"""
        return []


class UnifiedFixer:
    """
    Unified Fix System

    Consolidates all fix scripts into a single plugin-based system.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize unified fixer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.plugins: Dict[FixType, List[FixPlugin]] = {}
        self.fix_history: List[FixResult] = []

        logger.info("🔧 Unified Fix System initialized")

    def register_plugin(self, plugin: FixPlugin):
        """Register a fix plugin"""
        if plugin.fix_type not in self.plugins:
            self.plugins[plugin.fix_type] = []

        self.plugins[plugin.fix_type].append(plugin)
        logger.debug(f"   Registered plugin: {plugin.name} ({plugin.fix_type.value})")

    def list_fixes(self) -> Dict[str, List[str]]:
        """List all available fixes"""
        fixes = {}
        for fix_type, plugins in self.plugins.items():
            fixes[fix_type.value] = [p.name for p in plugins]
        return fixes

    def fix(self, fix_type: FixType, **kwargs) -> FixResult:
        """
        Execute a fix by type

        Args:
            fix_type: Type of fix to execute
            **kwargs: Arguments for the fix plugin

        Returns:
            FixResult with fix outcome
        """
        if fix_type not in self.plugins:
            return FixResult(
                fix_type=fix_type,
                success=False,
                message=f"No plugins registered for {fix_type.value}",
                details={"available_types": list(self.plugins.keys())}
            )

        # Try each plugin for this type
        for plugin in self.plugins[fix_type]:
            try:
                logger.info(f"🔧 Running fix: {plugin.name}")
                result = plugin.fix(**kwargs)
                self.fix_history.append(result)
                return result
            except Exception as e:
                logger.error(f"❌ Plugin {plugin.name} failed: {e}")
                continue

        return FixResult(
            fix_type=fix_type,
            success=False,
            message=f"All plugins for {fix_type.value} failed",
            details={"plugins_tried": [p.name for p in self.plugins[fix_type]]}
        )

    def auto_fix(self, issue_description: str, **kwargs) -> List[FixResult]:
        """
        Automatically detect and fix issues based on description

        Args:
            issue_description: Description of the issue
            **kwargs: Additional context

        Returns:
            List of FixResult objects
        """
        results = []

        # Check all plugins to see if they can fix this issue
        for fix_type, plugins in self.plugins.items():
            for plugin in plugins:
                if plugin.can_fix(issue_description):
                    logger.info(f"🔍 Auto-detected fix: {plugin.name}")
                    result = plugin.fix(**kwargs)
                    results.append(result)

        return results

    def detect_all_issues(self) -> Dict[FixType, List[str]]:
        """Detect all issues that can be fixed"""
        issues = {}

        for fix_type, plugins in self.plugins.items():
            type_issues = []
            for plugin in plugins:
                try:
                    detected = plugin.detect()
                    type_issues.extend(detected)
                except Exception as e:
                    logger.debug(f"Plugin {plugin.name} detection failed: {e}")

            if type_issues:
                issues[fix_type] = type_issues

        return issues

    def get_history(self, limit: int = 50) -> List[FixResult]:
        """Get fix history"""
        return self.fix_history[-limit:]


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Unified Fix System")
    parser.add_argument("--type", type=str, help="Fix type to execute")
    parser.add_argument("--list", action="store_true", help="List all available fixes")
    parser.add_argument("--detect", action="store_true", help="Detect all fixable issues")
    parser.add_argument("--auto", type=str, help="Auto-fix based on issue description")
    parser.add_argument("--history", type=int, help="Show fix history (limit)")

    args = parser.parse_args()

    # Initialize fixer
    fixer = UnifiedFixer()

    # Register all plugins
    try:
        from .plugins import register_all_plugins
    except ImportError:
        try:
            from fixes.plugins import register_all_plugins
        except ImportError:
            # Add scripts/python to path
            import sys
            scripts_python = Path(__file__).parent.parent
            if str(scripts_python) not in sys.path:
                sys.path.insert(0, str(scripts_python))
            from fixes.plugins import register_all_plugins
    register_all_plugins(fixer)

    if args.list:
        print("=" * 80)
        print("🔧 AVAILABLE FIXES")
        print("=" * 80)
        fixes = fixer.list_fixes()
        for fix_type, plugins in fixes.items():
            print(f"\n{fix_type}:")
            for plugin in plugins:
                print(f"   - {plugin}")

    elif args.detect:
        print("=" * 80)
        print("🔍 DETECTING ISSUES")
        print("=" * 80)
        issues = fixer.detect_all_issues()
        if issues:
            for fix_type, type_issues in issues.items():
                print(f"\n{fix_type.value}:")
                for issue in type_issues:
                    print(f"   - {issue}")
        else:
            print("✅ No issues detected")

    elif args.auto:
        print("=" * 80)
        print(f"🔧 AUTO-FIXING: {args.auto}")
        print("=" * 80)
        results = fixer.auto_fix(args.auto)
        for result in results:
            status = "✅" if result.success else "❌"
            print(f"{status} {result.fix_type.value}: {result.message}")

    elif args.type:
        try:
            fix_type = FixType(args.type)
            print("=" * 80)
            print(f"🔧 EXECUTING FIX: {fix_type.value}")
            print("=" * 80)
            result = fixer.fix(fix_type)
            status = "✅" if result.success else "❌"
            print(f"{status} {result.message}")
            if result.details:
                print(f"Details: {result.details}")
        except ValueError:
            print(f"❌ Unknown fix type: {args.type}")
            print(f"Available types: {[t.value for t in FixType]}")

    elif args.history:
        print("=" * 80)
        print(f"📜 FIX HISTORY (last {args.history})")
        print("=" * 80)
        history = fixer.get_history(args.history)
        for result in history:
            status = "✅" if result.success else "❌"
            print(f"{status} [{result.timestamp}] {result.fix_type.value}: {result.message}")

    else:
        parser.print_help()


if __name__ == "__main__":


    main()