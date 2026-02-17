#!/usr/bin/env python3
"""
Automate DSM LDAP Domain Join via Browser
Uses browser automation to configure LDAP in DSM web interface
#JARVIS #LDAP #AUTOMATION #BROWSER
"""

import sys
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, Optional

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_ldap_config(vault_name: str = "jarvis-lumina") -> Dict[str, str]:
    """Get LDAP configuration from Azure Key Vault"""
    import platform
    config = {}
    is_windows = platform.system() == "Windows"

    try:
        # Get username
        result = subprocess.run(
            ["az", "keyvault", "secret", "show", "--vault-name", vault_name,
             "--name", "ldap-service-username", "--query", "value", "-o", "tsv"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=is_windows
        )
        if result.returncode == 0:
            config["username"] = result.stdout.strip()

        # Get password
        result = subprocess.run(
            ["az", "keyvault", "secret", "show", "--vault-name", vault_name,
             "--name", "ldap-service-password", "--query", "value", "-o", "tsv"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=is_windows
        )
        if result.returncode == 0:
            config["password"] = result.stdout.strip()

        # Get domain
        result = subprocess.run(
            ["az", "account", "show", "--query", "tenantDefaultDomain", "-o", "tsv"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=is_windows
        )
        if result.returncode == 0:
            domain = result.stdout.strip()
            config["domain"] = domain
            # Generate Base DN
            parts = domain.split(".")
            config["base_dn"] = ",".join([f"DC={part}" for part in parts])

    except Exception as e:
        logger.error(f"Failed to get configuration: {e}")

    return config


def print_configuration_guide(config: Dict[str, str], nas_ip: str = "<NAS_PRIMARY_IP>"):
    """Print step-by-step configuration guide"""

    print("=" * 70)
    print("   DSM LDAP DOMAIN JOIN - CONFIGURATION GUIDE")
    print("=" * 70)
    print("")
    print("📋 Configuration Details:")
    print("")
    print(f"  Domain: {config.get('domain', 'NOT_SET')}")
    print(f"  Base DN: {config.get('base_dn', 'NOT_SET')}")
    print(f"  Username: {config.get('username', 'NOT_SET')}")
    print(f"  Password: {'*' * len(config.get('password', '')) if config.get('password') else 'NOT_SET'}")
    print(f"  Certificates: C:\\Users\\mlesn\\Desktop\\ldap_client.crt / .key")
    print("")
    print("=" * 70)
    print("   STEP-BY-STEP INSTRUCTIONS")
    print("=" * 70)
    print("")
    print("1. Open DSM Web Interface:")
    print(f"   https://{nas_ip}:5001")
    print("")
    print("2. Navigate to LDAP Configuration:")
    print("   Control Panel → Domain/LDAP → Join")
    print("")
    print("3. Select Profile Type:")
    print("   ✅ Custom (for Azure AD)")
    print("")
    print("4. Basic Settings:")
    print(f"   Domain/LDAP Server: {config.get('domain', 'yourdomain.onmicrosoft.com')}")
    print(f"   Base DN: {config.get('base_dn', 'DC=domain,DC=onmicrosoft,DC=com')}")
    print("   Port: 636")
    print("   Enable SSL/TLS: ✅ CHECKED")
    print("")
    print("5. Authentication:")
    print("   Option A (Recommended): Certificate-Based")
    print("   - Use Client Certificate: ✅ CHECKED")
    print("   - Certificate: C:\\Users\\mlesn\\Desktop\\ldap_client.crt")
    print("   - Private Key: C:\\Users\\mlesn\\Desktop\\ldap_client.key")
    print("")
    print("   Option B (Fallback): Username/Password")
    print(f"   - Username: {config.get('username', 'username@domain.onmicrosoft.com')}")
    print(f"   - Password: {config.get('password', 'YOUR_PASSWORD')}")
    print("")
    print("6. Custom Profile Attribute Mapping:")
    print("   User Base DN: CN=Users,{base_dn}".format(base_dn=config.get('base_dn', 'DC=domain,DC=onmicrosoft,DC=com')))
    print("   User Filter: (&(objectClass=user)(objectCategory=person))")
    print("   User ID Attribute: userPrincipalName")
    print("   User Name Attribute: displayName")
    print("   User Email Attribute: mail")
    print("")
    print("   Group Base DN: CN=Users,{base_dn}".format(base_dn=config.get('base_dn', 'DC=domain,DC=onmicrosoft,DC=com')))
    print("   Group Filter: (&(objectClass=group)(objectCategory=group))")
    print("   Group Name Attribute: cn")
    print("")
    print("7. Test Connection:")
    print("   Click 'Test Connection' button")
    print("   Wait for verification")
    print("")
    print("8. Join Domain:")
    print("   Click 'Apply' or 'Join' button")
    print("   Wait for join process (1-2 minutes)")
    print("")
    print("=" * 70)
    print("")
    print("💡 TIP: Keep this window open for reference while configuring DSM")
    print("")


def open_dsm_in_browser(nas_ip: str = "<NAS_PRIMARY_IP>"):
    try:
        """Open DSM in default browser"""
        import webbrowser
        url = f"https://{nas_ip}:5001"
        print(f"🌐 Opening DSM in browser: {url}")
        webbrowser.open(url)
        print("")


    except Exception as e:
        logger.error(f"Error in open_dsm_in_browser: {e}", exc_info=True)
        raise
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Automate DSM LDAP domain join")
    parser.add_argument("--nas-ip", default="<NAS_PRIMARY_IP>", help="NAS IP address")
    parser.add_argument("--vault-name", default="jarvis-lumina", help="Azure Key Vault name")
    parser.add_argument("--open-browser", action="store_true", help="Open DSM in browser")
    args = parser.parse_args()

    print("")
    print("🔧 Retrieving LDAP configuration from Azure Key Vault...")
    print("")

    config = get_ldap_config(args.vault_name)

    if not config.get("username") or not config.get("password"):
        print("❌ ERROR: Could not retrieve credentials from Key Vault")
        print("")
        print("Please ensure the following secrets exist in Key Vault:")
        print(f"  - ldap-service-username")
        print(f"  - ldap-service-password")
        print("")
        return 1

    if not config.get("domain"):
        print("❌ ERROR: Could not determine Azure AD domain")
        print("")
        return 1

    print("✅ Configuration retrieved successfully")
    print("")

    # Print configuration guide
    print_configuration_guide(config, args.nas_ip)

    # Open browser if requested
    if args.open_browser:
        open_dsm_in_browser(args.nas_ip)
        print("⏳ Waiting 5 seconds for browser to open...")
        time.sleep(5)

    print("=" * 70)
    print("   READY TO CONFIGURE")
    print("=" * 70)
    print("")
    print("Follow the instructions above to configure LDAP in DSM.")
    print("")
    print("After configuration, verify with:")
    print(f"  python scripts/python/verify_sso_readiness.py --nas-ip {args.nas_ip} --vault-name {args.vault_name}")
    print("")

    return 0


if __name__ == "__main__":


    sys.exit(main())