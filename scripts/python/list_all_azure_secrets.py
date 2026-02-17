#!/usr/bin/env python3
"""
List All Azure Key Vault Secrets
Helps discover secret names for phone numbers

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
    from lumina_logger import get_logger
    logger = get_logger("ListAzureSecrets")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ListAzureSecrets")

try:
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential, AzureCliCredential
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    logger.error("❌ Azure SDK not available")


def list_all_secrets():
    """List all secret names (not values)"""
    if not AZURE_AVAILABLE:
        logger.error("❌ Azure SDK not available")
        return []

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

        # List all secrets (names only, no values)
        secrets = []
        for secret_properties in client.list_properties_of_secrets():
            secrets.append(secret_properties.name)

        return sorted(secrets)

    except Exception as e:
        logger.error(f"❌ Failed to list secrets: {e}")
        return []


def main():
    """List all secrets"""
    logger.info("="*80)
    logger.info("📋 LISTING ALL AZURE KEY VAULT SECRET NAMES")
    logger.info("="*80)

    secrets = list_all_secrets()

    logger.info(f"\n📊 Found {len(secrets)} secrets:\n")

    # Group by potential category
    phone_secrets = []
    other_secrets = []

    phone_keywords = ["phone", "mobile", "cell", "sms", "text", "mlesn", "glenda"]

    for secret_name in secrets:
        if any(keyword in secret_name.lower() for keyword in phone_keywords):
            phone_secrets.append(secret_name)
        else:
            other_secrets.append(secret_name)

    if phone_secrets:
        logger.info("📱 Potential Phone Number Secrets:")
        for secret in phone_secrets:
            logger.info(f"   • {secret}")
        logger.info("")

    logger.info("💡 If your phone number secrets have different names, please share them")
    logger.info("   and I'll update the system to use them.")
    logger.info("")
    logger.info("="*80)

    return secrets


if __name__ == "__main__":


    main()