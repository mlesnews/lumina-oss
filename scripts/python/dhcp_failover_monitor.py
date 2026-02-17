#!/usr/bin/env python3
"""
DHCP Active Failover Monitor

Monitors pfSense DHCP and automatically enables NAS DHCP as fallback
when pfSense DHCP fails. Automatically disables NAS DHCP when pfSense recovers.

Tags: #DHCP #FAILOVER #MONITORING #NETWORK @JARVIS @LUMINA
"""

import sys
import time
import socket
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from pfsense_azure_vault_integration import PFSenseAzureVaultIntegration
    PFSENSE_AVAILABLE = True
except ImportError:
    PFSENSE_AVAILABLE = False

try:
    from nas_azure_vault_integration import NASAzureVaultIntegration
    NAS_AVAILABLE = True
except ImportError:
    NAS_AVAILABLE = False

try:
    from synology_api_base import SynologyAPIBase
    SYNOLOGY_API_AVAILABLE = True
except ImportError:
    SYNOLOGY_API_AVAILABLE = False

try:
    from lumina_logger import get_logger
    logger = get_logger("DHCPFailoverMonitor")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("DHCPFailoverMonitor")

try:
    from auto_cron_registration import register_cron_service, CronScheduleConfig
    CRON_REGISTRATION_AVAILABLE = True
except ImportError:
    CRON_REGISTRATION_AVAILABLE = False


class DHCPStatus(Enum):
    """DHCP server status"""
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    FAILED = "failed"
    RECOVERING = "recovering"


class DHCPFailoverMonitor:
    """
    Monitor DHCP servers and manage active failover
    """

    def __init__(
        self,
        pfsense_ip: str = "<NAS_IP>",
        nas_ip: str = "<NAS_PRIMARY_IP>",
        check_interval: int = 30,  # Check every 30 seconds
        failure_threshold: int = 3,  # 3 consecutive failures = down
        recovery_threshold: int = 3,  # 3 consecutive successes = recovered
        dhcp_port: int = 67,  # DHCP server port
        enable_nas_dhcp_on_failover: bool = True
    ):
        """
        Initialize DHCP Failover Monitor

        Args:
            pfsense_ip: pfSense IP address
            nas_ip: NAS IP address
            check_interval: Seconds between checks
            failure_threshold: Consecutive failures before declaring down
            recovery_threshold: Consecutive successes before declaring recovered
            dhcp_port: DHCP server port (67)
            enable_nas_dhcp_on_failover: Enable NAS DHCP when pfSense fails
        """
        self.pfsense_ip = pfsense_ip
        self.nas_ip = nas_ip
        self.check_interval = check_interval
        self.failure_threshold = failure_threshold
        self.recovery_threshold = recovery_threshold
        self.dhcp_port = dhcp_port
        self.enable_nas_dhcp_on_failover = enable_nas_dhcp_on_failover

        # State tracking
        self.pfsense_status = DHCPStatus.UNKNOWN
        self.nas_status = DHCPStatus.UNKNOWN
        self.pfsense_failure_count = 0
        self.pfsense_success_count = 0
        self.nas_dhcp_enabled = False
        self.last_check = None
        self.failover_active = False
        self.failover_started = None

        # Initialize integrations
        self.pfsense = None
        if PFSENSE_AVAILABLE:
            self.pfsense = PFSenseAzureVaultIntegration(pfsense_ip=pfsense_ip)

        self.nas = None
        if NAS_AVAILABLE:
            self.nas = NASAzureVaultIntegration(nas_ip=nas_ip)

        # Initialize Synology API (preferred over SSH)
        self.synology_api = None
        self.synology_api_credentials = None
        if SYNOLOGY_API_AVAILABLE:
            # Get credentials for API login
            if self.nas:
                self.synology_api_credentials = self.nas.get_nas_credentials()
                if self.synology_api_credentials:
                    self.synology_api = SynologyAPIBase(
                        nas_ip=nas_ip,
                        nas_port=5001,
                        verify_ssl=False
                    )
                    # Login to API
                    if self.synology_api.login(
                        username=self.synology_api_credentials.get("username", ""),
                        password=self.synology_api_credentials.get("password", "")
                    ):
                        logger.info("✅ Synology API initialized and logged in")
                    else:
                        logger.warning("⚠️  Synology API login failed, will use SSH fallback")
                        self.synology_api = None

        logger.info("DHCP Failover Monitor initialized")
        logger.info(f"  Primary: {pfsense_ip} (pfSense)")
        logger.info(f"  Fallback: {nas_ip} (NAS)")
        logger.info(f"  Check interval: {check_interval}s")
        logger.info(f"  Failure threshold: {failure_threshold}")
        logger.info(f"  Recovery threshold: {recovery_threshold}")

    def check_pfsense_dhcp(self) -> bool:
        """
        Check if pfSense DHCP is responding

        Returns:
            True if pfSense DHCP is healthy
        """
        try:
            # Method 1: Check if DHCP service is running (via SSH)
            if self.pfsense:
                # Try SSH check
                result = self.pfsense.execute_ssh_command(
                    "ps aux | grep dhcpd | grep -v grep"
                )
                if result.get("success") and result.get("output"):
                    return True

            # Method 2: Check if pfSense is reachable
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(2)
            try:
                sock.connect((self.pfsense_ip, 443))  # HTTPS port
                sock.close()
                return True
            except:
                sock.close()
                return False

        except Exception as e:
            logger.debug(f"Error checking pfSense DHCP: {e}")
            return False

    def check_nas_dhcp(self) -> bool:
        """
        Check if NAS DHCP is available

        Returns:
            True if NAS DHCP is available
        """
        try:
            # Method 1: Use Synology API (preferred)
            if self.synology_api and self.synology_api.sid:
                # Check DHCP service via API
                # Note: Synology doesn't have a direct DHCP API, but we can check package status
                # For now, fall back to SSH check
                pass

            # Method 2: Use SSH (fallback)
            if not self.nas:
                return False

            ssh_client = self.nas.get_ssh_client()
            if not ssh_client:
                return False

            # Check DHCP service status
            stdin, stdout, stderr = ssh_client.exec_command(
                "synoservice --status dhcpd"
            )
            status_output = stdout.read().decode('utf-8')
            ssh_client.close()

            # Check if DHCP Server package is installed and running
            if "running" in status_output.lower() or "start" in status_output.lower():
                return True

            return False

        except Exception as e:
            logger.debug(f"Error checking NAS DHCP: {e}")
            return False

    def enable_nas_dhcp(self) -> bool:
        """
        Enable NAS DHCP server

        Uses Synology API if available, falls back to SSH

        Returns:
            True if successfully enabled
        """
        try:
            # Method 1: Try Synology API first (if available)
            # Note: Synology doesn't have direct DHCP API, but we can use service control
            # For now, use SSH which is more reliable for service control

            # Method 2: Use SSH (primary method)
            if not self.nas:
                logger.error("NAS integration not available")
                return False

            ssh_client = self.nas.get_ssh_client()
            if not ssh_client:
                logger.error("Could not establish SSH connection to NAS")
                return False

            # Start DHCP service via SSH
            stdin, stdout, stderr = ssh_client.exec_command(
                "synoservice --start dhcpd"
            )
            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode('utf-8')
            ssh_client.close()

            if exit_status == 0:
                logger.info("✅ NAS DHCP enabled via SSH")
                self.nas_dhcp_enabled = True
                return True
            else:
                logger.warning(f"⚠️  Failed to enable NAS DHCP: {output}")
                return False

        except Exception as e:
            logger.error(f"❌ Error enabling NAS DHCP: {e}")
            return False

    def disable_nas_dhcp(self) -> bool:
        """
        Disable NAS DHCP server

        Uses Synology API if available, falls back to SSH

        Returns:
            True if successfully disabled
        """
        try:
            # Method 1: Try Synology API first (if available)
            # Note: Synology doesn't have direct DHCP API, use SSH for service control

            # Method 2: Use SSH (primary method)
            if not self.nas:
                return False

            ssh_client = self.nas.get_ssh_client()
            if not ssh_client:
                return False

            # Stop DHCP service via SSH
            stdin, stdout, stderr = ssh_client.exec_command(
                "synoservice --stop dhcpd"
            )
            exit_status = stdout.channel.recv_exit_status()
            output = stdout.read().decode('utf-8')
            ssh_client.close()

            if exit_status == 0:
                logger.info("✅ NAS DHCP disabled via SSH (pfSense recovered)")
                self.nas_dhcp_enabled = False
                return True
            else:
                logger.warning(f"⚠️  Failed to disable NAS DHCP: {output}")
                return False

        except Exception as e:
            logger.error(f"❌ Error disabling NAS DHCP: {e}")
            return False

    def check_and_failover(self) -> Dict[str, Any]:
        """
        Check DHCP status and perform failover if needed

        Returns:
            Status dictionary
        """
        self.last_check = datetime.now()

        # Check pfSense DHCP
        pfsense_healthy = self.check_pfsense_dhcp()

        if pfsense_healthy:
            self.pfsense_success_count += 1
            self.pfsense_failure_count = 0

            # Check if recovered
            if self.pfsense_status == DHCPStatus.FAILED:
                if self.pfsense_success_count >= self.recovery_threshold:
                    self.pfsense_status = DHCPStatus.HEALTHY
                    logger.info("✅ pfSense DHCP RECOVERED")

                    # Disable NAS DHCP if it was enabled
                    if self.nas_dhcp_enabled and self.enable_nas_dhcp_on_failover:
                        self.disable_nas_dhcp()
                        self.failover_active = False
                        failover_duration = None
                        if self.failover_started:
                            failover_duration = (datetime.now() - self.failover_started).total_seconds()
                            self.failover_started = None
                        logger.info(f"✅ Failover ended (duration: {failover_duration}s)")
            else:
                self.pfsense_status = DHCPStatus.HEALTHY
        else:
            self.pfsense_failure_count += 1
            self.pfsense_success_count = 0

            # Check if failed
            if self.pfsense_failure_count >= self.failure_threshold:
                if self.pfsense_status != DHCPStatus.FAILED:
                    self.pfsense_status = DHCPStatus.FAILED
                    logger.warning(f"❌ pfSense DHCP FAILED ({self.pfsense_failure_count} consecutive failures)")

                    # Enable NAS DHCP failover
                    if self.enable_nas_dhcp_on_failover and not self.nas_dhcp_enabled:
                        if self.enable_nas_dhcp():
                            self.failover_active = True
                            self.failover_started = datetime.now()
                            logger.warning("🔄 FAILOVER ACTIVATED: NAS DHCP enabled")

        # Check NAS DHCP status
        nas_available = self.check_nas_dhcp()
        if nas_available:
            self.nas_status = DHCPStatus.HEALTHY
        else:
            if self.nas_dhcp_enabled:
                self.nas_status = DHCPStatus.FAILED
            else:
                self.nas_status = DHCPStatus.UNKNOWN

        return {
            "timestamp": self.last_check.isoformat(),
            "pfsense": {
                "ip": self.pfsense_ip,
                "status": self.pfsense_status.value,
                "healthy": pfsense_healthy,
                "failure_count": self.pfsense_failure_count,
                "success_count": self.pfsense_success_count
            },
            "nas": {
                "ip": self.nas_ip,
                "status": self.nas_status.value,
                "available": nas_available,
                "dhcp_enabled": self.nas_dhcp_enabled
            },
            "failover": {
                "active": self.failover_active,
                "started": self.failover_started.isoformat() if self.failover_started else None
            }
        }

    def run_continuous(self, duration: Optional[int] = None):
        """
        Run continuous monitoring

        Args:
            duration: Duration in seconds (None = run forever)
        """
        logger.info("=" * 70)
        logger.info("🚀 DHCP FAILOVER MONITOR - Starting Continuous Monitoring")
        logger.info("=" * 70)

        start_time = datetime.now()
        check_count = 0

        try:
            while True:
                check_count += 1
                logger.info(f"\n📋 Check #{check_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                status = self.check_and_failover()

                # Log status
                pfsense_status = "✅" if status["pfsense"]["healthy"] else "❌"
                nas_status = "✅" if status["nas"]["dhcp_enabled"] else "⏸️"
                failover_status = "🔄 ACTIVE" if status["failover"]["active"] else "✅ NORMAL"

                logger.info(f"  {pfsense_status} pfSense DHCP: {status['pfsense']['status']}")
                logger.info(f"  {nas_status} NAS DHCP: {status['nas']['status']} (enabled: {status['nas']['dhcp_enabled']})")
                logger.info(f"  {failover_status} Failover: {status['failover']['active']}")

                # Check duration
                if duration:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    if elapsed >= duration:
                        logger.info(f"\n⏰ Monitoring duration reached ({duration}s)")
                        break

                # Sleep until next check
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            logger.info("\n\n⚠️  Monitoring stopped by user")
        except Exception as e:
            logger.error(f"\n❌ Error in monitoring loop: {e}", exc_info=True)
        finally:
            logger.info("\n" + "=" * 70)
            logger.info("📊 Monitoring Summary:")
            logger.info(f"  Total checks: {check_count}")
            logger.info(f"  Duration: {(datetime.now() - start_time).total_seconds():.1f}s")
            logger.info(f"  Final pfSense status: {self.pfsense_status.value}")
            logger.info(f"  Final NAS DHCP enabled: {self.nas_dhcp_enabled}")
            logger.info(f"  Failover active: {self.failover_active}")
            logger.info("=" * 70)


def run_monitor_check():
    """
    Run a single monitor check (for cron scheduling)

    This function is registered with the cron system to run periodic checks
    """
    monitor = DHCPFailoverMonitor()
    status = monitor.check_and_failover()
    return status


# Register with cron system if available
if CRON_REGISTRATION_AVAILABLE:
    try:
        from auto_cron_registration import get_registry
        registry = get_registry()
        registry.register_service(
            service_id="dhcp_failover_monitor",
            service_name="DHCP Active Failover Monitor",
            script_path="scripts/python/dhcp_failover_monitor.py",
            schedule_config=CronScheduleConfig.custom(
                cron_expr="*/1 * * * *",  # Every minute
                description="DHCP Active Failover Monitor - Checks pfSense DHCP and manages NAS failover",
                tags=["#DHCP", "#FAILOVER", "#MONITORING", "#NETWORK", "@JARVIS", "@LUMINA"]
            ),
            auto_deploy=True
        )
        logger.info("✅ DHCP Failover Monitor registered with cron system")
    except Exception as e:
        logger.warning(f"⚠️  Could not register with cron system: {e}")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="DHCP Active Failover Monitor"
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
        "--check-interval",
        type=int,
        default=30,
        help="Check interval in seconds (default: 30)"
    )
    parser.add_argument(
        "--failure-threshold",
        type=int,
        default=3,
        help="Consecutive failures before failover (default: 3)"
    )
    parser.add_argument(
        "--recovery-threshold",
        type=int,
        default=3,
        help="Consecutive successes before recovery (default: 3)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        help="Run for specified duration in seconds (default: forever)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run check once and exit"
    )
    parser.add_argument(
        "--disable-auto-failover",
        action="store_true",
        help="Disable automatic NAS DHCP enable/disable (monitor only)"
    )

    args = parser.parse_args()

    # Initialize monitor
    monitor = DHCPFailoverMonitor(
        pfsense_ip=args.pfsense_ip,
        nas_ip=args.nas_ip,
        check_interval=args.check_interval,
        failure_threshold=args.failure_threshold,
        recovery_threshold=args.recovery_threshold,
        enable_nas_dhcp_on_failover=not args.disable_auto_failover
    )

    if args.once:
        # Single check
        status = monitor.check_and_failover()
        print("\n📊 DHCP Status:")
        print(f"  pfSense: {status['pfsense']['status']} ({'✅' if status['pfsense']['healthy'] else '❌'})")
        print(f"  NAS: {status['nas']['status']} (enabled: {status['nas']['dhcp_enabled']})")
        print(f"  Failover: {'🔄 ACTIVE' if status['failover']['active'] else '✅ NORMAL'}")
        return 0
    else:
        # Continuous monitoring
        monitor.run_continuous(duration=args.duration)
        return 0


if __name__ == "__main__":


    sys.exit(main())