#!/usr/bin/env python3
"""
JARVIS ULTRON-LUMINA Integration Status

Verifies and reports on ULTRON cluster integration with LUMINA workflows.

Tags: #ULTRON #LUMINA #INTEGRATION @TEAM
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
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

logger = get_logger("JARVISULTRONStatus")


class JARVISULTRONLuminaIntegrationStatus:
    """
    JARVIS ULTRON-LUMINA Integration Status Checker
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        self.logger.info("✅ ULTRON-LUMINA Integration Status Checker initialized")

    def check_ultron_cluster(self) -> Dict[str, Any]:
        """Check ULTRON cluster status"""
        self.logger.info("🔍 Checking ULTRON cluster status...")

        status = {
            "cluster_name": "ULTRON",
            "type": "virtual_hybrid",
            "nodes": [],
            "status": "unknown",
            "integration": {}
        }

        # Check for ULTRON router
        try:
            from jarvis_ultron_hybrid_cluster import ULTRONHybridCluster
            cluster = ULTRONHybridCluster(self.project_root)

            # Get cluster status
            cluster_status = cluster.get_cluster_status()
            status["status"] = "available"
            status.update(cluster_status)
            status["integration"] = {
                "fencing": cluster.fencing_system is not None,
                "routing": True,
                "load_balancing": True,
                "health_monitoring": True
            }

        except ImportError as e:
            status["status"] = "module_not_found"
            status["error"] = f"ULTRON cluster module not found: {e}"
        except Exception as e:
            status["status"] = "error"
            status["error"] = str(e)

        return status

    def check_lumina_workflows(self) -> Dict[str, Any]:
        try:
            """Check LUMINA workflow integration"""
            self.logger.info("🔍 Checking LUMINA workflow integration...")

            workflows = {
                "workflow_systems": [],
                "integration_status": {},
                "total_workflows": 0
            }

            # Check for workflow files
            workflow_dir = self.project_root / "scripts" / "python"
            workflow_files = list(workflow_dir.glob("*workflow*.py"))

            workflows["workflow_files"] = [f.name for f in workflow_files]
            workflows["total_workflows"] = len(workflow_files)

            # Check key workflow systems
            key_workflows = [
                "jarvis_autonomous_workflow_executor",
                "jarvis_workflow_orchestrator",
                "jarvis_continuous_execution"
            ]

            for workflow in key_workflows:
                workflow_file = workflow_dir / f"{workflow}.py"
                if workflow_file.exists():
                    workflows["workflow_systems"].append(workflow)
                    workflows["integration_status"][workflow] = "available"
                else:
                    workflows["integration_status"][workflow] = "not_found"

            return workflows

        except Exception as e:
            self.logger.error(f"Error in check_lumina_workflows: {e}", exc_info=True)
            raise
    def check_ultron_workflow_integration(self) -> Dict[str, Any]:
        """Check ULTRON integration with workflows"""
        self.logger.info("🔍 Checking ULTRON-workflow integration...")

        integration = {
            "ultron_in_workflows": False,
            "workflow_routing": False,
            "local_first_enforcement": False,
            "cluster_health_monitoring": False
        }

        # Check for local-first router
        try:
            from jarvis_local_first_llm_router import LocalFirstLLMRouter
            router = LocalFirstLLMRouter(self.project_root)
            integration["local_first_enforcement"] = True
            integration["workflow_routing"] = True
        except ImportError:
            pass
        except Exception as e:
            self.logger.warning(f"⚠️  Router check error: {e}")

        # Check for ULTRON fencing
        try:
            from jarvis_ultron_fencing_system import ULTRONFencingSystem
            fencing = ULTRONFencingSystem(self.project_root)
            integration["cluster_health_monitoring"] = True
        except ImportError:
            pass
        except Exception as e:
            self.logger.warning(f"⚠️  Fencing check error: {e}")

        return integration

    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive integration status"""
        self.logger.info("📊 Generating comprehensive integration status...")

        status = {
            "timestamp": datetime.now().isoformat(),
            "ultron_cluster": self.check_ultron_cluster(),
            "lumina_workflows": self.check_lumina_workflows(),
            "integration": self.check_ultron_workflow_integration(),
            "summary": {}
        }

        # Generate summary
        ultron_ok = status["ultron_cluster"].get("status") == "available"
        workflows_ok = status["lumina_workflows"].get("total_workflows", 0) > 0
        integration_ok = any(status["integration"].values())

        status["summary"] = {
            "ultron_cluster_available": ultron_ok,
            "workflows_available": workflows_ok,
            "integration_active": integration_ok,
            "all_systems_go": ultron_ok and workflows_ok and integration_ok
        }

        return status


def main():
    try:
        """CLI interface"""
        import json

        project_root = Path(__file__).parent.parent.parent
        checker = JARVISULTRONLuminaIntegrationStatus(project_root)

        status = checker.get_comprehensive_status()
        print(json.dumps(status, indent=2, default=str))

        # Print summary
        print("\n" + "="*80)
        print("ULTRON-LUMINA INTEGRATION STATUS")
        print("="*80)
        print(f"ULTRON Cluster: {'✅' if status['summary']['ultron_cluster_available'] else '❌'}")
        print(f"LUMINA Workflows: {'✅' if status['summary']['workflows_available'] else '❌'}")
        print(f"Integration Active: {'✅' if status['summary']['integration_active'] else '❌'}")
        print(f"All Systems Go: {'✅' if status['summary']['all_systems_go'] else '❌'}")
        print("="*80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()