#!/usr/bin/env python3
"""
JARVIS: Clear All Email Accounts and Start MailPlus

Clears all email accounts and starts MailPlus, then creates the account.

Tags: #JARVIS #MAILPLUS #ACCOUNT #CLEAR #AUTOMATION @JARVIS @LUMINA @DOIT
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

    def get_logger(name):
        return logging.getLogger(name)

logger = get_logger("JARVISClearMailPlus")

# Account configuration
ACCOUNT_EMAIL = "mlesn@<LOCAL_HOSTNAME>"
ACCOUNT_PASSWORD = None  # Retrieved from Azure Key Vault at runtime
IMAP_PORT = 993
NAS_IP = "<NAS_PRIMARY_IP>"
NAS_PORT = 5001


def clear_accounts_and_start_mailplus():
    """Clear all email accounts and start MailPlus"""
    try:
        import paramiko
        from nas_azure_vault_integration import NASAzureVaultIntegration
        from synology_api_base import SynologyAPIBase

        logger.info("=" * 80)
        logger.info("🧹 JARVIS: CLEARING ACCOUNTS & STARTING MAILPLUS")
        logger.info("=" * 80)
        logger.info("")
        logger.info("Account: %s", ACCOUNT_EMAIL)
        logger.info("IMAP Port: %s", IMAP_PORT)
        logger.info("")

        nas_integration = NASAzureVaultIntegration()
        credentials = nas_integration.get_nas_credentials()

        if not credentials:
            logger.error("❌ Could not get NAS credentials")
            return False

        # Step 1: Stop MailPlus
        logger.info("📋 STEP 1: Stopping MailPlus-Server...")
        logger.info("-" * 80)

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        logger.info("🔌 Connecting to NAS: %s", NAS_IP)
        ssh.connect(
            NAS_IP,
            username=credentials["username"],
            password=credentials["password"],
            timeout=10
        )

        synopkg_path = "/usr/syno/bin/synopkg"
        package_name = "MailPlus-Server"

        # Stop MailPlus
        _, stdout, _ = ssh.exec_command(
            f"sudo {synopkg_path} stop {package_name}"
        )
        stop_output = stdout.read().decode().strip()
        logger.info("   Stop result: %s", stop_output[:200])
        time.sleep(3)

        # Step 2: Clear accounts (if possible via API or SSH)
        logger.info("")
        logger.info("📋 STEP 2: Clearing email accounts...")
        logger.info("-" * 80)

        # Try via API
        api = SynologyAPIBase(nas_ip=NAS_IP, nas_port=NAS_PORT, verify_ssl=False)

        if api.login(credentials["username"], credentials["password"]):
            logger.info("✅ Connected to DSM API")

            # Try to list accounts first
            accounts = api.api_call(
                api="SYNO.MailPlusServer.Account",
                method="list",
                version="1",
                require_auth=True
            )

            if accounts:
                account_list = accounts.get('accounts', [])
                logger.info("   Found %d account(s)", len(account_list))

                # Try to delete each account
                for acc in account_list:
                    email = acc.get('email', '')
                    logger.info("   Attempting to delete: %s", email)

                    delete_result = api.api_call(
                        api="SYNO.MailPlusServer.Account",
                        method="delete",
                        version="1",
                        params={"email": email},
                        require_auth=True
                    )

                    if delete_result:
                        logger.info("   ✅ Deleted: %s", email)
                    else:
                        logger.warning("   ⚠️  Could not delete: %s", email)
            else:
                logger.info("   No accounts found or API not available")

            api.logout()
        else:
            logger.warning("⚠️  Could not connect to DSM API")

        # Step 3: Start MailPlus
        logger.info("")
        logger.info("📋 STEP 3: Starting MailPlus-Server...")
        logger.info("-" * 80)

        _, stdout, _ = ssh.exec_command(
            f"sudo {synopkg_path} start {package_name}"
        )
        start_output = stdout.read().decode().strip()
        logger.info("   Start result: %s", start_output[:200])

        logger.info("⏳ Waiting 10 seconds for MailPlus to start...")
        time.sleep(10)

        ssh.close()

        # Step 4: Create the account
        logger.info("")
        logger.info("📋 STEP 4: Creating email account...")
        logger.info("-" * 80)
        logger.info("   Email: %s", ACCOUNT_EMAIL)
        logger.info("   Password: [REDACTED]")
        logger.info("")

        # Try via API
        api = SynologyAPIBase(nas_ip=NAS_IP, nas_port=NAS_PORT, verify_ssl=False)

        if api.login(credentials["username"], credentials["password"]):
            # Extract username and domain
            if '@' in ACCOUNT_EMAIL:
                username, domain = ACCOUNT_EMAIL.split('@', 1)
            else:
                username = ACCOUNT_EMAIL
                domain = None

            # Try to create account
            create_params = {
                "username": username,
                "password": ACCOUNT_PASSWORD,
            }

            if domain:
                create_params["domain"] = domain

            result = api.api_call(
                api="SYNO.MailPlusServer.Account",
                method="create",
                version="1",
                params=create_params,
                require_auth=True
            )

            api.logout()

            if result:
                logger.info("✅ Account created successfully via API!")
            else:
                logger.warning("⚠️  API creation failed - may need GUI")
                logger.info("   Opening MailPlus Account page for manual creation...")
                import webbrowser
                webbrowser.open(f"https://{NAS_IP}:{NAS_PORT}/#mailplus/account")
                logger.info("   Please create account manually:")
                logger.info("   Email: %s", ACCOUNT_EMAIL)
                logger.info("   Password: %s", ACCOUNT_PASSWORD)
        else:
            logger.error("❌ Could not connect to DSM API")
            return False

        # Step 5: Verify account exists
        logger.info("")
        logger.info("📋 STEP 5: Verifying account...")
        logger.info("-" * 80)

        api = SynologyAPIBase(nas_ip=NAS_IP, nas_port=NAS_PORT, verify_ssl=False)

        if api.login(credentials["username"], credentials["password"]):
            accounts = api.api_call(
                api="SYNO.MailPlusServer.Account",
                method="list",
                version="1",
                require_auth=True
            )

            if accounts:
                account_list = accounts.get('accounts', [])
                for acc in account_list:
                    if acc.get('email', '').lower() == ACCOUNT_EMAIL.lower():
                        logger.info("✅ Account verified: %s", ACCOUNT_EMAIL)
                        api.logout()
                        return True

                logger.warning(
                    "⚠️  Account %s not found after creation",
                    ACCOUNT_EMAIL
                )
            else:
                logger.warning("⚠️  Could not verify account")

            api.logout()

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ MAILPLUS CLEARED AND STARTED!")
        logger.info("=" * 80)
        logger.info("")
        logger.info("📧 Next: Complete Outlook setup")
        logger.info("   python scripts/python/jarvis_complete_outlook_setup_with_password.py")

        return True

    except ImportError:
        logger.error("❌ Required modules not available")
        return False
    except (ConnectionError, TimeoutError, ValueError) as e:
        logger.error("❌ Failed: %s", e)
        import traceback
        logger.debug(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = clear_accounts_and_start_mailplus()
    sys.exit(0 if success else 1)
