#!/usr/bin/env python3
"""
Copy MariaDB dbAdmin credentials from ProtonPass to Azure Key Vault
Searches ProtonPass for MariaDB-related items and copies credentials
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
    logger = get_logger("CopyMariaDBCreds")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("CopyMariaDBCreds")

try:
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential, AzureCliCredential
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    logger.error("❌ Azure SDK not available")

def search_protonpass_for_mariadb():
    """Search ProtonPass for MariaDB-related items"""
    manager = UnifiedSecretsManager(project_root)

    logger.info("🔍 Searching ProtonPass for MariaDB credentials...")

    # Try to list items and search for MariaDB
    try:
        import subprocess
        import json

        # Try multiple paths for ProtonPass CLI
        import os

        # Check environment variable first
        protonpass_path = os.getenv("PROTONPASS_CLI_PATH")
        if protonpass_path and Path(protonpass_path).exists():
            logger.info(f"✅ Using ProtonPass CLI from PROTONPASS_CLI_PATH: {protonpass_path}")
        else:
            protonpass_paths = [
                Path(r"C:\Users\mlesn\AppData\Local\Programs\ProtonPass\pass-cli.exe"),
                Path(r"C:\Program Files\ProtonPass\pass-cli.exe"),
                Path(os.path.expanduser("~/.protonpass/pass-cli.exe")),
                Path(os.path.expanduser("~/AppData/Local/ProtonPass/pass-cli.exe")),
                Path(os.path.expanduser("~/AppData/Roaming/ProtonPass/pass-cli.exe")),
                "protonpass",  # In PATH
                "ppass",  # Alternative name
                "pass",  # Short name
            ]

            protonpass_path = None
            for path in protonpass_paths:
                if isinstance(path, str):
                    # Try as command in PATH
                    try:
                        result = subprocess.run(
                            [path, "--version"],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        if result.returncode == 0:
                            protonpass_path = path
                            break
                    except:
                        continue
                elif path.exists():
                    protonpass_path = str(path)
                    break

            if not protonpass_path:
                logger.error("❌ ProtonPass CLI not found")
                logger.info("💡 Please provide the path via PROTONPASS_CLI_PATH environment variable")
                logger.info("   Example: $env:PROTONPASS_CLI_PATH='C:\\path\\to\\pass-cli.exe'")
                return None

        logger.info(f"✅ Using ProtonPass CLI at: {protonpass_path}")

        # List all items (use --output json instead of --json)
        result = subprocess.run(
            [protonpass_path, "item", "list", "--output", "json"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            logger.error(f"❌ Failed to list ProtonPass items: {result.stderr}")
            return None

        items = json.loads(result.stdout) if result.stdout.strip() else []

        # Search for MariaDB-related items
        mariadb_items = []
        search_terms = ["mariadb", "mysql", "database", "dbadmin", "db admin"]

        for item in items:
            title = item.get("title", "").lower()
            username = item.get("username", "").lower()
            urls = [url.get("url", "").lower() for url in item.get("urls", [])]
            all_text = f"{title} {username} {' '.join(urls)}".lower()

            # Check if any search term matches
            if any(term in all_text for term in search_terms):
                mariadb_items.append(item)
                logger.info(f"✅ Found potential MariaDB item: {item.get('title', 'Untitled')}")

        if not mariadb_items:
            logger.warning("⚠️  No MariaDB-related items found in ProtonPass")
            logger.info("💡 Searching all items for 'dbadmin' or 'database'...")
            # Try broader search
            for item in items:
                title = item.get("title", "").lower()
                if "dbadmin" in title or "database" in title:
                    mariadb_items.append(item)
                    logger.info(f"✅ Found database item: {item.get('title', 'Untitled')}")

        return mariadb_items

    except Exception as e:
        logger.error(f"❌ Error searching ProtonPass: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_item_details(item_id: str, protonpass_path: str):
    """Get full details of a ProtonPass item"""
    try:
        import subprocess
        import json

        result = subprocess.run(
            [protonpass_path, "item", "get", item_id, "--json"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            return json.loads(result.stdout)
        return None
    except Exception as e:
        logger.error(f"Error getting item details: {e}")
        return None

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

        # Set username
        logger.info("📤 Copying dbadmin-username to Azure Key Vault...")
        client.set_secret("dbadmin-username", username)
        logger.info("✅ dbadmin-username copied successfully")

        # Set password
        logger.info("📤 Copying dbadmin-password to Azure Key Vault...")
        client.set_secret("dbadmin-password", password)
        logger.info("✅ dbadmin-password copied successfully")

        return True

    except Exception as e:
        logger.error(f"❌ Failed to copy to Azure Key Vault: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Copy MariaDB credentials from ProtonPass to Azure Key Vault")
    parser.add_argument("--protonpass-path", help="Path to ProtonPass CLI (pass-cli.exe)")
    args = parser.parse_args()

    # Set path if provided
    if args.protonpass_path:
        import os
        os.environ["PROTONPASS_CLI_PATH"] = args.protonpass_path
        logger.info(f"Using ProtonPass CLI path: {args.protonpass_path}")

    logger.info("🔍 Searching ProtonPass for MariaDB credentials...")

    # Search ProtonPass
    items = search_protonpass_for_mariadb()

    if not items:
        logger.error("❌ No MariaDB items found in ProtonPass")
        logger.info("💡 Please ensure MariaDB credentials exist in ProtonPass")
        return 1

    # Show found items
    logger.info(f"\n📋 Found {len(items)} MariaDB-related item(s):")
    for i, item in enumerate(items, 1):
        logger.info(f"   {i}. {item.get('title', 'Untitled')} (ID: {item.get('itemId', item.get('id', 'unknown'))})")

    # Find protonpass path again for get_item_details
    protonpass_paths = [
        Path(r"C:\Users\mlesn\AppData\Local\Programs\ProtonPass\pass-cli.exe"),
        Path(r"C:\Program Files\ProtonPass\pass-cli.exe"),
        "protonpass",
    ]

    protonpass_path = None
    for path in protonpass_paths:
        if isinstance(path, str):
            try:
                result = subprocess.run(
                    [path, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    protonpass_path = path
                    break
            except:
                continue
        elif path.exists():
            protonpass_path = str(path)
            break

    if not protonpass_path:
        logger.error("❌ Could not find ProtonPass CLI")
        return 1

    # Get details of first item (or let user choose)
    if len(items) == 1:
        item = items[0]
        item_id = item.get("itemId") or item.get("id")
        logger.info(f"\n📥 Getting details for: {item.get('title', 'Untitled')}")
    else:
        # Multiple items - use first one that looks most relevant
        logger.info(f"\n💡 Multiple items found. Using first item: {items[0].get('title', 'Untitled')}")
        item = items[0]
        item_id = item.get("itemId") or item.get("id")

    # Get full item details
    details = get_item_details(item_id, protonpass_path)
    if not details:
        logger.error("❌ Could not retrieve item details")
        return 1

    # Extract credentials
    username = details.get("username") or details.get("content", {}).get("username", "")
    password = details.get("password") or details.get("content", {}).get("password", "")

    if not username:
        # Try alternative paths
        content = details.get("content", {})
        if isinstance(content, dict):
            username = content.get("username", "")
            password = content.get("password", "")
        elif isinstance(content, list):
            for field in content:
                if field.get("fieldName") == "username":
                    username = field.get("value", "")
                elif field.get("fieldName") == "password":
                    password = field.get("value", "")

    if not username or not password:
        logger.error("❌ Could not extract username or password from item")
        logger.debug(f"Item structure: {details}")
        return 1

    logger.info(f"\n✅ Extracted credentials:")
    logger.info(f"   Username: {username}")
    logger.info(f"   Password: [REDACTED]")

    # Copy to Azure Key Vault
    logger.info(f"\n📤 Copying to Azure Key Vault...")
    if copy_to_azure_vault(username, password):
        logger.info("\n✅ Successfully copied MariaDB credentials to Azure Key Vault!")
        logger.info("   - dbadmin-username")
        logger.info("   - dbadmin-password")
        return 0
    else:
        logger.error("\n❌ Failed to copy credentials to Azure Key Vault")
        return 1

if __name__ == "__main__":

    sys.exit(main())