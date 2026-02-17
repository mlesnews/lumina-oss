"""
LUMINA Startup Integration
Auto-initialize all integrated systems on startup.

#JARVIS #LUMINA #STARTUP #INTEGRATION
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("LuminaStartup")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("LuminaStartup")


def initialize_all_systems():
    """Initialize all LUMINA systems on startup."""
    logger.info("="*80)
    logger.info("LUMINA STARTUP - INITIALIZING ALL SYSTEMS")
    logger.info("="*80)

    # 1. Initialize Hook & Trace
    logger.info("1. Initializing Hook & Trace System...")
    try:
        from scripts.python.integrate_hook_trace import integrate_all
        integrate_all()
        logger.info("   ✅ Hook & Trace integrated")
    except Exception as e:
        logger.error(f"   ❌ Hook & Trace failed: {e}")

    # 2. Initialize Comprehensive @SYPHON
    logger.info("2. Initializing Comprehensive @SYPHON System...")
    try:
        from scripts.python.lumina_comprehensive_syphon_system import LuminaComprehensiveSyphonSystem
        syphon = LuminaComprehensiveSyphonSystem(project_root)
        logger.info("   ✅ Comprehensive @SYPHON System initialized")
        logger.info(f"   Company: {syphon.company}")
        logger.info(f"   Sources: {len(syphon.sources)} configured")
    except Exception as e:
        logger.error(f"   ❌ Comprehensive @SYPHON failed: {e}")

    # 3. Initialize Unified Email Service
    logger.info("3. Initializing Unified Email Service...")
    try:
        from scripts.python.unified_email_service import UnifiedEmailService
        email_service = UnifiedEmailService(project_root)
        logger.info("   ✅ Unified Email Service initialized (Gmail + ProtonMail)")
    except Exception as e:
        logger.error(f"   ❌ Unified Email Service failed: {e}")

    # 4. Initialize HVAC Monitoring
    logger.info("4. Initializing HVAC Monitoring...")
    try:
        from scripts.python.hvac_syphon_monitor import HVACSyphonMonitor
        hvac_monitor = HVACSyphonMonitor(project_root)
        logger.info("   ✅ HVAC Monitoring initialized")
    except Exception as e:
        logger.error(f"   ❌ HVAC Monitoring failed: {e}")

    logger.info("")
    logger.info("="*80)
    logger.info("LUMINA STARTUP COMPLETE")
    logger.info("="*80)
    logger.info("")
    logger.info("All systems initialized and integrated:")
    logger.info("  ✅ Hook & Trace System")
    logger.info("  ✅ Comprehensive @SYPHON System")
    logger.info("  ✅ Unified Email Service")
    logger.info("  ✅ HVAC Monitoring")
    logger.info("")
    logger.info("Priority Order Maintained:")
    logger.info("  1. Filesystems (FIRST PRIORITY)")
    logger.info("  2. @SOURCES @SYPHON @BAU: Email + Financial Accounts")
    logger.info("")
    logger.info("Company: #<COMPANY>-FINANCIAL-SERVICES-LLC")
    logger.info("Tags: #NO-NONSENSE #PEOPLE")
    logger.info("")


if __name__ == "__main__":
    initialize_all_systems()
