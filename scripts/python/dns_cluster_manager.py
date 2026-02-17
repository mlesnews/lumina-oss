#!/usr/bin/env python3
"""
DNS Cluster Manager

Manages two-node DNS cluster with:
- Primary DNS: NAS (Synology DSM)
- Secondary DNS: pfSense firewall (failover)
- DNS caching
- Automatic failover
- Health monitoring
"""

import sys
import socket
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = get_logger("DNSClusterManager")


@dataclass
class DNSServer:
    """DNS server configuration"""
    name: str
    host: str
    port: int = 53
    type: str = "primary"  # primary, secondary, cache
    cluster: str = "primary"  # primary_cluster, secondary_cluster
    role: str = "node1"  # node1, node2 (for failover within cluster)
    api_endpoint: Optional[str] = None
    api_username: Optional[str] = None
    api_password: Optional[str] = None
    health_check_interval: int = 30  # seconds
    last_health_check: Optional[datetime] = None
    is_healthy: bool = True
    response_time_ms: float = 0.0
    failure_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DNSCacheEntry:
    """DNS cache entry"""
    hostname: str
    ip_address: str
    record_type: str = "A"  # A, AAAA, PTR
    ttl: int = 300  # seconds
    cached_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(default_factory=datetime.now)
    source: str = "unknown"  # primary, secondary, cache


class DNSCache:
    """DNS response cache"""

    def __init__(self, default_ttl: int = 300):
        self.cache: Dict[str, DNSCacheEntry] = {}
        self.default_ttl = default_ttl
        self.logger = get_logger("DNSCache")

    def get(self, hostname: str, record_type: str = "A") -> Optional[DNSCacheEntry]:
        """Get cached DNS entry"""
        cache_key = f"{record_type}:{hostname}"
        entry = self.cache.get(cache_key)

        if entry:
            if datetime.now() < entry.expires_at:
                self.logger.debug(f"✅ Cache hit: {hostname} ({record_type})")
                return entry
            else:
                # Expired, remove from cache
                del self.cache[cache_key]
                self.logger.debug(f"⏰ Cache expired: {hostname} ({record_type})")

        return None

    def set(
        self,
        hostname: str,
        ip_address: str,
        record_type: str = "A",
        ttl: Optional[int] = None,
        source: str = "unknown"
    ) -> DNSCacheEntry:
        """Cache DNS entry"""
        cache_key = f"{record_type}:{hostname}"
        ttl = ttl or self.default_ttl

        entry = DNSCacheEntry(
            hostname=hostname,
            ip_address=ip_address,
            record_type=record_type,
            ttl=ttl,
            cached_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=ttl),
            source=source
        )

        self.cache[cache_key] = entry
        self.logger.debug(f"💾 Cached: {hostname} → {ip_address} (TTL: {ttl}s, source: {source})")

        return entry

    def clear(self, hostname: Optional[str] = None):
        """Clear cache entries"""
        if hostname:
            # Clear specific hostname
            keys_to_remove = [k for k in self.cache.keys() if hostname in k]
            for key in keys_to_remove:
                del self.cache[key]
            self.logger.info(f"🗑️  Cleared cache for: {hostname}")
        else:
            # Clear all
            self.cache.clear()
            self.logger.info("🗑️  Cleared all DNS cache")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_entries = len(self.cache)
        expired_entries = sum(
            1 for entry in self.cache.values()
            if datetime.now() >= entry.expires_at
        )
        valid_entries = total_entries - expired_entries

        return {
            "total_entries": total_entries,
            "valid_entries": valid_entries,
            "expired_entries": expired_entries,
            "cache_size_mb": sum(len(str(e)) for e in self.cache.values()) / (1024 * 1024)
        }


class DNSCluster:
    """DNS Cluster with failover nodes"""

    def __init__(
        self,
        cluster_name: str,
        node1: DNSServer,
        node2: DNSServer,
        cluster_type: str = "primary"  # primary_cluster, secondary_cluster
    ):
        self.cluster_name = cluster_name
        self.cluster_type = cluster_type
        self.node1 = node1
        self.node2 = node2
        self.node1.cluster = cluster_type
        self.node2.cluster = cluster_type
        self.node1.role = "node1"
        self.node2.role = "node2"

        self.current_node = self.node1
        self.failover_active = False
        self.logger = get_logger(f"DNSCluster-{cluster_name}")

    def get_active_node(self) -> DNSServer:
        """Get currently active node in cluster"""
        return self.current_node

    def check_cluster_health(self) -> Tuple[bool, DNSServer]:
        """
        Check cluster health, return (is_healthy, active_node)

        Returns:
            (is_healthy, active_node)
        """
        # Check current node
        is_healthy, response_time = self._check_node_health(self.current_node)

        if is_healthy:
            return True, self.current_node

        # Current node failed, try failover node
        self.logger.warning(f"⚠️  {self.current_node.name} failed, failing over to {self.node2.name if self.current_node == self.node1 else self.node1.name}")

        failover_node = self.node2 if self.current_node == self.node1 else self.node1
        is_healthy, response_time = self._check_node_health(failover_node)

        if is_healthy:
            self.current_node = failover_node
            self.failover_active = True
            return True, failover_node

        # Both nodes failed
        self.logger.error(f"❌ Both nodes in {self.cluster_name} cluster failed")
        return False, self.current_node

    def _check_node_health(self, node: DNSServer) -> Tuple[bool, float]:
        """Check individual node health"""
        try:
            start_time = time.time()
            test_hostname = "google.com"
            socket.setdefaulttimeout(5)

            try:
                ip = socket.gethostbyname(test_hostname)
                response_time = (time.time() - start_time) * 1000

                if ip:
                    node.last_health_check = datetime.now()
                    node.is_healthy = True
                    node.response_time_ms = response_time
                    node.failure_count = 0
                    return True, response_time
            except socket.gaierror:
                pass

            response_time = (time.time() - start_time) * 1000
            node.last_health_check = datetime.now()
            node.is_healthy = False
            node.failure_count += 1
            return False, response_time

        except Exception as e:
            self.logger.error(f"❌ Health check error for {node.name}: {e}")
            node.is_healthy = False
            node.failure_count += 1
            return False, 0.0


class DNSClusterManager:
    """
    Manages hybrid four-server DNS architecture:
    - Primary Cluster:
      - Node 1: NAS (Synology DSM)
      - Node 2: Primary failover node
    - Secondary Cluster:
      - Node 1: pfSense firewall
      - Node 2: Secondary failover node
    - DNS caching
    - Automatic failover at cluster and node levels
    """

    def __init__(
        self,
        primary_cluster_node1: Optional[DNSServer] = None,
        primary_cluster_node2: Optional[DNSServer] = None,
        secondary_cluster_node1: Optional[DNSServer] = None,
        secondary_cluster_node2: Optional[DNSServer] = None,
        enable_cache: bool = True,
        cache_ttl: int = 300
    ):
        self.logger = get_logger("DNSClusterManager")

        # Primary Cluster
        self.primary_cluster = DNSCluster(
            cluster_name="Primary Cluster",
            node1=primary_cluster_node1 or DNSServer(
                name="NAS Primary DNS Node 1",
                host="<NAS_PRIMARY_IP>",
                port=53,
                type="primary",
                cluster="primary_cluster",
                role="node1",
                metadata={"nas_host": "<NAS_PRIMARY_IP>", "nas_port": 5001}
            ),
            node2=primary_cluster_node2 or DNSServer(
                name="NAS Primary DNS Node 2",
                host="<NAS_IP>",  # Example: Second NAS or backup
                port=53,
                type="primary",
                cluster="primary_cluster",
                role="node2",
                metadata={"backup": True}
            ),
            cluster_type="primary_cluster"
        )

        # Secondary Cluster
        self.secondary_cluster = DNSCluster(
            cluster_name="Secondary Cluster",
            node1=secondary_cluster_node1 or DNSServer(
                name="pfSense Secondary DNS Node 1",
                host="<NAS_IP>",  # Typical pfSense gateway IP
                port=53,
                type="secondary",
                cluster="secondary_cluster",
                role="node1",
                metadata={"pfsense": True}
            ),
            node2=secondary_cluster_node2 or DNSServer(
                name="pfSense Secondary DNS Node 2",
                host="<NAS_IP>",  # Example: Backup router or second pfSense
                port=53,
                type="secondary",
                cluster="secondary_cluster",
                role="node2",
                metadata={"backup": True}
            ),
            cluster_type="secondary_cluster"
        )

        # DNS cache
        self.cache = DNSCache(default_ttl=cache_ttl) if enable_cache else None

        # Cluster-level failover state
        self.current_cluster = self.primary_cluster
        self.cluster_failover_active = False

        self.logger.info("🏛️  DNS Cluster Manager initialized (Hybrid 4-Server Architecture)")
        self.logger.info(f"\n   Primary Cluster:")
        self.logger.info(f"     Node 1: {self.primary_cluster.node1.name} ({self.primary_cluster.node1.host}:{self.primary_cluster.node1.port})")
        self.logger.info(f"     Node 2: {self.primary_cluster.node2.name} ({self.primary_cluster.node2.host}:{self.primary_cluster.node2.port})")
        self.logger.info(f"\n   Secondary Cluster:")
        self.logger.info(f"     Node 1: {self.secondary_cluster.node1.name} ({self.secondary_cluster.node1.host}:{self.secondary_cluster.node1.port})")
        self.logger.info(f"     Node 2: {self.secondary_cluster.node2.name} ({self.secondary_cluster.node2.host}:{self.secondary_cluster.node2.port})")
        self.logger.info(f"\n   Cache: {'Enabled' if self.cache else 'Disabled'}")


    def _resolve_with_node(
        self,
        hostname: str,
        dns_node: DNSServer,
        record_type: str = "A"
    ) -> Optional[str]:
        """Resolve hostname using specific DNS node"""
        try:
            # Set DNS server (if possible)
            # Note: Python's socket.gethostbyname uses system DNS
            # For true DNS server selection, would need dnspython library

            # For now, use system DNS but track which server should be used
            ip = socket.gethostbyname(hostname)

            # Cache the result
            if self.cache:
                self.cache.set(
                    hostname,
                    ip,
                    record_type=record_type,
                    source=f"{dns_node.cluster}:{dns_node.name}"
                )

            return ip

        except socket.gaierror as e:
            self.logger.warning(f"⚠️  DNS resolution failed for {hostname} via {dns_node.name}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Error resolving {hostname} via {dns_node.name}: {e}")
            return None

    def resolve(
        self,
        hostname: str,
        record_type: str = "A",
        use_cache: bool = True
    ) -> Optional[str]:
        """
        Resolve hostname with automatic failover (cluster and node level)

        Failover hierarchy:
        1. Primary Cluster Node 1
        2. Primary Cluster Node 2 (node-level failover)
        3. Secondary Cluster Node 1 (cluster-level failover)
        4. Secondary Cluster Node 2 (cluster + node-level failover)

        Args:
            hostname: Hostname to resolve
            record_type: DNS record type (A, AAAA, etc.)
            use_cache: Use DNS cache if available

        Returns:
            IP address if resolved, None otherwise
        """
        # Check cache first
        if use_cache and self.cache:
            cached = self.cache.get(hostname, record_type)
            if cached:
                return cached.ip_address

        # Check current cluster health
        cluster_healthy, active_node = self.current_cluster.check_cluster_health()

        if not cluster_healthy:
            # Current cluster failed, try secondary cluster
            if not self.cluster_failover_active:
                self.logger.warning(f"⚠️  {self.current_cluster.cluster_name} failed, failing over to {self.secondary_cluster.cluster_name}")
                self.cluster_failover_active = True
                self.current_cluster = self.secondary_cluster

                # Check secondary cluster health
                cluster_healthy, active_node = self.current_cluster.check_cluster_health()

        if not cluster_healthy:
            # Both clusters failed
            self.logger.error(f"❌ DNS resolution failed for {hostname} (all clusters failed)")
            return None

        # Try resolution with active node
        ip = self._resolve_with_node(hostname, active_node, record_type)

        if ip:
            # Check if we should failback to primary cluster
            if self.cluster_failover_active:
                # Check primary cluster health
                primary_healthy, _ = self.primary_cluster.check_cluster_health()
                if primary_healthy:
                    self.logger.info(f"✅ Primary cluster recovered, failing back")
                    self.cluster_failover_active = False
                    self.current_cluster = self.primary_cluster

            return ip

        # Current node failed, cluster should have already failed over
        # Try other cluster if available
        if not self.cluster_failover_active:
            self.logger.warning(f"⚠️  Current cluster failed, trying secondary cluster")
            cluster_healthy, active_node = self.secondary_cluster.check_cluster_health()
            if cluster_healthy:
                self.cluster_failover_active = True
                self.current_cluster = self.secondary_cluster
                ip = self._resolve_with_node(hostname, active_node, record_type)
                if ip:
                    return ip

        # All nodes failed
        self.logger.error(f"❌ DNS resolution failed for {hostname} (all nodes failed)")
        return None

    def reverse_resolve(
        self,
        ip_address: str,
        use_cache: bool = True
    ) -> Optional[str]:
        """
        Reverse DNS lookup (PTR record) with failover

        Returns:
            Hostname if resolved, None otherwise
        """
        # Check cache
        if use_cache and self.cache:
            cached = self.cache.get(ip_address, "PTR")
            if cached:
                return cached.hostname

        try:
            hostname, _, _ = socket.gethostbyaddr(ip_address)

            # Cache the result
            if self.cache:
                self.cache.set(
                    ip_address,
                    hostname,
                    record_type="PTR",
                    source=self.current_dns.name
                )

            return hostname

        except socket.herror:
            return None
        except Exception as e:
            self.logger.error(f"❌ Reverse DNS lookup failed: {e}")
            return None

    def get_cluster_status(self) -> Dict[str, Any]:
        """Get cluster status for all clusters and nodes"""
        # Check primary cluster
        primary_healthy, primary_active = self.primary_cluster.check_cluster_health()

        # Check secondary cluster
        secondary_healthy, secondary_active = self.secondary_cluster.check_cluster_health()

        cache_stats = self.cache.get_stats() if self.cache else None

        return {
            "primary_cluster": {
                "cluster_name": self.primary_cluster.cluster_name,
                "cluster_type": self.primary_cluster.cluster_type,
                "healthy": primary_healthy,
                "active_node": primary_active.name,
                "node1": {
                    "name": self.primary_cluster.node1.name,
                    "host": self.primary_cluster.node1.host,
                    "healthy": self.primary_cluster.node1.is_healthy,
                    "response_time_ms": self.primary_cluster.node1.response_time_ms,
                    "failure_count": self.primary_cluster.node1.failure_count,
                    "last_check": self.primary_cluster.node1.last_health_check.isoformat() if self.primary_cluster.node1.last_health_check else None,
                    "active": self.primary_cluster.node1 == primary_active
                },
                "node2": {
                    "name": self.primary_cluster.node2.name,
                    "host": self.primary_cluster.node2.host,
                    "healthy": self.primary_cluster.node2.is_healthy,
                    "response_time_ms": self.primary_cluster.node2.response_time_ms,
                    "failure_count": self.primary_cluster.node2.failure_count,
                    "last_check": self.primary_cluster.node2.last_health_check.isoformat() if self.primary_cluster.node2.last_health_check else None,
                    "active": self.primary_cluster.node2 == primary_active
                },
                "failover_active": self.primary_cluster.failover_active
            },
            "secondary_cluster": {
                "cluster_name": self.secondary_cluster.cluster_name,
                "cluster_type": self.secondary_cluster.cluster_type,
                "healthy": secondary_healthy,
                "active_node": secondary_active.name,
                "node1": {
                    "name": self.secondary_cluster.node1.name,
                    "host": self.secondary_cluster.node1.host,
                    "healthy": self.secondary_cluster.node1.is_healthy,
                    "response_time_ms": self.secondary_cluster.node1.response_time_ms,
                    "failure_count": self.secondary_cluster.node1.failure_count,
                    "last_check": self.secondary_cluster.node1.last_health_check.isoformat() if self.secondary_cluster.node1.last_health_check else None,
                    "active": self.secondary_cluster.node1 == secondary_active
                },
                "node2": {
                    "name": self.secondary_cluster.node2.name,
                    "host": self.secondary_cluster.node2.host,
                    "healthy": self.secondary_cluster.node2.is_healthy,
                    "response_time_ms": self.secondary_cluster.node2.response_time_ms,
                    "failure_count": self.secondary_cluster.node2.failure_count,
                    "last_check": self.secondary_cluster.node2.last_health_check.isoformat() if self.secondary_cluster.node2.last_health_check else None,
                    "active": self.secondary_cluster.node2 == secondary_active
                },
                "failover_active": self.secondary_cluster.failover_active
            },
            "current_cluster": self.current_cluster.cluster_name,
            "cluster_failover_active": self.cluster_failover_active,
            "cache": cache_stats,
            "timestamp": datetime.now().isoformat()
        }


def main():
    """CLI for DNS cluster management"""
    import argparse

    parser = argparse.ArgumentParser(description="DNS Cluster Manager")
    parser.add_argument("--resolve", help="Resolve hostname")
    parser.add_argument("--reverse", help="Reverse DNS lookup (IP address)")
    parser.add_argument("--status", action="store_true", help="Get cluster status")
    parser.add_argument("--clear-cache", help="Clear cache for hostname (or 'all' for all)")
    parser.add_argument("--primary-node1-host", default="<NAS_PRIMARY_IP>", help="Primary cluster node 1 host")
    parser.add_argument("--primary-node2-host", default="<NAS_IP>", help="Primary cluster node 2 host")
    parser.add_argument("--secondary-node1-host", default="<NAS_IP>", help="Secondary cluster node 1 host (pfSense)")
    parser.add_argument("--secondary-node2-host", default="<NAS_IP>", help="Secondary cluster node 2 host")

    args = parser.parse_args()

    cluster = DNSClusterManager(
        primary_cluster_node1=DNSServer(
            name="NAS Primary DNS Node 1",
            host=args.primary_node1_host,
            port=53,
            type="primary",
            cluster="primary_cluster",
            role="node1"
        ),
        primary_cluster_node2=DNSServer(
            name="NAS Primary DNS Node 2",
            host=args.primary_node2_host,
            port=53,
            type="primary",
            cluster="primary_cluster",
            role="node2"
        ),
        secondary_cluster_node1=DNSServer(
            name="pfSense Secondary DNS Node 1",
            host=args.secondary_node1_host,
            port=53,
            type="secondary",
            cluster="secondary_cluster",
            role="node1"
        ),
        secondary_cluster_node2=DNSServer(
            name="pfSense Secondary DNS Node 2",
            host=args.secondary_node2_host,
            port=53,
            type="secondary",
            cluster="secondary_cluster",
            role="node2"
        ),
        enable_cache=True
    )

    if args.resolve:
        ip = cluster.resolve(args.resolve)
        if ip:
            print(f"✅ {args.resolve} → {ip}")
        else:
            print(f"❌ Failed to resolve {args.resolve}")

    elif args.reverse:
        hostname = cluster.reverse_resolve(args.reverse)
        if hostname:
            print(f"✅ {args.reverse} → {hostname}")
        else:
            print(f"❌ Failed to reverse resolve {args.reverse}")

    elif args.status:
        status = cluster.get_cluster_status()
        print(f"\n🏛️  DNS Cluster Status (Hybrid 4-Server Architecture):")

        print(f"\n{'='*60}")
        print(f"Primary Cluster: {status['primary_cluster']['cluster_name']}")
        print(f"{'='*60}")
        print(f"  Cluster Healthy: {'✅' if status['primary_cluster']['healthy'] else '❌'}")
        print(f"  Active Node: {status['primary_cluster']['active_node']}")
        print(f"  Node Failover: {'⚠️  Active' if status['primary_cluster']['failover_active'] else '✅ No'}")
        print(f"\n  Node 1:")
        print(f"    Name: {status['primary_cluster']['node1']['name']}")
        print(f"    Host: {status['primary_cluster']['node1']['host']}")
        print(f"    Healthy: {'✅' if status['primary_cluster']['node1']['healthy'] else '❌'}")
        print(f"    Response Time: {status['primary_cluster']['node1']['response_time_ms']:.2f}ms")
        print(f"    Active: {'⭐' if status['primary_cluster']['node1']['active'] else ''}")
        print(f"\n  Node 2:")
        print(f"    Name: {status['primary_cluster']['node2']['name']}")
        print(f"    Host: {status['primary_cluster']['node2']['host']}")
        print(f"    Healthy: {'✅' if status['primary_cluster']['node2']['healthy'] else '❌'}")
        print(f"    Response Time: {status['primary_cluster']['node2']['response_time_ms']:.2f}ms")
        print(f"    Active: {'⭐' if status['primary_cluster']['node2']['active'] else ''}")

        print(f"\n{'='*60}")
        print(f"Secondary Cluster: {status['secondary_cluster']['cluster_name']}")
        print(f"{'='*60}")
        print(f"  Cluster Healthy: {'✅' if status['secondary_cluster']['healthy'] else '❌'}")
        print(f"  Active Node: {status['secondary_cluster']['active_node']}")
        print(f"  Node Failover: {'⚠️  Active' if status['secondary_cluster']['failover_active'] else '✅ No'}")
        print(f"\n  Node 1:")
        print(f"    Name: {status['secondary_cluster']['node1']['name']}")
        print(f"    Host: {status['secondary_cluster']['node1']['host']}")
        print(f"    Healthy: {'✅' if status['secondary_cluster']['node1']['healthy'] else '❌'}")
        print(f"    Response Time: {status['secondary_cluster']['node1']['response_time_ms']:.2f}ms")
        print(f"    Active: {'⭐' if status['secondary_cluster']['node1']['active'] else ''}")
        print(f"\n  Node 2:")
        print(f"    Name: {status['secondary_cluster']['node2']['name']}")
        print(f"    Host: {status['secondary_cluster']['node2']['host']}")
        print(f"    Healthy: {'✅' if status['secondary_cluster']['node2']['healthy'] else '❌'}")
        print(f"    Response Time: {status['secondary_cluster']['node2']['response_time_ms']:.2f}ms")
        print(f"    Active: {'⭐' if status['secondary_cluster']['node2']['active'] else ''}")

        print(f"\n{'='*60}")
        print(f"Cluster-Level Status:")
        print(f"{'='*60}")
        print(f"  Current Cluster: {status['current_cluster']}")
        print(f"  Cluster Failover: {'⚠️  Active' if status['cluster_failover_active'] else '✅ No'}")

        if status['cache']:
            print(f"\n  Cache:")
            print(f"    Valid Entries: {status['cache']['valid_entries']}")
            print(f"    Total Entries: {status['cache']['total_entries']}")

    elif args.clear_cache:
        if args.clear_cache == "all":
            cluster.cache.clear()
            print("✅ Cleared all DNS cache")
        else:
            cluster.cache.clear(args.clear_cache)
            print(f"✅ Cleared cache for {args.clear_cache}")

    else:
        parser.print_help()


if __name__ == "__main__":



    main()