#!/usr/bin/env python3
"""
JARVIS Smart Lighting with Admin Elevation

Uses admin elevation module to properly manage services and settings.

@JARVIS @SMART_LIGHTING @ADMIN @ELEVATION
"""

import sys
from pathlib import Path
from typing import Dict, Any

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

from scripts.python.jarvis_admin_elevation import AdminElevation, ensure_admin_or_exit
from scripts.python.jarvis_smart_lighting_day_night_sync import SmartLightingDayNightSync

logger = get_logger("SmartLightingWithAdmin")


class SmartLightingWithAdmin(SmartLightingDayNightSync):
    """
    Smart Lighting with Admin Elevation

    Extends SmartLightingDayNightSync with proper admin elevation support.
    """

    def re_enable_services(self) -> Dict[str, Any]:
        """Re-enable services with admin elevation"""
        logger.info("")
        logger.info("   🔧 Re-enabling services (with admin elevation)...")

        # Check if we have admin
        if not AdminElevation.is_admin():
            logger.warning("   ⚠️  Admin privileges required to modify services")
            logger.info("   💡 Requesting admin elevation...")
            ensure_admin_or_exit(
                script_path=Path(__file__).resolve(),
                message="Admin privileges required for service management"
            )
            return {"success": False, "error": "Admin elevation required"}

        services = ["ArmouryCrateService", "LightingService"]
        enabled_services = []

        for service in services:
            try:
                # Set to Manual startup
                result = AdminElevation.set_service_startup_type(service, "Manual")
                if result["success"]:
                    # Start service
                    start_result = AdminElevation.start_service(service)
                    if start_result["success"]:
                        enabled_services.append(service)
                        logger.info(f"      ✅ {service} re-enabled")
                    else:
                        logger.warning(f"      ⚠️  {service}: Startup type set but failed to start")
                else:
                    logger.warning(f"      ⚠️  {service}: Failed to set startup type")
            except Exception as e:
                logger.warning(f"      ⚠️  {service}: {str(e)}")

        return {
            "success": len(enabled_services) > 0,
            "enabled_services": enabled_services,
            "admin": AdminElevation.is_admin()
        }


def main():
    try:
        """Main execution"""
        logger.info("=" * 70)
        logger.info("🌓 SMART LIGHTING WITH ADMIN ELEVATION")
        logger.info("=" * 70)
        logger.info("")

        # Check admin status
        admin_status = AdminElevation.is_admin()
        logger.info(f"   Admin Status: {'✅ Running as admin' if admin_status else '❌ Not running as admin'}")

        if not admin_status:
            logger.info("")
            logger.info("   ⚠️  Admin privileges required for full functionality")
            logger.info("   🔄 Requesting admin elevation...")
            logger.info("")
            ensure_admin_or_exit(
                script_path=Path(__file__).resolve(),
                message="Admin privileges required for smart lighting setup"
            )
            return

        # Run setup with admin privileges
        project_root = Path(__file__).parent.parent.parent
        sync = SmartLightingWithAdmin(project_root)
        result = sync.setup_smart_lighting()

        print()
        print("=" * 70)
        print("🌓 SMART LIGHTING WITH ADMIN ELEVATION")
        print("=" * 70)
        print(f"   ✅ Admin Status: Running as admin")
        print(f"   🌓 Current Period: {result['settings']['period'].upper()}")
        print(f"   📊 Screen Brightness: {result['settings']['screen_brightness']}%")
        print(f"   📊 External Lighting: {result['settings']['external_lighting']}%")
        print()
        print("=" * 70)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()