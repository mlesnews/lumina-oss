#!/usr/bin/env python3
"""
Configure Surveillance Station after installation
JARVIS automated configuration
#JARVIS #MANUS #NAS #SYNOLOGY #SURVEILLANCE_STATION
"""

import sys
from pathlib import Path
from typing import Dict, Any

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from install_surveillance_station import SurveillanceStationInstaller
    INSTALLER_AVAILABLE = True
except ImportError:
    INSTALLER_AVAILABLE = False

logger = get_logger("ConfigureSurveillanceStation")


def main():
    """Configure Surveillance Station"""
    if not INSTALLER_AVAILABLE:
        logger.error("❌ Installer module not available")
        return 1

    logger.info("🔧 Configuring Surveillance Station...")

    try:
        with SurveillanceStationInstaller() as installer:
            # Check if installed
            status = installer.check_installed()
            if not status.get("installed"):
                logger.error("❌ Surveillance Station is not installed")
                return 1

            logger.info("✅ Surveillance Station is installed")

            # Configure storage
            logger.info("📁 Configuring storage...")
            storage_result = installer.configure_storage()

            if storage_result.get("success"):
                logger.info("✅ Storage configuration complete")
            else:
                logger.warning(f"⚠️  Storage configuration: {storage_result.get('error')}")

            # Summary
            logger.info("🎉 Configuration complete!")
            logger.info(f"📺 Access Surveillance Station at: https://<NAS_PRIMARY_IP>:9901")

            return 0

    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":


    sys.exit(main())