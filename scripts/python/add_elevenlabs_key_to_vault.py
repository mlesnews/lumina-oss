#!/usr/bin/env python3
"""
Add ElevenLabs API Key to Azure Key Vault

This script helps you add your ElevenLabs API key (generated from elevenlabs.ai)
to Azure Key Vault so JARVIS can use it automatically.
"""

import sys
import os
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from azure_service_bus_integration import AzureKeyVaultClient
    KEY_VAULT_AVAILABLE = True
except ImportError:
    KEY_VAULT_AVAILABLE = False
    print("❌ Azure Key Vault SDK not available")

def main():
    """Add ElevenLabs API key to Key Vault"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Add ElevenLabs API key to Azure Key Vault"
    )
    parser.add_argument('--api-key', type=str, help='ElevenLabs API key (or will prompt)')
    parser.add_argument('--vault-url', type=str, 
                       default=os.getenv('AZURE_KEY_VAULT_URL', 'https://jarvis-lumina.vault.azure.net/'),
                       help='Azure Key Vault URL')
    parser.add_argument('--list-secrets', action='store_true', 
                       help='List all secrets in Key Vault')
    parser.add_argument('--check', action='store_true',
                       help='Check if elevenlabs-api-key exists')

    args = parser.parse_args()

    if not KEY_VAULT_AVAILABLE:
        print("❌ Azure Key Vault SDK not available")
        print("   Install: pip install azure-keyvault-secrets azure-identity")
        return 1

    try:
        vault_client = AzureKeyVaultClient(vault_url=args.vault_url)

        # List all secrets
        if args.list_secrets:
            print("\n📋 Secrets in Key Vault:")
            print("="*60)
            try:
                secrets = vault_client.list_secrets()
                if secrets:
                    for secret in secrets:
                        print(f"  - {secret}")
                else:
                    print("  (no secrets found)")
            except Exception as e:
                print(f"❌ Error listing secrets: {e}")
            return 0

        # Check if key exists
        if args.check:
            print("\n🔍 Checking for elevenlabs-api-key...")
            try:
                key = vault_client.get_secret("elevenlabs-api-key")
                print("✅ elevenlabs-api-key found in Key Vault")
                print(f"   Key length: {len(key)} characters")
                return 0
            except Exception as e:
                print(f"❌ elevenlabs-api-key not found: {e}")
                print("\n💡 To add it, run:")
                print("   python scripts/python/add_elevenlabs_key_to_vault.py --api-key YOUR_KEY")
                return 1

        # Get API key
        api_key = args.api_key
        if not api_key:
            print("\n🔑 ElevenLabs API Key Setup")
            print("="*60)
            print("\nPlease provide your ElevenLabs API key.")
            print("You can get it from: https://elevenlabs.io/app/settings/api-keys")
            print()
            api_key = input("Enter your ElevenLabs API key: ").strip()

            if not api_key:
                print("❌ No API key provided")
                return 1

        # Add to Key Vault
        print(f"\n🔐 Adding API key to Key Vault: {args.vault_url}")
        print("   Secret name: elevenlabs-api-key")

        success = vault_client.set_secret("elevenlabs-api-key", api_key)

        if success:
            print("✅ API key added to Key Vault successfully!")
            print("\n🎉 JARVIS can now use ElevenLabs TTS automatically!")
            print("\n💡 Test it:")
            print("   python scripts/python/jarvis_elevenlabs_integration.py --text 'Hello, this is JARVIS'")
            return 0
        else:
            print("❌ Failed to add API key to Key Vault")
            return 1

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":


    sys.exit(main())