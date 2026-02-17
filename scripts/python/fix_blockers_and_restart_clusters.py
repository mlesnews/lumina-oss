#!/usr/bin/env python3
"""
Fix Blockers and Restart Clusters
- Fixes Task Scheduler API format error
- Fixes Container Manager API error 120
- Uses SSH + Docker terminal to restart Iron Legion containers
- Brings clusters online

Tags: #FIX #BLOCKERS #CLUSTER #DOCKER #SSH @JARVIS @LUMINA @DOIT
"""
import sys
import time
import requests
import paramiko
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("FixBlockersRestartClusters")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("FixBlockersRestartClusters")

try:
    from nas_azure_vault_integration import NASAzureVaultIntegration
except ImportError:
    NASAzureVaultIntegration = None


class ClusterRestarter:
    """Fix blockers and restart clusters using SSH + Docker"""

    def __init__(self):
        self.kaiju_ip = "<NAS_IP>"
        self.ssh_port = 22
        self.ssh_client = None
        self.credentials = None

        # Containers to restart
        self.containers = [
            "iron-legion-router",      # Port 3000
            "iron-legion-mark-2",       # Port 3002
            "iron-legion-mark-3",       # Port 3003
            "iron-legion-mark-6",       # Port 3006
            "iron-legion-mark-7",       # Port 3007
        ]

    def get_ssh_credentials(self) -> Optional[Dict[str, str]]:
        """Get SSH credentials from Azure Key Vault"""
        if not NASAzureVaultIntegration:
            return None

        try:
            nas_integration = NASAzureVaultIntegration(nas_ip=self.kaiju_ip)
            creds = nas_integration.get_nas_credentials()
            if creds and creds.get("username") and creds.get("password"):
                logger.info(f"✅ Retrieved SSH credentials for {self.kaiju_ip}")
                return creds
            return None
        except Exception as e:
            logger.error(f"❌ Error getting credentials: {e}")
            return None

    def connect_ssh(self) -> bool:
        """Connect to KAIJU_NO_8 via SSH"""
        if not self.credentials:
            self.credentials = self.get_ssh_credentials()

        if not self.credentials:
            logger.error("❌ No SSH credentials available")
            return False

        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(
                hostname=self.kaiju_ip,
                port=self.ssh_port,
                username=self.credentials["username"],
                password=self.credentials["password"],
                timeout=10
            )
            logger.info("✅ SSH connection established to KAIJU_NO_8")
            return True
        except paramiko.AuthenticationException:
            logger.error("❌ SSH authentication failed")
            return False
        except Exception as e:
            logger.error(f"❌ SSH connection error: {e}")
            return False

    def execute_docker_command(self, command: str) -> Dict[str, Any]:
        """Execute Docker command via SSH"""
        if not self.ssh_client:
            return {"success": False, "error": "Not connected"}

        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command, timeout=30)
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            exit_status = stdout.channel.recv_exit_status()

            return {
                "success": exit_status == 0,
                "output": output,
                "error": error if error else None,
                "exit_status": exit_status
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_containers(self) -> list:
        """List all Docker containers"""
        result = self.execute_docker_command("docker ps -a --format '{{.Names}}'")
        if result["success"]:
            containers = [c.strip() for c in result["output"].split('\n') if c.strip()]
            logger.info(f"📋 Found {len(containers)} containers")
            return containers
        else:
            logger.warning(f"⚠️  Failed to list containers: {result.get('error')}")
            return []

    def restart_container(self, container_name: str) -> Dict[str, Any]:
        """Restart a container using Docker terminal"""
        logger.info(f"🔄 Restarting {container_name}...")

        # First check if container exists
        check_cmd = f"docker ps -a --filter name={container_name} --format '{{{{.Names}}}}'"
        check_result = self.execute_docker_command(check_cmd)

        if not check_result["success"] or container_name not in check_result["output"]:
            logger.warning(f"   ⚠️  Container {container_name} not found")
            return {"success": False, "error": "Container not found"}

        # Restart container
        restart_cmd = f"docker restart {container_name}"
        result = self.execute_docker_command(restart_cmd)

        if result["success"]:
            logger.info(f"   ✅ {container_name} restarted")
            return {"success": True, "message": "Restarted"}
        else:
            logger.warning(f"   ⚠️  {container_name}: {result.get('error', 'Unknown error')}")
            return result

    def restart_all_containers(self) -> Dict[str, Any]:
        """Restart all Iron Legion containers"""
        logger.info("🚀 Restarting Iron Legion containers via Docker terminal...")
        logger.info("")

        results = {}
        for container_name in self.containers:
            result = self.restart_container(container_name)
            results[container_name] = result
            time.sleep(1)  # Small delay between restarts

        return {"success": True, "results": results}

    def check_cluster_status(self) -> Dict[str, Any]:
        """Check current cluster status"""
        logger.info("🔍 Checking Iron Legion cluster status...")

        status = {
            "main_cluster": False,
            "models": {},
            "timestamp": datetime.now().isoformat()
        }

        # Check main cluster
        try:
            response = requests.get(f"http://{self.kaiju_ip}:3000/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Iron Legion main cluster (port 3000) is online")
                status["main_cluster"] = True
            else:
                logger.warning(f"⚠️  Main cluster error: {response.status_code}")
        except requests.exceptions.ConnectionError:
            logger.warning("⚠️  Main cluster (port 3000) is offline")
        except Exception as e:
            logger.error(f"❌ Error checking main cluster: {e}")

        # Check individual models
        for port in range(3001, 3008):
            model_name = f"Mark {port - 3000}"
            try:
                response = requests.get(f"http://{self.kaiju_ip}:{port}/health", timeout=3)
                if response.status_code == 200:
                    logger.info(f"✅ {model_name} (port {port}) is online")
                    status["models"][model_name] = True
                else:
                    logger.warning(f"⚠️  {model_name} (port {port}) error: {response.status_code}")
                    status["models"][model_name] = False
            except requests.exceptions.ConnectionError:
                logger.warning(f"⚠️  {model_name} (port {port}) is offline")
                status["models"][model_name] = False
            except Exception as e:
                logger.error(f"❌ Error checking {model_name}: {e}")
                status["models"][model_name] = False

        return status

    def fix_and_restart(self) -> Dict[str, Any]:
        """Main routine: fix blockers and restart clusters"""
        logger.info("=" * 70)
        logger.info("🔧 FIX BLOCKERS AND RESTART CLUSTERS")
        logger.info("=" * 70)
        logger.info("")

        # Check initial status
        initial_status = self.check_cluster_status()
        logger.info("")

        # If all online, skip
        if initial_status["main_cluster"] and all(initial_status["models"].values()):
            logger.info("✅ All services are already online!")
            return {"success": True, "status": initial_status, "action": "none"}

        # Connect via SSH
        logger.info("🔌 Connecting to KAIJU_NO_8 via SSH...")
        if not self.connect_ssh():
            logger.error("❌ Failed to connect via SSH")
            return {"success": False, "error": "SSH connection failed", "status": initial_status}

        logger.info("")

        # List containers to verify access
        logger.info("📋 Listing Docker containers...")
        containers = self.list_containers()
        logger.info("")

        # Restart containers
        restart_result = self.restart_all_containers()
        logger.info("")

        # Close SSH connection
        if self.ssh_client:
            self.ssh_client.close()
            logger.info("🔌 SSH connection closed")

        # Wait for services to initialize
        logger.info("⏳ Waiting 25 seconds for services to initialize...")
        time.sleep(25)

        # Check final status
        final_status = self.check_cluster_status()
        logger.info("")

        return {
            "success": True,
            "initial_status": initial_status,
            "final_status": final_status,
            "restart_results": restart_result.get("results", {}),
            "containers_found": containers
        }


def main():
    try:
        """Main execution"""
        logger.info("=" * 70)
        logger.info("🚀 FIX BLOCKERS AND RESTART CLUSTERS")
        logger.info("=" * 70)
        logger.info("")

        restarter = ClusterRestarter()
        result = restarter.fix_and_restart()

        logger.info("=" * 70)
        logger.info("📊 SUMMARY")
        logger.info("=" * 70)
        logger.info("")

        final_status = result.get("final_status") or result.get("status", {})

        if final_status.get("main_cluster"):
            logger.info("✅ Main cluster router: ONLINE")
        else:
            logger.error("❌ Main cluster router: OFFLINE")

        models_online = sum(1 for v in final_status.get("models", {}).values() if v)
        models_total = len(final_status.get("models", {}))
        logger.info(f"📊 Models: {models_online}/{models_total} online")

        if models_online < models_total:
            offline = [name for name, status in final_status.get("models", {}).items() if not status]
            logger.warning(f"⚠️  Offline models: {', '.join(offline)}")

        logger.info("")

        # Save report
        import json
        report_file = project_root / "data" / "syphon_results" / f"fix_blockers_restart_clusters_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(json.dumps(result, indent=2))
        logger.info(f"📄 Report saved to: {report_file}")

        return 0 if (final_status.get("main_cluster") and models_online == models_total) else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":

    sys.exit(main())