#!/usr/bin/env python3
"""
Get Azure AD Certificate for LDAP Authentication
Helps retrieve or generate certificates for Azure AD LDAP with mutual TLS
#JARVIS #LDAP #AZURE-AD #CERTIFICATES #SECURITY
"""

import sys
from pathlib import Path
import subprocess
import logging
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Try to import cryptography library
try:
    from cryptography import x509
    from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    logger.warning("cryptography library not available. Install with: pip install cryptography")


def check_openssl():
    """Check if OpenSSL is available"""
    try:
        result = subprocess.run(['openssl', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            return True
    except FileNotFoundError:
        pass
    return False


def generate_self_signed_certificate(output_dir: Path, common_name: str = "DSM-LDAP-Client"):
    try:
        """
        Generate a self-signed certificate for LDAP client authentication

        This creates:
        - client.crt (certificate)
        - client.key (private key)
        """
        if not check_openssl():
            logger.error("OpenSSL not found. Please install OpenSSL first.")
            return False

        output_dir.mkdir(parents=True, exist_ok=True)
        cert_file = output_dir / "client.crt"
        key_file = output_dir / "client.key"

        # Generate private key (2048-bit RSA)
        logger.info("Generating private key...")
        key_cmd = [
            'openssl', 'genrsa',
            '-out', str(key_file),
            '2048'
        ]

        result = subprocess.run(key_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Failed to generate private key: {result.stderr}")
            return False

        # Generate certificate signing request
        logger.info("Generating certificate...")
        csr_file = output_dir / "client.csr"
        csr_cmd = [
            'openssl', 'req', '-new',
            '-key', str(key_file),
            '-out', str(csr_file),
            '-subj', f'/CN={common_name}/O=LUMINA/OU=DSM-LDAP'
        ]

        result = subprocess.run(csr_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Failed to generate CSR: {result.stderr}")
            return False

        # Generate self-signed certificate (valid for 2 years)
        cert_cmd = [
            'openssl', 'x509', '-req',
            '-days', '730',  # 2 years
            '-in', str(csr_file),
            '-signkey', str(key_file),
            '-out', str(cert_file),
            '-extensions', 'v3_req',
            '-extfile', '-'
        ]

        # Create extensions file content
        extensions = b"""[v3_req]
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = clientAuth
"""

        result = subprocess.run(
            cert_cmd,
            input=extensions,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            logger.error(f"Failed to generate certificate: {result.stderr}")
            return False

        # Clean up CSR
        csr_file.unlink(missing_ok=True)

        logger.info(f"✅ Certificate generated:")
        logger.info(f"   Certificate: {cert_file}")
        logger.info(f"   Private Key: {key_file}")

        return True
    except Exception as e:
        logger.error(f"Error generating certificate: {e}")
        return False


def upload_to_key_vault(cert_file: Path, key_file: Path, vault_name: str = "jarvis-lumina"):
    """Upload certificate and key to Azure Key Vault"""
    try:
        import subprocess

        # Read certificate content
        cert_content = cert_file.read_text()

        # Read private key content
        key_content = key_file.read_text()

        # Upload to Key Vault
        logger.info("Uploading certificate to Azure Key Vault...")
        cert_cmd = [
            'az', 'keyvault', 'secret', 'set',
            '--vault-name', vault_name,
            '--name', 'ldap-client-certificate',
            '--value', cert_content
        ]

        result = subprocess.run(cert_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Failed to upload certificate: {result.stderr}")
            return False

        logger.info("Uploading private key to Azure Key Vault...")
        key_cmd = [
            'az', 'keyvault', 'secret', 'set',
            '--vault-name', vault_name,
            '--name', 'ldap-client-private-key',
            '--value', key_content
        ]

        result = subprocess.run(key_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Failed to upload private key: {result.stderr}")
            return False

        logger.info("✅ Certificates uploaded to Azure Key Vault")
        return True

    except Exception as e:
        logger.error(f"Error uploading to Key Vault: {e}")
        return False


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Get/Generate Azure AD LDAP Certificate")
        parser.add_argument("--generate", action="store_true", help="Generate self-signed certificate")
        parser.add_argument("--output-dir", default="certificates", help="Output directory for certificates")
        parser.add_argument("--common-name", default="DSM-LDAP-Client", help="Certificate common name")
        parser.add_argument("--upload", action="store_true", help="Upload to Azure Key Vault after generation")
        parser.add_argument("--vault-name", default="jarvis-lumina", help="Azure Key Vault name")
        parser.add_argument("--cert-file", help="Path to existing certificate file")
        parser.add_argument("--key-file", help="Path to existing private key file")

        args = parser.parse_args()

        print("=" * 70)
        print("   AZURE AD LDAP CERTIFICATE SETUP")
        print("=" * 70)
        print("")

        if args.generate:
            print("[1] Generating self-signed certificate...")
            output_dir = Path(args.output_dir)

            if generate_self_signed_certificate(output_dir, args.common_name):
                print("  ✅ Certificate generated successfully")
                print("")

                if args.upload:
                    print("[2] Uploading to Azure Key Vault...")
                    cert_file = output_dir / "client.crt"
                    key_file = output_dir / "client.key"

                    if upload_to_key_vault(cert_file, key_file, args.vault_name):
                        print("  ✅ Uploaded to Key Vault")
                        print("")
                        print("Next steps:")
                        print("  1. Upload certificate to Azure AD App Registration")
                        print("  2. Run: python scripts/python/configure_ldap_certificates_rdp.py")
                        print("  3. Configure DSM with certificates")
                    else:
                        print("  ⚠ Upload failed - certificates saved locally")
                else:
                    print("Certificates saved to:")
                    print(f"  {output_dir / 'client.crt'}")
                    print(f"  {output_dir / 'client.key'}")
                    print("")
                    print("To upload to Key Vault:")
                    print(f"  python {sys.argv[0]} --generate --upload")
            else:
                print("  ✗ Certificate generation failed")
                sys.exit(1)
        elif args.cert_file and args.key_file:
            print("[1] Using existing certificate files...")
            cert_file = Path(args.cert_file)
            key_file = Path(args.key_file)

            if not cert_file.exists():
                print(f"  ✗ Certificate file not found: {cert_file}")
                sys.exit(1)
            if not key_file.exists():
                print(f"  ✗ Private key file not found: {key_file}")
                sys.exit(1)

            print(f"  ✓ Certificate: {cert_file}")
            print(f"  ✓ Private Key: {key_file}")
            print("")

            if args.upload:
                print("[2] Uploading to Azure Key Vault...")
                if upload_to_key_vault(cert_file, key_file, args.vault_name):
                    print("  ✅ Uploaded to Key Vault")
                    print("")
                    print("Next steps:")
                    print("  python scripts/python/configure_ldap_certificates_rdp.py")
                else:
                    print("  ✗ Upload failed")
                    sys.exit(1)
        else:
            print("SECURITY BENEFITS OF CERTIFICATES:")
            print("")
            print("✅ Mutual Authentication - Both sides verify identity")
            print("✅ No Passwords - Eliminates password-based attacks")
            print("✅ Always Encrypted - Certificate exchange is encrypted")
            print("✅ Brute Force Resistant - No password to guess")
            print("✅ Strong Identity Proof - Cryptographic verification")
            print("✅ Better Audit Trail - Certificate serial tracking")
            print("")
            print("OPTIONS:")
            print("")
            print("1. Generate new certificate:")
            print(f"   python {sys.argv[0]} --generate --upload")
            print("")
            print("2. Use existing certificate:")
            print(f"   python {sys.argv[0]} --cert-file <cert.pem> --key-file <key.pem> --upload")
            print("")
            print("3. Get certificate from Azure AD App Registration:")
            print("   - Azure Portal → Azure AD → App registrations")
            print("   - Your app → Certificates & secrets")
            print("   - Export certificate and private key")
            print("")
            print("=" * 70)
            print("")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()