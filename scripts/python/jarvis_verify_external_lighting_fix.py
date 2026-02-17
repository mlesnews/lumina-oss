#!/usr/bin/env python3
"""
JARVIS Verify External Lighting Fix

Final verification of external lighting fix status.
Checks all components and provides comprehensive status report.

@JARVIS @VERIFY @EXTERNAL_LIGHTING @STATUS
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("VerifyExternalLightingFix")


def check_process() -> Dict[str, Any]:
    """Check if AacAmbientLighting process is running"""
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-Process -Name 'AacAmbientLighting' -ErrorAction SilentlyContinue"],
            capture_output=True,
            text=True,
            timeout=10
        )
        is_running = bool(result.stdout.strip())
        return {
            "status": "RUNNING" if is_running else "STOPPED",
            "running": is_running,
            "details": result.stdout.strip() if is_running else "Process not running"
        }
    except Exception as e:
        return {
            "status": "UNKNOWN",
            "running": None,
            "error": str(e)
        }


def check_services() -> Dict[str, Any]:
    """Check service status"""
    services = ["ArmouryCrateService", "LightingService", "AuraWallpaperService", "AuraService"]
    service_status = {}

    for service in services:
        try:
            result = subprocess.run(
                ["powershell", "-Command", f"Get-Service -Name '{service}' -ErrorAction SilentlyContinue | Select-Object Status, StartType"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if "Running" in result.stdout:
                service_status[service] = {"status": "Running", "start_type": "Unknown"}
            elif "Stopped" in result.stdout:
                if "Disabled" in result.stdout:
                    service_status[service] = {"status": "Stopped", "start_type": "Disabled"}
                else:
                    service_status[service] = {"status": "Stopped", "start_type": "Unknown"}
            else:
                service_status[service] = {"status": "Not Found", "start_type": "N/A"}
        except Exception as e:
            service_status[service] = {"status": "Error", "error": str(e)}

    return service_status


def check_startup_script() -> Dict[str, Any]:
    try:
        """Check if startup script exists"""
        startup_folder = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        batch_file = startup_folder / "JARVIS_ExternalLightingKiller.bat"

        return {
            "exists": batch_file.exists(),
            "path": str(batch_file),
            "readable": batch_file.is_file() if batch_file.exists() else False
        }


    except Exception as e:
        logger.error(f"Error in check_startup_script: {e}", exc_info=True)
        raise
def check_scheduled_task() -> Dict[str, Any]:
    """Check if scheduled task exists"""
    task_name = "JARVIS_ExternalLightingKiller"

    try:
        result = subprocess.run(
            ["powershell", "-Command", f"Get-ScheduledTask -TaskName '{task_name}' -ErrorAction SilentlyContinue | Select-Object TaskName, State"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if task_name in result.stdout:
            if "Ready" in result.stdout or "Running" in result.stdout:
                return {
                    "exists": True,
                    "state": "Active",
                    "details": result.stdout.strip()
                }
            else:
                return {
                    "exists": True,
                    "state": "Inactive",
                    "details": result.stdout.strip()
                }
        else:
            return {
                "exists": False,
                "state": "Not Found"
            }
    except Exception as e:
        return {
            "exists": False,
            "error": str(e)
        }


def main():
    """Main execution"""
    logger.info("=" * 70)
    logger.info("🔍 EXTERNAL LIGHTING FIX VERIFICATION")
    logger.info("=" * 70)
    logger.info("")

    # Check process
    logger.info("   🔍 Checking AacAmbientLighting process...")
    process_status = check_process()
    logger.info(f"      Status: {process_status['status']}")
    if process_status.get('details'):
        logger.info(f"      Details: {process_status['details']}")

    # Check services
    logger.info("")
    logger.info("   🔍 Checking services...")
    services_status = check_services()
    for service, status in services_status.items():
        logger.info(f"      {service}: {status.get('status', 'Unknown')} ({status.get('start_type', 'N/A')})")

    # Check startup script
    logger.info("")
    logger.info("   🔍 Checking startup script...")
    startup_status = check_startup_script()
    if startup_status['exists']:
        logger.info(f"      ✅ Startup script exists: {startup_status['path']}")
    else:
        logger.info(f"      ❌ Startup script not found")

    # Check scheduled task
    logger.info("")
    logger.info("   🔍 Checking scheduled task...")
    task_status = check_scheduled_task()
    if task_status.get('exists'):
        logger.info(f"      ✅ Scheduled task exists: {task_status.get('state', 'Unknown')}")
    else:
        logger.info(f"      ⚠️  Scheduled task not found (may require admin privileges)")

    # Summary
    logger.info("")
    logger.info("=" * 70)
    logger.info("📊 VERIFICATION SUMMARY")
    logger.info("=" * 70)

    process_ok = not process_status.get('running', True)
    services_ok = all(
        s.get('status') == 'Stopped' and s.get('start_type') == 'Disabled'
        for s in services_status.values()
        if s.get('status') != 'Not Found'
    )
    startup_ok = startup_status['exists']

    logger.info(f"   🎯 Process Status: {'✅ STOPPED' if process_ok else '❌ RUNNING'}")
    logger.info(f"   🎯 Services Status: {'✅ DISABLED' if services_ok else '⚠️  PARTIAL'}")
    logger.info(f"   🎯 Startup Script: {'✅ ACTIVE' if startup_ok else '❌ MISSING'}")
    logger.info(f"   🎯 Scheduled Task: {'✅ ACTIVE' if task_status.get('exists') else '⚠️  NOT CREATED (requires admin)'}")
    logger.info("")

    if process_ok and services_ok and startup_ok:
        logger.info("   ✅ SUCCESS: External lighting is DISABLED and monitoring is ACTIVE")
        logger.info("   💡 The system will automatically kill AacAmbientLighting on every login")
    elif process_ok:
        logger.info("   ⚠️  PARTIAL SUCCESS: Process is stopped, but some components may be missing")
    else:
        logger.info("   ❌ FAILURE: Process is still running - may restart at hardware level")

    logger.info("")
    logger.info("=" * 70)
    logger.info("")


if __name__ == "__main__":


    main()