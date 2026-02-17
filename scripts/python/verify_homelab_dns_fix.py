#!/usr/bin/env python3
"""
Verify Homelab DNS Fix
Tests DNS resolution after fixes are applied

Tags: #HOMELAB #DNS #VERIFICATION
"""

import sys
import subprocess
from pathlib import Path

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

logger = get_logger("VerifyHomelabDNSFix")


def test_dns_server(dns_server: str, test_domains: list) -> dict:
    """Test DNS server with multiple domains"""
    logger.info(f"🔍 Testing DNS server: {dns_server}")
    logger.info("-" * 70)

    results = {}
    for domain in test_domains:
        try:
            result = subprocess.run(
                ["nslookup", domain, dns_server],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0 and "Address:" in result.stdout:
                # Extract IP
                lines = result.stdout.split('\n')
                ip = None
                for line in lines:
                    if 'Address:' in line and dns_server not in line:
                        potential_ip = line.split('Address:')[-1].strip()
                        if potential_ip and potential_ip.replace('.', '').isdigit():
                            ip = potential_ip
                            break

                if ip:
                    logger.info(f"   ✅ {domain} -> {ip}")
                    results[domain] = {"success": True, "ip": ip}
                else:
                    logger.warning(f"   ⚠️  {domain} - Query returned but couldn't parse IP")
                    results[domain] = {"success": False, "error": "Parse error"}
            else:
                logger.error(f"   ❌ {domain} - DNS query failed")
                results[domain] = {"success": False, "error": result.stderr}
        except subprocess.TimeoutExpired:
            logger.error(f"   ❌ {domain} - DNS query timed out")
            results[domain] = {"success": False, "error": "Timeout"}
        except Exception as e:
            logger.error(f"   ❌ {domain} - Error: {e}")
            results[domain] = {"success": False, "error": str(e)}

    return results


def main():
    """Main verification function"""
    logger.info("=" * 70)
    logger.info("✅ HOMELAB DNS FIX VERIFICATION")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Testing DNS resolution after fixes...")
    logger.info("")

    test_domains = [
        "google.com",
        "proton.me",
        "digital.fidelity.com"
    ]

    # Test pfSense
    logger.info("=" * 70)
    logger.info("TESTING PFSENSE DNS (<NAS_IP>)")
    logger.info("=" * 70)
    logger.info("")
    pfsense_results = test_dns_server("<NAS_IP>", test_domains)
    logger.info("")

    # Test NAS
    logger.info("=" * 70)
    logger.info("TESTING NAS DNS (<NAS_PRIMARY_IP>)")
    logger.info("=" * 70)
    logger.info("")
    nas_results = test_dns_server("<NAS_PRIMARY_IP>", test_domains)
    logger.info("")

    # Summary
    logger.info("=" * 70)
    logger.info("📊 VERIFICATION SUMMARY")
    logger.info("=" * 70)
    logger.info("")

    pfsense_success = sum(1 for r in pfsense_results.values() if r.get("success"))
    nas_success = sum(1 for r in nas_results.values() if r.get("success"))

    logger.info(f"   pfSense DNS: {pfsense_success}/{len(test_domains)} successful")
    logger.info(f"   NAS DNS: {nas_success}/{len(test_domains)} successful")
    logger.info("")

    if pfsense_success == len(test_domains) and nas_success == len(test_domains):
        logger.info("✅ All DNS servers are working correctly!")
        logger.info("   Browser should now be able to resolve DNS")
        logger.info("")
        logger.info("💡 Next steps:")
        logger.info("   1. Flush DNS cache: ipconfig /flushdns")
        logger.info("   2. Test browser connectivity")
        logger.info("   3. Retry Fidelity credential extraction")
    else:
        logger.warning("⚠️  Some DNS queries are still failing")
        logger.info("")
        logger.info("If you just fixed the DNS services:")
        logger.info("   - Wait a few seconds for services to restart")
        logger.info("   - Run this script again to verify")
        logger.info("")
        logger.info("If issues persist:")
        logger.info("   - Check DNS service logs on pfSense/NAS")
        logger.info("   - Verify upstream DNS servers are reachable")
        logger.info("   - Check firewall rules allow DNS traffic")

    logger.info("")


if __name__ == "__main__":


    main()