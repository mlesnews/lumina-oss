#!/usr/bin/env python3
"""
LDAP Certificate Setup Helper
Guides through certificate setup for DSM LDAP/Azure AD configuration
#JARVIS #LDAP #AZURE-AD #CERTIFICATES
"""

import sys
from pathlib import Path

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


def check_certificate_requirement():
    """
    Check if client certificates are required for LDAP/Azure AD

    For Azure AD LDAP:
    - Basic LDAP: Usually NO certificates needed
    - LDAPS (secure): May need server certificate
    - Mutual TLS: Requires client certificate

    DSM typically asks for certificates for:
    1. LDAPS server certificate validation
    2. Client certificate authentication (mutual TLS)
    """
    print("=" * 70)
    print("   LDAP CERTIFICATE REQUIREMENT CHECK")
    print("=" * 70)
    print("")
    print("For Azure AD LDAP configuration in DSM:")
    print("")
    print("OPTION 1: Basic LDAP (No Certificates)")
    print("  - Use port 389 (LDAP) or 636 (LDAPS)")
    print("  - Username/password authentication")
    print("  - No client certificates required")
    print("  - Recommended for most Azure AD setups")
    print("")
    print("OPTION 2: LDAPS with Server Certificate")
    print("  - Use port 636 (LDAPS)")
    print("  - May need Azure AD LDAPS certificate")
    print("  - Usually auto-validated by DSM")
    print("")
    print("OPTION 3: Mutual TLS (Client Certificates)")
    print("  - Requires client certificate + private key")
    print("  - Used for certificate-based authentication")
    print("  - Less common for Azure AD")
    print("")
    print("=" * 70)
    print("")


def get_azure_ad_certificate_info():
    """Provide information on getting certificates from Azure AD"""
    print("=" * 70)
    print("   GETTING CERTIFICATES FROM AZURE AD")
    print("=" * 70)
    print("")
    print("If you need client certificates for Azure AD:")
    print("")
    print("1. Azure Portal → Azure Active Directory")
    print("2. App registrations → Your app")
    print("3. Certificates & secrets")
    print("4. Upload certificate or create new")
    print("5. Download certificate (.cer) and export private key (.pfx)")
    print("")
    print("Convert PFX to PEM format:")
    print("  openssl pkcs12 -in certificate.pfx -nocerts -out client.key -nodes")
    print("  openssl pkcs12 -in certificate.pfx -clcerts -nokeys -out client.crt")
    print("")
    print("=" * 70)
    print("")


def create_certificate_skip_script():
    """Create script to configure LDAP without certificates"""
    script_content = '''#!/usr/bin/env python3
"""
Configure LDAP/Azure AD WITHOUT client certificates
Uses basic LDAP authentication (username/password)
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.python.nas_azure_vault_integration import NASAzureVaultIntegration

def main():
    nas_ip = "<NAS_PRIMARY_IP>"
    vault_name = "jarvis-lumina"

    print("=" * 70)
    print("   LDAP CONFIGURATION (NO CERTIFICATES)")
    print("=" * 70)
    print("")
    print("This will configure LDAP/Azure AD using basic authentication")
    print("(username/password) without client certificates.")
    print("")
    print("Configuration:")
    print("  - Domain: matthewlesnewski.onmicrosoft.com")
    print("  - Port: 636 (LDAPS)")
    print("  - Authentication: Username/Password")
    print("  - Certificates: Not required")
    print("")
    print("To proceed with certificate-free configuration:")
    print("1. Run: python scripts/python/configure_all_dsm_packages_full_auto.py")
    print("2. In DSM: Control Panel → Domain/LDAP → Join")
    print("3. Select: Active Directory")
    print("4. Enter domain and credentials")
    print("5. Leave certificate fields EMPTY (not required for basic LDAP)")
    print("")
    print("=" * 70)
    print("")

if __name__ == "__main__":
    main()
'''

    script_path = project_root / "scripts" / "python" / "configure_ldap_no_certificates.py"
    script_path.write_text(script_content)
    print(f"Created: {script_path}")
    return script_path


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="LDAP Certificate Setup Helper")
    parser.add_argument("--check", action="store_true", help="Check certificate requirements")
    parser.add_argument("--azure-ad-info", action="store_true", help="Show Azure AD certificate info")
    parser.add_argument("--skip-certs", action="store_true", help="Create script for LDAP without certificates")

    args = parser.parse_args()

    if args.check or (not args.azure_ad_info and not args.skip_certs):
        check_certificate_requirement()

    if args.azure_ad_info:
        get_azure_ad_certificate_info()

    if args.skip_certs:
        script_path = create_certificate_skip_script()
        print(f"Created script for certificate-free LDAP: {script_path}")
        print("")
        print("Run it with:")
        print(f"  python {script_path}")
        print("")

    # Always show summary
    print("=" * 70)
    print("   SUMMARY")
    print("=" * 70)
    print("")
    print("For most Azure AD LDAP configurations:")
    print("  ✓ Client certificates are NOT required")
    print("  ✓ Use basic username/password authentication")
    print("  ✓ Leave certificate fields empty in DSM")
    print("")
    print("If DSM specifically requires certificates:")
    print("  1. Get certificates from Azure AD (see --azure-ad-info)")
    print("  2. Add to Key Vault or use --cert-file/--key-file")
    print("  3. Run: python scripts/python/configure_ldap_certificates_rdp.py")
    print("")
    print("=" * 70)
    print("")


if __name__ == "__main__":


    main()