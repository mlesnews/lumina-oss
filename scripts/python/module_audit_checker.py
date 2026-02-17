#!/usr/bin/env python3
"""
Module Audit Checker - Verify Module Usage Before Implementation

Before implementing new functionality, check:
1. Does this already have a module?
2. Should it have a module?
3. Are we using existing modules correctly?

Tags: #MODULES #ARCHITECTURE #AUDIT #BEST-PRACTICES @LUMINA
"""

import sys
import ast
import importlib.util
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ModuleAuditChecker")


@dataclass
class ModuleInfo:
    """Information about a Python module"""
    name: str
    path: Path
    classes: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    purpose: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class DuplicateCheck:
    """Check for duplicate functionality"""
    functionality: str
    existing_modules: List[str]
    duplicate_locations: List[str]
    recommendation: str


class ModuleAuditChecker:
    """
    Audits codebase for module usage and identifies:
    - Existing modules that should be used
    - Duplicate implementations that should be consolidated
    - Missing modules that should be created
    """

    def __init__(self, scripts_dir: Path = None):
        """
        Initialize module auditor.

        Args:
            scripts_dir: Directory containing Python scripts (default: scripts/python)
        """
        if scripts_dir is None:
            scripts_dir = script_dir
        self.scripts_dir = Path(scripts_dir)
        self.modules: Dict[str, ModuleInfo] = {}
        self.duplicates: List[DuplicateCheck] = []

    def scan_modules(self) -> Dict[str, ModuleInfo]:
        """
        Scan scripts directory for all Python modules.

        Returns:
            Dictionary mapping module names to ModuleInfo
        """
        logger.info(f"🔍 Scanning modules in {self.scripts_dir}")

        for py_file in self.scripts_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue

            try:
                module_info = self._analyze_module(py_file)
                if module_info:
                    self.modules[module_info.name] = module_info
            except Exception as e:
                logger.warning(f"⚠️  Could not analyze {py_file.name}: {e}")

        logger.info(f"✅ Found {len(self.modules)} modules")
        return self.modules

    def _analyze_module(self, py_file: Path) -> Optional[ModuleInfo]:
        """Analyze a single Python file for module information"""
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content, filename=str(py_file))

            module_name = py_file.stem
            classes = []
            functions = []
            purpose = None
            tags = []

            # Extract docstring (purpose)
            if tree.body and isinstance(tree.body[0], ast.Expr):
                if isinstance(tree.body[0].value, ast.Str):
                    docstring = tree.body[0].value.s
                    # Extract purpose from docstring
                    if docstring:
                        lines = docstring.split('\n')
                        purpose = lines[0].strip() if lines else None
                        # Extract tags
                        for line in lines:
                            if 'Tags:' in line or '#TAG' in line:
                                tag_line = line.split('Tags:')[-1] if 'Tags:' in line else line
                                tags = [t.strip() for t in tag_line.split() if t.strip().startswith('#') or t.strip().startswith('@')]

            # Extract classes and functions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    if not node.name.startswith('_') or node.name.startswith('__'):
                        functions.append(node.name)

            return ModuleInfo(
                name=module_name,
                path=py_file,
                classes=classes,
                functions=functions,
                purpose=purpose,
                tags=tags
            )
        except Exception as e:
            logger.debug(f"Could not parse {py_file.name}: {e}")
            return None

    def check_for_duplicates(self, functionality: str) -> List[str]:
        """
        Check for duplicate implementations of functionality.

        Args:
            functionality: Description of functionality to check

        Returns:
            List of module names that implement this functionality
        """
        matches = []
        functionality_lower = functionality.lower()

        for module_name, module_info in self.modules.items():
            # Check module name
            if functionality_lower in module_name.lower():
                matches.append(module_name)
                continue

            # Check purpose
            if module_info.purpose and functionality_lower in module_info.purpose.lower():
                matches.append(module_name)
                continue

            # Check classes/functions
            for class_name in module_info.classes:
                if functionality_lower in class_name.lower():
                    matches.append(module_name)
                    break

            for func_name in module_info.functions:
                if functionality_lower in func_name.lower():
                    matches.append(module_name)
                    break

        return matches

    def recommend_module_usage(self, functionality: str) -> Optional[str]:
        """
        Recommend which module to use for functionality.

        Args:
            functionality: Description of functionality needed

        Returns:
            Recommended module name, or None if no module exists
        """
        matches = self.check_for_duplicates(functionality)

        if not matches:
            return None

        # Prefer modules with more specific names
        # e.g., "cursor_chat_retry_manager" over "retry_manager"
        specific_matches = [m for m in matches if functionality.lower() in m.lower()]
        if specific_matches:
            return specific_matches[0]

        return matches[0] if matches else None

    def audit_before_implementation(self, functionality: str) -> Dict[str, any]:
        """
        Audit before implementing new functionality.

        Returns:
            Dictionary with:
            - has_module: bool
            - recommended_module: str or None
            - should_create_module: bool
            - existing_implementations: List[str]
        """
        matches = self.check_for_duplicates(functionality)
        recommended = self.recommend_module_usage(functionality)

        return {
            "has_module": recommended is not None,
            "recommended_module": recommended,
            "should_create_module": recommended is None and len(matches) == 0,
            "existing_implementations": matches,
            "functionality": functionality
        }

    def generate_report(self) -> str:
        """Generate audit report"""
        report = []
        report.append("=" * 60)
        report.append("MODULE AUDIT REPORT")
        report.append("=" * 60)
        report.append("")
        report.append(f"Total Modules: {len(self.modules)}")
        report.append("")

        # Group by category
        categories = {
            "Logging": ["logger", "log"],
            "Retry": ["retry", "resilience"],
            "Error Handling": ["error", "exception", "handler"],
            "Voice": ["voice", "audio", "transcription"],
            "UI": ["ui", "window", "gui", "tkinter"],
            "Network": ["network", "http", "api", "request"],
        }

        for category, keywords in categories.items():
            matches = []
            for module_name, module_info in self.modules.items():
                if any(kw in module_name.lower() for kw in keywords):
                    matches.append(module_name)

            if matches:
                report.append(f"{category} Modules ({len(matches)}):")
                for match in sorted(matches):
                    report.append(f"  - {match}")
                report.append("")

        if self.duplicates:
            report.append("DUPLICATE IMPLEMENTATIONS:")
            for dup in self.duplicates:
                report.append(f"  - {dup.functionality}")
                report.append(f"    Existing: {', '.join(dup.existing_modules)}")
                report.append(f"    Recommendation: {dup.recommendation}")
                report.append("")

        return "\n".join(report)


def check_before_implementing(functionality: str) -> Dict[str, any]:
    """
    Convenience function to check for existing modules before implementing.

    Usage:
        result = check_before_implementing("retry logic")
        if result["has_module"]:
            # Use existing module
            from result["recommended_module"] import ...
        else:
            # Create new module
            ...
    """
    checker = ModuleAuditChecker()
    checker.scan_modules()
    return checker.audit_before_implementation(functionality)


if __name__ == "__main__":
    # Demo
    checker = ModuleAuditChecker()
    checker.scan_modules()

    # Check for common functionality
    checks = [
        "retry logic",
        "logging patterns",
        "error handling",
        "voice filtering",
        "transcription sending",
    ]

    print("MODULE AUDIT - Before Implementation Check")
    print("=" * 60)
    print()

    for check in checks:
        result = checker.audit_before_implementation(check)
        print(f"Functionality: {check}")
        print(f"  Has Module: {result['has_module']}")
        if result['recommended_module']:
            print(f"  Recommended: {result['recommended_module']}")
        print(f"  Should Create: {result['should_create_module']}")
        if result['existing_implementations']:
            print(f"  Existing: {', '.join(result['existing_implementations'])}")
        print()

    print(checker.generate_report())
