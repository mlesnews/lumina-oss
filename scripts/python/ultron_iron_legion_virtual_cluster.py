#!/usr/bin/env python3
"""
ULTRON-Iron Legion Virtual Cluster with Failover

12-node ULTRON cluster with Iron Legion failover capabilities.
Round-robin load balancing across all nodes.

Tags: #ULTRON #IRON_LEGION #CLUSTER #FAILOVER #ROUND_ROBIN @JARVIS @LUMINA
"""

import sys
import json
import time
import requests
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque
import random

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ULTRONIronLegionCluster")


@dataclass
class ClusterNode:
    """Cluster node configuration"""
    name: str
    endpoint: str
    cluster_type: str  # "ultron" or "iron_legion"
    port: int
    priority: int  # Lower = higher priority
    health_check_url: str
    is_active: bool = False
    last_health_check: Optional[datetime] = None
    response_time_ms: float = 0.0
    failure_count: int = 0
    success_count: int = 0


@dataclass
class ClusterVote:
    """Vote from a cluster node (12 votes for ULTRON)"""
    node_name: str
    vote: bool  # True = healthy, False = unhealthy
    timestamp: datetime
    response_time_ms: float
    cluster_type: str


class RoundRobinBalancer:
    """Round-robin load balancer"""

    def __init__(self):
        self.nodes: List[ClusterNode] = []
        self.current_index = 0
        self.lock = threading.Lock()

    def add_node(self, node: ClusterNode):
        """Add node to round-robin pool"""
        with self.lock:
            if node not in self.nodes:
                self.nodes.append(node)
                logger.info(f"✅ Added {node.name} to round-robin pool")

    def remove_node(self, node_name: str):
        """Remove node from round-robin pool"""
        with self.lock:
            self.nodes = [n for n in self.nodes if n.name != node_name]
            logger.info(f"❌ Removed {node_name} from round-robin pool")

    def get_next_node(self) -> Optional[ClusterNode]:
        """Get next node in round-robin order"""
        with self.lock:
            active_nodes = [n for n in self.nodes if n.is_active]
            if not active_nodes:
                return None

            # Round-robin selection
            node = active_nodes[self.current_index % len(active_nodes)]
            self.current_index += 1
            return node

    def get_all_active_nodes(self) -> List[ClusterNode]:
        """Get all active nodes"""
        with self.lock:
            return [n for n in self.nodes if n.is_active]


class FailoverManager:
    """Failover manager for ULTRON <-> Iron Legion"""

    def __init__(self):
        self.ultron_nodes: List[ClusterNode] = []
        self.iron_legion_nodes: List[ClusterNode] = []
        self.current_cluster: str = "ultron"  # "ultron" or "iron_legion"
        self.failover_threshold = 6  # Need 6+ healthy ULTRON nodes (50% of 12)
        self.failover_active = False

    def add_ultron_node(self, node: ClusterNode):
        """Add ULTRON node"""
        if node.cluster_type == "ultron":
            self.ultron_nodes.append(node)
            logger.info(f"✅ Added ULTRON node: {node.name}")

    def add_iron_legion_node(self, node: ClusterNode):
        """Add Iron Legion node"""
        if node.cluster_type == "iron_legion":
            self.iron_legion_nodes.append(node)
            logger.info(f"✅ Added Iron Legion node: {node.name}")

    def get_healthy_ultron_count(self) -> int:
        """Get count of healthy ULTRON nodes"""
        return sum(1 for n in self.ultron_nodes if n.is_active)

    def should_failover_to_iron_legion(self) -> bool:
        """Check if should failover to Iron Legion"""
        healthy_ultron = self.get_healthy_ultron_count()

        if healthy_ultron < self.failover_threshold:
            logger.warning(f"⚠️  ULTRON health low: {healthy_ultron}/12 nodes healthy")
            return True
        return False

    def should_failback_to_ultron(self) -> bool:
        """Check if should failback to ULTRON"""
        healthy_ultron = self.get_healthy_ultron_count()

        if healthy_ultron >= self.failover_threshold:
            logger.info(f"✅ ULTRON health restored: {healthy_ultron}/12 nodes healthy")
            return True
        return False

    def execute_failover(self):
        """Execute failover to Iron Legion"""
        if self.current_cluster == "iron_legion":
            return  # Already on Iron Legion

        logger.warning("🔄 FAILOVER: Switching to Iron Legion cluster")
        self.current_cluster = "iron_legion"
        self.failover_active = True

    def execute_failback(self):
        """Execute failback to ULTRON"""
        if self.current_cluster == "ultron":
            return  # Already on ULTRON

        logger.info("🔄 FAILBACK: Switching to ULTRON cluster")
        self.current_cluster = "ultron"
        self.failover_active = False

    def get_active_cluster_nodes(self) -> List[ClusterNode]:
        """Get active nodes from current cluster"""
        if self.current_cluster == "ultron":
            return [n for n in self.ultron_nodes if n.is_active]
        else:
            return [n for n in self.iron_legion_nodes if n.is_active]


class ULTRONIronLegionVirtualCluster:
    """ULTRON-Iron Legion Virtual Cluster with 12 votes and failover"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.round_robin = RoundRobinBalancer()
        self.failover_manager = FailoverManager()

        # 12 ULTRON nodes (votes)
        self.ultron_nodes: List[ClusterNode] = []
        self.iron_legion_nodes: List[ClusterNode] = []

        # Health monitoring
        self.monitoring = False
        self.monitor_thread = None
        self.health_check_interval = 10  # seconds

        # Statistics
        self.stats = {
            "total_requests": 0,
            "ultron_requests": 0,
            "iron_legion_requests": 0,
            "failover_count": 0,
            "failback_count": 0,
            "round_robin_rotations": 0
        }

    def initialize_ultron_nodes(self, count: int = 12, distributed: bool = True):
        """Initialize 12 ULTRON nodes distributed across physical infrastructure"""
        logger.info(f"🚀 Initializing {count} ULTRON nodes across physical infrastructure...")

        if distributed:
            # STACKED CLUSTER: 12 nodes across BOTH physical computers + NAS
            # All three machines stacked together for maximum capacity
            # LAPTOP: RTX 5090 GPU-accelerated nodes (uses VRAM, not disk space!)
            # DESKTOP: CPU/GPU nodes on KAIJU_NO_8
            # NAS: CPU nodes on Synology
            # STACKED ARCHITECTURE: All three machines work together as unified cluster

            ultron_config = [
                # Laptop (MILLENNIUM-FALC) - 4 GPU-accelerated nodes (RTX 5090)
                # Uses VRAM only - safe with 92.6% disk usage
                {"host": "<NAS_IP>", "port": 11434, "name": "laptop-gpu", "count": 4, "gpu": True, "vram": 24, "machine": "LAPTOP"},
                # Desktop (KAIJU_NO_8) - 4 nodes (RTX 3090 available)
                {"host": "<NAS_IP>", "port": 11434, "name": "desktop", "count": 4, "gpu": True, "vram": 24, "machine": "DESKTOP"},
                # NAS (Synology DS2118+) - 4 nodes (CPU-based, DSM Container Manager)
                {"host": "<NAS_PRIMARY_IP>", "port": 11434, "name": "nas", "count": 4, "gpu": False, "machine": "NAS"}
            ]

            node_index = 1
            for config in ultron_config:
                for i in range(config["count"]):
                    node = ClusterNode(
                        name=f"ultron-node-{node_index:02d}-{config['name']}",
                        endpoint=f"http://{config['host']}:{config['port']}",
                        cluster_type="ultron",
                        port=config["port"],
                        priority=node_index,
                        health_check_url=f"http://{config['host']}:{config['port']}/api/tags"
                    )
                    self.ultron_nodes.append(node)
                    self.failover_manager.add_ultron_node(node)
                    self.round_robin.add_node(node)
                    gpu_info = f" (GPU: RTX {config.get('vram', 0)}GB)" if config.get("gpu") else " (CPU)"
                    logger.info(f"   ✅ {node.name} → {config['host']}:{config['port']}{gpu_info} [{config['machine']}]")
                    node_index += 1

            logger.info(f"✅ Initialized {count} ULTRON nodes STACKED across all machines:")
            logger.info(f"   📦 STACKED ARCHITECTURE: Laptop + Desktop + NAS working together")
            logger.info(f"   - Laptop (MILLENNIUM-FALC): 4 GPU nodes @ <NAS_IP>:11434 (RTX 5090 24GB VRAM)")
            logger.info(f"   - Desktop (KAIJU_NO_8): 4 GPU nodes @ <NAS_IP>:11434 (RTX 3090 24GB VRAM)")
            logger.info(f"   - NAS (Synology DS2118+): 4 CPU nodes @ <NAS_PRIMARY_IP>:11434 (DSM Container Manager)")
            logger.info(f"   💡 All three machines STACKED for unified cluster capacity!")
            logger.info(f"   💡 GPU nodes use VRAM (not disk space) - safe with 92.6% disk usage!")
        else:
            # LOCAL CLUSTER: All nodes on localhost (for testing)
            base_endpoint = "http://localhost:11434"
            logger.info(f"   Using localhost only (testing mode)")

            for i in range(1, count + 1):
                node = ClusterNode(
                    name=f"ultron-node-{i:02d}",
                    endpoint=base_endpoint,
                    cluster_type="ultron",
                    port=11434,
                    priority=i,
                    health_check_url=f"{base_endpoint}/api/tags"
                )
                self.ultron_nodes.append(node)
                self.failover_manager.add_ultron_node(node)
                self.round_robin.add_node(node)

            logger.info(f"✅ Initialized {count} ULTRON nodes (localhost mode)")

    def initialize_iron_legion_nodes(self):
        """Initialize Iron Legion nodes from KAIJU desktop (Mark I-VII)"""
        logger.info("🚀 Initializing Iron Legion nodes on KAIJU desktop...")

        # Iron Legion nodes on KAIJU_NO_8 (Desktop) - Mark I-VII
        kaiju_host = "<NAS_IP>"  # KAIJU desktop (kaiju_no_8)
        iron_legion_ports = [3001, 3002, 3003, 3004, 3005, 3006, 3007]
        mark_names = ["Mark I", "Mark II", "Mark III", "Mark IV", "Mark V", "Mark VI", "Mark VII"]

        for port, mark_name in zip(iron_legion_ports, mark_names):
            node = ClusterNode(
                name=f"iron-legion-{mark_name.lower().replace(' ', '-')}",
                endpoint=f"http://{kaiju_host}:{port}",
                cluster_type="iron_legion",
                port=port,
                priority=100 + port,  # Lower priority than ULTRON
                health_check_url=f"http://{kaiju_host}:{port}/api/tags"
            )
            self.iron_legion_nodes.append(node)
            self.failover_manager.add_iron_legion_node(node)
            self.round_robin.add_node(node)
            logger.info(f"   ✅ {node.name} → {kaiju_host}:{port}")

        logger.info(f"✅ Initialized {len(iron_legion_ports)} Iron Legion nodes on KAIJU desktop")

    def initialize_iron_legion_nodes_custom(self, node_configs: List[tuple]):
        """Initialize Iron Legion nodes with custom configurations"""
        logger.info("🚀 Initializing Iron Legion nodes with custom configuration...")

        for node_name, endpoint in node_configs:
            # Parse endpoint to get host and port
            if "://" in endpoint:
                endpoint = endpoint.split("://")[1]
            host, port_str = endpoint.split(":")
            port = int(port_str)

            node = ClusterNode(
                name=node_name,
                endpoint=f"http://{host}:{port}",
                cluster_type="iron_legion",
                port=port,
                priority=100 + port,  # Lower priority than ULTRON
                health_check_url=f"http://{host}:{port}/api/tags"
            )
            self.iron_legion_nodes.append(node)
            self.failover_manager.add_iron_legion_node(node)
            self.round_robin.add_node(node)
            logger.info(f"   ✅ {node.name} → {host}:{port}")

        logger.info(f"✅ Initialized {len(node_configs)} Iron Legion nodes with custom configuration")

    def add_iron_legion_node_custom(self, node_name: str, endpoint: str):
        """Add a single Iron Legion node with custom configuration"""
        # Parse endpoint to get host and port
        if "://" in endpoint:
            endpoint = endpoint.split("://")[1]
        host, port_str = endpoint.split(":")
        port = int(port_str)

        node = ClusterNode(
            name=node_name,
            endpoint=f"http://{host}:{port}",
            cluster_type="iron_legion",
            port=port,
            priority=100 + port,  # Lower priority than ULTRON
            health_check_url=f"http://{host}:{port}/api/tags"
        )
        self.iron_legion_nodes.append(node)
        self.failover_manager.add_iron_legion_node(node)
        self.round_robin.add_node(node)
        logger.info(f"   ✅ Added {node.name} → {host}:{port}")

    def check_node_health(self, node: ClusterNode) -> bool:
        """Check health of a node"""
        try:
            start_time = time.time()
            response = requests.get(node.health_check_url, timeout=3)
            response_time = (time.time() - start_time) * 1000  # ms

            is_healthy = response.status_code == 200

            node.last_health_check = datetime.now()
            node.response_time_ms = response_time

            if is_healthy:
                node.success_count += 1
                if not node.is_active:
                    logger.info(f"✅ {node.name} is now healthy")
                node.is_active = True
                node.failure_count = 0
            else:
                node.failure_count += 1
                if node.is_active:
                    logger.warning(f"⚠️  {node.name} is now unhealthy")
                node.is_active = False

            return is_healthy

        except Exception as e:
            node.failure_count += 1
            node.is_active = False
            node.last_health_check = datetime.now()
            logger.debug(f"❌ {node.name} health check failed: {e}")
            return False

    def monitor_cluster_health(self):
        """Monitor cluster health and manage failover"""
        self.monitoring = True
        logger.info("🤖 Starting cluster health monitoring...")

        while self.monitoring:
            try:
                # Check all ULTRON nodes
                for node in self.ultron_nodes:
                    self.check_node_health(node)

                # Check all Iron Legion nodes
                for node in self.iron_legion_nodes:
                    self.check_node_health(node)

                # Check failover conditions
                if self.failover_manager.should_failover_to_iron_legion():
                    if self.failover_manager.current_cluster == "ultron":
                        self.failover_manager.execute_failover()
                        self.stats["failover_count"] += 1
                        logger.warning("🔄 FAILOVER EXECUTED: Using Iron Legion cluster")

                elif self.failover_manager.should_failback_to_ultron():
                    if self.failover_manager.current_cluster == "iron_legion":
                        self.failover_manager.execute_failback()
                        self.stats["failback_count"] += 1
                        logger.info("🔄 FAILBACK EXECUTED: Using ULTRON cluster")

                time.sleep(self.health_check_interval)

            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                time.sleep(self.health_check_interval)

    def start_monitoring(self):
        """Start health monitoring in background"""
        if self.monitoring:
            return

        self.monitor_thread = threading.Thread(target=self.monitor_cluster_health, daemon=True)
        self.monitor_thread.start()
        logger.info("✅ Cluster health monitoring started")

    def stop_monitoring(self):
        """Stop health monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        logger.info("🛑 Cluster health monitoring stopped")

    def get_next_node_round_robin(self) -> Optional[ClusterNode]:
        """Get next node using round-robin from active cluster"""
        # Get active nodes from current cluster
        active_nodes = self.failover_manager.get_active_cluster_nodes()

        if not active_nodes:
            logger.warning("⚠️  No active nodes available")
            return None

        # Round-robin selection
        node = active_nodes[self.round_robin.current_index % len(active_nodes)]
        self.round_robin.current_index += 1
        self.stats["round_robin_rotations"] += 1

        cluster_type = "ultron" if node.cluster_type == "ultron" else "iron_legion"
        if cluster_type == "ultron":
            self.stats["ultron_requests"] += 1
        else:
            self.stats["iron_legion_requests"] += 1

        return node

    def route_request(self, endpoint: str, method: str = "GET", **kwargs) -> Optional[requests.Response]:
        """Route request through round-robin to next available node"""
        node = self.get_next_node_round_robin()

        if not node:
            logger.error("❌ No nodes available for routing")
            return None

        try:
            url = f"{node.endpoint}{endpoint}"
            logger.debug(f"🔄 Routing to {node.name}: {url}")

            self.stats["total_requests"] += 1

            response = requests.request(method, url, timeout=10, **kwargs)
            return response

        except Exception as e:
            logger.error(f"❌ Request failed to {node.name}: {e}")
            node.failure_count += 1
            return None

    def get_cluster_status(self) -> Dict[str, Any]:
        """Get cluster status"""
        healthy_ultron = self.failover_manager.get_healthy_ultron_count()
        healthy_iron_legion = sum(1 for n in self.iron_legion_nodes if n.is_active)

        return {
            "timestamp": datetime.now().isoformat(),
            "current_cluster": self.failover_manager.current_cluster,
            "failover_active": self.failover_manager.failover_active,
            "ultron": {
                "total_nodes": len(self.ultron_nodes),
                "healthy_nodes": healthy_ultron,
                "unhealthy_nodes": len(self.ultron_nodes) - healthy_ultron,
                "health_percent": (healthy_ultron / len(self.ultron_nodes) * 100) if self.ultron_nodes else 0
            },
            "iron_legion": {
                "total_nodes": len(self.iron_legion_nodes),
                "healthy_nodes": healthy_iron_legion,
                "unhealthy_nodes": len(self.iron_legion_nodes) - healthy_iron_legion,
                "health_percent": (healthy_iron_legion / len(self.iron_legion_nodes) * 100) if self.iron_legion_nodes else 0
            },
            "round_robin": {
                "current_index": self.round_robin.current_index,
                "active_nodes": len(self.round_robin.get_all_active_nodes())
            },
            "statistics": self.stats.copy()
        }

    def get_votes(self) -> List[ClusterVote]:
        """Get votes from all 12 ULTRON nodes"""
        votes = []

        for node in self.ultron_nodes:
            vote = ClusterVote(
                node_name=node.name,
                vote=node.is_active,
                timestamp=node.last_health_check or datetime.now(),
                response_time_ms=node.response_time_ms,
                cluster_type="ultron"
            )
            votes.append(vote)

        return votes


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="ULTRON-Iron Legion Virtual Cluster")
    parser.add_argument("--init", action="store_true", help="Initialize cluster nodes")
    parser.add_argument("--monitor", action="store_true", help="Start health monitoring")
    parser.add_argument("--status", action="store_true", help="Show cluster status")
    parser.add_argument("--votes", action="store_true", help="Show ULTRON votes")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon (init + monitor)")

    args = parser.parse_args()

    cluster = ULTRONIronLegionVirtualCluster(project_root)

    if args.init or args.daemon:
        cluster.initialize_ultron_nodes(count=12, distributed=True)  # Distributed across infrastructure
        cluster.initialize_iron_legion_nodes()
        logger.info("✅ Cluster initialization complete")

    if args.monitor or args.daemon:
        cluster.start_monitoring()

        if args.daemon:
            print("🤖 Running as daemon...")
            print("   Press Ctrl+C to stop")
            try:
                while True:
                    time.sleep(60)
                    status = cluster.get_cluster_status()
                    print(f"\n📊 Status: {status['current_cluster']} | "
                          f"ULTRON: {status['ultron']['healthy_nodes']}/12 | "
                          f"Iron Legion: {status['iron_legion']['healthy_nodes']}/7")
            except KeyboardInterrupt:
                cluster.stop_monitoring()
                print("\n🛑 Stopped")

    elif args.status:
        if not cluster.ultron_nodes:
            cluster.initialize_ultron_nodes(count=12)
            cluster.initialize_iron_legion_nodes()

        status = cluster.get_cluster_status()
        print("\n" + "=" * 80)
        print("📊 CLUSTER STATUS")
        print("=" * 80)
        print()
        print(f"Current Cluster: {status['current_cluster'].upper()}")
        print(f"Failover Active: {status['failover_active']}")
        print()
        print(f"ULTRON: {status['ultron']['healthy_nodes']}/{status['ultron']['total_nodes']} healthy "
              f"({status['ultron']['health_percent']:.1f}%)")
        print(f"Iron Legion: {status['iron_legion']['healthy_nodes']}/{status['iron_legion']['total_nodes']} healthy "
              f"({status['iron_legion']['health_percent']:.1f}%)")
        print()
        print(f"Round-Robin: {status['round_robin']['active_nodes']} active nodes")
        print(f"Total Requests: {status['statistics']['total_requests']}")
        print(f"Failovers: {status['statistics']['failover_count']}")
        print(f"Failbacks: {status['statistics']['failback_count']}")
        print()

    elif args.votes:
        if not cluster.ultron_nodes:
            cluster.initialize_ultron_nodes(count=12)

        votes = cluster.get_votes()
        print("\n" + "=" * 80)
        print("🗳️  ULTRON VOTES (12 Nodes)")
        print("=" * 80)
        print()

        healthy = sum(1 for v in votes if v.vote)
        print(f"Healthy: {healthy}/12 ({healthy/12*100:.1f}%)")
        print()

        for vote in votes:
            icon = "✅" if vote.vote else "❌"
            print(f"{icon} {vote.node_name}: {vote.response_time_ms:.1f}ms")
        print()

    else:
        parser.print_help()


if __name__ == "__main__":

    main()