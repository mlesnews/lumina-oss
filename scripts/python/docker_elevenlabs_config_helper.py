#!/usr/bin/env python3
"""
Docker Desktop MCP Toolkit - ElevenLabs Configuration Helper
Retrieves ElevenLabs API key from Azure Key Vault for Docker Desktop configuration

This script helps you configure the ElevenLabs MCP server in Docker Desktop's MCP Toolkit
by retrieving your API key from Azure Key Vault and displaying it for easy copy-paste.

Tags: #DOCKER #MCP #ELEVENLABS #KEYVAULT @JARVIS @DOIT
"""

import os
import sys
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
    print("   Install: pip install azure-keyvault-secrets azure-identity")


def get_elevenlabs_key_from_vault(vault_url: str = None) -> str:
    """
    Retrieve ElevenLabs API key from Azure Key Vault

    Args:
        vault_url: Azure Key Vault URL (defaults to env var or standard vault)

    Returns:
        API key string or None if not found
    """
    if not KEY_VAULT_AVAILABLE:
        return None

    if vault_url is None:
        vault_url = os.getenv("AZURE_KEY_VAULT_URL", "https://jarvis-lumina.vault.azure.net/")

    try:
        vault_client = AzureKeyVaultClient(vault_url=vault_url)

        # Try common secret names (must be valid Key Vault names: alphanumeric and hyphens only)
        secret_names = [
            "elevenlabs-api-key",
            "elevenlabs-key",
            "elevenlabs-tts-key",
            "cursor-api-key",
        ]

        for secret_name in secret_names:
            try:
                key = vault_client.get_secret(secret_name)
                if key:
                    return key
            except (KeyError, ValueError, AttributeError):
                # Secret not found or invalid - try next name
                continue

        return None
    except (ImportError, AttributeError, ValueError) as e:
        print(f"❌ Error accessing Key Vault: {e}")
        return None


def main():
    """Main CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="ElevenLabs Configuration Helper - Docker Desktop & NAS Container Manager"
    )
    parser.add_argument(
        "--vault-url",
        type=str,
        default=os.getenv("AZURE_KEY_VAULT_URL", "https://jarvis-lumina.vault.azure.net/"),
        help="Azure Key Vault URL",
    )
    parser.add_argument(
        "--copy-to-clipboard",
        action="store_true",
        help="Copy API key to clipboard (requires pyperclip)",
    )
    parser.add_argument(
        "--data-path",
        type=str,
        default="elevenlabs.data",
        help="Data directory path for Docker Desktop config (default: elevenlabs.data)",
    )
    parser.add_argument(
        "--target",
        type=str,
        choices=["docker-desktop", "nas", "both"],
        default="both",
        help="Target platform: docker-desktop, nas, or both (default: both)",
    )

    args = parser.parse_args()

    print("\n" + "=" * 80)
    if args.target == "docker-desktop":
        print("🐳 Docker Desktop MCP Toolkit - ElevenLabs Configuration")
    elif args.target == "nas":
        print("🖥️  NAS Container Manager (Synology) - ElevenLabs Configuration")
    else:
        print("🐳 ElevenLabs Configuration - Docker Desktop & NAS Container Manager")
    print("=" * 80)
    print()

    if not KEY_VAULT_AVAILABLE:
        print("❌ Azure Key Vault SDK not available")
        print("   Install: pip install azure-keyvault-secrets azure-identity")
        return 1

    # Retrieve API key
    print("🔍 Retrieving ElevenLabs API key from Azure Key Vault...")
    api_key = get_elevenlabs_key_from_vault(args.vault_url)

    if not api_key:
        print("❌ ElevenLabs API key not found in Azure Key Vault")
        print()
        print("💡 To add your API key to Key Vault, run:")
        print("   python scripts/python/add_elevenlabs_key_to_vault.py --api-key YOUR_KEY")
        print()
        print("   Or get your key from: https://elevenlabs.io/app/settings/api-keys")
        return 1

    print("✅ API key retrieved successfully from Azure Key Vault!")
    print()
    print("🔒 SECURITY NOTE: API key is stored securely in Azure Key Vault")
    print("   Containers retrieve it at runtime - never stored in config files")
    print()

    # Only display key if explicitly needed (for Docker Desktop manual entry)
    if args.target in ["docker-desktop", "both"]:
        print("-" * 80)
        print("🔑 API KEY (for Docker Desktop MCP Toolkit only):")
        print("-" * 80)
        print(api_key)
        print("-" * 80)
        print("⚠️  WARNING: This key is displayed for Docker Desktop configuration only")
        print("   Never commit, log, or share this key")
        print()

    # Try to copy to clipboard
    if args.copy_to_clipboard:
        try:
            import pyperclip

            pyperclip.copy(api_key)
            print("✅ API key copied to clipboard!")
        except ImportError:
            print("💡 Install pyperclip to enable clipboard copy:")
            print("   pip install pyperclip")
        except (OSError, RuntimeError) as e:
            print(f"⚠️  Could not copy to clipboard: {e}")
        print()

    # Docker Desktop Configuration
    if args.target in ["docker-desktop", "both"]:
        print("=" * 80)
        print("📋 Docker Desktop MCP Toolkit Configuration")
        print("=" * 80)
        print()
        print("Follow these steps in Docker Desktop:")
        print()
        print("1️⃣  Open Docker Desktop → MCP Toolkit BETA → My Servers / elevenlabs")
        print()
        print("2️⃣  Click on the 'Configuration' tab")
        print()
        print("3️⃣  In the 'Configuration' section:")
        print(f"    • Set 'elevenlabs.data' to: {args.data_path}")
        print()
        print("4️⃣  In the 'Secrets' section:")
        print("    • Set 'elevenlabs.api_key' to the key above")
        print()
        print("5️⃣  Click 'Save' button in Docker Desktop")
        print()
        print("6️⃣  The ElevenLabs MCP server should now be configured!")
        print()

    # NAS Container Manager Configuration
    if args.target in ["nas", "both"]:
        if args.target == "both":
            print()
            print("=" * 80)
        print("📋 NAS Container Manager (Synology) Configuration")
        print("=" * 80)
        print()
        print("🔒 SECURE CONFIGURATION: API key retrieved from Azure Key Vault at runtime")
        print("   The container uses start_secure.py wrapper that:")
        print("   • Retrieves key from Key Vault when container starts")
        print("   • Sets key only in memory (never in files or logs)")
        print("   • Never exposes key in process lists or environment dumps")
        print()
        print(
            "✅ Current Configuration (containerization/services/nas-mcp-servers/docker-compose.yml):"
        )
        print("   • Service: elevenlabs-mcp-server")
        print("   • Port: 8086")
        print("   • AZURE_KEY_VAULT_URL: https://jarvis-lumina.vault.azure.net/")
        print("   • Wrapper Script: start_secure.py (retrieves key at runtime)")
        print("   • API Key: NEVER stored in docker-compose.yml or image")
        print()
        print("🔍 To verify the container can access the key:")
        print("   1. SSH to NAS: ssh backupadm@<NAS_PRIMARY_IP>")
        print("   2. Check container logs (key will NOT appear):")
        print("      docker logs elevenlabs-mcp-server")
        print("   3. Test the service:")
        print("      curl http://localhost:8086/health")
        print()
        print("✅ Security: API key is retrieved securely and never exposed")
        print()

    print("=" * 80)
    print("✅ Configuration Complete!")
    print("=" * 80)
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
