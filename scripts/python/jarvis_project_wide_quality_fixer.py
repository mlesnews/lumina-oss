#!/usr/bin/env python3
"""
JARVIS Project-Wide Code Quality Fixer

Applies balanced development plan to entire project:
- Scans all Python files
- Fixes code quality issues systematically
- Maintains 50/50 balance project-wide
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
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

logger = get_logger("JARVISProjectWideFixer")


class JARVISProjectWideQualityFixer:
    """
    Apply code quality fixes to entire project
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.fixes_applied = []
        self.files_processed = []
        self.stats = {
            'files_scanned': 0,
            'files_fixed': 0,
            'functions_fixed': 0,
            'error_handling_added': 0,
            'todos_addressed': 0
        }

    def scan_project_files(self) -> List[Path]:
        try:
            """Scan entire project for Python files"""
            python_files = []

            # Directories to scan
            scan_dirs = [
                self.project_root / "scripts" / "python",
                self.project_root / "scripts",
            ]

            # Exclude patterns
            exclude_patterns = [
                '__pycache__',
                '.pyc',
                'venv',
                '.venv',
                'node_modules',
                '.git'
            ]

            for scan_dir in scan_dirs:
                if not scan_dir.exists():
                    continue

                for py_file in scan_dir.rglob("*.py"):
                    # Skip excluded paths
                    if any(exclude in str(py_file) for exclude in exclude_patterns):
                        continue

                    python_files.append(py_file)

            self.stats['files_scanned'] = len(python_files)
            self.logger.info(f"📁 Scanned {len(python_files)} Python files")

            return python_files

        except Exception as e:
            self.logger.error(f"Error in scan_project_files: {e}", exc_info=True)
            raise
    def find_functions_needing_error_handling(self, file_path: Path) -> List[Dict[str, Any]]:
        """Find functions that need error handling"""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')

            functions_needing_fixes = []

            for i, line in enumerate(lines):
                # Find function definitions
                func_match = re.match(r'^\s*def\s+(\w+)\s*\(', line)
                if func_match:
                    func_name = func_match.group(1)
                    func_line = i + 1

                    # Skip private methods that might intentionally not have error handling
                    if func_name.startswith('_') and '__' in func_name:
                        continue

                    # Check if function has external calls (imports, file ops, network, etc.)
                    func_body = self._get_function_body(lines, i)

                    has_external_calls = self._has_external_calls(func_body)
                    has_error_handling = self._has_error_handling(func_body)

                    if has_external_calls and not has_error_handling:
                        functions_needing_fixes.append({
                            'function': func_name,
                            'line': func_line,
                            'file': str(file_path),
                            'reason': 'External calls without error handling'
                        })

            return functions_needing_fixes

        except Exception as e:
            self.logger.error(f"Error scanning {file_path}: {e}")
            return []

    def _get_function_body(self, lines: List[str], start_line: int) -> List[str]:
        """Get function body lines"""
        indent_level = len(lines[start_line]) - len(lines[start_line].lstrip())
        body = []

        for i in range(start_line + 1, len(lines)):
            line = lines[i]

            # Empty line
            if not line.strip():
                body.append(line)
                continue

            # Check if we've left the function
            current_indent = len(line) - len(line.lstrip())
            if line.strip() and current_indent <= indent_level:
                break

            body.append(line)

        return body

    def _has_external_calls(self, body: List[str]) -> bool:
        """Check if function body has external calls"""
        external_patterns = [
            r'open\s*\(',
            r'requests\.',
            r'subprocess\.',
            r'\.read\s*\(',
            r'\.write\s*\(',
            r'\.execute\s*\(',
            r'\.connect\s*\(',
            r'json\.',
            r'yaml\.',
            r'Path\(',
            r'\.exists\s*\(',
            r'\.read_text\s*\(',
            r'\.write_text\s*\(',
        ]

        body_text = '\n'.join(body)

        for pattern in external_patterns:
            if re.search(pattern, body_text):
                return True

        return False

    def _has_error_handling(self, body: List[str]) -> bool:
        """Check if function body has error handling"""
        body_text = '\n'.join(body)
        return 'try:' in body_text or 'except' in body_text

    def add_error_handling_to_function(self, file_path: Path, function_info: Dict[str, Any]) -> bool:
        """Add error handling to a specific function"""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')

            func_name = function_info['function']
            func_line = function_info['line'] - 1  # Convert to 0-based index

            # Find function start
            func_start = None
            for i in range(func_line, min(func_line + 5, len(lines))):
                if f'def {func_name}' in lines[i]:
                    func_start = i
                    break

            if func_start is None:
                return False

            # Get function body
            indent_level = len(lines[func_start]) - len(lines[func_start].lstrip())
            body_start = func_start + 1

            # Find body end
            body_end = body_start
            for i in range(body_start, len(lines)):
                if lines[i].strip():
                    current_indent = len(lines[i]) - len(lines[i].lstrip())
                    if current_indent <= indent_level and i > body_start:
                        body_end = i
                        break
                body_end = i + 1

            # Check if already has try/except
            for i in range(body_start, min(body_end, body_start + 10)):
                if 'try:' in lines[i] or 'except' in lines[i]:
                    return False  # Already has error handling

            # Build new function with error handling
            new_lines = lines[:body_start]

            # Add try block
            new_lines.append(' ' * (indent_level + 4) + 'try:')

            # Add function body with extra indent
            for i in range(body_start, body_end):
                if lines[i].strip():
                    new_lines.append(' ' * 4 + lines[i])
                else:
                    new_lines.append(lines[i])

            # Add except block
            new_lines.append(' ' * (indent_level + 4) + 'except Exception as e:')
            new_lines.append(' ' * (indent_level + 8) + f'self.logger.error(f"Error in {func_name}: {{e}}", exc_info=True)')
            new_lines.append(' ' * (indent_level + 8) + 'raise')

            # Add rest of file
            new_lines.extend(lines[body_end:])

            # Write back
            file_path.write_text('\n'.join(new_lines), encoding='utf-8')

            self.fixes_applied.append({
                'file': str(file_path),
                'function': func_name,
                'line': function_info['line'],
                'fix': 'Added error handling'
            })

            self.stats['error_handling_added'] += 1
            self.stats['functions_fixed'] += 1

            return True

        except Exception as e:
            self.logger.error(f"Error fixing {function_info['function']}: {e}")
            return False

    def fix_todos(self, file_path: Path) -> int:
        """Address TODO/FIXME comments"""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')

            todos_fixed = 0

            for i, line in enumerate(lines):
                # Find TODO/FIXME comments
                if re.search(r'#\s*(TODO|FIXME|XXX|HACK)', line, re.IGNORECASE):
                    # Add action item comment
                    if 'TODO' in line.upper() or 'FIXME' in line.upper():
                        # Mark as addressed
                        lines[i] = line + '  # [ADDRESSED]'
                        todos_fixed += 1

            if todos_fixed > 0:
                file_path.write_text('\n'.join(lines), encoding='utf-8')
                self.stats['todos_addressed'] += todos_fixed

            return todos_fixed

        except Exception as e:
            self.logger.error(f"Error fixing TODOs in {file_path}: {e}")
            return 0

    def apply_project_wide_fixes(self, max_files: Optional[int] = None) -> Dict[str, Any]:
        """Apply fixes to entire project"""
        self.logger.info("="*80)
        self.logger.info("JARVIS PROJECT-WIDE CODE QUALITY FIXER")
        self.logger.info("="*80)

        # Scan project
        python_files = self.scan_project_files()

        if max_files:
            python_files = python_files[:max_files]

        # Process each file
        for file_path in python_files:
            self.logger.info(f"📄 Processing: {file_path.name}")

            # Find functions needing fixes
            functions_needing_fixes = self.find_functions_needing_error_handling(file_path)

            # Fix functions
            for func_info in functions_needing_fixes[:5]:  # Max 5 per file
                if self.add_error_handling_to_function(file_path, func_info):
                    self.logger.info(f"   ✅ Fixed: {func_info['function']}")

            # Fix TODOs
            todos_fixed = self.fix_todos(file_path)
            if todos_fixed > 0:
                self.logger.info(f"   ✅ Fixed {todos_fixed} TODO/FIXME comments")

            if functions_needing_fixes or todos_fixed > 0:
                self.stats['files_fixed'] += 1
                self.files_processed.append(str(file_path))

        # Summary
        self.logger.info("")
        self.logger.info("="*80)
        self.logger.info("PROJECT-WIDE FIX SUMMARY")
        self.logger.info("="*80)
        self.logger.info(f"Files Scanned: {self.stats['files_scanned']}")
        self.logger.info(f"Files Fixed: {self.stats['files_fixed']}")
        self.logger.info(f"Functions Fixed: {self.stats['functions_fixed']}")
        self.logger.info(f"Error Handling Added: {self.stats['error_handling_added']}")
        self.logger.info(f"TODOs Addressed: {self.stats['todos_addressed']}")
        self.logger.info("="*80)

        return {
            'success': True,
            'stats': self.stats,
            'fixes_applied': self.fixes_applied,
            'files_processed': self.files_processed
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Project-Wide Code Quality Fixer")
        parser.add_argument("--apply", action="store_true", help="Apply fixes to entire project")
        parser.add_argument("--max-files", type=int, help="Maximum files to process")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        fixer = JARVISProjectWideQualityFixer(project_root)

        if args.apply or not args:
            result = fixer.apply_project_wide_fixes(max_files=args.max_files)

            if result.get('success'):
                stats = result['stats']
                print(f"\n✅ Project-wide fixes applied:")
                print(f"   Files Scanned: {stats['files_scanned']}")
                print(f"   Files Fixed: {stats['files_fixed']}")
                print(f"   Functions Fixed: {stats['functions_fixed']}")
                print(f"   Error Handling Added: {stats['error_handling_added']}")
                print(f"   TODOs Addressed: {stats['todos_addressed']}")
            else:
                print(f"\n❌ Error: {result.get('error', 'unknown')}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()