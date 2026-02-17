#!/usr/bin/env python3
"""
Network Security Orchestrator

Hybrid system that ties together:
- HTTP → HTTPS migration
- DNS resolution and validation
- Reverse DNS (PTR) verification
- Certificate management
- Network protocol security
"""

import sys
import socket
import ssl
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
import re
import ipaddress
from jarvis_lumina_master_orchestrator import SubAgent


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

try:
    from nas_certificate_manager import NASCertificateManager
    CERT_MANAGER_AVAILABLE = True
except ImportError:
    CERT_MANAGER_AVAILABLE = False
    NASCertificateManager = None

try:
    from nas_dns_manager import NASDNSManager
    NAS_DNS_AVAILABLE = True
except ImportError:
    NAS_DNS_AVAILABLE = False
    NASDNSManager = None

try:
    from dns_cluster_manager import DNSClusterManager, DNSServer
    DNS_CLUSTER_AVAILABLE = True
except ImportError:
    DNS_CLUSTER_AVAILABLE = False
    DNSClusterManager = None
    DNSServer = None

logger = get_logger("NetworkSecurityOrchestrator")


class DNSResolver:
    """DNS and Reverse DNS resolution"""

    def __init__(self):
        self.logger = get_logger("DNSResolver")

# SubAgent registry (Puppetmaster delegation via @SUBAGENTS)
        self.subagents = {}
        self._init_subagents()
    def resolve_hostname(self, hostname: str) -> Dict[str, Any]:
        """
        Resolve hostname to IP address(es)

        Returns:
            Dictionary with IP addresses and metadata
        """
        try:
            # Get all IP addresses (IPv4 and IPv6)
            addr_info = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC)
            ip_addresses = []

            for info in addr_info:
                ip = info[4][0]
                if ip not in ip_addresses:
                    ip_addresses.append(ip)

            return {
                "hostname": hostname,
                "ip_addresses": ip_addresses,
                "primary_ip": ip_addresses[0] if ip_addresses else None,
                "resolved": True,
                "timestamp": datetime.now().isoformat()
            }
        except socket.gaierror as e:
            self.logger.error(f"❌ DNS resolution failed for {hostname}: {e}")
            return {
                "hostname": hostname,
                "ip_addresses": [],
                "primary_ip": None,
                "resolved": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def reverse_dns_lookup(self, ip_address: str) -> Dict[str, Any]:
        """
        Reverse DNS lookup (PTR record) - IP to hostname

        Returns:
            Dictionary with hostname and metadata
        """
        try:
            hostname, aliases, ip_list = socket.gethostbyaddr(ip_address)

            return {
                "ip_address": ip_address,
                "hostname": hostname,
                "aliases": aliases,
                "resolved": True,
                "timestamp": datetime.now().isoformat()
            }
        except socket.herror as e:
            self.logger.warning(f"⚠️  Reverse DNS lookup failed for {ip_address}: {e}")
            return {
                "ip_address": ip_address,
                "hostname": None,
                "aliases": [],
                "resolved": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"❌ Error in reverse DNS lookup: {e}")
            return {
                "ip_address": ip_address,
                "hostname": None,
                "resolved": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def verify_dns_consistency(self, hostname: str, ip_address: str) -> Dict[str, Any]:
        """
        Verify DNS consistency: Forward DNS → IP, then Reverse DNS → hostname

        Returns:
            Dictionary with verification results
        """
        # Forward DNS
        forward_result = self.resolve_hostname(hostname)

        if not forward_result["resolved"]:
            return {
                "consistent": False,
                "reason": "Forward DNS resolution failed",
                "forward_dns": forward_result,
                "reverse_dns": None
            }

        # Check if IP matches
        if ip_address not in forward_result["ip_addresses"]:
            return {
                "consistent": False,
                "reason": f"IP {ip_address} not in resolved IPs {forward_result['ip_addresses']}",
                "forward_dns": forward_result,
                "reverse_dns": None
            }

        # Reverse DNS
        reverse_result = self.reverse_dns_lookup(ip_address)

        if not reverse_result["resolved"]:
            return {
                "consistent": False,
                "reason": "Reverse DNS resolution failed",
                "forward_dns": forward_result,
                "reverse_dns": reverse_result
            }

        # Check if hostnames match (allowing for aliases)
        reverse_hostname = reverse_result["hostname"].lower()
        original_hostname = hostname.lower()
        reverse_aliases = [a.lower() for a in reverse_result.get("aliases", [])]

        hostname_matches = (
            reverse_hostname == original_hostname or
            original_hostname in reverse_aliases or
            reverse_hostname in [original_hostname]  # Exact match
        )

        return {
            "consistent": hostname_matches,
            "reason": "DNS consistency verified" if hostname_matches else "Hostname mismatch",
            "forward_dns": forward_result,
            "reverse_dns": reverse_result,
            "hostname_match": hostname_matches
        }


class HTTPSMigrator:
    """HTTP to HTTPS migration and validation"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = get_logger("HTTPSMigrator")

        # Certificate manager
        self.cert_manager = None
        if CERT_MANAGER_AVAILABLE and NASCertificateManager:
            self.cert_manager = NASCertificateManager(project_root=self.project_root)

    def is_https_available(self, url: str) -> Dict[str, Any]:
        """
        Check if HTTPS is available for a URL

        Returns:
            Dictionary with HTTPS availability status
        """
        if not url.startswith("http://"):
            return {
                "url": url,
                "https_available": None,
                "error": "URL must start with http://"
            }

        https_url = url.replace("http://", "https://", 1)

        try:
            response = requests.get(https_url, timeout=5, verify=False, allow_redirects=True)
            return {
                "url": url,
                "https_url": https_url,
                "https_available": True,
                "status_code": response.status_code,
                "final_url": response.url,
                "timestamp": datetime.now().isoformat()
            }
        except requests.exceptions.SSLError as e:
            return {
                "url": url,
                "https_url": https_url,
                "https_available": True,  # HTTPS exists, but certificate issue
                "ssl_error": str(e),
                "needs_certificate": True,
                "timestamp": datetime.now().isoformat()
            }
        except requests.exceptions.ConnectionError:
            return {
                "url": url,
                "https_url": https_url,
                "https_available": False,
                "error": "Connection failed",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "url": url,
                "https_url": https_url,
                "https_available": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def migrate_url_to_https(self, url: str, verify_certificate: bool = True) -> Dict[str, Any]:
        """
        Migrate HTTP URL to HTTPS

        Returns:
            Dictionary with migration result
        """
        if url.startswith("https://"):
            return {
                "url": url,
                "migrated": False,
                "reason": "Already HTTPS",
                "final_url": url
            }

        if not url.startswith("http://"):
            return {
                "url": url,
                "migrated": False,
                "reason": "Invalid URL format",
                "error": "URL must start with http:// or https://"
            }

        https_url = url.replace("http://", "https://", 1)

        # Check HTTPS availability
        availability = self.is_https_available(url)

        if not availability.get("https_available"):
            return {
                "url": url,
                "https_url": https_url,
                "migrated": False,
                "reason": "HTTPS not available",
                "availability": availability
            }

        # Get certificate verification setting
        verify_setting = True  # Default
        if availability.get("needs_certificate"):
            # Extract hostname and port from URL
            from urllib.parse import urlparse
            parsed = urlparse(https_url)
            hostname = parsed.hostname
            port = parsed.port or 443

            if self.cert_manager:
                verify_setting = self.cert_manager.get_requests_verify_setting(
                    hostname,
                    port,
                    auto_download=True,
                    auto_generate=True
                )

        return {
            "url": url,
            "https_url": https_url,
            "migrated": True,
            "verify_certificate": verify_setting,
            "availability": availability,
            "timestamp": datetime.now().isoformat()
        }


class NetworkSecurityOrchestrator:
    """
    Hybrid system that orchestrates:
    - HTTP → HTTPS migration
    - DNS resolution and validation
    - Reverse DNS (PTR) verification
    - Certificate management
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = get_logger("NetworkSecurityOrchestrator")

        self.dns_resolver = DNSResolver()
        self.https_migrator = HTTPSMigrator(project_root=self.project_root)

        # Certificate manager
        self.cert_manager = None
        if CERT_MANAGER_AVAILABLE and NASCertificateManager:
            self.cert_manager = NASCertificateManager(project_root=self.project_root)

        # NAS DNS Manager (optional - for DSM DNS Server integration)
        self.nas_dns_manager = None
        if NAS_DNS_AVAILABLE and NASDNSManager:
            # Can be initialized later with credentials
            self.nas_dns_manager_class = NASDNSManager

        # DNS Cluster Manager (hybrid 4-server architecture)
        self.dns_cluster = None
        if DNS_CLUSTER_AVAILABLE and DNSClusterManager and DNSServer:
            try:
                self.dns_cluster = DNSClusterManager(
                    primary_cluster_node1=DNSServer(
                        name="NAS Primary DNS Node 1",
                        host="<NAS_PRIMARY_IP>",
                        port=53,
                        type="primary",
                        cluster="primary_cluster",
                        role="node1"
                    ),
                    primary_cluster_node2=DNSServer(
                        name="NAS Primary DNS Node 2",
                        host="<NAS_IP>",
                        port=53,
                        type="primary",
                        cluster="primary_cluster",
                        role="node2"
                    ),
                    secondary_cluster_node1=DNSServer(
                        name="pfSense Secondary DNS Node 1",
                        host="<NAS_IP>",
                        port=53,
                        type="secondary",
                        cluster="secondary_cluster",
                        role="node1"
                    ),
                    secondary_cluster_node2=DNSServer(
                        name="pfSense Secondary DNS Node 2",
                        host="<NAS_IP>",
                        port=53,
                        type="secondary",
                        cluster="secondary_cluster",
                        role="node2"
                    ),
                    enable_cache=True,
                    cache_ttl=300
                )
                self.logger.info("✅ DNS Cluster Manager initialized (hybrid 4-server architecture)")
            except Exception as e:
                self.logger.warning(f"⚠️  DNS Cluster initialization failed: {e}")

        self.logger.info("🔒 Network Security Orchestrator initialized")

    def secure_network_endpoint(
        self,
        url: str,
        verify_dns: bool = True,
        verify_reverse_dns: bool = True,
        require_https: bool = True
    ) -> Dict[str, Any]:
        """
        Secure a network endpoint with full validation:
        1. Migrate HTTP → HTTPS
        2. Verify DNS resolution
        3. Verify reverse DNS (PTR)
        4. Ensure certificate exists

        Returns:
            Comprehensive security validation result
        """
        from urllib.parse import urlparse

        self.logger.info(f"🔒 Securing network endpoint: {url}")

        result = {
            "original_url": url,
            "secure_url": None,
            "dns_verified": False,
            "reverse_dns_verified": False,
            "https_enabled": False,
            "certificate_available": False,
            "secure": False,
            "timestamp": datetime.now().isoformat()
        }

        # Parse URL
        parsed = urlparse(url)
        hostname = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        scheme = parsed.scheme

        if not hostname:
            result["error"] = "Invalid URL: no hostname"
            return result

        # Step 1: DNS Resolution (with cluster and caching)
        if verify_dns:
            # Use DNS cluster if available (with caching and failover)
            if self.dns_cluster:
                ip_address = self.dns_cluster.resolve(hostname, use_cache=True)
                if ip_address:
                    dns_result = {
                        "hostname": hostname,
                        "ip_addresses": [ip_address],
                        "primary_ip": ip_address,
                        "resolved": True,
                        "source": "dns_cluster",
                        "cache_used": True
                    }
                    result["dns_verified"] = True
                    result["dns_result"] = dns_result
                else:
                    result["dns_verified"] = False
                    result["error"] = "DNS resolution failed (both servers)"
                    return result
            else:
                # Fallback to standard DNS resolver
                dns_result = self.dns_resolver.resolve_hostname(hostname)
                result["dns_verified"] = dns_result["resolved"]
                result["dns_result"] = dns_result

                if not dns_result["resolved"]:
                    result["error"] = "DNS resolution failed"
                    return result

                ip_address = dns_result["primary_ip"]
        else:
            # Try to get IP from hostname (might be IP already)
            try:
                ip_address = ipaddress.ip_address(hostname)
                ip_address = str(ip_address)
            except ValueError:
                # Not an IP, resolve it
                dns_result = self.dns_resolver.resolve_hostname(hostname)
                if not dns_result["resolved"]:
                    result["error"] = "DNS resolution failed"
                    return result
                ip_address = dns_result["primary_ip"]

        # Step 2: Reverse DNS Verification
        if verify_reverse_dns:
            reverse_dns_result = self.dns_resolver.verify_dns_consistency(hostname, ip_address)
            result["reverse_dns_verified"] = reverse_dns_result.get("consistent", False)
            result["reverse_dns_result"] = reverse_dns_result

            if not result["reverse_dns_verified"]:
                self.logger.warning(f"⚠️  Reverse DNS verification failed for {hostname}")

        # Step 3: HTTPS Migration
        if require_https and scheme == "http":
            migration_result = self.https_migrator.migrate_url_to_https(url)
            result["https_migration"] = migration_result

            if migration_result.get("migrated"):
                secure_url = migration_result["https_url"]
                result["secure_url"] = secure_url
                result["https_enabled"] = True

                # Update parsed URL
                parsed = urlparse(secure_url)
                port = parsed.port or 443
            else:
                result["error"] = "HTTPS migration failed"
                return result
        elif scheme == "https":
            result["secure_url"] = url
            result["https_enabled"] = True
        else:
            result["secure_url"] = url

        # Step 4: Certificate Management
        if result["https_enabled"]:
            if self.cert_manager:
                cert_path = self.cert_manager.ensure_certificate(
                    hostname,
                    port,
                    auto_download=True,
                    auto_generate=True
                )
                result["certificate_available"] = cert_path is not None
                result["certificate_path"] = cert_path
            else:
                result["certificate_available"] = False
                result["warning"] = "Certificate manager not available"

        # Final security assessment
        result["secure"] = (
            result.get("dns_verified", True) and
            result.get("reverse_dns_verified", True) and
            result.get("https_enabled", False) and
            result.get("certificate_available", False)
        )

        if result["secure"]:
            self.logger.info(f"✅ Endpoint secured: {result['secure_url']}")
        else:
            self.logger.warning(f"⚠️  Endpoint security complete: {result.get('error', 'See details')}")

        return result

    def audit_http_urls(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Audit a file for HTTP URLs

        Returns:
            List of HTTP URLs found
        """
        http_urls = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find all HTTP URLs
            http_pattern = r'http://[^\s\'"<>\)]+'
            matches = re.findall(http_pattern, content)

            for match in matches:
                # Clean up URL (remove trailing punctuation)
                url = match.rstrip('.,;:!?)')
                http_urls.append({
                    "url": url,
                    "file": str(file_path),
                    "line_number": None  # Could add line number tracking
                })

        except Exception as e:
            self.logger.error(f"❌ Error auditing file {file_path}: {e}")

        return http_urls

    def migrate_file_to_https(self, file_path: Path, dry_run: bool = True) -> Dict[str, Any]:
        """
        Migrate all HTTP URLs in a file to HTTPS

        Returns:
            Migration result
        """
        http_urls = self.audit_http_urls(file_path)

        if not http_urls:
            return {
                "file": str(file_path),
                "migrated": False,
                "reason": "No HTTP URLs found",
                "urls_found": 0
            }

        migration_results = []
        secure_urls = []

        for url_info in http_urls:
            url = url_info["url"]
            secure_result = self.secure_network_endpoint(url)
            migration_results.append(secure_result)

            if secure_result.get("secure") and secure_result.get("secure_url"):
                secure_urls.append({
                    "original": url,
                    "secure": secure_result["secure_url"],
                    "file": str(file_path)
                })

        if not dry_run and secure_urls:
            # Perform actual file migration
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                for url_mapping in secure_urls:
                    content = content.replace(url_mapping["original"], url_mapping["secure"])

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                return {
                    "file": str(file_path),
                    "migrated": True,
                    "urls_migrated": len(secure_urls),
                    "urls_found": len(http_urls),
                    "migration_results": migration_results
                }
            except Exception as e:
                return {
                    "file": str(file_path),
                    "migrated": False,
                    "error": str(e),
                    "urls_found": len(http_urls)
                }

        return {
            "file": str(file_path),
            "migrated": dry_run,
            "dry_run": dry_run,
            "urls_found": len(http_urls),
            "secure_urls": secure_urls,
            "migration_results": migration_results
        }


def main():
    try:
        """CLI for network security orchestration"""
        import argparse

        parser = argparse.ArgumentParser(description="Network Security Orchestrator")
        parser.add_argument("--url", help="URL to secure")
        parser.add_argument("--audit-file", help="File to audit for HTTP URLs")
        parser.add_argument("--migrate-file", help="File to migrate HTTP → HTTPS")
        parser.add_argument("--dry-run", action="store_true", help="Dry run (no changes)")
        parser.add_argument("--verify-dns", action="store_true", default=True, help="Verify DNS resolution")
        parser.add_argument("--verify-reverse-dns", action="store_true", default=True, help="Verify reverse DNS")

        args = parser.parse_args()

        orchestrator = NetworkSecurityOrchestrator()

        if args.url:
            result = orchestrator.secure_network_endpoint(
                args.url,
                verify_dns=args.verify_dns,
                verify_reverse_dns=args.verify_reverse_dns
            )
            print(f"\n🔒 Security Result:")
            print(f"  Original URL: {result['original_url']}")
            print(f"  Secure URL: {result.get('secure_url', 'N/A')}")
            print(f"  DNS Verified: {result.get('dns_verified', False)}")
            print(f"  Reverse DNS Verified: {result.get('reverse_dns_verified', False)}")
            print(f"  HTTPS Enabled: {result.get('https_enabled', False)}")
            print(f"  Certificate Available: {result.get('certificate_available', False)}")
            print(f"  Secure: {result.get('secure', False)}")
            if result.get('error'):
                print(f"  Error: {result['error']}")

        elif args.audit_file:
            file_path = Path(args.audit_file)
            http_urls = orchestrator.audit_http_urls(file_path)
            print(f"\n📋 HTTP URLs found in {file_path}:")
            for url_info in http_urls:
                print(f"  - {url_info['url']}")
            print(f"\nTotal: {len(http_urls)} HTTP URLs")

        elif args.migrate_file:
            file_path = Path(args.migrate_file)
            result = orchestrator.migrate_file_to_https(file_path, dry_run=args.dry_run)
            print(f"\n🔄 Migration Result:")
            print(f"  File: {result['file']}")
            print(f"  URLs Found: {result.get('urls_found', 0)}")
            print(f"  Migrated: {result.get('migrated', False)}")
            if args.dry_run:
                print(f"  ⚠️  DRY RUN - No changes made")
            if result.get('secure_urls'):
                print(f"\n  Secure URLs:")
                for url_mapping in result['secure_urls']:
                    print(f"    {url_mapping['original']} → {url_mapping['secure']}")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()