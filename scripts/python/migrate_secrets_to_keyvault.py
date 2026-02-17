#!/usr/bin/env python3
"""
Migrate secrets to Azure Key Vault

Scans for secrets in config files and environment variables,
then migrates them to Azure Key Vault.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

try:
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential
    KEY_VAULT_AVAILABLE = True
except ImportError:
    KEY_VAULT_AVAILABLE = False
    print("Warning: Azure Key Vault SDK not installed")
    print("Install with: pip install azure-keyvault-secrets azure-identity")

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SecretMigration")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def get_secrets_from_config(project_root: Path) -> Dict[str, str]:
    """Scan config files for secrets"""
    secrets = {}

    # Check common config locations
    config_files = [
        project_root / "config" / "llm_api_keys.json",
        project_root / ".env",
        project_root / ".env.local",
    ]

    for config_file in config_files:
        if config_file.exists():
            try:
                if config_file.suffix == ".json":
                    with open(config_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Look for common secret keys
                        for key in ['api_key', 'apiKey', 'token', 'secret', 'password']:
                            if key in data:
                                secret_name = f"{config_file.stem}-{key}"
                                secrets[secret_name] = str(data[key])
                elif config_file.name.startswith(".env"):
                    with open(config_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if '=' in line and not line.strip().startswith('#'):
                                key, value = line.strip().split('=', 1)
                                if any(secret_word in key.lower() for secret_word in ['key', 'token', 'secret', 'password']):
                                    secrets[key] = value
            except Exception as e:
                logger.warning(f"Error reading {config_file}: {e}")

    return secrets


def get_secrets_from_env() -> Dict[str, str]:
    """Get secrets from environment variables"""
    secrets = {}

    # Common secret environment variables
    secret_patterns = ['API_KEY', 'TOKEN', 'SECRET', 'PASSWORD', 'CONNECTION_STRING']

    for key, value in os.environ.items():
        if any(pattern in key.upper() for pattern in secret_patterns):
            secrets[key] = value

    return secrets


def migrate_to_keyvault(
    vault_url: str,
    secrets: Dict[str, str],
    dry_run: bool = True
) -> Dict[str, bool]:
    """
    Migrate secrets to Azure Key Vault

    Args:
        vault_url: Key Vault URL
        secrets: Dictionary of secret names to values
        dry_run: If True, only simulate migration

    Returns:
        Dictionary of secret names to success status
    """
    results = {}

    if not KEY_VAULT_AVAILABLE:
        logger.error("Azure Key Vault SDK not available")
        return results

    if dry_run:
        logger.info("DRY RUN MODE - No secrets will be migrated")
        for secret_name, secret_value in secrets.items():
            logger.info(f"  Would migrate: {secret_name} (length: {len(secret_value)})")
            results[secret_name] = True
        return results

    try:
        credential = DefaultAzureCredential(

                            exclude_interactive_browser_credential=False,

                            exclude_shared_token_cache_credential=False

                        )
        client = SecretClient(vault_url=vault_url, credential=credential)

        for secret_name, secret_value in secrets.items():
            try:
                # Sanitize secret name (Key Vault has naming restrictions)
                safe_name = secret_name.replace(' ', '-').replace('_', '-').lower()
                safe_name = ''.join(c for c in safe_name if c.isalnum() or c == '-')

                client.set_secret(safe_name, secret_value)
                logger.info(f"  [OK] Migrated: {safe_name}")
                results[secret_name] = True
            except Exception as e:
                logger.error(f"  [FAIL] Failed to migrate {secret_name}: {e}")
                results[secret_name] = False

    except Exception as e:
        logger.error(f"Failed to connect to Key Vault: {e}")
        logger.error("Make sure you're logged in: az login")

    return results


def main():
    try:
        """Main execution"""
        script_path = Path(__file__).resolve()
        project_root = script_path.parent.parent.parent

        print("=" * 60)
        print("Secret Migration to Azure Key Vault")
        print("=" * 60)
        print(f"Project Root: {project_root}\n")

        # Get vault URL
        vault_url = os.getenv("AZURE_KEY_VAULT_URL")
        if not vault_url:
            vault_name = os.getenv("AZURE_KEY_VAULT_NAME", "jarvis-lumina")
            vault_url = f"https://{vault_name}.vault.azure.net/"

        print(f"Key Vault URL: {vault_url}\n")

        # Collect secrets
        print("[1] Collecting secrets from config files...")
        config_secrets = get_secrets_from_config(project_root)
        print(f"  Found {len(config_secrets)} secrets in config files")

        print("\n[2] Collecting secrets from environment variables...")
        env_secrets = get_secrets_from_env()
        print(f"  Found {len(env_secrets)} secrets in environment")

        # Combine
        all_secrets = {**config_secrets, **env_secrets}

        if not all_secrets:
            print("\n[INFO] No secrets found to migrate")
            print("  This could mean:")
            print("    - Secrets are already in Key Vault")
            print("    - Secrets are in files not scanned")
            print("    - No secrets are configured yet")
            return

        # Dry run first
        print("\n[3] Dry run migration...")
        dry_run_results = migrate_to_keyvault(vault_url, all_secrets, dry_run=True)

        # Ask for confirmation
        print("\n" + "=" * 60)
        print(f"Ready to migrate {len(all_secrets)} secrets")
        print("=" * 60)
        response = input("\nProceed with migration? (yes/no): ").strip().lower()

        if response != 'yes':
            print("Migration cancelled")
            return

        # Actual migration
        print("\n[4] Migrating secrets to Key Vault...")
        results = migrate_to_keyvault(vault_url, all_secrets, dry_run=False)

        # Summary
        print("\n" + "=" * 60)
        print("Migration Summary")
        print("=" * 60)
        successful = sum(1 for v in results.values() if v)
        failed = len(results) - successful

        print(f"Total: {len(results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")

        if successful > 0:
            print("\n[SUCCESS] Secrets migrated to Azure Key Vault")
            print("\nNext Steps:")
            print("  1. Update code to retrieve secrets from Key Vault")
            print("  2. Remove secrets from config files")
            print("  3. Remove secrets from environment variables")

        if failed > 0:
            print(f"\n[WARNING] {failed} secrets failed to migrate")
            print("  Review errors above and retry")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()