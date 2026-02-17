#!/usr/bin/env python3
"""
Fix Homelab DNS Services
Diagnoses and provides fixes for pfSense and NAS DNS services

Tags: #HOMELAB #DNS #PFSENSE #NAS #NETWORK #FIX
"""

import sys
import subprocess
import socket
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

logger = get_logger("FixHomelabDNSServices")


def check_dns_port(host: str, port: int = 53) -> dict:
    """Check if DNS port is open and responding"""
    logger.info(f"🔍 Checking DNS port {port} on {host}...")

    try:
        # Try UDP (DNS primary protocol)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        sock.connect((host, port))
        sock.close()
        logger.info(f"   ✅ UDP port {port} is open")
        return {"success": True, "protocol": "UDP", "port": port}
    except Exception as e:
        logger.debug(f"   UDP check: {e}")

    try:
        # Try TCP (DNS secondary protocol)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            logger.info(f"   ✅ TCP port {port} is open")
            return {"success": True, "protocol": "TCP", "port": port}
        else:
            logger.warning(f"   ⚠️  TCP port {port} connection failed (code: {result})")
    except Exception as e:
        logger.debug(f"   TCP check: {e}")

    logger.error(f"   ❌ DNS port {port} is not responding")
    return {"success": False, "port": port}


def test_dns_query(host: str, test_domain: str = "google.com") -> dict:
    """Test DNS query to server"""
    logger.info(f"🔍 Testing DNS query to {host} for {test_domain}...")

    try:
        result = subprocess.run(
            ["nslookup", test_domain, host],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0 and "Address:" in result.stdout:
            # Extract IP
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Address:' in line and host not in line:
                    ip = line.split('Address:')[-1].strip()
                    if ip and ip.replace('.', '').isdigit():
                        logger.info(f"   ✅ DNS query successful: {test_domain} -> {ip}")
                        return {"success": True, "ip": ip, "domain": test_domain}

            logger.warning(f"   ⚠️  Query returned but couldn't parse IP")
            return {"success": False, "error": "Parse error", "output": result.stdout}
        else:
            logger.error(f"   ❌ DNS query failed")
            logger.debug(f"   Error: {result.stderr}")
            return {"success": False, "error": result.stderr}
    except subprocess.TimeoutExpired:
        logger.error(f"   ❌ DNS query timed out")
        return {"success": False, "error": "Timeout"}
    except Exception as e:
        logger.error(f"   ❌ Error: {e}")
        return {"success": False, "error": str(e)}


def check_pfsense_dns():
    """Check pfSense DNS service"""
    logger.info("=" * 70)
    logger.info("🔍 CHECKING PFSENSE DNS (<NAS_IP>)")
    logger.info("=" * 70)
    logger.info("")

    # Check connectivity
    logger.info("STEP 1: Connectivity Check")
    logger.info("-" * 70)
    try:
        result = subprocess.run(
            ["ping", "-n", "2", "<NAS_IP>"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "Reply from" in result.stdout:
            logger.info("   ✅ pfSense is reachable")
        else:
            logger.error("   ❌ pfSense is not reachable")
            return False
    except Exception as e:
        logger.error(f"   ❌ Ping failed: {e}")
        return False

    logger.info("")

    # Check DNS port
    logger.info("STEP 2: DNS Port Check")
    logger.info("-" * 70)
    port_check = check_dns_port("<NAS_IP>", 53)

    logger.info("")

    # Test DNS query
    logger.info("STEP 3: DNS Query Test")
    logger.info("-" * 70)
    dns_test = test_dns_query("<NAS_IP>", "google.com")

    logger.info("")

    # Provide fix instructions
    logger.info("=" * 70)
    logger.info("📋 PFSENSE DNS FIX INSTRUCTIONS")
    logger.info("=" * 70)
    logger.info("")

    if not port_check.get("success") or not dns_test.get("success"):
        logger.warning("⚠️  pfSense DNS service is not working")
        logger.info("")
        logger.info("FIX STEPS:")
        logger.info("   1. Access pfSense Web UI: https://<NAS_IP>")
        logger.info("   2. Navigate to: Services > DNS Resolver (or DNS Forwarder)")
        logger.info("   3. Check the following:")
        logger.info("      - Service is ENABLED")
        logger.info("      - Service is RUNNING (check status)")
        logger.info("      - Upstream DNS servers are configured:")
        logger.info("        * 8.8.8.8 (Google)")
        logger.info("        * 1.1.1.1 (Cloudflare)")
        logger.info("        * 8.8.4.4 (Google secondary)")
        logger.info("   4. If using DNS Forwarder:")
        logger.info("      - Enable 'Enable Forwarding Mode'")
        logger.info("      - Add upstream DNS servers")
        logger.info("   5. If using DNS Resolver:")
        logger.info("      - Check 'Enable Forwarding Mode' if you want to forward")
        logger.info("      - Or configure root servers for recursive resolution")
        logger.info("   6. Save and apply changes")
        logger.info("   7. Restart DNS service if needed")
        logger.info("")
        logger.info("ALTERNATIVE: Restart DNS service via SSH")
        logger.info("   ssh admin@<NAS_IP>")
        logger.info("   # For DNS Resolver:")
        logger.info("   service unbound restart")
        logger.info("   # For DNS Forwarder:")
        logger.info("   service dnsmasq restart")
        logger.info("")
    else:
        logger.info("✅ pfSense DNS is working correctly")

    return port_check.get("success") and dns_test.get("success")


def check_nas_dns():
    """Check NAS DNS service"""
    logger.info("=" * 70)
    logger.info("🔍 CHECKING NAS DNS (<NAS_PRIMARY_IP>)")
    logger.info("=" * 70)
    logger.info("")

    # Check connectivity
    logger.info("STEP 1: Connectivity Check")
    logger.info("-" * 70)
    try:
        result = subprocess.run(
            ["ping", "-n", "2", "<NAS_PRIMARY_IP>"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "Reply from" in result.stdout:
            logger.info("   ✅ NAS is reachable")
        else:
            logger.error("   ❌ NAS is not reachable")
            return False
    except Exception as e:
        logger.error(f"   ❌ Ping failed: {e}")
        return False

    logger.info("")

    # Check DNS port
    logger.info("STEP 2: DNS Port Check")
    logger.info("-" * 70)
    port_check = check_dns_port("<NAS_PRIMARY_IP>", 53)

    logger.info("")

    # Test DNS query
    logger.info("STEP 3: DNS Query Test")
    logger.info("-" * 70)
    dns_test = test_dns_query("<NAS_PRIMARY_IP>", "google.com")

    logger.info("")

    # Provide fix instructions
    logger.info("=" * 70)
    logger.info("📋 NAS DNS FIX INSTRUCTIONS")
    logger.info("=" * 70)
    logger.info("")

    if not port_check.get("success") or not dns_test.get("success"):
        logger.warning("⚠️  NAS DNS service is not working")
        logger.info("")
        logger.info("FIX STEPS:")
        logger.info("   1. Access NAS Web UI: https://<NAS_PRIMARY_IP>:5001 (or DSM port)")
        logger.info("   2. Navigate to: Control Panel > Network > DNS Server")
        logger.info("   3. Check the following:")
        logger.info("      - DNS service is ENABLED")
        logger.info("      - DNS service is RUNNING")
        logger.info("      - Upstream DNS servers are configured:")
        logger.info("        * 8.8.8.8 (Google)")
        logger.info("        * 1.1.1.1 (Cloudflare)")
        logger.info("        * 8.8.4.4 (Google secondary)")
        logger.info("   4. Save and apply changes")
        logger.info("   5. Restart DNS service if needed")
        logger.info("")
        logger.info("ALTERNATIVE: Restart DNS service via SSH")
        logger.info("   ssh admin@<NAS_PRIMARY_IP>")
        logger.info("   sudo systemctl restart dnsmasq")
        logger.info("   # Or for Synology:")
        logger.info("   sudo synoservice --restart dnsmasq")
        logger.info("")
    else:
        logger.info("✅ NAS DNS is working correctly")

    return port_check.get("success") and dns_test.get("success")


def main():
    """Main diagnostic and fix function"""
    logger.info("=" * 70)
    logger.info("🔧 HOMELAB DNS SERVICES FIX")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Diagnosing and fixing DNS services on:")
    logger.info("   - pfSense (<NAS_IP>)")
    logger.info("   - NAS (<NAS_PRIMARY_IP>)")
    logger.info("")

    # Check pfSense
    pfsense_ok = check_pfsense_dns()
    logger.info("")

    # Check NAS
    nas_ok = check_nas_dns()
    logger.info("")

    # Summary
    logger.info("=" * 70)
    logger.info("📊 SUMMARY")
    logger.info("=" * 70)
    logger.info("")
    logger.info(f"   pfSense DNS: {'✅ Working' if pfsense_ok else '❌ Not Working'}")
    logger.info(f"   NAS DNS: {'✅ Working' if nas_ok else '❌ Not Working'}")
    logger.info("")

    if pfsense_ok and nas_ok:
        logger.info("✅ All homelab DNS services are working!")
        logger.info("   Browser should now be able to resolve DNS correctly")
    else:
        logger.warning("⚠️  Some DNS services need attention")
        logger.info("   Follow the fix instructions above for each server")
        logger.info("")
        logger.info("💡 After fixing, test with:")
        logger.info("   nslookup google.com <NAS_IP>")
        logger.info("   nslookup google.com <NAS_PRIMARY_IP>")

    logger.info("")


if __name__ == "__main__":


    main()