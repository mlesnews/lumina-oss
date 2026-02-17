#!/usr/bin/env python3
"""
Start Full VA System

Starts the complete virtual assistant system with:
- Full voice mode
- AI VFX
- Company-wide collaboration
- All VAs coordinated

Tags: #STARTUP #FULL_SYSTEM #VOICE #VFX #COLLABORATION @JARVIS @LUMINA
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger, setup_logging
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    setup_logging = lambda: None

logger = get_logger("StartFullVASystem")

# Import systems
try:
    from ai_managed_va_orchestrator import AIManagedVAOrchestrator
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False
    AIManagedVAOrchestrator = None

try:
    from va_company_collaboration_system import VACompanyCollaborationSystem
    COLLABORATION_AVAILABLE = True
except ImportError:
    COLLABORATION_AVAILABLE = False
    VACompanyCollaborationSystem = None


def start_full_system():
    """Start the full VA system"""
    logger.info("=" * 80)
    logger.info("🚀 STARTING FULL VA SYSTEM")
    logger.info("=" * 80)

    # Start orchestrator
    if ORCHESTRATOR_AVAILABLE:
        logger.info("📋 Starting VA Orchestrator...")
        orchestrator = AIManagedVAOrchestrator(project_root)

        # Start orchestrator in background
        import threading
        orchestrator_thread = threading.Thread(
            target=orchestrator.start,
            daemon=True
        )
        orchestrator_thread.start()
        logger.info("✅ Orchestrator started")

        # Wait for VAs to start
        time.sleep(5)

        # Get VA instances
        va_instances = {}
        for va_name, monitor in orchestrator.monitors.items():
            if monitor.process and monitor.process.is_running():
                # Try to get VA instance (this would need to be stored)
                logger.info(f"✅ {va_name} is running")
    else:
        logger.warning("⚠️  Orchestrator not available")
        va_instances = {}

    # Start collaboration system
    if COLLABORATION_AVAILABLE:
        logger.info("🤝 Starting Company Collaboration System...")
        collaboration = VACompanyCollaborationSystem(project_root)

        # Register VAs (if we have instances)
        for va_name in ["ironman", "kenny", "anakin", "jarvis"]:
            if va_name in va_instances:
                collaboration.register_va(va_name, va_instances[va_name])

        # Start full collaboration mode
        collaboration.start_full_collaboration_mode()
        logger.info("✅ Full collaboration mode activated")

        # Keep running
        logger.info("=" * 80)
        logger.info("✅ FULL VA SYSTEM RUNNING")
        logger.info("=" * 80)
        logger.info("Features:")
        logger.info("  ✅ Full voice mode (all VAs)")
        logger.info("  ✅ AI VFX system (visual effects)")
        logger.info("  ✅ Company-wide collaboration")
        logger.info("  ✅ Real-time coordination")
        logger.info("=" * 80)
        logger.info("Press Ctrl+C to stop")

        try:
            while True:
                time.sleep(1)
                # Update status
                status = collaboration.get_company_status()
                logger.debug(f"Status: {status.get('all_vas_online')} VAs online")
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            collaboration.stop_full_collaboration_mode()
            logger.info("✅ Full VA system stopped")
    else:
        logger.warning("⚠️  Collaboration system not available")
        logger.info("Press Ctrl+C to stop")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("✅ Stopped")


def main():
    """Main entry point"""
    start_full_system()


if __name__ == "__main__":


    main()