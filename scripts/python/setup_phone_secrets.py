#!/usr/bin/env python3
"""
Setup Phone Number Secrets in Azure Key Vault
Creates/updates phone number secrets for SMS approval

Tags: #AZURE_KEY_VAULT #PHONE #SETUP
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
    logger = get_logger("SetupPhoneSecrets")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("SetupPhoneSecrets")

try:
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential, AzureCliCredential
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    logger.error("❌ Azure SDK not available")


def setup_phone_secrets():
    """Setup phone number secrets in Azure Key Vault"""
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

        # Phone numbers (format: +1XXXXXXXXXX)
        # Last name: Lesnewski (L-E-S-N-E-W-S-K-I)
        # Pronunciation: "Less-New-Ski" (phonetic: /lɛs-nu-ski/)
        #   - "Les" = "less" (opposite of more) = /lɛs/
        #   - "New" = "new" (opposite of old) = /nu/
        #   - "Ski" = "ski" (like skiing) = /ski/
        phone_numbers = {
            "lesnewski-mobile": "+13023593913",         # Matt Lesnewski: 302-359-3913
            "matt-lesnewski-mobile": "+13023593913",   # Matt Lesnewski (full name)
            "glenda-lesnewski-mobile": "+13024802895",  # Glenda Lesnewski: 302-480-2895
            "glenda-mobile": "+13024802895",           # Glenda (short form)
            "user-mobile-phone": "+13023593913"        # Primary user (alias)
        }

        logger.info("="*80)
        logger.info("📱 SETTING UP PHONE NUMBER SECRETS IN AZURE KEY VAULT")
        logger.info("="*80)
        logger.info("")

        for secret_name, phone_number in phone_numbers.items():
            try:
                # Check if secret exists
                try:
                    existing = client.get_secret(secret_name)
                    logger.info(f"📝 Updating existing secret: {secret_name}")
                    client.set_secret(secret_name, phone_number)
                    logger.info(f"   ✅ Updated: {secret_name}")
                except:
                    # Secret doesn't exist, create it
                    logger.info(f"➕ Creating new secret: {secret_name}")
                    client.set_secret(secret_name, phone_number)
                    logger.info(f"   ✅ Created: {secret_name}")
            except Exception as e:
                logger.error(f"❌ Failed to set {secret_name}: {e}")

        logger.info("")
        logger.info("="*80)
        logger.info("✅ Phone number secrets setup complete!")
        logger.info("="*80)

        return True

    except Exception as e:
        logger.error(f"❌ Failed to setup phone secrets: {e}")
        return False


def main():
    """Main"""
    success = setup_phone_secrets()

    if success:
        logger.info("\n💡 Next steps:")
        logger.info("   1. Test phone number retrieval:")
        logger.info("      python scripts/python/dead_man_switch_sms_approval.py --test")
        logger.info("   2. Update SMS approval config if needed")

    return 0 if success else 1


if __name__ == "__main__":


    sys.exit(main())