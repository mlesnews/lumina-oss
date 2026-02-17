#!/usr/bin/env python3
"""
Discover NAS N8N (Workflow Automation)

Discovers and integrates N8N workflow automation on the NAS.
N8N is a workflow automation tool running on the NAS.

Tags: #NAS #N8N #WORKFLOW #AUTOMATION #LEVERAGE @JARVIS @LUMINA
"""

import sys
import json
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DiscoverNASN8N")


class NASN8NDiscoverer:
    """
    NAS N8N Discoverer

    Discovers N8N workflow automation on the NAS.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize NAS N8N discoverer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.nas_ip = "<NAS_PRIMARY_IP>"

        # Common N8N ports (expanded list)
        self.n8n_ports = [
            5678,   # Default N8N port
            8080,   # Alternative port
            3000,   # Development port
            5000,   # Alternative port
            8443,   # HTTPS alternative
            443,    # HTTPS
            80,     # HTTP
            9000,   # Alternative
            8888,   # Alternative
        ]

        logger.info("✅ NAS N8N Discoverer initialized")
        logger.info(f"   NAS IP: {self.nas_ip}")

    def discover_n8n(self) -> Dict[str, Any]:
        """
        Discover N8N on NAS

        Returns:
            N8N discovery information
        """
        logger.info("=" * 80)
        logger.info("🔍 DISCOVERING NAS N8N (WORKFLOW AUTOMATION)")
        logger.info("=" * 80)
        logger.info("")

        n8n_info = {
            "installed": False,
            "running": False,
            "endpoint": None,
            "port": None,
            "version": None,
            "workflows": [],
            "api_available": False,
            "leverage_workflows": []
        }

        # Check each port
        for port in self.n8n_ports:
            endpoint = f"http://{self.nas_ip}:{port}"

            try:
                logger.info(f"   🔍 Checking {endpoint}...")

                # Try root endpoint
                response = requests.get(endpoint, timeout=3)
                if response.status_code < 500:
                    # Check if it's N8N
                    if "n8n" in response.text.lower() or "workflow" in response.text.lower():
                        n8n_info["installed"] = True
                        n8n_info["running"] = True
                        n8n_info["endpoint"] = endpoint
                        n8n_info["port"] = port
                        n8n_info["api_available"] = True
                        logger.info(f"   ✅ N8N found at {endpoint}")
                        break
            except Exception as e:
                logger.debug(f"   Port {port} not accessible: {e}")
                continue

        # Try N8N API endpoints
        if n8n_info["running"]:
            # Check for workflows
            try:
                workflows_endpoint = f"{n8n_info['endpoint']}/api/v1/workflows"
                response = requests.get(workflows_endpoint, timeout=5)
                if response.status_code == 200:
                    workflows = response.json()
                    n8n_info["workflows"] = workflows.get("data", [])
                    logger.info(f"   ✅ Found {len(n8n_info['workflows'])} workflows")

                    # Check for leverage workflows
                    leverage_workflows = [
                        w for w in n8n_info["workflows"]
                        if "leverage" in w.get("name", "").lower()
                    ]
                    n8n_info["leverage_workflows"] = leverage_workflows
                    if leverage_workflows:
                        logger.info(f"   ✅ Found {len(leverage_workflows)} leverage workflows")
            except Exception as e:
                logger.debug(f"   Could not fetch workflows: {e}")

            # Check version
            try:
                version_endpoint = f"{n8n_info['endpoint']}/api/v1/version"
                response = requests.get(version_endpoint, timeout=3)
                if response.status_code == 200:
                    version_data = response.json()
                    n8n_info["version"] = version_data.get("version", "Unknown")
                    logger.info(f"   ✅ N8N version: {n8n_info['version']}")
            except Exception:
                pass

        # Check for N8N via Docker (if Docker is accessible)
        if not n8n_info["running"]:
            logger.info("   🔍 Checking Docker containers for N8N...")
            try:
                import subprocess
                # Check if we can access Docker on NAS
                result = subprocess.run(
                    ["docker", "ps", "--filter", "name=n8n", "--format", "{{.Names}}"],
                    capture_output=True,
                    timeout=5,
                    text=True
                )
                if result.returncode == 0 and result.stdout.strip():
                    containers = result.stdout.strip().split('\n')
                    logger.info(f"   ✅ Found N8N Docker containers: {', '.join(containers)}")
                    # Try to get port mapping
                    for container in containers:
                        port_result = subprocess.run(
                            ["docker", "port", container],
                            capture_output=True,
                            timeout=5,
                            text=True
                        )
                        if port_result.returncode == 0:
                            logger.info(f"   📡 Container {container} ports: {port_result.stdout.strip()}")
            except Exception as e:
                logger.debug(f"   Docker check failed: {e}")

        # Check for N8N in common NAS paths
        if not n8n_info["running"]:
            logger.info("   🔍 Checking NAS paths for N8N...")
            # N8N might be running via Docker or as a service
            # Common paths: /volume1/docker/n8n, /usr/local/n8n, etc.
            # This would require SSH access to check

        return n8n_info

    def get_leverage_workflows(self) -> List[Dict[str, Any]]:
        """
        Get leverage workflows from N8N

        Returns:
            List of leverage workflows
        """
        n8n_info = self.discover_n8n()

        if not n8n_info["running"]:
            logger.warning("   ⚠️  N8N not running, cannot fetch workflows")
            return []

        leverage_workflows = []

        for workflow in n8n_info["workflows"]:
            workflow_name = workflow.get("name", "").lower()
            if "leverage" in workflow_name:
                leverage_workflows.append({
                    "id": workflow.get("id"),
                    "name": workflow.get("name"),
                    "active": workflow.get("active", False),
                    "nodes": workflow.get("nodes", []),
                    "connections": workflow.get("connections", {})
                })

        return leverage_workflows

    def integrate_with_star_trek(self) -> Dict[str, Any]:
        """Integrate N8N with Star Trek First Contact Protocol"""
        logger.info("")
        logger.info("   🛸 Integrating N8N with Star Trek Protocol...")

        n8n_info = self.discover_n8n()

        try:
            from jarvis_star_trek_first_contact import JARVISStarTrekFirstContact, Affiliation

            first_contact = JARVISStarTrekFirstContact(self.project_root)

            ai_info = {
                "type": "workflow_automation",
                "capabilities": ["Workflow Automation", "LEVERAGE", "Task Automation"],
                "endpoint": n8n_info.get("endpoint"),
                "workflows": len(n8n_info.get("workflows", [])),
                "leverage_workflows": len(n8n_info.get("leverage_workflows", []))
            }

            encounter = first_contact.encounter_ai("nas_n8n", ai_info)

            # Register as Federation vessel (workflow automation is friendly)
            if "nas_n8n" in first_contact.vessel_registry:
                vessel = first_contact.vessel_registry["nas_n8n"]
                vessel.affiliation = Affiliation.FEDERATION
                vessel.designation = "USS N8N"
                vessel.status = "Active" if n8n_info["running"] else "Inactive"
                vessel.capabilities = ["Workflow Automation", "LEVERAGE", "Task Automation"]

            logger.info("   ✅ N8N integrated with Star Trek Protocol")

            return encounter
        except Exception as e:
            logger.error(f"   ❌ Error integrating with Star Trek: {e}")
            return {"error": str(e)}


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Discover NAS N8N")
        parser.add_argument("--discover", action="store_true", help="Discover N8N")
        parser.add_argument("--leverage", action="store_true", help="Get leverage workflows")
        parser.add_argument("--star-trek", action="store_true", help="Integrate with Star Trek protocol")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        discoverer = NASN8NDiscoverer()

        if args.leverage:
            workflows = discoverer.get_leverage_workflows()
            if args.json:
                print(json.dumps(workflows, indent=2, default=str))
            else:
                print(f"Found {len(workflows)} leverage workflows:")
                for wf in workflows:
                    print(f"  - {wf['name']} (ID: {wf['id']}, Active: {wf['active']})")

        elif args.star_trek:
            result = discoverer.integrate_with_star_trek()
            if args.json:
                print(json.dumps(result, indent=2, default=str))

        elif args.discover or not any(vars(args).values()):
            n8n_info = discoverer.discover_n8n()
            if args.json:
                print(json.dumps(n8n_info, indent=2, default=str))
            else:
                print("=" * 80)
                print("📊 NAS N8N DISCOVERY RESULTS")
                print("=" * 80)
                print("")
                print(f"Installed: {'✅' if n8n_info['installed'] else '❌'}")
                print(f"Running: {'✅' if n8n_info['running'] else '❌'}")
                if n8n_info['endpoint']:
                    print(f"Endpoint: {n8n_info['endpoint']}")
                if n8n_info['version']:
                    print(f"Version: {n8n_info['version']}")
                print(f"Workflows: {len(n8n_info['workflows'])}")
                print(f"Leverage Workflows: {len(n8n_info['leverage_workflows'])}")
                print("")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()