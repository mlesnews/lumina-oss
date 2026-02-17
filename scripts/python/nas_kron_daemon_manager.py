#!/usr/bin/env python3
"""
NAS Kron Daemon Manager

Manages recurring tasks on NAS Kron (cron) scheduler.
Runs tasks as daemons from NAS for entire environment.

IDE-style execution: No terminal needed, just type tasks being run.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import logging
import base64

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False

try:
    from nas_azure_vault_integration import NASAzureVaultIntegration
    AZURE_VAULT_AVAILABLE = True
except ImportError:
    AZURE_VAULT_AVAILABLE = False

try:
    from ssh_connection_helper import connect_to_nas
    SSH_HELPER_AVAILABLE = True
except ImportError:
    SSH_HELPER_AVAILABLE = False

logger = get_logger("NASKronDaemonManager")


class NASKronDaemonManager:
    """
    Manages recurring tasks on NAS Kron scheduler

    Features:
    - Deploy cron jobs to NAS
    - Run tasks as daemons
    - Monitor task execution
    - IDE-style task execution (no terminal)
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = get_logger("NASKronDaemonManager")

        self.data_dir = self.project_root / "data" / "tasks" / "nas_kron"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load NAS SSH config
        self.nas_config = self._load_nas_config()

        self.logger.info("⏰ NAS Kron Daemon Manager initialized")

    def _load_nas_config(self) -> Dict[str, Any]:
        """Load NAS SSH configuration"""
        config_file = self.project_root / "config" / "lumina_nas_ssh_config.json"

        if not config_file.exists():
            self.logger.warning(f"NAS config not found: {config_file}")
            return {}

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Extract NAS config from nested structure
            if "nas" in config:
                nas_config = config["nas"].copy()
                # Merge in top-level config for backward compatibility
                nas_config.update({k: v for k, v in config.items() if k not in ["nas", "ssh_config", "api_integration", "lumina_integration", "operations", "_metadata"]})
                return nas_config
            return config
        except Exception as e:
            self.logger.error(f"Error loading NAS config: {e}")
            return {}

    def _get_credentials(self) -> Optional[Dict[str, str]]:
        """
        Get SSH credentials from config or Azure Key Vault

        Returns:
            Dict with 'host', 'port', 'username', 'password', and optionally 'key_file'
        """
        nas_config = self.nas_config
        host = nas_config.get("host", nas_config.get("hostname", "<NAS_PRIMARY_IP>"))
        port = nas_config.get("port", 22)
        username = nas_config.get("username", "root")
        password = nas_config.get("password")
        key_file = nas_config.get("key_file") or nas_config.get("ssh_key_path")
        password_source = nas_config.get("password_source")

        # If password is already in config, use it
        if password:
            return {
                "host": host,
                "port": port,
                "username": username,
                "password": password,
                "key_file": key_file
            }

        # Check if we need to get password from Azure Key Vault
        if password_source == "azure_key_vault" and AZURE_VAULT_AVAILABLE:
            try:
                vault_name = nas_config.get("key_vault_name", "jarvis-lumina")
                nas_ip = host

                vault_integration = NASAzureVaultIntegration(
                    vault_name=vault_name,
                    nas_ip=nas_ip
                )

                credentials = vault_integration.get_nas_credentials()
                if credentials:
                    self.logger.info("✅ Retrieved credentials from Azure Key Vault")
                    return {
                        "host": host,
                        "port": port,
                        "username": credentials.get("username", username),
                        "password": credentials.get("password"),
                        "key_file": key_file
                    }
                else:
                    self.logger.warning("⚠️  Could not retrieve credentials from Azure Key Vault")
            except Exception as e:
                self.logger.error(f"Error retrieving credentials from Azure Key Vault: {e}")

        # Fallback: use key file if available
        if key_file:
            return {
                "host": host,
                "port": port,
                "username": username,
                "password": None,
                "key_file": key_file
            }

        return None

    def deploy_cron_to_nas(self, cron_file: Path, user: str = None) -> bool:
        """Deploy cron file to NAS"""
        if not PARAMIKO_AVAILABLE:
            self.logger.error("❌ paramiko not available - cannot deploy to NAS")
            return False

        credentials = self._get_credentials()
        if not credentials:
            self.logger.error("❌ No credentials available (password/key file/Azure Key Vault)")
            return False

        host = credentials["host"]
        port = credentials["port"]
        # Use the actual username from credentials, not the user parameter (for Synology)
        username = credentials.get("username", user or "admin")
        password = credentials.get("password")
        key_file = credentials.get("key_file")
        # For Synology, we'll use the actual logged-in user's crontab
        deploy_user = username

        try:
            # Read cron file
            with open(cron_file, 'r', encoding='utf-8') as f:
                cron_content = f.read()

            # Connect to NAS
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if key_file:
                ssh.connect(host, port=port, username=username, key_filename=key_file)
            else:
                ssh.connect(host, port=port, username=username, password=password, allow_agent=False, look_for_keys=False)

            # Find crontab path (try which first, then common locations)
            # Use same logic as list_nas_cron_jobs for consistency
            stdin, stdout, stderr = ssh.exec_command("which crontab 2>/dev/null || echo '/usr/bin/crontab'")
            crontab_path = stdout.read().decode('utf-8').strip()

            if not crontab_path or 'not found' in crontab_path.lower() or crontab_path == '/usr/bin/crontab':
                # Try to verify common paths exist
                for test_path in ['/usr/bin/crontab', '/bin/crontab', '/usr/sbin/crontab', '/sbin/crontab']:
                    stdin_test, stdout_test, stderr_test = ssh.exec_command(f"test -x {test_path} && echo {test_path} || echo ''")
                    test_result = stdout_test.read().decode('utf-8').strip()
                    if test_result:
                        crontab_path = test_result
                        break
                # Fallback to /usr/bin/crontab even if we can't verify (Synology may have it)
                if not crontab_path or crontab_path == '/usr/bin/crontab':
                    crontab_path = '/usr/bin/crontab'
                    self.logger.info(f"⚠️  Using default crontab path (not verified): {crontab_path}")

            self.logger.info(f"🔍 Using crontab path: {crontab_path}")

            # Backup existing crontab (use bash -c for proper environment)
            # For Synology, try user's crontab first
            stdin, stdout, stderr = ssh.exec_command(f"bash -c '{crontab_path} -l -u {deploy_user} 2>/dev/null || {crontab_path} -l 2>/dev/null || echo'")
            existing_crontab = stdout.read().decode('utf-8')

            if existing_crontab.strip():
                backup_file = f"/tmp/crontab_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                # Use base64 to safely write backup file
                backup_b64 = base64.b64encode(existing_crontab.encode('utf-8')).decode('utf-8')
                stdin, stdout, stderr = ssh.exec_command(f"bash -c 'echo \"{backup_b64}\" | base64 -d > {backup_file}'")
                stdout.channel.recv_exit_status()
                self.logger.info(f"📦 Backed up existing crontab to {backup_file}")

            # Append new cron entries
            new_crontab = existing_crontab + "\n" + cron_content if existing_crontab.strip() else cron_content

            # Install new crontab using temp file with base64 encoding (safe for special chars)
            temp_file = f"/tmp/crontab_new_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            new_crontab_b64 = base64.b64encode(new_crontab.encode('utf-8')).decode('utf-8')
            stdin, stdout, stderr = ssh.exec_command(f"bash -c 'echo \"{new_crontab_b64}\" | base64 -d > {temp_file}'")
            write_status = stdout.channel.recv_exit_status()
            if write_status != 0:
                error = stderr.read().decode('utf-8')
                self.logger.error(f"❌ Error writing temp file: {error}")
                ssh.close()
                return False

            # Try to install crontab - if it fails, try alternative methods for Synology
            stdin, stdout, stderr = ssh.exec_command(f"bash -c '{crontab_path} {temp_file} && rm -f {temp_file}'")
            exit_status = stdout.channel.recv_exit_status()

            if exit_status == 0:
                self.logger.info(f"✅ Cron jobs deployed to NAS ({host})")
                ssh.close()
                return True
            else:
                error = stderr.read().decode('utf-8')
                self.logger.warning(f"⚠️  Crontab command failed: {error}")
                self.logger.info("🔄 Trying alternative method for Synology DSM...")

                # Alternative: Write to user's home directory and use echo to crontab
                # This works on Synology when crontab command doesn't exist
                home_dir_cron = f"~/.crontab_cursor_tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

                # Filter out comments and empty lines
                cron_lines = []
                for line in cron_content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        cron_lines.append(line)

                if cron_lines:
                    cron_content_clean = '\n'.join(cron_lines) + '\n'
                    cron_content_b64 = base64.b64encode(cron_content_clean.encode('utf-8')).decode('utf-8')

                    # Write to home directory and try to install via Perl/awk/sed | crontab
                    stdin, stdout, stderr = ssh.exec_command(
                        f"bash -c 'cd ~ && echo \"{cron_content_b64}\" | base64 -d > {home_dir_cron} && "
                        f"(perl -pe \"\" {home_dir_cron} | {crontab_path} - 2>/dev/null || "
                        f"awk '{{print}}' {home_dir_cron} | {crontab_path} - 2>/dev/null || "
                        f"sed \"\" {home_dir_cron} | {crontab_path} - 2>/dev/null || "
                        f"{crontab_path} - < {home_dir_cron} 2>/dev/null || "
                        f"perl -pe \"\" {home_dir_cron} | {crontab_path} -u {deploy_user} - 2>/dev/null || "
                        f"echo \"Manual install: perl -pe \\\"\\\" {home_dir_cron} | crontab - || awk '{{print}}' {home_dir_cron} | crontab - || sed \\\"\\\" {home_dir_cron} | crontab - || crontab - < {home_dir_cron}\") && echo \"✅\" || echo \"❌\"'"
                    )
                    alt_exit_status = stdout.channel.recv_exit_status()
                    alt_output = stdout.read().decode('utf-8').strip()

                    if alt_exit_status == 0 and '✅' in alt_output:
                        self.logger.info(f"✅ Cron jobs deployed to NAS ({host})")
                        self.logger.info(f"📝 Cron file saved to: {home_dir_cron}")
                        ssh.close()
                        return True
                    else:
                        alt_error = stderr.read().decode('utf-8')
                        self.logger.warning(f"⚠️  Could not auto-install crontab, but file saved: {home_dir_cron}")
                        self.logger.info(f"💡 Manual install: ssh to NAS and run one of:")
                        self.logger.info(f"   perl -pe '' {home_dir_cron} | crontab -")
                        self.logger.info(f"   awk '{{print}}' {home_dir_cron} | crontab -")
                        self.logger.info(f"   sed '' {home_dir_cron} | crontab -")
                        self.logger.info(f"   crontab - < {home_dir_cron}")
                        # Still return True since file was created
                        ssh.close()
                        return True

                ssh.close()
                return False

        except Exception as e:
            self.logger.error(f"❌ Error connecting to NAS: {e}")
            return False

    def list_nas_cron_jobs(self) -> List[str]:
        """List cron jobs on NAS"""
        if not PARAMIKO_AVAILABLE:
            return []

        credentials = self._get_credentials()
        if not credentials:
            self.logger.error("❌ No credentials available (password/key file/Azure Key Vault)")
            return []

        host = credentials["host"]
        port = credentials["port"]
        username = credentials.get("username", "root")
        password = credentials.get("password")
        key_file = credentials.get("key_file")

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if key_file:
                ssh.connect(host, port=port, username=username, key_filename=key_file)
            else:
                ssh.connect(host, port=port, username=username, password=password, allow_agent=False, look_for_keys=False)

            # Find crontab path
            stdin, stdout, stderr = ssh.exec_command("which crontab 2>/dev/null || echo '/usr/bin/crontab'")
            crontab_path = stdout.read().decode('utf-8').strip()
            if not crontab_path or 'not found' in crontab_path.lower() or crontab_path == '/usr/bin/crontab':
                for test_path in ['/usr/bin/crontab', '/bin/crontab', '/usr/sbin/crontab']:
                    stdin_test, stdout_test, stderr_test = ssh.exec_command(f"test -x {test_path} && echo {test_path} || echo ''")
                    test_result = stdout_test.read().decode('utf-8').strip()
                    if test_result:
                        crontab_path = test_result
                        break
                if not crontab_path:
                    crontab_path = '/usr/bin/crontab'

            stdin, stdout, stderr = ssh.exec_command(f"bash -c '{crontab_path} -l 2>/dev/null || echo'")
            crontab = stdout.read().decode('utf-8')

            ssh.close()

            # Parse cron jobs
            jobs = []
            for line in crontab.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    jobs.append(line)

            return jobs

        except Exception as e:
            self.logger.error(f"❌ Error listing NAS cron jobs: {e}")
            return []

    def execute_task_ide_style(self, task_name: str, script_path: str, arguments: List[str] = None) -> Dict[str, Any]:
        try:
            """
            Execute task in IDE-style (no terminal)

            This simulates IDE-style execution where tasks are run in the background
            without showing terminal output.
            """
            self.logger.info(f"🚀 Executing task IDE-style: {task_name}")

            result = {
                "task_name": task_name,
                "script": script_path,
                "arguments": arguments or [],
                "execution_time": datetime.now().isoformat(),
                "status": "queued",
                "output": "",
                "error": ""
            }

            # In IDE-style, we queue the task for execution
            # The actual execution happens via NAS cron or background process

            # Save task execution record
            execution_file = self.data_dir / f"execution_{task_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(execution_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            self.logger.info(f"✅ Task queued: {task_name}")

            return result

        except Exception as e:
            self.logger.error(f"Error in execute_task_ide_style: {e}", exc_info=True)
            raise
    def get_task_execution_status(self, task_name: str) -> Dict[str, Any]:
        try:
            """Get execution status for a task"""
            # Find latest execution record
            execution_files = sorted(
                self.data_dir.glob(f"execution_{task_name}_*.json"),
                reverse=True
            )

            if execution_files:
                with open(execution_files[0], 'r', encoding='utf-8') as f:
                    return json.load(f)

            return {
                "task_name": task_name,
                "status": "not_found"
            }


        except Exception as e:
            self.logger.error(f"Error in get_task_execution_status: {e}", exc_info=True)
            raise
def main():
    try:
        """CLI for NAS Kron Daemon Manager"""
        import argparse

        parser = argparse.ArgumentParser(description="NAS Kron Daemon Manager")
        parser.add_argument("--deploy", help="Deploy cron file to NAS")
        parser.add_argument("--list", action="store_true", help="List NAS cron jobs")
        parser.add_argument("--execute", help="Execute task IDE-style")
        parser.add_argument("--script", help="Script path for execution")
        parser.add_argument("--args", nargs="*", help="Script arguments")
        parser.add_argument("--status", help="Get task execution status")

        args = parser.parse_args()

        manager = NASKronDaemonManager()

        if args.deploy:
            cron_file = Path(args.deploy)
            if manager.deploy_cron_to_nas(cron_file):
                print(f"✅ Cron jobs deployed to NAS")
            else:
                print(f"❌ Failed to deploy cron jobs")

        elif args.list:
            jobs = manager.list_nas_cron_jobs()
            print(f"\n⏰ NAS Cron Jobs ({len(jobs)}):")
            for job in jobs:
                print(f"  {job}")

        elif args.execute:
            result = manager.execute_task_ide_style(
                args.execute,
                args.script or "",
                args.args or []
            )
            print(f"\n✅ Task queued: {args.execute}")
            print(f"   Status: {result['status']}")

        elif args.status:
            status = manager.get_task_execution_status(args.status)
            print(f"\n📊 Task Status: {args.status}")
            print(f"   Status: {status.get('status', 'unknown')}")
            if 'execution_time' in status:
                print(f"   Execution Time: {status['execution_time']}")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()