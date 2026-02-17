#!/usr/bin/env python3
"""
Set WakaTime Environment Variable from Azure Key Vault

Run this at login/startup to set WAKATIME_API_KEY from Azure Key Vault.
NO SECRETS IN THE CLEAR!

Usage:
    python set_wakatime_env.py
    # Or add to Windows startup / profile scripts

Tags: #SECURITY #WAKATIME #AZURE_KEY_VAULT @JARVIS
"""

import os
import sys
import logging
logger = logging.getLogger("set_wakatime_env")


def get_wakatime_key_from_vault():
    """Retrieve WakaTime API key from Azure Key Vault"""
    try:
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient

        vault_url = "https://jarvis-lumina.vault.azure.net/"
        credential = DefaultAzureCredential(

                            exclude_interactive_browser_credential=False,

                            exclude_shared_token_cache_credential=False

                        )
        client = SecretClient(vault_url=vault_url, credential=credential)

        secret = client.get_secret("wakatime-api-key")
        return secret.value if secret else None
    except Exception as e:
        print(f"Error retrieving WakaTime key: {e}")
        return None

def main():
    try:
        """Set WAKATIME_API_KEY environment variable"""
        api_key = get_wakatime_key_from_vault()

        if api_key:
            # Set for current process
            os.environ["WAKATIME_API_KEY"] = api_key

            # For Windows, also set user environment variable
            if sys.platform == "win32":
                import subprocess
                # Set user environment variable (persists across sessions)
                subprocess.run([
                    "setx", "WAKATIME_API_KEY", api_key
                ], capture_output=True)
                print("✅ WAKATIME_API_KEY set (user environment)")
            else:
                print("✅ WAKATIME_API_KEY set (current session)")
                print("   Add to ~/.bashrc or ~/.zshrc for persistence")

            return 0
        else:
            print("❌ Could not retrieve WakaTime API key from vault")
            return 1

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())