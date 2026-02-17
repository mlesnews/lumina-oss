#!/usr/bin/env python3
"""
JARVIS ElevenLabs API Key Storage Utility
Stores ElevenLabs API key in Azure Key Vault

Supports storing the "Cursor - Cursor API Key" from ElevenLabs webui

Tags: #JARVIS #AZURE #KEYVAULT #ELEVENLABS @JARVIS @DOIT
"""

import sys
import os
from pathlib import Path
from typing import Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISStoreElevenLabsKey")


def store_key_in_azure_vault(api_key: str, secret_name: str = "Cursor - Cursor API Key", timeout: int = 10) -> bool:
    """
    Store ElevenLabs API key in Azure Key Vault with timeout protection

    Args:
        api_key: The ElevenLabs API key to store
        secret_name: Name to store the secret as (defaults to "Cursor - Cursor API Key")
        timeout: Timeout in seconds (default: 10)

    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"🔐 Storing ElevenLabs API key in Azure Key Vault as '{secret_name}'...")
        logger.info(f"   Timeout: {timeout} seconds")

        # Try Unified Secrets Manager first (supports Azure Key Vault)
        try:
            from unified_secrets_manager import UnifiedSecretsManager, SecretSource
            import threading
            import queue

            secret_manager = UnifiedSecretsManager(project_root=Path(__file__).parent.parent.parent)

            # Store in Azure Key Vault with timeout protection
            result_queue = queue.Queue()
            error_queue = queue.Queue()

            def store_with_timeout():
                try:
                    # Use set_secret method from UnifiedSecretsManager
                    success = secret_manager.set_secret(
                        secret_name=secret_name,
                        secret_value=api_key,
                        source=SecretSource.AZURE_KEY_VAULT
                    )
                    result_queue.put({"success": success, "vault_url": "https://jarvis-lumina.vault.azure.net/"})
                except Exception as e:
                    error_queue.put(e)

            thread = threading.Thread(target=store_with_timeout, daemon=True)
            thread.start()
            thread.join(timeout=timeout)

            if thread.is_alive():
                logger.error(f"❌ Azure Key Vault operation timed out after {timeout} seconds")
                logger.info("   💡 This usually means Azure authentication is required")
                logger.info("   💡 Run: az login")
                return False

            if not error_queue.empty():
                error = error_queue.get()
                logger.error(f"❌ Failed to store secret: {error}")
                return False

            if not result_queue.empty():
                result = result_queue.get()
                if result.get("success"):
                    logger.info(f"✅ Successfully stored '{secret_name}' in Azure Key Vault")
                    logger.info(f"   Key Vault: {result.get('vault_url', 'N/A')}")
                    return True
                else:
                    logger.error(f"❌ Failed to store secret: {result.get('error', 'Unknown error')}")
                    return False
            else:
                logger.error("❌ No result returned from storage operation")
                return False

        except ImportError:
            logger.warning("⚠️  Unified Secrets Manager not available, trying direct Azure Key Vault...")

        # Fallback: Direct Azure Key Vault access
        try:
            try:
                from azure_service_bus_integration import AzureKeyVaultClient
            except ImportError:
                from scripts.python.azure_service_bus_integration import AzureKeyVaultClient

            vault_url = os.getenv("AZURE_KEY_VAULT_URL", "https://jarvis-lumina.vault.azure.net/")

            vault_client = AzureKeyVaultClient(vault_url=vault_url)

            # Store secret
            result = vault_client.set_secret(secret_name, api_key)

            if result:
                logger.info(f"✅ Successfully stored '{secret_name}' in Azure Key Vault")
                logger.info(f"   Vault URL: {vault_url}")
                return True
            else:
                logger.error(f"❌ Failed to store secret in Azure Key Vault")
                return False

        except Exception as e:
            logger.error(f"❌ Azure Key Vault storage failed: {e}")
            logger.info("")
            logger.info("💡 Troubleshooting:")
            logger.info("   1. Ensure you're authenticated: az login")
            logger.info("   2. Check Azure Key Vault permissions")
            logger.info("   3. Verify vault URL is correct")
            return False

    except Exception as e:
        logger.error(f"❌ Failed to store API key: {e}")
        return False


def store_all_variations(api_key: str) -> dict:
    """
    Store API key under multiple name variations for compatibility

    Returns:
        Dictionary with results for each name variation
    """
    results = {}

    # Store under multiple names that the system checks
    secret_names = [
        "Cursor - Cursor API Key",  # Exact ElevenLabs webui name
        "elevenlabs-api-key",  # Standard name
        "cursor-api-key",  # Alternative
        "cursor-cursor-api-key",  # Dashed version
    ]

    logger.info("📝 Storing API key under multiple name variations for compatibility...")

    for secret_name in secret_names:
        logger.info(f"   Storing as: {secret_name}")
        success = store_key_in_azure_vault(api_key, secret_name)
        results[secret_name] = success
        if success:
            logger.info(f"   ✅ Stored as '{secret_name}'")
        else:
            logger.warning(f"   ⚠️  Failed to store as '{secret_name}'")

    return results


def main():
    """CLI interface"""
    import argparse
    import getpass

    parser = argparse.ArgumentParser(
        description="Store ElevenLabs API key in Azure Key Vault",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Store key from command line
  python jarvis_store_elevenlabs_key.py --key YOUR_API_KEY

  # Store key interactively (secure - won't show in terminal)
  python jarvis_store_elevenlabs_key.py --interactive

  # Store key from clipboard
  python jarvis_store_elevenlabs_key.py --clipboard

  # Store key from environment variable
  python jarvis_store_elevenlabs_key.py --env ELEVENLABS_API_KEY

  # Store under multiple name variations
  python jarvis_store_elevenlabs_key.py --key YOUR_API_KEY --all-variations
        """
    )

    parser.add_argument(
        "--key",
        type=str,
        help="ElevenLabs API key to store (not recommended - use --interactive instead)"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Prompt for API key securely (recommended)"
    )
    parser.add_argument(
        "--clipboard",
        action="store_true",
        help="Read API key from clipboard"
    )
    parser.add_argument(
        "--env",
        type=str,
        help="Read API key from environment variable (e.g., ELEVENLABS_API_KEY)"
    )
    parser.add_argument(
        "--secret-name",
        type=str,
        default="Cursor - Cursor API Key",
        help="Secret name in Azure Key Vault (default: 'Cursor - Cursor API Key')"
    )
    parser.add_argument(
        "--all-variations",
        action="store_true",
        help="Store under multiple name variations for compatibility"
    )

    args = parser.parse_args()

    # Get API key from various sources
    api_key = None

    if args.key:
        api_key = args.key
        logger.warning("⚠️  API key provided via --key (visible in command history)")
    elif args.interactive:
        api_key = getpass.getpass("Enter ElevenLabs API key: ")
    elif args.clipboard:
        try:
            import pyperclip
            api_key = pyperclip.paste().strip()
            logger.info("✅ API key read from clipboard")
        except ImportError:
            logger.error("❌ pyperclip not available. Install: pip install pyperclip")
            return 1
        except Exception as e:
            logger.error(f"❌ Failed to read from clipboard: {e}")
            return 1
    elif args.env:
        api_key = os.getenv(args.env)
        if not api_key:
            logger.error(f"❌ Environment variable '{args.env}' not set")
            return 1
        logger.info(f"✅ API key read from environment variable '{args.env}'")
    else:
        logger.error("❌ No API key source specified")
        logger.info("")
        logger.info("Use one of:")
        logger.info("  --key YOUR_API_KEY")
        logger.info("  --interactive (recommended)")
        logger.info("  --clipboard")
        logger.info("  --env VARIABLE_NAME")
        parser.print_help()
        return 1

    if not api_key:
        logger.error("❌ No API key provided")
        return 1

    # Validate API key format (ElevenLabs keys typically start with certain patterns)
    if len(api_key) < 20:
        logger.warning("⚠️  API key seems too short - please verify it's correct")

    # Store the key
    logger.info("")
    logger.info("=" * 80)
    logger.info("🔐 STORING ELEVENLABS API KEY IN AZURE KEY VAULT")
    logger.info("=" * 80)
    logger.info("")

    if args.all_variations:
        results = store_all_variations(api_key)

        # Summary
        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 STORAGE SUMMARY")
        logger.info("=" * 80)

        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)

        for name, success in results.items():
            status = "✅" if success else "❌"
            logger.info(f"{status} {name}")

        logger.info("")
        logger.info(f"Successfully stored: {success_count}/{total_count}")

        if success_count > 0:
            logger.info("✅ API key stored successfully!")
            logger.info("   JARVIS will now be able to retrieve it for TTS functionality")
            return 0
        else:
            logger.error("❌ Failed to store API key under any name")
            logger.info("")
            logger.info("💡 Troubleshooting:")
            logger.info("   1. Run: az login")
            logger.info("   2. Check Azure Key Vault permissions")
            logger.info("   3. Verify vault URL is correct")
            return 1
    else:
        success = store_key_in_azure_vault(api_key, args.secret_name)

        if success:
            logger.info("")
            logger.info("✅ API key stored successfully!")
            logger.info("   JARVIS will now be able to retrieve it for TTS functionality")
            logger.info("")
            logger.info("💡 Tip: Use --all-variations to store under multiple names for compatibility")
            return 0
        else:
            logger.error("❌ Failed to store API key")
            return 1


if __name__ == "__main__":


    sys.exit(main())