#!/usr/bin/env python3
"""
Get Matthew's Phone Number from Azure Key Vault
Retrieves phone number for ElevenLabs verification

Tags: #AZURE_VAULT #PHONE #ELEVENLABS
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    logger = get_logger("GetMatthewPhone")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("GetMatthewPhone")

try:
    from azure_service_bus_integration import AzureKeyVaultClient
    AZURE_VAULT_AVAILABLE = True
except ImportError:
    try:
        from azure_key_vault_client import AzureKeyVaultClient
        AZURE_VAULT_AVAILABLE = True
    except ImportError:
        AZURE_VAULT_AVAILABLE = False
        AzureKeyVaultClient = None
        logger.error("❌ Azure Key Vault client not available")


def get_matthew_phone_number() -> str:
    """Get Matthew's phone number from Azure Key Vault"""
    if not AZURE_VAULT_AVAILABLE:
        logger.error("❌ Azure Key Vault not available")
        return None

    try:
        vault = AzureKeyVaultClient(vault_url="https://jarvis-lumina.vault.azure.net/")

        # Try common secret names for Matthew's phone number
        secret_names = [
            "matt-lesnewski-mobile",
            "lesnewski-mobile",
            "mlesnewski-mobile",
            "mlesn-mobile",
            "mlesn-phone",
            "user-mobile-phone",
            "matthew-phone",
            "matthew-mobile",
            "phone-number",
            "mobile-number",
            "cell-phone",
            "phone",
            "matthew-cell",
            "mlesn-cell",
            "elevenlabs-phone",
            "verification-phone"
        ]

        for secret_name in secret_names:
            try:
                phone = vault.get_secret(secret_name)
                if phone:
                    # Never log full phone number - only confirm retrieval
                    logger.info(f"✅ Retrieved phone number from Azure Vault: {secret_name}")
                    logger.debug(f"   Phone number [REDACTED - stored securely in Azure Vault]")
                    return phone
            except Exception:
                continue

        logger.error("❌ Phone number not found in Azure Key Vault")
        logger.info("💡 Tried secret names:")
        for name in secret_names:
            logger.info(f"   • {name}")
        return None

    except Exception as e:
        logger.error(f"❌ Error accessing Azure Key Vault: {e}")
        return None


if __name__ == "__main__":
    phone = get_matthew_phone_number()
    if phone:
        print(phone)
        sys.exit(0)
    else:
        sys.exit(1)
