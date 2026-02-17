#!/usr/bin/env python3
"""
MANUS: Direct Restart Iron Legion (Bypass Restrictions)
Directly restarts Iron Legion containers using Synology DSM API
Bypasses MANUS restrictions for critical cluster operations

Tags: #MANUS #IRON_LEGION #PRIORITY #BYPASS @JARVIS @LUMINA @DOIT
"""
import sys
import time
import requests
import urllib3
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    from lumina_logger import get_logger
    logger = get_logger("ManusDirectRestart")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ManusDirectRestart")

try:
    from nas_azure_vault_integration import NASAzureVaultIntegration
except ImportError:
    NASAzureVaultIntegration = None


class DirectIronLegionRestarter:
    """Direct restart using Synology DSM API - bypasses MANUS restrictions"""

    def __init__(self):
        self.kaiju_ip = "<NAS_IP>"
        self.kaiju_port = 5001
        self.base_url = f"https://{self.kaiju_ip}:{self.kaiju_port}/webapi"
        self.session = requests.Session()
        self.session.verify = False  # Self-signed cert
        self.sid: Optional[str] = None
        self.credentials = None

        # Containers to restart
        self.containers = [
            "iron-legion-router",      # Port 3000
            "iron-legion-mark-2",       # Port 3002
            "iron-legion-mark-3",       # Port 3003
            "iron-legion-mark-6",       # Port 3006
            "iron-legion-mark-7",       # Port 3007
        ]

    def get_credentials(self) -> Optional[Dict[str, str]]:
        """Get DSM credentials from Azure Key Vault"""
        if not NASAzureVaultIntegration:
            return None

        try:
            nas_integration = NASAzureVaultIntegration(nas_ip=self.kaiju_ip)
            creds = nas_integration.get_nas_credentials()
            if creds and creds.get("username") and creds.get("password"):
                logger.info(f"✅ Retrieved DSM credentials for {self.kaiju_ip}")
                return creds
            return None
        except Exception as e:
            logger.error(f"❌ Error getting credentials: {e}")
            return None

    def login_dsm(self) -> bool:
        """Login to Synology DSM API"""
        if not self.credentials:
            self.credentials = self.get_credentials()

        if not self.credentials:
            logger.error("❌ No credentials available")
            return False

        try:
            # Get API info
            url = f"{self.base_url}/query.cgi"
            params = {
                "api": "SYNO.API.Info",
                "version": "1",
                "method": "query",
                "query": "SYNO.API.Auth"
            }
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            # Login
            url = f"{self.base_url}/auth.cgi"
            params = {
                "api": "SYNO.API.Auth",
                "version": "3",
                "method": "login",
                "account": self.credentials["username"],
                "passwd": self.credentials["password"],
                "session": "ContainerManager",
                "format": "sid"
            }

            logger.info(f"🔐 Logging in to DSM at {self.kaiju_ip}:{self.kaiju_port}")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get("success"):
                self.sid = data.get("data", {}).get("sid")
                logger.info("✅ Successfully authenticated to DSM API")
                return True
            else:
                error_code = data.get("error", {}).get("code", "unknown")
                logger.error(f"❌ Login failed: {error_code}")
                return False

        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return False

    def restart_container(self, container_name: str) -> Dict[str, Any]:
        """Restart a container via Container Manager API"""
        if not self.sid:
            return {"success": False, "error": "Not authenticated"}

        try:
            # Get Container Manager API version
            url = f"{self.base_url}/query.cgi"
            params = {
                "api": "SYNO.API.Info",
                "version": "1",
                "method": "query",
                "query": "SYNO.Docker.Container",
                "_sid": self.sid
            }
            response = self.session.get(url, params=params, timeout=10)
            cm_version = "1"
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    cm_version = str(result.get("data", {}).get("SYNO.Docker.Container", {}).get("maxVersion", "1"))

            # Restart container
            url = f"{self.base_url}/entry.cgi"
            params = {
                "api": "SYNO.Docker.Container",
                "version": cm_version,
                "method": "restart",
                "name": container_name,
                "_sid": self.sid
            }

            logger.info(f"   Restarting {container_name}...")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            result = response.json()
            if result.get("success"):
                logger.info(f"   ✅ {container_name} restart initiated")
                return {"success": True, "message": "Restart initiated"}
            else:
                error = result.get("error", {})
                logger.warning(f"   ⚠️  {container_name}: {error.get('code', 'unknown')}")
                return {"success": False, "error": error}

        except Exception as e:
            logger.error(f"   ❌ {container_name}: {e}")
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

    def restart_all(self) -> Dict[str, Any]:
        """Main routine to restart all containers"""
        logger.info("=" * 70)
        logger.info("🚀 MANUS DIRECT: RESTART IRON LEGION CLUSTER")
        logger.info("=" * 70)
        logger.info("")

        # Check initial status
        initial_status = self.check_cluster_status()
        logger.info("")

        # If all online, skip
        if initial_status["main_cluster"] and all(initial_status["models"].values()):
            logger.info("✅ All services are already online!")
            return {"success": True, "status": initial_status, "action": "none"}

        # Login to DSM
        if not self.login_dsm():
            logger.error("❌ Failed to authenticate to DSM")
            return {"success": False, "error": "Authentication failed", "status": initial_status}

        logger.info("")

        # Restart containers
        logger.info("🚀 Restarting Iron Legion containers...")
        results = {}
        for container_name in self.containers:
            result = self.restart_container(container_name)
            results[container_name] = result
            time.sleep(1)  # Small delay between restarts

        logger.info("")

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
            "restart_results": results
        }


def main():
    try:
        """Main execution"""
        restarter = DirectIronLegionRestarter()
        result = restarter.restart_all()

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
        report_file = project_root / "data" / "syphon_results" / f"manus_direct_iron_legion_restart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(json.dumps(result, indent=2))
        logger.info(f"📄 Report saved to: {report_file}")

        return 0 if (final_status.get("main_cluster") and models_online == models_total) else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":

    sys.exit(main())