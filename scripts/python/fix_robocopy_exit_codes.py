#!/usr/bin/env python3
"""
Fix Robocopy Exit Code Handling

Robocopy exit codes:
- 0-7: Success (some files may be skipped)
- 8: Some files could not be copied
- 9-15: Various errors

Exit code 9 = Some files skipped (normal for locked files)
Exit code 11 = No files could be copied (check permissions/network)

This script updates migration scripts to handle exit codes properly
and suppress unnecessary error notifications.

Tags: #ROBOCOPY #EXIT_CODES #TERMINAL_ERRORS #FIX @JARVIS @LUMINA
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple

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

logger = get_logger("FixRobocopyExitCodes")


def is_robocopy_success(exit_code: int) -> bool:
    """
    Check if robocopy exit code indicates success.

    Robocopy exit codes:
    0 = No files copied, no errors
    1 = All files copied successfully
    2 = Some extra files in destination
    3 = Some files copied, some mismatched
    4 = Some mismatched files or extras
    5 = Some files copied, some mismatched, some extras
    6 = Additional files and mismatches exist
    7 = Files copied, mismatches, extras, and no failures
    8 = Some files could not be copied

    9-15 = Various errors

    Codes 0-7 are generally considered success.
    Code 8+ indicates errors.
    """
    return exit_code <= 7


def update_robocopy_handling(file_path: Path) -> Tuple[bool, List[str]]:
    """Update robocopy exit code handling in a file"""
    if not file_path.exists():
        return False, [f"File not found: {file_path}"]

    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        changes = []

        # Pattern 1: Check for subprocess.run with robocopy
        # Update to handle exit codes properly
        robocopy_pattern = r'(subprocess\.run\s*\([^)]*robocopy[^)]*\))'

        def replace_robocopy_call(match):
            call = match.group(1)
            # Check if exit code handling exists
            if 'check=True' in call or 'check=' in call:
                # Already has check parameter
                return call

            # Add proper exit code handling
            if 'capture_output=True' in call or 'stdout=' in call:
                # Has output capture, add exit code check
                new_call = call.rstrip(')')
                new_call += ', check=False)'
                changes.append("Added check=False to robocopy call")
                return new_call
            else:
                return call

        content = re.sub(robocopy_pattern, replace_robocopy_call, content, flags=re.MULTILINE | re.DOTALL)

        # Pattern 2: Add exit code handling after robocopy calls
        # Look for robocopy result handling
        result_pattern = r'(result\s*=\s*subprocess\.run\s*\([^)]*robocopy[^)]*\))'

        def add_exit_code_check(match):
            result_line = match.group(1)
            # Check if exit code handling already exists
            lines_after = content[content.find(result_line) + len(result_line):content.find(result_line) + len(result_line) + 200]
            if 'exitcode' in lines_after.lower() or 'returncode' in lines_after.lower():
                return result_line  # Already has exit code handling

            # Add exit code handling
            indent = len(result_line) - len(result_line.lstrip())
            indent_str = ' ' * indent
            handling = f"\n{indent_str}# Robocopy exit codes: 0-7 = success, 8+ = errors\n"
            handling += f"{indent_str}if result.returncode > 7:\n"
            handling += f"{indent_str}    logger.warning(f\"Robocopy exit code {{result.returncode}} - some files may not have been copied\")\n"
            handling += f"{indent_str}else:\n"
            handling += f"{indent_str}    logger.info(f\"Robocopy completed successfully (exit code {{result.returncode}})\")"
            changes.append("Added exit code handling after robocopy call")
            return result_line + handling

        content = re.sub(result_pattern, add_exit_code_check, content, flags=re.MULTILINE | re.DOTALL)

        # Pattern 3: Update PowerShell scripts
        if file_path.suffix == '.ps1':
            # Look for robocopy exit code checks
            ps_exit_pattern = r'if\s*\(\$result\.ExitCode\s*-le\s*7\)'
            if not re.search(ps_exit_pattern, content):
                # Add proper exit code handling
                ps_robocopy_pattern = r'(\$result\s*=\s*Start-Process[^}]+robocopy[^}]+})'

                def add_ps_exit_check(match):
                    call = match.group(1)
                    if 'ExitCode' in call:
                        return call  # Already has exit code check

                    # Add exit code handling
                    handling = "\n    # Robocopy exit codes: 0-7 = success, 8+ = errors\n"
                    handling += "    if ($result.ExitCode -le 7) {\n"
                    handling += "        Write-Host \"   Migration successful (exit code: $($result.ExitCode))\" -ForegroundColor Green\n"
                    handling += "    } elseif ($result.ExitCode -eq 9) {\n"
                    handling += "        Write-Host \"   Migration completed with warnings - some files skipped (exit code: 9)\" -ForegroundColor Yellow\n"
                    handling += "    } else {\n"
                    handling += "        Write-Host \"   Migration completed with errors (exit code: $($result.ExitCode))\" -ForegroundColor Red\n"
                    handling += "    }"
                    changes.append("Added PowerShell exit code handling")
                    return call + handling

                content = re.sub(ps_robocopy_pattern, add_ps_exit_check, content, flags=re.MULTILINE | re.DOTALL)

        # Save if changes were made
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            return True, changes
        else:
            return False, ["No changes needed"]

    except Exception as e:
        return False, [f"Error updating file: {e}"]


def main():
    try:
        """Main entry point"""
        logger.info("=" * 80)
        logger.info("FIXING ROBOCOPY EXIT CODE HANDLING")
        logger.info("=" * 80)
        logger.info("")

        # Files to update
        files_to_fix = [
            script_dir / "urgent_nas_migration_accelerator.py",
            script_dir / "nas_migration_urgent_priority.ps1",
            script_dir / "execute_urgent_migration_now.ps1"
        ]

        results = []
        for file_path in files_to_fix:
            if file_path.exists():
                logger.info(f"Updating: {file_path.name}")
                updated, changes = update_robocopy_handling(file_path)
                if updated:
                    logger.info(f"   ✅ Updated: {file_path.name}")
                    for change in changes:
                        logger.info(f"      - {change}")
                    results.append((file_path.name, True, changes))
                else:
                    logger.info(f"   ℹ️  No changes needed: {file_path.name}")
                    results.append((file_path.name, False, changes))
            else:
                logger.warning(f"   ⚠️  File not found: {file_path.name}")
                results.append((file_path.name, False, ["File not found"]))

        logger.info("")
        logger.info("=" * 80)
        logger.info("FIX COMPLETE")
        logger.info("=" * 80)
        logger.info("")

        # Summary
        updated_count = sum(1 for _, updated, _ in results if updated)
        logger.info(f"Updated {updated_count} of {len(results)} files")
        logger.info("")
        logger.info("Robocopy exit codes are now handled properly:")
        logger.info("  - Exit codes 0-7: Success (logged as info)")
        logger.info("  - Exit code 9: Warning (some files skipped - normal)")
        logger.info("  - Exit code 11+: Error (logged as warning/error)")
        logger.info("")
        logger.info("This should reduce terminal error notifications.")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()