#!/usr/bin/env python3
"""
MANUS MCP Configuration Helper

Helper script to generate MCP configuration with API keys from Azure Key Vault.
This ensures all secrets are properly retrieved from Key Vault before configuration.

@MANUS @MCP @AZURE_KEY_VAULT
"""

import json
import sys
from pathlib import Path
import logging
logger = logging.getLogger("manus_mcp_config_helper")


# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from azure_service_bus_integration import AzureKeyVaultClient

    KEY_VAULT_AVAILABLE = True
except ImportError:
    KEY_VAULT_AVAILABLE = False
    print("Warning: Azure Key Vault client not available", file=sys.stderr)


def get_elevenlabs_api_key() -> str:
    """Get ElevenLabs API key from Azure Key Vault"""
    if not KEY_VAULT_AVAILABLE:
        return "<REPLACE_WITH_KEY_FROM_AZURE_KEY_VAULT>"

    try:
        # Default vault URL - adjust if different
        vault_url = "https://jarvis-lumina.vault.azure.net/"
        key_vault = AzureKeyVaultClient(vault_url)

        # Try common secret names for ElevenLabs API key (must be valid Key Vault names: alphanumeric and hyphens only)
        secret_names = ["elevenlabs-api-key", "elevenlabs-key", "elevenlabs-tts-key"]

        for secret_name in secret_names:
            try:
                api_key = key_vault.get_secret(secret_name)
                print(
                    f"✅ Retrieved ElevenLabs API key from Key Vault: {secret_name}",
                    file=sys.stderr,
                )
                return api_key
            except Exception:
                continue

        print("⚠️  ElevenLabs API key not found in Key Vault. Using placeholder.", file=sys.stderr)
        print(f"   Please ensure secret exists: {', '.join(secret_names)}", file=sys.stderr)
        return "<REPLACE_WITH_KEY_FROM_AZURE_KEY_VAULT>"

    except Exception as e:
        print(f"⚠️  Error accessing Key Vault: {e}", file=sys.stderr)
        print("   Using placeholder. Configure manually if needed.", file=sys.stderr)
        return "<REPLACE_WITH_KEY_FROM_AZURE_KEY_VAULT>"


def generate_claude_desktop_config(project_root: Path) -> dict:
    """Generate Claude Desktop MCP configuration using keys from Azure Key Vault"""
    project_root_str = str(project_root.resolve())

    # Get ElevenLabs API key from Key Vault
    elevenlabs_key = get_elevenlabs_api_key()

    # IMPORTANT: All keys MUST come from Azure Key Vault
    # The configuration uses a wrapper script that retrieves keys at runtime
    config = {
        "mcpServers": {
            "MANUS": {
                "command": "python",
                "args": ["-m", "scripts.python.manus_mcp_key_vault_wrapper"],
                "cwd": project_root_str,
                "env": {"AZURE_KEY_VAULT_URL": "https://jarvis-lumina.vault.azure.net/"},
            },
            "ElevenLabs": {
                "command": "python",
                "args": ["-m", "scripts.python.manus_mcp_key_vault_wrapper", "--elevenlabs"],
                "cwd": project_root_str,
                "env": {
                    "AZURE_KEY_VAULT_URL": "https://jarvis-lumina.vault.azure.net/",
                    "ELEVENLABS_MCP_BASE_PATH": "~/Desktop",
                    "ELEVENLABS_MCP_OUTPUT_MODE": "files",
                },
            },
        },
        "_metadata": {
            "note": "ALL API KEYS ARE STORED IN AZURE KEY VAULT",
            "key_vault_url": "https://jarvis-lumina.vault.azure.net/",
            "secrets_required": ["elevenlabs-api-key"],
            "setup_script": "python scripts/python/store_all_mcp_keys_to_vault.py",
        },
    }

    # Fallback: Use direct key if available (for compatibility, but not recommended)
    if elevenlabs_key and not elevenlabs_key.startswith("<"):
        config["mcpServers"]["ElevenLabs"]["env"]["ELEVENLABS_API_KEY"] = elevenlabs_key
        print(
            "⚠️  Using direct API key from Key Vault (runtime wrapper is preferred)", file=sys.stderr
        )

    return config


def main():
    try:
        """Main entry point"""
        # Determine project root
        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent

        # Generate configuration
        config = generate_claude_desktop_config(project_root)

        # Output JSON configuration
        print(json.dumps(config, indent=2))

        # Also save to file
        config_file = project_root / "config" / "claude_desktop_mcp_config.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)

        print(f"\n✅ Configuration saved to: {config_file}", file=sys.stderr)
        print("\n📋 Next steps:", file=sys.stderr)
        print("   1. Copy the configuration above to your Claude Desktop config", file=sys.stderr)
        print(
            "   2. Location: %APPDATA%\\Claude\\claude_desktop_config.json (Windows)",
            file=sys.stderr,
        )
        print(
            "   3. Or: ~/Library/Application Support/Claude/claude_desktop_config.json (macOS)",
            file=sys.stderr,
        )
        print(
            "   4. Ensure 'scripts.python.manus_mcp_server' is in your Python path", file=sys.stderr
        )
        print("   5. Install MCP SDK: pip install mcp", file=sys.stderr)
        print(
            "   6. Install ElevenLabs MCP: pip install elevenlabs-mcp or use uvx", file=sys.stderr
        )

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
