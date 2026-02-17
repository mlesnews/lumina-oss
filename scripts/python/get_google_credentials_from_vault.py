"""
Get Google API Credentials from Azure Key Vault
Looks for Google/Gmail API credentials in the vault

#JARVIS #LUMINA #AZURE #KEYVAULT #GOOGLE
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
    try:
        from scripts.python.azure_service_bus_integration import AzureKeyVaultClient
    except ImportError:
        print("ERROR: Could not import AzureKeyVaultClient")
        sys.exit(1)

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("GetGoogleCredentialsFromVault")


def main():
    """Get Google API credentials from Azure Key Vault"""
    vault_url = os.getenv("AZURE_KEY_VAULT_URL", "https://jarvis-lumina.vault.azure.net/")

    print(f"\n🔍 Checking Azure Key Vault: {vault_url}\n")

    try:
        vault_client = AzureKeyVaultClient(vault_url=vault_url)

        # List all secrets to see what's available
        print("📋 Listing all secrets in Key Vault...\n")
        all_secrets = vault_client.list_secrets()

        if all_secrets:
            print(f"✅ Found {len(all_secrets)} secrets total\n")

            # Filter for Google-related secrets
            google_secrets = [s for s in all_secrets if 'google' in s.lower() or 'gmail' in s.lower() or 'gdrive' in s.lower()]

            if google_secrets:
                print(f"🔑 Found {len(google_secrets)} Google-related secret(s):\n")
                for secret_name in sorted(google_secrets):
                    print(f"   - {secret_name}")
                    try:
                        value = vault_client.get_secret(secret_name)
                        # Show preview (first 50 chars)
                        preview = value[:50] + "..." if len(value) > 50 else value
                        print(f"     Preview: {preview}")

                        # Check if it's JSON (credentials file)
                        if value.strip().startswith('{'):
                            print(f"     ✅ Appears to be JSON credentials")
                    except Exception as e:
                        print(f"     ⚠️  Could not retrieve: {e}")
                print()
            else:
                print("⚠️  No Google-related secrets found\n")
                print("💡 Searching all secrets for 'google', 'gmail', 'gdrive'...\n")

        # Try common Google API secret names
        print("🔍 Checking common Google API secret names...\n")
        common_names = [
            "google-api-credentials",
            "google-credentials",
            "google-oauth2-credentials",
            "gmail-oauth2-credentials",
            "gmail-credentials",
            "google-drive-credentials",
            "google-drive-api-credentials",
            "google-client-secret",
            "google-oauth-client-secret",
            "google-api-key",
            "gmail-api-key"
        ]

        found_any = False
        for name in common_names:
            try:
                value = vault_client.get_secret(name)
                print(f"✅ Found: {name}")
                preview = value[:50] + "..." if len(value) > 50 else value
                print(f"   Preview: {preview}")

                # Check if JSON
                if value.strip().startswith('{'):
                    print(f"   ✅ JSON credentials file")
                    # Try to parse
                    import json
                    try:
                        creds_data = json.loads(value)
                        print(f"   ✅ Valid JSON")
                        if 'installed' in creds_data or 'web' in creds_data:
                            print(f"   ✅ OAuth2 credentials format")
                            client_id = creds_data.get('installed', creds_data.get('web', {})).get('client_id', 'N/A')
                            print(f"   Client ID: {client_id[:20]}...")
                    except:
                        pass

                found_any = True
                print()
            except Exception as e:
                if "SecretNotFound" in str(e) or "not found" in str(e).lower():
                    pass  # Not found, continue
                else:
                    print(f"⚠️  Error checking {name}: {e}\n")

        if not found_any and not google_secrets:
            print("❌ No Google API credentials found in Key Vault")
            print("\n💡 You may need to:")
            print("   1. Store Google OAuth2 credentials in Key Vault")
            print("   2. Check the secret name in Azure Portal")
            print("   3. Use: az keyvault secret list --vault-name jarvis-lumina-vault")

    except Exception as e:
        print(f"❌ Error accessing Key Vault: {e}")
        print("\n💡 Make sure you're authenticated to Azure:")
        print("   az login")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":


    main()