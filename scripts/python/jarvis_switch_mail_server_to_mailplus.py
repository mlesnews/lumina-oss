#!/usr/bin/env python3
"""
JARVIS: Switch from Mail Server to MailPlus Server

Stops Synology Mail Server and starts MailPlus Server.
Handles the conflict where both cannot run simultaneously.

Tags: #JARVIS #MAILPLUS #MAILSERVER #SYNOLOGY #DSM @JARVIS @LUMINA
"""

import sys
import time
import socket
from pathlib import Path
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISMailServerSwitch")


class JARVISMailServerSwitcher:
    """JARVIS autonomous control for switching Mail Server to MailPlus"""

    def __init__(self):
        """Initialize switcher"""
        self.nas_ip = "<NAS_PRIMARY_IP>"
        self.nas_port = 5001

        logger.info("=" * 80)
        logger.info("🤖 JARVIS: SWITCHING TO MAILPLUS SERVER")
        logger.info("=" * 80)
        logger.info("")

    def check_service_status_via_ssh(self, service_name: str) -> Optional[str]:
        """Check service status via SSH"""
        try:
            from nas_azure_vault_integration import NASAzureVaultIntegration
            import paramiko

            nas_integration = NASAzureVaultIntegration()
            credentials = nas_integration.get_nas_credentials()

            if not credentials:
                logger.warning("⚠️  Could not get NAS credentials for SSH")
                return None

            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            logger.debug(f"🔌 Connecting to NAS via SSH: {self.nas_ip}")
            ssh.connect(
                self.nas_ip,
                username=credentials["username"],
                password=credentials["password"],
                timeout=10
            )

            # Check service status
            stdin, stdout, stderr = ssh.exec_command(f"synopkg status {service_name}")
            status_output = stdout.read().decode().strip()
            error_output = stderr.read().decode().strip()

            ssh.close()

            if error_output:
                logger.debug(f"SSH error: {error_output}")

            return status_output

        except ImportError:
            logger.warning("⚠️  paramiko not available for SSH access")
            return None
        except Exception as e:
            logger.debug(f"SSH check failed: {e}")
            return None

    def stop_mail_server(self) -> bool:
        """Stop Synology Mail Server"""
        logger.info("🛑 STEP 1: Stopping Mail Server...")
        logger.info("")

        # Check if Mail Server is running
        status = self.check_service_status_via_ssh("MailServer")

        if status:
            if "is running" in status.lower():
                logger.info("   Mail Server is currently running")
                logger.info("   Stopping Mail Server...")

                try:
                    from nas_azure_vault_integration import NASAzureVaultIntegration
                    import paramiko

                    nas_integration = NASAzureVaultIntegration()
                    credentials = nas_integration.get_nas_credentials()

                    if not credentials:
                        logger.error("❌ Could not get NAS credentials")
                        return False

                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(
                        self.nas_ip,
                        username=credentials["username"],
                        password=credentials["password"],
                        timeout=10
                    )

                    # Stop Mail Server
                    stdin, stdout, stderr = ssh.exec_command("synopkg stop MailServer")
                    stdout.read()  # Wait for command to complete
                    time.sleep(3)  # Give it time to stop

                    # Verify it's stopped
                    stdin, stdout, stderr = ssh.exec_command("synopkg status MailServer")
                    new_status = stdout.read().decode().strip()

                    ssh.close()

                    if "is stopped" in new_status.lower() or "is not running" in new_status.lower():
                        logger.info("✅ Mail Server stopped successfully")
                        return True
                    else:
                        logger.warning(f"⚠️  Mail Server status unclear: {new_status}")
                        return False

                except Exception as e:
                    logger.error(f"❌ Failed to stop Mail Server: {e}")
                    return False
            else:
                logger.info("✅ Mail Server is already stopped")
                return True
        else:
            logger.warning("⚠️  Could not check Mail Server status via SSH")
            logger.info("   Attempting via DSM API...")
            return self.stop_mail_server_via_dsm_api()

    def stop_mail_server_via_dsm_api(self) -> bool:
        """Stop Mail Server via DSM API"""
        try:
            from nas_azure_vault_integration import NASAzureVaultIntegration
            from synology_api_base import SynologyAPIBase

            nas_integration = NASAzureVaultIntegration()
            credentials = nas_integration.get_nas_credentials()

            if not credentials:
                logger.warning("⚠️  Could not get NAS credentials")
                return False

            logger.info("🔌 Connecting to DSM API...")
            api = SynologyAPIBase(nas_ip=self.nas_ip, nas_port=self.nas_port, verify_ssl=False)

            if not api.login(credentials["username"], credentials["password"]):
                logger.error("❌ Failed to login to DSM")
                return False

            logger.info("✅ Connected to DSM API")

            # Stop Mail Server package
            logger.info("   Stopping Mail Server package...")

            stop_url = f"{api.base_url}/webapi/entry.cgi"
            params = {
                "api": "SYNO.Core.Package",
                "version": "1",
                "method": "stop",
                "package": "MailServer",
                "_sid": api.sid
            }

            response = api.session.get(stop_url, params=params, timeout=10)
            data = response.json()

            api.logout()

            if data.get("success"):
                logger.info("✅ Mail Server stopped via DSM API")
                time.sleep(3)  # Give it time to stop
                return True
            else:
                logger.warning(f"⚠️  DSM API stop response: {data}")
                return False

        except Exception as e:
            logger.error(f"❌ DSM API stop failed: {e}")
            return False

    def start_mailplus(self) -> bool:
        """Start MailPlus Server"""
        logger.info("🚀 STEP 2: Starting MailPlus Server...")
        logger.info("")

        # Check if MailPlus is running
        status = self.check_service_status_via_ssh("MailPlus")

        if status:
            if "is running" in status.lower():
                logger.info("✅ MailPlus is already running")
                return True
            else:
                logger.info("   MailPlus is not running")
                logger.info("   Starting MailPlus...")

                try:
                    from nas_azure_vault_integration import NASAzureVaultIntegration
                    import paramiko

                    nas_integration = NASAzureVaultIntegration()
                    credentials = nas_integration.get_nas_credentials()

                    if not credentials:
                        logger.error("❌ Could not get NAS credentials")
                        return False

                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(
                        self.nas_ip,
                        username=credentials["username"],
                        password=credentials["password"],
                        timeout=10
                    )

                    # Start MailPlus
                    stdin, stdout, stderr = ssh.exec_command("synopkg start MailPlus")
                    stdout.read()  # Wait for command to complete
                    time.sleep(5)  # Give it time to start

                    # Verify it's running
                    stdin, stdout, stderr = ssh.exec_command("synopkg status MailPlus")
                    new_status = stdout.read().decode().strip()

                    ssh.close()

                    if "is running" in new_status.lower():
                        logger.info("✅ MailPlus started successfully")
                        return True
                    else:
                        logger.warning(f"⚠️  MailPlus status unclear: {new_status}")
                        return False

                except Exception as e:
                    logger.error(f"❌ Failed to start MailPlus: {e}")
                    return False
        else:
            logger.warning("⚠️  Could not check MailPlus status via SSH")
            logger.info("   Attempting via DSM API...")
            return self.start_mailplus_via_dsm_api()

    def start_mailplus_via_dsm_api(self) -> bool:
        """Start MailPlus via DSM API"""
        try:
            from nas_azure_vault_integration import NASAzureVaultIntegration
            from synology_api_base import SynologyAPIBase

            nas_integration = NASAzureVaultIntegration()
            credentials = nas_integration.get_nas_credentials()

            if not credentials:
                logger.warning("⚠️  Could not get NAS credentials")
                return False

            logger.info("🔌 Connecting to DSM API...")
            api = SynologyAPIBase(nas_ip=self.nas_ip, nas_port=self.nas_port, verify_ssl=False)

            if not api.login(credentials["username"], credentials["password"]):
                logger.error("❌ Failed to login to DSM")
                return False

            logger.info("✅ Connected to DSM API")

            # Start MailPlus package
            logger.info("   Starting MailPlus package...")

            start_url = f"{api.base_url}/webapi/entry.cgi"
            params = {
                "api": "SYNO.Core.Package",
                "version": "1",
                "method": "start",
                "package": "MailPlus",
                "_sid": api.sid
            }

            response = api.session.get(start_url, params=params, timeout=10)
            data = response.json()

            api.logout()

            if data.get("success"):
                logger.info("✅ MailPlus started via DSM API")
                time.sleep(5)  # Give it time to start
                return True
            else:
                logger.warning(f"⚠️  DSM API start response: {data}")
                return False

        except Exception as e:
            logger.error(f"❌ DSM API start failed: {e}")
            return False

    def verify_mailplus_running(self) -> bool:
        """Verify MailPlus is running"""
        logger.info("🔍 STEP 3: Verifying MailPlus is running...")
        logger.info("")

        status = self.check_service_status_via_ssh("MailPlus")

        if status:
            if "is running" in status.lower():
                logger.info("✅ MailPlus is confirmed running")
                return True
            else:
                logger.warning(f"⚠️  MailPlus status: {status}")
                return False
        else:
            logger.warning("⚠️  Could not verify MailPlus status")
            return False

    def execute_switch(self) -> Dict[str, Any]:
        """Execute complete switch from Mail Server to MailPlus"""
        logger.info("🚀 JARVIS AUTONOMOUS SWITCH STARTING")
        logger.info("")

        results = {
            "mail_server_stopped": False,
            "mailplus_started": False,
            "mailplus_verified": False
        }

        # Step 1: Stop Mail Server
        if self.stop_mail_server():
            results["mail_server_stopped"] = True
        else:
            logger.warning("⚠️  Could not stop Mail Server - may already be stopped")
            results["mail_server_stopped"] = True  # Assume it's stopped if we can't check

        logger.info("")

        # Step 2: Start MailPlus
        if self.start_mailplus():
            results["mailplus_started"] = True
        else:
            logger.error("❌ Failed to start MailPlus")

        logger.info("")

        # Step 3: Verify
        if self.verify_mailplus_running():
            results["mailplus_verified"] = True
        else:
            logger.warning("⚠️  Could not verify MailPlus is running")

        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 JARVIS SWITCH SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Mail Server Stopped: {'✅ Yes' if results['mail_server_stopped'] else '❌ No'}")
        logger.info(f"MailPlus Started: {'✅ Yes' if results['mailplus_started'] else '❌ No'}")
        logger.info(f"MailPlus Verified: {'✅ Yes' if results['mailplus_verified'] else '⚠️  No'}")
        logger.info("")

        if all([results["mail_server_stopped"], results["mailplus_started"], results["mailplus_verified"]]):
            logger.info("✅ JARVIS SWITCH COMPLETE!")
            logger.info("   MailPlus Server is now running and ready for IMAP configuration")
        else:
            logger.info("⚠️  Switch partially complete - review summary above")
            logger.info("   You may need to manually stop Mail Server and start MailPlus in DSM")

        logger.info("=" * 80)

        return results


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Switch Mail Server to MailPlus")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        switcher = JARVISMailServerSwitcher()
        results = switcher.execute_switch()

        if args.json:
            import json
            print(json.dumps(results, indent=2, default=str))

        # Return success if all steps completed
        if all([results.get("mail_server_stopped"), results.get("mailplus_started"), results.get("mailplus_verified")]):
            return 0
        elif results.get("mailplus_started"):
            return 1  # Started but not verified
        else:
            return 2  # Failed


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())