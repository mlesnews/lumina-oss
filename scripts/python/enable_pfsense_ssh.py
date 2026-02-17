#!/usr/bin/env python3
"""
Enable SSH on pfSense via Web Portal

Since SSH is currently disabled, this script uses the web portal to enable SSH access.

Tags: #PFSENSE #SSH #CONFIGURATION @JARVIS @LUMINA
"""

import sys
from pathlib import Path

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from pfsense_azure_vault_integration import PFSenseAzureVaultIntegration
    from lumina_logger import get_logger
    logger = get_logger("EnablePFSenseSSH")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("EnablePFSenseSSH")


def enable_ssh_via_web_portal(pfsense_ip: str = "<NAS_IP>") -> bool:
    """
    Enable SSH on pfSense via web portal

    Manual steps (web portal):
    1. Login to https://<NAS_IP>
    2. Navigate to: System > Advanced > Admin Access
    3. Enable SSH: Check "Enable Secure Shell (SSH)"
    4. SSH Port: 22 (default)
    5. SSH Key Only: Unchecked (to allow password auth)
    6. Save

    Args:
        pfsense_ip: pfSense IP address

    Returns:
        True if instructions provided successfully
    """
    logger.info("=" * 70)
    logger.info("🔧 ENABLE SSH ON PFSENSE")
    logger.info("=" * 70)

    logger.info("\n⚠️  SSH is currently disabled on pfSense")
    logger.info("   To enable SSH, follow these steps via web portal:\n")

    logger.info("📋 Steps to Enable SSH:")
    logger.info("   1. Open browser: https://<NAS_IP>")
    logger.info("   2. Login with credentials from Azure Key Vault")
    logger.info("   3. Navigate to: System > Advanced > Admin Access")
    logger.info("   4. Enable SSH:")
    logger.info("      ✅ Check 'Enable Secure Shell (SSH)'")
    logger.info("      ✅ SSH Port: 22 (default)")
    logger.info("      ⚠️  SSH Key Only: UNCHECKED (to allow password auth)")
    logger.info("   5. Click 'Save'")
    logger.info("   6. SSH should now be accessible on port 22")

    logger.info("\n🔍 Verify SSH is enabled:")
    logger.info("   Test-NetConnection -ComputerName <NAS_IP> -Port 22")
    logger.info("   (Should show TcpTestSucceeded: True)")

    logger.info("\n📝 Alternative: Enable via SSH (if you have console access):")
    logger.info("   1. Access pfSense console (physical or via web shell)")
    logger.info("   2. Run: /etc/rc.d/sshd enable")
    logger.info("   3. Run: /etc/rc.d/sshd start")

    # Try to login to web portal and provide more specific instructions
    integration = PFSenseAzureVaultIntegration(pfsense_ip=pfsense_ip)

    if integration.login_web_portal():
        logger.info("\n✅ Successfully logged into pfSense web portal")
        logger.info("   You can now manually enable SSH via the web UI")
        logger.info("   Path: System > Advanced > Admin Access")
        return True
    else:
        logger.warning("\n⚠️  Could not login to web portal")
        logger.info("   Please login manually and enable SSH")
        return False


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Enable SSH on pfSense"
    )
    parser.add_argument(
        "--pfsense-ip",
        default="<NAS_IP>",
        help="pfSense IP address"
    )

    args = parser.parse_args()

    result = enable_ssh_via_web_portal(pfsense_ip=args.pfsense_ip)

    return 0 if result else 1


if __name__ == "__main__":


    sys.exit(main())