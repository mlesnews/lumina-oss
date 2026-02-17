#!/usr/bin/env python3
"""
JARVIS Complete Outlook Email Setup - Full Autonomous Control

JARVIS takes full autonomous control to complete Outlook Classic company email setup:
1. Enable IMAP port 993 on MailStation via SSH/DSM API
2. Retrieve or prompt for password
3. Complete Outlook Classic account setup
4. Verify account configuration
5. Store credentials in Azure Vault

Tags: #JARVIS #OUTLOOK #AUTOMATION #MAILSTATION #FULLAUTO
@JARVIS @LUMINA @MANUS @DOIT
"""

import sys
import os
import time
import socket
from pathlib import Path
from typing import Dict, Any, Optional

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

logger = get_logger("JARVISOutlookSetup")


class JARVISCompleteOutlookSetup:
    """JARVIS autonomous control for complete Outlook email setup"""

    def __init__(self):
        """Initialize JARVIS setup"""
        self.nas_ip = "<NAS_PRIMARY_IP>"
        self.nas_port = 5001
        self.imap_port = 993
        self.smtp_port = 587

        logger.info("=" * 80)
        logger.info("🤖 JARVIS AUTONOMOUS OUTLOOK EMAIL SETUP")
        logger.info("=" * 80)
        logger.info("")

    def check_imap_port(self) -> bool:
        """Check if IMAP port 993 is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((self.nas_ip, self.imap_port))
            sock.close()
            return result == 0
        except Exception as e:
            logger.debug(f"Port check error: {e}")
            return False

    def enable_imap_via_ssh(self) -> bool:
        """Enable IMAP port 993 via SSH"""
        try:
            from nas_azure_vault_integration import NASAzureVaultIntegration

            nas_integration = NASAzureVaultIntegration()
            credentials = nas_integration.get_nas_credentials()

            if not credentials:
                logger.warning("⚠️  Could not get NAS credentials for SSH")
                return False

            import paramiko

            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            logger.info(f"🔌 Connecting to NAS via SSH: {self.nas_ip}")
            ssh.connect(
                self.nas_ip,
                username=credentials["username"],
                password=credentials["password"],
                timeout=10
            )

            # Enable IMAP service via MailStation API or direct config
            logger.info("⚙️  Enabling IMAP service on MailStation...")

            # Method 1: Use synopkg to check MailStation status
            stdin, stdout, stderr = ssh.exec_command("synopkg status MailStation")
            mailstation_status = stdout.read().decode().strip()

            if "is running" in mailstation_status.lower():
                logger.info("✅ MailStation is running")
            else:
                logger.warning("⚠️  MailStation may not be running")

            # Method 2: Try to enable IMAP via MailStation config
            # Note: This may require DSM API access or manual configuration
            logger.info("📝 Attempting to configure IMAP port 993...")

            # Check current MailStation config
            stdin, stdout, stderr = ssh.exec_command(
                "cat /usr/syno/etc/mail/mailserver.conf 2>/dev/null || echo 'config_not_found'"
            )
            config = stdout.read().decode().strip()

            if "config_not_found" not in config:
                logger.info("✅ Found MailStation config file")
                # Could parse and update config here if needed
            else:
                logger.info("ℹ️  Config file not found in standard location")

            ssh.close()

            # Note: IMAP port configuration may require DSM web interface
            # or MailStation package API access
            logger.info("💡 IMAP configuration may require DSM web interface access")
            logger.info("   Attempting alternative methods...")

            return True

        except ImportError:
            logger.warning("⚠️  paramiko not available for SSH access")
            logger.info("   Install: pip install paramiko")
            return False
        except Exception as e:
            logger.error(f"❌ SSH connection failed: {e}")
            return False

    def enable_imap_via_dsm_api(self) -> bool:
        """Enable IMAP via DSM API"""
        try:
            from nas_azure_vault_integration import NASAzureVaultIntegration
            from synology_nas_upload import SynologyNASUploader

            nas_integration = NASAzureVaultIntegration()
            credentials = nas_integration.get_nas_credentials()

            if not credentials:
                logger.warning("⚠️  Could not get NAS credentials")
                return False

            logger.info("🔌 Connecting to DSM API...")
            nas_uploader = SynologyNASUploader(
                nas_ip=self.nas_ip,
                nas_port=self.nas_port
            )

            if not nas_uploader.login(credentials["username"], credentials["password"]):
                logger.error("❌ Failed to login to DSM")
                return False

            logger.info("✅ Connected to DSM API")

            # Try to access MailStation package API
            # Note: MailStation API endpoints may vary
            logger.info("⚙️  Attempting to configure MailStation IMAP...")

            # This would require specific MailStation API endpoints
            # For now, we'll provide instructions
            logger.info("💡 MailStation IMAP configuration requires:")
            logger.info("   1. Access DSM web interface: https://<NAS_PRIMARY_IP>:5001")
            logger.info("   2. Navigate to: MailStation → Settings → Mail Service")
            logger.info("   3. Enable IMAP service")
            logger.info("   4. Set IMAP port to 993 (SSL/TLS)")

            nas_uploader.logout()
            return False  # Manual intervention may be needed

        except Exception as e:
            logger.error(f"❌ DSM API access failed: {e}")
            return False

    def get_password(self) -> Optional[str]:
        """Get password from various sources"""
        # Try Azure Vault
        try:
            from nas_azure_vault_integration import NASAzureVaultIntegration

            nas_integration = NASAzureVaultIntegration()
            vault_client = nas_integration.get_key_vault_client()

            if vault_client:
                secret_names = [
                    "nas-email-password",
                    "mailplus-mlesn-password",
                    "company-email-password",
                    "email-password",
                    "nas-mailplus-password"
                ]

                for secret_name in secret_names:
                    try:
                        secret = vault_client.get_secret(secret_name)
                        if secret and secret.value:
                            logger.info(f"✅ Password retrieved from Azure Vault: {secret_name}")
                            return secret.value
                    except Exception:
                        continue
        except Exception as e:
            logger.debug(f"Vault access failed: {e}")

        # Try environment variable
        password = os.getenv("NAS_EMAIL_PASSWORD") or os.getenv("COMPANY_EMAIL_PASSWORD")
        if password:
            logger.info("✅ Password retrieved from environment variable")
            return password

        return None

    def store_password_in_vault(self, password: str) -> bool:
        """Store password in Azure Vault"""
        try:
            from nas_azure_vault_integration import NASAzureVaultIntegration

            nas_integration = NASAzureVaultIntegration()
            vault_client = nas_integration.get_key_vault_client()

            if not vault_client:
                logger.warning("⚠️  Could not access Azure Vault")
                return False

            # Store as nas-email-password
            try:
                vault_client.set_secret("nas-email-password", password)
                logger.info("✅ Password stored in Azure Vault as: nas-email-password")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to store password: {e}")
                return False
        except Exception as e:
            logger.error(f"❌ Vault storage failed: {e}")
            return False

    def setup_outlook(self, password: Optional[str]) -> bool:
        """Setup Outlook Classic account"""
        try:
            from setup_outlook_classic_company_email import OutlookClassicSetup

            setup = OutlookClassicSetup()
            success = setup.setup_account(password or "MANUAL_ENTRY_REQUIRED")
            return success
        except Exception as e:
            logger.error(f"❌ Outlook setup failed: {e}")
            return False

    def verify_account(self) -> bool:
        """Verify account is configured"""
        try:
            import win32com.client

            outlook = win32com.client.Dispatch("Outlook.Application")
            namespace = outlook.GetNamespace("MAPI")
            accounts = namespace.Accounts

            for i in range(accounts.Count):
                account = accounts.Item(i + 1)
                if account.SmtpAddress == "mlesn@<LOCAL_HOSTNAME>":
                    logger.info("✅ Company email account is configured!")
                    return True

            logger.warning("⚠️  Company email account not found")
            return False
        except Exception as e:
            logger.debug(f"Verification failed: {e}")
            return False

    def execute_full_setup(self) -> Dict[str, Any]:
        """Execute complete autonomous setup"""
        logger.info("🚀 JARVIS AUTONOMOUS EXECUTION STARTING")
        logger.info("")

        results = {
            "imap_enabled": False,
            "password_retrieved": False,
            "outlook_setup": False,
            "account_verified": False,
            "password_stored": False
        }

        # Step 1: Check IMAP port
        logger.info("STEP 1: Checking IMAP port 993...")
        if self.check_imap_port():
            logger.info("✅ IMAP port 993 is already open")
            results["imap_enabled"] = True
        else:
            logger.warning("❌ IMAP port 993 is closed")
            logger.info("   Attempting to enable via SSH...")

            if self.enable_imap_via_ssh():
                logger.info("✅ SSH connection successful")
                # Check again after a delay
                time.sleep(2)
                if self.check_imap_port():
                    logger.info("✅ IMAP port 993 is now open!")
                    results["imap_enabled"] = True
                else:
                    logger.warning("⚠️  IMAP port still closed - may require DSM web interface")
            else:
                logger.warning("⚠️  Could not enable IMAP via SSH")
                logger.info("   Manual intervention may be required:")
                logger.info("   DSM → MailStation → Settings → Mail Service → Enable IMAP (993)")

        logger.info("")

        # Step 2: Get password
        logger.info("STEP 2: Retrieving password...")
        password = self.get_password()
        if password:
            results["password_retrieved"] = True
        else:
            logger.warning("⚠️  Password not found - will prompt during setup")

        logger.info("")

        # Step 3: Setup Outlook
        logger.info("STEP 3: Setting up Outlook Classic...")
        if self.setup_outlook(password):
            results["outlook_setup"] = True
        else:
            logger.error("❌ Outlook setup failed")

        logger.info("")

        # Step 4: Verify account
        logger.info("STEP 4: Verifying account configuration...")
        time.sleep(3)  # Give Outlook time to process
        if self.verify_account():
            results["account_verified"] = True
        else:
            logger.warning("⚠️  Account verification failed - may need IMAP port enabled")

        logger.info("")

        # Step 5: Store password if we have it
        if password and not results["password_retrieved"]:
            logger.info("STEP 5: Storing password in Azure Vault...")
            if self.store_password_in_vault(password):
                results["password_stored"] = True

        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 JARVIS SETUP SUMMARY")
        logger.info("=" * 80)
        logger.info(f"IMAP Port 993: {'✅ Enabled' if results['imap_enabled'] else '❌ Needs Enable'}")
        logger.info(f"Password Retrieved: {'✅ Yes' if results['password_retrieved'] else '⚠️  No'}")
        logger.info(f"Outlook Setup: {'✅ Complete' if results['outlook_setup'] else '❌ Failed'}")
        logger.info(f"Account Verified: {'✅ Yes' if results['account_verified'] else '⚠️  No'}")
        logger.info(f"Password Stored: {'✅ Yes' if results['password_stored'] else '⚠️  No'}")
        logger.info("")

        if all([results["outlook_setup"], results["account_verified"]]):
            logger.info("✅ JARVIS AUTONOMOUS SETUP COMPLETE!")
        else:
            logger.info("⚠️  Setup partially complete - review summary above")

        logger.info("=" * 80)

        return results


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Complete Outlook Email Setup")
        parser.add_argument("--password", type=str, help="NAS Mail Hub password")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        jarvis = JARVISCompleteOutlookSetup()

        # Override password if provided
        if args.password:
            jarvis.get_password = lambda: args.password

        results = jarvis.execute_full_setup()

        if args.json:
            import json
            print(json.dumps(results, indent=2, default=str))

        # Return success if all critical steps completed
        if results.get("outlook_setup") and results.get("account_verified"):
            return 0
        elif results.get("outlook_setup"):
            return 1  # Setup done but not verified
        else:
            return 2  # Setup failed


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())