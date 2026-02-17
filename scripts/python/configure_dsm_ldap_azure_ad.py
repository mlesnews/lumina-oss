#!/usr/bin/env python3
"""
Configure DSM LDAP/Azure Active Directory Integration
Retrieves configuration from Azure Key Vault and configures DSM
"""

import sys
import json
from pathlib import Path
from typing import Dict, Optional, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.nas_azure_vault_integration import NASAzureVaultIntegration
    from scripts.python.azure_service_bus_integration import AzureKeyVaultClient
except ImportError as e:
    print(f"ERROR: Could not import required modules: {e}")
    sys.exit(1)

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def get_azure_ad_config(vault_name: str = "jarvis-lumina") -> Dict[str, Any]:
    """
    Retrieve Azure AD LDAP configuration from Azure Key Vault

    Returns:
        Dictionary with Azure AD configuration
    """
    config = {}

    try:
        vault_url = f"https://{vault_name}.vault.azure.net/"
        vault_client = AzureKeyVaultClient(vault_url)

        # Try to get Azure AD configuration secrets
        secrets_to_check = [
            "azure-ad-domain",
            "azure-ad-ldap-server",
            "azure-ad-base-dn",
            "azure-ad-bind-dn",
            "azure-ad-ldap-password",
            "azure-ad-tenant-id",
            "ldap-server-url",
            "ldap-base-dn",
            "ldap-bind-dn",
            "ldap-password"
        ]

        for secret_name in secrets_to_check:
            try:
                secret_value = vault_client.get_secret(secret_name)
                # Map to standard names
                if "domain" in secret_name:
                    config["domain"] = secret_value
                elif "server" in secret_name or "url" in secret_name:
                    config["server"] = secret_value
                elif "base-dn" in secret_name:
                    config["base_dn"] = secret_value
                elif "bind-dn" in secret_name:
                    config["bind_dn"] = secret_value
                elif "password" in secret_name:
                    config["password"] = secret_value
                elif "tenant" in secret_name:
                    config["tenant_id"] = secret_value

                logger.info(f"Retrieved {secret_name} from Key Vault")
            except Exception as e:
                logger.debug(f"Secret {secret_name} not found: {e}")
                continue

    except Exception as e:
        logger.warning(f"Could not retrieve from Key Vault: {e}")

    return config


def configure_dsm_ldap(
    nas_ip: str,
    azure_ad_config: Dict[str, Any],
    vault_name: str = "jarvis-lumina"
) -> bool:
    """
    Configure DSM LDAP/Azure AD via SSH

    Args:
        nas_ip: NAS IP address
        azure_ad_config: Azure AD configuration dictionary
        vault_name: Azure Key Vault name

    Returns:
        True if configuration successful
    """
    try:
        nas_integration = NASAzureVaultIntegration(
            vault_name=vault_name,
            nas_ip=nas_ip
        )

        # Check if LDAP package is installed
        logger.info("Checking LDAP package status...")
        check_cmd = "synopkg status LDAPServer 2>/dev/null || synopkg status DomainController 2>/dev/null || echo 'NOT_INSTALLED'"
        result = nas_integration.execute_ssh_command(check_cmd)

        if "NOT_INSTALLED" in result:
            logger.warning("LDAP package not installed. Install via Package Center.")
            return False

        logger.info("LDAP package is installed")

        # Create configuration script
        config_script = f"""
# DSM LDAP/Azure AD Configuration
# This script prepares configuration for DSM web interface

echo "=== Azure AD LDAP Configuration ==="
echo ""
echo "Domain: {azure_ad_config.get('domain', 'NOT_SET')}"
echo "Server: {azure_ad_config.get('server', 'NOT_SET')}"
echo "Base DN: {azure_ad_config.get('base_dn', 'NOT_SET')}"
echo "Bind DN: {azure_ad_config.get('bind_dn', 'NOT_SET')}"
echo ""
echo "Configuration will be done via DSM web interface:"
echo "  Control Panel -> Domain/LDAP -> Join"
echo ""
"""

        result = nas_integration.execute_ssh_command(config_script)
        logger.info("Configuration script executed")

        return True

    except Exception as e:
        logger.error(f"Error configuring DSM LDAP: {e}")
        return False


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Configure DSM LDAP/Azure AD")
    parser.add_argument("--nas-ip", default="<NAS_PRIMARY_IP>", help="NAS IP address")
    parser.add_argument("--vault-name", default="jarvis-lumina", help="Azure Key Vault name")
    parser.add_argument("--domain", help="Azure AD domain (overrides Key Vault)")
    parser.add_argument("--server", help="LDAP server URL (overrides Key Vault)")
    parser.add_argument("--base-dn", help="Base DN (overrides Key Vault)")
    parser.add_argument("--bind-dn", help="Bind DN (overrides Key Vault)")

    args = parser.parse_args()

    print("=" * 70)
    print("   CONFIGURE DSM LDAP / AZURE ACTIVE DIRECTORY")
    print("=" * 70)
    print("")

    # Get Azure AD configuration
    print("[1] Retrieving Azure AD configuration from Key Vault...")
    azure_ad_config = get_azure_ad_config(args.vault_name)

    # Override with command line arguments if provided
    if args.domain:
        azure_ad_config["domain"] = args.domain
    if args.server:
        azure_ad_config["server"] = args.server
    if args.base_dn:
        azure_ad_config["base_dn"] = args.base_dn
    if args.bind_dn:
        azure_ad_config["bind_dn"] = args.bind_dn

    if azure_ad_config:
        print("  ✓ Configuration retrieved from Key Vault")
        for key, value in azure_ad_config.items():
            if key != "password":
                print(f"    {key}: {value}")
            else:
                print(f"    {key}: [REDACTED]")
    else:
        print("  ⚠ No configuration found in Key Vault")
        print("  Provide configuration manually or add to Key Vault")

    print("")

    # Configure DSM
    print("[2] Configuring DSM LDAP...")
    success = configure_dsm_ldap(args.nas_ip, azure_ad_config, args.vault_name)

    if success:
        print("  ✓ Configuration prepared")
    else:
        print("  ⚠ Manual configuration required")

    print("")
    print("=" * 70)
    print("   CONFIGURATION INSTRUCTIONS")
    print("=" * 70)
    print("")
    print("1. Open DSM: http://{}:5000".format(args.nas_ip))
    print("2. Control Panel -> Domain/LDAP")
    print("3. Click: 'Join'")
    print("4. Select: 'Active Directory' or 'LDAP'")
    print("5. Enter configuration:")
    print("   - Domain: {}".format(azure_ad_config.get("domain", "yourdomain.onmicrosoft.com")))
    print("   - Server: {}".format(azure_ad_config.get("server", "ldaps://yourdomain.com:636")))
    print("   - Port: 636 (LDAPS)")
    print("   - Base DN: {}".format(azure_ad_config.get("base_dn", "DC=yourdomain,DC=onmicrosoft,DC=com")))
    print("   - Bind DN: {}".format(azure_ad_config.get("bind_dn", "CN=admin,CN=Users,DC=yourdomain,DC=onmicrosoft,DC=com")))
    print("   - Password: (from Key Vault)")
    print("6. Click: 'Join'")
    print("")
    print("=" * 70)
    print("")


if __name__ == "__main__":


    main()