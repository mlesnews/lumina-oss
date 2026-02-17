#!/usr/bin/env python3
"""
Verify NAS Cron Tasks Installation
Checks if cron tasks are installed and running on NAS
#JARVIS #MANUS #NAS #CRON #VERIFICATION
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
import logging

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from nas_azure_vault_integration import NASAzureVaultIntegration
    import paramiko
    SSH_AVAILABLE = True
except ImportError:
    SSH_AVAILABLE = False

logger = get_logger("VerifyNASCronTasks")


class NASCronVerifier:
    """Verify NAS cron tasks installation and status"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.nas_ip = "<NAS_PRIMARY_IP>"

    def verify_cron_installation(self) -> Dict[str, Any]:
        """Verify cron tasks are installed on NAS"""
        if not SSH_AVAILABLE:
            return {
                "success": False,
                "error": "SSH not available (paramiko not installed)"
            }

        try:
            # Get credentials
            vault = NASAzureVaultIntegration()
            credentials = vault.get_nas_credentials()

            if not credentials:
                return {
                    "success": False,
                    "error": "Could not retrieve NAS credentials"
                }

            username = credentials.get("username")
            password = credentials.get("password")

            # Connect via SSH
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            logger.info(f"🔍 Connecting to NAS ({self.nas_ip})...")
            ssh.connect(
                hostname=self.nas_ip,
                port=22,
                username=username,
                password=password,
                timeout=30,
                allow_agent=False,
                look_for_keys=False
            )

            results = {
                "success": True,
                "cron_installed": False,
                "cron_tasks": [],
                "cron_file_exists": False,
                "cron_file_path": None,
                "logs_available": False
            }

            # Check if crontab command works
            logger.info("📋 Checking crontab installation...")
            stdin, stdout, stderr = ssh.exec_command("which crontab")
            crontab_path = stdout.read().decode().strip()

            if crontab_path:
                logger.info(f"✅ Crontab found: {crontab_path}")

                # Try to list cron jobs
                stdin, stdout, stderr = ssh.exec_command("crontab -l 2>&1")
                exit_status = stdout.channel.recv_exit_status()
                cron_output = stdout.read().decode().strip()
                error_output = stderr.read().decode().strip()

                if exit_status == 0 and cron_output:
                    results["cron_installed"] = True
                    results["cron_tasks"] = [line for line in cron_output.split('\n') if line.strip() and not line.startswith('#')]
                    logger.info(f"✅ Found {len(results['cron_tasks'])} cron tasks")
                elif "no crontab" in cron_output.lower() or "no crontab" in error_output.lower():
                    logger.warning("⚠️  No crontab installed for user")
                else:
                    logger.warning(f"⚠️  Could not read crontab: {error_output}")

            # Check for cron file we created
            logger.info("📁 Checking for deployed cron file...")
            stdin, stdout, stderr = ssh.exec_command("ls -la ~/.crontab_cursor_tasks_* 2>&1 | head -1")
            cron_file_output = stdout.read().decode().strip()

            if cron_file_output and "No such file" not in cron_file_output:
                # Extract filename
                cron_file_path = cron_file_output.split()[-1] if cron_file_output.split() else None
                if cron_file_path:
                    results["cron_file_exists"] = True
                    results["cron_file_path"] = cron_file_path
                    logger.info(f"✅ Found cron file: {cron_file_path}")

                    # Read file contents
                    stdin, stdout, stderr = ssh.exec_command(f"perl -pe '' {cron_file_path} || awk '{{print}}' {cron_file_path} || sed '' {cron_file_path}")
                    file_contents = stdout.read().decode()
                    logger.info(f"📄 File contains {len(file_contents.splitlines())} lines")
            else:
                logger.warning("⚠️  Cron file not found")

            # Check cron logs
            logger.info("📊 Checking cron logs...")
            log_paths = [
                "/var/log/cron.log",
                "/var/log/syslog",
                f"/var/log/cron.{username}.log"
            ]

            for log_path in log_paths:
                stdin, stdout, stderr = ssh.exec_command(f"test -r {log_path} && echo 'exists' || echo 'not found'")
                if stdout.read().decode().strip() == "exists":
                    results["logs_available"] = True
                    logger.info(f"✅ Cron logs available: {log_path}")
                    break

            ssh.close()

            return results

        except Exception as e:
            logger.error(f"❌ Error verifying cron: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def install_cron_if_missing(self) -> Dict[str, Any]:
        """Install cron tasks if they're missing"""
        verification = self.verify_cron_installation()

        if not verification.get("success"):
            return verification

        if verification.get("cron_installed"):
            return {
                "success": True,
                "message": "Cron tasks already installed",
                "tasks": verification.get("cron_tasks", [])
            }

        # Try to install from file
        if verification.get("cron_file_exists"):
            cron_file = verification.get("cron_file_path")

            try:
                vault = NASAzureVaultIntegration()
                credentials = vault.get_nas_credentials()

                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(
                    hostname=self.nas_ip,
                    port=22,
                    username=credentials.get("username"),
                    password=credentials.get("password"),
                    timeout=30,
                    allow_agent=False,
                    look_for_keys=False
                )

                logger.info(f"📥 Installing cron from file: {cron_file}")
                stdin, stdout, stderr = ssh.exec_command(f"perl -pe '' {cron_file} | crontab - || awk '{{print}}' {cron_file} | crontab - || sed '' {cron_file} | crontab - || crontab - < {cron_file}")
                exit_status = stdout.channel.recv_exit_status()

                if exit_status == 0:
                    logger.info("✅ Cron tasks installed successfully")
                    ssh.close()

                    # Verify installation
                    return self.verify_cron_installation()
                else:
                    error = stderr.read().decode()
                    logger.error(f"❌ Failed to install: {error}")
                    ssh.close()
                    return {
                        "success": False,
                        "error": f"Installation failed: {error}"
                    }

            except Exception as e:
                logger.error(f"❌ Error installing cron: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }

        return {
            "success": False,
            "error": "No cron file found to install"
        }


def main():
    try:
        """CLI interface"""
        import argparse
        import json

        parser = argparse.ArgumentParser(description="Verify NAS Cron Tasks")
        parser.add_argument("--install", action="store_true", help="Install cron tasks if missing")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        verifier = NASCronVerifier(project_root)

        if args.install:
            result = verifier.install_cron_if_missing()
        else:
            result = verifier.verify_cron_installation()

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result.get("success"):
                print("=" * 70)
                print("   NAS CRON TASKS VERIFICATION")
                print("=" * 70)
                print("")

                if result.get("cron_installed"):
                    print("✅ Cron tasks are installed")
                    tasks = result.get("cron_tasks", [])
                    if tasks:
                        print(f"\n📋 Found {len(tasks)} cron tasks:")
                        for task in tasks:
                            print(f"   • {task}")
                    else:
                        print("   (No active tasks found)")
                else:
                    print("⚠️  Cron tasks not installed")
                    if result.get("cron_file_exists"):
                        print(f"   Cron file found: {result.get('cron_file_path')}")
                        print("   Run with --install to install")

                if result.get("logs_available"):
                    print("\n✅ Cron logs are available")

                print("")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
                return 1

        return 0 if result.get("success") else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())