#!/usr/bin/env python3
"""
Configure LDAP Client Certificates via RDP/MANUS
Retrieves certificates from Azure Key Vault and uploads to NAS via RDP automation
#JARVIS #LDAP #AZURE-AD #RDP #MANUS #AUTOMATION
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
import tempfile
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.nas_azure_vault_integration import NASAzureVaultIntegration
    from scripts.python.azure_service_bus_integration import AzureKeyVaultClient
except ImportError as e:
    print(f"ERROR: Could not import required modules: {e}")
    sys.exit(1)

try:
    from azure.identity import DefaultAzureCredential
    KEY_VAULT_AVAILABLE = True
except ImportError:
    KEY_VAULT_AVAILABLE = False
    print("WARNING: Azure Key Vault SDK not installed")

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def get_certificate_secrets(vault_name: str = "jarvis-lumina") -> Dict[str, Optional[str]]:
    """
    Retrieve LDAP client certificate and private key from Azure Key Vault

    Returns:
        Dict with 'certificate' and 'private_key' (or None if not found)
    """
    if not KEY_VAULT_AVAILABLE:
        logger.error("Azure Key Vault SDK not available")
        return {"certificate": None, "private_key": None}

    try:
        vault_url = f"https://{vault_name}.vault.azure.net/"
        credential = DefaultAzureCredential(

                            exclude_interactive_browser_credential=False,

                            exclude_shared_token_cache_credential=False

                        )
        vault_client = AzureKeyVaultClient(vault_url, credential)

        # Try multiple possible secret names
        cert_secret_names = [
            "ldap-client-certificate",
            "ldap-client-cert",
            "azure-ad-client-certificate",
            "ldap-cert",
            "ldap-certificate"
        ]

        key_secret_names = [
            "ldap-client-private-key",
            "ldap-client-key",
            "azure-ad-client-private-key",
            "ldap-key",
            "ldap-private-key"
        ]

        certificate = None
        private_key = None

        # Try to get certificate
        for secret_name in cert_secret_names:
            try:
                certificate = vault_client.get_secret(secret_name)
                logger.info(f"Found certificate in Key Vault: {secret_name}")
                break
            except Exception:
                continue

        # Try to get private key
        for secret_name in key_secret_names:
            try:
                private_key = vault_client.get_secret(secret_name)
                logger.info(f"Found private key in Key Vault: {secret_name}")
                break
            except Exception:
                continue

        return {
            "certificate": certificate,
            "private_key": private_key
        }
    except Exception as e:
        logger.error(f"Error retrieving certificates from Key Vault: {e}")
        return {"certificate": None, "private_key": None}


def save_certificates_to_nas(
    nas_integration: NASAzureVaultIntegration,
    certificate: str,
    private_key: str
) -> bool:
    """
    Save certificates to NAS via SSH (temporary location for RDP upload)
    """
    try:
        # Create temporary directory on NAS
        temp_dir = "/tmp/ldap_certificates"
        nas_integration.execute_ssh_command(f"mkdir -p {temp_dir}")

        # Save certificate
        cert_file = f"{temp_dir}/client.crt"
        cert_escaped = certificate.replace("'", "'\\''")
        cmd = f"cat > {cert_file} << 'CERT_EOF'\n{cert_escaped}\nCERT_EOF"
        result = nas_integration.execute_ssh_command(cmd)

        # Save private key
        key_file = f"{temp_dir}/client.key"
        key_escaped = private_key.replace("'", "'\\''")
        cmd = f"cat > {key_file} << 'KEY_EOF'\n{key_escaped}\nKEY_EOF"
        result = nas_integration.execute_ssh_command(cmd)

        # Set secure permissions
        nas_integration.execute_ssh_command(f"chmod 600 {cert_file} {key_file}")
        nas_integration.execute_ssh_command(f"chmod 700 {temp_dir}")

        logger.info(f"Certificates saved to NAS: {temp_dir}")
        return True
    except Exception as e:
        logger.error(f"Error saving certificates to NAS: {e}")
        return False


def create_rdp_upload_script(
    certificate_path: str,
    private_key_path: str,
    nas_ip: str = "<NAS_PRIMARY_IP>"
) -> str:
    """
    Create PowerShell script for RDP automation to upload certificates via DSM
    """
    script_content = f'''# PowerShell script for RDP/MANUS automation
# Upload LDAP client certificates via DSM web interface

$ErrorActionPreference = "Stop"

Write-Host "=== LDAP CERTIFICATE UPLOAD VIA RDP ===" -ForegroundColor Cyan
Write-Host ""

# Certificate locations on NAS (via SSH)
$certPath = "{certificate_path}"
$keyPath = "{private_key_path}"

Write-Host "Certificate locations:" -ForegroundColor Yellow
Write-Host "  Certificate: $certPath" -ForegroundColor White
Write-Host "  Private Key: $keyPath" -ForegroundColor White
Write-Host ""

Write-Host "INSTRUCTIONS FOR RDP/MANUS AUTOMATION:" -ForegroundColor Green
Write-Host ""
Write-Host "1. RDP to MANUS (<NAS_IP>)" -ForegroundColor Cyan
Write-Host "2. Open DSM web interface: https://{nas_ip}:5001" -ForegroundColor Cyan
Write-Host "3. Navigate to: Control Panel → Domain/LDAP" -ForegroundColor Cyan
Write-Host "4. Click: Join (or Edit if already joined)" -ForegroundColor Cyan
Write-Host "5. In 'Client Certificate' section:" -ForegroundColor Cyan
Write-Host "   - Certificate: $certPath" -ForegroundColor White
Write-Host "   - Private Key: $keyPath" -ForegroundColor White
Write-Host "6. Click: Apply" -ForegroundColor Cyan
Write-Host ""

Write-Host "NOTE: Certificates are already on NAS at the paths above" -ForegroundColor Yellow
Write-Host "      You can copy them from /tmp/ldap_certificates/ if needed" -ForegroundColor Yellow
Write-Host ""

# Alternative: Use browser automation if available
Write-Host "AUTOMATION OPTION:" -ForegroundColor Green
Write-Host "  If browser automation is configured, this can be automated" -ForegroundColor Gray
Write-Host "  via MANUS RDP session using browser automation tools" -ForegroundColor Gray
Write-Host ""
'''
    return script_content


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Configure LDAP Client Certificates via RDP/MANUS")
    parser.add_argument("--nas-ip", default="<NAS_PRIMARY_IP>", help="NAS IP address")
    parser.add_argument("--vault-name", default="jarvis-lumina", help="Azure Key Vault name")
    parser.add_argument("--manus-ip", default="<NAS_IP>", help="MANUS IP address for RDP")
    parser.add_argument("--cert-secret", help="Certificate secret name in Key Vault (optional)")
    parser.add_argument("--key-secret", help="Private key secret name in Key Vault (optional)")
    parser.add_argument("--cert-file", help="Path to local certificate file (.crt or .pem)")
    parser.add_argument("--key-file", help="Path to local private key file (.key or .pem)")

    args = parser.parse_args()

    print("=" * 70)
    print("   LDAP CLIENT CERTIFICATE CONFIGURATION - RDP/MANUS")
    print("=" * 70)
    print("")

    # Step 1: Verify Azure Key Vault
    print("[1] Verifying Azure Key Vault configuration...")
    print(f"  Vault Name: {args.vault_name}")
    print(f"  Vault URL: https://{args.vault_name}.vault.azure.net/")

    try:
        vault_url = f"https://{args.vault_name}.vault.azure.net/"
        credential = DefaultAzureCredential(

                            exclude_interactive_browser_credential=False,

                            exclude_shared_token_cache_credential=False

                        )
        vault_client = AzureKeyVaultClient(vault_url, credential)
        print("  ✓ Key Vault connection successful")
    except Exception as e:
        print(f"  ✗ Key Vault connection failed: {e}")
        print("")
        print("Please verify:")
        print("  1. Azure CLI is logged in: az login")
        print("  2. Key Vault exists: az keyvault show --name jarvis-lumina")
        print("  3. You have access to the Key Vault")
        sys.exit(1)
    print("")

    # Step 2: Retrieve certificates from Key Vault or local files
    print("[2] Retrieving LDAP client certificates...")

    certificate = None
    private_key = None

    # Check for local files first
    if args.cert_file and args.key_file:
        print("  Using local certificate files...")
        try:
            cert_path = Path(args.cert_file)
            key_path = Path(args.key_file)

            if not cert_path.exists():
                print(f"  ✗ Certificate file not found: {cert_path}")
                sys.exit(1)
            if not key_path.exists():
                print(f"  ✗ Private key file not found: {key_path}")
                sys.exit(1)

            certificate = cert_path.read_text()
            private_key = key_path.read_text()
            print(f"  ✓ Loaded certificate: {cert_path}")
            print(f"  ✓ Loaded private key: {key_path}")
        except Exception as e:
            print(f"  ✗ Error reading certificate files: {e}")
            sys.exit(1)
    elif args.cert_secret and args.key_secret:
        # Use specified secret names
        try:
            certificate = vault_client.get_secret(args.cert_secret)
            private_key = vault_client.get_secret(args.key_secret)
            print(f"  ✓ Retrieved certificate: {args.cert_secret}")
            print(f"  ✓ Retrieved private key: {args.key_secret}")
        except Exception as e:
            print(f"  ✗ Error retrieving specified secrets: {e}")
            sys.exit(1)
    else:
        # Auto-detect secret names
        certs = get_certificate_secrets(args.vault_name)
        certificate = certs.get("certificate")
        private_key = certs.get("private_key")

        if certificate and private_key:
            print("  ✓ Found certificates in Key Vault")
        else:
            print("  ⚠ Certificates not found in Key Vault")
            print("")
            print("Please add certificates to Key Vault:")
            print("  az keyvault secret set --vault-name jarvis-lumina --name ldap-client-certificate --file \"cert.pem\"")
            print("  az keyvault secret set --vault-name jarvis-lumina --name ldap-client-private-key --file \"key.pem\"")
            print("")
            print("Or provide certificate files manually:")
            print("  --cert-file <path-to-certificate.pem>")
            print("  --key-file <path-to-private-key.pem>")
            sys.exit(1)

    if not certificate or not private_key:
        print("  ✗ No certificates provided")
        print("")
        print("Please provide certificates using one of these methods:")
        print("  1. Add to Key Vault: az keyvault secret set ...")
        print("  2. Use local files: --cert-file <path> --key-file <path>")
        print("  3. Specify secret names: --cert-secret <name> --key-secret <name>")
        sys.exit(1)
    print("")

    # Step 3: Initialize NAS integration
    print("[3] Connecting to NAS...")
    nas_integration = NASAzureVaultIntegration(
        vault_name=args.vault_name,
        nas_ip=args.nas_ip
    )
    print("  ✓ NAS connection established")
    print("")

    # Step 4: Save certificates to NAS
    print("[4] Saving certificates to NAS...")
    if save_certificates_to_nas(nas_integration, certificate, private_key):
        print("  ✓ Certificates saved to NAS")
        print("    Location: /tmp/ldap_certificates/")
        print("    Files: client.crt, client.key")
    else:
        print("  ✗ Failed to save certificates to NAS")
        sys.exit(1)
    print("")

    # Step 5: Create RDP automation script
    print("[5] Creating RDP automation script...")
    script_content = create_rdp_upload_script(
        certificate_path="/tmp/ldap_certificates/client.crt",
        private_key_path="/tmp/ldap_certificates/client.key",
        nas_ip=args.nas_ip
    )

    script_path = project_root / "scripts" / "powershell" / "upload_ldap_certificates_rdp.ps1"
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(script_content)
    print(f"  ✓ RDP script created: {script_path}")
    print("")

    # Step 6: Summary and instructions
    print("=" * 70)
    print("   CERTIFICATE UPLOAD READY")
    print("=" * 70)
    print("")
    print("Certificates are now on NAS and ready for upload via DSM:")
    print("")
    print("CERTIFICATE LOCATIONS (on NAS):")
    print("  Certificate: /tmp/ldap_certificates/client.crt")
    print("  Private Key: /tmp/ldap_certificates/client.key")
    print("")
    print("NEXT STEPS (via RDP to MANUS):")
    print("")
    print("1. RDP to MANUS:")
    print(f"   mstsc /v:{args.manus_ip}")
    print("")
    print("2. In RDP session, open DSM:")
    print(f"   https://{args.nas_ip}:5001")
    print("")
    print("3. Navigate to: Control Panel → Domain/LDAP")
    print("")
    print("4. Click: Join (or Edit if already joined)")
    print("")
    print("5. In 'Client Certificate' section:")
    print("   - Certificate file: /tmp/ldap_certificates/client.crt")
    print("   - Private key file: /tmp/ldap_certificates/client.key")
    print("")
    print("6. Click: Apply")
    print("")
    print("ALTERNATIVE: Run the automation script from MANUS RDP session:")
    print(f"   powershell -File {script_path}")
    print("")
    print("=" * 70)
    print("")


if __name__ == "__main__":


    main()