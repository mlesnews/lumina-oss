#!/usr/bin/env python3
"""
JARVIS Setup Smart Lighting Startup

Creates startup script for continuous day/night monitoring.
Ensures smart lighting runs automatically on login.

@JARVIS @STARTUP @SMART_LIGHTING
"""

import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SetupSmartLightingStartup")


def create_startup_script():
    try:
        """Create startup script for continuous monitoring"""
        logger.info("=" * 70)
        logger.info("🚀 SETTING UP SMART LIGHTING STARTUP")
        logger.info("=" * 70)
        logger.info("")

        # Get startup folder
        startup_folder = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        startup_folder.mkdir(parents=True, exist_ok=True)

        # Script paths
        monitor_script = project_root / "scripts" / "python" / "jarvis_continuous_day_night_monitor.py"
        python_exe = sys.executable

        if not monitor_script.exists():
            logger.error(f"   ❌ Monitor script not found: {monitor_script}")
            return False

        # Create batch file
        batch_content = f"""@echo off
    except Exception as e:
        self.logger.error(f"Error in create_startup_script: {e}", exc_info=True)
        raise
REM JARVIS Smart Lighting Day/Night Monitor - Startup Script
REM Runs continuous monitoring for day/night lighting sync

cd /d "{project_root}"
"{python_exe}" "{monitor_script}" --interval 60
"""

        batch_file = startup_folder / "JARVIS_SmartLightingMonitor.bat"
        batch_file.write_text(batch_content, encoding='utf-8')

        logger.info(f"   ✅ Startup script created: {batch_file}")
        logger.info("")
        logger.info("   💡 Smart lighting will start automatically on login")
        logger.info("   💡 Monitor runs every 60 seconds to adjust lighting")
        logger.info("")

        return True
    except Exception as e:
        logger.error(f"Error setting up smart lighting startup: {e}")
        return False


def main():
    """Main execution"""
    success = create_startup_script()

    print()
    print("=" * 70)
    print("🚀 SMART LIGHTING STARTUP SETUP")
    print("=" * 70)
    if success:
        print("   ✅ Startup script created successfully")
        print("   💡 Smart lighting will start automatically on login")
    else:
        print("   ❌ Failed to create startup script")
    print()
    print("=" * 70)


if __name__ == "__main__":


    main()