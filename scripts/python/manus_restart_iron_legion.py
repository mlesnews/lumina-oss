#!/usr/bin/env python3
"""
MANUS: Restart Iron Legion Cluster
Uses MANUS unified control to restart Iron Legion services on KAIJU_NO_8

Tags: #MANUS #IRON_LEGION #CLUSTER #PRIORITY @JARVIS @LUMINA @DOIT
"""
import sys
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("ManusRestartIronLegion")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ManusRestartIronLegion")

try:
    from manus_unified_control import (
        MANUSUnifiedControl,
        ControlArea,
        ControlOperation,
        OperationResult
    )
    MANUS_AVAILABLE = True
except ImportError:
    MANUS_AVAILABLE = False
    logger.error("❌ MANUS Unified Control not available")


class IronLegionRestarter:
    """Restart Iron Legion cluster using MANUS"""

    def __init__(self):
        self.kaiju_ip = "<NAS_IP>"
        self.services_to_restart = [
            "iron-legion-router",      # Port 3000
            "iron-legion-mark-2",      # Port 3002
            "iron-legion-mark-3",      # Port 3003
            "iron-legion-mark-6",      # Port 3006
            "iron-legion-mark-7",      # Port 3007
        ]
        self.manus = None

        if MANUS_AVAILABLE:
            self.manus = MANUSUnifiedControl(project_root)
            logger.info("✅ MANUS Unified Control initialized")
        else:
            logger.error("❌ MANUS not available")

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

    def restart_services_via_manus(self) -> Dict[str, Any]:
        """Restart services using MANUS infrastructure control"""
        if not self.manus:
            return {"success": False, "error": "MANUS not available"}

        logger.info("🚀 Restarting Iron Legion services via MANUS...")
        logger.info("")

        results = {}

        for service_id in self.services_to_restart:
            logger.info(f"🔄 Restarting {service_id}...")

            operation = ControlOperation(
                operation_id=f"restart_{service_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                area=ControlArea.HOME_LAB_INFRASTRUCTURE,
                action="restart_service",
                parameters={
                    "service_id": service_id,
                    "host": self.kaiju_ip,
                    "timeout": 60
                },
                priority=10  # High priority
            )

            try:
                result = self.manus.execute_operation(operation)
                results[service_id] = {
                    "success": result.success,
                    "message": result.message,
                    "errors": result.errors
                }

                if result.success:
                    logger.info(f"   ✅ {service_id}: {result.message}")
                else:
                    logger.warning(f"   ⚠️  {service_id}: {result.message}")
                    if result.errors:
                        for error in result.errors:
                            logger.warning(f"      Error: {error}")
            except Exception as e:
                logger.error(f"   ❌ {service_id}: {e}")
                results[service_id] = {
                    "success": False,
                    "error": str(e)
                }

            # Small delay between restarts
            time.sleep(2)

        return {"success": True, "results": results}

    def restart_all(self) -> Dict[str, Any]:
        """Main routine to restart all services"""
        logger.info("=" * 70)
        logger.info("🚀 MANUS: RESTART IRON LEGION CLUSTER")
        logger.info("=" * 70)
        logger.info("")

        # Check initial status
        initial_status = self.check_cluster_status()
        logger.info("")

        # If all online, skip
        if initial_status["main_cluster"] and all(initial_status["models"].values()):
            logger.info("✅ All services are already online!")
            return {"success": True, "status": initial_status, "action": "none"}

        # Restart via MANUS
        restart_result = self.restart_services_via_manus()
        logger.info("")

        # Wait for services to initialize
        logger.info("⏳ Waiting 20 seconds for services to initialize...")
        time.sleep(20)

        # Check final status
        final_status = self.check_cluster_status()
        logger.info("")

        return {
            "success": restart_result.get("success", False),
            "initial_status": initial_status,
            "final_status": final_status,
            "restart_results": restart_result.get("results", {})
        }


def main():
    try:
        """Main execution"""
        if not MANUS_AVAILABLE:
            logger.error("❌ MANUS Unified Control is not available")
            logger.error("   Cannot restart services without MANUS")
            return 1

        restarter = IronLegionRestarter()
        result = restarter.restart_all()

        logger.info("=" * 70)
        logger.info("📊 SUMMARY")
        logger.info("=" * 70)
        logger.info("")

        if result.get("success"):
            logger.info("✅ Restart operations completed")
        else:
            logger.warning("⚠️  Some restart operations may have failed")

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
        report_file = project_root / "data" / "syphon_results" / f"manus_iron_legion_restart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(json.dumps(result, indent=2))
        logger.info(f"📄 Report saved to: {report_file}")

        return 0 if (result.get("success") and final_status.get("main_cluster") and models_online == models_total) else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":

    sys.exit(main())