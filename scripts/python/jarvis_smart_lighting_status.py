#!/usr/bin/env python3
"""
JARVIS Smart Lighting Status

Check current status of smart lighting system.

@JARVIS @STATUS @SMART_LIGHTING
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

from scripts.python.jarvis_smart_lighting_day_night_sync import SmartLightingDayNightSync

logger = get_logger("SmartLightingStatus")


def check_services():
    """Check service status"""
    services = ["ArmouryCrateService", "LightingService"]
    status = {}

    for service in services:
        try:
            result = subprocess.run(
                ["powershell", "-Command", f"Get-Service -Name '{service}' -ErrorAction SilentlyContinue | Select-Object Status, StartType"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if "Running" in result.stdout:
                status[service] = {"status": "Running", "start_type": "Unknown"}
            elif "Stopped" in result.stdout:
                if "Disabled" in result.stdout:
                    status[service] = {"status": "Stopped", "start_type": "Disabled"}
                elif "Manual" in result.stdout:
                    status[service] = {"status": "Stopped", "start_type": "Manual"}
                else:
                    status[service] = {"status": "Stopped", "start_type": "Unknown"}
            else:
                status[service] = {"status": "Not Found", "start_type": "N/A"}
        except Exception as e:
            status[service] = {"status": "Error", "error": str(e)}

    return status


def check_startup_script():
    try:
        """Check if startup script exists"""
        startup_folder = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        batch_file = startup_folder / "JARVIS_SmartLightingMonitor.bat"

        return {
            "exists": batch_file.exists(),
            "path": str(batch_file)
        }


    except Exception as e:
        logger.error(f"Error in check_startup_script: {e}", exc_info=True)
        raise
def main():
    """Main execution"""
    logger.info("=" * 70)
    logger.info("🌓 SMART LIGHTING STATUS")
    logger.info("=" * 70)
    logger.info("")

    # Check services
    logger.info("   🔍 Checking services...")
    services_status = check_services()
    for service, status in services_status.items():
        logger.info(f"      {service}: {status.get('status', 'Unknown')} ({status.get('start_type', 'N/A')})")

    # Check startup script
    logger.info("")
    logger.info("   🔍 Checking startup script...")
    startup_status = check_startup_script()
    if startup_status['exists']:
        logger.info(f"      ✅ Startup script exists")
    else:
        logger.info(f"      ❌ Startup script not found")

    # Check current period
    logger.info("")
    logger.info("   🔍 Checking current day/night period...")
    sync = SmartLightingDayNightSync(project_root)
    period = sync.get_current_period()
    is_night = sync.is_night_time()

    if is_night:
        screen_brightness = sync.config.night_screen_brightness
        external_brightness = sync.config.night_external_lighting
    else:
        screen_brightness = sync.config.day_screen_brightness
        external_brightness = sync.config.day_external_lighting

    logger.info(f"      Current period: {period.upper()}")
    logger.info(f"      Screen brightness: {screen_brightness}%")
    logger.info(f"      External lighting: {external_brightness}%")

    # Summary
    logger.info("")
    logger.info("=" * 70)
    logger.info("📊 STATUS SUMMARY")
    logger.info("=" * 70)
    logger.info(f"   🌓 Period: {period.upper()}")
    logger.info(f"   📊 Screen: {screen_brightness}%")
    logger.info(f"   💡 External Lighting: {external_brightness}%")
    logger.info(f"   💡 Display/Keyboard: DISABLED")
    logger.info(f"   🔧 Services: {'⚠️  Disabled (may require admin)' if any(s.get('start_type') == 'Disabled' for s in services_status.values()) else '✅ OK'}")
    logger.info(f"   🚀 Startup Script: {'✅ Active' if startup_status['exists'] else '❌ Missing'}")
    logger.info("")
    logger.info("   💡 Note: External lighting sync works even if services are disabled")
    logger.info("   💡 Screen dimming works independently of services")
    logger.info("")
    logger.info("=" * 70)
    logger.info("")


if __name__ == "__main__":


    main()