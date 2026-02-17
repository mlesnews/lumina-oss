#!/usr/bin/env python3
"""
JARVIS Unified Status Command

Provides unified status reporting for all JARVIS systems:
- Symbiotic Cluster Coordinator
- NAS Service Monitor
- Network Support Workflows
- Organizational Structure
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class JARVISUnifiedStatus:
    """Unified status reporting for all JARVIS systems"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize unified status"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JARVISUnifiedStatus")

    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all systems"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "systems": {}
        }

        # Symbiotic Cluster Status
        try:
            from symbiotic_cluster_coordinator import SymbioticClusterCoordinator
            from symbiotic_cluster_coordinator import get_master_coordinator as get_cluster_master

            # Try to get existing coordinator or create one
            try:
                coordinator = SymbioticClusterCoordinator()
                cluster_status = coordinator.get_cluster_status()
                utilization_report = coordinator.get_utilization_report()

                status["systems"]["symbiotic_cluster"] = {
                    "status": "operational",
                    "cluster_status": cluster_status,
                    "utilization_report": utilization_report
                }
            except Exception as e:
                status["systems"]["symbiotic_cluster"] = {
                    "status": "not_running",
                    "error": str(e)
                }
        except ImportError:
            status["systems"]["symbiotic_cluster"] = {
                "status": "not_available",
                "error": "Module not available"
            }

        # NAS Service Monitor Status
        try:
            from nas_service_monitor import get_master_coordinator
            master = get_master_coordinator()
            nas_status = master.get_all_status()

            status["systems"]["nas_service_monitor"] = {
                "status": "operational",
                "services": nas_status.get("services", {}),
                "total_services": nas_status.get("total_services", 0),
                "healthy_count": nas_status.get("healthy_count", 0)
            }
        except Exception as e:
            status["systems"]["nas_service_monitor"] = {
                "status": "not_available",
                "error": str(e)
            }

        # Network Support Workflows Status
        try:
            from network_support_workflows import NetworkSupportWorkflows
            workflows = NetworkSupportWorkflows(self.project_root)
            workflow_list = workflows.list_workflows()

            status["systems"]["network_support_workflows"] = {
                "status": "operational",
                "workflows": len(workflow_list),
                "workflow_list": [w["workflow_id"] for w in workflow_list]
            }
        except Exception as e:
            status["systems"]["network_support_workflows"] = {
                "status": "not_available",
                "error": str(e)
            }

        # Organizational Structure Status
        try:
            from lumina_organizational_structure import LuminaOrganizationalStructure
            org = LuminaOrganizationalStructure(self.project_root)
            chart = org.get_organizational_chart()

            status["systems"]["organizational_structure"] = {
                "status": "operational",
                "divisions": chart["summary"]["total_divisions"],
                "teams": chart["summary"]["total_teams"],
                "members": chart["summary"]["total_members"],
                "analysts": chart["summary"]["analysts"],
                "engineers": chart["summary"]["engineers"]
            }
        except Exception as e:
            status["systems"]["organizational_structure"] = {
                "status": "not_available",
                "error": str(e)
            }

        # Deployment Status
        try:
            from deploy_symbiotic_cluster import SymbioticClusterDeployment
            deployment = SymbioticClusterDeployment(self.project_root)
            deployment_status = deployment.get_deployment_status()

            status["systems"]["deployment"] = {
                "status": "available",
                "deployment_status": deployment_status
            }
        except Exception as e:
            status["systems"]["deployment"] = {
                "status": "not_available",
                "error": str(e)
            }

        # Network Nervous System Status
        try:
            from jarvis_network_nervous_system import JARVISNetworkNervousSystem
            nervous_system = JARVISNetworkNervousSystem(self.project_root)
            nervous_map = nervous_system.get_nervous_system_map()

            status["systems"]["network_nervous_system"] = {
                "status": "operational",
                "total_devices": nervous_map["statistics"]["total_devices"],
                "online_devices": nervous_map["statistics"]["online_devices"],
                "domain_devices": nervous_map["statistics"]["domain_devices"]
            }
        except Exception as e:
            status["systems"]["network_nervous_system"] = {
                "status": "not_available",
                "error": str(e)
            }

        return status

    def get_summary(self) -> Dict[str, Any]:
        """Get summary status"""
        all_status = self.get_all_status()

        summary = {
            "timestamp": all_status["timestamp"],
            "systems_operational": 0,
            "systems_total": len(all_status["systems"]),
            "systems": {}
        }

        for system_name, system_status in all_status["systems"].items():
            is_operational = system_status.get("status") == "operational"
            if is_operational:
                summary["systems_operational"] += 1

            summary["systems"][system_name] = {
                "status": system_status.get("status", "unknown"),
                "operational": is_operational
            }

        return summary


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Unified Status")
    parser.add_argument("--all", action="store_true", help="Show all status")
    parser.add_argument("--summary", action="store_true", help="Show summary")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    status = JARVISUnifiedStatus()

    if args.all:
        result = status.get_all_status()
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("\n📊 JARVIS Unified Status")
            print("=" * 60)
            for system_name, system_status in result["systems"].items():
                status_icon = "✅" if system_status.get("status") == "operational" else "⚠️"
                print(f"\n{status_icon} {system_name.replace('_', ' ').title()}")
                print(f"   Status: {system_status.get('status', 'unknown')}")
                if "error" in system_status:
                    print(f"   Error: {system_status['error']}")

    elif args.summary:
        result = status.get_summary()
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("\n📊 JARVIS Status Summary")
            print("=" * 60)
            print(f"Systems Operational: {result['systems_operational']}/{result['systems_total']}")
            print("\nSystems:")
            for system_name, system_info in result["systems"].items():
                icon = "✅" if system_info["operational"] else "⚠️"
                print(f"  {icon} {system_name.replace('_', ' ').title()}: {system_info['status']}")

    else:
        # Default: show summary
        result = status.get_summary()
        print("\n📊 JARVIS Status Summary")
        print("=" * 60)
        print(f"Systems Operational: {result['systems_operational']}/{result['systems_total']}")
        for system_name, system_info in result["systems"].items():
            icon = "✅" if system_info["operational"] else "⚠️"
            print(f"  {icon} {system_name.replace('_', ' ').title()}: {system_info['status']}")

