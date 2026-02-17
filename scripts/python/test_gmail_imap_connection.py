"""
Test Gmail IMAP Connection with Azure Key Vault Credentials
Quick test to verify Gmail IMAP connection using credentials from Azure Key Vault.

#JARVIS #LUMINA #GMAIL #IMAP #AZURE_KEY_VAULT #TEST
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import imaplib
from typing import Optional, Tuple

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("TestGmailIMAP")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("TestGmailIMAP")

try:
    from scripts.python.unified_secrets_manager import UnifiedSecretsManager, SecretSource
    SECRETS_AVAILABLE = True
except ImportError:
    SECRETS_AVAILABLE = False
    logger.warning("⚠️  Unified Secrets Manager not available")


def test_gmail_imap_connection(project_root: Path) -> Tuple[bool, str]:
    """
    Test Gmail IMAP connection using Azure Key Vault credentials.

    Args:
        project_root: Project root directory

    Returns:
        Tuple of (success, message)
    """
    logger.info("="*80)
    logger.info("TESTING GMAIL IMAP CONNECTION")
    logger.info("="*80)
    logger.info("")

    if not SECRETS_AVAILABLE:
        return False, "Secrets manager not available"

    try:
        # Initialize secrets manager
        secrets_manager = UnifiedSecretsManager(
            project_root,
            prefer_source=SecretSource.AZURE_KEY_VAULT
        )
        logger.info("✅ Secrets manager initialized")

        # Get Gmail credentials from Azure Key Vault
        logger.info("Retrieving Gmail credentials from Azure Key Vault...")
        try:
            gmail_email = secrets_manager.get_secret("login-account-gmail-ceo-gmail-email")
            gmail_password = secrets_manager.get_secret("login-account-gmail-ceo-gmail-app-password")
            logger.info(f"✅ Gmail credentials retrieved: {gmail_email}")
        except Exception as e:
            logger.warning(f"⚠️  Primary secret names not found, trying fallback...")
            try:
                gmail_email = secrets_manager.get_secret("gmail-email")
                gmail_password = secrets_manager.get_secret("gmail-app-password")
                logger.info(f"✅ Gmail credentials retrieved (fallback): {gmail_email}")
            except Exception as e2:
                return False, f"Failed to get Gmail credentials: {e2}"

        # Connect to Gmail IMAP
        logger.info("")
        logger.info("Connecting to Gmail IMAP...")
        logger.info("  Server: imap.gmail.com")
        logger.info("  Port: 993")
        logger.info("  Encryption: SSL")

        imap_server = "imap.gmail.com"
        imap_port = 993

        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        mail.login(gmail_email, gmail_password)
        logger.info("✅ Successfully connected to Gmail IMAP")

        # Select INBOX
        status, data = mail.select("INBOX")
        if status == "OK":
            logger.info("✅ INBOX selected")
            # Get message count (use RECENT to avoid large result sets)
            try:
                status, messages = mail.search(None, "RECENT")
                if status == "OK":
                    email_ids = messages[0].split()
                    logger.info(f"✅ Found {len(email_ids)} recent emails in INBOX")
                else:
                    logger.info("✅ INBOX accessible (too many emails to count)")
            except Exception as e:
                # If search fails due to large inbox, that's OK - connection works
                logger.info("✅ INBOX accessible (large inbox detected)")
                logger.debug(f"   Search note: {e}")

        # Close connection
        mail.close()
        mail.logout()

        logger.info("")
        logger.info("="*80)
        logger.info("✅ GMAIL IMAP CONNECTION TEST SUCCESSFUL")
        logger.info("="*80)

        return True, "Connection successful"

    except imaplib.IMAP4.error as e:
        error_msg = f"IMAP error: {e}"
        logger.error(f"❌ {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = f"Connection failed: {e}"
        logger.error(f"❌ {error_msg}")
        return False, error_msg


def main():
    try:
        """Main function."""
        import argparse

        parser = argparse.ArgumentParser(
            description="Test Gmail IMAP Connection with Azure Key Vault Credentials"
        )

        parser.add_argument(
            "--project-root",
            type=Path,
            default=Path(__file__).parent.parent.parent,
            help="Project root directory"
        )

        args = parser.parse_args()

        success, message = test_gmail_imap_connection(args.project_root)

        if success:
            logger.info("")
            logger.info("✅ Gmail IMAP is ready for email import!")
            logger.info("   You can now run: python scripts/python/import_emails_to_nas_hub.py")
        else:
            logger.error("")
            logger.error("❌ Gmail IMAP connection test failed")
            logger.error(f"   Error: {message}")
            logger.error("")
            logger.error("💡 Troubleshooting:")
            logger.error("   1. Verify Gmail credentials are in Azure Key Vault")
            logger.error("   2. Check secret names: login-account-gmail-ceo-gmail-email")
            logger.error("   3. Verify Gmail App Password is correct (16 characters)")
            logger.error("   4. Check Gmail IMAP is enabled in account settings")

        sys.exit(0 if success else 1)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()