#!/usr/bin/env python3
"""
JARVIS: Check Mail Services Status

Checks status of Mail Server and MailPlus Server via SSH to determine which is running.

Tags: #JARVIS #MAILPLUS #MAILSERVER #STATUS @JARVIS @LUMINA
"""

import sys
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

logger = get_logger("JARVISMailStatus")


def check_mail_services_status():
    """Check status of both Mail Server and MailPlus"""
    try:
        from nas_azure_vault_integration import NASAzureVaultIntegration
        import paramiko

        nas_integration = NASAzureVaultIntegration()
        credentials = nas_integration.get_nas_credentials()

        if not credentials:
            logger.error("❌ Could not get NAS credentials")
            return None

        nas_ip = "<NAS_PRIMARY_IP>"

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        logger.info(f"🔌 Connecting to NAS via SSH: {nas_ip}")
        ssh.connect(
            nas_ip,
            username=credentials["username"],
            password=credentials["password"],
            timeout=10
        )

        # Check Mail Server
        logger.info("📋 Checking Mail Server status...")
        stdin, stdout, stderr = ssh.exec_command("synopkg status MailServer")
        mail_server_status = stdout.read().decode().strip()
        mail_server_error = stderr.read().decode().strip()

        # Check MailPlus
        logger.info("📋 Checking MailPlus status...")
        stdin, stdout, stderr = ssh.exec_command("synopkg status MailPlus")
        mailplus_status = stdout.read().decode().strip()
        mailplus_error = stderr.read().decode().strip()

        # Also try alternative package names
        logger.info("📋 Checking alternative package names...")

        # Try MailStation (older name)
        stdin, stdout, stderr = ssh.exec_command("synopkg status MailStation")
        mailstation_status = stdout.read().decode().strip()

        # List all mail-related packages
        logger.info("📋 Listing all mail-related packages...")
        stdin, stdout, stderr = ssh.exec_command("synopkg list | grep -i mail")
        all_mail_packages = stdout.read().decode().strip()

        ssh.close()

        print("=" * 80)
        print("📊 MAIL SERVICES STATUS")
        print("=" * 80)
        print()

        print("Mail Server (MailServer):")
        print(f"  Status: {mail_server_status}")
        if mail_server_error:
            print(f"  Error: {mail_server_error}")
        print()

        print("MailPlus (MailPlus):")
        print(f"  Status: {mailplus_status}")
        if mailplus_error:
            print(f"  Error: {mailplus_error}")
        print()

        print("MailStation (MailStation):")
        print(f"  Status: {mailstation_status}")
        print()

        print("All Mail-Related Packages:")
        if all_mail_packages:
            for line in all_mail_packages.split('\n'):
                if line.strip():
                    print(f"  {line.strip()}")
        else:
            print("  (No packages found)")
        print()

        # Determine which is running
        mail_server_running = "is running" in mail_server_status.lower() or "running" in mail_server_status.lower()
        mailplus_running = "is running" in mailplus_status.lower() or "running" in mailplus_status.lower()

        print("=" * 80)
        print("📊 SUMMARY")
        print("=" * 80)
        print(f"Mail Server Running: {'✅ Yes' if mail_server_running else '❌ No'}")
        print(f"MailPlus Running: {'✅ Yes' if mailplus_running else '❌ No'}")
        print()

        if mail_server_running and mailplus_running:
            print("⚠️  CONFLICT: Both services are running!")
            print("   Mail Server and MailPlus cannot run simultaneously.")
            print("   You need to stop Mail Server first.")
        elif mail_server_running:
            print("✅ Mail Server is running")
            print("   To use MailPlus, stop Mail Server first:")
            print("   synopkg stop MailServer")
        elif mailplus_running:
            print("✅ MailPlus is running")
            print("   Ready for IMAP configuration!")
        else:
            print("⚠️  Neither service appears to be running")
            print("   You may need to start MailPlus:")
            print("   synopkg start MailPlus")

        print()
        print("=" * 80)

        return {
            "mail_server_running": mail_server_running,
            "mailplus_running": mailplus_running,
            "mail_server_status": mail_server_status,
            "mailplus_status": mailplus_status,
            "all_mail_packages": all_mail_packages
        }

    except ImportError:
        logger.error("❌ paramiko not available")
        print("   Install: pip install paramiko")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to check status: {e}")
        return None


if __name__ == "__main__":
    check_mail_services_status()
