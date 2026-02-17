#!/usr/bin/env python3
"""
JARVIS: Open DSM Package Center

Opens DSM Package Center in NEO browser for manual MailPlus-Server restart.

Tags: #JARVIS #MAILPLUS #DSM #AUTOMATION @JARVIS @LUMINA
"""

import sys
import subprocess
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISOpenDSM")


def find_neo_browser() -> str:
    try:
        """Find NEO browser executable"""
        import os

        neo_paths = [
            r"C:\Program Files\NeoBrowser\Application\neo.exe",
            r"C:\Program Files (x86)\NeoBrowser\Application\neo.exe",
            os.path.expanduser(r"~\AppData\Local\NeoBrowser\Application\neo.exe"),
        ]

        for path in neo_paths:
            if os.path.exists(path):
                return path

        # Try to find via registry or common locations
        return None


    except Exception as e:
        logger.error(f"Error in find_neo_browser: {e}", exc_info=True)
        raise
def open_dsm_package_center():
    """Open DSM Package Center in browser"""
    nas_ip = "<NAS_PRIMARY_IP>"
    dsm_url = f"https://{nas_ip}:5001/#packages"

    logger.info("=" * 80)
    logger.info("🌐 JARVIS: OPENING DSM PACKAGE CENTER")
    logger.info("=" * 80)
    logger.info("")
    logger.info(f"📋 URL: {dsm_url}")
    logger.info("")
    logger.info("📝 MANUAL STEPS:")
    logger.info("   1. Find 'MailPlus-Server' in the package list")
    logger.info("   2. Click the 'Action' button (three dots) next to MailPlus-Server")
    logger.info("   3. Select 'Restart' or 'Stop' then 'Start'")
    logger.info("   4. Wait for MailPlus-Server to start successfully")
    logger.info("")
    logger.info("🔧 If MailPlus-Server is in abnormal state:")
    logger.info("   - Try 'Restart' first")
    logger.info("   - If that fails, try 'Stop' then 'Start'")
    logger.info("   - Check logs if it still fails")
    logger.info("")

    # Try to open in NEO first
    neo_path = find_neo_browser()
    if neo_path:
        logger.info(f"🚀 Opening in NEO browser: {neo_path}")
        try:
            subprocess.Popen([neo_path, dsm_url], shell=False)
            logger.info("✅ Opened in NEO browser")
            return True
        except Exception as e:
            logger.warning(f"⚠️  Failed to open in NEO: {e}")

    # Fallback to default browser
    logger.info("🚀 Opening in default browser...")
    try:
        import webbrowser
        webbrowser.open(dsm_url)
        logger.info("✅ Opened in default browser")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to open browser: {e}")
        return False


if __name__ == "__main__":
    success = open_dsm_package_center()
    sys.exit(0 if success else 1)
