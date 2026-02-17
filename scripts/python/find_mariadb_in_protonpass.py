#!/usr/bin/env python3
"""
Find MariaDB credentials in ProtonPass and copy to Azure Key Vault
Uses existing ProtonPass credential finder
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
    from protonpass_credential_finder import ProtonPassCredentialFinder
    from lumina_logger import get_logger
    logger = get_logger("FindMariaDBProtonPass")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("FindMariaDBProtonPass")

try:
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential, AzureCliCredential
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    logger.error("❌ Azure SDK not available")

def copy_to_azure_vault(username: str, password: str):
    """Copy credentials to Azure Key Vault"""
    if not AZURE_AVAILABLE:
        logger.error("❌ Azure SDK not available")
        return False

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
        client.set_secret("dbadmin-username", username)
        logger.info("✅ dbadmin-username copied")
        client.set_secret("dbadmin-password", password)
        logger.info("✅ dbadmin-password copied")
        return True
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    logger.info("🔍 Searching ProtonPass for MariaDB credentials...")

    finder = ProtonPassCredentialFinder()

    # Search for MariaDB-related items
    search_terms = ["mariadb", "mysql", "database", "dbadmin", "db admin"]
    found_items = []

    for term in search_terms:
        logger.info(f"🔍 Searching for: {term}")
        items = finder.search_items(term)
        if items:
            found_items.extend(items)
            logger.info(f"✅ Found {len(items)} item(s) matching '{term}'")

    if not found_items:
        logger.warning("⚠️  No MariaDB items found")
        logger.info("💡 Listing all items to help find it...")
        all_items = finder.list_all_items()
        logger.info(f"📋 Total items in ProtonPass: {len(all_items)}")
        if all_items:
            logger.info("First 20 items:")
            for item in all_items[:20]:
                logger.info(f"   - {item}")
        return 1

    # Remove duplicates
    found_items = list(set(found_items))
    logger.info(f"\n📋 Found {len(found_items)} unique MariaDB-related item(s):")
    for item in found_items:
        logger.info(f"   - {item}")

    # Get credentials from first matching item
    item_name = found_items[0]
    logger.info(f"\n📥 Getting credentials from: {item_name}")

    fields = finder.get_item_fields(item_name)
    if not fields:
        logger.error("❌ Could not retrieve item fields")
        return 1

    # Extract username and password
    username = fields.get("username") or fields.get("user") or ""
    password = fields.get("password") or fields.get("pass") or ""

    # Try alternative field names
    if not username or not password:
        for key, value in fields.items():
            key_lower = key.lower()
            if "user" in key_lower and not username:
                username = value
            elif "pass" in key_lower and not password:
                password = value

    if not username or not password:
        logger.error("❌ Could not extract username or password")
        logger.debug(f"Available fields: {list(fields.keys())}")
        return 1

    logger.info(f"✅ Extracted credentials:")
    logger.info(f"   Username: {username}")
    logger.info(f"   Password: [REDACTED]")

    # Copy to Azure Key Vault
    if copy_to_azure_vault(username, password):
        logger.info("\n✅ Successfully copied MariaDB credentials to Azure Key Vault!")
        return 0
    else:
        return 1

if __name__ == "__main__":

    sys.exit(main())