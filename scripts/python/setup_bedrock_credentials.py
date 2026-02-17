#!/usr/bin/env python3
"""
Setup Bedrock Credentials - ProtonPass + Azure Vault Integration

Configures AWS Bedrock credentials using ProtonPass CLI and Azure Key Vault.
CRITICAL: +++++ MEMORY PRIORITY - Always use ProtonPass CLI and Azure Vault for ALL secrets.

Tags: #BEDROCK #AWS #CREDENTIALS #PROTONPASS #AZURE_VAULT #SETUP #+++++
@JARVIS @MARVIN @HK-47 @itsec
"""

import sys
from pathlib import Path
from typing import Optional

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from bedrock_credential_manager import BedrockCredentialManager
    BEDROCK_CREDENTIAL_MANAGER_AVAILABLE = True
except ImportError:
    BEDROCK_CREDENTIAL_MANAGER_AVAILABLE = False
    BedrockCredentialManager = None

logger = get_logger("SetupBedrockCredentials")


def setup_bedrock_credentials(
    access_key_id: Optional[str] = None,
    secret_access_key: Optional[str] = None,
    region: str = "us-east-1",
    session_token: Optional[str] = None,
    interactive: bool = False
) -> bool:
    """
    Setup AWS Bedrock credentials in ProtonPass + Azure Vault

    CRITICAL: +++++ MEMORY PRIORITY
    - ALWAYS stores in Azure Key Vault first
    - Then syncs to ProtonPass
    - NEVER stores in plain text files

    Args:
        access_key_id: AWS Access Key ID (if None, prompts interactively)
        secret_access_key: AWS Secret Access Key (if None, prompts interactively)
        region: AWS Region (default: us-east-1)
        session_token: Optional session token (for temporary credentials)
        interactive: If True, prompt for credentials if not provided

    Returns:
        True if setup successful
    """
    logger.info("=" * 80)
    logger.info("🔐 SETUP AWS BEDROCK CREDENTIALS")
    logger.info("CRITICAL: +++++ MEMORY PRIORITY - Using ProtonPass + Azure Vault")
    logger.info("=" * 80)
    logger.info("")

    if not BEDROCK_CREDENTIAL_MANAGER_AVAILABLE:
        logger.error("❌ Bedrock Credential Manager not available")
        return False

    manager = BedrockCredentialManager()

    # Get credentials if not provided
    if not access_key_id or not secret_access_key:
        if interactive:
            print("\n🔐 Enter AWS Bedrock Credentials")
            print("CRITICAL: These will be stored in Azure Key Vault + ProtonPass")
            print()

            if not access_key_id:
                access_key_id = input("AWS Access Key ID: ").strip()

            if not secret_access_key:
                secret_access_key = input("AWS Secret Access Key: ").strip()

            region_input = input(f"AWS Region [{region}]: ").strip()
            if region_input:
                region = region_input

            session_token_input = input("Session Token (optional, press Enter to skip): ").strip()
            if session_token_input:
                session_token = session_token_input
        else:
            logger.error("❌ Credentials not provided and interactive mode disabled")
            return False

    # Store credentials
    logger.info("📦 Storing credentials in Azure Key Vault + ProtonPass...")
    success = manager.store_credentials(
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        region=region,
        session_token=session_token
    )

    if not success:
        logger.error("❌ Failed to store credentials")
        return False

    # Test connection
    logger.info("")
    logger.info("🧪 Testing Bedrock connection...")
    if manager.test_connection():
        logger.info("✅ Bedrock connection successful!")
    else:
        logger.warning("⚠️  Credentials stored but connection test failed")
        logger.warning("   Verify credentials are correct and Bedrock is enabled in your AWS account")

    logger.info("")
    logger.info("=" * 80)
    logger.info("✅ SETUP COMPLETE")
    logger.info("=" * 80)
    logger.info("")
    logger.info("📋 Next Steps:")
    logger.info("   1. Credentials are stored in Azure Key Vault + ProtonPass")
    logger.info("   2. Use BedrockCredentialManager to retrieve credentials")
    logger.info("   3. Run: python scripts/python/bedrock_credential_manager.py --test")
    logger.info("")

    return True


def verify_setup() -> bool:
    """Verify Bedrock credentials are set up correctly"""
    logger.info("🔍 Verifying Bedrock credentials setup...")

    if not BEDROCK_CREDENTIAL_MANAGER_AVAILABLE:
        logger.error("❌ Bedrock Credential Manager not available")
        return False

    manager = BedrockCredentialManager()

    # Try to get credentials
    credentials = manager.get_credentials()
    if not credentials:
        logger.error("❌ Credentials not found in ProtonPass/Azure Vault")
        logger.info("   Run: python scripts/python/setup_bedrock_credentials.py --interactive")
        return False

    logger.info("✅ Credentials found in ProtonPass/Azure Vault")
    logger.info(f"   Region: {credentials.get('region', 'us-east-1')}")
    logger.info(f"   Access Key ID: {credentials['access_key_id'][:8]}***")

    # Test connection
    logger.info("")
    logger.info("🧪 Testing Bedrock connection...")
    if manager.test_connection():
        logger.info("✅ Bedrock connection successful!")
        return True
    else:
        logger.error("❌ Bedrock connection failed")
        return False


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Setup AWS Bedrock Credentials (ProtonPass + Azure Vault)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
CRITICAL: +++++ MEMORY PRIORITY
- ALWAYS uses ProtonPass CLI and Azure Key Vault for ALL secrets
- NEVER stores credentials in plain text files
- All secrets MUST be in Azure Key Vault first, then synced to ProtonPass

Examples:
  # Interactive setup
  python setup_bedrock_credentials.py --interactive

  # Verify existing setup
  python setup_bedrock_credentials.py --verify

  # Direct setup (not recommended - use interactive)
  python setup_bedrock_credentials.py --access-key-id AKIA... --secret-access-key ...
        """
    )

    parser.add_argument("--access-key-id", help="AWS Access Key ID")
    parser.add_argument("--secret-access-key", help="AWS Secret Access Key")
    parser.add_argument("--region", default="us-east-1", help="AWS Region (default: us-east-1)")
    parser.add_argument("--session-token", help="AWS Session Token (optional)")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode (prompt for credentials)")
    parser.add_argument("--verify", action="store_true", help="Verify existing setup")

    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("🔐 AWS BEDROCK CREDENTIALS SETUP")
    print("CRITICAL: +++++ MEMORY PRIORITY - ProtonPass + Azure Vault")
    print("=" * 80 + "\n")

    if args.verify:
        success = verify_setup()
        sys.exit(0 if success else 1)

    success = setup_bedrock_credentials(
        access_key_id=args.access_key_id,
        secret_access_key=args.secret_access_key,
        region=args.region,
        session_token=args.session_token,
        interactive=args.interactive or (not args.access_key_id and not args.secret_access_key)
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":


    main()