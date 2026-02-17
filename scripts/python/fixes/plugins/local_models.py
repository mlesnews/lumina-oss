"""
Local Models Fix Plugin

Fixes local model configuration issues.
Consolidates: auto_fix_local_models_on_startup.py, fix_local_models_no_subscription_error.py
"""

import sys
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

logger = get_logger("LocalModelsFixPlugin")


class LocalModelsFixPlugin(FixPlugin):
    """Fix local model configuration issues"""

    def __init__(self):
        super().__init__(
            fix_type=FixType.LOCAL_MODELS,
            name="Local Models Fixer",
            description="Fixes local model configuration to prevent subscription errors"
        )

    def can_fix(self, issue: str) -> bool:
        """Check if this plugin can fix the issue"""
        issue_lower = issue.lower()
        return any(keyword in issue_lower for keyword in [
            'local model', 'subscription error', 'ollama', 'ultron', 'kaiju'
        ])

    def detect(self, **kwargs) -> List[str]:
        """Detect local model issues"""
        issues = []

        # Check if local models are configured correctly
        # This would integrate with the actual fix_local_models_no_subscription_error logic

        return issues

    def fix(self, **kwargs) -> FixResult:
        """Fix local model configuration"""
        project_root = kwargs.get('project_root', Path(__file__).parent.parent.parent.parent)

        try:
            # Import and use the existing fix function
            try:
                from fix_local_models_no_subscription_error import fix_all_local_models
                fix_all_local_models(project_root)

                return FixResult(
                    fix_type=self.fix_type,
                    success=True,
                    message="Local models configuration fixed",
                    details={"project_root": str(project_root)}
                )
            except ImportError:
                # Fallback if module doesn't exist
                logger.warning("fix_local_models_no_subscription_error not available")
                return FixResult(
                    fix_type=self.fix_type,
                    success=False,
                    message="Local models fix module not available",
                    details={"error": "Module not found"}
                )

        except Exception as e:
            return FixResult(
                fix_type=self.fix_type,
                success=False,
                message=f"Failed to fix local models: {e}",
                details={"error": str(e)}
            )
