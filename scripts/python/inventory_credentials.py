#!/usr/bin/env python3
"""
Credential Inventory Script

Scans and inventories all credentials in the system for rotation management.
Identifies credentials in Azure Key Vault, ProtonPass, and code/config files.

Author: LUMINA Security Team
Date: 2025-01-24
Tags: @MARVIN @HK-47 @JARVIS
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from scripts.python.unified_secret_manager import UnifiedSecretManager, SecretCategory
    from scripts.python.password_rotation_manager import PasswordRotationManager, CredentialPriority
except ImportError:
    UnifiedSecretManager = None
    PasswordRotationManager = None
    SecretCategory = None
    CredentialPriority = None


class CredentialInventory:
    """Credential inventory manager"""

    def __init__(self, project_root: Optional[Path] = None):
        self.logger = get_logger("CredentialInventory")
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.inventory_file = self.project_root / "data" / "security" / "credential_inventory.json"
        self.inventory_file.parent.mkdir(parents=True, exist_ok=True)

        self.unified_secret_manager = None
        if UnifiedSecretManager:
            try:
                self.unified_secret_manager = UnifiedSecretManager(project_root=self.project_root)
            except Exception as e:
                self.logger.warning(f"Could not initialize UnifiedSecretManager: {e}")

    def inventory_azure_key_vault(self) -> List[Dict[str, Any]]:
        """Inventory credentials from Azure Key Vault"""
        credentials = []

        if not self.unified_secret_manager or not self.unified_secret_manager.azure_vault:
            self.logger.warning("Azure Key Vault not available")
            return credentials

        try:
            secret_names = self.unified_secret_manager.azure_vault.list_secrets()
            for secret_name in secret_names:
                credentials.append({
                    "name": secret_name,
                    "source": "azure_key_vault",
                    "storage_location": "azure_key_vault",
                    "security_level": self._infer_security_level(secret_name),
                    "category": self._infer_category(secret_name)
                })

            self.logger.info(f"Found {len(credentials)} credentials in Azure Key Vault")
        except Exception as e:
            self.logger.error(f"Error inventorying Azure Key Vault: {e}")

        return credentials

    def inventory_protonpass(self) -> List[Dict[str, Any]]:
        """Inventory credentials from ProtonPass"""
        credentials = []

        if not self.unified_secret_manager or not self.unified_secret_manager.proton_pass:
            self.logger.warning("ProtonPass not available")
            return credentials

        try:
            entries = self.unified_secret_manager.proton_pass.list_passwords()
            for entry in entries:
                name = entry.get("name", "")
                credentials.append({
                    "name": name,
                    "source": "protonpass",
                    "storage_location": "protonpass",
                    "security_level": self._infer_security_level(name),
                    "category": self._infer_category(name)
                })

            self.logger.info(f"Found {len(credentials)} credentials in ProtonPass")
        except Exception as e:
            self.logger.error(f"Error inventorying ProtonPass: {e}")

        return credentials

    def _infer_security_level(self, secret_name: str) -> str:
        """Infer security level from secret name"""
        name_lower = secret_name.lower()

        # Critical
        if any(term in name_lower for term in ["master", "root", "admin", "encryption-key", "vault-access"]):
            return "critical"

        # High priority
        if any(term in name_lower for term in ["api-key", "api_key", "token", "database", "connection"]):
            return "high_priority"

        # Standard (default)
        return "standard"

    def _infer_category(self, secret_name: str) -> str:
        """Infer category from secret name"""
        name_lower = secret_name.lower()

        if "api-key" in name_lower or "api_key" in name_lower:
            return "api_key"
        if "token" in name_lower:
            return "token"
        if "password" in name_lower or "credential" in name_lower:
            return "credential"

        return "credential"  # Default

    def create_inventory(self) -> Dict[str, Any]:
        try:
            """Create comprehensive credential inventory"""
            self.logger.info("🔍 Starting credential inventory...")

            inventory = {
                "version": "1.0.0",
                "inventory_date": datetime.now().isoformat(),
                "credentials": [],
                "summary": {
                    "total_credentials": 0,
                    "by_source": {},
                    "by_security_level": {},
                    "by_category": {}
                }
            }

            # Inventory from Azure Key Vault
            azure_creds = self.inventory_azure_key_vault()
            inventory["credentials"].extend(azure_creds)

            # Inventory from ProtonPass
            protonpass_creds = self.inventory_protonpass()
            inventory["credentials"].extend(protonpass_creds)

            # Generate summary
            inventory["summary"]["total_credentials"] = len(inventory["credentials"])
            inventory["summary"]["by_source"] = self._count_by_field(inventory["credentials"], "source")
            inventory["summary"]["by_security_level"] = self._count_by_field(inventory["credentials"], "security_level")
            inventory["summary"]["by_category"] = self._count_by_field(inventory["credentials"], "category")

            # Save inventory
            with open(self.inventory_file, 'w', encoding='utf-8') as f:
                json.dump(inventory, f, indent=2, ensure_ascii=False)

            self.logger.info(f"✅ Inventory created: {inventory['summary']['total_credentials']} credentials found")
            self.logger.info(f"   Saved to: {self.inventory_file}")

            return inventory

        except Exception as e:
            self.logger.error(f"Error in create_inventory: {e}", exc_info=True)
            raise
    def _count_by_field(self, credentials: List[Dict], field: str) -> Dict[str, int]:
        """Count credentials by field"""
        counts = {}
        for cred in credentials:
            value = cred.get(field, "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts

    def register_with_rotation_manager(self) -> int:
        """Register all inventoried credentials with PasswordRotationManager"""
        if not PasswordRotationManager:
            self.logger.warning("PasswordRotationManager not available")
            return 0

        if not self.inventory_file.exists():
            self.logger.warning("Inventory file not found, create inventory first")
            return 0

        try:
            with open(self.inventory_file, 'r', encoding='utf-8') as f:
                inventory = json.load(f)

            rotation_manager = PasswordRotationManager(project_root=self.project_root)

            # Map security level to priority
            priority_map = {
                "critical": CredentialPriority.CRITICAL,
                "high_priority": CredentialPriority.HIGH_PRIORITY,
                "standard": CredentialPriority.STANDARD,
                "low_priority": CredentialPriority.LOW_PRIORITY
            }

            registered_count = 0
            for cred in inventory.get("credentials", []):
                try:
                    security_level = cred.get("security_level", "standard")
                    priority = priority_map.get(security_level, CredentialPriority.STANDARD)
                    storage_location = cred.get("storage_location", "azure_key_vault")

                    rotation_manager.register_credential(
                        name=cred["name"],
                        priority=priority,
                        storage_location=storage_location
                    )
                    registered_count += 1
                except Exception as e:
                    self.logger.warning(f"Could not register credential '{cred.get('name')}': {e}")

            self.logger.info(f"✅ Registered {registered_count} credentials with PasswordRotationManager")
            return registered_count

        except Exception as e:
            self.logger.error(f"Error registering credentials: {e}")
            return 0


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Credential Inventory")
    parser.add_argument("--inventory", action="store_true", help="Create credential inventory")
    parser.add_argument("--register", action="store_true", help="Register with rotation manager")
    parser.add_argument("--all", action="store_true", help="Create inventory and register")

    args = parser.parse_args()

    inventory_tool = CredentialInventory()

    if args.inventory or args.all:
        result = inventory_tool.create_inventory()
        print(f"\n📋 Credential Inventory Summary")
        print(f"Total Credentials: {result['summary']['total_credentials']}")
        print(f"\nBy Source:")
        for source, count in result['summary']['by_source'].items():
            print(f"  {source}: {count}")
        print(f"\nBy Security Level:")
        for level, count in result['summary']['by_security_level'].items():
            print(f"  {level}: {count}")

    if args.register or args.all:
        count = inventory_tool.register_with_rotation_manager()
        print(f"\n✅ Registered {count} credentials with PasswordRotationManager")

    if not any([args.inventory, args.register, args.all]):
        parser.print_help()


if __name__ == "__main__":

    main()