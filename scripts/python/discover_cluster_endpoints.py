#!/usr/bin/env python3
"""
Automated Cluster Endpoint Discovery System

Automatically discovers available Ollama instances and AI model endpoints
on the local network and updates the endpoint registry.

Tags: #DISCOVERY #ENDPOINTS #NETWORK #AUTOMATION @JARVIS @LUMINA
"""

import ipaddress
import json
import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("discover_cluster_endpoints")


@dataclass
class DiscoveredEndpoint:
    """Represents a discovered endpoint"""

    url: str
    host: str
    port: int
    type: str  # "ollama", "router", "unknown"
    status: str  # "operational", "degraded", "offline"
    models: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    response_time_ms: Optional[float] = None
    error: Optional[str] = None


class EndpointDiscovery:
    """Discovers AI model endpoints on the network"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.registry_path = project_root / "config" / "cluster_endpoint_registry.json"
        self.discovered_endpoints: List[DiscoveredEndpoint] = []

    def get_local_network_range(self) -> List[str]:
        """Get local network IP range"""
        try:
            # Get local IP
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)

            # Parse network range (assuming /24 subnet)
            ip_obj = ipaddress.IPv4Address(local_ip)
            network = ipaddress.IPv4Network(f"{ip_obj}/24", strict=False)

            # Generate IP list
            ip_list = [str(ip) for ip in network.hosts()]
            return ip_list
        except Exception as e:
            logger.warning(f"Failed to determine network range: {e}")
            # Fallback to common ranges
            return [
                "127.0.0.1",
                "localhost",
                "<NAS_IP>",
                "<NAS_PRIMARY_IP>",
                "<NAS_IP>",
                "<NAS_IP>",
            ]

    def check_port_open(self, host: str, port: int, timeout: float = 2.0) -> bool:
        """Check if a port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def discover_ollama_endpoint(self, host: str, port: int) -> Optional[DiscoveredEndpoint]:
        """Discover Ollama endpoint"""
        url = f"http://{host}:{port}"

        # Check if port is open
        if not self.check_port_open(host, port):
            return None

        try:
            # Try Ollama API endpoints
            start_time = datetime.now()

            # Try /api/tags first
            try:
                response = requests.get(f"{url}/api/tags", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    models = [model.get("name", "") for model in data.get("models", [])]

                    response_time = (datetime.now() - start_time).total_seconds() * 1000

                    return DiscoveredEndpoint(
                        url=url,
                        host=host,
                        port=port,
                        type="ollama",
                        status="operational",
                        models=models,
                        capabilities=["chat", "completion", "code"],
                        response_time_ms=response_time,
                    )
            except requests.exceptions.RequestException:
                pass

            # Try /v1/models (OpenAI-compatible)
            try:
                response = requests.get(f"{url}/v1/models", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    models = [model.get("id", "") for model in data.get("data", [])]

                    response_time = (datetime.now() - start_time).total_seconds() * 1000

                    return DiscoveredEndpoint(
                        url=url,
                        host=host,
                        port=port,
                        type="openai_compatible",
                        status="operational",
                        models=models,
                        capabilities=["chat", "completion"],
                        response_time_ms=response_time,
                    )
            except requests.exceptions.RequestException:
                pass

            # Port is open but not responding to known endpoints
            return DiscoveredEndpoint(
                url=url,
                host=host,
                port=port,
                type="unknown",
                status="degraded",
                error="Port open but not responding to known API endpoints",
            )

        except Exception as e:
            return DiscoveredEndpoint(
                url=url, host=host, port=port, type="unknown", status="offline", error=str(e)
            )

    def discover_router_endpoint(self, host: str, port: int) -> Optional[DiscoveredEndpoint]:
        """Discover ULTRON router endpoint"""
        url = f"http://{host}:{port}"

        if not self.check_port_open(host, port):
            return None

        try:
            start_time = datetime.now()
            response = requests.get(f"{url}/health", timeout=5)

            if response.status_code == 200:
                data = response.json()
                response_time = (datetime.now() - start_time).total_seconds() * 1000

                return DiscoveredEndpoint(
                    url=url,
                    host=host,
                    port=port,
                    type="router",
                    status="operational",
                    capabilities=["routing", "load_balancing", "health_monitoring"],
                    response_time_ms=response_time,
                )
        except Exception:
            pass

        return None

    def discover_localhost_endpoints(self) -> List[DiscoveredEndpoint]:
        """Discover endpoints on localhost"""
        endpoints = []

        # Common ports to check
        ports_to_check = [
            11434,  # Standard Ollama
            11437,  # KAIJU Ollama
            8080,  # ULTRON Router
            3001,  # Iron Legion Mark I
            3002,  # Iron Legion Mark II
            3003,  # Iron Legion Mark III
            3004,  # Iron Legion Mark IV
            3005,  # Iron Legion Mark V
            3006,  # Iron Legion Mark VI
            3007,  # Iron Legion Mark VII
            11435,  # Port forwarded
        ]

        for port in ports_to_check:
            # Try Ollama endpoint
            endpoint = self.discover_ollama_endpoint("localhost", port)
            if endpoint:
                endpoints.append(endpoint)
                continue

            # Try router endpoint
            endpoint = self.discover_router_endpoint("localhost", port)
            if endpoint:
                endpoints.append(endpoint)

        return endpoints

    def discover_network_endpoints(self, network_range: List[str]) -> List[DiscoveredEndpoint]:
        """Discover endpoints on network"""
        endpoints = []

        ports_to_check = [11434, 11437, 8080]

        def check_endpoint(host: str, port: int):
            endpoint = self.discover_ollama_endpoint(host, port)
            if endpoint:
                return endpoint
            return self.discover_router_endpoint(host, port)

        # Use thread pool for parallel discovery
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = []
            for host in network_range:
                for port in ports_to_check:
                    futures.append(executor.submit(check_endpoint, host, port))

            for future in as_completed(futures):
                try:
                    endpoint = future.result()
                    if endpoint and endpoint.status == "operational":
                        endpoints.append(endpoint)
                except Exception as e:
                    logger.debug(f"Discovery error: {e}")

        return endpoints

    def discover_all(self, scan_network: bool = True) -> List[DiscoveredEndpoint]:
        """Discover all endpoints"""
        logger.info("Starting endpoint discovery...")

        # Discover localhost endpoints
        logger.info("Scanning localhost endpoints...")
        localhost_endpoints = self.discover_localhost_endpoints()
        self.discovered_endpoints.extend(localhost_endpoints)
        logger.info(f"Found {len(localhost_endpoints)} localhost endpoints")

        if scan_network:
            # Discover network endpoints
            logger.info("Scanning network endpoints...")
            network_range = self.get_local_network_range()
            logger.info(f"Scanning {len(network_range)} IP addresses...")

            network_endpoints = self.discover_network_endpoints(network_range)
            self.discovered_endpoints.extend(network_endpoints)
            logger.info(f"Found {len(network_endpoints)} network endpoints")

        # Remove duplicates
        seen_urls = set()
        unique_endpoints = []
        for endpoint in self.discovered_endpoints:
            if endpoint.url not in seen_urls:
                seen_urls.add(endpoint.url)
                unique_endpoints.append(endpoint)

        self.discovered_endpoints = unique_endpoints
        logger.info(f"Total unique endpoints discovered: {len(self.discovered_endpoints)}")

        return self.discovered_endpoints

    def update_registry(self, merge: bool = True) -> Dict[str, Any]:
        """Update endpoint registry with discovered endpoints"""
        if not self.registry_path.exists():
            logger.error("Registry file not found")
            return {}

        with open(self.registry_path, encoding="utf-8") as f:
            registry = json.load(f)

        endpoints = registry.get("endpoints", {})

        for discovered in self.discovered_endpoints:
            if discovered.status != "operational":
                continue

            # Find matching endpoint or create new
            endpoint_id = None
            for eid, endpoint in endpoints.items():
                if endpoint.get("url") == discovered.url:
                    endpoint_id = eid
                    break

            if not endpoint_id:
                # Create new endpoint ID
                endpoint_id = f"discovered_{discovered.host.replace('.', '_')}_{discovered.port}"

            # Update or create endpoint
            if merge and endpoint_id in endpoints:
                # Update existing
                endpoints[endpoint_id]["status"] = discovered.status
                if discovered.models:
                    endpoints[endpoint_id]["models"] = discovered.models
                if discovered.response_time_ms:
                    endpoints[endpoint_id]["response_time_ms"] = discovered.response_time_ms
            else:
                # Create new
                endpoints[endpoint_id] = {
                    "id": endpoint_id,
                    "name": f"Discovered {discovered.type} on {discovered.host}:{discovered.port}",
                    "display_name": f"{discovered.type.title()} ({discovered.host}:{discovered.port})",
                    "type": discovered.type,
                    "url": discovered.url,
                    "health_check": f"{discovered.url}/api/tags"
                    if discovered.type == "ollama"
                    else f"{discovered.url}/health",
                    "status": discovered.status,
                    "priority": 99,  # Low priority for discovered endpoints
                    "location": "discovered",
                    "description": f"Auto-discovered {discovered.type} endpoint",
                    "models": discovered.models,
                    "capabilities": discovered.capabilities,
                    "response_time_ms": discovered.response_time_ms,
                }

        registry["endpoints"] = endpoints
        registry["last_discovery"] = datetime.now().isoformat()
        registry["discovery_count"] = len(self.discovered_endpoints)

        # Backup existing registry
        backup_path = self.registry_path.with_suffix(".json.backup")
        if self.registry_path.exists():
            import shutil

            shutil.copy2(self.registry_path, backup_path)

        # Write updated registry
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)

        logger.info(f"Updated registry with {len(self.discovered_endpoints)} discovered endpoints")

        return registry

    def print_discovery_report(self):
        """Print discovery report"""
        print("=" * 80)
        print("ENDPOINT DISCOVERY REPORT")
        print("=" * 80)
        print(f"Discovered: {len(self.discovered_endpoints)} endpoints")
        print()

        operational = [e for e in self.discovered_endpoints if e.status == "operational"]
        degraded = [e for e in self.discovered_endpoints if e.status == "degraded"]
        offline = [e for e in self.discovered_endpoints if e.status == "offline"]

        print(f"✅ Operational: {len(operational)}")
        print(f"⚠️  Degraded: {len(degraded)}")
        print(f"❌ Offline: {len(offline)}")
        print()

        if operational:
            print("Operational Endpoints:")
            for endpoint in operational:
                print(f"  ✅ {endpoint.type.upper()}: {endpoint.url}")
                if endpoint.models:
                    print(f"     Models: {', '.join(endpoint.models[:5])}")
                if endpoint.response_time_ms:
                    print(f"     Response Time: {endpoint.response_time_ms:.0f}ms")
                print()

        if degraded:
            print("Degraded Endpoints:")
            for endpoint in degraded:
                print(f"  ⚠️  {endpoint.type.upper()}: {endpoint.url}")
                if endpoint.error:
                    print(f"     Error: {endpoint.error}")
                print()

        print("=" * 80)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Discover AI model endpoints on the network")
    parser.add_argument(
        "--no-network-scan", action="store_true", help="Skip network scanning (localhost only)"
    )
    parser.add_argument(
        "--update-registry",
        action="store_true",
        help="Update endpoint registry with discovered endpoints",
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        default=True,
        help="Merge with existing registry entries (default: True)",
    )

    args = parser.parse_args()

    discovery = EndpointDiscovery(project_root)
    endpoints = discovery.discover_all(scan_network=not args.no_network_scan)

    discovery.print_discovery_report()

    if args.update_registry:
        registry = discovery.update_registry(merge=args.merge)
        print("\n✅ Registry updated successfully")
    else:
        print("\n⚠️  Registry not updated (use --update-registry to update)")


if __name__ == "__main__":
    main()
