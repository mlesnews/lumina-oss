#!/usr/bin/env python3
"""
JARVIS Monitor IMAP and Complete Setup

Monitors IMAP port 993 and automatically completes Outlook setup when enabled.

Tags: #JARVIS #MAILSTATION #IMAP #MONITORING #AUTOMATION
@JARVIS @LUMINA @DOIT
"""

import sys
import time
import socket
from pathlib import Path
from typing import Dict, Any

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

logger = get_logger("JARVISMonitorIMAP")


def check_imap_port(nas_ip: str = "<NAS_PRIMARY_IP>", port: int = 993, timeout: int = 3) -> bool:
    """Check if IMAP port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((nas_ip, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def monitor_and_complete(max_wait: int = 300, check_interval: int = 5) -> Dict[str, Any]:
    """Monitor IMAP port and complete setup when enabled"""
    logger.info("=" * 80)
    logger.info("🤖 JARVIS MONITORING IMAP PORT 993")
    logger.info("=" * 80)
    logger.info("")
    logger.info(f"Monitoring IMAP port 993 on <NAS_PRIMARY_IP>")
    logger.info(f"Max wait time: {max_wait} seconds ({max_wait // 60} minutes)")
    logger.info(f"Check interval: {check_interval} seconds")
    logger.info("")
    logger.info("💡 Enable IMAP in DSM: MailStation → Settings → Mail Service")
    logger.info("")

    start_time = time.time()
    check_count = 0

    while (time.time() - start_time) < max_wait:
        check_count += 1
        is_open = check_imap_port()

        if is_open:
            logger.info("")
            logger.info("✅ IMAP PORT 993 IS NOW OPEN!")
            logger.info("")
            logger.info("🚀 JARVIS COMPLETING OUTLOOK SETUP...")
            logger.info("")

            # Import and run complete setup
            try:
                from jarvis_complete_outlook_email_setup import JARVISCompleteOutlookSetup

                jarvis = JARVISCompleteOutlookSetup()
                results = jarvis.execute_full_setup()

                logger.info("")
                logger.info("=" * 80)
                logger.info("📊 FINAL STATUS")
                logger.info("=" * 80)

                if results.get("account_verified"):
                    logger.info("✅ JARVIS AUTONOMOUS SETUP COMPLETE!")
                    logger.info("   Company email account is configured and verified")
                    return {
                        "success": True,
                        "imap_enabled": True,
                        "outlook_setup": True,
                        "account_verified": True,
                        "checks": check_count,
                        "wait_time": int(time.time() - start_time)
                    }
                else:
                    logger.warning("⚠️  Setup completed but account not verified")
                    logger.info("   Please check Outlook manually")
                    return {
                        "success": False,
                        "imap_enabled": True,
                        "outlook_setup": results.get("outlook_setup", False),
                        "account_verified": False,
                        "checks": check_count,
                        "wait_time": int(time.time() - start_time)
                    }
            except Exception as e:
                logger.error(f"❌ Setup completion failed: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "checks": check_count,
                    "wait_time": int(time.time() - start_time)
                }
        else:
            elapsed = int(time.time() - start_time)
            if check_count % 6 == 0:  # Log every 30 seconds
                logger.info(f"⏳ Still waiting... ({elapsed}s elapsed, {check_count} checks)")
            time.sleep(check_interval)

    logger.warning("")
    logger.warning("⏰ Timeout reached - IMAP port 993 not enabled")
    logger.warning("")
    logger.warning("Please enable IMAP manually and rerun:")
    logger.warning("   python scripts/python/jarvis_complete_outlook_email_setup.py")

    return {
        "success": False,
        "timeout": True,
        "checks": check_count,
        "wait_time": max_wait
    }


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Monitor IMAP and Complete Setup")
    parser.add_argument("--max-wait", type=int, default=300, help="Max wait time in seconds (default: 300)")
    parser.add_argument("--interval", type=int, default=5, help="Check interval in seconds (default: 5)")

    args = parser.parse_args()

    result = monitor_and_complete(max_wait=args.max_wait, check_interval=args.interval)

    return 0 if result.get("success") else 1


if __name__ == "__main__":


    sys.exit(main())