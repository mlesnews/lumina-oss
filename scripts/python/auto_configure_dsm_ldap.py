#!/usr/bin/env python3
"""
Automatically configure DSM LDAP/Azure AD
Attempts to find configuration and configure via DSM API or SSH
"""

import sys
import json
import requests
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


def get_azure_ad_info_from_azure_cli() -> Optional[Dict[str, str]]:
    """Try to get Azure AD info from Azure CLI"""
    import subprocess

    try:
        # Get current subscription/tenant
        result = subprocess.run(
            ["az", "account", "show"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            account_info = json.loads(result.stdout)
            tenant_id = account_info.get("tenantId")

            # Try to get tenant details
            tenant_result = subprocess.run(
                ["az", "ad", "tenant", "show", "--tenant", tenant_id],
                capture_output=True,
                text=True,
                timeout=10
            )

            if tenant_result.returncode == 0:
                tenant_info = json.loads(tenant_result.stdout)
                domain = tenant_info.get("defaultDomain")

                if domain:
                    return {
                        "tenant_id": tenant_id,
                        "domain": domain,
                        "base_dn": ",".join([f"DC={part}" for part in domain.split(".")]),
                        "server": f"ldaps://{domain}:636"
                    }
    except Exception as e:
        logger.debug(f"Could not get Azure AD info from CLI: {e}")

    return None


def configure_via_dsm_api(
    nas_ip: str,
    username: str,
    password: str,
    ldap_config: Dict[str, Any]
) -> bool:
    """Configure LDAP via DSM Web API"""

    try:
        # Step 1: Login to DSM
        session = requests.Session()
        login_url = f"http://{nas_ip}:5000/webapi/auth.cgi"

        login_params = {
            "api": "SYNO.API.Auth",
            "version": "3",
            "method": "login",
            "account": username,
            "passwd": password,
            "session": "LDAPConfig",
            "format": "sid"
        }

        logger.info("Attempting DSM API login...")
        response = session.get(login_url, params=login_params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                sid = data.get("data", {}).get("sid")
                logger.info("DSM API login successful")

                # Step 2: Configure LDAP (if API available)
                # Note: DSM LDAP configuration may require web interface
                # This is a placeholder for API-based configuration

                return True
            else:
                logger.warning("DSM API login failed")
        else:
            logger.warning(f"DSM API login returned status {response.status_code}")

    except Exception as e:
        logger.warning(f"DSM API configuration not available: {e}")

    return False


def configure_via_ssh(
    nas_ip: str,
    ldap_config: Dict[str, Any],
    vault_name: str = "jarvis-lumina"
) -> bool:
    """Configure LDAP via SSH commands"""

    try:
        nas_integration = NASAzureVaultIntegration(
            vault_name=vault_name,
            nas_ip=nas_ip
        )

        # Create LDAP configuration file
        config_script = f"""
# Create LDAP configuration
cat > /tmp/ldap_config.json << 'EOF'
{json.dumps(ldap_config, indent=2)}
EOF

echo "LDAP configuration saved to /tmp/ldap_config.json"
echo ""
echo "Configuration:"
echo "  Domain: {ldap_config.get('domain', 'NOT_SET')}"
echo "  Server: {ldap_config.get('server', 'NOT_SET')}"
echo "  Base DN: {ldap_config.get('base_dn', 'NOT_SET')}"
echo ""
echo "Note: LDAP join must be done via DSM web interface"
echo "  Control Panel -> Domain/LDAP -> Join"
"""

        result = nas_integration.execute_ssh_command(config_script)
        logger.info("LDAP configuration file created on NAS")

        return True

    except Exception as e:
        logger.error(f"SSH configuration failed: {e}")
        return False


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Auto-configure DSM LDAP/Azure AD")
    parser.add_argument("--nas-ip", default="<NAS_PRIMARY_IP>", help="NAS IP address")
    parser.add_argument("--vault-name", default="jarvis-lumina", help="Azure Key Vault name")
    parser.add_argument("--domain", help="Azure AD domain (auto-detected if not provided)")
    parser.add_argument("--server", help="LDAP server URL")
    parser.add_argument("--base-dn", help="Base DN")
    parser.add_argument("--bind-dn", help="Bind DN")
    parser.add_argument("--password", help="Bind password (or use Key Vault)")

    args = parser.parse_args()

    print("=" * 70)
    print("   AUTO-CONFIGURE DSM LDAP / AZURE ACTIVE DIRECTORY")
    print("=" * 70)
    print("")

    # Step 1: Get Azure AD configuration
    print("[1] Getting Azure AD configuration...")
    ldap_config = {}

    # Try Azure CLI first
    azure_info = get_azure_ad_info_from_azure_cli()
    if azure_info:
        print("  ✓ Found Azure AD info from Azure CLI")
        ldap_config.update(azure_info)
    else:
        print("  ⚠ Could not auto-detect Azure AD info")

    # Override with command line arguments
    if args.domain:
        ldap_config["domain"] = args.domain
        if not ldap_config.get("base_dn"):
            ldap_config["base_dn"] = ",".join([f"DC={part}" for part in args.domain.split(".")])
        if not ldap_config.get("server"):
            ldap_config["server"] = f"ldaps://{args.domain}:636"

    if args.server:
        ldap_config["server"] = args.server
    if args.base_dn:
        ldap_config["base_dn"] = args.base_dn
    if args.bind_dn:
        ldap_config["bind_dn"] = args.bind_dn
    if args.password:
        ldap_config["password"] = args.password

    # Try to get password from Key Vault
    if not ldap_config.get("password"):
        try:
            vault_url = f"https://{args.vault_name}.vault.azure.net/"
            vault_client = AzureKeyVaultClient(vault_url)

            for secret_name in ["azure-ad-ldap-password", "ldap-password"]:
                try:
                    password = vault_client.get_secret(secret_name)
                    ldap_config["password"] = password
                    print(f"  ✓ Retrieved password from Key Vault: {secret_name}")
                    break
                except:
                    continue
        except Exception as e:
            logger.debug(f"Could not get password from Key Vault: {e}")

    # Set default bind DN if not provided
    if not ldap_config.get("bind_dn") and ldap_config.get("base_dn"):
        # Common pattern: CN=admin,CN=Users,{base_dn}
        ldap_config["bind_dn"] = f"CN=admin,CN=Users,{ldap_config['base_dn']}"

    print("")
    print("Configuration:")
    for key, value in ldap_config.items():
        if key != "password":
            print(f"  {key}: {value}")
        else:
            print(f"  {key}: [REDACTED]" if value else f"  {key}: NOT_SET")

    print("")

    # Step 2: Configure via SSH
    print("[2] Configuring via SSH...")
    ssh_success = configure_via_ssh(args.nas_ip, ldap_config, args.vault_name)

    if ssh_success:
        print("  ✓ Configuration file created on NAS")
    else:
        print("  ⚠ SSH configuration had issues")

    print("")

    # Step 3: Open DSM for final configuration
    print("[3] Opening DSM for LDAP join...")
    import webbrowser
    dsm_url = f"http://{args.nas_ip}:5000"
    webbrowser.open(dsm_url)
    print(f"  ✓ DSM opened: {dsm_url}")
    print("")

    # Step 4: Provide instructions
    print("=" * 70)
    print("   FINAL CONFIGURATION STEPS")
    print("=" * 70)
    print("")
    print("1. In DSM (browser opened):")
    print("   Control Panel -> Domain/LDAP -> Join")
    print("")
    print("2. Select: 'Active Directory' or 'LDAP'")
    print("")
    print("3. Enter configuration:")
    print(f"   Domain: {ldap_config.get('domain', 'yourdomain.onmicrosoft.com')}")
    print(f"   Server: {ldap_config.get('server', 'ldaps://yourdomain.com:636')}")
    print(f"   Port: 636")
    print(f"   Base DN: {ldap_config.get('base_dn', 'DC=yourdomain,DC=onmicrosoft,DC=com')}")
    print(f"   Bind DN: {ldap_config.get('bind_dn', 'CN=admin,CN=Users,DC=yourdomain,DC=onmicrosoft,DC=com')}")
    print(f"   Password: {'(set)' if ldap_config.get('password') else '(enter manually)'}")
    print("")
    print("4. Click: 'Join'")
    print("")
    print("=" * 70)
    print("")

    # Save configuration for reference
    config_file = project_root / "config" / "dsm_ldap_config.json"
    config_file.parent.mkdir(parents=True, exist_ok=True)

    # Don't save password in plain text
    save_config = {k: v for k, v in ldap_config.items() if k != "password"}
    save_config["password_source"] = "Key Vault or manual entry"

    with open(config_file, "w") as f:
        json.dump(save_config, f, indent=2)

    print(f"Configuration saved to: {config_file}")
    print("")


if __name__ == "__main__":


    main()