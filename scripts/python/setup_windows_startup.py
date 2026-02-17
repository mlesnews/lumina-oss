#!/usr/bin/env python3
"""
Setup Windows Startup for Virtual Assistants

Creates a startup entry so VAs launch automatically when Windows starts.
Uses Replika-inspired renderer for beautiful experience.

Tags: #WINDOWS_STARTUP #AUTOSTART #VA_LAUNCHER @JARVIS @LUMINA
"""

import sys
import os
import shutil
from pathlib import Path
import logging
logger = logging.getLogger("setup_windows_startup")


script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

def get_startup_folder():
    try:
        """Get Windows Startup folder path"""
        startup_folder = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        startup_folder.mkdir(parents=True, exist_ok=True)
        return startup_folder

    except Exception as e:
        logger.error(f"Error in get_startup_folder: {e}", exc_info=True)
        raise
def create_startup_script():
    """Create startup script in project directory"""
    # Create batch file
    batch_content = f"""@echo off
REM LUMINA Virtual Assistants - Auto-start on Windows Login
REM Replika-inspired VA renderer

cd /d "{project_root}"
python scripts\\python\\replika_inspired_va_renderer.py
"""

    batch_file = script_dir / "start_vas_startup.bat"
    with open(batch_file, 'w', encoding='utf-8') as f:
        f.write(batch_content)

    return batch_file

def create_vbs_launcher(batch_file):
    """Create VBS launcher to run batch file silently"""
    vbs_content = f"""Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "{batch_file}" & Chr(34), 0
Set WshShell = Nothing
"""

    vbs_file = script_dir / "start_vas_startup.vbs"
    with open(vbs_file, 'w', encoding='utf-8') as f:
        f.write(vbs_content)

    return vbs_file

def setup_startup():
    """Setup Windows startup entry"""
    print("=" * 80)
    print("🚀 SETTING UP WINDOWS STARTUP FOR VIRTUAL ASSISTANTS")
    print("=" * 80)
    print()

    # Create startup script
    print("Creating startup script...")
    batch_file = create_startup_script()
    print(f"  ✅ Created: {batch_file}")

    # Create VBS launcher (runs silently)
    print("Creating silent launcher...")
    vbs_file = create_vbs_launcher(batch_file)
    print(f"  ✅ Created: {vbs_file}")

    # Get startup folder
    startup_folder = get_startup_folder()
    print(f"  📁 Startup folder: {startup_folder}")

    # Copy VBS to startup folder
    startup_shortcut = startup_folder / "LUMINA Virtual Assistants.vbs"
    try:
        shutil.copy2(vbs_file, startup_shortcut)
        print(f"  ✅ Added to startup: {startup_shortcut}")
        print()
        print("=" * 80)
        print("✅ SETUP COMPLETE!")
        print("=" * 80)
        print()
        print("Virtual Assistants will now start automatically when you log in to Windows.")
        print()
        print("To disable auto-start:")
        print(f"  1. Delete: {startup_shortcut}")
        print("  2. Or run this script again with --remove flag")
        print()
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        print()
        print("Manual setup:")
        print(f"  1. Copy this file to Startup folder:")
        print(f"     {vbs_file}")
        print(f"  2. Startup folder location:")
        print(f"     {startup_folder}")
        return False

def remove_startup():
    try:
        """Remove Windows startup entry"""
        startup_folder = get_startup_folder()
        startup_shortcut = startup_folder / "LUMINA Virtual Assistants.vbs"

        if startup_shortcut.exists():
            startup_shortcut.unlink()
            print(f"✅ Removed from startup: {startup_shortcut}")
            return True
        else:
            print("❌ No startup entry found")
            return False

    except Exception as e:
        logger.error(f"Error in remove_startup: {e}", exc_info=True)
        raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Setup Windows Startup for Virtual Assistants")
    parser.add_argument("--remove", action="store_true", help="Remove from startup")
    args = parser.parse_args()

    if args.remove:
        print("Removing from Windows startup...")
        remove_startup()
    else:
        setup_startup()

    return 0

if __name__ == "__main__":


    sys.exit(main())