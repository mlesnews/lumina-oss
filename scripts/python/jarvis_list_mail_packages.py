#!/usr/bin/env python3
"""
JARVIS: List Mail Packages

Lists all mail-related packages installed on NAS to find correct package name.

Tags: #JARVIS #MAILPLUS #PACKAGES @JARVIS @LUMINA
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

logger = get_logger("JARVISListMailPackages")


def list_mail_packages():
    """List all mail-related packages"""
    try:
        from nas_azure_vault_integration import NASAzureVaultIntegration
        import paramiko

        nas_integration = NASAzureVaultIntegration()
        credentials = nas_integration.get_nas_credentials()

        if not credentials:
            logger.error("❌ Could not get NAS credentials")
            return

        nas_ip = "<NAS_PRIMARY_IP>"
        synopkg_path = "/usr/syno/bin/synopkg"

        logger.info("=" * 80)
        logger.info("📦 JARVIS: LISTING MAIL PACKAGES")
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

        # List all packages
        logger.info("📋 Listing all packages...")
        stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} list")
        all_packages = stdout.read().decode().strip()

        # Filter for mail-related
        logger.info("")
        logger.info("📧 Mail-related packages:")
        logger.info("-" * 80)

        mail_packages = []
        for line in all_packages.split('\n'):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ["mail", "mailplus", "mailstation", "mail server"]):
                mail_packages.append(line)
                logger.info(f"   {line}")

        if not mail_packages:
            logger.info("   (No mail packages found in list)")

        # Also try listing installed packages differently
        logger.info("")
        logger.info("📋 Checking installed packages via Package Center API...")
        stdin, stdout, stderr = ssh.exec_command("ls /var/packages/ | grep -i mail")
        installed_packages = stdout.read().decode().strip()

        if installed_packages:
            logger.info("   Installed mail packages:")
            for pkg in installed_packages.split('\n'):
                if pkg.strip():
                    logger.info(f"      {pkg.strip()}")
        else:
            logger.info("   (No mail packages found in /var/packages/)")

        ssh.close()

        logger.info("")
        logger.info("=" * 80)
        logger.info("💡 Next Steps:")
        logger.info("   Use the correct package name from above to start MailPlus")
        logger.info("=" * 80)

    except ImportError:
        logger.error("❌ paramiko not available")
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        import traceback
        logger.debug(traceback.format_exc())


if __name__ == "__main__":
    list_mail_packages()
