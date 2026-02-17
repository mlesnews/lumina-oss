#!/usr/bin/env python3
"""
JARVIS Auto Accept All Changes
Automatically accepts all changes using MANUS to reduce manual intervention.

Tags: #JARVIS #MANUS #AUTOMATION #ACCEPT_ALL @manus @helpdesk
"""

import sys
import time
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

try:
    from manus_accept_all_button import MANUSAcceptAllButton
    ACCEPT_ALL_AVAILABLE = True
except ImportError:
    ACCEPT_ALL_AVAILABLE = False

logger = get_logger("JARVISAutoAcceptAll")


def auto_accept_all_changes():
    """Automatically accept all changes using MANUS"""

    logger.info("="*80)
    logger.info("🔄 AUTO ACCEPTING ALL CHANGES")
    logger.info("="*80)
    logger.info("")

    if not ACCEPT_ALL_AVAILABLE:
        logger.error("❌ MANUS Accept All not available")
        return False

    try:
        automator = MANUSAcceptAllButton()
        success = automator.accept_all_changes()

        if success:
            logger.info("")
            logger.info("✅ All changes accepted successfully")
            logger.info("   This will help reduce queue numbers by accepting fixes")
            return True
        else:
            logger.warning("⚠️  Failed to accept all changes")
            return False

    except Exception as e:
        logger.error(f"❌ Error accepting changes: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = auto_accept_all_changes()
    sys.exit(0 if success else 1)
