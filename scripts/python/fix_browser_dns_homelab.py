#!/usr/bin/env python3
"""
Fix Browser DNS for Homelab Issue
Temporarily configure browser to use working DNS while homelab DNS is down

Tags: #HOMELAB #DNS #BROWSER #FIX
"""

import sys
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

logger = get_logger("FixBrowserDNSHomelab")


def main():
    """Main function"""
    logger.info("=" * 70)
    logger.info("🔧 BROWSER DNS FIX FOR HOMELAB ISSUE")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Issue: Homelab DNS servers (pfSense/NAS) are timing out")
    logger.info("   - pfSense (<NAS_IP>): DNS queries timing out")
    logger.info("   - NAS (<NAS_PRIMARY_IP>): DNS queries timing out")
    logger.info("")
    logger.info("Solution: Configure browser to use working DNS")
    logger.info("   Options:")
    logger.info("   1. Use ProtonVPN DNS (10.2.0.1) - Currently working")
    logger.info("   2. Use public DNS (8.8.8.8, 1.1.1.1) - Always available")
    logger.info("   3. Fix homelab DNS servers (pfSense/NAS configuration)")
    logger.info("")
    logger.info("=" * 70)
    logger.info("📋 RECOMMENDATIONS")
    logger.info("=" * 70)
    logger.info("")
    logger.info("IMMEDIATE FIX (Browser):")
    logger.info("   1. Change Wi-Fi adapter DNS to use working servers:")
    logger.info("      Set-DnsClientServerAddress -InterfaceAlias 'Wi-Fi' -ServerAddresses '8.8.8.8','1.1.1.1'")
    logger.info("")
    logger.info("ROOT CAUSE FIX (Homelab):")
    logger.info("   1. Check pfSense DNS Resolver/Forwarder service:")
    logger.info("      - Services > DNS Resolver (or DNS Forwarder)")
    logger.info("      - Verify service is enabled and running")
    logger.info("      - Check 'Enable Forwarding Mode' if using forwarder")
    logger.info("      - Verify upstream DNS servers (8.8.8.8, 1.1.1.1)")
    logger.info("")
    logger.info("   2. Check NAS DNS service:")
    logger.info("      - Control Panel > Network > DNS Server")
    logger.info("      - Verify DNS service is running")
    logger.info("      - Check DNS forwarding configuration")
    logger.info("")
    logger.info("   3. Check firewall rules:")
    logger.info("      - Ensure UDP port 53 is allowed")
    logger.info("      - Check for any DNS filtering/blocking rules")
    logger.info("")
    logger.info("   4. Test DNS service directly:")
    logger.info("      - SSH to pfSense: dig @<NAS_IP> google.com")
    logger.info("      - SSH to NAS: dig @<NAS_PRIMARY_IP> google.com")
    logger.info("")
    logger.info("=" * 70)
    logger.info("")
    logger.info("💡 For now, browser automation will work better with:")
    logger.info("   - ProtonVPN DNS (10.2.0.1) - Already working")
    logger.info("   - Or public DNS (8.8.8.8, 1.1.1.1)")
    logger.info("")


if __name__ == "__main__":


    main()