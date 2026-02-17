#!/usr/bin/env python3
"""
DHCP Configuration: pfSense Primary, NAS Fallback

Configures DHCP with:
- Primary: pfSense (<NAS_IP>)
- Fallback: NAS (<NAS_PRIMARY_IP>)

This script ensures proper DHCP failover configuration.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from pfsense_azure_vault_integration import PFSenseAzureVaultIntegration
    PFSENSE_AVAILABLE = True
except ImportError:
    PFSENSE_AVAILABLE = False
    print("WARNING: pfSense integration not available")

try:
    from manus_configure_pfsense_dhcp import MANUSPFSenseDHCPConfigurator
    MANUS_PFSENSE_AVAILABLE = True
except ImportError:
    MANUS_PFSENSE_AVAILABLE = False

try:
    from nas_azure_vault_integration import NASAzureVaultIntegration
    NAS_AVAILABLE = True
except ImportError:
    NAS_AVAILABLE = False
    print("WARNING: NAS integration not available")

try:
    from lumina_logger import get_logger
    logger = get_logger("DHCPConfigurator")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("DHCPConfigurator")


class DHCPConfigurator:
    """
    Configure DHCP with pfSense as primary and NAS as fallback
    """

    def __init__(
        self,
        pfsense_ip: str = "<NAS_IP>",
        nas_ip: str = "<NAS_PRIMARY_IP>",
        subnet: str = "<NAS_IP>/24",
        gateway: str = "<NAS_IP>",
        dns_primary: str = "<NAS_IP>",
        dns_secondary: str = "<NAS_PRIMARY_IP>",
        dhcp_range_start: str = "<NAS_IP>",
        dhcp_range_end: str = "<NAS_IP>",
        lease_time: int = 86400  # 24 hours
    ):
        """
        Initialize DHCP Configurator

        Args:
            pfsense_ip: pfSense IP address
            nas_ip: NAS IP address
            subnet: Network subnet (CIDR notation)
            gateway: Default gateway
            dns_primary: Primary DNS server
            dns_secondary: Secondary DNS server
            dhcp_range_start: Start of DHCP range
            dhcp_range_end: End of DHCP range
            lease_time: DHCP lease time in seconds
        """
        self.pfsense_ip = pfsense_ip
        self.nas_ip = nas_ip
        self.subnet = subnet
        self.gateway = gateway
        self.dns_primary = dns_primary
        self.dns_secondary = dns_secondary
        self.dhcp_range_start = dhcp_range_start
        self.dhcp_range_end = dhcp_range_end
        self.lease_time = lease_time

        # Initialize integrations
        self.pfsense = None
        if PFSENSE_AVAILABLE:
            self.pfsense = PFSenseAzureVaultIntegration(pfsense_ip=pfsense_ip)

        self.nas = None
        if NAS_AVAILABLE:
            self.nas = NASAzureVaultIntegration(nas_ip=nas_ip)

        logger.info(f"DHCP Configurator initialized")
        logger.info(f"  Primary DHCP: {pfsense_ip} (pfSense)")
        logger.info(f"  Fallback DHCP: {nas_ip} (NAS)")
        logger.info(f"  Subnet: {subnet}")
        logger.info(f"  DHCP Range: {dhcp_range_start} - {dhcp_range_end}")

    def configure_pfsense_dhcp(self) -> Dict[str, Any]:
        """
        Configure pfSense as primary DHCP server

        Uses MANUS/NEO browser automation if SSH is not available

        Returns:
            Configuration result
        """
        logger.info("🔧 Configuring pfSense as PRIMARY DHCP server...")

        result = {
            "success": False,
            "pfsense_ip": self.pfsense_ip,
            "method": None,
            "commands": [],
            "output": []
        }

        # Method 1: Try MANUS/NEO browser automation (preferred when SSH unavailable)
        if MANUS_PFSENSE_AVAILABLE:
            logger.info("🚀 Attempting MANUS/NEO browser automation...")
            try:
                manus_config = MANUSPFSenseDHCPConfigurator(
                    pfsense_ip=self.pfsense_ip,
                    pfsense_port=443,
                    dhcp_range_start=self.dhcp_range_start,
                    dhcp_range_end=self.dhcp_range_end,
                    gateway=self.gateway,
                    dns_primary=self.dns_primary,
                    dns_secondary=self.dns_secondary
                )

                manus_result = manus_config.configure_dhcp_complete()
                result["method"] = "manus_neo_browser"
                result["manus_result"] = manus_result

                if manus_result.get("success"):
                    result["success"] = True
                    logger.info("✅ pfSense DHCP configured via MANUS/NEO browser automation")
                    return result
                else:
                    logger.warning("⚠️  MANUS automation had issues, trying SSH fallback...")
            except Exception as e:
                logger.warning(f"⚠️  MANUS automation failed: {e}, trying SSH fallback...")

        # Method 2: Try SSH (if available)
        if self.pfsense:
            logger.info("🔧 Attempting SSH configuration...")
            try:
                # Check current DHCP status
                logger.info("Checking current pfSense DHCP status...")
                status_cmd = "ps aux | grep dhcpd | grep -v grep"
                status_result = self.pfsense.execute_ssh_command(status_cmd)
                result["commands"].append(status_cmd)
                result["output"].append(status_result)

                # Enable DHCP service (if not already enabled)
                enable_dhcp_cmd = "/usr/local/sbin/pfSsh.php playback enableinterface dhcp"
                enable_result = self.pfsense.execute_ssh_command(enable_dhcp_cmd)
                result["commands"].append(enable_dhcp_cmd)
                result["output"].append(enable_result)

                # Restart DHCP service
                restart_dhcp_cmd = "/etc/rc.d/dhcpd restart"
                restart_result = self.pfsense.execute_ssh_command(restart_dhcp_cmd)
                result["commands"].append(restart_dhcp_cmd)
                result["output"].append(restart_result)

                # Verify DHCP is running
                verify_cmd = "ps aux | grep dhcpd | grep -v grep"
                verify_result = self.pfsense.execute_ssh_command(verify_cmd)
                result["commands"].append(verify_cmd)
                result["output"].append(verify_result)

                if verify_result.get("success") and verify_result.get("output"):
                    result["success"] = True
                    result["method"] = "ssh"
                    logger.info("✅ pfSense DHCP configured via SSH")
                    return result

            except Exception as e:
                logger.warning(f"⚠️  SSH configuration failed: {e}")

        # Method 3: Provide manual configuration instructions
        logger.warning("⚠️  Automated configuration unavailable, providing manual instructions")
        result["method"] = "manual"
        result["manual_config"] = {
            "url": f"https://{self.pfsense_ip}",
            "path": "Services > DHCP Server",
            "settings": {
                "Enable DHCP server": True,
                "Subnet": self.subnet,
                "Range": f"{self.dhcp_range_start} - {self.dhcp_range_end}",
                "Gateway": self.gateway,
                "DNS Servers": f"{self.dns_primary} {self.dns_secondary}",
                "Lease Time": f"{self.lease_time} seconds"
            },
            "note": "Use MANUS automation: python scripts/python/manus_configure_pfsense_dhcp.py"
        }
        result["success"] = False  # Manual configuration required

        return result

    def configure_nas_dhcp_fallback(self) -> Dict[str, Any]:
        """
        Configure NAS as fallback DHCP server

        Returns:
            Configuration result
        """
        logger.info("🔧 Configuring NAS as FALLBACK DHCP server...")

        if not self.nas:
            return {
                "success": False,
                "error": "NAS integration not available"
            }

        result = {
            "success": False,
            "nas_ip": self.nas_ip,
            "method": "ssh",
            "commands": [],
            "output": []
        }

        try:
            # Get SSH client
            ssh_client = self.nas.get_ssh_client()
            if not ssh_client:
                return {
                    "success": False,
                    "error": "Could not establish SSH connection to NAS"
                }

            # Check if DHCP Server package is installed
            check_package_cmd = "synopkg list | grep -i dhcp"
            stdin, stdout, stderr = ssh_client.exec_command(check_package_cmd)
            package_output = stdout.read().decode('utf-8')
            result["commands"].append(check_package_cmd)
            result["output"].append({
                "command": check_package_cmd,
                "output": package_output
            })

            # Check DHCP service status
            check_status_cmd = "synoservice --status dhcpd"
            stdin, stdout, stderr = ssh_client.exec_command(check_status_cmd)
            status_output = stdout.read().decode('utf-8')
            result["commands"].append(check_status_cmd)
            result["output"].append({
                "command": check_status_cmd,
                "output": status_output
            })

            # Note: NAS DHCP Server configuration is typically done via DSM web UI
            # We can check status and provide configuration instructions

            ssh_client.close()

            result["success"] = True
            result["manual_config"] = {
                "url": f"https://{self.nas_ip}:5001",
                "path": "Package Center > DHCP Server > Settings",
                "note": "Configure as FALLBACK DHCP server (only active if pfSense fails)",
                "settings": {
                    "Enable DHCP server": True,
                    "Subnet": self.subnet,
                    "Range": f"{self.dhcp_range_start} - {self.dhcp_range_end}",
                    "Gateway": self.gateway,
                    "DNS Servers": f"{self.dns_primary} {self.dns_secondary}",
                    "Lease Time": f"{self.lease_time} seconds",
                    "Priority": "FALLBACK (only if pfSense DHCP unavailable)"
                }
            }

            logger.info("✅ NAS DHCP fallback configuration prepared")
            logger.info("⚠️  Note: NAS DHCP Server must be configured via DSM web UI")

        except Exception as e:
            logger.error(f"❌ Error configuring NAS DHCP: {e}")
            result["error"] = str(e)
            result["success"] = False

        return result

    def verify_dhcp_configuration(self) -> Dict[str, Any]:
        """
        Verify DHCP configuration on both systems

        Returns:
            Verification result
        """
        logger.info("🔍 Verifying DHCP configuration...")

        result = {
            "pfsense": {},
            "nas": {},
            "overall": False
        }

        # Verify pfSense DHCP
        if self.pfsense:
            try:
                verify_cmd = "ps aux | grep dhcpd | grep -v grep"
                verify_result = self.pfsense.execute_ssh_command(verify_cmd)
                result["pfsense"] = {
                    "dhcp_running": bool(verify_result.get("output")),
                    "output": verify_result.get("output", ""),
                    "success": verify_result.get("success", False)
                }
            except Exception as e:
                result["pfsense"] = {
                    "error": str(e),
                    "success": False
                }

        # Verify NAS DHCP
        if self.nas:
            try:
                ssh_client = self.nas.get_ssh_client()
                if ssh_client:
                    check_status_cmd = "synoservice --status dhcpd"
                    stdin, stdout, stderr = ssh_client.exec_command(check_status_cmd)
                    status_output = stdout.read().decode('utf-8')
                    ssh_client.close()

                    result["nas"] = {
                        "dhcp_available": "dhcp" in status_output.lower(),
                        "output": status_output,
                        "success": True
                    }
                else:
                    result["nas"] = {
                        "error": "Could not establish SSH connection",
                        "success": False
                    }
            except Exception as e:
                result["nas"] = {
                    "error": str(e),
                    "success": False
                }

        # Overall status
        pfsense_ok = result["pfsense"].get("success", False) or result["pfsense"].get("dhcp_running", False)
        nas_ok = result["nas"].get("success", False) or result["nas"].get("dhcp_available", False)

        result["overall"] = pfsense_ok  # Primary must be working

        if result["overall"]:
            logger.info("✅ DHCP configuration verified")
            if pfsense_ok:
                logger.info("  ✅ pfSense DHCP: PRIMARY (active)")
            if nas_ok:
                logger.info("  ✅ NAS DHCP: FALLBACK (ready)")
        else:
            logger.warning("⚠️  DHCP configuration needs attention")

        return result

    def configure_dhcp_complete(self) -> Dict[str, Any]:
        """
        Complete DHCP configuration workflow

        Returns:
            Complete configuration result
        """
        logger.info("=" * 70)
        logger.info("🚀 DHCP CONFIGURATION: pfSense Primary, NAS Fallback")
        logger.info("=" * 70)

        result = {
            "timestamp": datetime.now().isoformat(),
            "pfsense_primary": {},
            "nas_fallback": {},
            "verification": {},
            "success": False,
            "manual_steps": []
        }

        # Step 1: Configure pfSense as primary
        logger.info("\n📋 Step 1: Configuring pfSense as PRIMARY DHCP...")
        pfsense_result = self.configure_pfsense_dhcp()
        result["pfsense_primary"] = pfsense_result

        if not pfsense_result.get("success"):
            logger.error("❌ Failed to configure pfSense DHCP")
            result["error"] = "pfSense DHCP configuration failed"
            return result

        # Step 2: Configure NAS as fallback
        logger.info("\n📋 Step 2: Configuring NAS as FALLBACK DHCP...")
        nas_result = self.configure_nas_dhcp_fallback()
        result["nas_fallback"] = nas_result

        # Step 3: Verify configuration
        logger.info("\n📋 Step 3: Verifying DHCP configuration...")
        verification_result = self.verify_dhcp_configuration()
        result["verification"] = verification_result

        # Collect manual steps
        if pfsense_result.get("manual_config"):
            result["manual_steps"].append({
                "system": "pfSense",
                "config": pfsense_result["manual_config"]
            })

        if nas_result.get("manual_config"):
            result["manual_steps"].append({
                "system": "NAS",
                "config": nas_result["manual_config"]
            })

        # Overall success
        result["success"] = (
            pfsense_result.get("success", False) and
            verification_result.get("overall", False)
        )

        # Summary
        logger.info("\n" + "=" * 70)
        if result["success"]:
            logger.info("✅ DHCP CONFIGURATION COMPLETE")
        else:
            logger.info("⚠️  DHCP CONFIGURATION REQUIRES MANUAL STEPS")
        logger.info("=" * 70)

        logger.info("\n📋 Configuration Summary:")
        logger.info(f"  Primary DHCP: {self.pfsense_ip} (pfSense)")
        logger.info(f"  Fallback DHCP: {self.nas_ip} (NAS)")
        logger.info(f"  Subnet: {self.subnet}")
        logger.info(f"  DHCP Range: {self.dhcp_range_start} - {self.dhcp_range_end}")

        if result["manual_steps"]:
            logger.info("\n⚠️  Manual Configuration Required:")
            for step in result["manual_steps"]:
                logger.info(f"\n  {step['system']}:")
                logger.info(f"    URL: {step['config']['url']}")
                logger.info(f"    Path: {step['config']['path']}")
                if "settings" in step["config"]:
                    logger.info("    Settings:")
                    for key, value in step["config"]["settings"].items():
                        logger.info(f"      {key}: {value}")

        return result


def main():
    try:
        """Main function"""
        import argparse

        parser = argparse.ArgumentParser(
            description="Configure DHCP: pfSense Primary, NAS Fallback"
        )
        parser.add_argument(
            "--pfsense-ip",
            default="<NAS_IP>",
            help="pfSense IP address (default: <NAS_IP>)"
        )
        parser.add_argument(
            "--nas-ip",
            default="<NAS_PRIMARY_IP>",
            help="NAS IP address (default: <NAS_PRIMARY_IP>)"
        )
        parser.add_argument(
            "--subnet",
            default="<NAS_IP>/24",
            help="Network subnet (default: <NAS_IP>/24)"
        )
        parser.add_argument(
            "--gateway",
            default="<NAS_IP>",
            help="Default gateway (default: <NAS_IP>)"
        )
        parser.add_argument(
            "--dhcp-range-start",
            default="<NAS_IP>",
            help="DHCP range start (default: <NAS_IP>)"
        )
        parser.add_argument(
            "--dhcp-range-end",
            default="<NAS_IP>",
            help="DHCP range end (default: <NAS_IP>)"
        )
        parser.add_argument(
            "--verify-only",
            action="store_true",
            help="Only verify current configuration (no changes)"
        )
        parser.add_argument(
            "--output",
            help="Output file for configuration results (JSON)"
        )

        args = parser.parse_args()

        # Initialize configurator
        configurator = DHCPConfigurator(
            pfsense_ip=args.pfsense_ip,
            nas_ip=args.nas_ip,
            subnet=args.subnet,
            gateway=args.gateway,
            dhcp_range_start=args.dhcp_range_start,
            dhcp_range_end=args.dhcp_range_end
        )

        if args.verify_only:
            # Only verify
            result = configurator.verify_dhcp_configuration()
            print("\n🔍 DHCP Verification Result:")
            print(json.dumps(result, indent=2))
        else:
            # Full configuration
            result = configurator.configure_dhcp_complete()

            # Save to file if requested
            if args.output:
                output_path = Path(args.output)
                with open(output_path, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"\n💾 Configuration result saved to: {output_path}")

        return 0 if result.get("success", False) else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())