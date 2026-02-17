#!/usr/bin/env python3
"""
JARVIS: Force Stop Mail Server and Start MailPlus

Aggressively stops Mail Server and starts MailPlus, handling package locks.

Tags: #JARVIS #MAILPLUS #MAILSERVER #AUTOMATION @JARVIS @LUMINA @DOIT
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

logger = get_logger("JARVISForceMailSwitch")


def force_stop_mail_start_mailplus():
    """Force stop Mail Server and start MailPlus"""
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

        logger.info("=" * 80)
        logger.info("🚀 JARVIS: FORCE STOP MAIL SERVER → START MAILPLUS")
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

        # Step 1: Find all mail packages
        logger.info("📦 STEP 1: Finding mail packages...")
        logger.info("-" * 80)

        # List installed packages
        stdin, stdout, stderr = ssh.exec_command("ls /var/packages/ | grep -iE '(mail|mailplus|mailstation)'")
        installed_packages = stdout.read().decode().strip()

        mail_packages = []
        if installed_packages:
            for pkg in installed_packages.split('\n'):
                if pkg.strip():
                    mail_packages.append(pkg.strip())
                    logger.info(f"   Found: {pkg.strip()}")

        # Try to get package names from synopkg
        stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} list | grep -iE '(mail|mailplus|mailstation)'")
        synopkg_list = stdout.read().decode().strip()
        if synopkg_list:
            logger.info("   Packages from synopkg:")
            for line in synopkg_list.split('\n'):
                if line.strip():
                    logger.info(f"      {line.strip()}")

        # Step 2: Check Mail Server status and stop it
        logger.info("")
        logger.info("🛑 STEP 2: Stopping Mail Server...")
        logger.info("-" * 80)

        mail_server_names = ["MailServer", "mail-server", "MailStation", "mailstation"]
        mail_server_stopped = False

        for name in mail_server_names:
            logger.info(f"   Checking {name}...")
            stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} status {name}")
            status = stdout.read().decode().strip()

            if "is running" in status.lower() or '"status":"start"' in status:
                logger.info(f"   ⚠️  {name} is running - stopping...")
                stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} stop {name}")
                output = stdout.read().decode().strip()
                if output:
                    logger.info(f"      {output}")
                time.sleep(3)

                # Verify stopped
                stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} status {name}")
                new_status = stdout.read().decode().strip()
                if "is stopped" in new_status.lower() or '"status":"stop"' in new_status:
                    logger.info(f"   ✅ {name} stopped")
                    mail_server_stopped = True
                else:
                    logger.warning(f"   ⚠️  {name} status unclear: {new_status}")
            elif "is stopped" in status.lower() or '"status":"stop"' in status:
                logger.info(f"   ✅ {name} already stopped")
                mail_server_stopped = True
            elif "No such package" in status or "non_installed" in status:
                logger.info(f"   ℹ️  {name} not installed")
            else:
                logger.info(f"   Status: {status[:100]}...")

        # Step 3: Wait for package locks to clear
        logger.info("")
        logger.info("⏳ STEP 3: Waiting for package locks to clear...")
        logger.info("-" * 80)
        time.sleep(5)

        # Step 4: Find and start MailPlus
        logger.info("")
        logger.info("🚀 STEP 4: Starting MailPlus...")
        logger.info("-" * 80)

        mailplus_names = ["MailPlus", "MailPlus-Server", "mailplus-server", "MailPlusServer", "mailplus"]
        mailplus_started = False

        for name in mailplus_names:
            logger.info(f"   Trying {name}...")
            stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} status {name}")
            status = stdout.read().decode().strip()

            if "No such package" in status or "non_installed" in status:
                logger.info(f"   ℹ️  {name} not found")
                continue

            logger.info(f"   ✅ Found {name} - starting...")
            stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} start {name}")
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()

            if output:
                logger.info(f"      Output: {output}")
            if error:
                logger.warning(f"      Error: {error}")

            # Check for lock error
            if "failed to lock" in output.lower() or "failed to lock" in error.lower():
                logger.warning(f"   ⚠️  Package lock detected - waiting and retrying...")
                time.sleep(10)
                stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} start {name}")
                output = stdout.read().decode().strip()
                if output:
                    logger.info(f"      Retry output: {output}")

            # Wait and verify
            time.sleep(8)
            stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} status {name}")
            final_status = stdout.read().decode().strip()

            if "is running" in final_status.lower() or '"status":"start"' in final_status:
                logger.info(f"   ✅ {name} is now running!")
                mailplus_started = True
                break
            else:
                logger.info(f"   Status: {final_status[:150]}...")

        ssh.close()

        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Mail Server Stopped: {'✅ Yes' if mail_server_stopped else '❌ No'}")
        logger.info(f"MailPlus Started: {'✅ Yes' if mailplus_started else '❌ No'}")
        logger.info("")

        if mail_server_stopped and mailplus_started:
            logger.info("✅ SUCCESS! MailPlus Server is running!")
            logger.info("   Ready for IMAP configuration")
            return True
        elif mail_server_stopped:
            logger.warning("⚠️  Mail Server stopped but MailPlus did not start")
            logger.info("   Please check DSM Package Center manually")
            logger.info("   The package name might be different")
            return False
        else:
            logger.warning("⚠️  Could not complete switch")
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
    success = force_stop_mail_start_mailplus()
    sys.exit(0 if success else 1)
