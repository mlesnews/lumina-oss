#!/usr/bin/env python3
"""
JARVIS: Verify MailPlus Running and Setup Outlook

Verifies MailPlus-Server is running, checks IMAP port 993, and completes Outlook setup.

Tags: #JARVIS #MAILPLUS #OUTLOOK #AUTOMATION @JARVIS @LUMINA @DOIT
"""

import sys
import socket
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

logger = get_logger("JARVISVerifyMailPlus")


def check_port_open(host: str, port: int, timeout: int = 5) -> bool:
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def verify_mailplus_and_setup_outlook():
    """Verify MailPlus is running and setup Outlook"""
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
        logger.info("✅ JARVIS: VERIFYING MAILPLUS & SETTING UP OUTLOOK")
        logger.info("=" * 80)
        logger.info("")

        # Step 1: Verify MailPlus-Server is running
        logger.info("📋 STEP 1: Verifying MailPlus-Server status...")
        logger.info("-" * 80)

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        logger.info(f"🔌 Connecting to NAS: {nas_ip}")
        ssh.connect(
            nas_ip,
            username=credentials["username"],
            password=credentials["password"],
            timeout=10
        )

        stdin, stdout, stderr = ssh.exec_command(f"{synopkg_path} status {package_name}")
        status = stdout.read().decode().strip()

        if "is running" in status.lower() or '"status":"start"' in status:
            logger.info("✅ MailPlus-Server is running!")
        else:
            logger.warning(f"⚠️  MailPlus-Server status unclear: {status[:200]}...")
            logger.info("   Please verify in DSM Package Center")
            ssh.close()
            return False

        # Step 2: Check IMAP port 993
        logger.info("")
        logger.info("📋 STEP 2: Checking IMAP port 993...")
        logger.info("-" * 80)

        if check_port_open(nas_ip, 993):
            logger.info("✅ IMAP port 993 is open!")
        else:
            logger.warning("⚠️  IMAP port 993 is not open")
            logger.info("   MailPlus-Server may need IMAP enabled in settings")
            logger.info("   Proceeding anyway - will configure IMAP if needed")

        ssh.close()

        # Step 3: Setup Outlook
        logger.info("")
        logger.info("📧 STEP 3: Setting up Outlook email account...")
        logger.info("-" * 80)

        # Import and run Outlook setup
        try:
            from setup_outlook_classic_company_email import setup_company_email

            logger.info("   Running Outlook setup script...")
            result = setup_company_email()

            if result.get("success"):
                logger.info("✅ Outlook email account configured!")
                logger.info(f"   Account: {result.get('account_name', 'Company Email')}")
                return True
            else:
                logger.warning(f"⚠️  Outlook setup had issues: {result.get('error', 'Unknown error')}")
                return False

        except ImportError:
            logger.warning("⚠️  Outlook setup script not found")
            logger.info("   Attempting to run jarvis_complete_outlook_email_setup.py...")

            # Try alternative script
            import subprocess
            result = subprocess.run(
                [sys.executable, str(script_dir / "jarvis_complete_outlook_email_setup.py")],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                logger.info("✅ Outlook setup completed!")
                return True
            else:
                logger.warning(f"⚠️  Outlook setup failed: {result.stderr[:200]}")
                return False

    except ImportError:
        logger.error("❌ Required modules not available")
        return False
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = verify_mailplus_and_setup_outlook()
    sys.exit(0 if success else 1)
