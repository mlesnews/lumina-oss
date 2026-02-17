#!/usr/bin/env python3
"""
Install VA Startup (User Level)

Installs VA orchestrator to start on user logon using Windows Startup folder.
No administrator privileges required.

Tags: #INSTALL #SERVICE #AUTO_START #VA @JARVIS @LUMINA
"""

import sys
import os
import shutil
from pathlib import Path

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

logger = get_logger("InstallVAStartupUser")


def create_startup_script():
    """Create startup batch script"""
    orchestrator_script = project_root / "scripts" / "python" / "ai_managed_va_orchestrator.py"
    python_exe = sys.executable

    # Create batch script
    batch_content = f'''@echo off
REM Lumina VA Orchestrator Startup Script
REM Auto-starts Virtual Assistants on user logon

cd /d "{project_root}"
"{python_exe}" "{orchestrator_script}" --start --daemon

REM Keep window hidden (optional - comment out to see window)
exit
'''

    # Save batch script
    batch_file = project_root / "scripts" / "python" / "start_va_orchestrator.bat"
    with open(batch_file, 'w') as f:
        f.write(batch_content)

    logger.info(f"✅ Startup batch script created: {batch_file}")
    return batch_file


def create_vbs_wrapper(batch_file):
    """Create VBS wrapper to run batch script hidden"""
    vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """{batch_file}""", 0, False
Set WshShell = Nothing
'''

    vbs_file = project_root / "scripts" / "python" / "start_va_orchestrator.vbs"
    with open(vbs_file, 'w') as f:
        f.write(vbs_content)

    logger.info(f"✅ VBS wrapper created: {vbs_file}")
    return vbs_file


def install_to_startup(vbs_file):
    """Install VBS script to Windows Startup folder"""
    startup_folder = Path(os.environ.get('APPDATA')) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    startup_folder.mkdir(parents=True, exist_ok=True)

    startup_shortcut = startup_folder / "Lumina VA Orchestrator.vbs"

    try:
        shutil.copy2(vbs_file, startup_shortcut)
        logger.info(f"✅ Installed to Startup folder: {startup_shortcut}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to install to Startup folder: {e}")
        return False


def check_existing_startup():
    try:
        """Check if already installed"""
        startup_folder = Path(os.environ.get('APPDATA')) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        startup_shortcut = startup_folder / "Lumina VA Orchestrator.vbs"
        return startup_shortcut.exists()


    except Exception as e:
        logger.error(f"Error in check_existing_startup: {e}", exc_info=True)
        raise
def main():
    """Main execution"""
    import platform

    print("=" * 80)
    print("🔧 INSTALL VA STARTUP (USER LEVEL)")
    print("=" * 80)
    print()

    if platform.system() != "Windows":
        print(f"⚠️  Unsupported system: {platform.system()}")
        print("   This script is for Windows only")
        return

    # Check if already installed
    if check_existing_startup():
        print("✅ VA Orchestrator is already installed in Startup folder")
        response = input("Do you want to reinstall? (y/n): ")
        if response.lower() != 'y':
            print("Skipping installation.")
            return
        # Remove existing
        startup_folder = Path(os.environ.get('APPDATA')) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        startup_shortcut = startup_folder / "Lumina VA Orchestrator.vbs"
        try:
            startup_shortcut.unlink()
            print("✅ Removed existing startup entry")
        except Exception as e:
            print(f"⚠️  Could not remove existing entry: {e}")

    print("Creating startup scripts...")
    batch_file = create_startup_script()
    vbs_file = create_vbs_wrapper(batch_file)

    print("Installing to Windows Startup folder...")
    if install_to_startup(vbs_file):
        print()
        print("✅ VA Startup installed successfully!")
        print()
        print("Installation Details:")
        print(f"  Batch Script: {batch_file}")
        print(f"  VBS Wrapper: {vbs_file}")
        print(f"  Startup Location: {Path(os.environ.get('APPDATA')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'}")
        print()
        print("Behavior:")
        print("  - VAs will start automatically when you log in")
        print("  - Runs in background (no visible window)")
        print("  - All VAs configured with auto_start=true will start")
        print()
        print("To test immediately:")
        print(f"  Double-click: {vbs_file}")
        print()
        print("To uninstall:")
        print("  Remove 'Lumina VA Orchestrator.vbs' from Startup folder")
    else:
        print("❌ Failed to install to Startup folder")
        print(f"   You can manually copy {vbs_file} to:")
        print(f"   {Path(os.environ.get('APPDATA')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'}")


if __name__ == "__main__":


    main()