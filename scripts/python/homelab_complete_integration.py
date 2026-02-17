#!/usr/bin/env python3
"""
Homelab Complete Integration System

Integrates all audit components into a single comprehensive system:
- Device & Feature Audit
- Control Interface Discovery
- Software Inventory
- Network Topology
- Connection Monitoring
- Anomaly Detection

Creates unified topographical view of entire homelab.

Tags: #HOMELAB #INTEGRATION #COMPLETE #TOPOLOGY @JARVIS @LUMINA
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.python.homelab_living_audit import HomelabLivingAudit

try:
    from lumina_logger import get_logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("homelab_complete_integration")


class HomelabCompleteIntegration:
    """Complete integration of all homelab audit systems"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.living_audit = HomelabLivingAudit(project_root)
        self.architecture_discovery = HomelabArchitectureDiscovery(project_root)

    def generate_complete_map(self) -> Dict[str, Any]:
        """Generate complete topographical map of homelab"""
        print("=" * 80)
        print("GENERATING COMPLETE HOMELAB TOPOGRAPHICAL MAP")
        print("=" * 80)

        # Run comprehensive audit
        audit_results = self.living_audit.run_comprehensive_audit(scan_network=True)

        # Load all component data
        audit_dir = project_root / "data" / "homelab_audit"
        software_dir = project_root / "data" / "homelab_software"
        topology_dir = project_root / "data" / "homelab_topology"
        control_dir = project_root / "data" / "homelab_control"
        monitoring_dir = project_root / "data" / "homelab_monitoring"
        architecture_dir = project_root / "data" / "homelab_architecture"

        # Find latest files
        audit_files = sorted(audit_dir.glob("audit_*.json"), reverse=True)
        software_files = sorted(software_dir.glob("software_inventory_*.json"), reverse=True)
        topology_files = sorted(topology_dir.glob("topology_map_*.json"), reverse=True)
        control_files = sorted(control_dir.glob("control_map_*.json"), reverse=True)
        monitoring_files = sorted(monitoring_dir.glob("monitoring_*.json"), reverse=True)
        architecture_files = sorted(
            architecture_dir.glob("architecture_inventory_*.json"), reverse=True
        )

        complete_map = {
            "map_id": f"complete_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "components": {
                "device_audit": None,
                "control_interfaces": None,
                "software_inventory": None,
                "network_topology": None,
                "connection_monitoring": None,
                "architecture": None,
            },
            "summary": {},
        }

        # Load device audit
        if audit_files:
            with open(audit_files[0], encoding="utf-8") as f:
                complete_map["components"]["device_audit"] = json.load(f)

        # Load software inventory
        if software_files:
            with open(software_files[0], encoding="utf-8") as f:
                complete_map["components"]["software_inventory"] = json.load(f)

        # Load topology
        if topology_files:
            with open(topology_files[0], encoding="utf-8") as f:
                complete_map["components"]["network_topology"] = json.load(f)

        # Load control interfaces
        if control_files:
            with open(control_files[0], encoding="utf-8") as f:
                complete_map["components"]["control_interfaces"] = json.load(f)

        # Load monitoring
        if monitoring_files:
            with open(monitoring_files[0], encoding="utf-8") as f:
                complete_map["components"]["connection_monitoring"] = json.load(f)

        # Load architecture
        if architecture_files:
            with open(architecture_files[0], encoding="utf-8") as f:
                complete_map["components"]["architecture"] = json.load(f)

        # Generate summary
        device_audit = complete_map["components"]["device_audit"]
        software = complete_map["components"]["software_inventory"]
        topology = complete_map["components"]["network_topology"]
        control = complete_map["components"]["control_interfaces"]
        monitoring = complete_map["components"]["connection_monitoring"]
        architecture = complete_map["components"]["architecture"]

        complete_map["summary"] = {
            "devices": len(device_audit.get("devices", [])) if device_audit else 0,
            "features": sum(len(d.get("features", [])) for d in device_audit.get("devices", []))
            if device_audit
            else 0,
            "software_packages": sum(
                d.get("total_packages", 0) for d in software.get("devices", [])
            )
            if software
            else 0,
            "network_segments": len(topology.get("segments", [])) if topology else 0,
            "network_connections": len(topology.get("connections", [])) if topology else 0,
            "control_commands": sum(
                len(i.get("commands", [])) for i in control.get("interfaces", [])
            )
            if control
            else 0,
            "control_apis": sum(
                len(i.get("api_endpoints", [])) for i in control.get("interfaces", [])
            )
            if control
            else 0,
            "control_clis": sum(len(i.get("cli_tools", [])) for i in control.get("interfaces", []))
            if control
            else 0,
            "active_connections": monitoring.get("summary", {}).get("total_connections", 0)
            if monitoring
            else 0,
            "active_accounts": monitoring.get("summary", {}).get("total_accounts", 0)
            if monitoring
            else 0,
            "anomaly_events": monitoring.get("summary", {}).get("total_events", 0)
            if monitoring
            else 0,
            "services": architecture.get("summary", {}).get("total_services", 0)
            if architecture
            else 0,
            "processes": architecture.get("summary", {}).get("total_processes", 0)
            if architecture
            else 0,
            "applications": architecture.get("summary", {}).get("total_applications", 0)
            if architecture
            else 0,
            "frameworks": architecture.get("summary", {}).get("total_frameworks", 0)
            if architecture
            else 0,
        }

        return complete_map

    def save_complete_map(self, complete_map: Dict[str, Any], output_file: Path):
        """Save complete map"""
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(complete_map, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"Complete map saved: {output_file}")

        # Also save summary-only version
        summary_file = output_file.parent / f"{output_file.stem}_summary.json"
        summary = {
            "map_id": complete_map["map_id"],
            "generated_at": complete_map["generated_at"],
            "summary": complete_map["summary"],
        }

        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False, default=str)

        return complete_map

    def generate_visualization_data(self, complete_map: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data structure for visualization"""
        viz_data = {
            "nodes": [],
            "edges": [],
            "layers": {"devices": [], "network": [], "services": [], "software": []},
        }

        # Device nodes
        device_audit = complete_map["components"]["device_audit"]
        if device_audit:
            for device in device_audit.get("devices", []):
                viz_data["nodes"].append(
                    {
                        "id": device["device_id"],
                        "type": "device",
                        "label": device.get("device_name", device["device_id"]),
                        "data": {
                            "ip": device.get("ip_address"),
                            "os": device.get("operating_system"),
                            "type": device.get("device_type"),
                            "features": len(device.get("features", [])),
                        },
                    }
                )
                viz_data["layers"]["devices"].append(device["device_id"])

        # Network topology edges
        topology = complete_map["components"]["network_topology"]
        if topology and "graph" in topology:
            for edge in topology["graph"].get("edges", []):
                viz_data["edges"].append(
                    {
                        "id": edge.get("edge_id"),
                        "source": edge.get("source_node_id"),
                        "target": edge.get("target_node_id"),
                        "type": edge.get("edge_type"),
                        "data": edge.get("metadata", {}),
                    }
                )

        # Software nodes
        software = complete_map["components"]["software_inventory"]
        if software:
            for device_data in software.get("devices", []):
                device_id = device_data["device_id"]
                for package in device_data.get("packages", [])[:10]:  # Top 10 per device
                    package_node_id = f"{device_id}_pkg_{package.get('package_id', '')}"
                    viz_data["nodes"].append(
                        {
                            "id": package_node_id,
                            "type": "software",
                            "label": package.get("name", ""),
                            "data": {
                                "version": package.get("version"),
                                "type": package.get("package_type"),
                                "category": package.get("category"),
                            },
                        }
                    )
                    viz_data["edges"].append(
                        {
                            "id": f"edge_{device_id}_{package_node_id}",
                            "source": device_id,
                            "target": package_node_id,
                            "type": "has_software",
                        }
                    )
                    viz_data["layers"]["software"].append(package_node_id)

        return viz_data


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate complete homelab topographical map")
    parser.add_argument("--output", help="Output file (default: complete_map_<timestamp>.json)")
    parser.add_argument("--visualization", action="store_true", help="Generate visualization data")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    integration = HomelabCompleteIntegration(project_root)

    # Generate complete map
    complete_map = integration.generate_complete_map()

    # Save map
    output_dir = project_root / "data" / "homelab_complete"
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.output:
        output_file = Path(args.output)
    else:
        output_file = output_dir / f"complete_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    integration.save_complete_map(complete_map, output_file)

    # Generate visualization data if requested
    if args.visualization:
        viz_data = integration.generate_visualization_data(complete_map)
        viz_file = output_file.parent / f"{output_file.stem}_visualization.json"
        with open(viz_file, "w", encoding="utf-8") as f:
            json.dump(viz_data, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n✅ Visualization data saved: {viz_file}")

    # Print summary
    print("\n" + "=" * 80)
    print("COMPLETE HOMELAB MAP SUMMARY")
    print("=" * 80)
    summary = complete_map["summary"]
    print(f"Devices: {summary['devices']}")
    print(f"Features: {summary['features']}")
    print(f"Software Packages: {summary['software_packages']}")
    print(f"Network Segments: {summary['network_segments']}")
    print(f"Network Connections: {summary['network_connections']}")
    print(f"Control Commands: {summary['control_commands']}")
    print(f"Control APIs: {summary['control_apis']}")
    print(f"Control CLIs: {summary['control_clis']}")
    print(f"Active Connections: {summary['active_connections']}")
    print(f"Active Accounts: {summary['active_accounts']}")
    print(f"Anomaly Events: {summary['anomaly_events']}")
    print(f"\nComplete map saved: {output_file}")
    print("=" * 80)

    if args.json:
        print(json.dumps(complete_map, indent=2, default=str))


if __name__ == "__main__":
    main()
