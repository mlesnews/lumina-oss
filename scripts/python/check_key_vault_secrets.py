#!/usr/bin/env python3
"""
Check Azure Key Vault for Speech Secrets

Lists all secrets in Key Vault to find the correct name for Azure Speech key.
"""

import sys
import os
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from azure_service_bus_integration import AzureKeyVaultClient
except ImportError:
    from scripts.python.azure_service_bus_integration import AzureKeyVaultClient

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CheckKeyVaultSecrets")


def main():
    """List all secrets in Key Vault"""
    vault_url = os.getenv("AZURE_KEY_VAULT_URL", "https://jarvis-lumina.vault.azure.net/")

    print(f"\n🔍 Checking Azure Key Vault: {vault_url}\n")

    try:
        vault_client = AzureKeyVaultClient(vault_url=vault_url)

        # List all secrets
        print("📋 Listing all secrets in Key Vault...\n")
        secrets = vault_client.list_secrets()

        if secrets:
            print(f"✅ Found {len(secrets)} secrets:\n")
            for secret_name in sorted(secrets):
                print(f"   - {secret_name}")

                # Check if it might be speech-related
                if "speech" in secret_name.lower() or "azure" in secret_name.lower():
                    try:
                        value = vault_client.get_secret(secret_name)
                        print(f"     ✅ Value: {value[:20]}..." if len(value) > 20 else f"     ✅ Value: {value}")
                    except:
                        print(f"     ⚠️  Could not retrieve value")
        else:
            print("⚠️  No secrets found in Key Vault")

        # Try common speech secret names
        print("\n🔍 Checking common Azure Speech secret names...\n")
        common_names = [
            "azure-speech-key",
            "azure-speech-api-key",
            "azure-speech-subscription-key",
            "speech-key",
            "speech-api-key",
            "azure-cognitive-services-speech-key"
        ]

        for name in common_names:
            try:
                value = vault_client.get_secret(name)
                print(f"✅ Found: {name}")
                print(f"   Value: {value[:20]}..." if len(value) > 20 else f"   Value: {value}")
            except Exception as e:
                if "SecretNotFound" in str(e):
                    print(f"❌ Not found: {name}")
                else:
                    print(f"⚠️  Error checking {name}: {e}")

    except Exception as e:
        print(f"❌ Error accessing Key Vault: {e}")
        print("\n💡 Make sure you're authenticated to Azure:")
        print("   az login")


if __name__ == "__main__":



    main()