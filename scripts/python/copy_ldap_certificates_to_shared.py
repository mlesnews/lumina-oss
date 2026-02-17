#!/usr/bin/env python3
"""
Copy LDAP Certificates to Shared Location
Copies certificates from NAS to a shared location accessible from laptop
#JARVIS #LDAP #CERTIFICATES #SHARED
"""

import sys
import argparse
from pathlib import Path
import tempfile
import shutil

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.python.nas_azure_vault_integration import NASAzureVaultIntegration
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_certificates_from_nas(nas_integration: NASAzureVaultIntegration, output_dir: Path) -> dict:
    """Download certificates from NAS to local directory"""
    result = {
        "cert_downloaded": False,
        "key_downloaded": False,
        "cert_path": None,
        "key_path": None
    }

    try:
        output_dir.mkdir(parents=True, exist_ok=True)

        # Download certificate
        logger.info("Downloading certificate from NAS...")
        cert_content = nas_integration.execute_ssh_command("cat /tmp/ldap_certificates/client.crt 2>/dev/null")
        if isinstance(cert_content, dict):
            cert_content = cert_content.get('output', '') or cert_content.get('stdout', '') or str(cert_content)

        if cert_content and 'BEGIN CERTIFICATE' in str(cert_content):
            cert_path = output_dir / "client.crt"
            with open(cert_path, "w", encoding="utf-8") as f:
                f.write(str(cert_content).strip())
            result["cert_downloaded"] = True
            result["cert_path"] = str(cert_path)
            logger.info(f"✓ Certificate downloaded: {cert_path}")

        # Download private key
        logger.info("Downloading private key from NAS...")
        key_content = nas_integration.execute_ssh_command("cat /tmp/ldap_certificates/client.key 2>/dev/null")
        if isinstance(key_content, dict):
            key_content = key_content.get('output', '') or key_content.get('stdout', '') or str(key_content)

        if key_content and ('BEGIN PRIVATE KEY' in str(key_content) or 'BEGIN RSA PRIVATE KEY' in str(key_content)):
            key_path = output_dir / "client.key"
            with open(key_path, "w", encoding="utf-8") as f:
                f.write(str(key_content).strip())
            result["key_downloaded"] = True
            result["key_path"] = str(key_path)
            logger.info(f"✓ Private key downloaded: {key_path}")

    except Exception as e:
        logger.error(f"Failed to download certificates: {e}")

    return result


def copy_to_shared_location(cert_path: Path, key_path: Path, shared_path: Path) -> bool:
    """Copy certificates to a shared location (like Desktop or Documents)"""
    try:
        shared_path.mkdir(parents=True, exist_ok=True)

        # Copy certificate
        shared_cert = shared_path / "ldap_client.crt"
        shutil.copy2(cert_path, shared_cert)
        logger.info(f"✓ Certificate copied to: {shared_cert}")

        # Copy private key
        shared_key = shared_path / "ldap_client.key"
        shutil.copy2(key_path, shared_key)
        logger.info(f"✓ Private key copied to: {shared_key}")

        return True
    except Exception as e:
        logger.error(f"Failed to copy to shared location: {e}")
        return False


def main():
    try:
        parser = argparse.ArgumentParser(description="Copy LDAP certificates to shared location")
        parser.add_argument("--nas-ip", default="<NAS_PRIMARY_IP>", help="NAS IP address")
        parser.add_argument("--vault-name", default="jarvis-lumina", help="Azure Key Vault name")
        parser.add_argument("--output-dir", help="Output directory (default: Desktop/LDAP_Certificates)")
        parser.add_argument("--shared-dir", help="Shared directory (default: Desktop)")
        args = parser.parse_args()

        print("=" * 70)
        print("   COPY LDAP CERTIFICATES TO SHARED LOCATION")
        print("=" * 70)
        print("")

        nas_integration = NASAzureVaultIntegration(vault_name=args.vault_name, nas_ip=args.nas_ip)

        # Determine output directory
        if args.output_dir:
            output_dir = Path(args.output_dir)
        else:
            # Default to Desktop/LDAP_Certificates
            desktop = Path.home() / "Desktop"
            output_dir = desktop / "LDAP_Certificates"

        # Determine shared directory
        if args.shared_dir:
            shared_dir = Path(args.shared_dir)
        else:
            # Default to Desktop
            shared_dir = Path.home() / "Desktop"

        print(f"Downloading certificates from NAS...")
        print(f"Output directory: {output_dir}")
        print(f"Shared directory: {shared_dir}")
        print("")

        # Download certificates
        result = download_certificates_from_nas(nas_integration, output_dir)

        if not result["cert_downloaded"] or not result["key_downloaded"]:
            print("✗ Failed to download certificates from NAS")
            return 1

        # Copy to shared location
        print("")
        print(f"Copying to shared location: {shared_dir}")
        if copy_to_shared_location(
            Path(result["cert_path"]),
            Path(result["key_path"]),
            shared_dir
        ):
            print("")
            print("✅ Certificates ready for DSM upload")
            print("")
            print("Certificate locations:")
            print(f"  Certificate: {shared_dir / 'ldap_client.crt'}")
            print(f"  Private Key: {shared_dir / 'ldap_client.key'}")
            print("")
            print("In DSM, browse to these files when prompted.")
            print("")
        else:
            print("")
            print("⚠️  Certificates downloaded but not copied to shared location")
            print(f"  Certificate: {result['cert_path']}")
            print(f"  Private Key: {result['key_path']}")
            print("")
            print("You can manually browse to these files in DSM.")
            print("")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())