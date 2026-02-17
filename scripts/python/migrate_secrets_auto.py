#!/usr/bin/env python3
"""
Auto-migrate secrets to Azure Key Vault (non-interactive)

This version automatically migrates secrets without prompting for confirmation.
Use with caution - ensure you have proper backups.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict

# Add scripts/python to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from migrate_secrets_to_keyvault import (
    get_secrets_from_config,
    get_secrets_from_env,
    migrate_to_keyvault
)
from universal_decision_tree import decide, DecisionContext, DecisionOutcome


# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def main():
    """Main execution - auto-migrate without prompts"""
    print("=" * 60)
    print("Auto Secret Migration to Azure Key Vault")
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
        return

    # Migrate (dry run first)
    print("\n[3] Dry run migration...")
    dry_run_results = migrate_to_keyvault(vault_url, all_secrets, dry_run=True)

    # Actual migration
    print(f"\n[4] Migrating {len(all_secrets)} secrets to Key Vault...")
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

if __name__ == "__main__":



    main()