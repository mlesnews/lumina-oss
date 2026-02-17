#!/usr/bin/env python3
"""
JARVIS KAIJU Cluster Deployment

Deploys and configures Ollama and ULTRON Router services on KAIJU NAS.
Uses Docker via Synology Container Manager.

Tags: #TROUBLESHOOTING #CLUSTER @KAIJU
"""

import sys
import json
import paramiko
import requests
import socket
from pathlib import Path
from typing import Dict, Any, Optional
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

logger = get_logger("JARVISKAIJUDeploy")


class KAIJUClusterDeployment:
    """
    KAIJU Cluster Deployment

    Deploys Ollama and ULTRON Router services on KAIJU.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # KAIJU connection info
        self.kaiju_ip = "<NAS_PRIMARY_IP>"
        self.kaiju_ssh_port = 22
        self.kaiju_ollama_port = 11434
        self.kaiju_ultron_router_port = 3008

        # SSH credentials
        self.ssh_username = None
        self.ssh_password = None
        self._load_credentials()

        self.logger.info("✅ KAIJU Cluster Deployment initialized")

    def _load_credentials(self):
        """Load SSH credentials from Azure Key Vault"""
        try:
            from nas_azure_vault_integration import NASAzureVaultIntegration
            nas_integration = NASAzureVaultIntegration(nas_ip=self.kaiju_ip)
            credentials = nas_integration.get_nas_credentials()

            if credentials:
                self.ssh_username = credentials.get("username")
                self.ssh_password = credentials.get("password")

                if self.ssh_username and self.ssh_password:
                    self.logger.info(f"✅ Loaded SSH credentials for {self.ssh_username}")
        except Exception as e:
            self.logger.warning(f"⚠️  Failed to load SSH credentials: {e}")

    def ssh_execute_command(self, command: str) -> Dict[str, Any]:
        """Execute command on KAIJU via SSH"""
        if not self.ssh_username or not self.ssh_password:
            return {
                "success": False,
                "error": "SSH credentials not available"
            }

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

            stdin, stdout, stderr = client.exec_command(command)
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
            return {
                "success": False,
                "error": str(e)
            }

    def deploy_ollama_container(self) -> Dict[str, Any]:
        """Deploy Ollama container on KAIJU"""
        self.logger.info("🚀 Deploying Ollama container on KAIJU...")

        # Find Docker binary (Synology uses /usr/local/bin/docker)
        docker_bin_result = self.ssh_execute_command(
            "ls -la /usr/local/bin/docker 2>/dev/null | awk '{print $NF}' || echo '/var/packages/ContainerManager/target/usr/bin/docker'"
        )
        docker_bin = docker_bin_result.get("output", "").strip()
        if not docker_bin or docker_bin == "/usr/local/bin/docker":
            # Use the symlink target or default path
            docker_bin = "/var/packages/ContainerManager/target/usr/bin/docker"

        # Check if we need sudo (user mentioned sudoless root access)
        # Try with sudo first, fallback to direct if it works
        docker_cmd_prefix = ""
        test_result = self.ssh_execute_command(f"{docker_bin} ps 2>&1 | head -1")
        if "permission denied" in test_result.get("output", "").lower() or "permission denied" in test_result.get("error", "").lower():
            # Try with sudo
            sudo_test = self.ssh_execute_command(f"sudo -n {docker_bin} ps 2>&1 | head -1")
            if sudo_test.get("success"):
                docker_cmd_prefix = "sudo "
                self.logger.info("   Using sudo for Docker commands")
            else:
                self.logger.warning("   ⚠️  Docker permission denied and sudo requires password")

        docker_bin = f"{docker_cmd_prefix}{docker_bin}"
        self.logger.info(f"   Using Docker command: {docker_bin}")

        # Check if container already exists
        check_result = self.ssh_execute_command(
            f"{docker_bin} ps -a --filter 'name=ollama' --format '{{{{.Names}}}}' 2>/dev/null || echo ''"
        )

        if check_result.get("success") and check_result.get("output", "").strip():
            container_name = check_result.get("output", "").strip()
            self.logger.info(f"   Found existing container: {container_name}")

            # Check if running
            status_result = self.ssh_execute_command(
                f"{docker_bin} ps --filter 'name=ollama' --format '{{{{.Status}}}}' 2>/dev/null || echo 'not running'"
            )

            if "Up" in status_result.get("output", ""):
                self.logger.info("   ✅ Ollama container is already running")
                return {
                    "success": True,
                    "action": "already_running",
                    "container": container_name
                }
            else:
                # Start existing container
                self.logger.info("   🔄 Starting existing Ollama container...")
                start_result = self.ssh_execute_command(
                    f"{docker_bin} start {container_name} 2>&1"
                )

                if start_result.get("success"):
                    self.logger.info("   ✅ Ollama container started")
                    return {
                        "success": True,
                        "action": "started",
                        "container": container_name
                    }

        # Deploy new container
        self.logger.info("   📦 Creating new Ollama container...")

        # Create volume for Ollama data
        volume_result = self.ssh_execute_command(
            f"{docker_bin} volume create ollama-data 2>&1 || echo 'Volume may already exist'"
        )

        # Deploy Ollama container
        deploy_command = f"""{docker_bin} run -d \\
            --name ollama \\
            --restart unless-stopped \\
            -v ollama-data:/root/.ollama \\
            -p {self.kaiju_ollama_port}:11434 \\
            ollama/ollama:latest 2>&1"""

        deploy_result = self.ssh_execute_command(deploy_command)

        if deploy_result.get("success"):
            container_id = deploy_result.get("output", "").strip().split()[-1] if deploy_result.get("output") else "unknown"
            self.logger.info(f"   ✅ Ollama container deployed: {container_id}")

            # Wait a bit for container to start
            import time
            time.sleep(3)

            # Verify it's running
            verify_result = self.ssh_execute_command(
                f"{docker_bin} ps --filter 'name=ollama' --format '{{{{.Status}}}}' 2>/dev/null || echo 'not running'"
            )

            if "Up" in verify_result.get("output", ""):
                self.logger.info("   ✅ Ollama container is running")
                return {
                    "success": True,
                    "action": "deployed",
                    "container": "ollama"
                }
            else:
                return {
                    "success": False,
                    "error": "Container deployed but not running",
                    "output": verify_result.get("output")
                }
        else:
            self.logger.error(f"   ❌ Failed to deploy Ollama: {deploy_result.get('error')}")
            return {
                "success": False,
                "error": deploy_result.get("error", "Unknown error"),
                "output": deploy_result.get("output", "")
            }

    def deploy_ultron_router(self) -> Dict[str, Any]:
        """Deploy ULTRON Router service on KAIJU"""
        self.logger.info("🚀 Deploying ULTRON Router on KAIJU...")

        # For now, ULTRON Router deployment would require the router code
        # This is a placeholder for future implementation
        self.logger.warning("   ⚠️  ULTRON Router deployment not yet implemented")
        self.logger.info("   📝 ULTRON Router requires custom service deployment")

        return {
            "success": False,
            "error": "ULTRON Router deployment not yet implemented",
            "note": "Requires custom router service code deployment"
        }

    def verify_services(self) -> Dict[str, Any]:
        """Verify deployed services are accessible"""
        self.logger.info("🔍 Verifying deployed services...")

        results = {
            "ollama": None,
            "ultron_router": None
        }

        # Check Ollama
        try:
            response = requests.get(
                f"http://{self.kaiju_ip}:{self.kaiju_ollama_port}/api/tags",
                timeout=5
            )

            if response.status_code == 200:
                models = response.json().get("models", [])
                self.logger.info(f"   ✅ Ollama is accessible ({len(models)} models)")
                results["ollama"] = {
                    "success": True,
                    "models": len(models)
                }
            else:
                self.logger.warning(f"   ⚠️  Ollama returned status {response.status_code}")
                results["ollama"] = {
                    "success": False,
                    "error": f"Status {response.status_code}"
                }
        except Exception as e:
            self.logger.warning(f"   ⚠️  Ollama not accessible: {e}")
            results["ollama"] = {
                "success": False,
                "error": str(e)
            }

        # Check ULTRON Router
        try:
            response = requests.get(
                f"http://{self.kaiju_ip}:{self.kaiju_ultron_router_port}/health",
                timeout=5
            )

            if response.status_code == 200:
                self.logger.info("   ✅ ULTRON Router is accessible")
                results["ultron_router"] = {
                    "success": True
                }
            else:
                results["ultron_router"] = {
                    "success": False,
                    "error": f"Status {response.status_code}"
                }
        except Exception as e:
            results["ultron_router"] = {
                "success": False,
                "error": str(e)
            }

        return results

    def full_deployment(self) -> Dict[str, Any]:
        """Perform full cluster deployment"""
        self.logger.info("🚀 Starting full KAIJU cluster deployment...")

        deployment = {
            "timestamp": datetime.now().isoformat(),
            "kaiju_ip": self.kaiju_ip,
            "ollama": None,
            "ultron_router": None,
            "verification": None
        }

        # Deploy Ollama
        ollama_result = self.deploy_ollama_container()
        deployment["ollama"] = ollama_result

        # Deploy ULTRON Router (placeholder)
        router_result = self.deploy_ultron_router()
        deployment["ultron_router"] = router_result

        # Verify services
        verification = self.verify_services()
        deployment["verification"] = verification

        # Summary
        ollama_ok = deployment["ollama"].get("success", False)
        router_ok = deployment["ultron_router"].get("success", False)
        ollama_verified = verification.get("ollama", {}).get("success", False)

        deployment["summary"] = {
            "ollama_deployed": ollama_ok,
            "ollama_verified": ollama_verified,
            "router_deployed": router_ok,
            "all_healthy": ollama_ok and ollama_verified
        }

        return deployment


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="KAIJU Cluster Deployment")
        parser.add_argument("--deploy", action="store_true", help="Deploy all services")
        parser.add_argument("--deploy-ollama", action="store_true", help="Deploy Ollama only")
        parser.add_argument("--verify", action="store_true", help="Verify services")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        deployment = KAIJUClusterDeployment(project_root)

        if args.deploy:
            result = deployment.full_deployment()
            print(json.dumps(result, indent=2, default=str))

        elif args.deploy_ollama:
            result = deployment.deploy_ollama_container()
            print(json.dumps(result, indent=2))

        elif args.verify:
            result = deployment.verify_services()
            print(json.dumps(result, indent=2))

        else:
            print("Usage:")
            print("  --deploy         : Deploy all services")
            print("  --deploy-ollama  : Deploy Ollama only")
            print("  --verify         : Verify services")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()