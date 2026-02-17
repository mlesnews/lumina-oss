"""
Cursor Config Fix Plugin

Fixes Cursor IDE configuration issues.
Consolidates: fix_cursor_bedrock_routing.py, fix_cursor_iron_legion_model.py, etc.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List

script_dir = Path(__file__).parent.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from fixes.fixer import FixPlugin, FixType, FixResult
except ImportError:
    from ..fixer import FixPlugin, FixType, FixResult

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CursorConfigFixPlugin")


class CursorConfigFixPlugin(FixPlugin):
    """Fix Cursor IDE configuration issues"""

    def __init__(self):
        super().__init__(
            fix_type=FixType.CURSOR_CONFIG,
            name="Cursor Config Fixer",
            description="Fixes Cursor IDE configuration issues (Bedrock routing, model config, etc.)"
        )

        # Cursor settings paths
        self.cursor_settings_paths = [
            Path.home() / ".cursor" / "settings.json",
            Path.home() / ".cursor" / "User" / "settings.json",
            Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "settings.json",
            Path.home() / "Library" / "Application Support" / "Cursor" / "User" / "settings.json",
        ]

    def can_fix(self, issue: str) -> bool:
        """Check if this plugin can fix the issue"""
        issue_lower = issue.lower()
        return any(keyword in issue_lower for keyword in [
            'cursor', 'bedrock', 'routing', 'model config', 'settings'
        ])

    def detect(self, **kwargs) -> List[str]:
        """Detect Cursor configuration issues"""
        issues = []
        settings_path = self._find_settings()

        if not settings_path:
            issues.append("Cursor settings.json not found")
            return issues

        try:
            settings = self._load_settings(settings_path)

            # Check for common issues
            if "cursor.ai.model" in settings:
                model = settings.get("cursor.ai.model", "")
                if "bedrock" in model.lower() and "ultron" in model.lower():
                    issues.append("Bedrock routing to ULTRON models (should be local)")

            # Add more detection logic as needed

        except Exception as e:
            issues.append(f"Error reading settings: {e}")

        return issues

    def fix(self, **kwargs) -> FixResult:
        """Fix Cursor configuration"""
        settings_path = self._find_settings()

        if not settings_path:
            return FixResult(
                fix_type=self.fix_type,
                success=False,
                message="Cursor settings.json not found",
                details={"searched_paths": [str(p) for p in self.cursor_settings_paths]}
            )

        try:
            settings = self._load_settings(settings_path)
            original_settings = settings.copy()

            # Apply fixes
            fixed = False

            # Fix Bedrock routing
            if "cursor.ai.model" in settings:
                model = settings.get("cursor.ai.model", "")
                if "bedrock" in model.lower() and "ultron" in model.lower():
                    # Remove bedrock routing for local models
                    settings["cursor.ai.model"] = model.replace("bedrock:", "").replace("Bedrock:", "")
                    fixed = True

            # Add more fix logic as needed

            if fixed:
                self._save_settings(settings_path, settings, original_settings)
                return FixResult(
                    fix_type=self.fix_type,
                    success=True,
                    message="Cursor configuration fixed",
                    details={"settings_path": str(settings_path), "changes": "Bedrock routing removed"}
                )
            else:
                return FixResult(
                    fix_type=self.fix_type,
                    success=True,
                    message="No fixes needed",
                    details={"settings_path": str(settings_path)}
                )

        except Exception as e:
            return FixResult(
                fix_type=self.fix_type,
                success=False,
                message=f"Failed to fix Cursor config: {e}",
                details={"error": str(e)}
            )

    def _find_settings(self) -> Path:
        try:
            """Find Cursor settings file"""
            for path in self.cursor_settings_paths:
                if path.exists():
                    return path
            return None

        except Exception as e:
            self.logger.error(f"Error in _find_settings: {e}", exc_info=True)
            raise
    def _load_settings(self, settings_path: Path) -> Dict[str, Any]:
        try:
            """Load Cursor settings"""
            with open(settings_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            self.logger.error(f"Error in _load_settings: {e}", exc_info=True)
            raise
    def _save_settings(self, settings_path: Path, settings: Dict[str, Any], original: Dict[str, Any]):
        try:
            """Save Cursor settings with backup"""
            import shutil

            # Create backup
            backup_path = settings_path.with_suffix('.json.backup')
            if settings_path.exists():
                shutil.copy2(settings_path, backup_path)
                logger.info(f"📦 Backup created: {backup_path}")

            # Save settings
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)

            logger.info(f"✅ Settings saved: {settings_path}")

        except Exception as e:
            self.logger.error(f"Error in _save_settings: {e}", exc_info=True)
            raise