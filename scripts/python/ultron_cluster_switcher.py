#!/usr/bin/env python3
"""
ULTRON Cluster Switcher
Allows ULTRON to swap between Iron Legion, MILLENNIUM_FALCON, and standalone

Tags: #ULTRON #CLUSTER_SWITCHER #IRON_LEGION #MILLENNIUM_FALCON @JARVIS @LUMINA @DOIT
"""

import json
from pathlib import Path
from typing import Dict, Optional

import requests

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
config_path = project_root / "config" / "ultron_cluster_selection.json"


class ULTRONClusterSwitcher:
    """Switch ULTRON between different clusters"""

    def __init__(self, config_path: Path = config_path):
        """Initialize switcher"""
        self.config_path = config_path
        self.config = self._load_config()
        self.clusters = self.config.get("available_clusters", {})
        self.current_cluster = self.config.get("ultron_config", {}).get("default_cluster", "iron_legion")

    def _load_config(self) -> Dict:
        """Load configuration"""
        try:
            with open(self.config_path, encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Error loading config: {e}")
            return {}

    def get_cluster_info(self, cluster_name: str) -> Optional[Dict]:
        """Get cluster information"""
        return self.clusters.get(cluster_name)

    def check_cluster_health(self, cluster_name: str) -> bool:
        """Check if cluster is healthy"""
        cluster = self.get_cluster_info(cluster_name)
        if not cluster:
            return False

        endpoint = cluster.get("endpoint", "")
        try:
            response = requests.get(f"{endpoint}/health", timeout=5)
            return response.status_code == 200
        except:
            try:
                response = requests.get(endpoint, timeout=5)
                return response.status_code == 200
            except:
                return False

    def switch_to_cluster(self, cluster_name: str) -> Dict:
        """Switch ULTRON to use specified cluster"""
        cluster = self.get_cluster_info(cluster_name)
        if not cluster:
            return {
                "success": False,
                "error": f"Cluster '{cluster_name}' not found"
            }

        # Check health
        is_healthy = self.check_cluster_health(cluster_name)

        self.current_cluster = cluster_name

        return {
            "success": True,
            "cluster": cluster_name,
            "endpoint": cluster.get("endpoint", ""),
            "healthy": is_healthy,
            "description": cluster.get("description", "")
        }

    def get_available_clusters(self) -> Dict:
        """Get list of available clusters with status"""
        available = {}
        for name, info in self.clusters.items():
            is_healthy = self.check_cluster_health(name)
            available[name] = {
                "name": info.get("name", name),
                "endpoint": info.get("endpoint", ""),
                "healthy": is_healthy,
                "type": info.get("type", ""),
                "models": info.get("models", 0)
            }
        return available

    def route_request(self, prompt: str, cluster_name: Optional[str] = None) -> Dict:
        """Route request through selected cluster"""
        if cluster_name:
            switch_result = self.switch_to_cluster(cluster_name)
            if not switch_result["success"]:
                return switch_result
        else:
            # Use current cluster
            cluster = self.get_cluster_info(self.current_cluster)
            if not cluster:
                return {"success": False, "error": "No cluster selected"}

        cluster = self.get_cluster_info(self.current_cluster)
        endpoint = cluster.get("endpoint", "")

        try:
            # Try expert router if Iron Legion
            if self.current_cluster == "iron_legion":
                url = f"{endpoint}/expert"
            else:
                url = f"{endpoint}/v1/chat/completions"

            payload = {
                "model": "default",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
                "stream": False
            }

            response = requests.post(url, json=payload, timeout=60)

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "cluster": self.current_cluster,
                    "response": data.get("choices", [{}])[0].get("message", {}).get("content", ""),
                    "full_response": data
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "cluster": self.current_cluster
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "cluster": self.current_cluster
            }


def main():
    """Test the cluster switcher"""
    import argparse

    parser = argparse.ArgumentParser(description="ULTRON Cluster Switcher")
    parser.add_argument("--list", action="store_true", help="List available clusters")
    parser.add_argument("--switch", help="Switch to cluster (iron_legion, millennium_falcon, ultron_standalone)")
    parser.add_argument("--test", help="Test cluster with prompt")

    args = parser.parse_args()

    switcher = ULTRONClusterSwitcher()

    if args.list:
        print("\n🔍 Available Clusters:\n")
        clusters = switcher.get_available_clusters()
        for name, info in clusters.items():
            health = "✅" if info["healthy"] else "❌"
            print(f"{health} {info['name']} ({name})")
            print(f"   Endpoint: {info['endpoint']}")
            print(f"   Type: {info['type']}")
            print(f"   Models: {info['models']}\n")
        return

    if args.switch:
        result = switcher.switch_to_cluster(args.switch)
        if result["success"]:
            print(f"\n✅ Switched to: {result['cluster']}")
            print(f"   Endpoint: {result['endpoint']}")
            print(f"   Healthy: {result['healthy']}")
        else:
            print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
        return

    if args.test:
        result = switcher.route_request(args.test)
        if result["success"]:
            print(f"\n✅ Response from {result['cluster']}:")
            print(result["response"])
        else:
            print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
        return

    print("Usage: python ultron_cluster_switcher.py --list")
    print("       python ultron_cluster_switcher.py --switch iron_legion")
    print("       python ultron_cluster_switcher.py --test 'Hello from ULTRON'")


if __name__ == "__main__":


    main()