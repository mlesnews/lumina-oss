#!/usr/bin/env python3
"""
JARVIS Enable IMAP via SSH - Direct Configuration

Uses SSH to directly configure MailStation IMAP settings.

Tags: #JARVIS #MAILSTATION #IMAP #SSH #AUTOMATION
@JARVIS @LUMINA @DOIT
"""

import sys
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

try:
    import paramiko
    SSH_AVAILABLE = True
except ImportError:
    SSH_AVAILABLE = False

try:
    from nas_azure_vault_integration import NASAzureVaultIntegration
    VAULT_AVAILABLE = True
except ImportError:
    VAULT_AVAILABLE = False

logger = get_logger("JARVISEnableIMAPSSH")


def enable_imap_via_ssh() -> Dict[str, Any]:
    """Enable IMAP via SSH"""
    logger.info("=" * 80)
    logger.info("🤖 JARVIS ENABLING IMAP VIA SSH")
    logger.info("=" * 80)
    logger.info("")

    result = {
        "success": False,
        "method": "ssh",
        "error": None
    }

    if not SSH_AVAILABLE:
        logger.error("❌ paramiko not available")
        result["error"] = "SSH not available"
        return result

    if not VAULT_AVAILABLE:
        logger.error("❌ Azure Vault not available")
        result["error"] = "Vault not available"
        return result

    # Get credentials
    nas_integration = NASAzureVaultIntegration()
    credentials = nas_integration.get_nas_credentials()

    if not credentials:
        logger.error("❌ Could not get credentials")
        result["error"] = "Credentials not available"
        return result

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        logger.info("🔌 Connecting to NAS via SSH...")
        ssh.connect(
            "<NAS_PRIMARY_IP>",
            username=credentials["username"],
            password=credentials["password"],
            timeout=10
        )

        logger.info("✅ Connected to NAS")
        logger.info("")
        logger.info("⚙️  Configuring MailStation IMAP...")

        # Method 1: Check MailStation package status
        logger.info("   Checking MailStation status...")
        stdin, stdout, stderr = ssh.exec_command("synopkg status MailStation")
        status_output = stdout.read().decode().strip()
        logger.info(f"   Status: {status_output[:100]}")

        # Method 2: Try to enable IMAP via MailStation config file
        logger.info("   Looking for MailStation configuration...")

        # Common MailStation config locations
        config_paths = [
            "/usr/syno/etc/mail/mailserver.conf",
            "/var/packages/MailStation/etc/mailserver.conf",
            "/usr/syno/etc/mailserver.conf"
        ]

        config_found = False
        for config_path in config_paths:
            stdin, stdout, stderr = ssh.exec_command(f"test -f {config_path} && echo 'exists' || echo 'not_found'")
            if stdout.read().decode().strip() == "exists":
                logger.info(f"   ✅ Found config: {config_path}")
                config_found = True

                # Read current config
                stdin, stdout, stderr = ssh.exec_command(f"cat {config_path}")
                config_content = stdout.read().decode()
                logger.debug(f"   Config content preview: {config_content[:200]}")
                break

        # Method 3: Use synoservice to enable IMAP
        logger.info("   Attempting to enable IMAP service...")

        # Check if IMAP service exists
        stdin, stdout, stderr = ssh.exec_command("synoservice --list | grep -i imap || echo 'not_found'")
        imap_services = stdout.read().decode().strip()
        logger.info(f"   IMAP services: {imap_services[:100]}")

        # Method 4: Try MailStation API via command line
        logger.info("   Attempting MailStation configuration via command line...")

        # Note: MailStation configuration may require DSM API or web interface
        # SSH access might be limited for package configuration

        logger.info("")
        logger.warning("⚠️  MailStation IMAP configuration via SSH is limited")
        logger.warning("   MailStation settings are typically managed via DSM web interface")
        logger.warning("")
        logger.info("💡 Alternative: Use DSM web interface (already opened by JARVIS)")
        logger.info("   Or try DSM API configuration")

        ssh.close()

        result["error"] = "SSH configuration limited - use DSM web interface"
        return result

    except Exception as e:
        logger.error(f"❌ SSH configuration failed: {e}")
        result["error"] = str(e)
        return result


def main():
    """Main entry point"""
    result = enable_imap_via_ssh()

    logger.info("")
    logger.info("=" * 80)
    logger.info("📊 CONFIGURATION STATUS")
    logger.info("=" * 80)
    logger.info(f"Method: {result['method']}")
    logger.info(f"Status: {'✅ Success' if result['success'] else '⚠️  Limited'}")
    if result.get('error'):
        logger.info(f"Note: {result['error']}")
    logger.info("=" * 80)

    logger.info("")
    logger.info("💡 RECOMMENDED: Complete IMAP configuration in DSM web interface")
    logger.info("   JARVIS has already opened DSM and logged in")
    logger.info("   Navigate to: MailStation → Settings → Mail Service")
    logger.info("   Enable IMAP port 993 (SSL/TLS)")

    return 0 if result["success"] else 1


if __name__ == "__main__":


    sys.exit(main())