#!/usr/bin/env python3
"""
NAS DNS Manager

Manages DNS records via Synology DSM DNS Server package.
Integrates with the Network Security Orchestrator for DNS/HTTPS/certificate management.

Similar to Active Directory DNS (now Azure AD DNS):
- Local DNS resolution
- Forward DNS (A/AAAA records)
- Reverse DNS (PTR records)
- DNS zone management
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
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

logger = get_logger("NASDNSManager")


class NASDNSManager:
    """
    Manages DNS via Synology DSM DNS Server package

    Similar to Active Directory DNS:
    - Local DNS resolution for internal network
    - Forward DNS (hostname → IP)
    - Reverse DNS (IP → hostname)
    - Zone management
    - Record management (A, AAAA, PTR, CNAME, etc.)
    """

    def __init__(
        self,
        nas_host: str = "<NAS_PRIMARY_IP>",
        nas_port: int = 5001,
        username: Optional[str] = None,
        password: Optional[str] = None,
        verify_ssl: bool = True
    ):
        self.nas_host = nas_host
        self.nas_port = nas_port
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl

        self.logger = get_logger("NASDNSManager")

        # Session for API calls
        self.session = None
        self.sid = None  # Session ID from DSM API

        # Certificate manager
        try:
            from nas_certificate_manager import NASCertificateManager
            project_root = Path(__file__).parent.parent.parent
            self.cert_manager = NASCertificateManager(project_root=project_root)
        except ImportError:
            self.cert_manager = None

        self.logger.info(f"🏛️  NAS DNS Manager initialized (NAS: {nas_host}:{nas_port})")

    def _get_verify_setting(self) -> Any:
        """Get SSL verification setting"""
        if not self.verify_ssl:
            return False

        if self.cert_manager:
            return self.cert_manager.get_requests_verify_setting(
                self.nas_host,
                self.nas_port,
                auto_download=True,
                auto_generate=True
            )

        return True

    def _login(self) -> bool:
        """Login to Synology DSM API"""
        if not REQUESTS_AVAILABLE:
            self.logger.error("❌ requests library not available")
            return False

        if not self.username or not self.password:
            self.logger.warning("⚠️  Username/password not provided")
            return False

        try:
            verify = self._get_verify_setting()
            api_url = f"https://{self.nas_host}:{self.nas_port}/webapi/auth.cgi"

            params = {
                "api": "SYNO.API.Auth",
                "version": "3",
                "method": "login",
                "account": self.username,
                "passwd": self.password,
                "session": "DSM",
                "format": "sid"
            }

            response = requests.get(api_url, params=params, verify=verify, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get("success"):
                self.sid = data.get("data", {}).get("sid")
                self.logger.info("✅ Logged in to Synology DSM")
                return True
            else:
                self.logger.error(f"❌ Login failed: {data.get('error', {}).get('msg', 'Unknown error')}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Login error: {e}")
            return False

    def _logout(self) -> bool:
        """Logout from Synology DSM API"""
        if not self.sid:
            return True

        try:
            verify = self._get_verify_setting()
            api_url = f"https://{self.nas_host}:{self.nas_port}/webapi/auth.cgi"

            params = {
                "api": "SYNO.API.Auth",
                "version": "3",
                "method": "logout",
                "session": "DSM",
                "_sid": self.sid
            }

            response = requests.get(api_url, params=params, verify=verify, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get("success"):
                self.sid = None
                self.logger.info("✅ Logged out from Synology DSM")
                return True

        except Exception as e:
            self.logger.warning(f"⚠️  Logout error: {e}")

        return False

    def _call_dns_api(self, method: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call Synology DNS Server API"""
        if not self.sid:
            if not self._login():
                return None

        try:
            verify = self._get_verify_setting()
            api_url = f"https://{self.nas_host}:{self.nas_port}/webapi/entry.cgi"

            # Add session ID
            params["_sid"] = self.sid

            response = requests.get(api_url, params=params, verify=verify, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data.get("success"):
                return data.get("data", {})
            else:
                self.logger.error(f"❌ DNS API error: {data.get('error', {}).get('msg', 'Unknown error')}")
                return None

        except Exception as e:
            self.logger.error(f"❌ DNS API call error: {e}")
            return None

    def get_dns_zones(self) -> List[Dict[str, Any]]:
        """
        Get all DNS zones

        Returns:
            List of DNS zones
        """
        self.logger.info("📋 Getting DNS zones...")

        params = {
            "api": "SYNO.DNS.Server.Zone",
            "version": "1",
            "method": "list"
        }

        result = self._call_dns_api("list", params)

        if result:
            zones = result.get("zones", [])
            self.logger.info(f"✅ Found {len(zones)} DNS zones")
            return zones

        return []

    def get_dns_records(self, zone: str) -> List[Dict[str, Any]]:
        """
        Get DNS records for a zone

        Args:
            zone: DNS zone name (e.g., "local", "example.com")

        Returns:
            List of DNS records
        """
        self.logger.info(f"📋 Getting DNS records for zone: {zone}")

        params = {
            "api": "SYNO.DNS.Server.Record",
            "version": "1",
            "method": "list",
            "zone": zone
        }

        result = self._call_dns_api("list", params)

        if result:
            records = result.get("records", [])
            self.logger.info(f"✅ Found {len(records)} DNS records in zone {zone}")
            return records

        return []

    def create_a_record(
        self,
        zone: str,
        hostname: str,
        ip_address: str,
        ttl: int = 3600
    ) -> bool:
        """
        Create A record (forward DNS: hostname → IP)

        Similar to Active Directory DNS A record creation

        Args:
            zone: DNS zone name
            hostname: Hostname (without zone)
            ip_address: IPv4 address
            ttl: Time to live (seconds)

        Returns:
            True if successful
        """
        self.logger.info(f"➕ Creating A record: {hostname}.{zone} → {ip_address}")

        params = {
            "api": "SYNO.DNS.Server.Record",
            "version": "1",
            "method": "create",
            "zone": zone,
            "type": "A",
            "name": hostname,
            "value": ip_address,
            "ttl": ttl
        }

        result = self._call_dns_api("create", params)

        if result:
            self.logger.info(f"✅ A record created: {hostname}.{zone} → {ip_address}")
            return True

        return False

    def create_ptr_record(
        self,
        reverse_zone: str,
        ip_address: str,
        hostname: str,
        ttl: int = 3600
    ) -> bool:
        """
        Create PTR record (reverse DNS: IP → hostname)

        Similar to Active Directory DNS PTR record creation

        Args:
            reverse_zone: Reverse DNS zone (e.g., "17.17.10.in-addr.arpa")
            ip_address: IP address
            hostname: Hostname (FQDN)
            ttl: Time to live (seconds)

        Returns:
            True if successful
        """
        self.logger.info(f"➕ Creating PTR record: {ip_address} → {hostname}")

        # Extract IP octets for reverse DNS
        ip_parts = ip_address.split(".")
        if len(ip_parts) == 4:
            # IPv4: <NAS_PRIMARY_IP> → 32.17.17.10.in-addr.arpa
            reverse_name = ".".join(reversed(ip_parts))
        else:
            self.logger.error(f"❌ Invalid IPv4 address: {ip_address}")
            return False

        params = {
            "api": "SYNO.DNS.Server.Record",
            "version": "1",
            "method": "create",
            "zone": reverse_zone,
            "type": "PTR",
            "name": reverse_name,
            "value": hostname,
            "ttl": ttl
        }

        result = self._call_dns_api("create", params)

        if result:
            self.logger.info(f"✅ PTR record created: {ip_address} → {hostname}")
            return True

        return False

    def ensure_dns_consistency(
        self,
        zone: str,
        hostname: str,
        ip_address: str,
        reverse_zone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ensure DNS consistency: Create both A and PTR records

        Similar to Active Directory DNS automatic PTR record creation

        Args:
            zone: Forward DNS zone
            hostname: Hostname (without zone)
            ip_address: IP address
            reverse_zone: Reverse DNS zone (auto-generated if not provided)

        Returns:
            Dictionary with creation results
        """
        self.logger.info(f"🔄 Ensuring DNS consistency for {hostname}.{zone} → {ip_address}")

        result = {
            "hostname": hostname,
            "ip_address": ip_address,
            "a_record_created": False,
            "ptr_record_created": False,
            "consistent": False
        }

        # Create A record
        a_created = self.create_a_record(zone, hostname, ip_address)
        result["a_record_created"] = a_created

        # Generate reverse zone if not provided
        if not reverse_zone:
            ip_parts = ip_address.split(".")
            if len(ip_parts) == 4:
                # For 10.17.17.x, use 17.17.10.in-addr.arpa
                reverse_zone = f"{ip_parts[1]}.{ip_parts[0]}.in-addr.arpa"

        # Create PTR record
        fqdn = f"{hostname}.{zone}"
        ptr_created = self.create_ptr_record(reverse_zone, ip_address, fqdn)
        result["ptr_record_created"] = ptr_created

        result["consistent"] = a_created and ptr_created

        if result["consistent"]:
            self.logger.info(f"✅ DNS consistency ensured: {hostname}.{zone} ↔ {ip_address}")
        else:
            self.logger.warning(f"⚠️  DNS consistency incomplete")

        return result

    def verify_dns_records(
        self,
        hostname: str,
        ip_address: str
    ) -> Dict[str, Any]:
        """
        Verify DNS records exist and are correct

        Args:
            hostname: Full hostname (FQDN)
            ip_address: IP address

        Returns:
            Verification result
        """
        from network_security_orchestrator import DNSResolver

        resolver = DNSResolver()

        # Forward DNS
        forward_result = resolver.resolve_hostname(hostname)

        # Reverse DNS
        reverse_result = resolver.reverse_dns_lookup(ip_address)

        # Consistency check
        consistency = resolver.verify_dns_consistency(hostname, ip_address)

        return {
            "hostname": hostname,
            "ip_address": ip_address,
            "forward_dns": forward_result,
            "reverse_dns": reverse_result,
            "consistency": consistency,
            "verified": consistency.get("consistent", False)
        }


def main():
    """CLI for NAS DNS management"""
    import argparse

    parser = argparse.ArgumentParser(description="NAS DNS Manager (Synology DSM)")
    parser.add_argument("--nas-host", default="<NAS_PRIMARY_IP>", help="NAS hostname or IP")
    parser.add_argument("--nas-port", type=int, default=5001, help="NAS HTTPS port")
    parser.add_argument("--username", help="DSM username")
    parser.add_argument("--password", help="DSM password")
    parser.add_argument("--list-zones", action="store_true", help="List DNS zones")
    parser.add_argument("--list-records", help="List records in zone")
    parser.add_argument("--create-a", nargs=3, metavar=("ZONE", "HOSTNAME", "IP"), help="Create A record")
    parser.add_argument("--create-ptr", nargs=4, metavar=("REVERSE_ZONE", "IP", "HOSTNAME", "TTL"), help="Create PTR record")
    parser.add_argument("--ensure-consistency", nargs=3, metavar=("ZONE", "HOSTNAME", "IP"), help="Ensure DNS consistency")

    args = parser.parse_args()

    manager = NASDNSManager(
        nas_host=args.nas_host,
        nas_port=args.nas_port,
        username=args.username,
        password=args.password
    )

    try:
        if args.list_zones:
            zones = manager.get_dns_zones()
            print(f"\n📋 DNS Zones ({len(zones)}):")
            for zone in zones:
                print(f"  - {zone.get('name', 'N/A')}")

        elif args.list_records:
            records = manager.get_dns_records(args.list_records)
            print(f"\n📋 DNS Records in {args.list_records} ({len(records)}):")
            for record in records:
                print(f"  - {record.get('name', 'N/A')} ({record.get('type', 'N/A')}) → {record.get('value', 'N/A')}")

        elif args.create_a:
            zone, hostname, ip = args.create_a
            success = manager.create_a_record(zone, hostname, ip)
            print(f"\n{'✅' if success else '❌'} A record creation: {success}")

        elif args.create_ptr:
            reverse_zone, ip, hostname, ttl = args.create_ptr
            success = manager.create_ptr_record(reverse_zone, ip, hostname, int(ttl))
            print(f"\n{'✅' if success else '❌'} PTR record creation: {success}")

        elif args.ensure_consistency:
            zone, hostname, ip = args.ensure_consistency
            result = manager.ensure_dns_consistency(zone, hostname, ip)
            print(f"\n🔄 DNS Consistency Result:")
            print(f"  A Record: {'✅' if result['a_record_created'] else '❌'}")
            print(f"  PTR Record: {'✅' if result['ptr_record_created'] else '❌'}")
            print(f"  Consistent: {'✅' if result['consistent'] else '❌'}")

        else:
            parser.print_help()

    finally:
        manager._logout()


if __name__ == "__main__":



    main()