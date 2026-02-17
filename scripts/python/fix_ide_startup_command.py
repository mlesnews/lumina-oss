#!/usr/bin/env python3
"""
Fix IDE Startup Command - Exit Code 64

Fixes malformed PowerShell command in IDE settings that causes exit code 64.
Removes the `&` separator and duplicate pwsh.exe invocation.
"""

import json
import sys
import copy
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)


def fix_args_array(args: List[str]) -> List[str]:
    """
    Fix malformed args array by removing & and duplicate pwsh.exe

    Args:
        args: Original args array

    Returns:
        Fixed args array
    """
    if not args:
        return args

    # Remove & separator
    fixed = [arg for arg in args if arg != "&" and arg.strip() != "&"]

    # Check if we have duplicate pwsh.exe or malformed command
    # Look for pattern: ["-NoProfile", "&", "pwsh.exe", ...]
    if len(fixed) > 1 and "pwsh.exe" in str(fixed):
        # Find the script path
        script_path = None
        for i, arg in enumerate(fixed):
            if "direct_fix_mcp.ps1" in arg:
                script_path = arg.strip('"')
                break

        if script_path:
            # Return clean args
            return [
                "-ExecutionPolicy",
                "Bypass",
                "-NoProfile",
                "-File",
                script_path
            ]

    return fixed


def fix_settings_json(settings_path: Path) -> bool:
    """
    Fix settings.json with malformed command

    Args:
        settings_path: Path to settings.json

    Returns:
        True if fixed, False if no issues found
    """
    logger = get_logger("FixIDEStartup")

    if not settings_path.exists():
        logger.debug(f"Settings file not found: {settings_path}")
        return False

    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {settings_path}: {e}")
        return False

    # Create deep copy of original settings for backup BEFORE modifications
    original_settings = copy.deepcopy(settings)
    fixed = False

    # Fix terminal profiles
    if "terminal.integrated.profiles.windows" in settings:
        profiles = settings["terminal.integrated.profiles.windows"]
        if isinstance(profiles, dict):
            for profile_name, profile_config in profiles.items():
                if isinstance(profile_config, dict) and "args" in profile_config:
                    original_args = profile_config["args"]
                    if isinstance(original_args, list):
                        fixed_args = fix_args_array(original_args)
                        if fixed_args != original_args:
                            profile_config["args"] = fixed_args
                            fixed = True
                            logger.info(f"Fixed args in profile '{profile_name}'")

    # Fix terminal automation profile
    if "terminal.integrated.automationProfile.windows" in settings:
        auto_profile = settings["terminal.integrated.automationProfile.windows"]
        if isinstance(auto_profile, dict) and "args" in auto_profile:
            original_args = auto_profile["args"]
            if isinstance(original_args, list):
                fixed_args = fix_args_array(original_args)
                if fixed_args != original_args:
                    auto_profile["args"] = fixed_args
                    fixed = True
                    logger.info("Fixed args in automation profile")

    # Fix shell args
    if "terminal.integrated.shellArgs.windows" in settings:
        shell_args = settings["terminal.integrated.shellArgs.windows"]
        if isinstance(shell_args, list):
            fixed_args = fix_args_array(shell_args)
            if fixed_args != shell_args:
                settings["terminal.integrated.shellArgs.windows"] = fixed_args
                fixed = True
                logger.info("Fixed shell args")

    if fixed:
        # Backup original (use original_settings, not modified settings)
        backup_path = settings_path.with_suffix('.json.backup')
        if not backup_path.exists():
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(original_settings, f, indent=2, ensure_ascii=False)
            logger.info(f"Created backup: {backup_path}")

        # Write fixed settings
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Fixed {settings_path}")
        return True
    else:
        logger.debug(f"ℹ️  No issues found in {settings_path}")
        return False


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Fix malformed IDE startup command (exit code 64)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fix all IDE settings automatically
  python fix_ide_startup_command.py

  # Fix specific settings file
  python fix_ide_startup_command.py --settings "C:\\Users\\mlesn\\AppData\\Roaming\\Cursor\\User\\settings.json"
        """
    )
    parser.add_argument(
        "--settings",
        type=str,
        help="Path to specific settings.json file (default: auto-detect)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fixed without making changes"
    )

    args = parser.parse_args()

    logger = get_logger("FixIDEStartup")

    if args.dry_run:
        logger.info("DRY RUN MODE - No changes will be made")

    # Determine settings files to check
    settings_files = []

    if args.settings:
        settings_files.append(Path(args.settings))
    else:
        # Auto-detect common locations
        appdata = Path.home() / "AppData" / "Roaming"
        settings_files = [
            appdata / "Code" / "User" / "settings.json",
            appdata / "Cursor" / "User" / "settings.json",
        ]

    fixed_any = False

    for settings_path in settings_files:
        if settings_path.exists():
            logger.info(f"Checking: {settings_path}")
            if args.dry_run:
                logger.info(f"  [DRY RUN] Would check and fix if needed")
            else:
                if fix_settings_json(settings_path):
                    fixed_any = True
        else:
            logger.debug(f"Settings file not found: {settings_path}")

    if not fixed_any and not args.dry_run:
        logger.warning("⚠️  No settings.json files found or no issues detected")
        logger.info("   Please check your IDE settings manually")
        logger.info("   Look for terminal.integrated.profiles.windows or terminal.integrated.automationProfile.windows")
        return 1

    if fixed_any:
        logger.info("\n✅ Fixed IDE startup command!")
        logger.info("   Please restart your IDE for changes to take effect")
        return 0

    return 0


if __name__ == "__main__":



    sys.exit(main())