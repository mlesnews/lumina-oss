#!/usr/bin/env python3
"""
Ensure MailPlus Services Auto-Start on NAS

Configures MailPlus IMAP and SMTP services to start automatically on NAS boot.
Uses DSM API or SSH to configure service auto-start settings.

Tags: #NAS #MAILPLUS #AUTOSTART #SERVICE #OUTLOOK
@JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False

logger = get_logger("EnsureMailPlusAutoStart")

# Load NAS configuration
config_file = project_root / "config" / "outlook" / "hybrid_email_config.json"


def load_nas_config() -> Dict[str, Any]:
    """Load NAS configuration"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config.get("nas_mail_hub", {})
    except Exception as e:
        logger.warning(f"Could not load config: {e}")
        return {
            "server": "<NAS_PRIMARY_IP>",
            "domain": "<LOCAL_HOSTNAME>"
        }


class MailPlusAutoStartConfigurator:
    """Configure MailPlus services to auto-start"""

    def __init__(self, nas_config: Optional[Dict[str, Any]] = None):
        """Initialize configurator"""
        if nas_config is None:
            nas_config = load_nas_config()

        self.nas_config = nas_config
        self.nas_host = nas_config.get("server", "<NAS_PRIMARY_IP>")
        self.nas_port = 5001
        self.nas_ssh_port = 22

        # Try to get credentials from Azure Key Vault or config
        self.username = None
        self.password = None
        self._load_credentials()

    def _load_credentials(self) -> None:
        """Load NAS credentials from Azure Key Vault or config"""
        try:
            from nas_azure_vault_integration import NASAzureVaultIntegration
            nas_integration = NASAzureVaultIntegration()
            self.username = nas_integration.get_username()
            self.password = nas_integration.get_password()
            logger.info("✅ Loaded credentials from Azure Key Vault")
        except Exception as e:
            logger.warning(f"Could not load credentials from vault: {e}")
            # Fallback to config or environment
            self.username = self.nas_config.get("username", "admin")
            logger.warning("⚠️  Using default username. Set password via environment or config.")

    def check_services_status(self) -> Dict[str, Any]:
        """Check current status of MailPlus services"""
        logger.info("=" * 80)
        logger.info("CHECKING MAILPLUS SERVICES STATUS")
        logger.info("=" * 80)
        logger.info("")

        status = {
            "imap_running": False,
            "smtp_running": False,
            "imap_autostart": False,
            "smtp_autostart": False,
            "method": None
        }

        # Try SSH method first
        if PARAMIKO_AVAILABLE and self.password:
            status = self._check_via_ssh()
            if status.get("method") == "ssh":
                return status

        # Try DSM API method
        if REQUESTS_AVAILABLE:
            api_status = self._check_via_api()
            if api_status.get("method") == "api":
                return api_status

        # Fallback: Manual instructions
        logger.warning("⚠️  Could not check automatically. Providing manual instructions.")
        return status

    def _check_via_ssh(self) -> Dict[str, Any]:
        """Check service status via SSH"""
        if not PARAMIKO_AVAILABLE or not self.password:
            return {"method": None}

        try:
            logger.info("Attempting SSH connection to NAS...")
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=self.nas_host,
                port=self.nas_ssh_port,
                username=self.username,
                password=self.password,
                timeout=10
            )

            logger.info("✅ Connected via SSH")

            # Check MailPlus service status
            stdin, stdout, stderr = client.exec_command("synopkg status MailPlus")
            mailplus_status = stdout.read().decode().strip()

            # Check if IMAP/SMTP are enabled in MailPlus
            # This requires checking MailPlus configuration files
            stdin, stdout, stderr = client.exec_command(
                r"grep -i 'imap.*enable\|smtp.*enable' /var/packages/MailPlus/etc/mailplus.conf 2>/dev/null || echo 'config_not_found'"
            )
            config_output = stdout.read().decode().strip()

            client.close()

            status = {
                "method": "ssh",
                "mailplus_installed": "installed" in mailplus_status.lower() or "started" in mailplus_status.lower(),
                "mailplus_running": "started" in mailplus_status.lower() or "running" in mailplus_status.lower(),
                "config_accessible": "config_not_found" not in config_output
            }

            logger.info(f"   MailPlus installed: {status['mailplus_installed']}")
            logger.info(f"   MailPlus running: {status['mailplus_running']}")

            return status

        except Exception as e:
            logger.warning(f"SSH check failed: {e}")
            return {"method": None}

    def _check_via_api(self) -> Dict[str, Any]:
        """Check service status via DSM API"""
        if not REQUESTS_AVAILABLE:
            return {"method": None}

        try:
            # DSM API requires authentication first
            api_url = f"https://{self.nas_host}:{self.nas_port}/webapi"

            # Step 1: Get API info
            response = requests.get(
                f"{api_url}/query.cgi",
                params={
                    'api': 'SYNO.API.Info',
                    'version': '1',
                    'method': 'query'
                },
                verify=False,  # Self-signed certificate
                timeout=5
            )

            if response.status_code == 200:
                logger.info("✅ DSM API accessible")
                return {"method": "api", "api_accessible": True}
            else:
                return {"method": None}

        except Exception as e:
            logger.debug(f"API check failed: {e}")
            return {"method": None}

    def configure_autostart(self) -> Dict[str, Any]:
        """Configure MailPlus services to auto-start"""
        logger.info("=" * 80)
        logger.info("CONFIGURING MAILPLUS AUTO-START")
        logger.info("=" * 80)
        logger.info("")

        result = {
            "success": False,
            "method": None,
            "imap_configured": False,
            "smtp_configured": False,
            "instructions": []
        }

        # Try SSH method
        if PARAMIKO_AVAILABLE and self.password:
            ssh_result = self._configure_via_ssh()
            if ssh_result.get("success"):
                return ssh_result

        # Provide manual instructions
        logger.info("")
        logger.info("MANUAL CONFIGURATION REQUIRED")
        logger.info("=" * 80)
        logger.info("")
        logger.info("Follow these steps to ensure MailPlus services start automatically:")
        logger.info("")
        logger.info("1. Log into DSM:")
        logger.info(f"   URL: https://{self.nas_host}:{self.nas_port}")
        logger.info("")
        logger.info("2. Open MailPlus Server:")
        logger.info("   • Package Center → Installed → MailPlus Server")
        logger.info("   • Or: Main Menu → MailPlus Server")
        logger.info("")
        logger.info("3. Configure IMAP Service:")
        logger.info("   • Go to 'IMAP/POP3' tab")
        logger.info("   • Enable 'IMAP service'")
        logger.info("   • Set port: 993")
        logger.info("   • Enable SSL/TLS")
        logger.info("   • Check 'Start automatically' or 'Auto-start'")
        logger.info("")
        logger.info("4. Configure SMTP Service:")
        logger.info("   • Go to 'SMTP' tab")
        logger.info("   • Enable 'SMTP service'")
        logger.info("   • Set port: 587")
        logger.info("   • Enable STARTTLS")
        logger.info("   • Check 'Start automatically' or 'Auto-start'")
        logger.info("")
        logger.info("5. Save Settings:")
        logger.info("   • Click 'Apply' or 'Save'")
        logger.info("   • Services should start automatically on NAS boot")
        logger.info("")
        logger.info("6. Verify Services are Running:")
        logger.info("   • Check 'Status' tab in MailPlus Server")
        logger.info("   • IMAP should show 'Running' on port 993")
        logger.info("   • SMTP should show 'Running' on port 587")
        logger.info("")

        result["instructions"] = [
            "Log into DSM",
            "Open MailPlus Server",
            "Enable IMAP service (port 993, SSL/TLS)",
            "Enable SMTP service (port 587, STARTTLS)",
            "Check 'Start automatically' for both services",
            "Save and verify services are running"
        ]

        return result

    def _configure_via_ssh(self) -> Dict[str, Any]:
        """Configure auto-start via SSH"""
        if not PARAMIKO_AVAILABLE or not self.password:
            return {"success": False}

        try:
            logger.info("Attempting SSH configuration...")
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=self.nas_host,
                port=self.nas_ssh_port,
                username=self.username,
                password=self.password,
                timeout=10
            )

            logger.info("✅ Connected via SSH")

            # MailPlus auto-start is typically controlled by:
            # 1. Package auto-start (synopkg)
            # 2. Service configuration files

            # Enable MailPlus package auto-start
            logger.info("   Configuring MailPlus package auto-start...")
            stdin, stdout, stderr = client.exec_command("synopkg setstartonboot MailPlus")
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()

            if "success" in output.lower() or not error:
                logger.info("   ✅ MailPlus package auto-start configured")
            else:
                logger.warning(f"   ⚠️  Package auto-start: {error}")

            # Note: IMAP/SMTP service auto-start within MailPlus
            # typically needs to be configured via DSM UI or config files
            logger.info("   ⚠️  IMAP/SMTP service auto-start needs DSM UI configuration")
            logger.info("   (See manual instructions below)")

            client.close()

            return {
                "success": True,
                "method": "ssh",
                "package_autostart": True,
                "services_need_manual": True
            }

        except Exception as e:
            logger.warning(f"SSH configuration failed: {e}")
            return {"success": False}

    def verify_services(self) -> Dict[str, Any]:
        """Verify that services are running"""
        logger.info("")
        logger.info("=" * 80)
        logger.info("VERIFYING SERVICES")
        logger.info("=" * 80)
        logger.info("")

        import socket

        results = {
            "imap_accessible": False,
            "smtp_accessible": False,
            "imap_port": 993,
            "smtp_port": 587
        }

        # Test IMAP port
        logger.info("Testing IMAP port 993...")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.nas_host, 993))
            sock.close()
            results["imap_accessible"] = (result == 0)
            if results["imap_accessible"]:
                logger.info("   ✅ IMAP service is accessible")
            else:
                logger.warning("   ❌ IMAP service is NOT accessible")
        except Exception as e:
            logger.warning(f"   ⚠️  IMAP test error: {e}")

        # Test SMTP port
        logger.info("Testing SMTP port 587...")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.nas_host, 587))
            sock.close()
            results["smtp_accessible"] = (result == 0)
            if results["smtp_accessible"]:
                logger.info("   ✅ SMTP service is accessible")
            else:
                logger.warning("   ❌ SMTP service is NOT accessible")
        except Exception as e:
            logger.warning(f"   ⚠️  SMTP test error: {e}")

        return results


def main():
    try:
        """Main function"""
        import argparse

        parser = argparse.ArgumentParser(description="Ensure MailPlus Services Auto-Start")
        parser.add_argument("--check", action="store_true", help="Check current status")
        parser.add_argument("--configure", action="store_true", help="Configure auto-start")
        parser.add_argument("--verify", action="store_true", help="Verify services are running")

        args = parser.parse_args()

        configurator = MailPlusAutoStartConfigurator()

        if args.check:
            status = configurator.check_services_status()
            logger.info(f"\nStatus: {json.dumps(status, indent=2)}")

        if args.configure:
            result = configurator.configure_autostart()
            logger.info(f"\nConfiguration result: {json.dumps(result, indent=2)}")

        if args.verify:
            results = configurator.verify_services()
            logger.info(f"\nVerification results: {json.dumps(results, indent=2)}")

        if not any([args.check, args.configure, args.verify]):
            # Default: do all
            logger.info("Running full configuration check...")
            logger.info("")

            # Check status
            status = configurator.check_services_status()

            # Configure
            result = configurator.configure_autostart()

            # Verify
            verify_results = configurator.verify_services()

            # Summary
            logger.info("")
            logger.info("=" * 80)
            logger.info("SUMMARY")
            logger.info("=" * 80)
            logger.info("")
            logger.info(f"IMAP Service: {'✅ Accessible' if verify_results['imap_accessible'] else '❌ Not accessible'}")
            logger.info(f"SMTP Service: {'✅ Accessible' if verify_results['smtp_accessible'] else '❌ Not accessible'}")
            logger.info("")
            logger.info("Next Steps:")
            logger.info("1. Follow manual configuration steps above if services are not accessible")
            logger.info("2. Verify services start automatically after NAS reboot")
            logger.info("3. Run this script again to verify: python ensure_mailplus_autostart.py --verify")
            logger.info("")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()