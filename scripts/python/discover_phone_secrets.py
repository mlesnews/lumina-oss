#!/usr/bin/env python3
"""
Discover Phone Number Secrets in Azure Key Vault
Finds all secrets that might contain phone numbers

Tags: #AZURE_KEY_VAULT #DISCOVERY #PHONE #SECRETS
"""

import sys
from pathlib import Path

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("DiscoverPhoneSecrets")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("DiscoverPhoneSecrets")

try:
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential, AzureCliCredential
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    logger.error("❌ Azure SDK not available")


def list_all_secrets():
    """List all secrets in Azure Key Vault"""
    if not AZURE_AVAILABLE:
        logger.error("❌ Azure SDK not available")
        return []

    try:
        vault_url = "https://jarvis-lumina.vault.azure.net/"

        # Try Azure CLI credential first
        try:
            credential = AzureCliCredential()
            client = SecretClient(vault_url=vault_url, credential=credential)
        except:
            credential = DefaultAzureCredential(

                                exclude_interactive_browser_credential=False,

                                exclude_shared_token_cache_credential=False

                            )
            client = SecretClient(vault_url=vault_url, credential=credential)

        # List all secrets
        secrets = []
        for secret_properties in client.list_properties_of_secrets():
            secrets.append(secret_properties.name)

        return secrets

    except Exception as e:
        logger.error(f"❌ Failed to list secrets: {e}")
        return []


def find_phone_secrets():
    """Find secrets that might contain phone numbers"""
    all_secrets = list_all_secrets()

    # Keywords that might indicate phone numbers
    phone_keywords = [
        "phone", "mobile", "cell", "sms", "text",
        "mlesn", "glenda", "user", "contact"
    ]

    phone_secrets = []
    for secret_name in all_secrets:
        secret_lower = secret_name.lower()
        if any(keyword in secret_lower for keyword in phone_keywords):
            phone_secrets.append(secret_name)

    return phone_secrets, all_secrets


def get_secret_value(secret_name: str) -> str:
    """Get secret value (masked for security)"""
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

        secret = client.get_secret(secret_name)
        value = secret.value

        # Mask phone number for display (show first 3 and last 4 digits)
        if len(value) >= 7:
            masked = value[:3] + "*" * (len(value) - 7) + value[-4:]
        else:
            masked = "*" * len(value)

        return masked

    except Exception as e:
        return f"ERROR: {e}"


def main():
    """Main discovery"""
    logger.info("="*80)
    logger.info("🔍 DISCOVERING PHONE NUMBER SECRETS IN AZURE KEY VAULT")
    logger.info("="*80)

    phone_secrets, all_secrets = find_phone_secrets()

    logger.info(f"\n📋 Found {len(all_secrets)} total secrets")
    logger.info(f"📱 Found {len(phone_secrets)} potential phone number secrets:\n")

    if phone_secrets:
        for secret_name in phone_secrets:
            masked_value = get_secret_value(secret_name)
            logger.info(f"  ✅ {secret_name}: {masked_value}")

        logger.info("\n💡 Suggested secret names for SMS approval:")
        logger.info("   - Primary user: 'user-mobile-phone' or 'mlesn-mobile'")
        logger.info("   - Secondary user: 'glenda-mobile' or 'glenda-phone'")
    else:
        logger.warning("⚠️  No phone number secrets found")
        logger.info("💡 You may need to check secret names manually")

    logger.info("\n" + "="*80)

    return phone_secrets


if __name__ == "__main__":


    main()