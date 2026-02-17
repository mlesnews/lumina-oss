#!/usr/bin/env python3
"""
Sync NAS credentials from ProtonPass CLI to Azure Key Vault (Triad Tier 1).

Clawedbot-style: read from ProtonPass CLI and write to Azure so deploy/NAS
integration can use Azure (or ProtonPass as fallback). Use when NAS credentials
exist in ProtonPass (e.g. backupadm) and you want to ensure Azure has them too.

Usage:
  python sync_nas_credentials_protonpass_to_vault.py
  python sync_nas_credentials_protonpass_to_vault.py --dry-run

@triad @JARVIS
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from azure.identity import AzureCliCredential, DefaultAzureCredential
    from azure.keyvault.secrets import SecretClient
    from lumina_logger import get_logger
    from nas_azure_vault_integration import NASAzureVaultIntegration
except ImportError as e:
    sys.exit(f"Import error: {e}")

logger = get_logger("SyncNASProtonPassToVault")
VAULT_URL = "https://jarvis-lumina.vault.azure.net/"


def get_vault_client():
    try:
        cred = AzureCliCredential()
        return SecretClient(vault_url=VAULT_URL, credential=cred)
    except Exception:  # Azure CLI not logged in or other credential failure
        cred = DefaultAzureCredential(
            exclude_interactive_browser_credential=False,
            exclude_shared_token_cache_credential=False,
        )
        return SecretClient(vault_url=VAULT_URL, credential=cred)


def main():
    import argparse

    p = argparse.ArgumentParser(
        description="Sync NAS credentials from ProtonPass CLI to Azure Key Vault"
    )
    p.add_argument(
        "--dry-run", action="store_true", help="Only fetch from ProtonPass, do not write to Azure"
    )
    p.add_argument("--nas-ip", default="<NAS_PRIMARY_IP>", help="NAS IP for credential lookup")
    args = p.parse_args()

    integration = NASAzureVaultIntegration(nas_ip=args.nas_ip)
    integration.clear_credential_cache()
    creds = integration.get_nas_credentials_from_protonpass()
    if not creds:
        logger.error(
            "Could not retrieve NAS credentials from ProtonPass CLI. Ensure ProtonPass CLI is installed and authenticated."
        )
        print()
        print("No credentials active. Please run: pass-cli login --interactive <your-proton-email>")
        print("(Replace with your Proton Pass email; type your password when prompted.)")
        try:
            from prompt_nas_login import prompt_and_run_protonpass_login

            if prompt_and_run_protonpass_login():
                creds = integration.get_nas_credentials_from_protonpass()
        except ImportError:
            pass
        if not creds:
            return 1
    logger.info(
        "Retrieved NAS credentials from ProtonPass CLI (username masked, length %d)",
        len(creds.get("username", "")),
    )

    if args.dry_run:
        logger.info("Dry run: not writing to Azure Key Vault")
        return 0

    try:
        client = get_vault_client()
        client.set_secret("nas-username", creds["username"])
        logger.info("Set nas-username in Azure Key Vault")
        client.set_secret("nas-password", creds["password"])
        logger.info("Set nas-password in Azure Key Vault")
        ip_suffix = args.nas_ip.replace(".", "-")
        client.set_secret(f"nas-username-{ip_suffix}", creds["username"])
        client.set_secret(f"nas-password-{ip_suffix}", creds["password"])
        logger.info(
            "Set nas-username-%s and nas-password-%s in Azure Key Vault", ip_suffix, ip_suffix
        )
        logger.info("NAS credentials synced from ProtonPass to Azure Key Vault (Triad Tier 1).")
        return 0
    except Exception as e:  # vault write / permission / network
        logger.error("Failed to write to Azure Key Vault: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
