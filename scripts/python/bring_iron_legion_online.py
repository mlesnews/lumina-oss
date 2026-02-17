#!/usr/bin/env python3
"""
Bring Iron Legion Cluster Online - PRIORITY
Restarts Iron Legion services on KAIJU_NO_8 (<NAS_IP>)

Tags: #CLUSTER #IRON_LEGION #PRIORITY @JARVIS @LUMINA @DOIT
"""
import sys
import subprocess
import requests
import time
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
    logger = get_logger("BringIronLegionOnline")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("BringIronLegionOnline")

try:
    from nas_azure_vault_integration import NASAzureVaultIntegration
    from unified_secrets_manager import UnifiedSecretsManager
except ImportError:
    NASAzureVaultIntegration = None
    UnifiedSecretsManager = None


class IronLegionClusterManager:
    """Manage Iron Legion cluster on KAIJU_NO_8"""

    def __init__(self):
        self.kaiju_ip = "<NAS_IP>"
        self.kaiju_hostname = "KAIJU_NO_8"
        self.ssh_port = 22
        self.ssh_client = None
        self.credentials = None

    def get_credentials(self) -> Optional[Dict[str, str]]:
        """Get SSH credentials from Azure Key Vault"""
        if not NASAzureVaultIntegration:
            logger.warning("⚠️  NASAzureVaultIntegration not available")
            return None

        try:
            nas_integration = NASAzureVaultIntegration(nas_ip=self.kaiju_ip)
            creds = nas_integration.get_nas_credentials()
            if creds and creds.get("username") and creds.get("password"):
                logger.info(f"✅ Retrieved credentials for {self.kaiju_ip}")
                return creds
            else:
                logger.warning("⚠️  Credentials not found in Azure Key Vault")
                return None
        except Exception as e:
            logger.error(f"❌ Error getting credentials: {e}")
            return None

    def test_ssh_connection(self) -> bool:
        """Test SSH connectivity to KAIJU_NO_8"""
        logger.info(f"🔍 Testing SSH connection to {self.kaiju_hostname} ({self.kaiju_ip})...")

        if not self.credentials:
            self.credentials = self.get_credentials()

        if not self.credentials:
            logger.warning("⚠️  No credentials available for SSH")
            return False

        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=self.kaiju_ip,
                port=self.ssh_port,
                username=self.credentials["username"],
                password=self.credentials["password"],
                timeout=10
            )

            # Test command
            stdin, stdout, stderr = client.exec_command("echo 'SSH connection successful'", timeout=5)
            output = stdout.read().decode().strip()
            client.close()

            if "successful" in output:
                logger.info("✅ SSH connection successful")
                return True
            else:
                logger.warning("⚠️  SSH connection test returned unexpected output")
                return False

        except paramiko.AuthenticationException:
            logger.error("❌ SSH authentication failed")
            return False
        except paramiko.SSHException as e:
            logger.error(f"❌ SSH error: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            return False

    def restart_iron_legion_services(self) -> Dict[str, Any]:
        """Restart Iron Legion services via SSH"""
        logger.info("🚀 Restarting Iron Legion services...")

        if not self.credentials:
            self.credentials = self.get_credentials()

        if not self.credentials:
            return {"success": False, "error": "No credentials available"}

        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=self.kaiju_ip,
                port=self.ssh_port,
                username=self.credentials["username"],
                password=self.credentials["password"],
                timeout=10
            )

            commands = [
                # Check if docker-compose is available
                "which docker-compose || which docker",
                # Find Iron Legion compose file
                "find / -name '*iron*legion*.yml' -o -name '*iron-legion*.yml' 2>/dev/null | head -5",
                # Restart containers (try common locations)
                "cd /docker/iron-legion && docker-compose restart || docker compose restart",
                "cd ~/iron-legion && docker-compose restart || docker compose restart",
                "cd /opt/iron-legion && docker-compose restart || docker compose restart",
                # Alternative: restart by container name
                "docker restart iron-legion-router iron-legion-mark-2 iron-legion-mark-3 iron-legion-mark-6 iron-legion-mark-7 2>/dev/null || true",
                # Check container status
                "docker ps -a | grep iron-legion || docker ps -a | grep iron"
            ]

            results = {}
            for cmd in commands:
                logger.info(f"   Running: {cmd[:60]}...")
                stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
                output = stdout.read().decode().strip()
                error = stderr.read().decode().strip()

                if output:
                    logger.info(f"   Output: {output[:200]}")
                    results[cmd[:50]] = output
                if error and "No such file" not in error:
                    logger.warning(f"   Error: {error[:200]}")

            client.close()

            # Wait for services to start
            logger.info("⏳ Waiting 15 seconds for services to initialize...")
            time.sleep(15)

            return {"success": True, "results": results}

        except Exception as e:
            logger.error(f"❌ Error restarting services: {e}")
            return {"success": False, "error": str(e)}

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

    def bring_cluster_online(self) -> Dict[str, Any]:
        """Main routine to bring cluster online"""
        logger.info("=" * 70)
        logger.info("🚀 BRINGING IRON LEGION CLUSTER ONLINE")
        logger.info("=" * 70)
        logger.info("")

        # Check current status
        initial_status = self.check_cluster_status()
        logger.info("")

        # If already online, return
        if initial_status["main_cluster"] and all(initial_status["models"].values()):
            logger.info("✅ All services are already online!")
            return {"success": True, "status": initial_status, "action": "none"}

        # Try SSH restart
        logger.info("Attempting to restart services via SSH...")
        if self.test_ssh_connection():
            restart_result = self.restart_iron_legion_services()
            logger.info("")

            # Check status after restart
            final_status = self.check_cluster_status()

            return {
                "success": restart_result.get("success", False),
                "initial_status": initial_status,
                "final_status": final_status,
                "restart_result": restart_result
            }
        else:
            logger.warning("⚠️  SSH connection failed - manual intervention required")
            logger.info("")
            logger.info("📋 Manual Steps:")
            logger.info(f"   1. Access {self.kaiju_hostname} ({self.kaiju_ip}) via:")
            logger.info("      - SSH: ssh user@<NAS_IP>")
            logger.info("      - Synology DSM: https://<NAS_IP>:5001")
            logger.info("   2. Restart Iron Legion containers:")
            logger.info("      - Container Manager → Restart containers:")
            logger.info("        • iron-legion-router (port 3000)")
            logger.info("        • iron-legion-mark-2 (port 3002)")
            logger.info("        • iron-legion-mark-3 (port 3003)")
            logger.info("        • iron-legion-mark-6 (port 3006)")
            logger.info("        • iron-legion-mark-7 (port 3007)")

            return {
                "success": False,
                "error": "SSH connection failed",
                "status": initial_status,
                "requires_manual": True
            }


def main():
    try:
        """Main execution"""
        logger.info("=" * 70)
        logger.info("🔧 IRON LEGION CLUSTER - BRING ONLINE")
        logger.info("=" * 70)
        logger.info("")

        manager = IronLegionClusterManager()
        result = manager.bring_cluster_online()

        logger.info("")
        logger.info("=" * 70)
        logger.info("📊 SUMMARY")
        logger.info("=" * 70)
        logger.info("")

        if result.get("success"):
            logger.info("✅ Cluster restart attempted")
        else:
            logger.warning("⚠️  Cluster restart failed or requires manual intervention")

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
        report_file = project_root / "data" / "syphon_results" / f"iron_legion_online_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(json.dumps(result, indent=2))
        logger.info(f"📄 Report saved to: {report_file}")

        return 0 if result.get("success") else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":

    sys.exit(main())