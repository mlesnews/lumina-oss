#!/usr/bin/env python3
"""
Get Proton Bridge Credentials
Retrieves Proton Bridge credentials from ProtonPassCli and/or Azure Key Vault.

Priority:
1. ProtonPassCli (primary source)
2. Azure Key Vault (fallback/redundancy)

Tags: #PROTONBRIDGE #CREDENTIALS #PROTONPASS #AZUREVAULT
@JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

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

logger = get_logger("GetProtonBridgeCredentials")


class ProtonBridgeCredentialManager:
    """Manage Proton Bridge credentials from ProtonPassCli and Azure Vault"""

    def __init__(self):
        """Initialize credential manager"""
        self.protonpass_manager = None
        self.azure_vault = None

        # Initialize ProtonPassCli
        if PROTONPASS_AVAILABLE:
            try:
                self.protonpass_manager = ProtonPassManager()
                if self.protonpass_manager.cli_available:
                    logger.info("✅ ProtonPassCli available")
                else:
                    logger.warning("⚠️  ProtonPassCli not available")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize ProtonPassCli: {e}")

        # Initialize Azure Key Vault
        if AZURE_VAULT_AVAILABLE:
            try:
                self.azure_vault = AzureKeyVaultClient(
                    vault_url="https://jarvis-lumina.vault.azure.net/"
                )
                logger.info("✅ Azure Key Vault available")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize Azure Key Vault: {e}")

    def get_bridge_password(self, account_name: str = "mlesn") -> Optional[str]:
        """
        Get Proton Bridge password from ProtonPassCli or Azure Vault

        Args:
            account_name: Name of the credential entry (default: "proton-bridge")

        Returns:
            Password string or None if not found
        """
        logger.info(f"🔐 Retrieving Proton Bridge password for: {account_name}")

        # Try ProtonPassCli first (primary source)
        if self.protonpass_manager and self.protonpass_manager.cli_available:
            try:
                # Try common entry names (based on actual config files)
                entry_names = [
                    f"proton-bridge-{account_name}-password",  # e.g., proton-bridge-mlesn-password
                    f"proton-bridge-{account_name}",  # e.g., proton-bridge-mlesn
                    "proton-bridge-password",
                    "protonmail-bridge-password",
                    "proton-bridge",
                    "protonmail-bridge",
                    account_name
                ]

                for entry_name in entry_names:
                    result = self.protonpass_manager.get_password(entry_name)
                    if result and result.get("password"):
                        password = result["password"]
                        logger.info(f"✅ Retrieved password from ProtonPassCli: {entry_name}")
                        return password

                logger.warning("⚠️  Password not found in ProtonPassCli")
            except Exception as e:
                logger.warning(f"⚠️  Error retrieving from ProtonPassCli: {e}")

        # Fallback to Azure Key Vault
        if self.azure_vault:
            try:
                # Try secret names based on actual config files
                secret_names = [
                    f"proton-bridge-{account_name}-password",  # e.g., proton-bridge-mlesn-password (from proton_bridge_accounts.json)
                    f"proton-bridge-{account_name}",  # e.g., proton-bridge-mlesn
                    "protonmail-bridge-password",  # from proton_family_integration.json
                    "proton-bridge-password",
                    "proton-bridge-username-password",
                    "protonmail-password",  # from protonbridge_config.json
                    account_name
                ]

                for secret_name in secret_names:
                    try:
                        password = self.azure_vault.get_secret(secret_name)
                        if password:
                            logger.info(f"✅ Retrieved password from Azure Vault: {secret_name}")
                            return password
                    except Exception:
                        continue

                logger.warning("⚠️  Password not found in Azure Key Vault")
            except Exception as e:
                logger.warning(f"⚠️  Error retrieving from Azure Vault: {e}")

        logger.error("❌ Could not retrieve password from ProtonPassCli or Azure Vault")
        return None

    def get_bridge_username(self, account_name: str = "mlesn") -> Optional[str]:
        """
        Get Proton Bridge username from ProtonPassCli or Azure Vault

        Args:
            account_name: Name of the credential entry

        Returns:
            Username string or None if not found
        """
        logger.info(f"👤 Retrieving Proton Bridge username for: {account_name}")

        # Try ProtonPassCli first
        if self.protonpass_manager and self.protonpass_manager.cli_available:
            try:
                # Try entry names (username might be in same entry as password)
                entry_names = [
                    f"proton-bridge-{account_name}-password",  # Username might be in password entry
                    f"proton-bridge-{account_name}",
                    "proton-bridge-password",
                    "protonmail-bridge-password",
                    "proton-bridge",
                    "protonmail-bridge",
                    account_name
                ]

                for entry_name in entry_names:
                    result = self.protonpass_manager.get_password(entry_name, show_details=True)
                    if result:
                        # Try username field first
                        if result.get("username"):
                            username = result["username"]
                            logger.info(f"✅ Retrieved username from ProtonPassCli: {entry_name}")
                            return username
                        # If no username field, the entry name might be the username
                        # Or username might be the ProtonMail email address

                logger.warning("⚠️  Username not found in ProtonPassCli")
            except Exception as e:
                logger.warning(f"⚠️  Error retrieving username from ProtonPassCli: {e}")

        # Fallback to Azure Vault
        if self.azure_vault:
            try:
                # Try secret names based on actual config files
                secret_names = [
                    f"proton-bridge-{account_name}-username",  # e.g., proton-bridge-mlesn-username
                    f"proton-bridge-{account_name}",  # e.g., proton-bridge-mlesn
                    "protonmail-username",  # from protonbridge_config.json
                    "protonmail-email",  # alternative name
                    "proton-bridge-username",
                    "proton-account-username",  # from proton_family_integration.json
                    account_name
                ]

                for secret_name in secret_names:
                    try:
                        username = self.azure_vault.get_secret(secret_name)
                        if username:
                            logger.info(f"✅ Retrieved username from Azure Vault: {secret_name}")
                            return username
                    except Exception:
                        continue

                logger.warning("⚠️  Username not found in Azure Key Vault")
            except Exception as e:
                logger.warning(f"⚠️  Error retrieving username from Azure Vault: {e}")

        logger.error("❌ Could not retrieve username from ProtonPassCli or Azure Vault")
        return None

    def get_bridge_credentials(self, account_name: str = "mlesn") -> Dict[str, Any]:
        """
        Get complete Proton Bridge credentials

        Args:
            account_name: Name of the credential entry

        Returns:
            Dictionary with username, password, and metadata
        """
        logger.info("=" * 80)
        logger.info("🔐 RETRIEVING PROTON BRIDGE CREDENTIALS")
        logger.info("=" * 80)

        credentials = {
            "username": None,
            "password": None,
            "source": None,
            "timestamp": datetime.now().isoformat(),
            "account_name": account_name
        }

        # Get username
        username = self.get_bridge_username(account_name)
        if username:
            credentials["username"] = username

        # Get password
        password = self.get_bridge_password(account_name)
        if password:
            credentials["password"] = password

        # Determine source
        if self.protonpass_manager and self.protonpass_manager.cli_available:
            credentials["source"] = "protonpasscli"
        elif self.azure_vault:
            credentials["source"] = "azure_vault"
        else:
            credentials["source"] = "none"

        # Summary
        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 CREDENTIAL RETRIEVAL SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Username: {'✅ Found' if credentials['username'] else '❌ Not Found'}")
        logger.info(f"Password: {'✅ Found' if credentials['password'] else '❌ Not Found'}")
        logger.info(f"Source: {credentials['source']}")
        logger.info("=" * 80)

        return credentials

    def store_bridge_credentials(self, username: str, password: str, 
                                 account_name: str = "proton-bridge",
                                 store_in_protonpass: bool = True,
                                 store_in_azure_vault: bool = True) -> Dict[str, bool]:
        """
        Store Proton Bridge credentials in ProtonPassCli and/or Azure Vault

        Args:
            username: Bridge username
            password: Bridge password
            account_name: Name for the credential entry
            store_in_protonpass: Whether to store in ProtonPassCli
            store_in_azure_vault: Whether to store in Azure Vault

        Returns:
            Dictionary with storage results
        """
        logger.info("=" * 80)
        logger.info("💾 STORING PROTON BRIDGE CREDENTIALS")
        logger.info("=" * 80)

        results = {
            "protonpass": False,
            "azure_vault": False
        }

        # Store in ProtonPassCli
        if store_in_protonpass and self.protonpass_manager and self.protonpass_manager.cli_available:
            try:
                entry_name = f"proton-bridge-{account_name}"
                success = self.protonpass_manager.create_password(
                    name=entry_name,
                    username=username,
                    password=password,
                    url="protonmail://bridge",
                    note=f"Proton Bridge credentials for {account_name}"
                )
                if success:
                    results["protonpass"] = True
                    logger.info(f"✅ Stored in ProtonPassCli: {entry_name}")
                else:
                    logger.warning("⚠️  Failed to store in ProtonPassCli")
            except Exception as e:
                logger.error(f"❌ Error storing in ProtonPassCli: {e}")

        # Store in Azure Vault
        if store_in_azure_vault and self.azure_vault:
            try:
                # Store username
                username_secret = f"proton-bridge-{account_name}-username"
                self.azure_vault.set_secret(username_secret, username)
                logger.info(f"✅ Stored username in Azure Vault: {username_secret}")

                # Store password
                password_secret = f"proton-bridge-{account_name}-password"
                self.azure_vault.set_secret(password_secret, password)
                logger.info(f"✅ Stored password in Azure Vault: {password_secret}")

                results["azure_vault"] = True
            except Exception as e:
                logger.error(f"❌ Error storing in Azure Vault: {e}")

        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 STORAGE SUMMARY")
        logger.info("=" * 80)
        logger.info(f"ProtonPassCli: {'✅ Stored' if results['protonpass'] else '❌ Failed'}")
        logger.info(f"Azure Vault: {'✅ Stored' if results['azure_vault'] else '❌ Failed'}")
        logger.info("=" * 80)

        return results


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Get Proton Bridge Credentials")
        parser.add_argument("--account-name", default="mlesn",
                           help="Account name for credential lookup (mlesn or glesn)")
        parser.add_argument("--username-only", action="store_true",
                           help="Retrieve username only")
        parser.add_argument("--password-only", action="store_true",
                           help="Retrieve password only")
        parser.add_argument("--store", action="store_true",
                           help="Store credentials (requires --username and --password)")
        parser.add_argument("--username", help="Username to store")
        parser.add_argument("--password", help="Password to store")

        args = parser.parse_args()

        manager = ProtonBridgeCredentialManager()

        if args.store:
            if not args.username or not args.password:
                logger.error("❌ --store requires --username and --password")
                return 1

            results = manager.store_bridge_credentials(
                username=args.username,
                password=args.password,
                account_name=args.account_name
            )

            if results["protonpass"] or results["azure_vault"]:
                return 0
            else:
                return 1
        else:
            if args.username_only:
                username = manager.get_bridge_username(args.account_name)
                if username:
                    print(username)
                    return 0
                else:
                    return 1
            elif args.password_only:
                password = manager.get_bridge_password(args.account_name)
                if password:
                    print(password)
                    return 0
                else:
                    return 1
            else:
                credentials = manager.get_bridge_credentials(args.account_name)
                if credentials["username"] and credentials["password"]:
                    # Output as JSON for scripts
                    import json
                    print(json.dumps(credentials, indent=2))
                    return 0
                else:
                    return 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    exit(main())