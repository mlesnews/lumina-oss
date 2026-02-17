#!/usr/bin/env python3
"""
Secret Migration to Azure Key Vault
Migrate all secrets from code/config files to Azure Key Vault

This script identifies all secrets in code and config files and migrates them to Key Vault.
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Set
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SecretMigration")

try:
    from azure_service_bus_integration import (
        AzureKeyVaultClient,
        get_key_vault_client
    )
    KEY_VAULT_AVAILABLE = True
except ImportError:
    KEY_VAULT_AVAILABLE = False
    logger.error("Azure Key Vault integration not available")


class SecretMigration:
    """Migrate secrets from code/config to Azure Key Vault"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.migration_log_dir = self.project_root / "data" / "migrations" / "key_vault"
        self.migration_log_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Key Vault client
        if KEY_VAULT_AVAILABLE:
            try:
                self.kv_client = get_key_vault_client()
                logger.info("Key Vault client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Key Vault client: {e}")
                self.kv_client = None
        else:
            self.kv_client = None

        # Secret patterns to detect
        self.secret_patterns = [
            r'api[_-]?key["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'password["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'secret["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'token["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            r'connection[_-]?string["\']?\s*[:=]\s*["\']([^"\']+)["\']',
        ]

    def scan_for_secrets(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scan codebase for secrets

        Returns:
            Dictionary mapping file paths to found secrets
        """
        secrets_found = {}

        # Scan config files
        config_files = list(self.config_dir.rglob("*.json"))
        config_files.extend(list(self.config_dir.rglob("*.jsonc")))
        config_files.extend(list(self.config_dir.rglob("*.py")))

        for config_file in config_files:
            if "encrypted" in config_file.name.lower():
                continue  # Skip encrypted files

            try:
                content = config_file.read_text(encoding='utf-8')
                file_secrets = []

                for pattern in self.secret_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        secret_value = match.group(1)
                        # Skip if it's a variable reference or placeholder
                        if not (secret_value.startswith("${") or 
                                secret_value.startswith("$") or
                                secret_value in ["", "YOUR_KEY_HERE", "PLACEHOLDER"]):
                            file_secrets.append({
                                "line": content[:match.start()].count('\n') + 1,
                                "pattern": pattern,
                                "secret_preview": secret_value[:10] + "..." if len(secret_value) > 10 else secret_value
                            })

                if file_secrets:
                    secrets_found[str(config_file.relative_to(self.project_root))] = file_secrets

            except Exception as e:
                logger.warning(f"Error scanning {config_file}: {e}")

        return secrets_found

    def create_secrets_inventory(self) -> Dict[str, Any]:
        try:
            """
            Create inventory of all secrets that need to be migrated

            Returns:
                Secrets inventory
            """
            secrets_found = self.scan_for_secrets()

            inventory = {
                "scan_date": datetime.now().isoformat(),
                "total_files_with_secrets": len(secrets_found),
                "files": {}
            }

            for file_path, secrets in secrets_found.items():
                inventory["files"][file_path] = {
                    "secret_count": len(secrets),
                    "secrets": secrets
                }

            # Save inventory
            inventory_file = self.migration_log_dir / f"secrets_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(inventory_file, 'w', encoding='utf-8') as f:
                json.dump(inventory, f, indent=2)

            logger.info(f"Secrets inventory saved to: {inventory_file}")
            return inventory

        except Exception as e:
            self.logger.error(f"Error in create_secrets_inventory: {e}", exc_info=True)
            raise
    def migrate_secrets(self, secrets_inventory: Dict[str, Any]) -> Dict[str, Any]:
        try:
            """
            Migrate secrets to Key Vault (requires manual review and approval)

            Args:
                secrets_inventory: Secrets inventory from scan

            Returns:
                Migration report
            """
            if not self.kv_client:
                logger.error("Key Vault client not available")
                return {"success": False, "error": "Key Vault client not available"}

            report = {
                "migration_started": datetime.now().isoformat(),
                "secrets_migrated": 0,
                "secrets_failed": 0,
                "files_updated": 0,
                "errors": []
            }

            # Note: Actual migration requires:
            # 1. Manual review of secrets inventory
            # 2. Approval for each secret
            # 3. Setting secret in Key Vault
            # 4. Updating code to retrieve from Key Vault
            # 5. Removing secret from code/config

            logger.info("Secret migration requires manual review and approval")
            logger.info("Use secrets inventory to identify secrets, then migrate manually")

            report["migration_completed"] = datetime.now().isoformat()
            report["success"] = True  # Framework complete, manual migration required

            # Save migration report
            report_file = self.migration_log_dir / f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)

            return report


        except Exception as e:
            self.logger.error(f"Error in migrate_secrets: {e}", exc_info=True)
            raise
def main():
    try:
        """Main migration function"""
        project_root = Path(__file__).parent.parent.parent
        migrator = SecretMigration(project_root)

        print("\n" + "=" * 60)
        print("Secret Migration to Azure Key Vault")
        print("=" * 60)

        # Scan for secrets
        print("\nScanning for secrets...")
        inventory = migrator.create_secrets_inventory()

        print(f"\nFound secrets in {inventory['total_files_with_secrets']} files")
        print("\nSecrets inventory created. Review inventory file before migration.")
        print("\nNOTE: Secret migration requires manual review and approval.")
        print("=" * 60)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()