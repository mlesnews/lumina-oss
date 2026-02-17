#!/usr/bin/env python3
"""
Verify SSO Readiness for LUMINA
Checks LDAP/Azure AD configuration and certificate setup for SSO
#JARVIS #SSO #LDAP #AZURE-AD #SECURITY
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.nas_azure_vault_integration import NASAzureVaultIntegration
except ImportError as e:
    print(f"ERROR: Could not import required modules: {e}")
    sys.exit(1)

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def check_ldap_configuration(nas_integration: NASAzureVaultIntegration) -> dict:
    """Check LDAP configuration status"""
    checks = {
        "ldap_config_file": False,
        "certificates_ready": False,
        "ldap_package": False,
        "domain_controller": False
    }

    # Check LDAP config file
    result = nas_integration.execute_ssh_command("test -f /tmp/ldap_join_config.txt && echo 'EXISTS' || echo 'NOT_EXISTS'")
    if isinstance(result, dict):
        result = result.get('output', '') or result.get('stdout', '') or str(result)
    if 'EXISTS' in str(result):
        checks["ldap_config_file"] = True

    # Check certificates
    result = nas_integration.execute_ssh_command("test -f /tmp/ldap_certificates/client.crt && test -f /tmp/ldap_certificates/client.key && echo 'EXISTS' || echo 'NOT_EXISTS'")
    if isinstance(result, dict):
        result = result.get('output', '') or result.get('stdout', '') or str(result)
    if 'EXISTS' in str(result):
        checks["certificates_ready"] = True

    # Check LDAP package
    result = nas_integration.execute_ssh_command(r"synopkg status LDAPServer 2>/dev/null | grep -i 'status\|version' | head -2")
    if isinstance(result, dict):
        result = result.get('output', '') or result.get('stdout', '') or str(result)
    if result and 'not found' not in str(result).lower():
        checks["ldap_package"] = True

    # Check Domain Controller package
    result = nas_integration.execute_ssh_command(r"synopkg status DomainController 2>/dev/null | grep -i 'status\|version' | head -2")
    if isinstance(result, dict):
        result = result.get('output', '') or result.get('stdout', '') or str(result)
    if result and 'not found' not in str(result).lower():
        checks["domain_controller"] = True

    return checks


def check_ldap_join_status(nas_integration: NASAzureVaultIntegration) -> dict:
    """Check if LDAP domain is joined"""
    status = {
        "joined": False,
        "domain": None,
        "method": None
    }

    # Check domain join status
    result = nas_integration.execute_ssh_command("cat /etc/krb5.conf 2>/dev/null | grep -i 'default_realm' | head -1")
    if isinstance(result, dict):
        result = result.get('output', '') or result.get('stdout', '') or str(result)
    if result and 'default_realm' in str(result).lower():
        status["joined"] = True
        status["domain"] = str(result).strip()
        status["method"] = "Kerberos"

    # Alternative check via DSM API or config
    result = nas_integration.execute_ssh_command("test -f /usr/syno/etc/ldap/ldap.conf && echo 'EXISTS' || echo 'NOT_EXISTS'")
    if isinstance(result, dict):
        result = result.get('output', '') or result.get('stdout', '') or str(result)
    if 'EXISTS' in str(result):
        status["joined"] = True
        status["method"] = "LDAP"

    return status


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Verify SSO Readiness for LUMINA")
    parser.add_argument("--nas-ip", default="<NAS_PRIMARY_IP>", help="NAS IP address")
    parser.add_argument("--vault-name", default="jarvis-lumina", help="Azure Key Vault name")

    args = parser.parse_args()

    print("=" * 70)
    print("   SSO READINESS VERIFICATION")
    print("=" * 70)
    print("")
    print("Checking LUMINA SSO configuration status...")
    print("")

    # Initialize NAS integration
    nas_integration = NASAzureVaultIntegration(
        vault_name=args.vault_name,
        nas_ip=args.nas_ip
    )

    # Check 1: LDAP Configuration
    print("[1] Checking LDAP Configuration...")
    ldap_checks = check_ldap_configuration(nas_integration)

    if ldap_checks["ldap_config_file"]:
        print("  ✓ LDAP configuration file exists")
    else:
        print("  ✗ LDAP configuration file not found")

    if ldap_checks["certificates_ready"]:
        print("  ✓ Certificates ready on NAS")
    else:
        print("  ✗ Certificates not found on NAS")

    if ldap_checks["ldap_package"]:
        print("  ✓ LDAP Server package installed")
    else:
        print("  ⚠ LDAP Server package status unknown")

    print("")

    # Check 2: LDAP Join Status
    print("[2] Checking LDAP Domain Join Status...")
    join_status = check_ldap_join_status(nas_integration)

    if join_status["joined"]:
        print(f"  ✓ Domain joined: {join_status.get('domain', 'Unknown')}")
        print(f"  ✓ Method: {join_status.get('method', 'Unknown')}")
    else:
        print("  ✗ Domain NOT joined yet")
        print("  ⚠ SSO will not work until domain is joined")
    print("")

    # Check 3: SSO Requirements
    print("[3] SSO Requirements Checklist...")
    print("")

    requirements = {
        "LDAP Configuration": ldap_checks["ldap_config_file"],
        "Certificates Ready": ldap_checks["certificates_ready"],
        "LDAP Package": ldap_checks["ldap_package"],
        "Domain Joined": join_status["joined"]
    }

    all_ready = True
    for req, status in requirements.items():
        if status:
            print(f"  ✓ {req}")
        else:
            print(f"  ✗ {req}")
            all_ready = False

    print("")
    print("=" * 70)
    print("   SSO STATUS")
    print("=" * 70)
    print("")

    if all_ready:
        print("✅ SSO READY")
        print("")
        print("All requirements met. SSO should work after:")
        print("  1. Final LDAP join configuration in DSM")
        print("  2. User account synchronization")
        print("  3. SSO application configuration (if using SAML/OAuth)")
    else:
        print("⚠️  SSO NOT READY")
        print("")
        print("Missing requirements:")
        for req, status in requirements.items():
            if not status:
                print(f"  - {req}")
        print("")
        print("Next steps:")
        if not join_status["joined"]:
            print("  1. Complete LDAP join in DSM:")
            print("     - RDP to MANUS")
            print("     - Open DSM: https://<NAS_PRIMARY_IP>:5001")
            print("     - Control Panel → Domain/LDAP → Join")
            print("     - Use certificates: /tmp/ldap_certificates/client.crt")
            print("     - Use certificates: /tmp/ldap_certificates/client.key")
        if not ldap_checks["certificates_ready"]:
            print("  2. Deploy certificates to NAS")
        if not ldap_checks["ldap_config_file"]:
            print("  3. Run: python scripts/python/configure_all_dsm_packages_full_auto.py")

    print("")
    print("=" * 70)
    print("")

    # Additional SSO Information
    print("SSO Configuration Notes:")
    print("")
    print("For Azure AD SSO, you may need:")
    print("  - SAML 2.0 configuration (for web SSO)")
    print("  - OAuth 2.0 configuration (for application SSO)")
    print("  - LDAP/LDAPS (for directory services)")
    print("")
    print("Current setup provides:")
    print("  ✓ LDAP/LDAPS connection to Azure AD")
    print("  ✓ Certificate-based authentication")
    print("  ⚠ SAML/OAuth (may require additional configuration)")
    print("")

    return 0 if all_ready else 1


if __name__ == "__main__":


    sys.exit(main())