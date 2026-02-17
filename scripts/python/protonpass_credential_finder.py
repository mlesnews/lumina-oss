#!/usr/bin/env python3
"""
ProtonPass Credential Finder
Searches ProtonPass CLI for specific credentials (like Plaid)

Tags: #PROTONPASS #CREDENTIALS #SEARCH
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    from protonpass_auto_login import main as auto_login
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    auto_login = None

logger = get_logger("ProtonPassCredentialFinder")

PROTONPASS_CLI = Path(r"C:\Users\mlesn\AppData\Local\Programs\ProtonPass\pass-cli.exe")


class ProtonPassCredentialFinder:
    """Find credentials in ProtonPass CLI"""

    def __init__(self):
        """Initialize finder"""
        self.authenticated = False
        logger.info("✅ ProtonPass Credential Finder initialized")

    def ensure_authenticated(self) -> bool:
        """Ensure ProtonPass is authenticated"""
        if self.authenticated:
            return True

        if auto_login:
            logger.info("🔐 Authenticating ProtonPass CLI...")
            result = auto_login()
            if result:
                self.authenticated = True
            return result
        return False

    def list_all_items(self) -> List[str]:
        """List all items in ProtonPass"""
        if not PROTONPASS_CLI.exists():
            logger.warning("⚠️  ProtonPass CLI not found")
            return []

        self.ensure_authenticated()

        items = []
        try:
            result = subprocess.run(
                [str(PROTONPASS_CLI), "item", "list"],
                capture_output=True,
                text=True,
                timeout=15
            )

            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    lines = output.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('Error') and 'needs extra password' not in line.lower():
                            items.append(line)
        except Exception as e:
            logger.debug(f"Error listing items: {e}")

        return items

    def search_items(self, query: str) -> List[str]:
        """Search for items matching query"""
        all_items = self.list_all_items()
        matching = [item for item in all_items if query.lower() in item.lower()]
        return matching

    def get_item_fields(self, item_name: str) -> Dict[str, Any]:
        """Get all fields from a ProtonPass item"""
        if not PROTONPASS_CLI.exists():
            return {}

        self.ensure_authenticated()

        fields = {}

        try:
            # Try JSON format first
            result = subprocess.run(
                [str(PROTONPASS_CLI), "item", "get", item_name, "--format", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout.strip())
                    # Extract fields
                    item_fields = data.get("fields", {})
                    # Also check top-level
                    for key in ["client_id", "secret", "password", "username", "url", 
                               "publishable_key", "secret_key", "api_key"]:
                        if key in data:
                            fields[key] = data[key]
                    # Add all fields
                    fields.update(item_fields)
                    return fields
                except json.JSONDecodeError:
                    pass

            # Try individual field retrieval - expanded list for Stripe, Plaid, and general API keys
            field_names = [
                # Plaid fields
                "client_id", "Client ID", "client-id", "secret", "Secret", "api_secret", "API Secret",
                # Stripe fields
                "publishable_key", "publishable-key", "Publishable Key", "secret_key", "secret-key", "Secret Key",
                "api_key", "api-key", "API Key", "pk_live", "pk_test", "sk_live", "sk_test",
                # General
                "password", "Password", "username", "Username"
            ]
            for field_name in field_names:
                result = subprocess.run(
                    [str(PROTONPASS_CLI), "item", "get", item_name, "--field", field_name],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    value = result.stdout.strip()
                    if value and not value.startswith("Error"):
                        fields[field_name.lower().replace(" ", "_").replace("-", "_")] = value

        except Exception as e:
            logger.debug(f"Error getting item fields: {e}")

        return fields

    def find_stripe_credentials(self) -> Optional[Dict[str, Any]]:
        """Find Stripe credentials in ProtonPass"""
        logger.info("🔍 Searching ProtonPass for Stripe credentials...")

        # Search for Stripe-related items
        stripe_items = self.search_items("stripe")

        if not stripe_items:
            logger.info("⚠️  No Stripe-related items found in ProtonPass")
            return None

        logger.info(f"📋 Found {len(stripe_items)} Stripe-related items: {', '.join(stripe_items)}")

        # Check each item for credentials
        for item_name in stripe_items:
            fields = self.get_item_fields(item_name)

            # Stripe uses publishable_key and secret_key (or api_key)
            publishable_key = (fields.get("publishable_key") or 
                             fields.get("publishable-key") or
                             fields.get("publishablekey") or
                             fields.get("Publishable Key") or
                             fields.get("pk_live") or
                             fields.get("pk_test"))

            secret_key = (fields.get("secret_key") or 
                         fields.get("secret-key") or
                         fields.get("secretkey") or
                         fields.get("Secret Key") or
                         fields.get("api_key") or
                         fields.get("api-key") or
                         fields.get("apikey") or
                         fields.get("sk_live") or
                         fields.get("sk_test") or
                         fields.get("password"))  # Sometimes API keys are in password field

            if publishable_key and secret_key:
                logger.info(f"✅ Found Stripe credentials in: {item_name}")
                return {
                    "account_name": item_name,
                    "publishable_key": publishable_key,
                    "secret_key": secret_key,
                    "environment": "live" if "live" in publishable_key.lower() or "live" in secret_key.lower() else "test",
                    "all_fields": fields
                }

        logger.warning("⚠️  Stripe credentials not found in any items")
        return None

    def find_plaid_credentials(self) -> Optional[Dict[str, Any]]:
        """Find Plaid credentials in ProtonPass"""
        logger.info("🔍 Searching ProtonPass for Plaid credentials...")

        # Search for Plaid-related items
        plaid_items = self.search_items("plaid")

        if not plaid_items:
            logger.info("⚠️  No Plaid-related items found in ProtonPass")
            return None

        logger.info(f"📋 Found {len(plaid_items)} Plaid-related items: {', '.join(plaid_items)}")

        # Check each item for credentials
        for item_name in plaid_items:
            fields = self.get_item_fields(item_name)

            # Look for client_id and secret in various formats
            client_id = (fields.get("client_id") or 
                        fields.get("clientid") or
                        fields.get("client-id"))

            secret = (fields.get("secret") or 
                     fields.get("api_secret") or
                     fields.get("apisecret") or
                     fields.get("api-secret") or
                     fields.get("password"))  # Sometimes API keys are in password field

            if client_id and secret:
                logger.info(f"✅ Found Plaid credentials in: {item_name}")
                return {
                    "account_name": item_name,
                    "client_id": client_id,
                    "secret": secret,
                    "environment": fields.get("environment") or "sandbox",
                    "all_fields": fields
                }

        logger.warning("⚠️  Plaid credentials not found in any items")
        return None


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Find credentials in ProtonPass")
    parser.add_argument("--search", type=str, help="Search for items")
    parser.add_argument("--list", action="store_true", help="List all items")
    parser.add_argument("--find-stripe", action="store_true", help="Find Stripe credentials")
    parser.add_argument("--find-plaid", action="store_true", help="Find Plaid credentials")
    parser.add_argument("--item", type=str, help="Get item details")

    args = parser.parse_args()

    finder = ProtonPassCredentialFinder()

    if args.list:
        items = finder.list_all_items()
        print(f"\n📋 ProtonPass Items ({len(items)}):")
        for item in items:
            print(f"   • {item}")

    elif args.search:
        items = finder.search_items(args.search)
        print(f"\n🔍 Search results for '{args.search}' ({len(items)}):")
        for item in items:
            print(f"   • {item}")

    elif args.find_stripe:
        creds = finder.find_stripe_credentials()
        if creds:
            print("\n✅ Stripe Credentials Found:")
            print(f"   Account: {creds['account_name']}")
            print(f"   Publishable Key: {creds['publishable_key'][:20]}...")
            print(f"   Secret Key: {'*' * len(creds['secret_key'])}")
            print(f"   Environment: {creds['environment']}")
        else:
            print("\n❌ Stripe credentials not found")
            print("\n💡 To add Stripe credentials to ProtonPass:")
            print("   1. Open ProtonPass app")
            print("   2. Create new item named 'Stripe' or 'Stripe API'")
            print("   3. Add fields: publishable_key, secret_key")
            print("   4. Run this script again")

    elif args.find_plaid:
        creds = finder.find_plaid_credentials()
        if creds:
            print("\n✅ Plaid Credentials Found:")
            print(f"   Account: {creds['account_name']}")
            print(f"   Client ID: {creds['client_id']}")
            print(f"   Secret: {'*' * len(creds['secret'])}")
            print(f"   Environment: {creds['environment']}")
        else:
            print("\n❌ Plaid credentials not found")
            print("\n💡 To add Plaid credentials to ProtonPass:")
            print("   1. Open ProtonPass app")
            print("   2. Create new item named 'Plaid' or 'Plaid API'")
            print("   3. Add fields: client_id, secret")
            print("   4. Run this script again")

    elif args.item:
        fields = finder.get_item_fields(args.item)
        print(f"\n📊 Item: {args.item}")
        print(f"   Fields: {len(fields)}")
        for key, value in fields.items():
            if 'secret' in key.lower() or 'password' in key.lower():
                print(f"   {key}: {'*' * len(str(value))}")
            else:
                print(f"   {key}: {value}")

    else:
        parser.print_help()


if __name__ == "__main__":


    main()