#!/usr/bin/env python3
"""
Store All MCP Keys to Azure Key Vault

Script to store all MCP-related API keys to Azure Key Vault.
This ensures ALL secrets are stored securely in Key Vault.

@MANUS @MCP @AZURE_KEY_VAULT @SECURITY
"""

import sys
import getpass
from pathlib import Path

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from azure_service_bus_integration import AzureKeyVaultClient
    KEY_VAULT_AVAILABLE = True
except ImportError:
    KEY_VAULT_AVAILABLE = False
    print("ERROR: Azure Key Vault client not available", file=sys.stderr)
    print("Install with: pip install azure-keyvault-secrets azure-identity", file=sys.stderr)
    sys.exit(1)


def store_secret_interactive(key_vault: AzureKeyVaultClient, secret_name: str, description: str) -> bool:
    """
    Interactively store a secret to Key Vault.

    Args:
        key_vault: Azure Key Vault client
        secret_name: Name of the secret in Key Vault
        description: Description of what this secret is for

    Returns:
        True if secret was stored successfully
    """
    print(f"\n{'='*60}")
    print(f"Secret: {secret_name}")
    print(f"Description: {description}")
    print(f"{'='*60}")

    # Check if secret already exists
    try:
        existing = key_vault.get_secret(secret_name)
        print(f"⚠️  Secret '{secret_name}' already exists in Key Vault")
        response = input("Do you want to update it? (y/n): ").strip().lower()
        if response != 'y':
            print("Skipping...")
            return False
    except Exception:
        pass  # Secret doesn't exist, which is fine

    # Get secret value
    print(f"\nEnter the value for '{secret_name}':")
    print("(Input will be hidden for security)")
    secret_value = getpass.getpass("Value: ").strip()

    if not secret_value:
        print("⚠️  Empty value provided. Skipping...")
        return False

    # Confirm
    print(f"\nAbout to store secret '{secret_name}' to Key Vault")
    confirm = input("Confirm? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return False

    # Store secret
    try:
        success = key_vault.set_secret(secret_name, secret_value)
        if success:
            print(f"✅ Successfully stored '{secret_name}' to Key Vault")
            return True
        else:
            print(f"❌ Failed to store '{secret_name}' to Key Vault")
            return False
    except Exception as e:
        print(f"❌ Error storing '{secret_name}': {e}")
        return False


def main():
    """Main entry point"""
    print("="*60)
    print("Store All MCP Keys to Azure Key Vault")
    print("="*60)
    print("\nThis script will help you store all MCP-related API keys")
    print("securely in Azure Key Vault.\n")

    # Initialize Key Vault client
    vault_url = input("Azure Key Vault URL (default: https://jarvis-lumina.vault.azure.net/): ").strip()
    if not vault_url:
        vault_url = "https://jarvis-lumina.vault.azure.net/"

    try:
        key_vault = AzureKeyVaultClient(vault_url)
        print(f"✅ Connected to Key Vault: {vault_url}\n")
    except Exception as e:
        print(f"❌ Error connecting to Key Vault: {e}")
        sys.exit(1)

    # Define secrets to store
    secrets_to_store = [
        {
            "name": "elevenlabs-api-key",
            "description": "ElevenLabs API key for text-to-speech and audio processing. Get from: https://elevenlabs.io/app/settings/api-keys"
        },
        # Add more secrets here as needed
    ]

    stored_count = 0
    for secret_info in secrets_to_store:
        if store_secret_interactive(key_vault, secret_info["name"], secret_info["description"]):
            stored_count += 1

    print(f"\n{'='*60}")
    print(f"✅ Stored {stored_count} out of {len(secrets_to_store)} secrets")
    print(f"{'='*60}\n")

    print("Next steps:")
    print("1. Verify secrets are accessible:")
    print("   python scripts/python/manus_mcp_config_helper.py")
    print("\n2. The MCP configuration will now use keys from Key Vault")
    print("\n3. For Docker deployments, ensure Azure credentials are configured")


if __name__ == "__main__":


    main()