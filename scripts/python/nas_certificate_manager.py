#!/usr/bin/env python3
"""
NAS Certificate Manager

Manages SSL certificates for NAS connections, including downloading and storing
self-signed certificates for secure connections.
"""

import sys
import ssl
import socket
import certifi
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

try:
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    x509 = None

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("NASCertificateManager")


class NASCertificateManager:
    """Manages SSL certificates for NAS connections"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.certs_dir = self.project_root / "config" / "certs"
        self.certs_dir.mkdir(parents=True, exist_ok=True)

        # CA directory for Certificate Authority
        self.ca_dir = self.certs_dir / "ca"
        self.ca_dir.mkdir(parents=True, exist_ok=True)

        self.logger = get_logger("NASCertificateManager")
        self.logger.info("🔒 NAS Certificate Manager initialized")

    def get_certificate_path(self, nas_host: str, nas_port: int = 5001) -> Path:
        """Get path to certificate file for NAS"""
        cert_filename = f"nas_{nas_host}_{nas_port}.crt"
        return self.certs_dir / cert_filename

    def download_nas_certificate(self, nas_host: str, nas_port: int = 5001) -> Optional[Path]:
        """
        Download and save NAS SSL certificate

        Args:
            nas_host: NAS hostname or IP
            nas_port: NAS HTTPS port (default: 5001 for Synology)

        Returns:
            Path to certificate file if successful, None otherwise
        """
        self.logger.info(f"📥 Downloading certificate from {nas_host}:{nas_port}...")

        try:
            # Create SSL context
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            # Connect and get certificate
            with socket.create_connection((nas_host, nas_port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=nas_host) as ssock:
                    cert_der = ssock.getpeercert(binary_form=True)
                    cert_pem = ssl.DER_cert_to_PEM_cert(cert_der)

            # Save certificate
            cert_path = self.get_certificate_path(nas_host, nas_port)
            with open(cert_path, 'w', encoding='utf-8') as f:
                f.write(cert_pem)

            self.logger.info(f"✅ Certificate saved: {cert_path}")
            return cert_path

        except socket.timeout:
            self.logger.error(f"❌ Connection timeout to {nas_host}:{nas_port}")
            return None
        except socket.gaierror as e:
            self.logger.error(f"❌ DNS resolution failed for {nas_host}: {e}")
            return None
        except ssl.SSLError as e:
            self.logger.error(f"❌ SSL error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Error downloading certificate: {e}")
            return None

    def get_certificate_verify_path(self, nas_host: str, nas_port: int = 5001) -> Optional[str]:
        try:
            """
            Get certificate path for requests.verify parameter

            Returns:
                Path to certificate file if exists, None if not found
            """
            cert_path = self.get_certificate_path(nas_host, nas_port)

            if cert_path.exists():
                self.logger.debug(f"✅ Certificate found: {cert_path}")
                return str(cert_path)
            else:
                self.logger.warning(f"⚠️  Certificate not found: {cert_path}")
                self.logger.info(f"   Run: download_nas_certificate('{nas_host}', {nas_port})")
                return None

        except Exception as e:
            self.logger.error(f"Error in get_certificate_verify_path: {e}", exc_info=True)
            raise
    def ensure_certificate(self, nas_host: str, nas_port: int = 5001, auto_download: bool = True) -> Optional[str]:
        try:
            """
            Ensure certificate exists, download if needed

            Args:
                nas_host: NAS hostname or IP
                nas_port: NAS HTTPS port
                auto_download: Automatically download if certificate doesn't exist

            Returns:
                Path to certificate file if available, None otherwise
            """
            cert_path = self.get_certificate_path(nas_host, nas_port)

            if cert_path.exists():
                self.logger.debug(f"✅ Certificate already exists: {cert_path}")
                return str(cert_path)

            if auto_download:
                self.logger.info(f"📥 Certificate not found, downloading...")
                downloaded = self.download_nas_certificate(nas_host, nas_port)
                if downloaded:
                    return str(downloaded)

            return None

        except Exception as e:
            self.logger.error(f"Error in ensure_certificate: {e}", exc_info=True)
            raise
    def verify_certificate(self, nas_host: str, nas_port: int = 5001) -> Dict[str, Any]:
        """
        Verify certificate validity and get details

        Returns:
            Dictionary with certificate information
        """
        cert_path = self.get_certificate_path(nas_host, nas_port)

        if not cert_path.exists():
            return {
                "exists": False,
                "error": "Certificate file not found"
            }

        try:
            # Read certificate
            with open(cert_path, 'r', encoding='utf-8') as f:
                cert_pem = f.read()

            # Parse certificate
            cert = ssl.PEM_cert_to_DER_cert(cert_pem)
            x509 = ssl.DER_cert_to_PEM_cert(cert)

            # Get certificate details
            cert_dict = ssl._ssl._test_decode_cert(cert_path)

            return {
                "exists": True,
                "path": str(cert_path),
                "subject": cert_dict.get("subject", {}),
                "issuer": cert_dict.get("issuer", {}),
                "serial_number": cert_dict.get("serialNumber", ""),
                "not_before": cert_dict.get("notBefore", ""),
                "not_after": cert_dict.get("notAfter", ""),
                "valid": True  # If we can parse it, it's valid format
            }

        except Exception as e:
            return {
                "exists": True,
                "path": str(cert_path),
                "error": str(e),
                "valid": False
            }

    def generate_self_signed_certificate(
        self,
        nas_host: str,
        nas_port: int = 5001,
        validity_days: int = 365,
        organization: str = "LUMINA NAS",
        country: str = "US"
    ) -> Optional[Path]:
        """
        Generate a self-signed certificate for NAS connection

        Args:
            nas_host: NAS hostname or IP
            nas_port: NAS HTTPS port
            validity_days: Certificate validity in days (default: 365)
            organization: Organization name for certificate
            country: Country code for certificate

        Returns:
            Path to certificate file if successful, None otherwise
        """
        if not CRYPTOGRAPHY_AVAILABLE:
            self.logger.error("❌ cryptography library not available. Install with: pip install cryptography")
            return None

        self.logger.info(f"🔨 Generating self-signed certificate for {nas_host}:{nas_port}...")

        try:
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )

            # Create certificate subject
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, country),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
                x509.NameAttribute(NameOID.COMMON_NAME, nas_host),
            ])

            # Create certificate
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
                datetime.utcnow() + timedelta(days=validity_days)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName(nas_host) if not self._is_ip(nas_host) else x509.IPAddress(self._parse_ip(nas_host))
                ]),
                critical=False,
            ).sign(private_key, hashes.SHA256(), default_backend())

            # Save certificate
            cert_path = self.get_certificate_path(nas_host, nas_port)
            with open(cert_path, 'wb') as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))

            # Save private key (for reference, but not used for client connections)
            key_path = self.certs_dir / f"nas_{nas_host}_{nas_port}.key"
            with open(key_path, 'wb') as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))

            self.logger.info(f"✅ Self-signed certificate generated: {cert_path}")
            self.logger.info(f"   Private key saved: {key_path}")
            self.logger.warning(f"⚠️  This is a self-signed certificate. For production, use a proper CA-signed certificate.")

            return cert_path

        except Exception as e:
            self.logger.error(f"❌ Error generating certificate: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return None

    def _is_ip(self, host: str) -> bool:
        """Check if host is an IP address"""
        try:
            import ipaddress
            ipaddress.ip_address(host)
            return True
        except ValueError:
            return False

    def _parse_ip(self, host: str):
        """Parse IP address string to ipaddress object"""
        import ipaddress
        return ipaddress.ip_address(host)

    def get_ca_certificate_path(self) -> Path:
        """Get path to CA certificate file"""
        return self.ca_dir / "ca_certificate.crt"

    def get_ca_private_key_path(self) -> Path:
        """Get path to CA private key file"""
        return self.ca_dir / "ca_private_key.key"

    def create_certificate_authority(
        self,
        organization: str = "LUMINA Certificate Authority",
        country: str = "US",
        validity_years: int = 10
    ) -> Dict[str, Any]:
        """
        Create a local Certificate Authority (CA)

        Args:
            organization: Organization name for CA
            country: Country code for CA
            validity_years: CA certificate validity in years (default: 10)

        Returns:
            Dictionary with CA certificate and key paths
        """
        if not CRYPTOGRAPHY_AVAILABLE:
            self.logger.error("❌ cryptography library not available. Install with: pip install cryptography")
            return {"success": False, "error": "cryptography not available"}

        self.logger.info("🏛️  Creating Certificate Authority...")

        try:
            # Generate CA private key
            ca_private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096,  # CA uses stronger key
                backend=default_backend()
            )

            # Create CA certificate subject
            ca_subject = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, country),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
                x509.NameAttribute(NameOID.COMMON_NAME, f"{organization} Root CA"),
            ])

            # Create CA certificate
            ca_cert = x509.CertificateBuilder().subject_name(
                ca_subject
            ).issuer_name(
                ca_subject  # Self-signed CA
            ).public_key(
                ca_private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + timedelta(days=validity_years * 365)
            ).add_extension(
                x509.BasicConstraints(ca=True, path_length=None),
                critical=True,
            ).add_extension(
                x509.KeyUsage(
                    key_cert_sign=True,
                    crl_sign=True,
                    digital_signature=False,
                    content_commitment=False,
                    key_encipherment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    encipher_only=False,
                    decipher_only=False
                ),
                critical=True,
            ).add_extension(
                x509.SubjectKeyIdentifier.from_public_key(ca_private_key.public_key()),
                critical=False,
            ).sign(ca_private_key, hashes.SHA256(), default_backend())

            # Save CA certificate
            ca_cert_path = self.get_ca_certificate_path()
            with open(ca_cert_path, 'wb') as f:
                f.write(ca_cert.public_bytes(serialization.Encoding.PEM))

            # Save CA private key
            ca_key_path = self.get_ca_private_key_path()
            with open(ca_key_path, 'wb') as f:
                f.write(ca_private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))

            # Set restrictive permissions on private key (Unix-like systems)
            try:
                import os
                os.chmod(ca_key_path, 0o600)  # Read/write for owner only
            except (AttributeError, OSError):
                pass  # Windows doesn't support chmod the same way

            self.logger.info(f"✅ Certificate Authority created:")
            self.logger.info(f"   CA Certificate: {ca_cert_path}")
            self.logger.info(f"   CA Private Key: {ca_key_path}")
            self.logger.warning(f"⚠️  Keep CA private key secure! Do not share it.")

            return {
                "success": True,
                "ca_certificate_path": str(ca_cert_path),
                "ca_private_key_path": str(ca_key_path),
                "organization": organization,
                "validity_years": validity_years
            }

        except Exception as e:
            self.logger.error(f"❌ Error creating CA: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return {"success": False, "error": str(e)}

    def ca_exists(self) -> bool:
        try:
            """Check if CA certificate and key exist"""
            return (self.get_ca_certificate_path().exists() and 
                    self.get_ca_private_key_path().exists())

        except Exception as e:
            self.logger.error(f"Error in ca_exists: {e}", exc_info=True)
            raise
    def generate_ca_signed_certificate(
        self,
        nas_host: str,
        nas_port: int = 5001,
        validity_days: int = 365,
        organization: str = "LUMINA NAS"
    ) -> Optional[Path]:
        """
        Generate a CA-signed certificate for NAS connection

        Args:
            nas_host: NAS hostname or IP
            nas_port: NAS HTTPS port
            validity_days: Certificate validity in days (default: 365)
            organization: Organization name for certificate

        Returns:
            Path to certificate file if successful, None otherwise
        """
        if not CRYPTOGRAPHY_AVAILABLE:
            self.logger.error("❌ cryptography library not available. Install with: pip install cryptography")
            return None

        if not self.ca_exists():
            self.logger.error("❌ CA not found. Create CA first with create_certificate_authority()")
            return None

        self.logger.info(f"📜 Generating CA-signed certificate for {nas_host}:{nas_port}...")

        try:
            # Load CA certificate and private key
            with open(self.get_ca_certificate_path(), 'rb') as f:
                ca_cert = x509.load_pem_x509_certificate(f.read(), default_backend())

            with open(self.get_ca_private_key_path(), 'rb') as f:
                ca_private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )

            # Generate server private key
            server_private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )

            # Create certificate subject
            subject = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
                x509.NameAttribute(NameOID.COMMON_NAME, nas_host),
            ])

            # Build SAN list
            san_list = [x509.DNSName(nas_host)]
            if self._is_ip(nas_host):
                san_list.append(x509.IPAddress(self._parse_ip(nas_host)))

            # Create certificate signed by CA
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                ca_cert.subject  # Issued by CA
            ).public_key(
                server_private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + timedelta(days=validity_days)
            ).add_extension(
                x509.SubjectAlternativeName(san_list),
                critical=False,
            ).add_extension(
                x509.KeyUsage(
                    key_cert_sign=False,
                    crl_sign=False,
                    digital_signature=True,
                    content_commitment=False,
                    key_encipherment=True,
                    data_encipherment=False,
                    key_agreement=False,
                    encipher_only=False,
                    decipher_only=False
                ),
                critical=True,
            ).add_extension(
                x509.ExtendedKeyUsage([
                    x509.ExtendedKeyUsageOID.SERVER_AUTH,
                ]),
                critical=True,
            ).add_extension(
                x509.AuthorityKeyIdentifier.from_issuer_subject_key_identifier(
                    ca_cert.extensions.get_extension_for_class(x509.SubjectKeyIdentifier).value
                ),
                critical=False,
            ).sign(ca_private_key, hashes.SHA256(), default_backend())

            # Save certificate
            cert_path = self.get_certificate_path(nas_host, nas_port)
            with open(cert_path, 'wb') as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))

            # Save private key
            key_path = self.certs_dir / f"nas_{nas_host}_{nas_port}.key"
            with open(key_path, 'wb') as f:
                f.write(server_private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))

            self.logger.info(f"✅ CA-signed certificate generated: {cert_path}")
            self.logger.info(f"   Private key saved: {key_path}")
            self.logger.info(f"   Signed by: {ca_cert.subject}")

            return cert_path

        except Exception as e:
            self.logger.error(f"❌ Error generating CA-signed certificate: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return None

    def get_ca_certificate_for_verification(self) -> Optional[str]:
        try:
            """
            Get CA certificate path for requests.verify parameter

            Returns:
                Path to CA certificate file if exists, None if not found
            """
            ca_cert_path = self.get_ca_certificate_path()

            if ca_cert_path.exists():
                self.logger.debug(f"✅ CA certificate found: {ca_cert_path}")
                return str(ca_cert_path)
            else:
                self.logger.warning(f"⚠️  CA certificate not found: {ca_cert_path}")
                return None

        except Exception as e:
            self.logger.error(f"Error in get_ca_certificate_for_verification: {e}", exc_info=True)
            raise
    def ensure_certificate(
        self,
        nas_host: str,
        nas_port: int = 5001,
        auto_download: bool = True,
        auto_generate: bool = False
    ) -> Optional[str]:
        """
        Ensure certificate exists, download or generate if needed

        Args:
            nas_host: NAS hostname or IP
            nas_port: NAS HTTPS port
            auto_download: Automatically download if certificate doesn't exist
            auto_generate: Automatically generate self-signed certificate if download fails

        Returns:
            Path to certificate file if available, None otherwise
        """
        cert_path = self.get_certificate_path(nas_host, nas_port)

        if cert_path.exists():
            self.logger.debug(f"✅ Certificate already exists: {cert_path}")
            return str(cert_path)

        # Try to download first
        if auto_download:
            self.logger.info(f"📥 Certificate not found, attempting download...")
            downloaded = self.download_nas_certificate(nas_host, nas_port)
            if downloaded:
                return str(downloaded)

            # Download failed - try generation if enabled
            if auto_generate:
                self.logger.info(f"🔨 Download failed, generating self-signed certificate...")
                generated = self.generate_self_signed_certificate(nas_host, nas_port)
                if generated:
                    return str(generated)

        return None

    def get_requests_verify_setting(
        self,
        nas_host: str,
        nas_port: int = 5001,
        auto_download: bool = True,
        auto_generate: bool = False
    ) -> Any:
        """
        Get verify setting for requests library

        Args:
            nas_host: NAS hostname or IP
            nas_port: NAS HTTPS port
            auto_download: Automatically download if certificate doesn't exist
            auto_generate: Automatically generate self-signed certificate if download fails

        Returns:
            Certificate path (str) if available, False if should skip verification,
            True if should use system certificates
        """
        cert_path = self.ensure_certificate(nas_host, nas_port, auto_download, auto_generate)

        if cert_path:
            return cert_path  # Use specific certificate
        else:
            self.logger.warning(f"⚠️  Certificate not available for {nas_host}:{nas_port}, verification disabled")
            self.logger.info(f"   Options:")
            self.logger.info(f"   1. Download: python nas_certificate_manager.py --host {nas_host} --port {nas_port} --download")
            self.logger.info(f"   2. Generate: python nas_certificate_manager.py --host {nas_host} --port {nas_port} --generate")
            return False  # Fallback to no verification (not ideal, but maintains functionality)


def main():
    """CLI for certificate management"""
    import argparse

    parser = argparse.ArgumentParser(description="NAS Certificate Manager")
    parser.add_argument("--host", help="NAS hostname or IP (required for download/generate/ca-signed/verify/ensure)")
    parser.add_argument("--port", type=int, default=5001, help="NAS HTTPS port")
    parser.add_argument("--download", action="store_true", help="Download certificate from NAS")
    parser.add_argument("--generate", action="store_true", help="Generate self-signed certificate")
    parser.add_argument("--create-ca", action="store_true", help="Create Certificate Authority")
    parser.add_argument("--ca-signed", action="store_true", help="Generate CA-signed certificate")
    parser.add_argument("--verify", action="store_true", help="Verify certificate")
    parser.add_argument("--ensure", action="store_true", help="Ensure certificate exists (download or generate)")
    parser.add_argument("--validity-days", type=int, default=365, help="Certificate validity in days (for generation)")
    parser.add_argument("--validity-years", type=int, default=10, help="CA validity in years (for CA creation)")
    parser.add_argument("--organization", default="LUMINA NAS", help="Organization name (for generation)")
    parser.add_argument("--ca-organization", default="LUMINA Certificate Authority", help="CA organization name")

    args = parser.parse_args()

    manager = NASCertificateManager()

    # Handle CA creation first (doesn't need host)
    if args.create_ca:
        result = manager.create_certificate_authority(
            organization=args.ca_organization,
            validity_years=args.validity_years
        )
        if result.get("success"):
            print(f"✅ Certificate Authority created:")
            print(f"   CA Certificate: {result['ca_certificate_path']}")
            print(f"   CA Private Key: {result['ca_private_key_path']}")
            print(f"⚠️  Keep CA private key secure! Do not share it.")
            sys.exit(0)
        else:
            print(f"❌ Failed to create CA: {result.get('error', 'Unknown error')}")
            if not CRYPTOGRAPHY_AVAILABLE:
                print(f"   Install cryptography: pip install cryptography")
            sys.exit(1)

    # For other operations, host is required
    if not args.host and (args.download or args.generate or args.ca_signed or args.verify or args.ensure):
        parser.error("--host is required for download, generate, ca-signed, verify, or ensure operations")

    if args.generate:
        cert_path = manager.generate_self_signed_certificate(
            args.host,
            args.port,
            validity_days=args.validity_days,
            organization=args.organization
        )
        if cert_path:
            print(f"✅ Self-signed certificate generated: {cert_path}")
            print(f"⚠️  Note: This is a self-signed certificate. For production, use a CA-signed certificate.")
        else:
            print(f"❌ Failed to generate certificate")
            if not CRYPTOGRAPHY_AVAILABLE:
                print(f"   Install cryptography: pip install cryptography")
            sys.exit(1)

    if args.ca_signed:
        if not args.host:
            print(f"❌ --host required for CA-signed certificate generation")
            sys.exit(1)

        cert_path = manager.generate_ca_signed_certificate(
            args.host,
            args.port,
            validity_days=args.validity_days,
            organization=args.organization
        )
        if cert_path:
            print(f"✅ CA-signed certificate generated: {cert_path}")
            print(f"   This certificate is signed by the local CA and provides proper certificate chain validation.")
        else:
            print(f"❌ Failed to generate CA-signed certificate")
            if not manager.ca_exists():
                print(f"   Create CA first with: --create-ca")
            sys.exit(1)

    if args.ensure:
        cert_path = manager.ensure_certificate(
            args.host,
            args.port,
            auto_download=True,
            auto_generate=True
        )
        if cert_path:
            print(f"✅ Certificate ensured: {cert_path}")
        else:
            print(f"❌ Failed to ensure certificate exists")
            sys.exit(1)

    if args.verify:
        info = manager.verify_certificate(args.host, args.port)
        print(f"\nCertificate Information:")
        print(f"  Exists: {info.get('exists', False)}")
        if info.get('exists'):
            print(f"  Path: {info.get('path', 'N/A')}")
            print(f"  Valid: {info.get('valid', False)}")
            if info.get('subject'):
                print(f"  Subject: {info.get('subject', {})}")
            if info.get('error'):
                print(f"  Error: {info.get('error')}")


if __name__ == "__main__":



    main()