#!/usr/bin/env python3
"""
Homelab Network Topology Mapper

Creates a complete topographical map of the homelab network including:
- All devices and their connections
- Network segments and subnets
- Firewall rules and routing
- Service endpoints
- Device relationships

Tags: #HOMELAB #NETWORK #TOPOLOGY #MAP @JARVIS @LUMINA
"""

import ipaddress
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("homelab_network_topology")


@dataclass
class NetworkInterface:
    """Network interface information"""

    interface_id: str
    name: str
    ip_address: str
    subnet_mask: Optional[str] = None
    mac_address: Optional[str] = None
    gateway: Optional[str] = None
    dns_servers: List[str] = field(default_factory=list)
    status: str = "unknown"  # "up", "down", "unknown"
    device_id: str = ""


@dataclass
class NetworkConnection:
    """Connection between devices"""

    connection_id: str
    source_device_id: str
    target_device_id: str
    connection_type: str = "network"  # "network", "service", "api", "ssh", "http"
    protocol: Optional[str] = None  # "tcp", "udp", "icmp"
    port: Optional[int] = None
    status: str = "unknown"  # "active", "inactive", "unknown"
    last_seen: Optional[str] = None


@dataclass
class NetworkSegment:
    """Network segment/subnet"""

    segment_id: str
    subnet: str
    gateway: Optional[str] = None
    devices: List[str] = field(default_factory=list)
    description: Optional[str] = None


@dataclass
class TopologyNode:
    """Node in topology graph"""

    node_id: str
    node_type: str  # "device", "service", "endpoint"
    name: str
    device_id: Optional[str] = None
    ip_address: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TopologyEdge:
    """Edge in topology graph"""

    edge_id: str
    source_node_id: str
    target_node_id: str
    edge_type: str  # "network", "service", "api", "dependency"
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class NetworkTopologyMapper:
    """Maps network topology"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.devices: List[Dict[str, Any]] = []
        self.interfaces: List[NetworkInterface] = []
        self.connections: List[NetworkConnection] = []
        self.segments: List[NetworkSegment] = []

    def load_audit_data(self, audit_file: Path):
        """Load device data from audit"""
        with open(audit_file, encoding="utf-8") as f:
            audit_data = json.load(f)

        self.devices = audit_data.get("devices", [])
        logger.info(f"Loaded {len(self.devices)} devices from audit")

    def discover_network_segments(self) -> List[NetworkSegment]:
        """Discover network segments/subnets"""
        segments = {}

        for device in self.devices:
            ip = device.get("ip_address")
            if ip:
                try:
                    # Determine subnet (assume /24 for now)
                    network = ipaddress.ip_network(f"{ip}/24", strict=False)
                    subnet_str = str(network)

                    if subnet_str not in segments:
                        segments[subnet_str] = NetworkSegment(
                            segment_id=f"segment_{subnet_str.replace('/', '_')}",
                            subnet=subnet_str,
                            devices=[],
                        )

                    segments[subnet_str].devices.append(device["device_id"])
                except Exception as e:
                    logger.debug(f"Failed to parse IP {ip}: {e}")

        return list(segments.values())

    def discover_connections(self) -> List[NetworkConnection]:
        """Discover connections between devices"""
        connections = []
        connection_id = 0

        # Network connections (same subnet)
        segments = self.discover_network_segments()
        for segment in segments:
            devices = segment.devices
            for i, source_id in enumerate(devices):
                for target_id in devices[i + 1 :]:
                    connections.append(
                        NetworkConnection(
                            connection_id=f"conn_{connection_id}",
                            source_device_id=source_id,
                            target_device_id=target_id,
                            connection_type="network",
                            protocol="ip",
                            status="potential",
                        )
                    )
                    connection_id += 1

        # Service connections (from audit data)
        for device in self.devices:
            device_id = device["device_id"]
            ip = device.get("ip_address")

            # Check for common services
            services = device.get("features", [])
            for service in services:
                if service.get("category") == "service":
                    service_name = service.get("name", "")

                    # Map service to port
                    service_ports = {
                        "ssh": 22,
                        "http": 80,
                        "https": 443,
                        "rdp": 3389,
                        "vnc": 5900,
                        "smb": 445,
                        "nfs": 2049,
                        "docker": 2376,
                        "kubernetes": 6443,
                        "ollama": 11434,
                        "synology_dsm": 5000,
                    }

                    port = None
                    for key, p in service_ports.items():
                        if key in service_name.lower():
                            port = p
                            break

                    if port and ip:
                        # Create connection to service
                        connections.append(
                            NetworkConnection(
                                connection_id=f"conn_{connection_id}",
                                source_device_id=device_id,
                                target_device_id=f"{device_id}_service_{service_name}",
                                connection_type="service",
                                protocol="tcp",
                                port=port,
                                status="active",
                            )
                        )
                        connection_id += 1

        return connections

    def build_topology_graph(self) -> Dict[str, Any]:
        """Build complete topology graph"""
        nodes: List[TopologyNode] = []
        edges: List[TopologyEdge] = []

        # Add device nodes
        for device in self.devices:
            nodes.append(
                TopologyNode(
                    node_id=device["device_id"],
                    node_type="device",
                    name=device.get("device_name", device["device_id"]),
                    device_id=device["device_id"],
                    ip_address=device.get("ip_address"),
                    metadata={
                        "device_type": device.get("device_type"),
                        "os": device.get("operating_system"),
                        "mac_address": device.get("mac_address"),
                    },
                )
            )

        # Add network segment nodes
        segments = self.discover_network_segments()
        for segment in segments:
            nodes.append(
                TopologyNode(
                    node_id=segment.segment_id,
                    node_type="network",
                    name=f"Network: {segment.subnet}",
                    metadata={"subnet": segment.subnet, "gateway": segment.gateway},
                )
            )

            # Connect devices to segments
            for device_id in segment.devices:
                edges.append(
                    TopologyEdge(
                        edge_id=f"edge_{len(edges)}",
                        source_node_id=device_id,
                        target_node_id=segment.segment_id,
                        edge_type="network",
                        metadata={"subnet": segment.subnet},
                    )
                )

        # Add connection edges
        connections = self.discover_connections()
        for conn in connections:
            edges.append(
                TopologyEdge(
                    edge_id=conn.connection_id,
                    source_node_id=conn.source_device_id,
                    target_node_id=conn.target_device_id,
                    edge_type=conn.connection_type,
                    metadata={"protocol": conn.protocol, "port": conn.port, "status": conn.status},
                )
            )

        return {
            "topology_id": f"topology_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "nodes": [asdict(n) for n in nodes],
            "edges": [asdict(e) for e in edges],
            "summary": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "device_nodes": len([n for n in nodes if n.node_type == "device"]),
                "network_nodes": len([n for n in nodes if n.node_type == "network"]),
                "service_nodes": len([n for n in nodes if n.node_type == "service"]),
            },
        }

    def generate_topology_map(self, audit_file: Path) -> Dict[str, Any]:
        """Generate complete topology map"""
        self.load_audit_data(audit_file)

        topology = {
            "map_id": f"topology_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "devices": self.devices,
            "segments": [asdict(s) for s in self.discover_network_segments()],
            "connections": [asdict(c) for c in self.discover_connections()],
            "graph": self.build_topology_graph(),
        }

        return topology

    def save_topology(self, topology: Dict[str, Any], output_file: Path):
        """Save topology map"""
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(topology, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"Topology map saved: {output_file}")
        return topology


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Map homelab network topology")
    parser.add_argument("--audit-file", help="Audit file to use (default: latest)")
    parser.add_argument("--output", help="Output file (default: topology_map_<timestamp>.json)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    mapper = NetworkTopologyMapper(project_root)

    # Find audit file
    audit_dir = project_root / "data" / "homelab_audit"
    if args.audit_file:
        audit_file = Path(args.audit_file)
    else:
        audit_files = sorted(audit_dir.glob("audit_*.json"), reverse=True)
        if not audit_files:
            print("❌ No audit files found")
            sys.exit(1)
        audit_file = audit_files[0]
        print(f"Using audit: {audit_file.name}")

    # Generate topology
    print("Mapping network topology...")
    topology = mapper.generate_topology_map(audit_file)

    # Save topology
    output_dir = project_root / "data" / "homelab_topology"
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.output:
        output_file = Path(args.output)
    else:
        output_file = output_dir / f"topology_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    mapper.save_topology(topology, output_file)

    # Print summary
    print("\n" + "=" * 80)
    print("NETWORK TOPOLOGY MAP SUMMARY")
    print("=" * 80)
    print(f"Devices: {len(topology['devices'])}")
    print(f"Network Segments: {len(topology['segments'])}")
    print(f"Connections: {len(topology['connections'])}")
    graph_summary = topology["graph"]["summary"]
    print("\nTopology Graph:")
    print(f"  Nodes: {graph_summary['total_nodes']}")
    print(f"  Edges: {graph_summary['total_edges']}")
    print(f"  Device Nodes: {graph_summary['device_nodes']}")
    print(f"  Network Nodes: {graph_summary['network_nodes']}")
    print(f"\nTopology map saved: {output_file}")
    print("=" * 80)

    if args.json:
        print(json.dumps(topology, indent=2, default=str))


if __name__ == "__main__":
    main()
