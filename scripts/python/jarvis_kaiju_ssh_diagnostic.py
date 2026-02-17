#!/usr/bin/env python3
"""
JARVIS KAIJU SSH Diagnostic
Diagnoses SSH connectivity to KAIJU_NO_8 and credential requirements.

Tags: #DIAGNOSTIC #SSH #KAIJU @AUTO
"""

import sys
import paramiko
import socket
from pathlib import Path
from typing import Dict, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from nas_azure_vault_integration import NASAzureVaultIntegration
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    NASAzureVaultIntegration = None

logger = get_logger("JARVISKAIJUSSH")


class KAIJUSSHDiagnostic:
    """Diagnose SSH connectivity to KAIJU_NO_8"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.kaiju_ip = "<NAS_IP>"
        self.kaiju_ssh_port = 22

    def check_port(self) -> Dict[str, Any]:
        """Check if SSH port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.kaiju_ip, self.kaiju_ssh_port))
            sock.close()

            if result == 0:
                return {"open": True, "accessible": True}
            else:
                return {"open": False, "accessible": False, "error": f"Connection refused (code: {result})"}
        except Exception as e:
            return {"open": False, "accessible": False, "error": str(e)}

    def test_ssh_connection(self, username: str, password: str) -> Dict[str, Any]:
        """Test SSH connection with credentials"""
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=self.kaiju_ip,
                port=self.kaiju_ssh_port,
                username=username,
                password=password,
                timeout=10
            )

            # Test a simple command
            stdin, stdout, stderr = client.exec_command("echo 'SSH connection successful'", timeout=5)
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()

            client.close()

            return {
                "success": True,
                "output": output,
                "error": error,
                "message": "SSH connection successful"
            }
        except paramiko.AuthenticationException:
            return {
                "success": False,
                "error": "Authentication failed",
                "message": "Invalid username or password"
            }
        except paramiko.SSHException as e:
            return {
                "success": False,
                "error": f"SSH error: {e}",
                "message": "SSH connection failed"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Connection failed"
            }

    def check_credentials(self) -> Dict[str, Any]:
        """Check available credentials from Azure Key Vault"""
        credentials = {}

        if NASAzureVaultIntegration:
            try:
                # Try KAIJU-specific credentials first
                kaiju_integration = NASAzureVaultIntegration(nas_ip=self.kaiju_ip)
                kaiju_creds = kaiju_integration.get_nas_credentials()

                if kaiju_creds:
                    credentials["kaiju"] = {
                        "username": kaiju_creds.get("username", "N/A"),
                        "password_set": bool(kaiju_creds.get("password")),
                        "source": "Azure Key Vault (KAIJU IP)"
                    }

                # Try NAS credentials (might work if same)
                nas_integration = NASAzureVaultIntegration(nas_ip="<NAS_PRIMARY_IP>")
                nas_creds = nas_integration.get_nas_credentials()

                if nas_creds:
                    credentials["nas"] = {
                        "username": nas_creds.get("username", "N/A"),
                        "password_set": bool(nas_creds.get("password")),
                        "source": "Azure Key Vault (NAS IP)"
                    }
            except Exception as e:
                credentials["error"] = str(e)
        else:
            credentials["error"] = "NASAzureVaultIntegration not available"

        return credentials

    def diagnose(self) -> Dict[str, Any]:
        """Run full diagnostic"""
        self.logger.info("="*80)
        self.logger.info("KAIJU_NO_8 SSH DIAGNOSTIC")
        self.logger.info("="*80)

        diagnostic = {
            "kaiju_ip": self.kaiju_ip,
            "ssh_port": self.kaiju_ssh_port,
            "port_check": {},
            "credentials": {},
            "ssh_test": {}
        }

        # Check port
        self.logger.info(f"\n1. Checking SSH port ({self.kaiju_ip}:{self.kaiju_ssh_port})...")
        port_check = self.check_port()
        diagnostic["port_check"] = port_check

        if port_check.get("open"):
            self.logger.info("   ✅ SSH port is OPEN")
        else:
            self.logger.error(f"   ❌ SSH port is CLOSED: {port_check.get('error', 'Unknown error')}")
            return diagnostic

        # Check credentials
        self.logger.info("\n2. Checking available credentials...")
        credentials = self.check_credentials()
        diagnostic["credentials"] = credentials

        if credentials.get("kaiju"):
            kaiju_creds = credentials["kaiju"]
            self.logger.info(f"   ✅ KAIJU credentials found:")
            self.logger.info(f"      Username: {kaiju_creds.get('username')}")
            self.logger.info(f"      Password: {'✅ SET' if kaiju_creds.get('password_set') else '❌ NOT SET'}")
        else:
            self.logger.warning("   ⚠️  No KAIJU-specific credentials found")

        if credentials.get("nas"):
            nas_creds = credentials["nas"]
            self.logger.info(f"   ℹ️  NAS credentials available (may differ):")
            self.logger.info(f"      Username: {nas_creds.get('username')}")

        # Test SSH connection if credentials available
        if credentials.get("kaiju") and credentials.get("kaiju").get("password_set"):
            self.logger.info("\n3. Testing SSH connection with KAIJU credentials...")
            # Note: We can't actually test without the password value, but we can show what we have
            self.logger.info("   ℹ️  Credentials available - manual test recommended")
            self.logger.info(f"   Test command: ssh {credentials['kaiju']['username']}@{self.kaiju_ip}")

        self.logger.info("\n" + "="*80)
        self.logger.info("DIAGNOSTIC SUMMARY")
        self.logger.info("="*80)
        self.logger.info(f"Port Status: {'✅ OPEN' if port_check.get('open') else '❌ CLOSED'}")
        self.logger.info(f"Credentials: {'✅ AVAILABLE' if credentials.get('kaiju') else '❌ NOT FOUND'}")

        return diagnostic


def main():
    try:
        """CLI interface"""
        project_root = Path(__file__).parent.parent.parent
        diagnostic = KAIJUSSHDiagnostic(project_root)
        result = diagnostic.diagnose()

        import json
        print("\n" + json.dumps(result, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()