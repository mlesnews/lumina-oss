#!/usr/bin/env python3
"""
JARVIS Create Persistent Monitoring

Creates a simple, reliable persistent monitoring system for external lighting.
Uses Windows Task Scheduler with a simpler approach.

@JARVIS @PERSISTENT @MONITORING @AUTOMATED
"""

import sys
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CreatePersistentMonitoring")


def create_scheduled_task():
    try:
        """Create Windows scheduled task for persistent monitoring"""
        logger.info("=" * 70)
        logger.info("🔧 CREATING PERSISTENT MONITORING")
        logger.info("=" * 70)
        logger.info("")

        script_path = project_root / "scripts" / "python" / "jarvis_persistent_lighting_killer.py"
        python_exe = sys.executable

        if not script_path.exists():
            logger.error(f"   ❌ Script not found: {script_path}")
            return False

        task_name = "JARVIS_ExternalLightingKiller"

        # Remove existing task
        logger.info(f"   Removing existing task '{task_name}' if it exists...")
        subprocess.run(
            ["powershell", "-Command", f"Unregister-ScheduledTask -TaskName '{task_name}' -Confirm:$false -ErrorAction SilentlyContinue"],
            capture_output=True
        )

        # Create task using schtasks command (more reliable)
        logger.info(f"   Creating scheduled task '{task_name}'...")

        # Create task that runs every 5 minutes
        cmd = f'''schtasks /Create /TN "{task_name}" /TR "\\"{python_exe}\\" \\"{script_path}\\" --once" /SC MINUTE /MO 5 /F'''

        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            logger.info(f"   ✅ Scheduled task '{task_name}' created successfully")

            # Verify task exists
            verify = subprocess.run(
                ["powershell", "-Command", f"Get-ScheduledTask -TaskName '{task_name}' -ErrorAction SilentlyContinue"],
                capture_output=True,
                text=True
            )

            if verify.returncode == 0:
                logger.info(f"   ✅ Task verified and active")
                return True
            else:
                logger.warning(f"   ⚠️  Task created but verification failed")
                return False
        else:
            logger.error(f"   ❌ Failed to create task: {result.stderr}")
            return False


    except Exception as e:
        logger.error(f"Error in create_scheduled_task: {e}", exc_info=True)
        raise
def verify_startup_script():
    try:
        """Verify startup script exists"""
        logger.info("")
        logger.info("   Verifying startup script...")

        startup_folder = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        batch_file = startup_folder / "JARVIS_ExternalLightingKiller.bat"

        if batch_file.exists():
            logger.info(f"   ✅ Startup script exists: {batch_file}")
            return True
        else:
            logger.warning(f"   ⚠️  Startup script not found: {batch_file}")
            return False


    except Exception as e:
        logger.error(f"Error in verify_startup_script: {e}", exc_info=True)
        raise
def main():
    """Main execution"""
    logger.info("")

    # Create scheduled task
    task_created = create_scheduled_task()

    # Verify startup script
    script_exists = verify_startup_script()

    logger.info("")
    logger.info("=" * 70)
    logger.info("📊 PERSISTENT MONITORING SUMMARY")
    logger.info("=" * 70)
    logger.info(f"   🔧 Scheduled Task: {'✅ Created' if task_created else '❌ Failed'}")
    logger.info(f"   🔧 Startup Script: {'✅ Exists' if script_exists else '❌ Missing'}")
    logger.info("")

    if task_created or script_exists:
        logger.info("   ✅ Persistent monitoring is ACTIVE")
        logger.info("   💡 The system will automatically kill AacAmbientLighting")
        logger.info("      - On every login (startup script)")
        logger.info("      - Every 5 minutes (scheduled task)")
    else:
        logger.warning("   ⚠️  Persistent monitoring setup incomplete")

    logger.info("")
    logger.info("=" * 70)
    logger.info("")


if __name__ == "__main__":


    main()