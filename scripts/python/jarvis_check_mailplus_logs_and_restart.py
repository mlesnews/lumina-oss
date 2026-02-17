#!/usr/bin/env python3
"""
JARVIS: Check MailPlus Logs and Attempt Restart

Checks MailPlus-Server logs for errors and attempts restart via DSM API.

Tags: #JARVIS #MAILPLUS #LOGS #AUTOMATION @JARVIS @LUMINA
"""

import sys
import time
from pathlib import Path

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

logger = get_logger("JARVISCheckMailPlusLogs")


def check_logs_and_restart():
    """Check MailPlus logs and attempt restart"""
    try:
        from nas_azure_vault_integration import NASAzureVaultIntegration
        import paramiko

        nas_integration = NASAzureVaultIntegration()
        credentials = nas_integration.get_nas_credentials()

        if not credentials:
            logger.error("❌ Could not get NAS credentials")
            return False

        nas_ip = "<NAS_PRIMARY_IP>"

        logger.info("=" * 80)
        logger.info("📋 JARVIS: CHECKING MAILPLUS LOGS & ATTEMPTING RESTART")
        logger.info("=" * 80)
        logger.info("")

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        logger.info(f"🔌 Connecting to NAS: {nas_ip}")
        ssh.connect(
            nas_ip,
            username=credentials["username"],
            password=credentials["password"],
            timeout=10
        )

        # Check MailPlus logs
        logger.info("📋 Checking MailPlus-Server logs...")
        logger.info("-" * 80)

        log_paths = [
            "/var/log/mailplus.log",
            "/var/log/mailplus/mailplus.log",
            "/var/packages/MailPlus-Server/var/log/mailplus.log",
            "/var/log/synolog/mailplus.log",
        ]

        for log_path in log_paths:
            stdin, stdout, stderr = ssh.exec_command(f"tail -50 {log_path} 2>/dev/null || echo 'Log not found'")
            log_output = stdout.read().decode().strip()
            if log_output and "Log not found" not in log_output:
                logger.info(f"   Found log: {log_path}")
                logger.info(f"   Last 50 lines:")
                for line in log_output.split('\n')[-10:]:  # Show last 10 lines
                    if line.strip():
                        logger.info(f"      {line[:150]}")
                break

        # Check systemd/journalctl logs
        logger.info("")
        logger.info("📋 Checking systemd logs for MailPlus...")
        logger.info("-" * 80)
        stdin, stdout, stderr = ssh.exec_command("journalctl -u MailPlus-Server --no-pager -n 20 2>/dev/null || echo 'No systemd logs'")
        systemd_logs = stdout.read().decode().strip()
        if systemd_logs and "No systemd logs" not in systemd_logs:
            logger.info("   Recent systemd logs:")
            for line in systemd_logs.split('\n')[-10:]:
                if line.strip():
                    logger.info(f"      {line[:150]}")

        ssh.close()

        # Try DSM API restart
        logger.info("")
        logger.info("🚀 Attempting restart via DSM API...")
        logger.info("-" * 80)

        try:
            from synology_api_base import SynologyAPIBase

            api = SynologyAPIBase(nas_ip=nas_ip, nas_port=5001, verify_ssl=False)

            if api.login(credentials["username"], credentials["password"]):
                logger.info("✅ Logged in to DSM API")

                # Try Package Manager API to restart
                package_url = f"{api.base_url}/webapi/entry.cgi"

                # First, get package info
                params = {
                    "api": "SYNO.Core.Package",
                    "version": "1",
                    "method": "list",
                    "_sid": api.sid
                }

                response = api.session.get(package_url, params=params, timeout=10)
                data = response.json()

                if data.get("success"):
                    packages = data.get("data", {}).get("packages", [])

                    # Find MailPlus-Server
                    mailplus_pkg = None
                    for pkg in packages:
                        if "mailplus" in pkg.get("name", "").lower() and "server" in pkg.get("name", "").lower():
                            mailplus_pkg = pkg
                            break

                    if mailplus_pkg:
                        logger.info(f"   Found package: {mailplus_pkg.get('name')}")
                        pkg_id = mailplus_pkg.get("id")

                        # Try restart
                        logger.info("   Attempting restart...")
                        restart_params = {
                            "api": "SYNO.Core.Package",
                            "version": "1",
                            "method": "restart",
                            "id": pkg_id,
                            "_sid": api.sid
                        }

                        response = api.session.get(package_url, params=restart_params, timeout=30)
                        result = response.json()

                        if result.get("success"):
                            logger.info("✅ Restart command sent via API")
                            time.sleep(10)

                            # Check status
                            status_params = {
                                "api": "SYNO.Core.Package",
                                "version": "1",
                                "method": "list",
                                "_sid": api.sid
                            }
                            response = api.session.get(package_url, params=status_params, timeout=10)
                            data = response.json()

                            if data.get("success"):
                                packages = data.get("data", {}).get("packages", [])
                                for pkg in packages:
                                    if pkg.get("id") == pkg_id:
                                        status = pkg.get("status", "")
                                        logger.info(f"   Package status: {status}")
                                        if status == "running":
                                            logger.info("✅ MailPlus-Server is running!")
                                            api.logout()
                                            return True

                        logger.warning("⚠️  API restart may not have worked")
                    else:
                        logger.warning("⚠️  Could not find MailPlus-Server package in API")

                api.logout()
            else:
                logger.warning("⚠️  Failed to login to DSM API")
        except Exception as e:
            logger.warning(f"⚠️  DSM API method failed: {e}")

        logger.info("")
        logger.info("=" * 80)
        logger.info("🔧 MANUAL INTERVENTION REQUIRED")
        logger.info("=" * 80)
        logger.info("")
        logger.info("MailPlus-Server is in an abnormal state that requires manual restart:")
        logger.info("")
        logger.info("1. Open DSM: https://<NAS_PRIMARY_IP>:5001")
        logger.info("2. Go to: Package Center")
        logger.info("3. Find: MailPlus-Server")
        logger.info("4. Click: Action menu (three dots) → Restart")
        logger.info("")
        logger.info("If restart fails, check the logs above for errors.")
        logger.info("=" * 80)

        return False

    except ImportError:
        logger.error("❌ Required modules not available")
        return False
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = check_logs_and_restart()
    sys.exit(0 if success else 1)
