#!/usr/bin/env python3
"""
Setup LUMINA Autostart

Configures LUMINA to run automatically on Windows startup.
No reboots required - everything works from first boot.

Tags: #AUTOSTART #SETUP #LUMINA_CORE @JARVIS @LUMINA
"""

import sys
import winreg
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from lumina_adaptive_logger import get_adaptive_logger

logger = get_adaptive_logger("SetupAutostart")


def setup_autostart():
    """Set up LUMINA to run on Windows startup"""
    try:
        # Find Pythonw
        pythonw_exe = sys.executable.replace("python.exe", "pythonw.exe")
        if not Path(pythonw_exe).exists():
            pythonw_exe = sys.executable

        # Startup launcher script
        launcher_script = project_root / "scripts" / "python" / "lumina_startup_launcher.pyw"

        # Register in Windows Run key (runs on every startup)
        reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            reg_path,
            0,
            winreg.KEY_SET_VALUE
        )

        winreg.SetValueEx(
            key,
            "LUMINA_Startup",
            0,
            winreg.REG_SZ,
            f'"{pythonw_exe}" "{launcher_script}"'
        )

        winreg.CloseKey(key)

        logger.info("="*80)
        logger.info("✅ LUMINA AUTOSTART CONFIGURED")
        logger.info("="*80)
        logger.info("")
        logger.info("   🚀 LUMINA will now run automatically on Windows startup")
        logger.info("   📺 First boot: Welcome video + full initialization")
        logger.info("   ✅ Subsequent boots: Service verification only")
        logger.info("   🎯 No reboots required - ready to use immediately")
        logger.info("")

        return True

    except Exception as e:
        logger.error(f"   ❌ Failed to setup autostart: {e}")
        return False


def remove_autostart():
    """Remove LUMINA from Windows startup"""
    try:
        reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            reg_path,
            0,
            winreg.KEY_SET_VALUE
        )

        try:
            winreg.DeleteValue(key, "LUMINA_Startup")
            logger.info("   ✅ Autostart removed")
        except FileNotFoundError:
            logger.info("   ℹ️  Autostart not configured")

        winreg.CloseKey(key)
        return True

    except Exception as e:
        logger.error(f"   ❌ Failed to remove autostart: {e}")
        return False


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Setup LUMINA Autostart")
    parser.add_argument("--setup", action="store_true", help="Setup autostart")
    parser.add_argument("--remove", action="store_true", help="Remove autostart")

    args = parser.parse_args()

    if args.setup:
        success = setup_autostart()
        return 0 if success else 1
    elif args.remove:
        success = remove_autostart()
        return 0 if success else 1
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":


    sys.exit(main())