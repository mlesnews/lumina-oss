#!/usr/bin/env python3
"""
Install Surveillance Station via SSH using synopkg command
JARVIS automated installation via SSH
#JARVIS #MANUS #NAS #SYNOLOGY #SSH #SURVEILLANCE_STATION
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
import logging

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

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
    logger = get_logger("InstallSurveillanceStationSSH")
    logger.error("❌ paramiko not available. Install with: pip install paramiko")

try:
    from nas_azure_vault_integration import NASAzureVaultIntegration
    VAULT_AVAILABLE = True
except ImportError:
    VAULT_AVAILABLE = False

logger = get_logger("InstallSurveillanceStationSSH")


class SurveillanceStationSSHInstaller:
    """Install Surveillance Station via SSH using synopkg"""

    def __init__(self, nas_ip: str = "<NAS_PRIMARY_IP>", nas_port: int = 22):
        """Initialize SSH installer"""
        if not PARAMIKO_AVAILABLE:
            raise ImportError("paramiko not available")

        self.nas_ip = nas_ip
        self.nas_port = nas_port
        self.ssh_client: Optional[paramiko.SSHClient] = None
        self.credentials: Dict[str, str] = {}

        logger.info(f"🔧 Surveillance Station SSH Installer initialized for {nas_ip}:{nas_port}")

    def _get_credentials(self) -> bool:
        """Get NAS credentials from vault"""
        if not VAULT_AVAILABLE:
            logger.error("❌ Vault integration not available")
            return False

        try:
            vault = NASAzureVaultIntegration()
            self.credentials = vault.get_nas_credentials()
            return True
        except Exception as e:
            logger.error(f"❌ Failed to get credentials: {e}")
            return False

    def _connect_ssh(self) -> bool:
        """Connect to NAS via SSH"""
        if not self.credentials:
            if not self._get_credentials():
                return False

        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            username = self.credentials.get("username")
            password = self.credentials.get("password")

            if not username or not password:
                logger.error("❌ Missing SSH credentials")
                return False

            logger.info(f"🔌 Connecting to {self.nas_ip}:{self.nas_port} via SSH...")
            self.ssh_client.connect(
                hostname=self.nas_ip,
                port=self.nas_port,
                username=username,
                password=password,
                timeout=10
            )

            logger.info("✅ SSH connection established")
            return True

        except paramiko.AuthenticationException:
            logger.error("❌ SSH authentication failed")
            return False
        except paramiko.SSHException as e:
            logger.error(f"❌ SSH connection error: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error connecting via SSH: {e}")
            return False

    def _execute_command(self, command: str) -> tuple[bool, str, str]:
        """Execute command via SSH and return (success, stdout, stderr)"""
        if not self.ssh_client:
            if not self._connect_ssh():
                return False, "", "SSH not connected"

        try:
            logger.debug(f"Executing: {command}")
            stdin, stdout, stderr = self.ssh_client.exec_command(command, timeout=30)

            exit_status = stdout.channel.recv_exit_status()
            stdout_text = stdout.read().decode('utf-8').strip()
            stderr_text = stderr.read().decode('utf-8').strip()

            success = exit_status == 0
            return success, stdout_text, stderr_text

        except Exception as e:
            logger.error(f"❌ Error executing command: {e}")
            return False, "", str(e)

    def check_installed(self) -> Dict[str, Any]:
        """Check if Surveillance Station is installed"""
        # Try multiple paths for synopkg
        synopkg_paths = [
            "/usr/syno/bin/synopkg",
            "/usr/bin/synopkg",
            "synopkg"
        ]

        for synopkg_cmd in synopkg_paths:
            success, stdout, stderr = self._execute_command(f"{synopkg_cmd} status SurveillanceStation")

            if success or "installed" in stdout.lower() or "running" in stdout.lower() or "not installed" in stdout.lower():
                # Parse output
                if "installed" in stdout.lower() or "running" in stdout.lower():
                    return {"success": True, "installed": True, "status": stdout, "command": synopkg_cmd}
                else:
                    return {"success": True, "installed": False, "status": stdout, "command": synopkg_cmd}

        # If all failed, try checking via Package Center API status
        success, stdout, stderr = self._execute_command("ls /var/packages/SurveillanceStation 2>/dev/null && echo 'exists' || echo 'not_found'")
        if "exists" in stdout:
            # Check if it's actually running/started
            success2, stdout2, stderr2 = self._execute_command("/usr/syno/bin/synoservice --status pkgctl-SurveillanceStation 2>/dev/null || echo 'not_running'")
            if "running" in stdout2.lower() or "started" in stdout2.lower():
                return {"success": True, "installed": True, "status": "Installed and running", "details": stdout2}
            else:
                return {"success": True, "installed": True, "status": "Installed but may need to be started", "details": stdout2}

        return {"success": False, "installed": False, "error": "Could not determine installation status"}

    def install_package(self, volume: str = "volume1") -> Dict[str, Any]:
        """Install Surveillance Station using synopkg install_from_server"""
        logger.info(f"📦 Installing SurveillanceStation to {volume}...")

        # Try multiple paths for synopkg
        synopkg_paths = [
            "/usr/syno/bin/synopkg",
            "/usr/bin/synopkg",
            "synopkg"
        ]

        for synopkg_cmd in synopkg_paths:
            # Command: synopkg install_from_server <package> [volume] [user] [beta]
            command = f"{synopkg_cmd} install_from_server SurveillanceStation {volume}"
            logger.info(f"   Trying: {command}")

            success, stdout, stderr = self._execute_command(command)

            if success or "installing" in stdout.lower() or "download" in stdout.lower():
                logger.info(f"✅ Command succeeded with: {synopkg_cmd}")
                break
        else:
            # All paths failed
            logger.error(f"❌ All synopkg paths failed. Last error: {stderr}")
            return {
                "success": False,
                "error": stderr or "synopkg command not found",
                "stdout": stdout
            }

        if not success:
            logger.error(f"❌ Installation command failed: {stderr}")
            return {
                "success": False,
                "error": stderr or "Installation command failed",
                "stdout": stdout
            }

        logger.info("✅ Installation command executed successfully")
        logger.info(f"Output: {stdout}")

        # Wait for installation to complete
        logger.info("⏳ Waiting for installation to complete...")
        max_attempts = 60  # 5 minutes
        for attempt in range(max_attempts):
            time.sleep(5)
            status = self.check_installed()
            if status.get("installed"):
                logger.info("✅ Installation complete!")
                return {
                    "success": True,
                    "installed": True,
                    "message": "Surveillance Station installed successfully",
                    "output": stdout
                }
            if attempt % 12 == 0:  # Log every minute
                logger.info(f"   Still installing... ({attempt // 12 + 1}/5 minutes)")

        # Final check
        final_status = self.check_installed()
        if final_status.get("installed"):
            return {
                "success": True,
                "installed": True,
                "message": "Surveillance Station installed successfully",
                "output": stdout
            }
        else:
            return {
                "success": False,
                "error": "Installation timeout - package may still be installing",
                "status": final_status
            }

    def install_and_configure(self) -> Dict[str, Any]:
        """Main installation flow"""
        logger.info("🚀 Starting Surveillance Station installation via SSH...")

        # Step 1: Check if already installed
        logger.info("📋 Step 1: Checking if Surveillance Station is already installed...")
        status = self.check_installed()

        if status.get("installed"):
            logger.info("✅ Surveillance Station is already installed!")
            return {
                "success": True,
                "installed": True,
                "message": "Surveillance Station is already installed",
                "status": status.get("status")
            }

        # Step 2: Install package
        logger.info("📋 Step 2: Installing Surveillance Station...")
        result = self.install_package()

        if result.get("success"):
            logger.info("🎉 Surveillance Station installation complete!")
            return {
                **result,
                "access_url": f"https://{self.nas_ip}:9901"
            }
        else:
            return result

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup"""
        if self.ssh_client:
            self.ssh_client.close()
            logger.info("🔌 SSH connection closed")


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Install Surveillance Station on Synology NAS via SSH",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--nas-ip", default="<NAS_PRIMARY_IP>", help="NAS IP address")
    parser.add_argument("--nas-port", type=int, default=22, help="SSH port")
    parser.add_argument("--volume", default="volume1", help="Target volume")
    parser.add_argument("--check-only", action="store_true", help="Only check if installed")

    args = parser.parse_args()

    try:
        with SurveillanceStationSSHInstaller(nas_ip=args.nas_ip, nas_port=args.nas_port) as installer:
            if args.check_only:
                status = installer.check_installed()
                import json
                print(json.dumps(status, indent=2))
                return 0 if status.get("success") else 1
            else:
                result = installer.install_and_configure()
                import json
                print(json.dumps(result, indent=2))
                return 0 if result.get("success") else 1

    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":


    sys.exit(main())