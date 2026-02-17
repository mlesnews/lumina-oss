"""
Open Outlook Account Settings Dialog
Attempts to open Outlook and navigate to Account Settings.

#JARVIS #LUMINA #OUTLOOK #AUTOMATION
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("OpenOutlookAccountSettings")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("OpenOutlookAccountSettings")


def open_outlook_account_settings():
    """Open Outlook and attempt to navigate to Account Settings."""
    logger.info("="*80)
    logger.info("OPENING OUTLOOK ACCOUNT SETTINGS")
    logger.info("="*80)
    logger.info("")

    try:
        import win32com.client

        logger.info("Connecting to Outlook...")
        outlook = win32com.client.Dispatch("Outlook.Application")
        logger.info("✅ Outlook connected")

        # Get namespace
        namespace = outlook.GetNamespace("MAPI")

        # Try to open Account Settings
        logger.info("")
        logger.info("Attempting to open Account Settings...")
        logger.info("")
        logger.info("NOTE: Outlook COM API cannot directly open Account Settings dialog.")
        logger.info("However, Outlook is now open and ready.")
        logger.info("")
        logger.info("Please manually:")
        logger.info("  1. In Outlook, go to: File → Account Settings → Account Settings")
        logger.info("  2. Click 'New...'")
        logger.info("  3. Follow the setup guide: config/outlook/OUTLOOK_QUICK_SETUP.md")
        logger.info("")

        # Show current accounts
        accounts = namespace.Accounts
        logger.info("Current Outlook Accounts:")
        logger.info("-" * 80)

        if accounts.Count == 0:
            logger.info("  (No accounts configured)")
        else:
            for i in range(accounts.Count):
                account = accounts.Item(i + 1)
                logger.info(f"  [{i+1}] {account.DisplayName} ({account.SmtpAddress})")

        logger.info("")
        logger.info("✅ Outlook is ready for account configuration")
        logger.info("")

        return True

    except ImportError:
        logger.error("❌ pywin32 not installed")
        logger.info("   Install with: pip install pywin32")
        return False
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        logger.info("")
        logger.info("Please open Outlook manually and follow:")
        logger.info("  config/outlook/OUTLOOK_QUICK_SETUP.md")
        return False


def main():
    """Main function."""
    success = open_outlook_account_settings()
    sys.exit(0 if success else 1)


if __name__ == "__main__":


    main()