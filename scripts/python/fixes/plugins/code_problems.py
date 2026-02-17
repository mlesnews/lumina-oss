"""
Code Problems Fix Plugin

Fixes code structure and syntax issues.
Consolidates: jarvis_auto_fix_code_problems.py
"""

import sys
import ast
import subprocess
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

logger = get_logger("CodeProblemsFixPlugin")


class CodeProblemsFixPlugin(FixPlugin):
    """Fix code structure and syntax issues"""

    def __init__(self):
        super().__init__(
            fix_type=FixType.CODE_PROBLEMS,
            name="Code Problems Fixer",
            description="Detects and fixes code structure, syntax, and import issues"
        )

    def can_fix(self, issue: str) -> bool:
        """Check if this plugin can fix the issue"""
        issue_lower = issue.lower()
        return any(keyword in issue_lower for keyword in [
            'syntax error', 'attribute error', 'import error', 'code problem',
            'missing method', 'code structure'
        ])

    def detect(self, **kwargs) -> List[str]:
        """Detect code problems"""
        issues = []
        project_root = kwargs.get('project_root', Path(__file__).parent.parent.parent.parent)

        # Check for syntax errors in key files
        key_files = [
            project_root / "scripts" / "python" / "jarvis_physician_heal_thyself.py",
            # Add more key files to check
        ]

        for file_path in key_files:
            if file_path.exists():
                try:
                    # Try to parse the file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        ast.parse(f.read())
                except SyntaxError as e:
                    issues.append(f"Syntax error in {file_path.name}: {e}")
                except Exception as e:
                    issues.append(f"Error checking {file_path.name}: {e}")

        return issues

    def fix(self, **kwargs) -> FixResult:
        """Fix code problems"""
        project_root = kwargs.get('project_root', Path(__file__).parent.parent.parent.parent)

        try:
            # Import and use the existing fix function
            try:
                from jarvis_auto_fix_code_problems import JARVISAutoFixCodeProblems
                fixer = JARVISAutoFixCodeProblems(project_root)
                results = fixer.detect_and_fix_all_problems()

                return FixResult(
                    fix_type=self.fix_type,
                    success=len(results.get("problems_fixed", [])) > 0,
                    message=f"Fixed {len(results.get('problems_fixed', []))} code problem(s)",
                    details=results
                )
            except ImportError:
                # Fallback if module doesn't exist
                logger.warning("jarvis_auto_fix_code_problems not available")
                return FixResult(
                    fix_type=self.fix_type,
                    success=False,
                    message="Code problems fix module not available",
                    details={"error": "Module not found"}
                )

        except Exception as e:
            return FixResult(
                fix_type=self.fix_type,
                success=False,
                message=f"Failed to fix code problems: {e}",
                details={"error": str(e)}
            )
