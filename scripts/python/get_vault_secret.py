#!/usr/bin/env python3
"""
Get Secret from Azure Key Vault

Simple utility to retrieve a single secret from Azure Key Vault.
Used by startup scripts to populate environment variables.

NO SECRETS IN THE CLEAR! 🔐

Tags: #SECURITY #AZURE_KEY_VAULT @JARVIS
"""

import sys
import argparse


def get_secret(secret_name: str, vault_url: str = "https://jarvis-lumina.vault.azure.net/") -> str:
    """Retrieve secret from Azure Key Vault

    Uses AzureCliCredential first to avoid certificate prompts.
    Falls back to DefaultAzureCredential with certificate authentication excluded.
    """
    try:
        from azure.identity import (
            AzureCliCredential,
            DefaultAzureCredential
        )
        from azure.keyvault.secrets import SecretClient
        from azure.core.exceptions import ClientAuthenticationError

        # Try Azure CLI credential first (no certificate prompts)
        try:
            credential = AzureCliCredential()
            client = SecretClient(vault_url=vault_url, credential=credential)
            secret = client.get_secret(secret_name)
            return secret.value if secret else ""
        except (ClientAuthenticationError, Exception) as cli_error:
            # If Azure CLI fails, try DefaultAzureCredential but exclude certificate auth
            # This prevents certificate selection prompts
            try:
                # DefaultAzureCredential will try: Environment, Managed Identity, VS Code, Azure CLI, PowerShell
                # It will NOT try certificate-based auth unless explicitly configured
                credential = DefaultAzureCredential(
                    exclude_interactive_browser_credential=False,
                    exclude_shared_token_cache_credential=False
                )
                client = SecretClient(vault_url=vault_url, credential=credential)
                secret = client.get_secret(secret_name)
                return secret.value if secret else ""
            except Exception as default_error:
                # If both fail, log the error
                print(f"Error: Azure CLI failed: {cli_error}, DefaultAzureCredential failed: {default_error}", file=sys.stderr)
                return ""
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return ""


def main():
    parser = argparse.ArgumentParser(description="Get secret from Azure Key Vault")
    parser.add_argument('--secret', required=True, help='Secret name to retrieve')
    parser.add_argument('--vault', default="https://jarvis-lumina.vault.azure.net/", help='Vault URL')

    args = parser.parse_args()

    value = get_secret(args.secret, args.vault)
    if value:
        print(value)
        return 0
    return 1


if __name__ == "__main__":


    sys.exit(main())