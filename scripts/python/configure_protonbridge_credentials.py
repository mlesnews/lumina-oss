"""
Configure ProtonBridge Credentials
Helper script to find and configure ProtonMail credentials from secrets manager.

#JARVIS #LUMINA #PROTONBRIDGE #CONFIGURATION
"""

import sys
from pathlib import Path

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.unified_secrets_manager import UnifiedSecretsManager, SecretSource
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("ConfigureProtonBridge")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ConfigureProtonBridge")


def find_protonmail_credentials(project_root: Path):
    """Find ProtonMail credentials in secrets manager."""
    manager = UnifiedSecretsManager(project_root)

    # List all secrets
    all_secrets = manager.list_secrets()

    logger.info("="*80)
    logger.info("SEARCHING FOR PROTONMAIL CREDENTIALS")
    logger.info("="*80)

    # Search for ProtonMail-related secrets
    protonmail_secrets = []

    for source, secrets in all_secrets.items():
        logger.info(f"\n{source}:")
        for secret_name in secrets:
            # Check if secret name contains protonmail-related terms
            if any(term in secret_name.lower() for term in ["proton", "protonmail", "proton-bridge", "protonbridge"]):
                protonmail_secrets.append((source, secret_name))
                logger.info(f"  ✅ Found: {secret_name}")

    if not protonmail_secrets:
        logger.warning("\n⚠️  No ProtonMail credentials found with standard names")
        logger.info("\n💡 Possible secret names to check:")
        logger.info("   - protonmail-username")
        logger.info("   - protonmail-email")
        logger.info("   - protonmail-password")
        logger.info("   - protonmail-credentials")
        logger.info("   - proton-bridge-username")
        logger.info("   - proton-bridge-password")
        logger.info("\n📋 All available secrets:")
        for source, secrets in all_secrets.items():
            logger.info(f"\n{source}:")
            for secret_name in sorted(secrets):
                logger.info(f"  - {secret_name}")

    return protonmail_secrets


def test_protonbridge_connection(project_root: Path, username: str = None, password: str = None):
    """Test ProtonBridge connection with credentials."""
    try:
        from scripts.python.protonbridge_integration import ProtonBridgeIntegration

        bridge = ProtonBridgeIntegration(project_root)

        # If credentials provided, test connection
        if username and password:
            logger.info("Testing ProtonBridge connection...")
            if bridge.connect_imap():
                logger.info("✅ ProtonBridge IMAP connection successful!")
                bridge.disconnect()
                return True
            else:
                logger.error("❌ ProtonBridge IMAP connection failed")
                return False
        else:
            logger.info("Credentials not provided - testing with secrets manager...")
            if bridge.connect_imap():
                logger.info("✅ ProtonBridge IMAP connection successful!")
                bridge.disconnect()
                return True
            else:
                logger.warning("⚠️  Could not connect - credentials may need to be stored")
                return False

    except Exception as e:
        logger.error(f"❌ Error testing connection: {e}")
        return False


def main():
    try:
        """Main function."""
        import argparse

        parser = argparse.ArgumentParser(description="Configure ProtonBridge Credentials")
        parser.add_argument("--project-root", type=Path, default=Path(__file__).parent.parent.parent)
        parser.add_argument("--find", action="store_true", help="Find ProtonMail credentials in vault")
        parser.add_argument("--test", action="store_true", help="Test ProtonBridge connection")
        parser.add_argument("--username", type=str, help="ProtonMail username/email (for testing)")
        parser.add_argument("--password", type=str, help="ProtonMail password (for testing)")

        args = parser.parse_args()

        if args.find:
            find_protonmail_credentials(args.project_root)
        elif args.test:
            test_protonbridge_connection(args.project_root, args.username, args.password)
        else:
            # Do both
            secrets = find_protonmail_credentials(args.project_root)
            if secrets:
                logger.info("\n" + "="*80)
                logger.info("TESTING CONNECTION")
                logger.info("="*80)
                test_protonbridge_connection(args.project_root)
            else:
                logger.info("\n💡 To store credentials, use:")
                logger.info("   python scripts/python/unified_secrets_manager.py --set protonmail-username <email> --source azure_key_vault")
                logger.info("   python scripts/python/unified_secrets_manager.py --set protonmail-password <password> --source azure_key_vault")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()