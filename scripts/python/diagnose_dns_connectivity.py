#!/usr/bin/env python3
"""
Diagnose DNS and IPv4 Connectivity Issues
Checks DNS resolution, IPv4 connectivity, and browser-specific issues

Tags: #NETWORK #DNS #TROUBLESHOOTING
"""

import sys
import socket
import subprocess
from pathlib import Path

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DiagnoseDNSConnectivity")


def check_dns_resolution(hostname: str) -> dict:
    """Check DNS resolution for a hostname"""
    logger.info(f"🔍 Checking DNS resolution for: {hostname}")

    try:
        # IPv4 resolution
        ipv4 = socket.gethostbyname(hostname)
        logger.info(f"   ✅ IPv4: {ipv4}")

        # IPv6 resolution (if available)
        try:
            ipv6 = socket.getaddrinfo(hostname, None, socket.AF_INET6)[0][4][0]
            logger.info(f"   ✅ IPv6: {ipv6}")
        except:
            logger.info(f"   ℹ️  IPv6: Not available")

        return {"success": True, "ipv4": ipv4, "hostname": hostname}
    except socket.gaierror as e:
        logger.error(f"   ❌ DNS resolution failed: {e}")
        return {"success": False, "error": str(e), "hostname": hostname}


def check_connectivity(hostname: str, port: int = 443) -> dict:
    """Check TCP connectivity to hostname:port"""
    logger.info(f"🔍 Checking connectivity to: {hostname}:{port}")

    try:
        # Resolve hostname
        ip = socket.gethostbyname(hostname)

        # Try to connect
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((ip, port))
        sock.close()

        if result == 0:
            logger.info(f"   ✅ Connection successful to {ip}:{port}")
            return {"success": True, "ip": ip, "port": port}
        else:
            logger.error(f"   ❌ Connection failed (error code: {result})")
            return {"success": False, "error_code": result, "ip": ip, "port": port}
    except Exception as e:
        logger.error(f"   ❌ Connectivity check failed: {e}")
        return {"success": False, "error": str(e)}


def check_browser_dns():
    """Check if browser might have DNS issues"""
    logger.info("🔍 Checking browser DNS configuration...")

    # Check if Neo browser is running
    try:
        import psutil
        neo_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                if 'neo' in (proc.info['name'] or '').lower():
                    neo_processes.append(proc.info['pid'])
            except:
                pass

        if neo_processes:
            logger.info(f"   ✅ Neo browser running ({len(neo_processes)} process(es))")
        else:
            logger.info("   ℹ️  Neo browser not running")
    except ImportError:
        logger.warning("   ⚠️  psutil not available")

    # Check DNS servers
    try:
        result = subprocess.run(
            ["ipconfig", "/all"],
            capture_output=True,
            text=True,
            timeout=5
        )
        dns_servers = []
        for line in result.stdout.split('\n'):
            if 'DNS Servers' in line:
                dns_servers.append(line.strip())

        if dns_servers:
            logger.info(f"   DNS Servers configured:")
            for dns in dns_servers[:3]:  # Show first 3
                logger.info(f"      {dns}")
    except Exception as e:
        logger.debug(f"   Could not check DNS servers: {e}")


def main():
    """Main diagnostic function"""
    logger.info("=" * 70)
    logger.info("🔍 DNS AND CONNECTIVITY DIAGNOSTIC")
    logger.info("=" * 70)
    logger.info("")

    # Test sites
    test_sites = [
        "proton.me",
        "digital.fidelity.com",
        "google.com",
        "8.8.8.8"  # Google DNS
    ]

    results = {
        "dns": {},
        "connectivity": {}
    }

    # Check DNS resolution
    logger.info("STEP 1: DNS Resolution Tests")
    logger.info("-" * 70)
    for site in test_sites:
        if not site.replace('.', '').isdigit():  # Skip IP addresses
            results["dns"][site] = check_dns_resolution(site)
    logger.info("")

    # Check connectivity
    logger.info("STEP 2: Connectivity Tests")
    logger.info("-" * 70)
    for site in test_sites:
        if not site.replace('.', '').isdigit():  # Skip IP addresses
            results["connectivity"][site] = check_connectivity(site, 443)
    logger.info("")

    # Check browser DNS
    logger.info("STEP 3: Browser DNS Configuration")
    logger.info("-" * 70)
    check_browser_dns()
    logger.info("")

    # Summary
    logger.info("=" * 70)
    logger.info("📊 SUMMARY")
    logger.info("=" * 70)

    dns_success = sum(1 for r in results["dns"].values() if r.get("success"))
    conn_success = sum(1 for r in results["connectivity"].values() if r.get("success"))

    logger.info(f"   DNS Resolution: {dns_success}/{len(results['dns'])} successful")
    logger.info(f"   Connectivity: {conn_success}/{len(results['connectivity'])} successful")
    logger.info("")

    if dns_success < len(results['dns']) or conn_success < len(results['connectivity']):
        logger.warning("⚠️  Some tests failed - DNS or connectivity issues detected")
        logger.info("")
        logger.info("💡 Recommendations:")
        logger.info("   1. Flush DNS cache: ipconfig /flushdns")
        logger.info("   2. Check VPN connection")
        logger.info("   3. Restart network adapter")
        logger.info("   4. Check firewall settings")
    else:
        logger.info("✅ All tests passed - DNS and connectivity working")

    logger.info("")


if __name__ == "__main__":


    main()