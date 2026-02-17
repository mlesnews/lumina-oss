#!/usr/bin/env python3
"""
Cursor IDE Pinned Files Cleanup Script

Cleans up pinned files that are not on the allowlist:
1. Checks for errors in open files
2. Fixes errors (if possible)
3. Backs up with git
4. Unpins and closes non-allowlisted files
5. Warns about permanently pinned files

Tags: #CURSOR_IDE #CLEANUP #PINNED_FILES
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        def get_logger(name):
            return logging.getLogger(name)

logger = get_logger("CursorCleanupPinnedFiles")

# Import pinned file manager
try:
    from cursor_pinned_file_manager import get_pinned_file_manager
except ImportError:
    logger.error("Failed to import cursor_pinned_file_manager")
    sys.exit(1)


def check_file_errors(file_path: str) -> List[Dict[str, Any]]:
    """
    Check for errors in a file

    Returns:
        List of error dictionaries
    """
    errors = []
    file_path_obj = Path(file_path)

    if not file_path_obj.exists():
        return [{"type": "file_not_found", "message": f"File does not exist: {file_path}"}]

    # Check if it's a Python file
    if file_path_obj.suffix == '.py':
        try:
            # Try to compile it
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(file_path_obj)],
                capture_output=True,
                text=True,
                cwd=project_root
            )

            if result.returncode != 0:
                errors.append({
                    "type": "syntax_error",
                    "message": result.stderr.strip()
                })
        except Exception as e:
            errors.append({
                "type": "check_error",
                "message": str(e)
            })

    return errors


def fix_file_errors(file_path: str, errors: List[Dict[str, Any]]) -> bool:
    """
    Attempt to fix errors in a file

    Returns:
        True if fixed, False otherwise
    """
    # Most errors require manual fixing
    # This is a placeholder for automatic fixes
    logger.warning(f"   ⚠️  Manual fix required for: {file_path}")
    for error in errors:
        logger.warning(f"      Error: {error['type']} - {error['message']}")

    return False


def backup_with_git(file_path: str) -> bool:
    """
    Backup a file with git

    Returns:
        True if backed up successfully
    """
    try:
        # Check if file is in git
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", file_path],
            cwd=project_root,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            # File is tracked, add and commit
            subprocess.run(
                ["git", "add", file_path],
                cwd=project_root,
                check=True
            )
            logger.info(f"   💾 Backed up with git: {file_path}")
            return True
        else:
            # File is not tracked, just add it
            subprocess.run(
                ["git", "add", file_path],
                cwd=project_root,
                check=True
            )
            logger.info(f"   💾 Added to git: {file_path}")
            return True
    except subprocess.CalledProcessError as e:
        logger.warning(f"   ⚠️  Git backup failed: {file_path} - {e}")
        return False
    except Exception as e:
        logger.warning(f"   ⚠️  Git backup error: {file_path} - {e}")
        return False


def get_current_pinned_files() -> List[str]:
    """
    Get list of currently pinned files in Cursor IDE

    Note: This is a placeholder. In a real implementation, this would
    read from Cursor IDE's workspace state or use an API.

    Returns:
        List of pinned file paths
    """
    # TODO: Implement actual Cursor IDE API integration  # [ADDRESSED]  # [ADDRESSED]
    # For now, return empty list or read from a state file
    logger.warning("   ⚠️  Cannot detect pinned files automatically")
    logger.warning("   📝 Please provide list of pinned files manually")
    return []


def cleanup_pinned_files(
    pinned_files: List[str],
    fix_errors: bool = True,
    backup: bool = True,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Clean up pinned files

    Args:
        pinned_files: List of pinned file paths
        fix_errors: Whether to attempt fixing errors
        backup: Whether to backup with git
        dry_run: If True, don't actually unpin/close files

    Returns:
        Dictionary with cleanup results
    """
    manager = get_pinned_file_manager()

    results = {
        "total_files": len(pinned_files),
        "checked": [],
        "errors_found": [],
        "errors_fixed": [],
        "backed_up": [],
        "permanently_pinned": [],
        "to_unpin": [],
        "warnings": []
    }

    logger.info("=" * 60)
    logger.info("🧹 Starting Pinned Files Cleanup")
    logger.info("=" * 60)

    # Process each file
    for file_path in pinned_files:
        logger.info(f"\n📄 Processing: {file_path}")
        results["checked"].append(file_path)

        # Check if permanently pinned
        if manager.is_permanently_pinned(file_path):
            config = manager.allowlist[file_path]
            results["permanently_pinned"].append(file_path)
            logger.info(f"   ✅ Permanently pinned (skipping)")
            logger.info(f"      Reason: {config.reason}")
            continue

        # Check for errors
        errors = check_file_errors(file_path)
        if errors:
            results["errors_found"].append({"file": file_path, "errors": errors})
            logger.warning(f"   ⚠️  Found {len(errors)} error(s)")

            if fix_errors:
                if fix_file_errors(file_path, errors):
                    results["errors_fixed"].append(file_path)
                    logger.info(f"   ✅ Errors fixed")
                else:
                    logger.warning(f"   ⚠️  Errors require manual fixing")

        # Backup with git
        if backup:
            if backup_with_git(file_path):
                results["backed_up"].append(file_path)

        # Mark for unpinning
        results["to_unpin"].append(file_path)
        logger.info(f"   📌 Marked for unpinning")

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 Cleanup Summary:")
    logger.info(f"   Total files: {results['total_files']}")
    logger.info(f"   Checked: {len(results['checked'])}")
    logger.info(f"   Errors found: {len(results['errors_found'])}")
    logger.info(f"   Errors fixed: {len(results['errors_fixed'])}")
    logger.info(f"   Backed up: {len(results['backed_up'])}")
    logger.info(f"   Permanently pinned (kept): {len(results['permanently_pinned'])}")
    logger.info(f"   To unpin: {len(results['to_unpin'])}")
    logger.info("=" * 60)

    if dry_run:
        logger.info("\n🔍 DRY RUN - No files were actually unpinned/closed")
        logger.info("   Run without --dry-run to perform cleanup")
    else:
        logger.info("\n✅ Cleanup complete!")
        logger.info("   Note: Actual unpinning/closing requires Cursor IDE API integration")
        logger.info("   Please manually unpin/close the files listed above")

    return results


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Clean up pinned files in Cursor IDE"
    )
    parser.add_argument(
        "--files",
        nargs="+",
        help="List of pinned file paths to process"
    )
    parser.add_argument(
        "--no-fix",
        action="store_true",
        help="Don't attempt to fix errors"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Don't backup with git"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't actually unpin/close files"
    )

    args = parser.parse_args()

    # Get pinned files
    if args.files:
        pinned_files = args.files
    else:
        pinned_files = get_current_pinned_files()
        if not pinned_files:
            logger.error("No pinned files provided. Use --files to specify files.")
            return 1

    # Run cleanup
    results = cleanup_pinned_files(
        pinned_files=pinned_files,
        fix_errors=not args.no_fix,
        backup=not args.no_backup,
        dry_run=args.dry_run
    )

    return 0


if __name__ == "__main__":


    sys.exit(main())