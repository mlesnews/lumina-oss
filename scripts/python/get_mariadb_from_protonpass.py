#!/usr/bin/env python3
"""
Get MariaDB credentials from ProtonPass and copy to Azure Key Vault
Tries multiple methods to access ProtonPass
"""
import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from unified_secrets_manager import UnifiedSecretsManager, SecretSource
    from lumina_logger import get_logger
    logger = get_logger("GetMariaDBFromProtonPass")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("GetMariaDBFromProtonPass")

def try_get_from_protonpass():
    """Try to get MariaDB credentials from ProtonPass"""
    manager = UnifiedSecretsManager(project_root)

    # Try different secret name patterns
    patterns = [
        "mariadb",
        "MariaDB",
        "dbadmin",
        "dbAdmin",
        "database",
        "Database",
        "DSM MariaDB",
        "NAS MariaDB"
    ]

    logger.info("🔍 Searching ProtonPass for MariaDB credentials...")

    for pattern in patterns:
        try:
            # Try to get as password
            password = manager.get_secret(f"{pattern}-password", source=SecretSource.PROTONPASS)
            username = manager.get_secret(f"{pattern}-username", source=SecretSource.PROTONPASS)

            if password:
                if not username:
                    # Try to get username from the same item
                    username = manager.get_secret(pattern, source=SecretSource.PROTONPASS)
                    if not username:
                        username = "dbadmin"  # Default

                logger.info(f"✅ Found credentials for pattern: {pattern}")
                return username, password
        except Exception as e:
            logger.debug(f"Pattern {pattern} failed: {e}")
            continue

    # Try direct item name search
    try:
        # Try common ProtonPass item names
        item_names = [
            "MariaDB",
            "MariaDB dbAdmin",
            "dbAdmin",
            "Database Admin",
            "DSM MariaDB",
            "NAS Database"
        ]

        for item_name in item_names:
            try:
                # Try to get the item
                result = manager.get_secret(item_name, source=SecretSource.PROTONPASS)
                if result:
                    logger.info(f"✅ Found item: {item_name}")
                    # The result might be the password, need to extract username separately
                    # For now, return what we found
                    return "dbadmin", result
            except:
                continue
    except Exception as e:
        logger.debug(f"Direct search failed: {e}")

    return None, None

def copy_to_azure_vault(username: str, password: str):
    """Copy credentials to Azure Key Vault"""
    try:
        from azure.keyvault.secrets import SecretClient
        from azure.identity import DefaultAzureCredential, AzureCliCredential

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

        logger.info("📤 Copying to Azure Key Vault...")
        client.set_secret("dbadmin-username", username)
        client.set_secret("dbadmin-password", password)
        logger.info("✅ Credentials copied successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        return False

def main():
    logger.info("🔍 Attempting to get MariaDB credentials from ProtonPass...")

    username, password = try_get_from_protonpass()

    if username and password:
        logger.info(f"✅ Found credentials from ProtonPass")
        logger.info(f"   Username: {username}")
        logger.info(f"   Password: [REDACTED]")

        if copy_to_azure_vault(username, password):
            logger.info("\n✅ Successfully copied to Azure Key Vault!")
            return 0
        else:
            return 1
    else:
        logger.warning("⚠️  Could not automatically retrieve from ProtonPass")
        logger.info("\n💡 Manual steps:")
        logger.info("   1. Open ProtonPass browser extension")
        logger.info("   2. Search for 'MariaDB' or 'dbAdmin'")
        logger.info("   3. Copy username and password")
        logger.info("   4. Run: python scripts/python/copy_mariadb_protonpass_to_vault.py --username <user> --password <pass>")
        return 1

if __name__ == "__main__":

    sys.exit(main())