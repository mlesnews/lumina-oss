#!/usr/bin/env python3
"""
JARVIS: Wait for IMAP to be enabled and verify

Monitors IMAP port 993 and verifies when it's enabled.

Tags: #JARVIS #MAILPLUS #IMAP #MONITORING @JARVIS @LUMINA
"""

import sys
import time
import socket
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

logger = get_logger("JARVISWaitIMAP")


def check_port_open(host: str, port: int, timeout: int = 3) -> bool:
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def wait_for_imap(max_wait: int = 300) -> bool:
    try:
        """Wait for IMAP port 993 to open"""
        nas_ip = "<NAS_PRIMARY_IP>"
        imap_port = 993

        logger.info("=" * 80)
        logger.info("⏳ JARVIS: WAITING FOR IMAP PORT 993 TO OPEN")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"Monitoring: {nas_ip}:{imap_port}")
        logger.info(f"Max wait time: {max_wait} seconds")
        logger.info("")
        logger.info("💡 Enable IMAP in MailPlus Settings if you haven't already:")
        logger.info("   1. MailPlus → Settings → Mail Service")
        logger.info("   2. Enable 'IMAP service' checkbox")
        logger.info("   3. Port: 993, Encryption: SSL/TLS")
        logger.info("   4. Click Apply")
        logger.info("")

        start_time = time.time()
        check_interval = 5  # Check every 5 seconds

        while time.time() - start_time < max_wait:
            if check_port_open(nas_ip, imap_port):
                elapsed = int(time.time() - start_time)
                logger.info("")
                logger.info("=" * 80)
                logger.info(f"✅ SUCCESS: IMAP port 993 is now OPEN! (detected after {elapsed}s)")
                logger.info("=" * 80)
                logger.info("")
                logger.info("📧 Next: Complete Outlook email setup:")
                logger.info("   python scripts/python/jarvis_complete_outlook_email_setup.py")
                return True

            elapsed = int(time.time() - start_time)
            remaining = max_wait - elapsed
            logger.info(f"⏳ Still waiting... ({elapsed}s elapsed, {remaining}s remaining)")
            time.sleep(check_interval)

        logger.warning("")
        logger.warning("⚠️  Timeout: IMAP port 993 did not open within the wait time")
        logger.warning("   Please check MailPlus settings manually")
        return False


    except Exception as e:
        logger.error(f"Error in wait_for_imap: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Wait for IMAP port 993 to open")
    parser.add_argument("--max-wait", type=int, default=300, help="Maximum wait time in seconds (default: 300)")
    args = parser.parse_args()

    success = wait_for_imap(max_wait=args.max_wait)
    sys.exit(0 if success else 1)
