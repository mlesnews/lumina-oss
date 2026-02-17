#!/usr/bin/env python3
"""
JARVIS: Create MailPlus Email Account

Creates the email account in MailPlus via API or opens GUI for manual creation.

Tags: #JARVIS #MAILPLUS #ACCOUNT #AUTOMATION @JARVIS @LUMINA @DOIT
"""

import sys
import webbrowser
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

logger = get_logger("JARVISCreateMailPlusAccount")

ACCOUNT_EMAIL = "mlesn@<LOCAL_HOSTNAME>"
NAS_IP = "<NAS_PRIMARY_IP>"


def create_account_via_api():
    """Try to create account via MailPlus API"""
    try:
        from nas_azure_vault_integration import NASAzureVaultIntegration
        from synology_api_base import SynologyAPIBase

        nas_integration = NASAzureVaultIntegration()
        credentials = nas_integration.get_nas_credentials()

        if not credentials:
            return False, "Could not get NAS credentials"

        api = SynologyAPIBase(nas_ip=NAS_IP, nas_port=5001, verify_ssl=False)

        if not api.login(credentials["username"], credentials["password"]):
            return False, "Failed to login to DSM API"

        # Try to create account via API
        # Note: MailPlus account creation API may require domain setup first
        logger.info("📋 Attempting to create account via API...")

        # First, check if domain exists
        domains = api.api_call(
            api="SYNO.MailPlusServer.Domain",
            method="list",
            version="1",
            require_auth=True
        )

        if domains:
            logger.info(f"✅ Found {len(domains.get('domains', []))} domain(s)")
            # Extract domain from email
            domain = ACCOUNT_EMAIL.split('@')[1] if '@' in ACCOUNT_EMAIL else None
            if domain:
                domain_found = False
                for d in domains.get('domains', []):
                    if d.get('domain', '').lower() == domain.lower():
                        domain_found = True
                        logger.info(f"✅ Domain {domain} exists")
                        break

                if not domain_found:
                    logger.warning(f"⚠️  Domain {domain} not found")
                    logger.info("   Domain may need to be created first")

        # Try to create account
        # MailPlus account creation typically requires:
        # - Domain to exist
        # - Username (part before @)
        # - Password
        # - Display name (optional)

        username = ACCOUNT_EMAIL.split('@')[0] if '@' in ACCOUNT_EMAIL else ACCOUNT_EMAIL
        domain = ACCOUNT_EMAIL.split('@')[1] if '@' in ACCOUNT_EMAIL else None

        account_params = {
            "username": username,
            "domain": domain,
            "password": credentials["password"],  # Use NAS password
            "mailbox_quota": "0",  # Unlimited
        }

        result = api.api_call(
            api="SYNO.MailPlusServer.Account",
            method="create",
            version="1",
            params=account_params,
            require_auth=True
        )

        api.logout()

        if result:
            logger.info("✅ Account created successfully via API!")
            return True, "Account created"
        else:
            return False, "API call failed - may need GUI creation"

    except Exception as e:
        return False, f"Error: {e}"


def open_account_creation_gui():
    try:
        """Open MailPlus account creation page in browser"""
        account_url = f"https://{NAS_IP}:5001/#mailplus/account"

        logger.info(f"Opening: {account_url}")
        webbrowser.open(account_url)

        logger.info("")
        logger.info("📋 Manual Steps to Create Account:")
        logger.info("-" * 80)
        logger.info("1. In the browser window that opened:")
        logger.info("2. Click 'Create' or 'Add' button")
        logger.info(f"3. Enter email: {ACCOUNT_EMAIL}")
        logger.info("4. Set password (can use NAS password)")
        logger.info("5. Set mailbox quota (or leave default)")
        logger.info("6. Click 'Create' or 'Save'")
        logger.info("")
        logger.info("💡 After creating the account:")
        logger.info("   Run: python scripts/python/jarvis_complete_outlook_setup_with_password.py")


    except Exception as e:
        logger.error(f"Error in open_account_creation_gui: {e}", exc_info=True)
        raise
def main():
    """Main execution"""
    logger.info("=" * 80)
    logger.info("📧 JARVIS: CREATING MAILPLUS EMAIL ACCOUNT")
    logger.info("=" * 80)
    logger.info("")
    logger.info(f"Account: {ACCOUNT_EMAIL}")
    logger.info("")

    # Try API first
    logger.info("📋 STEP 1: Attempting API creation...")
    logger.info("-" * 80)
    success, message = create_account_via_api()

    if success:
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ ACCOUNT CREATED SUCCESSFULLY!")
        logger.info("=" * 80)
        logger.info("")
        logger.info("📧 Next: Complete Outlook setup")
        logger.info("   python scripts/python/jarvis_complete_outlook_setup_with_password.py")
        return True
    else:
        logger.warning(f"⚠️  API creation failed: {message}")
        logger.info("")
        logger.info("📋 STEP 2: Opening GUI for manual creation...")
        logger.info("-" * 80)
        open_account_creation_gui()
        return False


if __name__ == "__main__":
    sys.exit(0 if success else 1)


    success = main()