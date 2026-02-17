#!/usr/bin/env python3
"""
JARVIS ULTRON Virtual Hybrid Cluster

Creates a virtual hybrid cluster model that intelligently routes between:
- Laptop ULTRON (localhost:11434)
- KAIJU Iron Legion (<NAS_PRIMARY_IP>:11434)

This provides a single "ULTRON" model that represents the combined cluster.
"""

import sys
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import logging
import time

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISULTRONHybrid")


class ClusterNode(Enum):
    """Cluster node types"""
    ULTRON_LOCAL = "ultron_local"  # Laptop ULTRON
    KAIJU_IRON_LEGION = "kaiju_iron_legion"  # KAIJU NAS


class ULTRONHybridCluster:
    """
    ULTRON Virtual Hybrid Cluster

    Combines laptop ULTRON and KAIJU Iron Legion into a single virtual cluster.
    Provides intelligent routing, load balancing, and failover.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Cluster nodes
        self.nodes = {
            ClusterNode.ULTRON_LOCAL: {
                "name": "ULTRON Local",
                "base_url": "http://localhost:11434",
                "enabled": True,
                "priority": 1,
                "models": ["qwen2.5:72b", "llama3.2:11b", "codellama:13b"],
                "health": False,
                "last_check": None,
                "load": 0,
                "response_time": 0.0
            },
            ClusterNode.KAIJU_IRON_LEGION: {
                "name": "KAIJU",
                "base_url": "http://<NAS_PRIMARY_IP>:11434",
                "enabled": True,
                "priority": 2,
                "models": ["llama3", "codellama:13b"],
                "health": False,
                "last_check": None,
                "load": 0,
                "response_time": 0.0
            }
        }

        # Cluster configuration
        self.config = self._load_config()

        # Routing strategy
        self.routing_strategy = self.config.get("routing_strategy", "load_balanced")

        # Statistics
        self.stats = {
            "total_requests": 0,
            "ultron_local_requests": 0,
            "kaiju_requests": 0,
            "failovers": 0,
            "errors": 0
        }

        # Fencing system integration
        self.fencing_system = None
        self._init_fencing_system()

        # Check health on init
        self._check_cluster_health()

        self.logger.info("✅ ULTRON Virtual Hybrid Cluster initialized")
        self.logger.info(f"   Nodes: {len([n for n in self.nodes.values() if n['health']])}/{len(self.nodes)} healthy")
        if self.fencing_system:
            self.logger.info("   Fencing: Enabled (AIQ + JEDI-COUNCIL)")

    def _init_fencing_system(self):
        """Initialize fencing system for intelligent troubleshooting"""
        try:
            from jarvis_ultron_fencing_system import ULTRONFencingSystem
            self.fencing_system = ULTRONFencingSystem(self.project_root, cluster=self)
            self.logger.info("✅ Fencing system integrated")
        except ImportError:
            self.logger.debug("Fencing system not available")
        except Exception as e:
            self.logger.debug(f"Fencing system error: {e}")

    def _load_config(self) -> Dict[str, Any]:
        """Load cluster configuration"""
        config_file = self.project_root / "config" / "ultron_hybrid_cluster.json"

        default_config = {
            "cluster_name": "ULTRON",
            "routing_strategy": "load_balanced",  # load_balanced, round_robin, priority, adaptive
            "preferred_model": "qwen2.5:72b",
            "timeout": 30,
            "max_retries": 3,
            "health_check_interval": 60,
            "failover_enabled": True,
            "load_balancing": {
                "enabled": True,
                "weight_ultron_local": 1.0,
                "weight_kaiju": 1.0
            }
        }

        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to load config: {e}, using defaults")
        else:
            # Save default config
            try:
                config_file.parent.mkdir(parents=True, exist_ok=True)
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2)
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to save default config: {e}")

        return default_config

    def _check_node_health(self, node: ClusterNode) -> bool:
        """Check health of a cluster node"""
        node_config = self.nodes[node]
        base_url = node_config["base_url"]

        try:
            start_time = time.time()
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            response_time = time.time() - start_time

            if response.status_code == 200:
                node_config["health"] = True
                node_config["last_check"] = datetime.now()
                node_config["response_time"] = response_time
                self.logger.debug(f"   ✅ {node_config['name']} - HEALTHY ({response_time:.2f}s)")
                return True
            else:
                node_config["health"] = False
                self.logger.debug(f"   ❌ {node_config['name']} - Unhealthy (HTTP {response.status_code})")
                return False
        except Exception as e:
            node_config["health"] = False
            self.logger.debug(f"   ❌ {node_config['name']} - Unavailable: {e}")
            return False

    def _check_cluster_health(self):
        """Check health of all cluster nodes with fencing integration"""
        self.logger.info("🔍 Checking ULTRON Hybrid Cluster health...")

        for node in ClusterNode:
            self._check_node_health(node)

        healthy_nodes = [n for n in self.nodes.values() if n['health']]
        self.logger.info(f"   Cluster Status: {len(healthy_nodes)}/{len(self.nodes)} nodes healthy")

        # Use fencing system for intelligent monitoring and decision-making
        if self.fencing_system:
            try:
                fencing_results = self.fencing_system.monitor_and_fence()
                if fencing_results.get("nodes_fenced", 0) > 0:
                    self.logger.warning(f"   ⚠️  {fencing_results['nodes_fenced']} node(s) fenced via AIQ/JEDI-COUNCIL decision")
            except Exception as e:
                self.logger.debug(f"Fencing monitor error: {e}")

    def get_available_nodes(self) -> List[ClusterNode]:
        """Get list of available nodes, ordered by priority"""
        available = []

        for node in ClusterNode:
            if self.nodes[node]["health"]:
                available.append(node)

        # Sort by priority
        available.sort(key=lambda n: self.nodes[n]["priority"])

        return available

    def select_node(self, strategy: Optional[str] = None) -> Optional[ClusterNode]:
        """
        Select best node based on routing strategy

        Strategies:
        - load_balanced: Select node with lowest load
        - round_robin: Alternate between nodes
        - priority: Always use highest priority available
        - adaptive: Learn from response times
        """
        if strategy is None:
            strategy = self.routing_strategy

        available = self.get_available_nodes()

        if not available:
            return None

        if strategy == "priority":
            # Always use highest priority (first in list)
            return available[0]

        elif strategy == "load_balanced":
            # Select node with lowest load
            best_node = min(available, key=lambda n: self.nodes[n]["load"])
            return best_node

        elif strategy == "round_robin":
            # Alternate between nodes (simple round-robin)
            # For now, just use priority order
            return available[self.stats["total_requests"] % len(available)]

        elif strategy == "adaptive":
            # Select node with best response time
            best_node = min(available, key=lambda n: self.nodes[n]["response_time"])
            return best_node

        else:
            # Default to priority
            return available[0]

    def route_request(self, prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Route request through ULTRON hybrid cluster

        This is the main entry point - provides a single "ULTRON" model
        that intelligently routes between laptop and KAIJU.
        """
        self.logger.info("📤 Routing request through ULTRON Hybrid Cluster...")

        # Select best node
        selected_node = self.select_node()

        if not selected_node:
            self.logger.error("❌ No healthy nodes available in ULTRON cluster!")
            self.stats["errors"] += 1
            return {
                "success": False,
                "error": "No healthy nodes available in ULTRON cluster",
                "cluster": "ULTRON",
                "node": None
            }

        node_config = self.nodes[selected_node]
        self.logger.info(f"   Selected: {node_config['name']} ({selected_node.value})")

        # Try selected node
        result = self._send_request(selected_node, prompt, model)

        if result["success"]:
            # Update stats
            self.stats["total_requests"] += 1
            if selected_node == ClusterNode.ULTRON_LOCAL:
                self.stats["ultron_local_requests"] += 1
            else:
                self.stats["kaiju_requests"] += 1

            # Decrease load
            node_config["load"] = max(0, node_config["load"] - 1)

            return result

        # If selected node failed, try failover
        if self.config.get("failover_enabled", True):
            self.logger.warning(f"   ⚠️  {node_config['name']} failed, attempting failover...")
            self.stats["failovers"] += 1

            available = self.get_available_nodes()
            # Remove the failed node
            available = [n for n in available if n != selected_node]

            if available:
                failover_node = available[0]
                self.logger.info(f"   Failover to: {self.nodes[failover_node]['name']}")
                result = self._send_request(failover_node, prompt, model)

                if result["success"]:
                    self.stats["total_requests"] += 1
                    if failover_node == ClusterNode.ULTRON_LOCAL:
                        self.stats["ultron_local_requests"] += 1
                    else:
                        self.stats["kaiju_requests"] += 1

                return result

        # All nodes failed
        self.stats["errors"] += 1
        self.logger.error("❌ All ULTRON cluster nodes failed!")
        return {
            "success": False,
            "error": "All ULTRON cluster nodes failed",
            "cluster": "ULTRON",
            "node": None
        }

    def _send_request(self, node: ClusterNode, prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        """Send request to specific node"""
        node_config = self.nodes[node]
        base_url = node_config["base_url"]

        # Select model
        if not model:
            model = node_config.get("models", [None])[0] or self.config.get("preferred_model", "qwen2.5:72b")

        # Increase load
        node_config["load"] += 1

        try:
            start_time = time.time()
            response = requests.post(
                f"{base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=self.config.get("timeout", 30)
            )
            response_time = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                node_config["response_time"] = response_time

                return {
                    "success": True,
                    "cluster": "ULTRON",
                    "node": node.value,
                    "node_name": node_config["name"],
                    "response": data.get("response", ""),
                    "model": model,
                    "base_url": base_url,
                    "response_time": response_time
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "cluster": "ULTRON",
                    "node": node.value
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "cluster": "ULTRON",
                "node": node.value
            }
        finally:
            # Decrease load
            node_config["load"] = max(0, node_config["load"] - 1)

    def get_cluster_status(self) -> Dict[str, Any]:
        """Get cluster status and statistics"""
        healthy_nodes = [n for n in self.nodes.values() if n['health']]

        return {
            "cluster_name": "ULTRON",
            "cluster_type": "virtual_hybrid",
            "nodes": {
                node.value: {
                    "name": config["name"],
                    "health": config["health"],
                    "load": config["load"],
                    "response_time": config["response_time"],
                    "last_check": config["last_check"].isoformat() if config["last_check"] else None
                }
                for node, config in self.nodes.items()
            },
            "healthy_nodes": len(healthy_nodes),
            "total_nodes": len(self.nodes),
            "routing_strategy": self.routing_strategy,
            "statistics": self.stats.copy()
        }

    def register_as_cursor_model(self) -> Dict[str, Any]:
        """
        Register ULTRON as a Cursor model configuration

        Returns configuration that can be added to .cursor/settings.json
        """
        return {
            "title": "ULTRON",
            "name": "ULTRON",
            "provider": "ollama",
            "model": self.config.get("preferred_model", "qwen2.5:72b"),
            "apiBase": "http://localhost:11434",  # Primary endpoint (will route internally)
            "contextLength": 32768,
            "description": "ULTRON Virtual Hybrid Cluster - Laptop ULTRON + KAIJU Iron Legion",
            "cluster": {
                "type": "virtual_hybrid",
                "nodes": [
                    {
                        "name": "ULTRON Local",
                        "endpoint": "http://localhost:11434",
                        "priority": 1
                    },
                    {
                        "name": "KAIJU",
                        "endpoint": "http://<NAS_PRIMARY_IP>:11434",
                        "priority": 2
                    }
                ],
                "routing": self.routing_strategy
            }
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="ULTRON Virtual Hybrid Cluster")
        parser.add_argument("--health", action="store_true", help="Check cluster health")
        parser.add_argument("--status", action="store_true", help="Get cluster status")
        parser.add_argument("--test", type=str, help="Test with a prompt")
        parser.add_argument("--register", action="store_true", help="Generate Cursor model config")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        cluster = ULTRONHybridCluster(project_root)

        if args.health:
            cluster._check_cluster_health()
            print("\n📊 Cluster Health:")
            for node, config in cluster.nodes.items():
                status = "✅ HEALTHY" if config["health"] else "❌ UNAVAILABLE"
                print(f"   {config['name']}: {status}")

        elif args.status:
            status = cluster.get_cluster_status()
            import json
            print(json.dumps(status, indent=2, default=str))

        elif args.test:
            result = cluster.route_request(args.test)
            if result["success"]:
                print(f"\n✅ Response from {result['node_name']} ({result['node']}):")
                print(result["response"][:500])
            else:
                print(f"\n❌ Error: {result.get('error')}")

        elif args.register:
            import json as json_module
            config = cluster.register_as_cursor_model()
            print("\n📝 ULTRON Cursor Model Configuration:")
            print(json_module.dumps(config, indent=2))
            print("\n💡 Add this to .cursor/settings.json under cursor.composer.customModels or cursor.agent.customModels")

        else:
            print("Usage:")
            print("  --health          : Check cluster health")
            print("  --status          : Get cluster status")
            print("  --test 'prompt'   : Test with a prompt")
            print("  --register        : Generate Cursor model config")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()