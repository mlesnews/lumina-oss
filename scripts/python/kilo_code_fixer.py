#!/usr/bin/env python3
"""
Kilo Code Fixer - Systematic Code Error Resolution

Applies systematic fixes to Python files for common error patterns.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple


class KiloCodeFixer:
    """Systematic code fixer for common Python patterns"""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def fix_file(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Fix a single file and return (success, fixes_applied)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return False, [f"Error reading file: {e}"]

        original_content = content
        fixes = []

        # Fix 1: Remove duplicate main() calls
        content, main_fixes = self._fix_duplicate_main(content)
        fixes.extend(main_fixes)

        # Fix 2: Remove trailing whitespace from blank lines
        content, whitespace_fixes = self._fix_trailing_whitespace(content)
        fixes.extend(whitespace_fixes)

        # Only write if changes were made
        if content != original_content:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True, fixes
            except Exception as e:
                return False, [f"Error writing file: {e}"]
        else:
            return True, []

    def _fix_duplicate_main(self, content: str) -> Tuple[str, List[str]]:
        """Remove duplicate main() calls"""
        fixes = []
        lines = content.split('\n')

        new_lines = []
        i = 0
        main_section_started = False
        main_calls = []
        
        while i < len(lines):
            line = lines[i]
            
            if 'if __name__ == "__main__":' in line:
                main_section_started = True
                new_lines.append(line)
                i += 1
                # Collect all lines until next top-level statement or EOF
                while i < len(lines):
                    next_line = lines[i]
                    stripped = next_line.strip()
                    
                    # Stop at next top-level statement (no indent) that's not empty/comment
                    if stripped and not next_line.startswith((' ', '\t')) and not stripped.startswith('#'):
                        break
                    
                    if 'main()' in next_line:
                        main_calls.append((i, next_line))
                    else:
                        new_lines.append(next_line)
                    i += 1
                
                # Only keep first main() call
                if len(main_calls) > 1:
                    new_lines.append(main_calls[0][1])
                    fixes.append(f"Line {main_calls[0][0]+1}: Removed {len(main_calls)-1} duplicate main() call(s)")
                elif main_calls:
                    new_lines.append(main_calls[0][1])
            else:
                new_lines.append(line)
                i += 1

        return '\n'.join(new_lines), fixes

    def _fix_trailing_whitespace(self, content: str) -> Tuple[str, List[str]]:
        """Remove trailing whitespace from blank lines"""
        fixes = []
        lines = content.split('\n')

        new_lines = []
        for i, line in enumerate(lines):
            if line.strip() == '' and line != '':
                new_lines.append('')
                fixes.append(f"Line {i+1}: Removed trailing whitespace")
            else:
                new_lines.append(line)

        return '\n'.join(new_lines), fixes

    def fix_directory(self, directory: Path, pattern: str = "*.py") -> dict:
        """Fix all Python files in a directory"""
        results = {}
        python_files = list(directory.rglob(pattern))

        for file_path in python_files:
            if file_path.name == 'kilo_code_fixer.py':
                continue  # Skip self
            success, fixes = self.fix_file(file_path)
            if fixes:
                results[str(file_path.relative_to(self.project_root))] = fixes

        return results


def main():
    try:
        """Main entry point"""
        import argparse
    
        parser = argparse.ArgumentParser(
            description="Kilo Code Fixer - Systematic Code Error Resolution"
        )
        parser.add_argument(
            "--file", type=str, help="Fix a specific file"
        )
        parser.add_argument(
            "--directory", type=str, default="scripts/python",
            help="Directory to fix (default: scripts/python)"
        )
        parser.add_argument(
            "--all", action="store_true",
            help="Fix all Python files in project"
        )

        args = parser.parse_args()

        # Determine project root
        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent

        fixer = KiloCodeFixer(project_root)

        if args.file:
            # Fix specific file
            file_path = project_root / args.file
            if file_path.exists():
                success, fixes = fixer.fix_file(file_path)
                if fixes:
                    print(f"✅ Fixed {file_path.name}:")
                    for fix in fixes:
                        print(f"   - {fix}")
                else:
                    print(f"ℹ️  No fixes needed for {file_path.name}")
            else:
                print(f"❌ File not found: {file_path}")
                sys.exit(1)
        elif args.all:
            # Fix all Python files
            results = fixer.fix_directory(project_root, "*.py")
            if results:
                print(f"✅ Fixed {len(results)} files:")
                for file_path, fixes in results.items():
                    print(f"\n📄 {file_path}:")
                    for fix in fixes:
                        print(f"   - {fix}")
            else:
                print("ℹ️  No fixes needed")
        else:
            # Fix directory
            directory = project_root / args.directory
            if directory.exists():
                results = fixer.fix_directory(directory, "*.py")
                if results:
                    print(f"✅ Fixed {len(results)} files:")
                    for file_path, fixes in results.items():
                        print(f"\n📄 {file_path}:")
                        for fix in fixes:
                            print(f"   - {fix}")
                else:
                    print("ℹ️  No fixes needed")
            else:
                print(f"❌ Directory not found: {directory}")
                sys.exit(1)


    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
if __name__ == "__main__":
    main()
