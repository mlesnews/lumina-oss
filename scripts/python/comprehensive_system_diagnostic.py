#!/usr/bin/env python3
"""
Comprehensive System Diagnostic
Full sweep of DNS, network, browser, and automation readiness

Tags: #DIAGNOSTIC #SWEEP #SCAN #SYSTEM
"""

import sys
import json
import socket
import subprocess
import time
from pathlib import Path
from datetime import datetime

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

logger = get_logger("ComprehensiveSystemDiagnostic")


class ComprehensiveSystemDiagnostic:
    """Comprehensive system diagnostic sweep"""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "dns": {},
            "network": {},
            "browser": {},
            "automation": {},
            "homelab": {}
        }

    def run_all_diagnostics(self):
        """Run all diagnostic checks"""
        logger.info("=" * 70)
        logger.info("🔍 COMPREHENSIVE SYSTEM DIAGNOSTIC SWEEP")
        logger.info("=" * 70)
        logger.info("")

        # DNS Diagnostics
        logger.info("=" * 70)
        logger.info("1. DNS DIAGNOSTICS")
        logger.info("=" * 70)
        self.check_dns()
        logger.info("")

        # Network Diagnostics
        logger.info("=" * 70)
        logger.info("2. NETWORK CONNECTIVITY")
        logger.info("=" * 70)
        self.check_network()
        logger.info("")

        # Browser Diagnostics
        logger.info("=" * 70)
        logger.info("3. BROWSER STATUS")
        logger.info("=" * 70)
        self.check_browser()
        logger.info("")

        # Automation Readiness
        logger.info("=" * 70)
        logger.info("4. AUTOMATION READINESS")
        logger.info("=" * 70)
        self.check_automation()
        logger.info("")

        # Homelab Services
        logger.info("=" * 70)
        logger.info("5. HOMELAB SERVICES")
        logger.info("=" * 70)
        self.check_homelab()
        logger.info("")

        # Generate Summary
        self.generate_summary()

    def check_dns(self):
        """Check DNS resolution"""
        test_sites = ["google.com", "proton.me", "digital.fidelity.com"]
        dns_servers = ["<NAS_IP>", "<NAS_PRIMARY_IP>", "10.2.0.1", "8.8.8.8"]

        for dns_server in dns_servers:
            logger.info(f"Testing DNS Server: {dns_server}")
            results = []
            for site in test_sites:
                try:
                    result = subprocess.run(
                        ["nslookup", site, dns_server],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    success = result.returncode == 0 and "Address:" in result.stdout
                    results.append({"site": site, "success": success})
                    status = "✅" if success else "❌"
                    logger.info(f"   {status} {site}")
                except:
                    results.append({"site": site, "success": False})
                    logger.info(f"   ❌ {site} (timeout/error)")

            self.results["dns"][dns_server] = results

    def check_network(self):
        """Check network connectivity"""
        test_hosts = [
            ("google.com", 443),
            ("proton.me", 443),
            ("digital.fidelity.com", 443),
            ("<NAS_IP>", 53),
            ("<NAS_PRIMARY_IP>", 53)
        ]

        for host, port in test_hosts:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                result = sock.connect_ex((socket.gethostbyname(host) if not host.replace('.', '').isdigit() else host, port))
                sock.close()
                success = result == 0
                status = "✅" if success else "❌"
                logger.info(f"   {status} {host}:{port}")
                self.results["network"][f"{host}:{port}"] = success
            except Exception as e:
                logger.info(f"   ❌ {host}:{port} - {e}")
                self.results["network"][f"{host}:{port}"] = False

    def check_browser(self):
        """Check browser status"""
        try:
            import psutil
            neo_processes = []
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if 'neo' in (proc.info['name'] or '').lower():
                        neo_processes.append(proc.info['pid'])
                except:
                    pass

            logger.info(f"   Neo Browser: {len(neo_processes)} process(es) running")
            self.results["browser"]["neo_processes"] = len(neo_processes)

            # Check CDP
            try:
                import requests
                response = requests.get("http://localhost:9222/json", timeout=2)
                if response.status_code == 200:
                    sessions = response.json()
                    logger.info(f"   CDP: ✅ Available ({len(sessions)} session(s))")
                    self.results["browser"]["cdp_available"] = True
                    self.results["browser"]["cdp_sessions"] = len(sessions)
                else:
                    logger.info(f"   CDP: ❌ Not available (HTTP {response.status_code})")
                    self.results["browser"]["cdp_available"] = False
            except:
                logger.info(f"   CDP: ❌ Not available")
                self.results["browser"]["cdp_available"] = False
        except ImportError:
            logger.info("   ⚠️  psutil not available for process check")
            self.results["browser"]["neo_processes"] = 0

    def check_automation(self):
        """Check automation readiness"""
        try:
            from neo_browser_automation_engine import NEOBrowserAutomationEngine
            neo = NEOBrowserAutomationEngine(project_root)

            if neo._connect_cdp():
                logger.info("   Neo CDP: ✅ Connected")
                self.results["automation"]["neo_cdp"] = True

                # Test script execution
                test_result = neo.execute_script("return 'test';")
                if test_result == "test":
                    logger.info("   Script Execution: ✅ Working")
                    self.results["automation"]["script_execution"] = True
                else:
                    logger.info(f"   Script Execution: ⚠️  Returned: {test_result}")
                    self.results["automation"]["script_execution"] = False
            else:
                logger.info("   Neo CDP: ❌ Not connected")
                self.results["automation"]["neo_cdp"] = False
        except Exception as e:
            logger.info(f"   Automation Check: ❌ Error - {e}")
            self.results["automation"]["error"] = str(e)

    def check_homelab(self):
        """Check homelab services"""
        services = [
            ("pfSense", "<NAS_IP>", [53, 443, 80]),
            ("NAS", "<NAS_PRIMARY_IP>", [53, 443, 5000, 5001])
        ]

        for name, host, ports in services:
            logger.info(f"Checking {name} ({host}):")
            service_results = {}
            for port in ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    result = sock.connect_ex((host, port))
                    sock.close()
                    success = result == 0
                    status = "✅" if success else "❌"
                    logger.info(f"   {status} Port {port}")
                    service_results[port] = success
                except:
                    logger.info(f"   ❌ Port {port} (error)")
                    service_results[port] = False

            self.results["homelab"][name] = service_results

    def generate_summary(self):
        try:
            """Generate diagnostic summary"""
            logger.info("=" * 70)
            logger.info("📊 DIAGNOSTIC SUMMARY")
            logger.info("=" * 70)
            logger.info("")

            # DNS Summary
            dns_working = []
            dns_failing = []
            for server, results in self.results["dns"].items():
                success_count = sum(1 for r in results if r.get("success"))
                if success_count == len(results):
                    dns_working.append(server)
                else:
                    dns_failing.append(server)

            logger.info("DNS Servers:")
            logger.info(f"   ✅ Working: {', '.join(dns_working) if dns_working else 'None'}")
            logger.info(f"   ❌ Failing: {', '.join(dns_failing) if dns_failing else 'None'}")
            logger.info("")

            # Network Summary
            network_success = sum(1 for v in self.results["network"].values() if v)
            network_total = len(self.results["network"])
            logger.info(f"Network Connectivity: {network_success}/{network_total} successful")
            logger.info("")

            # Browser Summary
            logger.info("Browser Status:")
            logger.info(f"   Neo Processes: {self.results['browser'].get('neo_processes', 0)}")
            logger.info(f"   CDP Available: {'✅' if self.results['browser'].get('cdp_available') else '❌'}")
            logger.info("")

            # Automation Summary
            logger.info("Automation Readiness:")
            logger.info(f"   Neo CDP: {'✅' if self.results['automation'].get('neo_cdp') else '❌'}")
            logger.info(f"   Script Execution: {'✅' if self.results['automation'].get('script_execution') else '❌'}")
            logger.info("")

            # Recommendations
            logger.info("=" * 70)
            logger.info("💡 RECOMMENDATIONS")
            logger.info("=" * 70)
            logger.info("")

            if dns_failing:
                logger.warning("⚠️  DNS Issues Detected:")
                for server in dns_failing:
                    logger.info(f"   - {server}: Fix DNS service configuration")
                logger.info("")

            if not self.results['browser'].get('cdp_available'):
                logger.warning("⚠️  Browser CDP not available:")
                logger.info("   - Restart Neo with: python scripts/python/restart_neo_with_cdp.py")
                logger.info("")

            if not self.results['automation'].get('script_execution'):
                logger.warning("⚠️  Script execution not working:")
                logger.info("   - Check CDP connection")
                logger.info("   - Verify WebSocket connectivity")
                logger.info("")

            # Save results
            output_file = project_root / "data" / "diagnostics" / f"system_diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(self.results, f, indent=2)

            logger.info(f"📄 Full diagnostic report saved to: {output_file}")
            logger.info("")


        except Exception as e:
            self.logger.error(f"Error in generate_summary: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    diagnostic = ComprehensiveSystemDiagnostic()
    diagnostic.run_all_diagnostics()


if __name__ == "__main__":


    main()