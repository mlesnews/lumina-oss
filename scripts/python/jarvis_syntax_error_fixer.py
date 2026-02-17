#!/usr/bin/env python3
"""
JARVIS Syntax Error Fixer

Automatically fixes syntax errors introduced by automatic error handling.
"""

import sys
import re
import ast
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISSyntaxErrorFixer")


class JARVISSyntaxErrorFixer:
    """
    Fix syntax errors from automatic error handling
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.fixes_applied = []

    def fix_incomplete_try_except(self, file_path: Path, line_number: int) -> bool:
        """Fix incomplete try/except blocks"""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')

            # Find the problematic try block
            problem_line_idx = line_number - 1

            # Look backwards for the try statement
            try_line_idx = None
            for i in range(problem_line_idx, max(-1, problem_line_idx - 20), -1):
                if 'try:' in lines[i] and not lines[i].strip().startswith('#'):
                    try_line_idx = i
                    break

            if try_line_idx is None:
                return False

            # Check if there's already an except or finally
            has_except = False
            has_finally = False
            for i in range(try_line_idx + 1, min(try_line_idx + 50, len(lines))):
                if 'except' in lines[i] and not lines[i].strip().startswith('#'):
                    has_except = True
                    break
                if 'finally:' in lines[i] and not lines[i].strip().startswith('#'):
                    has_finally = True
                    break
                # Check if we've left the function/scope
                if i > try_line_idx + 1:
                    current_indent = len(lines[i]) - len(lines[i].lstrip())
                    try_indent = len(lines[try_line_idx]) - len(lines[try_line_idx].lstrip())
                    if lines[i].strip() and current_indent <= try_indent:
                        break

            # If no except/finally, add one
            if not has_except and not has_finally:
                # Find where to insert except
                insert_idx = try_line_idx + 1
                try_indent = len(lines[try_line_idx]) - len(lines[try_line_idx].lstrip())

                # Find the end of the try block
                for i in range(try_line_idx + 1, len(lines)):
                    if lines[i].strip():
                        current_indent = len(lines[i]) - len(lines[i].lstrip())
                        if current_indent <= try_indent and i > try_line_idx + 1:
                            insert_idx = i
                            break

                # Insert except block
                except_block = [
                    ' ' * try_indent + 'except Exception as e:',
                    ' ' * (try_indent + 4) + 'self.logger.error(f"Error: {e}", exc_info=True)',
                    ' ' * (try_indent + 4) + 'raise'
                ]

                new_lines = lines[:insert_idx] + except_block + lines[insert_idx:]
                file_path.write_text('\n'.join(new_lines), encoding='utf-8')

                self.fixes_applied.append({
                    'file': str(file_path),
                    'line': line_number,
                    'fix': 'Added missing except block'
                })

                return True

            return False

        except Exception as e:
            self.logger.error(f"Error fixing {file_path}: {e}")
            return False

    def fix_syntax_errors(self, errors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fix all syntax errors"""
        self.logger.info("="*80)
        self.logger.info("JARVIS SYNTAX ERROR FIXER")
        self.logger.info("="*80)

        fixed_count = 0

        for error in errors:
            file_path = Path(error['file'])
            line_number = error.get('line', 0)
            error_msg = error.get('error', '')

            self.logger.info(f"Fixing: {file_path.name} (line {line_number})")

            # Fix incomplete try/except
            if 'except' in error_msg.lower() or 'finally' in error_msg.lower():
                if self.fix_incomplete_try_except(file_path, line_number):
                    fixed_count += 1
                    self.logger.info(f"   ✅ Fixed incomplete try/except")

            # Fix parenthesis issues
            elif 'parenthesis' in error_msg.lower():
                # Try to fix by reading and re-parsing
                try:
                    content = file_path.read_text(encoding='utf-8')
                    # Try to parse and see if we can identify the issue
                    ast.parse(content)
                    # If it parses, might be a false positive
                except SyntaxError as e:
                    # Manual fix needed
                    self.logger.warning(f"   ⚠️  Manual fix needed for parenthesis issue")

        self.logger.info("")
        self.logger.info(f"✅ Fixed {fixed_count} syntax errors")

        return {
            'success': True,
            'fixed': fixed_count,
            'fixes': self.fixes_applied
        }


def main():
    """CLI interface"""
    # Known syntax errors from validation
    errors = [
        {
            'file': 'C:\\Users\\mlesn\\Dropbox\\my_projects\\.lumina\\scripts\\python\\aios_kernel.py',
            'line': 325,
            'error': "closing parenthesis '}' does not match opening parenthesis '('"
        },
        {
            'file': 'C:\\Users\\mlesn\\Dropbox\\my_projects\\.lumina\\scripts\\python\\apply_anthropic_learnings.py',
            'line': 421,
            'error': "expected 'except' or 'finally' block'"
        },
        {
            'file': 'C:\\Users\\mlesn\\Dropbox\\my_projects\\.lumina\\scripts\\python\\auto_inject_cursor_find_issues.py',
            'line': 195,
            'error': "expected 'except' or 'finally' block'"
        },
        {
            'file': 'C:\\Users\\mlesn\\Dropbox\\my_projects\\.lumina\\scripts\\python\\babelfish_subtitle_extractor.py',
            'line': 212,
            'error': 'invalid syntax'
        },
        {
            'file': 'C:\\Users\\mlesn\\Dropbox\\my_projects\\.lumina\\scripts\\python\\convert_all_tasks_to_daemons.py',
            'line': 217,
            'error': "expected 'except' or 'finally' block'"
        }
    ]

    project_root = Path(__file__).parent.parent.parent
    fixer = JARVISSyntaxErrorFixer(project_root)

    result = fixer.fix_syntax_errors(errors)

    if result.get('success'):
        print(f"\n✅ Fixed {result['fixed']} syntax errors")
    else:
        print(f"\n❌ Error: {result.get('error', 'unknown')}")


if __name__ == "__main__":


    main()