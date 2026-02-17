#!/usr/bin/env python3
"""
JARVIS: Find synopkg and Start MailPlus

Finds the correct synopkg executable and starts MailPlus Server.

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

logger = get_logger("JARVISFindMailPlus")


def find_and_start_mailplus():
    """Find synopkg executable and start MailPlus"""
    try:
        from nas_azure_vault_integration import NASAzureVaultIntegration
        import paramiko

        nas_integration = NASAzureVaultIntegration()
        credentials = nas_integration.get_nas_credentials()

        if not credentials:
            logger.error("❌ Could not get NAS credentials")
            return False

        nas_ip = "<NAS_PRIMARY_IP>"

        logger.info("=" * 80)
        logger.info("🚀 JARVIS: FINDING SYNOPKG AND STARTING MAILPLUS")
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

        # Find synopkg executable
        logger.info("🔍 Finding synopkg executable...")
        find_commands = [
            "which synopkg",
            "find /usr/syno -name synopkg -type f 2>/dev/null | head -1",
            "ls -la /usr/syno/bin/synopkg 2>/dev/null || echo ''",
            "ls -la /usr/syno/synopkg/bin/synopkg 2>/dev/null || echo ''",
        ]

        synopkg_path = None
        for cmd in find_commands:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            result = stdout.read().decode().strip()
            if result and "/" in result:
                synopkg_path = result.split()[0] if " " in result else result
                logger.info(f"✅ Found synopkg: {synopkg_path}")
                break

        if not synopkg_path:
            # Try common paths
            common_paths = [
                "/usr/syno/bin/synopkg",
                "/usr/syno/synopkg/bin/synopkg",
                "/usr/local/bin/synopkg",
            ]
            for path in common_paths:
                stdin, stdout, stderr = ssh.exec_command(f"test -f {path} && echo {path} || echo ''")
                if stdout.read().decode().strip():
                    synopkg_path = path
                    logger.info(f"✅ Found synopkg at: {synopkg_path}")
                    break

        if not synopkg_path:
            logger.error("❌ Could not find synopkg executable")
            ssh.close()
            return False

        # Check Mail Server status and stop if running
        logger.info("📋 Checking Mail Server status...")
        stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} status MailServer")
        mail_server_status = stdout.read().decode().strip()
        logger.info(f"   Mail Server: {mail_server_status}")

        if "is running" in mail_server_status.lower():
            logger.info("🛑 Stopping Mail Server...")
            stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} stop MailServer")
            output = stdout.read().decode().strip()
            if output:
                logger.info(f"   {output}")
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

        # Wait and check status
        logger.info("   Waiting for MailPlus to start...")
        time.sleep(8)

        logger.info("📋 Checking MailPlus status...")
        stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} status MailPlus")
        status = stdout.read().decode().strip()
        logger.info(f"   Status: {status}")

        ssh.close()

        logger.info("")
        logger.info("=" * 80)

        if "is running" in status.lower():
            logger.info("✅ SUCCESS! MailPlus Server is now running!")
            logger.info("   Ready for IMAP configuration")
            return True
        elif status:
            logger.info(f"✅ MailPlus start command executed")
            logger.info(f"   Status: {status}")
            logger.info("   Please verify in DSM Package Center that MailPlus is running")
            return True
        else:
            logger.warning("⚠️  Could not verify MailPlus status")
            logger.info("   Please check DSM Package Center manually")
            return False

    except ImportError:
        logger.error("❌ paramiko not available")
        return False
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = find_and_start_mailplus()
    sys.exit(0 if success else 1)
