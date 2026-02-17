#!/usr/bin/env python3
"""
MANUS MCP Key Vault Wrapper

Wrapper script that retrieves all API keys from Azure Key Vault before
launching the MANUS MCP server. Ensures ALL secrets are stored in Key Vault.

@MANUS @MCP @AZURE_KEY_VAULT @SECURITY
"""

import os
import sys
from pathlib import Path

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from azure_service_bus_integration import AzureKeyVaultClient

    KEY_VAULT_AVAILABLE = True
except ImportError:
    KEY_VAULT_AVAILABLE = False
    print("ERROR: Azure Key Vault client not available", file=sys.stderr)
    print("Install with: pip install azure-keyvault-secrets azure-identity", file=sys.stderr)
    sys.exit(1)


def get_secrets_from_key_vault() -> dict:
    """
    Retrieve all required secrets from Azure Key Vault.

    Returns:
        Dictionary of environment variables to set
    """
    vault_url = os.getenv("AZURE_KEY_VAULT_URL", "https://jarvis-lumina.vault.azure.net/")

    try:
        key_vault = AzureKeyVaultClient(vault_url)
        env_vars = {}

        # ElevenLabs API Key (must be valid Key Vault names: alphanumeric and hyphens only)
        secret_names = {
            "ELEVENLABS_API_KEY": ["elevenlabs-api-key", "elevenlabs-key", "elevenlabs-tts-key"],
        }

        for env_var, secret_name_options in secret_names.items():
            value = None
            for secret_name in secret_name_options:
                try:
                    value = key_vault.get_secret(secret_name)
                    print(f"✅ Retrieved {env_var} from Key Vault: {secret_name}", file=sys.stderr)
                    break
                except Exception:
                    continue

            if value:
                env_vars[env_var] = value
            else:
                print(f"⚠️  Warning: Could not retrieve {env_var} from Key Vault", file=sys.stderr)
                print(f"   Tried secret names: {', '.join(secret_name_options)}", file=sys.stderr)
                print("   Please ensure the secret exists in Key Vault", file=sys.stderr)

        return env_vars

    except Exception as e:
        print(f"❌ Error accessing Azure Key Vault: {e}", file=sys.stderr)
        print(f"   Vault URL: {vault_url}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point - retrieves secrets and launches MCP server"""
    import sys

    # Check if we're launching ElevenLabs MCP server
    launch_elevenlabs = "--elevenlabs" in sys.argv

    # Get all secrets from Key Vault
    env_vars = get_secrets_from_key_vault()

    # Set environment variables
    for key, value in env_vars.items():
        os.environ[key] = value

    if launch_elevenlabs:
        # Launch ElevenLabs MCP server
        # Ensure ELEVENLABS_API_KEY is set
        if "ELEVENLABS_API_KEY" not in env_vars:
            print("ERROR: ELEVENLABS_API_KEY not found in Key Vault", file=sys.stderr)
            print(
                "Please store it using: python scripts/python/store_all_mcp_keys_to_vault.py",
                file=sys.stderr,
            )
            sys.exit(1)

        # Launch ElevenLabs MCP server using uvx or python module
        import subprocess

        try:
            # Try uvx first (recommended)
            result = subprocess.run(["uvx", "elevenlabs-mcp"], env=os.environ)
            sys.exit(result.returncode)
        except FileNotFoundError:
            # Fallback to python module
            try:
                # Use sys.executable to ensure we use the same Python environment (venv)
                result = subprocess.run([sys.executable, "-m", "elevenlabs_mcp"], env=os.environ)
                sys.exit(result.returncode)
            except Exception as e:
                print(f"ERROR: Could not launch ElevenLabs MCP server: {e}", file=sys.stderr)
                print("Install with: pip install elevenlabs-mcp or use uvx", file=sys.stderr)
                sys.exit(1)
    else:
        # Import and run the MANUS MCP server
        # This will use the environment variables we just set
        import asyncio

        import manus_mcp_server

        asyncio.run(manus_mcp_server.main())


if __name__ == "__main__":
    main()
