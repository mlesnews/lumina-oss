#!/usr/bin/env python3
"""
🤖 ULTRON Cluster Router

Routes AI requests across the ULTRON virtual cluster:
- MILLENNIUM-FALC (laptop)
- KAIJU (NAS)
- Iron Legion (future cluster nodes)

Integrates with Azure AI Foundry for model management and testing.
"""

import sys
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("ULTRONClusterRouter")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ULTRONClusterRouter")


class NodeType(Enum):
    LAPTOP = "laptop"
    NAS = "nas"
    CLUSTER = "cluster"


@dataclass
class ClusterNode:
    """A node in the ULTRON cluster"""
    name: str
    node_type: NodeType
    endpoint: str
    models: List[str]
    is_online: bool = False
    latency_ms: float = 0.0


class ULTRONClusterRouter:
    """
    Routes requests across the ULTRON virtual cluster.

    CORRECTED ARCHITECTURE:
    - MILLENNIUM-FALC: Laptop with RTX 5090 Mobile (24GB VRAM)
    - IRON LEGION (KAIJU): 7-node cluster on <NAS_IP> with RTX 3090 (24GB VRAM)
      - Mark I (port 3001): CodeLlama:13b - Code Expert
      - Mark II (port 3002): Llama3.2:11b - General (restarting)
      - Mark III (port 3003): Qwen2.5-coder:1.5b - Quick Response (restarting)
      - Mark IV (port 3004): Llama3:8b - Balanced
      - Mark V (port 3005): Mistral:7b - Reasoning
      - Mark VI (port 3006): Mixtral:8x7b - Complex (restarting)
      - Mark VII (port 3007): Gemma:2b - Fallback (restarting)
    - NAS: Synology storage with lightweight Ollama (CPU-only)
    """

    def __init__(self):
        self.nodes: Dict[str, ClusterNode] = {
            # Primary laptop node
            "millennium_falc": ClusterNode(
                name="MILLENNIUM-FALC",
                node_type=NodeType.LAPTOP,
                endpoint="http://localhost:11434",
                models=[]
            ),
            # Iron Legion 7-node cluster (KAIJU @ <NAS_IP>)
            "iron_legion_mark_i": ClusterNode(
                name="IRON-LEGION-MARK-I",
                node_type=NodeType.CLUSTER,
                endpoint="http://<NAS_IP>:3001",
                models=["codellama:13b"]
            ),
            "iron_legion_mark_iv": ClusterNode(
                name="IRON-LEGION-MARK-IV",
                node_type=NodeType.CLUSTER,
                endpoint="http://<NAS_IP>:3004",
                models=["llama3:8b"]
            ),
            "iron_legion_mark_v": ClusterNode(
                name="IRON-LEGION-MARK-V",
                node_type=NodeType.CLUSTER,
                endpoint="http://<NAS_IP>:3005",
                models=["mistral:7b"]
            ),
            # NAS for lightweight/backup
            "nas": ClusterNode(
                name="NAS",
                node_type=NodeType.NAS,
                endpoint="http://<NAS_PRIMARY_IP>:11434",
                models=[]
            )
        }

        self.default_node = "millennium_falc"
        self.fallback_node = "iron_legion_mark_v"  # Iron Legion as primary fallback

        logger.info("🤖 ULTRON Cluster Router initialized")
        logger.info("   📍 MILLENNIUM-FALC: RTX 5090 Mobile (24GB)")
        logger.info("   🦾 IRON LEGION: RTX 3090 (24GB) - 7 nodes @ <NAS_IP>")

    def health_check(self) -> Dict[str, Any]:
        """Check health of all nodes"""
        results = {}

        for node_id, node in self.nodes.items():
            try:
                start = datetime.now()
                response = requests.get(
                    f"{node.endpoint}/api/tags",
                    timeout=5
                )
                latency = (datetime.now() - start).total_seconds() * 1000

                if response.status_code == 200:
                    data = response.json()
                    node.is_online = True
                    node.latency_ms = latency
                    node.models = [m["name"] for m in data.get("models", [])]

                    results[node_id] = {
                        "name": node.name,
                        "status": "online",
                        "latency_ms": round(latency, 1),
                        "models": node.models,
                        "model_count": len(node.models)
                    }
                else:
                    node.is_online = False
                    results[node_id] = {
                        "name": node.name,
                        "status": "error",
                        "error": f"HTTP {response.status_code}"
                    }

            except requests.exceptions.Timeout:
                node.is_online = False
                results[node_id] = {
                    "name": node.name,
                    "status": "timeout"
                }
            except requests.exceptions.ConnectionError:
                node.is_online = False
                results[node_id] = {
                    "name": node.name,
                    "status": "offline"
                }
            except Exception as e:
                node.is_online = False
                results[node_id] = {
                    "name": node.name,
                    "status": "error",
                    "error": str(e)
                }

        return results

    def get_best_node_for_model(self, model: str) -> Optional[str]:
        """Find the best node that has a specific model"""
        # Refresh health
        self.health_check()

        # Check primary node first
        if self.nodes[self.default_node].is_online:
            if model in self.nodes[self.default_node].models:
                return self.default_node

        # Check fallback
        if self.nodes[self.fallback_node].is_online:
            if model in self.nodes[self.fallback_node].models:
                return self.fallback_node

        # Check all nodes
        for node_id, node in self.nodes.items():
            if node.is_online and model in node.models:
                return node_id

        return None

    def route_request(
        self,
        prompt: str,
        model: Optional[str] = None,
        prefer_speed: bool = False,
        prefer_quality: bool = False
    ) -> Dict[str, Any]:
        """
        Route a request to the best available node.

        Args:
            prompt: The prompt to send
            model: Specific model to use (optional)
            prefer_speed: Prefer faster models/nodes
            prefer_quality: Prefer higher quality models

        Returns:
            Response from the selected node
        """
        # Refresh cluster status
        health = self.health_check()

        # Model selection logic
        if model:
            target_node = self.get_best_node_for_model(model)
            if not target_node:
                return {"error": f"Model {model} not found on any online node"}
        else:
            # Auto-select model based on preferences
            if prefer_speed:
                model = "smollm:135m"  # Fastest
            elif prefer_quality:
                model = "codellama:13b"  # Best quality
            else:
                model = "mistral:latest"  # Balanced

            target_node = self.get_best_node_for_model(model)

            if not target_node:
                # Fallback to any available model
                for node_id, node in self.nodes.items():
                    if node.is_online and node.models:
                        target_node = node_id
                        model = node.models[0]
                        break

        if not target_node:
            return {"error": "No online nodes available"}

        # Send request
        node = self.nodes[target_node]
        try:
            response = requests.post(
                f"{node.endpoint}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "response": data.get("response", ""),
                    "model": model,
                    "node": node.name,
                    "eval_duration_ms": data.get("eval_duration", 0) / 1_000_000,
                    "tokens_per_second": data.get("eval_count", 0) / (data.get("eval_duration", 1) / 1_000_000_000)
                }
            else:
                return {"error": f"Request failed: HTTP {response.status_code}"}

        except Exception as e:
            return {"error": f"Request error: {e}"}

    def get_cluster_status(self) -> Dict[str, Any]:
        """Get full cluster status"""
        health = self.health_check()

        total_models = set()
        online_nodes = 0

        for node_id, status in health.items():
            if status.get("status") == "online":
                online_nodes += 1
                total_models.update(status.get("models", []))

        return {
            "cluster_name": "ULTRON",
            "timestamp": datetime.now().isoformat(),
            "nodes_online": online_nodes,
            "nodes_total": len(self.nodes),
            "unique_models": len(total_models),
            "model_list": sorted(list(total_models)),
            "nodes": health
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="ULTRON Cluster Router")
        parser.add_argument("--status", action="store_true", help="Show cluster status")
        parser.add_argument("--health", action="store_true", help="Run health check")
        parser.add_argument("--query", type=str, help="Send a query to the cluster")
        parser.add_argument("--model", type=str, help="Specific model to use")
        parser.add_argument("--fast", action="store_true", help="Prefer speed")
        parser.add_argument("--quality", action="store_true", help="Prefer quality")

        args = parser.parse_args()

        router = ULTRONClusterRouter()

        if args.status:
            status = router.get_cluster_status()
            print("\n" + "=" * 80)
            print("🤖 ULTRON CLUSTER STATUS")
            print("=" * 80)
            print(f"Nodes Online: {status['nodes_online']}/{status['nodes_total']}")
            print(f"Unique Models: {status['unique_models']}")
            print(f"\nModels Available:")
            for model in status['model_list']:
                print(f"  - {model}")
            print(f"\nNode Details:")
            for node_id, node_status in status['nodes'].items():
                icon = "✅" if node_status.get("status") == "online" else "❌"
                print(f"  {icon} {node_status['name']}: {node_status.get('status', 'unknown')}")
                if node_status.get("latency_ms"):
                    print(f"     Latency: {node_status['latency_ms']}ms")
                if node_status.get("models"):
                    print(f"     Models: {', '.join(node_status['models'])}")
            print("=" * 80)

        elif args.health:
            health = router.health_check()
            print(json.dumps(health, indent=2))

        elif args.query:
            result = router.route_request(
                prompt=args.query,
                model=args.model,
                prefer_speed=args.fast,
                prefer_quality=args.quality
            )
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"\n📍 Node: {result['node']}")
                print(f"🤖 Model: {result['model']}")
                print(f"⚡ Speed: {result.get('tokens_per_second', 0):.1f} tokens/sec")
                print(f"\n{result['response']}")

        else:
            # Default: show status
            status = router.get_cluster_status()
            print(f"\n🤖 ULTRON Cluster: {status['nodes_online']}/{status['nodes_total']} nodes online")
            print(f"   Models: {status['unique_models']} available")
            print("\nUse --status for details, --query 'prompt' to send requests")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()