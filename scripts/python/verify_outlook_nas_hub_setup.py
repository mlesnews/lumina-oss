"""
Verify Outlook Classic NAS Mail Hub Setup
Checks if Outlook is configured with NAS Mail Hub account.

#JARVIS #LUMINA #OUTLOOK #VERIFICATION
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("VerifyOutlookNASHubSetup")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("VerifyOutlookNASHubSetup")


def verify_outlook_setup() -> bool:
    """
    Verify Outlook is configured with NAS Mail Hub account.

    Returns:
        True if configured, False otherwise
    """
    logger.info("="*80)
    logger.info("VERIFYING OUTLOOK CLASSIC - NAS MAIL HUB SETUP")
    logger.info("="*80)
    logger.info("")

    try:
        import win32com.client
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        accounts = namespace.Accounts

        logger.info("✅ Outlook is accessible")
        logger.info("")
        logger.info("Current Outlook Accounts:")
        logger.info("-" * 80)

        nas_account_found = False
        account_count = 0

        for account in accounts:
            account_count += 1
            email = account.SmtpAddress
            display_name = account.DisplayName
            account_type = account.AccountType

            logger.info(f"  [{account_count}] {display_name}")
            logger.info(f"      Email: {email}")
            logger.info(f"      Type: {account_type}")

            # Check if this is the NAS Mail Hub account
            if email == "mlesn@<LOCAL_HOSTNAME>" or "<LOCAL_HOSTNAME>" in email.lower():
                nas_account_found = True
                logger.info(f"      ✅ NAS Mail Hub account found!")

            logger.info("")

        if account_count == 0:
            logger.warning("⚠️  No accounts configured in Outlook")
            logger.info("")
            logger.info("Please add the NAS Mail Hub account:")
            logger.info("  1. File → Account Settings → Account Settings")
            logger.info("  2. Click 'New...' and follow the setup guide")
            logger.info("  3. See: config/outlook/OUTLOOK_DETAILED_SETUP_GUIDE.md")
            return False

        logger.info("="*80)
        if nas_account_found:
            logger.info("✅ NAS MAIL HUB ACCOUNT IS CONFIGURED")
            logger.info("="*80)
            logger.info("")
            logger.info("Next Steps:")
            logger.info("  1. Check Outlook inbox for emails")
            logger.info("  2. Verify emails are syncing (press F9)")
            logger.info("  3. Test sending/receiving emails")
            return True
        else:
            logger.warning("⚠️  NAS MAIL HUB ACCOUNT NOT FOUND")
            logger.info("="*80)
            logger.info("")
            logger.info("Please add the NAS Mail Hub account:")
            logger.info("  Email: mlesn@<LOCAL_HOSTNAME>")
            logger.info("  Server: <NAS_PRIMARY_IP>")
            logger.info("  See: config/outlook/OUTLOOK_QUICK_SETUP.md")
            return False

    except ImportError:
        logger.error("❌ pywin32 not installed")
        logger.info("   Install with: pip install pywin32")
        return False
    except Exception as e:
        logger.error(f"❌ Error checking Outlook: {e}")
        logger.info("")
        logger.info("Please verify Outlook is installed and accessible")
        return False


def main():
    """Main function."""
    success = verify_outlook_setup()
    sys.exit(0 if success else 1)


if __name__ == "__main__":


    main()