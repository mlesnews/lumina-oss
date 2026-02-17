#!/usr/bin/env python3
"""
JARVIS Open DSM MailPlus Configuration

Opens DSM web interface in default browser (NEO) to configure MailPlus IMAP.

Tags: #JARVIS #MAILPLUS #DSM #BROWSER #AUTOMATION
@JARVIS @LUMINA
"""

import sys
import os
import subprocess
import webbrowser
from pathlib import Path
from typing import Optional

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


def find_neo_browser() -> Optional[str]:
    try:
        """Find NEO browser executable"""
        neo_paths = [
            r"C:\Program Files\Neo\Application\neo.exe",
            r"C:\Program Files (x86)\Neo\Application\neo.exe",
            r"C:\Users\{}\AppData\Local\Neo\Application\neo.exe".format(
                os.getenv("USERNAME", "")
            )
        ]

        for path in neo_paths:
            if Path(path).exists():
                return path

        return None


    except Exception as e:
        logger.error(f"Error in find_neo_browser: {e}", exc_info=True)
        raise
def open_dsm_in_browser() -> bool:
    """Open DSM in default browser"""
    dsm_url = "https://<NAS_PRIMARY_IP>:5001"

    logger.info("=" * 80)
    logger.info("🌐 JARVIS OPENING DSM FOR MAILPLUS CONFIGURATION")
    logger.info("=" * 80)
    logger.info("")
    logger.info(f"URL: {dsm_url}")
    logger.info("")

    # Try NEO first
    neo_path = find_neo_browser()
    if neo_path:
        logger.info(f"✅ Found NEO browser: {neo_path}")
        try:
            subprocess.Popen([neo_path, dsm_url], shell=False)
            logger.info("✅ Opened DSM in NEO browser")
            logger.info("")
            logger.info("📋 Next Steps:")
            logger.info("   1. Login to DSM (credentials from Azure Vault)")
            logger.info("   2. Navigate to: MailPlus → Settings → Mail Service")
            logger.info("   3. Enable: 'IMAP service' checkbox")
            logger.info("   4. Set IMAP port: 993")
            logger.info("   5. Select encryption: SSL/TLS")
            logger.info("   6. Click: Apply/Save")
            logger.info("")
            logger.info("   After enabling IMAP, run:")
            logger.info("   python scripts/python/jarvis_complete_mailplus_imap_setup.py")
            return True
        except Exception as e:
            logger.warning(f"⚠️  Failed to open NEO: {e}")
            logger.info("   Falling back to default browser...")

    # Fallback to default browser
    try:
        webbrowser.open(dsm_url)
        logger.info("✅ Opened DSM in default browser")
        logger.info("")
        logger.info("📋 Next Steps:")
        logger.info("   1. Accept certificate warning (if prompted)")
        logger.info("   2. Login to DSM (credentials from Azure Vault)")
        logger.info("   3. Navigate to: MailPlus → Settings → Mail Service")
        logger.info("   4. Enable: 'IMAP service' checkbox")
        logger.info("   5. Set IMAP port: 993")
        logger.info("   6. Select encryption: SSL/TLS")
        logger.info("   7. Click: Apply/Save")
        logger.info("")
        logger.info("   After enabling IMAP, run:")
        logger.info("   python scripts/python/jarvis_complete_outlook_email_setup.py")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to open browser: {e}")
        return False


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Open DSM MailPlus Configuration")
    args = parser.parse_args()

    success = open_dsm_in_browser()
    return 0 if success else 1


if __name__ == "__main__":


    sys.exit(main())