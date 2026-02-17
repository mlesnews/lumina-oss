#!/usr/bin/env python3
"""
Find Phone Secrets Directly
Tries to get phone numbers by testing common patterns and checking if values look like phone numbers

Tags: #AZURE_KEY_VAULT #PHONE #DISCOVERY
"""

import sys
import re
from pathlib import Path

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("FindPhoneSecrets")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("FindPhoneSecrets")

try:
    from unified_secrets_manager import UnifiedSecretsManager
    SECRETS_AVAILABLE = True
except ImportError:
    SECRETS_AVAILABLE = False
    logger.error("❌ UnifiedSecretsManager not available")


def looks_like_phone_number(value: str) -> bool:
    """Check if a value looks like a phone number"""
    if not value:
        return False

    # Remove common formatting
    cleaned = re.sub(r'[\s\-\(\)\+]', '', value)

    # Check if it's mostly digits and reasonable length (7-15 digits)
    digits = sum(1 for c in cleaned if c.isdigit())
    if 7 <= digits <= 15:
        return True

    return False


def find_phone_secrets():
    """Try to find phone number secrets by testing common patterns"""
    if not SECRETS_AVAILABLE:
        logger.error("❌ UnifiedSecretsManager not available")
        return {}

    secrets_manager = UnifiedSecretsManager(project_root)

    # Comprehensive list of possible secret names
    secret_names_to_try = [
        # User phone variations
        "mlesn-mobile",
        "mlesn-phone",
        "mlesn-mobile-phone",
        "mlesn-cell",
        "mlesn-sms",
        "user-mobile",
        "user-phone",
        "user-mobile-phone",
        "user-cell",
        "primary-mobile",
        "primary-phone",
        "admin-mobile",
        "admin-phone",
        # Glenda phone variations
        "glenda-mobile",
        "glenda-phone",
        "glenda-mobile-phone",
        "glenda-cell",
        "glenda-sms",
        "wife-mobile",
        "wife-phone",
        "secondary-mobile",
        "secondary-phone",
        # Generic variations
        "mobile-phone",
        "phone-number",
        "mobile-number",
        "cell-phone",
        "sms-phone",
        "text-phone",
        "contact-phone",
        "emergency-phone",
        # With numbers
        "phone-1",
        "phone-2",
        "mobile-1",
        "mobile-2",
        # Direct names
        "mlesn",
        "glenda",
        "phone",
        "mobile"
    ]

    found_phones = {}

    logger.info("🔍 Testing secret names for phone numbers...\n")

    for secret_name in secret_names_to_try:
        try:
            value = secrets_manager.get_secret(secret_name)
            if value and looks_like_phone_number(value):
                # Mask for display
                masked = value[:3] + "*" * max(0, len(value) - 7) + value[-4:] if len(value) >= 7 else "*" * len(value)
                found_phones[secret_name] = value
                logger.info(f"✅ FOUND: {secret_name} = {masked}")
        except Exception as e:
            # Secret doesn't exist or error - continue
            pass

    if found_phones:
        logger.info(f"\n✅ Found {len(found_phones)} phone number secret(s)!")
        logger.info("\n💡 These will be used for SMS approval:")
        for name in found_phones.keys():
            logger.info(f"   • {name}")
    else:
        logger.warning("\n⚠️  No phone number secrets found with common names")
        logger.info("💡 Please provide the exact secret names from Azure Key Vault")
        logger.info("   and I'll update the system to use them.")

    return found_phones


def main():
    """Main"""
    logger.info("="*80)
    logger.info("🔍 FINDING PHONE NUMBER SECRETS IN AZURE KEY VAULT")
    logger.info("="*80)
    logger.info("")

    phones = find_phone_secrets()

    logger.info("")
    logger.info("="*80)

    return phones


if __name__ == "__main__":


    main()