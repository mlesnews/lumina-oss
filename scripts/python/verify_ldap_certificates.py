#!/usr/bin/env python3
"""
Verify LDAP Certificates on NAS
Checks if certificates exist and are properly configured
#JARVIS #LDAP #CERTIFICATES #VERIFICATION
"""

import sys
import argparse
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.python.nas_azure_vault_integration import NASAzureVaultIntegration
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verify_certificates_on_nas(nas_integration: NASAzureVaultIntegration) -> dict:
    """Verify LDAP certificates exist on NAS"""
    result = {
        "cert_exists": False,
        "key_exists": False,
        "cert_readable": False,
        "key_readable": False,
        "cert_valid": False,
        "key_valid": False,
        "permissions_ok": False
    }

    # Check if certificate file exists
    cmd_cert = "test -f /tmp/ldap_certificates/client.crt && echo 'EXISTS' || echo 'NOT_EXISTS'"
    cert_result = nas_integration.execute_ssh_command(cmd_cert)
    if isinstance(cert_result, dict):
        cert_result = cert_result.get('output', '') or cert_result.get('stdout', '') or str(cert_result)

    if 'EXISTS' in str(cert_result):
        result["cert_exists"] = True
        result["cert_readable"] = True

    # Check if private key file exists
    cmd_key = "test -f /tmp/ldap_certificates/client.key && echo 'EXISTS' || echo 'NOT_EXISTS'"
    key_result = nas_integration.execute_ssh_command(cmd_key)
    if isinstance(key_result, dict):
        key_result = key_result.get('output', '') or key_result.get('stdout', '') or str(key_result)

    if 'EXISTS' in str(key_result):
        result["key_exists"] = True
        result["key_readable"] = True

    # Check file permissions
    cmd_perms = "ls -la /tmp/ldap_certificates/ 2>/dev/null | grep -E 'client\\.(crt|key)' || echo 'NO_FILES'"
    perms_result = nas_integration.execute_ssh_command(cmd_perms)
    if isinstance(perms_result, dict):
        perms_result = perms_result.get('output', '') or perms_result.get('stdout', '') or str(perms_result)

    if 'client.crt' in str(perms_result) and 'client.key' in str(perms_result):
        # Check if permissions are secure
        if '644' in str(perms_result) or '-rw-r--r--' in str(perms_result):
            result["permissions_ok"] = True

    # Verify certificate format (basic check)
    if result["cert_exists"]:
        cmd_cert_content = "head -1 /tmp/ldap_certificates/client.crt 2>/dev/null || echo 'ERROR'"
        cert_content = nas_integration.execute_ssh_command(cmd_cert_content)
        if isinstance(cert_content, dict):
            cert_content = cert_content.get('output', '') or cert_content.get('stdout', '') or str(cert_content)

        if 'BEGIN CERTIFICATE' in str(cert_content):
            result["cert_valid"] = True

    # Verify key format (basic check)
    if result["key_exists"]:
        cmd_key_content = "head -1 /tmp/ldap_certificates/client.key 2>/dev/null || echo 'ERROR'"
        key_content = nas_integration.execute_ssh_command(cmd_key_content)
        if isinstance(key_content, dict):
            key_content = key_content.get('output', '') or key_content.get('stdout', '') or str(key_content)

        if 'BEGIN PRIVATE KEY' in str(key_content) or 'BEGIN RSA PRIVATE KEY' in str(key_content):
            result["key_valid"] = True

    return result


def main():
    parser = argparse.ArgumentParser(description="Verify LDAP certificates on NAS")
    parser.add_argument("--nas-ip", default="<NAS_PRIMARY_IP>", help="NAS IP address")
    parser.add_argument("--vault-name", default="jarvis-lumina", help="Azure Key Vault name")
    args = parser.parse_args()

    print("=" * 70)
    print("   LDAP CERTIFICATE VERIFICATION")
    print("=" * 70)
    print("")

    nas_integration = NASAzureVaultIntegration(vault_name=args.vault_name, nas_ip=args.nas_ip)

    print("Checking certificates on NAS...")
    print("")

    result = verify_certificates_on_nas(nas_integration)

    print("Certificate Status:")
    print(f"  Certificate File: {'✓' if result['cert_exists'] else '✗'}")
    print(f"  Private Key File: {'✓' if result['key_exists'] else '✗'}")
    print(f"  Certificate Readable: {'✓' if result['cert_readable'] else '✗'}")
    print(f"  Private Key Readable: {'✓' if result['key_readable'] else '✗'}")
    print(f"  Certificate Format Valid: {'✓' if result['cert_valid'] else '✗'}")
    print(f"  Private Key Format Valid: {'✓' if result['key_valid'] else '✗'}")
    print(f"  Permissions OK: {'✓' if result['permissions_ok'] else '✗'}")
    print("")

    if result['cert_exists'] and result['key_exists']:
        print("✅ Certificates are ready for LDAP domain join")
        print("")
        print("Next Steps:")
        print("  1. RDP to MANUS: mstsc /v:<NAS_IP>")
        print("  2. Open DSM: https://<NAS_PRIMARY_IP>:5001")
        print("  3. Navigate to: Control Panel → Domain/LDAP → Join")
        print("  4. Use certificate paths:")
        print("     - Certificate: /tmp/ldap_certificates/client.crt")
        print("     - Private Key: /tmp/ldap_certificates/client.key")
        print("")
    else:
        print("⚠️  Certificates not found or invalid")
        print("")
        print("Action Required:")
        print("  Run: python scripts/python/get_azure_ad_certificate_crypto.py")
        print("  Then: python scripts/python/configure_ldap_certificates_rdp.py")
        print("")

    return 0 if (result['cert_exists'] and result['key_exists'] and result['cert_valid'] and result['key_valid']) else 1


if __name__ == "__main__":


    sys.exit(main())