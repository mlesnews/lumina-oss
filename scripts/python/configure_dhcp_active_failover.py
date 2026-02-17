#!/usr/bin/env python3
"""
DHCP Active Failover Configuration

Configures DHCP with active failover:
- Primary: pfSense (<NAS_IP>) - Range: <NAS_IP> - <NAS_IP>
- Fallback: NAS (<NAS_PRIMARY_IP>) - Range: <NAS_IP> - <NAS_IP>

Uses non-overlapping ranges to prevent conflicts when both are active.

Tags: #DHCP #FAILOVER #ACTIVE #NETWORK @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from configure_dhcp_pfsense_primary_nas_fallback import DHCPConfigurator
    from dhcp_failover_monitor import DHCPFailoverMonitor
    from lumina_logger import get_logger
    logger = get_logger("DHCPActiveFailover")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("DHCPActiveFailover")


def configure_active_failover(
    pfsense_ip: str = "<NAS_IP>",
    nas_ip: str = "<NAS_PRIMARY_IP>",
    subnet: str = "<NAS_IP>/24",
    gateway: str = "<NAS_IP>"
) -> Dict[str, Any]:
    """
    Configure DHCP with active failover using non-overlapping ranges

    Args:
        pfsense_ip: pfSense IP address
        nas_ip: NAS IP address
        subnet: Network subnet
        gateway: Default gateway

    Returns:
        Configuration result
    """
    logger.info("=" * 70)
    logger.info("🚀 DHCP ACTIVE FAILOVER CONFIGURATION")
    logger.info("=" * 70)

    # Non-overlapping ranges
    pfsense_range_start = "<NAS_IP>"
    pfsense_range_end = "<NAS_IP>"
    nas_range_start = "<NAS_IP>"
    nas_range_end = "<NAS_IP>"

    result = {
        "timestamp": None,
        "pfsense_config": {},
        "nas_config": {},
        "failover_monitor": {},
        "success": False
    }

    # Step 1: Configure pfSense (Primary)
    logger.info("\n📋 Step 1: Configuring pfSense as PRIMARY DHCP...")
    logger.info(f"  Range: {pfsense_range_start} - {pfsense_range_end}")

    pfsense_config = DHCPConfigurator(
        pfsense_ip=pfsense_ip,
        nas_ip=nas_ip,
        subnet=subnet,
        gateway=gateway,
        dhcp_range_start=pfsense_range_start,
        dhcp_range_end=pfsense_range_end
    )

    pfsense_result = pfsense_config.configure_pfsense_dhcp()
    result["pfsense_config"] = pfsense_result

    # Step 2: Configure NAS (Fallback with separate range)
    logger.info("\n📋 Step 2: Configuring NAS as FALLBACK DHCP...")
    logger.info(f"  Range: {nas_range_start} - {nas_range_end}")
    logger.info("  ⚠️  NAS DHCP will be DISABLED by default")
    logger.info("  ⚠️  Failover monitor will enable it automatically if pfSense fails")

    nas_config = DHCPConfigurator(
        pfsense_ip=pfsense_ip,
        nas_ip=nas_ip,
        subnet=subnet,
        gateway=gateway,
        dhcp_range_start=nas_range_start,
        dhcp_range_end=nas_range_end
    )

    nas_result = nas_config.configure_nas_dhcp_fallback()
    result["nas_config"] = nas_result

    # Step 3: Initialize Failover Monitor
    logger.info("\n📋 Step 3: Initializing Failover Monitor...")
    monitor = DHCPFailoverMonitor(
        pfsense_ip=pfsense_ip,
        nas_ip=nas_ip,
        check_interval=30,  # Check every 30 seconds
        failure_threshold=3,  # 3 failures = down
        recovery_threshold=3,  # 3 successes = recovered
        enable_nas_dhcp_on_failover=True
    )

    # Test monitor
    monitor_status = monitor.check_and_failover()
    result["failover_monitor"] = monitor_status

    logger.info("✅ Failover Monitor initialized")
    logger.info(f"  Check interval: 30 seconds")
    logger.info(f"  Failure threshold: 3 consecutive failures")
    logger.info(f"  Recovery threshold: 3 consecutive successes")

    # Step 4: Summary
    result["success"] = (
        pfsense_result.get("success", False) and
        nas_result.get("success", False)
    )

    logger.info("\n" + "=" * 70)
    if result["success"]:
        logger.info("✅ ACTIVE FAILOVER CONFIGURATION COMPLETE")
    else:
        logger.info("⚠️  CONFIGURATION REQUIRES MANUAL STEPS")
    logger.info("=" * 70)

    logger.info("\n📋 Active Failover Configuration:")
    logger.info(f"  Primary DHCP: {pfsense_ip} (pfSense)")
    logger.info(f"    Range: {pfsense_range_start} - {pfsense_range_end}")
    logger.info(f"    Status: ACTIVE")
    logger.info(f"  Fallback DHCP: {nas_ip} (NAS)")
    logger.info(f"    Range: {nas_range_start} - {nas_range_end}")
    logger.info(f"    Status: STANDBY (auto-enabled on failover)")
    logger.info(f"  Failover Monitor: ENABLED")
    logger.info(f"    Auto-enable NAS DHCP when pfSense fails")
    logger.info(f"    Auto-disable NAS DHCP when pfSense recovers")

    logger.info("\n🚀 Next Steps:")
    logger.info("  1. Start failover monitor:")
    logger.info("     python scripts/python/dhcp_failover_monitor.py")
    logger.info("  2. Or run as cron service (every minute):")
    logger.info("     python scripts/python/deploy_activate_all_cron_services.py")
    logger.info("  3. Monitor status:")
    logger.info("     python scripts/python/dhcp_failover_monitor.py --once")

    return result


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Configure DHCP Active Failover"
    )
    parser.add_argument(
        "--pfsense-ip",
        default="<NAS_IP>",
        help="pfSense IP address"
    )
    parser.add_argument(
        "--nas-ip",
        default="<NAS_PRIMARY_IP>",
        help="NAS IP address"
    )
    parser.add_argument(
        "--subnet",
        default="<NAS_IP>/24",
        help="Network subnet"
    )
    parser.add_argument(
        "--gateway",
        default="<NAS_IP>",
        help="Default gateway"
    )

    args = parser.parse_args()

    result = configure_active_failover(
        pfsense_ip=args.pfsense_ip,
        nas_ip=args.nas_ip,
        subnet=args.subnet,
        gateway=args.gateway
    )

    return 0 if result.get("success", False) else 1


if __name__ == "__main__":


    sys.exit(main())