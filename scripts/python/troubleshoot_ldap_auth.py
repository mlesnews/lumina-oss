#!/usr/bin/env python3
"""
Troubleshoot LDAP Authentication Issues
Tests LDAP connection and authentication with Azure AD
#JARVIS #LDAP #TROUBLESHOOTING #AZURE-AD
"""

import platform
import subprocess
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_ldap_config(vault_name: str = "jarvis-lumina") -> dict:
    """Get LDAP configuration from Azure Key Vault"""
    config = {}
    is_windows = platform.system() == "Windows"

    try:
        # Get username
        result = subprocess.run(
            [
                "az",
                "keyvault",
                "secret",
                "show",
                "--vault-name",
                vault_name,
                "--name",
                "ldap-service-username",
                "--query",
                "value",
                "-o",
                "tsv",
            ],
            capture_output=True,
            text=True,
            timeout=10,
            shell=is_windows,
        )
        if result.returncode == 0:
            config["username"] = result.stdout.strip()

        # Get password
        result = subprocess.run(
            [
                "az",
                "keyvault",
                "secret",
                "show",
                "--vault-name",
                vault_name,
                "--name",
                "ldap-service-password",
                "--query",
                "value",
                "-o",
                "tsv",
            ],
            capture_output=True,
            text=True,
            timeout=10,
            shell=is_windows,
        )
        if result.returncode == 0:
            config["password"] = result.stdout.strip()

        # Get domain
        result = subprocess.run(
            ["az", "account", "show", "--query", "tenantDefaultDomain", "-o", "tsv"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=is_windows,
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


def test_ldap_connection_ldapsearch(
    domain: str, username: str, password: str, base_dn: str
) -> bool:
    """Test LDAP connection using ldapsearch (if available)"""
    try:
        # Test LDAPS connection
        import ldap3
        from ldap3 import ALL, TLS, Connection, Server

        server = Server(f"ldaps://{domain}:636", use_ssl=True, get_info=ALL)

        # Try connection with username/password
        conn = Connection(
            server, user=username, password=password, auto_bind=True, authentication=ldap3.SIMPLE
        )

        if conn.bound:
            logger.info("✓ LDAP connection successful")
            # Try a simple search
            conn.search(
                search_base=base_dn,
                search_filter="(objectClass=*)",
                search_scope=ldap3.BASE,
                attributes=["*"],
            )
            conn.unbind()
            return True
        else:
            logger.error("✗ LDAP connection failed - not bound")
            return False

    except ImportError:
        logger.warning("ldap3 library not installed. Install with: pip install ldap3")
        return False
    except Exception as e:
        logger.error(f"✗ LDAP connection test failed: {e}")
        return False


def print_troubleshooting_guide(config: dict):
    """Print troubleshooting guide"""

    print("=" * 70)
    print("   LDAP AUTHENTICATION TROUBLESHOOTING GUIDE")
    print("=" * 70)
    print("")
    print("📋 Current Configuration:")
    print("")
    print(f"  Domain: {config.get('domain', 'NOT_SET')}")
    print(f"  Base DN: {config.get('base_dn', 'NOT_SET')}")
    print(f"  Username: {config.get('username', 'NOT_SET')}")
    print(
        f"  Password: {'*' * len(config.get('password', '')) if config.get('password') else 'NOT_SET'}"
    )
    print("")
    print("=" * 70)
    print("   COMMON AUTHENTICATION ISSUES")
    print("=" * 70)
    print("")
    print("1. ❌ Username Format Issue")
    print("   Problem: Azure AD may require different username format")
    print("   Solutions:")
    print(f"     a) Try: {config.get('username', 'username@domain.onmicrosoft.com')}")
    print(
        f"     b) Try: {config.get('username', '').split('@')[0] if '@' in config.get('username', '') else 'username'}"
    )
    print(
        f"     c) Try: CN={config.get('username', '').split('@')[0] if '@' in config.get('username', '') else 'username'},CN=Users,{config.get('base_dn', 'DC=domain,DC=onmicrosoft,DC=com')}"
    )
    print("")
    print("2. ❌ Password Issue")
    print("   Problem: Password may be incorrect or expired")
    print("   Solutions:")
    print("     a) Verify password in Azure Key Vault")
    print("     b) Try resetting password in Azure AD")
    print("     c) Check if account is locked")
    print("")
    print("3. ❌ Base DN Issue")
    print("   Problem: Base DN may be incorrect for Azure AD")
    print("   Current Base DN:")
    print(f"     {config.get('base_dn', 'NOT_SET')}")
    print("   Alternative Base DNs to try:")
    print(f"     a) CN=Users,{config.get('base_dn', 'DC=domain,DC=onmicrosoft,DC=com')}")
    print(f"     b) OU=Users,{config.get('base_dn', 'DC=domain,DC=onmicrosoft,DC=com')}")
    print("")
    print("4. ❌ Certificate Authentication Issue")
    print("   Problem: Certificate-based auth may not be working")
    print("   Solutions:")
    print("     a) Try password-based authentication first")
    print("     b) Verify certificate files exist:")
    print("        - C:\\Users\\mlesn\\Desktop\\ldap_client.crt")
    print("        - C:\\Users\\mlesn\\Desktop\\ldap_client.key")
    print("     c) Check certificate format (should be PEM)")
    print("")
    print("5. ❌ LDAP Server Address Issue")
    print("   Problem: Azure AD LDAP endpoint may be different")
    print(
        "   Current: ldaps://{domain}:636".format(
            domain=config.get("domain", "domain.onmicrosoft.com")
        )
    )
    print("   Azure AD LDAP endpoints:")
    print(
        "     - ldaps://{domain}:636 (Standard)".format(
            domain=config.get("domain", "domain.onmicrosoft.com")
        )
    )
    print(
        "     - ldap://{domain}:389 (Non-SSL - not recommended)".format(
            domain=config.get("domain", "domain.onmicrosoft.com")
        )
    )
    print("")
    print("6. ❌ Port/Firewall Issue")
    print("   Problem: Port 636 may be blocked")
    print("   Solutions:")
    print(
        "     a) Verify port 636 is open: telnet {domain} 636".format(
            domain=config.get("domain", "domain.onmicrosoft.com")
        )
    )
    print("     b) Check firewall rules")
    print("     c) Try port 389 (non-SSL) as test (not recommended for production)")
    print("")
    print("=" * 70)
    print("   DSM CONFIGURATION RECOMMENDATIONS")
    print("=" * 70)
    print("")
    print("For DSM LDAP Configuration, try these settings:")
    print("")
    print("Profile Type: Custom")
    print("")
    print("Basic Settings:")
    print(f"  Domain/LDAP Server: {config.get('domain', 'domain.onmicrosoft.com')}")
    print(f"  Base DN: {config.get('base_dn', 'DC=domain,DC=onmicrosoft,DC=com')}")
    print("  Port: 636")
    print("  Enable SSL/TLS: ✅ CHECKED")
    print("")
    print("Authentication - Try Option 1 (Password):")
    print(f"  Username: {config.get('username', 'username@domain.onmicrosoft.com')}")
    print(
        f"  Password: {'*' * len(config.get('password', '')) if config.get('password') else '(set in vault or env)'}"
    )
    print("")
    print("If Option 1 fails, try Option 2 (Certificate):")
    print("  Certificate: C:\\Users\\mlesn\\Desktop\\ldap_client.crt")
    print("  Private Key: C:\\Users\\mlesn\\Desktop\\ldap_client.key")
    print("")
    print("Custom Profile Attribute Mapping:")
    print(f"  User Base DN: CN=Users,{config.get('base_dn', 'DC=domain,DC=onmicrosoft,DC=com')}")
    print("  User Filter: (&(objectClass=user)(objectCategory=person))")
    print("  User ID Attribute: userPrincipalName")
    print("  User Name Attribute: displayName")
    print("  User Email Attribute: mail")
    print("")
    print("=" * 70)
    print("")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Troubleshoot LDAP authentication issues")
    parser.add_argument("--vault-name", default="jarvis-lumina", help="Azure Key Vault name")
    parser.add_argument("--test-connection", action="store_true", help="Test LDAP connection")
    args = parser.parse_args()

    print("")
    print("🔍 Retrieving LDAP configuration...")
    print("")

    config = get_ldap_config(args.vault_name)

    if not config.get("username") or not config.get("password"):
        print("❌ ERROR: Could not retrieve credentials from Key Vault")
        print("")
        return 1

    if not config.get("domain"):
        print("❌ ERROR: Could not determine Azure AD domain")
        print("")
        return 1

    print("✅ Configuration retrieved")
    print("")

    # Print troubleshooting guide
    print_troubleshooting_guide(config)

    # Test connection if requested
    if args.test_connection:
        print("=" * 70)
        print("   TESTING LDAP CONNECTION")
        print("=" * 70)
        print("")
        print("Testing connection to Azure AD...")
        print("")

        success = test_ldap_connection_ldapsearch(
            config["domain"], config["username"], config["password"], config["base_dn"]
        )

        if success:
            print("")
            print("✅ LDAP connection test PASSED")
        else:
            print("")
            print("❌ LDAP connection test FAILED")
            print("")
            print("See troubleshooting guide above for solutions")
        print("")

    return 0


if __name__ == "__main__":
    sys.exit(main())
