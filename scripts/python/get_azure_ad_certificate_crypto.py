#!/usr/bin/env python3
"""
Get Azure AD Certificate for LDAP Authentication (Using Cryptography Library)
Helps retrieve or generate certificates for Azure AD LDAP with mutual TLS
#JARVIS #LDAP #AZURE-AD #CERTIFICATES #SECURITY #HARDENING
"""

import sys
from pathlib import Path
import subprocess
import logging
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Use cryptography library (preferred, no external dependencies)
try:
    from cryptography import x509
    from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    print("ERROR: cryptography library not installed")
    print("Install with: pip install cryptography")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def generate_self_signed_certificate(output_dir: Path, common_name: str = "DSM-LDAP-Client"):
    """
    Generate a self-signed certificate for LDAP client authentication using cryptography library

    This creates:
    - client.crt (certificate)
    - client.key (private key)
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    cert_file = output_dir / "client.crt"
    key_file = output_dir / "client.key"

    try:
        logger.info("Generating private key (2048-bit RSA)...")
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        # Save private key
        pem_key = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        key_file.write_bytes(pem_key)
        logger.info(f"  ✓ Private key saved: {key_file}")

        # Create certificate
        logger.info("Generating certificate...")
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Security"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "LUMINA"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "LUMINA"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "DSM-LDAP"),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])

        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=730)  # 2 years
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=True,
                content_commitment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        ).add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CLIENT_AUTH]),
            critical=True,
        ).sign(private_key, hashes.SHA256())

        # Save certificate
        pem_cert = cert.public_bytes(serialization.Encoding.PEM)
        cert_file.write_bytes(pem_cert)
        logger.info(f"  ✓ Certificate saved: {cert_file}")

        logger.info(f"✅ Certificate generated successfully:")
        logger.info(f"   Certificate: {cert_file}")
        logger.info(f"   Private Key: {key_file}")
        logger.info(f"   Valid for: 2 years")
        logger.info(f"   Key Size: 2048-bit RSA")
        logger.info(f"   Purpose: Client Authentication (LDAP)")

        return True

    except Exception as e:
        logger.error(f"Failed to generate certificate: {e}")
        import traceback
        traceback.print_exc()
        return False


def upload_to_key_vault(cert_file: Path, key_file: Path, vault_name: str = "jarvis-lumina"):
    """Upload certificate and key to Azure Key Vault"""
    try:
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

        parser = argparse.ArgumentParser(description="Get/Generate Azure AD LDAP Certificate for LUMINA Hardening")
        parser.add_argument("--generate", action="store_true", help="Generate self-signed certificate")
        parser.add_argument("--output-dir", default="certificates", help="Output directory for certificates")
        parser.add_argument("--common-name", default="DSM-LDAP-Client", help="Certificate common name")
        parser.add_argument("--upload", action="store_true", help="Upload to Azure Key Vault after generation")
        parser.add_argument("--vault-name", default="jarvis-lumina", help="Azure Key Vault name")
        parser.add_argument("--cert-file", help="Path to existing certificate file")
        parser.add_argument("--key-file", help="Path to existing private key file")

        args = parser.parse_args()

        print("=" * 70)
        print("   LUMINA SECURITY HARDENING - CERTIFICATE GENERATION")
        print("=" * 70)
        print("")
        print("🔒 Hardening LUMINA with certificate-based authentication")
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
                        print("[3] Next steps for hardening:")
                        print("  1. Run: python scripts/python/configure_ldap_certificates_rdp.py")
                        print("  2. Configure DSM with certificates (RDP to MANUS)")
                        print("  3. Verify mutual TLS authentication")
                        print("  4. Document in security hardening log")
                    else:
                        print("  ⚠ Upload failed - certificates saved locally")
                        print("  You can upload manually later")
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
            print("SECURITY HARDENING BENEFITS:")
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
            print("1. Generate and upload certificate:")
            print(f"   python {sys.argv[0]} --generate --upload")
            print("")
            print("2. Use existing certificate:")
            print(f"   python {sys.argv[0]} --cert-file <cert.pem> --key-file <key.pem> --upload")
            print("")
            print("=" * 70)
            print("")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()