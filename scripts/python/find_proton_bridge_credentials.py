#!/usr/bin/env python3
"""
Find Proton Bridge Credentials
Searches ProtonPassCli and Azure Vault to find where credentials are actually stored.

Tags: #PROTONBRIDGE #CREDENTIALS #FIND #DISCOVERY
@JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from protonpass_manager import ProtonPassManager
    PROTONPASS_AVAILABLE = True
except ImportError:
    PROTONPASS_AVAILABLE = False
    ProtonPassManager = None

try:
    from azure_service_bus_integration import AzureKeyVaultClient
    AZURE_VAULT_AVAILABLE = True
except ImportError:
    try:
        from azure_key_vault_client import AzureKeyVaultClient
        AZURE_VAULT_AVAILABLE = True
    except ImportError:
        AZURE_VAULT_AVAILABLE = False
        AzureKeyVaultClient = None

logger = get_logger("FindProtonBridgeCredentials")


class ProtonBridgeCredentialFinder:
    """Find where Proton Bridge credentials are actually stored"""

    def __init__(self):
        """Initialize finder"""
        self.protonpass_manager = None
        self.azure_vault = None

        # Initialize ProtonPassCli
        if PROTONPASS_AVAILABLE:
            try:
                self.protonpass_manager = ProtonPassManager()
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize ProtonPassCli: {e}")

        # Initialize Azure Key Vault
        if AZURE_VAULT_AVAILABLE:
            try:
                self.azure_vault = AzureKeyVaultClient(
                    vault_url="https://jarvis-lumina.vault.azure.net/"
                )
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize Azure Key Vault: {e}")

    def search_protonpasscli(self) -> List[Dict[str, Any]]:
        """Search ProtonPassCli for Bridge-related entries"""
        logger.info("🔍 Searching ProtonPassCli...")

        found = []

        if not self.protonpass_manager or not self.protonpass_manager.cli_available:
            logger.warning("⚠️  ProtonPassCli not available")
            return found

        try:
            # List all entries
            entries = self.protonpass_manager.list_passwords()

            # Search for Bridge-related entries
            search_terms = ["proton", "bridge", "mail", "imap", "smtp"]

            for entry in entries:
                name = entry.get("name", "").lower()
                url = entry.get("url", "").lower()
                note = entry.get("note", "").lower()

                # Check if entry matches search terms
                if any(term in name or term in url or term in note for term in search_terms):
                    found.append({
                        "source": "protonpasscli",
                        "name": entry.get("name"),
                        "username": entry.get("username"),
                        "has_password": bool(entry.get("password")),
                        "url": entry.get("url"),
                        "note": entry.get("note")
                    })

            if found:
                logger.info(f"✅ Found {len(found)} Bridge-related entries in ProtonPassCli")
                for entry in found:
                    logger.info(f"   • {entry['name']} (username: {entry.get('username', 'N/A')})")
            else:
                logger.info("   No Bridge-related entries found in ProtonPassCli")

        except Exception as e:
            logger.error(f"❌ Error searching ProtonPassCli: {e}")

        return found

    def search_azure_vault(self) -> List[Dict[str, Any]]:
        """Search Azure Vault for Bridge-related secrets"""
        logger.info("🔍 Searching Azure Key Vault...")

        found = []

        if not self.azure_vault:
            logger.warning("⚠️  Azure Key Vault not available")
            return found

        # Common secret name patterns to try
        secret_patterns = [
            "proton",
            "bridge",
            "protonmail",
            "proton-bridge",
            "protonmail-bridge",
            "proton-bridge-username",
            "proton-bridge-password",
            "proton-bridge-mlesn",
            "proton-bridge-glesn"
        ]

        # Try to list secrets (if API supports it) or try common names
        for pattern in secret_patterns:
            try:
                # Try different variations
                variations = [
                    pattern,
                    f"{pattern}-username",
                    f"{pattern}-password",
                    f"{pattern}-mlesn",
                    f"{pattern}-glesn"
                ]

                for secret_name in variations:
                    try:
                        secret_value = self.azure_vault.get_secret(secret_name)
                        if secret_value:
                            found.append({
                                "source": "azure_vault",
                                "secret_name": secret_name,
                                "has_value": True,
                                "value_length": len(secret_value)
                            })
                            logger.info(f"✅ Found secret: {secret_name} (length: {len(secret_value)})")
                    except Exception:
                        continue  # Secret doesn't exist, try next
            except Exception as e:
                logger.debug(f"   Pattern {pattern} not found: {e}")

        if not found:
            logger.info("   No Bridge-related secrets found in Azure Vault")
            logger.info("   💡 Note: Azure Vault doesn't support listing all secrets")
            logger.info("   💡 You may need to check manually in Azure Portal")

        return found

    def find_all_credentials(self) -> Dict[str, Any]:
        """Find all Proton Bridge credentials"""
        logger.info("=" * 80)
        logger.info("🔍 FINDING PROTON BRIDGE CREDENTIALS")
        logger.info("=" * 80)
        logger.info("")

        results = {
            "protonpasscli": [],
            "azure_vault": [],
            "recommendations": []
        }

        # Search ProtonPassCli
        results["protonpasscli"] = self.search_protonpasscli()
        logger.info("")

        # Search Azure Vault
        results["azure_vault"] = self.search_azure_vault()
        logger.info("")

        # Generate recommendations
        if results["protonpasscli"]:
            logger.info("✅ Credentials found in ProtonPassCli")
            results["recommendations"].append(
                f"Use ProtonPassCli entry: {results['protonpasscli'][0]['name']}"
            )

        if results["azure_vault"]:
            logger.info("✅ Credentials found in Azure Vault")
            results["recommendations"].append(
                f"Use Azure Vault secret: {results['azure_vault'][0]['secret_name']}"
            )

        if not results["protonpasscli"] and not results["azure_vault"]:
            logger.warning("⚠️  No credentials found in ProtonPassCli or Azure Vault")
            results["recommendations"].append(
                "Store credentials using: python scripts/python/get_proton_bridge_credentials.py --store"
            )

        # Summary
        logger.info("=" * 80)
        logger.info("📊 SEARCH SUMMARY")
        logger.info("=" * 80)
        logger.info(f"ProtonPassCli entries found: {len(results['protonpasscli'])}")
        logger.info(f"Azure Vault secrets found: {len(results['azure_vault'])}")
        logger.info("")

        if results["recommendations"]:
            logger.info("💡 Recommendations:")
            for rec in results["recommendations"]:
                logger.info(f"   • {rec}")

        logger.info("=" * 80)

        return results


def main():
    try:
        """Main execution"""
        import argparse
        import json

        parser = argparse.ArgumentParser(description="Find Proton Bridge Credentials")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        finder = ProtonBridgeCredentialFinder()
        results = finder.find_all_credentials()

        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            # Already printed by find_all_credentials
            pass

        return 0 if (results["protonpasscli"] or results["azure_vault"]) else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    exit(main())