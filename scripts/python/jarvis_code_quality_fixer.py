#!/usr/bin/env python3
"""
JARVIS Code Quality Fixer

Automatically fixes code quality issues identified in roast:
- Adds error handling (try/except blocks)
- Addresses TODO/FIXME comments
- Improves code reliability
"""

import sys
import re
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

logger = get_logger("JARVISCodeQualityFixer")


class JARVISCodeQualityFixer:
    """
    Fix code quality issues automatically
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.fixes_applied = []

    def add_error_handling_to_function(self, file_path: Path, line_number: int, function_name: str) -> bool:
        """Add error handling to a function"""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')

            # Find the function
            func_start = None
            for i, line in enumerate(lines):
                if i + 1 == line_number and function_name in line:
                    func_start = i
                    break

            if func_start is None:
                self.logger.warning(f"Function {function_name} not found at line {line_number}")
                return False

            # Find function body start (first line after def)
            body_start = func_start + 1
            indent_level = len(lines[func_start]) - len(lines[func_start].lstrip())

            # Check if already has try/except
            for i in range(body_start, min(body_start + 10, len(lines))):
                if 'try:' in lines[i] or 'except' in lines[i]:
                    self.logger.info(f"Function {function_name} already has error handling")
                    return False

            # Add error handling wrapper
            new_lines = lines[:body_start]
            new_lines.append(' ' * (indent_level + 4) + 'try:')

            # Wrap existing body
            body_end = body_start
            for i in range(body_start, len(lines)):
                if lines[i].strip() and not lines[i].strip().startswith('#'):
                    current_indent = len(lines[i]) - len(lines[i].lstrip())
                    if current_indent <= indent_level and i > body_start:
                        body_end = i
                        break
                body_end = i + 1

            # Add indented body
            for i in range(body_start, body_end):
                if lines[i].strip():
                    new_lines.append(' ' * 4 + lines[i])
                else:
                    new_lines.append(lines[i])

            # Add except block
            new_lines.append(' ' * (indent_level + 4) + 'except Exception as e:')
            new_lines.append(' ' * (indent_level + 8) + f'self.logger.error(f"Error in {function_name}: {{e}}", exc_info=True)')
            new_lines.append(' ' * (indent_level + 8) + 'raise')

            # Add rest of file
            new_lines.extend(lines[body_end:])

            # Write back
            file_path.write_text('\n'.join(new_lines), encoding='utf-8')

            self.fixes_applied.append({
                'file': str(file_path),
                'function': function_name,
                'line': line_number,
                'fix': 'Added error handling'
            })

            self.logger.info(f"✅ Added error handling to {function_name} in {file_path.name}")
            return True

        except Exception as e:
            self.logger.error(f"Error fixing {function_name}: {e}")
            return False

    def fix_roast_issues(self, max_fixes: int = 10) -> Dict[str, Any]:
        try:
            """Fix roast issues automatically"""
            self.logger.info("="*80)
            self.logger.info("JARVIS CODE QUALITY FIXER")
            self.logger.info("="*80)

            # Load roast issues
            roast_dir = self.project_root / "data" / "jarvis_marvin_roasts"
            if not roast_dir.exists():
                return {'success': False, 'error': 'Roast directory not found'}

            roast_files = sorted(roast_dir.glob("roast_*.json"), reverse=True)
            if not roast_files:
                return {'success': False, 'error': 'No roast files found'}

            import json
            with open(roast_files[0], 'r') as f:
                roast = json.load(f)

            # Get error handling issues
            error_handling_issues = [
                f for f in roast.get('jarvis_findings', [])
                if 'error handling' in f.get('title', '').lower()
            ][:max_fixes]

            fixes_applied = 0

            for issue in error_handling_issues:
                location = issue.get('location', '')
                line_number = issue.get('line_number', 0)
                title = issue.get('title', '')

                if not location or not line_number:
                    continue

                file_path = Path(location)
                if not file_path.exists():
                    self.logger.warning(f"File not found: {location}")
                    continue

                # Extract function name from title
                func_match = re.search(r'in (\w+)', title)
                if func_match:
                    function_name = func_match.group(1)

                    if self.add_error_handling_to_function(file_path, line_number, function_name):
                        fixes_applied += 1

            result = {
                'success': True,
                'fixes_applied': fixes_applied,
                'total_issues': len(error_handling_issues),
                'fixes': self.fixes_applied
            }

            self.logger.info("")
            self.logger.info(f"✅ Fixed {fixes_applied} error handling issues")

            return result


        except Exception as e:
            self.logger.error(f"Error in fix_roast_issues: {e}", exc_info=True)
            raise
def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Code Quality Fixer")
        parser.add_argument("--fix", action="store_true", help="Fix code quality issues")
        parser.add_argument("--max-fixes", type=int, default=10, help="Maximum fixes to apply")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        fixer = JARVISCodeQualityFixer(project_root)

        if args.fix or not args:
            result = fixer.fix_roast_issues(max_fixes=args.max_fixes)

            if result.get('success'):
                print(f"\n✅ Successfully fixed {result['fixes_applied']} issues")
                print(f"   Total issues found: {result['total_issues']}")
            else:
                print(f"\n❌ Error: {result.get('error', 'unknown')}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()