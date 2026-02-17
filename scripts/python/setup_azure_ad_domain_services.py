#!/usr/bin/env python3
"""
Setup Azure AD Domain Services for DSM LDAP
Automates AAD DS deployment and configuration
#JARVIS #AZURE-AD #AAD-DS #LDAP #AUTOMATION
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


def check_prerequisites():
    """Check prerequisites for AAD DS setup"""
    is_windows = platform.system() == "Windows"

    print("=" * 70)
    print("   AZURE AD DOMAIN SERVICES SETUP")
    print("=" * 70)
    print("")
    print("Checking prerequisites...")
    print("")

    # Check Azure login
    try:
        result = subprocess.run(
            ["az", "account", "show"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=is_windows
        )
        if result.returncode == 0:
            account = json.loads(result.stdout)
            print(f"✅ Azure CLI logged in: {account.get('user', {}).get('name', 'Unknown')}")
            print(f"   Subscription: {account.get('name', 'Unknown')}")
            print(f"   Tenant: {account.get('tenantDefaultDomain', 'Unknown')}")
        else:
            print("❌ Not logged in to Azure CLI")
            print("   Run: az login")
            return False
    except Exception as e:
        print(f"❌ Error checking Azure login: {e}")
        return False

    print("")
    return True


def get_tenant_info():
    """Get Azure AD tenant information"""
    is_windows = platform.system() == "Windows"

    try:
        result = subprocess.run(
            ["az", "account", "show", "--query", "{tenantId:tenantId, tenantDefaultDomain:tenantDefaultDomain}", "-o", "json"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=is_windows
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        logger.error(f"Failed to get tenant info: {e}")

    return None


def print_setup_instructions(tenant_info):
    """Print setup instructions"""
    domain = tenant_info.get("tenantDefaultDomain", "yourdomain.onmicrosoft.com")
    tenant_id = tenant_info.get("tenantId", "")

    print("=" * 70)
    print("   SETUP INSTRUCTIONS")
    print("=" * 70)
    print("")
    print("Azure AD Domain Services setup requires manual steps in Azure Portal.")
    print("")
    print("Step 1: Enable Azure AD Domain Services")
    print("")
    print("  1. Azure Portal → Search 'Azure AD Domain Services'")
    print("  2. Click 'Create' or 'Add'")
    print("  3. Configure:")
    print(f"     - DNS Domain Name: {domain}")
    print("     - Region: eastus (or closest to you)")
    print("     - Resource Group: Create new 'aadds-rg'")
    print("     - Virtual Network: Create new or select existing")
    print("     - Subnet: Create dedicated subnet (e.g., 10.0.1.0/24)")
    print("")
    print("  4. Administrator Group:")
    print("     - AAD DC Administrators: Select or create group")
    print("     - Add your account to this group")
    print("")
    print("  5. Review and Create")
    print("  6. Wait 20-30 minutes for deployment")
    print("")
    print("Step 2: Get LDAP Endpoint")
    print("")
    print("  After deployment:")
    print("  1. Azure Portal → Azure AD Domain Services")
    print("  2. Properties tab")
    print("  3. Note LDAP Endpoint:")
    print(f"     Format: ldaps://{domain}:636")
    print("")
    print("Step 3: Configure Network Connectivity")
    print("")
    print("  Option A: VPN Connection")
    print("    - Create Site-to-Site VPN")
    print("    - Configure on-premises router")
    print("")
    print("  Option B: ExpressRoute (Enterprise)")
    print("    - Set up ExpressRoute")
    print("")
    print("Step 4: Configure DSM")
    print("")
    print("  DSM → Control Panel → Domain/LDAP → Join")
    print(f"  - Domain/LDAP Server: {domain}")
    print(f"  - Base DN: DC={domain.split('.')[0]},DC={domain.split('.')[1]},DC={domain.split('.')[2]}")
    print("  - Port: 636")
    print("  - Enable SSL/TLS: ✅")
    print("  - Bind DN: ldapadm@{domain}".format(domain=domain))
    print("  - Password: [from Key Vault]")
    print("")
    print("=" * 70)
    print("   COST ESTIMATE")
    print("=" * 70)
    print("")
    print("  AAD DS: ~$100-200/month (depends on region)")
    print("  VPN Gateway: ~$30-100/month (if using VPN)")
    print("  Data Transfer: Variable")
    print("")
    print("=" * 70)
    print("")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Setup Azure AD Domain Services for DSM")
    parser.add_argument("--resource-group", default="aadds-rg", help="Resource group name")
    parser.add_argument("--region", default="eastus", help="Azure region")
    parser.add_argument("--vnet-name", help="Virtual network name (creates new if not provided)")
    parser.add_argument("--subnet-name", default="aadds-subnet", help="Subnet name")
    parser.add_argument("--subnet-cidr", default="10.0.1.0/24", help="Subnet CIDR")
    args = parser.parse_args()

    print("")

    # Check prerequisites
    if not check_prerequisites():
        return 1

    # Get tenant info
    tenant_info = get_tenant_info()
    if not tenant_info:
        print("❌ Could not get tenant information")
        return 1

    print("")

    # Print setup instructions
    print_setup_instructions(tenant_info)

    print("=" * 70)
    print("   RECOMMENDATION")
    print("=" * 70)
    print("")
    print("For consistency with Azure services, enable AAD DS.")
    print("")
    print("Alternative: Use SAML SSO (free, but requires SSO Server package)")
    print("")
    print("See: docs/system/DSM_SAML_SSO_SETUP_GUIDE.md")
    print("")
    print("=" * 70)
    print("")

    return 0


if __name__ == "__main__":


    sys.exit(main())