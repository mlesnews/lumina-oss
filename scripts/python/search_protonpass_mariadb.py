#!/usr/bin/env python3
"""
Search ProtonPass for MariaDB credentials using Unified Secrets Manager
"""
import sys
import os
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
    logger = get_logger("SearchProtonPassMariaDB")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("SearchProtonPassMariaDB")

def search_protonpass_items():
    """Search ProtonPass for all items and filter for MariaDB"""
    manager = UnifiedSecretsManager(project_root)

    # Try to use ProtonPass directly
    if not manager.protonpass_available:
        logger.warning("⚠️  ProtonPass CLI not available via UnifiedSecretsManager")
        logger.info("💡 Trying direct ProtonPass CLI access...")

        # Try direct access
        import subprocess
        protonpass_paths = [
            r"C:\Users\mlesn\AppData\Local\Programs\ProtonPass\pass-cli.exe",
            r"C:\Program Files\ProtonPass\pass-cli.exe",
            "protonpass"
        ]

        for path in protonpass_paths:
            try:
                if isinstance(path, str) and not os.path.exists(path) and path != "protonpass":
                    continue

                cmd = [path] if path != "protonpass" else ["protonpass"]
                result = subprocess.run(
                    cmd + ["--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    logger.info(f"✅ Found ProtonPass CLI at: {path}")
                    # Try to list items
                    list_result = subprocess.run(
                        cmd + ["item", "list", "--json"],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if list_result.returncode == 0:
                        import json
                        items = json.loads(list_result.stdout) if list_result.stdout.strip() else []
                        logger.info(f"📋 Found {len(items)} items in ProtonPass")

                        # Search for MariaDB
                        mariadb_items = []
                        search_terms = ["mariadb", "mysql", "database", "dbadmin", "db admin", "dsm"]

                        for item in items:
                            title = str(item.get("title", "")).lower()
                            username = str(item.get("username", "")).lower()
                            urls = [str(url.get("url", "")).lower() for url in item.get("urls", [])]
                            all_text = f"{title} {username} {' '.join(urls)}".lower()

                            if any(term in all_text for term in search_terms):
                                mariadb_items.append(item)
                                logger.info(f"✅ Found: {item.get('title', 'Untitled')}")

                        return mariadb_items, cmd[0] if isinstance(cmd, list) else cmd
                    else:
                        logger.warning(f"⚠️  Could not list items: {list_result.stderr}")
            except Exception as e:
                logger.debug(f"Tried {path}: {e}")
                continue

        logger.error("❌ Could not access ProtonPass CLI")
        return None, None

    # If ProtonPass is available via manager, try to use it
    logger.info("🔍 Searching ProtonPass via Unified Secrets Manager...")
    # The manager doesn't have a direct search method, so we'll need to try item names
    return None, None

def get_item_credentials(item_id: str, protonpass_cmd: str):
    """Get credentials from a ProtonPass item"""
    import subprocess
    import json

    try:
        cmd = [protonpass_cmd] if protonpass_cmd != "protonpass" else ["protonpass"]
        result = subprocess.run(
            cmd + ["item", "get", item_id, "--json"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            logger.error(f"❌ Failed to get item: {result.stderr}")
            return None
    except Exception as e:
        logger.error(f"❌ Error getting item: {e}")
        return None

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

        logger.info("📤 Copying credentials to Azure Key Vault...")

        # Set username
        client.set_secret("dbadmin-username", username)
        logger.info("✅ dbadmin-username copied to Azure Key Vault")

        # Set password
        client.set_secret("dbadmin-password", password)
        logger.info("✅ dbadmin-password copied to Azure Key Vault")

        return True
    except Exception as e:
        logger.error(f"❌ Failed to copy to Azure Key Vault: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    try:
        logger.info("🔍 Searching ProtonPass for MariaDB credentials...")

        items, protonpass_cmd = search_protonpass_items()

        if not items:
            logger.error("❌ No MariaDB items found in ProtonPass")
            return 1

        logger.info(f"\n📋 Found {len(items)} MariaDB-related item(s):")
        for i, item in enumerate(items, 1):
            logger.info(f"   {i}. {item.get('title', 'Untitled')} (ID: {item.get('itemId', item.get('id', 'unknown'))})")

        # Use first item
        item = items[0]
        item_id = item.get("itemId") or item.get("id")

        logger.info(f"\n📥 Getting credentials from: {item.get('title', 'Untitled')}")
        details = get_item_credentials(item_id, protonpass_cmd)

        if not details:
            logger.error("❌ Could not retrieve item details")
            return 1

        # Extract credentials - try multiple paths
        username = (details.get("username") or 
                    details.get("content", {}).get("username", "") if isinstance(details.get("content"), dict) else "" or
                    details.get("fields", [{}])[0].get("value", "") if details.get("fields") else "")

        password = (details.get("password") or 
                    details.get("content", {}).get("password", "") if isinstance(details.get("content"), dict) else "" or
                    details.get("fields", [{}])[1].get("value", "") if details.get("fields") and len(details.get("fields", [])) > 1 else "")

        # Try alternative extraction
        if not username or not password:
            content = details.get("content", {})
            if isinstance(content, list):
                for field in content:
                    field_name = field.get("fieldName", "").lower()
                    field_value = field.get("value", "")
                    if "user" in field_name:
                        username = field_value
                    elif "pass" in field_name:
                        password = field_value

        if not username or not password:
            logger.error("❌ Could not extract username or password")
            logger.debug(f"Item structure: {json.dumps(details, indent=2)}")
            return 1

        logger.info(f"\n✅ Extracted credentials:")
        logger.info(f"   Username: {username}")
        logger.info(f"   Password: [REDACTED]")

        # Copy to Azure Key Vault
        if copy_to_azure_vault(username, password):
            logger.info("\n✅ Successfully copied MariaDB credentials to Azure Key Vault!")
            return 0
        else:
            logger.error("\n❌ Failed to copy credentials")
            return 1

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    import json

    sys.exit(main())