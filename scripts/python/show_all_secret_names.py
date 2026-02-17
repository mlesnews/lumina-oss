#!/usr/bin/env python3
"""
Show All Azure Key Vault Secret Names
Lists all secret names (not values) to help identify phone number secrets

Tags: #AZURE_KEY_VAULT #LIST #SECRETS
"""

import sys
from pathlib import Path

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential, AzureCliCredential
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    print("❌ Azure SDK not available")
    sys.exit(1)


def main():
    """List all secret names"""
    print("="*80)
    print("📋 ALL AZURE KEY VAULT SECRET NAMES")
    print("="*80)
    print()

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

        # List all secrets (names only)
        secrets = []
        for secret_properties in client.list_properties_of_secrets():
            secrets.append(secret_properties.name)

        secrets = sorted(secrets)

        print(f"📊 Total secrets: {len(secrets)}\n")
        print("All Secret Names:")
        print("-" * 80)

        for i, secret_name in enumerate(secrets, 1):
            print(f"{i:3d}. {secret_name}")

        print()
        print("="*80)
        print("💡 Please identify which secrets contain phone numbers")
        print("   and share the exact secret names so I can update the system.")
        print("="*80)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":


    main()