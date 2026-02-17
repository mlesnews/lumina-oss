#!/usr/bin/env python3
"""
JARVIS: Fix Abnormal MailPlus State

Fixes MailPlus-Server abnormal state by force stopping and restarting.

Tags: #JARVIS #MAILPLUS #AUTOMATION @JARVIS @LUMINA @DOIT
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

logger = get_logger("JARVISFixMailPlus")


def fix_abnormal_mailplus():
    """Fix MailPlus-Server abnormal state"""
    try:
        from nas_azure_vault_integration import NASAzureVaultIntegration
        import paramiko

        nas_integration = NASAzureVaultIntegration()
        credentials = nas_integration.get_nas_credentials()

        if not credentials:
            logger.error("❌ Could not get NAS credentials")
            return False

        nas_ip = "<NAS_PRIMARY_IP>"
        synopkg_path = "/usr/syno/bin/synopkg"
        package_name = "MailPlus-Server"

        logger.info("=" * 80)
        logger.info("🔧 JARVIS: FIXING ABNORMAL MAILPLUS STATE")
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

        # Step 1: Check current status
        logger.info("📋 STEP 1: Checking current status...")
        logger.info("-" * 80)
        stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} status {package_name}")
        status_before = stdout.read().decode().strip()
        logger.info(f"   Status: {status_before[:200]}...")

        # Step 2: Force stop MailPlus-Server to clear abnormal state
        logger.info("")
        logger.info("🛑 STEP 2: Force stopping MailPlus-Server to clear abnormal state...")
        logger.info("-" * 80)

        # Try stop command
        stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} stop {package_name}")
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        if output:
            logger.info(f"   Stop output: {output}")
        if error:
            logger.info(f"   Stop error: {error}")

        # Wait for stop to complete
        logger.info("   Waiting for stop to complete...")
        time.sleep(5)

        # Verify stopped
        stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} status {package_name}")
        status_after_stop = stdout.read().decode().strip()
        logger.info(f"   Status after stop: {status_after_stop[:200]}...")

        # Step 3: Ensure Mail Server is stopped
        logger.info("")
        logger.info("🛑 STEP 3: Ensuring Mail Server is stopped...")
        logger.info("-" * 80)

        stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} status MailServer")
        mail_server_status = stdout.read().decode().strip()

        if "is running" in mail_server_status.lower() or '"status":"start"' in mail_server_status:
            logger.info("   ⚠️  Mail Server is running - stopping...")
            stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} stop MailServer")
            stdout.read()  # Wait for completion
            time.sleep(3)
            logger.info("   ✅ Mail Server stopped")
        else:
            logger.info("   ✅ Mail Server already stopped")

        # Step 4: Wait for locks to clear
        logger.info("")
        logger.info("⏳ STEP 4: Waiting for package locks to clear...")
        logger.info("-" * 80)
        time.sleep(5)

        # Step 5: Start MailPlus-Server
        logger.info("")
        logger.info("🚀 STEP 5: Starting MailPlus-Server...")
        logger.info("-" * 80)

        stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} start {package_name}")
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        if output:
            logger.info(f"   Start output: {output}")
        if error:
            logger.warning(f"   Start error: {error}")

        # Wait for start
        logger.info("   Waiting for MailPlus-Server to start...")
        time.sleep(10)

        # Step 6: Verify status
        logger.info("")
        logger.info("📋 STEP 6: Verifying final status...")
        logger.info("-" * 80)

        stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} status {package_name}")
        final_status = stdout.read().decode().strip()
        logger.info(f"   Final status: {final_status[:300]}...")

        ssh.close()

        logger.info("")
        logger.info("=" * 80)

        # Check if running
        if "is running" in final_status.lower() or '"status":"start"' in final_status:
            logger.info("✅ SUCCESS! MailPlus-Server is now running!")
            logger.info("   Ready for IMAP configuration")
            return True
        elif "start_failed" in final_status or "abnormal" in final_status.lower():
            logger.warning("⚠️  MailPlus-Server still in abnormal state")
            logger.info("   Please check DSM Package Center manually")
            logger.info("   You may need to restart the package from DSM web interface")
            return False
        else:
            logger.info("✅ MailPlus-Server start command executed")
            logger.info("   Please verify in DSM Package Center that it's running")
            return True

    except ImportError:
        logger.error("❌ paramiko not available")
        return False
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = fix_abnormal_mailplus()
    sys.exit(0 if success else 1)
