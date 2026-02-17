#!/usr/bin/env python3
"""
JARVIS Docker Cleanup
Cleans up Docker configurations on both ULTRON (local) and KAIJU (NAS)
Removes unused containers, images, volumes, and networks
"""

import sys
import subprocess
import paramiko
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISDockerCleanup")


class DockerCleanup:
    """Cleanup Docker on ULTRON and KAIJU"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # KAIJU_NO_8 connection info (Desktop PC, NOT the NAS)
        # KAIJU_NO_8 = Desktop PC at <NAS_IP> (RTX 3090, 64GB RAM)
        # NAS = Synology DS1821plus at <NAS_PRIMARY_IP> (storage server)
        self.kaiju_ip = "<NAS_IP>"  # KAIJU_NO_8 Desktop PC
        self.kaiju_ssh_port = 22
        # Note: Docker on Windows desktop, not Synology Docker path
        self.docker_bin = "docker"  # Windows Docker Desktop

        # SSH credentials
        self.ssh_username = None
        self.ssh_password = None
        self._load_credentials()

        self.logger.info("✅ Docker Cleanup initialized")

    def _load_credentials(self):
        """Load SSH credentials from Azure Key Vault"""
        try:
            from nas_azure_vault_integration import NASAzureVaultIntegration
            nas_integration = NASAzureVaultIntegration(nas_ip=self.kaiju_ip)
            credentials = nas_integration.get_nas_credentials()

            if credentials:
                self.ssh_username = credentials.get("username")
                self.ssh_password = credentials.get("password")
        except Exception as e:
            self.logger.warning(f"⚠️  Failed to load SSH credentials: {e}")

    def ssh_execute(self, command: str, use_sudo: bool = False) -> Dict[str, Any]:
        """Execute command on KAIJU via SSH"""
        if not self.ssh_username or not self.ssh_password:
            return {"success": False, "error": "SSH credentials not available"}

        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=self.kaiju_ip,
                port=self.kaiju_ssh_port,
                username=self.ssh_username,
                password=self.ssh_password,
                timeout=10
            )

            if use_sudo:
                full_cmd = f'echo "{self.ssh_password}" | sudo -S {command}'
            else:
                full_cmd = command

            stdin, stdout, stderr = client.exec_command(full_cmd)
            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode()
            error = stderr.read().decode()

            client.close()

            return {
                "success": exit_status == 0,
                "exit_status": exit_status,
                "output": output,
                "error": error
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def cleanup_local_docker(self) -> Dict[str, Any]:
        """Cleanup Docker on ULTRON (local machine)"""
        self.logger.info("🧹 Cleaning up Docker on ULTRON (local)...")

        results = {
            "containers_removed": 0,
            "images_removed": 0,
            "volumes_removed": 0,
            "networks_removed": 0,
            "space_freed": "0B"
        }

        try:
            # Remove stopped containers
            self.logger.info("   Removing stopped containers...")
            result = subprocess.run(
                ['docker', 'container', 'prune', '-f'],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                # Parse output for count
                output = result.stdout
                if "Total reclaimed space" in output:
                    results["space_freed"] = output.split("Total reclaimed space:")[-1].strip().split()[0]

            # Remove unused images
            self.logger.info("   Removing unused images...")
            result = subprocess.run(
                ['docker', 'image', 'prune', '-a', '-f'],
                capture_output=True,
                text=True,
                timeout=120
            )

            # Remove unused volumes
            self.logger.info("   Removing unused volumes...")
            result = subprocess.run(
                ['docker', 'volume', 'prune', '-f'],
                capture_output=True,
                text=True,
                timeout=60
            )

            # Remove unused networks
            self.logger.info("   Removing unused networks...")
            result = subprocess.run(
                ['docker', 'network', 'prune', '-f'],
                capture_output=True,
                text=True,
                timeout=30
            )

            # System prune (everything)
            self.logger.info("   Running full system prune...")
            result = subprocess.run(
                ['docker', 'system', 'prune', '-a', '--volumes', '-f'],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                output = result.stdout
                if "Total reclaimed space" in output:
                    results["space_freed"] = output.split("Total reclaimed space:")[-1].strip().split()[0]
                self.logger.info(f"   ✅ ULTRON cleanup complete - Space freed: {results['space_freed']}")

            results["success"] = True
            return results

        except FileNotFoundError:
            return {"success": False, "error": "Docker not found on ULTRON"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def cleanup_kaiju_docker(self) -> Dict[str, Any]:
        """Cleanup Docker on KAIJU (NAS)"""
        self.logger.info("🧹 Cleaning up Docker on KAIJU (NAS)...")

        if not self.ssh_username or not self.ssh_password:
            return {"success": False, "error": "SSH credentials not available"}

        results = {
            "containers_removed": 0,
            "images_removed": 0,
            "volumes_removed": 0,
            "networks_removed": 0,
            "space_freed": "0B"
        }

        # Test Docker access
        docker_cmd = self.docker_bin
        test_result = self.ssh_execute(f"{docker_cmd} ps 2>&1 | head -1")

        if "permission denied" in test_result.get("output", "").lower():
            docker_cmd = f"sudo {self.docker_bin}"
            use_sudo = True
        else:
            use_sudo = False

        # Remove stopped containers
        self.logger.info("   Removing stopped containers...")
        result = self.ssh_execute(
            f"{docker_cmd} container prune -f 2>&1",
            use_sudo=use_sudo
        )

        # Remove unused images
        self.logger.info("   Removing unused images...")
        result = self.ssh_execute(
            f"{docker_cmd} image prune -a -f 2>&1",
            use_sudo=use_sudo
        )

        # Remove unused volumes
        self.logger.info("   Removing unused volumes...")
        result = self.ssh_execute(
            f"{docker_cmd} volume prune -f 2>&1",
            use_sudo=use_sudo
        )

        # Remove unused networks
        self.logger.info("   Removing unused networks...")
        result = self.ssh_execute(
            f"{docker_cmd} network prune -f 2>&1",
            use_sudo=use_sudo
        )

        # System prune
        self.logger.info("   Running full system prune...")
        result = self.ssh_execute(
            f"{docker_cmd} system prune -a --volumes -f 2>&1",
            use_sudo=use_sudo
        )

        if result.get("success"):
            output = result.get("output", "")
            if "Total reclaimed space" in output:
                results["space_freed"] = output.split("Total reclaimed space:")[-1].strip().split()[0]
            self.logger.info(f"   ✅ KAIJU cleanup complete - Space freed: {results['space_freed']}")

        results["success"] = result.get("success", False)
        return results

    def full_cleanup(self) -> Dict[str, Any]:
        """Cleanup Docker on both ULTRON and KAIJU"""
        self.logger.info("="*80)
        self.logger.info("🧹 DOCKER CLEANUP - ULTRON & KAIJU")
        self.logger.info("="*80)

        cleanup_results = {
            "timestamp": datetime.now().isoformat(),
            "ultron": None,
            "kaiju": None
        }

        # Cleanup ULTRON
        ultron_result = self.cleanup_local_docker()
        cleanup_results["ultron"] = ultron_result

        # Cleanup KAIJU
        kaiju_result = self.cleanup_kaiju_docker()
        cleanup_results["kaiju"] = kaiju_result

        # Summary
        self.logger.info("="*80)
        self.logger.info("CLEANUP SUMMARY")
        self.logger.info("="*80)

        if ultron_result.get("success"):
            self.logger.info(f"ULTRON: ✅ Cleaned - Space freed: {ultron_result.get('space_freed', 'Unknown')}")
        else:
            self.logger.warning(f"ULTRON: ❌ Failed - {ultron_result.get('error', 'Unknown error')}")

        if kaiju_result.get("success"):
            self.logger.info(f"KAIJU: ✅ Cleaned - Space freed: {kaiju_result.get('space_freed', 'Unknown')}")
        else:
            self.logger.warning(f"KAIJU: ❌ Failed - {kaiju_result.get('error', 'Unknown error')}")

        self.logger.info("="*80)

        return cleanup_results


def main():
    try:
        """CLI interface"""
        import argparse
        import json

        parser = argparse.ArgumentParser(description="Docker Cleanup - ULTRON & KAIJU")
        parser.add_argument("--cleanup", action="store_true", help="Cleanup both ULTRON and KAIJU")
        parser.add_argument("--ultron-only", action="store_true", help="Cleanup ULTRON only")
        parser.add_argument("--kaiju-only", action="store_true", help="Cleanup KAIJU only")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        cleanup = DockerCleanup(project_root)

        if args.cleanup:
            result = cleanup.full_cleanup()
            print(json.dumps(result, indent=2, default=str))
        elif args.ultron_only:
            result = cleanup.cleanup_local_docker()
            print(json.dumps(result, indent=2))
        elif args.kaiju_only:
            result = cleanup.cleanup_kaiju_docker()
            print(json.dumps(result, indent=2))
        else:
            print("Usage:")
            print("  --cleanup      : Cleanup both ULTRON and KAIJU")
            print("  --ultron-only  : Cleanup ULTRON only")
            print("  --kaiju-only   : Cleanup KAIJU only")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()