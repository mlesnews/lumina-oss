#!/usr/bin/env python3
"""
Iron Legion Failover Router
Routes requests between Iron Legion and MILLENNIUM_FALCON with failover

Tags: #IRON_LEGION #FAILOVER #MILLENNIUM_FALCON #ULTRON @JARVIS @LUMINA @DOIT
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import requests

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
config_path = project_root / "config" / "iron_legion_cluster_config.json"


@dataclass
class ClusterStatus:
    """Cluster status information"""
    name: str
    endpoint: str
    healthy: bool
    response_time: float
    available_models: list


class IronLegionFailoverRouter:
    """Router with failover between Iron Legion and MILLENNIUM_FALCON"""

    def __init__(self, config_path: Path = config_path):
        """Initialize router"""
        self.config_path = config_path
        self.config = self._load_config()
        self.failover_config = self.config.get("failover_config", {})
        self.ultron_config = self.config.get("ultron_integration", {})

    def _load_config(self) -> Dict:
        """Load configuration"""
        try:
            with open(self.config_path, encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Error loading config: {e}")
            return {}

    def check_cluster_health(self, endpoint: str, timeout: int = 5) -> ClusterStatus:
        """Check if cluster is healthy"""
        try:
            # Try health endpoint first
            health_url = f"{endpoint}/health" if not endpoint.endswith("/health") else endpoint
            start_time = requests.get(health_url, timeout=timeout).elapsed.total_seconds()

            return ClusterStatus(
                name="cluster",
                endpoint=endpoint,
                healthy=True,
                response_time=start_time,
                available_models=[]
            )
        except:
            # Try root endpoint
            try:
                response = requests.get(endpoint, timeout=timeout)
                return ClusterStatus(
                    name="cluster",
                    endpoint=endpoint,
                    healthy=response.status_code == 200,
                    response_time=response.elapsed.total_seconds(),
                    available_models=[]
                )
            except:
                return ClusterStatus(
                    name="cluster",
                    endpoint=endpoint,
                    healthy=False,
                    response_time=999.0,
                    available_models=[]
                )

    def select_cluster(self, prefer_iron_legion: bool = True) -> Dict:
        """Select cluster with failover"""
        primary = self.failover_config.get("primary", {})
        secondary = self.failover_config.get("secondary", {})

        if prefer_iron_legion:
            # Check Iron Legion first
            iron_legion_status = self.check_cluster_health(primary.get("endpoint", ""))
            if iron_legion_status.healthy:
                return {
                    "cluster": "iron_legion",
                    "endpoint": primary.get("endpoint", ""),
                    "status": "primary",
                    "healthy": True
                }

            # Fallback to MILLENNIUM_FALCON
            falcon_status = self.check_cluster_health(secondary.get("endpoint", ""))
            if falcon_status.healthy:
                return {
                    "cluster": "millennium_falcon",
                    "endpoint": secondary.get("endpoint", ""),
                    "status": "failover",
                    "healthy": True
                }
        else:
            # Prefer MILLENNIUM_FALCON
            falcon_status = self.check_cluster_health(secondary.get("endpoint", ""))
            if falcon_status.healthy:
                return {
                    "cluster": "millennium_falcon",
                    "endpoint": secondary.get("endpoint", ""),
                    "status": "primary",
                    "healthy": True
                }

            # Fallback to Iron Legion
            iron_legion_status = self.check_cluster_health(primary.get("endpoint", ""))
            if iron_legion_status.healthy:
                return {
                    "cluster": "iron_legion",
                    "endpoint": primary.get("endpoint", ""),
                    "status": "failover",
                    "healthy": True
                }

        return {
            "cluster": None,
            "endpoint": None,
            "status": "unavailable",
            "healthy": False
        }

    def route_request(self, prompt: str, cluster_preference: Optional[str] = None) -> Dict:
        """Route request to appropriate cluster"""
        if cluster_preference == "iron_legion":
            selection = self.select_cluster(prefer_iron_legion=True)
        elif cluster_preference == "millennium_falcon":
            selection = self.select_cluster(prefer_iron_legion=False)
        else:
            # Auto-select based on health
            selection = self.select_cluster(prefer_iron_legion=True)

        if not selection["healthy"]:
            return {
                "success": False,
                "error": "No healthy clusters available",
                "selection": selection
            }

        # Make request to selected cluster
        try:
            url = f"{selection['endpoint']}/v1/chat/completions"
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
                    "cluster": selection["cluster"],
                    "status": selection["status"],
                    "response": data.get("choices", [{}])[0].get("message", {}).get("content", ""),
                    "full_response": data
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "cluster": selection["cluster"]
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "cluster": selection["cluster"]
            }

    def get_cluster_status(self) -> Dict:
        """Get status of all clusters"""
        primary = self.failover_config.get("primary", {})
        secondary = self.failover_config.get("secondary", {})

        iron_legion_status = self.check_cluster_health(primary.get("endpoint", ""))
        falcon_status = self.check_cluster_health(secondary.get("endpoint", ""))

        return {
            "iron_legion": {
                "name": primary.get("name", "Iron Legion"),
                "endpoint": primary.get("endpoint", ""),
                "healthy": iron_legion_status.healthy,
                "response_time": iron_legion_status.response_time
            },
            "millennium_falcon": {
                "name": secondary.get("name", "MILLENNIUM_FALCON"),
                "endpoint": secondary.get("endpoint", ""),
                "healthy": falcon_status.healthy,
                "response_time": falcon_status.response_time
            }
        }


def main():
    """Test the failover router"""
    import argparse

    parser = argparse.ArgumentParser(description="Iron Legion Failover Router")
    parser.add_argument("--status", action="store_true", help="Show cluster status")
    parser.add_argument("--test", action="store_true", help="Test failover")
    parser.add_argument("--prefer", choices=["iron_legion", "millennium_falcon"], help="Prefer specific cluster")

    args = parser.parse_args()

    router = IronLegionFailoverRouter()

    if args.status:
        print("\n🔍 Cluster Status:\n")
        status = router.get_cluster_status()
        for cluster_name, info in status.items():
            health = "✅" if info["healthy"] else "❌"
            print(f"{health} {info['name']}: {info['endpoint']}")
            if info["healthy"]:
                print(f"   Response time: {info['response_time']:.2f}s")
        return

    if args.test:
        print("\n🧪 Testing failover routing...\n")
        selection = router.select_cluster(prefer_iron_legion=(args.prefer != "millennium_falcon"))
        print(f"Selected: {selection['cluster']} ({selection['status']})")
        print(f"Endpoint: {selection['endpoint']}")
        print(f"Healthy: {selection['healthy']}")
        return

    print("Usage: python iron_legion_failover_router.py --status")
    print("       python iron_legion_failover_router.py --test")
    print("       python iron_legion_failover_router.py --test --prefer millennium_falcon")


if __name__ == "__main__":


    main()