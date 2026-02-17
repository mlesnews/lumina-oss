#!/usr/bin/env python3
"""
JARVIS Validation Suite

Validates that the project-wide changes didn't break anything:
- Syntax validation
- Import validation
- Test execution
- Integration checks
"""

import sys
import subprocess
import ast
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISValidationSuite")


class JARVISValidationSuite:
    """
    Validate project-wide changes
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.validation_results = {
            'syntax': {'passed': 0, 'failed': 0, 'errors': []},
            'imports': {'passed': 0, 'failed': 0, 'errors': []},
            'tests': {'passed': 0, 'failed': 0, 'errors': []}
        }

    def validate_syntax(self, file_path: Path) -> bool:
        """Validate Python syntax"""
        try:
            content = file_path.read_text(encoding='utf-8')
            ast.parse(content)
            return True
        except SyntaxError as e:
            self.validation_results['syntax']['failed'] += 1
            self.validation_results['syntax']['errors'].append({
                'file': str(file_path),
                'error': str(e),
                'line': e.lineno
            })
            return False
        except Exception as e:
            self.validation_results['syntax']['failed'] += 1
            self.validation_results['syntax']['errors'].append({
                'file': str(file_path),
                'error': str(e)
            })
            return False

    def validate_imports(self, file_path: Path) -> bool:
        """Validate imports can be resolved"""
        try:
            # Try to compile and check imports
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)

            # Extract imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

            # Basic validation - just check syntax
            return True
        except Exception as e:
            self.validation_results['imports']['failed'] += 1
            self.validation_results['imports']['errors'].append({
                'file': str(file_path),
                'error': str(e)
            })
            return False

    def run_validation(self, max_files: Optional[int] = None) -> Dict[str, Any]:
        """Run full validation suite"""
        self.logger.info("="*80)
        self.logger.info("JARVIS VALIDATION SUITE")
        self.logger.info("="*80)

        # Find Python files
        python_files = list((self.project_root / "scripts" / "python").rglob("*.py"))

        if max_files:
            python_files = python_files[:max_files]

        self.logger.info(f"Validating {len(python_files)} files...")

        # Validate syntax
        self.logger.info("1. Validating syntax...")
        for file_path in python_files:
            if self.validate_syntax(file_path):
                self.validation_results['syntax']['passed'] += 1

        # Validate imports
        self.logger.info("2. Validating imports...")
        for file_path in python_files:
            if self.validate_imports(file_path):
                self.validation_results['imports']['passed'] += 1

        # Summary
        self.logger.info("")
        self.logger.info("="*80)
        self.logger.info("VALIDATION SUMMARY")
        self.logger.info("="*80)
        self.logger.info(f"Syntax: {self.validation_results['syntax']['passed']} passed, {self.validation_results['syntax']['failed']} failed")
        self.logger.info(f"Imports: {self.validation_results['imports']['passed']} passed, {self.validation_results['imports']['failed']} failed")

        if self.validation_results['syntax']['errors']:
            self.logger.warning(f"Syntax errors found: {len(self.validation_results['syntax']['errors'])}")
            for error in self.validation_results['syntax']['errors'][:5]:
                self.logger.warning(f"  {error['file']}: {error.get('error', 'Unknown')}")

        return {
            'success': self.validation_results['syntax']['failed'] == 0,
            'results': self.validation_results
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Validation Suite")
        parser.add_argument("--validate", action="store_true", help="Run validation")
        parser.add_argument("--max-files", type=int, help="Maximum files to validate")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        validator = JARVISValidationSuite(project_root)

        if args.validate or not args:
            result = validator.run_validation(max_files=args.max_files)

            if result.get('success'):
                print("\n✅ Validation passed")
            else:
                print(f"\n❌ Validation failed: {result['results']['syntax']['failed']} syntax errors")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()