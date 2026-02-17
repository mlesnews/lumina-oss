#!/usr/bin/env python3
"""
Deploy NAS Migration Script to NAS
Deploys the migration script and optionally sets up cron job
#JARVIS #NAS #MIGRATION #DEPLOYMENT
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
import json
import logging

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from nas_kron_daemon_manager import NASKronDaemonManager
    NAS_MANAGER_AVAILABLE = True
except ImportError:
    NAS_MANAGER_AVAILABLE = False

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

logger = get_logger("DeployNASMigration")


class NASMigrationDeployer:
    """Deploy migration script to NAS and optionally set up cron job"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = get_logger("NASMigrationDeployer")

        # Load NAS config
        self.nas_config = self._load_nas_config()
        self.ssh_client = None

    def _load_nas_config(self) -> Dict[str, Any]:
        """Load NAS SSH configuration"""
        config_file = self.project_root / "config" / "lumina_nas_ssh_config.json"

        if not config_file.exists():
            self.logger.warning(f"NAS config not found: {config_file}")
            return {}

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            if "nas" in config:
                nas_config = config["nas"].copy()
                nas_config.update({k: v for k, v in config.items() if k not in ["nas", "ssh_config"]})
                return nas_config
            return config
        except Exception as e:
            self.logger.error(f"Error loading NAS config: {e}")
            return {}

    def _get_credentials(self) -> Optional[Dict[str, str]]:
        """Get SSH credentials"""
        nas_config = self.nas_config
        host = nas_config.get("host", nas_config.get("hostname", "<NAS_PRIMARY_IP>"))
        port = nas_config.get("port", 22)
        username = nas_config.get("username", "root")
        password = nas_config.get("password")
        password_source = nas_config.get("password_source")

        if password:
            return {
                "host": host,
                "port": port,
                "username": username,
                "password": password,
                "key_file": nas_config.get("key_file") or nas_config.get("ssh_key_path")
            }

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
                        "key_file": nas_config.get("key_file")
                    }
            except Exception as e:
                self.logger.error(f"Error retrieving credentials: {e}")

        return None

    def _connect_ssh(self) -> bool:
        """Connect to NAS via SSH"""
        if not PARAMIKO_AVAILABLE:
            self.logger.error("❌ paramiko not available")
            return False

        credentials = self._get_credentials()
        if not credentials:
            self.logger.error("❌ No credentials available")
            return False

        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            host = credentials["host"]
            port = credentials["port"]
            username = credentials["username"]
            password = credentials.get("password")
            key_file = credentials.get("key_file")

            if key_file:
                self.ssh_client.connect(host, port=port, username=username, key_filename=key_file)
            else:
                self.ssh_client.connect(host, port=port, username=username, password=password, 
                                      allow_agent=False, look_for_keys=False)

            self.logger.info(f"✅ Connected to NAS: {host}")
            return True
        except Exception as e:
            self.logger.error(f"❌ SSH connection failed: {e}")
            return False

    def _disconnect_ssh(self):
        """Disconnect SSH"""
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None

    def deploy_script(self, script_path: Path, remote_path: str = "/usr/local/bin/nas_migration.sh") -> bool:
        """Deploy migration script to NAS"""
        if not self.ssh_client and not self._connect_ssh():
            return False

        try:
            # Read script content
            with open(script_path, 'r', encoding='utf-8') as f:
                script_content = f.read()

            # Create remote directory if needed
            remote_dir = str(Path(remote_path).parent)
            stdin, stdout, stderr = self.ssh_client.exec_command(f"mkdir -p {remote_dir}")
            stdout.channel.recv_exit_status()

            # Write script to NAS (use base64 to avoid encoding issues)
            import base64
            script_b64 = base64.b64encode(script_content.encode('utf-8')).decode('utf-8')

            # Write script file
            stdin, stdout, stderr = self.ssh_client.exec_command(
                f"bash -c 'echo \"{script_b64}\" | base64 -d > {remote_path}'"
            )
            if stdout.channel.recv_exit_status() != 0:
                error = stderr.read().decode('utf-8')
                self.logger.error(f"❌ Failed to write script: {error}")
                return False

            # Make script executable
            stdin, stdout, stderr = self.ssh_client.exec_command(f"chmod +x {remote_path}")
            if stdout.channel.recv_exit_status() != 0:
                error = stderr.read().decode('utf-8')
                self.logger.error(f"❌ Failed to make script executable: {error}")
                return False

            self.logger.info(f"✅ Script deployed to: {remote_path}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Deployment error: {e}")
            return False

    def setup_cron_job(self, script_path: str = "/usr/local/bin/nas_migration.sh", 
                       schedule: str = "0 */6 * * *") -> bool:
        """Setup cron job to run migration periodically"""
        if not self.ssh_client and not self._connect_ssh():
            return False

        try:
            # Try to find crontab command
            stdin, stdout, stderr = self.ssh_client.exec_command("which crontab")
            crontab_path = stdout.read().decode('utf-8').strip()

            if not crontab_path:
                # Try common locations
                for path in ["/usr/bin/crontab", "/bin/crontab", "/usr/sbin/crontab"]:
                    stdin, stdout, stderr = self.ssh_client.exec_command(f"test -x {path} && echo {path}")
                    if stdout.read().decode('utf-8').strip():
                        crontab_path = path
                        break

            if not crontab_path:
                self.logger.warn("⚠️  crontab command not found")
                self.logger.info("💡 On Synology, you may need to:")
                self.logger.info("   1. Set up Task Scheduler via DSM web interface")
                self.logger.info("   2. Or use /usr/syno/bin/synoschedtask")
                self.logger.info(f"   3. Or manually add to /etc/crontab as root")
                self.logger.info(f"      {schedule} $(whoami) {script_path} >> /tmp/nas_migration_cron.log 2>&1")
                return False

            # Get current crontab
            stdin, stdout, stderr = self.ssh_client.exec_command(f"{crontab_path} -l 2>/dev/null || echo ''")
            existing_crontab = stdout.read().decode('utf-8')

            # Check if job already exists (check for script path or filename)
            script_name = Path(script_path).name
            if script_name in existing_crontab or script_path in existing_crontab:
                self.logger.warn("⚠️  Cron job already exists")
                return True

            # Add new cron job
            cron_entry = f"{schedule} {script_path} >> /tmp/nas_migration_cron.log 2>&1"
            new_crontab = existing_crontab.rstrip() + "\n" + cron_entry + "\n"

            # Install new crontab
            import base64
            crontab_b64 = base64.b64encode(new_crontab.encode('utf-8')).decode('utf-8')
            stdin, stdout, stderr = self.ssh_client.exec_command(
                f"bash -c 'echo \"{crontab_b64}\" | base64 -d | {crontab_path} -'"
            )

            if stdout.channel.recv_exit_status() == 0:
                self.logger.info(f"✅ Cron job installed: {schedule}")
                return True
            else:
                error = stderr.read().decode('utf-8')
                self.logger.warn(f"⚠️  Failed to install cron job: {error}")
                self.logger.info("💡 Alternative: Set up via Synology DSM Task Scheduler")
                self.logger.info(f"   Script path: {script_path}")
                self.logger.info(f"   Schedule: {schedule}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Cron setup error: {e}")
            return False

    def run_migration_now(self, script_path: str = "/usr/local/bin/nas_migration.sh") -> bool:
        """Run migration script immediately on NAS"""
        if not self.ssh_client and not self._connect_ssh():
            return False

        try:
            # Run script in background
            stdin, stdout, stderr = self.ssh_client.exec_command(
                f"nohup {script_path} > /tmp/nas_migration_run.log 2>&1 &"
            )

            if stdout.channel.recv_exit_status() == 0:
                self.logger.info("✅ Migration started on NAS (running in background)")
                self.logger.info("   Monitor with: tail -f /tmp/nas_migration_run.log")
                return True
            else:
                error = stderr.read().decode('utf-8')
                self.logger.error(f"❌ Failed to start migration: {error}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Error starting migration: {e}")
            return False


def main():
    try:
        """Main deployment function"""
        import argparse

        parser = argparse.ArgumentParser(description="Deploy NAS Migration Script")
        parser.add_argument("--script", default="scripts/nas/nas_migration_from_laptop.sh",
                           help="Path to migration script")
        parser.add_argument("--remote-path", default="/usr/local/bin/nas_migration.sh",
                           help="Remote path on NAS")
        parser.add_argument("--setup-cron", action="store_true",
                           help="Setup cron job to run migration periodically")
        parser.add_argument("--cron-schedule", default="0 */6 * * *",
                           help="Cron schedule (default: every 6 hours)")
        parser.add_argument("--run-now", action="store_true",
                           help="Run migration immediately after deployment")
        parser.add_argument("--no-deploy", action="store_true",
                           help="Skip deployment, only run existing script")

        args = parser.parse_args()

        print("=" * 70)
        print("   DEPLOY NAS MIGRATION SCRIPT")
        print("=" * 70)
        print("")

        deployer = NASMigrationDeployer()

        # Deploy script
        if not args.no_deploy:
            script_path = Path(args.script)
            if not script_path.exists():
                print(f"❌ Script not found: {script_path}")
                return 1

            print(f"📤 Deploying script: {script_path}")
            if not deployer.deploy_script(script_path, args.remote_path):
                print("❌ Deployment failed")
                deployer._disconnect_ssh()
                return 1
            print("✅ Script deployed successfully")
            print("")

        # Setup cron job
        if args.setup_cron:
            print(f"⏰ Setting up cron job: {args.cron_schedule}")
            if deployer.setup_cron_job(args.remote_path, args.cron_schedule):
                print("✅ Cron job installed")
            else:
                print("❌ Cron setup failed")
            print("")

        # Run now
        if args.run_now:
            print("🚀 Starting migration now...")
            if deployer.run_migration_now(args.remote_path):
                print("✅ Migration started")
                print("")
                print("Monitor migration:")
                print("  ssh to NAS and run: tail -f /tmp/nas_migration_run.log")
                print("  Or check log file on NAS")
            else:
                print("❌ Failed to start migration")
            print("")

        deployer._disconnect_ssh()

        print("=" * 70)
        print("   DEPLOYMENT COMPLETE")
        print("=" * 70)
        print("")
        print("Next Steps:")
        print("  1. SSH to NAS and verify script: ls -l /usr/local/bin/nas_migration.sh")
        print("  2. Test script: /usr/local/bin/nas_migration.sh")
        print("  3. Check cron: crontab -l (if --setup-cron was used)")
        print("  4. Monitor logs: tail -f /volume1/backups/MATT_Backups/logs/migration_*.log")
        print("")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())