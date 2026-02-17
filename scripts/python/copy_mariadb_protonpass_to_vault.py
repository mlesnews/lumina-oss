#!/usr/bin/env python3
"""
Copy MariaDB credentials from ProtonPass to Azure Key Vault
This script helps you copy dbAdmin credentials from ProtonPass to Azure Key Vault

Usage:
1. Open ProtonPass browser extension
2. Search for "MariaDB" or "dbAdmin"
3. Copy the username and password
4. Run this script with the credentials
"""
import sys
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential, AzureCliCredential
    from lumina_logger import get_logger
    logger = get_logger("CopyMariaDBProtonPass")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("CopyMariaDBProtonPass")

def copy_to_vault(username: str, password: str):
    """Copy credentials to Azure Key Vault"""
    try:
        vault_url = "https://jarvis-lumina.vault.azure.net/"

        try:
            credential = AzureCliCredential()
            client = SecretClient(vault_url=vault_url, credential=credential)
        except:
            credential = DefaultAzureCredential(
                exclude_interactive_browser_credential=False,
                exclude_shared_token_cache_credential=False
            )
            client = SecretClient(vault_url=vault_url, credential=credential)

        logger.info("📤 Copying credentials to Azure Key Vault...")

        # Set username
        client.set_secret("dbadmin-username", username)
        logger.info("✅ dbadmin-username copied to Azure Key Vault")

        # Set password
        client.set_secret("dbadmin-password", password)
        logger.info("✅ dbadmin-password copied to Azure Key Vault")

        logger.info("\n✅ Successfully copied MariaDB credentials to Azure Key Vault!")
        logger.info("   - dbadmin-username")
        logger.info("   - dbadmin-password")

        return True
    except Exception as e:
        logger.error(f"❌ Failed to copy to Azure Key Vault: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Copy MariaDB dbAdmin credentials from ProtonPass to Azure Key Vault",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # With credentials as arguments
  python copy_mariadb_protonpass_to_vault.py --username dbadmin --password "your_password"

  # Interactive mode (will prompt)
  python copy_mariadb_protonpass_to_vault.py
        """
    )
    parser.add_argument("--username", help="dbAdmin username from ProtonPass")
    parser.add_argument("--password", help="dbAdmin password from ProtonPass")

    args = parser.parse_args()

    username = args.username
    password = args.password

    # If not provided, show instructions
    if not username or not password:
        logger.info("=" * 70)
        logger.info("📋 COPY MARIADB CREDENTIALS FROM PROTONPASS TO AZURE VAULT")
        logger.info("=" * 70)
        logger.info("")
        logger.info("Instructions:")
        logger.info("1. Open ProtonPass browser extension")
        logger.info("2. Search for 'MariaDB' or 'dbAdmin'")
        logger.info("3. Copy the username and password")
        logger.info("4. Run this script with:")
        logger.info("   python copy_mariadb_protonpass_to_vault.py --username <user> --password <pass>")
        logger.info("")

        if not username:
            username = input("Enter dbAdmin username from ProtonPass: ").strip()
        if not password:
            import getpass
            password = getpass.getpass("Enter dbAdmin password from ProtonPass: ").strip()

    if not username or not password:
        logger.error("❌ Username and password are required")
        return 1

    logger.info(f"\n📤 Copying credentials to Azure Key Vault...")
    logger.info(f"   Username: {username}")
    logger.info(f"   Password: [REDACTED]")

    if copy_to_vault(username, password):
        logger.info("\n✅ Done! MariaDB MCP server can now use these credentials.")
        return 0
    else:
        return 1

if __name__ == "__main__":

    sys.exit(main())