#!/usr/bin/env python3
"""
Check Azure AD Domain Services Status
Determines if AAD DS is enabled and provides setup guidance
#JARVIS #AZURE-AD #AAD-DS #LDAP
"""

import sys
import subprocess
import platform
import json
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_aad_ds_status():
    """Check if Azure AD Domain Services is enabled"""
    is_windows = platform.system() == "Windows"

    print("=" * 70)
    print("   AZURE AD DOMAIN SERVICES STATUS CHECK")
    print("=" * 70)
    print("")
    print("Checking if Azure AD Domain Services is enabled...")
    print("")

    # Try to list AAD DS instances
    try:
        # First, try with extension enabled
        result = subprocess.run(
            ["az", "config", "set", "extension.dynamic_install_allow_preview=true"],
            capture_output=True,
            text=True,
            timeout=5,
            shell=is_windows
        )

        result = subprocess.run(
            ["az", "ad", "ds", "list", "--output", "json"],
            capture_output=True,
            text=True,
            timeout=15,
            shell=is_windows
        )

        if result.returncode == 0:
            domains = result.stdout.strip()
            if domains and domains != "[]" and domains:
                try:
                    domains_json = json.loads(domains)
                    if domains_json and len(domains_json) > 0:
                        print("✅ Azure AD Domain Services IS ENABLED")
                        print("")
                        print("Domain Services Found:")
                        for domain in domains_json:
                            print(f"  - Domain: {domain.get('domainName', 'Unknown')}")
                            print(f"    Resource Group: {domain.get('resourceGroup', 'Unknown')}")
                            print(f"    Status: {domain.get('healthStatus', 'Unknown')}")
                        print("")
                        print("✅ You can use LDAP authentication!")
                        print("")
                        print("Next Steps:")
                        print("  1. Get LDAP endpoint from Azure Portal")
                        print("  2. Configure DSM with AAD DS LDAP endpoint")
                        print("  3. Use Bind DN: ldapadm@matthewlesnewski.onmicrosoft.com")
                        return True
                except json.JSONDecodeError:
                    pass

        print("❌ Azure AD Domain Services NOT ENABLED")
        print("")
        print("This means:")
        print("  - Regular Azure AD does NOT support LDAP")
        print("  - LDAP authentication will NOT work")
        print("  - You need to enable AAD DS or use SAML/OAuth")
        print("")
        return False

    except subprocess.TimeoutExpired:
        print("⚠️  Command timed out")
        print("")
        print("Manual Check Required:")
        print("  1. Azure Portal → Azure AD Domain Services")
        print("  2. Check if a managed domain exists")
        print("")
        return None
    except Exception as e:
        print(f"⚠️  Could not check automatically: {e}")
        print("")
        print("Manual Check Required:")
        print("  1. Azure Portal → Azure AD Domain Services")
        print("  2. Check if a managed domain exists")
        print("")
        return None


def print_setup_guide():
    """Print setup guide for AAD DS"""
    print("=" * 70)
    print("   AZURE AD DOMAIN SERVICES SETUP GUIDE")
    print("=" * 70)
    print("")
    print("To enable Azure AD Domain Services:")
    print("")
    print("1. Azure Portal → Azure AD Domain Services")
    print("2. Click 'Create' or 'Add'")
    print("3. Configure:")
    print("   - Subscription: Your subscription")
    print("   - Resource Group: Create new or use existing")
    print("   - Region: Choose closest to your location")
    print("   - DNS Domain Name: matthewlesnewski.onmicrosoft.com")
    print("   - Virtual Network: Create new or select existing")
    print("")
    print("4. Review and Create (takes 20-30 minutes)")
    print("")
    print("5. After deployment:")
    print("   - Get LDAP endpoint from Azure Portal")
    print("   - Configure DSM with AAD DS endpoint")
    print("")
    print("Cost: ~$100-200/month depending on region")
    print("")
    print("=" * 70)
    print("")


def print_saml_alternative():
    """Print SAML/OAuth alternative guide"""
    print("=" * 70)
    print("   SAML/OAUTH ALTERNATIVE")
    print("=" * 70)
    print("")
    print("If you don't want to enable AAD DS, consider SAML/OAuth:")
    print("")
    print("1. Check if DSM supports SAML:")
    print("   - DSM → Control Panel → Domain/LDAP")
    print("   - Look for 'SAML' or 'SSO' options")
    print("")
    print("2. If supported, set up SAML SSO:")
    print("   - Create Azure AD App Registration")
    print("   - Configure SAML in Azure AD")
    print("   - Configure SAML in DSM")
    print("")
    print("3. Benefits:")
    print("   - No additional cost")
    print("   - Works with regular Azure AD")
    print("   - Modern, secure protocol")
    print("")
    print("=" * 70)
    print("")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Check Azure AD Domain Services status")
    args = parser.parse_args()

    print("")

    # Check status
    has_aadds = check_aad_ds_status()

    print("")

    if has_aadds is False:
        print_setup_guide()
        print("")
        print_saml_alternative()

    print("=" * 70)
    print("   RECOMMENDATION")
    print("=" * 70)
    print("")

    if has_aadds:
        print("✅ AAD DS is enabled - proceed with LDAP configuration")
    elif has_aadds is False:
        print("⚠️  AAD DS is NOT enabled")
        print("")
        print("Options:")
        print("  1. Enable Azure AD Domain Services (~$100-200/month)")
        print("  2. Use SAML/OAuth if DSM supports it (free)")
        print("  3. Use Synology Directory Server (not recommended)")
        print("")
        print("Recommendation: Enable AAD DS for consistency with Azure services")
    else:
        print("⚠️  Could not determine status automatically")
        print("")
        print("Please check manually:")
        print("  Azure Portal → Azure AD Domain Services")
        print("")

    print("=" * 70)
    print("")

    return 0


if __name__ == "__main__":


    sys.exit(main())