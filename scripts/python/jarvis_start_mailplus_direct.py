#!/usr/bin/env python3
"""
JARVIS: Direct MailPlus Start

Directly starts MailPlus Server via SSH using full path to synopkg.

Tags: #JARVIS #MAILPLUS #AUTOMATION @JARVIS @LUMINA
"""

import sys
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

logger = get_logger("JARVISStartMailPlus")


def start_mailplus():
    """Start MailPlus Server directly"""
    try:
        from nas_azure_vault_integration import NASAzureVaultIntegration
        import paramiko

        nas_integration = NASAzureVaultIntegration()
        credentials = nas_integration.get_nas_credentials()

        if not credentials:
            logger.error("❌ Could not get NAS credentials")
            return False

        nas_ip = "<NAS_PRIMARY_IP>"
        synopkg_path = "/usr/syno/synopkg"

        logger.info("=" * 80)
        logger.info("🚀 JARVIS: STARTING MAILPLUS SERVER")
        logger.info("=" * 80)
        logger.info("")

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        logger.info(f"🔌 Connecting to NAS: {nas_ip}")
        ssh.connect(
            nas_ip,
            username=credentials["username"],
            password=credentials["password"],
            timeout=10
        )

        # Check current status
        logger.info("📋 Checking current status...")
        stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} status MailPlus")
        status_before = stdout.read().decode().strip()
        logger.info(f"   Status before: {status_before}")

        # Check Mail Server status
        stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} status MailServer")
        mail_server_status = stdout.read().decode().strip()
        logger.info(f"   Mail Server status: {mail_server_status}")

        # Stop Mail Server if running
        if "is running" in mail_server_status.lower():
            logger.info("🛑 Stopping Mail Server first...")
            stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} stop MailServer")
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            if output:
                logger.info(f"   Output: {output}")
            if error:
                logger.warning(f"   Error: {error}")
            time.sleep(3)

        # Start MailPlus
        logger.info("🚀 Starting MailPlus...")
        stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} start MailPlus")
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        if output:
            logger.info(f"   Output: {output}")
        if error:
            logger.warning(f"   Error: {error}")

        # Wait for service to start
        logger.info("   Waiting for MailPlus to start...")
        time.sleep(5)

        # Check status after
        logger.info("📋 Checking status after start...")
        stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} status MailPlus")
        status_after = stdout.read().decode().strip()
        logger.info(f"   Status after: {status_after}")

        ssh.close()

        logger.info("")
        logger.info("=" * 80)

        if "is running" in status_after.lower():
            logger.info("✅ SUCCESS! MailPlus Server is now running!")
            logger.info("   Ready for IMAP configuration")
            return True
        else:
            logger.warning("⚠️  MailPlus status unclear")
            logger.info(f"   Status output: {status_after}")
            logger.info("   MailPlus may still be starting - check DSM Package Center")
            return False

    except ImportError:
        logger.error("❌ paramiko not available")
        logger.info("   Install: pip install paramiko")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to start MailPlus: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = start_mailplus()
    sys.exit(0 if success else 1)
