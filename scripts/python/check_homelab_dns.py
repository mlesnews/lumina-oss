#!/usr/bin/env python3
"""
Check Homelab DNS Configuration
Tests DNS resolution through pfSense and NAS DNS servers

Tags: #HOMELAB #DNS #PFSENSE #NAS #NETWORK
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

logger = get_logger("CheckHomelabDNS")


def test_dns_server(hostname: str, dns_server: str) -> dict:
    """Test DNS resolution using specific DNS server"""
    logger.info(f"🔍 Testing DNS resolution for '{hostname}' via {dns_server}...")

    try:
        result = subprocess.run(
            ["nslookup", hostname, dns_server],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0 and "Address:" in result.stdout:
            # Extract IP address
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Address:' in line and dns_server not in line:
                    ip = line.split('Address:')[-1].strip()
                    if ip and ip.replace('.', '').isdigit():
                        logger.info(f"   ✅ Resolved to: {ip}")
                        return {"success": True, "ip": ip, "dns_server": dns_server}

            logger.warning(f"   ⚠️  Resolution returned but couldn't parse IP")
            return {"success": False, "error": "Could not parse IP", "output": result.stdout}
        else:
            logger.error(f"   ❌ DNS resolution failed")
            logger.debug(f"   Error output: {result.stderr}")
            return {"success": False, "error": result.stderr, "dns_server": dns_server}
    except subprocess.TimeoutExpired:
        logger.error(f"   ❌ DNS query timed out")
        return {"success": False, "error": "Timeout", "dns_server": dns_server}
    except Exception as e:
        logger.error(f"   ❌ Error: {e}")
        return {"success": False, "error": str(e), "dns_server": dns_server}


def main():
    """Main diagnostic function"""
    logger.info("=" * 70)
    logger.info("🔍 HOMELAB DNS CONFIGURATION CHECK")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Testing DNS resolution through homelab infrastructure:")
    logger.info("   - pfSense (primary/secondary)")
    logger.info("   - NAS (primary/secondary)")
    logger.info("")

    # Homelab DNS servers (typical setup)
    # Adjust these based on your actual configuration
    homelab_dns_servers = [
        "<NAS_IP>",  # Likely pfSense
        "<NAS_PRIMARY_IP>",  # Likely NAS (from earlier context)
    ]

    # Test sites
    test_sites = [
        "proton.me",
        "digital.fidelity.com",
        "google.com",
        "8.8.8.8"  # Google DNS for comparison
    ]

    results = {}

    # Test each DNS server
    logger.info("STEP 1: Testing Homelab DNS Servers")
    logger.info("-" * 70)

    for dns_server in homelab_dns_servers:
        logger.info(f"")
        logger.info(f"Testing DNS Server: {dns_server}")
        logger.info("-" * 40)

        results[dns_server] = {}
        for site in test_sites:
            if not site.replace('.', '').isdigit():  # Skip IP addresses
                results[dns_server][site] = test_dns_server(site, dns_server)

    logger.info("")

    # Test system default DNS
    logger.info("STEP 2: Testing System Default DNS")
    logger.info("-" * 70)
    for site in test_sites:
        if not site.replace('.', '').isdigit():
            try:
                ip = socket.gethostbyname(site)
                logger.info(f"   ✅ {site} -> {ip} (system default)")
            except Exception as e:
                logger.error(f"   ❌ {site} -> {e}")

    logger.info("")

    # Summary
    logger.info("=" * 70)
    logger.info("📊 SUMMARY")
    logger.info("=" * 70)

    for dns_server, sites in results.items():
        success_count = sum(1 for r in sites.values() if r.get("success"))
        total = len(sites)
        status = "✅" if success_count == total else "⚠️"
        logger.info(f"   {status} {dns_server}: {success_count}/{total} successful")

    logger.info("")

    # Recommendations
    failed_servers = []
    for dns_server, sites in results.items():
        failed = [site for site, result in sites.items() if not result.get("success")]
        if failed:
            failed_servers.append((dns_server, failed))

    if failed_servers:
        logger.warning("⚠️  Some DNS servers are failing to resolve sites")
        logger.info("")
        logger.info("💡 Recommendations:")
        logger.info("   1. Check pfSense DNS forwarder/recursor configuration")
        logger.info("   2. Verify NAS DNS service is running and forwarding correctly")
        logger.info("   3. Check DNS server connectivity: ping <NAS_IP> and <NAS_PRIMARY_IP>")
        logger.info("   4. Review DNS logs on pfSense and NAS")
        logger.info("   5. Consider adding fallback DNS (8.8.8.8, 1.1.1.1) to pfSense")
    else:
        logger.info("✅ All homelab DNS servers resolving correctly")

    logger.info("")


if __name__ == "__main__":


    main()