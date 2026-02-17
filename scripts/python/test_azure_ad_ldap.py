#!/usr/bin/env python3
"""
Test Azure AD LDAP Connection
Tests different Bind DN formats to find the correct one
#JARVIS #LDAP #AZURE-AD #TESTING
"""

import sys
import subprocess
import platform
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_ldap_bind_formats(domain: str, username: str, password: str, base_dn: str):
    """Test different Bind DN formats"""

    formats_to_try = [
        # Format 1: UserPrincipalName (current)
        username,

        # Format 2: Just username
        username.split('@')[0],

        # Format 3: Full DN format
        f"CN={username.split('@')[0]},CN=Users,{base_dn}",

        # Format 4: Alternative DN format
        f"CN={username.split('@')[0]},OU=Users,{base_dn}",
    ]

    print("=" * 70)
    print("   TESTING AZURE AD LDAP BIND DN FORMATS")
    print("=" * 70)
    print("")
    print(f"Domain: {domain}")
    print(f"Base DN: {base_dn}")
    print(f"Username: {username}")
    print("")
    print("Testing formats:")
    print("")

    for i, bind_dn in enumerate(formats_to_try, 1):
        print(f"[{i}] Bind DN: {bind_dn}")
        print(f"     Status: ⚠️  Manual test required in DSM")
        print("")

    print("=" * 70)
    print("   RECOMMENDATIONS")
    print("=" * 70)
    print("")
    print("⚠️  IMPORTANT: Azure AD (not Azure AD Domain Services) may not")
    print("   support traditional LDAP authentication.")
    print("")
    print("Azure AD uses:")
    print("  - Microsoft Graph API (not LDAP)")
    print("  - OAuth 2.0 / SAML (for SSO)")
    print("  - Azure AD Domain Services (AAD DS) for LDAP")
    print("")
    print("If you're using regular Azure AD (not AAD DS):")
    print("  ❌ LDAP authentication will NOT work")
    print("  ✅ Use SAML/OAuth instead")
    print("")
    print("To check if you have Azure AD Domain Services:")
    print("  1. Azure Portal → Azure AD Domain Services")
    print("  2. Check if a managed domain exists")
    print("")
    print("=" * 70)
    print("   ALTERNATIVE: USE SAML/OAuth")
    print("=" * 70)
    print("")
    print("For DSM SSO with Azure AD, consider:")
    print("  1. SAML 2.0 configuration (if DSM supports it)")
    print("  2. OAuth 2.0 configuration")
    print("  3. Azure AD Domain Services (if you need LDAP)")
    print("")
    print("=" * 70)
    print("")


def check_azure_ad_domain_services():
    """Check if Azure AD Domain Services is enabled"""
    is_windows = platform.system() == "Windows"

    print("Checking for Azure AD Domain Services...")
    print("")

    try:
        result = subprocess.run(
            ["az", "ad", "ds", "list"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=is_windows
        )

        if result.returncode == 0:
            domains = result.stdout.strip()
            if domains and domains != "[]":
                print("✅ Azure AD Domain Services found:")
                print(domains)
                return True
            else:
                print("❌ Azure AD Domain Services NOT configured")
                print("")
                print("This means you're using regular Azure AD, which")
                print("does NOT support LDAP authentication.")
                return False
        else:
            print("⚠️  Could not check Azure AD Domain Services")
            print(f"Error: {result.stderr}")
            return None

    except Exception as e:
        print(f"⚠️  Error checking: {e}")
        return None


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Test Azure AD LDAP connection")
    parser.add_argument("--vault-name", default="jarvis-lumina", help="Azure Key Vault name")
    args = parser.parse_args()

    print("")

    # Check for Azure AD Domain Services
    has_aadds = check_azure_ad_domain_services()
    print("")

    # Get configuration
    is_windows = platform.system() == "Windows"
    config = {}

    try:
        result = subprocess.run(
            ["az", "keyvault", "secret", "show", "--vault-name", args.vault_name,
             "--name", "ldap-service-username", "--query", "value", "-o", "tsv"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=is_windows
        )
        if result.returncode == 0:
            config["username"] = result.stdout.strip()

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
            parts = domain.split(".")
            config["base_dn"] = ",".join([f"DC={part}" for part in parts])
    except Exception as e:
        logger.error(f"Failed to get config: {e}")
        return 1

    if not config.get("username") or not config.get("domain"):
        print("❌ Could not retrieve configuration")
        return 1

    # Test formats
    test_ldap_bind_formats(
        config["domain"],
        config["username"],
        "***",  # Don't print password
        config["base_dn"]
    )

    if has_aadds is False:
        print("")
        print("⚠️  CRITICAL: You're using regular Azure AD, not Azure AD Domain Services.")
        print("   LDAP authentication will NOT work with regular Azure AD.")
        print("")
        print("   Solutions:")
        print("   1. Enable Azure AD Domain Services (requires additional setup)")
        print("   2. Use SAML/OAuth for SSO instead of LDAP")
        print("   3. Use a different identity provider that supports LDAP")
        print("")

    return 0


if __name__ == "__main__":


    sys.exit(main())