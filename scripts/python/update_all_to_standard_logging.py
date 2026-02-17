#!/usr/bin/env python3
"""
Update All Scripts to Use Standard Logging Module

Finds and updates all scripts that use non-standard logging patterns
to use the standard lumina_logger module instead.

CRITICAL: This enforces the 5/5 importance requirement to always use lumina_logger.
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger

logger = get_logger("UpdateToStandardLogging")

# Pattern to find non-standard logging usage
NON_STANDARD_PATTERNS = [
    (r'import logging\s*\n\s*logging\.basicConfig', 'Direct basicConfig'),
    (r'except ImportError:.*?logging\.basicConfig', 'Fallback basicConfig', re.DOTALL),
    (r'logging\.basicConfig\(', 'basicConfig call'),
]

STANDARD_PATTERN = """from lumina_logger import get_logger

logger = get_logger("{module_name}")"""

def find_files_with_non_standard_logging(scripts_dir: Path) -> List[Tuple[Path, str]]:
    """Find all Python files with non-standard logging"""
    files_to_update = []

    for py_file in scripts_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding='utf-8')

            # Skip this script itself
            if py_file.name == __file__.name:
                continue

            # Check for non-standard patterns
            for pattern, description in NON_STANDARD_PATTERNS:
                flags = pattern[2] if len(pattern) > 2 else 0
                if flags:
                    pattern_re = re.compile(pattern[0], flags)
                else:
                    pattern_re = re.compile(pattern[0])

                if pattern_re.search(content):
                    files_to_update.append((py_file, description))
                    logger.info(f"Found: {py_file.relative_to(scripts_dir.parent.parent)} - {description}")
                    break  # Only report once per file
        except Exception as e:
            logger.debug(f"Error reading {py_file}: {e}")

    return files_to_update

def update_file_to_standard_logging(file_path: Path, dry_run: bool = True) -> bool:
    """Update a file to use standard logging"""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content

        # Get module name from file path
        module_name = file_path.stem.replace('_', ' ').title().replace(' ', '')

        # Pattern 1: Replace fallback logging.basicConfig in try/except
        fallback_pattern = r'try:\s*\n\s*from lumina_logger import get_logger\s*\n\s*except ImportError:\s*\n\s*import logging\s*\n\s*logging\.basicConfig\([^)]*\)\s*\n\s*get_logger = lambda name: logging\.getLogger\(name\)'
        replacement = f'from lumina_logger import get_logger'
        content = re.sub(fallback_pattern, replacement, content, flags=re.MULTILINE)

        # Pattern 2: Replace direct logging.basicConfig
        content = re.sub(r'import logging\s*\n\s*logging\.basicConfig\([^)]*\)', 
                        f'from lumina_logger import get_logger', 
                        content, flags=re.MULTILINE)

        # Pattern 3: Ensure logger is created with get_logger
        if 'from lumina_logger import get_logger' in content:
            # Check if logger is already created
            if not re.search(r'logger\s*=\s*get_logger\(', content):
                # Find where to insert logger creation (after imports)
                import_end = max(
                    content.rfind('from lumina_logger import get_logger'),
                    content.rfind('import lumina_logger')
                )
                if import_end >= 0:
                    # Find end of import block
                    next_line = content.find('\n', import_end)
                    if next_line >= 0:
                        # Insert logger creation
                        logger_line = f'\nlogger = get_logger("{module_name}")'
                        content = content[:next_line+1] + logger_line + content[next_line+1:]

        if content != original_content:
            if not dry_run:
                file_path.write_text(content, encoding='utf-8')
                logger.info(f"✅ Updated: {file_path.name}")
            else:
                logger.info(f"📝 Would update: {file_path.name}")
            return True
        else:
            logger.debug(f"   No changes needed: {file_path.name}")
            return False

    except Exception as e:
        logger.error(f"❌ Error updating {file_path}: {e}")
        return False

def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Update scripts to use standard logging")
        parser.add_argument('--dry-run', action='store_true', default=True, 
                           help='Dry run (default: True, use --no-dry-run to actually update)')
        parser.add_argument('--no-dry-run', action='store_false', dest='dry_run',
                           help='Actually update files (not a dry run)')

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        scripts_dir = project_root / "scripts" / "python"

        logger.info("=" * 80)
        logger.info("🔍 FINDING FILES WITH NON-STANDARD LOGGING")
        logger.info("=" * 80)
        logger.info("")
        logger.info("CRITICAL REQUIREMENT: All scripts MUST use lumina_logger.get_logger()")
        logger.info("This is a 5/5 (+++++) importance requirement")
        logger.info("")

        files_to_update = find_files_with_non_standard_logging(scripts_dir)

        logger.info("")
        logger.info("=" * 80)
        logger.info(f"📊 FOUND {len(files_to_update)} FILES TO UPDATE")
        logger.info("=" * 80)
        logger.info("")

        if not files_to_update:
            logger.info("✅ All files already use standard logging!")
            logger.info("")
            return 0

        updated_count = 0
        for file_path, description in files_to_update:
            if update_file_to_standard_logging(file_path, dry_run=args.dry_run):
                updated_count += 1

        logger.info("")
        logger.info("=" * 80)
        if args.dry_run:
            logger.info(f"📋 DRY RUN COMPLETE: {updated_count} files would be updated")
            logger.info("   Run with --no-dry-run to actually update files")
        else:
            logger.info(f"✅ UPDATE COMPLETE: {updated_count} files updated")
        logger.info("=" * 80)
        logger.info("")

        return 0

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())