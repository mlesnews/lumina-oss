#!/usr/bin/env python3
"""
Add N8N API Key to Azure Vault from Clipboard

Reads API key from clipboard and adds it to Azure Key Vault.
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False
    print("WARNING: pyperclip not installed. Install with: pip install pyperclip")

from azure_service_bus_integration import AzureKeyVaultClient

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AddN8NAPIKey")

def get_clipboard():
    """Get clipboard contents"""
    if not CLIPBOARD_AVAILABLE:
        logger.error("pyperclip not available. Please install: pip install pyperclip")
        return None

    try:
        return pyperclip.paste().strip()
    except Exception as e:
        logger.error(f"Failed to read clipboard: {e}")
        return None

def add_to_vault(api_key: str, secret_name: str = "n8n-api-token"):
    """Add API key to Azure Vault"""
    vault = AzureKeyVaultClient(vault_url="https://jarvis-lumina.vault.azure.net/")

    try:
        vault.set_secret(secret_name, api_key)
        logger.info(f"✅ Successfully added {secret_name} to Azure Vault")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to add secret to vault: {e}")
        return False

def main():
    """Main execution"""
    logger.info("="*80)
    logger.info("🔐 ADDING N8N API KEY TO AZURE VAULT")
    logger.info("="*80)
    logger.info("")

    # Get API key from clipboard
    logger.info("📋 Reading API key from clipboard...")
    api_key = get_clipboard()

    if not api_key:
        logger.error("❌ Could not read API key from clipboard")
        logger.info("")
        logger.info("💡 Please ensure:")
        logger.info("   1. API key is copied to clipboard")
        logger.info("   2. pyperclip is installed: pip install pyperclip")
        return 1

    if len(api_key) < 10:
        logger.warning(f"⚠️  API key seems too short ({len(api_key)} chars). Continue anyway?")

    logger.info(f"   ✅ Read API key from clipboard ({len(api_key)} characters)")
    logger.info("")

    # Add to vault
    logger.info("💾 Adding to Azure Vault...")
    if add_to_vault(api_key):
        logger.info("")
        logger.info("="*80)
        logger.info("✅ API KEY SUCCESSFULLY ADDED TO AZURE VAULT")
        logger.info("="*80)
        logger.info("")
        logger.info("🚀 You can now deploy workflows using:")
        logger.info("   python scripts/python/deploy_n8n_with_vault_creds.py")
        return 0
    else:
        logger.info("")
        logger.info("="*80)
        logger.info("❌ FAILED TO ADD API KEY")
        logger.info("="*80)
        return 1

if __name__ == "__main__":


    exit(main())